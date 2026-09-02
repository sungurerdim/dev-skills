# Generated Files — ds-tune Phase 4

Exact schema and script contracts for every file Phase 4 creates in project `ds/tune/` (committed; `ds/<skill>/` is the user-facing operational namespace). Loaded when Phase 4 runs.

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

## `--status` output shape

```
Total experiments: {count} | Kept: {kept_count} | Discarded: {discarded_count} | Crashed: {crashed_count} | Hit rate: {kept/total}%
Baseline: {first keep metric} | Best: {best metric} | Improvement: {improvement}%
Total time: {sum of durations, HH:MM:SS} | Avg per experiment: {avg HH:MM:SS}
First experiment: {earliest timestamp} | Last experiment: {latest timestamp}

Last 5 experiments: {last 5 rows from results.tsv as table}
```
