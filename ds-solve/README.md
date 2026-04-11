# ds-solve

Some problems resist single-pass fixes. Environment conflicts, integration failures, migration breakage — they need multiple attempts with different approaches. This skill plans, executes, researches alternatives on failure, backtracks, and re-plans until it solves the problem or exhausts its budget.

Combines [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) persistence with [ds-tune](../ds-tune/) mechanical verification and web-research-driven alternative discovery. Backtrack logic and state schema documented in [references/backtrack-logic.md](references/backtrack-logic.md). Research scoring uses [CRAAP+ methodology](references/craap-scoring.md).

## Install

```bash
cp -r ds-solve ~/.claude/skills/ds-solve
```

## Use

```bash
/ds-solve                    # Interactive: detect red lines, ask objective, plan, solve
/ds-solve --auto             # Skip confirmations, still escalates on exhaustion
/ds-solve --resume           # Resume from .ds-solve-state.json
/ds-solve --status           # Show current session progress
/ds-solve --dry-run          # Plan + Research only, no execution
/ds-solve --budget=2x2x3     # Custom budget: 2 plans, 2 rounds, 3 alternatives
```

## How It Works

1. **Setup** — Scans project docs (README, CI, configs) to auto-detect red lines. Confirms with you. Asks for objective.
2. **Plan** — Decomposes objective into 2-10 ordered steps, each with a verification criterion.
3. **Research** — For each step: local codebase search first, then web search. Ranks top 5 alternatives per step.
4. **Execute** — Tries alternatives in order. Checks red lines before/after every attempt. Reverts on violation.
5. **Backtrack** — Step fails all alternatives? Researches new ones (up to 3 rounds per step).
6. **Re-plan** — Research rounds exhausted? Redesigns the entire step sequence using learned constraints.
7. **Escalate** — 3 plans exhausted? Presents full report with suggested paths (relax constraints, reduce scope, manual action).

## Budget System

```
3 plans x 3 research rounds x 5 alternatives = 45 max attempts per step
```

Override with `--budget=PxRxA`. Most problems resolve in plan 1, round 1.

## State & Resume

Progress is saved to `.ds-solve-state.json` after every state change. Use `--resume` to continue after interruption. Use `--status` to check progress.

## Red Lines

Red lines are constraints that must never be violated. The skill:
- Auto-detects from project docs (test suites, CI, configs, package constraints)
- Asks you to confirm, remove, or add more (unlimited)
- Checks before and after every execution attempt
- Reverts immediately on violation

## Works With

Any problem with a verifiable success criterion: tests passing, commands succeeding, services responding, builds completing, configurations working.
