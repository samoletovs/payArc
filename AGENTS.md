# payArc — Agent Instructions

> Project-specific instructions for AI coding agents.

## Phase: 🔍 Discovery

**There is no application code yet.** This project is in the discovery phase.
The deliverables are documents in `docs/`, not code.

### Document layout

- `docs/vision.md` — problem statement, business model, target scale,
  research angles. Kept in sync as discovery deepens.
- `docs/glossary.md` — domain terms (cardholder, acquirer, PayFac, ISO 8583,
  rolling reserve, …).
- `docs/questions.md` — open questions, with a **Resolved** section for
  closed ones.
- `docs/discovery/` — raw source materials shared by the team.
- `docs/discovery/SOURCES.md` — index of materials with one-paragraph
  takeaways and pointers into vision/glossary/questions.
- `docs/plan.md` — architecture & build plan (written at end of discovery).

### Do NOT (during discovery)

- Scaffold code (`src/`, `api/`, `frontend/`, etc.)
- Pick a stack (React, FastAPI, Container Apps, Cosmos DB, …)
- Write Bicep / Terraform / `infrastructure/`
- Add a GitHub Actions deploy workflow
- Reserve any DNS / subdomain

The signal to leave discovery is: **`docs/plan.md` is written and the
team has approved it.** Nothing else.

## Discovery loop (when a new file lands in `docs/discovery/`)

1. Read it carefully (Russian / English / mixed — all fine).
2. Extract: key concepts, entities, flows, constraints, references.
3. Update `docs/vision.md` if framing shifts.
4. Update `docs/glossary.md` with any new domain terms.
5. Append unresolved items to `docs/questions.md` (or move closed items
   into the **Resolved** section).
6. Append a one-paragraph summary + citation to `docs/discovery/SOURCES.md`.
7. **Never rewrite or delete the original source file.**

## "Draft the plan" trigger

When the team says "draft the plan" (or equivalent like "let's write the
plan", "ready to plan", "compose docs/plan.md"):

- Synthesize everything in `docs/` into `docs/plan.md`.
- Required sections (see `docs/plan.md` template): scope, hypothesis,
  architecture, stack choice + rationale, data model, security posture,
  MVP slice, milestones, risks, open questions, subdomain decision,
  done criteria.
- Do **not** start writing code in the same session — present the plan
  for review first.

## Known framing (already established by the discovery materials)

- **Business model:** PayFac orchestrator, external acquirer, no license,
  no ISO 8583. ("Our part" is gateway internals only.)
- **Scale target:** 150–300 tx/day, €10.8M GMV/yr, 3-person team,
  ~52% EBITDA target (stress-tested in the plan — generic-merchant
  pricing is not realistic; vertical-first is required).
- **Anti-fraud:** staged — basic rules + 3DS + manual review at v1; no ML
  until 10k+ tx/day. Dominant risk is merchant abuse, not cardholder fraud.
- **Integration:** REST/JSON merchant→gateway and gateway→acquirer.
  Tokenization outsourced to a vault provider to stay SAQ-A.
- **AI research bets:** smart routing, agent onboarding, LLM fraud co-pilot,
  merchant-abuse detection.

These do not need to be re-asked or re-derived. Build on them.

## Stack: TBD

To be decided in `docs/plan.md`. Likely candidates given the domain
(API-first, security-heavy, async webhooks, real DB, secrets-heavy):

- Backend: Azure Container Apps (most likely)
- Database: PostgreSQL on Azure (transactions are relational, ACID matters)
- Async: Service Bus
- Secrets: Managed Identity + Key Vault from day one
- Frontend: minimal admin/merchant dashboard, if any
- Observability: Application Insights + append-only audit log

But again: **decide in `docs/plan.md`, not here.**

## Build / Test / Deploy

_To be filled in once a stack is chosen. Until then, the only "build" is
writing docs in `docs/`._
