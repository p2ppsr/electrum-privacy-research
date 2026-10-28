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
