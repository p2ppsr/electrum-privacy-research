#!/usr/bin/env python3
"""Export only a committed repository payload, with deterministic gzip and SHA-256."""
import argparse,gzip,hashlib,json,subprocess,tarfile,io
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--ref',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
commit=subprocess.check_output(['git','rev-parse',a.ref+'^{commit}'],text=True).strip();raw=subprocess.check_output(['git','archive','--format=tar','--prefix=electrum-privacy-research/',commit])
with tarfile.open(fileobj=io.BytesIO(raw)) as tar:
    names=tar.getnames();assert not any('/.runtime/' in name or name.endswith(('.dmg','.key','.sqlite')) for name in names)
a.output.parent.mkdir(parents=True,exist_ok=True)
with a.output.open('xb') as stream:
    with gzip.GzipFile(filename='',mode='wb',fileobj=stream,mtime=0) as zipped:zipped.write(raw)
print(json.dumps(dict(commit=commit,archive=str(a.output),sha256=hashlib.sha256(a.output.read_bytes()).hexdigest(),bytes=a.output.stat().st_size,entries=len(names),includes_runtime_or_distributions=False),indent=2))
