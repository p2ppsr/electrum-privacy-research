"""Create or verify the public repository payload's SHA-256 inventory."""
import argparse,hashlib,json,subprocess
from pathlib import Path
MANIFEST=Path('evidence/SHA256SUMS.json')
def facts(path):
    raw=path.read_bytes();return dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    if a.check:
        rows=json.loads(MANIFEST.read_text())
        for name,expected in rows.items():
            path=Path(name);assert not path.is_absolute() and '..' not in path.parts and not path.is_symlink();assert facts(path)==expected,name
        print('Manifest: PASS ('+str(len(rows))+' files)')
    else:
        names=sorted(set(subprocess.check_output(['git','ls-files','-c','-o','--exclude-standard','-z']).decode().split('\0'))-{str(MANIFEST),''})
        rows={name:facts(Path(name)) for name in names if Path(name).is_file()};MANIFEST.write_text(json.dumps(rows,indent=2)+'\n');print('Manifest written: '+str(len(rows))+' files')
if __name__=='__main__':main()
