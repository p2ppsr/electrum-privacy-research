"""Record source availability and actual default-endpoint self-identification."""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import socket
import ssl
import subprocess
import urllib.error
import urllib.request


def now():
    return datetime.now(timezone.utc).isoformat()


def probe(host):
    result = dict(host=host,port=50002,observed_at=now(),
                  identification_is_self_reported=True, binary_attestation=False)
    try:
        result["dns"] = sorted({r[4][0] for r in socket.getaddrinfo(host,50002,type=socket.SOCK_STREAM)})
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with socket.create_connection((host,50002),timeout=10) as raw:
            with context.wrap_socket(raw,server_hostname=host) as stream:
                stream.settimeout(10)
                result["peer"] = stream.getpeername()
                result["tls"] = stream.version()
                result["certificate_sha256"] = hashlib.sha256(stream.getpeercert(binary_form=True)).hexdigest()
                result["certificate_validation"] = False
                file = stream.makefile("rwb")
                for i,(method,params) in enumerate([
                    ("server.version",["controlled-privacy-research",["1.4","1.4.2"]]),
                    ("server.features",[]),("server.banner",[])]):
                    req = dict(jsonrpc="2.0",id=i+1,method=method,params=params)
                    file.write((json.dumps(req)+"\n").encode()); file.flush()
                    result[method] = json.loads(file.readline())
    except Exception as exc:
        result["error"] = repr(exc)
    return result


def command(args):
    result = subprocess.run(args,text=True,capture_output=True)
    return dict(command=args,exit_code=result.returncode,stdout=result.stdout,stderr=result.stderr,at=now())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--source",type=Path,required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    with concurrent.futures.ThreadPoolExecutor() as ex:
        probes = list(ex.map(probe,["sv.electrumr.sv","sv2.electrumr.sv"]))
    (args.output/"default-server-probes.json").write_text(json.dumps(probes,indent=2)+"\n")
    queries = [
        ["gh","api","repos/KeyvanJS/ElectrumR"],
        ["gh","api","repos/KeyvanJS/ElectrumR/releases"],
        ["gh","api","users/KeyvanJS/repos?per_page=100","--jq","[.[] | {full_name,updated_at}]"],
        ["gh","search","repos","ElectrumR","--limit","50","--json","fullName,description,url"],
        ["gh","search","code",'"ElectrumR" "SessionManager"',"--limit","30","--json","repository,path"],
        ["git","-C",str(args.source),"rev-parse","HEAD"],
        ["git","-C",str(args.source),"status","--porcelain"],
    ]
    (args.output/"source-discovery.json").write_text(json.dumps([command(q) for q in queries],indent=2)+"\n")
    # Only record links and hashes of site pages; avoid republishing site prose.
    pages = []
    import certifi
    import re
    for url in ["https://electrumr.io/index.html","https://electrumr.io/docs.html"]:
        row = dict(url=url,at=now())
        try:
            with urllib.request.urlopen(url,timeout=20,context=ssl.create_default_context(cafile=certifi.where())) as response:
                data = response.read()
                row.update(http_status=response.status,sha256=hashlib.sha256(data).hexdigest(),
                           github_links=sorted(set(re.findall(r'https://github.com/[^\s"<>]+',data.decode()))))
        except Exception as exc:
            row["error"] = repr(exc)
        pages.append(row)
    (args.output/"official-source-links.json").write_text(json.dumps(pages,indent=2)+"\n")


if __name__ == "__main__":
    main()
