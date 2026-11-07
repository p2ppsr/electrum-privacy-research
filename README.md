# Electrum privacy research

**Public research revision 0.2.0 — November 3, 2026.** Experiments collected October 28–29 examine what an operator can retain during ordinary ElectrumSVP 0.2.0 use. This update examines known privacy risks, security tradeoffs and accountability. Capability is assessed independently of logging defaults or retention promises; actual surveillance by a named service is not established.

Start with **[the plain-English shopkeeper story](EXPLAINER.md)**: one checkout address can name a wider wallet-associated profile; changing servers cannot revoke identifiers already disclosed.

**What users and reviewers need to know:** default queries enable lasting financial observation without exposing spending keys. Inclusion proofs do not conceal queries or prevent retention. Fresh addresses do not remove grouping already disclosed to a service. Unauthenticated TLS additionally allows a capable active intermediary to obtain that service's visibility; passive capture alone cannot decrypt it.

**Known risks and claimed remediation:** the [public maintainer response](https://github.com/TruthMachine/ElectrumSVP/issues/21#issuecomment-6540727570) acknowledges query visibility, proposes stricter TLS initially disabled by default, and reports unpublished integrity/proxy fixes and operator contact. On November 3, public master still contains the reviewed unauthenticated core/helper paths and latest release remains v0.2.0. Those local changes have not been independently tested. See [dated evidence and status](DISCLOSURE-TIMELINE.md); optional authentication, if shipped as described, would leave default exposure in place.

**Start the accountability review here:** [who controls and receives the data](ACCOUNTABILITY.md), [the highest-priority unanswered questions](OPEN-QUESTIONS.md), and [what was reported, acknowledged, claimed and released](DISCLOSURE-TIMELINE.md). The central questions are who accepts default risks, what users are told before disclosure, and which operator/source/retention commitments can be verified. These are governance and ecosystem dependencies as well as technical issues. No inference of bad intent, actual pooling or an impossibility of future privacy commitments is needed to identify those gaps.

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

**Independent review and replication are invited through [GitHub Issues](https://github.com/p2ppsr/electrum-privacy-research/issues) and pull requests.** See the [open research questions](OPEN-QUESTIONS.md), [contribution guide](CONTRIBUTING.md) and [release notes](RELEASE-NOTES.md). Public review is ongoing; advance review, direct outreach and reader studies are not publication prerequisites. The [reader-study protocol](READER-STUDY.md) remains available for optional follow-up research.

Original research is Apache-2.0, **© Peer-to-peer Privacy Systems Research, LLC.** See [LICENSE](LICENSE), [NOTICE](NOTICE), [third-party boundaries](LICENSING.md) and [citation metadata](CITATION.cff).

## Conflict of interest

This research is published by Peer-to-peer Privacy Systems Research, LLC (P2PPSR / Project Babbage). Ty Everett and Project Babbage develop and promote BRC-100-based wallet technology, which competes with the Electrum wallet design examined here. Readers should consider this potential commercial and technical conflict of interest and assess the findings against the published evidence and reproduction methods.
