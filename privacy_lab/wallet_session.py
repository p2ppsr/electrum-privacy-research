"""Launch a real upstream Wallet/Network against the selected research TLS endpoint.

Defaults for address discovery, script types, history and transaction handling are
unchanged. Endpoint pinning, one-server mode, application-directory isolation and
headless application callbacks are explicit experimental controls, not defaults.
"""
import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
import shutil
import sys
import threading
import time


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--state", type=Path, required=True)
    p.add_argument("--port", type=int, required=True)
    p.add_argument("--timeout", type=int, default=150)
    p.add_argument("--fixture", action="store_true")
    p.add_argument("--empty-local", action="store_true",
                   help="unfunded loopback-only observation for correlation research")
    args = p.parse_args()
    args.state.mkdir(parents=True, exist_ok=False)
    # Redirect only the wallet's hardcoded ~/.electrum-sv path. Never open the
    # operator's real wallet directories; do not change the process HOME variable.
    original_expanduser = os.path.expanduser
    def isolated_expanduser(value):
        if isinstance(value, str) and value.startswith("~/.electrum-sv"):
            return str(args.state / "legacy-home") + value[len("~/.electrum-sv"):]
        return original_expanduser(value)
    os.path.expanduser = isolated_expanduser
    sys.path.insert(0, str(args.source))
    logging.basicConfig(level=logging.WARNING)
    from electrumsv.simple_config import SimpleConfig
    from electrumsv.app_state import AppStateProxy, DefaultApp
    from electrumsv.storage import WalletStorage
    from electrumsv.wallet import Wallet
    from electrumsv import keystore
    from electrumsv.mnemonic import generate_bip39_seed
    from electrumsv.network import Network
    from electrumsv.bitcoin import scripthash_hex
    from electrumsv.keystore import bip44_derivation_cointype
    from electrumsv.networks import Net
    if args.fixture or args.empty_local:
        # Keep manufactured ledger data entirely local, including verification helpers.
        from electrumsv import verification_utils
        verification_utils.SERVERS = {"127.0.0.1": {"s": args.port}}
        def local_only(event, values):
            if event == "socket.connect" and isinstance(values[1], tuple):
                if values[1][0] not in ("127.0.0.1", "::1"):
                    raise PermissionError("fixture mode blocks non-loopback connections")
        sys.addaudithook(local_only)
    config_dir = args.state / "config"
    config = SimpleConfig(dict(electrum_sv_path=str(config_dir),
        server=f"127.0.0.1:{args.port}:s", oneserver=True, auto_connect=False))
    app = AppStateProxy(config, "cmdline")
    app.set_app(DefaultApp())
    app.app.run_in_thread = lambda fn, *a: threading.Thread(target=fn, args=a, daemon=True).start()
    shutil.copyfile(args.source / "electrumsv/resources/headersloaded/headers", config_dir / "headers")
    seed = generate_bip39_seed(12)
    # This fresh, unfunded wallet is disposable; recovery material stays ignored.
    (args.state / "seed.txt").write_text(seed)
    os.chmod(args.state / "seed.txt", 0o600)
    app.async_.__enter__()
    wallet = network = None
    try:
        storage = WalletStorage.create(str(args.state / "wallet"), "disposable-research-wallet")
        wallet = Wallet(storage)
        ks = keystore.from_bip39_seed(seed, "", bip44_derivation_cointype(Net.BIP44_COIN_TYPE, 0))
        ks.update_password("disposable-research-wallet")
        account = wallet.create_account_from_keystore(ks)
        account.synchronize()
        truth = [dict(key=k, derivation=list(account._keypath[k]),
                      script=bytes(script).hex(), scripthash=scripthash_hex(script))
                 for k in account.existing_active_keys()
                 for _,script in account.get_possible_scripts_for_id(k)]
        (args.state / "ground-truth.json").write_text(json.dumps(truth, indent=2))
        network = Network()
        wallet.start(network)
        deadline = time.monotonic() + args.timeout
        sent, next_progress = False, 0
        while time.monotonic() < deadline:
            if time.monotonic() > next_progress:
                print(json.dumps(dict(progress=True,connected=network.is_connected(),
                    responses=account.response_count,balance=sum(u.value for u in account.get_utxos()),sent=sent)),flush=True)
                next_progress = time.monotonic()+10
            if network.future.done():
                network.future.result()
                raise RuntimeError("network task exited")
            if network.is_connected() and account.response_count >= len(truth):
                if args.fixture:
                    if not sent:
                        if sum(u.value for u in account.get_utxos()) != 13_500_000:
                            time.sleep(0.1)
                            continue
                        from bitcoinx import Script
                        from electrumsv.transaction import XTxOutput
                        from privacy_lab.fixture import RECIPIENT_SCRIPT
                        coins = [u for u in account.get_utxos() if u.value == 8_000_000]
                        tx = account.make_unsigned_transaction(coins,
                            [XTxOutput(5_000_000, Script(bytes.fromhex(RECIPIENT_SCRIPT)))],
                            config, fixed_fee=1000)
                        account.sign_transaction(tx, "disposable-research-wallet")
                        if not tx.is_complete():
                            raise AssertionError("controlled wallet failed to sign")
                        network.broadcast_transaction_and_wait(tx)
                        sent = True
                    if sum(u.value for u in account.get_utxos()) != 8_499_000:
                        time.sleep(0.1)
                        continue
                time.sleep(2)
                result = dict(status="PASS", connected=True, initial_scripts=len(truth),
                              response_count=account.response_count, wallet_source_unchanged=True)
                if args.fixture:
                    result["fixture_wallet_balance_sats"] = sum(u.value for u in account.get_utxos())
                (args.state / "result.json").write_text(json.dumps(result, indent=2))
                print(json.dumps(result))
                return
            time.sleep(0.2)
        raise TimeoutError(f"wallet sync timeout: connected={network.is_connected()}, responses={account.response_count}")
    finally:
        if wallet is not None and not wallet._stopped:
            wallet.stop()
        if network is not None:
            async def quiesce():
                await network.shutdown_wait()
                await asyncio.sleep(0.2)
                leftovers = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()
                             and getattr(t.get_coro(), "__qualname__", "") != "ASync._wait_until_stopped"]
                for task in leftovers:
                    task.cancel()
                await asyncio.gather(*leftovers, return_exceptions=True)
            app.async_.spawn_and_wait(quiesce, timeout=15)
        app.async_.__exit__(None, None, None)


if __name__ == "__main__":
    main()
