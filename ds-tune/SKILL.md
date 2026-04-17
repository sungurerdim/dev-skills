# /ds-tune

Manual optimization is slow — 8-10 experiments per day, subjective judgment, no audit trail. Skill runs 100+ experiments autonomously, keeping only what measurably improves.

**Autonomous Optimization** — [Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern generalized for any project with a measurable metric. Thanks to Andrej Karpathy for open-sourcing the core idea.

## Triggers

- User runs `/ds-tune`
- User asks to optimize, tune, or improve a measurable aspect of their project
- User asks "make this faster", "improve accuracy", "reduce bundle size", or similar
- User asks to set up a self-improving loop

## Contract

- One file, one metric, one loop — Karpathy's core constraint
- Git ratchet — only improvements survive, failures are reverted
- Every experiment committed before evaluation — full audit trail
- Evaluation is mechanical (deterministic assertions or benchmarks), not subjective
- Skill generates optimization infrastructure (auto/ folder), then runs the loop
- Standalone. Uses blueprint when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Full setup: discover goal, analyze project, generate auto/ folder, measure baseline, start loop |
| `run` | Resume optimization loop from existing auto/ setup |
| `status` | Show results summary (experiments, hit rate, improvement) |

## Execution Flow

Discovery → Analysis → Plan → Generate → Baseline → [Needs-Approval] → Loop

### Phase 1: Discovery

**Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use as baseline context for metric selection. Blueprint scores can suggest which dimensions to optimize.

**IDU:** Profile → Ideal Metrics, Type + Stack. Findings() → verify + use. Absent → own analysis.

Ask ONE question:

> What do you want to improve in this project? No technical detail needed — describe the goal in your own words.

Wait for answer. Only proceed after receiving it.

**Gate:** User has stated an optimization goal.

### Phase 2: Analysis

Work autonomously — do not ask more questions. Apply experiment design rules from [references/rules-optimization.md](references/rules-optimization.md).

1. Read project root: README, package files, entry points, test files, benchmarks
2. Understand project stack, structure, and purpose
3. Map user's goal to measurable metric(s)
4. Identify ONE target file most relevant to goal
5. Identify or create an evaluation method (existing tests, benchmark script, or new eval)
6. Check for existing test data and fixtures

Determine these values:

| Field | Description |
|-------|-------------|
| `target_file` | Single file the agent will modify |
| `metric` | Primary measurable signal (e.g., wer, accuracy, latency_ms, pass_rate, bundle_kb) |
| `direction` | `lower` or `higher` — which direction is better |
| `secondary` | Optional second metric for monitoring (not for keep/discard decisions) |
| `bench_cmd` | Command to run evaluation |
| `budget_sec` | Max seconds per experiment (based on eval duration) |

**Gate:** All fields determined. Metric is mechanical (computable in seconds, deterministic).

### Phase 3: Plan

Show summary:

```
Project:    [project name]
Goal:       [user's goal in their words]
File:       [target_file]
Metric:     [metric] ([direction]: lower/higher is better)
Bench:      [bench_cmd]
Budget:     [budget_sec] seconds / experiment
```

If test data is missing, state what will be created.

Ask: "Confirm? (yes / suggest changes)"

**Gate:** User confirmed.

### Phase 4: Generate

Create these files in project root `auto/` directory:

**auto/.autotune.json** — Configuration:
```json
{
  "target": "<target_file>",
  "metric": "<metric>",
  "direction": "<lower|higher>",
  "secondary": "<secondary|null>",
  "bench_cmd": "<command>",
  "budget_sec": <number>,
  "tag": "<YYYY-MM-DD>"
}
```

**auto/bench.sh** — Evaluation wrapper:
```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."
<eval_command> > auto/run.log 2>&1
```

Requirements: cd to project root, redirect ALL output to `auto/run.log`, output metrics as `metric_name:    value` (grep-able), complete within budget_sec.

**auto/eval script** — Project-specific evaluation (Python, Bash, or project language). Must output metrics in exact format: `<metric>:    <value>`. If test data doesn't exist, create minimal fixtures.

**auto/results.tsv** — Initialize with header:
```
timestamp	commit	status	<metric>	<secondary>	duration	description
```

Column notes: `timestamp` is ISO 8601. `duration` is `HH:MM:SS` format (wall-clock time for experiment).

**auto/program.md** — Agent instructions generated from template below with all project-specific values filled in.

**Gate:** All files created and executable.

### Phase 5: Baseline

1. Run `bash auto/bench.sh`
2. Extract metrics: search for `<metric>:` in `auto/run.log`
3. Record baseline in results.tsv
4. Commit auto/ folder: `git add auto/ && git commit -m "autotune: setup with baseline"`
5. Create branch: `git checkout -b autotune/<tag>`

Report:
```
Baseline:  [metric] = [value]
Branch:    autotune/[tag]
```

**Gate:** Baseline measured and committed.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 7: Loop

Execute loop defined in auto/program.md. Follow it exactly:

1. Read and analyze target file. What could improve the metric?
2. Form a hypothesis. One change per experiment.
3. Edit target file with experimental idea.
4. Commit: `git add <target_file> && git commit -m "description of change"`
5. Run: `bash auto/bench.sh`
6. Read results: search for `<metric>:` in `auto/run.log`
7. Append to auto/results.tsv (tab-separated): `<ISO8601_timestamp>\t<commit_7char>\t<status>\t<metric>\t<secondary>\t<HH:MM:SS>\t<description>`
8. Decision:
   - Metric improved → KEEP. Branch advances.
   - Metric same or worse → DISCARD. Run: `git reset HEAD~1 --hard`
9. Go to step 1. Continue without interruption.

**Gate:** Loop runs until user interrupts or context limit approaches.

## program.md Template

Generated in Phase 4 with all placeholders filled:

```markdown
# AutoTune: <project_name>

## Objective
<user's goal in natural language>

## Metric
- Primary: <metric> (<direction>: lower/higher is better)
- Secondary: <secondary> (monitoring only, not for keep/discard)

## Files
| File | Permission | Purpose |
|------|-----------|---------|
| <target_file> | EDITABLE | Optimization target |
| auto/bench.sh | read-only | Evaluation harness |
| auto/eval script | read-only | Metric extraction |
| auto/.autotune.json | read-only | Configuration |
| auto/results.tsv | append-only | Experiment log |
| All other files | read-only | Keep unchanged |

## Baseline
- <metric>: <baseline_value>
- commit: <baseline_commit>

## Experiment Loop

Repeat forever:

1. Read and analyze <target_file>. What could improve <metric>?
2. Form a hypothesis. Think about what change might help.
3. Edit <target_file> with your experimental idea.
4. Commit: git add <target_file> && git commit -m "description of change"
5. Run: bash auto/bench.sh
6. Read results: grep "^<metric>:" auto/run.log
7. Append to auto/results.tsv (tab-separated):
   <ISO8601_timestamp>\t<commit_7char>\t<status>\t<metric_value>\t<secondary_value>\t<HH:MM:SS>\t<description>
8. Decision:
   - <metric> improved (<direction>) -> KEEP. Branch advances.
   - <metric> same or worse -> DISCARD. Run: git reset HEAD~1 --hard
9. Go to step 1. Continue without interruption.

## Rules

1. ONLY modify <target_file>. Everything else is read-only.
2. Only use packages and dependencies already in the project.
3. Each experiment must complete within <budget_sec> seconds.
   If exceeded, kill and treat as crash.
4. Simplicity criterion: a small improvement that adds ugly complexity is NOT worth it.
5. Crash handling:
   - Simple bug (typo, import) -> fix and retry. Log only as retry, keep crash for fundamental failures.
   - Fundamental problem -> skip, log as crash, move on.
   - For crashes: <metric>=0.000000, status=crash in results.tsv
6. Continue without interruption. Keep experimenting autonomously.
   If stuck, re-read the target file for new angles, combine previous ideas,
   or try more radical approaches.
7. Only attempt experiments with new hypotheses — skip previously discarded approaches.
   Read results.tsv descriptions to avoid duplicates.
```

## `/ds-tune run` — Resume

1. Verify `auto/` folder exists, read `auto/.autotune.json`
2. Read `auto/program.md`
3. Read `auto/results.tsv` — find current baseline (last `keep` entry)
4. Check current git branch — if not on `autotune/*`, checkout the branch
5. Resume experiment loop from auto/program.md

## `/ds-tune status` — Results

1. Read `auto/results.tsv`
2. Display summary:

```
Total experiments:  [count]
Kept:               [kept_count]
Discarded:          [discarded_count]
Crashed:            [crashed_count]
Hit rate:           [kept/total]%

Baseline:           [first keep metric]
Best:               [best metric]
Improvement:        [improvement]%

Total time:         [sum of durations, formatted as HH:MM:SS]
Avg per experiment: [avg duration as HH:MM:SS]
First experiment:   [earliest timestamp]
Last experiment:    [latest timestamp]

Last 5 experiments:
[last 5 rows from results.tsv as table]
```

Summary line:
```
ds-tune: {OK|WARN|FAIL} | Experiments: N | Best: {metric_value} | Improvement: {delta} | Fixed: N | Skipped: N | Failed: N | Total: N
```

3. Show git log of kept improvements: `git log --oneline autotune/<tag> | head -10`

## Quality Gates

- Every experiment committed before evaluation — full audit trail in git
- Only target file modified — all other files are read-only
- Metric evaluation is mechanical (deterministic script output, not subjective judgment)
- Discarded experiments fully reverted (git reset --hard) — zero residue
- Results.tsv is append-only — complete experiment history preserved
- Simplicity criterion: complexity must earn its keep with measurable improvement
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| bench.sh fails to run | Check script permissions, verify eval dependencies exist |
| Metric not found in run.log | Check eval script output format, verify grep pattern |
| Experiment exceeds time budget | Kill process, log as crash, move to next hypothesis |
| Git conflict on reset | Stash changes, hard reset to last keep commit |
| No improvement after 10 consecutive experiments | Re-read target file, analyze results.tsv patterns, try fundamentally different approaches |
| auto/ folder missing (for `run`) | Run full setup first |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No testable metric exists | Help user define one: suggest assertions, benchmarks, or timing measurements |
| Multiple files need changes | Identify ONE most impactful file. If changes truly span files, expand target scope but keep it minimal |
| Metric is subjective (e.g., "code quality") | Convert to mechanical proxy: lint error count, test pass rate, complexity score |
| Eval takes > 5 minutes | Suggest sampling (subset of test data) or lighter proxy metric |
| User wants to optimize prompt/SKILL.md | Target = the .md file, metric = eval assertions pass rate |
| Project has no tests | Create minimal eval fixtures in Phase 4 |
