"""Actual wallet/core worker with explicit isolated regtest network parameters.

The release comments out its regtest class and hardcodes mainnet in its header
loader. This harness supplies a research network class and header-loader adapter;
it does not claim an unmodified packaged regtest feature or replace consensus checks.
"""
import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import threading
import time


def write(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--state',type=Path,required=True)
    p.add_argument('--headers',type=Path,required=True);p.add_argument('--port',type=int,required=True)
    a=p.parse_args();a.state.mkdir(parents=True,exist_ok=False)
    old_expand=os.path.expanduser
    os.path.expanduser=lambda s:str(a.state/'legacy-home')+s[len('~/.electrum-sv'):] if isinstance(s,str) and s.startswith('~/.electrum-sv') else old_expand(s)
    sys.path.insert(0,str(a.source));logging.basicConfig(level=logging.WARNING)
    from bitcoinx import BitcoinRegtest,Script,hash_to_hex_str
    from electrumsv.simple_config import SimpleConfig
    from electrumsv.app_state import AppStateProxy,DefaultApp
    from electrumsv.headers_storage import PersistentHeaders
    from electrumsv.storage import WalletStorage
    from electrumsv.wallet import Wallet
    from electrumsv import keystore,verification_utils
    from electrumsv.mnemonic import generate_bip39_seed
    from electrumsv.network import Network,SVServer
    from electrumsv.networks import Net,SVMainnet
    from electrumsv.keystore import bip44_derivation_cointype
    from electrumsv.transaction import XTxOutput
    from electrumsv.bitcoin import scripthash_hex

    class ResearchRegtest(SVMainnet):
        NAME='regtest';COIN=BitcoinRegtest;ADDRTYPE_P2PKH=111;ADDRTYPE_P2SH=196;WIF_PREFIX=0xef;BIP44_COIN_TYPE=1
        GENESIS=hash_to_hex_str(__import__('bitcoinx').header_hash(BitcoinRegtest.genesis_header))
        CHECKPOINT=dict(raw_header=BitcoinRegtest.genesis_header,height=0,prev_work=0)
        VERIFICATION_BLOCK_MERKLE_ROOT=None;TWENTY_MINUTE_RULE=False
    Net.set_to(ResearchRegtest)
    verification_utils.SERVERS={'127.0.0.1':{'s':a.port}}
    def local_only(event,values):
        if event=='socket.connect' and isinstance(values[1],tuple) and values[1][0] not in ('127.0.0.1','::1'):
            raise PermissionError('valid-chain wallet blocks non-loopback socket connections')
    sys.addaudithook(local_only)
    config=SimpleConfig(dict(electrum_sv_path=str(a.state/'config'),oneserver=True,auto_connect=False))
    config.set_key('server',f'127.0.0.1:{a.port}:s',True)
    app=AppStateProxy(config,'cmdline');app.set_app(DefaultApp())
    app.app.run_in_thread=lambda fn,*args:threading.Thread(target=fn,args=args,daemon=True).start()
    headers_path=Path(config.file_path('headers'));shutil.copyfile(a.headers,headers_path)
    def load_regtest_headers():
        app.headers=PersistentHeaders(network=BitcoinRegtest,file_path=str(headers_path))
    app.read_headers=load_regtest_headers
    app.async_.__enter__();wallet=network=None;password='disposable-regtest-wallet'
    try:
        storage=WalletStorage.create(str(a.state/'wallet'),password);wallet=Wallet(storage)
        ks=keystore.from_bip39_seed(generate_bip39_seed(12),'',bip44_derivation_cointype(1,0));ks.update_password(password)
        account=wallet.create_account_from_keystore(ks);account.synchronize()
        truth=[dict(key=k,derivation=list(account._keypath[k]),script=bytes(script).hex(),scripthash=scripthash_hex(script)) for k in account.existing_active_keys() for _,script in account.get_possible_scripts_for_id(k)]
        write(a.state/'truth.json',truth)
        network=Network();wallet.start(network)
        deadline=time.monotonic()+90
        while time.monotonic()<deadline and account.response_count<40:time.sleep(.1)
        assert account.response_count>=40,'initial subscriptions incomplete'
        write(a.state/'ready.json',dict(initial_scripts=len(truth),responses=account.response_count))
        handled=set();stop=False
        while not stop:
            for command_path in sorted(a.state.glob('command-*.json')):
                if command_path.name in handled:continue
                command=json.loads(command_path.read_text());result={}
                try:
                    kind=command['action']
                    if kind=='pay':
                        coins=[coin for coin in account.get_utxos() if coin.value==command['input_sats']]
                        assert len(coins)==1,('expected one controlled coin',len(coins))
                        tx=account.make_unsigned_transaction(coins,[XTxOutput(command['value_sats'],Script(bytes.fromhex(command['script'])))],config,fixed_fee=1000)
                        account.sign_transaction(tx,password);assert tx.is_complete()
                        txid=network.broadcast_transaction_and_wait(tx)
                        result=dict(txid=txid,raw=tx.to_bytes().hex())
                    elif kind=='switch':
                        verification_utils.SERVERS={'127.0.0.1':{'s':command['port']}}
                        replacement=SVServer.unique('127.0.0.1',command['port'],'s')
                        SVServer.all_servers={('127.0.0.1',command['port'],'s'):replacement}
                        network.set_server(replacement,False)
                        deadline=time.monotonic()+30
                        while time.monotonic()<deadline:
                            session=network.main_session()
                            if session and session.server.port==command['port'] and network.is_connected():break
                            time.sleep(.1)
                        assert network.main_session().server.port==command['port']
                        result=dict(server_port=command['port'],helper_explicitly_moved=True)
                    elif kind=='status':
                        proofs=[]
                        for txid in command.get('txids',[]):
                            txhash=bytes.fromhex(txid)[::-1]
                            try:height,confirmations,_=wallet.get_tx_height(txhash)
                            except AssertionError:height,confirmations=0,0
                            proof=wallet.get_transaction_proof(txhash)
                            proofs.append(dict(txid=txid,height=height,confirmations=confirmations,proof_stored=proof is not None))
                        result=dict(balance_sats=sum(c.value for c in account.get_utxos()),responses=account.response_count,
                                    main_port=network.main_server.port,proofs=proofs,
                                    active_script_count=len(list(account.existing_active_keys())))
                    elif kind=='stop':stop=True;result=dict(stopped=True)
                    else:raise ValueError(kind)
                    result['status']='PASS'
                except Exception as exc:result=dict(status='ERROR',error=repr(exc))
                write(a.state/('result-'+command_path.name[len('command-'):]),result);handled.add(command_path.name)
            time.sleep(.1)
    finally:
        if wallet and not wallet._stopped:wallet.stop()
        if network:
            async def quiesce():
                await network.shutdown_wait();await asyncio.sleep(.2)
                tasks=[t for t in asyncio.all_tasks() if t is not asyncio.current_task() and getattr(t.get_coro(),'__qualname__','')!='ASync._wait_until_stopped']
                for task in tasks:task.cancel()
                await asyncio.gather(*tasks,return_exceptions=True)
            app.async_.spawn_and_wait(quiesce,timeout=15)
        app.async_.__exit__(None,None,None)


if __name__=='__main__':main()
