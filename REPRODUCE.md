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


The default-core observation leaves `server`, `oneserver`, `auto_connect`, `proxy` and the server cache unset. It creates and removes a fresh unfunded wallet under ignored `.runtime/` state and directly contacts public endpoints. It records client-side RPC completions and successful helper TLS sends, not remote retention logs. It does not start the GUI or daemon FX task. Use a new output directory:

```bash
.venv/bin/python -m privacy_lab.default_session \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-default-core-run
```

The retained count and observation accounting can be checked offline with standard-library Python, without network access or any wallet files:

```bash
python3 -S -m privacy_lab.trust_model --verify
```

The verifier checks the canonical October 28 run, not an arbitrary future run. The model calculates literal pool intersections, attribution and conservative correlation groups separately, and checks network/DNS annotations against retained receipts. `source-receipts.json` records hashes of pinned wallet files reviewed for startup helper, automatic proof/BEEF, price, update and extension paths. The collector requires unchanged pinned source; evidence directories are retained rather than overwritten. Common ownership and actual data sharing remain unverified; the consumer sharing assumptions are explicit.


To repeat the strictly local three-wallet subscription/correlation scenario, use a new output directory:

```bash
.venv/bin/python -m privacy_lab.run_correlation \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-correlation-run
```

The actual wallets synchronize empty histories against loopback TLS with non-loopback sockets blocked. They exit before the harness manufactures the later ledger. The analyzer takes only the capture, raw ledger and one checkout address. The later unsigned transactions have fictional funding parents and no monetary value; no signing, confirmation, real-chain funding or ElectrumR claim is made. Runtime wallet/TLS state is removed on closeout.

Replay the canonical result and disclosure/source receipt checks without wallet files, site packages or network access:

```bash
python3 -S -m privacy_lab.verify_correlation
```

To collect the same bounded messaging audit into a fresh directory:

```bash
.venv/bin/python -m privacy_lab.disclosure_audit \
  --source /Users/tyeverett/projects/ElectrumSVP \
  --output evidence/my-disclosure-audit
```

Both pinned Git objects must be available locally: release `672df8f4` and the observed public-master snapshot `35b92ec9`. Fetching master supplied the latter without changing the detached release checkout. The collector reviews English source/UI/docs and six first-party public pages. Negative findings are bounded manual-review conclusions, not an automated score or a user-awareness survey. The canonical release-body summary was separately obtained through the GitHub connector. Newer master pools differ from the tested release; do not silently substitute them into the earlier counts or tests.

The public-discussion follow-up used the GitHub connector separately. Its retained search URLs include explicit issue/PR type filters; direct issue/comment GET URLs and narrow review summaries are preserved under `evidence/disclosure-audit-20261028/`. The first four rejected queries are retained alongside eight corrected queries. Search indexes are not an exhaustive awareness survey, and no public message was posted.

## October 29 package, certificate and valid-chain experiments

The full [package method](PACKAGED-WALLET.md) specifies the official DMG hash, PGP receipts, bundled runtime and isolation/GUI observation controls. Download and verify the artifact separately; it is not redistributed here. The operator authorized Rosetta installation on this Mac. Do not open an existing personal wallet or disable OS trust protections to reproduce a test. `create_packaged_wallet.py` creates only new ignored state; `packaged_bootstrap.py` launches the unchanged bundled entrypoint with isolated paths and optional client RPC observations. Its lab bundle wrapper/identity is an explicit control, not a vendor artifact. The source checkout passed to the other tools must remain pinned at `672df8f4512f6adf16a3c99146baa6be9b93d86f`.

With Docker already running, the pinned vendor image available and a clean disposable `.runtime/valid-chain` path, the node setup refuses to overwrite existing state:

```sh
.venv/bin/python -m privacy_lab.setup_node --output evidence/my-node-setup
.venv/bin/python -m privacy_lab.run_valid_chain --source /absolute/path/to/ElectrumSVP --output evidence/my-valid-chain
.venv/bin/python -m privacy_lab.replay_chain --evidence evidence/my-valid-chain --output evidence/my-clean-node-replay
.venv/bin/python -m privacy_lab.tls_matrix --source /absolute/path/to/ElectrumSVP --output evidence/my-tls-source
.venv/bin/python -m privacy_lab.proxy_boundary --source /absolute/path/to/ElectrumSVP --output evidence/my-proxy-boundary
```

For the bundled matrix, add `--bundled-app /absolute/path/to/ElectrumSVP-0.2.0.app` and set `--source` to its `Contents/usr/lib/python3.9/site-packages`. The controller uses the research virtual environment only to generate test certificates; every matrix client then uses the vendor interpreter and modules. All endpoints are loopback. No CA is installed system-wide. Ports are ephemeral; only the named Docker network/node and ignored private state belong to this experiment. Stop/remove only these owned resources after exporting evidence. Do not stop unrelated Docker workloads. The exact retained chain has 210 non-genesis blocks because failed experiment histories are preserved; a fresh successful run may need fewer blocks while producing the same controlled financial outcome.

Offline checks need only Python's standard library and no live server, wallet, Docker or network access. They include capture hash chains, controlled financial reconstruction, role accounting, the 18-claim ledger, all retained block hashes/linkage/PoW/Merkle roots, 36 TLS results, package/module observations and local evidence links. The consensus-node replay is separately retained; the offline verifier is not a new consensus implementation. Run `RESEARCH_PYTHON=python3 bash scripts/validate.sh`. The GitHub workflow runs the same command with read-only repository permissions and no stored checkout credentials. It does not recreate the live wallet experiments.

`scripts/export-release.py --ref COMMIT_OR_TAG --output .runtime/releases/candidate.tar.gz` creates a deterministic compressed Git archive with a reported SHA-256. It contains committed evidence and source only. Independent human replications and optional reader studies are invited through [OPEN-QUESTIONS](OPEN-QUESTIONS.md) and [CONTRIBUTING](CONTRIBUTING.md). Their results can extend or correct the published evidence; they are not publication prerequisites.

The final fresh-node setup recipe explicitly uses `blockassembler=LEGACY`, `par=1`, `maxparallelblocks=1` and `maxparallelblocksperpeer=1` as explicit requested mining/validation controls. The actual node log still identifies its assembler as JournalingBlockAssembler and reports eight script-verification threads; do not infer an effective legacy assembler or a wholly single-threaded process from the requested flags. A fresh default-assembler attempt stalled on the first local block; the original successful chain and independent raw-block replay remain separate evidence. The first limited-thread retry failed its dependent per-peer parameter gate; the corrected configuration mined 201 blocks with zero peers. These are research-node controls, not proposed public server defaults. Node RPC subprocesses now have a 60-second bound.
