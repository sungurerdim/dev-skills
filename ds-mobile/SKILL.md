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
- Fully functional standalone — uses `.findings.md` for optimization when available

---

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `quick-fix`, `release-ready` |
| `--scope=<domains>` | Comma-separated: security, privacy, regulatory, store, ux, visual, a11y, arch, testing, perf, network, i18n, release, or `all` |
| `--platform=<p>` | Override: `flutter`, `react-native`, `ios`, `android` |
| `--release-ready` | Shorthand for `--mode=release-ready` — runs release-critical domains only |
| `--skip-manual` | Skip manual verification gates (release-ready mode) |
| `--diff` | Compare with previous release readiness report |

Without flags: present mode selection to the user.

## Modes

| Mode | Scope | Behavior |
|------|-------|----------|
| `audit` | All selected domains | Scan and report only |
| `audit+fix` | All selected domains | Scan, review findings, then fix |
| `quick-fix` | All selected domains | Scan and auto-fix, minimal review |
| `release-ready` | security, privacy, regulatory, store, release, i18n, a11y | 100-point scoring + manual gates + live policy fetch |

---

## Execution Flow

Detect → Configure → [Architecture Discovery] → Scan → Report → [Fix/Score] → Summary

### Phase 1: Detect

1. **Project detection.** Search for project files to identify platform:

| Platform | Detection |
|----------|-----------|
| Flutter | `pubspec.yaml` with `flutter:` section |
| React Native | `package.json` with `react-native` dependency |
| iOS Native | `*.xcodeproj` or `Package.swift` |
| Android Native | `build.gradle` with `android {}` block |
| Cross-platform | Multiple platform indicators |

2. **Platform confirmation.** If ambiguous, ask the user to confirm.

3. **Mode selection.** Ask the user or use flags:
   - Audit Only (default) — scan all domains, report only
   - Audit & Fix — scan, review, then fix
   - Quick Fix — scan and auto-fix, minimal review
   - Release Ready — 100-point scoring with manual gates
   - Custom — pick specific domains and mode

4. **Scope parsing.** Map selection to domains and mode. Default: `audit` mode, `all` domains.

5. **Custom scope** (only if Custom selected): Ask for domains and mode.

6. **Regulatory framework detection** (when scope includes security, regulatory, store, or all):
   - Auto-detect by searching codebase for framework indicators (GDPR, KVKK, CCPA, LGPD, PIPL, etc.)
   - Confirm detected frameworks with user, or ask which apply
   - Rules tagged `[FRAMEWORK: X,Y]` only checked if at least one framework is active

7. **Release-ready setup** (only if release-ready mode):
   - Detect available platforms (android/ and ios/ directories)
   - If both available, ask which to audit
   - Set report directory: `{project_root}/.mobileaudit/`
   - Load previous reports for diff comparison
   - Fetch live policy data (see references/scoring.md)

**Gate:** Platform identified, mode and scope confirmed, regulatory frameworks resolved.

---

### Phase 2: Architecture Discovery [SKIP if 1-2 domains]

**When:** Scope includes 3+ domains or `all`.

1. **Detect architecture:** pattern (Clean/MVVM/MVC), auth, state management, navigation, backend, offline capability, design system, testing, CI/CD, i18n, dependency injection.

2. **Confirm with user.** Present detected architecture for corrections.

3. **Classify rules:**
   - **CAT-1 Conformance:** Universal best practice, existing pattern used incorrectly, bug, security flaw — auto-fixable
   - **CAT-2 Enhancement:** New layer/structure not in current architecture — requires approval

   A rule's category depends on the architecture. Example:
   - User has Riverpod → unidirectional data flow violation is CAT-1
   - User has no state management → adding it is CAT-2

4. **Present ideal scenario.** Show CAT-1 (auto-fixable) and CAT-2 opportunities. Ask which enhancements to include (default: none).

5. **Finalize scope:** All CAT-1 rules + only approved CAT-2 rules. This scope is fixed for the entire audit.

**Critical rule:** CAT-2 fixes are NEVER applied without user approval.

**Gate:** Architecture confirmed by user, every rule classified as CAT-1 or CAT-2, scope finalized with approved enhancements.

---

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

---

### Phase 4: Scan

**Large scope (3+ domains):** Use progress tracking to survive context loss:
1. Create numbered progress checklist with all domains in scope
2. Create `.findings.md` in project root (add to .gitignore)
3. After each domain scan, append findings to the file
4. Maximum 2 parallel domain scans

**Per domain:**
1. Search for relevant files
2. Search contents for violation patterns
3. Read files to verify findings in context
4. Skip rules that cannot be verified from client code

**Confidence:** HIGH = specific pattern match + context verified, MEDIUM = pattern match, ambiguous context, LOW = heuristic only.

**False positive prevention:** Check surrounding context. Never flag: `// noqa`, `// intentional`, `// safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures.

**Category assignment:**
- CAT-1: Always report
- CAT-2: Only report if in approved enhancements

**Recovery (if context lost mid-audit):**
1. Don't restart — check progress checklist
2. Read `.findings.md` to restore completed findings
3. Resume from first incomplete domain
4. Never re-scan a completed domain

**Gate:** Every in-scope domain scanned, all findings recorded with severity and confidence.

---

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

**Severity:** CRITICAL > HIGH > MEDIUM > LOW. When uncertain, choose lower.

#### Release Readiness Report (release-ready mode)

Per references/scoring.md: 100-point dynamic scoring across 7 dimensions, manual gates, consequence table, diff against previous report.

Include: policy values used (fetched vs fallback), dimension breakdown with bar chart, findings by severity, manual gate status, and "if you publish now" consequence table for CRITICAL+HIGH.

**Gate:** Report presented to user with all findings, severities, and summary table.

---

### Phase 6: Post-Report

| Mode | Behavior |
|------|----------|
| `audit` | Ask: Fix all / CRITICAL+HIGH only / Pick by severity / Report only |
| `audit+fix` | Auto-transition to fix phase |
| `quick-fix` | Auto-transition, auto-apply all |
| `release-ready` | Ask: Fix plan / Save report only / Guidance for key findings |

**Gate:** User selected post-report action; mode-specific next step determined.

---

### Phase 7: Fix [SKIP if audit-only or report-only]

1. **Plan.** Read findings (from `.findings.md` for large scopes). Apply severity filter. Group by file. Identify fix dependencies. Present grouped fix plan:
   - CAT-1 Conformance (auto-fixable)
   - CAT-2 Enhancement (pre-approved)

2. **Confirmation** (mode-dependent):
   - `quick-fix`: Show summary, proceed without per-item approval
   - `audit+fix`: Show full plan, ask: Apply all / Review each / Cancel
   - `release-ready`: Show auto-fixable vs guidance-required split

3. **Execute.** Apply fixes grouped by file. Re-read each file before editing. Re-read after editing to verify. Record: applied, failed, skipped.

4. **Summary.**
   ```
   Applied: N | Failed: N | Skipped: N | Total: N
   ```

**Cleanup:** Delete `.findings.md` after fix summary.

**Gate:** Applied + failed + skipped = total findings; every modified file re-read and verified; `.findings.md` deleted.

---

## Quality Gates

1. **No cascading breakage** — after fixes, verify no broken imports/references
2. **Format preservation** — fixes match existing indentation and code style
3. **Scope boundary** — only touch lines the task requires
4. **Platform consistency** — fixes use correct platform API
5. **Artifact-first recovery** — re-read files before and after editing

---

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
