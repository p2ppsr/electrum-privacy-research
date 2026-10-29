"""Local certificate authentication matrix using actual wallet context/helper code."""
import argparse
from datetime import datetime,timedelta,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import ssl
import sys
import subprocess
import tempfile
import threading


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--bundled-app',type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    Path('.runtime').mkdir(exist_ok=True)
    private=Path(tempfile.mkdtemp(prefix='tls-',dir='.runtime'))
    old=os.path.expanduser
    os.path.expanduser=lambda s:str(private/'home')+s[len('~/.electrum-sv'):] if isinstance(s,str) and s.startswith('~/.electrum-sv') else old(s)
    if not a.bundled_app:
        sys.path.insert(0,str(a.source))
        from electrumsv.network import SVServer
        from electrumsv import verification_utils
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes,serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID
    utc=datetime.now(timezone.utc)
    def key():return rsa.generate_private_key(public_exponent=65537,key_size=2048)
    def name(s):return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,s)])
    cakey=key();caname=name('Research local CA')
    ca=x509.CertificateBuilder().subject_name(caname).issuer_name(caname).public_key(cakey.public_key()).serial_number(x509.random_serial_number()).not_valid_before(utc-timedelta(days=2)).not_valid_after(utc+timedelta(days=2)).add_extension(x509.BasicConstraints(ca=True,path_length=None),True).sign(cakey,hashes.SHA256())
    capath=private/'ca.pem';capath.write_bytes(ca.public_bytes(serialization.Encoding.PEM))
    cases=[('trusted-matching',True,'localhost',False),('trusted-wrong-host',True,'wrong.test',False),('untrusted-matching',False,'localhost',False),('untrusted-wrong-host',False,'wrong.test',False),('expired-trusted-matching',True,'localhost',True),('plaintext-endpoint',False,'localhost',False)]
    rows=[]
    try:
        for label,signed,hostname,expired in cases:
            leafkey=key();subject=name(hostname)
            cert=x509.CertificateBuilder().subject_name(subject).issuer_name(caname if signed else subject).public_key(leafkey.public_key()).serial_number(x509.random_serial_number()).not_valid_before(utc-timedelta(days=10)).not_valid_after(utc-timedelta(days=1) if expired else utc+timedelta(days=1)).add_extension(x509.SubjectAlternativeName([x509.DNSName(hostname)]),False).sign(cakey if signed else leafkey,hashes.SHA256())
            certpath=private/'leaf.pem';keypath=private/'leaf.key';certpath.write_bytes(cert.public_bytes(serialization.Encoding.PEM));keypath.write_bytes(leafkey.private_bytes(serialization.Encoding.PEM,serialization.PrivateFormat.PKCS8,serialization.NoEncryption()))
            (a.output/(label+'.pem')).write_bytes(certpath.read_bytes())
            for mode in ['wallet-core','wallet-helper','verified-control']:
                capture=[];errors=[];listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1);listener.settimeout(8);port=listener.getsockname()[1]
                server_context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);server_context.load_cert_chain(certpath,keypath)
                def serve():
                    try:
                        conn,_=listener.accept()
                        if label=='plaintext-endpoint':
                            conn.sendall(b'plaintext is not a TLS endpoint\n');conn.close();return
                        with server_context.wrap_socket(conn,server_side=True) as stream:
                            data=b''
                            while not data.endswith(b'\n'):data+=stream.recv(65536)
                            request=json.loads(data);capture.append(request)
                            stream.sendall((json.dumps(dict(id=request['id'],result=[]))+'\n').encode())
                    except Exception as exc:errors.append(type(exc).__name__+': '+str(exc))
                    finally:listener.close()
                thread=threading.Thread(target=serve,daemon=True);thread.start();accepted=False;error=None
                request=dict(id=1,method='blockchain.scripthash.get_history',params=['42'*32])
                try:
                    if a.bundled_app:
                        env=os.environ.copy();env['PYTHONHOME']=str(a.bundled_app/'Contents/usr');env['DYLD_LIBRARY_PATH']=str(a.bundled_app/'Contents/Frameworks')+':'+str(a.bundled_app/'Contents/usr/lib')
                        run=subprocess.run([str(a.bundled_app/'Contents/usr/bin/python3.9'),str(Path(__file__).with_name('tls_client.py').resolve()),'--source',str(a.source),'--private',str(private.resolve()),'--port',str(port),'--mode',mode,'--ca',str(capath.resolve())],env=env,text=True,capture_output=True,timeout=20)
                        response=json.loads(next(line[len('TLS_RESULT '):] for line in run.stdout.splitlines() if line.startswith('TLS_RESULT ')))
                        accepted=response['accepted'];error=response['error']
                    elif mode=='wallet-helper':
                        result=verification_utils.electrum_request(request['method'],request['params'],servers={'localhost':{'s':port}})
                        accepted=result is not None
                    else:
                        context=SVServer.unique('localhost',port,'s')._sslc() if mode=='wallet-core' else ssl.create_default_context(cafile=str(capath))
                        # Supplying the lab CA makes wrong-host/expiry checks independently testable.
                        context.load_verify_locations(cafile=str(capath))
                        with socket.create_connection(('127.0.0.1',port),timeout=5) as conn:
                            with context.wrap_socket(conn,server_hostname='localhost') as stream:
                                stream.sendall((json.dumps(request)+'\n').encode());accepted=bool(stream.recv(65536))
                except Exception as exc:error=type(exc).__name__+': '+str(exc)
                thread.join(9)
                rows.append(dict(case=label,client=mode,client_runtime=response if a.bundled_app else None,accepted=accepted,operator_received=capture,error=error,server_errors=errors))
        if a.bundled_app:core_flags=response['core_context']
        else:
            core=SVServer.unique('localhost',1,'s')._sslc();core_flags=dict(verify_mode=int(core.verify_mode),check_hostname=core.check_hostname)
        result=dict(python=sys.version,openssl=ssl.OPENSSL_VERSION,source=str(a.source),bundled_app=str(a.bundled_app),core_context=core_flags,rows=rows,scope='Loopback certificate authentication and operator-visible request test; actual wallet core context and helper function, not full GUI for this matrix')
        assert all(r['accepted'] for r in rows if r['client']!='verified-control' and r['case']!='plaintext-endpoint')
        assert not any(r['accepted'] for r in rows if r['case']=='plaintext-endpoint')
        assert [r['case'] for r in rows if r['client']=='verified-control' and r['accepted']]==['trusted-matching']
        (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(status='PASS',cases=len(rows),core_context=result['core_context'])))
    finally:shutil.rmtree(private)

if __name__=='__main__':main()
