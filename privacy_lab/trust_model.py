"""Offline endpoint, attribution and observation accounting; never adds unlike counts."""
import argparse
import ast
from collections import Counter
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import subprocess

PIN = "672df8f4512f6adf16a3c99146baa6be9b93d86f"
ROOT = Path("evidence/trust-model-20261028")
# Attribution buckets are analytical labels, not verified independent legal persons.
ANNOTATIONS = {
    "sv.electrumr.sv": ("Satoshi.io / ElectrumR public association", "55286", "Cloudflare"),
    "sv2.electrumr.sv": ("Satoshi.io / ElectrumR public association", "55286", "Cloudflare"),
    "sv.satoshi.io": ("Satoshi.io / ElectrumR public association", "55286", "Cloudflare"),
    "sv2.satoshi.io": ("Satoshi.io / ElectrumR public association", "55286", "Cloudflare"),
    "sv3.satoshi.io": ("Satoshi.io / ElectrumR public association", "55286", "Cloudflare"),
    "electrumx.gorillapool.io": ("GorillaPool first-party operator statement", "7018", "Cloudflare"),
    "esv.bitails.io": ("Bitails first-party endpoint/source association", "24940", "Cloudflare"),
    "electrum.server.sv": ("Unresolved: electrum.server.sv", "55286", "101domain"),
    "bsv.aftrek.org": ("Unresolved: bsv.aftrek.org", "24940", "AWS DNS"),
}


def read(path):
    return json.loads(Path(path).read_text())


def model():
    pools = read("evidence/destinations-20261028/source-destinations.json")
    core = {h for h, _ in pools["priority_pool"]["entries"]}
    helper = set(pools["verification_pool"]["entries"])
    hosts = core | helper
    assert hosts == set(ANNOTATIONS)
    # The network mapping is checked against retained routing observations below.
    dns = read("evidence/destinations-20261028/dns.json")
    zones=read("evidence/ownership-20261028/dns-zones.json")
    routing = read("evidence/ownership-20261028/routing.json")
    rows = []
    for host in sorted(hosts):
        bucket, asn, dns_provider = ANNOTATIONS[host]
        domain=".".join(host.split(".")[-2:])
        zone=next(z for z in zones if z["domain"]==domain)
        ns=next(r["values"] for r in zone["records"] if r["type"]=="NS")
        expected_suffix={"Cloudflare":"ns.cloudflare.com.","101domain":"101domain.com.","AWS DNS":"awsdns-"}[dns_provider]
        assert all(expected_suffix in value for value in ns),(domain,ns)
        addresses=next(r["addresses"] for r in dns if r["host"]==host)
        for address in addresses:
            observed=next((r["reported_data"] for r in routing
                           if r["url"].endswith("resource="+address.replace(":","%3A"))),None)
            if observed is None and address.startswith("198.154.93."):
                observed=next(r["reported_data"] for r in routing if r["url"].endswith("resource=198.154.93.197"))
            assert observed is not None and asn in observed["asns"],(host,address)
            assert ipaddress.ip_address(address) in ipaddress.ip_network(observed["prefix"])
        rows.append(dict(host=host,core=host in core,helper=host in helper,
                         attribution_bucket=bucket,origin_asn=asn,dns_provider=dns_provider,
                         consumer_correlation_domain="Shared 198.154.93.0/24" if asn=="55286" else bucket))
    def counts(selected, key):
        return dict(sorted(Counter(r[key] for r in rows if r["host"] in selected).items()))
    return dict(wallet_commit=PIN,
                counts=dict(core_literal_hosts=len(core),helper_literal_hosts=len(helper),
                            overlap=len(core & helper),union=len(hosts),
                            core_only=sorted(core - helper),helper_only=sorted(helper - core),
                            attribution_buckets=len(counts(hosts,"attribution_bucket")),
                            identified_public_association_buckets=3,unresolved_endpoint_buckets=2,
                            independent_legal_operator_count=None,
                            network_resource_origin_organizations=3,authoritative_dns_provider_brands=3,
                            core_connection_target=10,additional_default_http_hosts=2,
                            literal_client_service_hostname_inventory=11,
                            consumer_correlation_domains_union=4,consumer_correlation_domains_core=4,
                            consumer_correlation_domains_helper=3,
                            all_provider_sharing_financial_correlation_domains=1,
                            shared_prefix_union_hosts=6,shared_prefix_core_hosts=5,shared_prefix_helper_hosts=6),
                distributions={scope:{key:counts(selected,key) for key in ["attribution_bucket","origin_asn","dns_provider","consumer_correlation_domain"]}
                               for scope,selected in [("core",core),("helper",helper),("union",hosts)]},
                endpoints=rows,
                consumer_assumptions=["Treat all six 198.154.93.0/24 endpoints as related and pooling all observations",
                                      "Evaluate every service provider sharing its received observations across brands",
                                      "These are conservative threat assumptions, not verified common ownership or actual sharing"],
                default_http=[dict(host="electrumsv.io",url="https://electrumsv.io/release.json",trigger="GUI startup, check_updates=True and not offline",wallet_identifiers_in_reviewed_call=False),
                              dict(host="bananablocks.com",url="https://bananablocks.com/api/v1/exchangerates",history_url="https://bananablocks.com/api/v1/stats/chart/exchange_rate?days=365",trigger="online daemon FxTask, enabled by default, USD default",wallet_identifiers_in_reviewed_call=False)],
                limits=["Attribution buckets are not established independent legal operators",
                        "Network and DNS provider counts overlap application relationships and must not be summed",
                        "Literal destination inventory is not a guarantee every destination receives a request in every session",
                        "Core main changes, cached/discovered peers, HTTP redirects and downstream services prevent a universal fixed party count",
                        "HTTP defaults are source findings; the headless observation does not run the GUI or daemon FX task",
                        "No likelihood, equal selection probability, or operational independence follows from counts"])


def source_receipts(source):
    head = subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
    assert head == PIN
    files = ["electrumsv/network.py","electrumsv/verification_utils.py","electrumsv/headers_storage.py",
             "electrumsv/exchange_rate.py","electrumsv/gui/qt/app.py","electrumsv/daemon.py",
             "electrumsv/extensions.py","electrumsv/wallet.py"]
    receipts=[]
    trees={}
    for name in files:
        raw = subprocess.check_output(["git","-C",str(source),"show",f"{PIN}:{name}"])
        assert (source/name).read_bytes() == raw, name
        tree=ast.parse(raw)
        trees[name]=tree
        receipts.append(dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
                             url=f"https://github.com/TruthMachine/ElectrumSVP/blob/{PIN}/{name}"))
    pools=read("evidence/destinations-20261028/source-destinations.json")
    def assigned(tree,name):
        return next(ast.literal_eval(node.value) for node in ast.walk(tree)
                    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in node.targets))
    assert assigned(trees[files[0]],"priority_servers")==[tuple(row) for row in pools["priority_pool"]["entries"]]
    assert assigned(trees[files[1]],"SERVERS")==pools["verification_pool"]["entries"]
    def config_defaults(tree,key):
        return [ast.literal_eval(n.args[1]) for n in ast.walk(tree)
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=="get"
                and len(n.args)>1 and isinstance(n.args[0],ast.Constant) and n.args[0].value==key]
    assert True in config_defaults(trees[files[0]],"auto_connect")
    assert True in config_defaults(trees[files[3]],"use_exchange_rate")
    assert "BananaBlocks" in config_defaults(trees[files[3]],"use_exchange")
    assert True in config_defaults(trees[files[4]],"check_updates")
    assert any(isinstance(n,ast.IfExp) and isinstance(n.body,ast.Constant) and n.body.value==1
               and isinstance(n.orelse,ast.Constant) and n.orelse.value==10 for n in ast.walk(trees[files[0]]))
    return dict(wallet_commit=PIN,collection_utc=datetime.now(timezone.utc).isoformat(),files=receipts,
                checked=["literal core/helper pools match pinned source AST",
                         "auto_connect=True, use_exchange_rate=True, BananaBlocks default, check_updates=True",
                         "all receipt bytes match pinned Git blobs and unchanged local files"],
                manually_reviewed_flow_locations={"startup_header_helper":"electrumsv/headers_storage.py:99-134,213-216",
                    "automatic_proof_BEEF":"electrumsv/wallet.py:3043-3060",
                    "missing_transaction_helper":"electrumsv/verification_utils.py:865-905",
                    "proof_helper":"electrumsv/verification_utils.py:565-603,975-1027",
                    "default_FX_launch":"electrumsv/daemon.py:153-160",
                    "default_GUI_update_launch":"electrumsv/gui/qt/app.py:370-388,417-423"})


def verify_observation():
    root=Path("evidence/default-session-attempt-01")
    run=read(root/"run.json")
    events=[json.loads(line) for line in (root/"events.jsonl").read_text().splitlines()]
    assert [e["sequence"] for e in events]==list(range(1,len(events)+1))
    core=[e for e in events if e["event"]=="rpc_completed"]
    helper=[e for e in events if e["event"]=="helper_tls_send_completed"]
    assert run["network_settings_supplied"]==[] and run["network_target_connections"]==10
    assert run["auto_connect"] is True and run["proxy"]=="None"
    assert run["observed_balance_sats"]==0 and run["disposable_state_removed"] is True
    assert run["status"]=="PASS"
    core_hosts={e["host"] for e in core}
    helper_hosts={e["host"] for e in helper}
    assert core_hosts==set(run["core_completed_hosts"])
    assert helper_hosts==set(run["helper_sent_hosts"])
    assert {e["method"] for e in helper}=={"blockchain.block.header"}
    assert len({tuple(e["params"]) for e in helper})==1
    subscriptions=[e for e in core if e["method"]=="blockchain.scripthash.subscribe"]
    assert len({e["host"] for e in subscriptions})==1
    assert len({e["params"][0] for e in subscriptions})==40
    assert all(e["params"] for e in subscriptions)
    assert not any(e["method"].startswith("blockchain.transaction.") for e in core+helper)
    union=core_hosts|helper_hosts
    return dict(status="PASS",core_rpc_response_hosts=len(core_hosts),helper_tls_send_hosts=len(helper_hosts),
                observed_electrum_hostname_union=len(union),
                attribution_buckets_represented=len({ANNOTATIONS[h][0] for h in union}),
                consumer_correlation_domains_represented=len({"shared-prefix" if ANNOTATIONS[h][1]=="55286" else ANNOTATIONS[h][0] for h in union}),
                origin_organizations_represented=len({ANNOTATIONS[h][1] for h in union}),
                full_script_collection_recipients=sorted({e["host"] for e in subscriptions}),
                script_hashes=40,financial_helper_rpc_observed=False,
                helper_scope="block height only; successful client TLS send does not prove server retention",
                gui_http_observed=False,independent_legal_operator_count=None)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path)
    parser.add_argument("--verify",action="store_true")
    args=parser.parse_args()
    if args.verify:
        assert read(ROOT/"model.json")==model()
        observed=verify_observation()
        assert read(ROOT/"observation-verification.json")==observed
        print(json.dumps(observed,indent=2))
        return
    assert args.source is not None,"--source is required to collect pinned source receipts"
    ROOT.mkdir(parents=True,exist_ok=False)
    (ROOT/"source-receipts.json").write_text(json.dumps(source_receipts(args.source),indent=2)+"\n")
    (ROOT/"model.json").write_text(json.dumps(model(),indent=2)+"\n")
    observed=verify_observation()
    (ROOT/"observation-verification.json").write_text(json.dumps(observed,indent=2)+"\n")
    print(json.dumps(observed,indent=2))


if __name__=="__main__":main()
