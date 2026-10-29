"""Offline checks for the package, certificate, valid-chain and publication evidence."""
import hashlib,json,re
from pathlib import Path
from .correlation import analyze
from .dossier import load_journal
from .claims import render

def read(path):return json.loads(Path(path).read_text())
def dh(raw):return hashlib.sha256(hashlib.sha256(raw).digest()).digest()
def merkle(raws):
    level=[dh(bytes.fromhex(raw)) for raw in raws]
    while len(level)>1:
        if len(level)%2:level.append(level[-1])
        level=[dh(level[i]+level[i+1]) for i in range(0,len(level),2)]
    return level[0]
def main():
    root=Path('evidence/valid-chain-attempt-05');result=read(root/'result.json');rows=load_journal(root/'capture-A.jsonl')
    assert not any(r.get('direction')=='request' and r['sequence']>result['migration_sequence'] for r in rows)
    again=analyze(root/'capture-A.jsonl',root/'ledger.json',root/'checkout.json')
    for key,value in [('shop_gross_receipts_sats',9450000),('shop_remaining_observed_sats',8349000)]:assert again[key]==result[key]==value
    assert result['node_verifychain'] and result['node_peers']==0 and result['shop_wallet_reported_balance_sats']==8349000
    assert read(root/'cleanup.json')['worker_exit_codes']==[0,0,0]
    records=read(root/'node-transactions.json');blocks=read(root/'node-blocks.json');previous=None
    for height,block in enumerate(blocks):
        assert block['height']==height
        raw=bytes.fromhex(block['raw']);header=raw[:80];assert dh(header)[::-1].hex()==block['blockhash']
        if previous:assert header[4:36]==bytes.fromhex(previous)[::-1]
        bits=int.from_bytes(header[72:76],'little');target=(bits&0x7fffff)<<(8*((bits>>24)-3));assert int.from_bytes(dh(header),'little')<=target
        txs=[records['transactions'][txid] for txid in block['txids']]
        assert all(dh(bytes.fromhex(tx))[::-1].hex()==txid for tx,txid in zip(txs,block['txids']))
        assert merkle(txs)==header[36:68]
        count=len(txs);prefix=bytes([count]) if count<253 else b'\xfd'+count.to_bytes(2,'little')
        assert raw==header+prefix+bytes.fromhex(''.join(txs));previous=block['blockhash']
    replay=read('evidence/chain-clean-replay-attempt-03/result.json');assert replay['status']=='PASS' and replay['verifychain'] and replay['peers']==0 and replay['bestblockhash']==previous
    assert [c['rejection'] for c in replay['negative_controls']]==['bad-txnmrklroot','blk-bad-inputs']
    for path in ['evidence/tls-source-20261029-attempt-03/result.json','evidence/tls-packaged-20261029-attempt-04/result.json']:
        tls=read(path);assert tls['core_context']==dict(verify_mode=0,check_hostname=False);assert len(tls['rows'])==18
        for row in tls['rows']:
            expected=row['case']!='plaintext-endpoint' and (row['client']!='verified-control' or row['case']=='trusted-matching')
            assert row['accepted']==expected,(path,row['case'],row['client'])
            assert bool(row['operator_received'])==expected
    gui=read('evidence/packaged-gui-attempt-01/result.json');assert gui['status']=='PASS' and gui['unique_scripts']==40 and gui['network_settings_supplied']==[]
    assert len(gui['core_hosts'])==7 and len(gui['helper_hosts'])==7 and gui['main_hosts']==['sv2.electrumr.sv']
    package=read('evidence/packaged-wallet-20261029/python-module-comparison.json');assert len(package)==145 and all(row['ast_identical'] for row in package)
    proxy=read('evidence/proxy-boundary-attempt-04/result.json');assert proxy['core_proxy_connects']==1 and proxy['helper_additional_proxy_connects']==0 and len(proxy['operator_requests'])==2
    assert Path('CLAIMS.md').read_text()==render(read('claims.json'))
    count=0
    for file in Path('.').glob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',file.read_text()):
            if '://' in target or target.startswith('#'):continue
            relative=target.split('#')[0]
            if relative:assert (file.parent/relative).exists(),(file,target)
            count+=1
    print(json.dumps(dict(status='PASS',retained_blocks=len(blocks),certificate_cases=36,shared_package_modules=145,checked_local_links=count,scope='Offline consistency, cryptographic hashes/PoW/Merkle and capture reconstruction; actual consensus replay is separately retained')))
if __name__=='__main__':main()
