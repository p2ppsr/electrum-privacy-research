"""Auditable local research Electrum adapter backed by an actual BSV regtest node.

This is not ElectrumR or ElectrumX. Headers, transactions, inclusion branches and
broadcast acceptance come from a locally isolated consensus-validating node.
"""
import asyncio
import io
import json
from pathlib import Path
import subprocess

from bitcoinx import Tx
from .dossier import parse_tx,sha256
from .fixture import Fixture


class NodeRPC:
    def __init__(self,container="electrum-privacy-bsv-20261029"):
        self.container=container

    def __call__(self,method,*params):
        values=[json.dumps(p,separators=(",",":")) if not isinstance(p,str) else p for p in params]
        r=subprocess.run(["docker","exec",self.container,"bitcoin-cli","-datadir=/data",method,*values],text=True,capture_output=True,timeout=60)
        if r.returncode:
            raise RuntimeError(f"node {method}: {r.stderr.strip()}")
        try:return json.loads(r.stdout)
        except ValueError:return r.stdout.strip()


def varint(read):
    first=read(1)[0]
    return first if first<253 else int.from_bytes(read({253:2,254:4,255:8}[first]),"little")


def decode_block(raw):
    stream=io.BytesIO(bytes.fromhex(raw));header=stream.read(80)
    transactions=[Tx.read(stream.read).to_bytes().hex() for _ in range(varint(stream.read))]
    assert not stream.read(),"trailing block bytes"
    return header.hex(),transactions


def merkle_branch(txids,index):
    level=[bytes.fromhex(txid)[::-1] for txid in txids];branch=[]
    while len(level)>1:
        if len(level)%2:level.append(level[-1])
        branch.append(level[index^1][::-1].hex());index//=2
        level=[sha256(sha256(level[i]+level[i+1])) for i in range(0,len(level),2)]
    return branch


class NodeIndexer(Fixture):
    def __init__(self,rpc,output):
        self.rpc=rpc;self.output=Path(output)
        self.output.mkdir(parents=True,exist_ok=True)
        self.headers=[];self.blocks=[];self.records={};self.clients={}
        self.transactions={};self.observed_scripts={};self.signature_checks=[]
        self.lock=asyncio.Lock();self.task=None

    def initialize(self):
        pass

    def refresh_sync(self):
        tip=self.rpc("getblockcount")
        for height in range(len(self.headers),tip+1):
            blockhash=self.rpc("getblockhash",height)
            raw=self.rpc("getblock",blockhash,0)
            header,transactions=decode_block(raw)
            assert sha256(sha256(bytes.fromhex(header)))[::-1].hex()==blockhash
            ids=[parse_tx(tx)["txid"] for tx in transactions]
            for index,(txid,tx) in enumerate(zip(ids,transactions)):
                self.records[txid]=dict(height=height,index=index,blockhash=blockhash)
                self.transactions[txid]=tx
            self.blocks.append(dict(height=height,blockhash=blockhash,raw=raw,txids=ids))
            self.headers.append(header)
        pending=self.rpc("getrawmempool")
        for txid in pending:
            if txid not in self.transactions:self.transactions[txid]=self.rpc("getrawtransaction",txid,False)
            self.records[txid]=dict(height=0,index=None,blockhash=None)

    def header(self,height):
        return self.headers[height]

    def history(self,sh):
        relevant=[]
        for txid,raw in list(self.transactions.items()):
            tx=parse_tx(raw)
            touches=any(out["scripthash"]==sh for out in tx["outputs"])
            for inp in tx["inputs"]:
                parent=self.transactions.get(inp["txid"])
                if parent:
                    outs=parse_tx(parent)["outputs"]
                    if inp["index"]<len(outs) and outs[inp["index"]]["scripthash"]==sh:touches=True
            if touches:relevant.append(dict(tx_hash=txid,height=self.records[txid]["height"]))
        return sorted(relevant,key=lambda row:(row["height"]==0,row["height"],row["tx_hash"]))

    def dispatch(self,method,params,subscriptions):
        if method=="server.version":return ["RESEARCH_NODE_ADAPTER_NOT_ELECTRUMR","1.4.2"]
        if method=="server.banner":return "Local BSV consensus-validating regtest research adapter"
        if method=="blockchain.headers.subscribe":return dict(height=len(self.headers)-1,hex=self.headers[-1])
        if method=="blockchain.block.headers":
            start,count=params[:2];raw="".join(self.headers[start:start+count])
            return dict(hex=raw,count=len(raw)//160,max=2016)
        if method=="blockchain.transaction.get_merkle":
            txid,height=params;block=self.blocks[height]
            return dict(block_height=height,pos=block["txids"].index(txid),merkle=merkle_branch(block["txids"],block["txids"].index(txid)))
        if method=="blockchain.transaction.broadcast":
            txid=self.rpc("sendrawtransaction",params[0]);self.transactions[txid]=params[0]
            self.records[txid]=dict(height=0,index=None,blockhash=None)
            self.signature_checks.append(dict(txid=txid,result="accepted by BSV node sendrawtransaction; consensus/mempool validation"))
            return txid
        return super().dispatch(method,params,subscriptions)

    async def refresh(self):
        async with self.lock:
            before={sh:self.status(sh) for group in self.clients.values() for sh in group}
            prior=len(self.headers)
            await asyncio.to_thread(self.refresh_sync)
            for writer,hashes in list(self.clients.items()):
                if writer.is_closing():continue
                if len(self.headers)!=prior:
                    writer.write((json.dumps(dict(jsonrpc="2.0",method="blockchain.headers.subscribe",params=[dict(height=len(self.headers)-1,hex=self.headers[-1])]))+"\n").encode())
                for sh in list(hashes):
                    current=self.status(sh)
                    if current!=before.get(sh):
                        writer.write((json.dumps(dict(jsonrpc="2.0",method="blockchain.scripthash.subscribe",params=[sh,current]))+"\n").encode())
                await writer.drain()

    async def poll(self):
        while True:
            await self.refresh();await asyncio.sleep(1)

    async def start(self):
        await asyncio.to_thread(self.refresh_sync)
        port=await super().start();self.task=asyncio.create_task(self.poll())
        return port

    async def stop(self):
        if self.task:
            self.task.cancel();await asyncio.gather(self.task,return_exceptions=True)
        await super().stop()
        (self.output/"node-blocks.json").write_text(json.dumps(self.blocks,indent=2)+"\n")
        (self.output/"node-transactions.json").write_text(json.dumps(dict(transactions=self.transactions,metadata=self.records,node_broadcast_checks=self.signature_checks),indent=2)+"\n")
