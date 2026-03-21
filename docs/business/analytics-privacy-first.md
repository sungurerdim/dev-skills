# Privacy-First Analytics Guide

A practical, privacy-respecting analytics reference for solo developers building production apps in 2026.

---

## Table of Contents

1. [Privacy-First Philosophy](#1-privacy-first-philosophy)
2. [Analytics Tool Comparison](#2-analytics-tool-comparison)
3. [Event Taxonomy Design](#3-event-taxonomy-design)
4. [AARRR Funnel Definition](#4-aarrr-funnel-definition)
5. [Retention Metrics](#5-retention-metrics)
6. [Churn Indicators](#6-churn-indicators)
7. [A/B Testing](#7-ab-testing)
8. [Cohort Analysis](#8-cohort-analysis)
9. [Revenue Metrics](#9-revenue-metrics)
10. [Crash-Free Rate Monitoring](#10-crash-free-rate-monitoring)
11. [Feature Adoption Tracking](#11-feature-adoption-tracking)
12. [Privacy-Compliant Implementation](#12-privacy-compliant-implementation)
13. [Dashboard Design](#13-dashboard-design)
14. [Mobile Specifics](#14-mobile-specifics)
15. [Starter Event Taxonomy Template](#15-starter-event-taxonomy-template)
16. [Sources](#16-sources)

---

## 1. Privacy-First Philosophy

### The Minimum-Data Principle

Collect only what you need, keep it only as long as you need it, and never collect what you cannot justify. This is not idealism — it is a legal requirement under GDPR Article 5(1)(c) and a competitive advantage in 2026.

### Why It Matters Now

- **EU DPA enforcement against GA4**: Austria, France, Italy, and Denmark DPAs ruled GA4 US transfers violate GDPR Chapter V. GA4 without EU-only hosting is a compliance liability.
- **User expectations shifted**: ATT opt-in ~35% globally (2025). Users refuse tracking when given a choice.
- **Regulatory momentum**: EU AI Act, ePrivacy Regulation, and US state privacy laws (CO, CT, TX, OR) all trend toward stricter consent.

### Core Principles

1. **No PII in analytics events** — hash or drop identifiers at the edge.
2. **Cookieless by default** — session-based or anonymous identification.
3. **EU-hosted infrastructure** — eliminate Schrems II risk.
4. **Purpose limitation** — every event answers a specific product question.
5. **Data minimization** — minimum properties needed for analysis.

---

## 2. Analytics Tool Comparison

### Decision Matrix

| Factor | GA4 | Plausible | PostHog | Matomo |
|---|---|---|---|---|
| **Cookies required** | Yes (default) | No | No (cookieless mode) | Configurable |
| **GDPR compliant (out-of-box)** | No (US transfer) | Yes | Yes (EU Cloud) | Yes (self-hosted) |
| **Consent banner needed** | Yes | No | No (cookieless mode) | No (cookieless mode) |
| **Free tier** | Unlimited (with data sharing) | No ($9/mo; self-host free) | 1M events/month | Self-host free |
| **Product analytics** | Basic | No | Full (funnels, paths, retention) | Basic |
| **Session replay** | No | No | Yes | Yes (plugin) |
| **A/B testing** | Limited | No | Yes (built-in) | No |
| **Feature flags** | No | No | Yes | No |
| **Surveys** | No | No | Yes | No |
| **EU hosting** | Partial (GA4 EU) | Yes | Yes (Frankfurt) | Self-host |
| **Self-hostable** | No | Yes (Community) | Yes (open source) | Yes |
| **Script size** | ~80 KB | <1 KB | ~70 KB | ~22 KB |
| **Learning curve** | High | Low | Medium | Medium |
| **Best for** | Enterprises with legal teams | Marketing sites, blogs | SaaS, product teams | Privacy-strict orgs |

**Solo-dev pick**: PostHog (free 1M events/month) for product analytics + feature flags. Add Plausible ($9/mo) for marketing traffic. Avoid GA4 unless you have a DPA-compliant EU setup.

---

## 3. Event Taxonomy Design

### Object-Action Naming Convention

Use `Object Action` in **Title Case**. Object (noun) first, action (past-tense verb) second. Groups related events alphabetically and reads naturally.

- Good: `Account Created`, `Subscription Started`
- Bad: `created_account`, `userDeletedAccount`, `start-subscription`

### Three-Level Hierarchy

| Category | Object | Action | Event Name |
|---|---|---|---|
| auth | account | created | Account Created |
| auth | session | started | Session Started |
| onboarding | tutorial | completed | Tutorial Completed |
| core | document | exported | Document Exported |
| billing | subscription | upgraded | Subscription Upgraded |

Keep to 5-8 categories maximum. Use them to organize dashboards and set permissions.

### Property Rules

| Rule | Example |
|---|---|
| `snake_case` for properties | `plan_type`, `error_code` |
| Prefix when ambiguous | `subscription_plan_type` |
| No PII in properties | `user_tier` not `user_email` |
| Enum values over free text | `plan_type: "pro"` not `"Professional Plan"` |
| Include `source` for cross-platform | `source: "ios"` / `"web"` |
| ISO 8601 timestamps | `created_at: "2026-03-20T..."` |

### Governance

1. **Taxonomy doc** — version-controlled, single source of truth.
2. **Validation** — reject events not matching schema at instrumentation time.
3. **Review** — new events require justification: "This answers: [product question]."
4. **Quarterly audit** — remove events with zero queries in 90 days.

---

## 4. AARRR Funnel Definition

| Stage | Key Events | Benchmark (Mobile SaaS) |
|---|---|---|
| **Acquisition** | `App Installed`, `Landing Page Viewed`, `Signup Started` | Install-to-signup: 20-30% |
| **Activation** | `Onboarding Completed`, `Core Feature Used`, `Aha Moment Reached` | Signup-to-activated: 30-50% |
| **Retention** | `Session Started` (D1/D7/D30), `Feature Reused` | D1: 25-40%, D7: 15-25%, D30: 8-15% |
| **Revenue** | `Subscription Started`, `Purchase Completed`, `Trial Converted` | Trial-to-paid: 10-25% |
| **Referral** | `Invite Sent`, `Referral Link Shared`, `Referral Converted` | Users who refer: 5-15% |

**Defining your aha moment**: Pick 3-5 candidate actions, compute D30 retention for did vs. did-not cohorts. Highest retention delta = your aha moment.

---

## 5. Retention Metrics

| Metric | Formula | Good (SaaS) | Good (Consumer) |
|---|---|---|---|
| **D1 retention** | Users active Day 1 / Users from Day 0 | 40-60% | 25-40% |
| **D7 retention** | Users active Day 7 / Users from Day 0 | 25-40% | 15-25% |
| **D30 retention** | Users active Day 30 / Users from Day 0 | 15-30% | 8-15% |
| **DAU/MAU (stickiness)** | Daily Active Users / Monthly Active Users | 20-30% | 15-25% |

### Cohort Retention Table

| Cohort | Wk 0 | Wk 1 | Wk 2 | Wk 3 | Wk 4 | Shape |
|---|---|---|---|---|---|---|
| A | 100% | 42% | 28% | 24% | 23% | Flattening (healthy) |
| B | 100% | 38% | 20% | 12% | 7% | Declining (problem) |
| C | 100% | 45% | 35% | 33% | 34% | Smile curve (excellent) |

### Curve Interpretation

- **Flattening** — users who survive Week 2 tend to stay. Focus on the drop-off cliff.
- **Declining** — product not delivering ongoing value. Investigate core loop.
- **Smile curve** — users return after initial drop. Ideal shape, often after re-engagement.

---

## 6. Churn Indicators

### Leading vs. Lagging Signals

| Signal | Type | Window |
|---|---|---|
| Session frequency drop >50% vs. prior 2 weeks | Leading | 7-14 days |
| Core feature usage drop | Leading | 7-14 days |
| Support ticket without resolution | Leading | 3-7 days |
| Billing page visited, no upgrade | Leading | 1-3 days |
| Subscription cancelled | Lagging | Event itself |
| No session in 30+ days | Lagging | Passive churn |

### 2026 Benchmarks by Segment

| Segment | Monthly | Annual |
|---|---|---|
| Enterprise SaaS (>$50K ACV) | 0.5-1.0% | 5-10% |
| Mid-market ($5K-$50K ACV) | 1.0-2.0% | 10-20% |
| SMB (<$5K ACV) | 3.0-5.0% | 30-45% |
| Consumer subscription | 5.0-8.0% | 45-65% |
| Freemium (paid tier) | 4.0-7.0% | 40-60% |

### Intervention Triggers

| Trigger | Action |
|---|---|
| Session frequency -50% for 7d | Re-engagement nudge (in-app/email) |
| Core feature unused 14d | Onboarding reminder for unused features |
| Trial day 5, no activation | Targeted activation email |
| Billing page, no conversion | Limited discount or feature highlight |

---

## 7. A/B Testing

### Hypothesis Template

```
We believe [change] for [segment] will cause [outcome] because [rationale].
Measure: [primary metric]. Guard: [guardrail metrics].
Need: [sample size] over [duration] to detect [MDE] at 95% confidence.
```

### Sample Size Calculation

**Formula**: `n = (Z_alpha/2 + Z_beta)^2 * 2 * p * (1 - p) / MDE^2`

**Example** — detecting 2% absolute lift (10% to 12% conversion):

| Parameter | Value |
|---|---|
| Baseline (p) | 10% |
| MDE | 2% absolute |
| Alpha / Power | 5% (Z=1.96) / 80% (Z=0.84) |
| **Per variant / Total** | **~3,600 / ~7,200 users** |

**Key parameters**: Significance p<0.05 (never peek). Power 80%+ (90% for high-stakes). Runtime: 2-4 weeks minimum, covering full business cycles.

### When NOT to Test

- Traffic <1,000/week per variant. Bug fixes or legal requirements. No measurable metric. Irreversible changes.

**Tools**: PostHog (built-in, free), GrowthBook (open source), Statsig (free tier), LaunchDarkly (enterprise).

---

## 8. Cohort Analysis

### Cohort Types

| Type | Grouped By | Use Case |
|---|---|---|
| Acquisition | Signup date | Retention trends over time |
| Behavioral | Action taken | Feature adoption impact |
| Channel | Acquisition source | Channel quality comparison |
| Plan | Pricing tier | Revenue retention by segment |

### Behavioral Cohorts for Product Decisions

Compare users who did vs. did not perform a specific action:

1. **Completed onboarding** vs. skipped — measure D30 retention delta.
2. **Used Feature X in Week 1** vs. did not — measure conversion to paid.
3. **Invited a teammate** vs. solo — measure LTV difference.
4. **Organic search** vs. paid ads — measure activation rate delta.

If the delta is significant (>10% retention or >20% LTV), that action becomes a product priority.

---

## 9. Revenue Metrics

### Formulas

| Metric | Formula |
|---|---|
| **MRR** | Sum of active monthly subscriptions |
| **ARPU** | Total revenue / Active users |
| **ARPPU** | Total revenue / Paying users |
| **LTV** | ARPU x (1 / Monthly churn rate) |
| **LTV:CAC** | LTV / Customer Acquisition Cost |
| **NRR** | (Start MRR + Expansion - Contraction - Churn) / Start MRR |
| **GRR** | (Start MRR - Contraction - Churn) / Start MRR |
| **Rule of 40** | Revenue growth % + Profit margin % >= 40 |

### 2026 Benchmarks by Stage

| Metric | Pre-Seed | Seed | Series A+ |
|---|---|---|---|
| MRR | $0-5K | $10-50K | $100K+ |
| LTV:CAC | >1.5 | >3.0 | >4.0 |
| NRR | >90% | >100% | >110% |
| GRR | >80% | >85% | >90% |
| Payback | <12mo | <12mo | <18mo |

**Rule of 40**: >40 = investor-grade, 20-40 = acceptable early-stage, <20 = growth stalled or burn unsustainable.

---

## 10. Crash-Free Rate Monitoring

### Sentry Setup with PII Scrubbing

```javascript
Sentry.init({
  dsn: "https://your-key@sentry.io/project-id",
  tracesSampleRate: 0.2,
  beforeSend(event) {
    if (event.user) {
      delete event.user.email;
      delete event.user.ip_address;
      event.user.id = hashUserId(event.user.id); // one-way hash
    }
    if (event.request) {
      delete event.request.cookies;
      delete event.request.headers?.["Authorization"];
    }
    if (event.breadcrumbs) {
      event.breadcrumbs = event.breadcrumbs.map(b => {
        if (b.data?.url) b.data.url = stripQueryParams(b.data.url);
        return b;
      });
    }
    return event;
  },
  beforeBreadcrumb(breadcrumb) {
    if (breadcrumb.category === "ui.input") return null; // no PII from inputs
    return breadcrumb;
  },
});
```

### Error Budgets

| Metric | Target | Alert |
|---|---|---|
| Crash-free sessions | >99.5% | <99.0% |
| Crash-free users | >99.8% | <99.5% |
| ANR rate (Android) | <0.5% | >1.0% |
| P95 API latency | <500ms | >1,000ms |
| Error rate (non-crash) | <1.0% | >2.0% |

### Alert Thresholds

- **P0 (page now)**: Crash-free <98%. All users affected.
- **P1 (4 hours)**: Crash-free 98-99%. Specific flows affected.
- **P2 (24 hours)**: Crash-free 99-99.5%. Edge cases.
- **P3 (next sprint)**: Error rate above baseline, crash-free >99.5%.

---

## 11. Feature Adoption Tracking

### Adoption Funnel

| Stage | Definition | Benchmark |
|---|---|---|
| **Exposed** | Had access (flag on) | 100% |
| **Activated** | Tried once | 40% |
| **Used** | Completed core action | 25% |
| **Retained** | Returned in Week 2+ | 15% |
| **Power User** | 3+ times/week | 5% |

### Feature Flags and Rollout Strategy

1. **Internal** (0.1%) — dogfooding. 2. **Beta** (5-10%) — early adopters + feedback. 3. **Gradual** (25% -> 50% -> 100%) — monitor crash rate and adoption. 4. **GA** (100%) — remove flag.

At each stage monitor: crash-free rate, adoption rate, support tickets, core metric impact.

### Adoption Benchmarks

| Timeline | Target | Action if Below |
|---|---|---|
| Week 1 | >20% activation | Improve discoverability |
| Week 4 | >10% retained | Investigate value prop |
| Week 8 | >5% power users | Validated, invest in polish |
| Week 8 | <5% activation | Consider sunsetting |

---

## 12. Privacy-Compliant Implementation

### Consent Strategy by Tool

| Tool | Consent? | Strategy |
|---|---|---|
| Plausible | No | Deploy without banner |
| PostHog (cookieless) | No | `persistence: "memory"`, no cookies |
| PostHog (full) | Yes | Gated behind consent; enables replay + identity |
| Matomo (cookieless) | No | Enable cookieless in settings |
| GA4 | Yes | Full opt-in; Google Consent Mode v2 |
| Sentry | No | Legitimate interest; strip PII in `beforeSend` |

### Anonymization Checklist

- [ ] User IDs hashed (one-way, salted) before reaching analytics.
- [ ] IP addresses not stored (or truncated to /24 for geo).
- [ ] No email, name, or phone in event properties.
- [ ] Free-text fields excluded or sanitized.
- [ ] URLs stripped of query params containing tokens or PII.
- [ ] Session replay masks all input fields by default.
- [ ] Error reports scrub headers, cookies, and auth tokens.

### Data Retention Policy

| Data Type | Retention |
|---|---|
| Raw analytics events | 12 months |
| Aggregated metrics | 36 months |
| Session recordings | 30 days |
| Error/crash data | 90 days |
| Consent records | Account duration + 3 years |

### GDPR Requirements Checklist

- [ ] Privacy policy lists all analytics tools, purpose, and legal basis.
- [ ] DPAs signed with all third-party processors.
- [ ] Right to erasure — user deletion removes analytics linkage.
- [ ] Right to export — includes analytics profile if identifiable.
- [ ] Consent records stored with timestamp, scope, and version.
- [ ] Transfer Impact Assessment completed for non-EU data flows.

---

## 13. Dashboard Design

### 8 Weekly Metrics (Solo-Dev Dashboard)

| # | Metric | Source | Target | Alert |
|---|---|---|---|---|
| 1 | Weekly Active Users (WAU) | PostHog | Trending up | >20% WoW drop |
| 2 | Activation rate | PostHog funnel | >30% | <20% |
| 3 | D7 retention | PostHog retention | >20% | <12% |
| 4 | Trial-to-paid conversion | PostHog + billing | >10% | <5% |
| 5 | MRR | Billing system | Growth >5% MoM | Decline |
| 6 | Crash-free rate | Sentry | >99.5% | <99.0% |
| 7 | P95 API latency | Sentry/APM | <500ms | >1,000ms |
| 8 | NPS / satisfaction | PostHog surveys | >40 | <20 |

### Alert Rules

**Immediate**: Crash-free <99%, API errors >5%, MRR -10%. **Daily**: Activation/retention/conversion >10% WoW change. **Weekly**: All 8 metrics with trends, Monday morning.

### Dashboard Principles

1. **One screen** — if it scrolls, too many metrics.
2. **Comparison** — always show WoW or MoM delta, not just absolutes.
3. **Actionable** — every metric links to a drill-down or playbook.
4. **No vanity metrics** — total signups and page views alone tell you nothing.

---

## 14. Mobile Specifics

### ATT Opt-In Rates (2025-2026)

Global blended ATT opt-in: **~35%** (Adjust, Q2 2025). Sports ~50%, hyper-casual ~43%, action games ~40%, board games ~30%, utility ~20-25%, education ~14%.

**Higher opt-in**: Pre-permission screen explaining value, delay prompt until user experiences value, A/B test copy and timing.

### SKAdNetwork 4.0 and AdAttributionKit

- **SKAN 4.0** (iOS 16.1+): Three conversion windows (0-2d, 3-7d, 8-35d) with coarse values (low/medium/high) plus fine-grained for high-threshold campaigns.
- **AdAttributionKit** (iOS 17.4+): Apple's successor to SKAN. Adds re-engagement attribution and developer postbacks.
- **Strategy**: AdAttributionKit for new projects, SKAN 4.0 fallback for iOS 16. Map conversion values to AARRR funnel stages.

### Privacy Manifests (Required Since May 2024)

Apple requires `PrivacyInfo.xcprivacy` in all apps and SDKs. Declare: required reason APIs, collected data types and purposes, tracking domains. Third-party SDKs must include their own manifest. App Store Connect rejects incomplete manifests.

---

## 15. Starter Event Taxonomy Template

Copy-paste ready. Uses `Object Action` (Title Case) convention with `snake_case` properties.

```
=== AUTH ===
Account Created           { method: "email"|"google"|"apple", source: "ios"|"android"|"web" }
Account Deleted           { reason: "user_request"|"inactivity", days_since_creation: number }
Session Started           { source: "ios"|"android"|"web", session_number: number }
Session Ended             { duration_seconds: number, screens_viewed: number }

=== ONBOARDING ===
Onboarding Started        { source: string, variant: string }
Onboarding Step Completed { step_number: number, step_name: string, duration_seconds: number }
Onboarding Completed      { duration_seconds: number, steps_completed: number, steps_skipped: number }
Onboarding Skipped        { step_number: number, step_name: string }

=== CORE FEATURE ===
[Feature] Viewed          { source: string, entry_point: string }
[Feature] Completed       { duration_seconds: number, result: "success"|"failure" }
[Feature] Shared          { method: "link"|"email"|"social", recipient_count: number }
Search Performed          { query_length: number, results_count: number, category: string }

=== SUBSCRIPTION ===
Paywall Viewed            { source: string, variant: string, trigger: string }
Trial Started             { plan_type: "monthly"|"annual", source: string }
Trial Converted           { plan_type: string, trial_duration_days: number }
Subscription Started      { plan_type: string, price_cents: number, currency: string }
Subscription Cancelled    { plan_type: string, reason: string, days_active: number }
Subscription Upgraded     { from_plan: string, to_plan: string }

=== REFERRAL ===
Invite Sent               { method: "link"|"email"|"sms"|"social", source: string }
Referral Converted        { referrer_plan: string, referee_plan: string }

=== ERROR ===
Error Occurred            { error_code: string, error_domain: string, screen: string, is_fatal: bool }
App Crash Detected        { screen: string, os_version: string, app_version: string }
Network Error Occurred    { endpoint: string, status_code: number, retry_count: number }
```

Replace `[Feature]` with your actual feature name (e.g., `Document Exported`, `Workout Completed`).

## 16. Sources

- [PostHog vs Plausible](https://posthog.com/blog/posthog-vs-plausible) | [Privacy-First Analytics 2026 (LegalForge)](https://www.legal-forge.com/en/blog/privacy-first-analytics-alternatives-2026/)
- [Privacy-First Analytics 2026 (Vemetric)](https://vemetric.com/blog/privacy-first-analytics) | [GDPR-Compliant Tools (PostHog)](https://posthog.com/blog/best-gdpr-compliant-analytics-tools)
- [ATT Opt-In 2025 (Adjust)](https://www.adjust.com/blog/att-opt-in-rates-2025/) | [ATT Opt-In 2025 (Purchasely)](https://www.purchasely.com/blog/att-opt-in-rates-in-2025-and-how-to-increase-them)
- [ATT Opt-In 2026 (Business of Apps)](https://www.businessofapps.com/data/att-opt-in-rates/)
- [Event Taxonomy (Amplitude)](https://amplitude.com/explore/data/event-taxonomy) | [Naming Conventions (Segment)](https://segment.com/academy/collecting-data/naming-conventions-for-clean-data/)
- [Naming Conventions (Heap)](https://www.heap.io/blog/naming-conventions-and-their-place-in-analytics) | [Taxonomy Design (Optizent)](https://www.optizent.com/blog/a-practical-guide-to-designing-your-amplitude-event-taxonomy/)
- [Apple Privacy Manifests](https://developer.apple.com/documentation/bundleresources/privacy_manifest_files) | [SKAdNetwork 4.0](https://developer.apple.com/documentation/storekit/skadnetwork)
- [AdAttributionKit](https://developer.apple.com/documentation/AdAttributionKit) | [Sentry PII Scrubbing](https://docs.sentry.io/platforms/javascript/data-management/sensitive-data/)
