"""Explicit manufactured unconfirmed ledger, NOT ElectrumR or a Bitcoin node.

Allows the unchanged real wallet to exercise subscription, history, transaction,
signing and broadcast paths over sockets. Amounts have no monetary value. Header
responses use the wallet's genuine shipped headers. No fabricated confirmations.
"""
import asyncio
import hashlib
import json
import struct
from pathlib import Path

from .dossier import parse_tx, scripthash

RECIPIENT_SCRIPT = "76a914" + hashlib.sha256(b"controlled-external-recipient").digest()[:20].hex() + "88ac"


def varint(n):
    if n < 253:
        return bytes([n])
    if n <= 65535:
        return b"\xfd" + struct.pack("<H", n)
    return b"\xfe" + struct.pack("<I", n)


def funding(script_hex, value, nonce):
    script = bytes.fromhex(script_hex)
    # Deliberately fictional parent. This vector is not valid real-chain funding.
    parent = hashlib.sha256(f"manufactured-fixture-parent-{nonce}".encode()).digest()
    raw = (struct.pack("<I",1) + b"\x01" + parent + struct.pack("<I",0) + b"\x00" +
           bytes.fromhex("ffffffff") + b"\x01" + struct.pack("<Q",value) + varint(len(script)) + script + b"\0"*4)
    return raw.hex()


class Fixture:
    def __init__(self, headers_path, truth_path):
        self.headers_path, self.truth_path = Path(headers_path), Path(truth_path)
        self.transactions, self.clients, self.observed_scripts = {}, {}, {}
        self.signature_checks = []

    def initialize(self):
        if self.transactions:
            return
        truth = json.loads(self.truth_path.read_text())
        by_path = {tuple(r["derivation"]): r for r in truth}
        for index, amount in [(0,8_000_000),(1,3_500_000),(5,2_000_000)]:
            raw = funding(by_path[(0,index)]["script"], amount, index)
            self.transactions[parse_tx(raw)["txid"]] = raw
        self.by_path = by_path

    def history(self, sh):
        result = []
        parsed = {txid:parse_tx(raw) for txid,raw in self.transactions.items()}
        for txid,tx in parsed.items():
            matches = any(o["scripthash"] == sh for o in tx["outputs"])
            for inp in tx["inputs"]:
                parent = parsed.get(inp["txid"])
                if parent and inp["index"] < len(parent["outputs"]):
                    matches |= parent["outputs"][inp["index"]]["scripthash"] == sh
            if matches:
                result.append(dict(tx_hash=txid,height=0))
        return result

    def status(self, sh):
        hist = self.history(sh)
        if not hist:
            return None
        return hashlib.sha256("".join(f"{r['tx_hash']}:{r['height']}:" for r in hist).encode()).hexdigest()

    def header(self, height):
        with self.headers_path.open("rb") as f:
            f.seek(height*80)
            return f.read(80).hex()

    def dispatch(self, method, params, subscriptions):
        self.initialize()
        if method == "server.version": return ["CONTROLLED_PROTOCOL_FIXTURE_NOT_ELECTRUMR", "1.4.2"]
        if method == "server.banner": return "Manufactured ledger, no real-chain confirmations or funds"
        if method == "server.donation_address": return ""
        if method == "server.peers.subscribe": return []
        if method == "server.ping": return None
        if method == "blockchain.headers.subscribe":
            h = self.headers_path.stat().st_size//80-1
            return dict(height=h,hex=self.header(h))
        if method == "blockchain.block.header": return self.header(params[0])
        if method == "blockchain.block.headers":
            start,count = params[:2]
            raw = bytes.fromhex("".join(self.header(h) for h in range(start,start+count)))
            return dict(hex=raw.hex(),count=len(raw)//80,max=2016)
        if method == "blockchain.scripthash.subscribe":
            subscriptions.add(params[0])
            return self.status(params[0])
        if method == "blockchain.scripthash.unsubscribe":
            subscriptions.discard(params[0]); return True
        if method == "blockchain.scripthash.get_history": return self.history(params[0])
        if method == "blockchain.transaction.get": return self.transactions[params[0]]
        if method == "blockchain.transaction.broadcast":
            from bitcoinx import Tx, TxOutput, Script
            tx = Tx.from_hex(params[0])
            for inp in tx.inputs:
                parent = parse_tx(self.transactions[inp.prev_hash[::-1].hex()])
                previous = parent["outputs"][inp.prev_idx]
                inp.txo = TxOutput(previous["value_sats"], Script(bytes.fromhex(previous["script"])))
            tx.verify_inputs()
            parsed = parse_tx(params[0])
            self.signature_checks.append(dict(txid=parsed["txid"], result="valid BSV input signatures against fixture prevouts"))
            self.transactions[parsed["txid"]] = params[0]
            return parsed["txid"]
        raise ValueError("unsupported fixture RPC: " + method)

    async def start(self):
        self.server = await asyncio.start_server(self.handle, "127.0.0.1", 0)
        return self.server.sockets[0].getsockname()[1]

    async def handle(self, reader, writer):
        subscriptions = set()
        self.clients[writer] = subscriptions
        try:
            while line := await reader.readline():
                batch = json.loads(line)
                is_batch = isinstance(batch, list)
                replies, broadcast = [], False
                for req in batch if is_batch else [batch]:
                    try:
                        result = self.dispatch(req["method"], req.get("params", []), subscriptions)
                        reply = dict(jsonrpc="2.0",id=req["id"],result=result)
                        broadcast |= req["method"] == "blockchain.transaction.broadcast"
                    except Exception as exc:
                        reply = dict(jsonrpc="2.0",id=req["id"],error=dict(code=-32603,message=repr(exc)))
                    replies.append(reply)
                writer.write((json.dumps(replies if is_batch else replies[0])+"\n").encode())
                await writer.drain()
                if broadcast:
                    for other, hashes in list(self.clients.items()):
                        for sh in hashes:
                            other.write((json.dumps(dict(jsonrpc="2.0",method="blockchain.scripthash.subscribe",params=[sh,self.status(sh)]))+"\n").encode())
                        await other.drain()
        finally:
            self.clients.pop(writer,None)
            writer.close()

    async def stop(self):
        self.server.close()
        await self.server.wait_closed()
        for writer in list(self.clients):
            writer.close()
