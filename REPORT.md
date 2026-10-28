# Operator-visible wallet dossier and the end-user trust model

Research date: 2026-10-28, America/Los_Angeles. Scope: a covert serving operator retaining everything available at its API boundary while a user follows the wallet's ordinary synchronization behavior. No reliance is placed on server logging defaults or retention promises.

## Source and deployment identification

The client is [TruthMachine/ElectrumSVP v0.2.0](https://github.com/TruthMachine/ElectrumSVP/releases/tag/v0.2.0), commit `672df8f4512f6adf16a3c99146baa6be9b93d86f`. Its source working tree remained unchanged. The runtime is CPython 3.10.20 on macOS arm64, BitcoinX 0.9 and aiorpcX 0.18.7. All resolved versions are in `requirements-wallet.lock.txt`. This is not an assertion that the published desktop binaries use exactly this environment.

The release's [priority server list](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1699-L1753) includes `sv.electrumr.sv:50002` and `sv2.electrumr.sv:50002`. Both answered ordinary public metadata RPCs and identified themselves as `ElectrumR 0.2.0`, protocol 1.4.2. The recorded endpoints resolved to `198.154.93.197` and `198.154.93.212`. DNS addresses and server identity strings are observations at the capture time, not permanent identifiers or attestations of the running binary. See [exact probes and certificate fingerprints](evidence/provenance-20261028/default-server-probes.json).

The [ElectrumR documentation](https://electrumr.io/docs.html) points to `https://github.com/KeyvanJS/ElectrumR` as the build source. That repository and its releases endpoint returned HTTP 404 through public retrieval and the operator's authenticated account. The publisher's public-repository list and scoped repository/code searches did not identify the advertised implementation. Direct Python retrieval of the website separately returned HTTP 403; those errors are retained, while the documentation and its GitHub link were readable through the web research tool.

**No matching accessible public ElectrumR source or build artifact was found in this investigation.** A website advertising a source link and MIT licensing does not make unavailable source auditable. This prevents independent inspection of the actual server implementation, reproducible builds, code-to-deployment comparison, inspection of undisclosed collection/forwarding, and the requested self-hosted instrumented run. It is an additional accountability and provenance gap on top of the protocol privacy exposure.

These observations do not establish that the implementation is legally proprietary, that source never existed, or that an operator actually misuses requests. A 404 alone cannot determine whether a repository was made private, deleted, renamed or is otherwise inaccessible. The available evidence also cannot determine the latest unpublished build; 0.2.0 is the version advertised by the two bundled endpoints on the research date.

## Hardcoded destinations and current network observations

The table below combines the eight literal core priority hosts in `network.py` with the eight literal verification-helper hosts in `verification_utils.py`: **nine unique hostnames**. The pool columns identify request paths; they do not imply every server received the complete wallet collection. A selected core main server receives core wallet subscriptions/history/broadcasts. A helper recipient receives copies of the individual helper RPCs that are invoked. Auxiliary core connections ordinarily receive protocol/header traffic rather than the entire subscription set.

Source locations: [core pool](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1699-L1753), [verification pool](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/verification_utils.py#L30-L44). Hostnames and ports are pinned source facts; the IP addresses and advertised software below are independent DNS/metadata observations collected on **2026-10-28 UTC**. All active literal entries use **TLS on port 50002**. We performed ordinary metadata RPCs only; no third-party wallet was queried.

| Hostname | Core priority pool | Verification helper | Port/transport | DNS addresses observed | Advertised server version |
| --- | --- | --- | --- | --- | --- |
| `bsv.aftrek.org` | Yes | Yes | `50002` / TLS | `128.140.53.204`, `2a01:4f8:c17:3e4c::1` | `ElectrumX 1.19.0` |
| `electrum.server.sv` | Yes | Yes | `50002` / TLS | `198.154.93.210` | `No successful identification; see raw error` |
| `electrumx.gorillapool.io` | Yes | Yes | `50002` / TLS | `99.127.49.102` | `ElectrumX 1.20.2` |
| `esv.bitails.io` | Yes | No | `50002` / TLS | `49.13.228.56` | `ElectrumX 1.20.2` |
| `sv.electrumr.sv` | Yes | Yes | `50002` / TLS | `198.154.93.197` | `ElectrumR 0.2.0` |
| `sv.satoshi.io` | Yes | Yes | `50002` / TLS | `198.154.93.195` | `ElectrumX 1.20.2` |
| `sv2.electrumr.sv` | Yes | Yes | `50002` / TLS | `198.154.93.212` | `ElectrumR 0.2.0` |
| `sv2.satoshi.io` | Yes | Yes | `50002` / TLS | `198.154.93.202` | `ElectrumR 0.2.0` |
| `sv3.satoshi.io` | No | Yes | `50002` / TLS | `198.154.93.200` | `ElectrumR 0.2.0` |

Raw [DNS answers, record types and TTLs](evidence/destinations-20261028/dns.json), [metadata RPC responses, connected peer addresses and certificate fingerprints](evidence/destinations-20261028/endpoint-metadata.json), and [literal source pools](evidence/destinations-20261028/source-destinations.json) are retained separately. DNS was not authenticated with DNSSEC. A DNS answer establishes a candidate address at the observation time; it does not establish a successful connection, long-term routing, operator identity, or ownership.

Four responding hostnames advertised **ElectrumR 0.2.0**: `sv.electrumr.sv`, `sv2.electrumr.sv`, `sv2.satoshi.io`, and `sv3.satoshi.io`. `electrum.server.sv` resolved but did not successfully identify itself during the bounded probe; that is not evidence it is permanently offline. Six of the nine names resolved to IPv4 addresses in `198.154.93.0/24`. This address grouping does not prove common ownership or independent operators. Different names, IPs and self-reported software versions do not attest different collection policies or independently controlled systems.

This is **not an exhaustive egress allowlist**. Cached/custom server objects and server-supplied peers with usable ports can expand the core pool. Main selection uses `random.choice` over eligible server objects, not a promise to choose the first listed hostname. In the retained live run, the main server also advertised these additional names:

| Advertised hostname | Server-advertised IP | Advertised transport flags | Acceptance in the tested client parser |
| --- | --- | --- | --- |
| `neptune.api.sv` | `195.144.22.198` | `s`, `t`, without numeric ports | Rejected |
| `electrum.api.sv` | `78.110.160.26` | `s`, `t`, without numeric ports | Rejected |

Those IPs are server-provided advertisements, not current DNS results or proof of connections. An [exact upstream parser check](evidence/destinations-20261028/peer-discovery-check.json) found that **all seven peers in that captured response were rejected**: bare `s`/`t` flags produced empty port strings rather than numeric ports in this client. The report does not silently supply default ports or claim those advertised servers received data in this run. Other peer responses containing explicit usable ports can still extend the pool. See [the parser](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1182-L1196).

There are also important differences between bundled configuration sources:

- `esv.bitails.io` is in the core priority pool but absent from the verification-helper pool.
- `sv3.satoshi.io` is in the helper pool but absent from the literal core priority pool.
- `electrum.api.sv`, `neptune.api.sv`, and `alpha-esv.api.sv` appear as **commented-out** entries in the examined pool code. Commented entries are not active literal defaults; advertisements or saved user state are separate paths.
- The fallback [mainnet `servers.json`](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/data/servers.json) literally contains `sv.electrumr.sv'` and `sv2.electrumr.sv'`, with trailing apostrophes. These must not be silently normalized in a provenance record. It lists TLS `s=50002` and, except for Bitails, optional plaintext `t=50001`, protocol label `1.4`, and pruning marker `-`. Import from that fallback is conditional on fewer than five known server objects after priority insertion; the eight valid priority entries ordinarily already exceed that threshold. Its presence does not prove the malformed hosts are contacted by a fresh default run.

## Relevant hardcoded default values

These are the reviewed release's fresh ordinary-desktop/mainnet values, rather than a dump of an existing user's configuration. Saved configuration, another network mode, an explicit server selection or a discovered peer can change destinations. The controlled experiments' endpoint pinning and one-server settings remain explicit deviations.

| Setting / source path | Default or literal value | Relevance |
| --- | --- | --- |
| `commands.add_network_options`: `server` | `None` | No user-pinned endpoint on a fresh configuration. |
| `Network._read_config` / `_random_server_nowait` | Random eligible server using protocol `s` | The selected main endpoint can vary. |
| `oneserver` / connection-loop target | `False` / **10** connection slots | This is a target, not proof ten distinct servers connected or all received address subscriptions. |
| `Network.auto_connect` | `True` | Main selection can move to another eligible endpoint after failure/lag. |
| `Network._read_config`: `proxy` | `None` | Ordinary desktop default connects directly. TAILS/helper Tor handling is separate. |
| Core pool fallback threshold | Fewer than **5** known server objects | Controls when bundled JSON entries are imported. |
| Startup main-server batch | `server.banner`, `server.donation_address`, `server.peers.subscribe` | The peer response can influence the known-server collection. |
| Client version / protocol range | `0.2.0` / `1.4` through `1.4.2` | Supplied in the version handshake. |
| Receiving / change lookahead | **20 / 20** | A fresh standard account initially monitors 40 scripts. |
| Enabled standard-account script type | `P2PKH` | Requests contain hashes of these output scripts. |
| Script identifier | Reversed hexadecimal `SHA256(locking_script)` | Matches the server's public-ledger index and future outputs. |
| `deactivate_used_keys` | `False` | Spent keys are not automatically removed from monitoring. |
| New-account seed / BIP39 passphrase | **12** words / empty string | Wallet-creation defaults; no generated seed is published in this research. |
| Mainnet BIP44 coin type / account 0 | **0** / `m/44'/0'/0'` | Source wizard default; receiving/change suffixes are local wallet structure. |
| Change / multiple-change settings | `True` / `True`; `max_change_outputs=10` | These affect which wallet-associated outputs may appear. |
| Fee-rate fallback | `DEFAULT_FEE=105` sats/kB | The experiment's fixed **1,000-sat total fee** is a scenario control, not this default rate. |
| Script subscription retry loop | **3** attempts, **2** seconds between temporary-failure retries | Repeated requests can expose the same identifiers again. |
| Per-server connect retry loop | Up to **6** attempts, **10**-second failure sleeps | Failed connectivity can lead to retries and later main-server changes. |
| Verification helper default pool / workers | `SERVERS` / `len(server_items)`; **8** peers here | Parallel copies may reach several operators. |
| Verification helper socket timeout | `TIMEOUT=5` seconds | Bounds each connect/read stage, not a deletion/retention window. |
| Helper Tor endpoint / detection probe | `127.0.0.1:9050` / **1** second | Helper independently selects SOCKS5 on TAILS or when a local Tor daemon responds. |
| Core connector TLS context | `ssl.SSLContext(ssl.PROTOCOL_TLS)` | In the tested Python 3.10 runtime: **`CERT_NONE`, `check_hostname=False`**. |
| Verification helper TLS context | `ssl._create_unverified_context()` | Certificate and hostname authentication are disabled on this path. |

The core constructor is visible [here](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L296-L307); the helper context and independent Tor choice are visible [here](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/verification_utils.py#L335-L410). We separately evaluated the core constructor's verification flags in the recorded research runtime. The presence of `certifi` imports or bundled PEM files does not establish that this connector enables verification. This is a source/runtime observation, not a staged MITM or a packaged-binary audit. TLS encryption on these paths should not be described as proof of an authenticated operator identity.

Further source anchors: [CLI defaults](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/commands.py#L294-L301), [connection slots](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1573-L1587), [automatic switching](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L2007-L2008), [subscription retries](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1096-L1117), [account discovery](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L2208-L2221), [standard scripts](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L2261-L2272), [account creation](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/account_wizard.py#L427-L447), [mainnet derivation](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/networks.py#L74-L87), [change policy](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L1455-L1474), and [fee fallback](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/simple_config.py#L276-L282).

## What one connection directly reveals

The wallet sends [all active script subscriptions for each loaded account through the main session](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1886-L1909). A standard account generates a [20-key lookahead](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L418-L419) on [both receiving and change chains](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L2208-L2221). Default deactivation of spent keys is [disabled](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L1853-L1861).

Every request arriving on that socket already has a session association. The operator need not guess address ownership from a common IP or wait for on-chain co-spending. It can preserve the collection of queried interests, client version/protocol parameters, timing, raw request arguments, returned histories and transaction bodies, and submitted broadcasts. Multiple loaded accounts can share that connection; the protocol need not reveal their local account names or boundaries.

The wallet sends [reversed SHA-256 hashes of locking scripts](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/bitcoin.py#L238-L243). These are the same identifiers used to index the ledger. A funded script can be identified by hashing publicly available outputs; an unused hash can remain on a watchlist until an output with a matching script appears. An operator does not have to invert SHA-256. Stable script collections can also associate later sessions after IP changes.

The [default ordinary-desktop proxy is absent](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1747-L1753). A serving operator therefore also ordinarily sees the client's connecting network address. In this local capture the instrumented frontend sees `127.0.0.1`, because we intentionally used a loopback relay; this is not a capture of a victim's residential IP or an identity-deanonymization experiment.

The wallet normally targets ten connections, but core address subscriptions go to its main session. It would be incorrect to claim all ten auxiliary connections necessarily receive the same address set. Main-server switching can disclose it to additional operators over time.

## Observed live run

`evidence/live-attempt-02/` contains a real fresh-wallet network run against the bundled `sv.electrumr.sv` endpoint behind a local recording TLS relay. The source's actual Wallet, StandardAccount, SQLite storage, ASync thread, Network, SVSession and aiorpcX transport ran. The wallet generated 40 monitored scripts and sent them on one connection. All were reported empty. The source supplied `0.2.0` as the client version, rather than an explicit ElectrumSVP product string.

The relay is operator-equivalent instrumentation at a serving frontend: it terminates TLS as the selected server and forwards the decrypted RPC stream. It is not an interception of a third party's TLS session, and it does not inspect the public server's internal logs or memory. That endpoint's source and binary remain unaudited. The live zero-balance run establishes actual client disclosure to an endpoint advertising ElectrumR, not a funded live-chain dossier.

## Controlled financial reconstruction

`evidence/fixture-attempt-04/` uses the same upstream wallet core, with a clearly identified local protocol fixture. The fixture advertises `CONTROLLED_PROTOCOL_FIXTURE_NOT_ELECTRUMR`. It supplies three manufactured unconfirmed funding transactions for 8,000,000, 3,500,000 and 2,000,000 sats to receiving scripts 0, 1 and 5. These transactions have fictional parents and are not real-chain funding. No Merkle inclusion or fabricated confirmations are supplied. Genuine shipped header responses are used only to initialize the normal mainnet header/network path.

The real wallet discovers the transactions, retrieves their serialized bodies, selects the 8,000,000-sat UTXO, creates a 5,000,000-sat external payment with a specified 1,000-sat fee, signs it, and submits its full transaction through the normal broadcast path. The fixture verifies the BSV input signatures against the known fixture prevouts before adding it to the modeled ledger and sending status notifications. This verifies signing against supplied prevouts; it does not validate the fictional funding ancestry or establish real-network acceptance.

The actual main wallet session is session 2; session 1 is a separate startup header helper. The main session reveals 47 distinct script hashes as the rolling lookahead advances: receiving scripts through index 25 and change scripts through index 20. The operator's dossier does not receive these derivation labels; they explain the count using fixture ground truth only.

| Capture-derived fact | Result |
| --- | ---: |
| Incoming transactions / total received | 3 / 13,500,000 sats |
| Submitted outgoing transaction | `75851e189bf0c97d82a17ea0abfbb671ef5c8db407c279bf4cfd252b25211385` |
| External destination | `1QELJr58J6jUtMuqtjLMvePoRXmmdDZsJh` |
| External payment | 5,000,000 sats |
| Wallet-associated input | 8,000,000 sats |
| Wallet-associated change | 2,999,000 sats |
| Fee | 1,000 sats |
| Remaining modeled balance | 8,499,000 sats across 3 UTXOs |
| Resolved / unresolved monitored scripts | 4 / 43 |

`privacy_lab.dossier` is a separate program with **only the raw capture path as its input**. It cannot read wallet files, seed words, derivation paths, the fixture object, or the expected scenario. It decodes raw transactions, verifies their TXIDs, matches output-script hashes to the queried set, resolves available prevouts and performs integer-satoshi arithmetic. Missing input data produces an unknown fee, not zero. Rejected broadcast attempts remain in the dossier but are excluded from the accepted balance. Request IDs are scoped to their connection, and captured statuses are checked against history digests before marking a response-consistent balance complete.

“Complete” here means consistent with the captured responses for the observed script collection. It is not proof that a server disclosed every real-chain transaction. The fixture's independent expected amounts and the actual wallet's final balance both match the reconstruction. Full evidence, addresses, outpoints and timestamps are retained. Capture journals also preserve exact newline-delimited wire bytes and a hash chain. Hash chains detect unrecomputed edits, not a malicious author's ability to rewrite an entire journal.

After the wallet exits, a separate manufactured 1,700,000-sat transaction pays to a script previously present only as an unresolved hash. Matching its output against the retained subscription set resolves the new address without reopening the wallet. `future-watch.json` records this modeled post-session event separately from the session's four-transaction balance.

## Automatic verification can disclose to additional servers

After storing a transaction proof, [`Wallet.add_transaction_proof`](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/wallet.py#L3011-L3083) attempts automatic BREAD/BEEF construction. Its helper can retrieve missing transaction bodies and Merkle proofs through [`verification_utils.electrum_request`](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/verification_utils.py#L335-L500). That function starts requests to the hardcoded server collection concurrently and returns the first successful response. Returning early does not retract copies already delivered to other recipients.

The controlled helper test executed the exact upstream function against eight local TLS peers. A barrier made each recipient retain the request before any could answer. All eight retained the same `blockchain.transaction.get` request. This is a separate method-level socket experiment, not evidence that every funded GUI action always sends every request to eight public peers. Whether a particular transaction lookup occurs depends on available local transaction/proof data and the invoked verification path.

The helper independently decides whether to use Tor based on TAILS or a local daemon at port 9050. It does not consult `app_state.config` for the main network's arbitrary proxy or selected server. Thus selecting a private main server or setting a different main-network proxy does not, by that configuration alone, constrain this helper's destinations. The helper's TLS context also disables certificate validation. The controlled test demonstrates fanout; the proxy-setting separation is a source finding, not a full anonymity-leak test on TAILS or every platform.

## Trust implications and boundaries

An operator can associate queried scripts, reconstruct histories and holdings for them, identify external transaction destinations, infer which outputs return to the observed collection, retain precise query/broadcast timing, and maintain a future watchlist. This collection can be sold, shared or combined with an exchange's identity records without any wallet software change. The experiments demonstrate collection capability, not a claim that the observed public operators perform those actions.

An address-query association is evidence of interest, not cryptographic ownership. Watch-only wallets, external lookups, shared devices, NAT, VPNs and shared public IPs complicate attribution. The operator cannot infer a legal name, salary, business purpose, private labels, cost basis or profit from this API alone. The ordinary requests do not transmit the mnemonic, private keys or an xpub for unlimited future derivation. Monitored lookahead hashes are different from access to the entire unlimited HD tree.

TLS protects traffic between endpoints but exposes requests to the serving operator. SPV inclusion checks concern transaction authenticity, not query privacy or proof of absence. A correctly functioning Tor route can conceal the original connecting IP from that destination while leaving the queried script collection linkable. Any privacy recommendation must also account for the separate verification helper.

The default trust model therefore includes a remote operator's discretion over an IP/session-associated financial dossier. Accessible source and reproducible deployment provenance would permit more implementation auditing, but would not remove the underlying request disclosure or prove that an operator runs the published code without added collection.

## Outstanding exact-system reproduction

To complete the originally requested self-hosted ElectrumR experiment: obtain source and build provenance for the deployed implementation; build a pinned instrumented server; establish isolated BSV/regtest compatibility with a source-pinned node; fund a controlled wallet with consensus-valid local-chain transactions; demonstrate confirmed and unconfirmed history, a signed payment and recovery through that server; and reconstruct its dossier from server evidence alone. This investigation does not mark those unperformed steps as passed.
