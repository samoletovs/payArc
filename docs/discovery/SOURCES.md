# payArc — Sources Index

> Running index of source materials in this folder. Each entry: a citation,
> a one-paragraph takeaway, and pointers to where the material influenced
> `vision.md`, `glossary.md`, or `questions.md`.

Format:

```
## YYYY-MM-DD — <short title>

**Source:** <filename or URL>
**Provided by:** <Sam / agent research / etc.>

<one-paragraph takeaway>

Influenced: `vision.md` §<section>, `glossary.md` (added: …), `questions.md` (added: …)
```

---

## 2026-05-16 — Payment gateway description (Russian)

**Source:** [`2026-05-16-payment-gateway-description-ru.txt`](2026-05-16-payment-gateway-description-ru.txt)
**Provided by:** Sam, alongside the project creation request.

A definition-grade overview of what a payment gateway is, the seven actors
involved (cardholder, merchant, gateway, processor, acquirer, issuer, card
network), the end-to-end flow (initiation → encryption → authorization →
response → capture & settlement), the key gateway functions (security,
routing, payment-method support, API surface), and why gateways matter for
engineering teams vs. for business.

Influenced: `vision.md` (entire structure), `glossary.md` (full actor +
flow + security vocabulary).

---

## 2026-05-16 — Anti-fraud for an early-stage gateway (Russian)

**Source:** [`2026-05-16-anti-fraud-early-stage-ru.txt`](2026-05-16-anti-fraud-early-stage-ru.txt)
**Provided by:** Sam.

Pragmatic anti-fraud roadmap for a small payment gateway. Key claims:

- At ~150 tx/day, **enterprise anti-fraud (Forter-level) is not needed**.
  Basic rules + good acquiring + manual review is enough.
- Anti-fraud already exists at multiple layers: merchant, gateway,
  **acquirer**, issuer. Our gateway only needs to "shave off obvious fraud"
  and protect the chargeback ratio.
- Staged roadmap:
  - **Stage 1 (≤150 tx/day):** basic rules, manual review, 3DS, 0–1 risk person.
  - **Stage 2 (1k–5k tx/day):** device fingerprinting, merchant scoring,
    automated alerts, stronger risk engine.
  - **Stage 3 (10k+ tx/day):** dedicated fraud team, ML models, streaming
    analytics, graph analysis.
- Minimum production rule set: velocity, geo-mismatch, BIN risk, basic
  device fingerprint, VPN/TOR detection, merchant monitoring.
- Main fraud risk for a small gateway is **merchant abuse**, not
  cardholder fraud.

Influenced: `vision.md` (anti-fraud is staged, not big-bang ML),
`glossary.md` (added: BIN, MCC, rolling reserves), `questions.md` (closes
the "how much fraud tech do we need on day 1?" question — answer: very
little).

---

## 2026-05-16 — Financial model (Russian)

**Source:** [`2026-05-16-financial-model-ru.txt`](2026-05-16-financial-model-ru.txt)
**Provided by:** Sam.

Unit economics for a lean PayFac-style gateway:

- **Volume:** 300 tx/day × €100 avg ticket = €30k/day GMV → ~€900k/month →
  **€10.8M/year GMV**.
- **Spread:** 6% merchant fee − 3% acquirer = **3% net gateway margin**.
- **Revenue:** ~€27k/month → **~€324k/year**.
- **Team:** 3 people × €3,000 gross/month + 24% LV employer taxes = ~€11.2k/month
  payroll → ~€134k/year.
- **OPEX:** ~€1k/month infra + ~€700/month legal/accounting → ~€20k/year.
- **Total expenses:** ~€154k/year.
- **Operating profit:** ~€170k/year → **~52% EBITDA margin**.

Not yet modelled: chargeback losses, rolling reserves, refund ops,
compliance escalation, PSP downtime. The model assumes the company does
**not** hold its own acquiring license — it's an orchestration / reseller
PayFac model.

Influenced: `vision.md` (sized as a real lean business, not a toy),
`questions.md` (closes scale + team size questions; opens "where does the
6% merchant fee actually come from in our market?" and "what's the
rolling-reserve impact on cashflow?").

---

## 2026-05-16 — Gateway → acquirer integration formats (Russian)

**Source:** [`2026-05-16-gateway-to-acquirer-formats-ru.txt`](2026-05-16-gateway-to-acquirer-formats-ru.txt)
**Provided by:** Sam.

Technical reference for how the gateway talks downstream to acquirers /
processors:

- **Merchant → Gateway:** always modern HTTPS + JSON REST.
- **Gateway → Acquirer:** three options:
  1. **REST/JSON API** — modern processors (Stripe, Adyen, Checkout.com,
     Nuvei, Rapyd). The default early-stage choice.
  2. **ISO 8583** — legacy financial messaging standard used by Visa/MC
     networks, ATM rails, issuing/acquiring processors. Required only if
     we become an acquirer / build direct processor / build issuer
     processing / build our own payment rails.
  3. **Proprietary protocols** — TCP, XML, SOAP, host-to-host (legacy
     banks).
- The gateway is fundamentally a **translation layer**: modern API in →
  acquirer-specific protocol out.
- Card data downstream typically uses **network tokens / vault tokens /
  surrogate IDs**, not raw PANs. Security: TLS 1.2+, HSM, PCI DSS, P2PE,
  MAC/signatures.
- Authorization is real-time; settlement is batch (often SFTP / clearing
  files).

Influenced: `vision.md` (gateway = translation layer), `glossary.md`
(added: MTI, STAN, DE2/DE4/…, P2PE, HSM, MAC, clearing file),
`questions.md` (closes "do we need ISO 8583 for v1?" — answer: no, REST
acquirer is sufficient).

---

## 2026-05-16 — High-level architecture sketch

**Source:** [`2026-05-16-high-level-architecture.jpg`](2026-05-16-high-level-architecture.jpg)
**Provided by:** Sam, hand-drawn sticky-note style diagram.

Sketch of the system Sam intends to build. Key signals:

- **Card brands feeding in on the left:** Mastercard, Visa, Apple Pay,
  Google Pay.
- **Inbound:** "Merchant sends payment request to OUR PayFac API."
  → This frames payArc as a **PayFac (Payment Facilitator) / orchestrator**,
  not a full acquirer.
- **Inside our perimeter ("our part" — labelled in green):**
  1. Encrypt card data, generate a token, store token securely
     (PCI rules apply) — with a question mark beside "можем не хранить?"
     (can we avoid storing PANs entirely? → likely use external vault and
     stay SAQ-A).
  2. Pre-acquirer checks: fraud score, velocity rules, amount anomalies,
     IP / device checks. Fraud pre-assessment possibly via external
     vendor (Forter mentioned).
  3. Decision branch: **Approve & continue** / **Require 3DS** / **Block**.
  4. Send authorization / capture request to the **acquirer**.
- **Outbound:** the acquirer block sits outside "our part" — confirms we
  partner with an external acquirer rather than building one.
- Annotation: "IT затраты?" (IT costs?) — open question on hosting / infra
  cost ceiling.
- Annotation listing supporting systems: gateway, merchant dashboard,
  anti-fraud tool (Forter / Fortmer).

Influenced: `vision.md` (concrete component breakdown — tokenization,
fraud pipeline, decision branch, acquirer call), `questions.md` (opens:
"build-vs-buy for tokenization vault?", "Forter vs in-house fraud
heuristics — what's the budget threshold?").

---

## 2026-05-16 — Web research synthesis (competitors, regulation, PCI, economics)

**Source:** [`2026-05-16-web-research-synthesis.md`](2026-05-16-web-research-synthesis.md)
**Provided by:** Agent research; primary sources: Wikipedia (Payment_gateway,
ISO_8583, Acquiring_bank, Payment_Services_Directive, Strong_customer_authentication,
3-D_Secure), ECB (PSD2 explainer), Stripe (connect, docs.stripe.com/connect/onboarding),
VGS, Basis Theory, Gr4vy, PCI SSC document library.

Comprehensive market and regulatory landscape scan. Key findings, summarized:

- **Architecture taxonomy**: Gateway / Processor / Acquirer / PayFac /
  Orchestrator / Vault / Issuer / Card Network — the PayFac and Orchestrator
  roles are converging fast.
- **ISO 8583 not needed for v1** — confirmed; modern acquirers expose REST.
  But model internal data structures around ISO 8583 concepts (MTI-like
  message classes, response codes) to avoid being painted into a corner.
- **Stripe Connect at scale**: 16,000+ platforms, 11M+ accounts, $1B+ on
  104 platforms last year. Holds EMI license EU + MTL US so platforms
  don't have to. Three onboarding modes (hosted / embedded / API). **This
  is the canonical PayFac stack we're competing with.**
- **Sam's 6% merchant fee is unrealistic for generic merchants** — Stripe's
  EU rate is ~1.5% + €0.25. 6% is only viable in: (a) high-risk verticals
  (gambling, crypto, adult, CBD, nutra), (b) sub-€10 micro-merchants
  Stripe rejects, or (c) vertical SaaS where payments are bundled with
  software. **Generic Baltic merchants = no economic moat against Stripe.**
- **PSD2 in effect since 2018**; PSD3/PSR proposed June 2023, expected 2026–2027.
  PayFacs either need a Payment Institution (PI) or Electronic Money
  Institution (EMI) license, OR operate under another PI/EMI's umbrella.
  Passporting works across EU/EEA once authorized in one member state.
  Latvia regulator: FCMC / Latvijas Banka.
- **PCI DSS v4.0.1** (current, since June 2024). The only economical path
  is **SAQ-A** as a merchant (card data never touches our servers; vault
  proxies for us). PayArc as a Service Provider = SAQ-D SP at level 4
  initially (no QSA audit until ~1M tx/yr).
- **Vault providers** (Basis Theory, VGS, Skyflow) carry the heavy PCI
  Level 1 burden; we pay ~€0.05–0.15/tx + base. **Vault from day one** —
  never touch raw PANs.
- **3DS2 + SCA required by law** for EEA e-commerce. Use acquirer-bundled
  3DS server or a specialist; don't build it.
- **AI in payments** — fraud ML, smart retries, network tokens, account
  updater are all commodity. Real differentiation room: conversational
  KYB onboarding, explainable routing, merchant-behavior anomaly co-pilot,
  agentic dispute response, agentic commerce.
- **Unmodeled costs ~€60–100k/yr**: rolling reserves (5–10% of GMV held
  for ~6 months = ~€450k locked up), PCI audit (€15k–€80k), chargebacks,
  vault, 3DS, cyber insurance.
- **Chargeback ratio sacred**: Visa/MC fines kick in above ~0.9–1%. At
  150 tx/day that's ≤1.35 chargebacks/day. Single hardest constraint on
  a small PayFac.

Influenced: `vision.md` (added "Validation against research" section that
flags the 6% assumption and recommends vertical-first scoping),
`questions.md` (closed: ISO 8583 / scale / anti-fraud; opens new ones on
vertical choice, vault vendor, license path, rolling-reserve negotiation),
`plan.md` (entire plan is grounded in this synthesis).
