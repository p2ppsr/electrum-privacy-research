# Certificate authentication, impersonation and limits

Both the released source and the official macOS distribution accept an encrypted connection without authenticating the serving certificate. In each runtime, the actual core context and actual helper function accepted all five presented-certificate cases below and sent a controlled financial-history identifier to the endpoint. A standard verified TLS control accepted only the trusted, matching case.

| Certificate presented by local endpoint | Core | Helper | Verified control |
| --- | --- | --- | --- |
| Lab CA trusted by control, matching hostname | Accepted | Accepted | Accepted |
| Lab CA trusted by control, wrong hostname | Accepted | Accepted | Rejected |
| Untrusted self-signed, matching hostname | Accepted | Accepted | Rejected |
| Untrusted self-signed, wrong hostname | Accepted | Accepted | Rejected |
| Expired, lab-CA-signed, matching hostname | Accepted | Accepted | Rejected |
| Plaintext endpoint | Rejected | Rejected | Rejected |

[Source runtime, 18 tests](evidence/tls-source-20261029-attempt-03/result.json) · [DMG's bundled Python 3.9.13/runtime, 18 tests](evidence/tls-packaged-20261029-attempt-04/result.json) · [matrix runner](privacy_lab/tls_matrix.py) · [bundled client](privacy_lab/tls_client.py). Public test certificates are retained; private CA/leaf keys were removed. Only the control context trusts the lab CA for verification; no system trust store was modified. Loading that CA into the core context does not enable its disabled verification flags.

The core returns `SSLContext(PROTOCOL_TLS)` with `verify_mode=0` (`CERT_NONE`) and `check_hostname=False`. The helper explicitly calls `_create_unverified_context()`. The presence of TLS, bundled CA files, or a `certifi` import is therefore insufficient evidence of authentication. The controlled history request used an arbitrary test identifier. Separately, the [bundled-core wallet capture](evidence/packaged-core-attempt-01/capture.jsonl) shows an actual fresh wallet disclosing 40 identifiers through a TLS endpoint with an untrusted, mismatching certificate. That endpoint forwarded requests to a real public ElectrumR-advertising service. This was a deliberately selected local frontend, not a redirection attack against a real user or public DNS.

An attacker able to redirect a victim's connection—through a compromised network, DNS, proxy, routing path or endpoint configuration—can impersonate a service without possessing its legitimate TLS key. The attacker can terminate encryption, collect requests, forward them to the real backend, and return altered or omitted responses. The experiments demonstrate acceptance and disclosure to an impersonating endpoint. They do not establish that a particular network can redirect users or that an actual public operator does so.

A passive carrier cannot decrypt TLS merely because verification is disabled. Authentication would prevent this particular impersonation path; it would still disclose every request to the correctly authenticated operator. Tor or a VPN may conceal the original IP when **all** relevant routes use it, but does not conceal the query collection from its recipient. See [measured routing boundaries](MITIGATIONS.md).

Server statements can affect availability, omitted history and unconfirmed state. SPV inclusion checks do not prove that a server reported every relevant transaction. Conversely, certificate weakness does not by itself yield a spending key, forge a signature or establish arbitrary confirmed transactions. The valid-chain replay [rejected corrupted inclusion data and an invalid signature](evidence/chain-clean-replay-attempt-03/result.json). Those are node negative controls, not a complete hostile-response audit of every wallet feature or a proof of the strength of the release's mainnet checkpoint/chain-selection design. A full malicious-server review remains a separate audit.

A remedy should deliberately establish server authentication: verified PKI hostname checks or an explicitly designed, disclosed pinning/onion-identity model, with safe first-use and rotation behavior. Compatibility failures should be visible. This research did not change upstream wallet defaults, system trust settings or public servers. No fix is claimed deployed. PGP artifact integrity and TLS server identity are different assurances.

Final matching-host cases use `localhost` consistently for core, helper and verified clients. Earlier matrix receipts used an IP for the helper and are superseded for matching-host classification; the final results retain the corrected endpoint names.
