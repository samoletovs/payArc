# payArc — Open Questions

> Questions to be answered (by Sam or by further research) before the plan
> is written. Updated 2026-05-16 after processing the initial discovery
> batch. Items in **Resolved** are already answered by Sam's materials in
> `docs/discovery/`.

## Resolved (closed by initial discovery batch)

- ✅ **Business model.** PayFac / payment orchestrator. We do **not** hold
  an acquiring license, do **not** implement ISO 8583, do **not** become a
  card-scheme member. Acquirer is external.
  (Source: architecture sketch — "OUR PayFac API" / "our part".)
- ✅ **Scale target for v1.** ~150–300 tx/day, €100 avg ticket,
  €10.8M annual GMV, 3-person team. ~52% EBITDA target.
  (Source: financial model.)
- ✅ **Need ISO 8583 on day one?** No. REST/JSON to the acquirer is
  sufficient until/unless we become an acquirer ourselves.
  (Source: gateway-to-acquirer formats document.)
- ✅ **Anti-fraud sophistication for v1.** Basic rules + 3DS + manual
  review, 0–1 risk person. Velocity / geo / BIN / device-fingerprint /
  VPN-TOR / merchant-monitoring. No ML/Forter at <1k tx/day.
  (Source: anti-fraud roadmap.)
- ✅ **Dominant fraud risk at our scale.** Merchant abuse, not cardholder
  fraud. Build merchant monitoring first.

## Open — Scope

- [ ] **Geography & market.** Latvia / Baltics / EU / global? Drives
  acquirer choice, currency support, PSD2/SCA scope, MCC mix.
- [ ] **Methods in scope for v1.** Cards only? Cards + Apple Pay/Google
  Pay (the sketch shows all four)? Any local APM?
- [ ] **Merchant verticals.** Generic merchants, or focus on a vertical
  where we have an edge (e-commerce / SaaS / marketplaces)? Could connect
  to turgo as a first internal merchant.

## Open — Tokenization & PCI

- [ ] **Do we store PANs at all?** Sketch annotates "можем не хранить?".
  Strong preference: **no** — outsource the vault to stay SAQ-A. Need to
  pick a vault partner (Basis Theory, VGS, acquirer's own vault).
- [ ] **If we store any card data, what's the PCI scope reduction plan?**
  Tokenization-only? P2PE? Hosted Checkout iframe?
- [ ] **3DS orchestrator — build or buy?** 3DS server stacks exist
  (Adyen, Stripe Radar, Cardinal); building one in-house adds significant
  PCI surface.

## Open — Acquirer & partnerships

- [ ] **Which acquirer(s)?** Baltic candidates: Worldline, Nets, SEB,
  Tietoevry. Global candidates: Worldpay, FIS, Checkout.com, Nuvei.
  Drives spread, settlement timing, supported methods.
- [ ] **Single acquirer vs. multi-acquirer routing?** Smart routing is one
  of our research bets — but it requires ≥2 acquirers integrated.
- [ ] **Rolling reserve.** What % does our chosen acquirer hold back, and
  for how long? Financial model assumes none — need to validate.
- [ ] **6% merchant fee — is that realistic in our market?** Stripe charges
  ~1.4% EU / ~2.9% US. 6% only makes sense for high-risk verticals or
  small Baltic-specific merchants. Financial model needs sensitivity
  analysis.

## Open — Anti-fraud (beyond Stage 1)

- [ ] **Forter / external fraud vendor — at what volume threshold?**
  Sketch shows Forter as optional. Define the trigger to add it.
- [ ] **Merchant-abuse detection.** What does v1 look like — manual
  dashboards, anomaly alerts, or an LLM co-pilot? (NauroLabs research bet.)

## Open — Architecture & stack

- [ ] **Hosting.** Container Apps (most likely for an API-first service)
  vs. Functions vs. AKS. See [`.github/PLATFORM.md`](../../.github/PLATFORM.md)
  for the golden path; payArc is off-path either way.
- [ ] **Database.** Cosmos DB (NauroLabs default) vs. PostgreSQL.
  Transactions are highly relational with strong consistency requirements
  → PostgreSQL is probably the right call.
- [ ] **Async / events.** Service Bus for webhooks + retries? Event Grid?
- [ ] **Secrets.** Managed Identity + Key Vault from day one (HSM-backed
  for crypto keys, processor credentials).
- [ ] **Observability.** Application Insights + structured audit log to
  immutable storage (append-only / WORM).

## Open — Compliance & legal

- [ ] **EU regulations.** PSD2, SCA, GDPR — when do they apply to a
  PayFac vs. an acquirer? Need legal opinion before launch.
- [ ] **Latvia-specific.** Any regulator notifications needed for a
  PayFac operating from LV? (Sam's employer-tax assumption is LV — confirm
  this is also the company-of-record jurisdiction.)
- [ ] **Licensing escalation path.** If we grow past PayFac thresholds,
  what's the path to a PI/EMI license — and what's the volume that triggers it?

## Open — Operations

- [ ] **Cost ceiling for the prototype.** Sam has €150/month Azure credit.
  Can the prototype live within that, or do we need a dedicated subscription?
- [ ] **SLAs.** Target latency, target uptime. Industry standard for
  authorization is <300ms / 99.95% — feasible at our scale?
- [ ] **Settlement & reconciliation.** Daily SFTP from acquirer? How do
  we reconcile our DB against acquirer settlement files?
- [ ] **Chargeback ops.** Process for receiving / responding to chargebacks.
  Pure manual at 150 tx/day, but we need the UI + escalation path.

## Open — NauroLabs angle

- [ ] **Publishable artifact.** Is the NauroLabs deliverable a working
  prototype, a public dashboard, a benchmark dataset, or a write-up
  comparing AI-routed vs. rule-routed?
- [ ] **Cross-pollination.** Does payArc accept payments for turgo (our
  marketplace) or era (our SaaS billing) as its first real merchant?
- [ ] **Subdomain.** Reserve `payarc.naurolabs.com` now or wait?
  (Working assumption: wait until `docs/plan.md` is approved.)
