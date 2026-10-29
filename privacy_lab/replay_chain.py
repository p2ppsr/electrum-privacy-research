"""Validate retained raw blocks in a second empty BSV node, with negative controls."""
import argparse,hashlib,json,secrets,shutil,subprocess,time
from pathlib import Path
from .node_indexer import NodeRPC
from bitcoinx import Tx,Script
IMAGE='bitcoinsv/bitcoin-sv@sha256:d96fe4786a00e5fc10bc9e0e76a6006376f9472d4eb74d07e4c1e0d019493d33'
def dh(data):return hashlib.sha256(hashlib.sha256(data).digest()).digest()
def merkle(raws):
    level=[dh(bytes.fromhex(raw)) for raw in raws]
    while len(level)>1:
        if len(level)%2:level.append(level[-1])
        level=[dh(level[i]+level[i+1]) for i in range(0,len(level),2)]
    return level[0]
def mined(header):
    h=bytearray(header);bits=int.from_bytes(h[72:76],'little');target=(bits&0x7fffff) << (8*((bits>>24)-3))
    for nonce in range(2**32):
        h[76:80]=nonce.to_bytes(4,'little')
        if int.from_bytes(dh(h),'little')<=target:return bytes(h)
    raise AssertionError('nonce exhausted')
def count(value):return bytes([value]) if value<253 else b'\xfd'+value.to_bytes(2,'little')
def main():
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    state=Path('.runtime/chain-clean-replay');state.mkdir(exist_ok=False);node='electrum-privacy-replay-20261029'
    (state/'bitcoin.conf').write_text('regtest=1\nserver=1\nlisten=0\ndnsseed=0\ndiscover=0\nconnect=0\nrpcuser=replay\nrpcpassword='+secrets.token_hex(32)+'\nexcessiveblocksize=100000000\nmaxstackmemoryusageconsensus=10000000\nmaxstackmemoryusagepolicy=10000000\nminminingtxfee=0.000005\n')
    records=json.loads((a.evidence/'node-transactions.json').read_text());blocks=json.loads((a.evidence/'node-blocks.json').read_text());phases=json.loads((a.evidence/'phases.json').read_text());outgoing=next(p['outgoing'] for p in phases if p['phase']=='post-departure-receipt-spend-and-confirmations')
    result=dict(image=IMAGE,clean_empty_datadir=True,implementation_independent=False,external_peers_allowed=False,negative_controls=[])
    try:
        subprocess.run(['docker','run','-d','--name',node,'--network','electrum-privacy-lab-20261029','--cpus','1','--memory','1g','--pids-limit','128','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(state.resolve())+':/data','--entrypoint','bitcoind',IMAGE,'-datadir=/data','-printtoconsole=1'],check=True,capture_output=True)
        rpc=NodeRPC(node)
        for _ in range(60):
            try:rpc('getblockchaininfo');break
            except RuntimeError:time.sleep(.2)
        else:raise TimeoutError('fresh node RPC readiness')
        for block in blocks[1:-1]:
            acceptance=rpc('submitblock',block['raw']);assert acceptance in (None,''),(block['height'],acceptance)
        last=blocks[-1];raws=[records['transactions'][txid] for txid in last['txids']]
        header=bytearray(bytes.fromhex(last['raw'][:160]));header[68:72]=(int.from_bytes(header[68:72],'little')+1).to_bytes(4,'little')
        tx=Tx.from_hex(records['transactions'][outgoing]);tx.inputs[0].script_sig=Script(b'\x00');bad=tx.to_bytes().hex();altered=[bad if txid==outgoing else raw for txid,raw in zip(last['txids'],raws)]
        malformed=(mined(header)+count(len(altered))+bytes.fromhex(''.join(altered))).hex();reason=rpc('submitblock',malformed)
        result['negative_controls'].append(dict(case='mutated-transaction-with-invalid-merkle-root',rejection=reason));assert reason and 'mrkl' in reason
        header[36:68]=merkle(altered);bad_signature=(mined(header)+count(len(altered))+bytes.fromhex(''.join(altered))).hex();reason=rpc('submitblock',bad_signature)
        result['negative_controls'].append(dict(case='invalid-signature-with-correct-merkle-root-and-regtest-proof-of-work',rejection=reason));assert reason and ('script' in reason or 'inputs' in reason)
        assert rpc('submitblock',last['raw']) in (None,'')
        result.update(status='PASS',accepted_blocks=len(blocks)-1,height=rpc('getblockcount'),bestblockhash=rpc('getbestblockhash'),verifychain=rpc('verifychain',4,0),peers=rpc('getconnectioncount'))
        assert result['bestblockhash']==last['blockhash'] and result['verifychain'] and result['peers']==0
    finally:
        logs=subprocess.run(['docker','logs',node],text=True,capture_output=True);(a.output/'node.log').write_text(logs.stdout+logs.stderr)
        subprocess.run(['docker','rm','-f',node],capture_output=True);shutil.rmtree(state)
        result['cleanup']=dict(container_removed=True,private_datadir_removed=not state.exists());(a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
