# Phases — the one contract every ds-audit phase follows

Every phase has the same input, steps, output and error handling. `audit.py` (in `../assets/`) does every countable step; the model reads, judges, fixes and writes rows. Terms (severity, disposition, Category A/B, principles) are defined once in [kernel.md](../../core/kernel.md); this file adds only what is specific to phases.

## Phases

Order = what changes the code the next phase audits. A phase runs the areas its signals load ([rules/README.md](../../core/rules/README.md)).

| Phase | Areas | May change | Ends when |
|-------|-------|------------|-----------|
| lean | `rules` `lean` | rule files, `SCOPE.md`, cuts and merges | every recorded rule and unit has a decision; `audit.py lean-check` green; every file on its reading list read |
| build | `arch` `code` `test` `perf` | code and tests (fixers run first, once) | every file on its reading list read, `validate` green, no `open` row, `checks now` no redder than baseline |
| safe | `sec` `privacy` `auth` `api` `db` | code, config, tests | same |
| surface | `web` `a11y` `ux` `i18n` `mobile` `store` `money` | code, copy, assets | same |
| ship | `ci` `ops` `docs` `repo` | CI, release, deploy config, docs | same; docs describe the final state; the changelog's unreleased part names every user-visible commit of `git log --oneline {last tag}..HEAD` (last tag: `git describe --tags --abbrev=0`) |

## Steps — identical in every phase

1. **Inventory** — `audit.py scan {phase}`: runs each loaded rule's `Mech:` commands. `hit` = candidate, `clean` = rule passes, `tool absent` = that rule falls back to its Detect text, never to a pass; `not applicable` = the rule's `applies_when:` excludes this project's signals, so its command is not run.
2. **Detect** — S hits: read 3 lines around each, record. T hits: read the code; record only the real ones. M rules: apply their Detect. Then **read every file on the phase's reading list in full** (Coverage, below) and apply the phase's loaded rules and judgment to it: what no rule names but breaks, misleads or costs more than it gives (cite a kernel §7 principle). Changed scope: the list is the changed files; findings only on changed lines and the code they break. Every candidate passes kernel §1 steps 1-3 first.
3. **Decide** — kernel §1 all six steps → the simplest fix in `Plan`; same root cause → one fix. **Every finding whose fix a test or check can prove is fixed** — Category B too, decided on evidence and noted `decided:`. Only two things are not applied: the kernel §5 never-performed items (`only you can do (exact command)`) and a choice only the owner can make — a policy (who may see a secret, what is collected), a public contract others depend on (published API, CLI, file format), a business or legal value — which becomes one `decide:` line with options and a recommendation (Output). "Open an issue", "needs discussion", "large", "a project rule prefers later" are not dispositions: fix it, or write the `decide:` line. Write each row the moment its finding is decided (as `open` until applied), never in a batch at the phase end: a run cut short resumes from the rows.
4. **Apply** (not in `dry`) — one unit → narrowest check (format → lint → type → targeted test) → one commit `type(scope): summary` → row `fixed` + hash. A bug fix lands behind a test seen red first. A refactor of code no test covers lands behind a characterization test written first and seen green on the unchanged code. Red after 3 attempts → reverse-apply the unit's own diff, row `reverted (error)`.
5. **Verify** — `audit.py checks now`; a step newly red → fix or revert the unit that caused it. `audit.py validate` → green. `audit.py phase {phase} done` (it refuses while a file of the reading list is unread, and runs `lean-check` when `SCOPE.md` exists, refusing on red).

## Coverage — every file is read, by groups, in parallel

`audit.py init` writes the run's reading list (`ds/audit/coverage.json`): every tracked text file a pending phase must read — lean: code and recorded-rule files; build: code and tests; safe: code, config, templates; surface: code, templates and styles; ship: docs, config, rule files. Lockfiles, binaries and files over 1 MiB are listed as not read, by name. A file is read only when `audit.py read {phase} FILE…` says so; an unread file keeps the phase from `done` and the run from anything but INCOMPLETE.

1. `audit.py groups {phase}` packs the unread files into groups of ≤ 2500 lines (a directory together where it fits).
2. One **reviewer** per group, all at once (the host's subagents, in parallel), with the brief below. Without subagents, this context reads the groups one after another.
3. Each reviewer reads every file of its group in full, records `audit.py read {phase} FILE…` for each one it finished, and returns its findings as ledger rows. **No cap** — not on findings, files or lines: a reviewer never stops at a number and never drops a finding to stay short. Out of room → it returns the files it did not finish; they stay unread.
4. This context dedupes the rows (same root cause → one), writes them, applies fixes one unit at a time (one writer to the working tree), then runs `audit.py groups {phase}` again until it prints `[]`.

```
Review group {n} of phase {phase} for /ds-audit {words} in {root}. Read only; do not edit or commit.
Read: kernel.md §1, §3, §4, §7; these rule files: {the phase's loaded files}; the project's agent rules.
Files — read each in full: {group files}
For each finished file run `audit.py --root {root} read {phase} FILE…`.
Return every finding (no limit) as ledger rows: Phase · Sev · Area · Rule · Where · Finding · Prevents · Plan, plus `decide:` lines for owner choices. Then: files not finished.
```

**Fixers** run once, at the start of the first code phase: the project's own fix scripts, else the Fix commands of [toolchains.md](../../core/toolchains.md) (formatter, then the linter's safe autofix; never unsafe fixes; no install, config or dependency change — its "Install and Bootstrap lines" rule); one commit per fixer (`style: apply {tool} fixes`); `checks now` after each — a newly red step reverts that fixer.

**Dependency updates** run once, in ship (area `ci`), never in `dry`: patch and minor updates of direct dependencies, one group per ecosystem with the stack's own command (lockfile updated, no new dependency), one commit per group (`build(deps): update {ecosystem} patch and minor`), `checks now` after each — a newly red step reverts that group and records it. Majors and versions published less than 7 days ago are not applied: each becomes an `only-you` line with its changelog link (DOP-10, DOP-11).

## Output — the ledger language

`ds/audit/report.md`, Findings table; one row per finding, appended by the model; columns in this order:

| Column | Allowed values |
|--------|----------------|
| `#` | next integer |
| Phase | a phase name |
| Sev | CRITICAL · HIGH · MEDIUM · LOW (kernel §4) |
| Area | an area word |
| Rule | a rule ID · a kernel §7 principle (any case; the part before ` / ` suffices: `DRY`) · `tool:{name}` · `judgment`; several joined by ` · `. A standard (the rule index's Standards column) is named in Plan or Prevents, never here |
| Where | `path:line` (checked: the file and line exist now or at the run's start) · `host:{service}/{setting}` for a host or account setting (`host:github/branch-protection`; checked: that form) · a unit · an item |
| Finding | what is wrong — plain words |
| Prevents | what goes wrong without the fix, for whom — plain words |
| Plan | the simplest fix (kernel §1) |
| Disposition | `open` · `fixed` · `reverted (error)` · `skipped (blocker)` · `not applicable (reason)` · `only you can do (action)` |
| Commit | hash for `fixed` (checked: exists, after the run's start) · `uncommitted` (file had user edits) · `—` |

Notes lines: `decide: {question} · options: {a}; {b}[; …] · recommend: {option} — {why}` (a choice only the owner can make, step 3; listed last in the closing message, never cut; `validate` rejects one with fewer than two options), `decided: {decision} · {reason}` (the closing message's five: `decided!:` first, then by the first word of branch · signal · cut/merge/unit · rules · budget · scope · push · check command; `audit.py signal` with the current value writes none) and `only-you: {exact action or command}`, each once; an action already in a row's Disposition is not repeated as a note. A decision is a choice the owner may reverse; scan triage (why a hit is not a finding) goes into the row or nowhere, never into Notes. A cell never contains `|`. Everything else in the file, and `report.html` beside it, is written by `audit.py`.

## Running the phases

- **Changed scope** (no word): every phase in one invocation; lean runs SIM-* on the changed lines and LEAN-11 when `SCOPE.md` exists, not the rules review or the tiering.
- **`all` / a phase word**: `audit.py init` names the next phase. One context runs every phase in order and its reviewers read the files (Coverage). A fresh subagent per phase only when `size=large` or the context runs short, given the handoff below; without subagents the invocation then ends with `next: /ds-audit {words} — continues at {phase}`, the exact words of the run (`init` resumes only the same words, or none; other words start a new run and keep the old report).
- **Handoff** — the whole brief of a phase subagent, filled from `init`'s JSON:

```
Phase {phase} of /ds-audit {words} in {root}; ledger ds/audit/report.md; branch {branch}.
Read: phases.md, kernel.md, SKILL.md, and only these rule files: {the phase's files from core/rules/README.md}.
Facts (do not re-derive): {Signals line} · check: {check} ({check_from}) · scope: {scope} · baseline taken.
Do: Steps 1-5 for {phase}, reading by Coverage until `audit.py groups {phase}` prints []; write each row as it is decided; end with `audit.py phase {phase} done` or `blocked "{reason}"`.
Return: Done (the phase command's output: push result, next) · rows #{first}-#{last} · Not done + why · Scope deviation.
```
- **One review branch**: every phase of an `all`, phase or area run commits on `ds/audit` (`audit.py init` creates or resumes it; the owner's branch is untouched), and `phase … done` pushes it without force — unless push is off: the word `local`, or `audit.py push off "{rule file:line}"` when the project's rules forbid pushing (no stand-in remote). Later phases audit the code lean already cut. The report ends with the merge commands as `only-you`.

## surface — see the running app (optional)

After the static pass, when `ui≠none`: start the app locally (the project's documented dev or preview command; never a deploy, never production data) and open it with the host's browser tool (Playwright, the host's built-in browser). Static or generated pages need no server: open the file directly (`file://…`), generating it first with the project's own command when it is generated output. At a narrow (~400 px) and a wide (~1280 px) viewport check: no horizontal overflow, keyboard focus order and a visible focus ring, contrast (axe when present; otherwise `audit.py contrast FG BG` on the computed colours), and capture the empty, error and loading states of the main flow. Each problem is a row with the screenshot path in its Finding. Cannot start the app, or no browser tool → `decided: visual check skipped — {reason}`; the run is not INCOMPLETE for it. Stop the app afterwards.

## lean

The one interactive phase: scope and recorded rules are owner values (kernel §5). It asks when named (`/ds-audit lean`, `/ds-audit rules`) or with `ask`; inside an unattended `all`, each question becomes a `decide:` line with its options and recommendation, and nothing the owner must decide is applied.

**With `auto`** the recommendation is applied instead of asked, as `decided: {decision} · {evidence} · revert: {command}`, within these limits:
- **Purpose** — derived only from the project's own words (README, spec, issues, agent rules), quoted in `SCOPE.md`; none found → `Purpose: unconfirmed`, and cuts are limited to units with no inbound use and no need named anywhere (no reference, no doc, no issue).
- **Rules** — a rule with a stated reason is kept or reworded, never deleted; delete only a rule that contradicts the purpose or another rule, or names something that no longer exists; a one-moment rule (LEAN-12) is scoped `until {date}` rather than deleted.
- **Units** — `cut` needs zero fan-in confirmed by reading plus no need in the purpose; a unit with users, docs or issues asking for it becomes `T2` (deferred), never cut; `merge` only where LEAN-04 names one reason to change for both.

1. **Rules** — `audit.py rules [--since {Rules reviewed sha}] [--also {spec the rules cite}] [--also {host memory dir}]`. Group lines into decisions (one cluster = one question); order: unreasoned absolutes, most cited, oldest. Ask at most 12 clusters, 4 per round: the rule verbatim, `file:line`, date and the commit subject that added it, what it forces today, its fit with the purpose, and a recommendation — keep · reword (new text) · scope (`until {date or condition}`) · move to a dated decision log · delete. Apply answers as commits on the run's branch. Unasked clusters stay as they are and are listed. LEAN-12.
2. **Purpose** — `SCOPE.md` `Purpose:` and `Done when:`, else proposed from README/spec/issues and confirmed (LEAN-01). A product that is not source code (Markdown skills, data) is named as `Product:` globs in code spans: `audit.py lean` then counts it as product, not docs, and budgets it as `product ≤ n KB`.
3. **Measure** — `audit.py lean`. Write the minimal sketch: the fewest units that meet T0 and T1, reusing platform, stdlib and existing dependencies (LEAN-04).
4. **Tier** — one `SCOPE.md` row per unit: `| Unit | Tier | Serves | Evidence |`; tier `T0` · `T1` · `T2` · `cut` · `merge→{unit}`. Confirm fan-in by reading importers before `cut`. Units protected by a kept rule or an ADR stay. Apply LEAN-02..10.
5. **Apply**: one cut or merge per commit, with its tests, docs, CI steps, config and dependencies; the commit message names the last commit that had it. Then write `SCOPE.md` without `cut`/`merge` rows, `Budget:` = the `budget` line of `audit.py lean` after the cuts (measured + 10 %, rounded up; a later raise names its reason in `SCOPE.md`), `Rules reviewed: {date} ({sha})`; add one line to the project's agent rules file: `Scope: SCOPE.md — a new unit gets a row first`.
6. **Verify** — `audit.py lean-check` green; `checks now` no redder than baseline; `audit.py lean` before → after in the report.

## Errors — one table for every phase

| Situation | Behaviour | Recorded as |
|-----------|-----------|-------------|
| No git repository | run is `dry` (no commits, no changed scope) | `decided:` |
| Fetch fails (offline, no remote) | audit against the local upstream ref | `decided:` |
| Branch behind, not diverged | `merge --ff-only`; refused → audit as is | `decided:` / `only-you:` |
| Branch diverged | no rebase, no pull; audit as is | `only-you: git pull --rebase` |
| File with uncommitted user edits | not edited in `all`; in changed scope edited under `git stash create`, never committed | row Commit `uncommitted` + snapshot hash in Notes |
| No runnable check | Verification gap (HIGH); Category A fixes only | row + `decided:` |
| Check red at baseline | red-at-baseline, never inherited as green | Effect line |
| A step or command hangs | its timeout ends it; the run continues with what does not depend on it | `skipped (timeout: {cmd})` |
| Tool absent | the rule falls back to its Detect text | scan `tool absent` |
| Judged signal (`?`) wrong | `audit.py signal {key} {value} {why}` re-plans phases not started | `decided:` |
| Unknown word, or `ask` with `auto` | `init` stops and names the valid choice | — |
| Context or time runs out | progress is in `report.md`; the next `init` resumes the open phase: fetches, switches back to `ds/audit`, prints the open phase's rows and commits, and splits uncommitted files into `run_files` (the run's, finish or revert them) and `user_files` (there before the run, left alone) | `decided:` / `only-you:` |
| Subagent returns nothing usable | rerun the phase once; again → `phase {p} blocked "{reason}"` | status INCOMPLETE |
| Reviewer runs out of room | its unfinished files stay unread; `groups` packs them again | — |
| Project rules forbid pushing | `audit.py push off "{rule file:line}"`; the branch stays local | `decided:` |
| Earlier run open, other words asked | `init` starts a new run; the old report is kept, its open rows carried | `decided:` |
| `ds/audit` already exists | `init` resumes on it; never recreated | `decided:` |
| Cannot switch to `ds/audit` | run becomes `dry` | `only-you:` |
| Push of `ds/audit` refused | no force; the run continues | `only-you:` |
| A workflow runs on every push | push still happens; the cost is named | `decided:` |
| `SCOPE.md` malformed | `lean-check` names each problem | LEAN-11 rows |
| App cannot start or no browser tool (surface) | visual check skipped; static checks stand | `decided:` |
| Same obstacle 3 times | stop that unit, record, continue (kernel §3) | `reverted (error)` / `skipped (blocker)` |
