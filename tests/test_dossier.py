import json
from pathlib import Path
import tempfile
import unittest

from privacy_lab.dossier import load_journal,parse_tx,reconstruct,scripthash
from privacy_lab.fixture import funding
from privacy_lab.tap import Journal


SCRIPT = "76a914"+"11"*20+"88ac"


class DossierTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name)/"capture.jsonl"
        self.journal = Journal(self.path)

    def tearDown(self):
        if not self.journal.file.closed:
            self.journal.close()
        self.temp.cleanup()

    def frame(self,sid,direction,message):
        self.journal.frame(sid,direction,(json.dumps(message)+"\n").encode())

    def request(self,sid,i,method,params):
        self.frame(sid,"request",dict(id=i,method=method,params=params))

    def reply(self,sid,i,result):
        self.frame(sid,"response",dict(id=i,result=result))

    def test_unknown_funding_parent_does_not_invent_fee(self):
        raw=funding(SCRIPT,12345,1)
        tx=parse_tx(raw)
        sh=scripthash(bytes.fromhex(SCRIPT))
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.request(1,1,"blockchain.scripthash.get_history",[sh])
        self.reply(1,1,[dict(tx_hash=tx["txid"],height=0)])
        self.request(1,2,"blockchain.transaction.get",[tx["txid"]])
        self.reply(1,2,raw)
        self.journal.close()
        cluster=reconstruct(self.path)["clusters"][0]
        self.assertEqual(cluster["observed_unspent_sats"],12345)
        self.assertIsNone(cluster["activity"][0]["fee_sats"])
        self.assertEqual(cluster["activity"][0]["unknown_input_count"],1)

    def test_failed_broadcast_is_retained_but_not_counted_as_balance(self):
        raw=funding(SCRIPT,9999,2)
        sh=scripthash(bytes.fromhex(SCRIPT))
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.request(1,1,"blockchain.scripthash.subscribe",[sh]);self.reply(1,1,None)
        self.request(1,2,"blockchain.transaction.broadcast",[raw])
        self.frame(1,"response",dict(id=2,error=dict(code=1,message="rejected")))
        self.journal.close()
        dossier=reconstruct(self.path)
        self.assertEqual(len(dossier["broadcasts"]),1)
        self.assertEqual(dossier["clusters"][0]["observed_unspent_sats"],0)

    def test_request_ids_are_scoped_to_sessions(self):
        for sid,sh in [(1,"aa"*32),(2,"bb"*32)]:
            self.journal.record(event="connect",session=sid,peer=["127.0.0.1",sid])
            self.request(sid,1,"blockchain.scripthash.subscribe",[sh])
        self.reply(2,1,None);self.reply(1,1,None)
        self.journal.close()
        result=reconstruct(self.path)
        self.assertEqual([c["script_count"] for c in result["clusters"]],[1,1])
        self.assertTrue(all(c["balance_complete_for_observed_history"] for c in result["clusters"]))

    def test_tampering_is_rejected(self):
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.journal.close()
        self.path.write_text(self.path.read_text().replace('127.0.0.1','127.0.0.2'))
        with self.assertRaisesRegex(ValueError,"integrity failure"):
            load_journal(self.path)

    def test_transaction_hash_mismatch_is_rejected(self):
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.request(1,1,"blockchain.transaction.get",["aa"*32])
        self.reply(1,1,funding(SCRIPT,100,1))
        self.journal.close()
        with self.assertRaisesRegex(ValueError,"wrong TXID"):
            reconstruct(self.path)

    def test_unanswered_status_change_makes_balance_incomplete(self):
        sh=scripthash(bytes.fromhex(SCRIPT))
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.request(1,1,"blockchain.scripthash.subscribe",[sh]);self.reply(1,1,None)
        self.frame(1,"response",dict(method="blockchain.scripthash.subscribe",params=[sh,"ab"*32]))
        self.journal.close()
        cluster=reconstruct(self.path)["clusters"][0]
        self.assertFalse(cluster["balance_complete_for_observed_history"])
        self.assertEqual(cluster["unresolved_status_updates"],[sh])

    def test_missing_history_body_makes_balance_incomplete(self):
        sh=scripthash(bytes.fromhex(SCRIPT))
        self.journal.record(event="connect",session=1,peer=["127.0.0.1",1])
        self.request(1,1,"blockchain.scripthash.get_history",[sh])
        self.reply(1,1,[dict(tx_hash="aa"*32,height=0)])
        self.journal.close()
        cluster=reconstruct(self.path)["clusters"][0]
        self.assertFalse(cluster["balance_complete_for_observed_history"])
        self.assertEqual(cluster["missing_transaction_bodies"],["aa"*32])


if __name__ == "__main__":
    unittest.main()
