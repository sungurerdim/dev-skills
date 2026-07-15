---
name: ds-tune
description: Autonomous optimization — iterate on any project with a measurable metric (Karpathy autoresearch pattern). Use when optimizing toward a metric via automated experiment loops.
---

# /ds-tune

Manual optimization is slow — 8-10 experiments per day, subjective judgment, no audit trail. Skill runs 100+ experiments autonomously, keeping only what measurably improves.

**Autonomous Optimization** — [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern generalized for any project with a measurable metric. Thanks to Andrej Karpathy for open-sourcing the core idea.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-tune`
- User asks to optimize, tune, or improve a measurable aspect of their project
- User asks "make this faster", "improve accuracy", "reduce bundle size", or similar
- User asks to set up a self-improving loop

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "make this faster", "optimize bundle size", "self-improving loop" | "audit performance once (no loop)" (→ ds-review --perf) |
| "100+ experiments for one metric" | "set performance budget + CI gate" (→ ds-launch --perf-budget) |
| "Karpathy-style autoresearch loop" | "research optimization techniques abstractly" (→ ds-research) |
| "git-ratchet: keep only improvements" | "manual optimization decisions" (→ user owns the choice) |

## Contract

**Dimensions:** D1

- One file, one metric, one loop — Karpathy's core constraint. Skill generates optimization infrastructure (`ds/tune/`), then runs the loop under the git ratchet defined in Quality Gates (only measured improvements survive; every experiment committed before mechanical evaluation).
- Standalone: use blueprint when available; own analysis when absent.
- FRC+DSC enforced. Detected pre-existing / out-of-scope errors get a concrete disposition (W11), fixed inline or escalated with a concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Full setup: discover goal, analyze project, generate `ds/tune/`, measure baseline, start loop |
| `run` | Resume loop from existing `ds/tune/` setup + `ds/audit/tune.json` |
| `status` | Show results summary (experiments, hit rate, improvement) |
| `--resume` | Equivalent to `run` — force resume from state without prompt |
| `--clean` | Delete `ds/audit/tune.json` (keeps `ds/tune/`), re-enter setup |

## Delegation

**Owns:** optimization-loop, experimentation, measurable-metric-tuning | **Delegates:** ds-test → per-experiment test validation | **Receives:** none

## Execution Flow

Discovery → Analysis → Plan → Generate → Baseline → [Needs-Approval] → Loop

### Phase 1: Discovery

**Recovery check:** DETECT `ds/audit/tune.json`. Absent + no `--resume`/`run` → fresh setup. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY: re-read `ds/tune/.autotune.json` + tail of `ds/tune/results.tsv`, skip `done` phases, enter Loop at next experiment. Announce `[TUN] Resuming from Phase {N}: {name}. Baseline {metric}={value}, {N} experiments recorded.` On user-triggered stop or context exhaustion, state persists; on graceful completion, delete state. Verify `ds/audit/` in `.gitignore` on fresh start.

**State `data`:** `{ target_file, metric, direction, secondary, bench_cmd, budget_sec, tag, tune_dir: "ds/tune/", baseline: {value, commit}, branch, experiment_count, last_experiment_idx }`.

**Findings file check:** `ds/audit/findings.md` exists with fresh `git_hash` → use as baseline context for metric selection. Blueprint scores can suggest which dimensions to optimize. **IDU:** Profile → Ideal Metrics, Type + Stack. Findings() → verify + use. Absent → own analysis.

Ask ONE question:

> What do you want to improve in this project? No technical detail needed — describe the goal in your own words.

Wait for answer. Only proceed after receiving it.

**Gate:** User stated an optimization goal. If fails (no response after one re-prompt) → exit with WARN "ds-tune: no optimization goal provided — re-run and describe what you want to improve (e.g. 'make inference faster', 'reduce bundle size')."

### Phase 2: Analysis

Work autonomously — answer from project files, asking no further questions. Apply experiment design rules from [references/rules-optimization.md](references/rules-optimization.md).

1. Read project root (README, package files, entry points, test files, benchmarks); understand stack, structure, purpose.
2. Map user's goal to measurable metric(s); identify ONE target file most relevant to goal.
3. Identify or create an evaluation method (existing tests, benchmark script, or new eval); check for existing test data and fixtures.

Determine these values:

| Field | Description |
|-------|-------------|
| `target_file` | Single file the agent will modify |
| `metric` | Primary measurable signal (e.g. {wer}, {accuracy}, {latency_ms}, {pass_rate}, {bundle_kb}, {cost_per_run}, {tokens_per_request}) |
| `direction` | `lower` or `higher` — which direction is better |
| `secondary` | Optional second metric for monitoring (not for keep/discard decisions) |
| `bench_cmd` | Command to run evaluation |
| `budget_sec` | Max seconds per experiment (based on eval duration) |
| `noisy` | `true`/`false` — does the metric vary run-to-run under identical conditions? Wall-clock, latency, throughput, sampled-accuracy → `true`. Byte/line/file counts, bundle size, lint-error count → `false`. Uncertain → default `true` (OPT-05, conservative). |

**Gate:** All fields determined; metric is mechanical (computable in seconds, deterministic). If fails (no mechanical metric inferrable) → present 2–3 candidate proxy metrics with suggested `bench_cmd` (e.g. lint error count, test pass rate, timing), ask user to confirm one; user declines all → exit with WARN "ds-tune: cannot proceed without a measurable metric — provide a benchmark command or choose one of the suggested proxies."

### Phase 3: Plan

Show summary:

```
Project: {project-name} | Goal: {user-goal in their words}
File: {target_file} | Metric: {metric} ({direction}: lower/higher is better)
Bench: {bench_cmd} | Budget: {budget_sec} seconds / experiment
```

Test data missing → state what will be created. Ask: "Confirm? (yes / suggest changes)"

**Gate:** User confirmed. If fails (user suggests changes) → apply requested changes to plan (target_file, metric, bench_cmd, budget_sec), redisplay updated summary, ask re-confirmation; user asks to abort → exit cleanly without creating `ds/tune/` files.

### Phase 4: Generate

Create these files in project `ds/tune/` (committed; `ds/<skill>/` is the user-facing operational namespace):

**`ds/tune/.autotune.json`** — Configuration:
```json
{
  "target": "{target_file}",
  "metric": "{metric}",
  "direction": "{lower|higher}",
  "secondary": "{secondary|null}",
  "bench_cmd": "{command}",
  "budget_sec": {number},
  "tag": "{YYYY-MM-DD}",
  "noisy": {true|false},
  "runs_n": {3 if noisy else 1}
}
```

**`ds/tune/bench.sh`** — Evaluation wrapper:
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
{eval_command} > ds/tune/run.log 2>&1
```
Requirements: cd to project root, redirect ALL output to `ds/tune/run.log`, output metrics as `{metric}:    {value}` (grep-able), complete within `budget_sec`.

**`ds/tune/eval`** — Project-specific evaluation (Python, Bash, or project language). Must output metrics in exact format: `{metric}:    {value}`. If test data doesn't exist, create minimal fixtures.

**`ds/tune/results.tsv`** — Initialize with header `timestamp	commit	status	{metric}	{secondary}	duration	description`. Column notes: `timestamp` ISO 8601; `duration` is `HH:MM:SS` (wall-clock).

**`ds/tune/program.md`** — Agent instructions generated from [references/program-template.md](references/program-template.md) with all project-specific values filled in.

**Gate:** All files created and executable. If fails (file uncreatable or `bench.sh`/`eval` not executable) → surface specific file + error (e.g. "ds/tune/bench.sh: permission denied"), attempt `chmod +x` on shell scripts, retry once; still failing → exit with WARN listing unresolved files — do not proceed to Phase 5 over a broken eval setup.

### Phase 5: Baseline

1. Run `bash ds/tune/bench.sh` — `noisy: true` → `runs_n` times (OPT-05, same condition as the Loop) and record mean ± stddev; `noisy: false` → once. Extract metrics by searching for `{metric}:` in `ds/tune/run.log`; record baseline in `results.tsv`.
2. Commit `ds/tune/`: `git add ds/tune/ && git commit -m "autotune: setup with baseline"`; create branch: `git checkout -b autotune/{tag}`.
3. Write `ds/audit/tune.json` with canonical envelope + baseline snapshot in `data`.
4. Report: `Baseline: {metric} = {value} | Branch: autotune/{tag}`

**Gate:** Baseline measured and committed. If fails (`bench.sh` returns non-zero or no metric line found in `ds/tune/run.log`) → show raw log to user, surface specific error (missing metric line, eval script crash, missing dependency), exit with WARN "ds-tune: baseline measurement failed — fix ds/tune/eval or ds/tune/bench.sh and re-run"; do not proceed to the Loop with an unmeasured baseline.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails (no response) → mark unresolved `skipped (user did not respond)` in state.data, proceed to Loop.

### Phase 7: Loop

Execute the experiment loop defined in `ds/tune/program.md` (steps 1-9 of [references/program-template.md](references/program-template.md)). Follow it exactly, with three skill-side rules layered on top:

- **Significance check (OPT-05, template steps 5-6):** `noisy: true` → run `bash ds/tune/bench.sh` `runs_n` times (min 3) under identical conditions instead of once; extract the metric from each run, compute mean ± standard deviation. When the `runs_n` runs disagree wildly (stddev > baseline mean), still decide by the 2×stddev rule below — keep all runs, drop no outliers. `noisy: false` → single run, exactly as the template states.
- **Decision (template step 8, strengthened):** `noisy: false` → metric improved AND no test regressions (run full test suite, not just bench) → KEEP, branch advances; metric same or worse OR any previously passing test now fails → DISCARD. `noisy: true` → KEEP only if (mean improved in `direction`) AND (improvement exceeds 2× the combined standard deviation of baseline and experiment) AND no test regressions; otherwise DISCARD as statistically insignificant (log the row with mean±stddev in the `description` column so it reads as noise, not a bug). DISCARD in either case: `git reset HEAD~1 --hard`. (Per [references/principles.md §7](references/principles.md): a metric win that breaks tests is still a regression; per OPT-05, a metric win within noise is not a win.)
- **After each experiment:** update `ds/audit/tune.json` — increment `experiment_count`, update `last_experiment_idx`, phase 7 stays `in_progress`.

**Gate:** Each experiment appends exactly one `keep|discard|crash` row to `results.tsv`; the loop exits on user interrupt, context exceeding 85% of the model token limit (checked each iteration), or `experiment_count` reaching `--budget`. If an experiment fails (`bench.sh` non-zero and no parseable metric on any run) → log a `crash` row and continue to the next; if `git reset --hard` fails during DISCARD → stop the loop, surface git state, and ask the user to clean up before resuming.

## program.md Template

Generated in Phase 4 with all placeholders filled — full template in [references/program-template.md](references/program-template.md) (loaded only during Phase 4 generation and Phase 7 loop).

## `/ds-tune run` — Resume

1. Read `ds/audit/tune.json` — verify `skill: ds-tune`, `version: 1`, `git_hash` vs HEAD (prompt on mismatch).
2. Verify `ds/tune/` folder exists; read `ds/tune/.autotune.json`, `ds/tune/program.md`, and `ds/tune/results.tsv` (current baseline = last `keep` entry).
3. Check current git branch — not on `autotune/*` → checkout the branch.
4. Resume loop from `ds/tune/program.md`, announce `[TUN] Resuming from experiment {N+1}, current best = {metric}={value}`.

## `/ds-tune status` — Results

Read `ds/tune/results.tsv`, display summary:

```
Total experiments: {count} | Kept: {kept_count} | Discarded: {discarded_count} | Crashed: {crashed_count} | Hit rate: {kept/total}%
Baseline: {first keep metric} | Best: {best metric} | Improvement: {improvement}%
Total time: {sum of durations, HH:MM:SS} | Avg per experiment: {avg HH:MM:SS}
First experiment: {earliest timestamp} | Last experiment: {latest timestamp}

Last 5 experiments: {last 5 rows from results.tsv as table}
```

Summary line:
```
ds-tune: {OK|WARN|FAIL} | Experiments: {n} | Best: {metric_value} | Improvement: {delta} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Then show git log of kept improvements: `git log --oneline autotune/{tag} | head -10`.

**Value Delivered:** 1-5 concrete optimization outcomes. Example shapes (placeholders, not literal):

- `Metric improved from {baseline-value} to {best-value} ({direction} {delta}) across {n} accepted experiments — gain is git-ratcheted, only improvements survived`
- `{n} experiments rejected as no-improvement / regression — failed paths discarded, no manual cleanup needed`
- `Full audit trail: every experiment committed before evaluation — what improved {metric} is reproducible from git log alone`
- `Bench harness at ds/tune/bench.sh repeatable on any machine — re-validation does not require the original session`

Zero-improvement run: `{n} experiments ran, none beat baseline {baseline-value} — current implementation appears near a local optimum for this metric / harness`.

## Quality Gates

- Every experiment committed before evaluation — full audit trail in git
- Only target file modified — all other files read-only
- Metric evaluation mechanical (deterministic script output, not subjective)
- Discarded experiments fully reverted (`git reset --hard`) — zero residue
- `results.tsv` append-only — complete experiment history preserved
- Simplicity criterion: complexity must earn its keep with measurable improvement
- **Shell quoting ([references/principles.md §5](references/principles.md)):** generated `ds/tune/bench.sh` and `ds/tune/eval` MUST quote every variable reference (`"$VAR"`, `"${VAR}"`). Never interpolate user-supplied metric names or commands without quoting.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/tune.json` updated per experiment, `ds/audit/` in `.gitignore`, cleared only on user-confirmed completion (`ds/tune/` stays committed). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W12: an experiment wins only if the real goal improves, not just the metric (Goodhart) — never special-case the scorer, hard-code target values, or overfit the eval (see references/rules-optimization.md OPT-07).

## Error Recovery

| Situation | Action |
|-----------|--------|
| `bench.sh` fails to run | Check script permissions, verify eval dependencies exist |
| Metric not found in `run.log` | Check eval script output format, verify grep pattern |
| Experiment exceeds time budget | Kill process, log as crash, move to next hypothesis |
| Git conflict on reset | Stash changes, hard reset to last keep commit |
| No improvement after 10 consecutive experiments | Re-read target file, analyze `results.tsv` patterns, try fundamentally different approaches |
| `ds/tune/` folder missing (for `run`) | Run full setup first |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No testable metric exists | Help user define one: suggest assertions, benchmarks, or timing measurements |
| Multiple files need changes | Identify ONE most impactful file. If changes truly span files, expand target scope but keep it minimal |
| Metric is subjective (e.g. "code quality") | Convert to mechanical proxy: lint error count, test pass rate, complexity score |
| Eval takes > 5 minutes | Suggest sampling (subset of test data) or lighter proxy metric |
| User wants to optimize prompt/SKILL.md | Target = the .md file, metric = eval assertions pass rate |
| Project has no tests | Create minimal eval fixtures in Phase 4 |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
