# Retained attempt ledger

All attempts are retained separately. Later successes do not erase failed or qualified samples.

| Attempt | Disposition | Explanation |
| --- | --- | --- |
| `live-attempt-01` | Successful 40-script live observation, with qualifications | Fresh unfunded wallet; initial harness used coin type 236 rather than the source wizard's default 0 and emitted shutdown task warnings. This is not the canonical default-derivation run. |
| `fixture-attempt-01` | Failed | Fixture omitted the JSON-RPC 2.0 response marker expected by the actual transport. Rejected during version negotiation. Corrected in the fixture; wallet source unchanged. |
| `live-attempt-02` | Passed | Correct default coin-type derivation, 40 subscriptions and empty history through a live endpoint advertising ElectrumR; orderly harness shutdown. One public header-helper peer timed out; the wallet session completed. |
| `fixture-attempt-02` | Failed observer completion | Capture reached the signed payment and independently correct operator ledger; the headless callback adapter executed work synchronously and prevented wallet-side completion. The owned wallet process was terminated with SIGTERM. Exit -15 remains failed. |
| `fixture-attempt-03` | Passed | Correct asynchronous headless callbacks; real wallet final balance 8,499,000 sats; signed payment verified against fixture prevouts. |
| `fanout-attempt-01` | Passed | Exact upstream helper delivered one transaction lookup to all eight controlled TLS peers. |
| `fixture-attempt-04` | Passed, canonical financial sample | Adds retained post-session future-watch evidence and verification of history/status consistency. Captured 47 scripts and four modeled transactions; wallet and capture-only reconstruction agree. |

Unperformed: self-hosted source-pinned ElectrumR, consensus-valid funded BSV chain, confirmed financial history through that server, and packaged desktop GUI qualification. The server source/artifact was unavailable after scoped public and authenticated discovery. See the report and provenance receipts.

## Public attribution, source and liveness follow-up

- Public registry/routing collection succeeded for the shared prefix and other endpoint networks. Domain registry channels did not reveal an end-user legal operator for the shared-prefix services; two .io WHOIS connections reset. Those outcomes remain inconclusive.
- Two GitHub CLI language-filter queries failed with HTTP 422 due to CLI query parsing. Their failed receipts remain in `server-sources-20261028/github-searches.json`; corrected direct API queries completed with zero results in `github-search-query-repairs.json`.
- Two isolated source-repair/tree-check launches used system Python and failed to import the collector's ASN.1 dependency before sending external requests. Corrected launches used the existing research virtual environment. No server state or successful liveness sample was altered by these local startup errors.
- Software Heritage returned non-JSON HTML. This is an inconclusive archive check, not a successful absence result.
- Liveness round 1: eight endpoints answered Electrum; seven returned current matching headers. Bitails answered version but timed out on the header request. `electrum.server.sv` timed out during TCP connection.
- Liveness round 2: eight endpoints answered Electrum and supplied matching current headers; `electrum.server.sv` again timed out during TCP connection. This later Bitails success does not erase or convert its first timeout.
- All 15 obtained headers matched the contemporaneous Bitails and WhatsOnChain reference hashes at height 973092. These bounded observations are not an uptime or historical-completeness qualification.


The `default-session-attempt-01` follow-up passed with routing settings unset, ten default core connection slots, seven core RPC-response hosts and seven successful client-side header-helper TLS sends (eight unique hosts in their union). Only the selected main completed the 40 script subscriptions. The fresh unfunded run had no transaction/proof helper requests. Headless callbacks, isolated paths and observation wrappers remain explicit controls; this is not a full GUI capture or server-retention evidence. Disposable wallet state was removed. Default HTTP recipients are source findings, not observed GUI traffic. The observer required no recovery attempt.


`correlation-attempt-01` passed: three fresh real wallet processes, isolated loopback TLS, each with the default 40 script subscriptions, no financial history, no privacy-specific opt-in and no non-loopback socket access. All three exited before the unsigned fictional-parent later ledger was constructed. One simulated checkout address anchored 40 identifiers; separate observed/unobserved payer flows and three non-reused receiving scripts were reconstructed. All disposable state was removed. Four negative/boundary tests and the independent offline verifier passed. No real shop, payment, live server or third-party client was investigated.

The disclosure review searched 92 English consumer/source files and first collected 15 manual file receipts plus six successful public page snapshots. Three supplemental startup/account receipts brought the final reviewed source total to 18; the collector was updated accordingly. A Git command initially assumed an `origin/master` tracking ref that this tag-oriented clone lacks. Fetching succeeded; the subsequent read command failed locally, then `FETCH_HEAD` resolved observed master `35b92ec9` without changing the release working tree. Public-master server-pool changes and unchanged relevant UI messages are recorded separately from the release experiments. A guessed `/docs/` web path was inaccessible; the actual homepage documentation link successfully redirected to upstream sv-1.3.15 docs. Neither failed lookup is evidence of absent documentation. No actual user-awareness measurement was performed.

Public issue/PR discovery initially returned four connector validation errors because the queries omitted a required issue/PR type. Eight corrected queries completed successfully and led to review of issues #19 and #15 plus maintainer replies. The retained receipts distinguish rejected searches, bounded zero results, positive technical risk-awareness evidence and the absence of an actual user-comprehension study. No public comment was sent.

## October 29 continuation

The claim ledger and Apache licensing foundation were committed first. Rosetta installation/license acceptance was explicitly approved by the operator. The verified Intel DMG initially failed for missing Rosetta, stripped library-path environment under the sandbox, and its pre-`-D` fixed home path. Lab wrapper/path controls and stale-daemon recovery are documented in PACKAGED-WALLET. A moved app path was initially unquoted; the path was corrected. Original failure logs remain. The operator brought the window forward after computer-control identification failures; subsequent UI capture and input used that tool. The final desktop capture and bundled-core relay both passed.

Valid-chain attempts 01–04 retained their method/wait/locked-setting/candidate-selection failures; attempt 05 passed with all worker exits zero, a complete main/helper departure, signed confirmed payments and deterministic old-observer reconstruction. Initial node startup lacked a required mining-policy parameter. Fresh-state replay attempts 01–02 exposed entrypoint/null-output observer errors; attempt 03 accepted 210 blocks and rejected the two invalid-block controls. Proxy attempts 01–03 exposed constructor/address/JSON-RPC response-format errors; attempt 04 passed. These are local harness errors, not public-service findings. Source/package certificate matrices passed; the first bundled controller attempt used an incompatible architecture import, then isolated bundled clients corrected that observer error. Final matrices include plaintext rejection and 18 tests per runtime.

October 29 liveness appends two bounded samples. All eight responding endpoints appeared current; electrum.server.sv again did not respond from this vantage. Earlier Bitails timeout evidence remains unchanged. The documented ElectrumR source URL again returned authenticated 404. No real shop, user, funds, public DNS redirection, maintainer outreach or privacy-default remediation was involved.

Final TLS source attempt 03 and bundled attempt 04 also align the helper target with the localhost SAN used for matching-host cases. Earlier IP-target helper rows are superseded for that case classification. Their acceptance behavior remains recorded, without relabeling the earlier target.
