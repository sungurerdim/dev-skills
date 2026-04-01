# /ds-analytics

Most apps either track everything (privacy violation) or nothing (flying blind). This skill designs the minimum event taxonomy that gives you maximum insight — privacy-first.

**Analytics & Metrics** — Privacy-first analytics setup, event taxonomy, funnel design, and user insights.

## Triggers

- User runs `/ds-analytics`
- User asks about analytics, metrics, event tracking, or user insights
- User asks "what should I track" or "set up analytics"
- User asks about retention, churn, funnels, or A/B testing

## Contract

- Privacy-first: maximum insights with minimum data collection
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- FRC+DSC enforced.
- Generates event taxonomies, tracking plans, and dashboard specs — not tracking code
- **Maximum privacy:** recommends privacy-respecting tools, no invasive tracking
- **Minimum dependencies:** prefer self-hosted or minimal analytics over heavyweight SDKs
- **Maximum efficiency:** focus on actionable metrics, not vanity metrics

## Arguments

| Flag | Effect |
|------|--------|
| `--design` | Event taxonomy design: naming, hierarchy, properties |
| `--setup` | Analytics integration guide for project's stack |
| `--audit` | Audit existing analytics for gaps, privacy issues, noise |
| `--auto` | All modes, no questions, single-line summary |

Without flags: present interactive mode selection.

## Scopes

### Event Taxonomy Scope

| Area | What It Covers |
|------|---------------|
| Naming | `object_actioned` in snake_case, past tense (e.g., `signup_completed`, `plan_upgraded`) |
| Hierarchy | Area > Object > Action (e.g., `auth > password > reset_requested`) |
| Properties | Required vs optional per event, snake_case, units in name (`duration_seconds`), no PII |
| Standards | Taxonomy versioning, deprecation with `_legacy` suffix, CI lint for convention |
| Template | Starter event taxonomy covering auth, onboarding, core feature, subscription, referral, errors |

### Funnel Scope

| Funnel | What It Covers |
|--------|---------------|
| Acquisition | Install → First open → Signup → Activation |
| Activation | Signup → Core action → Value moment ("aha") |
| Retention | Day 1 / Day 7 / Day 30 return rates |
| Revenue | Free → Trial → Paid → Renewal / Upgrade |
| Referral | Share action → Invite sent → Invite accepted |

### Metrics Scope

| Category | Metrics |
|----------|---------|
| Engagement | DAU, MAU, DAU/MAU ratio, session length, screens/session |
| Retention | Day 1/7/30 retention (targets: >40%, >20%, >10%), cohort curves, churn rate |
| Churn signals | Leading indicators (login frequency drop, feature disuse), intervention triggers |
| Revenue | MRR, ARR, ARPU, LTV formula (ARPU × gross margin / churn), NRR, Rule of 40 |
| Quality | Crash-free rate, ANR rate, error rate, app rating |
| Growth | Install rate, organic vs paid, viral coefficient (K-factor) |

### Privacy Scope

| Check | What It Covers |
|-------|---------------|
| Data minimization | Only track what you'll act on |
| Consent | Proper opt-in/opt-out for tracking |
| PII | No PII in event properties (no emails, names, IPs) |
| Tools | Privacy-respecting tool recommendations |
| Compliance | GDPR consent, ATT (iOS), CCPA opt-out |

Recommend analytics tool based on privacy requirements — see `references/tool-comparison.md`.

## Execution Flow

Setup → Discover → Design/Audit → Generate → [Needs-Approval] → Summary

### Phase 1: Setup

**Goal:** Understand analytics needs and context.

1. If flags provided, proceed directly
2. If no flags, present interactive menu
3. **IDU:** Profile → Config.data, Config.audience, Config.regulations, Type+Stack. Findings(privacy, coverage, noise, quality) → verify + use. Absent → own analysis.
4. Detect platform (web, mobile, API) from project signals
5. Detect existing analytics (search for analytics SDKs in dependencies)
6. Ask: Which decisions will analytics inform? Options: feature prioritization, monetization, quality improvement, user retention

**Gate:** Platform and goals confirmed.

### Phase 2: Discover

**Goal:** Map current analytics state.

1. Search for analytics SDK imports and initialization
2. Search for existing event tracking calls
3. Search for existing dashboard/reporting configuration
4. Build inventory: tracked events, tools in use, consent mechanism

**Gate:** Current state mapped.

### Phase 3: Design [--design]

**Goal:** Create event taxonomy and tracking plan.

1. **Core events:** Generate essential events for the app type:
   - All apps: app_open, signup_complete, error_occurred
   - SaaS: feature_used, subscription_started, subscription_cancelled
   - E-commerce: product_viewed, cart_updated, purchase_completed
   - Content: content_viewed, content_shared, content_saved
2. **Naming convention:** `{object}_{action}` in snake_case
   - Example: `transcript_created`, `subscription_started`, `settings_changed`
3. **Event properties:** For each event, define:
   - Required properties (always present)
   - Optional properties (context-dependent)
   - Forbidden properties (PII: email, name, IP, device ID)
4. **Funnels:** Define 3-5 key funnels with conversion targets
5. **Dashboards:** Recommend 1-2 dashboards with specific metrics

**Gate:** Taxonomy covers all key user journeys with zero PII in properties.

### Phase 4: Setup [--setup]

**Goal:** Integration guide for chosen tool.

1. Recommend analytics tool based on project needs and privacy requirements
2. Generate integration pattern:
   - SDK initialization with consent check
   - Event helper module (centralized tracking, type-safe events)
   - Consent management integration
   - PII scrubbing middleware
3. Generate testing approach:
   - Debug mode for event verification
   - Event validation in CI

**Gate:** Integration guide is complete and privacy-compliant.

### Phase 5: Audit [--audit]

**Goal:** Review existing analytics.

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, read findings matching scopes (privacy, coverage, noise, quality). For each match: verify still valid (re-read file:line), skip own analysis for verified scopes. For uncovered scopes, run full analysis.
2. **Coverage check:** Map tracked events to user journeys — identify gaps
3. **Privacy check:**
   - PII in event properties? (emails, names, IPs, precise location)
   - Consent mechanism present?
   - Data retention configured?
   - Third-party sharing documented?
4. **Noise check:**
   - Events tracked but never used in dashboards?
   - Duplicate events?
   - Events with >10 properties (too complex)?
5. **Quality check:**
   - Naming consistency?
   - Missing required properties?
   - Events without clear business purpose?

**Gate:** Findings collected.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 7: Summary

```
ds-analytics: {OK|WARN|FAIL} | Mode: {design|setup|audit} | Events: N defined | Gaps: N | Privacy: {OK|WARN} | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Design output:** Event taxonomy table + funnel definitions + dashboard spec.

**Setup output:** Integration guide with code patterns.

**Audit output:** Coverage map, privacy findings, noise findings.

FRC+DSC accounting.

**Gate:** Summary printed with all metrics and recommendations.

## Quality Gates

- Zero PII in event properties (no emails, names, IPs, device IDs)
- Consent mechanism required before any tracking
- Every tracked event has a documented business purpose
- Event naming follows consistent convention
- Funnels have defined conversion targets
- Every finding gets a disposition in the summary — zero silent drops (FRC)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No analytics SDK found | Start from design mode, recommend tool |
| Multiple analytics tools | Ask which is primary, audit all for overlap |
| No consent mechanism | Flag as HIGH, generate consent integration guide |
| Unclear business goals | Ask: what 3 decisions will data inform? |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | PII in events without consent, tracking without opt-in mechanism |
| HIGH | No consent mechanism, excessive data collection, no retention policy |
| MEDIUM | Naming inconsistency, tracking gaps, unused events |
| LOW | Missing documentation, suboptimal tool choice |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Zero analytics currently | Start from design, recommend minimal viable analytics |
| Privacy-only audit | Focus solely on privacy scope, skip coverage/noise |
| Server-side only (API) | Focus on request logging, error rates, not client events |
| Regulated industry | Flag additional compliance requirements (HIPAA, PCI) |
| iOS with ATT | Include App Tracking Transparency flow, SKAdNetwork 4.0/AdAttributionKit conversion values, PrivacyInfo.xcprivacy manifest validation |
