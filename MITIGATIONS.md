# Measured protection boundaries

| Choice | What the evidence supports | What it does not establish |
| --- | --- | --- |
| Fresh receive address per customer | Avoids simple public address reuse | Does not hide collection membership already queried together; valid-chain shop reproduced this |
| Leave the old service | Stops new requests after **both** core/helper routes move | Cannot revoke saved identifiers or stop public-chain watching |
| Verified TLS | Lab control rejects wrong-host, untrusted and expired certificates | Does not hide requests from the authenticated operator |
| A custom core SOCKS proxy | Actual core connector sent its controlled history request through the lab proxy | Actual helper made a separate successful direct request with zero additional proxy connections |
| One-server mode / manual main server | Narrows the core route under explicit experiment controls | Does not rewrite the hard-coded helper pool; may reduce independent header observations |
| Tor/VPN for every route | Can change which source IP a recipient sees | No full Tor/VPN anonymity, DNS-leak or platform-wide routing qualification was performed |
| A private trusted serving stack plus enforced egress | Could avoid third-party financial query disclosure if every financial path is covered | This is a proposed architecture, not a shipped ElectrumSVP privacy preset or verified fix |

The [proxy experiment](evidence/proxy-boundary-attempt-04/result.json) calls the actual `SVServer._connector` with a controlled SOCKS5 proxy and separately invokes the actual `electrum_request` helper. Both TLS endpoints see their test identifiers. The proxy sees one core CONNECT and none for the helper. No Tor listener was supplied. This tests the relevant code paths; it is not a click-through test of every GUI preference or a Tor leak measurement. The [GUI assurance](evidence/packaged-gui-attempt-01/proxy-assurance.png) is broader than these paths implement.

The valid-chain switch explicitly moved helper and core traffic and constrained candidate selection to the new local service. No post-switch request reached A. A still reconstructed later activity. A completely undisclosed new script or separate wallet stays outside the demonstrated deterministic join until another link exists. No mitigation should promise retrospective erasure of public chain records or previously copied query collections.
