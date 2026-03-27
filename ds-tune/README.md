# ds-tune

Manual optimization means 8-10 experiments per day with no audit trail. This skill sets up an autonomous loop that runs 100+ experiments, keeping only what measurably improves.

[Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern — generalized for any project with a measurable metric. Thanks to Andrej Karpathy for open-sourcing the core idea.

## Install

```bash
cp -r ds-tune ~/.claude/skills/ds-tune
```

## Use

```bash
/ds-tune           # Full setup: discover goal, analyze, generate, baseline, start loop
/ds-tune run       # Resume loop from existing auto/ setup
/ds-tune status    # Show experiment results and improvement
```

## How It Works

1. You describe your goal in plain language
2. Skill analyzes your project, identifies target file and metric
3. Generates `auto/` folder: bench script, eval, config, program.md
4. Measures baseline, creates branch
5. Runs keep/discard experiment loop until you interrupt

## What It Creates

```
auto/
  .autotune.json    Config (target, metric, direction, budget)
  bench.sh          Evaluation wrapper
  eval.*            Project-specific metric extraction
  program.md        Agent instructions for the loop
  results.tsv       Experiment log (commit, metric, status, description)
  run.log           Last evaluation output
```

## Works With

Any project that has a measurable, computable metric: test pass rate, benchmark score, bundle size, latency, WER, coverage percentage, lint error count, eval assertions.
