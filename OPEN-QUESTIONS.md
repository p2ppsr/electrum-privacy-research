# Open research questions

Independent replication, corrections, additional evidence and competing interpretations are welcome through [GitHub Issues](https://github.com/p2ppsr/electrum-privacy-research/issues) and pull requests. These questions are addressed to the research community, software authors, service operators and users. Contributions are open to everyone; no private review, direct maintainer outreach, response deadline or approval is required for publication.

Start with [the claim ledger](CLAIMS.md), [package methods](PACKAGED-WALLET.md), [valid-chain experiment](VALID-CHAIN.md), [certificate tests](CERTIFICATES.md) and [trust-party accounting](TRUST-MODEL.md). [CONTRIBUTING](CONTRIBUTING.md) explains how to make findings reproducible and keep discussion focused on evidence. An unanswered question is not evidence of misconduct or confirmation of a hypothesis.

<a id="oq01"></a>
## OQ01 — Package and build provenance

Can the official 0.2.0 DMG be reproduced from an immutable source revision and documented native dependencies? The 145 shared Python modules have identical parsed code to the release tag; what additional evidence establishes the provenance of the interpreter, native libraries, resources and full build? Do other official platform packages show the same defaults and behavior? See [the package comparison](PACKAGED-WALLET.md).

<a id="oq02"></a>
## OQ02 — Accessible ElectrumR implementation

What accessible public source, license, immutable revision, build recipe and artifact correspond to the advertised ElectrumR deployments? The documented `KeyvanJS/ElectrumR` URL returned 404 in the retained observations. Can another source or archive be tied to those deployments with verifiable evidence? A 404 does not establish proprietary licensing, deletion, or actual retention practices. See [source identification and its limits](REPORT.md#source-and-deployment-identification).

<a id="oq03"></a>
## OQ03 — Endpoint administration and infrastructure boundaries

Which organization administers each listed endpoint and controls TLS termination, query data, logs and upstream forwarding? What evidence distinguishes administrators, hosting customers, machines and legal organizations among the names sharing `198.154.93.0/24`? The conservative pooling assumption remains separate from verified common ownership. See [the role and infrastructure model](TRUST-MODEL.md).

<a id="oq04"></a>
## OQ04 — Deployed software and downstream services

Can endpoints publish independently checkable source-to-build and deployment attestations? Which RPC paths forward data to another API, and who operates that backend? How do the accessible Bitails adapter and ElectrumX implementations correspond to actual deployed versions? A banner or repository head alone does not establish that correspondence. See [the retained source-head observations](evidence/publication-20261029/server-source-heads.json) and [the report](REPORT.md).

<a id="oq05"></a>
## OQ05 — Server authentication and remediation

What server-identity guarantee is intended by the core and helper TLS paths? What source-pinned changes, authenticated identity model and certificate/key rotation behavior address the observed acceptance of wrong-host, self-signed and expired certificates? Can replications and later fixes be evaluated against the same acceptance matrix on each supported platform? See [the certificate results and integrity boundaries](CERTIFICATES.md).

<a id="oq06"></a>
## OQ06 — Proxy coverage across every route

Which core, helper, DNS, update and price-service routes honor each GUI, environment or platform proxy setting? How does that behavior reconcile with the captured assurance that proxy settings cover every connection? What happens with a custom SOCKS endpoint, a local Tor listener, unavailable proxies, environment proxies and enforced egress? The existing test covers the core connector and separately routed helper; full GUI/platform Tor or VPN coverage has not been measured. See [measured mitigation boundaries](MITIGATIONS.md).

<a id="oq07"></a>
## OQ07 — Switching, failure and long-lived sessions

Which actions move every financial request path, and which leave the helper pool unchanged? How many additional services learn a collection through automatic main-server changes, reconnects, cached peers, failure or recovery over time? Can this be measured with default packaged sessions and controlled endpoints? The valid-chain departure test deliberately moved both main and helper routes. See [the departure experiment](VALID-CHAIN.md).

<a id="oq08"></a>
## OQ08 — Financial helper fanout during ordinary use

How often do normal funded GUI workflows invoke transaction-body, history, UTXO or proof helpers, and which candidates receive each request before cancellation or timeout? How do larger histories, BEEF/BREAD construction, errors and retries change that exposure? The empty default GUI session observed header-only helper traffic; the eight-peer experiment demonstrates what one invoked financial lookup can disclose. See [helper routing and evidence](TRUST-MODEL.md) and [the claim ledger](CLAIMS.md).

<a id="oq09"></a>
## OQ09 — Query collections and identity attribution

How do multiple accounts, simultaneous wallets, watch-only collections, delegated shop administration, shared IPs and proxies affect grouping and attribution? Can controlled negative cases quantify incorrect joins or ambiguous payer assignments? A queried collection is an interest set; a connection or IP is not proof of a legal person's identity or ownership. See [the correlation boundaries](PERSISTENT-CORRELATION.md).

<a id="oq10"></a>
## OQ10 — Persistent observation and effective privacy controls

How far do deterministic joins extend through disclosed lookahead, known outpoints and change, and where do they require a new observation or a heuristic? What wallet architecture can keep financial lookups within a user-controlled serving stack across every route? What can a new, undisclosed collection protect after an earlier collection has already been copied? See [the lasting-watch example](EXPLAINER.md#leaving-does-not-take-back-the-record) and [mitigation limits](MITIGATIONS.md).

<a id="oq11"></a>
## OQ11 — Integrity under hostile responses

How do the released wallet's mainnet checkpoints, header selection, transaction checks and proof/BEEF error paths behave against a systematically malicious service? Can omission, fabricated unconfirmed state, inconsistent responses, stale headers and malformed proofs be tested separately? The retained node negative controls and successful wallet proofs do not constitute a full hostile-response audit of every wallet feature. See [the integrity boundary](CERTIFICATES.md).

<a id="oq12"></a>
## OQ12 — Consumer disclosure and understanding

Where do versioned consumer UI/docs explain grouped identifiers, financial helper fanout, persistent observation after departure and one-checkout shop anchoring? Which wording and diagrams help ordinary readers understand these consequences and the main/helper/auxiliary distinction? Public technical discussions show some risk awareness; ordinary-user comprehension has not been measured. [Captured messaging](PACKAGED-WALLET.md#messaging-actually-shown) and the [optional reader-study protocol](READER-STUDY.md) provide starting points.

<a id="oq13"></a>
## OQ13 — Policies and data-access accountability

What public evidence documents retention policies, sharing arrangements, subprocessors and administrator access for each financial-data recipient? Which statements are independently auditable? Policy assertions should be attributed to their authors; they do not remove API-level capabilities or establish that surveillance does or does not occur. See [the trust model](TRUST-MODEL.md).

<a id="oq14"></a>
## OQ14 — Replication, coverage and later versions

Can independent researchers reproduce the packaged defaults, server-side dossier, shop anchor and post-departure results using only the retained inputs and documented controls? How do results change across supported platforms, later releases and network vantage points? Which liveness or ownership observations change when sampled again? Preserve version/date boundaries and failed samples, and identify new evidence that narrows, contradicts or extends a claim. See [REPRODUCE](REPRODUCE.md), [dated liveness evidence](evidence/liveness-20261029/liveness-table.md) and [the attempt ledger](evidence/ATTEMPTS.md).
