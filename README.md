# Electrum wallet privacy research

One normal ElectrumSVP account discloses a collection of wallet interests to its main serving operator. That operator can retain the queried script hashes together with the connecting IP/session, reconstruct the associated ledger, identify wallet-associated outputs, and keep watching unused hashes after the wallet disconnects.

**Research date: October 28, 2026. Private repository.** This evaluates what a covert operator can collect, without relying on promises about logging defaults, deletion, or acceptable use.

## What was actually demonstrated

| Experiment | Actual components | Result |
| --- | --- | --- |
| Live endpoint observation | Unchanged ElectrumSVP 0.2.0 `Wallet`/`Network`, fresh BIP39 account, recording TLS relay, bundled `sv.electrumr.sv` endpoint | One session disclosed 40 distinct script hashes. The unfunded account had zero transaction history. |
| Controlled financial dossier | Unchanged ElectrumSVP wallet/network/signing code, recording TLS endpoint, explicitly manufactured Electrum protocol ledger | One wallet session disclosed 47 scripts and four transactions. Capture-only reconstruction recovered the payment, fee, change and remaining balance. |
| Parallel verification disclosure | Exact upstream `electrum_request` function, eight controlled local TLS peers | All eight peers received the same transaction lookup before a winning response was returned. |
| Source provenance | Both bundled ElectrumR endpoints, documented source link, GitHub repository/releases lookup, publisher public-repository enumeration and repository/code search | Both endpoints advertised `ElectrumR 0.2.0`; no matching accessible public source or release artifact was found. |

**We did not self-host or modify an ElectrumR binary.** Its documented repository returned HTTP 404 publicly and through the operator's authenticated GitHub account. Consequently, the financial experiment uses an explicitly labeled local protocol fixture, **not ElectrumR**. It contains manufactured, unconfirmed funding transactions with fictional parents, not consensus-valid real-chain deposits. The outgoing transaction is signed by the real wallet and its BSV signatures are independently checked against the fixture prevouts. No real BSV was funded or spent.

The wallet runs headlessly using its actual account, SQLite storage, synchronization, RPC transport, coin selection, signing and broadcast code. This is a core-wallet network experiment, not a packaged-GUI qualification. Endpoint pinning, one-server mode and isolated application data are experimental controls; the entire configuration is not claimed to be stock. Default address discovery and transaction synchronization logic remain unchanged. See [the report](REPORT.md) for every material control and limitation.

## Financial dossier from the controlled session

These are **fixture satoshis with no monetary value**. The analyzer receives only `capture.jsonl`, not the seed, wallet database, derivation paths, expected amounts, or fixture server internals.

| Reconstructed observation | Amount/count |
| --- | ---: |
| Scripts associated with the wallet connection | 47 |
| Scripts resolved to concrete addresses from returned transactions | 4 |
| Retained unresolved script hashes | 43 |
| Transaction history | 4 transactions |
| Three incoming payments | 13,500,000 sats |
| Outgoing external payment | 5,000,000 sats |
| Transaction fee | 1,000 sats |
| Wallet-associated change | 2,999,000 sats |
| Remaining observed UTXOs | 8,499,000 sats |

The payment destination is `1QELJr58J6jUtMuqtjLMvePoRXmmdDZsJh`. The full addresses, outpoints, TXIDs, raw requests/responses, session identifiers and timestamps are in [the reconstructed dossier](evidence/fixture-attempt-04/dossier.json). The wallet independently reported the same final 8,499,000-sat balance in [its process log](evidence/fixture-attempt-04/wallet-process.log).

A [modeled later transaction](evidence/fixture-attempt-04/future-watch.json) also matches a previously unresolved subscribed hash after the wallet process exits. That illustrates persistent future monitoring without reversing SHA-256 or keeping the client online. It is explicitly a synthetic later ledger event, not a real blockchain confirmation.

## Read and reproduce

- [Detailed findings, trust model and provenance gap](REPORT.md)
- [All literal destinations, current IPs and hardcoded defaults](REPORT.md#hardcoded-destinations-and-current-network-observations)
- [Reproduction instructions](REPRODUCE.md)
- [Machine-readable verification results](evidence/verification.json)
- [Offline replay from a clean Git export without wallet files or site packages](evidence/clean-replay.json)
- [Raw live unfunded-wallet capture](evidence/live-attempt-02/capture.jsonl)
- [Raw controlled financial capture](evidence/fixture-attempt-04/capture.jsonl)
- [Eight-peer verification-helper capture](evidence/fanout-attempt-01/fanout.json)
- [Source discovery and live server identification](evidence/provenance-20261028/)
- [Attempt ledger, including failures](evidence/ATTEMPTS.md)

The unresolved work is a self-hosted, source-pinned ElectrumR run with consensus-valid local-chain funding and confirmed history. The absence of accessible server source is recorded as an audit/reproducibility limitation, not concealed by substituting another server implementation.
