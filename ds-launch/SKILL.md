# /ds-launch

~40% of iOS submissions get delayed or rejected for preventable errors. This skill scans your project and flags them before you submit.

**Store & Release Management** — Store submission, listing optimization, release strategy, and post-launch monitoring.

## Triggers

- User runs `/ds-launch`
- User asks to submit to app store, prepare for launch, or manage releases
- User asks about store listing, screenshots, privacy labels, or release notes
- User asks "how do I publish my app" or "prepare for App Store"

## Contract

- Covers store account setup, listing metadata, review preparation, release management
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- FRC+DSC enforced.
- Generates checklists and metadata — does NOT submit to stores directly
- **Minimal liability:** generates store-compliant metadata, flags common rejection reasons
- **Maximum privacy:** privacy label generation with minimal data collection focus
- **Maximum automation:** version management, release notes generation, staged rollout

## Arguments

| Flag | Effect |
|------|--------|
| `--setup` | Store account setup checklists and initial configuration |
| `--listing` | Store listing metadata: description, keywords, screenshots |
| `--privacy` | Privacy label and data safety declarations |
| `--review` | Pre-review checklist: common rejection prevention |
| `--aso` | App Store Optimization — keyword research and search ranking |
| `--release` | Release management: version, notes, staged rollout |
| `--post-launch` | Post-launch monitoring checklist |
| `--auto` | All modes, no questions, single-line summary |

Without flags: present interactive mode selection (setup, listing, aso, privacy, review, release, post-launch).

## Scopes

### Store Setup Scope

Verify store account setup is complete. Check: developer account active, app ID registered, signing configured.

### Listing Scope

| Element | What It Covers |
|---------|---------------|
| App name | Character limits, keyword inclusion, localization |
| Description | Short/long description with pain-first opening sentence — see voice guide in [references/aso-2026-updates.md](references/aso-2026-updates.md). First line must state the problem solved or the outcome delivered — never open with a feature list. Benefit-driven highlights, not feature highlights |
| Keywords | Keyword research, competitor analysis, localization |
| Screenshots | First 3 screenshots decide the install — must follow problem → solution → delight narrative. Text overlay captions with benefit-driven copy (captions now index in Apple search as of June 2025). Platform-specific: do not reuse iOS screenshots on Play. Required sizes per device, layout guidance, A/B testing |
| Video preview | Portrait video: +7% watch time, +5% conversion vs landscape (Google Play). 15-30 seconds, no audio dependency, demonstrate core value proposition |
| Icon | Platform requirements, design guidelines |
| Category | Primary/secondary category selection |
| Age rating | Rating questionnaire guidance |

### ASO Scope

| Check | What It Covers |
|-------|---------------|
| Keyword research | Competitor keyword analysis, search volume estimation, keyword difficulty |
| Title optimization | Primary keyword in title, character limit compliance, localized titles |
| Subtitle/short description | Secondary keywords, value proposition, character limits |
| Screenshot caption indexing | Apple (June 2025): text overlays on screenshots now index in search. Captions must contain target keywords with benefit-driven copy. See screenshot narrative in [references/aso-2026-updates.md](references/aso-2026-updates.md) |
| Custom Product Pages | Apple: 70 CPPs per app (expanded from 35), each keyword-linkable for organic search. Create CPPs for different audience segments and keyword clusters |
| Category selection | Primary vs secondary category, competition density analysis |
| Search ranking factors | Both stores shifting from keyword-matching to intent-driven semantic discovery. Apple: download velocity, ratings, update frequency, engagement signals. Google Play: engagement/retention signals outweigh raw downloads (2:1 redownload ratio), battery optimization as core vital (5% threshold — non-compliant apps excluded from discovery, March 2026) |
| A/B test recommendations | Title variants, screenshot order, icon alternatives. Google Play: portrait video variants. Apple PPO: up to 3 treatment variants |

### Privacy Scope

| Platform | What It Covers |
|----------|---------------|
| Apple Privacy Labels | Nutrition label declarations, data types, tracking status |
| Google Data Safety | Data safety section, ephemeral data, deletion support |
| Web privacy | Cookie consent, privacy policy, GDPR/CCPA compliance |

### Review Scope (Active Detection)

Each check scans the codebase and produces PASS/FAIL with severity and file:line references — not a manual checklist.

| Check | Detection Method | Severity |
|-------|-----------------|----------|
| Privacy policy | Scan configs + metadata for URL, verify HTTP 200 | CRITICAL |
| Metadata completeness | Scan store metadata dirs for empty/placeholder content | CRITICAL |
| Permission descriptions | Parse Info.plist / AndroidManifest.xml for missing descriptions | HIGH |
| Privacy manifests & SDK compliance | Scan for PrivacyInfo.xcprivacy, flag SDKs without manifests | HIGH |
| AI data consent | Check for consent modal if external AI services detected | HIGH |
| Data deletion | Search for account deletion UI flow | HIGH |
| Platform cross-references | Search listing text for competing platform mentions | MEDIUM |
| Crash-prone patterns | Scan entry points for force-unwraps, unhandled exceptions | MEDIUM |
| Age rating | Verify age questionnaire completeness, new 13+/16+/18+ tiers | MEDIUM |
| SDK & build requirements | Check minimum SDK version (iOS 26 SDK required from April 2026) | MEDIUM |
| ATT & Privacy Manifests | App Tracking Transparency prompt, SDK PrivacyInfo.xcprivacy validation | HIGH |
| Review timing | Apple: 24-48h typical. Google: 1-7 days (first app longer) | INFO |

### Release Scope

| Element | What It Covers |
|---------|---------------|
| Versioning | Semantic versioning, build number management |
| Release notes | User-facing changelog, localization |
| Staged rollout | Google Play: 1% → 5% → 20% → 50% → 100% (manual). Apple: 7-day phased 1% → 2% → 5% → 10% → 20% → 50% → 100% (can pause) |
| Force update | Minimum version enforcement, update UX |
| Rollback | Emergency rollback procedure |

## Execution Flow

Setup → Detect → Analyze → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**Goal:** Determine platform and launch stage.

1. If flags provided, proceed directly
2. If no flags, present interactive menu
3. **IDU:** Profile → Config.audience, Config.deploy, Type, Stack. Findings(store, review, privacy-labels, release) → verify + use. Absent → own analysis.
4. Detect platform from project signals (pubspec.yaml → mobile, package.json → web, etc.)
5. Detect current launch stage: pre-submission, in-review, post-launch

**Gate:** Platform and mode confirmed.

### Phase 2: Detect Current State

**Goal:** Understand what's already prepared.

1. Search for store-related configs (fastlane, metadata directories, screenshots)
2. Check version information in project config files
3. Search for existing privacy policy, terms of service
4. Check for CI/CD release workflows
5. Build inventory of what exists vs what's missing

**Gate:** Inventory complete.

### Phase 3: Generate [setup, listing, aso, privacy, review]

**Goal:** Create store preparation artifacts.

**Store setup:**
1. Generate platform-specific account setup checklist
2. Generate certificate/signing key management guide
3. Generate TestFlight/Internal Testing setup steps

**Listing metadata:**
1. Generate final store-ready app description (short + long). If ds-market draft descriptions exist (files marked `[DRAFT — finalize with ds-launch --listing]`), use them as the starting point — refine, verify character limits, and produce the final versions. If no drafts exist, generate from scratch.
2. Generate keyword research framework
3. Generate screenshot size requirements per platform
4. Generate localization checklist

**Listing template structure:**
- **Short description** (80 chars max) per supported language — per-locale keyword optimization, not literal translation
- **Full description** with consistent section structure across all languages:
  - How it works (3-5 steps)
  - Key features (bullet list, benefit-first phrasing: "Get X" not "Has X")
  - Privacy/security highlights (if applicable to app category)
  - Pricing/plans (if applicable)
- **Privacy highlight table** (maps directly to Apple Privacy Labels + Google Data Safety):

  | Data Type | Collected | Shared with 3rd Party | Purpose |
  |-----------|-----------|----------------------|---------|
  | {type} | Yes/No | Yes/No | {purpose} |

- **Review notes** for store review teams: special permission justifications, demo account credentials (if needed), features requiring network, consumable vs subscription IAP model
- **Screenshot narrative** (6 recommended screens covering the full user journey): auth/onboarding → main list/home → core action → progress/processing → result/output → monetization/settings

**ASO mode:**
1. Analyze competitor keywords, optimize title/subtitle for search ranking
2. Recommend category placement based on competition density
3. Suggest A/B test variants for title, screenshots, and icon

**Privacy labels:**
1. Scan codebase for data collection patterns (analytics, auth, storage, networking)
2. Map detected patterns to Apple/Google privacy label categories
3. Generate privacy label declaration guide with your app's specific data types
4. Flag discrepancies between code behavior and declared privacy labels

**Review preparation (active scan — not just a checklist):**

Scan the project for the top rejection triggers. Each check produces PASS/FAIL with file:line references.

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, read findings matching scopes (store, review, privacy-labels, release). For each match: verify still valid (re-read file:line), skip own analysis for verified scopes. For uncovered scopes, run full analysis.
2. **Privacy policy [CRITICAL]:** Search for privacy policy URL in project config, metadata files, and store listing drafts. Verify URL is accessible (HTTP 200). If missing → FAIL with "Missing privacy policy URL — will cause rejection."
3. **Metadata completeness [CRITICAL]:** Scan store metadata directories (fastlane/metadata, app store connect export, Play Console drafts). Flag: empty description, missing screenshots, placeholder text ("Lorem ipsum", "TODO", "Coming soon"). Guideline 2.1 (App Completeness) accounts for 40%+ of unresolved rejections.
4. **Permission descriptions [HIGH]:** Scan `Info.plist` (iOS) for `NS*UsageDescription` keys, `AndroidManifest.xml` for permissions. Every permission must have a user-facing description. Missing → FAIL.
5. **Privacy manifest & SDK compliance [HIGH]:** Scan for `PrivacyInfo.xcprivacy` (iOS). Verify all third-party SDKs have privacy manifests. Flag SDKs that track users without disclosure.
6. **Platform cross-references [MEDIUM]:** Search store listing text for references to other platforms ("available on Android" in iOS listing, "App Store" in Play listing). Flag as rejection risk.
7. **Crash-prone patterns [MEDIUM]:** Scan for force-unwraps (Swift `!`), unhandled exceptions at app entry, missing null checks on launch-critical paths. Flag as "Performance — crash on launch review risk."
8. **AI data consent [HIGH — new 2025]:** If app uses external AI services, check for consent modal implementation. Apple requires provider name + data types disclosure before personal data sharing.
9. **Age rating compliance [MEDIUM]:** Check if age rating questionnaire is complete. New 13+/16+/18+ tiers (July 2025). Deadline: January 31, 2026 for updated questionnaire.
10. **Data deletion [HIGH]:** Search for account deletion UI flow. Both stores require in-app account deletion mechanism. Missing → FAIL.
11. **SDK & build requirements [MEDIUM]:** Check minimum SDK version. Starting April 2026: all iOS submissions must use iOS 26 SDK.

**Gate:** All listing, ASO, and review artifacts generated.

### Phase 4: Release Management [release, post-launch]

**Goal:** Manage version and release.

**Version management:**
1. Check current version in project config
2. Suggest version bump based on changes (patch/minor/major)
3. Generate release notes from commit history since last release
4. Generate staged rollout strategy (1% → 5% → 20% → 50% → 100%)

**Post-launch monitoring:**
Generate post-launch monitoring checklist: crash-free rate targets, store rating tracking, review response process, download monitoring, update cadence, and force-update threshold recommendations.

**Gate:** Release artifacts generated.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 6: Summary

```
ds-launch: {OK|WARN|FAIL} | Platform: {iOS|Android|Web|All} | Ready: N/N checks | Missing: N items | Fixed: N | Skipped: N | Failed: N | Total: N
```

Include checklist of remaining items before submission.

FRC+DSC accounting.

**Gate:** Summary printed with submission readiness status.

## Quality Gates

- Every store listing element meets platform character limits
- Privacy labels match actual code behavior (verified by codebase scan)
- Pre-review checklist has zero CRITICAL items
- Version numbers are valid semver with incrementing build numbers
- Release notes are user-friendly (not developer jargon)
- Every finding gets a disposition in the summary — zero silent drops (FRC)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

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
| CRITICAL | Will cause store rejection: missing privacy policy, crash, policy violation |
| HIGH | Likely rejection: incomplete metadata, permission without description |
| MEDIUM | Quality issue: poor screenshots, weak description, missing keywords |
| LOW | Optimization: A/B test opportunity, localization gap |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Web-only app (no store) | Focus on domain, hosting, SEO meta tags, PWA manifest |
| First-ever submission | Start from account setup, include all beginner steps |
| Update to existing app | Skip setup, focus on release notes and rollout |
| Multi-platform | Generate per-platform checklists, note shared vs platform-specific items |
| Enterprise/internal distribution | Skip public store, focus on MDM/enterprise distribution |
