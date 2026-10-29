"""Consensus-valid BSV local-chain shop, then permanent departure from observer A."""
import argparse
import asyncio
from datetime import datetime,timezone
import json
from pathlib import Path
import shutil
import ssl
import subprocess
import sys
import time

from .correlation import analyze
from .dossier import address,parse_tx,load_journal
from .node_indexer import NodeRPC,NodeIndexer
from .tap import Journal,Tap


def now():return datetime.now(timezone.utc).isoformat()


async def wait_file(path,process=None,timeout=90):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if path.exists():return json.loads(path.read_text())
        if process and process.returncode is not None:raise RuntimeError(f'worker exited {process.returncode} before {path.name}')
        await asyncio.sleep(.1)
    raise TimeoutError(path.name)


async def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    private=Path('.runtime')/args.output.name;private.mkdir(parents=True,exist_ok=False)
    rpc=NodeRPC();indexer=NodeIndexer(rpc,args.output)
    journals=[];taps=[];workers=[];commands={};events=[]
    def note(phase,**details):
        row=dict(utc=now(),phase=phase,**details);events.append(row)
        (args.output/'phases.json').write_text(json.dumps(events,indent=2)+'\n')
    async def command(index,action,**values):
        state,process=workers[index];number=commands.get(index,0)+1;commands[index]=number
        path=state/f'command-{number:03d}.json';temp=path.with_suffix('.tmp')
        temp.write_text(json.dumps(dict(action=action,**values)));temp.replace(path)
        result=await wait_file(state/f'result-{number:03d}.json',process,60)
        assert result['status']=='PASS',result
        return result
    async def wait_balance(index,value,txids=()):
        deadline=time.monotonic()+60
        while time.monotonic()<deadline:
            result=await command(index,'status',txids=list(txids))
            if result['balance_sats']==value and all(p['height']>0 and p['proof_stored'] for p in result['proofs']):return result
            await asyncio.sleep(.5)
        raise TimeoutError(('wallet state',index,value,result))
    async def mine():
        miner=(Path('.runtime/valid-chain/miner-address')).read_text().strip()
        hashes=await asyncio.to_thread(rpc,'generatetoaddress',1,miner)
        await indexer.refresh();return hashes
    try:
        assert rpc('getblockchaininfo')['chain']=='regtest' and rpc('getconnectioncount')==0
        backend=await indexer.start()
        (private/'headers').write_bytes(bytes.fromhex(''.join(indexer.headers)))
        for role in ['A','B']:
            cert,key=private/f'{role}.pem',private/f'{role}.key'
            subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj',f'/CN=controlled-observer-{role}.test','-keyout',str(key),'-out',str(cert)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(cert,key)
            journal=Journal(args.output/f'capture-{role}.jsonl');journals.append(journal)
            tap=Tap(journal,('127.0.0.1',backend,False),context);taps.append(tap);await tap.start()
        ports=[tap.server.sockets[0].getsockname()[1] for tap in taps]
        note('node-and-observers-ready',node_version=rpc('getnetworkinfo')['subversion'],node_height=len(indexer.headers)-1,observer_ports=ports)
        truth=[]
        for i in range(3):
            state=private/f'wallet-{i}'
            log=(args.output/f'wallet-{i}.log').open('w')
            process=await asyncio.create_subprocess_exec(sys.executable,'-m','privacy_lab.valid_wallet_worker','--source',str(args.source),'--state',str(state),'--headers',str(private/'headers'),'--port',str(ports[0]),stdout=log,stderr=log)
            workers.append((state,process));await wait_file(state/'ready.json',process)
            truth.append({tuple(r['derivation']):r['script'] for r in json.loads((state/'truth.json').read_text())})
        def node_address(script):return address(bytes.fromhex(script),testnet=True)
        checkout=dict(label='Controlled valid-chain shop',address=address(bytes.fromhex(truth[2][(0,0)])),context='simulated checkout address; raw locking script is identical across address encodings')
        (args.output/'checkout.json').write_text(json.dumps(checkout,indent=2)+'\n')
        note('three-wallets-disclosed-before-payments',initial_identifiers_per_wallet=40,checkout_address_count=1)
        fund_a=rpc('sendtoaddress',node_address(truth[0][(0,0)]),0.08)
        fund_b=rpc('sendtoaddress',node_address(truth[1][(0,0)]),0.07)
        await mine()
        await wait_balance(0,8_000_000,[fund_a]);await wait_balance(1,7_000_000,[fund_b])
        note('real-funding-confirmed',funding_txids=[fund_a,fund_b])
        p1=await command(0,'pay',input_sats=8_000_000,script=truth[2][(0,0)],value_sats=2_500_000)
        p2=await command(1,'pay',input_sats=7_000_000,script=truth[2][(0,1)],value_sats=4_000_000)
        unknown=rpc('sendtoaddress',node_address(truth[2][(0,2)]),0.0125)
        await mine()
        incoming=[p1['txid'],p2['txid'],unknown]
        shop_before=await wait_balance(2,7_750_000,incoming)
        note('three-fresh-shop-addresses-paid-and-confirmed',incoming=incoming,shop=shop_before)
        for i in [0,1]:await command(i,'stop');await asyncio.wait_for(workers[i][1].wait(),30)
        switched=await command(2,'switch',port=ports[1]);await asyncio.sleep(1)
        journals[0].record(event='migration_complete',utc_note=now(),helper_and_main_moved=True)
        migration_sequence=journals[0].sequence
        note('full-departure-from-observer-A',migration_sequence=migration_sequence,main_and_helper_move=switched)
        later=rpc('sendtoaddress',node_address(truth[2][(0,10)]),0.017)
        outside_script='76a914'+'91'*20+'88ac'
        outgoing=await command(2,'pay',input_sats=2_500_000,script=outside_script,value_sats=1_100_000)
        await mine()
        shop_after=await wait_balance(2,8_349_000,incoming+[later,outgoing['txid']])
        note('post-departure-receipt-spend-and-confirmations',later_receipt=later,outgoing=outgoing['txid'],shop=shop_after)
        await command(2,'stop');await asyncio.wait_for(workers[2][1].wait(),30)
        for tap in taps:await tap.stop()
        taps=[]
        for j in journals:j.close()
        await indexer.stop();indexer=None
        rows=load_journal(args.output/'capture-A.jsonl')
        assert not any(r.get('direction')=='request' for r in rows if r['sequence']>migration_sequence),'old observer got new client request after departure'
        records=json.loads((args.output/'node-transactions.json').read_text())
        ledger=dict(mode='Actual consensus-valid local Bitcoin SV regtest ledger',generated_after_wallet_exit=False,raw_transactions=list(records['transactions'].values()))
        (args.output/'ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
        result=analyze(args.output/'capture-A.jsonl',args.output/'ledger.json',args.output/'checkout.json')
        result.update(mode='Actual wallet signing and real isolated BSV regtest confirmations; research adapter, not ElectrumR',
                      limits=['Interest collections do not prove legal ownership; unrelated/mixed inputs remain unattributed','Network constants and header loading adapted for regtest; not packaged regtest qualification','No real-chain funds; no production users; node has zero peers'],
                      old_observer_requests_after_departure=0,node_verifychain=rpc('verifychain',4,0),node_peers=rpc('getconnectioncount'),
                      shop_wallet_reported_balance_sats=shop_after['balance_sats'],migration_sequence=migration_sequence)
        assert result['shop_gross_receipts_sats']==9_450_000 and result['shop_remaining_observed_sats']==8_349_000
        assert result['node_verifychain'] is True and result['node_peers']==0
        (args.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');note('PASS',gross_sats=9_450_000,remaining_sats=8_349_000)
        print(json.dumps({k:v for k,v in result.items() if k not in ['edges','checkout','limits']},indent=2))
    finally:
        for _,process in workers:
            if process.returncode is None:process.terminate();await process.wait()
        for tap in taps:await tap.stop()
        if indexer:await indexer.stop()
        for j in journals:
            if not j.file.closed:j.close()
        shutil.rmtree(private)
        (args.output/'cleanup.json').write_text(json.dumps(dict(disposable_wallet_state_removed=not private.exists(),worker_exit_codes=[p.returncode for _,p in workers]),indent=2)+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    asyncio.run(run(p.parse_args()))


if __name__=='__main__':main()
