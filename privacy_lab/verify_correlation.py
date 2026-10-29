"""Offline consistency checks for retained correlation and disclosure evidence."""
from datetime import datetime
import json
from pathlib import Path

from .correlation import analyze
from .dossier import load_journal,parse_tx


def main():
    root=Path("evidence/correlation-attempt-01")
    expected=json.loads((root/"correlation.json").read_text())
    result=analyze(root/"capture.jsonl",root/"later-ledger.json",root/"checkout.json")
    assert result==expected
    assert [c["script_count"] for c in result["observed_collections"]]==[40,40,40]
    rows=load_journal(root/"capture.jsonl")
    ledger=json.loads((root/"later-ledger.json").read_text())
    assert datetime.fromisoformat(ledger["generated_at"])>max(datetime.fromisoformat(r["utc"]) for r in rows)
    assert all(not r.get("message",{}).get("method","").startswith("blockchain.transaction.")
               for r in rows if isinstance(r.get("message"),dict))
    hashes={}
    for r in rows:
        m=r.get("message")
        if isinstance(m,dict) and r.get("direction")=="request" and m.get("method")=="blockchain.scripthash.subscribe":
            hashes.setdefault(r["session"],set()).add(m["params"][0])
    assert len(set.union(*hashes.values()))==120
    assert result["anchored_collection_script_count"]==40
    assert result["unique_shop_receiving_scripts_used"]==3
    assert result["shop_gross_receipts_sats"]==7_750_000
    assert result["shop_receipts_from_observed_payer_collections_sats"]==6_500_000
    assert result["shop_receipts_from_unattributed_payers_sats"]==1_250_000
    assert result["shop_remaining_observed_sats"]==6_649_000
    assert parse_tx(ledger["raw_transactions"][-1])["txid"] in result["transactions_unlinked_to_any_collection"]
    run=json.loads((root/"run.json").read_text())
    assert run["wallet_exit_codes"]==[0,0,0] and run["disposable_state_removed"] is True
    audit=json.loads(Path("evidence/disclosure-audit-20261028/source-audit.json").read_text())
    def excerpt(path):
        return "\n".join(e["text"] for r in audit["source_receipts"] if r["path"]==path for e in r["excerpts"])
    assert "wallet payment script metadata to a single server" in excerpt("electrumsv/data/text/misc/network-dialog.html")
    assert "Proxy settings apply to all connections" in excerpt("electrumsv/gui/qt/network_dialog.py")
    assert "socket.create_connection" in excerpt("electrumsv/verification_utils.py")
    assert "unique and private receiving addresses" in excerpt("docs/standalone/index.rst")
    assert audit["searched_source_file_count"]==92
    assert len(audit["source_receipts"])==18
    for path in ["electrumsv/gui/qt/network_dialog.py","electrumsv/data/text/misc/network-dialog.html",
                 "electrumsv/gui/qt/dialogs.py","electrumsv/gui/qt/preferences.py","docs/standalone/index.rst"]:
        assert next(r["unchanged_in_latest"] for r in audit["source_receipts"] if r["path"]==path)
    pools=audit["source_pool_version_comparison"]
    release=pools[audit["release_commit"]];latest=pools[audit["latest_public_master_observed"]]
    assert (release["core_count"],release["helper_count"],release["union_count"] )==(8,8,9)
    assert (latest["core_count"],latest["helper_count"],latest["union_count"] )==(8,8,8)
    searches=json.loads(Path("evidence/disclosure-audit-20261028/public-discussion-searches.json").read_text())
    assert len(searches["initial_rejected_queries"])==4
    assert len(searches["corrected_queries"])==8
    assert all(not r["tool_error"] for r in searches["corrected_queries"])
    discussions=json.loads(Path("evidence/disclosure-audit-20261028/public-discussion-review.json").read_text())
    assert all(not r["tool_error"] for r in discussions)
    assert any(record.get("author_association")=="OWNER" for row in discussions for record in row["records"])
    outcome=dict(status="PASS",actual_wallet_collections=3,disclosed_identifiers=120,
                 checkout_address_anchors_identifiers=40,distinct_shop_receiving_addresses=3,
                 observed_payer_flow_sats=6_500_000,unattributed_payer_flow_sats=1_250_000,
                 ledger_created_after_all_captured_connections_closed=True,
                 source_files_searched=92,manually_reviewed_source_receipts=18,
                 public_technical_risk_awareness_evidence_present=True,
                 actual_user_awareness_measured=False,
                 disclosure_absence_is_bounded_manual_review=True)
    Path("evidence/correlation-disclosure-verification.json").write_text(json.dumps(outcome,indent=2)+"\n")
    print(json.dumps(outcome,indent=2))


if __name__=="__main__":main()
