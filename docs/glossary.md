# payArc — Glossary

> Domain terms used in payment gateway architecture. Updated during discovery.

## Actors

- **Cardholder** — End user paying with a card.
- **Merchant** — Business accepting payment.
- **Payment Gateway** — Technology layer that accepts payment data from the
  merchant, encrypts it, and routes it into the payment infrastructure.
- **Payment Processor** — System that talks to card networks and banks on
  behalf of the gateway/merchant.
- **Acquiring Bank (Acquirer)** — The merchant's bank; receives funds from the
  card networks.
- **Issuing Bank (Issuer)** — The cardholder's bank; issued the card and
  ultimately approves/declines the transaction.
- **Card Network (Scheme)** — Visa, Mastercard, Amex, etc. Routes authorization
  messages between acquirers and issuers.
- **PSP (Payment Service Provider)** — Umbrella term covering gateway +
  processor + acquirer relationships, often bundled (e.g. Stripe, Adyen).

## Flow stages

- **Authorization** — Issuer confirms funds and validity; reserves the amount.
- **Capture** — Merchant requests the reserved funds. Can be immediate or
  delayed (e.g. ship-then-charge).
- **Settlement** — Actual movement of funds from issuer → acquirer → merchant.
- **Refund** — Returning funds to the cardholder after settlement.
- **Reversal / Void** — Cancelling an authorization before capture.
- **Chargeback** — Cardholder disputes a transaction; funds clawed back from
  the merchant.

## Security & compliance

- **PCI DSS** — Payment Card Industry Data Security Standard. Regulates how
  card data may be stored, processed, and transmitted.
- **Tokenization** — Replacing card numbers (PANs) with non-sensitive tokens
  so the merchant never touches raw card data.
- **3D Secure (3DS / 3DS2)** — Cardholder-authentication protocol (e.g. SMS
  code, biometric prompt in banking app).
- **TLS** — Transport encryption for data in transit.
- **Velocity checks** — Rate-limiting transactions per card / IP / device to
  detect fraud.
- **Device fingerprinting** — Identifying a device across sessions to detect
  fraud patterns.
- **SAQ (Self-Assessment Questionnaire)** — PCI DSS compliance level a
  merchant must complete; depends on how card data is handled.

## Payment methods

- **Card payments** — Visa / Mastercard / Amex etc.
- **Wallets** — Apple Pay, Google Pay; act as tokenized card credentials.
- **Bank transfers** — Direct bank-to-bank (SEPA, ACH, …).
- **BNPL (Buy Now Pay Later)** — Klarna, Affirm, etc.
- **APMs (Alternative Payment Methods)** — Local methods like iDEAL,
  Bancontact, Sofort, Blik.
- **Crypto** — On-chain settlement (still rare for retail).

## API surface

- **REST API** — Synchronous request/response for payment intents,
  captures, refunds, customers.
- **Webhooks** — Async server-to-server notifications (e.g.
  `payment.succeeded`, `chargeback.created`).
- **SDKs** — Client libraries wrapping the REST API and tokenization.
- **Hosted Checkout** — Gateway-hosted payment page that keeps the merchant
  out of PCI-DSS scope.
- **Token APIs** — Convert raw card data into reusable tokens.
- **Subscription Billing APIs** — Recurring charges, plans, dunning.

## Response statuses

- `Approved` — Transaction allowed.
- `Declined` — Transaction refused (insufficient funds, invalid card, …).
- `Requires Authentication` — Issuer requires 3DS step.
- `Suspected Fraud` — Refused due to fraud heuristics.
- `Soft Decline` — Retryable decline (e.g. transient issuer issue).
- `Hard Decline` — Non-retryable decline (e.g. lost/stolen card).

## Business / regulatory

- **PayFac (Payment Facilitator)** — A model where one entity (us, payArc)
  signs up sub-merchants under its own master merchant account with an
  acquirer, instead of each merchant signing up directly. Lower barrier
  for merchants; we own onboarding, monitoring, support.
- **Payment Orchestration** — A meta-layer that routes transactions
  across multiple acquirers/PSPs. Often combined with PayFac.
- **MCC (Merchant Category Code)** — 4-digit code classifying a merchant
  (e.g. 5732 = electronics, 7995 = gambling). Drives interchange fees and
  risk scoring.
- **BIN (Bank Identification Number)** — First 6–8 digits of a card,
  identifying the issuing bank. Used for routing, fees, and risk.
- **Rolling Reserve** — A percentage of merchant volume the acquirer
  holds back (e.g. 5–10% for 6 months) to cover potential chargebacks.
  Significant cashflow impact for the merchant.
- **Chargeback Ratio** — Chargebacks ÷ transactions. Card networks
  impose penalties above ~0.9–1%; gateway must protect this aggressively.
- **PSD2 / SCA** — EU regulation (Payment Services Directive 2 / Strong
  Customer Authentication). Mandates 3DS-style authentication for most EU
  payments above small thresholds.
- **SAQ-A** — Lowest PCI DSS Self-Assessment Questionnaire level. Available
  only if the merchant never touches raw card data (uses Hosted Checkout
  or external tokenization vault).
- **KYB (Know Your Business)** — Merchant equivalent of KYC. Required
  before onboarding a sub-merchant under a PayFac.

## Card-network messaging (ISO 8583)

- **ISO 8583** — Legacy financial-messaging standard used by Visa,
  Mastercard, acquiring processors, and ATM networks. Required for
  direct card-network integration; **not** required for early-stage
  gateways that talk to acquirers via REST.
- **MTI (Message Type Indicator)** — 4-digit ISO 8583 message class
  (e.g. `0100` = authorization request, `0110` = authorization response).
- **STAN (System Trace Audit Number)** — Unique transaction sequence
  number for tracing within an ISO 8583 session.
- **Data Elements (DEs)** — Numbered fields in an ISO 8583 message.
  Common ones: DE2 (PAN), DE3 (processing code), DE4 (amount), DE7
  (timestamp), DE11 (STAN), DE49 (currency).
- **POS Entry Mode** — DE22; how the card data was captured
  (chip / swipe / contactless / e-commerce keyed).

## Crypto & key management

- **HSM (Hardware Security Module)** — Tamper-resistant hardware that
  stores cryptographic keys. Required by PCI DSS for key management at
  card-network scale.
- **P2PE (Point-to-Point Encryption)** — Encrypting card data at the
  terminal so it stays encrypted all the way to the decryption point —
  takes intermediate systems out of PCI scope.
- **MAC (Message Authentication Code)** — Cryptographic checksum on a
  financial message to detect tampering.
- **Network Token** — Card-network-issued token (Visa Token Service /
  Mastercard Digital Enablement Service) that replaces the PAN for
  e-commerce; can be used cross-merchant.
- **Vault Token** — A token issued by a tokenization vault (in-house or
  external like Basis Theory / VGS) referring to a stored PAN.

## Settlement

- **Clearing File** — Daily batch file (typically SFTP) from the
  acquirer summarizing the day's transactions for settlement.
- **Settlement Batch** — The set of authorized + captured transactions
  cleared together (usually daily).
- **Funding** — The actual bank wire from the acquirer to the merchant's
  bank account after settlement.
- **Interchange** — Fee paid by the acquirer to the issuer for each
  transaction; the largest cost component in card processing.
