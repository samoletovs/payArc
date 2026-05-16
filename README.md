# payArc

> Lean PayFac / payment-orchestration experiment — secure, API-first
> payment infrastructure with AI-native routing, onboarding, and fraud.

A standalone research-driven prototype. Run as an experiment: hypothesis →
prototype → measure → iterate or kill.

## Status: 🔍 Discovery

This project is in the **discovery phase**. No code yet, no stack committed,
no subdomain reserved. The deliverables of this phase are documents, not
applications.

- Vision & problem statement → [`docs/vision.md`](docs/vision.md)
- Domain glossary → [`docs/glossary.md`](docs/glossary.md)
- Open questions → [`docs/questions.md`](docs/questions.md)
- Source materials (research, articles, sketches) → [`docs/discovery/`](docs/discovery/)
- Architecture & build plan (written at the END of discovery) → [`docs/plan.md`](docs/plan.md)

## What is this?

payArc is a **PayFac (payment facilitator) / orchestrator**: the API +
onboarding + fraud-orchestration + routing layer between merchants and an
external acquirer. We are **not** building a full acquirer, not holding a
license, not implementing ISO 8583. The acquirer is a REST partner.

The framing was set by the initial materials in
[`docs/discovery/SOURCES.md`](docs/discovery/SOURCES.md):

- Target scale: **~150–300 tx/day, €10.8M GMV/year, 3-person team,
  ~52% EBITDA** (stress-tested against current market data in the plan)
- Anti-fraud is **staged** — basic rules + 3DS at v1, ML only past 10k tx/day
- The dominant fraud risk at our scale is **merchant abuse**, not cardholder fraud
- The gateway is fundamentally a **translation layer**: modern API in →
  acquirer-specific protocol out

## Research angles

Inside the lean-business shell sits the actual research experiment — proving
or disproving:

1. **Agent-driven merchant onboarding** — compress KYB from weeks to minutes
2. **AI-native smart routing** — learn acquirer choice + retry policy per tx
3. **LLM fraud co-pilot** — augment rules, explain declines, propose rules
4. **Merchant-abuse detection** — agent monitoring merchant behavior patterns

## How discovery works

1. The team drops research / articles / sketches into [`docs/discovery/`](docs/discovery/)
2. Agent processes them → updates `vision.md`, `glossary.md`, `questions.md`
   and appends a takeaway to [`docs/discovery/SOURCES.md`](docs/discovery/SOURCES.md)
3. Once enough material is gathered, the team says "draft the plan" → agent
   writes [`docs/plan.md`](docs/plan.md)
4. The team reviews the plan → discovery phase closes, build phase begins

Only after `docs/plan.md` is approved do we pick a stack, scaffold code,
provision infrastructure, or commit to a public subdomain.

## Conventions

- Project lifecycle: hypothesis → MVP → measure → iterate or kill
- AI-native: ask "what if AI did 90% of this?" before designing
- Open-source by default; a public artifact is one of the deliverables
