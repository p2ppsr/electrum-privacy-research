# One checkout address can expose far more than one sale

Imagine Mei runs a small online shop accepting Bitcoin SV (BSV). She gives every customer a new payment address. She keeps her recovery words safe. She expects each customer to see only their own payment.

Mei uses ElectrumSVP normally. To find her payments, the wallet asks a remote service about a group of payment addresses. It sends stable fingerprints of their payment instructions, including some prepared for future use. The service can save those fingerprints together as one profile.

Now imagine that service's operator opens Mei's checkout as a prospective customer. The checkout reveals one address. The operator computes its fingerprint and finds it in the saved profile. **One checkout address can give the operator a shop name for a much larger collection of financial activity.** It does not need to buy anything.

Payments to other addresses in that collection can now be associated with Mei's shop—even when every customer gets a different address. If the operator also observes customers' wallets, it can connect their payments to the shop. It can keep watching matching activity on the public blockchain after Mei changes servers and never comes back.

**Normal online use supplies the information for this kind of lasting financial surveillance. No separate privacy opt-in is needed for the default payment checks examined here.**

Mei is fictional. This explainer describes what a covert operator could collect, not evidence that a particular public service has done so. The research examined ElectrumSVP 0.2.0 and controlled wallet sessions on October 28, 2026. [What was tested](#what-we-demonstrated).

## How one address opens a wider view

An address is where a customer sends a payment. Its fingerprint is a stable identifier the service can match to blockchain records. The wallet sends several fingerprints through the same connection, so the service learns that they are being checked together.

The service does not need to recover every unused address from its fingerprint. As matching payments appear, their public records reveal the payment details. The checkout address provides the outside clue that associates the saved group with a shop.

![The wallet sends a group of address fingerprints. One checkout address lets the operator label that group as shop-associated and recognize other matching payments.](diagrams/explainer-shop.svg)

This is why fresh addresses alone do not hide the collection from the service checking them. A regular customer may know one address; the serving operator has the additional record of which fingerprints the wallet checked together.

**Evidence:** [the shop scenario and its conditions](PERSISTENT-CORRELATION.md#one-checkout-address-can-identify-much-more-than-one-sale), [the single simulated checkout address](evidence/correlation-attempt-01/checkout.json), and [the reconstructed shop profile](evidence/correlation-attempt-01/correlation.json).

## Leaving does not take back the record

Suppose Mei stops using that service. The operator can keep its saved list and compare it with the public blockchain. It can recognize later payments to disclosed addresses, first payments to previously unused disclosed addresses, and spends of coins it already knows about.

**The old service needs no new connection from Mei.** Closing the app, asking it to stop notifications, changing an IP address or choosing a different server does not erase a copy already kept.

![The operator keeps the earlier fingerprint list. After Mei leaves, new public blockchain records let the old operator recognize matching receipts and spends without another wallet connection.](diagrams/explainer-lasting-watch.svg)

There is a boundary: the disclosed collection is finite. Completely undisclosed addresses or a separate wallet need another link. A spend of known coins is visible, but an unfamiliar destination is not automatically proven to be Mei's new change address. That boundary does not expire the identifiers already disclosed.

**Evidence:** [continued monitoring and its limits](PERSISTENT-CORRELATION.md#leaving-a-server-does-not-revoke-the-disclosed-collection), [a modeled later match after the wallet exited](evidence/fixture-attempt-04/future-watch.json), and [the later-ledger experiment](evidence/correlation-attempt-01/run.json).

## The operator can connect customers to the shop

If customers use services that observe their wallets, the operator can have profiles on both sides of a payment. It can recognize a payment spending coins associated with one profile and reaching an address in the shop's profile. This reveals a relationship and the amount flowing along it.

The names in such a picture may initially be unknown. A checkout address can name the shop-associated profile. Other information would be needed to name a customer. Even unnamed wallet profiles can reveal repeated business relationships.

The controlled example below uses **fictional test amounts with no monetary value**. A “test sat” is a unit in the manufactured example.

![Two observed wallet profiles pay the shop 2.5 million and 4 million test sats. An unidentified payer sends 1.25 million. The shop sends 1.1 million to an unidentified recipient. All amounts are fictional.](diagrams/explainer-payment-links.svg)

Three different shop receive addresses were each paid once. The observer still reconstructed **7.75 million test sats received**. It linked 6.5 million to the two observed payer profiles. The third payer remained unidentified. Gross receipts alone do not establish sales revenue, profit or ownership of every payment.

**Evidence:** [the payment-graph analysis](PERSISTENT-CORRELATION.md#the-multi-user-payment-graph), [the reconstructed amounts and links](evidence/correlation-attempt-01/correlation.json), and [the independent checks](evidence/correlation-disclosure-verification.json).

## What ordinary use reveals

| Recipient | What it can learn from the reviewed requests |
| --- | --- |
| Main wallet service | The group of payment fingerprints, related payment history, requested transactions and submitted payments. It also ordinarily sees the connecting IP address, or a proxy's exit address. |
| Separate built-in helper services | Copies of individual checks sent to them. A startup block-height check does not reveal a wallet balance; a later transaction lookup can reveal a specific financial interest. Some later checks happen automatically. |
| Price and update services | App-use and connection information from generic requests. The reviewed calls do not contain wallet balances or payment identifiers. |
| Network and DNS providers | Connection destinations, timing and related name queries as their role permits. Passive observation of encrypted traffic does not automatically reveal the financial requests inside it. |

The main service's record can be linked through a connection even without knowing the user's name. An IP address alone is not proof of one person's identity. Shared wallets, watched addresses and shared internet connections also affect attribution.

Different server names do not establish separate privacy boundaries. Several names in the tested release share infrastructure. For cautious privacy planning, this research assumes those related services can pool their observations, and also considers sharing across providers. Common ownership and actual sharing remain unproved. [Recipient counts, shared infrastructure and the full visibility table](TRUST-MODEL.md).

## Your keys can stay private while your finances are observed

The ordinary requests examined did not send recovery words or private keys. Those protect the ability to spend. The questions sent to a remote service can still expose payment history and relationships.

Transport encryption can hide requests from passive observers along the route; the receiving service processes the questions. The examined Electrum connections also failed to check the server's identity properly, allowing an attacker who can redirect or intercept the connection to impersonate it. A correctly routed privacy proxy can hide the original connecting IP, but the service still receives the payment fingerprints. The separate helper has its own routing decision: choosing a main server or setting a main proxy does not by itself control every path. [Routing and protection limits](TRUST-MODEL.md#who-can-see-which-data).

The reviewed project does offer some technical Network help about sending payment metadata for history. It does not explain the full lasting-surveillance and shop-correlation consequences in the consumer material we reviewed. Its broad proxy-help assurance also conflicts with the helper's separate routing. Public technical discussions acknowledge related server-security risks. **We did not measure what ordinary users understood.** [Disclosure evidence and its limits](DISCLOSURE-AUDIT.md).

## What we demonstrated

We recorded three real, empty wallet sessions using the wallet's normal discovery behavior. Each disclosed **40 identifiers: 20 receiving and 20 change**. “Change” is the part of a payment returned to the wallet. All three wallet processes then exited.

We supplied one simulated checkout address and constructed a fictional later transaction history. Using only the saved traffic, that later history and the checkout address, the analyzer associated **40 shop identifiers** and reconstructed the payments shown above. It did not receive recovery words, wallet files or a list explaining which addresses belonged to whom. It could associate the shop's collection before any payment was present, and it refused to assign mixed-profile payments to a single identified payer.

The sessions ran the wallet's actual account and networking code without the desktop interface. Local test settings preserved normal address discovery. The later payment records were invented for the test: no real money was spent and no real blockchain confirmed them. No actual shop or customer was investigated. The advertised ElectrumR server's documented source was unavailable, which prevented an independent run of that software. [Full method, controls and limitations](PERSISTENT-CORRELATION.md#controlled-demonstration-after-all-clients-exit).

A separate [unfunded run using default network settings](evidence/default-session-attempt-01/run.json) reached eight different Electrum server names through successful responses or helper sends. Only its selected main service received the full 40-identifier collection. That distinction matters: several recipients does not mean each automatically receives the whole wallet.

## The trust you are placing in the service

Your financial privacy depends on the operator choosing **not to keep a lasting financial profile, identify it through outside clues, connect it to other users, share it, or keep watching it after you leave**. A promise about today's logging defaults does not remove those capabilities.

Before using the wallet, a person needs clear answers about who receives the payment identifiers, which settings cover every connection, what can remain observable afterward, and which server names may share observations. This explainer documents that trust burden. The [research report](REPORT.md), [version-specific server counts](DISCLOSURE-AUDIT.md#version-specific-destination-counts), [raw records](evidence/correlation-attempt-01/) and [reproduction instructions](REPRODUCE.md) provide the evidence behind it.
