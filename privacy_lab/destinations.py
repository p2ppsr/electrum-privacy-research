"""Extract bundled destinations from pinned source and record current DNS/metadata."""
import argparse
import ast
import concurrent.futures
from datetime import datetime, timezone
import json
from pathlib import Path
import ssl
import subprocess
import warnings

import dns.resolver

from .provenance import probe


def assignment(tree, name):
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value), node.lineno
    raise ValueError("assignment not found: " + name)


def resolve(host):
    result = dict(host=host, observed_at=datetime.now(timezone.utc).isoformat(),
                  addresses=[], answers=[], dnssec_authenticated=False)
    for record_type in ("A", "AAAA"):
        try:
            answer = dns.resolver.resolve(host, record_type, lifetime=5, raise_on_no_answer=False)
            for rrset in answer.response.answer:
                result["answers"].append(dict(name=str(rrset.name), ttl=rrset.ttl,
                    type=dns.rdatatype.to_text(rrset.rdtype), records=[r.to_text() for r in rrset]))
            if answer.rrset:
                result["addresses"] += [r.to_text() for r in answer]
        except Exception as exc:
            result.setdefault("errors", []).append(dict(type=record_type, error=repr(exc)))
    result["addresses"] = sorted(set(result["addresses"]))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    network_source = (args.source/"electrumsv/network.py").read_text()
    verification_source = (args.source/"electrumsv/verification_utils.py").read_text()
    priority, priority_line = assignment(ast.parse(network_source), "priority_servers")
    helper, helper_line = assignment(ast.parse(verification_source), "SERVERS")
    fallback = json.loads((args.source/"electrumsv/data/servers.json").read_text())
    priorities = {host: ports for host, ports in priority}
    hosts = sorted(set(priorities) | set(helper))
    with concurrent.futures.ThreadPoolExecutor(max_workers=9) as executor:
        dns_rows = list(executor.map(resolve, hosts))
        metadata = list(executor.map(probe, hosts))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    source = dict(
        wallet_commit=subprocess.check_output(["git","-C",str(args.source),"rev-parse","HEAD"], text=True).strip(),
        priority_pool=dict(source="electrumsv/network.py",line=priority_line,entries=priority),
        verification_pool=dict(source="electrumsv/verification_utils.py",line=helper_line,entries=helper),
        fallback_json=dict(source="electrumsv/data/servers.json",entries=fallback,
            note="Fallback import is conditional on fewer than five known server objects after priority insertion. Two literal keys have trailing apostrophes; do not silently correct them."),
        excluded_commented_hosts=["electrum.api.sv","neptune.api.sv","alpha-esv.api.sv"],
        core_ssl_context_runtime=dict(constructor="ssl.SSLContext(ssl.PROTOCOL_TLS)",
            verify_mode=context.verify_mode.name,check_hostname=context.check_hostname),
        scope="Nine literal active mainnet destinations. Peer-discovered, cached, custom, testnet and browser destinations are separate; this is not an exhaustive egress allowlist.")
    (args.output/"source-destinations.json").write_text(json.dumps(source,indent=2)+"\n")
    (args.output/"dns.json").write_text(json.dumps(dns_rows,indent=2)+"\n")
    (args.output/"endpoint-metadata.json").write_text(json.dumps(metadata,indent=2)+"\n")
    lines = ["| Hostname | Core priority pool | Verification helper | Port/transport | DNS addresses observed | Advertised server version |",
             "| --- | --- | --- | --- | --- | --- |"]
    for host, dns_row, meta in zip(hosts,dns_rows,metadata):
        version = meta.get("server.version",{}).get("result")
        identity = version[0] if isinstance(version,list) and version else "No successful identification; see raw error"
        addresses = ", ".join(f"`{a}`" for a in dns_row["addresses"]) or "No A/AAAA answer"
        lines.append(f"| `{host}` | {'Yes' if host in priorities else 'No'} | {'Yes' if host in helper else 'No'} | `50002` / TLS | {addresses} | `{identity}` |")
    (args.output/"destinations-table.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(dict(active_literal_destinations=len(hosts),source_commit=source["wallet_commit"],
                         ssl_context=source["core_ssl_context_runtime"]),indent=2))


if __name__ == "__main__":
    main()
