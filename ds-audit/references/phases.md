# Phases — the one contract every ds-audit phase follows

Every phase has the same input, steps, output and error handling. `audit.py` (in `../assets/`) does every countable step; the model reads, judges, fixes and writes rows. Terms (severity, disposition, Category A/B, principles) are defined once in [kernel.md](../../core/kernel.md); this file adds only what is specific to phases.

## Phases

Order = what changes the code the next phase audits. A phase runs the areas its signals load ([rules/README.md](../../core/rules/README.md)).

| Phase | Areas | May change | Ends when |
|-------|-------|------------|-----------|
| lean | `rules` `lean` | rule files, `SCOPE.md`, cuts and merges — all on the local branch `ds/lean` | every recorded rule and unit has a decision; `audit.py lean-check` green on `ds/lean`; the invocation stops for the owner to merge |
| build | `arch` `code` `test` `perf` | code and tests (fixers run first, once) | `validate` green, no `open` row, `checks now` no redder than baseline |
| safe | `sec` `privacy` `auth` `api` `db` | code, config, tests | same |
| surface | `web` `a11y` `ux` `i18n` `mobile` `store` `money` | code, copy, assets | same |
| ship | `ci` `ops` `docs` `repo` | CI, release, deploy config, docs | same; docs describe the final state |

## Steps — identical in every phase

1. **Inventory** — `audit.py scan {phase}`: runs each loaded rule's `Mech:` commands. `hit` = candidate, `clean` = rule passes, `tool absent` = that rule falls back to its Detect text, never to a pass.
2. **Detect** — S hits: read 3 lines around each, record. T hits: read the code; record only the real ones. M rules: apply their Detect. Then judgment: what no rule names but breaks, misleads or costs more than it gives (cite a kernel §7 principle). Changed scope: only changed lines and the code they break. Every candidate passes kernel §1 steps 1-3 first.
3. **Decide** — kernel §1 all six steps → the simplest fix in `Plan`; Category A apply, B decide and note `decided:`; same root cause → one fix.
4. **Apply** (not in `dry`) — one unit → narrowest check (format → lint → type → targeted test) → one commit `type(scope): summary` → row `fixed` + hash. A bug fix lands behind a test seen red first. Red after 3 attempts → reverse-apply the unit's own diff, row `reverted (error)`.
5. **Verify** — `audit.py checks now`; a step newly red → fix or revert the unit that caused it. `audit.py validate` → green. `audit.py phase {phase} done`.

**Fixers** run once, at the start of the first code phase: the project's own fix scripts, else the Fix commands of [toolchains.md](../../core/toolchains.md) (formatter, then the linter's safe autofix; never unsafe fixes or a dependency change); one commit per fixer (`style: apply {tool} fixes`); `checks now` after each — a newly red step reverts that fixer.

## Output — the ledger language

`ds/audit/report.md`, Findings table; one row per finding, appended by the model:

| Column | Allowed values |
|--------|----------------|
| `#` | next integer |
| Phase / Area | a phase name / an area word |
| Sev | CRITICAL · HIGH · MEDIUM · LOW (kernel §4) |
| Rule | a rule ID · a kernel §7 principle · `tool:{name}` · `judgment`; several joined by ` · ` |
| Where | `path:line` (checked: the file and line exist now or at the run's start) · a unit · an item |
| Finding / Prevents | what is wrong / what goes wrong without the fix, for whom — plain words |
| Plan | the simplest fix (kernel §1) |
| Disposition | `open` · `fixed` · `reverted (error)` · `skipped (blocker)` · `not applicable (reason)` · `only you can do (action)` |
| Commit | hash for `fixed` (checked: exists, after the run's start) · `uncommitted` (file had user edits) · `—` |

Notes lines: `decided: {decision} · {reason}` and `only-you: {exact action or command}`. A cell never contains `|`. Everything else in the file is written by `audit.py`.

## Running the phases

- **Changed scope** (no word): every phase in one invocation; lean runs only `lean-check` (when `SCOPE.md` exists).
- **`all` / a phase word**: `audit.py init` names the next phase. With subagents: one fresh subagent per phase, in order, given this file, kernel.md, SKILL.md, the phase's rule files and the report path; it returns after `phase … done`. Without subagents: one phase per invocation, ending with `next: /ds-audit all — continues at {phase}`.
- **lean stops the invocation** after it changed anything: `only-you: review and merge ds/lean (git diff {start}...ds/lean; git merge --ff-only ds/lean; git branch -d ds/lean)`. `all` resumes at build once merged.

## lean

The one interactive phase: scope and recorded rules are owner values (kernel §5). It asks when named (`/ds-audit lean`, `/ds-audit rules`) or with `ask`; inside an unattended `all`, each question becomes `only-you` with its recommendation, and nothing the owner must decide is applied.

1. **Rules** — `audit.py rules [--since {Rules reviewed sha}] [--also {spec the rules cite}] [--also {host memory dir}]`. Group lines into decisions (one cluster = one question); order: unreasoned absolutes, most cited, oldest. Ask at most 12 clusters, 4 per round: the rule verbatim, `file:line`, date and the commit subject that added it, what it forces today, its fit with the purpose, and a recommendation — keep · reword (new text) · scope (`until {date or condition}`) · move to a dated decision log · delete. Apply answers on `ds/lean`. Unasked clusters stay as they are and are listed. LEAN-12.
2. **Purpose** — `SCOPE.md` `Purpose:` and `Done when:`, else proposed from README/spec/issues and confirmed (LEAN-01).
3. **Measure** — `audit.py lean`. Write the minimal sketch: the fewest units that meet T0 and T1, reusing platform, stdlib and existing dependencies (LEAN-04).
4. **Tier** — one `SCOPE.md` row per unit: `| Unit | Tier | Serves | Evidence |`; tier `T0` · `T1` · `T2` · `cut` · `merge→{unit}`. Confirm fan-in by reading importers before `cut`. Units protected by a kept rule or an ADR stay. Apply LEAN-02..10.
5. **Apply** on `git switch -c ds/lean` (exists → resume it): one cut or merge per commit, with its tests, docs, CI steps, config and dependencies; the commit message names the last commit that had it. Then write `SCOPE.md` without `cut`/`merge` rows, `Budget:` = the measured counts after the cuts, `Rules reviewed: {date} ({sha})`; add one line to the project's agent rules file: `Scope: SCOPE.md — a new unit gets a row first`.
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
| Judged signal (`?`) wrong | `audit.py signal {key} {value}` re-plans phases not started | `decided:` |
| Unknown word | `init` stops and lists the valid words | — |
| Context or time runs out | progress is in `report.md`; the next invocation resumes the open phase | — |
| Subagent returns nothing usable | rerun the phase once; again → `phase {p} blocked "{reason}"` | status INCOMPLETE |
| `ds/lean` already exists | resume on it; never recreate | — |
| `SCOPE.md` malformed | `lean-check` names each problem | LEAN-11 rows |
| Same obstacle 3 times | stop that unit, record, continue (kernel §3) | `reverted (error)` / `skipped (blocker)` |
