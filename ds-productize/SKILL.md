---
name: ds-productize
description: Paid-product readiness — monetization model, billing/entitlement integrity, pricing/packaging, go-to-market baseline. Use when turning a project into a paid product or auditing an existing monetization setup.
---

# /ds-productize

Projects reach technical ship-readiness with zero revenue readiness: no monetization model chosen, paid features unenforced, pricing invented in the release week, and no funnel instrumentation to learn from. Skill audits the business layer with the same file:line rigor the rest of the suite applies to code.

**Productize** — monetization, pricing/packaging, and go-to-market readiness audit + productization plan.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-productize`
- User asks to turn a project into a paid product / SaaS ("make this a paid SaaS", "how do I monetize this")
- User asks for a monetization or paywall audit ("is my billing production-ready", "audit my subscription setup")
- User asks to design pricing tiers or packaging ("design my pricing page", "which tiers should I offer")
- User asks for go-to-market readiness ("is this ready to sell", "GTM baseline check")

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "make this a paid SaaS", "monetization audit" | "optimize store listing / ASO" (→ ds-launch) |
| "design pricing tiers / packaging" | "full GDPR/KVKK privacy audit" (→ ds-compliance --privacy) |
| "is my paywall/billing production-ready" | "review billing API code quality" (→ ds-backend --audit) |
| "go-to-market readiness check" | "research competitors' architecture" (→ ds-benchmark) |
| "why does nobody convert to paid" | "optimize a conversion metric via experiments" (→ ds-tune) |

## Contract

**Dimensions:** A1 (GTM), A2, A3 (funnel), A11 (GTM signal)

- Covers three scopes: monetization (model + billing/entitlement integrity), pricing (metric + tiers + packaging + channels + unit economics), gtm (positioning + funnel baseline, including funnel-analytics instrumentation — ops telemetry delegated to ds-deploy).
- Audits and plans — generates findings and `ds/productize/plan.md`; payment-provider integration code itself is implemented by the user or ds-backend.
- Only recommends established patterns with published benchmarks — no speculative growth hacks.
- Minimal liability + maximum privacy: recommends Merchant-of-Record or managed billing over hand-rolled payment handling; funnel metrics are privacy-first (no PII in events, consent-gated where required).
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- State-exempt: audit + plan are regenerable from source; the plan file and git are the durable record.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Audit existing monetization/pricing/gtm state for gaps (recommended default) |
| `--plan` | Produce a productization plan (`ds/productize/plan.md`): model choice, tier design, GTM checklist |
| `--scope={x}` | Specific scope: monetization, pricing, gtm (comma-separated) |
| `--auto` | All scopes, no questions, single-line summary; B items listed and skipped |
| `--force-approve` | Apply `needs_approval` items without asking (CRITICAL still confirms per item) |

Without flags: present the full mode menu — Audit (recommended) — find gaps in monetization/pricing/gtm / Plan — design the productization path from current state / All — audit then plan / (Cancel). A disambiguating flag skips the menu.

## Scopes

### Monetization

1. Model fit — chosen model (freemium / hard paywall / subscription / one-time / hybrid) matches product type and cost structure; AI apps with variable per-unit cost use hybrid or usage caps; recommendations default to hybrid (base + metered) over pure usage-based (MON-01 benchmark)
2. Entitlement enforcement — every paid feature checks entitlement server-side; no client-only gating of paid capability
3. Billing integration — managed provider or MoR present; payment webhooks signature-verified; both idempotency layers audited — API-request keys and webhook event dedup are distinct checks (MON-04); no card data touches own servers
4. Subscription lifecycle — trial terms disclosed before purchase, renewal reminders, grace period + dunning for failed payments, restore purchases available
5. Cancellation parity — cancelling takes no more steps than subscribing; no dark patterns (roach motel, confirm-shaming, forced continuity)
6. Free-tier gate design — free tier demonstrates core value but preserves an upgrade reason; no bait-and-switch removal of shipped free features

### Pricing

1. Price metric — value metric selected before model/tiers (Stripe 4-property test: flexible with value, self-explanatory, hard to game, budget-aligned); seat-only pricing on agentic-AI products flagged (PLD-01, PLD-03)
2. Tier structure — 2-3 tiers with a marked target tier; decoy/anchor logic intentional, not accidental; public page ≤3-4 plans, ≤2 pricing axes (PLD-02)
3. Price presentation — charm vs round pricing matches positioning; per-day/savings framing on the pricing page; annual discount at segment norm (consumer 30-40%, B2B 15-20% — PRC-02/DSC-02) with savings badge
4. Packaging page — pricing page exists, lists outcomes over features, ≤3 choices, highlighted recommended plan
5. WTP evidence — price traceable to willingness-to-pay input (Van Westendorp for new-to-market, conjoint for established/tiered — WTP-01) and a competitor price map (CPR-01; delegate scan to ds-benchmark when present)
6. Commission/processor fit — store Small-Business programs claimed where eligible; current commission tables used (Play structure changes 30 Jun 2026 — CHN-02); web checkout processor matches revenue stage (MoR below tax-complexity threshold); sales motion matches ACV band (CHN-01)
7. Price externalization — prices/products defined in provider dashboard or remote config, never hardcoded in client builds
8. Price-change protocol — planned increases carry contract-clause check + notice period + grandfathering sunset (CHG-01/02); discounts under a ceiling with tracked cohorts (DSC-01)
9. Projection sanity — revenue plan anchored to segment-correct benchmarks (NRR, churn by segment, AI-adjusted gross margin, LTV:CAC floor semantics — PRJ-01)

### GTM

1. Value proposition — one-paragraph concrete promise exists and matches what the code ships (cross-checked against blueprint `spec-alignment` when fresh)
2. Persona/JTBD — target user and job-to-be-done stated somewhere durable (README, landing copy, plan)
3. Landing/conversion surface — landing page (or store listing for mobile) with headline, social proof slot, single primary CTA
4. Funnel instrumentation — acquisition→activation→revenue→retention events defined, object-action naming, privacy-first (no PII in properties, consent where required)
5. Revenue metrics baseline — MRR/churn/trial-to-paid measurable from existing data; LTV:CAC computable once ads spend exists
6. Launch plan — pre-launch checklist exists (waitlist/beta, announcement channels, press-kit basics) or is generated into the plan
7. Ecosystem openness (A11, advisory) — webhook emission, standard export formats (ICS/CSV/JSON), embeddable surfaces, public API posture flagged as an anti-lock-in GTM signal when a competitor offers it and this product lacks it; never a blocker (SKILL-SPEC §15); technical implementation is ds-backend's A11 scope

## Delegation

**Owns:** monetization, pricing, gtm, analytics (funnel) | **Delegates:** ds-compliance → subscription-law + privacy canonical audit; ds-backend → billing data model + webhook endpoint security pass; ds-deploy → analytics (ops telemetry); ds-benchmark → competitor price-map scan (CPR-01, advisory-handoff: absent → inline top-3-5 pricing-page scan); ds-launch → store/IAP listing + release execution; ds-research → pricing/competitor evidence (optional) | **Receives:** ds-ship → Phase 2 productize pass on paid-product intent

## Execution Flow

Setup → Discover → Audit → [Plan] → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → interactive menu.
2. **IDU:** Profile → {Type + Stack, Config.audience, Config.deploy, Config.data}. Findings({monetization, pricing, gtm, spec-alignment}) → verify + use. Absent → own analysis.
3. Ask the monetization-intent block once (single block, only unknowns): current/target model, target price range, B2B vs B2C vs prosumer, platforms (store IAP vs web checkout vs both).
4. Load references by active scope: [references/rules-monetization.md](references/rules-monetization.md) (monetization + pricing surface), [references/rules-pricing.md](references/rules-pricing.md) (pricing method, channels, unit economics), [references/rules-gtm.md](references/rules-gtm.md) (gtm).

**Gate:** Mode + scope + intent answers recorded. If fails → no response to intent block → proceed with `--audit --scope=monetization,pricing,gtm`, mark unknown intents `not-stated`, WARN, calibrate findings to "model not yet chosen" instead of guessing one.

### Phase 2: Discover

1. Search for billing/provider signals: payment SDK deps, webhook routes, product/price identifiers, paywall components, entitlement checks.
2. Search for pricing surfaces: pricing page routes/files, store product metadata, price literals in source.
3. Search for GTM surfaces: landing page, analytics/event calls, funnel definitions, launch docs.
4. Build inventory per scope: present / partial / absent, each with file:line evidence.

**Gate:** Inventory complete with evidence. If fails → a scope has zero detectable surface → mark scope `greenfield` (audit reports gaps as design targets, not violations), continue.

### Phase 3: Audit [--audit or default]

1. Evaluate every scope checklist item (Scopes section) against the inventory — each check yields finding / pass / N/A with reason.
2. Severity per the Severity table; benchmarks and thresholds from the loaded references. Security baseline on billing surfaces ([references/principles.md §5](references/principles.md)): validate at every boundary, least privilege on provider credentials, no secrets in source; config discipline ([references/principles.md §8](references/principles.md)): prices/product IDs externalized to provider config, never hardcoded.
3. Classify: **A** — code-level conformance to the already-chosen model (unverified webhook signature, client-only entitlement check, hardcoded price literal). **B** — model, tier, price, packaging, or promise changes (business decisions).
4. Cross-check value proposition against blueprint `spec-alignment` findings when fresh — a promised-not-implemented paid feature is CRITICAL here (selling what doesn't exist).
5. Write findings to `ds/audit/findings.md` (scoped overwrite: monetization, pricing, gtm).

**Gate:** Every checklist item has an outcome; findings written. If fails → un-evaluable check (e.g., store metadata unreadable) → record `N/A (unreadable: {reason})`, never silently skip.

### Phase 4: Plan [--plan or All]

1. Generate `ds/productize/plan.md` (overwrite per run): chosen/recommended model with rationale + benchmark, tier table with prices and gates, billing-provider decision path, GTM checklist (landing, funnel events, launch steps), open business decisions as an explicit decision table.
2. Every recommendation cites a rule ID from references or an inventory fact — no unsourced business advice. KISS/YAGNI ([references/principles.md §6](references/principles.md)): recommend the simplest stack that fits the stated revenue stage — no enterprise billing machinery, custom receipt servers, or multi-tier entitlement services pre-revenue.
3. Present the plan's decision table to the user; record chosen options in the plan file.

**Gate:** Plan written, decision table present. If fails → write unresolved decisions as `OPEN — needs owner decision` rows; plan ships with open rows rather than invented answers.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** state the question (`Decide these N items?`) and present each item compactly (one line `[severity] title — file:line or surface`) grouped by scope with counts; ask Apply all / per-scope bulk (`Apply all pricing` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → no response → `skipped (no response)`, proceed.

### Phase 6: Summary

```
ds-productize: {OK|WARN|FAIL} | Scope: {monetization,pricing,gtm} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

FRC+DSC accounting. Audit output: findings table grouped by scope. Plan output: `ds/productize/plan.md` path + open-decision count.

**Value Delivered:** 1-5 concrete bullets, real outputs only. Example shapes (placeholders, not literal):

- `{n} paid features had client-only gating — entitlements now flagged for server-side enforcement before launch`
- `Pricing page decision table produced: {n} tiers, target tier marked, {model} model backed by published conversion benchmarks`
- `Cancellation flow fails parity ({n} steps vs {m} to subscribe) — legal exposure flagged before first paying customer`

Zero-change run: `No gaps — monetization/pricing/gtm surfaces meet reviewed scope`.

**Gate:** Summary + Value Delivered printed; plan path confirmed when Phase 4 ran. If fails → plan unwritten → surface error, print plan content to chat as fallback, status WARN.

## Quality Gates

- Every monetization finding cites the file:line or surface (store metadata, provider dashboard item) it was observed on
- Every benchmark claim in findings/plan cites a rule ID from references — no from-memory statistics
- Recommendations never include a provider/package that fails Trust Verification (exists, maintained, fits revenue stage)
- W1: cite file:line or surface, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit + plan regenerable; plan file + git are the durable record. W10: defer to fresh `ds/audit/findings.md` for covered scopes (esp. spec-alignment); own scan only for uncovered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No monetization surface at all (pure OSS/internal tool) | Ask whether paid intent exists; no → exit with `not-applicable`, suggest ds-repo --oss-ready |
| Payment provider undetectable but billing code present | Ask user which provider; unanswered → audit provider-agnostic checks only, mark provider checks `N/A (provider unknown)` |
| Store-distributed app (IAP rules apply) | Route store-specific execution to ds-launch; keep model/tier/entitlement checks here |
| User rejects every B item | Plan records rejections as intentional decisions; report Ship-ready-to-sell: no with open count |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Entitlement bypass (paid feature free), unverified payment webhook, card data on own servers, selling a promised-not-implemented feature |
| HIGH | No cancellation parity / dark pattern (legal exposure), no dunning (25-30% of churn unmitigated), trial without disclosure, prices hardcoded in client |
| MEDIUM | No annual option, pricing page over 3 choices, missing funnel events, no target-tier highlight |
| LOW | Copy/framing improvements, missing savings badge, persona not written down |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Pre-revenue greenfield (no billing code) | All scopes `greenfield` → audit becomes design-target list; recommend `--plan` |
| Library/CLI with paid tier (license keys) | Skip store/IAP checks; audit license-key entitlement + web checkout only |
| Existing revenue, migration question (e.g., IAP → web checkout) | Present as B decision with commission math from references; never auto-migrate; pricing-model changes carry the MON-13 safety window (grandfather + shadow billing) |
| Multiple products in one repo | Ask which product; audit one per run, note others as out-of-scope |
| B2B invoice-based sales (no self-serve) | Skip paywall/trial checks as N/A; audit entitlement, pricing page, GTM only |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
