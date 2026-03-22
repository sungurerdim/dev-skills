# /ds-launch

**Store & Release Management** — Store submission, listing optimization, release strategy, and post-launch monitoring.

## Triggers

- User runs `/ds-launch`
- User asks to submit to app store, prepare for launch, or manage releases
- User asks about store listing, screenshots, privacy labels, or release notes
- User asks "how do I publish my app" or "prepare for App Store"

## Contract

- Covers store account setup, listing metadata, review preparation, release management
- Fully functional standalone. Uses `.findings.md` for optimization when available
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
| Description | Short/long description, feature highlights, formatting |
| Keywords | Keyword research, competitor analysis, localization |
| Screenshots | Required sizes per device, layout guidance, A/B testing |
| Icon | Platform requirements, design guidelines |
| Category | Primary/secondary category selection |
| Age rating | Rating questionnaire guidance |

### ASO Scope

| Check | What It Covers |
|-------|---------------|
| Keyword research | Competitor keyword analysis, search volume estimation, keyword difficulty |
| Title optimization | Primary keyword in title, character limit compliance, localized titles |
| Subtitle/short description | Secondary keywords, value proposition, character limits |
| Category selection | Primary vs secondary category, competition density analysis |
| Search ranking factors | Download velocity, ratings, update frequency, engagement signals |
| A/B test recommendations | Title variants, screenshot order, icon alternatives |

### Privacy Scope

| Platform | What It Covers |
|----------|---------------|
| Apple Privacy Labels | Nutrition label declarations, data types, tracking status |
| Google Data Safety | Data safety section, ephemeral data, deletion support |
| Web privacy | Cookie consent, privacy policy, GDPR/CCPA compliance |

### Review Scope

| Check | What It Covers |
|-------|---------------|
| Common rejections | Missing privacy policy, crash on launch, incomplete metadata |
| Platform rules | App Store Review Guidelines, Play Store policies |
| Content compliance | Age-appropriate content, restricted categories |
| Technical | 64-bit support, permissions usage, background modes |
| ATT & Privacy Manifests | App Tracking Transparency prompt, SDK PrivacyInfo.xcprivacy validation |
| Age compliance | Declared Age Range API (iOS), Play Age Signals API (Android), COPPA if applicable |
| Data deletion | In-app account deletion mechanism required by both stores |
| Review timing | Apple: 24-48h typical. Google: 1-7 days (first app longer) |

### Release Scope

| Element | What It Covers |
|---------|---------------|
| Versioning | Semantic versioning, build number management |
| Release notes | User-facing changelog, localization |
| Staged rollout | Google Play: 1% → 5% → 20% → 50% → 100% (manual). Apple: 7-day phased 1% → 2% → 5% → 10% → 20% → 50% → 100% (can pause) |
| Force update | Minimum version enforcement, update UX |
| Rollback | Emergency rollback procedure |

## Execution Flow

Setup → Detect → Analyze → Generate → Verify → Summary

### Phase 1: Setup

**Goal:** Determine platform and launch stage.

1. If flags provided, proceed directly
2. If no flags, present interactive menu
3. Detect platform from project signals (pubspec.yaml → mobile, package.json → web, etc.)
4. Detect current launch stage: pre-submission, in-review, post-launch

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
1. Generate app description template (short + long) with placeholder structure
2. Generate keyword research framework
3. Generate screenshot size requirements per platform
4. Generate localization checklist

**ASO mode:**
1. Analyze competitor keywords, optimize title/subtitle for search ranking
2. Recommend category placement based on competition density
3. Suggest A/B test variants for title, screenshots, and icon

**Privacy labels:**
1. Scan codebase for data collection patterns (analytics, auth, storage, networking)
2. Map detected patterns to Apple/Google privacy label categories
3. Generate privacy label declaration guide with your app's specific data types
4. Flag discrepancies between code behavior and declared privacy labels

**Review preparation:**
1. Run pre-review checklist:
   - Privacy policy URL accessible?
   - All required metadata filled?
   - App does not crash on cold start?
   - Permissions have usage descriptions?
   - No references to other platforms ("available on Android" in iOS listing)?
2. Flag common rejection reasons for the detected platform

**Gate:** All requested artifacts generated.

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

### Phase 5: Summary

```
ds-launch: {OK|WARN|FAIL} | Platform: {iOS|Android|Web|All} | Ready: N/N checks | Missing: N items
```

Include checklist of remaining items before submission.

## Quality Gates

- Every store listing element meets platform character limits
- Privacy labels match actual code behavior (verified by codebase scan)
- Pre-review checklist has zero CRITICAL items
- Version numbers are valid semver with incrementing build numbers
- Release notes are user-friendly (not developer jargon)

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
