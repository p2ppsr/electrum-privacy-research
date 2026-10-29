"""Join controlled session interests to a later synthetic ledger and one public anchor.

The analyzer takes only the capture, raw ledger and checkout address. No wallet
database, seed, derivation metadata or scenario ground truth is an input.
"""
import argparse
import hashlib
import json
from pathlib import Path

from .dossier import parse_tx, reconstruct, scripthash


def script_for_address(value):
    alphabet="123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number=0
    for char in value:
        number=number*58+alphabet.index(char)
    raw=number.to_bytes((number.bit_length()+7)//8,"big")
    raw=b"\0"*(len(value)-len(value.lstrip("1")))+raw
    assert len(raw)==25 and raw[0]==0,"only mainnet P2PKH anchors are supported"
    assert hashlib.sha256(hashlib.sha256(raw[:-4]).digest()).digest()[:4]==raw[-4:],"address checksum"
    return b"\x76\xa9\x14"+raw[1:21]+b"\x88\xac"


def analyze(capture,ledger,checkout):
    sessions=[c for c in reconstruct(capture)["clusters"] if c["script_count"]]
    interests={c["session"]:{s["scripthash"] for s in c["scripts"]} for c in sessions}
    def owners(output):
        return sorted(sid for sid,hashes in interests.items() if output["scripthash"] in hashes)
    anchor=json.loads(Path(checkout).read_text())
    anchor_hash=scripthash(script_for_address(anchor["address"]))
    anchored=sorted(sid for sid,hashes in interests.items() if anchor_hash in hashes)
    assert len(anchored)==1,"checkout must match exactly one observed collection in this scenario"
    shop=anchored[0]
    ledger_data=json.loads(Path(ledger).read_text())
    transactions=[parse_tx(raw) for raw in ledger_data["raw_transactions"]]
    by_id={tx["txid"]:tx for tx in transactions}
    assert len(by_id)==len(transactions),"duplicate transaction"
    edges=[]
    unlinked=[]
    all_outputs={}
    spent=set()
    for tx in transactions:
        input_groups=[]
        for inp in tx["inputs"]:
            spent.add((inp["txid"],inp["index"]))
            parent=by_id.get(inp["txid"])
            previous=parent["outputs"][inp["index"]] if parent and inp["index"]<len(parent["outputs"]) else None
            input_groups.append(owners(previous) if previous else [])
        # Attribution requires every input to match one and the same collection.
        unique={g[0] for g in input_groups if len(g)==1}
        source=next(iter(unique)) if len(unique)==1 and all(len(g)==1 for g in input_groups) else None
        touches=any(input_groups)
        for out in tx["outputs"]:
            target_groups=owners(out)
            all_outputs[(tx["txid"],out["index"])]=out
            touches=touches or bool(target_groups)
            if len(target_groups)==1:
                target=target_groups[0]
                if target!=source:
                    edges.append(dict(txid=tx["txid"],output=out["index"],value_sats=out["value_sats"],
                                      from_session=source,to_session=target,
                                      source_basis="all inputs in one observed collection" if source is not None else "unattributed or mixed inputs"))
            elif source is not None:
                edges.append(dict(txid=tx["txid"],output=out["index"],value_sats=out["value_sats"],
                                  from_session=source,to_session=None,source_basis="all inputs in one observed collection"))
        if not touches:
            unlinked.append(tx["txid"])
    shop_incoming=[e for e in edges if e["to_session"]==shop]
    shop_outgoing=[e for e in edges if e["from_session"]==shop]
    remaining=sum(out["value_sats"] for key,out in all_outputs.items() if key not in spent and shop in owners(out))
    return dict(status="PASS",mode="actual empty-wallet captures plus manufactured later unsigned ledger; NOT real-chain funding or ElectrumR",
                observed_collections=[dict(session=sid,script_count=len(hashes)) for sid,hashes in interests.items()],
                checkout=anchor,checkout_matches_session=shop,checkout_hash=anchor_hash,
                anchored_collection_script_count=len(interests[shop]),
                unique_shop_receiving_scripts_used=len({transactions_by_output(by_id,e)["scripthash"] for e in shop_incoming}),
                shop_gross_receipts_sats=sum(e["value_sats"] for e in shop_incoming),
                shop_receipts_from_observed_payer_collections_sats=sum(e["value_sats"] for e in shop_incoming if e["from_session"] is not None),
                shop_receipts_from_unattributed_payers_sats=sum(e["value_sats"] for e in shop_incoming if e["from_session"] is None),
                shop_external_outflow_sats=sum(e["value_sats"] for e in shop_outgoing),shop_remaining_observed_sats=remaining,
                edges=edges,transactions_unlinked_to_any_collection=unlinked,
                ledger_generated_after_wallet_exit=ledger_data["generated_after_wallet_exit"],
                inputs=[str(capture),str(ledger),str(checkout)],wallet_or_ground_truth_input=False,
                limits=["Session interest is not cryptographic ownership or a proven natural person",
                        "An unobserved payer has no inferred identity; multi-owner or ambiguous inputs are not assigned to one payer",
                        "An undisclosed unrelated script does not become attributable from the known collection alone",
                        "No real shop contacted; no real user's data; no consensus validity or input-signature claim for the manufactured ledger"])


def transactions_by_output(by_id,edge):
    return by_id[edge["txid"]]["outputs"][edge["output"]]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capture",type=Path,required=True)
    p.add_argument("--ledger",type=Path,required=True)
    p.add_argument("--checkout",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=analyze(a.capture,a.ledger,a.checkout)
    a.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ["edges","checkout","limits"]},indent=2))


if __name__=="__main__":main()
