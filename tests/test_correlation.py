import json
from pathlib import Path
import struct
import tempfile
import unittest

from privacy_lab.correlation import analyze,script_for_address
from privacy_lab.dossier import parse_tx


ROOT=Path("evidence/correlation-attempt-01")


class CorrelationBoundaries(unittest.TestCase):
    def run_with(self,raws):
        with tempfile.TemporaryDirectory() as temporary:
            ledger=Path(temporary)/"ledger.json"
            ledger.write_text(json.dumps(dict(raw_transactions=raws,generated_after_wallet_exit=True)))
            return analyze(ROOT/"capture.jsonl",ledger,ROOT/"checkout.json")

    def test_checkout_anchors_collection_before_any_payment(self):
        result=self.run_with([])
        self.assertEqual(result["anchored_collection_script_count"],40)
        self.assertEqual(result["shop_gross_receipts_sats"],0)

    def test_unobserved_payer_does_not_gain_an_identity(self):
        ledger=json.loads((ROOT/"later-ledger.json").read_text())
        result=self.run_with(ledger["raw_transactions"])
        incoming=[e for e in result["edges"] if e["to_session"]==result["checkout_matches_session"] and e["value_sats"]==1_250_000]
        self.assertEqual(len(incoming),1)
        self.assertIsNone(incoming[0]["from_session"])
        self.assertIn(parse_tx(ledger["raw_transactions"][-1])["txid"],result["transactions_unlinked_to_any_collection"])

    def test_mixed_profile_inputs_do_not_become_one_identified_payer(self):
        ledger=json.loads((ROOT/"later-ledger.json").read_text())
        parents=ledger["raw_transactions"][:2]
        raw=struct.pack("<I",1)+b"\x02"
        for parent in parents:
            raw+=bytes.fromhex(parse_tx(parent)["txid"])[::-1]+struct.pack("<I",0)+b"\x00"+bytes.fromhex("ffffffff")
        script=script_for_address(json.loads((ROOT/"checkout.json").read_text())["address"])
        raw+=b"\x01"+struct.pack("<Q",14_999_000)+bytes([len(script)])+script+b"\0"*4
        result=self.run_with(parents+[raw.hex()])
        edge=next(e for e in result["edges"] if e["to_session"]==result["checkout_matches_session"])
        self.assertIsNone(edge["from_session"])

    def test_invalid_public_anchor_is_rejected(self):
        value=json.loads((ROOT/"checkout.json").read_text())["address"]
        with self.assertRaises(AssertionError):
            script_for_address(value[:-1]+("1" if value[-1]!="1" else "2"))


if __name__=="__main__":unittest.main()
