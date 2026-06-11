# program.md Template

Generated into `ds/tune/program.md` during Phase 4 with all `{placeholders}` filled. The agent executing the loop follows this file exactly (skill-side rules in SKILL.md Phase 7 layer on top).

```markdown
# AutoTune: {project-name}

## Objective
{user-goal in natural language}

## Metric
- Primary: {metric} ({direction}: lower/higher is better)
- Secondary: {secondary} (monitoring only, not for keep/discard)

## Files
| File | Permission | Purpose |
|------|-----------|---------|
| {target_file} | EDITABLE | Optimization target |
| ds/tune/bench.sh | read-only | Evaluation harness |
| ds/tune/eval | read-only | Metric extraction |
| ds/tune/.autotune.json | read-only | Configuration |
| ds/tune/results.tsv | append-only | Experiment log |
| All other files | read-only | Keep unchanged |

## Baseline
- {metric}: {baseline_value}
- commit: {baseline_commit}

## Experiment Loop

Repeat forever:

1. Read and analyze {target_file}. What could improve {metric}?
2. Form a hypothesis: identify one specific change to {target_file} predicted to improve {metric}. State the change and predicted direction before editing.
3. Edit {target_file} with your experimental idea.
4. Commit: git add {target_file} && git commit -m "description of change"
5. Run: bash ds/tune/bench.sh
6. Read results: grep "^{metric}:" ds/tune/run.log
7. Append to ds/tune/results.tsv (tab-separated):
   {ISO8601_timestamp}\t{commit_7char}\t{status}\t{metric_value}\t{secondary_value}\t{HH:MM:SS}\t{description}
8. Decision:
   - {metric} improved ({direction}) → KEEP. Branch advances.
   - {metric} same or worse → DISCARD. Run: git reset HEAD~1 --hard
9. Go to step 1. Continue without interruption.

## Rules

1. ONLY modify {target_file}. Everything else is read-only.
2. Only use packages and dependencies already in the project.
3. Each experiment must complete within {budget_sec} seconds. If exceeded, kill and treat as crash.
4. Simplicity criterion: a small improvement that adds ugly complexity is NOT worth it.
5. Crash handling:
   - Simple bug (typo, import) → fix and retry. Log only as retry, keep crash for fundamental failures.
   - Fundamental problem → skip, log as crash, move on.
   - For crashes: {metric}=0.000000, status=crash in results.tsv
6. Continue without interruption. Keep experimenting autonomously. If stuck, re-read target file for new angles, combine previous ideas, or try more radical approaches.
7. Only attempt experiments with new hypotheses — skip previously discarded approaches. Read results.tsv descriptions to avoid duplicates.
```
