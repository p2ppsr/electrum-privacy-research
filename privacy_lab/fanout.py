"""Execute the exact upstream verification helper against eight local TLS servers."""
import argparse
import ast
import json
import os
from pathlib import Path
import random
import socket
import socketserver
import ssl
import subprocess
import threading
import time
from datetime import datetime, timezone


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    private = Path(".runtime")/args.output.name
    private.mkdir(parents=True,exist_ok=False)
    cert,key = private/"tls.pem",private/"tls.key"
    subprocess.run(["openssl","req","-x509","-newkey","rsa:2048","-nodes","-days","1",
        "-subj","/CN=fanout-fixture","-keyout",str(key),"-out",str(cert)],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert,key)
    barrier,lock,received = threading.Barrier(8,timeout=10),threading.Lock(),[]
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            req = json.loads(self.rfile.readline())
            with lock:
                received.append(dict(server=self.server.label,utc=datetime.now(timezone.utc).isoformat(),request=req))
            barrier.wait()
            self.wfile.write((json.dumps(dict(id=0,result="controlled-response"))+"\n").encode())
    class Server(socketserver.ThreadingTCPServer):
        daemon_threads = True
        def get_request(self):
            stream,addr = super().get_request()
            return context.wrap_socket(stream,server_side=True),addr
    servers,threads,mapping = [],[],{}
    for n in range(8):
        server = Server(("127.0.0.1",0),Handler)
        server.label = f"controlled-server-{n}"
        servers.append(server)
        mapping[server.label] = {"s":server.server_address[1]}
        thread = threading.Thread(target=server.serve_forever,daemon=True)
        thread.start();threads.append(thread)
    class RoutedSocket:
        @staticmethod
        def create_connection(endpoint,**kw):
            host,port = endpoint
            if host not in mapping:
                # Simulate the ordinary desktop case: no Tor daemon.
                raise OSError("no Tor in controlled helper experiment")
            return socket.create_connection(("127.0.0.1",port),**kw)
    source = (args.source/"electrumsv/verification_utils.py").read_text()
    tree = ast.parse(source)
    node = next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="electrum_request")
    function_source = ast.get_source_segment(source,node)
    env = dict(socket=RoutedSocket,ssl=ssl,json=json,os=os,random=random,time=time,TIMEOUT=5,SERVERS=mapping)
    exec(compile(function_source,"<exact upstream electrum_request>","exec"),env)
    try:
        result = env["electrum_request"]("blockchain.transaction.get",["cd"*32])
        # The barrier ensures every recipient retained the request before a reply wins.
        assert len(received)==8
        report = dict(status="PASS",source_start_line=node.lineno,source_end_line=node.end_lineno,
            mode="exact upstream helper function, eight controlled local TLS peers",
            controls=["SERVERS replaced with eight local TLS peers", "socket host routing for loopback isolation", "no Tor"],
            recipients=len(received),first_success=result,requests=received,
            implication="Returning the first response does not retract requests already delivered to other servers.")
        (args.output/"fanout.json").write_text(json.dumps(report,indent=2)+"\n")
        print(json.dumps({k:v for k,v in report.items() if k not in ("requests",)},indent=2))
    finally:
        for server in servers:
            server.shutdown();server.server_close()
        for thread in threads:
            thread.join(timeout=2)


if __name__ == "__main__":
    main()
