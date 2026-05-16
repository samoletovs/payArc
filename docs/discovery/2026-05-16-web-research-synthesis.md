# Web Research Synthesis — Payment Gateway / PayFac landscape

> Compiled 2026-05-16 from primary sources (Wikipedia, Stripe docs, ECB,
> EMVCo, PCI SSC, VGS, Basis Theory). Used to write `docs/plan.md`.
> Citations inline; full URLs at the bottom.

---

## 1. Architecture: the canonical online card transaction flow

From Wikipedia (Payment Gateway) + Stripe docs, the canonical flow is:

1. Customer's browser sends card data **directly to the gateway** (via iframe /
   hosted page / Elements) — this is the key trick to keep merchant out of PCI scope.
2. Gateway tokenizes + converts payload to acquirer-specific format (REST or ISO 8583).
3. Acquirer's processor forwards to card network (Visa/Mastercard).
4. Card network routes to issuing bank.
5. Issuing bank decides → response propagates back. **Typical RTT: 2–3 seconds.**
6. End-of-day batch: acquirer submits captures → card networks clear → funds
   move from issuer → acquirer → merchant (T+1 to T+3 typical).

The gateway itself is fundamentally a **translation + policy layer**. It does
not "move money" — it shapes the message and decides who to send it to.

### Architectural roles (consolidated taxonomy)

| Role | What it does | Who plays it |
|---|---|---|
| **Gateway** | Accepts merchant API, tokenizes, talks to processor | Authorize.net, Spreedly, payArc |
| **Processor** | Talks ISO 8583 to card networks | First Data/Fiserv, TSYS, Worldpay |
| **Acquirer** | Holds merchant account, settles funds | Worldline, Nets, SEB, Tietoevry |
| **PayFac** | Master-merchant under one acquirer; onboards sub-merchants | Stripe, Square, Adyen, payArc |
| **Orchestrator** | Routes across multiple acquirers/PSPs | Gr4vy, Primer, Spreedly, VGS, Basis Theory |
| **Vault** | Stores tokens; lets clients stay SAQ-A | Basis Theory, VGS, Skyflow, network tokens |
| **Issuer** | Issues cards, approves/declines | Banks |
| **Card network** | Routes auth between acquirers and issuers | Visa, Mastercard, Amex, JCB, Discover |

The interesting thing for payArc: **the line between PayFac and Orchestrator
is blurring fast**. Stripe Connect is a PayFac that also routes intelligently.
Primer/Gr4vy/Spreedly/VGS/Basis Theory are orchestrators that increasingly
look like PayFacs.

### Two business models inside payArc

If we read Sam's sketch and financial model carefully:

- **PayFac model** = we're the master merchant; sub-merchants sign up under
  us; we onboard, monitor, take 3% spread, handle support. **More margin,
  more risk** (we eat chargebacks above merchant's reserve).
- **Orchestration model** = we sit between merchants and their *own*
  acquirer relationships; we add fraud/routing intelligence; charge per tx
  or % of volume. **Less margin (~0.1–0.5%), less risk.**

Sam's 3% spread and 6% merchant fee strongly imply **PayFac**, not
orchestration. This is a critical assumption to validate (see §8).

---

## 2. ISO 8583 — when do we actually need it?

ISO 8583 is the 1987/1993/2003 legacy financial messaging standard. Key facts
from the Wikipedia deep-dive:

- **It is everywhere downstream**: Visa, Mastercard, Verve, all ATM networks
  base their authorization comms on ISO 8583 variants. Each scheme has its
  own private extensions.
- **It is not what merchants/gateways talk to**: modern acquirers expose
  REST APIs. ISO 8583 is the acquirer↔network protocol.
- **Bitmaps + Data Elements**: a message is an MTI (4 digits) + bitmap +
  up to 128 data elements (e.g. DE2=PAN, DE3=processing code, DE4=amount,
  DE7=timestamp, DE11=STAN, DE22=POS entry mode, DE39=response code,
  DE49=currency).
- **Response codes** are also standardized (00=approved, 05=do not honor,
  51=insufficient funds, 34=suspected fraud, etc.) — gateway-level routing
  decisions are made on these codes.

**Decision for payArc v1: do NOT build ISO 8583.** REST to the acquirer.
ISO 8583 is only required if we become a processor/acquirer ourselves.

But we SHOULD model our internal data structures around ISO 8583 concepts
(MTI-like message classes, response code mapping) so we're not painted into
a corner if we ever scale to direct network integration.

---

## 3. The big competitors — what they actually do

### Stripe Connect

Source: stripe.com/connect + docs.stripe.com/connect

- **16,000+ active platforms**, **11M+ onboarded accounts**, "$1B+ payments
  processed by 104 different platforms on Connect over the last year."
- Holds **EMI license in EU** and **MTL in US** — so platforms don't have
  to.
- Three onboarding modes: Stripe-hosted, embedded (themeable), API (full
  control + full pain).
- "Tokenises card data to help with PCI compliance; manages identity
  verifications, KYC, and sanctions checks while onboarding your users."
- This is the **canonical PayFac stack** we are competing with.

Stripe pricing in EU: typically **1.5% + €0.25 for EEA cards**, more for
international cards. **Not 6%.** This is the central blow to Sam's
financial model — see §8.

### Adyen

"Enterprise unified payments." Direct acquirer in many regions, doesn't
need a third-party acquirer. Much harder/more expensive to enter as a
merchant (no self-serve) but Tier-1 enterprise focus.

### Checkout.com

Modern REST-first competitor to Adyen. Strong in EMEA.

### Nuvei, Rapyd, Worldpay/Fiserv

Established processor/acquirers offering REST APIs to PayFacs and merchants.
These are who payArc would partner with — not compete with.

### Payment orchestrators (true peers if we go orchestration)

- **Primer** — "unified payments infrastructure", visual workflows,
  multi-processor routing.
- **Gr4vy** — "world's first cloud-based payment orchestration platform."
  Heavy on payment data portability, vendor-lock-in avoidance.
- **Spreedly** — vault + routing, longest-running orchestrator.
- **VGS (Very Good Security)** — "World's Leader in Payment Tokenization."
  Tokenization + network tokens + account updater + 3DS + payment
  orchestration. Investors include **Visa, Andreessen Horowitz, Goldman
  Sachs**. 7B tokens stored, 45B annual interactions.
- **Basis Theory** — payment vault + smart retries + multi-PSP routing.
  PCI Level 1, SOC 2 Type II, ISO 27001. Investor includes Visa
  (Visa OnTheList partner).

**Implication:** the orchestration space is **crowded with Visa-backed,
well-funded incumbents.** Sam's lean 3-person team cannot out-engineer them
on raw orchestration. payArc's edge has to be either:
(a) vertical/geographic focus (Baltic merchants Stripe doesn't bother with),
or (b) AI-native onboarding/routing/fraud as a real differentiator.

---

## 4. Regulation: PSD2 / SCA / PSD3

Source: Wikipedia PSD + ECB MIP Online + Strong Customer Authentication article.

### PSD2 — already in effect (since 2018)

- Directive (EU) 2015/2366. Transposed into national law across the EEA.
- Defines two regulated entity types relevant to us:
  - **Payment Institution (PI)** — non-bank entity authorized to provide
    payment services. **PayFacs need this OR must operate under a PI's umbrella.**
  - **Electronic Money Institution (EMI)** — for holding e-money. Stripe
    holds an EMI in the EU.
- **Passporting**: once authorized in one EU member state, you can offer
  services across the EU/EEA without a separate license per country.
  This is critical for any Baltic-launched PayFac wanting EU reach.
- **Strong Customer Authentication (SCA)**: legal requirement since
  14 Sept 2019 (final deadline 31 Dec 2020). Two of {knowledge, possession,
  inherence} required for most electronic payments.
- **Surcharge ban**: PSD2 prohibits merchants from charging customers extra
  for using cards (when both parties are in EEA). **This caps how much a
  PayFac can pass downstream as a per-transaction fee** — relevant for our
  pricing model.
- **Refund liability**: in the case of an unauthorized payment, the
  account-servicing PSP must refund the user immediately.

### PSD3 / PSR — coming

- **Proposed by European Commission in June 2023**; expected to enter into
  force ~2026–2027 (still in trilogue at the time of this writing).
- Strengthens open banking, fraud liability (issuers more liable),
  tightens authorisation, merges PI + EMI categories under a unified
  regime.
- **Implication for payArc**: any license strategy we sketch needs to be
  PSD3-aware. Capital and operational requirements will likely *increase*
  somewhat.

### Licensing decision tree for payArc

```
Are we just a SaaS gateway with no money flow? ─── No license needed
                                                   (but rare; almost any
                                                   payment service touches
                                                   "executing a payment")
              │
              ▼
Do we move/hold customer money?
              │
              ▼
PayFac under another PI/EMI's umbrella? ────── No license, but the umbrella
                                                provider sets the rules
              │
              ▼
Own PI license ────────────────────────────────── Initial capital: €20k-€125k
                                                   depending on activity;
                                                   ongoing regulatory burden
              │
              ▼
Own EMI license ─────────────────────────────────── Initial capital: €350k;
                                                     can hold e-money
```

**Realistic payArc path:** start as a PayFac under a partner acquirer's
umbrella (no license); if we hit material volume, apply for a PI license
in Latvia (FCMC / `Latvijas Banka` is the regulator).

---

## 5. PCI DSS — minimizing scope is everything

Source: pcisecuritystandards.org + VGS/Basis Theory marketing materials.

### Current version: PCI DSS v4.0.1 (June 2024)

- Replaces v3.2.1. Mandatory since 31 March 2024 (with some "future-dated"
  requirements that become mandatory 31 March 2025).
- Adds: customized approach, more emphasis on continuous validation,
  client-side script integrity (JS file tracking), MFA for all CDE access,
  new password rules.

### Self-Assessment Questionnaire levels (smallest → largest scope)

| SAQ | When it applies | Effort |
|-----|-----------------|--------|
| **SAQ-A** | E-commerce, all card data fully outsourced (hosted iframe/redirect; merchant has *no* PAN, even encrypted) | ~22 controls. Tractable. |
| SAQ-A-EP | Direct-post POST iframes; merchant page touches data briefly | ~191 controls. Painful. |
| SAQ-D Merchant | Stores, processes, or transmits cardholder data | Full DSS. PCI assessor required at higher levels. |
| SAQ-D SP | Service Provider (this is **us** as a PayFac) | Full DSS. Mandatory QSA assessment if Level 1. |

### Levels (by transaction volume — applies to gateway/processor):

| Level | Annual tx | Validation |
|-------|-----------|------------|
| Level 1 | >6M | External QSA audit annually + quarterly ASV scans |
| Level 2 | 1M–6M | Internal audit; ASV scans |
| Level 3 | 20k–1M | SAQ + ASV scans |
| Level 4 | <20k | SAQ; ASV scans recommended |

**payArc at 150–300 tx/day = ~55k–110k tx/year = Level 4 service provider
initially.** Still requires PCI DSS compliance (probably SAQ-D SP), but
no QSA audit until we cross 1M tx (~3000 tx/day).

### Scope reduction strategy (the only path that's economical)

The pattern used by every modern PayFac and orchestrator:

1. **Never let card data touch our servers.** Use a vault provider's
   iframe / Elements / Form Tokens so PANs go directly customer→vault.
2. **Operate on vault tokens** (not real PANs) inside our system.
3. **Vault detokenizes only when proxying out to the acquirer** (via VGS
   Proxy / Basis Theory Proxy / equivalent).
4. **Result: SAQ-A as a merchant; the vault provider carries Level 1 PCI.**

Vault providers offering this:
- **VGS** — proxy-based, "Zero Data" architecture; investors include Visa.
- **Basis Theory** — vault + smart retries + multi-PSP, PCI L1.
- **Skyflow** — multi-data-type vault (PII + PCI).
- **Network tokens (VTS/MDES)** — direct from Visa/Mastercard, replace
  PAN entirely for repeat usage; available via VGS/Basis Theory/acquirer.

**Decision for payArc v1: outsource the vault. Pick Basis Theory or VGS.
Stay SAQ-A as the gateway / SAQ-D SP "lite" as the PayFac.**

---

## 6. 3DS2 and fraud

Source: Wikipedia 3-D Secure + EMVCo.

### 3-D Secure 2.x (EMV 3DS)

- Replaces 3DS 1.0 (Verified by Visa / SecureCode). Mandatory under PSD2
  SCA for most EEA e-commerce.
- Risk-based: issuer can grant **frictionless** authentication if risk is
  low; only step up to a challenge (biometric/OTP) when needed.
- Sends ~100+ data points to issuer (device, address, history) for risk
  scoring — better-informed risk-based authentication.
- Liability shift: a 3DS-authenticated transaction shifts chargeback
  liability for "fraud" reason codes from the merchant to the issuer.

**Decision for payArc:** must support 3DS2 from day one to be EU-compliant.
Likely use the acquirer's bundled 3DS server (Worldline, Nets, etc. all
include this) OR a specialist (Cardinal, Stripe Radar). Building our own
3DS server is in scope for a "real gateway" but **out of scope for v1**.

### Fraud layers (consolidated)

| Layer | What it does | Day-1 essential? |
|-------|--------------|------------------|
| 1. Merchant antifraud | Order-level checks at the merchant | Up to merchant |
| 2. Gateway antifraud (us) | Velocity, BIN, geo, device fingerprint | **YES — basic rules** |
| 3. 3DS2 | Issuer risk-based step-up | **YES (regulatory)** |
| 4. Acquirer antifraud | Velocity at acquirer, MCC monitoring | Built into partner |
| 5. Issuer antifraud | Customer behavior, ML | Out of our control |
| 6. Vendor antifraud | Forter, Riskified, Stripe Radar, Signifyd | At higher volume |

This confirms Sam's anti-fraud staging exactly: we start with Layer 2 rules
+ Layer 3 3DS2; add Layer 6 vendor only past a threshold.

### Chargeback ratio is sacred

Card networks (Visa/Mastercard) impose fines on acquirers (and through them
the PayFac/merchant) when **chargeback ratio > ~0.9–1%**. At 150 tx/day,
that's **~1.35 chargebacks/day max**. Visa's "Visa Dispute Monitoring
Program" thresholds are even lower for new merchants. This is the single
hardest constraint on a small PayFac.

---

## 7. AI in payments — where the differentiation actually is

From competitor blogs (Stripe, Gr4vy, VGS, Basis Theory):

### Already commodity (table stakes, not differentiation)

- ML-based fraud scoring on aggregate features (Stripe Radar, Adyen RevenueProtect).
- Smart retries on soft declines (every orchestrator does this).
- Network tokens for higher auth rates (standard since ~2020).
- Account updater for stale-card replacement (standard).

### Emerging (where there's room to do something novel)

- **LLM-driven KYB onboarding** — extracting merchant data from documents,
  cross-checking against sanctions lists, generating risk briefs. Stripe
  uses this but doesn't expose it.
- **LLM merchant-monitoring co-pilot** — natural-language explanation of
  why a merchant's behavior is changing (volume spike, MCC drift, decline
  pattern shift). No competitor exposes this as a product.
- **Agentic dispute response** — auto-drafting chargeback rebuttal evidence
  from merchant data (Chargebacks911 does this but old-school NLP).
- **Agentic commerce** — VGS and Stripe both have "agentic commerce
  toolkits" (May 2026 launches) — AI agents transacting on behalf of users.
  Adjacent but worth watching.

### Where payArc could genuinely win (research-grade angles)

1. **Conversational merchant onboarding** — chat-based KYB that compresses
   weeks to minutes. Reference Stripe-hosted onboarding (~70% drop-off);
   conversational could halve that.
2. **Explainable routing** — every routing/decline decision returns an
   LLM-generated natural-language explanation; useful for ops + merchant
   trust.
3. **Merchant-behavior anomaly co-pilot** — agent watching merchant
   patterns; raises issues in natural language before a chargeback storm.
4. **Open-source the prototype** — almost nobody open-sources a working
   PayFac. Doing so would build NauroLabs credibility.

---

## 8. Economics — Sam's model, stress-tested

Sam's financial model assumed:

- 6% merchant fee, 3% acquirer cost, 3% gateway net spread.
- 300 tx/day, €100 avg ticket, €10.8M GMV/yr → €324k revenue.
- 3 people @ €3k gross + 24% LV employer taxes = €11.16k/mo.
- ~€170k operating profit / ~52% EBITDA.

### Reality check from market data

**Stripe in EU: ~1.5% + €0.25 standard rate.** For a €100 ticket, that's
about **1.75% all-in**. Adyen for enterprise is even lower (~0.6% +
interchange).

This means **payArc cannot realistically charge 6% to a generic merchant**.
Three scenarios that *can* charge 6%+:

| Scenario | Plausibility | Notes |
|----------|--------------|-------|
| **High-risk verticals** (gambling, CBD, adult, crypto, nutra) | High | These pay 5–10% routinely. But Visa/MC ratings as "high-brand-risk" require significant compliance overhead. |
| **Sub-€10 micro-merchants** that can't get Stripe accounts | Medium | Stripe rejects ~10–15% of EU applicants; some markets (Baltics small shops) can't get clean Stripe onboarding. |
| **Vertical SaaS PayFac** (we bundle payments with software they already need) | High | Standard SaaS-fintech model; merchant pays 3–4% but gets full POS/ops bundle. Toast, Mindbody, etc. work this way. |

### Revised financial model (more realistic scenarios)

**Scenario A — generic Baltic merchants (low risk):**
- 1.8% merchant fee − 1.0% acquirer = **0.8% net**
- €10.8M GMV × 0.8% = **€86k revenue/yr** → loss-making with 3 people.

**Scenario B — high-risk vertical (e.g. crypto on-ramp):**
- 4.5% merchant fee − 2.5% acquirer = **2.0% net**
- €10.8M GMV × 2.0% = **€216k revenue/yr** → ~€80k profit.

**Scenario C — vertical SaaS with embedded payments:**
- 3.0% merchant fee − 1.2% acquirer = **1.8% net**
- €10.8M GMV × 1.8% = **€194k revenue/yr** → ~€60k profit, plus
  SaaS subscription revenue on top.

**Scenario D — pure orchestration (no merchant of record):**
- 0.3% routing fee (no spread on processing)
- €10.8M GMV × 0.3% = **€32k revenue/yr** → not viable at this scale.

**Conclusion: the financial model works *only* if payArc serves a
specific vertical or risk class where 3%+ spread is normal.** A generic
"Baltic payment gateway" has no economic moat against Stripe.

### Other unmodeled costs

| Item | Annual impact |
|------|---------------|
| **Rolling reserve** | Acquirer holds 5–10% of volume for 6 months. At €10.8M GMV, ~€450k locked up = working capital problem. |
| **PCI compliance** | SAQ-D SP audit ~€15k–€30k/yr at Level 4–2; QSA ~€80k+ at Level 1. |
| **Chargebacks** | At 0.5% rate × €100 avg × €25 fee/chargeback = ~€14k/yr in fees alone, plus the lost goods value. |
| **Vault** | Basis Theory / VGS run **~€0.05–0.15/tx + base fee**. At 110k tx/yr ≈ €8k–€16k/yr. |
| **3DS** | ~€0.05–0.10/tx with vendor. ~€5k–€11k/yr. |
| **Insurance** | Cyber + E&O for a regulated PayFac: ~€15k+/yr. |

**These unmodeled costs ≈ €60k–€100k/yr** — i.e., a much larger hit to
margin than the original model showed.

---

## 9. Risks (consolidated)

| Risk | Severity | Mitigation |
|------|----------|------------|
| Cannot get acquirer to sign a small PayFac | **High** | Start by partnering with someone who needs a tech layer (vertical SaaS) rather than cold-calling Worldline. |
| 6% fee is unsustainable vs. Stripe at 1.5% | **High** | Pick a vertical where the fee is the going rate. |
| Chargeback ratio kills the program | High | Strict merchant onboarding; merchant-monitoring co-pilot is critical, not optional. |
| PSD2/PSD3 regulatory drift | Medium | Start under umbrella; defer license decision. |
| PCI scope creep | Medium | Outsource vault from day one — never touch raw PANs. |
| Rolling reserve choking cashflow | High | Negotiate hard; pick partners with shorter reserve periods (some EU acquirers do 1–3 months for low-risk merchants). |
| Visa/MC reputation risk (high-risk vertical) | Medium | If we go HR vertical, the cost is real but normal there. |
| Stripe-level competitor enters our niche | Medium | Move fast; build moat in onboarding UX. |
| Sam alone, no payments-industry deep expertise yet | High | Ship docs/plan & MVP slowly; treat first 6 months as learning. |

---

## 10. Decision posture — what this research changes

**Confirmed (Sam's instincts were right):**
- ✅ PayFac orchestrator framing, not full acquirer.
- ✅ REST/JSON for v1, no ISO 8583.
- ✅ Tokenization outsourced to vault.
- ✅ Anti-fraud staged with volume.
- ✅ Merchant abuse is the dominant risk at small scale.
- ✅ AI-native angles in onboarding/routing/fraud are real and underserved.

**Updated (research changed our position):**
- ⚠️ 6% merchant fee is **only viable in specific verticals** — generic
  Baltic merchants will not pay this. Pick a vertical.
- ⚠️ ~€60–100k/yr unmodeled costs (rolling reserve cashflow, PCI audit,
  chargebacks, vault, 3DS, insurance) — the lean P&L is tighter than it
  looked.
- ⚠️ Sam-alone (or 1-2 people) for early discovery is fine; the 3-person
  budget kicks in once we have an acquirer signed.
- ⚠️ PSD3 is coming (~2026–2027). Don't lock in license strategy yet.
- ⚠️ The orchestration space is **crowded with Visa-backed unicorns**.
  We cannot beat them on raw orchestration. Pick a niche or a research angle.

**New decisions to bake into the plan:**
- 🆕 **Vertical-first**, not horizontal: pick 1 vertical for v1 (likely
  vertical SaaS or a Baltic-specific niche).
- 🆕 **Vault from day one**: Basis Theory or VGS, decided before v1 ships.
- 🆕 **3DS2 from day one**: acquirer-bundled or specialist.
- 🆕 **Open-source the gateway core** as a research artifact — the only
  way a 3-person team builds a defensible brand against Stripe.
- 🆕 **Two-track development**: a real (small-scale, vertical) PayFac
  *and* an open-source / research artifact, sharing the same codebase.

---

## Sources

| # | URL | Used for |
|---|-----|----------|
| 1 | https://en.wikipedia.org/wiki/Payment_gateway | Canonical flow, white-label gateways |
| 2 | https://en.wikipedia.org/wiki/ISO_8583 | MTI, bitmaps, DEs, response codes |
| 3 | https://en.wikipedia.org/wiki/Acquiring_bank | Acquirer risk model, chargeback ratio |
| 4 | https://en.wikipedia.org/wiki/Payment_Services_Directive | PSD2, PSD3, PI/EMI licenses, passporting |
| 5 | https://www.ecb.europa.eu/paym/intro/mip-online/2018/html/1803_revisedpsd.en.html | ECB on PSD2, SCA, third-party PSPs |
| 6 | https://en.wikipedia.org/wiki/Strong_customer_authentication | SCA legal requirement, multi-factor |
| 7 | https://en.wikipedia.org/wiki/3-D_Secure | 3DS 1.0 vs 2.0, MPI, ACS, EMV 3DS |
| 8 | https://stripe.com/connect | Stripe Connect scale (16k+ platforms, 11M+ accounts) |
| 9 | https://docs.stripe.com/connect/onboarding | Hosted / embedded / API onboarding tradeoffs |
| 10 | https://www.verygoodsecurity.com/ | VGS scope, network tokens, account updater |
| 11 | https://www.basistheory.com/ | Basis Theory vault, smart retries, compliance |
| 12 | https://gr4vy.com/blog/ | Payment orchestration thinking |
| 13 | https://www.pcisecuritystandards.org/document_library/ | PCI DSS v4.0.1 current version |
