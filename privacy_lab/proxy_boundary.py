"""Exercise core SOCKS connector and helper routing against controlled TLS peers."""
import argparse,asyncio,json,os,shutil,ssl,subprocess,sys,tempfile
from pathlib import Path
async def run(a):
    a.output.mkdir(parents=True,exist_ok=False);Path('.runtime').mkdir(exist_ok=True);private=Path(tempfile.mkdtemp(prefix='proxy-',dir='.runtime'))
    old=os.path.expanduser;os.path.expanduser=lambda s:str(private/'home')+s[len('~/.electrum-sv'):] if isinstance(s,str) and s.startswith('~/.electrum-sv') else old(s)
    sys.path.insert(0,str(a.source))
    from electrumsv.network import SVServer,SVProxy
    from electrumsv import verification_utils
    from aiorpcx import RPCSession
    subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-days','1','-subj','/CN=untrusted-proxy-test.invalid','-keyout',str(private/'key'),'-out',str(private/'cert')],check=True,capture_output=True)
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.load_cert_chain(private/'cert',private/'key')
    requests=[];proxy_connects=[]
    async def endpoint(r,w):
        try:
            while line:=await r.readline():
                q=json.loads(line);requests.append(q);w.write((json.dumps(dict(jsonrpc='2.0',id=q['id'],result=[]))+'\n').encode());await w.drain()
        finally:w.close();await w.wait_closed()
    tls=await asyncio.start_server(endpoint,'127.0.0.1',0,ssl=context);target=tls.sockets[0].getsockname()[1]
    async def proxy(r,w):
        backend=None
        try:
            ver,count=await r.readexactly(2);assert ver==5;await r.readexactly(count);w.write(b'\x05\x00');await w.drain()
            ver,cmd,_,kind=await r.readexactly(4);assert cmd==1
            if kind==1:host='.'.join(str(v) for v in await r.readexactly(4))
            elif kind==3:host=(await r.readexactly((await r.readexactly(1))[0])).decode()
            else:raise ValueError(kind)
            port=int.from_bytes(await r.readexactly(2),'big');proxy_connects.append(dict(host=host,port=port))
            assert host in ('localhost','127.0.0.1') and port==target
            br,backend=await asyncio.open_connection('127.0.0.1',port);w.write(b'\x05\x00\x00\x01\x7f\x00\x00\x01\x00\x00');await w.drain()
            async def pump(reader,writer):
                while data:=await reader.read(65536):writer.write(data);await writer.drain()
            tasks=[asyncio.create_task(pump(r,backend)),asyncio.create_task(pump(br,w))];await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
            for task in tasks:task.cancel()
            await asyncio.gather(*tasks,return_exceptions=True)
        finally:
            w.close()
            if backend:backend.close()
    socks=await asyncio.start_server(proxy,'127.0.0.1',0);port=socks.sockets[0].getsockname()[1]
    try:
        async with SVServer.unique('localhost',target,'s')._connector(RPCSession,SVProxy(f'127.0.0.1:{port}','SOCKS5',None)) as session:
            await session.send_request('blockchain.scripthash.get_history',['ab'*32])
        before=len(proxy_connects)
        answer=await asyncio.to_thread(verification_utils.electrum_request,'blockchain.scripthash.get_history',['cd'*32],{'127.0.0.1':{'s':target}})
        result=dict(status='PASS',core_proxy_connects=before,helper_additional_proxy_connects=len(proxy_connects)-before,operator_requests=requests,proxy_requests=proxy_connects,helper_answer=answer,scope='Actual core connector supplied custom SOCKS5 proxy; actual helper called separately with its normal independent routing. No GUI proxy preference qualification or Tor anonymity claim.')
        assert before==1 and len(proxy_connects)==1 and len(requests)==2 and answer is not None
        (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    finally:
        tls.close();socks.close();await tls.wait_closed();await socks.wait_closed();shutil.rmtree(private)
def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);asyncio.run(run(p.parse_args()))
if __name__=='__main__':main()
