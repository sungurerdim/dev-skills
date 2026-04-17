# /ds-mobile

Mobile apps ship with permission abuse, missing accessibility, hardcoded keys, and store-blocking issues that only surface during review. This skill catches them across 145+ rules before you submit.

**Mobile App Quality Audit** — 145+ rules across 13 domains with release readiness scoring. Flutter, SwiftUI, Kotlin/Compose, React Native.

## Triggers

- User runs `/ds-mobile`
- User asks to audit or review a mobile app (Flutter, React Native, iOS, Android)
- User asks about app store compliance, release readiness, or store submission
- Project contains `pubspec.yaml` (Flutter), `react-native` in package.json, `*.xcodeproj`, or Android `build.gradle` with `android {}` block

## Contract

- Every finding cites file path and line number — never fabricate
- Only audits mobile app quality — does not modify non-mobile code
- Platform-specific rules only apply to detected platforms
- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `quick-fix`, `release-ready` |
| `--scope=<domains>` | Comma-separated: security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release, or `all` |
| `--platform=<p>` | Override: `flutter`, `react-native`, `ios`, `android` |
| `--release-ready` | Shorthand for `--mode=release-ready` — runs release-critical domains only |
| `--skip-manual` | Skip manual verification gates (release-ready mode) |
| `--diff` | Compare with previous release readiness report |

No flags → present mode selection.

## Modes

| Mode | Scope | Behavior |
|------|-------|----------|
| `audit` | All selected domains | Scan and report only |
| `audit+fix` | All selected domains | Scan, review findings, then fix |
| `quick-fix` | All selected domains | Scan and auto-fix, minimal review |
| `release-ready` | security, privacy, regulatory, store, release, i18n, a11y | 100-point scoring + manual gates + live policy fetch |

---

## Execution Flow

Detect → Configure → [Architecture Discovery] → Scan → Report → [Fix/Score] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **Project detection.**

| Platform | Detection |
|----------|-----------|
| Flutter | `pubspec.yaml` with `flutter:` section |
| React Native | `package.json` with `react-native` dependency |
| iOS Native | `*.xcodeproj` or `Package.swift` |
| Android Native | `build.gradle` with `android {}` block |
| Cross-platform | Multiple platform indicators |

2. **Platform confirmation.** Ambiguous → ask user.

3. **Findings file check:** `.ds-findings.md` with fresh `git_hash` → read findings matching mobile scopes. Use verified findings to skip redundant analysis. Stale or absent → run own full analysis.

4. **IDU:** Profile → Config.data, Config.deploy, Current Scores, Type+Stack. Findings(mobile scopes) → verify + use. Absent → own analysis.

5. **Mode selection.** Ask user or use flags: Audit Only / Audit & Fix / Quick Fix / Release Ready / Custom.

6. **Scope parsing.** Map selection to domains and mode. Default: `audit` mode, `all` domains.

7. **Custom scope** (only if Custom selected): Ask for domains and mode.

8. **Regulatory framework detection** (when scope includes security, regulatory, store, or all):
   - Auto-detect by searching codebase for framework indicators (GDPR, KVKK, CCPA, LGPD, PIPL, etc.)
   - Confirm detected frameworks with user, or ask which apply
   - Rules tagged `[FRAMEWORK: X,Y]` only checked if at least one framework is active

9. **Release-ready setup** (only if release-ready mode):
   - Detect available platforms (android/ and ios/ directories)
   - If both available, ask which to audit
   - Set report directory: `{project_root}/.mobileaudit/`
   - Load previous reports for diff comparison
   - Fetch live policy data (see references/scoring.md)

**Gate:** Platform identified, mode and scope confirmed, regulatory frameworks resolved.

### Phase 2: Architecture Discovery [SKIP if 1-2 domains]

**When:** Scope includes 3+ domains or `all`.

1. **Detect architecture:** pattern (Clean/MVVM/MVC), auth, state management, navigation, backend, offline, design system, testing, CI/CD, i18n, DI.
2. **Confirm with user.** Present for corrections.
3. **Classify rules:** CAT-1 = universal best practice, existing pattern used incorrectly, bug, security flaw (auto-fixable). CAT-2 = new layer/structure not in current architecture (requires approval). Category depends on architecture — e.g., user has Riverpod → UDF violation is CAT-1; no state management → adding it is CAT-2.
4. **Present ideal scenario.** Show CAT-1 and CAT-2 opportunities. Ask which enhancements to include (default: none).
5. **Finalize scope:** All CAT-1 + only approved CAT-2. Scope is fixed for entire audit.

**Critical rule:** CAT-2 fixes are NEVER applied without user approval.

**Gate:** Architecture confirmed by user, every rule classified as CAT-1 or CAT-2, scope finalized with approved enhancements.

### Phase 3: Rule Loading

Load only reference files matching scope:

| Scope | Reference File |
|-------|---------------|
| security, privacy, regulatory, store | [rules-compliance.md](references/rules-compliance.md) |
| ux, visual, a11y | [rules-experience.md](references/rules-experience.md) |
| arch, testing, perf, network, i18n | [rules-engineering.md](references/rules-engineering.md) |
| release (release-ready mode) | [rules-release.md](references/rules-release.md) |
| release-ready scoring | [scoring.md](references/scoring.md) |

**Gate:** All reference files for in-scope domains loaded successfully; unloadable domains marked N/A.

### Phase 4: Scan

1. **Findings file check:** `.ds-findings.md` with fresh `git_hash` → read findings matching scopes. Verify each (re-read file:line), skip verified; run full for uncovered.

**Large scope (3+ domains):** Progress checklist + append findings to `.ds-findings.md` after each domain. Max 2 parallel scans.

**Per domain:** Search files → search for violations → read context to verify → skip unverifiable rules.

**Confidence:** HIGH = pattern + context verified; MEDIUM = pattern, ambiguous context; LOW = heuristic.

**False positive prevention:** Never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Category assignment:** CAT-1: always report. CAT-2: only if in approved enhancements.

**Recovery (context lost):** Progress checklist → read `.ds-findings.md` → resume from first incomplete domain. Never re-scan completed domains.

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence.

### Phase 5: Report

#### Standard Report (audit modes)

```
## Audit Report — [project_name]
Platform: [platform] | Scanned: [domains] | Date: [today]
Architecture: [summary]

### Conformance Issues (CAT-1)
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Enhancement Opportunities (CAT-2) — pre-approved
| # | Rule | Sev | File:Line | Issue | Impact | Fix | Conf |

### Potential Issues (LOW confidence)
| # | Rule | File:Line | Issue | Suggested Fix |

### Summary
| Category | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. Uncertain → choose lower.

#### Release Readiness Report (release-ready mode)

Per references/scoring.md: 100-point dynamic scoring across 7 dimensions, manual gates, consequence table, diff against previous report.

Include: policy values used (fetched vs fallback), dimension breakdown with bar chart, findings by severity, manual gate status, and "if you publish now" consequence table for CRITICAL+HIGH.

**Gate:** Report presented to user with all findings, severities, and summary table.

### Phase 6: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Pick by severity / Report only |
| `audit+fix` | Auto-transition to fix phase |
| `quick-fix` | Auto-transition, auto-apply all |
| `release-ready` | Ask: Fix plan / Save report only / Guidance for key findings |

**Gate:** User selected post-report action; mode-specific next step determined.

### Phase 7: Fix [SKIP if audit-only or report-only]

1. **Plan.** Read findings, apply severity filter, group by file, identify dependencies. Present: CAT-1 (auto-fixable) and CAT-2 (pre-approved).
2. **Confirmation:** `quick-fix` → summary + proceed; `audit+fix` → full plan + ask; `release-ready` → show auto-fixable vs guidance split.
3. **Execute.** Apply grouped by file. Re-read before and after each edit. Record applied/failed/skipped.

**Gate:** All standard fixes attempted; each recorded as applied, failed, or skipped.

### Phase 8: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 9: Summary

```
ds-mobile: {OK|WARN|FAIL} | Mode: {audit|audit+fix|quick-fix|release-ready} | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Cleanup:** Remove only mobile-scoped findings (security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release) from `.ds-findings.md`. If file becomes empty after removal (no findings from other scopes remain), delete file entirely.

FRC+DSC accounting.

**Gate:** Fixed + failed + skipped + needs_approval + not_applicable = total findings; every modified file re-read and verified; mobile-scoped findings removed from `.ds-findings.md`.

## Quality Gates

1. **No cascading breakage** — after fixes, verify no broken imports/references
2. **Format preservation** — fixes match existing indentation and code style
3. **Scope boundary** — only touch lines task requires
4. **Platform consistency** — fixes use correct platform API
5. **Artifact-first recovery** — re-read files before and after editing
6. **Every finding gets a disposition in summary — zero silent drops (FRC)**
7. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Platform detection fails | Ask user to specify platform manually |
| Reference file fails to load | Skip affected domain, mark findings as N/A |
| Fix breaks another file | Revert fix, flag as failed, continue with next finding |
| Context lost mid-audit (large scope) | Resume from progress checklist + `.ds-findings.md` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No project file found | Stop: "Mobile project not found in current directory." |
| Platform ambiguous | Ask user to confirm |
| Reference file fails to load | Skip domain, note as N/A |
| Architecture Discovery: no corrections | Use detected values |
| CAT-2 list: user selects 'none' | Audit CAT-1 rules only (default) |
| Zero findings in domain | Report domain as clean |
| Fix: file changed externally | Re-read before each edit |
| Fix: edit fails | Skip, log as failed, continue |
| Regulatory: no active frameworks | Skip PRV-06–18 regulatory rules |
| Release-ready: policy fetch fails | Use fallback values, warn in report |
| Release-ready: first run | No diff, note "First audit" |
| Release-ready: corrupt JSON report | Rename .corrupt, warn, skip diff |
