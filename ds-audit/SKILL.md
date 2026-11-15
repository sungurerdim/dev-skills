---
name: ds-audit
description: Audit and improve a project to production quality — detect what the project is, check every area that applies against named standards, fix what is safe, verify with the project's own checks, and report. Use to review and fix what the current branch changes (the default), for an end-to-end audit with `all` ("make this production ready"), or for named areas such as `sec a11y`.
argument-hint: '[all] [sec|privacy|auth|api|db|arch|code|test|perf|web|a11y|ux|i18n|mobile|store|money|ci|ops|docs|repo ...] [dry] [ask] [<path>]'
---

# /ds-audit

Audit what the branch changes (or, with `all`, the whole project), fix what is safe, prove it with the project's own checks, and leave one report. Every step follows [kernel.md](../core/kernel.md) — read it first; this file adds only what is specific to an audit pass.

## Input

| Word | Effect |
|------|--------|
| *(none)* | Every area whose signal holds, on what this branch changes (below); fixes applied; decisions by judgment, recorded |
| `all` | The whole project: the weekly, monthly or pre-release audit |
| area words | Only those areas, each runnable alone: `sec` `privacy` `auth` `api` `db` `arch` `code` `test` `perf` `web` `a11y` `ux` `i18n` `mobile` `store` `money` `ci` `ops` `docs` `repo` ([rules/README.md](../core/rules/README.md)) |
| `dry` | Detect and plan only; no file changes, no commits |
| `ask` | Each decision point becomes a question with a recommended option (kernel §5) |
| `<path>` | One package of a monorepo; without it, each package with its own manifest is a unit |

**Changed scope (default)** — files changed in `{base}...HEAD` plus uncommitted and untracked ones; `{base}` = the freshly fetched upstream, else `origin/HEAD`; no remote → uncommitted files only, said in the report. Findings only on changed lines or code they break (callers, contracts, covering tests); checks still run whole-project. No changed file → report `nothing changed — /ds-audit all audits the whole project` and stop. Uncommitted files are edited too, under kernel §3's snapshot; fixes there stay uncommitted and are listed for review with `git diff`.

## Done when

`ds/audit/report.md` exists; every fixer that applies has run (step 4); every area is `ran` or `N/A — reason`; every finding has a disposition (kernel §4) and the totals balance; `{check-cmd}` is no redder than at baseline, shown by its output.

## Steps

### 1. Prepare

1. **Current code, one command:** `git fetch --prune` (read-only), then `git status --porcelain=v2 --branch -uall` (branch, upstream, ahead/behind, changed files) and, unless `all`, `git diff --name-status -M {base}...HEAD`. Behind and not diverged → `git merge --ff-only @{u}` (no history rewrite; git refuses rather than overwrite local edits). Diverged → never rebase or pull automatically (a pushed branch would need a force-push, kernel §5): audit against the fetched base, report `diverged: behind {n}, ahead {m}`, and list the files that would conflict from `git merge-tree --write-tree HEAD @{u}` (git ≥ 2.38; changes nothing). With `all`, files with uncommitted user changes are not edited (kernel §3).
2. Read project rules first, in one batch: `AGENTS.md`, `CLAUDE.md`, `README*`, `CONTRIBUTING*`, ADRs, specs. They override this file and the rule files where they differ.
3. Previous run: `ds/audit/findings.md` exists → load it. Open findings in scope are re-verified, not re-detected; `fixed` ones are spot-checked once.
4. Add `ds/audit/` to `.git/info/exclude` (not `.gitignore`) so the run leaves no tracked footprint.

### 2. Signals and areas

1. Resolve the `Signals:` line per [signals.md](../core/signals.md) from files and manifests only.
2. Map signals to areas with [rules/README.md](../core/rules/README.md); area words narrow the set; a named area runs even when its signal does not hold. Each excluded area gets one line: `N/A — {key}=none`. Without `all`, an area runs only if a changed file falls in it.
3. `size=large` → order work by hotspots: files with the most commits in the last year (one call: `git log --since=1.year --name-only --format=`) × size. Read the hottest first; stop an area when new findings stop appearing.

### 3. Baseline

Resolve `{check-cmd}` from [toolchains.md](../core/toolchains.md) for each detected stack; run it once; record pass/fail per step with output. Red at baseline is reported as red-at-baseline, never inherited as green. No runnable check → a `Verification gap` finding (HIGH), and fixes in that unit are limited to Category A.

### 4. Auto-fix — tools first, judgment after

1. **Fixers** — the project's own fix scripts (`format`, `lint:fix`, Makefile `fix`, `pre-commit run`), else the Fix column of toolchains.md: formatter, then the linter's safe autofix. Never `--unsafe-fixes`, `-A` or a dependency change.
2. **Scope** — the changed files as arguments where the tool takes paths, else the project; uncommitted files under kernel §3's snapshot.
3. **One commit per fixer** (`style: apply {tool} fixes`), then the baseline's test step again: a test that turned red → revert that fixer's commit and record it.
4. **Re-run the checks**; what stays red feeds step 5's Tools pass.

`dry` runs fixers in check mode and reports what they would fix.

### 5. Detect

Per area, in the README order, cheapest first:

1. **Tools** — what step 4 left red (lint, type and test output), plus installed scanners: `npm audit`/`pip-audit`/`cargo audit`-class advisories, `gitleaks`/`semgrep` when present. Tool output is a finding source, not the verdict; confirm each hit by reading the line.
2. **Rules** — load the area's rule files; apply each rule's Detect to the project; skip a rule whose `applies_when:` fails.
3. **Judgment** — what no rule names but breaks, misleads, or costs more than it gives. Cite the principle (kernel §7) or standard it rests on.

Every candidate passes kernel §1 steps 1-3 before it is recorded: real need? already solved elsewhere? would deleting something resolve it? Record in `ds/audit/findings.md`:

```
| # | Sev | Area | Rule / principle | file:line | Finding | Plan | Disposition |
```

### 6. Plan

Order by impact/effort (kernel §2). For each finding run all six steps of kernel §1 and write the simplest fix in the Plan column. Category A → apply; Category B → decide from impact, effort and risk and record why (kernel §4). Same root cause across findings → one fix.

`dry` stops here and writes the report.

### 7. Fix

One unit at a time: one change → the narrowest check that covers it (format → lint → type → targeted test) → one local commit (`type(scope): summary`, Conventional Commits); in a file that had uncommitted user edits, no commit (Changed scope above). A bug fix lands behind a test observed red on the unfixed code (kernel §3). Still red after 3 attempts → revert the unit (kernel §3), record `reverted` with the error, continue.

### 8. Verify

Run the full `{check-cmd}`. Compare with the baseline step by step. A step that turned red → fix or revert the unit that caused it. Re-read the `file:line` of every `fixed` finding to confirm the change is there.

### 9. Report

Write `ds/audit/report.md`: the closing message first, then `Signals: {line}`, `Areas: {word} ran · {word} N/A — {reason} · …`, each check baseline → now, every finding, and since the last run: new · fixed · still open. Print the closing message (kernel §6):

- counts: `scope {changed: n files|all} · auto-fixed {n} files · findings {n} · fixed {n} · open {n} · only-you {n}`
- Change table: an `auto-fix` row, then the rest of the code
- Effect: each check baseline → now; new / fixed / still open since the last run

`OK` = no open CRITICAL/HIGH and checks no redder than baseline; `WARN` = open HIGH or a verification gap; `FAIL` = open CRITICAL or a check newly red; `INCOMPLETE` = a step did not run.

## Notes

- Parallel areas: with subagents, one per area for steps 5-6, given kernel.md and its rule files only; fixes stay sequential.
- No commit-time or stop-time gate in the project → a finding in the `ci` area; the `ds-gate` skill installs one.
- Publishing, pushing, releases and anything needing a human-only value stay `Only you can do` with the exact command (kernel §5).
