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
