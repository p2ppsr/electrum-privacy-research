"""Independent expected amounts and capture integrity gates for retained evidence."""
import argparse
import hashlib
import json
from pathlib import Path
from .dossier import reconstruct,parse_tx


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--live",type=Path,required=True)
    p.add_argument("--fixture",type=Path,required=True)
    p.add_argument("--fanout",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    live=reconstruct(args.live/"capture.jsonl")
    demo=reconstruct(args.fixture/"capture.jsonl")
    l=[c for c in live["clusters"] if c["script_count"]]
    f=[c for c in demo["clusters"] if c["script_count"]]
    assert len(l)==len(f)==1
    assert l[0]["script_count"]==40 and l[0]["history_transaction_count"]==0
    assert l[0]["observed_unspent_sats"]==0 and l[0]["balance_complete_for_observed_history"]
    assert f[0]["script_count"]>=40
    assert f[0]["history_transaction_count"]==4
    assert f[0]["observed_unspent_sats"]==8_499_000
    assert f[0]["balance_complete_for_observed_history"]
    outgoing=[a for a in f[0]["activity"] if a["submitted"]]
    assert len(outgoing)==1
    assert outgoing[0]["known_cluster_inputs_sats"]==8_000_000
    assert sum(o["value_sats"] for o in outgoing[0]["external_outputs"])==5_000_000
    assert outgoing[0]["cluster_outputs_sats"]==2_999_000 and outgoing[0]["fee_sats"]==1000
    assert sum(a["cluster_delta_sats"] for a in f[0]["activity"] if not a["submitted"])==13_500_000
    run=json.loads((args.fixture/"run.json").read_text())
    assert run["exit_code"]==0 and len(run["signature_checks"])==1
    fan=json.loads(args.fanout.read_text())
    assert fan["status"]=="PASS" and len({r["server"] for r in fan["requests"]})==8
    future=json.loads((args.fixture/"future-watch.json").read_text())
    tx=parse_tx(future["raw_transaction"])
    watched={s["scripthash"] for s in f[0]["scripts"]}
    already_resolved={s["scripthash"] for s in f[0]["scripts"] if "script" in s}
    assert len([o for o in tx["outputs"] if o["scripthash"] in watched])==1
    assert tx["outputs"][0]["scripthash"] not in already_resolved
    assert tx["outputs"][0]["value_sats"]==1_700_000
    # Rebuild dossiers in a clean read without any wallet files or oracle metadata.
    for root,data in [(args.live,live),(args.fixture,demo)]:
        (root/"dossier.json").write_text(json.dumps(data,indent=2)+"\n")
    result=dict(status="PASS",live_scripts=l[0]["script_count"],fixture_scripts=f[0]["script_count"],
        fixture_transactions=4,fixture_incoming_sats=13_500_000,fixture_external_payment_sats=5_000_000,
        fixture_fee_sats=1000,fixture_remaining_sats=8_499_000,
        future_watch_sats=1_700_000,fanout_recipients=8,
        analyzer_inputs="retained server-side capture only; future check adds a modeled later ledger transaction",
        limitations=["No self-hosted ElectrumR source or binary was available", "Funded case is a manufactured unconfirmed ledger, not real BSV", "Endpoint identity strings are self-reported"])
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
