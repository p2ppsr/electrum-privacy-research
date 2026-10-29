"""Unfunded real-wallet observation through a server-side recording TLS relay.

The upstream is an actual bundled public endpoint claiming ElectrumR. This does
not claim we possess, instrumented, or attested that endpoint's server binary.
"""
import argparse
import asyncio
import json
import os
import shutil
from pathlib import Path
import ssl
import subprocess
import sys

from .dossier import reconstruct
from .tap import Journal, Tap
from .fixture import Fixture, funding
from .dossier import parse_tx


async def run(args):
    args.output.mkdir(parents=True, exist_ok=False)
    private = Path(".runtime") / args.output.name
    private.mkdir(parents=True, exist_ok=False)
    cert, key = private / "server.pem", private / "server.key"
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-days", "1",
                    "-subj", "/CN=controlled-research.local", "-keyout", str(key), "-out", str(cert)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(cert, key)
    journal = Journal(args.output / "capture.jsonl")
    fixture = None
    if args.fixture:
        fixture = Fixture(args.source / "electrumsv/resources/headersloaded/headers",
                          private / "wallet-state/ground-truth.json")
        backend = ("127.0.0.1", await fixture.start(), False)
    else:
        backend = (args.upstream, 50002, True)
    tap = Tap(journal, backend, context)
    port = await tap.start()
    command = [sys.executable, "-m", "privacy_lab.wallet_session", "--source", str(args.source),
               "--state", str(private / "wallet-state"), "--port", str(port)]
    env=None
    if args.bundled_app:
        command[0]=str(args.bundled_app/'Contents/usr/bin/python3.9')
        env=os.environ.copy();env['PYTHONHOME']=str(args.bundled_app/'Contents/usr')
        env['DYLD_LIBRARY_PATH']=str(args.bundled_app/'Contents/Frameworks')+':'+str(args.bundled_app/'Contents/usr/lib')
    if args.fixture:
        command.append("--fixture")
    try:
        with (args.output / "wallet-process.log").open("w") as log:
            process = await asyncio.create_subprocess_exec(*command, env=env, stdout=log, stderr=log)
            try:
                code = await asyncio.wait_for(process.wait(), timeout=240)
            except asyncio.TimeoutError:
                process.terminate()
                await process.wait()
                code = -1
        result = dict(client="ElectrumSVP 0.2.0 real Wallet/Network", upstream=args.upstream,
            mode="public upstream behind local operator-equivalent recording relay; unfunded wallet",
            self_hosted_electrumr=False, exit_code=code,
            controls=["loopback TLS endpoint", "oneserver=True", "auto_connect=False",
                      "headless application callbacks", "isolated application data"],
            defaults_preserved=["20 receiving + 20 change lookahead", "P2PKH scripts", "history/transaction RPC logic"])
        if args.bundled_app:
            result['client']='Official macOS DMG bundled Python 3.9.13 and unchanged bundled Wallet/Network modules; headless harness'
            result['bundled_app']=str(args.bundled_app)
            result['packaged_GUI_session']=False
        if args.fixture:
            result.update(upstream="manufactured protocol fixture, NOT ElectrumR",
                mode="real upstream Wallet/Network against manufactured unconfirmed ledger",
                no_real_chain_funding=True, confirmed_transaction_claims=False,
                signature_checks=fixture.signature_checks)
            result["controls"] += ["verification helper endpoints redirected to local fixture", "non-loopback connections denied", "scripted controlled payment"]
        (args.output / "run.json").write_text(json.dumps(result, indent=2) + "\n")
    finally:
        await tap.stop()
        if fixture:
            await fixture.stop()
        journal.close()
    dossier = reconstruct(args.output / "capture.jsonl")
    (args.output / "dossier.json").write_text(json.dumps(dossier, indent=2) + "\n")
    if fixture and code == 0:
        raw = funding(fixture.by_path[(0,10)]["script"],1_700_000,"offline-future")
        observed = parse_tx(raw)
        watched = {s["scripthash"] for c in dossier["clusters"] for s in c["scripts"]}
        matches = [o for o in observed["outputs"] if o["scripthash"] in watched]
        (args.output/"future-watch.json").write_text(json.dumps(dict(
            scenario="manufactured later ledger event after wallet process exited; NOT a real-chain transaction",
            raw_transaction=raw,txid=observed["txid"],matching_outputs=matches,
            analyzer_inputs=["capture.jsonl","this later raw transaction"],
            requires_wallet_online=False),indent=2)+"\n")
    if args.bundled_app:
        shutil.rmtree(private)
        (args.output/'cleanup.json').write_text(json.dumps(dict(disposable_state_removed=not private.exists()))+'\n')
    print(json.dumps(result, indent=2))
    if code:
        raise SystemExit(code)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--upstream", default="sv.electrumr.sv", choices=["sv.electrumr.sv", "sv2.electrumr.sv"])
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--fixture", action="store_true")
    p.add_argument("--bundled-app", type=Path)
    asyncio.run(run(p.parse_args()))


if __name__ == "__main__":
    main()
