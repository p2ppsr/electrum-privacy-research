# What the project tells users about financial observation

**There is some network disclosure, but the reviewed material does not explain the full surveillance capability.** The strongest positive example is optional in-wallet Network help: it explains that payment-script metadata goes to a server to retrieve transaction history. The reviewed material does not explain durable post-disconnection watching, cross-user payment graphs or identifying a merchant's wider disclosed collection through one checkout address. A specific universal-proxy assurance also conflicts with the independently routed helper.

This is a bounded evidence review, **not a measurement of what users believe**. We did not interview users, run comprehension tests or measure whether people read a help screen. The evidence supports a disclosure gap and a plausible mismatch between expectations and capabilities; it does not establish that every user is unaware, that developers intended deception, or that public servers actually run covert surveillance.

## Scope and method

The tested release is ElectrumSVP 0.2.0 at `672df8f4512f6adf16a3c99146baa6be9b93d86f`. We searched **92 English-language source/documentation files**, retained **14 discovery-term matches**, and manually reviewed **18 pinned source-file receipts** across startup, account creation, optional network help, preferences, welcome/release notices, relevant networking and basic documentation. Terms are discovery aids, not a numerical score for disclosure quality. Relevant surrounding text and call paths were reviewed as well.

On October 28, 2026, we also retrieved the official homepage, two release articles and three linked documentation pages successfully, retaining retrieval times, redirects, hashes, narrow relevant paragraphs and policy-link observations. The homepage's documentation link led to **upstream ElectrumSV sv-1.3.15 documentation**, not a version-matched ElectrumSVP 0.2.0 manual. GitHub's v0.2.0 release body was checked separately. We also searched public issues and pull requests for privacy, proxy, surveillance and server terms, then read two relevant server-authentication discussions and their maintainer replies.

The latest public master observed was **`35b92ec9ddb7575d453e35ed018fe106d9169b54`**, dated October 11, 2026. The reviewed Network help, proxy message, preferences, welcome/dialog text, README, wallet-location text and basic documentation files were byte-for-byte unchanged from the tested release. Account creation and server-pool code do contain later changes; this review does not call the entire latest tree identical or qualify its packaged behavior. No new explicit privacy disclosure was identified in the reviewed newer material.

Receipts: [source review and discovery inventory](evidence/disclosure-audit-20261028/source-audit.json), [first-party web pages](evidence/disclosure-audit-20261028/public-pages.json), [release-body summary/hash](evidence/disclosure-audit-20261028/release-messaging.json). Non-English translations, every historical communication, social-media conversation and external advice source were not exhaustively audited.

## Positive evidence and its reach

| Surface | What it communicates | Reach and remaining gap |
| --- | --- | --- |
| [Optional Network help](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/data/text/misc/network-dialog.html#L4-L13) | Multiple servers supply headers; one server receives wallet payment-script metadata for transaction history | A meaningful disclosure of the core architecture. It is help text opened from the Network dialog, not a demonstrated first-run explanation or acknowledgement of lasting financial profiling. |
| [Network dialog](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/network_dialog.py#L270-L307) | Automatic server selection, selected server, peers and connection information | Shows destinations and control choices, but not the complete separate helper path, shared-provider grouping or downstream correlation consequences. |
| [Welcome notice](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/dialogs.py#L135-L157) | Warns about bad decisions/coin loss and links to release information | Financial custody/theft caution is useful but does not explain query surveillance. Dismissing a welcome message is not evidence of understanding the unmentioned risks. |
| [Wallet password/location text](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/wallet_wizard.py#L64-L76) | Password encryption covers keys and essential data; location matters to other local wallet data | Concerns local file protection; it is not an explanation of remote server visibility. The constant's presence alone does not prove every user sees it. |
| [Change-address preference](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/preferences.py#L438-L465) | Different change keys can make transaction analysis harder | Plausible against some outside observers, but no stated exception for the service already receiving those keys' script identifiers. |
| [Official receiving documentation](https://electrumsv.readthedocs.io/en/sv-1.3.15/getting-started/receiving-a-payment.html) | Receive addresses rotate after incoming payment; instructions cover handing out addresses and avoiding substitution | Does not explain why rotation alone does not prevent the serving operator grouping them. |
| [GitHub v0.2.0 release](https://github.com/TruthMachine/ElectrumSVP/releases/tag/v0.2.0) and [release article](https://electrumsv.io/articles/2026/electrumsvp-0_2_0.html) | Key-storage security, verification, reliability, controls and cached proof retrieval | These are real but different security topics. The release body contained no privacy/surveillance/server terms; this word count is only a discovery observation. The article discusses reducing unnecessary proof queries but not the financial-privacy consequences. |

The [current homepage](https://electrumsv.io/) emphasizes control of keys, coins and addresses, encrypted wallet files and verification. It did not present the reviewed server-surveillance risk explanation or link a privacy/terms policy in the collected anchors. That observation is about this page, not proof no policy exists anywhere. **Control of private keys and validity verification do not establish confidentiality of financial queries.** The marketing is not, by itself, an explicit promise that servers cannot observe users.

## Messaging that can foster an inaccurate expectation

The [linked documentation index](https://electrumsv.readthedocs.io/en/sv-1.3.15/) calls receiving addresses “unique and private.” The [v0.1.0 project article](https://electrumsv.io/articles/2026/electrumsvp-0_1_0.html) describes a focus on privacy, Tor environments and randomized splitting. These messages can be compatible with some protections. However, the reviewed nearby material does not distinguish public-chain observers from the serving party that receives the address collection. A reader could reasonably overgeneralize address rotation or key custody into financial privacy from that party. Actual reader beliefs remain unmeasured.

The most concrete discrepancy is the Proxy tab's help statement:

> Proxy settings apply to all connections: both ElectrumSV servers and third-party services.

Source: [network_dialog.py, lines 362–366](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/gui/qt/network_dialog.py#L362-L366). This message is unchanged in the observed latest master.

The examined [verification helper](https://github.com/TruthMachine/ElectrumSVP/blob/672df8f4512f6adf16a3c99146baa6be9b93d86f/electrumsv/verification_utils.py#L335-L405) independently detects TAILS or a daemon at `127.0.0.1:9050`; otherwise it opens ordinary sockets. It does not read the arbitrary main-network proxy setting. Price and update code call Requests directly without applying that core setting. OS/environment proxy configuration can affect Requests separately. Consequently, setting a custom main proxy alone does **not** support the UI's universal assurance. This is a concrete source-level scope mismatch, not a claim of a tested leak on every OS, or proof that Tor fails when correctly used.

Even correct Tor routing hides an originating IP from a destination without hiding its queried script collection. The review found no nearby explanation of continued collection-based linkage or the finite lookahead already exposed.

## Public technical discussion shows some related risk awareness

The project has public technical discussion of related risks. [Issue #19](https://github.com/TruthMachine/ElectrumSVP/issues/19), opened October 9, reports missing certificate authentication on the normal core and verification-helper paths. In the [October 11 maintainer reply](https://github.com/TruthMachine/ElectrumSVP/issues/19#issuecomment-6105753556), the project acknowledges unfinished authentication work, explains that enabling hostname checking would break some existing server connections, and cites the small operating server pool in its compatibility trade-off. It also explains that malicious-server risks extend beyond extracting private keys. [Issue #15 and its reply](https://github.com/TruthMachine/ElectrumSVP/issues/15) discuss sweep-path TLS and existing self-signed certificates.

This is positive evidence that technically engaged participants and the maintainer publicly recognize some server-security risks. It would be inaccurate to report that the project has never discussed them. The material reviewed in those threads does not explain retained wallet-interest profiles, continuing observation after departure, merchant anchoring or cross-user value-flow graphs. A public technical thread also does not establish that ordinary users encounter or understand its contents. An issue's closed/completed label does not establish a particular remaining problem was fixed: the maintainer reply explicitly describes deferred work, and this study independently checks source behavior.

Eight corrected issue/PR search queries are retained, along with four initial query rejections requiring an issue/PR type filter. Privacy/proxy/surveillance keyword queries returned no results; server queries located the discussions above. Indexing and keyword limitations mean zero search results cannot prove an absence of prior awareness. [Search receipts](evidence/disclosure-audit-20261028/public-discussion-searches.json) and [narrow discussion summaries](evidence/disclosure-audit-20261028/public-discussion-review.json) preserve the distinction. No issue, comment or message was posted by this research.

## Coverage of the material risks

“Not found” below means not identified in the bounded reviewed consumer surfaces, not proof no person has ever discussed the topic.

| Risk a consumer would need explained | Review result |
| --- | --- |
| Core payment metadata sent to a server for history | **Present**, in optional technical help |
| Multiple core header connections | **Present**, in optional help and Network controls |
| Connecting IP/session joined to a wallet-wide interest collection | **No explicit risk explanation found** |
| Unused receiving/change lookahead identifiers disclosed automatically | **No explicit risk explanation found** |
| Continued public-ledger monitoring after changing servers or quitting | **No explicit risk explanation found** |
| Cross-user value-flow graphs and later identity anchors | **No explicit risk explanation found** |
| One shop checkout address can anchor other disclosed fresh addresses | **No explicit risk explanation found** |
| Separate hardcoded helper fanout, including sometimes automatic financial lookups | **No explicit risk explanation found** |
| Shared infrastructure and pooled observations across names/providers | **No explicit risk explanation found** |
| Limits of main-server/proxy choices across all paths | **No clear scope disclosure found; a universal proxy assurance conflicts with the reviewed helper** |
| Distinction between key custody/verification and server-side financial confidentiality | **No clear explanation found in the reviewed onboarding/basic guidance** |

We found **no separate acknowledgement gate for these financial-observation risks** in the reviewed startup, account-creation and subscription paths. Normal online use supplies the script collection automatically; our controlled runs required no privacy-specific opt-in. These runs use core-wallet harnesses, so the gate finding also relies on source review rather than claiming a complete packaged-GUI walkthrough. Offline use and altered infrastructure are different operating modes; merely opening an ordinary online wallet is not evidence of informed agreement to the unmentioned profiling capabilities.

## Impact and appropriate closeout language

The trust imposed on an ordinary online user includes entrusting the serving infrastructure **not to retain, identify, join, share and perpetually monitor** its financial interests, including relationships with other observed users. A basic explanation that a server supplies history does not fully communicate those consequences. Missing that distinction can make privacy controls appear more comprehensive than the reviewed data paths support.

The supported conclusion is **incomplete, weakly surfaced consumer risk disclosure, with a concrete proxy-scope inconsistency, some public technical risk awareness and unmeasured ordinary-user understanding**. It is not a measured prevalence of misunderstanding or an accusation of deliberate concealment. Before the project could demonstrate informed user understanding, it would need an accurate plain-language explanation before disclosure, controls whose scope matches their labels, and evidence that users comprehend persistence, cross-user correlation and helper routing. The [privacy stories](PRIVACY-STORIES.md) and [correlation demonstration](PERSISTENT-CORRELATION.md) supply reviewable examples rather than claiming that product work has been implemented.

## Version-specific destination counts

The main experiment and nine-host tables remain pinned to released **0.2.0**. The newer public master is not the same snapshot:

| Snapshot | Core / helper / overlap | Union | Shared-segment names | Helper conservative groups |
| --- | --- | ---: | ---: | ---: |
| Tested 0.2.0 `672df8f4` | 8 / 8 / 7 | 9 | 6/9 union; 5/8 core; 6/8 helper | 3 |
| Observed master `35b92ec9` | 8 / 8 / 8 | 8 | 5/8 in core, helper and union | 4 |

Master comments out `electrum.server.sv`, adds `sv3.satoshi.io` to core and adds Bitails to the helper. Its core and helper lists therefore coincide. The concentration and surveillance mechanisms remain relevant, while exact version counts must not be mixed. No newer-master runtime experiment or packaged-binary qualification was performed in this follow-up. Relevant public source changes do not constitute an observed privacy disclosure or a remedy for retained-data correlation.
