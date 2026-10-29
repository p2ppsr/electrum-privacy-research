"""TLS matrix client, also executable by the distribution's bundled interpreter."""
import argparse,json,os,socket,ssl,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--private',required=True);p.add_argument('--port',type=int,required=True);p.add_argument('--mode',required=True);p.add_argument('--ca',required=True);a=p.parse_args()
original=os.path.expanduser
os.path.expanduser=lambda value:a.private+'/home'+value[len('~/.electrum-sv'):] if isinstance(value,str) and value.startswith('~/.electrum-sv') else original(value)
sys.path.insert(0,a.source)
from electrumsv.network import SVServer
from electrumsv import verification_utils
request=dict(id=1,method='blockchain.scripthash.get_history',params=['42'*32]);accepted=False;error=None
try:
    if a.mode=='wallet-helper':accepted=verification_utils.electrum_request(request['method'],request['params'],servers={'localhost':{'s':a.port}}) is not None
    else:
        context=SVServer.unique('localhost',a.port,'s')._sslc() if a.mode=='wallet-core' else ssl.create_default_context(cafile=a.ca)
        context.load_verify_locations(cafile=a.ca)
        with socket.create_connection(('127.0.0.1',a.port),timeout=5) as conn:
            with context.wrap_socket(conn,server_hostname='localhost') as stream:
                stream.sendall((json.dumps(request)+'\n').encode());accepted=bool(stream.recv(65536))
except Exception as exc:error=type(exc).__name__+': '+str(exc)
core=SVServer.unique('localhost',1,'s')._sslc()
print('TLS_RESULT '+json.dumps(dict(accepted=accepted,error=error,core_context=dict(verify_mode=int(core.verify_mode),check_hostname=core.check_hostname),python=sys.version,openssl=ssl.OPENSSL_VERSION)))
