---
name: ds-launch
description: Store and release management — store submission, listing optimization, release strategy, post-launch monitoring. Use when preparing an app-store release or planning a launch.
---

# /ds-launch

~40% of iOS submissions get delayed or rejected for preventable errors. This skill scans your project and flags them before you submit.

**Store & Release Management** — Store submission, listing optimization, release strategy, and post-launch monitoring.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

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
- Standalone. Uses blueprint profile when available; `ds/audit/findings.md` only when fresh (`git_hash == HEAD` AND current run-cycle); own analysis otherwise.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--setup` | Store account setup checklists + initial configuration |
| `--listing` | Store listing metadata: description, keywords, screenshots |
| `--privacy` | Privacy label declarations — **store-label-correctness only**. Canonical privacy audit delegated to `/ds-compliance --privacy` (privacy audit belongs to ds-compliance). Verifies store labels match actual code behavior; does not re-audit data collection or consent. |
| `--review` | Pre-review checklist: common rejection prevention |
| `--submission-notes` | **Proactive submission notes generator** — fills App Review Information Notes upfront so reviewer doesn't need to ask follow-ups (saves +24-48h per round-trip). See [references/app-store-submission-template.md](references/app-store-submission-template.md) |
| `--aso` | App Store Optimization — keyword research + search ranking |
| `--seo` | Web discoverability: meta/OG tags, sitemap, robots, canonicals, JSON-LD (web platform) |
| `--email` | Email deliverability: SPF/DKIM/DMARC, one-click unsubscribe, spam-rate posture (sending domain detected) |
| `--release` | Release management: version, notes, staged rollout |
| `--post-launch` | Post-launch monitoring checklist |
| `--perf-budget` | Author a formal perf budget (LCP, INP, p99, bundle size, startup) + wire CI enforcement via `/ds-devops` |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

No flags → present an up-front menu of every mode in the Arguments table (each with its one-line effect), Setup marked (recommended), plus (Cancel). A disambiguating flag skips the menu. `--auto` alone (no mode flag) also skips the menu — runs every mode in sequence, the skill's best-judgment default (a flag disambiguates every menu).

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

**Under `--auto`:** auto-detected fields (app purpose, test path, auth providers, payment processors, AI services, data handling, account deletion) still populate automatically; fields with no inferable value (demo credentials, reviewer-only contact) are never fabricated — they match the publish/irreversible exception list (a value only a human can supply) and are recorded `needs-human` in the summary instead of prompted for.

**Output:** `ds/launch/submission-notes-apple.txt` + `ds/launch/submission-notes-google.txt` + `ds/launch/submission-meta.yml` (audit trail, committed). Generic template + cookbook of pre-written reject replies in [references/app-store-submission-template.md](references/app-store-submission-template.md). **Pre-submission self-audit:** mode runs `--review` active-detection scan first — any CRITICAL → submission notes not generated until fixed; WARN if HIGH findings present but not blocking.

### Review (Active Detection)

Each check scans codebase + produces PASS/FAIL with severity and file:line — not a manual checklist.

| Check | Detection Method | Severity |
|-------|-----------------|----------|
| Privacy policy | Scan configs + metadata for URL; `curl -s -o /dev/null -w '%{http_code}' {url}` → `200` | CRITICAL |
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
| IAP external-payment | StoreKit/Play Billing present alongside Stripe/PayPal/checkout URLs for digital content, or "pay on our website" / "subscribe at" strings pointing off-store. **Jurisdiction-split (post-Epic, verify-current):** US App Store storefront — external payment links are permitted without entitlement (Ninth Circuit Dec 11 2025: Apple may eventually charge a "reasonable" cost-based commission — rate not yet set — and may keep external links no more visually prominent than IAP); outside the US — StoreKit External Purchase Link Entitlement required in designated regions, otherwise IAP-only (Guideline 3.1.1). Play: alternative billing per settlement terms; third-party Android stores open from 22 Jul 2026. Flag as CRITICAL only where the pattern violates the target storefront's current rules — never blanket-flag US-storefront external links | CRITICAL (jurisdiction-conditional) |
| Clone-category risk (4.3(b), Jun 2026) | App's category/concept matches Apple's named spam-prone classes (dating, flashlight, sound effects, wallpaper, simple timers, fortune telling) without a meaningfully differentiated feature set — new "indistinguishable" submissions in these categories are barred and existing low-quality apps may be removed | HIGH |
| Live Activities misuse (4.5.3) | ActivityKit/Live Activities used for promotional/unsolicited content — 4.5.3 bars using Live Activities to spam, phish, or send unsolicited messages; random/anonymous-chat features additionally fall under Guideline 1.2 UGC duties (Feb 6 2026 revision) | MEDIUM |
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
| User-facing changelog (D6, advisory) | Distinct from dev/store release notes — a plain-language "what changed" surface exists, especially when an OTA/silent auto-update channel is detected (CodePush, Expo Updates, Electron auto-updater, or equivalent). OTA channel detected + no user-facing changelog surface -> advisory finding "silent OTA channel with no user-facing changelog" (never a blocker) |
| Staged rollout | Google Play: 1% → 5% → 20% → 50% → 100% (manual). Apple: 7-day phased 1% → 2% → 5% → 10% → 20% → 50% → 100% (can pause). |
| Rollout automation (advisory) | Mobile project (`pubspec.yaml` / `*.xcodeproj` / `build.gradle` with `android {}`) with no `Fastfile` → MEDIUM finding "no fastlane automation — staged rollout percentages require manual store-console execution". `Fastfile` present → verify release lanes cover the staged-rollout steps above. |
| Force update | Minimum version enforcement, update UX |
| Rollback | Emergency rollback procedure |
| Rollback narrative (D6, advisory) | Beyond the technical rollback procedure above — is there a documented plan for how users are informed when a bad release is rolled back (in-app notice, status page, email)? No documented rollback communication plan -> advisory finding "no rollback communication plan" (never a blocker) |

### SEO (`--seo` — web platform; auto-included for web-only projects; audit-rule counterpart: ds-compliance WEB-08 — generation/execution is canonical here)

| Element | What It Covers |
|---------|---------------|
| Meta tags | Title, description, OG tags (og:title, og:description, og:image, og:url) per page |
| Sitemap | XML sitemap generation, index coverage, lastmod/priority |
| robots.txt | Disallow rules, sitemap directive, crawl-delay |
| Canonical URLs | Self-referencing canonicals, duplicate-content prevention |
| Structured data | JSON-LD (Organization, WebSite, BreadcrumbList, FAQ, Product) — validate against schema.org types, don't just emit |
| Core Web Vitals link | CWV "Good" bands (LCP ≤2.5s, INP <200ms, CLS <0.1) act as a ranking tie-breaker among similar-quality pages — not a primary ranking driver; budget + enforcement via `--perf-budget` |
| llms.txt | **Speculative, low signal** — no major AI provider (Google, OpenAI, Anthropic, Meta) uses it in production retrieval; Google confirmed non-support. Only worth adding (~half a day) when serving developer-tool docs to AI coding agents (Cursor/Claude Code class), never as an SEO lever |

### Email Deliverability (`--email` — activates when a sending domain is detected: transactional/marketing email service config, SMTP creds, newsletter tooling)

| Check | What It Covers | Severity |
|-------|---------------|----------|
| SPF + DKIM + DMARC | DNS records present on the sending domain; DMARC at minimum `p=none`; RFC5322-From domain aligned to SPF or DKIM org domain. Bulk-sender rule (Gmail: ~5,000+ msgs/24h to personal Gmail) requires both SPF and DKIM + DMARC | HIGH |
| One-click unsubscribe (RFC 8058) | Promotional messages carry `List-Unsubscribe` + `List-Unsubscribe-Post` headers with an HTTPS POST endpoint (idempotent, async-processed, responds inside Gmail's ~30s timeout; unsubscribes processed within ~2 days) | HIGH |
| Spam-rate posture | Complaint rate monitored via Gmail Postmaster Tools; 0.3% is the hard blocking ceiling, <0.08% the safe operating target — approaching it → list hygiene + frequency reduction, not new domains | MEDIUM |
| BIMI (optional) | Brand logo in supporting inboxes — requires DMARC at enforcement (`p=quarantine`/`reject`) + verified logo record; only after DMARC enforcement is stable | LOW (advisory) |

### Desktop Distribution (conditional — desktop project detected: Electron/Tauri config, `*.xcodeproj` with macOS target, MSIX/WiX manifest)

| Check | What It Covers | Severity |
|-------|---------------|----------|
| macOS notarization | Distribution outside MAS: hardened runtime enabled, app signed with Developer ID cert, notarized via `notarytool` (not legacy `altool`), ticket stapled (`stapler`) — unnotarized apps are blocked by Gatekeeper | HIGH |
| Windows signing | Authenticode signature on installer + binaries (unsigned → SmartScreen warning kills conversion); MSIX packaging where Microsoft Store or clean install/uninstall matters | HIGH |
| Auto-update integrity | Update channel (Sparkle, electron-updater, Tauri updater) serves signed updates over HTTPS with signature verification ON — an unsigned update feed is remote code execution as a feature | HIGH |
| Store option fit | MAS (sandbox + entitlements review) vs direct distribution vs Microsoft Store — chosen deliberately with the sandbox-restriction tradeoff stated; MAS submission then follows the standard store scopes above | MEDIUM |
| User-facing changelog + staged rollout | Same D6 rules as mobile Release scope — desktop auto-update is the archetypal silent OTA channel | MEDIUM |

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | OAuth consent screen — verify production approval status, homepage/privacy URLs, authorized domains (Google OAuth verification requirement — a citable external platform mandate, so a blocker, not advisory) | review |
| Apple | Sign in with Apple — verify entitlement + `ASAuthorizationAppleIDProvider` import (Guideline 4.8) | review |
| Google | Data safety section — ensure declarations match actual API scopes used | privacy |
| Apple | Apple Privacy Labels — verify nutrition label declares sign-in and contact info if applicable | privacy |

## Delegation

**Owns:** store, release, privacy-labels (store-label-correctness only), seo (web discoverability), email-deliverability, perf-budget (`--perf-budget` mode) | **Delegates:** ds-compliance → canonical privacy; ds-mobile → mobile-specific store compliance | **Receives:** ds-ship → Phase 5 launch pass; ds-productize → store/IAP listing + release execution

## Execution Flow

Setup → Detect → Analyze → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → interactive menu.
2. **Upstream artifacts:** Profile → Config.audience, Config.deploy, Type, Stack. Findings(store, review, privacy-labels, release) → verify + use. Absent → own analysis.
3. Detect platform from project signals (`pubspec.yaml` → mobile, `package.json` → web, Electron/Tauri config or macOS/MSIX packaging manifests → desktop, etc.) + current launch stage: pre-submission, in-review, post-launch. Desktop detected → activate the Desktop Distribution scope.

**Gate:** Platform + mode confirmed. If fails → ambiguous platform → prompt iOS / Android / Web / Desktop / All (**under `--auto`:** default to All — safest coverage, no prompt); no mode after menu → re-prompt once then exit with WARN "No mode selected — run /ds-launch with a flag to proceed."

### Phase 2: Detect Current State

Search for store-related configs, version info, existing privacy policy / ToS, CI/CD release workflows; build inventory of what exists vs missing.

**Gate:** Inventory lists each config type (store configs, version info, privacy policy / ToS, CI release workflows) as present or absent. If fails → note what was found as partial; mark missing config type (store configs, version info, privacy policy, CI workflows) as absent rather than unknown; proceed to Phase 3 — missing entries become FAIL findings in review scope.

### Phase 3: Generate [setup, listing, aso, seo, email, privacy, review, submission-notes]

- **Store setup:** platform-specific account setup checklist; certificate / signing key guide (CI automation: authenticate with App Store Connect API keys, not Apple-ID/password auth); TestFlight / Internal Testing steps.
- **Listing metadata:** final store-ready app description (short + long; refine existing `[DRAFT]` descriptions). Keyword research framework, screenshot size requirements, localization checklist. Template structure:
  - Short description (80 chars max) per language — per-locale keyword optimization, not literal translation; full description with consistent sections across all languages: How it works (3-5 steps), Key features (bullet list, benefit-first: `"Get {benefit}"` not `"Has {feature}"`), Privacy/security highlights + Pricing/plans (if applicable)
  - Privacy highlight table `| Data Type | Collected (Yes/No) | Shared with 3rd Party (Yes/No) | Purpose |` — maps directly to Apple Privacy Labels + Google Data Safety
  - Review notes for store review teams: special permission justifications, demo credentials (if needed), features requiring network, consumable vs subscription IAP model
  - Screenshot narrative (6 recommended, full journey): auth/onboarding → main list/home → core action → progress/processing → result/output → monetization/settings
- **ASO mode:** competitor keyword analysis, title/subtitle optimization, category placement recommendation, A/B variant suggestions.
- **SEO mode (web):** audit each §SEO element against the actual routes/pages (missing → generate: meta/OG per page, sitemap.xml, robots.txt, canonicals, JSON-LD validated against schema.org types); report CWV tie-breaker status from the perf budget when one exists.
- **Email mode (sending domain detected):** query DNS (`dig +short TXT {domain}` → `v=spf1…`; `dig +short TXT {selector}._domainkey.{domain}` → DKIM key record; `dig +short TXT _dmarc.{domain}` → `v=DMARC1…`) and verify alignment; inspect outbound-mail code/config for RFC 8058 headers + unsubscribe endpoint; produce missing DNS record values and header/endpoint stubs as findings (DNS changes are Category B — user applies them at the registrar).
- **Release automation safety ([references/principles.md §8](references/principles.md)):** any generated release-automation file (Fastlane, `Matchfile`, CI workflow, signing scripts) MUST externalize credentials to env vars. Generate `.env.example` placeholders for: keystore passwords, App Store Connect API keys, Play Console JSON keys, signing identities, OAuth client secrets. Never embed actual values in committed files. Commit message gate: `grep -E 'AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN.*PRIVATE KEY-----' {generated-files}` → no output, plus a high-entropy string review, before suggesting commit.
- **Privacy labels:** scan codebase for data collection → map to Apple/Google categories → generate declaration guide → flag code/label discrepancies.
- **Submission notes (`--submission-notes`):** run pre-submission self-audit (12-item checklist from references/app-store-submission-template.md); block on CRITICAL findings. Auto-detect AI services / auth providers / IAP presence; prompt user for license + hosting per AI service, reviewer-only contact, screen recording URL. Generate per-platform notes (`ds/launch/submission-notes-{apple,google}.txt`) following proactive template; persist `ds/launch/submission-meta.yml` (committed, audit trail). Include "Common Rejection Cookbook" (5 prewritten reply templates for Guidelines 2.1 / 5.1.1(v) / 3.1.1 / 4.8 / 5.1.2 / 5.1.1(i)) so re-submission is one-step.
- **Review preparation (active scan — not just a checklist):** scan project for top rejection triggers; each check produces an evidence-cited PASS/FAIL finding with severity + file:line. Scope checks listed in §Review (Active Detection) above.

**Gate:** All listing, ASO, review artifacts generated. If fails → identify failed artifact (listing metadata, ASO, privacy labels, review scan), record `status: failed`, mark phase `partial`, continue with rest; surface failed artifacts in Phase 6 summary as WARN "manual completion required". Live policy fetch failures (App Store Connect, Play Console) → use fallback values, annotate artifact "(fallback values used — verify before submission)".

### Phase 4: Release Management [release, post-launch]

**Version management:** check current version, suggest bump (patch/minor/major), generate release notes from commits + staged rollout strategy. **Post-launch monitoring:** checklist covering crash-free rate targets, store rating tracking, review response, download monitoring, update cadence, force-update thresholds.

**Marketplace re-verification trigger:** once publicly listed on a marketplace (e.g. Workspace Marketplace), any change to OAuth scopes or redirect URIs starts a new verification cycle — record this permanently in the security/scope-hygiene doc and gate scope/redirect changes as release events; an unreviewed change can get the listing suspended. (XR-125)

**Gate:** Release artifacts generated. If fails → un-generatable release artifact (version bump, release notes, staged rollout, post-launch checklist) → log as `failed`, proceed with successful ones, list failures in summary with "manual action required".

### Phase 5: Needs-Approval Review [needs_approval > 0]

**Under `--auto`:** no review step is shown — every item resolves by best judgment (applied, using the same impact/effort/risk reasoning this review block would show), except items matching the publish/irreversible exception list, which become `skipped (needs-human)`. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → record unresolved as `pending-user-decision`, proceed to Summary with WARN, list prominently.

### Phase 6: Summary

```
ds-launch: {OK|WARN|FAIL} | Platform: {iOS|Android|Web|Desktop|All} | Ready: {n}/{n} checks | Missing: {n} items | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Include checklist of remaining items before submission. Disposition accounting — totals balance.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `Store listing + privacy labels generated — submission no longer rejected for missing required fields`
- `App Review Notes pre-filled — reviewer round-trip eliminated (saves 24-48h per round)`
- `{n} ASO keyword candidates with search volume + competition score — listing copy is data-driven, not gut feeling`
- `Perf budget authored at `ds/launch/perf-budget.json` (LCP {x}ms, INP {y}ms, bundle {z}kB) + CI wiring — regressions now block release instead of slipping`

Zero-change run: `Submission package already complete — no missing fields`.

**Gate:** Summary + Value Delivered printed with submission readiness status. If fails → write partial summary: completed phases, generated artifacts (even partial), open CRITICAL/HIGH findings, status FAIL with "Summary incomplete — re-run to complete remaining phases."

## Quality Gates

- Every store listing element meets platform character limits; privacy labels match actual code behavior (verified by codebase scan)
- Pre-review checklist has zero CRITICAL items; version numbers are valid semver with incrementing build numbers
- Release notes are user-friendly (not developer jargon); every finding gets a disposition
- W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No store config found | Start from setup mode |
| Platform ambiguous | Ask: iOS / Android / Web / All (`--auto`: default to All) |
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
| Web-only app (no store) | Skip store scopes; run seo (auto-included) + email (when sending domain present) + release + post-launch |
| First-ever submission | Start from account setup, include all beginner steps |
| Update to existing app | Skip setup, focus on release notes + rollout |
| Multi-platform | Generate per-platform checklists, note shared vs platform-specific |
| Enterprise / internal distribution | Skip public store, focus on MDM / enterprise distribution |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
