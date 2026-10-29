"""Generate and check the versioned claim-to-evidence table."""
import argparse,json
from pathlib import Path

def render(value):
    rows=['# Claim-to-evidence ledger','','Updated '+value['updated_on']+'. Status: **'+value['publication_status']+'**. Classifications describe support, not confidence that an operator behaves ethically. Historical failures remain evidence.','','| Claim | Classification and scope | Evidence | Limits / next check |','| --- | --- | --- | --- |']
    ids=set()
    for row in value['claims']:
        assert row['id'] not in ids;ids.add(row['id'])
        for path in row['evidence']:assert Path(path).exists(),path
        cell=lambda s:s.replace('|','\\|').replace('\n',' ')
        links='; '.join('['+p+']('+p+')' for p in row['evidence'])
        rows.append('| **'+row['id']+'** '+cell(row['claim'])+' | '+cell(row['classification']+' — '+row['scope'])+' | '+links+' | '+cell(row['limits']+' Next: '+row['next_check'])+' |')
    return '\n'.join(rows)+'\n'
def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();text=render(json.loads(Path('claims.json').read_text()))
    if a.check:assert Path('CLAIMS.md').read_text()==text,'claim table is stale'
    else:Path('CLAIMS.md').write_text(text)
    print('Claim ledger: PASS')
if __name__=='__main__':main()
