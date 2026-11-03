# Disclosure and remediation timeline

**Review date: November 3, 2026.** Times below are UTC; dates explicitly marked PDT use America/Los_Angeles. The [retained receipt](evidence/governance-20261103/public-record.json) contains GitHub timestamps, IDs, links and hashes of retrieved body text. Summaries are research annotations. They establish what was published, not whether every statement is true. The issue bodies/comments may later be edited; consult the captured hash and updated timestamp.

| Time | Event and source | What it establishes |
| --- | --- | --- |
| September 17, 01:33:59 UTC | [v0.2.0 published](https://github.com/TruthMachine/ElectrumSVP/releases/tag/v0.2.0) | The version later tested; latest-release API still returns it on November 3 |
| October 9, 15:22:31 UTC | [Issue #19](https://github.com/TruthMachine/ElectrumSVP/issues/19) reports missing normal-path certificate authentication among other findings | The underlying certificate issue was publicly discussed before this research report |
| October 11, 05:16:13 UTC | [Maintainer reply to #19](https://github.com/TruthMachine/ElectrumSVP/issues/19#issuecomment-6105753556) | Acknowledges deferred authentication and compatibility/small-pool considerations; also credits and reports accepting other contributions |
| October 28–29, PDT | [Controlled research](REPORT.md) | Default disclosure, package behavior, TLS acceptance, proxy boundary and lasting-correlation experiments; not evidence of actual covert retention by public operators |
| October 29, 23:18:32 UTC | [Issue #21 opened](https://github.com/TruthMachine/ElectrumSVP/issues/21) by `ty-everett` with an encrypted statement addressed to the maintainer's published key | An encrypted submission is publicly visible; body presence does not prove decryption, private agreement or contents |
| October 30, 00:42:29 UTC (October 29 PDT) | [Reporter publishes plaintext](https://github.com/TruthMachine/ElectrumSVP/issues/21#issuecomment-6512044366); issue closes at the same timestamp | Reporter says coordinated disclosure is no longer considered necessary by maintainer and says maintainer already made public statements. This is an attributed account of those preceding events |
| October 31, 07:40:47 UTC (October 30 PDT) | [Maintainer response](https://github.com/TruthMachine/ElectrumSVP/issues/21#issuecomment-6540727570) | Publicly acknowledges unverified helper TLS and query privacy considerations; announces optional strict TLS initially disabled, local integrity/proxy changes, and reported operator contact |
| November 3 | [Public branch](https://github.com/TruthMachine/ElectrumSVP/tree/35b92ec9ddb7575d453e35ed018fe106d9169b54), [latest-release API](https://api.github.com/repos/TruthMachine/ElectrumSVP/releases/latest), source and [ElectrumR URL](https://github.com/KeyvanJS/ElectrumR) rechecked | Public master remains October 11's `35b92ec9`; reviewed code still lacks core/helper authentication and uses height-based balance classification; latest release remains v0.2.0; documented ElectrumR URL returns 404 |

## Remediation status at this observation

| Topic | Public maintainer position | Independently reviewable status |
| --- | --- | --- |
| TLS | Future preference for stricter checks, initially disabled; compatibility cited | Not in observed public master or a newer latest release. Exact preference scope, helper coverage, trust bootstrap, rotation and failure behavior require published implementation/testing |
| Balance, coinbase maturity and CPFP | Verified-state gating and six passing account tests reported in local build | Claimed local fix, not independently reproduced; current public balance method still uses positive height. Forged-height GUI scenario remains source-derived and unperformed by this research |
| Helper proxy | Custom SOCKS inheritance and no direct fallback on unavailable configured proxy reported; TAILS retest planned | Claimed local fix; historical controlled finding remains version-specific. No blanket TAILS or Tor leak was demonstrated by our experiment |
| Operator coordination | Contact with satoshi.io operators and Rust server development reported | First-party statement; no independent attestation of ownership, deployment, certificate migration or data-access commitments |
| Privacy | Query grouping acknowledged; existing network/privacy features and possible decoys discussed | Acknowledgment is useful. Protocol novelty, real-world identity and actual operator misuse are not claimed by this report |

## Reported treatment and inaccessible evidence

The researcher reports personal attacks/smears, rejection of coordinated handling and maintainer publicity before a fix. The reporter's GitHub comment points to [this X thread](https://x.com/ProjectBabbage/status/2115935556383445090). On November 3, the web retrieval tool returned HTTP 403. This is a failed retrieval from this tool/vantage, not evidence the post was removed or never existed. The exact public statements, their authorship/context and their ordering against private exchanges are not independently established in this repository update. No private correspondence is published here.

Because #19 already discussed the weakness publicly, do not describe the later episode as the first public disclosure of certificate-validation failure. Distinguish an already public flaw, new experimental details, and the contested handling of a specific coordinated report. No blockchain timestamp assertion or encrypted/plaintext equivalence was independently verified during this update.

## Review and correction

Append newly retrievable evidence with dates and provenance. Preserve earlier receipts and failed retrievals. A closed/completed issue is not proof of a shipped fix; a local-fix statement is not proof that no work exists. Evaluate future source and official artifacts against both the [certificate matrix](CERTIFICATES.md) and each separately claimed integrity/routing correction. [Open questions](OPEN-QUESTIONS.md) invite ongoing review without advance approval or further outreach.
