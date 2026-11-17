# Phases — the one contract every ds-audit phase follows

Every phase has the same input, steps, output and error handling. `audit.py` (in `../assets/`) does every countable step; the model reads, judges, fixes and writes rows. Terms (severity, disposition, Category A/B, principles) are defined once in [kernel.md](../../core/kernel.md); this file adds only what is specific to phases.

## Phases

Order = what changes the code the next phase audits. A phase runs the areas its signals load ([rules/README.md](../../core/rules/README.md)).

| Phase | Areas | May change | Ends when |
|-------|-------|------------|-----------|
| lean | `rules` `lean` | rule files, `SCOPE.md`, cuts and merges | every recorded rule and unit has a decision; `audit.py lean-check` green |
| build | `arch` `code` `test` `perf` | code and tests (fixers run first, once) | `validate` green, no `open` row, `checks now` no redder than baseline |
| safe | `sec` `privacy` `auth` `api` `db` | code, config, tests | same |
| surface | `web` `a11y` `ux` `i18n` `mobile` `store` `money` | code, copy, assets | same |
| ship | `ci` `ops` `docs` `repo` | CI, release, deploy config, docs | same; docs describe the final state |

## Steps — identical in every phase

1. **Inventory** — `audit.py scan {phase}`: runs each loaded rule's `Mech:` commands. `hit` = candidate, `clean` = rule passes, `tool absent` = that rule falls back to its Detect text, never to a pass; `not applicable` = the rule's `applies_when:` excludes this project's signals, so its command is not run.
2. **Detect** — S hits: read 3 lines around each, record. T hits: read the code; record only the real ones. M rules: apply their Detect. Then judgment: what no rule names but breaks, misleads or costs more than it gives (cite a kernel §7 principle). Changed scope: only changed lines and the code they break. Every candidate passes kernel §1 steps 1-3 first.
3. **Decide** — kernel §1 all six steps → the simplest fix in `Plan`; Category A apply, B decide and note `decided:`; same root cause → one fix. Write each row the moment its finding is decided (as `open` until applied), never in a batch at the phase end: a run cut short resumes from the rows.
4. **Apply** (not in `dry`) — one unit → narrowest check (format → lint → type → targeted test) → one commit `type(scope): summary` → row `fixed` + hash. A bug fix lands behind a test seen red first. A refactor of code no test covers lands behind a characterization test written first and seen green on the unchanged code. Red after 3 attempts → reverse-apply the unit's own diff, row `reverted (error)`.
5. **Verify** — `audit.py checks now`; a step newly red → fix or revert the unit that caused it. `audit.py validate` → green. `audit.py phase {phase} done` (it also runs `lean-check` when `SCOPE.md` exists and refuses on red).

**Fixers** run once, at the start of the first code phase: the project's own fix scripts, else the Fix commands of [toolchains.md](../../core/toolchains.md) (formatter, then the linter's safe autofix; never unsafe fixes or a dependency change); one commit per fixer (`style: apply {tool} fixes`); `checks now` after each — a newly red step reverts that fixer.

**Dependency updates** run once, in ship (area `ci`), never in `dry`: patch and minor updates of direct dependencies, one group per ecosystem with the stack's own command (lockfile updated, no new dependency), one commit per group (`build(deps): update {ecosystem} patch and minor`), `checks now` after each — a newly red step reverts that group and records it. Majors and versions published less than 7 days ago are not applied: each becomes an `only-you` line with its changelog link (DOP-10, DOP-11).

## Output — the ledger language

`ds/audit/report.md`, Findings table; one row per finding, appended by the model; columns in this order:

| Column | Allowed values |
|--------|----------------|
| `#` | next integer |
| Phase | a phase name |
| Sev | CRITICAL · HIGH · MEDIUM · LOW (kernel §4) |
| Area | an area word |
| Rule | a rule ID · a kernel §7 principle (any case; the part before ` / ` suffices: `DRY`) · `tool:{name}` · `judgment`; several joined by ` · ` |
| Where | `path:line` (checked: the file and line exist now or at the run's start) · a unit · an item |
| Finding | what is wrong — plain words |
| Prevents | what goes wrong without the fix, for whom — plain words |
| Plan | the simplest fix (kernel §1) |
| Disposition | `open` · `fixed` · `reverted (error)` · `skipped (blocker)` · `not applicable (reason)` · `only you can do (action)` |
| Commit | hash for `fixed` (checked: exists, after the run's start) · `uncommitted` (file had user edits) · `—` |

Notes lines: `decided: {decision} · {reason}` (`decided!:` puts it among the closing message's five) and `only-you: {exact action or command}`, each once; an action already in a row's Disposition is not repeated as a note. A decision is a choice the owner may reverse; scan triage (why a hit is not a finding) goes into the row or nowhere, never into Notes. A cell never contains `|`. Everything else in the file, and `report.html` beside it, is written by `audit.py`.

## Running the phases

- **Changed scope** (no word): every phase in one invocation; lean runs SIM-* on the changed lines and LEAN-11 when `SCOPE.md` exists, not the rules review or the tiering.
- **`all` / a phase word**: `audit.py init` names the next phase. With subagents: one fresh subagent per phase, in order, given this file, kernel.md, SKILL.md, the phase's rule files and the report path; it returns after `phase … done`. Without subagents: one phase per invocation, ending with `next: /ds-audit all — continues at {phase}`.
- **One review branch**: every phase of an `all`, phase or area run commits on `ds/audit` (`audit.py init` creates or resumes it; the owner's branch is untouched), and `phase … done` pushes it without force. Later phases audit the code lean already cut. The report ends with the merge commands as `only-you`.

## surface — see the running app (optional)

After the static pass, when `ui≠none`: start the app locally (the project's documented dev or preview command; never a deploy, never production data) and open it with the host's browser tool (Playwright, the host's built-in browser). At a narrow (~400 px) and a wide (~1280 px) viewport check: no horizontal overflow, keyboard focus order and a visible focus ring, contrast (axe when present), and capture the empty, error and loading states of the main flow. Each problem is a row with the screenshot path in Notes. Cannot start the app, or no browser tool → `decided: visual check skipped — {reason}`; the run is not INCOMPLETE for it. Stop the app afterwards.

## lean

The one interactive phase: scope and recorded rules are owner values (kernel §5). It asks when named (`/ds-audit lean`, `/ds-audit rules`) or with `ask`; inside an unattended `all`, each question becomes `only-you` with its recommendation, and nothing the owner must decide is applied.

**With `auto`** the recommendation is applied instead of asked, as `decided: {decision} · {evidence} · revert: {command}`, within these limits:
- **Purpose** — derived only from the project's own words (README, spec, issues, agent rules), quoted in `SCOPE.md`; none found → `Purpose: unconfirmed`, and cuts are limited to units with no inbound use and no need named anywhere (no reference, no doc, no issue).
- **Rules** — a rule with a stated reason is kept or reworded, never deleted; delete only a rule that contradicts the purpose or another rule, or names something that no longer exists; a one-moment rule (LEAN-12) is scoped `until {date}` rather than deleted.
- **Units** — `cut` needs zero fan-in confirmed by reading plus no need in the purpose; a unit with users, docs or issues asking for it becomes `T2` (deferred), never cut; `merge` only where LEAN-04 names one reason to change for both.

1. **Rules** — `audit.py rules [--since {Rules reviewed sha}] [--also {spec the rules cite}] [--also {host memory dir}]`. Group lines into decisions (one cluster = one question); order: unreasoned absolutes, most cited, oldest. Ask at most 12 clusters, 4 per round: the rule verbatim, `file:line`, date and the commit subject that added it, what it forces today, its fit with the purpose, and a recommendation — keep · reword (new text) · scope (`until {date or condition}`) · move to a dated decision log · delete. Apply answers as commits on the run's branch. Unasked clusters stay as they are and are listed. LEAN-12.
2. **Purpose** — `SCOPE.md` `Purpose:` and `Done when:`, else proposed from README/spec/issues and confirmed (LEAN-01).
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
| `ds/audit` already exists | `init` resumes on it; never recreated | `decided:` |
| Cannot switch to `ds/audit` | run becomes `dry` | `only-you:` |
| Push of `ds/audit` refused | no force; the run continues | `only-you:` |
| A workflow runs on every push | push still happens; the cost is named | `decided:` |
| `SCOPE.md` malformed | `lean-check` names each problem | LEAN-11 rows |
| App cannot start or no browser tool (surface) | visual check skipped; static checks stand | `decided:` |
| Same obstacle 3 times | stop that unit, record, continue (kernel §3) | `reverted (error)` / `skipped (blocker)` |
