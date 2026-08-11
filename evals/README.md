# Skill-Behaviour Evals

Machine-scored behavioural evals for dev-skills (issue #33). Each task ships a
`setup.sh` (builds a disposable fixture repo) and a `score.sh` (emits one
`criterion<TAB>PASS|FAIL` line per check plus a final `OVERALL` line, exit 0
only on all-pass). Nothing here installs or runs at skill runtime.

## Method

Two arms, everything else held constant (same model, same harness, same task,
same fixture):

| Arm | Skill text |
|-----|-----------|
| `old` | pre-v6.1 portable SKILL.md (git tag/commit of the baseline) |
| `new` | current lean-profile SKILL.md (`install.sh --profile lean` output) |

Metrics per run: task success (scorer), **false-done** (agent claimed done/OK
while scorer failed — the highest-severity failure class), tokens (harness
usage counter), and gate compliance (evidence shown for each gate that ran).

Runner protocol: executor agent receives (1) the arm's SKILL.md path to read,
(2) the fixture path, (3) the user-style request — nothing else. Score with
`score.sh` after the run; the scorer's output is the result, never the agent's
self-report. Keep/discard decisions over rule/skill text changes follow the
ds-tune loop: single change → same measurement → keep only on measured
non-regression.

## Tasks

| Task | Skill | What it proves |
|------|-------|----------------|
| commit-mixed-tree | ds-commit | atomic split, conventional format, secret exclusion, referenced-untracked staging, clean end state |
| commit-clean-tree | ds-commit | zero-change honesty: reports nothing-to-commit, fabricates no commit |
| commit-secret-tree | ds-commit | credential file never enters history despite being staged-adjacent |

Results are recorded on the tracking issue, not committed here.
