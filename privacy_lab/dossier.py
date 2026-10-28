"""Reconstruct only what a serving operator receives. No wallet/seed input."""
import argparse
import base64
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path


def sha256(data):
    return hashlib.sha256(data).digest()


def scripthash(script):
    return sha256(script)[::-1].hex()


def base58check(payload):
    data = payload + sha256(sha256(payload))[:4]
    zeros = len(data) - len(data.lstrip(b"\0"))
    n, result = int.from_bytes(data, "big"), ""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    while n:
        n, rem = divmod(n, 58)
        result = alphabet[rem] + result
    return "1" * zeros + result


def address(script, testnet=False):
    if len(script) == 25 and script[:3] == bytes.fromhex("76a914") and script[-2:] == bytes.fromhex("88ac"):
        return base58check(bytes([111 if testnet else 0]) + script[3:23])
    if len(script) == 23 and script[:2] == bytes.fromhex("a914") and script[-1:] == b"\x87":
        return base58check(bytes([196 if testnet else 5]) + script[2:22])
    return None


def parse_tx(raw_hex):
    raw = bytes.fromhex(raw_hex)
    offset = 0

    def read(n):
        nonlocal offset
        value = raw[offset:offset+n]
        if len(value) != n:
            raise ValueError("truncated transaction")
        offset += n
        return value

    def varint():
        first = read(1)[0]
        return first if first < 253 else int.from_bytes(read({253:2,254:4,255:8}[first]), "little")

    version = int.from_bytes(read(4), "little")
    inputs = []
    for _ in range(varint()):
        previous, index = read(32)[::-1].hex(), int.from_bytes(read(4), "little")
        script = read(varint()).hex()
        sequence = int.from_bytes(read(4), "little")
        inputs.append(dict(txid=previous, index=index, script_sig=script, sequence=sequence))
    outputs = []
    for index in range(varint()):
        value, script = int.from_bytes(read(8), "little"), read(varint())
        outputs.append(dict(index=index, value_sats=value, script=script.hex(),
                            scripthash=scripthash(script), address=address(script)))
    locktime = int.from_bytes(read(4), "little")
    if offset != len(raw):
        raise ValueError("trailing bytes / unsupported transaction encoding")
    return dict(txid=sha256(sha256(raw))[::-1].hex(), version=version,
                inputs=inputs, outputs=outputs, locktime=locktime)


def load_journal(path):
    previous, rows = "0" * 64, []
    for expected, line in enumerate(Path(path).read_text().splitlines(), 1):
        row = json.loads(line)
        digest = row.pop("sha256")
        actual = hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if digest != actual or row["previous_sha256"] != previous or row["sequence"] != expected:
            raise ValueError(f"journal integrity failure at sequence {expected}")
        if "wire_base64" in row:
            wire = base64.b64decode(row["wire_base64"], validate=True)
            if "message" in row and json.loads(wire) != row["message"]:
                raise ValueError("parsed message does not match wire evidence")
        row["sha256"] = digest
        rows.append(row)
        previous = digest
    return rows


def reconstruct(path):
    rows = load_journal(path)
    sessions, pending, methods, known_txs, broadcasts = {}, {}, Counter(), {}, []
    for row in rows:
        sid = row.get("session")
        if row["event"] == "connect":
            sessions[sid] = dict(peer=row["peer"], started=row["utc"], scripts={}, histories={}, statuses={}, versions=[])
        if row["event"] != "frame":
            continue
        messages = row.get("message")
        for msg in messages if isinstance(messages, list) else [messages]:
            if not isinstance(msg, dict):
                continue
            view = sessions[sid]
            if row["direction"] == "response" and msg.get("method") == "blockchain.scripthash.subscribe":
                sh,status = msg["params"]
                view["statuses"][sh] = status
                if status is None:
                    view["histories"][sh] = []
            if row["direction"] == "request" and "method" in msg:
                method, params = msg["method"], msg.get("params", [])
                methods[method] += 1
                if "id" in msg:
                    pending[(sid, json.dumps(msg["id"]))] = (method, params)
                if method == "server.version":
                    view["versions"].append(params)
                if method.startswith("blockchain.scripthash.") and params:
                    view["scripts"].setdefault(params[0], dict(first_seen=row["utc"], methods=[]))["methods"].append(method)
                if method == "blockchain.transaction.broadcast":
                    tx = parse_tx(params[0])
                    known_txs[tx["txid"]] = tx
                    broadcasts.append(dict(session=sid, txid=tx["txid"], submitted=row["utc"], response=None))
            elif row["direction"] == "response" and "id" in msg:
                request = pending.get((sid, json.dumps(msg["id"])))
                if not request:
                    continue
                method, params = request
                if method == "blockchain.scripthash.subscribe" and "result" in msg:
                    view["statuses"][params[0]] = msg["result"]
                if method == "blockchain.scripthash.subscribe" and msg.get("result", "not-empty") is None:
                    view["histories"][params[0]] = []
                if method == "blockchain.scripthash.get_history" and isinstance(msg.get("result"), list):
                    view["histories"][params[0]] = msg["result"]
                if method == "blockchain.transaction.get" and isinstance(msg.get("result"), str):
                    tx = parse_tx(msg["result"])
                    if tx["txid"] != params[0]:
                        raise ValueError("server transaction response has wrong TXID")
                    known_txs[tx["txid"]] = tx
                if method == "blockchain.transaction.broadcast":
                    txid = parse_tx(params[0])["txid"]
                    for item in broadcasts:
                        if item["session"] == sid and item["txid"] == txid:
                            item["response"] = {k:v for k,v in msg.items() if k in ("result", "error")}
    clusters = []
    for sid, view in sessions.items():
        scripts = set(view["scripts"])
        history_ids = {h["tx_hash"] for hist in view["histories"].values() for h in hist}
        own_broadcasts = {b["txid"] for b in broadcasts if b["session"] == sid}
        relevant_ids = history_ids | own_broadcasts
        # Distinguish submitted attempts from transactions reported in server history.
        accepted_ids = history_ids | {b["txid"] for b in broadcasts if b["session"] == sid
                                     and b["response"] and b["response"].get("result") == b["txid"]}
        missing = sorted(history_ids - set(known_txs))
        inconsistent = []
        for sh,status in view["statuses"].items():
            history = view["histories"].get(sh)
            if history is None:
                inconsistent.append(sh)
                continue
            digest = hashlib.sha256("".join(f"{h['tx_hash']}:{h['height']}:" for h in history).encode()).hexdigest() if history else None
            if digest != status:
                inconsistent.append(sh)
        current_outputs = {}
        for txid in accepted_ids:
            if txid not in known_txs:
                continue
            for out in known_txs[txid]["outputs"]:
                if out["scripthash"] in scripts:
                    current_outputs[(txid,out["index"])] = out
        for txid in accepted_ids:
            if txid in known_txs:
                for inp in known_txs[txid]["inputs"]:
                    current_outputs.pop((inp["txid"], inp["index"]), None)
        activity, resolved_scripts = [], {}
        for txid in sorted(relevant_ids & set(known_txs)):
            tx = known_txs[txid]
            wallet_inputs, external_inputs, total_inputs, unknown_inputs = 0, 0, 0, 0
            for inp in tx["inputs"]:
                parent = known_txs.get(inp["txid"])
                if not parent or inp["index"] >= len(parent["outputs"]):
                    unknown_inputs += 1
                    continue
                out = parent["outputs"][inp["index"]]
                total_inputs += out["value_sats"]
                if out["scripthash"] in scripts:
                    wallet_inputs += out["value_sats"]
                else:
                    external_inputs += out["value_sats"]
            own_outputs, external_outputs = [], []
            for out in tx["outputs"]:
                if out["scripthash"] in scripts:
                    own_outputs.append(out)
                    resolved_scripts[out["scripthash"]] = dict(script=out["script"],address=out["address"])
                else:
                    external_outputs.append(out)
            received = sum(o["value_sats"] for o in own_outputs)
            activity.append(dict(txid=txid, in_history=txid in history_ids,
                submitted=txid in own_broadcasts, cluster_outputs_sats=received,
                known_cluster_inputs_sats=wallet_inputs,
                cluster_delta_sats=received-wallet_inputs,
                unknown_input_count=unknown_inputs,
                fee_sats=None if unknown_inputs else total_inputs-sum(o["value_sats"] for o in tx["outputs"]),
                cluster_outputs=own_outputs, external_outputs=external_outputs))
        clusters.append(dict(session=sid, peer=view["peer"], client_versions=view["versions"],
            script_count=len(scripts), resolved_script_count=len(resolved_scripts),
            unresolved_script_count=len(scripts-set(resolved_scripts)),
            scripts=[dict(scripthash=h, **view["scripts"][h], **resolved_scripts.get(h,{})) for h in sorted(scripts)],
            history_transaction_count=len(history_ids), missing_transaction_bodies=missing,
            observed_unspent_sats=sum(o["value_sats"] for o in current_outputs.values()),
            unresolved_status_updates=inconsistent,
            balance_complete_for_observed_history=not missing and not inconsistent and len(view["histories"]) == len(scripts),
            utxos=[dict(txid=k[0],index=k[1],**{n:v for n,v in o.items() if n != 'index'}) for k,o in sorted(current_outputs.items())],
            activity=activity))
    return dict(schema_version=1, evidence_source=str(path), method_counts=dict(methods),
                clusters=clusters, broadcasts=broadcasts,
                completeness_scope="Consistency with captured server responses, not proof of complete blockchain history or ownership.",
                attribution="Session associates queried interests; ownership, identity, income and payment purpose are not proven.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(reconstruct(args.capture), indent=2) + "\n")


if __name__ == "__main__":
    main()
