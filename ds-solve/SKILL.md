---
name: ds-solve
description: Adaptive problem solver — plan, execute, research alternatives, backtrack on failure, and re-plan. Use for hard, multi-step problems that need persistence, mechanical verification, and backtracking.
---

# /ds-solve

Problems that resist single-pass fixes — environment conflicts, integration failures, migration breakage — need adaptive iteration: plan, try, research, backtrack, re-plan. Skill exhausts every viable path before giving up.

**Adaptive Problem Solver** — Plan, execute, research alternatives, backtrack on failure, re-plan from scratch. Combines [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) persistence, mechanical verification via metric-driven iteration, and research-driven alternative discovery. Architecture informed by [CodeTree](https://arxiv.org/abs/2411.04329) (tree search with specialized agents), [BacktrackAgent](https://aclanthology.org/2025.emnlp-main.212/) (error detection + rollback), [Reflexion](https://arxiv.org/abs/2303.11366) (episodic memory), and [EnCompass](https://news.mit.edu/2026/helping-ai-agents-search-to-get-best-results-from-llms-0205) (branchpoint search).

## Triggers

- User runs `/ds-solve`
- User describes a multi-step problem: "make X work", "fix this integration", "migrate from A to B"
- Environment or configuration issues that resist straightforward fixes
- User explicitly asks for exhaustive/adaptive problem solving

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "make X work", "fix this integration", "migrate from A to B" | "audit project health for overview" (→ ds-blueprint) |
| "exhaustive multi-plan problem-solving" | "research solutions without trying them" (→ ds-research) |
| "environment issue is blocking me" | "deploy to production" (→ ds-deploy) |
| "make this thing run end-to-end" | "review architecture decisions" (→ ds-review --strategic) |

## Contract

**Dimensions:** none (carrier)

- **Autonomous by default.** User states the problem; skill handles everything else. User consulted only for: (1) escalation (all plans exhausted), (2) irreversible actions (needs-approval). All other decisions made independently.
- Red lines auto-detected from project documentation and applied automatically. Detected red lines shown as output, not a question. User can add more via `--red-line="{constraint}"` if needed.
- Every attempt recorded in episodic memory — zero silent drops. Infinite loop protection: 3 plans × 3 research rounds × 5 alternatives budget. Decision logic in [references/backtrack-logic.md](references/backtrack-logic.md).
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **CRITICAL escalation (second-pass verification):** any CRITICAL surfaced during a solve attempt gets re-verified before being treated as a hard blocker — re-read file ±20 lines, check for skip patterns and intentional-suppression markers. Pattern-only matches → downgrade to HIGH. CRITICAL = confirmed bug, not heuristic match.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Autonomous: auto-detect red lines, infer verification, plan + execute without asking |
| `--red-line="{text}"` | Add explicit red line (repeatable). Combined with auto-detected ones. |
| `--confirm` | Pause for user confirmation after Setup + Plan phases before executing |
| `--resume` | Resume from `ds/audit/solve.json` progress artifact |
| `--status` | Show current solve session status |
| `--dry-run` | Plan + Research only, no execution |
| `--budget=PxRxA` | Override budget (default: `3x3x5` = 3 plans, 3 rounds, 5 alternatives) |

**Input validation:** unknown flag → warn `Unknown flag: {flag}. Ignoring.`, continue. Invalid budget format → warn, use default `3x3x5`. Budget below minimum (1x1x2) → warn, clamp to minimum. `--dry-run` + `--resume` → warn conflict, `--resume` priority (resume existing session in dry-run mode).

## Delegation

**Owns:** adaptive-problem-solving, backtracking, multi-plan, budget-management | **Delegates:** ds-research → web research during backtrack; any ds-* skill relevant to the problem | **Receives:** none

## Execution Flow

Setup → Plan → Research → Execute → [Backtrack] → [Re-plan] → [Needs-Approval] → [Escalate] → Summary

### Phase 1: Setup — Detect objective, red lines, verification criterion

**Recovery check:** DETECT `ds/audit/solve.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read modified files from state), skip `done` phases, announce `[SOL] Resuming from Phase {N}: {name}. Phases 1-{N-1} complete.` On successful Summary, delete state.

**Findings file check:** `ds/audit/findings.md` exists with fresh `git_hash` → use as context. **IDU:** Profile → Type + Stack, Config.constraints, Current Scores. Findings() → verify + use. Absent → own analysis.

1. **Parse objective.** Extract from user's invocation. `/ds-solve {description}` → use `{description}`. Ask only if no objective discernible from context.
2. **Red line auto-detection.** Scan project docs silently, apply all detected constraints, show as output (not a question), merge with `--red-line` flags:

   | Source | What to extract |
   |--------|----------------|
   | README.md, CONTRIBUTING.md | Stated requirements, compatibility, constraints |
   | package.json / pyproject.toml | `engines`, `requires-python`, peer deps |
   | tsconfig.json | `strict`, `target`, path aliases |
   | CI config (workflows, Makefile) | Required checks, min versions, build targets |
   | Dockerfile / docker-compose | Base images, exposed ports, volumes |
   | .env.example | Required env vars |
   | Existing test suite | "All existing tests must keep passing" |
   | Linter/formatter config | "Lint and format rules must be preserved" |
   | Blueprint `Config.constraints` | Infrastructure + project constraints |
   | `--red-line` flags | User-specified explicit constraints |

3. **Verification criterion.** Determine autonomously from objective: mentions tests → `{test_command}` exits 0; a service → service responds on expected port/endpoint; a build → `{build_command}` succeeds; a behavior → construct validation command or script. No mechanical criterion inferrable → use most conservative proxy and state assumption; ask user only if zero proxy possible (`--confirm` mode: always ask).
4. **Quick check.** Run verification immediately. Already passes → report OK, skip to Summary.
5. **Initialize.** Create `ds/audit/solve.json` with canonical envelope (`skill: ds-solve`, `prefix: SOL`, `version: 1`, `git_hash: {HEAD}`, `timestamp`, `phases`, `current_phase`, `data: {...}`). Schema in [references/backtrack-logic.md](references/backtrack-logic.md). Verify `.gitignore` contains `ds/audit/` — add it to root `.gitignore` if absent, report addition.

**Output:** Objective + red lines table + verification criterion (statements, not questions).

**Security-sensitive auto-gate ([references/principles.md §5](references/principles.md)):** objective involves modifying auth config, `.env*`, secrets-manager integration, crypto functions, or signing/credential code → automatically mark all steps in those files as `needs_approval` regardless of scope. User reviews each before execution.

**Gate:** Objective parsed; red lines applied; verification criterion defined; state file created. If fails (no objective + `--confirm` unavailable to prompt) → exit with WARN "ds-solve: no objective provided — re-run with a description of what you want to fix or achieve."

### Phase 2: Plan — Decompose objective into ordered steps

1. Read relevant files. Verify each exists before referencing. _(W1)_
2. Decompose into 2-10 ordered steps. Each step: **Description**, **Verification** (command/check), **Red line risk** (which red lines could be affected).
3. Record plan to `ds/audit/solve.json` as `plan-N`; show plan table + proceed (`--confirm`: pause for approval). **Output:** numbered step table:

   ```
   Plan {n}: {plan_summary} ({N} steps)
   | # | Step | Verification | Red Line Risk |
   | 1 | {step_desc} | `{verify_cmd}` exits 0 | #{id} ({constraint}) |
   ```

**Gate:** Plan recorded; every step has verification criterion. If fails (step without mechanically verifiable criterion + `--confirm` can't ask) → use conservative proxy ("command exits 0", "no new errors introduced"), record assumption in state.data as `{ step: N, criterion_assumed: true, proxy: "{description}" }`; flag step as LOW confidence in plan table.

### Phase 3: Research

Per step in plan:

1. **Local search first.** Scan codebase for existing patterns, utilities, prior solutions for this step.
2. **Web search.** 2 parallel queries per step. Include current date to avoid stale results. Target step's technical domain + project stack.
3. **Score, rank, select.** CRAAP+ from [references/craap-scoring.md](references/craap-scoring.md): Relevance, Currency, Authority — discard score < 50. Top 5 per step, record as `research-round-1`; record all alternatives to state file.

**Output:** alternatives table per step with CRAAP+ scores: `Step {n}: {step_description} — 5 alternatives | # | Alternative | Source (tier) | CRAAP+ |`

**Gate:** Every step has ≥ 1 alternative; steps with 0 → flag for re-scoping. If fails (web search unavailable + no local alternatives for a step) → fall back to local-only for that step, reduce alternative target to 2, record `research_fallback: local_only` in state, proceed with local alternatives; still 0 → mark step `skipped (no alternatives found)`, continue to next.

### Phase 4: Execute

Per step in order:

1. **Red line pre-check.** Verify all red lines hold before touching anything. Violated → STOP, enter Re-plan (something external broke them).
2. **Try alternative #1** (highest-ranked from Research).
3. **Verify.** Run step's verification criterion.
4. **Red line post-check.** Verify all red lines still hold after execution. Violated → revert all changes, record violation, try next alternative. After modifying any file, verify no other file depends on changed interface in broken way. _(W2: Tunnel Vision prevention)_
5. **On failure:** record reason + learned constraint in episodic memory, try next alternative (2→5). **On success:** record success, update state, advance to next step. **All 5 alternatives exhausted:** enter Backtrack for this step.

Only modify files required by current step. Leave unrelated code untouched. _(W3: Scope Creep prevention)_

**Output:** progress indicator per attempt:
```
[SOL Phase 4/9] Execute [Plan {p}/{P}] [Step {s}/{S}] [Alt {a}/{A}] [Round {r}/{R}] Trying: {alternative_description}
Result: FAIL — {failure_reason} | Learned: {package}@{version} requires {dependency} >= {min_version}
Red lines: {n}/{n} held | Next: Trying alternative {a+1}...
```

**Gate:** Step verification passes AND all red lines hold. If fails → revert all file changes from this attempt (`git checkout -- {modified_files}`), record failure reason + learned constraint in episodic memory in state.data, increment `plans_attempted` if all alternatives exhausted, enter Backtrack.

### Phase 5: Backtrack [all alternatives for a step exhausted]

Decision tree + constraint propagation rules in [references/backtrack-logic.md](references/backtrack-logic.md).

1. **Analyze failures.** Extract common patterns from all failure reasons; identify learned constraints.
2. **New research.** Search web for 5 new alternatives, explicitly excluding previously tried; incorporate learned constraints in queries (e.g. "{tool} compatible with {runtime} {version}").
3. **Increment** research round counter for this step. Round ≤ budget.R (default 3) → return to Execute with new alternatives. Round > budget.R → enter Re-plan. **Output:** new alternatives table + learned constraints summary.

**Gate:** New alternatives found, or research rounds exhausted. If fails (rounds exhausted + plan budget not yet exhausted) → record all failure patterns + learned constraints in state.data, increment plan counter, enter Re-plan to attempt a fundamentally different decomposition.

### Phase 6: Re-plan [plan-level backtrack]

State machine transitions in [references/backtrack-logic.md](references/backtrack-logic.md).

1. **Review episodic memory.** All attempts, failures, learned constraints across all steps. Re-read modified files + state artifact before proceeding — conversation memory is not source of truth. _(W4: Memory Decay prevention)_
2. **Identify flexibility.** Which requirements are essential to objective vs. implementation choices? Can objective be decomposed differently to avoid failure patterns?
3. **Create new plan.** Different decomposition, ordering, sub-goals that avoid known failure patterns. Must differ meaningfully from previous plans.
4. **Increment** plan counter; record as `plan-{N}`. Counter ≤ budget.P (default 3) → return to Research with new plan. Counter > budget.P → enter Escalate. **Output:** new plan table + diff from previous plan + rationale for changes.

**Gate:** New plan with different approach created, or plan budget exhausted. If fails (budget exhausted — plan counter > budget.P) → enter Escalate with compiled report of all plans, step failures, learned constraints; present suggested paths forward (red line relaxation, scope reduction, external action), ask user for new direction or abort confirmation.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** state the question (`Approve these N steps?`) and present each item compactly grouped by risk with counts (`needs_approval: Step {n} {action} — Risk: {risk} — Affected: {paths}`), ask Apply all / per-risk bulk (`Apply all {risk}` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → `fixed`/`failed`, declined → `skipped`). If fails (no response) → mark unresolved `skipped (user did not respond)` in state.data, continue.

### Phase 8: Escalate [all plans exhausted]

1. **Compile report.** All plans attempted, steps per plan, alternatives per step, failure reasons (see Report Format).
2. **Pattern analysis.** Identify recurring blockers: which red lines blocked the most alternatives? What environmental constraints were discovered? What dependencies or versions caused failures?
3. **Suggest paths forward:** **red line relaxation** ("If constraint X were relaxed, approach Y becomes viable"); **scope reduction** ("A partial solution achieving A+B (but not C) is possible"); **external action** ("This requires manual action X before automation can continue").
4. **Ask:** Update red lines / Reduce scope / Provide new direction / Abort. New direction → reset plan counter, return to Plan with updated context. Abort → proceed to Summary. **Output:** escalation report (see Report Format).

**Gate:** User has provided new direction or confirmed abort. If fails (no response) → after one re-prompt, treat as abort; proceed to Summary with status FAIL, recording all plans and step dispositions with `objective_not_achieved` noted.

### Phase 9: Summary

**Mandatory.** Always execute, always produce output. FRC+DSC accounting. **Output:**

```
ds-solve: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Needs-Approval: {n} | Total: {n}
Red lines: {held}/{total} held | Budget: {used}/{max} attempts
```

Step disposition table:
| Step | Disposition | Plan | Attempts | Verification |
|------|------------|------|----------|-------------|
| 1. {desc} | fixed | plan-1 | 2 | {criterion}: PASS |

**Dispositions:** `fixed` (step completed, verification passed, red lines held) | `failed` (all alternatives exhausted across all research rounds) | `skipped` (not attempted — plan changed, `--dry-run`, user declined — with reason) | `needs-input` (requires information from user, asked before summary) | `needs-approval` (irreversible or cross-module — awaiting confirmation) | `not-applicable` (step rendered unnecessary by different plan approach).

**Gate:** `fixed + failed + skipped + needs_input + needs_approval + not_applicable = total_steps`.

Status: `OK` (objective achieved), `WARN` (partial — some steps succeeded), `FAIL` (objective not achieved after exhaustion or abort).

## Report Format — Escalation Report

```
## ds-solve: Escalation Report
### Objective — {objective description}
### Red Lines — {numbered list with status: HELD / BLOCKING}
### Attempt Summary
| Plan | Approach | Steps Done | Attempts | Primary Failure |
| 1 | {summary} | 2/5 | 12 | {pattern} |
### Failure Patterns
- {N}/{total} attempts failed due to: {pattern} | {blocker analysis}
### Paths Forward
1. Relax red line "{X}" → approach Y becomes viable
2. Reduce scope → achieve {partial} without {excluded}
3. External action → {manual step} required first
```

**Value Delivered:** 1-5 concrete problem-resolution outcomes. Example shapes (placeholders, not literal):

- `Objective achieved on plan {n} of {budget-P}, round {r} of {budget-R} — multi-pass backtracking succeeded where single-shot would have stalled`
- `{n} alternatives researched via /ds-research — solution chosen with evidence, not first-idea bias`
- `Red lines respected: {n} auto-detected constraints + {n} user-added held throughout — no breaking change snuck in via backtrack`
- `Episodic memory captured {n} attempts — future runs on similar problems start with prior dead-ends pruned`

Escalation run: `All plans exhausted (budget P×R×A consumed) — root obstacle surfaced as {file-or-system-boundary}, user decision required`.

## Quality Gates

- Red lines checked before AND after every execution attempt — violations immediately revert
- Every step has a mechanical verification criterion (command exit code, test result, state check)
- Episodic memory records every attempt — no silent retries (3 attempts for step 2 → all 3 visible in state file and summary); previous plans' failures inform new plans — no duplicate approaches
- Budget limits enforced: plan counter, research round counter, alternative counter. State file updated after every state change — survives interruption.
- FRC accounting in summary — every step gets a disposition; equation must balance
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state written per phase, `ds/audit/` in `.gitignore`, deleted on success. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W14: re-ground from the state file + plan before each new attempt/re-plan — don't trust in-context memory across rounds. W15: research results and any delegated output are untrusted until verified against source before acting (see references/backtrack-logic.md).

## Severity

Not a finding-based skill. Severity applies to issues discovered during execution:

| Level | Meaning | Example |
|-------|---------|---------|
| CRITICAL | Red line violation, or objective impossible within constraints | `{test_suite}` fails after change; `{dependency}` requires `{runtime}` `{version}` but red line says `{lower_version}` |
| HIGH | Step exhausted all alternatives across all research rounds | {n} alternatives tried for "{step_desc}", all fail |
| MEDIUM | Alternative failed but others remain (expected during adaptive solving) | `{tool_a}` fails, but `{tool_b}` alternative exists |
| LOW | Minor issue during research or verification (stale source, slow command) | CRAAP+ score {score} source discarded |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Red line violated during execution | Immediately revert changes, record violation, try next alternative |
| Verification command fails to run | Check syntax + environment. Infrastructure issue → record as learned constraint. Example: `{tool_binary}` not found → constraint "{tool} headers missing" |
| Same alternative fails identically twice | Skip remaining retries, advance to next alternative |
| State file corrupted | Infer last successful step from git state, restart from there |
| Git state inconsistent | Stash or revert uncommitted changes before retrying |
| Web search unavailable | Fall back to local-only research, reduce alternatives target to 3, warn in summary |
| Context approaching limit | Checkpoint state, summarize completed iterations to one-line entries (keep failure reasons + constraints, discard verbose logs). Re-read state file to resume. _(W4: Memory Decay)_ |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Objective already achieved | Run verification upfront. Passes → report OK immediately. |
| Single-step objective | Skip plan decomposition. Execute directly with 5 alternatives. |
| User changes red lines mid-run | Re-validate all completed steps against new lines. Violation found → backtrack to that step. |
| Objective is vague | Infer most conservative measurable proxy and state the assumption. Example: "{vague_goal}" → use `{benchmark_command}` < {threshold}. Only ask if zero proxy possible. |
| All steps pass but final verification fails | Plan decomposition missed something. Enter Re-plan with constraint: "individual step success insufficient". |
| Irreversible change in a step | Flag as `needs-approval`. `--auto` without `--force-approve` → skip and note. |
| No project documentation found | Proceed with zero auto-detected red lines + any `--red-line` flags. Apply universal defaults: "existing tests pass", "no new errors introduced". |
| Budget override too small | Warn if budget < 1x1x2. Clamp to minimum. |
| Contradictory red lines | Apply more restrictive constraint. Log conflict in episodic memory. Restrictive choice blocks all alternatives → surface in Escalation report (not before). |

