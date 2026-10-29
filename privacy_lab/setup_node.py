"""Create only the named isolated research node; refuse to overwrite existing state."""
import argparse,json,secrets,subprocess,time
from pathlib import Path
from .node_indexer import NodeRPC
from .replay_chain import IMAGE

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    private=Path('.runtime/valid-chain');private.mkdir(parents=True,exist_ok=False);data=private/'node';data.mkdir()
    network='electrum-privacy-lab-20261029';container='electrum-privacy-bsv-20261029'
    (data/'bitcoin.conf').write_text('regtest=1\nserver=1\nlisten=0\ndnsseed=0\ndiscover=0\nconnect=0\ntxindex=1\nrpcuser=privacy-lab\nrpcpassword='+secrets.token_hex(32)+'\nexcessiveblocksize=100000000\nmaxstackmemoryusageconsensus=10000000\nmaxstackmemoryusagepolicy=10000000\nminminingtxfee=0.000005\nblockassembler=LEGACY\npar=1\nmaxparallelblocks=1\nmaxparallelblocksperpeer=1\n')
    subprocess.run(['docker','network','create','--internal','--label','p2ppsr.electrum-privacy=research',network],check=True,capture_output=True)
    subprocess.run(['docker','run','-d','--name',container,'--label','p2ppsr.electrum-privacy=research','--network',network,'--cpus','2','--memory','2g','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges','-v',str(data.resolve())+':/data','--entrypoint','bitcoind',IMAGE,'-datadir=/data','-printtoconsole=1'],check=True,capture_output=True)
    rpc=NodeRPC()
    for _ in range(100):
        try:rpc('getblockchaininfo');break
        except RuntimeError:time.sleep(.2)
    else:raise TimeoutError('node RPC readiness')
    miner=rpc('getnewaddress');(private/'miner-address').write_text(miner+'\n');hashes=rpc('generatetoaddress',201,miner)
    result=dict(image=IMAGE,container=container,internal_network=network,mined_blocks=len(hashes),height=rpc('getblockcount'),peers=rpc('getconnectioncount'),verifychain=rpc('verifychain',4,0))
    assert result['peers']==0 and result['verifychain'];(a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
