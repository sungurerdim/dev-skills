---
name: ds-mobile
description: Mobile app quality audit — 174 rules across 13 domains with release-readiness scoring (Flutter, SwiftUI, Kotlin/Compose, React Native). Use when auditing a mobile app for quality or release readiness.
---

# /ds-mobile

Mobile apps ship with permission abuse, missing accessibility, hardcoded keys, and store-blocking issues that only surface during review. This skill catches them across 174 rules before you submit.

**Mobile App Quality Audit** — 174 rules across 13 domains with release readiness scoring. Flutter, SwiftUI, Kotlin/Compose, React Native.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-mobile`
- User asks to audit or review a mobile app (Flutter, React Native, iOS, Android)
- User asks about app store compliance, release readiness, or store submission
- Project contains `pubspec.yaml` (Flutter), `react-native` in `package.json`, `*.xcodeproj`, or Android `build.gradle` with `android {}` block

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "Flutter / iOS / Android / React-Native app audit" | "audit backend API" (→ ds-backend) |
| "mobile permissions audit", "release readiness for App Store" | "web-app privacy compliance" (→ ds-compliance --privacy) |
| "mobile UX (gestures, store presence, jank)" | "design system / token audit (cross-platform)" (→ ds-frontend) |
| "mobile-specific store rejection prevention" | "App Store submission metadata" (→ ds-launch) |

## Contract

**Dimensions:** A7 (implementation, mobile), A9 (conditional ecosystem rules), C1 (mobile-security)

- Audits mobile app quality; every finding cites file:line — never fabricates. Only touches mobile code; platform rules only on detected platforms.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- State-exempt: audit is regenerable from source; applied fixes land in the working tree — git is the durable record.
- FRC+DSC enforced. Detected pre-existing / out-of-scope errors get a concrete disposition (W11), fixed inline or escalated with a concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `quick-fix`, `release-ready` |
| `--scope={list}` | security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release, or `all` |
| `--platform={p}` | Override: `flutter`, `react-native`, `ios`, `android` |
| `--release-ready` | Shorthand for `--mode=release-ready` |
| `--skip-manual` | Skip manual gates (release-ready) |
| `--diff` | Compare with previous release report |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

No flags → present mode selection.

## Modes

| Mode | Scope | Behavior |
|------|-------|----------|
| `audit` | All selected | Scan and report only |
| `audit+fix` | All selected | Scan, review, fix |
| `quick-fix` | All selected | Scan + auto-fix, minimal review |
| `release-ready` | security, privacy, regulatory, store, release, i18n, a11y | 100-point scoring + manual gates + live policy fetch |

## Delegation

**Owns:** mobile-security, mobile-privacy, mobile-regulatory, mobile-ux, mobile-store, mobile-permissions, mobile-release, mobile-visual | **Delegates:** none (authoritative for mobile projects) | **Receives:** ds-compliance → security / privacy / regulatory on mobile projects; ds-launch → mobile-specific store compliance; ds-ship → Phase 2 stack-specific delegation

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Scope |
|----------|------|-------|
| Apple | Guideline 4.8 "Login Services" — third-party/social login as primary auth requires an equivalent privacy-preserving option (Sign in with Apple satisfies it; 5 exemptions incl. own-account-system-only) | security, store |
| Apple | Entitlements correctness — `com.apple.developer.applesignin`, push, iCloud, in-app-purchase | security |
| Google | `google-services.json` hygiene — no committed dev keys, correct package name, version match | security |

## Execution Flow

Detect → Configure → [Architecture Discovery] → Scan → Report → [Fix/Score] → [Needs-Approval] → Summary

### Phase 1: Detect

1. **Project detection.**

   | Platform | Detection |
   |----------|-----------|
   | Flutter | `pubspec.yaml` with `flutter:` |
   | React Native | `package.json` dep `react-native` |
   | iOS Native | `*.xcodeproj` or `Package.swift` |
   | Android Native | `build.gradle` with `android {}` |
   | Cross-platform | Multiple platform indicators |

2. **Platform confirmation.** Ambiguous → ask user. **Under `--auto`:** best-judgment default — `Cross-platform` when multiple indicators are present, else the single detected platform; never blocks.
3. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → read findings matching mobile scopes, skip redundant analysis. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
4. **IDU:** Profile → Config.data, Config.deploy, Current Scores, Type+Stack. Findings(mobile scopes) → verify + use. Absent → own analysis.
5. **Mode selection.** No flag → present a menu covering every mode, each with a one-line what-it-does: Audit (recommended) — scan + report, no changes / Audit & Fix — scan + review + fix / Quick Fix — scan + auto-fix, minimal review / Release Ready — 100-point scoring + manual gates / Custom — pick scopes / (Cancel). A disambiguating flag (e.g. `--mode`, `--release-ready`) skips the menu. `--auto` alone also skips the menu — defaults to `audit+fix` (scan, review, fix — the most complete unattended default) unless `--release-ready` is also passed.
6. **Scope parsing.** Default: `audit` mode, all domains.
7. **Custom scope** (if Custom): ask for domains + mode.
8. **Regulatory framework detection** (security/regulatory/store/all):
   - Auto-detect framework indicators (GDPR, KVKK, CCPA, LGPD, PIPL, etc.)
   - Confirm with user. **Under `--auto`:** skip the confirmation — use every detected framework indicator as-is.
   - Rules tagged `[FRAMEWORK: X,Y]` only checked if at least one active
9. **Release-ready setup** (release-ready only):
   - Detect available platforms (`android/`, `ios/`); both → ask which
   - Release report path: `ds/mobile/release.json` (single file, committed, overwritten each run — `ds/<skill>/` user-facing operational namespace)
   - `--diff`: read previous content of `ds/mobile/release.json` before overwriting, compute diff in memory, present in chat. Trend over >1 run → `git log -- ds/mobile/release.json` is authoritative — never a directory of stale per-run reports.
   - Fetch live policy data (see references/scoring.md)

**Gate:** Platform identified; mode + scope confirmed; regulatory frameworks resolved. If fails → platform undetectable → prompt user (Flutter / RN / iOS / Android / Cross-platform), record the detected platform; mode/scope unconfirmed after prompt → default `audit` + `all`, warn; regulatory ambiguous → ask user to confirm before proceeding.

### Phase 2: Architecture Discovery [SKIP if 1-2 domains]

**When:** scope includes 3+ domains or `all`.

1. **Detect architecture:** pattern (Clean/MVVM/MVC), auth, state management, navigation, backend, offline, design system, testing, CI/CD, i18n, DI.
2. **Confirm with user.** Present for corrections. **Under `--auto`:** skip the confirmation — treat the detected architecture as confirmed.
3. **Classify rules:** CAT-1 = universal best practice, existing pattern misused, bug, security flaw (auto-fixable). CAT-2 = new layer/structure not in current architecture (needs approval). Category depends on architecture — user has Riverpod → UDF violation is CAT-1; no state management → adding it is CAT-2.
4. **Present ideal scenario.** Show CAT-1 + CAT-2 opportunities; ask which enhancements to include (default: none). **Under `--auto`:** skip the ask — CAT-2 opportunities are included per best-judgment impact/effort/risk reasoning (Unattended Mode rule 3) instead of defaulting to none.
5. **Finalize scope:** all CAT-1 + only approved CAT-2; scope is fixed for entire audit.

**Critical rule:** CAT-2 fixes are NEVER applied without user approval. **Under `--auto`:** this is an interactive-mode floor only — CAT-2 items resolve automatically per Unattended Mode rule 3 (applied, using the same impact/effort/risk reasoning the approval step would show), recorded in the summary, except items matching the rule-4 exception list.

**Gate:** Architecture confirmed; every rule classified CAT-1 / CAT-2; scope finalized with approved enhancements. If fails → no user corrections + no enhancement selections after one re-prompt → treat detected architecture as confirmed, classify unclassified rules as CAT-1, include zero CAT-2, record the detected architecture, proceed with note that architecture was auto-confirmed.

### Phase 3: Rule Loading

Load only reference files matching scope:

| Scope | Reference File |
|-------|---------------|
| security, privacy, regulatory, store | [rules-compliance.md](references/rules-compliance.md) |
| ux, visual, a11y | [rules-experience.md](references/rules-experience.md) |
| arch, testing, perf, network, i18n | [rules-engineering.md](references/rules-engineering.md) |
| release (release-ready) | [rules-release.md](references/rules-release.md) |
| release-ready scoring | [scoring.md](references/scoring.md) |

**Gate:** All reference files for in-scope domains loaded; unloadable domains marked N/A. If fails → file unloadable → mark domains N/A in the scopes-done tracking, reason "reference file unavailable", skip in Phase 4, surface in Phase 9 summary as "domains skipped: {list} — reference files not found".

### Phase 4: Scan

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND current run-cycle) → read findings matching scopes; verify each (re-read file:line), skip verified; run full for uncovered.

**Large scope (3+ domains):** progress checklist + append findings to `ds/audit/findings.md` after each domain. Max 2 parallel scans.

**Per domain:** search files → search violations → read context to verify → skip unverifiable rules.

**arch scope mandatory checks ([references/principles.md §2](references/principles.md)):** evaluate widget / screen / view-model / repository layers against SOLID — SRP (widget changes for >1 reason: UI + state + I/O), OCP, LSP (subtype violates parent navigation contract), ISP (consumer forced to implement unused lifecycle hooks), DIP (UI imports concrete platform-channel instead of abstraction). GRASP — Information Expert, Low Coupling (>7 unrelated peer imports), High Cohesion. Cite principle by name.

**network + perf scope reliability checks ([references/principles.md §4](references/principles.md)):** flag missing — timeout on every API call, retry-with-exponential-backoff on transient failures, offline / slow-network graceful degradation, app-lifecycle handlers (background → foreground state restoration), idempotency keys on payment / order / write endpoints, structured logging surviving across app restart, fail-fast input validation at every boundary (deep links, push notifications, intent extras).

**Confidence:** HIGH = match + context verified. MEDIUM = pattern, ambiguous. LOW = heuristic.

**False-positive prevention:** never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Category assignment:** CAT-1 always reported; CAT-2 only if in approved enhancements.

**Recovery (context lost):** progress checklist → read `ds/audit/findings.md` → resume from first incomplete domain. Scan each domain once.

**Gate:** Every in-scope domain scanned; findings recorded with severity + confidence. If fails → re-read progress checklist + `ds/audit/findings.md`; resume from first incomplete; if a domain still fails after retry (file unreadable, context lost) → mark `partial` in the scopes-done tracking with collected findings, continue.

### Phase 5: Report

#### Standard Report (audit modes)

```
## Audit Report — {project-name}
Platform: {platform} | Scanned: {domains} | Date: {today}
Architecture: {summary}

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

**Gate:** Report with findings + severities + summary. If fails → domain produced no findings due to scan error (not because it was clean) → re-run scan once; still fails → present report with failed domains marked "scan incomplete", findings count `?` in summary.

### Phase 6: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Pick by severity / Report only |
| `audit+fix` | Auto-transition to fix |
| `quick-fix` | Auto-apply all |
| `release-ready` | Ask: Fix plan / Save report only / Guidance for key findings |

**Gate:** User selected post-report action; mode-specific next step determined. If no selection after one re-prompt → apply the mode default (`audit` → Report only; `audit+fix` → Fix all; `quick-fix` → Auto-apply all; `release-ready` → Save report only) and record that default choice. **Under `--auto`:** skip the ask entirely — apply this same mode default immediately, no prompt or wait.

### Phase 7: Fix [SKIP if audit-only or report-only]

1. **Plan.** Read findings, apply severity filter, group by file, identify dependencies. Present CAT-1 + CAT-2 (pre-approved) — one line per fix (`[severity] title — file:line`) grouped by severity with counts; state the question (`Apply these N fixes?`). "All" = exactly the displayed set.
2. **Confirmation:** `quick-fix` → summary + proceed; `audit+fix` → full plan + ask (Apply all / per-severity bulk `Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item); `release-ready` → show auto-fixable vs guidance split. **Under `--auto`:** skip the confirmation for every mode — apply all CAT-1 + pre-approved CAT-2 fixes automatically, including CRITICAL, per Unattended Mode rule 3.
3. **Execute.** Apply grouped by file. Re-read before + after each edit. Record applied/failed/skipped.

**Gate:** All standard fixes attempted; each recorded. If fails → fix unattempt-able (file unreadable, edit error) → record `failed` as the finding's disposition, revert any partial edit via re-read + restore, continue; list failed fixes in Phase 9 summary with reason.

### Phase 8: Needs-Approval Review [needs_approval > 0]

**Under `--auto`:** no review step is shown — every item resolves per Unattended Mode rule 3 (applied, using the same impact/effort/risk reasoning this review block would show), except items matching the rule-4 exception list, which become `skipped (needs-human)`. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → record `pending-user-decision` as the finding's disposition, proceed to Summary with status WARN, list unresolved items prominently.

### Phase 9: Summary

```
ds-mobile: {OK|WARN|FAIL} | Mode: {audit|audit+fix|quick-fix|release-ready} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Cleanup:** remove mobile-scoped findings (security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release) from `ds/audit/findings.md`. Empty after removal → delete file.

FRC+DSC accounting.

**Gate:** `fixed + failed + skipped + needs_approval + not_applicable = total`; every modified file re-read; mobile-scoped findings removed from `ds/audit/findings.md`. If fails → counts unreconciled → identify undisposed finding, assign `failed` reason "disposition not recorded", re-run count; cleanup fails → warn, leave file intact rather than partial-modify.

**Value Delivered:** 1-5 concrete mobile-quality outcomes. Example shapes (placeholders, not literal):

- `{n} store-rejection risks intercepted (permission abuse, missing privacy declarations, undocumented background tasks) — submission round-trip saved`
- `{n} CRITICAL findings: hardcoded API keys / unencrypted PII in shared preferences — exposure window before next release closed`
- `{n} mobile a11y findings (small touch targets, missing semantic labels, contrast on dark mode) — accessibility lawsuit + EAA compliance risk reduced`
- `Release-readiness score: {before} → {after} / 100 — go/no-go decision is now measurable, not vibes`

Audit-only run: `{n} findings (severity: {breakdown}) — actionable list returned, no source modified`.

## Quality Gates

1. **No cascading breakage** — verify no broken imports/references after fixes; fix breaks another file → revert, mark failed, continue
2. **Format preservation** — match existing indentation + code style
3. **Scope boundary** — only touch lines task requires
4. **Platform consistency** — fixes use correct platform API
5. **Artifact-first recovery** — re-read files before + after editing
6. **FRC** — every finding gets a disposition in summary
7. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit is regenerable from source; applied fixes land in the working tree, git is the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No project file found | Stop: "Mobile project not found in current directory." |
| Platform ambiguous | Ask user to confirm (`--auto`: Cross-platform if multiple indicators, else the single detected platform) |
| Reference file fails to load | Skip domain, note as N/A |
| Architecture Discovery: no corrections | Use detected values |
| CAT-2 list: user selects 'none' | Audit CAT-1 rules only (default) |
| Zero findings in domain | Report domain as clean |
| Fix: file changed externally | Re-read before each edit |
| Fix: edit fails | Skip, log as failed, continue |
| Regulatory: no active frameworks | Skip PRV-06–18 regulatory rules |
| Release-ready: policy fetch fails | Use fallback values, warn in report |
| Release-ready: first run | No previous `ds/mobile/release.json` → no diff, note "First audit" |
| Release-ready: corrupt JSON report | Warn, treat as first audit (skip diff), overwrite |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
