"""Run vendor-bundled entrypoint with isolated home-path resolution and audit metadata.

No vendor module is edited. Path.home and the legacy ~/.electrum-sv expansion
resolve to disposable state because bundled main.py writes there before -D.
This filesystem control and explicit -D are experimental deviations.
"""
import json
import os
from pathlib import Path
import runpy
import sys
import time

bundle=Path(sys.argv[1]).resolve();state=Path(sys.argv[2]).resolve();output=Path(sys.argv[3]).resolve()
arguments=sys.argv[4:];state.mkdir(parents=True,exist_ok=True)
original_home=Path.home()
blocked_prefixes=[str(original_home/name) for name in ['.electrum-sv','.electrumsv','.bitcoin']]
private_home=state/'private-home';private_home.mkdir(exist_ok=True)
Path.home=classmethod(lambda cls:private_home)
original_expand=os.path.expanduser
os.path.expanduser=lambda value:str(private_home)+value[1:] if isinstance(value,str) and value.startswith('~/.electrum') else original_expand(value)
audit=(output/'socket-audit.jsonl').open('a',buffering=1)
def observe(event,args):
    if event in ('open','os.listdir','os.scandir','os.mkdir','os.remove','os.rmdir') and args and isinstance(args[0],(str,bytes)):
        candidate=os.path.abspath(os.fsdecode(args[0]))
        if any(candidate==prefix or candidate.startswith(prefix+'/') for prefix in blocked_prefixes):raise PermissionError('research audit guard blocks existing wallet/node directory')
    if event in ('socket.connect','socket.getaddrinfo'):
        values=list(args[1:]) if event=='socket.connect' else list(args)
        audit.write(json.dumps(dict(time_ns=time.time_ns(),event=event,values=values),default=str)+'\n')
sys.addaudithook(observe)
if '--observe-rpc' in arguments:
    arguments.remove('--observe-rpc')
    import ssl,threading
    sys.path.insert(0,str(bundle/'Contents/usr/lib/python3.9/site-packages'))
    from electrumsv.network import SVSession
    rpcfile=(output/'gui-rpc-events.jsonl').open('a',buffering=1);lock=threading.Lock()
    def record(**fields):
        with lock:rpcfile.write(json.dumps(dict(time_ns=time.time_ns(),**fields),default=str)+'\n')
    original_request=SVSession.send_request
    async def observed(session,method,args=(),*values,**kw):
        fields=dict(path='core',host=session.server.host,method=method,params=args)
        record(event='rpc_attempt',**fields)
        try:result=await original_request(session,method,args,*values,**kw)
        except BaseException as exc:record(event='rpc_error',error=type(exc).__name__,**fields);raise
        record(event='rpc_completed',**fields);return result
    SVSession.send_request=observed
    original_sendall=ssl.SSLSocket.sendall
    def sent(stream,data,*values,**kw):
        result=original_sendall(stream,data,*values,**kw)
        try:message=json.loads(bytes(data))
        except (ValueError,UnicodeDecodeError):return result
        if isinstance(message,dict) and 'method' in message:record(event='helper_tls_send_completed',path='helper',host=stream.server_hostname,method=message['method'],params=message.get('params',[]))
        return result
    ssl.SSLSocket.sendall=sent
sys.argv=[str(bundle/'Contents/MacOS/ElectrumSV.py'),'-D',str(state/'data'),*arguments]
runpy.run_path(sys.argv[0],run_name='__main__')
