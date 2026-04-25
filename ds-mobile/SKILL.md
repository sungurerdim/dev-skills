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
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
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
| `--resume` | Resume from `ds/audit/mobile.json` without prompting |
| `--clean` | Delete existing state and start fresh |

No flags → present mode selection.

## Modes

| Mode | Scope | Behavior |
|------|-------|----------|
| `audit` | All selected domains | Scan and report only |
| `audit+fix` | All selected domains | Scan, review findings, then fix |
| `quick-fix` | All selected domains | Scan and auto-fix, minimal review |
| `release-ready` | security, privacy, regulatory, store, release, i18n, a11y | 100-point scoring + manual gates + live policy fetch |

---

## Delegation

**Owns:** mobile-security, mobile-privacy, mobile-regulatory, mobile-ux, mobile-store, mobile-permissions, mobile-release, mobile-visual | **Delegates:** none (authoritative for mobile projects) | **Receives:** ds-compliance → security / privacy / regulatory on mobile projects

## Execution Flow

Detect → Configure → [Architecture Discovery] → Scan → Report → [Fix/Score] → [Needs-Approval] → Summary

### Phase 1: Detect

**Recovery check:** DETECT `ds/audit/mobile.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files referenced by pending findings, discard stale ones), skip `done` phases, announce `[MOB] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

**State `data` shape:** `{ platform, mode, scopes_selected, scopes_done[], frameworks_detected[], findings[{id, severity, file, line, scope, disposition}], fix_progress, release_ready_score }`.

1. **Project detection.**

| Platform | Detection |
|----------|-----------|
| Flutter | `pubspec.yaml` with `flutter:` section |
| React Native | `package.json` with `react-native` dependency |
| iOS Native | `*.xcodeproj` or `Package.swift` |
| Android Native | `build.gradle` with `android {}` block |
| Cross-platform | Multiple platform indicators |

2. **Platform confirmation.** Ambiguous → ask user.

3. **Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → read findings matching mobile scopes. Use verified findings to skip redundant analysis. Stale or absent → run own full analysis.

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
   - Release report path: `ds/mobile/release.json` (single file, committed, overwritten each run — `ds/<skill>/` user-facing operational namespace)
   - For `--diff`: read the previous content of `ds/mobile/release.json` before overwriting, compute diff in memory, present in chat. Trend over >1 run → `git log -- ds/mobile/release.json` is authoritative — never a persistent directory of stale per-run reports.
   - Fetch live policy data (see references/scoring.md)

**Gate:** Platform identified, mode and scope confirmed, regulatory frameworks resolved. If fails → if platform cannot be auto-detected, prompt user to select from Flutter / React Native / iOS / Android / Cross-platform and record in `state.data.platform`; if mode or scope is not confirmed after prompting, default to `audit` mode with `all` domains and warn the user; if regulatory framework detection is ambiguous, ask the user to confirm which frameworks apply before proceeding.

### Phase 2: Architecture Discovery [SKIP if 1-2 domains]

**When:** Scope includes 3+ domains or `all`.

1. **Detect architecture:** pattern (Clean/MVVM/MVC), auth, state management, navigation, backend, offline, design system, testing, CI/CD, i18n, DI.
2. **Confirm with user.** Present for corrections.
3. **Classify rules:** CAT-1 = universal best practice, existing pattern used incorrectly, bug, security flaw (auto-fixable). CAT-2 = new layer/structure not in current architecture (requires approval). Category depends on architecture — e.g., user has Riverpod → UDF violation is CAT-1; no state management → adding it is CAT-2.
4. **Present ideal scenario.** Show CAT-1 and CAT-2 opportunities. Ask which enhancements to include (default: none).
5. **Finalize scope:** All CAT-1 + only approved CAT-2. Scope is fixed for entire audit.

**Critical rule:** CAT-2 fixes are NEVER applied without user approval.

**Gate:** Architecture confirmed by user, every rule classified as CAT-1 or CAT-2, scope finalized with approved enhancements. If fails → if the user provides no corrections and no enhancement selections within one re-prompt, treat the auto-detected architecture as confirmed, classify all unclassified rules as CAT-1, include zero CAT-2 enhancements, record this in `state.data.frameworks_detected`, and proceed to Phase 3 with a note that architecture was auto-confirmed.

### Phase 3: Rule Loading

Load only reference files matching scope:

| Scope | Reference File |
|-------|---------------|
| security, privacy, regulatory, store | [rules-compliance.md](references/rules-compliance.md) |
| ux, visual, a11y | [rules-experience.md](references/rules-experience.md) |
| arch, testing, perf, network, i18n | [rules-engineering.md](references/rules-engineering.md) |
| release (release-ready mode) | [rules-release.md](references/rules-release.md) |
| release-ready scoring | [scoring.md](references/scoring.md) |

**Gate:** All reference files for in-scope domains loaded successfully; unloadable domains marked N/A. If fails → for any reference file that cannot be loaded, mark its domains as N/A in `state.data.scopes_done` with reason "reference file unavailable", skip those domains in Phase 4, and surface them in the Phase 9 summary as "domains skipped: {list} — reference files not found".

### Phase 4: Scan

1. **Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → read findings matching scopes. Verify each (re-read file:line), skip verified; run full for uncovered.

**Large scope (3+ domains):** Progress checklist + append findings to `ds/audit/findings.md` after each domain. Max 2 parallel scans.

**Per domain:** Search files → search for violations → read context to verify → skip unverifiable rules.

**arch scope mandatory checks ([references/principles.md §2](references/principles.md)):** Evaluate widget / screen / view-model / repository layers against SOLID — SRP (widget changes for >1 reason: UI + state + I/O), OCP, LSP (subtype violates parent navigation contract), ISP (consumer forced to implement unused lifecycle hooks), DIP (UI imports concrete platform-channel instead of abstraction). GRASP — Information Expert, Low Coupling (>7 unrelated peer imports), High Cohesion. Cite principle by name.

**network + perf scope reliability checks ([references/principles.md §4](references/principles.md)):** Flag missing — timeout on every API call, retry-with-exponential-backoff on transient failures, offline / slow-network graceful degradation, app-lifecycle handlers (background → foreground state restoration), idempotency keys on payment / order / write endpoints, structured logging that survives across app restart, fail-fast input validation at every system boundary (deep links, push notifications, intent extras).

**Confidence:** HIGH = pattern + context verified; MEDIUM = pattern, ambiguous context; LOW = heuristic.

**False positive prevention:** Never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Category assignment:** CAT-1: always report. CAT-2: only if in approved enhancements.

**Recovery (context lost):** Progress checklist → read `ds/audit/findings.md` → resume from first incomplete domain. Never re-scan completed domains.

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence. If fails → re-read the progress checklist and `ds/audit/findings.md` to identify the last completed domain; resume scanning from the first incomplete domain without re-scanning completed ones; if a specific domain scan fails after retry (file unreadable, context lost), mark that domain as `partial` in `state.data.scopes_done` with the findings collected so far and continue to the next domain.

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

**Gate:** Report presented to user with all findings, severities, and summary table. If fails → if any domain produced no findings due to a scan error (not because it was clean), re-run the scan for that domain once; if it still fails, present the report with the failed domains clearly marked as "scan incomplete" and their findings count as "?" in the summary table.

### Phase 6: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Pick by severity / Report only |
| `audit+fix` | Auto-transition to fix phase |
| `quick-fix` | Auto-transition, auto-apply all |
| `release-ready` | Ask: Fix plan / Save report only / Guidance for key findings |

**Gate:** User selected post-report action; mode-specific next step determined. If fails → if the user provides no selection after one re-prompt, apply the mode default: `audit` → Report only; `audit+fix` → Fix all; `quick-fix` → Auto-apply all; `release-ready` → Save report only. Record the defaulted action in `state.data.fix_progress` and proceed.

### Phase 7: Fix [SKIP if audit-only or report-only]

1. **Plan.** Read findings, apply severity filter, group by file, identify dependencies. Present: CAT-1 (auto-fixable) and CAT-2 (pre-approved).
2. **Confirmation:** `quick-fix` → summary + proceed; `audit+fix` → full plan + ask; `release-ready` → show auto-fixable vs guidance split.
3. **Execute.** Apply grouped by file. Re-read before and after each edit. Record applied/failed/skipped.

**Gate:** All standard fixes attempted; each recorded as applied, failed, or skipped. If fails → for any finding where the fix could not be attempted (file unreadable, edit error), record it as `failed` in `state.data.findings[].disposition`, revert any partial edit via re-read and restore, continue with the next finding, and list all failed fixes in the Phase 9 summary with the reason.

### Phase 8: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → record the unresolved item in `state.data.findings[].disposition` as `pending-user-decision`, proceed to Summary with status WARN, and list all unresolved needs_approval items prominently so the user can address them outside this session.

### Phase 9: Summary

```
ds-mobile: {OK|WARN|FAIL} | Mode: {audit|audit+fix|quick-fix|release-ready} | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Cleanup:** Remove only mobile-scoped findings (security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release) from `ds/audit/findings.md`. If file becomes empty after removal (no findings from other scopes remain), delete file entirely.

FRC+DSC accounting.

**Gate:** Fixed + failed + skipped + needs_approval + not_applicable = total findings; every modified file re-read and verified; mobile-scoped findings removed from `ds/audit/findings.md`. If fails → if the counts do not reconcile, identify which finding lacks a disposition, assign it `failed` with reason "disposition not recorded", re-run the summary count; if `ds/audit/findings.md` cleanup fails, warn the user and leave the file intact rather than partially modifying it.

## Quality Gates

1. **No cascading breakage** — after fixes, verify no broken imports/references
2. **Format preservation** — fixes match existing indentation and code style
3. **Scope boundary** — only touch lines task requires
4. **Platform consistency** — fixes use correct platform API
5. **Artifact-first recovery** — re-read files before and after editing
6. **Every finding gets a disposition in summary — zero silent drops (FRC)**
7. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/mobile.json` updated per scope, gitignored, deleted on successful Summary.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Platform detection fails | Ask user to specify platform manually |
| Reference file fails to load | Skip affected domain, mark findings as N/A |
| Fix breaks another file | Revert fix, flag as failed, continue with next finding |
| Context lost mid-audit (large scope) | Resume from progress checklist + `ds/audit/findings.md` |

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
| Release-ready: first run | No previous `ds/mobile/release.json` → no diff, note "First audit" |
| Release-ready: corrupt JSON report | Warn, treat as first audit (skip diff), overwrite with current run |
