# Operator-visible wallet dossier and the end-user trust model

Research date: 2026-10-28, America/Los_Angeles. Scope: a covert serving operator retaining everything available at its API boundary while a user follows the wallet's ordinary synchronization behavior. No reliance is placed on server logging defaults or retention promises.

## Source and deployment identification

The client is [TruthMachine/ElectrumSVP v0.2.0](https://github.com/TruthMachine/ElectrumSVP/releases/tag/v0.2.0), commit `672df8f4512f6adf16a3c99146baa6be9b93d86f`. Its source working tree remained unchanged. The runtime is CPython 3.10.20 on macOS arm64, BitcoinX 0.9 and aiorpcX 0.18.7. All resolved versions are in `requirements-wallet.lock.txt`. This is not an assertion that the published desktop binaries use exactly this environment.

The release's [priority server list](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/network.py#L1699-L1753) includes `sv.electrumr.sv:50002` and `sv2.electrumr.sv:50002`. Both answered ordinary public metadata RPCs and identified themselves as `ElectrumR 0.2.0`, protocol 1.4.2. The recorded endpoints resolved to `198.154.93.197` and `198.154.93.212`. DNS addresses and server identity strings are observations at the capture time, not permanent identifiers or attestations of the running binary. See [exact probes and certificate fingerprints](evidence/provenance-20261028/default-server-probes.json).

The [ElectrumR documentation](https://electrumr.io/docs.html) points to `https://github.com/KeyvanJS/ElectrumR` as the build source. That repository and its releases endpoint returned HTTP 404 through public retrieval and the operator's authenticated account. The publisher's public-repository list and scoped repository/code searches did not identify the advertised implementation. Direct Python retrieval of the website separately returned HTTP 403; those errors are retained, while the documentation and its GitHub link were readable through the web research tool.

**No matching accessible public ElectrumR source or build artifact was found in this investigation.** A website advertising a source link and MIT licensing does not make unavailable source auditable. This prevents independent inspection of the actual server implementation, reproducible builds, code-to-deployment comparison, inspection of undisclosed collection/forwarding, and the requested self-hosted instrumented run. It is an additional accountability and provenance gap on top of the protocol privacy exposure.

These observations do not establish that the implementation is legally proprietary, that source never existed, or that an operator actually misuses requests. A 404 alone cannot determine whether a repository was made private, deleted, renamed or is otherwise inaccessible. The available evidence also cannot determine the latest unpublished build; 0.2.0 is the version advertised by the two bundled endpoints on the research date.

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
