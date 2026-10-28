"""Offline checks of attribution receipts, source evidence and liveness arithmetic."""
import hashlib
import ipaddress
import json
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text())


def main():
    ownership=Path("evidence/ownership-20261028")
    registry=read(ownership/"rdap.json")
    allocation=next(r["registry_facts"] for r in registry if r["url"].endswith("/ip/198.154.93.197"))
    assert allocation["cidr0_cidrs"]==[dict(v4prefix="198.154.80.0",length=20)]
    assert any(e["handle"]=="BNS-34" and e["name"]=="B2 Net Solutions Inc." for e in allocation["organizations"])
    asn=next(r["registry_facts"] for r in registry if r["url"].endswith("/autnum/55286"))
    assert asn["name"]=="SERVER-MANIA"
    routing=read(ownership/"routing.json")
    routed=next(r["reported_data"] for r in routing if "prefix-overview" in r["url"])
    assert routed["resource"]=="198.154.93.0/24" and routed["asns"][0]["asn"]==55286
    for record in registry:
        for entity in record.get("registry_facts",{}).get("organizations",[]):
            if entity.get("kind")=="individual":assert entity["name"] is None
    certs=[r for r in read(ownership/"tls-certificates.json") if "spki_sha256" in r]
    assert len(certs)==8 and len({r["spki_sha256"] for r in certs})==8
    zones=read(ownership/"dns-zones.json")
    def nameservers(domain):
        row=next(z for z in zones if z["domain"]==domain)
        return set(next(r["values"] for r in row["records"] if r["type"]=="NS"))
    assert nameservers("satoshi.io")==nameservers("electrumr.io")
    assert nameservers("server.sv")!=nameservers("satoshi.io")
    sources=Path("evidence/server-sources-20261028")
    facts=read(sources/"source-facts.json")
    assert all(row["exit_code"]==0 for row in facts)
    tcp=next(r for r in facts if r.get("path")=="src/tcp/tcp.service.ts")
    assert any("['ElectrumX 1.20.2', '1.4']" in line["text"] for line in tcp["matched_lines"])
    env=next(r for r in facts if r.get("path")==".env.sample")
    assert any(line["text"]=="BITAILS_API_ENDPOINT=https://api.bitails.io" for line in env["matched_lines"])
    repairs=read(sources/"github-search-query-repairs.json")["query_repairs"]
    assert all(r["exit_code"]==0 and r["result"]["total_count"]==0 for r in repairs)
    node=read(sources/"additional-components.json")
    assert any(r.get("result",{}).get("full_name")=="bitcoin-sv/bitcoin-sv" for r in node if isinstance(r.get("result"),dict))
    root=Path("evidence/liveness-20261028")
    summary=read(root/"summary.json")
    rounds=[read(root/f"round-{i}.json") for i in [1,2]]
    expected_hosts={r["host"] for r in summary["samples"]}
    assert len(expected_hosts)==9
    observed_current={host:0 for host in expected_hosts}
    observed_responsive={host:0 for host in expected_hosts}
    matching_headers=0
    for row in rounds:
        assert {s["host"] for s in row["servers"]}==expected_hosts
        references=[r for r in row["references_before"]+row["references_after"] if "height" in r]
        assert len({r["url"] for r in references})==2
        for sample in row["servers"]:
            host=sample["host"]
            observed_responsive[host]+=int(sample["electrum_response"])
            assert sample["wallet_queries_sent"] is False
            assert all(c["request"]["method"] in ["server.version","blockchain.headers.subscribe","server.ping"] for c in sample["calls"])
            if "tip" not in sample:
                continue
            call=next(c for c in sample["calls"] if c["request"]["method"]=="blockchain.headers.subscribe")
            raw=bytes.fromhex(call["response"]["result"]["hex"])
            assert len(raw)==80
            digest=hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex()
            assert digest==sample["tip"]["block_hash"]
            same=[r for r in references if r["height"]==sample["tip"]["height"]]
            assert len({r["url"] for r in same})==2
            assert all(r["block_hash"]==digest for r in same)
            observed_current[host]+=1
            matching_headers+=1
    for row in summary["samples"]:
        assert row["responsive_samples"]==observed_responsive[row["host"]]
        assert row["current_samples"]==observed_current[row["host"]]
    assert observed_responsive["electrum.server.sv"]==0
    assert observed_current["esv.bitails.io"]==1
    assert matching_headers==15
    result=dict(status="PASS",literal_endpoints=9,rounds=2,
        responsive_in_both_samples=sum(n==2 for n in observed_responsive.values()),
        current_in_both_samples=sum(n==2 for n in observed_current.values()),
        valid_headers_matching_both_reference_providers=matching_headers,
        registered_network_holder="B2 Net Solutions Inc.",shared_prefix="198.154.93.0/24",origin_asn=55286,
        observed_unique_spki_fingerprints=8,public_bitails_source_verified=True,
        legal_application_operator_for_all_six_shared_prefix_hosts_established=False,
        electrumr_deployed_build_source_attested=False)
    Path("evidence/followup-verification.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
