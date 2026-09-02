---
name: ds-build
description: Plan executor — take an issue, a specs/{feature}/tasks.md, or a plain request and implement it unit by unit with a verify signal per unit, red-proven tests, budgeted backtracking, and a code-proven close. Use when the plan exists and the work is to be done, not planned.
---

# /ds-build

A plan is not progress. Handing an AI a task list produces half-implemented units, "done" claims with no signal behind them, and a tree nobody can bisect. This skill takes a source of work — a GitHub issue, a `specs/{feature}/tasks.md`, or a plain request — and executes it one bounded unit at a time, each proven by its own verify command before the next starts, then closes the record with the evidence.

**Plan Executor** — intake → re-verify → impact map → bounded units → red proof → aggregate gate → code-proven close.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-build`
- User says "implement this plan", "execute the tasks", "do issue #N", "build the feature in the spec"
- A `specs/{feature}/tasks.md` with unchecked tasks exists and the user asks to proceed
- `/ds-issue --do`, ds-pipeline (after tasks are generated) or ds-freeze (kept set) hand execution here

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "execute specs/001-x/tasks.md", "implement the plan" | "turn this idea into a plan" (→ ds-pipeline) |
| "do issue #42 end to end" | "file an issue for this" (→ ds-issue intake) |
| "build the kept set from the freeze" | "decide what ships now vs later" (→ ds-freeze) |
| "this bug — reproduce and fix it" → only when the fix is planned; otherwise | "find why this fails" (→ ds-debug) |
| "add the feature described in the request" | "write tests for X" alone (→ ds-test) |

## Contract

**Dimensions:** none (carrier)

- Executes work; never plans a feature from scratch (a plain request is normalized into a one-line goal + files + done criteria, not a spec) and never decides scope (that is ds-freeze's job).
- Standalone. Sources: a GitHub issue (via `gh`), a `specs/{feature}/tasks.md`, or the request text. The shared loop it runs is [../core/execution-loop.md](../core/execution-loop.md); this file adds only the executor-specific rules.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Every unit has a signal.** A task without a runnable verify command gets one before any edit (stack-native check from [../core/toolchains.md](../core/toolchains.md), a test, or an observable effect); "looks right" is not a signal.
- **Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)): `git status --porcelain` before the first write; a dirty path the plan would touch → that unit is `only you can do` (commit or stash first); disjoint dirt is listed and left alone. Failed units are reverted file-by-file (`git checkout -- {files}`), never with a tree-wide reset.
- **Mechanical Done Gate:** `{check-cmd}` resolved at setup (priority: ds-quality enforcement arm, profile `Toolchain:`, stack-native format → lint → type → test), baseline captured, re-run after every unit and once in aggregate before close; new red → fix ≤ 3 attempts with the same command, then revert the unit and record `reverted`; baseline red reported red-at-baseline; no tooling → Verification-Infrastructure Gap surfaced, never skipped.
- **Budgeted backtracking:** ≤ 3 fix attempts per approach, ≤ 3 approaches per unit; every failed attempt records `{approach} failed because {root cause}`; all approaches exhausted → unit `blocked` with the recorded causes, dependent units re-planned, never a fourth identical retry.
- **Publishing is never done here:** commits are local; push, PR, tag, release, deploy are on the exception list ([../core/ask-exception-list.md](../core/ask-exception-list.md)) and reported `only you can do` with the exact command.
- State-exempt: the record (issue body, `tasks.md` ticks, commits) is durable outside the run; a resumed run re-reads it.

## Arguments

| Flag | Effect |
|------|--------|
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--source={x}` | `issue:#N` · `tasks:{path}` · `request` (default: auto-detect — an issue number in the request → issue; an unchecked `specs/*/tasks.md` named or unique → tasks; else request) |
| `--preview` | Intake + re-verify + impact map + unit plan, written to the record (issue body or a plan block under the task file); no source edits |
| `--unit={n}` | Execute only unit `n` of the plan (after a `--preview` or a partial run) |
| `--research` | Allow web lookups when a unit needs an external fact (library API, platform behavior); default: repo + installed docs only, gap-noted |

Without flags: source auto-detected, the whole plan executed, every decision by best judgment and recorded. `--ask`: confirm the source, the unit plan, and each `needs-approval` item.

## Delegation

**Owns:** build-execution, task-loop | **Delegates:** ds-test → red-proven regression tests for fix-type units (absent → inline test with the observed red pasted); ds-commit → per-unit conventional commits (absent → inline `git commit` with a conventional message); ds-quality → enforcement-arm bootstrap when no gate exists (absent → stack-native `{check-cmd}` from core toolchains); ds-debug → a unit whose verify signal stays red after 3 approaches (absent → the unit is `blocked` with recorded causes) | **Receives:** ds-issue → issue execution (its `--do` mode); ds-pipeline → executor handoff of `specs/{feature}/tasks.md`; ds-freeze → implementation of the kept `ship` set

## Execution Flow

Intake → Re-verify → Impact map → Plan units → Execute + verify each → Aggregate gate → Close → Summary

### Phase 1: Intake

1. Resolve the source (Arguments). Issue → `gh issue view {N} --json body,title,comments`; `gh` absent or unauthenticated → the issue text pasted in the request, else `only you can do: gh not available — paste the issue body`. Tasks → read the file; every `- [ ]` line is a task, its `— verify:` clause is the signal. Request → restate as `→ [goal] | [files] | done: [criteria]`; missing criteria → derive the most conservative testable criterion and record it under `Decided without asking`.
2. Build the **done set**: issue → the body's Done list after comment-criteria promotion (each comment-borne criterion is promoted into the body or rejected with a reason — [../core/execution-loop.md](../core/execution-loop.md) § 0); tasks → every unchecked task; request → the done criteria.
3. Every done-set item without a verify signal gets one now (a command → expected output), recorded beside the item.
4. Resolve `{check-cmd}` and capture the baseline (Mechanical Done Gate). Run the Checkpoint pre-gate.

**Gate:** Source resolved, done set listed, every item carries a signal, baseline captured, tree checkpointed. If fails → no source found → stop with the three accepted forms; a done-set item that cannot get a signal → `only you can do: state how {item} is verified`, the rest proceeds.

### Phase 2: Re-verify + Impact map

1. **Re-verify root cause / premise** before any edit: read the cited anchors; a fix-type item is reproduced (observe the red); a feature is checked for prior implementation; stale or already done → stop that item with the evidence, never fabricate work for a non-problem.
2. **Impact map:** touched · linked · affected across callers/importers, implementors, configs and env vars, docs and examples, tests, generated artifacts — each axis `affected — {path}` or `N/A — {reason}`.

**Gate:** Every item re-verified (`still open` / `already done` / `stale`), impact map complete. If fails → an anchor no longer exists → the item is `stale`, reported, excluded from the plan.

### Phase 3: Plan units

Bounded units: ≤ ~5 files and ≤ ~25 tool calls each; each names the gap it closes, its files, and its verify signal; tasks map 1:1 to units when the task file already bounds them; every done-set item maps to ≥ 1 unit (an unowned item = incomplete plan). `--preview` → write the plan into the record (issue body `## Steps` + `## Impact surface`, or a `<!-- ds-build plan -->` block under the task file) and stop. Files exceeding 2× the intake estimate → stop, report the actual scope; `--ask` re-confirms, default proceeds with the reason recorded.

**Gate:** Every done-set item owned by a unit; every unit has files + signal. If fails → unowned item → add a unit or record `only you can do: no unit can close {item} because {reason}`.

### Phase 4: Execute + verify each unit

For each unit, in order:

1. Note the starting commit (`git rev-parse --short HEAD`) and the unit's file set.
2. Fix-type → write the regression test first, run it, **paste the observed red**; a test that never went red is rewritten (delegate to ds-test when present).
3. Implement, touching only task-required lines.
4. Run the unit's signal; interface changed → re-check the impact-map callers for that symbol.
5. Red → fix (≤ 3 attempts, same command); still red → next approach (≤ 3), each with `{approach} failed because {root cause}`; exhausted → revert the unit's files, mark `blocked`, hand to ds-debug when present, continue with independent units and re-plan dependents.
6. Green → run `{check-cmd}` for the touched scope; commit the unit (ds-commit when present, else `git add {files} && git commit -m "{type}({scope}): {what}"`); tick the task (`- [x] … — verified: {command} → {output}`) or note the evidence for the issue's Closure block.
7. Every detected error on the way — in the unit's files or not — gets a disposition ([../core/principles.md](../core/principles.md) §11 reject list applies).

**Gate:** Each unit `done` (signal green + committed) or `blocked` with causes, never silently skipped. If fails → a commit is rejected by a hook → fix what it names and retry (≤ 3), never bypass the hook; a checkpoint conflict appears mid-run (new dirt on a planned path) → that unit `only you can do`, continue with the rest.

### Phase 5: Aggregate gate

1. Run the full `{check-cmd}` once — per-unit greens compose into reds; new red → fix ≤ 3 attempts, then revert the offending unit and record `red`.
2. Issue source → run every row of the body's Gates table against its baseline; below baseline = regression caused by this run.
3. Fix-type → the red-proven regression test exists; absent → add it now (ds-test) with its red proof.
4. Re-read the diff: task-required lines only, no drive-by reformatting, affected-set callers intact.

**Gate:** Aggregate green (or no new red vs a red baseline), diff in scope. If fails → still red after the attempts → the offending unit is reverted and recorded, the close proceeds with the reduced done set and states it.

### Phase 6: Close — evidence into the record

| Source | What is written |
|--------|-----------------|
| Issue | The body: each Done item ticked with its observed output; a `## Closure` block (one evidence line per done-set item: signal → output → `file:line`; each Gates row: command → output vs baseline; the doctrine note); `Handoffs — Deferred to #K` lines with the counterpart written into `#K`; a dated `## Log` line. Then `gh issue close --reason completed` (`--ask` confirms; closing is not publishing — it is reversible). An uncovered item keeps the issue open. |
| tasks.md | Every task ticked with its verify output on the line; all ticked → the file is deleted (the commits are the record) and its deletion committed as `chore(specs): retire tasks for {feature}`. |
| Request | The Outcome Report with the verify-echo per unit. |

**Gate:** Record written; no done-set item without evidence; blocked items listed with causes. If fails → issue body write fails (permissions, `gh` down) → print the Closure block in chat and keep the issue open, `only you can do: paste the closure block`.

### Phase 7: Summary

```
ds-build: {OK|WARN|FAIL} | Source: {issue #N | tasks:{path} | request} | Units: {done}/{total} | Blocked: {n} | Reverted: {n} | Only you can do: {n} | Commits: {n}
```

Disposition accounting — totals balance. Then the verify-echo (each unit's signal + `{check-cmd}` aggregate output), `Decided without asking` lines, and every `only you can do` item in full ([../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md)). Status: OK (every unit done, aggregate green), WARN (blocked or only you can do items remain), FAIL (aggregate red or a revert left the record incomplete).

**Gate:** Summary printed with per-unit evidence. If fails → a unit's output is missing → run its signal again and paste it; never print a unit as done without it.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} of {n} planned units landed, each behind its own passing check — the feature is done in a way anyone can verify by re-running {check-cmd}`
- `Bug {id} fixed with a regression test that was seen failing first — the same defect cannot return unnoticed`
- `{n} units blocked with recorded root causes — the next attempt starts from the causes, not from zero`

Zero-change run: `Nothing to build — every done-set item was already implemented ({evidence})`.

## Quality Gates

- A unit is done only when its named signal was observed green in this run; a phase with no visible output was not executed
- No unit edits a file outside its declared set without recording why (impact-map miss → the map is corrected first)
- Commits are local; push / PR / tag / release stay `only you can do`
- W9: state-exempt — the record (issue, tasks.md, commits) is durable outside the run. W10: a fresh `ds/audit/findings.md` covering a unit's scope is consumed, never re-detected. W13: a reproduced red stays reproduced under "are you sure?" — withdrawn only on evidence.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Source ambiguous (several unchecked task files, no issue number) | Default: the most recently modified task file, recorded under `Decided without asking`; `--ask`: menu of candidates |
| Verify command missing a tool | Verification-Infrastructure Gap: report it, offer `/ds-quality`, substitute the nearest stack-native check, never mark the unit done without a signal |
| Same obstacle blocks 3 units | Stop, report the pattern with the recorded causes, propose 2–3 options with a recommendation |
| Context gap / resumed run | Re-read the record (issue body or task file) and `git diff`; the record is the ledger, not memory |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Task file already fully ticked | Report `nothing to build`, offer the retire commit |
| Issue closed while running | Stop at the next unit boundary, report the closure, write the evidence so far into the body |
| Unit needs a value only a human has (credential, business rule) | `only you can do` with the exact question; dependent units wait, independent units continue |
| Plan wants a publishing step (push, tag, release) | Recorded `only you can do` with the command; the local work is committed |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
