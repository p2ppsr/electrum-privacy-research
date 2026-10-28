"""Observe an unfunded upstream core session with network settings left unset.

This is a client-side observer, not server-side receipt evidence or a GUI run.
Only a freshly generated disposable wallet is opened. No real funds are used.
"""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import shutil
import ssl
import sys
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=int, default=35, choices=range(20, 61))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    state = Path(".runtime") / args.output.name
    state.mkdir(parents=True, exist_ok=False)
    original_expanduser = os.path.expanduser

    def isolated_expanduser(value):
        if isinstance(value, str) and value.startswith("~/.electrum-sv"):
            return str(state.resolve() / "legacy-home") + value[len("~/.electrum-sv"):]
        return original_expanduser(value)

    os.path.expanduser = isolated_expanduser
    sys.path.insert(0, str(args.source))
    logging.basicConfig(level=logging.WARNING)
    from electrumsv.simple_config import SimpleConfig
    from electrumsv.app_state import AppStateProxy, DefaultApp
    from electrumsv.storage import WalletStorage
    from electrumsv.wallet import Wallet
    from electrumsv import keystore, verification_utils
    from electrumsv.mnemonic import generate_bip39_seed
    from electrumsv.network import Network, SVSession, SVServer
    from electrumsv.keystore import bip44_derivation_cointype
    from electrumsv.networks import Net

    events = []
    lock = threading.Lock()

    def record(**fields):
        with lock:
            row = dict(sequence=len(events) + 1,
                       utc=datetime.now(timezone.utc).isoformat(), **fields)
            events.append(row)
            with (args.output / "events.jsonl").open("a") as out:
                out.write(json.dumps(row) + "\n")

    original_request = SVSession.send_request

    async def observed_request(session, method, args=(), *positional, **kw):
        fields = dict(path="core", host=session.server.host, method=method, params=args)
        record(event="rpc_attempt", **fields)
        try:
            result = await original_request(session, method, args, *positional, **kw)
        except BaseException as exc:
            record(event="rpc_error", error=type(exc).__name__, **fields)
            raise
        record(event="rpc_completed", result_type=type(result).__name__, **fields)
        return result

    SVSession.send_request = observed_request
    original_connect = SVServer.connect

    async def observed_connect(server, network, slot):
        record(event="core_connect_attempt", host=server.host, port=server.port, slot=slot)
        return await original_connect(server, network, slot)

    SVServer.connect = observed_connect
    original_sendall = ssl.SSLSocket.sendall

    def observed_sendall(stream, data, *positional, **kw):
        result = original_sendall(stream, data, *positional, **kw)
        try:
            message = json.loads(bytes(data))
        except (ValueError, UnicodeDecodeError):
            return result
        if isinstance(message, dict) and "method" in message:
            record(event="helper_tls_send_completed", path="helper",
                   host=stream.server_hostname, method=message["method"],
                   params=message.get("params", []))
        return result

    ssl.SSLSocket.sendall = observed_sendall
    original_helper = verification_utils.electrum_request

    def observed_helper(method, params, servers=None):
        record(event="helper_invoked", method=method, params=params)
        try:
            result = original_helper(method, params, servers)
        except BaseException as exc:
            record(event="helper_error", method=method, error=type(exc).__name__)
            raise
        record(event="helper_returned", method=method)
        return result

    verification_utils.electrum_request = observed_helper
    # No server, oneserver, auto_connect, proxy, or server-cache setting is supplied.
    config = SimpleConfig(dict(electrum_sv_path=str(state.resolve() / "config")))
    app = AppStateProxy(config, "cmdline")
    app.set_app(DefaultApp())
    app.app.run_in_thread = lambda fn, *a: threading.Thread(target=fn, args=a, daemon=True).start()
    app.async_.__enter__()
    wallet = network = None
    result = dict(status="INCOMPLETE", no_real_funds=True, gui_observed=False,
                  financial_helper_fanout_observed=False,
                  observer="client-side RPC completions and successful TLS send calls; not server logs",
                  controls=["headless app callbacks", "isolated application data", "fresh unfunded BIP39 wallet", "client observation wrappers"],
                  network_settings_supplied=[], observation_seconds=args.seconds)
    record(event="run_started", **result)
    try:
        password = "disposable-research-wallet"
        seed = generate_bip39_seed(12)
        storage = WalletStorage.create(str(state.resolve() / "wallet"), password)
        wallet = Wallet(storage)
        ks = keystore.from_bip39_seed(seed, "", bip44_derivation_cointype(Net.BIP44_COIN_TYPE, 0))
        ks.update_password(password)
        account = wallet.create_account_from_keystore(ks)
        account.synchronize()
        network = Network()
        wallet.start(network)
        deadline = time.monotonic() + args.seconds
        while time.monotonic() < deadline:
            if network.future.done():
                network.future.result()
                raise RuntimeError("network task exited")
            time.sleep(0.2)
        result.update(status="PASS" if account.response_count >= 40 else "PARTIAL",
                      wallet_response_count=account.response_count,
                      observed_balance_sats=sum(u.value for u in account.get_utxos()),
                      main_server_at_end=network.main_server.host,
                      connected_servers_at_end=sorted({s.server.host for s in network.sessions}),
                      network_target_connections=1 if config.get("oneserver") else 10,
                      auto_connect=network.auto_connect(), proxy=str(network.proxy))
    except BaseException as exc:
        result.update(status="ERROR", error=repr(exc))
        raise
    finally:
        try:
            if wallet is not None and not wallet._stopped:
                wallet.stop()
            if network is not None:
                async def quiesce():
                    await network.shutdown_wait()
                    await asyncio.sleep(0.2)
                    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()
                             and getattr(t.get_coro(), "__qualname__", "") != "ASync._wait_until_stopped"]
                    for task in tasks:
                        task.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
                app.async_.spawn_and_wait(quiesce, timeout=15)
            app.async_.__exit__(None, None, None)
        finally:
            core = [e for e in events if e["event"] == "rpc_completed"]
            helper = [e for e in events if e["event"] == "helper_tls_send_completed"]
            result.update(core_completed_hosts=sorted({e["host"] for e in core}),
                          core_connect_attempt_hosts=sorted({e["host"] for e in events if e["event"] == "core_connect_attempt"}),
                          helper_sent_hosts=sorted({e["host"] for e in helper}),
                          helper_methods=dict(Counter(e["method"] for e in helper)),
                          financial_query_hosts=sorted({e["host"] for e in core + helper if e["method"].startswith(("blockchain.scripthash.", "blockchain.transaction."))}),
                          subscribed_script_counts={h:len({e["params"][0] for e in core if e["host"] == h and e["method"] == "blockchain.scripthash.subscribe"}) for h in {e["host"] for e in core if e["method"] == "blockchain.scripthash.subscribe"}})
            shutil.rmtree(state)
            result["disposable_state_removed"] = not state.exists()
            (args.output / "run.json").write_text(json.dumps(result, indent=2) + "\n")
            print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
