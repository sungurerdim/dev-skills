---
name: ds-launch
description: Store and release management — store submission, listing optimization, release strategy, post-launch monitoring. Use when preparing an app-store release or planning a launch.
---

# /ds-launch

~40% of iOS submissions get delayed or rejected for preventable errors. This skill scans your project and flags them before you submit.

**Store & Release Management** — Store submission, listing optimization, release strategy, and post-launch monitoring.

## Triggers

- User runs `/ds-launch`, asks to submit to app store, prepare for launch, or manage releases — or about store listing, screenshots, privacy labels, release notes, "how do I publish my app"

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "submit to App Store / Play Store / Mac App Store" | "deploy backend to VPS / container" (→ ds-deploy) |
| "App Store privacy labels (store-correctness check)" | "full GDPR/KVKK privacy compliance" (→ ds-compliance --privacy) |
| "author a perf budget (LCP/INP/p99/bundle) + wire CI enforcement" | "fix the performance regression itself" (→ ds-review / ds-fix) |
| "pre-review checklist (rejection prevention)" | "audit mobile app quality" (→ ds-mobile) |

## Contract

**Dimensions:** A4, D1 (perf-budget), D6, A9 (conditional ecosystem rules)

- Covers store account setup, listing metadata, review preparation, release management; generates checklists + metadata — does NOT submit to stores directly.
- Minimal liability + maximum privacy + maximum automation: store-compliant metadata + common rejection flags; privacy labels with minimal data-collection focus; version management + release notes generation + staged rollout.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--setup` | Store account setup checklists + initial configuration |
| `--listing` | Store listing metadata: description, keywords, screenshots |
| `--privacy` | Privacy label declarations — **store-label-correctness only**. Canonical privacy audit delegated to `/ds-compliance --privacy` (OVERLAP-4). Verifies store labels match actual code behavior; does not re-audit data collection or consent. |
| `--review` | Pre-review checklist: common rejection prevention |
| `--submission-notes` | **Proactive submission notes generator** — fills App Review Information Notes upfront so reviewer doesn't need to ask follow-ups (saves +24-48h per round-trip). See [references/app-store-submission-template.md](references/app-store-submission-template.md) |
| `--aso` | App Store Optimization — keyword research + search ranking |
| `--release` | Release management: version, notes, staged rollout |
| `--post-launch` | Post-launch monitoring checklist |
| `--perf-budget` | Author a formal perf budget (LCP, INP, p99, bundle size, startup) + wire CI enforcement via `/ds-devops` |
| `--auto` | All modes, no questions, single-line summary |

No flags → present an up-front menu covering every mode, each with a one-line what-it-does — Setup (recommended) — launch-readiness setup / Listing — store listing copy / ASO — keyword + listing optimization / Privacy — store privacy labels / Review — pre-submission active-detection scan / Submission-notes — reviewer notes + reject replies / Release — release process / Post-launch — post-launch monitoring / Perf-budget — performance budget / (Cancel). A disambiguating flag skips the menu.

### Perf Budget Mode (`--perf-budget`)

Authors `ds/launch/perf-budget.json` (committed; `ds/<skill>/` operational namespace) + wires CI enforcement to read from that path — a functional CI gate (Category B, user-approved, version-controlled), not transient state. Keep only sections fitting the project type; default values from blueprint profile `Config.priorities` + industry baselines.

```json
{
  "web":    { "lcp_ms": 2500, "inp_ms": 200, "cls": 0.1, "ttfb_ms": 600, "bundle_js_kb": 300, "bundle_css_kb": 60 },
  "api":    { "p50_ms": 50, "p95_ms": 200, "p99_ms": 500, "error_rate_pct": 0.5 },
  "mobile": { "cold_start_ms": 2000, "warm_start_ms": 800, "app_size_mb": 40, "jank_pct": 1.0 }
}
```

**CI enforcement:** delegate to `/ds-devops` to add a CI step running the project's native perf tool (Lighthouse CI, k6, Firebase Test Lab, etc.) + compare to `ds/launch/perf-budget.json`; over-budget → CI fails with offending metric(s) named. Budget authoring is Category B (commits project to enforceable numbers); CI wiring is Category A once budget exists.

## Scopes

**Store Setup:** verify store account setup complete — developer account active, app ID registered, signing configured.

### Listing

| Element | What It Covers |
|---------|---------------|
| App name | Character limits, keyword inclusion, localization |
| Description | Short/long with pain-first opening — see voice guide in [references/aso-2026-updates.md](references/aso-2026-updates.md). First line states problem solved or outcome delivered — never feature list. Benefit-driven highlights. |
| Keywords | Keyword research, competitor analysis, localization |
| Screenshots | First 3 decide install — problem → solution → delight narrative. Text overlay captions with benefit-driven copy (captions index in Apple search since June 2025). Platform-specific: do not reuse iOS screenshots on Play. Required sizes per device, layout, A/B testing. |
| Video preview | Portrait video: +7% watch time, +5% conversion vs landscape (Google Play). 15-30s, no audio dependency, demonstrate core value. |
| Icon | Platform requirements, design guidelines |
| Category | Primary / secondary category selection |
| Age rating | Rating questionnaire guidance |

### ASO

| Check | What It Covers |
|-------|---------------|
| Keyword research | Competitor analysis, search volume estimation, difficulty |
| Title optimization | Primary keyword in title, character limits, localized titles |
| Subtitle / short description | Secondary keywords, value proposition, character limits |
| Screenshot caption indexing | Apple (June 2025): screenshot text overlays index in search. Captions must contain target keywords with benefit-driven copy. See narrative in [references/aso-2026-updates.md](references/aso-2026-updates.md). |
| Custom Product Pages | Apple: 70 CPPs per app (expanded from 35), each keyword-linkable for organic search. Create CPPs for audience segments + keyword clusters. |
| Category selection | Primary vs secondary, competition density analysis |
| Search ranking factors | Both stores shifting from keyword-matching to intent-driven semantic discovery. Apple: download velocity, ratings, update frequency, engagement. Google Play: engagement/retention outweighs raw downloads (2:1 redownload ratio), battery optimization as core vital (5% threshold — non-compliant apps excluded from discovery, March 2026). |
| A/B test recommendations | Title variants, screenshot order, icon alternatives. Google Play: portrait video variants. Apple PPO: up to 3 treatment variants. |

### Privacy

| Platform | What It Covers |
|----------|---------------|
| Apple Privacy Labels | Nutrition label declarations, data types, tracking status |
| Google Data Safety | Data safety section, ephemeral data, deletion support |
| Web privacy | Cookie consent, privacy policy, GDPR / CCPA compliance |

### Submission-Notes (`--submission-notes`)

Generates the **App Review Information → Notes** body upfront so reviewer never sends a Guideline 2.1 information request — each follow-up round-trip costs **+24-48 hours**; supplying everything in first submission eliminates them.

| Section | Auto-detected | User-confirmed |
|---------|--------------|---------------|
| App purpose + audience | from blueprint profile (`Type`, `Config.audience`) | yes |
| How to review (test path) | from existing READMEs / docs | yes |
| Demo / test credentials | — | required input |
| Auth providers | scan OAuth/OIDC client IDs, Sign in with Apple capability | confirmed |
| Payment processors | StoreKit / Play Billing imports | confirmed |
| **AI / ML services** | scan `requirements.txt`, `pubspec.yaml`, `package.json`, code imports for `{ai-libs}`. For each: name + license + repo URL + hosting location | required input — license & hosting per service |
| Data handling | privacy-labels cross-reference | yes |
| Account deletion procedure | search `delete account` UI flow | yes |
| Regional differences | default "consistent across all regions" | confirm or override |
| Regulated industry | default "N/A" | confirm or override |
| Reviewer-only contact | — | required input |

**Output:** `ds/launch/submission-notes-apple.txt` + `ds/launch/submission-notes-google.txt` + `ds/launch/submission-meta.yml` (audit trail, committed). Generic template + cookbook of pre-written reject replies in [references/app-store-submission-template.md](references/app-store-submission-template.md). **Pre-submission self-audit:** mode runs `--review` active-detection scan first — any CRITICAL → submission notes not generated until fixed; WARN if HIGH findings present but not blocking.

### Review (Active Detection)

Each check scans codebase + produces PASS/FAIL with severity and file:line — not a manual checklist.

| Check | Detection Method | Severity |
|-------|-----------------|----------|
| Privacy policy | Scan configs + metadata for URL, verify HTTP 200 | CRITICAL |
| Metadata completeness | Scan store metadata dirs for empty/placeholder content | CRITICAL |
| Permission descriptions | Parse `Info.plist` / `AndroidManifest.xml` for missing descriptions | HIGH |
| Privacy manifests + SDK compliance | Scan for `PrivacyInfo.xcprivacy`, flag SDKs without manifests | HIGH |
| AI data consent | Check for consent modal if external AI services detected | HIGH |
| Data deletion | Search for account deletion UI flow | HIGH |
| Platform cross-references | Search listing text for competing platform mentions | MEDIUM |
| Crash-prone patterns | Scan entry points for force-unwraps, unhandled exceptions | MEDIUM |
| Age rating | Verify questionnaire completeness, new 13+/16+/18+ tiers | MEDIUM |
| SDK + build requirements | Check minimum SDK version (iOS 26 SDK required from April 2026) | MEDIUM |
| ATT + Privacy Manifests | App Tracking Transparency prompt, SDK `PrivacyInfo.xcprivacy` validation | HIGH |
| IAP external-payment | StoreKit/Play Billing present alongside Stripe/PayPal/checkout URLs for digital content, or "pay on our website" / "subscribe at" strings pointing off-store (Guideline 3.1.1; Play Payments policy) | CRITICAL |
| Restore purchases | Non-consumable IAP or subscription imports detected but no restore-purchases call / UI entry point found (Guideline 3.1.2) | HIGH |
| Sign in with Apple | Google/Facebook/Twitter auth SDK detected without `com.apple.developer.applesignin` entitlement or `ASAuthorizationAppleIDProvider` import (Guideline 4.8) | HIGH |
| Reviewer-access gap | Login/auth flow detected but `ds/launch/submission-notes-apple.txt` absent or missing demo-credentials section — reviewer will hit a login wall with no way through | HIGH |
| App completeness / remote gating | Primary feature classes wrapped in remote-config / feature-flag conditions with no guaranteed-on default — app may appear non-functional to reviewer (Guideline 2.1; Play deceptive-behavior policy) | HIGH |
| Content-vs-rating | Gambling SDK, loot-box pattern, open `WebView` with no URL restriction, or UGC text-input detected alongside an age-rating declaration of 4+ / Everyone — declared rating inconsistent with detected content signals | MEDIUM |
| Review timing | Apple: 24-48h typical. Google: 1-7 days (first app longer). | INFO |

### Release

| Element | What It Covers |
|---------|---------------|
| Versioning | Semantic versioning, build number management |
| Release notes | User-facing changelog, localization |
| Staged rollout | Google Play: 1% → 5% → 20% → 50% → 100% (manual). Apple: 7-day phased 1% → 2% → 5% → 10% → 20% → 50% → 100% (can pause). |
| Force update | Minimum version enforcement, update UX |
| Rollback | Emergency rollback procedure |

### SEO

| Element | What It Covers |
|---------|---------------|
| Meta tags | Title, description, OG tags (og:title, og:description, og:image, og:url) per page |
| Sitemap | XML sitemap generation, index coverage, lastmod/priority |
| robots.txt | Disallow rules, sitemap directive, crawl-delay |
| Canonical URLs | Self-referencing canonicals, duplicate-content prevention |
| Structured data | JSON-LD (Organization, WebSite, BreadcrumbList, FAQ, Product) |

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | OAuth consent screen — verify production approval status, homepage/privacy URLs, authorized domains | review |
| Apple | Sign in with Apple — verify entitlement + `ASAuthorizationAppleIDProvider` import (Guideline 4.8) | review |
| Google | Data safety section — ensure declarations match actual API scopes used | privacy |
| Apple | Apple Privacy Labels — verify nutrition label declares sign-in and contact info if applicable | privacy |

## Delegation

**Owns:** store, release, privacy-labels (store-label-correctness only), perf-budget (`--perf-budget` mode) | **Delegates:** ds-compliance → canonical privacy; ds-mobile → mobile-specific store compliance | **Receives:** ds-ship → Phase 5 launch pass

## Execution Flow

Setup → Detect → Analyze → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → interactive menu.
2. **IDU:** Profile → Config.audience, Config.deploy, Type, Stack. Findings(store, review, privacy-labels, release) → verify + use. Absent → own analysis.
3. Detect platform from project signals (`pubspec.yaml` → mobile, `package.json` → web, etc.) + current launch stage: pre-submission, in-review, post-launch.

**Gate:** Platform + mode confirmed. If fails → ambiguous platform → prompt iOS / Android / Web / All; no mode after menu → re-prompt once then exit with WARN "No mode selected — run /ds-launch with a flag to proceed."

### Phase 2: Detect Current State

Search for store-related configs, version info, existing privacy policy / ToS, CI/CD release workflows; build inventory of what exists vs missing.

**Gate:** Inventory complete. If fails → note what was found as partial; mark missing config type (store configs, version info, privacy policy, CI workflows) as absent rather than unknown; proceed to Phase 3 — missing entries become FAIL findings in review scope.

### Phase 3: Generate [setup, listing, aso, privacy, review, submission-notes]

- **Store setup:** platform-specific account setup checklist; certificate / signing key guide; TestFlight / Internal Testing steps.
- **Listing metadata:** final store-ready app description (short + long; refine existing `[DRAFT]` descriptions). Keyword research framework, screenshot size requirements, localization checklist. Template structure:
  - Short description (80 chars max) per language — per-locale keyword optimization, not literal translation; full description with consistent sections across all languages: How it works (3-5 steps), Key features (bullet list, benefit-first: `"Get {benefit}"` not `"Has {feature}"`), Privacy/security highlights + Pricing/plans (if applicable)
  - Privacy highlight table `| Data Type | Collected (Yes/No) | Shared with 3rd Party (Yes/No) | Purpose |` — maps directly to Apple Privacy Labels + Google Data Safety
  - Review notes for store review teams: special permission justifications, demo credentials (if needed), features requiring network, consumable vs subscription IAP model
  - Screenshot narrative (6 recommended, full journey): auth/onboarding → main list/home → core action → progress/processing → result/output → monetization/settings
- **ASO mode:** competitor keyword analysis, title/subtitle optimization, category placement recommendation, A/B variant suggestions.
- **Release automation safety ([references/principles.md §8](references/principles.md)):** any generated release-automation file (Fastlane, `Matchfile`, CI workflow, signing scripts) MUST externalize credentials to env vars. Generate `.env.example` placeholders for: keystore passwords, App Store Connect API keys, Play Console JSON keys, signing identities, OAuth client secrets. Never embed actual values in committed files. Commit message gate: scan generated files for high-entropy strings before suggesting commit.
- **Privacy labels:** scan codebase for data collection → map to Apple/Google categories → generate declaration guide → flag code/label discrepancies.
- **Submission notes (`--submission-notes`):** run pre-submission self-audit (12-item checklist from references/app-store-submission-template.md); block on CRITICAL findings. Auto-detect AI services / auth providers / IAP presence; prompt user for license + hosting per AI service, reviewer-only contact, screen recording URL. Generate per-platform notes (`ds/launch/submission-notes-{apple,google}.txt`) following proactive template; persist `ds/launch/submission-meta.yml` (committed, audit trail). Include "Common Rejection Cookbook" (5 prewritten reply templates for Guidelines 2.1 / 5.1.1(v) / 3.1.1 / 4.8 / 5.1.2 / 5.1.1(i)) so re-submission is one-step.
- **Review preparation (active scan — not just a checklist):** scan project for top rejection triggers; each check produces an evidence-cited PASS/FAIL finding with severity + file:line. Scope checks listed in §Review (Active Detection) above.

**Gate:** All listing, ASO, review artifacts generated. If fails → identify failed artifact (listing metadata, ASO, privacy labels, review scan), record `status: failed`, mark phase `partial`, continue with rest; surface failed artifacts in Phase 6 summary as WARN "manual completion required". Live policy fetch failures (App Store Connect, Play Console) → use fallback values, annotate artifact "(fallback values used — verify before submission)".

### Phase 4: Release Management [release, post-launch]

**Version management:** check current version, suggest bump (patch/minor/major), generate release notes from commits + staged rollout strategy. **Post-launch monitoring:** checklist covering crash-free rate targets, store rating tracking, review response, download monitoring, update cadence, force-update thresholds.

**Gate:** Release artifacts generated. If fails → un-generatable release artifact (version bump, release notes, staged rollout, post-launch checklist) → log as `failed`, proceed with successful ones, list failures in summary with "manual action required".

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → record unresolved as `pending-user-decision`, proceed to Summary with WARN, list prominently.

### Phase 6: Summary

```
ds-launch: {OK|WARN|FAIL} | Platform: {iOS|Android|Web|All} | Ready: {n}/{n} checks | Missing: {n} items | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Include checklist of remaining items before submission. FRC+DSC accounting.

**Value Delivered:** 1-5 concrete bullets, real submission outcomes only. Example shapes (placeholders, not literal):

- `Store listing + privacy labels generated — submission no longer rejected for missing required fields`
- `App Review Notes pre-filled — reviewer round-trip eliminated (saves 24-48h per round)`
- `{n} ASO keyword candidates with search volume + competition score — listing copy is data-driven, not gut feeling`
- `Perf budget authored at `ds/launch/perf-budget.json` (LCP {x}ms, INP {y}ms, bundle {z}kB) + CI wiring — regressions now block release instead of slipping`

Zero-change run: `Submission package already complete — no missing fields`.

**Gate:** Summary + Value Delivered printed with submission readiness status. If fails → write partial summary: completed phases, generated artifacts (even partial), open CRITICAL/HIGH findings, status FAIL with "Summary incomplete — re-run to complete remaining phases."

## Quality Gates

- Every store listing element meets platform character limits; privacy labels match actual code behavior (verified by codebase scan)
- Pre-review checklist has zero CRITICAL items; version numbers are valid semver with incrementing build numbers
- Release notes are user-friendly (not developer jargon); every finding gets a disposition (FRC)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No store config found | Start from setup mode |
| Platform ambiguous | Ask: iOS / Android / Web / All |
| Privacy label mismatch | Flag specific discrepancy, suggest correction |
| Missing required metadata | List missing items, prioritize by blocking vs non-blocking |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Will cause rejection: missing privacy policy, crash, policy violation |
| HIGH | Likely rejection: incomplete metadata, permission without description |
| MEDIUM | Quality issue: poor screenshots, weak description, missing keywords |
| LOW | Optimization: A/B test opportunity, localization gap |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Web-only app (no store) | Focus on domain, hosting, SEO meta tags, PWA manifest |
| First-ever submission | Start from account setup, include all beginner steps |
| Update to existing app | Skip setup, focus on release notes + rollout |
| Multi-platform | Generate per-platform checklists, note shared vs platform-specific |
| Enterprise / internal distribution | Skip public store, focus on MDM / enterprise distribution |

