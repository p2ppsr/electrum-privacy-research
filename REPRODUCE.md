# Reproduce the retained experiments

Use Python 3.10 and an unchanged checkout of [ElectrumSVP v0.2.0](https://github.com/TruthMachine/ElectrumSVP/tree/672df8f4512f6adf16a3c99146baa6be9b93d86f). Verify commit `672df8f4512f6adf16a3c99146baa6be9b93d86f` and a clean source working tree before running. The scripts accept an existing source checkout; they do not silently substitute another client.

The retained runtime used macOS arm64, CPython 3.10.20, and the full package versions in `requirements-wallet.lock.txt`. OpenSSL is required to generate disposable local TLS certificates. Source-wallet GUI dependencies are installed even though the GUI is not opened. There is no cluster deployment, Linux image build, or paid provider dependency.

```bash
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -r requirements-wallet.lock.txt
.venv/bin/python -m unittest discover -s tests -v
```

Rebuild the retained dossiers and verify expected amounts without wallet runtime access or any network connection:

```bash
.venv/bin/python -m privacy_lab.verify_evidence \
  --live evidence/live-attempt-02 \
  --fixture evidence/fixture-attempt-04 \
  --fanout evidence/fanout-attempt-01/fanout.json \
  --output evidence/verification.json
```

The journal reader checks the record hash chain, wire/JSON agreement, request/response scoping, transaction IDs, and history/status consistency. The independent verifier asserts the three incoming amounts, payment, fee, remaining balance, eight helper recipients and post-session watchlist match. It does not assert real-chain funding.

Run a new controlled wallet/fixture experiment using a **new output directory**:

```bash
.venv/bin/python -m privacy_lab.run_live \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-fixture-run --fixture
```

The fixture mode blocks non-loopback socket connections in the wallet process and redirects verification-helper endpoints locally. It generates a fresh BIP39 account and signs a payment against manufactured unconfirmed prevouts. It is not an ElectrumR server or a consensus-valid local blockchain. Never present its fabricated funding or later watchlist event as real BSV activity.

The fixture path preserves normal lookahead, P2PKH, key activation, synchronization, transaction retrieval, signing and broadcast code. Material controls are: headless app callbacks; a pinned loopback TLS endpoint; `oneserver=True`; `auto_connect=False`; isolated paths; helper routing; a chosen 8,000,000-sat UTXO; a scripted 5,000,000-sat recipient; and `fixed_fee=1000`. The mainnet account uses the source wizard's BIP44 coin type 0, not an assumed coin type 236. Source files and consensus checks are not patched. Transaction names and receiving/change derivation labels are fixture ground truth, not information fed to the dossier analyzer.

Optionally repeat the actual public-endpoint observation with another fresh **unfunded** account:

```bash
.venv/bin/python -m privacy_lab.run_live \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-live-run
```

This explicitly contacts `sv.electrumr.sv:50002`; startup header validation can also contact the hardcoded helper peers as the original source does. The selected public operator sees the research host's connecting IP. The local journal records the local client's loopback peer address. The relay does not verify the upstream certificate, and the upstream's advertised version is not binary attestation. Source, runtime and endpoint controls differ from a packaged wallet with every setting left untouched. No existing user wallet is opened.

Repeat source discovery or the exact-function fanout check:

```bash
.venv/bin/python -m privacy_lab.provenance \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-provenance-check
.venv/bin/python -m privacy_lab.fanout \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-fanout-check
```

Each new experiment creates ignored `.runtime/<output-directory-name>/` state: disposable wallet data, seed, header copies and TLS private keys. These are excluded from Git and never supplied to reconstruction. Use unique directory names, never fund generated accounts on a real chain, and remove that run's disposable state after reviewing the evidence. Captures contain only the controlled experiment's public scripts, transactions and protocol metadata; do not substitute production wallets or collect uninvolved clients.

The remaining self-hosted ElectrumR experiment requires an accessible source/build artifact and an isolated consensus-valid chain setup. This repository deliberately does not disguise the fixture as that missing implementation.

To refresh the nine literal destinations and collect ordinary public DNS/metadata responses, use a new directory:

```bash
.venv/bin/python -m privacy_lab.destinations \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-destination-check
```

The report distinguishes the source pools from DNS, connected peer addresses, self-reported versions, saved/discovered peers and malformed fallback entries. Metadata probes contain no wallet addresses or transactions.

The attribution/source/liveness follow-up can be inspected offline without any wallet, network access or third-party Python packages:

```bash
python3 -S -m privacy_lab.verify_followup
```

To collect new public snapshots, use unique output directories (the collectors refuse overwrites):

```bash
.venv/bin/python -m privacy_lab.ownership --output evidence/my-ownership-check
.venv/bin/python -m privacy_lab.server_sources --output evidence/my-source-check
.venv/bin/python -m privacy_lab.liveness --output evidence/my-liveness-check
```

Ownership collection queries public registration/routing/DNS records, official sites and the existing nine TLS endpoints. It omits individual registry-contact names, street addresses, phone numbers and mailbox details from retained registry summaries. Source discovery queries public repository/code indexes and obtains narrow facts from pinned public files; inaccessible repositories, failed queries and inconclusive archive responses remain explicit. The public profile name/company fields are self-declarations, not legal-identity attestations.

Liveness collection performs two bounded rounds, ten seconds apart, against the nine literal TLS endpoints. It sends only version, header-subscription and ping methods, and brackets observations with public Bitails/WhatsOnChain chain-info responses. It distinguishes reachability, protocol replies and apparent current tip. It does not query wallets, validate complete chains, establish an uptime SLA, or prove historical indexing completeness. The retained verifier deliberately checks the October 28 canonical snapshots; a new snapshot requires review and updated expected observations before being substituted into the report.
