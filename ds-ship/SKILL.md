---
name: ds-ship
description: Audit and improve a whole project to production quality — detect what the project is, check every area that applies against named standards, fix what is safe, verify with the project's own checks, and report. Use for an end-to-end project review, "make this production ready", or a focused pass with --focus.
---

# /ds-ship

Audit the whole project, fix what is safe, prove it with the project's own checks, and leave one report. Every step follows [kernel.md](../core/kernel.md) — read it first; this file adds only what is specific to a project-wide pass.

## Input

| Flag | Effect |
|------|--------|
| *(none)* | Every area whose signal holds; fixes applied; decisions by judgment, recorded |
| `--focus=<area>[,<area>]` | Only the named areas from [rules/README.md](../core/rules/README.md) (e.g. `security,a11y`) |
| `--preview` | Detect and plan only; no file changes, no commits |
| `--ask` | Each decision point becomes a question with a recommended option (kernel §5) |
| `<path>` | Run on one package of a monorepo; without it, each package with its own manifest is a unit |

## Done when

`ds/audit/report.md` exists; every area is `ran` or `N/A — reason`; every finding has a disposition (kernel §4) and the totals balance; `{check-cmd}` is no redder than at baseline, shown by its output.

## Steps

### 1. Prepare

1. `git status --porcelain` → files with uncommitted user changes are not edited (kernel §3).
2. Read project rules first: `AGENTS.md`, `CLAUDE.md`, `README*`, `CONTRIBUTING*`, ADRs, specs. They override this file and the rule files where they differ.
3. Previous run: `ds/audit/findings.md` exists → load it. Open findings are re-verified, not re-detected; `fixed` ones are spot-checked once.
4. Add `ds/audit/` to `.git/info/exclude` (not `.gitignore`) so the run leaves no tracked footprint.

### 2. Signals and areas

1. Resolve the `Signals:` line per [signals.md](../core/signals.md) from files and manifests only.
2. Map signals to areas with [rules/README.md](../core/rules/README.md); `--focus` narrows the set. Each excluded area gets one line: `N/A — {key}=none`.
3. `size=large` → order work by hotspots: files with the most commits in the last year (`git log --since=1.year --name-only`) × size. Read the hottest first; stop an area when new findings stop appearing.

### 3. Baseline

Resolve `{check-cmd}` from [toolchains.md](../core/toolchains.md) for each detected stack; run it once; record pass/fail per step with output. Red at baseline is reported as red-at-baseline, never inherited as green. No runnable check → a `Verification gap` finding (HIGH), and fixes in that unit are limited to Category A.

### 4. Detect

Per area, in the README order, cheapest first:

1. **Tools** — run what is already installed: linters and type checkers in check mode, the test suite, `npm audit`/`pip-audit`/`cargo audit`-class advisories, `gitleaks`/`semgrep` when present. Tool output is a finding source, not the verdict; confirm each hit by reading the line.
2. **Rules** — load the area's rule files; apply each rule's Detect to the project; skip a rule whose `applies_when:` fails.
3. **Judgment** — what no rule names but breaks, misleads, or costs more than it gives. Cite the principle (kernel §7) or standard it rests on.

Every candidate passes kernel §1 steps 1-3 before it is recorded: real need? already solved elsewhere? would deleting something resolve it? Record in `ds/audit/findings.md`:

```
| # | Sev | Area | Rule / principle | file:line | Finding | Plan | Disposition |
```

### 5. Plan

Order by impact/effort (kernel §2). For each finding run all six steps of kernel §1 and write the simplest fix in the Plan column. Category A → apply; Category B → decide from impact, effort and risk and record why (kernel §4). Same root cause across findings → one fix.

`--preview` stops here and writes the report.

### 6. Fix

One unit at a time: one change → the narrowest check that covers it (format → lint → type → targeted test) → one local commit (`type(scope): summary`, Conventional Commits). A bug fix lands behind a test observed red on the unfixed code (kernel §3). Still red after 3 attempts → revert the unit, record `reverted` with the error, continue.

### 7. Verify

Run the full `{check-cmd}`. Compare with the baseline step by step. A step that turned red → fix or revert the unit that caused it. Re-read the `file:line` of every `fixed` finding to confirm the change is there.

### 8. Report

Write `ds/audit/report.md`, then print its first block:

```
ds-ship: OK|WARN|FAIL|INCOMPLETE | findings {n} · fixed {n} · open {n} · only-you {n}
Signals: {line}
Areas: {area} ran · {area} N/A — {reason} · …
Checks: {check-cmd step} baseline→now (pass/fail) · …
Since last run: new {n} · fixed {n} · still open {n}      (omit on first run)
```

Then the findings table grouped by severity, and the closing block of kernel §6. `OK` = no open CRITICAL/HIGH and checks no redder than baseline; `WARN` = open HIGH or a verification gap; `FAIL` = open CRITICAL or a check newly red; `INCOMPLETE` = a step did not run.

## Notes

- Parallel areas: when the host can run subagents, one per area for steps 4-5, each given kernel.md and its rule files only; fixes stay sequential in this run.
- No commit-time or stop-time gate in the project → a finding in the `ci` area; the `ds-quality` skill installs one.
- Publishing, pushing, releases and anything needing a human-only value stay `Only you can do` with the exact command (kernel §5).
