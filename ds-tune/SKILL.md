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
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Full setup: discover goal, analyze project, generate `ds/tune/`, measure baseline, start loop |
| `--resume` | Resume loop from existing `ds/tune/` setup + `ds/audit/tune.json`, without prompt |
| `--status` | Show results summary (experiments, hit rate, improvement) |
| `--clean` | Delete `ds/audit/tune.json` (keeps `ds/tune/`), re-enter setup |
| `--budget={n}` | Stop the loop after {n} experiments (default: run until user interrupt or context limit) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

## Delegation

**Owns:** optimization-loop, experimentation, measurable-metric-tuning | **Delegates:** ds-test → per-experiment test validation | **Receives:** none

## Execution Flow

Discovery → Analysis → Plan → Generate → Baseline → [Needs-Approval] → Loop

### Phase 1: Discovery

**Recovery check:** DETECT `ds/audit/tune.json`. Absent + no `--resume` → fresh setup. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY: re-read `ds/tune/.autotune.json` + tail of `ds/tune/results.tsv`, skip `done` phases, enter Loop at next experiment. Announce `[TUN] Resuming from Phase {N}: {name}. Baseline {metric}={value}, {N} experiments recorded.` On user-triggered stop or context exhaustion, state persists; on graceful completion, delete state. Fresh start: `grep -qx 'ds/audit/' .gitignore` → exit 0; non-zero → append `ds/audit/` and report the addition.

**State `data`:** `{ target_file, metric, direction, secondary, bench_cmd, budget_sec, tag, tune_dir: "ds/tune/", baseline: {value, commit}, branch, experiment_count, last_experiment_idx }`.

**Findings file check:** `ds/audit/findings.md` exists with fresh `git_hash` → use as baseline context for metric selection. **Upstream artifacts:** Profile → {`Scores:` — suggests which dimension to optimize, `Ideal:`, `Type:`, `Stack:`}. Findings() → verify + use. Absent → own analysis.

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

**Gate:** All fields determined; metric is mechanical (computable in seconds, deterministic). If fails (no mechanical metric inferable) → present 2–3 candidate proxy metrics with suggested `bench_cmd` (e.g. lint error count, test pass rate, timing), ask user to confirm one; user declines all → exit with WARN "ds-tune: cannot proceed without a measurable metric — provide a benchmark command or choose one of the suggested proxies."

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

Create these files in project `ds/tune/` (committed; `ds/<skill>/` is the user-facing operational namespace): `.autotune.json` (config), `bench.sh` (evaluation wrapper), `eval` (project-specific evaluation script), `results.tsv` (append-only log — header `timestamp commit status {metric} {secondary} duration description`). Exact schema, script contract, and format requirements: [references/generated-files.md](references/generated-files.md).

**`ds/tune/program.md`** — Agent instructions generated from [references/program-template.md](references/program-template.md) with all project-specific values filled in.

**Gate:** All files created and executable — `test -x ds/tune/bench.sh && test -x ds/tune/eval && test -f ds/tune/.autotune.json && test -f ds/tune/results.tsv && test -f ds/tune/program.md` → exit 0. If fails (file uncreatable or `bench.sh`/`eval` not executable) → surface specific file + error (e.g. "ds/tune/bench.sh: permission denied"), attempt `chmod +x` on shell scripts, retry once; still failing → exit with WARN listing unresolved files — do not proceed to Phase 5 over a broken eval setup.

### Phase 5: Baseline

0. **Checkpoint pre-gate (stop-hard):** `git status --porcelain` → exclude `ds/tune/` and `ds/audit/` lines → empty output → proceed; non-empty → the loop does not start (Phase 7's DISCARD, `git reset HEAD~1 --hard`, resets tracked files and would destroy uncommitted work). Default: stop, record `only you can do: dirty working tree — commit or stash before the experiment loop`. `--ask`: show the dirty files, ask Commit first (recommended) / Stash / Abort — Proceed-anyway is never offered for this stop-hard skill. Full protocol: [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md).
1. Run `bash ds/tune/bench.sh` — `noisy: true` → `runs_n` times (OPT-05, same condition as the Loop) and record mean ± stddev; `noisy: false` → once. Extract metrics by searching for `{metric}:` in `ds/tune/run.log`; record baseline in `results.tsv`.
2. Create branch first, then commit setup on it (the user's current branch stays untouched): `git checkout -b autotune/{tag} && git add ds/tune/ && git commit -m "autotune: setup with baseline"` — then `git branch --show-current` → `autotune/{tag}`.
3. Write `ds/audit/tune.json` with canonical envelope + baseline snapshot in `data`.
4. Report: `Baseline: {metric} = {value} | Branch: autotune/{tag}`

**Gate:** Baseline measured and committed. If fails (`bench.sh` returns non-zero or no metric line found in `ds/tune/run.log`) → show raw log to user, surface specific error (missing metric line, eval script crash, missing dependency), exit with WARN "ds-tune: baseline measurement failed — fix ds/tune/eval or ds/tune/bench.sh and re-run"; do not proceed to the Loop with an unmeasured baseline.

### Phase 6: Needs-Approval Review [needs_approval > 0]

**Default:** every item resolves automatically using the same impact/effort/risk reasoning an approval block would show, recorded in the summary; items matching the publish/irreversible exception list are skipped and recorded `only you can do` instead. **`--ask`:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails (no response) → mark unresolved `skipped (user did not respond)` in state.data, proceed to Loop.

### Phase 7: Loop

Execute the experiment loop defined in `ds/tune/program.md` (steps 1-9 of [references/program-template.md](references/program-template.md)). Follow it exactly, with skill-side rules layered on top — significance check, keep/discard decision table, reward-hacking + loop-abort red flags, Mechanical Done Gate, per-experiment bookkeeping, Goodhart exit check: [references/loop-mechanics.md](references/loop-mechanics.md).

**Gate:** Each experiment appends exactly one `keep|discard|crash` row to `results.tsv`; the loop exits on user interrupt, context exceeding 85% of the model token limit (checked each iteration), `experiment_count` reaching `--budget`, or a loop-abort red flag firing (regression streak / runtime blowout / gate red). If an experiment fails (`bench.sh` non-zero and no parseable metric on any run) → log a `crash` row and continue to the next; if `git reset --hard` fails during DISCARD → stop the loop, surface git state, and ask the user to clean up before resuming.

## program.md Template

Generated in Phase 4 with all placeholders filled — full template in [references/program-template.md](references/program-template.md) (loaded only during Phase 4 generation and Phase 7 loop).

## `/ds-tune --resume` — Resume

1. Read `ds/audit/tune.json` — verify `skill: ds-tune`, `version: 1`, `git_hash` vs HEAD (prompt on mismatch).
2. Verify `ds/tune/` folder exists; read `ds/tune/.autotune.json`, `ds/tune/program.md`, and `ds/tune/results.tsv` (current baseline = last `keep` entry).
3. `git branch --show-current` → not `autotune/*` → checkout the branch. Then apply the Phase 5 Checkpoint pre-gate (stop-hard) — the loop never resumes over a dirty tree either.
4. Resume loop from `ds/tune/program.md`, announce `[TUN] Resuming from experiment {N+1}, current best = {metric}={value}`.

## `/ds-tune --status` — Results

Read `ds/tune/results.tsv`, display summary. Compute every count, rate, and duration with a single `awk` pass over `results.tsv` — never by manual tallying of rows. Output shape: [references/generated-files.md](references/generated-files.md) § `--status` output shape.

Summary line:
```
ds-tune: {OK|WARN|FAIL} | Experiments: {n} | Best: {metric_value} | Improvement: {delta} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Then show git log of kept improvements: `git log --oneline autotune/{tag} | head -10`.

Disposition accounting — totals balance. Closing shape (`Decided without asking` lines, every `only you can do` item in full): [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

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
- **Shell quoting ([../core/principles.md §5](../core/principles.md)):** generated `ds/tune/bench.sh` and `ds/tune/eval` MUST quote every variable reference (`"$VAR"`, `"${VAR}"`). Never interpolate user-supplied metric names or commands without quoting.
- W9: `ds/audit/tune.json` updated per experiment, `ds/audit/` in `.gitignore`, cleared only on user-confirmed completion (`ds/tune/` stays committed). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W12: an experiment wins only if the real goal improves, not just the metric (Goodhart) — never special-case the scorer, hard-code target values, or overfit the eval (see references/rules-optimization.md OPT-07).
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| `bench.sh` fails to run | Check script permissions, verify eval dependencies exist |
| Metric not found in `run.log` | Check eval script output format, verify grep pattern |
| Experiment exceeds time budget | Kill process, log as crash, move to next hypothesis |
| Git conflict on reset | Stash changes, hard reset to last keep commit |
| No improvement after 10 consecutive experiments | Re-read target file, analyze `results.tsv` patterns, try fundamentally different approaches |
| `ds/tune/` folder missing (for `--resume`) | Run full setup first |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No testable metric exists | Help user define one: suggest assertions, benchmarks, or timing measurements |
| Multiple files need changes | Identify ONE most impactful file. If changes truly span files, expand target scope but keep it minimal |
| Metric is subjective (e.g. "code quality") | Convert to mechanical proxy: lint error count, test pass rate, complexity score |
| Eval takes > 5 minutes | Suggest sampling (subset of test data) or lighter proxy metric |
| User wants to optimize prompt/SKILL.md | Target = the .md file, metric = eval assertions pass rate |
| Project has no tests | Create minimal eval fixtures in Phase 4 |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
