---
name: ds-fix
description: Universal code quality fix — format, lint, type-check, l10n, and security scan for any stack. Use when the user asks to fix code quality, run formatters/linters/type-checks, or scan for secrets.
---

# /ds-fix

AI assistants skip formatting, ignore lint errors, and never run type checks. This skill runs all five quality passes in the correct order and verifies the result.

**Universal Code Quality Fix** — Format, lint, type-check, l10n, and security scan for any stack.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-fix`, asks to format code, run linters / fix lint errors or code quality issues, run type checker / fix type errors, scan for secrets, or audit dependencies

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "run formatter, linter, type checker", "fix lint errors" | "review architecture / patterns" (→ ds-review --strategic) |
| "scan for hardcoded secrets / dep CVEs" | "full regulatory security audit" (→ ds-compliance --security) |
| "format + l10n consistency check" | "generate translations / new locales" (→ manual / external) |
| "fix all auto-fixable issues across stack" | "design a new API" (→ ds-backend) |

## Contract

**Dimensions:** B1 (fix), A8 (mechanical), C1 (mechanical)

- Runs automated fixers in safe, deterministic order: l10n → format → lint → typecheck → security. Mutating scopes first (l10n, format, lint auto-fix), read-only verification after (typecheck validates the post-fix state) — same canonical order as the ds-quality gate (format → lint → type).
- `--check` mode: report only, zero modifications.
- Missing tools skipped with a warning — never fails due to absent optional tooling.
- Re-validates after fix to confirm fix worked. Reports counts, not verbose output.
- Does NOT perform manual code review, architecture analysis, or refactoring.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** tool-driven, fast, independent passes — re-running repeats idempotent fixes. No `ds/audit/fix.json` written.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Fix all scopes |
| `--check` | Report only, no modifications |
| `--scope=X,Y` | Specific scope(s), comma-separated |
| `--skip-if-clean` | Run only scopes whose check-mode reports issues. Default `true` when invoked by another skill (ds-commit / ds-pr / ds-ship gates), `false` when user-invoked. |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

## Scopes

| Scope | What It Does |
|-------|-------------|
| `format` | Apply code formatter |
| `lint` | Run linter with auto-fix |
| `typecheck` | Run static type checker |
| `l10n` | Generate/validate localization files |
| `security` | Secret pattern scan + dependency audit |

Default: all five scopes in order.

## Delegation

**Owns:** format, lint, typecheck, l10n, secret-scan-quick, dep-quick-check | **Delegates:** ds-deps → deps-upgrade-execution; ds-review → code-level quality fixes | **Receives:** ds-commit → pre-commit gates; ds-pr → pre-PR gates; ds-issue → format/lint/type passes during issue execution; ds-quality → verify-loop toolchain passes; ds-ship → Phase 2 rule audit

## Tool Install Policy (applied to every scope below)

Scope tool (formatter, linter, typecheck binary, l10n generator, audit command) unavailable → apply one flow for every scope, stated once here:

| Case | Action |
|------|--------|
| Installable tool missing | Show install command (e.g., `{install-command-for-tool}`), ask **"Install and continue?"** — accept → install + re-run scope; decline → mark scope `⚠ Skipped (tool unavailable, declined install)`, continue to next scope. **Under `--auto`:** no ask — resolves per Unattended Mode rule 3: install (after Trust Verification — registry-published, non-trivial age) and re-run the scope; install blocked by missing system/sudo permissions → `needs-human`, scope marked `skipped` |
| System-level tool missing (e.g., `{compiler-or-runtime}`) | Show manual install instructions, skip scope |
| Filesystem access error | Mark scope `WARN` with the specific OS error |

## Execution Flow

Detection → [L10n] → [Format] → [Lint] → [Typecheck] → [Security] → [Needs-Approval] → Summary

### Phase 1: Stack Detection

1. **IDU:** Profile → Toolchain, Type+Stack. Absent → own detection.

Detect stacks in two tiers. Multiple stacks may coexist (e.g., monorepo).

**Tier 1 — Primary stacks** (full toolchain: format + lint + typecheck + security):

| Manifest | Stack |
|----------|-------|
| `pubspec.yaml` | flutter |
| `package.json` | node |
| `pyproject.toml` / `setup.py` / `requirements.txt` | python |
| `go.mod` | go |
| `Cargo.toml` | rust |
| `build.gradle` / `build.gradle.kts` / `pom.xml` | jvm |
| `Package.swift` / `*.xcodeproj` | swift |
| `*.csproj` / `*.sln` | dotnet |
| `Gemfile` | ruby |
| `composer.json` | php |
| `mix.exs` | elixir |
| `build.sbt` | scala |

**Tier 2 — Supplementary stacks** (applicable tools only, never sole detected stack):

| Signal | Stack | Activation condition |
|--------|-------|----------------------|
| `CMakeLists.txt` / `Makefile` | c-cpp | Only if `.c/.cpp/.cc/.h` source exists in `src/` or root. `Makefile` without C/C++ sources = task runner only — skip. |
| `*.sh` files | shell | Only if 3+ `.sh` files OR `scripts/` with `.sh` files. A single `setup.sh` does not make this a shell project. |
| `*.tf` files | terraform | High confidence — unique extension. Treat as primary if no other stack. |
| `Dockerfile` / `docker-compose.yml` | docker | Always supplementary. Run hadolint/trivy alongside primary stack. |

**Disambiguation:**

| Detected | Action |
|----------|--------|
| Tier 2 only (e.g., Dockerfile + shell) | Run security scope universally; Tier 2 tools for their files only |
| Tier 1 + Tier 2 | Full toolchain for Tier 1; supplementary tools for Tier 2 |
| `*.tf` only | Treat as primary (IaC project) |

Per stack: load toolchain from [references/toolchains.md](references/toolchains.md).

**Gate:** ≥1 stack detected or security-only mode. If fails → no manifests; run security scope only (universal secret scan + dep audit where available), announce "No stack detected — running security scope only", skip other scopes.

**Checkpoint [fix mode — N/A under `--check`]:** before the first mutating scope, run `git status --porcelain` → non-empty → interactive: ask **Commit first (recommended) / Stash / Proceed anyway** (risk stated: fixer edits interleave with uncommitted work, single-command rollback is lost); `--auto`: proceed only when the pre-existing dirty state stays untouched by this skill's writes — otherwise stop and record `needs-human`. Never run a bulk fix over uncommitted unrelated changes silently. Empty output → clean tree, proceed.

### Phase 2: L10n [scope: l10n]

Run these steps in order:

| Step | Action |
|------|--------|
| Detect framework | Read project config + dependencies |
| Generate | Localization files if stack supports it (e.g., `{l10n-generator-command}`) |
| Cross-check keys | Every locale file MUST carry the same keys as the base locale |
| Placeholder consistency | Every `{placeholder-token}` in base MUST exist in all translations |
| Encoding | Detect mojibake (cp1252→UTF-8 double-encoding) |

**Fix mode:** generate files, stage generated output. **Check mode:** report mismatches only.

L10n frameworks per stack:

| Stack | Framework | Key files |
|-------|-----------|-----------|
| flutter | flutter_localizations / gen-l10n | `lib/l10n/*.arb` |
| node | i18next / react-intl / next-intl | `locales/*.json`, `messages/*.json` |
| python | gettext / babel | `*.po`, `babel.cfg` |
| jvm | Android resources / Spring messages | `res/values-*/strings.xml`, `messages_*.properties` |
| swift | NSLocalizedString / String Catalogs | `*.lproj/*.strings`, `*.xcstrings` |
| dotnet | resx | `Resources/*.resx` |
| ruby | rails-i18n | `config/locales/*.yml` |
| php | Laravel lang / Symfony translations | `lang/*.php`, `translations/*.yaml` |
| c-cpp | gettext | `*.po`, `*.pot` |
| elixir | Gettext | `priv/gettext/*.po` |
| scala | Play i18n / Java ResourceBundle | `conf/messages.*`, `*.properties` |

No framework detected → skip silently.

**Gate:** L10n files generated/validated, or no framework. If fails → tool unavailable: apply Tool Install Policy; persistent key mismatches after one fix attempt → report mismatched keys, mark scope `WARN`, don't abort.

### Phase 3: Format [scope: format]

Look up format tool from `references/toolchains.md`. **Fix mode:** run fix command. **Check mode:** run check command, report exit code. Non-default formatter (e.g., `{alt-formatter}` instead of `{default-formatter}`) → detect from config files and use that.

**Gate:** Format clean before proceeding to lint. If fails → tool unavailable: apply Tool Install Policy; formatter exits non-zero after run → report file count, proceed to lint (don't block pipeline on residual format issues).

### Phase 4: Lint [scope: lint]

Look up lint tool from `references/toolchains.md`. **Fix mode:** run fix command, then re-run check to verify. **Check mode:** run check command only, report issues. Non-default linter → detect from config and use that.

**Stack-specific extra checks** (content-based, not tool-dependent):

| Stack | Pattern | Where | Suggestion |
|-------|---------|-------|------------|
| flutter | `print(` | outside test files | Use structured logger (e.g., `{logger-class}`) |
| node | `console.log` | in `src/` | Use structured logger |
| python | `print(` | in `src/` | Use `logging` module |
| go | `fmt.Println` | in non-main packages | Use structured logger (e.g., `slog`) |
| ruby | `puts` / `p ` | in `app/` / `lib/` | Use `Rails.logger` or structured logger |
| php | `var_dump` / `dd(` | in `src/` / `app/` | Use structured logger |
| c-cpp | `printf(` / `cout <<` | in `src/` (not main) | Use structured logger (e.g., `spdlog`) |
| elixir | `IO.inspect` / `IO.puts` | in `lib/` | Use `Logger` module |
| scala | `println` | in `src/main/` | Use structured logger (e.g., `slf4j`) |

**Complexity thresholds (linter-owned, not hand-audited):** enable these in the stack's linter config (tool per `references/toolchains.md`) so the check is mechanical and runs on every pass. Linter offers no complexity rule → report the gap once under Tool Install Policy and move on; never substitute a manual read-through.

| Metric | Threshold |
|--------|-----------|
| Cyclomatic complexity | ≤ 15 |
| Function / method length | ≤ 50 lines |
| File length | ≤ 500 lines |
| Nesting depth | ≤ 3 |
| Parameters | ≤ 4 |

Existing config already sets a different threshold → keep the project's value, report the delta; the project's own convention wins.

**Spell check (advisory, all stacks):** `typos` binary present → run `typos` (fix mode: `typos -w`), report correction count — its known-misspellings design keeps false positives low even on large repos; absent → skip silently (optional sub-check, exempt from Tool Install Policy prompting).

**Gate:** Lint re-check passes after auto-fix, or check-mode issues reported. If fails → tool unavailable: apply Tool Install Policy; unfixable errors after auto-fix → report residual count + file:line each, mark scope `WARN`, proceed to typecheck (don't re-run lint).

### Phase 5: Typecheck [scope: typecheck]

Look up typecheck tool from `references/toolchains.md`; detect if type checking is configured (e.g., `tsconfig.json` for Node, type hints in Python) — none configured → skip silently. Run type checker (read-only — reports but doesn't auto-fix) on the post-fix state, so its verdict covers what format + lint actually left on disk; report error count + top issues.

**Gate:** Type checker reports zero errors, or no type checker configured. If fails → tool missing: apply Tool Install Policy; type errors un-fixable (read-only checker) → record error count, proceed to security (type errors don't block subsequent scopes).

### Phase 6: Security [scope: security]

**6a. Secret scan (all stacks):** search project files for these patterns, excluding `.git/`, `node_modules/`, `build/`, `dist/`, `.dart_tool/`, `vendor/`, `__pycache__/`, `bin/`, `obj/`, `_build/`, `deps/`, `.terraform/`, `target/`:

| Pattern | Description |
|---------|-------------|
| `AKIA[0-9A-Z]{16}` | AWS access key |
| `(api_key\|api_secret\|secret_key\|access_token\|auth_token\|password)\s*[=:]\s*["'][^"']{8,}` | Generic secrets |
| `-----BEGIN.*PRIVATE KEY-----` | Private keys |
| `sk-[A-Za-z0-9_-]{20,}` | OpenAI / Anthropic API key (covers `sk-proj-…`, `sk-ant-…`) |
| `sk_(live\|test)_[A-Za-z0-9]{10,}` | Stripe secret key |
| `AIza[0-9A-Za-z_-]{35}` | Google API key |
| `ghp_[a-zA-Z0-9]{36}` | GitHub PAT (classic) |
| `github_pat_[A-Za-z0-9_]{22,}` | GitHub PAT (fine-grained) |
| `xox[baprs]-[a-zA-Z0-9-]+` | Slack token |

**Scanner augmentation (advisory):** `gitleaks` present → run it alongside the patterns above (rule-first, sub-second on typical diffs) and merge findings; `trufflehog` present → offer a verified deep scan for CRITICAL triage (its verifier modules distinguish live credentials from expired ones); neither present → the built-in patterns above stand alone as the zero-dependency baseline.

**6b. Dependency audit (per stack):** look up audit command from `references/toolchains.md`. Tool unavailable → skip with warning. Stack toolchain lists a source security scanner (e.g. Bandit for Python) → run it read-only alongside the dep audit, merge findings.

**6c. Debug residue & temp-file discipline (advisory, all stacks):**
- **Debug endpoints:** grep route registrations whose path literal matches `/(debug|__test|_internal)` outside test directories → flag each for manual review, never auto-remove. Honesty note: this class is explicitly not amenable to complete static analysis (CMU SEI) — the grep narrows candidates, a human confirms intent.
- **Temp files in shell scripts:** hardcoded `/tmp/<name>` paths or `$$`-based temp names → propose `TMPFILE=$(mktemp)` (mode 600, unpredictable name — closes the symlink-attack window) with `trap 'rm -f "$TMPFILE"' EXIT` set immediately after creation so cleanup fires on every exit path, not just normal completion.

**Gate:** Secret scan + dep audit completed with classifications. If fails → dep audit tool missing: skip dep sub-phase, warn in summary; secret scan is built-in pattern matching (no external tool) and must always complete — filesystem access error → mark scope `WARN`. Any confirmed secret = CRITICAL, never suppressed.

### Phase 7: Needs-Approval Review [needs_approval > 0]

**Under `--auto`:** no review step is shown — items resolve per Unattended Mode rule 3 (`fixed` or `failed`), except items matching the irreversible-exception list, which become `skipped (needs-human)`. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → forced binary re-prompt per item; no response → mark `skipped (no response)` and proceed.

### Mechanical Done Gate

This skill's five passes ARE the project's `{check-cmd}` — the gate here is self-referential but still explicit: after all mutating scopes, re-run every mutated scope's check command once (aggregate re-verify — per-scope greens can compose into a red, e.g. a lint auto-fix that breaks the type graph). The aggregate run's exact commands + observed outputs are the Completion Evidence. Residual red in any scope → status is `WARN`/`FAIL` with the counts, never `OK` — and the summary names the follow-up owner (code-level fixes → `/ds-review`; permanent enforcement so red blocks "done" host-wide → `/ds-quality`, offered once when no enforcement arm is installed). Baseline red that predates this run is reported as red-at-baseline, never silently inherited.

### Phase 8: Summary

Per-scope status table `| Scope | Status | Details |` — one row each in run order: L10n ({count or message}), Format ({files-fixed} fixed), Lint ({issues-found} issues), Typecheck ({errors-found} errors), Security ({findings} findings). Status legend: ✓ = pass, ✗ = issues found, ⊘ = not applicable, ⚠ = tool unavailable (skipped).

`ds-fix: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Disposition accounting — totals balance.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} hardcoded secrets intercepted in {scope-paths} — credentials no longer leak into git history on next commit`
- `{n} type errors surfaced in `{module-path}` — runtime crashes prevented before users hit them`
- `{n} format violations auto-fixed across {n} files — diff-noise eliminated on next code review`

Zero-issue run: `No changes applied — {detected-stacks} pass all enabled scopes`.

**Gate:** Summary table emitted + Value Delivered block. If fails → any scope missing from the table → add with `⊘ (skipped, detail: not reached)`, re-emit as `WARN`; ds-fix is state-exempt, so re-run the skill to retry skipped scopes.

## Quality Gates

- Format runs before lint — never reverse this order
- Post-fix re-verification is owned by each scope's in-phase re-check plus the Mechanical Done Gate's aggregate run — that command's observed output is the evidence; no separate prose re-check. `--check` mode: only report; zero modifications proven by `git status --porcelain` output identical before and after the run.
- Scope boundary: only run scopes user requested (or all if none specified).
- **Secrets always CRITICAL** — never auto-fix, always report. Surface rotation guidance: "rotate this credential immediately, then add the variable name (placeholder value) to `.env.example`" ([references/principles.md §8](references/principles.md)).
- **Regression-test gate:** fix modifies security-critical or business-logic code → check if a regression test exists for the affected path; if absent, add MEDIUM finding `regression test missing for {file}:{line} fix path` before completing ([references/principles.md §7](references/principles.md)).
- **CRITICAL escalation (second-pass verification):** any CRITICAL secret finding re-verified before reporting — re-read file ±20 lines, check skip patterns (`# noqa`, test fixtures, generated files, env-loader patterns). Insufficient evidence → downgrade to HIGH. CRITICAL reserved for confirmed exposures.
- **Educational output triple:** every applied fix includes three lines beside "what changed": `why:` (impact if unfixed), `avoid:` (anti-pattern), `prefer:` (correct pattern). Single-line counts/messages exempt — applies to per-finding fix records.
- **needs_approval reason validator:** parse every `skipped` / `needs-approval` reason against the reject list in [references/principles.md §12](references/principles.md). Match → reason rejected, item re-routed (fix inline or escalate). Status `OK` forbidden while any rejected-reason item remains.
- W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Exposed secrets, known vulnerable dependencies |
| HIGH | Type errors, lint errors that affect correctness |
| MEDIUM | Format violations, lint warnings |
| LOW | Style suggestions, outdated dependencies without CVEs |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Unknown stack | Run security scope only (universal), skip others |
| Multiple stacks in monorepo | Detect all, run each stack's tools in its subdirectory |
| Tool not installed | Tool Install Policy (above) — warn once per tool, skip, continue |
| Formatter and linter conflict | Formatter wins (runs first), linter adapts |
| No l10n framework | Skip l10n silently |
| No type checker | Skip typecheck silently |
| `--check` with `--scope=format` | Run format check only, exit code = pass/fail |
| Large repo (>10K files) | Default file filtering, don't override excludes |
| Pre-existing config (`.eslintrc`, `ruff.toml`, etc.) | Respect project config — never override with defaults |
| Lock file conflict | Warn, skip dependency operations |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
