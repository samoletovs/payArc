# payArc — Build Plan

> Drafted 2026-05-16 by agent, grounded in 5 source materials in
> [`discovery/`](discovery/) and the web research synthesis at
> [`discovery/2026-05-16-web-research-synthesis.md`](discovery/2026-05-16-web-research-synthesis.md).
> Awaiting team review.

## TL;DR

payArc is a **lean, vertical-focused, AI-native PayFac/orchestrator**,
not a generic Stripe competitor. v1 ships an open-source gateway core +
a single sandbox merchant integration (a demo merchant app built
alongside the gateway). Live cards are out of scope for v1; the proof is
**end-to-end flow against a sandbox acquirer**, exercising the AI-native
onboarding and routing layers that are the actual research bets.

---

## 1. Scope

### In scope for v1

- A **REST/JSON API** that accepts a `POST /payments` from a merchant and
  routes it to a sandbox acquirer (Checkout.com sandbox preferred for
  REST-first ergonomics; fallback Stripe Test Connect).
- A **vault integration** (Basis Theory sandbox preferred for cost + DX;
  fallback VGS) so card data never reaches our servers — **SAQ-A by design**.
- **3DS2** via the sandbox acquirer's bundled flow.
- **Merchant onboarding API + chat UI** — the agentic-KYB research bet.
- A **rule-based fraud engine** (velocity, BIN risk, geo-mismatch,
  VPN/TOR detection) + an **LLM "explainability layer"** that narrates each
  decline.
- **Merchant dashboard** (read-only v1) showing transactions, declines,
  rule firings, narrative explanations.
- **Webhook delivery** to merchants (auth/capture/fail events).
- **Append-only audit log** of every state change.
- **Open-source repo** with reproducible local-dev setup.
- **One reference merchant integration**: a small demo merchant app
  (or pilot merchant) calls payArc end-to-end.

### Out of scope for v1

- ❌ **Live cards / production acquirer** — sandbox only until plan v2.
- ❌ **PayFac license / PI license / EMI license** — we are not regulated
  yet, since no real funds move. License hunt begins in v2.
- ❌ **ISO 8583** — REST only.
- ❌ **Direct card-network integration** — we never talk Visa/MC directly.
- ❌ **Multi-acquirer routing** — single sandbox acquirer; "smart routing"
  research happens in v2 when 2+ acquirers exist.
- ❌ **Settlement / reconciliation** — sandbox doesn't really settle.
  Capture works but no real ledger reconciliation in v1.
- ❌ **Chargeback handling UI** — manual / out-of-band for v1.
- ❌ **In-house 3DS server** — use acquirer's.
- ❌ **In-house tokenization vault** — use Basis Theory / VGS.
- ❌ **Local payment methods, BNPL, crypto** — cards only.
- ❌ **Apple Pay / Google Pay** — defer to v2; sandbox cards prove the flow.
- ❌ **ML fraud models** — rules + LLM explainability is the v1 frontier.
- ❌ **Mobile SDK** — REST + a vanilla JS Elements iframe is the v1 surface.

### Vertical decision (carried over as an open question)

Research showed a generic horizontal play loses to Stripe. v1 assumes
**"technology proof first"**: ship a working sandbox PayFac with a
reference demo merchant integration so the engineering, security, and
AI hypotheses can be tested in isolation. The wider vertical question
(high-risk, micro-merchants, vertical-SaaS, marketplaces) is deferred
to v2 and gated on a deliberate vertical choice. **v1 is the technology
proof, not the commercial proof.**

---

## 2. Hypothesis

> A 3-person AI-native team can build an open-source PayFac orchestrator
> that compresses merchant onboarding from weeks to minutes, makes routing
> and fraud decisions explainable, and serves a defined vertical at
> sustainable margins — without obtaining a payment license in v1.

Concretely, v1 proves or disproves:

1. **H1 (Onboarding):** An LLM-driven KYB flow can take a merchant from
   "I want to accept payments" to "first sandbox auth succeeds" in
   **<10 minutes**, vs. industry's days-to-weeks.
2. **H2 (Explainability):** Every decline / 3DS challenge / route choice
   carries an LLM-generated human-readable explanation that an unskilled
   ops person can act on.
3. **H3 (Cost):** The whole prototype fits in a tight Azure budget
   (~€150/mo) while serving ≥100 tx/day on sandbox volume.
4. **H4 (Integration ergonomics):** A new merchant integration (custom
   backend wiring payArc into a working checkout flow) takes
   **<1 sprint** of focused work, end-to-end.

Each hypothesis is a measurable lab outcome regardless of commercial fate.

---

## 3. Architecture

### Component diagram (logical)

```
                                    Card networks (Visa, MC) — out of scope
                                                ▲
                                                │
                              ┌─────────────────┴─────────────────┐
                              │   Sandbox Acquirer (Checkout.com  │
                              │   sandbox / Stripe Test Connect)  │ ← external
                              │   includes 3DS2 server            │
                              └─────────────────▲─────────────────┘
                                                │  REST/JSON
                                                │
       ┌────────────────────────────────────────┴────────────────────────────────┐
       │                                                                          │
       │                          payArc — "our part"                            │
       │                                                                          │
       │  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐    │
       │  │ Public API       │    │ Decision engine  │    │ Acquirer        │    │
       │  │ POST /payments   ├───▶│ (rules + LLM     ├───▶│ adapter         │    │
       │  │ POST /merchants  │    │  explainability) │    │ (REST out)      │    │
       │  │ POST /webhooks   │    └────────┬─────────┘    └─────────────────┘    │
       │  └──────────────────┘             │                                      │
       │           │                       │                                      │
       │           ▼                       ▼                                      │
       │  ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐    │
       │  │ Onboarding agent │    │ Fraud rule engine│    │ Audit log       │    │
       │  │ (LLM KYB chat)   │    │ (velocity/BIN/   │    │ (append-only)   │    │
       │  │                  │    │  geo/device)     │    │                 │    │
       │  └──────────────────┘    └──────────────────┘    └─────────────────┘    │
       │           │                       │                       │              │
       │           ▼                       ▼                       ▼              │
       │  ┌─────────────────────────────────────────────────────────────────┐    │
       │  │     PostgreSQL — merchants, transactions, rules, decisions      │    │
       │  │     (no PAN ever; only vault tokens & last-4)                   │    │
       │  └─────────────────────────────────────────────────────────────────┘    │
       │           ▲                       ▲                                      │
       └───────────┼───────────────────────┼──────────────────────────────────────┘
                   │ token references      │ webhook events
                   │                       │
       ┌───────────┴─────────┐   ┌─────────┴────────┐   ┌──────────────────────┐
       │ Basis Theory vault  │   │ Merchant         │   │ Merchant dashboard   │
       │ (Elements iframe;   │   │ backend          │   │ (read-only React)    │
       │ card data never     │   │ (demo merchant)  │   │ Azure SWA            │
       │ touches our srvrs)  │   └──────────────────┘   └──────────────────────┘
       └─────────────────────┘
                   ▲
                   │ direct from cardholder browser
                   │ via Elements iframe
       ┌───────────┴─────────┐
       │   Cardholder        │
       │   (browser)         │
       └─────────────────────┘
```

### Data flow — `POST /payments` happy path

1. Cardholder browser loads merchant checkout → renders **Basis Theory
   Elements iframe** for card input. Card data never reaches our servers.
2. Elements posts card data to Basis Theory → returns **vault token**.
3. Merchant backend posts `{amount, currency, vaultToken, merchantId,
   metadata}` to payArc API.
4. payArc:
   - Validates merchant is active, KYB-approved.
   - Runs fraud rule engine → produces a decision + LLM-narrated reason.
   - If `allow` or `challenge` → calls Basis Theory Proxy to detokenize
     → forwards REST request to sandbox acquirer.
   - Receives auth response (≤300ms target round-trip including 3DS2 if
     frictionless).
   - Writes auth event to append-only audit log.
   - Returns `{paymentId, status, last4, declineReason?}`.
5. Webhook delivered async to merchant for state changes.

---

## 4. Stack choice + rationale

This stack is chosen for principled reasons given the domain (API-first,
security-heavy, async webhooks, real DB, secrets-heavy). Notable choices:

| Concern | Choice | Why |
|---------|--------|-----|
| Hosting | **Azure Container Apps** | Long-running REST API service with auth/fraud logic, scale-to-zero, managed identity, custom domains. A static-site host (e.g. SWA Free) is not sufficient. |
| Auth | **Custom API keys + Entra for dashboard** | Merchant auth is API keys (industry standard); dashboard auth uses Entra. |
| DB | **PostgreSQL (Azure Flexible Server)** | Payments need strong consistency, joins, double-entry ledger discipline. NoSQL is the wrong primitive for reconciliation. |
| Frontend | React + SWA (Free) | Read-only dashboard, static hosting is fine. |
| Secrets | **Key Vault + Managed Identity** | Acquirer credentials and vault API keys must be HSM-backed and rotatable. |
| Lang | **TypeScript (Node 20 LTS)** | Strong types map well to the payments domain; mature payment-SDK ecosystem; matches the team's expertise. Python (FastAPI) is a viable alternative if the team prefers. |

**Per-component stack:**

- **API service**: Node 20 LTS, TypeScript, Fastify (lighter than Express,
  built-in JSON schema validation), Zod for input validation, OpenAPI 3.1
  spec auto-generated. Deployed to Azure Container Apps, single replica
  v1, region `northeurope`.
- **DB**: Azure Database for PostgreSQL Flexible Server, Burstable tier
  (B1ms) for v1. Migrations via `node-pg-migrate` or Prisma Migrate.
- **Vault**: Basis Theory SaaS (preferred) or VGS. Elements iframe on
  merchant frontend; Proxy for outbound to acquirer.
- **Sandbox acquirer**: Checkout.com sandbox (REST-first, well-documented).
  Stripe Test Connect as fallback.
- **3DS2**: bundled with acquirer.
- **LLM**: Azure OpenAI (gpt-4o-mini class for explainability narration;
  gpt-4o for onboarding agent reasoning). Cost cap: ~€20/mo on the
  shared Azure subscription.
- **Frontend dashboard**: React + Vite + TypeScript on Azure SWA Free
  (read-only; calls payArc API with Entra ID auth).
- **Async/jobs**: Azure Service Bus (Basic tier, ~€10/mo) for webhook
  delivery retries. Event Grid for internal fan-out if needed.
- **Observability**: Azure Application Insights (free quota fits v1).
- **CI/CD**: GitHub Actions, OIDC to Azure, Bicep-based infrastructure.
- **Repo**: monorepo (api/, dashboard/, infra/, sdk/) under MIT or
  Apache-2.0 license (decision in v1 milestone M0).

### Estimated monthly Azure cost (sandbox only)

| Resource | Tier | Est. €/mo |
|----------|------|-----------|
| Container Apps | 1 replica, scale-to-zero outside business hours | 15 |
| PostgreSQL Flexible | B1ms, 32GB | 30 |
| SWA Free | Free | 0 |
| Service Bus Basic | Basic | 10 |
| Key Vault | Standard | 5 |
| App Insights | Free tier | 0 |
| Storage (audit log) | LRS, ~5GB | 2 |
| Egress | Sandbox volume | 5 |
| Azure OpenAI | gpt-4o-mini + small gpt-4o | 20 |
| **Total** | | **~€87/mo** |

Fits within the available ~€150/mo Azure budget. ✓

---

## 5. Data model

Five core entities. PostgreSQL schema sketch (illustrative, not final):

```sql
-- Merchant: a customer of payArc
CREATE TABLE merchant (
  id              UUID PRIMARY KEY,
  external_ref    TEXT UNIQUE,            -- merchant's chosen handle
  legal_name      TEXT NOT NULL,
  status          TEXT NOT NULL,          -- pending | approved | suspended | rejected
  mcc             TEXT,                   -- merchant category code
  country         TEXT NOT NULL,
  kyb_payload     JSONB,                  -- collected during onboarding
  kyb_decision    JSONB,                  -- LLM agent's decision + reasoning
  created_at      TIMESTAMPTZ DEFAULT now(),
  approved_at     TIMESTAMPTZ
);

-- API key: how a merchant authenticates
CREATE TABLE api_key (
  id              UUID PRIMARY KEY,
  merchant_id     UUID NOT NULL REFERENCES merchant(id),
  prefix          TEXT NOT NULL,          -- e.g. "pa_live_" or "pa_test_"
  hash            TEXT NOT NULL,          -- bcrypt of full key
  name            TEXT,
  created_at      TIMESTAMPTZ DEFAULT now(),
  revoked_at      TIMESTAMPTZ
);

-- Payment: a transaction attempt
CREATE TABLE payment (
  id                  UUID PRIMARY KEY,
  merchant_id         UUID NOT NULL REFERENCES merchant(id),
  amount_minor        BIGINT NOT NULL,    -- always in minor units
  currency            CHAR(3) NOT NULL,
  vault_token_ref     TEXT NOT NULL,      -- Basis Theory token id
  card_last4          CHAR(4),
  card_brand          TEXT,
  status              TEXT NOT NULL,      -- pending | authorized | captured | declined | failed
  decline_reason_code TEXT,
  decline_narrative   TEXT,               -- LLM-generated human explanation
  acquirer_ref        TEXT,               -- acquirer's payment id
  metadata            JSONB,
  created_at          TIMESTAMPTZ DEFAULT now(),
  authorized_at       TIMESTAMPTZ,
  captured_at         TIMESTAMPTZ
);

-- Decision: one row per rule/LLM evaluation, immutable
CREATE TABLE decision (
  id              UUID PRIMARY KEY,
  payment_id      UUID NOT NULL REFERENCES payment(id),
  decision        TEXT NOT NULL,          -- allow | challenge | block
  rules_fired     JSONB NOT NULL,         -- which rules matched
  llm_narrative   TEXT,
  score           NUMERIC(5,3),
  evaluated_at    TIMESTAMPTZ DEFAULT now()
);

-- Audit log: append-only stream of every state change
CREATE TABLE audit_event (
  id              BIGSERIAL PRIMARY KEY,
  occurred_at     TIMESTAMPTZ DEFAULT now(),
  actor           TEXT NOT NULL,          -- merchant:<id> | system | admin:<id>
  entity_type     TEXT NOT NULL,
  entity_id       UUID NOT NULL,
  event_type      TEXT NOT NULL,
  payload         JSONB NOT NULL
);
-- Audit log is append-only; ALL changes flow through it. Enforced via
-- revoked UPDATE/DELETE grants on the role used by the app.
```

**Encryption boundaries:**
- PostgreSQL: TDE on by default (Azure managed). No PANs ever in the DB.
- `vault_token_ref` is the only card-data identifier we hold; it's
  worthless without Basis Theory API auth.
- Secrets (acquirer credentials, vault keys, LLM keys) in Key Vault.

**Partition strategy:** none in v1 (single-region, single-tenant DB).
Future: partition `payment` and `decision` by `merchant_id` once volume
warrants.

---

## 6. Security posture

### PCI DSS scope

- **Merchant pages**: SAQ-A (card data goes browser→vault, fully iframed).
- **payArc API service**: SAQ-D Service Provider, level 4 (<1M tx/yr).
  No QSA audit required v1; we self-assess.
- **PostgreSQL**: contains no PAN, no CVV. Holds vault token references,
  last-4, BIN, brand only. Per PCI DSS v4.0.1, the BIN + last-4 are
  permitted to be stored.
- **Audit log**: holds the same. Never logs the vault token's plaintext
  detokenized value.

### Secret handling

- All secrets in **Azure Key Vault**. App accesses via **Managed Identity**.
- API keys for merchants: stored as bcrypt hashes; only shown once at creation.
- Acquirer credentials rotated quarterly via automated script.
- No `.env` file in repo; only `.env.example` with placeholders.

### Audit trail

- Every API call → entry in `audit_event` (action + actor + result).
- Every state change → entry. The table is append-only via DB grant.
- App Insights export retains 90 days; long-term audit stored in
  Azure Blob with immutability policy (WORM, 7-year retention).

### OWASP Top 10 alignment (v1 checklist, will be hardened in M5)

- A01 Broken Access Control → tenant isolation by `merchant_id` on every query.
- A02 Crypto failures → TLS 1.3 only; Key Vault for secrets; bcrypt for keys.
- A03 Injection → Zod input validation; parameterized SQL via Prisma.
- A04 Insecure Design → threat model in M0.
- A05 Misconfig → Azure Defender for Cloud baseline.
- A07 Auth failures → API-key + Entra; rate limits on auth endpoints.
- A08 Software integrity → Dependabot; SBOM in CI; signed container images.
- A09 Logging failures → structured logs to App Insights + audit log.
- A10 SSRF → outbound HTTP allowlist (vault + acquirer only).

### Threat model summary (full version in `docs/security/threat-model.md`, M0)

| Threat | Likelihood | Impact | Mitigation in v1 |
|--------|-----------|--------|------------------|
| Card data exfiltration | Low (no PAN) | High | Vault-only; SAQ-A |
| API key leak | Medium | High | Rate limits, audit, easy rotation |
| Acquirer credential leak | Low | Catastrophic | Managed Identity → Key Vault |
| Merchant abuse (fake business) | High | High | LLM KYB review + manual sign-off in v1 |
| Cardholder fraud | Medium | Low (sandbox) | Rules + 3DS2 |
| LLM prompt injection in onboarding | Medium | Medium | Structured output, server-side validation, no privileged tools |
| Replay of vault tokens | Low | Medium | Per-merchant token binding |

---

## 7. MVP slice (smallest end-to-end demoable thing)

> **The demo**: A live React page (a small demo merchant checkout)
> where a buyer enters a Visa test card, the request flows browser →
> vault → payArc → Checkout.com sandbox → returns approved, the
> dashboard shows the transaction with an LLM-narrated decision trail,
> and a webhook fires to the demo merchant.

Concretely the MVP slice is:

1. One demo merchant exists in the DB, pre-approved (KYB skipped for demo).
2. One API key issued for that merchant.
3. Basis Theory Elements iframe rendered on the demo merchant checkout page.
4. payArc `POST /payments` endpoint exists, accepting `{amount, currency,
   vaultToken, merchantId}`, returns `{paymentId, status}`.
5. Decision engine has 3 hard-coded rules + LLM narrator.
6. Acquirer adapter calls Checkout.com sandbox; returns auth result.
7. Dashboard shows the transaction with narrative explanation.
8. Webhook fires to the demo merchant with the auth result.

Anything beyond this is gated to a later milestone.

---

## 8. Milestones

Each milestone has a **measurable done criterion**. Estimated effort in
ideal-team-days (no calendar dates; pace is whatever pace).

### M0 — Foundation (idem)
- ✅ Discovery docs complete (this state)
- [ ] License chosen for the open-source repo (MIT recommended)
- [ ] Threat model written (`docs/security/threat-model.md`)
- [ ] Stack confirmed by the team (see §4 above)
- [ ] Vault vendor confirmed (Basis Theory vs VGS)
- [ ] Sandbox acquirer confirmed (Checkout.com vs Stripe)
- **Done when:** the team approves this plan + answers the four ⬚ items above.

### M1 — Skeleton (foundation code)
- [ ] Monorepo scaffolded: `api/`, `dashboard/`, `infra/`, `sdk/`, `docs/`
- [ ] `infra/main.bicep`: Container App + PostgreSQL Flexible + Key Vault
  + App Insights + Service Bus + SWA, deployed to Azure
- [ ] CI: GitHub Actions with OIDC to Azure, lint + test + build + deploy
- [ ] API service responds to `GET /healthz` with version + commit SHA
- [ ] PostgreSQL migrations: initial schema (merchant, api_key, payment,
  decision, audit_event)
- **Done when:** `/healthz` returns 200 on the deployed instance.

### M2 — Vault + acquirer integration (the technical heart)
- [ ] Basis Theory account, Elements integrated into a tiny dev page
- [ ] Checkout.com sandbox account, test merchant approved
- [ ] `POST /payments` accepts `{amount, currency, vaultToken, merchantId}`
- [ ] Acquirer adapter: detokenize via Basis Theory Proxy → call
  Checkout.com → return result
- [ ] Sandbox auth response stored in `payment` table
- **Done when:** a `curl` call with a sandbox vault token returns an
  `authorized` payment in under 1 second.

### M3 — Fraud rules + LLM explainability
- [ ] Rule engine framework (declarative rules in JSON, evaluated per payment)
- [ ] 3 rules: velocity (>5 tx/min from same IP), BIN risk (test list),
  geo-mismatch (BIN country ≠ IP country)
- [ ] LLM narrator: given the rule outcomes, generate one paragraph of
  human explanation; stored in `decision.llm_narrative`
- [ ] Every payment in `payment` has a linked `decision` row
- **Done when:** a deliberately-bad test transaction is declined with a
  human-readable narrative.

### M4 — Onboarding agent (the H1 hypothesis)
- [ ] `POST /merchants/start-onboarding` returns a session URL
- [ ] Chat UI in dashboard: LLM agent collects KYB data (legal name,
  country, MCC, beneficial owner, IBAN, expected volume)
- [ ] Agent produces a structured KYB decision: `{recommendation,
  risk_flags[], rationale}`
- [ ] Admin endpoint to approve/reject; on approve → merchant.status =
  approved + API key issued
- **Done when:** an honest fake merchant can complete onboarding end-to-end
  in <10 min on first try (per H1).

### M5 — Dashboard + webhooks + audit
- [ ] React dashboard (SWA): transactions list, single-tx detail with
  full narrative trail, rule firings, audit events
- [ ] Webhook delivery: Service Bus queue → worker → POST to merchant URL
  → retry with backoff
- [ ] Audit log immutable storage exported nightly to Blob WORM
- **Done when:** a merchant integrator can see every state change end-to-end
  with no DB access.

### M6 — Reference merchant integration
- [ ] A small demo merchant app (or external pilot's checkout) calls
  payArc instead of (a placeholder / Stripe)
- [ ] One real sandbox transaction flows end-to-end
- [ ] Webhook updates the demo merchant's order state
- **Done when:** the demo merchant's E2E test passes against payArc sandbox.

### M7 — Public artifact + write-up
- [ ] Repo made public + linkable (clear README, license, contribution guide)
- [ ] README with quickstart (`docker compose up` for local dev)
- [ ] Blog/whitepaper: "AI-native PayFac in <100kg LOC: what we learned"
  on the team's chosen publication channel (repo README, public blog,
  preprint server — decide at M7)
- [ ] Public landing page (subdomain TBD — see §11)
- **Done when:** an external developer can clone the repo, run it
  locally, and hit a sandbox auth in <15 min.

---

## 9. Risks

Distilled from the research synthesis. Severity = impact × likelihood at
*v1 (sandbox) scope*.

| # | Risk | Severity | Detection signal | Mitigation |
|---|------|----------|------------------|------------|
| R1 | The 6% fee assumption doesn't hold; no commercial path | **High** | Plan v2 vertical-choice exercise reveals no defensible vertical | v1 is engineering proof only; commercial decision deferred |
| R2 | Basis Theory / Checkout.com sandbox limitations block flow | Medium | Sandbox docs gap, ticket needed | Have VGS + Stripe Test Connect as named fallbacks in M0 |
| R3 | LLM onboarding agent fails H1 (>10 min on average) | Medium | M4 done-criterion test fails | Iterate on prompts; fall back to form-based KYB with LLM only for review |
| R4 | Costs creep past €150/mo Azure credit | Low | App Insights billing alert | Aggressive scale-to-zero; monthly cost report; switch to free tiers |
| R5 | PostgreSQL chosen but Cosmos was right | Low | DB queries become awkward | Reversible in v1; schema is simple; PG → Cosmos migration cost <1 week |
| R6 | Small team, no payments-industry deep contacts; can't sign a real acquirer in v2 | High | Cold outreach yields no response | Build for sandbox v1, use the public artifact + write-up to attract introductions for v2 |
| R7 | Open-source becomes our moat — but also lets competitors copy | Low | n/a | Embrace it; the moat is the AI-native operational layer + brand, not the gateway code |
| R8 | PSD3 lands during build and changes the rules | Medium | EU regulatory news monitoring | We hold no license in v1; impact is on v2 license path. Re-evaluate plan v2 at PSD3 entry into force |
| R9 | Chargeback ratio spike when we go live in v2 | High (v2) | Visa Dispute Monitoring alert | Out of scope v1; named for v2 |
| R10 | Vault/acquirer pricing makes unit economics unworkable | Medium | M2 cost-per-tx test against assumptions | Re-negotiate or re-pick vendor at M2 cost test |
| R11 | No willing reference merchant at M6 | Medium | M6 dropped or postponed | Build a synthetic demo merchant app inside the same repo; if external pilot lands later, swap |

---

## 10. Open questions

Carry-over from [`docs/questions.md`](questions.md) — these don't block
M0–M3 but must be resolved before later milestones:

1. **Vertical for v2 commercial play** — vertical SaaS embedding, high-risk,
   micro-merchants, or marketplaces? (Blocks v2 plan, not v1 build.)
2. **First production acquirer partner** — who, and how do we get the meeting?
   (Blocks v2.)
3. **License posture for v2** — own PI license vs. umbrella-under-someone?
   (Blocks v2.)
4. **Forter / Sift / Stripe Radar threshold** — what tx/day triggers the
   add? (Blocks v2 risk planning.)
5. **Merchant-monitoring co-pilot v1 shape** — manual dashboard with LLM
   narration (current plan) vs. agentic alerting system. (Blocks M5
   refinement.)
6. **Reference integration timeline** — is the M6 reference merchant a
   synthetic demo app, an external pilot, or both? (Blocks M6.)

---

## 11. Subdomain decision

**Recommendation: defer the public subdomain decision to M7.**

For v1 development and the sandbox demo, the Azure-provided URLs
(`<app>.<region>.azurecontainerapps.io` for the API,
`<app>.azurestaticapps.net` for the dashboard) are sufficient.

The DNS / subdomain choice at M7 depends on where the project ends up
hosted publicly — the team's own domain, a project-specific domain, or
the open-source repo README acting as the primary public surface.

**Action:** decide at the start of M7, after the open-source license
and publication channel are picked.

---

## 12. Done criteria for the experiment

payArc as a research experiment is **successful** if at the end of M7
**all four** of the following are true:

1. **Working artifact**: a developer can clone the repo, run
   `docker compose up`, and complete a sandbox transaction in under 15
   minutes. Demonstrates the "AI-native PayFac is buildable by 1–3
   people" claim.
2. **Hypothesis evidence**: H1 (onboarding <10 min) and H2
   (explainability) are demonstrated with a recorded end-to-end demo.
3. **Reference integration**: a reference merchant app (synthetic demo
   or external pilot) runs at least one transaction through payArc in
   sandbox. Proves integration ergonomics (H4).
4. **Public write-up**: a blog post / paper / repo write-up documenting
   what worked, what didn't, and what we'd build differently.

payArc is **a failed experiment** (but a valid outcome) if:
- After M3, the unit economics show no plausible vertical that survives
  the realistic ~€60–100k/yr unmodeled cost stack. We write up the
  finding and archive the repo. The research is still valuable.

payArc **graduates to a real business attempt (v2)** if:
- All success criteria above are met AND
- A specific vertical is identified with willing pilot merchants AND
- A path to a real acquirer (or umbrella) is concretely identified.

Otherwise it stays a research artifact in the public repository —
the project succeeded as a learning exercise, even if it does not
graduate to a business.
