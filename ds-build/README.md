# ds-build

A plan is not progress. Handing an AI a task list produces half-implemented units, "done" claims with no signal behind them, and a tree nobody can bisect.

**Plan executor — issue, `specs/{feature}/tasks.md`, or plain request → bounded units, each proven by its own verify command, red-proven tests, budgeted backtracking, code-proven close.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git && cd dev-skills && ./install.sh
```

Any Agent Skills host: `./install.sh --target <that host's skills dir>` (ships `core/` beside the skill).

## Use

```bash
/ds-build                          # auto-detect the source, execute the whole plan, decisions by best judgment
/ds-build --source=issue:#42       # execute one issue end to end (also what ds-issue --do hands here)
/ds-build --source=tasks:specs/001-x/tasks.md
/ds-build --preview                # intake + re-verify + impact map + unit plan into the record, no edits
/ds-build --unit=3                 # one unit of an existing plan
/ds-build --ask                    # confirm the source, the plan and every needs-approval item
/ds-build --research               # allow web lookups for external facts
```

## Flow

1. Intake — source, done set, a verify signal per item, `{check-cmd}` baseline, checkpoint
2. Re-verify + impact map — reproduce the red / confirm the premise, map callers·configs·docs·tests
3. Plan units — ≤ ~5 files each, every done-set item owned by a unit
4. Execute + verify each — regression test seen red first, implement, signal green, commit per unit
5. Aggregate gate — full check once, gates vs baseline, diff in scope
6. Close — evidence written into the issue body / task ticks / outcome report
7. Summary — units done/blocked/reverted, verify-echo, needs-human items in full

## Features

- **Three sources, one loop** — GitHub issue, tasks.md, plain request all run the shared execution loop in `core/execution-loop.md`
- **Red proof** — a fix without a test that was observed failing first is not done
- **Budgeted backtracking** — ≤3 attempts per approach, ≤3 approaches per unit, every failure records its root cause
- **Checkpoint + revert per unit** — never a tree-wide reset; dirty paths the plan would touch become `needs-human`
- **Mechanical Done Gate** — the project's own check chain (or the ds-quality arm) decides "done", not the model
- **Publishing stays human** — commits are local; push, PR, tag, release are reported with the exact command
