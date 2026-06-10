# /ds-analytics

Most apps track everything (privacy violation) or nothing (flying blind). Skill designs minimum event taxonomy for maximum insight — privacy-first.

**Analytics & Metrics** — Privacy-first analytics setup, event taxonomy, funnel design, and user insights.

## Triggers

- User runs `/ds-analytics`
- User asks about analytics, metrics, event tracking, or user insights
- User asks "what should I track" or "set up analytics"
- User asks about retention, churn, funnels, or A/B testing

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "design event taxonomy", "set up analytics" | "audit code quality" (→ ds-review) |
| "privacy audit of events" (event-PII scan) | "full GDPR/KVKK privacy compliance" (→ ds-compliance --privacy) |
| "what should I track in v1" | "what features should I build" (→ ds-market) |
| "design conversion funnel" | "improve conversion rate" (→ ds-tune) |

## Contract

- Privacy-first: maximum insights with minimum data collection. Recommends privacy-respecting tools, no invasive tracking. Prefer self-hosted or minimal analytics over heavyweight SDKs. Focus on actionable metrics, not vanity metrics.
- Generates event taxonomies, tracking plans, and dashboard specs — not tracking code.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--design` | Event taxonomy design: naming, hierarchy, properties |
| `--setup` | Analytics integration guide for project's stack |
| `--audit` | Audit existing analytics for gaps, noise, coverage |
| `--privacy-audit` | **Narrow scope (OVERLAP-4):** event-property PII scan only. Canonical privacy audit (consent, retention, regulatory framing) delegated to `/ds-compliance --privacy`. |
| `--auto` | All modes, no questions, single-line summary |
| `--resume` | Resume from `ds/audit/analytics.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present interactive mode selection.

### Privacy-audit scope (runtime enforcement — OVERLAP-4)

When `--privacy-audit` is active (or privacy concerns surface in `--audit` mode):

1. **Announce scope narrowing:** "Privacy canonical owner is /ds-compliance. This run limits to event-property PII scan."
2. **Scan only:** every event declaration (`track(...)`, `logEvent(...)`, `analytics.track(...)`, stack-native equivalents) — inspect properties payload for PII patterns (email, phone, full name, national ID, address, IP when not anonymized, precise geolocation, biometric, health, financial data).
3. **Do not emit findings on:** consent mechanisms, retention policies, regulatory framework mapping, data-subject-request endpoints — those belong to `/ds-compliance`.
4. **Write findings with scope `event-pii-scan` only** (not `privacy`). This distinguishes event-level scans from canonical privacy findings.

## Scopes

### Event Taxonomy

| Area | What It Covers |
|------|---------------|
| Naming | `{object}_{action}` in snake_case, past tense (e.g., `{noun}_{past-verb}`) |
| Hierarchy | Area > Object > Action (e.g., `{area} > {object} > {action}`) |
| Properties | Required vs optional per event, snake_case, units in name (`duration_seconds`), no PII |
| Standards | Taxonomy versioning, deprecation with `_legacy` suffix, CI lint for convention |
| Template | Starter taxonomy covering auth, onboarding, core feature, subscription, referral, errors |

### Funnel

| Funnel | What It Covers |
|--------|---------------|
| Acquisition | Install → First open → Signup → Activation |
| Activation | Signup → Core action → Value moment ("aha") |
| Retention | Day 1 / Day 7 / Day 30 return rates |
| Revenue | Free → Trial → Paid → Renewal / Upgrade |
| Referral | Share action → Invite sent → Invite accepted |

### Metrics

| Category | Metrics |
|----------|---------|
| Engagement | DAU, MAU, DAU/MAU ratio, session length, screens/session |
| Retention | Day 1/7/30 retention (targets: >40%, >20%, >10%), cohort curves, churn rate |
| Churn signals | Leading indicators (login-frequency drop, feature disuse), intervention triggers |
| Revenue | MRR, ARR, ARPU, LTV (ARPU × gross-margin / churn), NRR, Rule of 40 |
| Quality | Crash-free rate, ANR rate, error rate, app rating |
| Growth | Install rate, organic vs paid, viral coefficient (K-factor) |

### Privacy

| Check | What It Covers |
|-------|---------------|
| Data minimization | Only track what you'll act on |
| Consent | Proper opt-in/opt-out for tracking |
| PII | No PII in event properties (no emails, names, IPs) |
| Tools | Privacy-respecting tool recommendations |
| Compliance | GDPR consent, ATT (iOS), CCPA opt-out |

Tool recommendation by privacy posture → [references/tool-comparison.md](references/tool-comparison.md). Event taxonomy + privacy audit rules → [references/rules-analytics.md](references/rules-analytics.md).

## Delegation

**Owns:** analytics, event-taxonomy, funnels, metrics, event-pii-scan (narrow privacy-audit only) | **Delegates:** ds-compliance → canonical privacy / regulatory | **Receives:** ds-ship → Phase 2 `--privacy-audit` invocation only

## Execution Flow

Setup → Discover → Design/Audit → Generate → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/analytics.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read analytics inventory, discard stale detections), skip `done` phases, announce `[ANL] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data` shape:** `{ mode, platform, goals[], inventory: {sdks[], events[]}, scopes_done[], taxonomy_generated, privacy_findings[{id, severity, disposition}] }`.

1. Flags provided → proceed directly. No flags → interactive menu.
2. **IDU:** Profile → Config.data, Config.audience, Config.regulations, Type+Stack. Findings(privacy, coverage, noise, quality) → verify + use. Absent → own analysis.
3. Detect platform (web, mobile, API) from project signals.
4. Detect existing analytics (search analytics SDKs in dependencies).
5. Ask: Which decisions will analytics inform? Options: feature prioritization, monetization, quality improvement, user retention.

**Gate:** Platform + goals confirmed. If fails → re-prompt missing item; 2 prompts no response → default platform `web` + goal `feature prioritization` with WARN note in state.data.goals.

### Phase 2: Discover

1. Search for analytics SDK imports + initialization.
2. Search for existing event tracking calls.
3. Search for existing dashboard/reporting configuration.
4. Build inventory: tracked events, tools in use, consent mechanism.

**Gate:** Current state mapped. If fails → no SDK + no tracking calls → set inventory empty, add WARN "No analytics instrumentation detected", proceed to Phase 3 (Design) regardless of flags.

### Phase 3: Design [--design]

1. **Core events** for app type:
   - All apps: `app_open`, `signup_complete`, `error_occurred`
   - SaaS: `feature_used`, `subscription_started`, `subscription_cancelled`
   - E-commerce: `product_viewed`, `cart_updated`, `purchase_completed`
   - Content: `content_viewed`, `content_shared`, `content_saved`
2. **Naming convention:** `{object}_{action}` snake_case past tense (placeholder format, replace with project's actual events).
3. **Event properties** per event: Required (always present) / Optional (context-dependent) / Forbidden (PII: email, name, IP, device ID).
4. **Funnels:** define 3-5 key funnels with conversion targets.
5. **Dashboards:** recommend 1-2 dashboards with specific metrics.

**Gate:** Taxonomy covers all key user journeys; zero PII in properties. If fails → replace each PII property with privacy-safe alternative (e.g., hashed ID); for each uncovered journey, add placeholder event marked `[INCOMPLETE]` so consumers know coverage is partial.

### Phase 4: Setup [--setup]

1. Recommend analytics tool based on project needs + privacy requirements.
2. Generate integration pattern:
   - SDK initialization with consent check
   - Event helper module (centralized tracking, type-safe events)
   - Consent management integration
   - PII scrubbing middleware
3. Generate testing approach: debug mode for event verification + event validation in CI.

**Gate:** Integration guide complete + privacy-compliant. If fails → identify non-compliant element (missing consent check, PII-capable SDK recommended); substitute compliant alternative or add mandatory TODO marked `[PRIVACY-REQUIRED]` at the exact insertion point; flag guide `partial`, note gap in summary.

### Phase 5: Audit [--audit]

1. **Findings file check:** `ds/audit/findings.md` fresh `git_hash` → read findings matching scopes (privacy, coverage, noise, quality). Per match: verify still valid (re-read `{file}:{line}`); uncovered scopes → run full analysis.
2. **Coverage:** map tracked events → user journeys, identify gaps.
3. **Privacy:** PII in event properties? Consent present? Retention configured? Third-party sharing documented?
4. **Noise:** events tracked-but-unused-in-dashboards? Duplicates? Events with >10 properties (too complex)?
5. **Quality:** naming consistency? Missing required properties? Events without clear business purpose?

**Gate:** Findings collected. If fails → unanalyzable scope (no events file, no consent mechanism to inspect) → mark as `inconclusive` in state.data.scopes_done, continue with the rest, flag each inconclusive scope in output for manual review.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → forced binary re-prompt; no response → mark `skipped (no response)` and proceed.

### Phase 7: Summary

```
ds-analytics: {OK|WARN|FAIL} | Mode: {design|setup|audit} | Events: {n} defined | Gaps: {n} | Privacy: {OK|WARN} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Per-mode output:
- **Design:** event taxonomy table + funnel definitions + dashboard spec.
- **Setup:** integration guide with code patterns.
- **Audit:** coverage map + privacy findings + noise findings.

FRC+DSC accounting.

**Value Delivered:** 1-5 concrete bullets, real changes only. Example shapes (placeholders, not literal):

- `{n} PII fields removed from event properties — user data no longer leaks into analytics pipeline / vendor systems`
- `Event taxonomy of {n} events covers {m} core funnels — product decisions now have measurable inputs instead of intuition`
- `Consent gate wired before SDK init — no event fires before user opts in (GDPR/ATT compliant)`
- `{n} unused events deprecated with `_legacy` suffix — telemetry volume reduced, dashboard noise gone`

**Gate:** Summary + Value Delivered emitted. If fails → uncomputable metric (Events/Gaps/Privacy) → substitute `N/A`, print partial summary with WARN, list incomplete phases.

## Quality Gates

- Zero PII in event properties (no emails, names, IPs, device IDs)
- Consent mechanism required before any tracking
- Every tracked event has a documented business purpose
- **Least privilege for analytics SDK credentials ([references/principles.md §5](references/principles.md)):** write keys / API tokens scoped to write-only project IDs; read tokens never embedded in client code. Validate every event property at the tracking boundary — reject PII patterns before send.
- Event naming follows consistent convention
- Funnels have defined conversion targets
- Every finding gets a disposition (FRC)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/analytics.json` updated per scope + per deliverable, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | PII in events without consent, tracking without opt-in mechanism |
| HIGH | No consent mechanism, excessive data collection, no retention policy |
| MEDIUM | Naming inconsistency, tracking gaps, unused events |
| LOW | Missing documentation, suboptimal tool choice |

## Error Recovery

| Situation | Action |
|-----------|--------|
| No analytics SDK found | Start from design mode, recommend tool |
| Multiple analytics tools | Ask which is primary, audit all for overlap |
| No consent mechanism | Flag HIGH, generate consent integration guide |
| Unclear business goals | Ask: what 3 decisions will data inform? |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Zero analytics currently | Start from design, recommend minimal viable analytics |
| Privacy-only audit | Focus solely on privacy scope, skip coverage/noise |
| Server-side only (API) | Focus on request logging, error rates, not client events |
| Regulated industry | Flag additional compliance requirements (HIPAA, PCI) |
| iOS with ATT | Include ATT flow, SKAdNetwork 4.0 / AdAttributionKit conversion values, PrivacyInfo.xcprivacy manifest validation |
