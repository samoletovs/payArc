# payArc — Vision

> Source of truth for what this project is, why it exists, and what success
> looks like. Updated during discovery as we learn more.

## What is a payment gateway?

A **payment gateway** is the technological service that accepts and routes
payment data between a customer, an online merchant, the payment system, the
acquiring bank, and the card-issuing bank.

In plain terms: it is the infrastructure layer that allows an online payment
to be performed securely and to receive a real-time result.

In the modern digital economy, the payment gateway is one of the key
components of e-commerce, SaaS services, mobile apps, marketplaces, and
fintech platforms.

## Core responsibility

The main function of a payment gateway is to organize the **secure and
standardized transmission of payment information**.

When a user enters card data on a site or in an app, the gateway:

- accepts the payment data
- encrypts it
- runs security checks
- sends the request into the payment infrastructure
- receives the response from the banking system
- returns the result to the merchant and the user

The gateway acts as a mediator between several participants in the payment
chain.

## Actors

| # | Actor | Role |
|---|-------|------|
| 1 | **Cardholder** | The user who initiates the payment |
| 2 | **Merchant** | The company or service accepting payment |
| 3 | **Payment Gateway** | Technology layer for routing & processing payment data |
| 4 | **Payment Processor** | Processing system that talks to bank networks |
| 5 | **Acquiring Bank** | The merchant's bank |
| 6 | **Issuing Bank** | The bank that issued the customer's card |
| 7 | **Card Network** | Payment scheme (Visa, Mastercard, etc.) |

## End-to-end flow

### Step 1 — Initiation
User presses "Pay" and enters card data:
- card number
- expiration date
- CVV/CVC
- optionally 3D Secure confirmation

### Step 2 — Encryption
Gateway encrypts payment info using TLS/SSL and tokenization. Compliance with
**PCI DSS** is critical here (standard for storage and transmission of card data).

### Step 3 — Authorization
Gateway forwards the request:
- to the **payment processor**
- then to the **acquiring bank**
- via the **card network** to the **issuing bank**

The issuing bank checks:
- available funds
- card validity
- fraud risk
- limits and restrictions

### Step 4 — Bank response
Issuing bank returns a status:
- `Approved`
- `Declined`
- `Requires Authentication`
- `Suspected Fraud`
- … etc.

Response propagates back through the chain to the merchant application.

### Step 5 — Capture & Settlement
After successful authorization, funds are reserved; later, **settlement**
moves the actual money to the merchant.

## Key gateway functions

### 1. Security
- TLS encryption
- Tokenization
- PCI DSS compliance
- Anti-fraud monitoring
- 3D Secure
- Velocity checks
- Device fingerprinting

### 2. Payment routing
Modern gateways dynamically pick:
- acquiring bank
- processor
- regional infrastructure
- fallback processing channels

### 3. Multiple payment methods
- Bank cards
- Apple Pay
- Google Pay
- Bank transfers
- Buy Now Pay Later
- Crypto
- Local payment methods

### 4. APIs & integrations
For engineering teams, a gateway is API-first:
- REST API
- Webhooks
- SDKs
- Hosted Checkout
- Token APIs
- Subscription Billing APIs

## Why this matters

For **engineering teams**: a gateway is an API-oriented financial service
integrated into the backend of a product.

For **business**: it is a monetization mechanism, a global payment-acceptance
channel, and a cash-flow management tool.

## Project framing

> Updated 2026-05-16 after processing the initial materials in `discovery/`.

payArc is being scoped as a **lean PayFac / payment orchestration
business**, not an abstract research toy. The high-level architecture
sketch ([`discovery/2026-05-16-high-level-architecture.jpg`](discovery/2026-05-16-high-level-architecture.jpg))
explicitly labels the gateway core as **"our part"** and the acquirer as
external.

### Business model (PayFac / orchestrator)

We do **not** intend to:
- Hold an acquiring or e-money license
- Build direct ISO 8583 / card-network integrations
- Become a card scheme member

We **do** intend to:
- Be the API + onboarding + fraud-orchestration + routing layer
- Partner with an external acquirer (REST API integration)
- Optionally outsource the tokenization vault to stay SAQ-A
- Optionally outsource heavy anti-fraud (Forter-style) only above a volume
  threshold

### Target scale (per the initial financial model)

| Metric | Value |
|---|---|
| Volume | 300 tx/day → €10.8M GMV/year |
| Avg ticket | €100 |
| Merchant fee | 6% |
| Acquirer fee | 3% |
| Gateway spread | 3% |
| Annual revenue | ~€324k |
| Team | 3 people |
| Operating profit | ~€170k/year (~52% EBITDA) |

Source: [`discovery/2026-05-16-financial-model-ru.txt`](discovery/2026-05-16-financial-model-ru.txt).
The model does **not yet account for** chargebacks, rolling reserves,
refund ops, compliance escalation, PSP downtime — these go into the risk
section of `docs/plan.md`.

### Anti-fraud posture (staged)

Per [`discovery/2026-05-16-anti-fraud-early-stage-ru.txt`](discovery/2026-05-16-anti-fraud-early-stage-ru.txt),
fraud capability is **staged with volume**:

- **Stage 1 (≤150 tx/day):** basic rules, 3DS, manual review, 0–1 risk person
- **Stage 2 (1k–5k tx/day):** device fingerprinting, merchant scoring, alerts
- **Stage 3 (10k+ tx/day):** fraud team, ML models, streaming, graph analysis

Minimum production rule set on day one: velocity, geo-mismatch, BIN risk,
basic device fingerprint, VPN/TOR detection, **merchant monitoring**
(the dominant risk at our scale is merchant abuse, not cardholder fraud).

### Integration shape

Per [`discovery/2026-05-16-gateway-to-acquirer-formats-ru.txt`](discovery/2026-05-16-gateway-to-acquirer-formats-ru.txt):

- **Merchant → Gateway:** HTTPS + JSON REST. Always.
- **Gateway → Acquirer:** REST/JSON for v1 (no ISO 8583 — only required if
  we become an acquirer ourselves).
- Card data downstream uses network/vault tokens, never raw PANs.

### The "our part" perimeter

From the architecture sketch, the gateway internals are:

1. **Ingress** — Merchant calls `OUR PayFac API` (HTTPS + JSON)
2. **Tokenization** — Encrypt card data, generate a token, store securely
   (open question: do we store at all, or fully outsource the vault?)
3. **Pre-acquirer checks** — Fraud score, velocity, amount anomalies,
   IP / device checks. Possibly Forter-style external fraud pre-assessment.
4. **Decision branch** — Approve → continue / Require 3DS / Block
5. **Egress** — Send authorization / capture request to the acquirer
6. **Response** — Propagate result back to the merchant
7. **Supporting:** merchant dashboard, anti-fraud tool, ops console

### Research angles (where AI changes the game)

Even though this is a real lean business, it is also run as a research
experiment — hypothesis → prototype → measure → iterate or kill. Candidate
AI-native bets to prove/disprove:

1. **Agent-driven merchant onboarding** — compress weeks of manual KYB
   review into minutes via an LLM + structured-output pipeline
2. **Smart routing** — pick acquirer / retry path per transaction using a
   learned cost+approval policy (vs. static config)
3. **LLM fraud co-pilot** — augment rule engine with an LLM that explains
   declines and proposes new rules from chargeback cases
4. **Merchant abuse detection** — agent that monitors merchant behavior
   patterns (the dominant fraud risk at our scale)

The discovery phase produces:
- this `vision.md` (kept in sync as understanding deepens)
- `docs/glossary.md` (domain terms)
- `docs/questions.md` (open questions for the team to answer)
- `docs/plan.md` (architecture & build plan — written at the END)

## Open hypotheses to test

1. **AI-native routing** beats rule-based routing for cost/approval optimization
2. **Agent-driven merchant onboarding** can compress weeks to minutes
3. **LLM fraud co-pilot** can outperform classical fraud rules on edge cases
4. A lean 3-person PayFac orchestrator can hit ~50% EBITDA at €10.8M GMV
   (per the initial financial model — needs validation against real
   chargeback / rolling-reserve / PSP-downtime data)

## Validation against external research (2026-05-16)

After web research across primary sources
([`discovery/2026-05-16-web-research-synthesis.md`](discovery/2026-05-16-web-research-synthesis.md)),
several elements of the original framing are confirmed and a few are
adjusted:

### ✅ Confirmed

- PayFac-orchestrator framing (not full acquirer)
- REST/JSON to acquirer for v1, no ISO 8583
- Tokenization outsourced to vault (Basis Theory / VGS class)
- Anti-fraud staged with volume; merchant-abuse is the dominant risk early
- AI-native angles in onboarding/routing/fraud are real and underserved

### ⚠️ Adjusted

- **6% merchant fee is not viable for generic merchants.** Stripe's EU
  rate is ~1.5% + €0.25. The 6% model only holds in (a) high-risk
  verticals, (b) sub-€10 micro-merchants Stripe rejects, or (c) vertical
  SaaS bundles. **payArc v1 must commit to one vertical.**
- **Unmodeled costs ~€60–100k/yr**: rolling reserves (~€450k working
  capital locked at €10.8M GMV), PCI compliance audit, vault per-tx,
  3DS, cyber insurance. Tightens the lean P&L significantly.
- **Chargeback ratio is the hardest constraint** at small scale —
  ≤0.9–1% before Visa/MC fines kick in.
- **Orchestration space is crowded with Visa-backed unicorns** (Stripe,
  Adyen, Checkout.com, Gr4vy, Primer, Spreedly, VGS, Basis Theory). We
  cannot win on raw orchestration. The edge must be vertical/geographic
  focus or AI-native research-grade differentiation (likely both).
- **License posture**: start as a PayFac under a partner acquirer/EMI's
  umbrella — no own license needed. If we scale, the path is PI license
  via Latvijas Banka. PSD3 (~2026–2027) may shift thresholds; don't
  lock-in early.

### 🆕 New decisions baked into the plan

- **Vertical-first**, not horizontal-generic
- **Vault from day one** (Basis Theory or VGS)
- **3DS2 from day one** (acquirer-bundled or specialist; not in-house)
- **Open-source the gateway core** as a research artifact — the only
  asymmetry a 3-person team can build against Stripe's machine.

## Source materials

Raw research, articles, and notes shared by the team are stored in
[`discovery/`](discovery/). The index lives in
[`discovery/SOURCES.md`](discovery/SOURCES.md).
