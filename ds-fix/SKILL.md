---
name: ds-fix
description: Universal code quality fix — format, lint, type-check, l10n, and security scan for any stack. Use when the user asks to fix code quality, run formatters/linters/type-checks, or scan for secrets.
---

# /ds-fix

AI assistants skip formatting, ignore lint errors, and never run type checks. This skill runs all five passes in order and verifies the result.

**Universal Code Quality Fix** — format, lint, type-check, l10n, security scan for any stack.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-fix`, or asks to format code, run linters/fix lint errors, run type checks, scan for secrets, or audit dependencies

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "run formatter, linter, type checker", "fix lint errors" | "review architecture / patterns" (→ ds-review --strategic) |
| "scan for hardcoded secrets / dep CVEs" | "full regulatory security audit" (→ ds-compliance --security) |
| "format + l10n consistency check" | "generate translations / new locales" (→ manual / external) |
| "fix all auto-fixable issues across stack" | "design a new API" (→ ds-backend) |

## Contract

**Dimensions:** B1 (fix), A8 (mechanical), C1 (mechanical)

- Runs automated fixers in safe order: l10n → format → lint → typecheck → security — mutating scopes first, read-only verification after (typecheck validates the post-fix state), matching the ds-quality gate order (format → lint → type).
- `--check` mode: report only, zero modifications.
- Missing tools skip with a warning — never fails on absent optional tooling.
- Re-validates after fix to confirm it worked. Reports counts, not verbose output.
- Does not perform code review, architecture analysis, or refactoring.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** tool-driven, fast, independent passes — re-running repeats idempotent fixes. No `ds/audit/fix.json` written.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Fix all scopes; diff-default file scoping applies automatically when a diff exists (see Phase 1) |
| `--check` | Report only, no modifications |
| `--scope=X,Y` | Specific scope(s), comma-separated; `all` forces a full-project run even when a diff exists |
| `--diff[={ref}]` | Force diff-file scoping explicitly: bare → working tree + staged vs HEAD; with `{ref}` → merge-base diff vs that ref. Redundant when a diff already exists — see Phase 1 default |
| `--skip-if-clean` | Run only scopes whose check-mode reports issues. Default `true` when invoked by another skill (ds-commit/ds-pr/ds-ship gates), `false` when user-invoked. |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

## Scopes

| Scope | What It Does |
|-------|-------------|
| `format` | Apply code formatter |
| `lint` | Run linter with auto-fix |
| `typecheck` | Run static type checker |
| `l10n` | Generate/validate localization files |
| `security` | Secret pattern scan + dependency audit |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| format | a detected stack's formatter tool/config is present (Phase 1) | N/A — no stack detected (security-only mode) |
| lint | a detected stack's linter tool/config is present | N/A — no stack detected |
| typecheck | the detected stack configures a type checker (`tsconfig.json`, Python type config, …) | N/A — no type checker configured |
| l10n | i18n=yes (locale files or an i18n framework detected) | N/A — i18n=no / no framework detected |
| security | any source — secret scan always runs; dep audit adds when a stack's audit tool exists | — |

Default: all five scopes in order.

## Delegation

**Owns:** format, lint, typecheck, l10n, secret-scan-quick, dep-quick-check | **Delegates:** ds-deps → deps-upgrade-execution; ds-review → code-level quality fixes | **Receives:** ds-commit → pre-commit gates; ds-pr → pre-PR gates; ds-issue → format/lint/type passes during issue execution; ds-quality → verify-loop toolchain passes; ds-ship → Phase 2 rule audit

## Tool Install Policy (applied to every scope below)

Scope tool (formatter, linter, typecheck, l10n generator, audit command) unavailable → apply this flow, stated once for every scope:

| Case | Action |
|------|--------|
| Installable tool missing | Default: install (Trust-Verified — registry-published, non-trivial age), re-run scope; blocked by missing system/sudo perms → `only you can do`, scope `skipped`. `--ask`: show install command (e.g., `{install-command-for-tool}`), ask **"Install and continue?"** — accept → install + re-run; decline → `⚠ Skipped (declined install)`, continue. |
| System-level tool missing (e.g., `{compiler-or-runtime}`) | Show manual install instructions, skip scope |
| Filesystem access error | Mark scope `WARN` with the specific OS error |

## Execution Flow

Detection → [L10n] → [Format] → [Lint] → [Typecheck] → [Security] → [Needs-Approval] → Summary

### Phase 1: Stack Detection

1. **Upstream artifacts:** Profile → Toolchain, Type+Stack. Absent → own detection.

Detect stacks in two tiers (multiple stacks may coexist, e.g. monorepo): Tier 1 primary manifests get the full toolchain (format + lint + typecheck + security); Tier 2 supplementary signals add applicable tools only, never as the sole detected stack. Manifests, activation conditions, and disambiguation: [references/stack-detection.md](references/stack-detection.md). Per stack: load toolchain from [../core/toolchains.md](../core/toolchains.md).

**Gate:** ≥1 stack detected or security-only mode. If fails → no manifests; run security scope only (universal secret scan + dep audit where available), announce "No stack detected — running security scope only", skip other scopes.

**Diff-default scope.** `--scope=all` → full-project run, skip this step. Otherwise detect whether a diff exists and scope file-touching fixers to it automatically (an explicit `--diff[={ref}]` forces the same resolution against the named ref):
- Base branch: `git symbolic-ref -q refs/remotes/origin/HEAD`, stripped of `refs/remotes/origin/`; unresolved → `main`; that absent too → `master`.
- Change set: `git diff --name-only` (working tree) ∪ `git diff --name-only --cached` (staged) ∪ `git diff --name-only origin/{base}...HEAD` (branch vs base; skip this leg when `origin/{base}` does not resolve).
- Any non-empty → format/lint/l10n run against that file set (tools that accept file args); typecheck and security's dependency-audit leg always run project-wide (partial type-checking/dep audits are unsound). All empty → full-project run.

**Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)) **[fix mode — N/A under `--check`]:** before the first mutating scope, run `git status --porcelain`. Default: proceed only when pre-existing dirty state stays untouched by this skill's writes — otherwise stop that unit, record `only you can do`. `--ask`: non-empty → ask **Commit first (recommended) / Stash / Proceed anyway** (risk: fixer edits interleave with uncommitted work, single-command rollback is lost). Empty output → clean tree, proceed.

### Phase 2: L10n [scope: l10n]

Run these steps in order:

| Step | Action |
|------|--------|
| Detect framework | Read project config + dependencies |
| Generate | Localization files if stack supports it (e.g., `{l10n-generator-command}`) |
| Cross-check keys | Every locale file MUST carry the same keys as the base locale |
| Placeholder consistency | Every `{placeholder-token}` in base MUST exist in all translations |
| Encoding | Detect mojibake (cp1252→UTF-8 double-encoding) |

**Fix mode:** generate files, stage generated output. **Check mode:** report mismatches only. Framework + key files per stack: [references/l10n-frameworks.md](references/l10n-frameworks.md). No framework detected → skip silently.

**Gate:** L10n files generated/validated, or no framework. If fails → tool unavailable: apply Tool Install Policy; persistent key mismatches after one fix attempt → report mismatched keys, mark scope `WARN`, don't abort.

### Phase 3: Format [scope: format]

Look up format tool from [`../core/toolchains.md`](../core/toolchains.md). **Fix mode:** run fix command. **Check mode:** run check command, report exit code. Non-default formatter (e.g., `{alt-formatter}` instead of `{default-formatter}`) → detect from config files and use that.

**Gate:** Format clean before proceeding to lint. If fails → tool unavailable: apply Tool Install Policy; formatter exits non-zero after run → report file count, proceed to lint (don't block pipeline on residual format issues).

### Phase 4: Lint [scope: lint]

Look up lint tool from [`../core/toolchains.md`](../core/toolchains.md). **Fix mode:** run fix command, then re-run check to verify. **Check mode:** run check command only, report issues. Non-default linter → detect from config and use that.

Stack-specific content patterns (e.g. `print(`/`console.log` outside a logger, per stack), linter-owned complexity thresholds, and the advisory `typos` spell-check sub-check: [references/lint-checks.md](references/lint-checks.md). Complexity thresholds run mechanically via the stack's linter config; project already sets a different threshold → keep the project's value, report the delta.

**Gate:** Lint re-check passes after auto-fix, or check-mode issues reported. If fails → tool unavailable: apply Tool Install Policy; unfixable errors after auto-fix → report residual count + file:line each, mark scope `WARN`, proceed to typecheck (don't re-run lint).

### Phase 5: Typecheck [scope: typecheck]

Look up typecheck tool from [`../core/toolchains.md`](../core/toolchains.md); detect if configured (e.g., `tsconfig.json` for Node, Python type hints) — none configured → skip silently. Run type checker (read-only) on the post-fix state, so its verdict covers what format + lint left on disk; report error count + top issues.

**Gate:** Type checker reports zero errors, or no type checker configured. If fails → tool missing: apply Tool Install Policy; type errors un-fixable (read-only checker) → record error count, proceed to security (type errors don't block subsequent scopes).

### Phase 6: Security [scope: security]

**6a. Secret scan (all stacks):** scan project files for the content regexes in [`../core/secret-patterns.md`](../core/secret-patterns.md), excluding the paths and `*.example` files that file lists.

| Match location | Severity | Action |
|-----------------|----------|--------|
| Tracked file (`git ls-files --error-unmatch {file}` exits 0) | CRITICAL | Report the site; "rotate this credential now, then add the variable name with a placeholder value to `.env.example`" |
| Untracked file | HIGH | Report the site; "add `{file}` (or its pattern) to `.gitignore` before it is ever committed" |

Never auto-fix a secret — the finding reports the site and the action above; the run's status is FAIL until the owner acts.

**Scanner augmentation (advisory):** `gitleaks` present → run alongside the patterns above (rule-first, sub-second) and merge findings; `trufflehog` present → offer a verified deep scan for CRITICAL triage (distinguishes live credentials from expired); neither present → the built-in patterns stand alone as the zero-dependency baseline.

**6b. Dependency audit (per stack):** look up audit command from [`../core/toolchains.md`](../core/toolchains.md); unavailable → skip with warning. Toolchain lists a source scanner (e.g. Bandit for Python) → run it read-only alongside the dep audit, merge findings.

**6c. Debug residue & temp-file discipline (advisory, all stacks):** grep for stray debug routes (flag for manual review, never auto-remove) and unsafe shell temp-file patterns (propose `mktemp` + `trap`). Detect signals + fix guidance: [references/security-checks.md](references/security-checks.md).

**Gate:** Secret scan + dep audit completed with classifications. If fails → dep audit tool missing: skip dep sub-phase, warn in summary; secret scan (built-in, no external tool) must always complete — filesystem access error → mark scope `WARN`. Any confirmed secret is CRITICAL (tracked) or HIGH (untracked), never suppressed.

### Phase 7: Needs-Approval Review [--ask, needs_approval > 0]

Default: items resolve by best judgment (`fixed` or `failed`), except items matching the publish/irreversible exception list, which become `skipped (only you can do)`. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → forced binary re-prompt per item; no response → mark `skipped (no response)` and proceed.

### Mechanical Done Gate

This skill's five passes ARE the project's `{check-cmd}` — the gate is self-referential but explicit: after all mutating scopes, re-run every mutated scope's check command once (per-scope greens can compose into a red, e.g. a lint auto-fix breaking the type graph). The aggregate commands + observed outputs are the Completion Evidence. Residual red in any scope → status `WARN`/`FAIL` with counts, never `OK`; the summary names the follow-up owner (code-level fixes → `/ds-review`; host-wide enforcement → `/ds-quality`, offered once when no arm is installed). Baseline red predating this run is reported red-at-baseline, never silently inherited.

### Phase 8: Summary

Per-scope status table `| Scope | Status | Details |` — one row per scope in run order (L10n/Format/Lint/Typecheck/Security), each with its count or message. Status legend: ✓ pass, ✗ issues found, ⊘ not applicable, ⚠ tool unavailable (skipped).

`ds-fix: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Disposition accounting — totals balance.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} hardcoded secrets intercepted in {scope-paths} — credentials no longer leak into git history on next commit`
- `{n} type errors surfaced in `{module-path}` — runtime crashes prevented before users hit them`

Zero-issue run: `No changes — {detected-stacks} pass all enabled scopes`.

**Gate:** Summary table emitted + Effect block. If fails → any scope missing from the table → add with `⊘ (skipped, detail: not reached)`, re-emit as `WARN`; ds-fix is state-exempt, so re-run the skill to retry skipped scopes.

## Quality Gates

- Format runs before lint — never reverse the order
- Post-fix re-verification is owned by each scope's in-phase re-check plus the Mechanical Done Gate's aggregate run — the observed output is the evidence. `--check` mode: report only; zero modifications proven by identical `git status --porcelain` output before and after.
- Scope boundary: only run scopes requested (or all if none specified).
- **Secrets — tracked file is CRITICAL, untracked is HIGH** (Phase 6a) — never auto-fix, always report. Tracked: "rotate this credential immediately, then add the variable name (placeholder value) to `.env.example`". Untracked: "add to `.gitignore` before it is ever committed" ([../core/secret-patterns.md](../core/secret-patterns.md)).
- **Regression-test gate:** fix touches security-critical or business-logic code and no regression test covers the affected path → add MEDIUM finding `regression test missing for {file}:{line} fix path` before completing ([../core/principles.md §7](../core/principles.md)).
- **CRITICAL escalation:** any CRITICAL secret finding re-verified before reporting — re-read file ±20 lines, check skip patterns (`# noqa`, test fixtures, generated files, env-loader patterns). Insufficient evidence → downgrade to HIGH.
- **Educational output triple:** every applied fix includes `why:` (impact if unfixed), `avoid:` (anti-pattern), `prefer:` (correct pattern) beside "what changed". Single-line counts/messages exempt.
- **needs_approval reason validator:** parse every `skipped` / `needs-approval` reason against the reject list in [../core/principles.md §11](../core/principles.md). Match → reason rejected, item re-routed. Status `OK` forbidden while any rejected-reason item remains.
- W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Severity

One home: [`../core/severity-score-categories.md`](../core/severity-score-categories.md) — format/lint/type/dependency/secret findings map onto that same four-level set; never re-derive a local scale.

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Unknown stack | Run security scope only (universal), skip others |
| Multiple stacks in monorepo | Detect all, run each stack's tools in its subdirectory |
| Tool not installed | Tool Install Policy (above) — warn once per tool, skip, continue |
| Formatter and linter conflict | Formatter wins (runs first), linter adapts |
| No l10n framework / no type checker | Skip that scope silently |
| `--check` with `--scope=format` | Run format check only, exit code = pass/fail |
| Large repo (>10K files) | Default file filtering, don't override excludes |
| Pre-existing config (`.eslintrc`, `ruff.toml`, etc.) | Respect project config — never override with defaults |
| Lock file conflict | Warn, skip dependency operations |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
