# payArc — Open Questions

> Questions to be answered (by Sam or by further research) before the plan
> is written. Updated 2026-05-16 after web research synthesis
> ([`discovery/2026-05-16-web-research-synthesis.md`](discovery/2026-05-16-web-research-synthesis.md)).

## Resolved (closed by discovery + web research)

- ✅ **Business model.** PayFac / orchestrator. No acquiring license, no
  ISO 8583, no card-scheme membership. External acquirer.
- ✅ **Scale target for v1.** ~150–300 tx/day, €100 avg ticket,
  €10.8M annual GMV.
- ✅ **Need ISO 8583 on day one?** No. REST/JSON to the acquirer.
- ✅ **Anti-fraud sophistication for v1.** Basic rules + 3DS + manual
  review. No ML/Forter at <1k tx/day.
- ✅ **Dominant fraud risk at our scale.** Merchant abuse, not cardholder fraud.
- ✅ **PCI scope strategy.** SAQ-A via outsourced vault — never let PANs
  touch our servers. Vault provider carries Level 1 PCI.
- ✅ **3DS server build vs. buy.** Buy. Use acquirer-bundled or specialist
  (Cardinal, Stripe Radar). Not in-house v1.
- ✅ **License on day one.** None. Operate under partner acquirer/EMI
  umbrella. Defer PI license decision until material volume + post-PSD3.
- ✅ **EU regulations apply.** PSD2 SCA (already in force), PCI DSS v4.0.1
  (since June 2024), GDPR. PSD3 expected 2026–2027.

## Open — Scope (highest priority — these gate the plan)

- [ ] **🔥 Which vertical?** Research shows generic Baltic merchants =
  no economic moat against Stripe. Candidates ranked by Sam's existing
  ecosystem fit:
  - **Vertical SaaS embedding** (payments inside era / turgo / future
    SaaS) — easiest, defensible, but tiny initial volume
  - **High-risk vertical** (crypto on-ramp, CBD, nutra) — high margin,
    high compliance burden, hard to acquire merchants ethically
  - **Baltic micro-merchants Stripe rejects** — feasible, but smallest TAM
  - **Marketplaces / two-sided platforms** (turgo-class) — payArc as
    the payment engine for marketplaces; aligns with NauroLabs ecosystem
- [ ] **Geography.** Latvia / Baltics / EU? Currency? PSD2 passporting
  changes this dramatically.
- [ ] **Methods.** Cards only for v1? Apple Pay / Google Pay? Local APM?
- [ ] **First real merchant.** turgo? era? An external pilot? Determines
  the actual integration shape of v1.

## Open — Acquirer & partnerships

- [ ] **Which acquirer?** Baltic candidates: Worldline (likely largest in
  the region), Nets/Nexi, SEB, Tietoevry. Global REST-friendly: Checkout.com,
  Nuvei, Rapyd. Need an introduction or RFP path.
- [ ] **Single vs. multi-acquirer.** Multi enables smart-routing research
  but doubles the integration burden. v1: single.
- [ ] **Rolling reserve negotiation.** What % and duration is achievable?
  At €10.8M GMV, every 1% of reserve = €108k locked up.
- [ ] **Umbrella PayFac option.** Could we operate as a sub-PayFac under
  someone like Adyen for Platforms or Stripe Connect, with our value-add
  being the AI/vertical layer? This sidesteps the acquirer hunt entirely.

## Open — Vault & tokenization vendor

- [ ] **Vault vendor:** Basis Theory vs. VGS vs. Skyflow vs.
  acquirer-bundled vault. Pricing, network-token support, EU data
  residency.
- [ ] **Network tokens** (VTS / MDES) from day one or later?
- [ ] **Account Updater** integration timing.

## Open — Anti-fraud (beyond Stage 1)

- [ ] **Merchant-monitoring co-pilot v1 shape.** Manual dashboard with
  rules + LLM-generated narrative summary, or a more agentic alert system?
  This is one of NauroLabs's research bets — needs a concrete design.
- [ ] **Forter / Sift / Stripe Radar threshold.** What volume justifies
  the cost? Likely ~1k tx/day per the staged roadmap.

## Open — Architecture & stack

- [ ] **Hosting.** Container Apps (most likely for an API-first service)
  vs. Functions vs. AKS. See [`.github/PLATFORM.md`](../../.github/PLATFORM.md)
  — payArc is off-path because SWA Free can't host a real API service.
- [ ] **Database.** PostgreSQL (relational, strong consistency for ledger)
  is the right choice over Cosmos despite the NauroLabs default.
- [ ] **Async / events.** Service Bus for webhooks + retries.
- [ ] **Secrets.** Managed Identity + Key Vault from day one.
- [ ] **Observability.** App Insights + immutable audit log (append-only
  storage or Cosmos with TTL=infinite + WORM).
- [ ] **Language.** TypeScript (Node) or Python (FastAPI)? Both viable;
  TypeScript aligns better with existing NauroLabs projects (era, turgo),
  Python aligns with foundryLab / mindMe AI patterns.

## Open — Operations

- [ ] **Cost ceiling for the prototype.** Sam's €150/month Azure credit
  must cover compute + storage + monitoring. Likely OK at v1 scale.
- [ ] **SLA targets.** Industry standard: <300ms auth, 99.95% uptime.
  Reasonable for v1 at single-region northeurope.
- [ ] **Reconciliation.** Daily acquirer settlement file → reconciler
  job. What's the data model for matching auth → capture → settlement?
- [ ] **Chargeback ops UI.** Pure manual at 150 tx/day, but the UI +
  evidence-collection flow needs to exist.

## Open — NauroLabs angle

- [ ] **Publishable artifact.** Working open-source PayFac core +
  research write-up? Public benchmark dashboard? Whitepaper on
  AI-native onboarding?
- [ ] **Cross-pollination with turgo / era.** Concrete: does turgo
  switch to payArc for its v2 payments?
- [ ] **Subdomain.** Decide in plan.md.
