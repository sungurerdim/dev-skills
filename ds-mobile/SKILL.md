---
name: ds-mobile
description: Mobile app quality audit — 181 rules across 13 domains with release-readiness scoring (Flutter, SwiftUI, Kotlin/Compose, React Native, Capacitor). Use when auditing a mobile app for quality or release readiness.
---

# /ds-mobile

Mobile apps ship with permission abuse, missing accessibility, hardcoded keys, and store-blocking issues that only surface during review. This skill catches them across 181 rules before you submit.

**Mobile App Quality Audit** — Flutter, SwiftUI, Kotlin/Compose, React Native, Capacitor.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

User runs `/ds-mobile`, asks to audit/review a mobile app (Flutter, RN, iOS, Android) or its store compliance/release readiness, or the project contains `pubspec.yaml` (Flutter), `react-native` in `package.json`, `*.xcodeproj`, or Android `build.gradle` with `android {}`.

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
- State-qualifying: a resumable multi-scope audit whose domain-by-domain progress lives nowhere else — an interrupted run would otherwise re-scan from zero. Progress persists to `ds/audit/mobile.json` with the run's `git_hash`; applied fixes still land in the working tree, git remains the durable record. State deleted when the Summary completes.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--scope={list}` | security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release, or `all` |
| `--platform={p}` | Override: `flutter`, `react-native`, `ios`, `android` |
| `--preview` | Analyze and report only — no file is written |
| `--release-ready` | Score release readiness — scope + behavior in Run Types below |
| `--skip-manual` | Skip manual gates (release-ready) |
| `--diff` | Compare with previous release report |
| `--resume` | Resume from `ds/audit/mobile.json` without the confirmation prompt |
| `--clean` | Delete `ds/audit/mobile.json` and start fresh |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default: resolves to scan, review, fix across all scopes, recorded in the summary, unless `--preview` or `--release-ready` is passed. `--ask` with no disambiguating flag: present the run-type menu.

## Run Types

| Run | Scope | Behavior |
|-----|-------|----------|
| Default | All selected | Scan, review, fix |
| `--preview` | All selected | Scan and report only |
| `--release-ready` | security, privacy, regulatory, store, release, i18n, a11y | 100-point scoring + manual gates + live policy fetch |

## Delegation

**Owns:** mobile-security, mobile-privacy, mobile-regulatory, mobile-ux, mobile-store, mobile-permissions, mobile-release, mobile-visual | **Delegates:** none (authoritative for mobile projects) | **Receives:** ds-compliance → mobile security/privacy/regulatory; ds-launch → mobile store compliance; ds-ship → Phase 2 stack delegation

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent. Full rules: STO-11 (Sign in with Apple), SEC-13 (entitlements correctness), SEC-14 (`google-services.json` hygiene) — [references/rules-compliance.md](references/rules-compliance.md).

## Execution Flow

Detect → Configure → [Architecture Discovery] → Scan → Report → [Fix/Score] → [Needs-Approval] → Summary

### Phase 1: Detect

**Recovery check (first step, runs unconditionally on every invocation):** DETECT `ds/audit/mobile.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, compare state `git_hash` against `git rev-parse HEAD` output. Mismatch → default: resume silently (best judgment — the re-verify step below catches real drift), recorded in the summary; `--ask`: prompt `Resume anyway? [Y/n]`. Resume → RE-VERIFY the `in_progress` domain by re-reading the files its recorded findings cite, keep `done` domains, announce `[MOB] Resuming from Phase {N}: {name}.` On successful Summary, delete state; `ds/audit/` empty afterwards → remove it. On fresh start: `grep -qxF 'ds/audit/' .gitignore` → exit 0; non-zero → append the `ds/audit/` line.

**State `data`:** `{ release_ready, platform, scopes_selected, scopes_done[], architecture, cat2_approved[], findings_per_domain: {domain: [{id, severity, file, line, category, confidence, disposition}]}, release_score }`.

1. **Project detection.**

   | Platform | Detection |
   |----------|-----------|
   | Flutter | `pubspec.yaml` with `flutter:` |
   | React Native | `package.json` dep `react-native` |
   | Expo | `app.json`/`app.config.*` with an `expo` key, plus `eas.json` present |
   | iOS Native | `*.xcodeproj` or `Package.swift` |
   | Android Native | `build.gradle` with `android {}` |
   | Kotlin Multiplatform | `shared/` module directory containing `commonMain` |
   | Hybrid / WebView shell | `capacitor.config.{ts,js,json}` or `@capacitor/core` in `package.json`; Cordova `config.xml` |
   | Cross-platform | Multiple platform indicators |

   Expo is a modifier on React Native (`--platform=react-native` covers it; Expo-specific rules load from the REL-02/04/08 branches). Kotlin Multiplatform is a modifier on Android Native for the shared module's cross-platform logic — the `android {}` and iOS rows still apply to their native targets. Hybrid is a modifier, not an alternative: a Capacitor app is also an iOS and an Android app, so the native rows still apply to `ios/`/`android/`. Detecting hybrid additionally activates the HYB rules (Phase 3).

2. **Platform confirmation.** Default: ambiguous detection resolves to `Cross-platform` when multiple indicators are present, else the single detected platform — best judgment, recorded in the summary, never blocks. `--ask`: ambiguous → ask user.
3. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND current run-cycle; prior-cycle — however recent — is stale, diff context only) → read findings matching mobile scopes, skip redundant analysis. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
4. **Upstream artifacts:** Profile → `Data:`, `Deploy:`, `Scores:`, Type+Stack. Findings(mobile scopes) → verify + use. Absent → own analysis.
5. **Run-type selection.** Default: resolves to scan, review, fix (all scopes) unless `--preview` or `--release-ready` is passed, recorded in the summary. A disambiguating flag (`--preview`, `--release-ready`, `--scope`) selects that run directly. `--ask` with no disambiguating flag: present the Run Types table above as the menu (Audit marked `(recommended)`), plus Custom — pick scopes — and `(Cancel)`.
6. **Scope parsing.** Default: all domains.
7. **Custom scope** (if Custom, `--ask` only): ask for domains + run type.
8. **Regulatory framework detection** (security/regulatory/store/all): auto-detect indicators (GDPR, KVKK, CCPA, LGPD, PIPL, etc.). Default: every detected indicator used as-is, recorded in the summary. `--ask`: confirm with user. Rules tagged `[FRAMEWORK: X,Y]` checked only if at least one is active.
9. **Release-ready setup** (release-ready only): detect available platforms (`android/`, `ios/`; both → ask which). Report path: `ds/mobile/release.json` (single committed file, overwritten each run). `--diff`: read the previous report first, diff in memory, present in chat — trend over >1 run comes from `git log -- ds/mobile/release.json`, never a directory of stale reports. Fetch live policy data (references/scoring.md).

**Gate:** Platform identified; run type + scope confirmed; regulatory frameworks resolved. If fails → platform undetectable → prompt user (Flutter / RN / iOS / Android / Cross-platform), record the detected platform; run type/scope unconfirmed after prompt → default to `--preview` + `all`, warn; regulatory ambiguous → ask user to confirm before proceeding.

### Phase 2: Architecture Discovery [SKIP if 1-2 domains]

**When:** scope includes 3+ domains or `all`.

1. **Detect architecture:** pattern (Clean/MVVM/MVC), auth, state management, navigation, backend, offline, design system, testing, CI/CD, i18n, DI.
2. **Confirm architecture.** Default: the detected architecture is treated as confirmed, recorded in the summary. `--ask`: present for corrections.
3. **Classify rules:** CAT-1 = universal best practice, existing pattern misused, bug, security flaw (auto-fixable). CAT-2 = new layer/structure not in current architecture (needs approval) — depends on architecture: user has Riverpod → UDF violation is CAT-1; no state management → adding it is CAT-2.
4. **Present ideal scenario.** Show CAT-1 + CAT-2 opportunities. Default: CAT-2 opportunities included per the same impact/effort/risk reasoning an approval block would show, recorded in the summary. `--ask`: ask which enhancements to include (default: none).
5. **Finalize scope:** all CAT-1 + only approved CAT-2; scope is fixed for entire audit.

**Critical rule:** CAT-2 fixes require the same approval discipline as any decision point — per-item confirmation is an `--ask` floor only. Default: CAT-2 items resolve automatically by best judgment (same reasoning the approval step would show), recorded in the summary, except items matching the publish/irreversible exception list. `--ask`: CAT-2 fixes are never applied without explicit per-item approval.

**Gate:** Architecture confirmed; every rule classified CAT-1 / CAT-2; scope finalized with approved enhancements. If fails → no corrections + no enhancement selections after one re-prompt: treat detected architecture as confirmed, classify unclassified rules as CAT-1, include zero CAT-2, record the detected architecture, note it was auto-confirmed.

### Phase 3: Rule Loading

Load only reference files matching scope:

| Scope | Reference File |
|-------|---------------|
| security, privacy, regulatory, store | [rules-compliance.md](references/rules-compliance.md) |
| ux, visual, a11y | [rules-experience.md](references/rules-experience.md) |
| arch, testing, perf, network, i18n | [rules-engineering.md](references/rules-engineering.md) |
| arch (hybrid shell detected) | [rules-engineering.md § Hybrid & WebView Bridge](references/rules-engineering.md) — HYB-01–04, conditional: skipped entirely on native/Flutter/RN projects |
| release (release-ready) | [rules-release.md](references/rules-release.md) |
| release-ready scoring | [scoring.md](references/scoring.md) |

**Gate:** All reference files for in-scope domains loaded; unloadable domains marked N/A. If fails → file unloadable → mark domains N/A in the scopes-done tracking, reason "reference file unavailable", skip in Phase 4, surface in Phase 9 summary as "domains skipped: {list} — reference files not found".

### Phase 4: Scan

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND current run-cycle) → read findings matching scopes; verify each (re-read file:line), skip verified; run full for uncovered.

**Large scope (3+ domains):** progress checklist + append findings to `ds/audit/findings.md` after each domain, max 2 parallel scans. **Per domain:** search files → search violations → read context to verify → skip unverifiable rules.

**Cross-cutting checks** (arch SOLID/GRASP, arch hybrid HYB-01–04, network+perf reliability): [references/rules-engineering.md § Scan-Time Cross-Cutting Checks](references/rules-engineering.md).

**Confidence** (per [../core/severity-score-categories.md](../core/severity-score-categories.md)): HIGH = match + context verified. MEDIUM = pattern, ambiguous. LOW = heuristic.

**False-positive prevention:** never flag `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING`, test fixtures.

**Category assignment:** CAT-1 always reported; CAT-2 only if in approved enhancements.

**Recovery (context lost):** read `ds/audit/mobile.json` → resume from the first domain not marked `done`, re-verifying the `in_progress` one; `ds/audit/findings.md` supplies the finding bodies. The state file is the progress record; an in-chat checklist does not survive the interruption it exists for. Write state after every completed domain, not only at phase boundaries. Scan each domain once.

**Gate:** Every in-scope domain scanned; findings recorded with severity + confidence. If fails → re-read progress checklist + `ds/audit/findings.md`; resume from first incomplete; if a domain still fails after retry (file unreadable, context lost) → mark `partial` in the scopes-done tracking with collected findings, continue.

### Phase 5: Report

#### Standard Report (non-`--release-ready` runs)

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

#### Release Readiness Report (`--release-ready` runs)

Per references/scoring.md: 100-point dynamic scoring across 7 dimensions, manual gates, consequence table, diff against previous report. Include: policy values used (fetched vs fallback), dimension breakdown with bar chart, findings by severity, manual gate status, and "if you publish now" consequence table for CRITICAL+HIGH.

**Gate:** Report with findings + severities + summary. If fails → a domain produced no findings due to scan error (not because it was clean): re-run scan once; still fails → present report with failed domains marked "scan incomplete", findings count `?` in summary.

### Phase 6: Post-Report

| Run | Behavior |
|-----|----------|
| Standard | `--preview` → Report only. Otherwise default: auto-transition to fix. `--ask`: ask Fix all / CRITICAL+HIGH only / Pick by severity / Report only |
| `--release-ready` | Default: Save report only. `--ask`: ask Fix plan / Save report only / Guidance for key findings |

**Gate:** Post-report action determined — default (no `--ask`): Standard runs auto-transition to fix unless `--preview` (then Report only); `--release-ready` defaults to Save report only; applied immediately with no prompt, recorded in the summary. `--ask`: the user's selection. If fails → `--ask` gets no selection after one re-prompt: apply the run's default action, record it.

### Phase 7: Fix [SKIP if Phase 6 resolved to report-only]

0. **Checkpoint** (`../core/checkpoint-protocol.md`). `git status --porcelain` → empty → clean tree, proceed. Non-empty: default — proceed only when the pre-existing dirty state stays untouched by this skill's writes, else stop and record `only you can do`; `--ask` — ask **Commit first (recommended) / Stash / Proceed anyway** (risk: fix edits interleave with uncommitted work, single-command rollback is lost). Never run a bulk fix over uncommitted unrelated changes silently.
1. **Plan.** Read findings, apply severity filter, group by file, identify dependencies. Present CAT-1 + CAT-2 (pre-approved) — one line per fix (`[severity] title — file:line`) grouped by severity with counts; state the question (`Apply these N fixes?`). "All" = exactly the displayed set.
2. **Confirmation.** Default: apply all CAT-1 + pre-approved CAT-2 fixes automatically, including CRITICAL, by best judgment, recorded in the summary. `--ask`: Standard run → full plan + ask (Apply all / per-severity bulk, CRITICAL still confirms per item); `--release-ready` → show auto-fixable vs guidance split.
3. **Execute.** Apply grouped by file. Re-read before + after each edit. Record applied/failed/skipped.

**Gate:** All standard fixes attempted; each recorded. If fails → fix unattempt-able (file unreadable, edit error): record `failed` as the finding's disposition, revert any partial edit via re-read + restore, continue; list failed fixes in Phase 9 summary with reason.

### Phase 8: Needs-Approval Review [needs_approval > 0]

Default: every item resolves by best judgment (same impact/effort/risk reasoning this review block would show), except items matching the publish/irreversible exception list, which become `skipped (only you can do)`; no review step is shown. `--ask`: present each item compactly (`[severity] title — file:line`) grouped by severity with counts, state the question (`Approve these N items?`); ask Apply all / per-severity bulk (alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → record `pending-user-decision` as the finding's disposition, proceed to Summary with status WARN, list unresolved items prominently.

### Mechanical Done Gate [any fix applied]

Resolve `{check-cmd}` in Phase 1: ds-quality enforcement arm installed → use its gate command; else platform-native analyze/lint/type/test (`flutter analyze` + `flutter test`, `dart analyze`, eslint/tsc + jest for RN, `swiftlint`/xcodebuild test, gradle lint/test); none detectable → Verification-Infrastructure Gap, offer `/ds-quality`, record the decision. Baseline captured before Phase 7; baseline red → done means "no *new* red", never inherited as green. After each fix batch: run `{check-cmd}` on the touched scope — new red → repair, re-run (≤3 attempts); still red → revert via `git checkout -- {file}`, disposition `failed (mechanical gate)`. Before Phase 9: run the full `{check-cmd}` once — its command + output is the Completion Evidence, distinct from re-reading files. Never report `OK` with a new red. Audit/report-only runs → gate N/A, state it.

### Phase 9: Summary

```
ds-mobile: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

**Cleanup:** remove mobile-scoped findings (security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release) from `ds/audit/findings.md`. Empty after removal → delete file. Run completed → delete `ds/audit/mobile.json`; `ds/audit/` now empty → remove the directory. Run ended WARN/FAIL → leave state in place so the next invocation can resume it.

Disposition accounting — totals balance.

**Gate:** `fixed + failed + skipped + needs_approval + not_applicable = total`; every modified file re-read; mobile-scoped findings removed from `ds/audit/findings.md`; state file deleted on a completed run (`test ! -f ds/audit/mobile.json`). If fails → counts unreconciled → identify undisposed finding, assign `failed` reason "disposition not recorded", re-run count; cleanup fails → warn, leave file intact rather than partial-modify.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} store-rejection risks intercepted (permission abuse, missing privacy declarations, undocumented background tasks) — submission round-trip saved`
- `{n} CRITICAL findings: hardcoded API keys / unencrypted PII in shared preferences — exposure window before next release closed`
- `Release-readiness score: {before} → {after} / 100 — go/no-go decision is now measurable, not vibes`

Audit-only run: `{n} findings (severity: {breakdown}) — actionable list returned, no source modified`.

## Quality Gates

Additional to the W-checks below: format preservation (match existing style) and platform consistency (correct platform API). Cascading breakage, scope boundary, artifact recovery, and full accounting are the Mechanical Done Gate and W3/W4/the Contract's accounting bullet — not restated here.

- W9: state-qualifying — domain-by-domain progress persists to `ds/audit/mobile.json` (written after each completed domain, deleted on a completed Summary); applied fixes land in the working tree, git is the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No project file found | Stop: "Mobile project not found in current directory." |
| Platform ambiguous | Default: Cross-platform if multiple indicators, else the single detected platform. `--ask`: confirm with user. |
| Hybrid shell, native dirs not committed (generated at build) | Run HYB rules against `capacitor.config.*` + `package.json`; report native-only checks `not_applicable`, never as missing-file findings |
| Reference file fails to load | Skip domain, note as N/A |
| Architecture Discovery: no corrections | Use detected values |
| CAT-2 list: user selects 'none' | Audit CAT-1 rules only (default) |
| Zero findings in domain | Report domain as clean |
| Fix: file changed externally | Re-read before each edit |
| Fix: edit fails | Skip, log failed, continue |
| Regulatory: no active frameworks | Skip PRV-06–18 |
| Release-ready: policy fetch fails / first run / corrupt prior report | Respectively: fallback values (warn) / no diff, note "First audit" / treat as first audit, overwrite |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
