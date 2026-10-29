# Factual review and right-of-reply packet — draft, unsent

Status: prepared for review. No maintainer, service provider, registry contact, merchant or customer has been contacted in this task. No response, independent replication or endorsement is claimed. Repository visibility remains private. Sending this packet is a separate communication action; the user should approve the recipients, exact content and response deadline before outreach.

Proposed recipients are the public ElectrumSVP maintainer contact/issue channel and documented public contacts for the named services. Verify their current official contact channels before sending; do not infer private individuals from shared IP space. Provide private read-only access only after explicit recipient authorization. Never send ignored wallet state, seeds, private keys or RPC credentials.

Draft covering message:

> Peer-to-peer Privacy Systems Research, LLC is preparing a technical study of ElectrumSVP 0.2.0's server trust model. We would appreciate factual corrections on the attached claim ledger, methods and version-specific evidence. The study distinguishes API capability from actual retention, and infrastructure relationships from verified application ownership. It includes no production user transactions. Please identify any incorrect behavior, source/version mapping, or disclosure citation, and provide reproducible evidence where possible. We can include your response and retest a source-pinned fix before any publication. A publication date and response period have not yet been set.

Questions for the wallet publisher:

1. Do the attached 145-module AST comparison, DMG hash and GUI default observations match the intended 0.2.0 distribution? Is there a reproducible build recipe and native-dependency provenance?
2. Are the core `CERT_NONE` context and helper unverified context intentional? What authenticated-server model, migration/rotation plan or fix should readers evaluate? Public issues #15/#19 show related technical discussion; identify any newer remediation.
3. Which routes are intended to honor the GUI proxy setting? How should the universal proxy assurance be reconciled with independent helper routing and HTTP clients?
4. Where are ordinary users informed about grouped identifiers, financial helper fanout, indefinite post-departure monitoring and cross-user/shop anchoring? Please supply exact versioned UI/docs locations.
5. Which default services have formally independent administrators and data-access boundaries? Does a main-server change affect every financial helper route?

Questions for ElectrumR/service publishers:

1. The documented `KeyvanJS/ElectrumR` source URL returned 404, including on the October 29 refresh. What current public source, license, immutable revision and build artifact correspond to the advertised deployed versions?
2. Which organization administers each endpoint and controls TLS termination, logs, query data and upstream API forwarding? Which infrastructure relationships can be independently documented?
3. Are service descriptions, retention policies and subprocessors publicly documented? These statements will be attributed as assertions; protocol capability remains independent of policy promises.
4. Can a deployment publish source-to-binary/build attestations or other independently checkable provenance?

Reviewers should start with [CLAIMS](CLAIMS.md), [package methods](PACKAGED-WALLET.md), [valid chain](VALID-CHAIN.md), [TLS](CERTIFICATES.md) and [trust-party accounting](TRUST-MODEL.md). Review outcomes need an append-only dated log: claim, correction requested, evidence, disposition, retest artifact and final text change. Preserve adverse results and disagreements; silence is not confirmation. Give affected parties a concrete fair response period before setting a public-release date. Do not promise that independent review is complete until a named reviewer has actually provided it.
