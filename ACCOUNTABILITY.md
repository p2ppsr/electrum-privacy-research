# Default disclosure, risk acceptance and accountability

**Updated November 3, 2026.** This research asks what users must entrust to a wallet project, its selected services and intervening networks. The October 28–29 experiments establish capabilities; the November 3 review adds public responses and publication status. It does not establish that a named provider actually profiles users. Start with [the shopkeeper story](EXPLAINER.md), [claim ledger](CLAIMS.md) and [disclosure timeline](DISCLOSURE-TIMELINE.md).

## What reviewers should know first

- A main Electrum service can record the grouped payment identifiers the wallet queries. A later checkout address can identify the matching shop-associated group even when each customer receives a fresh address. Saved identifiers support later public-chain observation after the user leaves. This is a demonstrated capability, with finite scope and attribution limits; protocol novelty is not a prerequisite for its privacy significance.
- Transaction inclusion checks do not conceal queries, establish complete history or prevent retention. Protecting spending keys does not establish financial confidentiality.
- Certificate authentication limits impersonation by intermediaries. The authenticated service still receives the queries. These are two distinct trust relationships requiring separate controls.
- Compatibility decisions determine default exposure. A future opt-in protection does not protect ordinary users who leave it disabled, if implemented as announced.
- A statement about a local fix is evidence of a maintainer's position. Published source, released artifacts and reproduced behavior are different evidence.

## Evidence and claim status

| Status | Current record | Boundary |
| --- | --- | --- |
| Measured | Official macOS 0.2.0 default session, core/helper certificate tests, routing test and isolated valid-chain shop demonstration | Experimental controls and limits remain in [package](PACKAGED-WALLET.md), [certificate](CERTIFICATES.md), [routing](MITIGATIONS.md) and [chain](VALID-CHAIN.md) methods |
| Public source observed November 3 | Public master remains `35b92ec9ddb7575d453e35ed018fe106d9169b54`; reviewed core/helper authentication and height-based balance code remain unchanged; latest-release API returns v0.2.0 | Source review, not a new packaged-runtime or public-server liveness experiment |
| Maintainer statement | Stricter TLS planned as an option initially disabled; local balance/coinbase/CPFP and proxy changes reported; contact with satoshi.io operators and a Rust server project reported | Unpublished code, regression results, operator coordination and new server provenance have not been independently verified |
| Research interpretation | Default security choices, dependency concentration, disclosure and auditable commitments are governance questions as well as implementation questions | No inference of deliberate deception, actual data pooling or universal user misunderstanding |
| Researcher account | Reporter describes personal attacks and an end to coordinated disclosure after public maintainer statements | Linked X thread could not be retrieved; exact statements and ordering remain unverified here |

The dated [public-response receipt](evidence/governance-20261103/public-record.json) and [source receipt](evidence/governance-20261103/public-source.json) identify permalinks, source revision, timestamps, body/file hashes, narrow quotations and summaries. Historical evidence remains unchanged.

## Who is responsible for which protection?

| Role | Relevant responsibility or capability | Evidence needed for accountability |
| --- | --- | --- |
| Wallet maintainers | Choose default destinations, authentication, helper routing, fallback, labels and warnings | Published design decisions, complete path inventory, versioned tests, advisories and reproducible release artifacts |
| Application service administrators | Receive queries; may retain, combine, forward or continue matching them | Identifiable responsible organization, administrative boundaries, downstream recipients, attributable policies and independently auditable controls |
| Hosting and network providers | Infrastructure access or routing position can create additional capabilities | Evidence of actual access and administration; allocation records alone do not establish application ownership |
| Active path attacker | Can impersonate a tested unauthenticated Electrum destination if able to interpose on that connection | Conditional capability established by certificate/relay tests; no attack by a named ISP, VPN or Tor operator is alleged |
| Users | Select settings using the information available to them | Accurate explanation before disclosure and controls whose scope matches their labels |
| Researchers and reviewers | Test claims, preserve failures and distinguish evidence from inference | Versioned methods, negative controls, public corrections and accessible review without personal attacks |

An ISP or hostile Wi-Fi operator on a direct path, a VPN provider carrying the connection, or a Tor exit carrying a clearnet Electrum connection may have the required active position. A passive observer cannot decrypt merely because validation is disabled. An ISP outside an intact VPN/Tor tunnel does not automatically gain access to the inner connection. A Tor exit generally lacks the home IP, while an outside identity anchor can still name a captured collection. Header-only interception does not reveal the full collection. See [the trust diagram](TRUST-MODEL.md#active-interception-expands-the-trust-boundary).

## Compatibility, concentration and coordination

The [October 30 PDT maintainer response](https://github.com/TruthMachine/ElectrumSVP/issues/21#issuecomment-6540727570) describes certificate compatibility concerns, future optional verification, and contact with satoshi.io operators said to run a significant portion of the infrastructure. This is positive evidence of reported coordination; it is not an independently verified ownership map or completed migration. The report should assess its concrete outcomes rather than assert no coordination exists.

The compatibility claims need a matrix naming server endpoints, affected client versions, trust mechanisms and demonstrated failure modes. Self-signed certificates do not make authenticated connections impossible: deliberately authenticated pins or a designed trust bootstrap may be alternatives, with first-use and rotation risks made explicit. Standard PKI validation, pinning and onion identity are design options to evaluate, not interchangeable fixes already deployed by this study.

The release's six of nine names in one IPv4 segment establish concentration of default entries, not six independent providers or a measured traffic share. The consumer model assumes those services correlate data; public evidence has not proven their common legal ownership or actual sharing. [Versioned counts and infrastructure relationships](TRUST-MODEL.md).

Difficulty migrating certificates does not logically prove that privacy commitments are impossible. This investigation has not established adequate independently verifiable commitments across all financial-data recipients. Identify who can promise what, under which technical controls, audit arrangements and enforceable obligations. A retention policy cannot remove protocol access, establish compliance by itself or recall a copy already made. Our bounded searches are not a comprehensive finding that no policy or agreement exists anywhere.

## Transparency and user awareness

ElectrumR's documented source repository again returned 404 on November 3. The source/build gap prevents inspection of the matching deployment, and the newly mentioned Rust implementation needs its own public repository, license, immutable revision and deployment evidence. A 404 does not establish proprietary licensing, deletion or data misuse. The research adapter is not ElectrumR. [Provenance questions](OPEN-QUESTIONS.md#oq02).

The existing disclosure audit found partial optional Network help, incomplete explanation of persistent profiling and a proxy-scope mismatch. It did not measure user comprehension. The maintainer recognizes query visibility and distinguishes Tor's network-identity role from script disclosure; that acknowledgment should be credited. Their suggestions concerning fresh addresses, coin control, output splitting or decoys need evaluation against server-observed grouping, not only public-chain heuristics. Our shop result does not require address reuse. [Response assessment](DISCLOSURE-AUDIT.md#november-3-public-response-assessment).

## Disclosure process and review

The timeline records earlier public awareness, the encrypted report, the reporter's public text and the maintainer's later reply separately. The researcher reports hostile treatment; this document does not convert that account into independently verified quotations or infer motives. If public posts become retrievable, preserve their exact dates, context and narrow relevant excerpts, and append corrections. A hash identifies captured text; it does not prove the author's claims or an uncaptured sequence of events.

Questions about confidential reporting, escalation, publication decisions and treatment of reporters belong in [OQ15](OPEN-QUESTIONS.md#oq15). This project invites technical corrections from everyone, including the maintainer and operators, through the same [open contribution process](CONTRIBUTING.md). No further private outreach, right-of-reply request, approval window or prepublication review is required. Governance criticism should identify a decision, evidence and consequence; personal attacks are not research evidence for unrelated technical claims.
