# Who can see my wallet?

October 29 update: [official desktop capture](PACKAGED-WALLET.md), [valid-chain shop/departure proof](VALID-CHAIN.md), [certificate tests](CERTIFICATES.md) and [claim ledger](CLAIMS.md) now supplement the earlier evidence below. Earlier synthetic cases remain explicitly separate.

For a connected story that starts with the shopkeeper, read [the plain-English explainer](EXPLAINER.md). The examples below explore individual situations.

Opening this wallet asks a remote service which payments belong to the payment identifiers it supplies. The service can remember those questions and join the answers together. That can expose a financial picture associated with a connection, even while the recovery words stay safely on the user's device.

**For privacy decisions, this report assumes related services share what they see.** Six of the nine built-in Electrum destinations share one IPv4 segment. We treat those six as one group that can combine observations. We also consider sharing across all service providers. This is a cautious consumer assumption; common legal ownership and actual sharing have not been proved.

In one fresh, unfunded default-core test, **eight Electrum hosts had successful responses or helper sends**. Only the selected main service received all **40 wallet payment identifiers**. The other traffic included startup block-header checks. The default desktop source also includes separate price and update requests. More recipients does not mean each receives the same data.

This information is supplied during normal online use, without a separate privacy opt-in. Under the covert-operator model, it supports financial surveillance infrastructure: durable profiles and connections between people who pay one another.

The people and situations below are fictional. They explain demonstrated capabilities and source findings, not accusations about anyone's actual retention practices. [The technical report](TRUST-MODEL.md) links each data path to evidence.

## Maya checks whether her wages arrived

Maya opens the wallet at home. It asks one main service about a collection of payment identifiers, including ones she has not used yet. That service can remember the collection and associate it with her connection. For identifiers that have received money, it can use the public ledger to recover payments and unspent amounts.

It does not learn the word “wages” from the wallet's private labels. A real-world identity or purpose would require other information. But the user has already supplied the service a useful financial collection without sending a name.

**Privacy expectation:** checking a balance should make clear which service receives the collection and what that service could retain.

## Luis pays a shop and gets change

Luis spends an existing payment. His wallet sends the signed transaction to its serving service. That transaction contains the payment destination and amount. Because the service already knows the identifiers the wallet monitors, it may recognize an output returning to that collection as change and reconstruct the remaining observed funds.

The controlled experiment recovered the payment, fee, change and remaining balance from the recorded session alone. Its money was fictional test data, not a funded real-world wallet. A destination address alone also does not identify a shop's legal name.

**Privacy expectation:** “my keys never leave my device” should not be presented as “the service cannot see my finances.” Those are separate protections.

## Asha makes a new address and closes the app

Asha has never received money at a new address. The wallet can still ask about its hashed payment identifier while preparing for future use. The service can save that identifier. If a matching payment later appears on the public ledger, the service can recognize it without Asha reopening the wallet.

It does not need to break the hash or obtain her recovery words. It compares the saved identifier with identifiers computed from public payments. The experiment modeled this later match after the wallet process exited.

The same applies to identifiers already used: the old operator can see later receipts and spends from public records even if Asha changes servers and never comes back. If the change returns to an already disclosed identifier, that link is visible too. Completely undisclosed addresses require another link; the operator did not receive an unlimited master key.

**Privacy expectation:** a new address, quitting, unsubscribing or permanently leaving the server does not revoke identifiers already disclosed.

## Ben chooses a server he trusts

Ben selects a main server and assumes it is the only place his wallet will ask questions. A separate built-in helper has its own list of eight destinations. Startup can ask those services about a block header. Later, missing transaction or proof data can cause the helper to copy a particular financial lookup to that list. Some of those later lookups can happen automatically.

This does not mean every helper receives Ben's whole wallet. It does mean a main-server choice alone does not control every recipient. A separate controlled test showed eight services receiving the same transaction lookup before the first answer was returned.

**Privacy expectation:** one connection policy should cover the main service, helpers, prices and updates, with recipient and proxy differences disclosed.

## Nora switches to a different server name

Nora sees several names and assumes they represent independent choices. Six built-in Electrum names resolve into one IPv4 segment. Under this report's consumer threat model, their operators can combine observations. Switching among those names offers no assumed separation. If unrelated brands also share data, even a switch outside that segment does not erase earlier copies.

The exact legal relationships remain unresolved. The visible concentration is still a **major centralization risk**: one segment holds two-thirds of the literal destinations and three-quarters of the helper entries. Those fractions describe entries, not the probability a session selects them.

**Privacy expectation:** a list of different server names should not imply independently operated privacy boundaries.

## Sam uses a cafe's Wi-Fi

Sam's network can ordinarily observe connection destinations and timing. Passive observation of encrypted traffic does not reveal the wallet's full requests. The selected serving service, however, receives those requests after encryption ends there.

There is an additional problem in the examined Electrum connection code: certificates are not authenticated. An attacker able to redirect or intercept that path could pretend to be a server. This is a source/runtime finding; this investigation did not attack a cafe or another person's traffic. A functioning privacy proxy can change the IP a destination sees, while leaving the requested payment collection visible to that destination. Different wallet subsystems must use that proxy consistently for the expectation to hold.

**Privacy expectation:** explain separately who sees network activity, who receives financial requests, and whether the connection authenticates the intended service.

## Priya sees a price in dollars

The default source fetches generic prices from `bananablocks.com` and checks `electrumsv.io` for updates. Those services can see their own connection and app-use metadata. The reviewed calls do not send Priya's balance, payment identifiers or transaction IDs. Fetching a historical price chart is not uploading her payment history.

**Privacy expectation:** distinguish routine app metadata from disclosure of a financial ledger, while accounting for both.

## Mei runs a shop and never reuses an address

Mei gives every customer a different payment address. Her wallet has nevertheless asked its serving service about a collection of receiving and change identifiers. A covert operator opens the shop's checkout as an ordinary prospective customer and learns just one address. It does not need to buy anything.

If that address matches the disclosed collection, the operator can associate the collection with Mei's shop. It can then recognize receipts to other disclosed fresh addresses, examine earlier matching records, and keep watching those identifiers after the shop leaves the server. Address rotation did not hide the collection from the party that was given its membership. The anchor identifies a shop-associated collection; shared administration or watched outside addresses can affect what it proves about ownership.

The controlled demonstration linked one checkout address to 40 identifiers. Three different shop addresses received fictional payments, and the observer reconstructed all three without any wallet returning. No actual shop or customer was investigated.

**Privacy expectation:** fresh addresses alone do not stop a serving operator turning one checkout address into a wider view of the shop's observed finances.

## Two customers pay the same shop

Jon and Leila each use the wallet normally. The service already has separate collections associated with their connections. Their payments reach different addresses in the shop's observed collection. The operator can connect Jon's collection to the shop, connect Leila's collection to the shop, and record the amounts flowing along each link. Identity learned elsewhere can give those profiles names.

In the controlled later ledger, two observed payer collections sent 2.5 million and 4 million fixture satoshis to the shop. Another payer sent 1.25 million, but that payer's identity stayed unknown because its collection had not been observed. Gross receipts do not by themselves establish business revenue or profit. Still, even a partly unnamed payment graph can reveal commercially sensitive relationships.

**Privacy expectation:** the risk includes who pays whom and how much, across multiple users, without anyone enabling a financial-tracking feature.

## Eli reads that the addresses are private

Eli reads the linked documentation's description of private receiving addresses and sees that change addresses can improve privacy. He assumes that the serving service cannot connect his fresh addresses. That is a fictional but plausible misunderstanding: the service receives their payment identifiers together as part of synchronization.

There is some useful disclosure in optional Network help about sending payment metadata for history. The reviewed material does not explain persistent watching, the shop anchor or cross-user payment graphs. Proxy help also says its settings apply to every connection, although the helper has a separate routing decision. Public issue discussions do acknowledge related server-authentication risks, so the project is not silent about every network risk. The audit did not measure what real users understood or whether Eli's imagined belief is common.

**Privacy expectation:** explain the service's financial view before disclosure, and distinguish control of keys, protection from outside observers, and confidentiality from the service itself.

## What an understandable privacy screen would need to answer

- Which recipients will get my wallet identifiers, individual transaction lookups, and ordinary app metadata?
- Which choices apply to every network path, including helpers and proxies?
- Which server names share infrastructure or are treated as one correlation group?
- What can a recipient keep watching after I close the app or permanently leave its server?
- Can one checkout address identify other shop addresses, and can recipients link payments between users?
- What is observed, what follows from source code, and what is a conservative sharing assumption?

These are communication and product requirements for later work. This research does not implement a new wallet privacy screen or promise that changing a setting removes prior disclosures.

See the [controlled correlation demonstration](PERSISTENT-CORRELATION.md) and [disclosure audit](DISCLOSURE-AUDIT.md). The reviewed default counts refer to the tested 0.2.0 release; newer public source changes the destination inventory, as recorded in the audit.
