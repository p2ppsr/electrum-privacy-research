"""Three fresh real-wallet subscription captures, then an offline correlation fixture."""
import argparse
import asyncio
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import ssl
import struct
import subprocess
import sys

from .correlation import analyze
from .dossier import address,parse_tx
from .fixture import Fixture,funding,varint
from .tap import Journal,Tap


class EmptyFixture(Fixture):
    def initialize(self):
        pass


def payment(parent,outputs):
    prev=parse_tx(parent)
    raw=struct.pack("<I",1)+b"\x01"+bytes.fromhex(prev["txid"])[::-1]+struct.pack("<I",0)+b"\x00"+bytes.fromhex("ffffffff")+varint(len(outputs))
    for script,value in outputs:
        raw+=struct.pack("<Q",value)+varint(len(bytes.fromhex(script)))+bytes.fromhex(script)
    return (raw+b"\0"*4).hex()


async def run(args):
    args.output.mkdir(parents=True,exist_ok=False)
    private=Path(".runtime")/args.output.name
    private.mkdir(parents=True,exist_ok=False)
    journal=Journal(args.output/"capture.jsonl")
    fixture=EmptyFixture(args.source/"electrumsv/resources/headersloaded/headers",private/"unused")
    tap=None
    codes=[]
    try:
        cert,key=private/"server.pem",private/"server.key"
        subprocess.run(["openssl","req","-x509","-newkey","rsa:2048","-nodes","-days","1","-subj","/CN=controlled-correlation.local","-keyout",str(key),"-out",str(cert)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert,key)
        tap=Tap(journal,("127.0.0.1",await fixture.start(),False),context)
        port=await tap.start()
        truth=[]
        for i in range(3):
            state=private/f"wallet-{i}"
            command=[sys.executable,"-m","privacy_lab.wallet_session","--source",str(args.source),"--state",str(state),"--port",str(port),"--empty-local"]
            with (args.output/f"wallet-{i}-process.log").open("w") as log:
                process=await asyncio.create_subprocess_exec(*command,stdout=log,stderr=log)
                try:
                    code=await asyncio.wait_for(process.wait(),timeout=90)
                except asyncio.TimeoutError:
                    process.terminate()
                    await process.wait()
                    raise
            codes.append(code)
            assert code==0,f"controlled wallet {i} failed; keep process log"
            truth.append({tuple(r["derivation"]):r["script"] for r in json.loads((state/"ground-truth.json").read_text())})
        await tap.stop()
        tap=None
        journal.close()
        # All clients have exited before these modeled public transactions exist.
        buyer_a,buyer_b,shop=truth
        unobserved="76a914"+hashlib.sha256(b"unobserved-controlled-party").digest()[:20].hex()+"88ac"
        outside="76a914"+hashlib.sha256(b"unlinked-negative-control").digest()[:20].hex()+"88ac"
        a=funding(buyer_a[(0,0)],8_000_000,"correlation-buyer-a")
        b=funding(buyer_b[(0,0)],7_000_000,"correlation-buyer-b")
        u=funding(unobserved,2_000_000,"correlation-unobserved")
        p1=payment(a,[(shop[(0,0)],2_500_000),(buyer_a[(1,0)],5_499_000)])
        p2=payment(b,[(shop[(0,1)],4_000_000),(buyer_b[(1,0)],2_999_000)])
        p3=payment(u,[(shop[(0,2)],1_250_000),(unobserved,749_000)])
        spend=payment(p1,[(outside,1_100_000),(shop[(1,0)],1_399_000)])
        negative=funding(outside,555_000,"unlinked-negative-control")
        ledger=dict(mode="manufactured later unsigned ledger, fictional funding parents; no real funds or confirmations",
                    generated_after_wallet_exit=True,generated_at=datetime.now(timezone.utc).isoformat(),
                    raw_transactions=[a,b,u,p1,p2,p3,spend,negative])
        (args.output/"later-ledger.json").write_text(json.dumps(ledger,indent=2)+"\n")
        checkout=dict(label="Fictional controlled web shop",address=address(bytes.fromhex(shop[(0,0)])),
                      context="simulated public checkout; no actual shop contacted; one address only")
        (args.output/"checkout.json").write_text(json.dumps(checkout,indent=2)+"\n")
        result=analyze(args.output/"capture.jsonl",args.output/"later-ledger.json",args.output/"checkout.json")
        assert [r["script_count"] for r in result["observed_collections"]]==[40,40,40]
        assert result["shop_gross_receipts_sats"]==7_750_000
        assert result["shop_receipts_from_observed_payer_collections_sats"]==6_500_000
        assert result["shop_receipts_from_unattributed_payers_sats"]==1_250_000
        assert result["shop_external_outflow_sats"]==1_100_000
        assert result["shop_remaining_observed_sats"]==6_649_000
        assert result["unique_shop_receiving_scripts_used"]==3
        (args.output/"correlation.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({k:v for k,v in result.items() if k not in ["edges","checkout","limits"]},indent=2))
    finally:
        if tap:await tap.stop()
        await fixture.stop()
        if not journal.file.closed:journal.close()
        shutil.rmtree(private)
        (args.output/"run.json").write_text(json.dumps(dict(wallet_exit_codes=codes,disposable_state_removed=not private.exists(),
            no_public_destinations=True,no_real_funds=True,self_hosted_electrumr=False,
            controls=["loopback TLS", "oneserver=True", "auto_connect=False", "headless callbacks", "isolated paths", "non-loopback socket connections blocked in wallet processes"],
            defaults_preserved=["actual upstream Wallet, StandardAccount and Network", "20 receiving and 20 change lookahead", "automatic script subscriptions without a privacy opt-in"],
            financial_ledger="manufactured unsigned transactions constructed after all three wallet processes exited; not wallet signing or consensus validation"),indent=2)+"\n")


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    asyncio.run(run(p.parse_args()))


if __name__=="__main__":main()
