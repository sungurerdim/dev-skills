# /ds-solve

Problems that resist single-pass fixes — environment conflicts, integration failures, migration breakage — need adaptive iteration: plan, try, research, backtrack, re-plan. This skill exhausts every viable path before giving up.

**Adaptive Problem Solver** — Plan, execute, research alternatives, backtrack on failure, re-plan from scratch. Combines [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) persistence, [ds-tune](../ds-tune/) mechanical verification, and research-driven alternative discovery. Architecture informed by [CodeTree](https://arxiv.org/abs/2411.04329) (tree search with specialized agents), [BacktrackAgent](https://aclanthology.org/2025.emnlp-main.212/) (error detection + rollback), [Reflexion](https://arxiv.org/abs/2303.11366) (episodic memory), and [EnCompass](https://news.mit.edu/2026/helping-ai-agents-search-to-get-best-results-from-llms-0205) (branchpoint search).

## Triggers

- User runs `/ds-solve`
- User describes a multi-step problem: "make X work", "fix this integration", "migrate from A to B"
- Environment or configuration issues that resist straightforward fixes
- User explicitly asks for exhaustive/adaptive problem solving

## Contract

- Red lines are preserved throughout — checked before and after every attempt. Example: if "Node 16 compatibility" is a red line, every alternative is validated against Node 16 before advancing.
- Red lines are auto-detected from project documentation, then confirmed by user. User can add unlimited additional red lines.
- Every attempt is recorded in episodic memory — zero silent drops. Example: alternative #3 fails with "peer dep conflict" → recorded with failure reason + learned constraint, visible in summary.
- Infinite loop protection: 3 plans x 3 research rounds x 5 alternatives budget. Decision logic in [references/backtrack-logic.md](references/backtrack-logic.md).
- Backtrack and re-plan decisions are automatic. User is only consulted on escalation (3 plans exhausted) or needs-approval items.
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every step receives a disposition in the summary — zero silent drops (FRC)

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Interactive: detect red lines, confirm with user, ask for objective, confirm plan |
| `--auto` | Skip plan confirmation. Still escalates on exhaustion. |
| `--resume` | Resume from `.ds-solve-state.json` progress artifact |
| `--status` | Show current solve session status |
| `--dry-run` | Plan + Research only, no execution |
| `--budget=PxRxA` | Override budget (default: `3x3x5` = 3 plans, 3 rounds, 5 alternatives) |

**Input validation:**
- Unknown flag → warn `Unknown flag: {flag}. Ignoring.` and continue
- Invalid budget format → warn, use default `3x3x5`
- Budget below minimum (1x1x2) → warn, clamp to minimum
- `--dry-run` + `--resume` → warn conflict, `--resume` takes priority (resume existing session in dry-run mode)

## Execution Flow

Setup → Plan → Research → Execute → [Backtrack] → [Re-plan] → [Needs-Approval] → [Escalate] → Summary

### Phase 1: Setup

**Goal:** Understand the objective, detect and confirm red lines.

**Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use as context for understanding project state and known issues.

**Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
- **Type + Stack** → context for research queries
- **Config.constraints** → automatic red lines (user confirms)
- **Current Scores** → context for identifying weak dimensions related to objective

1. **Red line auto-detection.** Scan project documentation:

   | Source | What to extract |
   |--------|----------------|
   | README.md, CONTRIBUTING.md | Stated requirements, compatibility, constraints |
   | package.json / pyproject.toml | `engines`, `requires-python`, peer deps |
   | tsconfig.json | `strict`, `target`, path aliases |
   | CI config (workflows, Makefile) | Required checks, min versions, build targets |
   | Dockerfile / docker-compose | Base images, exposed ports, volumes |
   | .env.example | Required environment variables |
   | Existing test suite | "All existing tests must keep passing" |
   | Linter/formatter config | "Lint and format rules must be preserved" |
   | Blueprint `Config.constraints` | Infrastructure and project constraints |

   Example — detected red lines from a Next.js project:
   ```
   Red lines detected:
   1. Node >= 18 (from package.json engines)
   2. TypeScript strict mode (from tsconfig.json)
   3. All 47 existing tests pass (from jest config)
   4. ESLint rules preserved (from .eslintrc)
   ```

2. **Red line confirmation.** Present detected red lines as a numbered list. Ask user to:
   - Confirm or remove detected red lines
   - Add any additional red lines (no limit)
   - If nothing detected: explicitly ask for constraints

3. **Objective.** Ask: "What do you want to achieve?" Wait for answer.

4. **Verification criterion.** Define how to prove the objective is met: a command that returns 0, a test that passes, a state check, or an observable condition. Confirm with user.

   Example — verification criteria:
   ```
   Objective: "Make the app work with PostgreSQL instead of SQLite"
   Verification: `npm test && node -e "require('./db').query('SELECT 1')"`
   ```

5. **Quick check.** Run verification criterion immediately. If it already passes → report OK, skip to Summary.

6. **Initialize.** Create `.ds-solve-state.json` (schema in [references/backtrack-logic.md](references/backtrack-logic.md)) with objective, red lines, verification, and budget config. Parse `--budget` if provided, otherwise use `3x3x5`.

**Output:** Red lines table + objective + verification criterion.

**Gate:** Objective stated, red lines confirmed, verification criterion defined, state file created.

### Phase 2: Plan

**Goal:** Decompose objective into ordered steps.

1. Read relevant files. Understand current state relative to the objective. Verify each file exists before referencing — state "not verified" rather than assuming. _(W1: Hallucination prevention)_
2. Decompose into 2-10 ordered steps. Each step has:
   - **Description:** what this step achieves
   - **Verification:** command or check that proves this step succeeded
   - **Red line risk:** which red lines this step could potentially violate
3. Record plan to `.ds-solve-state.json` as `plan-N`.
4. Present plan to user. (`--auto`: proceed without confirmation.)

   Example — plan output:
   ```
   Plan 1: SQLite → PostgreSQL Migration (4 steps)
   | # | Step | Verification | Red Line Risk |
   |---|------|-------------|---------------|
   | 1 | Install pg driver | `node -e "require('pg')"` exits 0 | #2 (strict TS) |
   | 2 | Update connection config | Config loads without error | #1 (Node 18) |
   | 3 | Adapt query syntax | `npm test` passes | #3 (47 tests) |
   | 4 | Remove SQLite deps | `npm ls` clean | — |
   ```

**Output:** Numbered step table with verification criteria.

**Gate:** Plan confirmed. Every step has a verification criterion.

### Phase 3: Research

**Goal:** For each step, identify ranked alternatives before execution.

For each step in the plan:

1. **Local search first.** Scan codebase for existing patterns, utilities, prior solutions that address this step.
2. **Web search.** 2 parallel search queries per step. Include current date in queries to avoid stale results. Target the step's technical domain + project stack.
3. **Score alternatives.** Use CRAAP+ methodology from [../ds-research/references/craap.md](../ds-research/references/craap.md): Relevance to step, Currency, Authority. Discard score < 50.
4. **Rank and select.** Top 5 alternatives per step. Record as `research-round-1`.

Record all alternatives to state file.

   Example — research output for step 1:
   ```
   Step 1: Install pg driver — 5 alternatives
   | # | Alternative | Source | CRAAP+ |
   |---|------------|--------|--------|
   | 1 | npm install pg @types/pg | npmjs.com (T1) | 92 |
   | 2 | npm install postgres (postgres.js) | github.com (T2) | 87 |
   | 3 | npm install knex pg (query builder) | knexjs.org (T1) | 81 |
   | 4 | npm install drizzle-orm pg | orm.drizzle.team (T2) | 78 |
   | 5 | npm install sequelize pg | sequelize.org (T1) | 72 |
   ```

**Output:** Alternatives table per step with CRAAP+ scores.

**Gate:** Every step has at least 1 alternative. Steps with 0 → flag for re-scoping.

### Phase 4: Execute

**Goal:** Execute each step using alternatives on failure.

For each step in order:

1. **Red line pre-check.** Verify all red lines hold before touching anything. If any violated → STOP, enter Re-plan (something external broke them).
2. **Try alternative #1** (highest-ranked from Research).
3. **Verify.** Run the step's verification criterion.
4. **Red line post-check.** Verify all red lines still hold after execution. If violated → revert all changes from this attempt, record violation, try next alternative. After modifying any file, verify no other file depends on the changed interface in a now-broken way. _(W2: Tunnel Vision prevention)_
5. **On failure:** Record failure reason and learned constraint in episodic memory. Try next alternative (2→5).
6. **On success:** Record success, update state, advance to next step.
7. **All 5 alternatives exhausted:** Enter Backtrack for this step.

Only modify files required by the current step. Leave unrelated code untouched. _(W3: Scope Creep prevention)_

Progress indicator after each attempt:
```
[Plan 1/3] [Step 2/5] [Alt 1/5] [Round 1/3] Trying: Install pg via npm
Result: FAIL — peer dependency conflict with @types/node@16
Learned: pg@8.x requires @types/node >= 18
Red lines: 4/4 held
Next: Trying alternative 2...
```

**Output:** Progress indicator per attempt.

**Gate:** Step verification passes AND all red lines hold.

### Phase 5: Backtrack [all alternatives for a step exhausted]

**Goal:** Research new alternatives incorporating learned constraints. Decision tree and constraint propagation rules in [references/backtrack-logic.md](references/backtrack-logic.md).

1. **Analyze failures.** Extract common patterns from all failure reasons for this step. What constraints did we learn?
2. **New research.** Search web for 5 new alternatives. Explicitly exclude previously tried approaches. Incorporate learned constraints in queries (e.g., "PostgreSQL driver compatible with Node 16" if Node 16 was the blocker).
3. **Increment** research round counter for this step.
4. Round <= budget.R (default 3): Return to Execute with new alternatives.
5. Round > budget.R: Enter Re-plan.

**Output:** New alternatives table + learned constraints summary.

**Gate:** New alternatives found, or research rounds exhausted.

### Phase 6: Re-plan [plan-level backtrack]

**Goal:** Redesign step sequence from scratch using accumulated knowledge. State machine transitions in [references/backtrack-logic.md](references/backtrack-logic.md).

1. **Review episodic memory.** All attempts, all failures, all learned constraints across all steps. Re-read modified files and state artifact before proceeding — conversation memory is not source of truth. _(W4: Memory Decay prevention)_
2. **Identify flexibility.** Which requirements are essential to the objective vs. which are implementation choices? Can the objective be decomposed differently to avoid the failure patterns?
3. **Create new plan.** Different step decomposition, different ordering, different sub-goals that avoid known failure patterns. Must differ meaningfully from previous plan(s).
4. **Increment** plan counter. Record as `plan-{N}`.
5. Plan counter <= budget.P (default 3): Return to Research with new plan.
6. Plan counter > budget.P: Enter Escalate.

**Output:** New plan table + diff from previous plan + rationale for changes.

**Gate:** New plan with different approach created, or plan budget exhausted.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Items flagged `needs_approval` during execution (irreversible changes, cross-module modifications, destructive actions):

- **`--auto` without `--force-approve`:** List items, skip them, note in summary
- **`--force-approve`:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items with risk context. Ask: Apply All / Review Each / Skip All

Example — needs-approval item:
```
needs_approval: Step 3 deletes migration table (irreversible)
  Risk: Cannot undo without database backup
  Affected: migrations/, db/schema.sql
  → Apply / Skip?
```

**Gate:** All needs_approval items resolved (applied → `fixed`/`failed`, declined → `skipped`).

### Phase 8: Escalate [all plans exhausted]

**Goal:** Present exhaustive report and ask user for direction.

1. **Compile report.** All plans attempted, steps per plan, alternatives per step, failure reasons. See Report Format below.
2. **Pattern analysis.** Identify recurring blockers across all attempts:
   - Which red lines blocked the most alternatives?
   - What environmental constraints were discovered?
   - What dependencies or versions caused failures?
3. **Suggest paths forward:**
   - **Red line relaxation:** "If constraint X were relaxed, approach Y becomes viable"
   - **Scope reduction:** "A partial solution achieving A+B (but not C) is possible"
   - **External action:** "This requires manual action X before automation can continue"
4. **Ask user:** Update red lines / Reduce scope / Provide new direction / Abort
5. User provides new direction → reset plan counter, return to Plan phase with updated context.
6. User aborts → proceed to Summary.

**Output:** Escalation report (see Report Format).

**Gate:** User has provided new direction or confirmed abort.

### Phase 9: Summary

**Mandatory.** Always execute, always produce output — never skip regardless of mode or flags.

**FRC accounting:** Every step from every plan appears with a disposition.

**Output:**

```
ds-solve: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Needs-Approval: N | Total: N
```

Step disposition table:

| Step | Disposition | Plan | Attempts | Verification |
|------|------------|------|----------|-------------|
| 1. {desc} | fixed | plan-1 | 2 | {criterion}: PASS |
| 2. {desc} | failed | plan-1,2,3 | 15 | {criterion}: FAIL |
| 3. {desc} | skipped (user declined) | plan-2 | 0 | — |

Red line status:
```
Red lines: {held}/{total} held | Budget: {used}/{max} attempts
```

**Dispositions:**

| Disposition | Meaning |
|-------------|---------|
| `fixed` | Step completed, verification passed, red lines held |
| `failed` | All alternatives exhausted across all research rounds |
| `skipped` | Not attempted (plan changed, `--dry-run`, user declined) with reason |
| `needs-input` | Requires information from user (asked before summary) |
| `needs-approval` | Irreversible or cross-module — awaiting confirmation |
| `not-applicable` | Step rendered unnecessary by different plan approach |

**Accounting gate:** `fixed + failed + skipped + needs_input + needs_approval + not_applicable = total_steps`

**Mandatory phase verification:** Confirm all mandatory phases (Setup, Plan, Research, Execute, Summary) produced visible output. _(W6: Skip Tendency prevention)_

Status: `OK` (objective achieved), `WARN` (partial — some steps succeeded), `FAIL` (objective not achieved after exhaustion or abort).

## Report Format

### Escalation Report

```
## ds-solve: Escalation Report

### Objective
{objective description}

### Red Lines
{numbered list with status: HELD / BLOCKING}

### Attempt Summary
| Plan | Approach | Steps Done | Attempts | Primary Failure |
|------|----------|-----------|----------|-----------------|
| 1 | {summary} | 2/5 | 12 | {pattern} |
| 2 | {summary} | 3/4 | 8 | {pattern} |
| 3 | {summary} | 1/3 | 7 | {pattern} |

### Failure Patterns
- {N}/{total} attempts failed due to: {pattern}
- {blocker analysis}

### Paths Forward
1. Relax red line "{X}" → approach Y becomes viable
2. Reduce scope → achieve {partial} without {excluded}
3. External action → {manual step} required first
```

## Quality Gates

- Red lines checked before AND after every execution attempt — violations immediately revert
- Every step has a mechanical verification criterion (command exit code, test result, state check)
- Episodic memory records every attempt — no silent retries. Example: 3 attempts for step 2 → all 3 visible in state file and summary.
- Budget limits enforced: plan counter, research round counter, alternative counter
- State file updated after every state change — survives interruption. Re-read state file after context gap before modifying. _(W4: Memory Decay)_
- Previous plans' failures inform new plans — no duplicate approaches. Same file:step combination failing identically → merge, keep latest. _(W7: Redundancy Blindness)_
- FRC accounting in summary — every step gets a disposition, equation must balance
- Before using any dependency, API, or tool in an alternative → verify it exists via search or docs. State "not verified" rather than assuming. _(W1: Hallucination)_
- Only modify files required by the current step — leave unrelated code untouched. _(W3: Scope Creep)_
- Validate all external input before interpolating into shell commands. Quote paths, use `--` separators, reject metacharacters. _(W8: Injection Risk)_

## Severity

Not a finding-based skill. Severity applies to issues discovered during execution:

| Level | Meaning | Example |
|-------|---------|---------|
| CRITICAL | Red line violation, or objective impossible within constraints | Test suite fails after change; dependency requires Node 20 but red line says Node 16 |
| HIGH | Step exhausted all alternatives across all research rounds | 15 alternatives tried for "install driver", all fail |
| MEDIUM | Alternative failed but others remain (expected during adaptive solving) | npm install fails, but yarn alternative exists |
| LOW | Minor issue during research or verification (stale source, slow command) | CRAAP+ score 45 source discarded |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Red line violated during execution | Immediately revert changes, record violation, try next alternative |
| Verification command fails to run | Check syntax and environment. If infrastructure issue, record as learned constraint. Example: `pg_config` not found → constraint "PostgreSQL dev headers missing" |
| Same alternative fails identically twice | Skip remaining retries, advance to next alternative |
| State file corrupted | Infer last successful step from git state, restart from there |
| Git state inconsistent | Stash or revert uncommitted changes before retrying |
| Web search unavailable | Fall back to local-only research, reduce alternatives target to 3, warn in summary |
| Context approaching limit | Checkpoint state, compress episodic memory (keep failure reasons + constraints, drop verbose logs). Re-read state file to resume. _(W4: Memory Decay)_ |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Objective already achieved | Run verification upfront. If passes, report OK immediately. |
| Single-step objective | Skip plan decomposition. Execute directly with 5 alternatives. |
| User changes red lines mid-run | Re-validate all completed steps against new lines. If violation found, backtrack to that step. |
| Objective is vague | Ask user for a verification criterion. If they cannot define one, suggest measurable proxies. Example: "make it faster" → suggest `time npm run build` < 30s. |
| All steps pass but final verification fails | Plan decomposition missed something. Enter Re-plan with constraint: "individual step success insufficient". |
| Irreversible change in a step | Flag as `needs-approval`. In `--auto` without `--force-approve`, skip and note. |
| No project documentation found | Ask user directly for all red lines. Proceed with user-stated constraints only. |
| Budget override too small | Warn if budget < 1x1x2. Clamp to minimum. |
| Contradictory red lines | Explain conflict (e.g., "Node 16 required" + "use pg@8.x which needs Node 18"), ask which takes priority. |
