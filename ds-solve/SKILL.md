# /ds-solve

Problems that resist single-pass fixes — environment conflicts, integration failures, migration breakage — need adaptive iteration: plan, try, research, backtrack, re-plan. This skill exhausts every viable path before giving up.

**Adaptive Problem Solver** — Plan, execute, research alternatives, backtrack on failure, re-plan from scratch. Combines [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) persistence, [ds-tune](../ds-tune/) mechanical verification, and research-driven alternative discovery. Architecture informed by [CodeTree](https://arxiv.org/abs/2411.04329) (tree search with specialized agents), [BacktrackAgent](https://aclanthology.org/2025.emnlp-main.212/) (error detection + rollback), [Reflexion](https://arxiv.org/abs/2303.11366) (episodic memory), and [EnCompass](https://news.mit.edu/2026/helping-ai-agents-search-to-get-best-results-from-llms-0205) (branchpoint search).

## Triggers

- User runs `/ds-solve`
- User describes a multi-step problem: "make X work", "fix this integration", "migrate from A to B"
- Environment or configuration issues that resist straightforward fixes
- User explicitly asks for exhaustive/adaptive problem solving

## Contract

- **Autonomous by default.** The user states the problem — the skill handles everything else. User is only consulted for: (1) escalation (all plans exhausted), (2) irreversible actions (needs-approval). All other decisions are made independently.
- Red lines are auto-detected from project documentation and applied automatically. Detected red lines are shown as output, not as a question. User can add more via `--red-line="{constraint}"` flag if needed.
- Every attempt is recorded in episodic memory — zero silent drops.
- Infinite loop protection: 3 plans x 3 research rounds x 5 alternatives budget. Decision logic in [references/backtrack-logic.md](references/backtrack-logic.md).
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Autonomous: auto-detect red lines, infer verification, plan and execute without asking |
| `--red-line="{text}"` | Add explicit red line (repeatable). Combined with auto-detected ones. |
| `--confirm` | Pause for user confirmation after Setup and Plan phases before executing |
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

### Phase 1: Setup — Detect objective, red lines, and verification criterion

**Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use as context.

**IDU:** Profile → Type + Stack, Config.constraints, Current Scores. Findings() → verify + use. Absent → own analysis.

1. **Parse objective.** Extract from user's invocation message. If the user wrote `/ds-solve {description}`, use `{description}` as the objective. Only ask if no objective is discernible from context.

2. **Red line auto-detection.** Scan project documentation silently and apply all detected constraints:

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
   | `--red-line` flags | User-specified explicit constraints |

   Show detected red lines as output (not a question). Merge with any `--red-line` flags.

3. **Verification criterion.** Determine autonomously from the objective:
   - Objective mentions tests → `{test_command}` exits 0
   - Objective mentions a service → service responds on expected port/endpoint
   - Objective mentions a build → `{build_command}` succeeds
   - Objective mentions a behavior → construct a validation command or script
   - If no mechanical criterion can be inferred → use the most conservative proxy and state the assumption. Only ask the user if zero proxy is possible (`--confirm` mode: always ask).

4. **Quick check.** Run verification criterion immediately. If already passes → report OK, skip to Summary.

5. **Initialize.** Create `.ds-solve-state.json` (schema in [references/backtrack-logic.md](references/backtrack-logic.md)) with objective, red lines, verification, and budget config.

**Output:** Objective + red lines table + verification criterion (all as statements, not questions).

**Gate:** Objective parsed, red lines applied, verification criterion defined, state file created.

### Phase 2: Plan — Decompose objective into ordered steps

1. Read relevant files. Verify each file exists before referencing. _(W1)_
2. Decompose into 2-10 ordered steps. Each step: **Description**, **Verification** (command/check), **Red line risk** (which red lines could be affected).
3. Record plan to `.ds-solve-state.json` as `plan-N`.
4. Show plan table and proceed immediately. (`--confirm`: pause for user approval before executing.)

   ```
   Plan 1: {plan_summary} ({N} steps)
   | # | Step | Verification | Red Line Risk |
   |---|------|-------------|---------------|
   | 1 | {step_desc} | `{verify_cmd}` exits 0 | #{id} ({constraint}) |
   ```

**Output:** Numbered step table.

**Gate:** Plan recorded. Every step has a verification criterion. Proceed to Research.

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
   Step 1: {step_description} — 5 alternatives
   | # | Alternative | Source | CRAAP+ |
   |---|------------|--------|--------|
   | 1 | {alt_1_desc} | {source_url} (T1) | {score} |
   | 2 | {alt_2_desc} | {source_url} (T2) | {score} |
   | 3 | {alt_3_desc} | {source_url} (T1) | {score} |
   | 4 | {alt_4_desc} | {source_url} (T2) | {score} |
   | 5 | {alt_5_desc} | {source_url} (T1) | {score} |
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
[Plan 1/3] [Step 2/5] [Alt 1/5] [Round 1/3] Trying: {alternative_description}
Result: FAIL — {failure_reason}
Learned: {package}@{version} requires {dependency} >= {min_version}
Red lines: {n}/{n} held
Next: Trying alternative 2...
```

**Output:** Progress indicator per attempt.

**Gate:** Step verification passes AND all red lines hold.

### Phase 5: Backtrack [all alternatives for a step exhausted]

**Goal:** Research new alternatives incorporating learned constraints. Decision tree and constraint propagation rules in [references/backtrack-logic.md](references/backtrack-logic.md).

1. **Analyze failures.** Extract common patterns from all failure reasons for this step. What constraints did we learn?
2. **New research.** Search web for 5 new alternatives. Explicitly exclude previously tried approaches. Incorporate learned constraints in queries (e.g., "{tool} compatible with {runtime} {version}" if {runtime} version was the blocker).
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

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context (`needs_approval: Step {n} {action} — Risk: {risk} — Affected: {paths}`), ask Apply All / Review Each / Skip All.

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

FRC+DSC accounting.

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
- State file updated after every state change — survives interruption.
- Previous plans' failures inform new plans — no duplicate approaches.
- FRC accounting in summary — every step gets a disposition, equation must balance.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Severity

Not a finding-based skill. Severity applies to issues discovered during execution:

| Level | Meaning | Example |
|-------|---------|---------|
| CRITICAL | Red line violation, or objective impossible within constraints | {test_suite} fails after change; {dependency} requires {runtime} {version} but red line says {lower_version} |
| HIGH | Step exhausted all alternatives across all research rounds | {n} alternatives tried for "{step_desc}", all fail |
| MEDIUM | Alternative failed but others remain (expected during adaptive solving) | {tool_a} fails, but {tool_b} alternative exists |
| LOW | Minor issue during research or verification (stale source, slow command) | CRAAP+ score {score} source discarded |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Red line violated during execution | Immediately revert changes, record violation, try next alternative |
| Verification command fails to run | Check syntax and environment. If infrastructure issue, record as learned constraint. Example: `{tool_binary}` not found → constraint "{tool} headers missing" |
| Same alternative fails identically twice | Skip remaining retries, advance to next alternative |
| State file corrupted | Infer last successful step from git state, restart from there |
| Git state inconsistent | Stash or revert uncommitted changes before retrying |
| Web search unavailable | Fall back to local-only research, reduce alternatives target to 3, warn in summary |
| Context approaching limit | Checkpoint state, summarize completed iterations to one-line entries (keep failure reasons + constraints, discard verbose logs). Re-read state file to resume. _(W4: Memory Decay)_ |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Objective already achieved | Run verification upfront. If passes, report OK immediately. |
| Single-step objective | Skip plan decomposition. Execute directly with 5 alternatives. |
| User changes red lines mid-run | Re-validate all completed steps against new lines. If violation found, backtrack to that step. |
| Objective is vague | Infer the most conservative measurable proxy and state the assumption. Example: "{vague_goal}" → use `{benchmark_command}` < {threshold}. Only ask if zero proxy is possible. |
| All steps pass but final verification fails | Plan decomposition missed something. Enter Re-plan with constraint: "individual step success insufficient". |
| Irreversible change in a step | Flag as `needs-approval`. In `--auto` without `--force-approve`, skip and note. |
| No project documentation found | Proceed with zero auto-detected red lines + any `--red-line` flags. Apply universal defaults: "existing tests pass", "no new errors introduced". |
| Budget override too small | Warn if budget < 1x1x2. Clamp to minimum. |
| Contradictory red lines | Apply the more restrictive constraint. Log the conflict in episodic memory. If the restrictive choice blocks all alternatives → surface in Escalation report (not before). |
