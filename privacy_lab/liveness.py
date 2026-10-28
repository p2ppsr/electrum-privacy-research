"""Bounded public Electrum liveness and chain-tip checks, without wallet queries."""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import socket
import ssl
import time

from .ownership import fetch

REFERENCES=["https://api.bitails.io/network/info",
            "https://api.whatsonchain.com/v1/bsv/main/chain/info"]


def utc():
    return datetime.now(timezone.utc).isoformat()


def reference(url):
    row,data=fetch(url)
    if data:
        try:
            value=json.loads(data)
            row.update(reported=value,height=value.get("blocks"),
                       block_hash=value.get("bestBlockhash",value.get("bestblockhash")))
        except Exception as exc:
            row["parse_error"]=repr(exc)
    return row


def probe(host):
    result=dict(host=host,port=50002,started_at=utc(),calls=[],tcp_connected=False,
                tls_connected=False,electrum_response=False,
                wallet_queries_sent=False,certificate_identity_authenticated=False)
    start=time.monotonic()
    phase="DNS"
    try:
        result["dns_addresses"]=sorted({r[4][0] for r in socket.getaddrinfo(host,50002,type=socket.SOCK_STREAM)})
        phase="TCP"
        with socket.create_connection((host,50002),timeout=5) as raw:
            result.update(tcp_connected=True,connected_peer=raw.getpeername())
            phase="TLS"
            context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.check_hostname=False
            context.verify_mode=ssl.CERT_NONE
            with context.wrap_socket(raw,server_hostname=host) as stream:
                result.update(tls_connected=True,tls=stream.version(),
                              certificate_sha256=hashlib.sha256(stream.getpeercert(binary_form=True)).hexdigest())
                stream.settimeout(5)
                file=stream.makefile("rwb")
                for number,(method,params) in enumerate([
                    ("server.version",["controlled-privacy-research-liveness",["1.4","1.4.2"]]),
                    ("blockchain.headers.subscribe",[]),("server.ping",[])],1):
                    phase=method
                    request=dict(jsonrpc="2.0",id=number,method=method,params=params)
                    call=dict(request=request,sent_at=utc())
                    result["calls"].append(call)
                    sent=time.monotonic()
                    file.write((json.dumps(request)+"\n").encode());file.flush()
                    deadline=sent+5
                    response=None
                    while time.monotonic()<deadline:
                        stream.settimeout(max(0.05,deadline-time.monotonic()))
                        line=file.readline(2*1024*1024)
                        if not line:
                            raise ConnectionError("EOF before requested response")
                        message=json.loads(line)
                        if isinstance(message,dict) and message.get("id")==number:
                            response=message
                            break
                        call.setdefault("other_messages",[]).append(message)
                    if response is None:
                        raise TimeoutError("No matching JSON-RPC response")
                    call.update(received_at=utc(),elapsed_ms=round((time.monotonic()-sent)*1000,2),response=response)
                    result["electrum_response"]=True
                    if method=="server.version":
                        value=response.get("result")
                        if not isinstance(value,list) or len(value)!=2:
                            raise ValueError("Invalid version response")
                        result.update(advertised_software=value[0],negotiated_protocol=value[1])
                    if method=="blockchain.headers.subscribe":
                        value=response.get("result")
                        if not isinstance(value,dict) or not isinstance(value.get("height"),int):
                            raise ValueError("Invalid header subscription result")
                        header=bytes.fromhex(value.get("hex",""))
                        if len(header)!=80:
                            raise ValueError("Expected one 80-byte block header")
                        timestamp=int.from_bytes(header[68:72],"little")
                        block_hash=hashlib.sha256(hashlib.sha256(header).digest()).digest()[::-1].hex()
                        result["tip"]=dict(height=value["height"],block_hash=block_hash,
                            header_timestamp=timestamp,header_time_utc=datetime.fromtimestamp(timestamp,timezone.utc).isoformat(),
                            locally_computed_hash=True,proof_of_work_validated=False)
    except Exception as exc:
        result.update(failed_phase=phase,error=repr(exc))
    result.update(finished_at=utc(),elapsed_ms=round((time.monotonic()-start)*1000,2))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--rounds",type=int,default=2,choices=range(1,4))
    parser.add_argument("--interval",type=int,default=10,choices=range(0,31))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    source=json.loads(Path("evidence/destinations-20261028/source-destinations.json").read_text())
    hosts=sorted({h for h,ports in source["priority_pool"]["entries"]}|set(source["verification_pool"]["entries"]))
    rounds=[]
    for n in range(args.rounds):
        with concurrent.futures.ThreadPoolExecutor(max_workers=11) as executor:
            before=list(executor.map(reference,REFERENCES))
            samples=list(executor.map(probe,hosts))
            after=list(executor.map(reference,REFERENCES))
        row=dict(round=n+1,references_before=before,servers=samples,references_after=after)
        (args.output/f"round-{n+1}.json").write_text(json.dumps(row,indent=2)+"\n")
        rounds.append(row)
        print(json.dumps(dict(round=n+1,responsive=sum(s["electrum_response"] for s in samples),valid_tip=sum("tip" in s for s in samples))),flush=True)
        if n+1<args.rounds:
            time.sleep(args.interval)
    summary=[]
    for host in hosts:
        samples=[next(s for s in row["servers"] if s["host"]==host) for row in rounds]
        assessments=[]
        for row,sample in zip(rounds,samples):
            refs=[r for r in row["references_before"]+row["references_after"] if isinstance(r.get("height"),int)]
            tip=sample.get("tip")
            assessment=dict(round=row["round"],electrum_response=sample["electrum_response"],tip=tip)
            if tip and refs:
                maximum=max(r["height"] for r in refs)
                same=[r for r in refs if r["height"]==tip["height"]]
                matches=[r["url"] for r in same if r.get("block_hash")==tip["block_hash"]]
                usable_same=[r for r in same if isinstance(r.get("block_hash"),str)]
                conflicting_reference_hashes=len({r["block_hash"] for r in usable_same})>1
                assessment.update(reference_max_height=maximum,height_lag=maximum-tip["height"],
                    same_height_reference_hash_matches=sorted(set(matches)),
                    reference_hash_disagreement=conflicting_reference_hashes,
                    apparent_current=(0<=maximum-tip["height"]<=2 and not conflicting_reference_hashes
                                      and (not usable_same or len(matches)==len(usable_same))))
            else:
                assessment["apparent_current"]=False
            assessments.append(assessment)
        success=sum(s["electrum_response"] for s in samples)
        current=sum(a["apparent_current"] for a in assessments)
        classification="responsive and apparently current" if current==args.rounds else (
            "responsive; current tip not established in every sample" if success else "no response from this vantage in bounded samples")
        summary.append(dict(host=host,classification=classification,responsive_samples=success,
            current_samples=current,total_samples=args.rounds,assessments=assessments,
            errors=[dict(round=i+1,phase=s.get("failed_phase"),error=s["error"]) for i,s in enumerate(samples) if "error" in s]))
    report=dict(collected_on=utc(),samples=summary,
        criteria="Apparently current = valid 80-byte reported header within 0..2 blocks of contemporaneous public reference maximum; same-height reference hash must match when available.",
        limits=["Bounded samples from one network vantage, not an uptime SLA or proof of global outage",
                "Headers are self-reported; only their hash is computed locally; no proof-of-work or full-chain validation",
                "Reachability/current tip does not prove historical completeness, backend data integrity, privacy, physical independence or published-code deployment"])
    (args.output/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    lines=["| Endpoint (TLS 50002) | Electrum replies | Apparently current samples | Latest reported height | Header hash matches reference | Disposition |",
           "| --- | ---: | ---: | ---: | --- | --- |"]
    for row in summary:
        latest=row["assessments"][-1]
        height=latest.get("tip",{}).get("height") if latest.get("tip") else "Unknown"
        match=", ".join("Bitails" if "bitails" in url else "WhatsOnChain" for url in latest.get("same_height_reference_hash_matches",[])) or "Not established"
        lines.append(f"| `{row['host']}` | {row['responsive_samples']}/{args.rounds} | {row['current_samples']}/{args.rounds} | {height} | {match} | {row['classification']} |")
    (args.output/"liveness-table.md").write_text("\n".join(lines)+"\n")


if __name__=="__main__":main()
