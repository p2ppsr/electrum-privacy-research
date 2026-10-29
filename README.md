# Electrum privacy research

**Private prepublication research — October 28–29, 2026.** What can a serving operator retain and correlate when people use ElectrumSVP 0.2.0? This studies technical capability, independently of logging defaults or retention promises. It does not establish actual surveillance by a named service.

Start with **[the plain-English shopkeeper story](EXPLAINER.md)**: one checkout address can name a wider wallet-associated profile; changing servers cannot revoke identifiers already disclosed.

| Completed experiment | Result and scope |
| --- | --- |
| [Official macOS package](PACKAGED-WALLET.md) | PGP/checksum verified. Desktop session with network settings unset completed 40 subscriptions to its main service, with seven core and seven helper hosts observed. 145 shared Python modules have identical parsed code to the release tag. |
| [Valid-chain shop](VALID-CHAIN.md) | Actual wallets signed, node-confirmed payments on isolated BSV regtest. One checkout anchor plus observer A's saved requests reconstructed 9,450,000 sats gross and 8,349,000 remaining, including activity after all shop routes moved to B. |
| [Fresh-state replay](evidence/chain-clean-replay-attempt-03/result.json) | Another empty node accepted all 210 blocks, reproduced the tip, and rejected bad Merkle-root and invalid-signature controls. Same implementation; no independent human replication claim. |
| [Certificate matrix](CERTIFICATES.md) | Source and bundled core/helper accepted wrong-host, self-signed and expired certificates; verified controls rejected them. Plaintext endpoints were rejected. No system trust store change. |
| [Proxy boundary](MITIGATIONS.md) | Core used the supplied SOCKS connector; the separately invoked helper succeeded directly. The captured GUI assurance says proxy settings apply to all connections. |
| [Earlier fixtures and fanout](REPORT.md) | Retained synthetic-ledger reconstruction and exact helper delivering one lookup to eight controlled TLS peers. They remain labeled separately from the later valid-chain experiment. |

The receiving main service can retain the active identifier collection, connection metadata and financial RPCs. Auxiliary core peers ordinarily see generic protocol/header traffic. Helpers see the particular lookups invoked; not every helper automatically gets the entire wallet. [Trust-party counts, infrastructure and who sees what](TRUST-MODEL.md).

The tested release has eight core and eight helper names, a nine-name union, with six names in `198.154.93.0/24`. The conservative consumer model assumes shared-segment correlation and considers all-provider pooling. This is an explicit threat assumption; common legal ownership and actual sharing are unproved. The newer master has different pools and remains separately versioned.

**Matching ElectrumR source/build remains unavailable.** Its documented repository again returned 404 on October 29. We did not self-host or attest an ElectrumR binary. The valid-chain serving component is an explicitly named research adapter over a consensus-validating BSV node. No real-chain funds, real merchant or production user were involved. A finite observed collection does not expose an unlimited HD tree or prove a legal person's ownership of everything queried.

Read [the technical report](REPORT.md), [claim-to-evidence ledger](CLAIMS.md), [persistent correlation](PERSISTENT-CORRELATION.md), [disclosure audit](DISCLOSURE-AUDIT.md), [related work](RELATED-WORK.md), and [reproduction instructions](REPRODUCE.md). The [October 29 liveness table](evidence/liveness-20261029/liveness-table.md) appends bounded observations without overwriting October 28 samples.

[Publication readiness](PUBLICATION-READINESS.md) tracks remaining human review, [right-of-reply drafts](REVIEW-PACKET.md) and [reader-study preparation](READER-STUDY.md). No outreach, user-comprehension result or public release is claimed.

Original research is Apache-2.0, **© Peer-to-peer Privacy Systems Research, LLC.** See [LICENSE](LICENSE), [NOTICE](NOTICE), [third-party boundaries](LICENSING.md) and [citation metadata](CITATION.cff).
