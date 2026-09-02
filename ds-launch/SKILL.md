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
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.
- **Metadata directory:** `ds/launch/` holds this skill's committed deliverables only — store listing text, privacy-label mappings, release notes, `perf-budget.json`, submission notes (`submission-notes-{apple,google}.txt`, `submission-meta.yml`). No other skill or scratch output writes there.

## Arguments

| Flag | Effect |
|------|--------|
| `--setup` | Store account setup checklists + initial configuration |
| `--listing` | Store listing metadata: description, keywords, screenshots |
| `--privacy` | Privacy label declarations — **store-label-correctness only**, always runs inline regardless of `/ds-compliance`. `/ds-compliance` present → additionally delegate the canonical privacy audit (`--privacy`, data collection + consent); absent → gap-note `[privacy-canonical] not analyzed — requires /ds-compliance --privacy`, store-label check stands alone. |
| `--review` | Pre-review checklist: common rejection prevention |
| `--submission-notes` | **Proactive submission notes generator** — fills App Review Information Notes upfront so reviewer doesn't need to ask follow-ups (saves +24-48h per round-trip). See [references/app-store-submission-template.md](references/app-store-submission-template.md) |
| `--aso` | App Store Optimization — keyword research + search ranking |
| `--seo` | Advisory handoff to `/ds-compliance` (web scope, WEB-08) for SEO audit + generation (meta/OG, sitemap, robots, canonicals, JSON-LD) — this skill runs no local SEO detector |
| `--email` | Advisory handoff to `/ds-compliance` for email-authentication audit (SPF/DKIM/DMARC, one-click unsubscribe, spam-rate posture) — this skill runs no local DNS detector |
| `--release` | Release management: version, notes, staged rollout |
| `--post-launch` | Post-launch monitoring checklist |
| `--perf-budget` | Author a formal perf budget (LCP, INP, p99, bundle size, startup) + wire CI enforcement via `/ds-devops` |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Without flags: every mode runs in sequence, each decision resolved by best judgment and recorded (the skill's default). `--ask` alone (no mode flag) presents an up-front menu of every mode in the Arguments table (each with its one-line effect), Setup marked (recommended), plus (Cancel). A disambiguating flag skips the menu.

### Perf Budget Mode (`--perf-budget`)

Authors `ds/launch/perf-budget.json` (committed; `ds/<skill>/` operational namespace) + wires CI enforcement to read from that path — a functional CI gate (Category B, user-approved, version-controlled), not transient state. Schema + CI-enforcement detail: [references/perf-budget-schema.md](references/perf-budget-schema.md).

## Scopes

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| Store Setup, Listing, ASO, Privacy (store-label) | `platforms` ∩ {ios, android} ≠ ∅ | N/A — no store target (web/desktop-only project) |
| Submission-Notes | `--submission-notes` | N/A — mode not selected |
| Review | any source (individual store-only checks N/A when no store target) | — |
| Release | any source | — |
| SEO | `ui=web` (advisory handoff to `/ds-compliance` — no local detector) | N/A — `ui≠web` |
| Email Deliverability | sending domain detected (advisory handoff to `/ds-compliance` — no local detector) | N/A — no sending domain detected |
| Desktop Distribution | desktop project detected (Electron/Tauri config, `*.xcodeproj` macOS target, MSIX/WiX manifest) | N/A — no desktop target |
| A9 Ecosystem | `integrations` signal or Blueprint Profile `Integrations:` names `google-workspace`/`apple-ecosystem` | N/A — neither source names it |

**Store Setup:** verify store account setup complete — developer account active, app ID registered, signing configured.

### Listing

| Element | What It Covers |
|---------|---------------|
| App name | Character limits, keyword inclusion, localization |
| Description | Short/long with pain-first opening — see voice guide in [references/aso-2026-updates.md](references/aso-2026-updates.md). First line states problem solved or outcome delivered — never feature list. Benefit-driven highlights. |
| Keywords | Keyword research, competitor analysis, localization |
| Screenshots | 3-shot narrative + caption rules + required sizes — see [references/aso-2026-updates.md](references/aso-2026-updates.md) § Screenshot Narrative. Platform-specific: do not reuse iOS screenshots on Play. |
| Video preview | 15-30s, no audio dependency, demonstrate core value — portrait-format conversion data: references/aso-2026-updates.md § Screenshot Narrative (Video Preview subsection). |
| Icon | Platform requirements, design guidelines |
| Category | Primary / secondary category selection |
| Age rating | Rating questionnaire guidance |

### ASO

| Check | What It Covers |
|-------|---------------|
| Keyword research | Competitor analysis, search volume estimation, difficulty |
| Title optimization | Primary keyword in title, character limits, localized titles |
| Subtitle / short description | Secondary keywords, value proposition, character limits |
| Screenshot caption indexing | Apple (June 2025+): screenshot text overlays index in search — target keywords with benefit-driven copy. Detail: [references/aso-2026-updates.md](references/aso-2026-updates.md) § Algorithm Changes. |
| Custom Product Pages | Apple: up to 70 CPPs per app, each keyword-linkable for organic search — create CPPs per audience segment / keyword cluster. |
| Category selection | Primary vs secondary, competition density analysis |
| Search ranking factors | Both stores shifting from keyword-matching to intent-driven semantic discovery — full factor breakdown: references/aso-2026-updates.md § Algorithm Changes. |
| A/B test recommendations | Title variants, screenshot order, icon alternatives. Google Play: portrait video variants. Apple PPO: up to 3 treatment variants. |

### Privacy

| Platform | What It Covers |
|----------|---------------|
| Apple Privacy Labels | Nutrition label declarations, data types, tracking status |
| Google Data Safety | Data safety section, ephemeral data, deletion support |
| Web privacy | Cookie consent, privacy policy, GDPR / CCPA compliance |

### Submission-Notes (`--submission-notes`)

Generates the **App Review Information → Notes** body upfront so reviewer never sends a Guideline 2.1 information request — each follow-up round-trip costs **+24-48 hours**; supplying everything in first submission eliminates them. Field-by-field detection method + required user input: [references/app-store-submission-template.md](references/app-store-submission-template.md) § Skill Generation Rules.

Default and `--ask` alike: auto-detected fields (app purpose, test path, auth providers, payment processors, AI services, data handling, account deletion) populate automatically; fields with no inferable value (demo credentials, reviewer-only contact) are never fabricated — they match the publish/irreversible exception list (a value only a human can supply) and are recorded `only you can do` in the summary instead of guessed. `--ask` additionally prompts for these fields instead of leaving them `only you can do`.

**Output:** `ds/launch/submission-notes-apple.txt` + `ds/launch/submission-notes-google.txt` + `ds/launch/submission-meta.yml` (audit trail, committed). Generic template + cookbook of pre-written reject replies in [references/app-store-submission-template.md](references/app-store-submission-template.md). **Pre-submission self-audit:** mode runs `--review` active-detection scan first — any CRITICAL → submission notes not generated until fixed; WARN if HIGH findings present but not blocking.

### Review (Active Detection)

28 checks (LCH-01 to LCH-28), each scanning codebase + producing PASS/FAIL with severity and file:line — not a manual checklist. Full Detect/Fix/Impact/Source per check: [references/rules-store-review.md](references/rules-store-review.md).

### Release

| Element | What It Covers |
|---------|---------------|
| Versioning | Semantic versioning, build number management |
| Release notes | User-facing changelog, localization |
| User-facing changelog (D6, advisory) | Distinct from dev/store release notes — a plain-language "what changed" surface exists, especially when an OTA/silent auto-update channel is detected (CodePush, Expo Updates, Electron auto-updater, or equivalent). OTA channel detected + no user-facing changelog surface -> advisory finding "silent OTA channel with no user-facing changelog" (never a blocker) — impact: users get silently-changed behavior with no explanation, driving confused support tickets |
| Staged rollout | Google Play: 1% → 5% → 20% → 50% → 100% (manual). Apple: 7-day phased 1% → 2% → 5% → 10% → 20% → 50% → 100% (can pause). |
| Rollout automation (advisory) | Mobile project (`pubspec.yaml` / `*.xcodeproj` / `build.gradle` with `android {}`) with no `Fastfile` → MEDIUM finding "no fastlane automation — staged rollout percentages require manual store-console execution". `Fastfile` present → verify release lanes cover the staged-rollout steps above. — impact: manual percentage bumps get forgotten or delayed, so the staged rollout silently stalls at its first step |
| Force update | Minimum version enforcement, update UX |
| Rollback | Emergency rollback procedure |
| Rollback narrative (D6, advisory) | Beyond the technical rollback procedure above — is there a documented plan for how users are informed when a bad release is rolled back (in-app notice, status page, email)? No documented rollback communication plan -> advisory finding "no rollback communication plan" (never a blocker) — impact: users hit a silently-reverted feature with no explanation, mid-incident, when trust matters most |

### SEO (`--seo` — advisory handoff only, no local detector)

SEO audit and generation (meta/OG tags, sitemap.xml, robots.txt, canonical URLs, JSON-LD structured data, llms.txt posture) is canonical in `/ds-compliance` (web scope, WEB-08). `/ds-compliance` present → delegate; absent → gap-note `[seo] not analyzed — requires /ds-compliance --scope=web`, no local fallback generation. SEO copywriting/content-authoring may route through `/ds-docs` when present. `--perf-budget`'s Core Web Vitals bands stay this skill's own: CWV "Good" bands (LCP ≤2.5s, INP <200ms, CLS <0.1) act as a ranking tie-breaker among similar-quality pages, not a primary ranking driver.

### Email Deliverability (`--email` — advisory handoff only, no local detector)

Email authentication and deliverability (SPF + DKIM + DMARC alignment, RFC 8058 one-click unsubscribe, spam-rate posture, BIMI) is canonical in `/ds-compliance`. `/ds-compliance` present → delegate; absent → gap-note `[email-deliverability] not analyzed — requires /ds-compliance`, no local DNS query or record generation. Provider-credential hygiene for transactional sends (API keys, idempotency, opt-out-at-send-time) is `/ds-backend`'s Transactional Messaging scope when that skill is present — distinct from the deliverability/authentication check above.

### Desktop Distribution (conditional — desktop project detected: Electron/Tauri config, `*.xcodeproj` with macOS target, MSIX/WiX manifest)

5 checks (macOS notarization, Windows signing, auto-update integrity, store option fit, changelog + staged rollout): [references/scopes-conditional.md](references/scopes-conditional.md) § Desktop Distribution.

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** the `integrations` signal names it — `Signals: integrations=` contains `google-workspace` or `apple-ecosystem` ([../core/signal-inventory.md](../core/signal-inventory.md)), or the Blueprint Profile's `Integrations:` field states either. Never inferred from a guess. Zero checks when absent from both. Rule table: [references/scopes-conditional.md](references/scopes-conditional.md) § A9 Ecosystem.

## Delegation

**Owns:** store, release, privacy-labels (store-label-correctness only), perf-budget (`--perf-budget` mode) | **Delegates:** ds-compliance → canonical privacy, seo audit + generation (web scope), email-authentication audit; ds-mobile → mobile-specific store compliance | **Receives:** ds-ship → Phase 5 launch pass; ds-productize → store/IAP listing + release execution; ds-release → store submission after the release tag

## Execution Flow

Setup → Detect Current State → Generate → Release Management → [Needs-Approval] → Summary

### Phase 1: Setup

1. A disambiguating flag skips this step. Without one: every mode runs in sequence (the default). `--ask` with no other flag: present the mode menu.
2. **Upstream artifacts:** Profile → `Audience:`, `Deploy:`, Type, Stack. Findings(store, review, privacy-labels, release) → verify + use. Absent → own analysis.
3. Detect platform from project signals (`pubspec.yaml` → mobile, `package.json` → web, Electron/Tauri config or macOS/MSIX packaging manifests → desktop, etc.) + current launch stage: pre-submission, in-review, post-launch. Desktop detected → activate the Desktop Distribution scope.

**Gate:** Platform + mode confirmed. If fails → ambiguous platform → default: All (safest coverage), recorded under `Decided without asking`. `--ask`: prompt iOS / Android / Web / Desktop / All; no mode after menu → re-prompt once then exit with WARN "No mode selected — run /ds-launch with a flag to proceed."

### Phase 2: Detect Current State

Search for store-related configs, version info, existing privacy policy / ToS, CI/CD release workflows; build inventory of what exists vs missing.

**Gate:** Inventory lists each config type (store configs, version info, privacy policy / ToS, CI release workflows) as present or absent. If fails → note what was found as partial; mark missing config type (store configs, version info, privacy policy, CI workflows) as absent rather than unknown; proceed to Phase 3 — missing entries become FAIL findings in review scope.

### Phase 3: Generate [setup, listing, aso, seo, email, privacy, review, submission-notes]

- **Store setup:** platform-specific account setup checklist; certificate / signing key guide (CI automation: authenticate with App Store Connect API keys, not Apple-ID/password auth); TestFlight / Internal Testing steps.
- **Listing metadata:** final store-ready app description (short + long; refine existing `[DRAFT]` descriptions) — template + structure: [references/aso-2026-updates.md](references/aso-2026-updates.md) § Store Listing Voice Guide. Keyword research framework, screenshot size requirements, localization checklist. Additionally: privacy highlight table `| Data Type | Collected (Yes/No) | Shared with 3rd Party (Yes/No) | Purpose |` mapping to Apple Privacy Labels + Google Data Safety; review notes for store review teams (special permission justifications, demo credentials if needed, features requiring network, consumable vs subscription IAP model); screenshot narrative (6 recommended, full journey): auth/onboarding → main list/home → core action → progress/processing → result/output → monetization/settings.
- **ASO mode:** competitor keyword analysis, title/subtitle optimization, category placement recommendation, A/B variant suggestions.
- **SEO mode (web):** advisory handoff to `/ds-compliance --scope=web` (WEB-08) — this skill does not audit or generate SEO artifacts locally. `/ds-compliance` absent → gap-note `[seo] not analyzed — requires /ds-compliance --scope=web`. CWV tie-breaker status is still reported here from the perf budget when one exists.
- **Email mode (sending domain detected):** advisory handoff to `/ds-compliance` — this skill does not query DNS or generate SPF/DKIM/DMARC records locally. `/ds-compliance` absent → gap-note `[email-deliverability] not analyzed — requires /ds-compliance`.
- **Release automation safety ([core principles §8](../core/principles.md)):** any generated release-automation file (Fastlane, `Matchfile`, CI workflow, signing scripts) MUST externalize credentials to env vars. Generate `.env.example` placeholders for: keystore passwords, App Store Connect API keys, Play Console JSON keys, signing identities, OAuth client secrets. Never embed actual values in committed files. Commit message gate: scan `{generated-files}` against the content regexes in [core secret patterns](../core/secret-patterns.md) → no match, plus a high-entropy string review, before suggesting commit.
- **Privacy labels:** scan codebase for data collection → map to Apple/Google categories → generate declaration guide → flag code/label discrepancies.
- **Submission notes (`--submission-notes`):** run pre-submission self-audit (12-item checklist from references/app-store-submission-template.md); block on CRITICAL findings. Auto-detect AI services / auth providers / IAP presence; prompt user for license + hosting per AI service, reviewer-only contact, screen recording URL. Generate per-platform notes (`ds/launch/submission-notes-{apple,google}.txt`) following proactive template; persist `ds/launch/submission-meta.yml` (committed, audit trail). Include "Common Rejection Cookbook" (5 prewritten reply templates for Guidelines 2.1 / 5.1.1(v) / 3.1.1 / 4.8 / 5.1.2 / 5.1.1(i)) so re-submission is one-step.
- **Review preparation (active scan — not just a checklist):** scan project for top rejection triggers; each check produces an evidence-cited PASS/FAIL finding with severity + file:line. Scope checks listed in §Review (Active Detection) above.

**Gate:** All listing, ASO, review artifacts generated. If fails → identify failed artifact (listing metadata, ASO, privacy labels, review scan), record `status: failed`, mark phase `partial`, continue with rest; surface failed artifacts in Phase 6 summary as WARN "manual completion required". Live policy fetch failures (App Store Connect, Play Console) → use fallback values, annotate artifact "(fallback values used — verify before submission)".

### Phase 4: Release Management [release, post-launch]

**Version management:** check current version, suggest bump (patch/minor/major), generate release notes from commits + staged rollout strategy. **Post-launch monitoring:** checklist covering crash-free rate targets, store rating tracking, review response, download monitoring, update cadence, force-update thresholds.

**Marketplace re-verification trigger:** once publicly listed on a marketplace (e.g. Workspace Marketplace), any change to OAuth scopes or redirect URIs starts a new verification cycle — record this permanently in the security/scope-hygiene doc and gate scope/redirect changes as release events; an unreviewed change can get the listing suspended. (XR-125)

**Gate:** Release artifacts generated. If fails → un-generatable release artifact (version bump, release notes, staged rollout, post-launch checklist) → log as `failed`, proceed with successful ones, list failures in summary with "manual action required".

### Phase 5: Needs-Approval Review [--ask, needs_approval > 0]

Without `--ask` this phase does not run — every item was already resolved by best judgment (applied, using the same impact/effort/risk reasoning this review block would show), except items matching the publish/irreversible exception list, which became `skipped (only you can do)`. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → record unresolved as `pending-user-decision`, proceed to Summary with WARN, list prominently.

### Phase 6: Summary

```
ds-launch: {OK|WARN|FAIL} | Platform: {iOS|Android|Web|Desktop|All} | Ready: {n}/{n} checks | Missing: {n} items | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

`Scopes: ran {store, listing, aso, privacy, review, release} · N/A — {platforms=web, no store target} · {seo: ran | N/A — ui≠web} · {email: ran | N/A — no sending domain} · {desktop: ran | N/A — no desktop target} · {a9: ran | N/A — no ecosystem signal}`

Include checklist of remaining items before submission. Disposition accounting — totals balance.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `Store listing + privacy labels generated — submission no longer rejected for missing required fields`
- `App Review Notes pre-filled — reviewer round-trip eliminated (saves 24-48h per round)`
- `{n} ASO keyword candidates with search volume + competition score — listing copy is data-driven, not gut feeling`
- `Perf budget authored at `ds/launch/perf-budget.json` (LCP {x}ms, INP {y}ms, bundle {z}kB) + CI wiring — regressions now block release instead of slipping`

Zero-change run: `Submission package already complete — no missing fields`.

**Gate:** Summary + Effect printed with submission readiness status. If fails → write partial summary: completed phases, generated artifacts (even partial), open CRITICAL/HIGH findings, status FAIL with "Summary incomplete — re-run to complete remaining phases."

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
| Platform ambiguous | Default: All (safest coverage). `--ask`: ask iOS / Android / Web / All. |
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
