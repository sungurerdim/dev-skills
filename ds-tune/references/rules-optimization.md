# Rules: Autonomous Optimization

Rules for experiment design, metric selection, and result validation. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Experiment Design** | OPT-01–07 (3 HIGH, 3 MEDIUM, 1 LOW) | ~12 |

---

## Experiment Design

### OPT-01 [HIGH] Single Metric
Each experiment optimizes exactly one measurable metric. Secondary metrics tracked but not optimized.
- **Detect:**
  - Experiment changes multiple variables simultaneously
  - No clear success metric defined before starting
  - Success criteria described qualitatively ("make it better") instead of quantitatively
  - Multiple metrics optimized in same experiment, making attribution impossible
- **Fix:** Define primary metric before starting experiment. State: metric name, current value, target value, measurement method. Track secondary metrics as guardrails (they should not regress) but optimize only one
- **Impact:** Optimizing several metrics at once makes an improvement unattributable to any one change, so the experiment proves nothing and the "win" cannot be trusted.
- **Source:** Karpathy autoresearch pattern, A/B testing fundamentals

### OPT-02 [HIGH] Baseline Measurement
Record baseline before any experiment. Without baseline, improvement cannot be measured.
- **Detect:**
  - Experiment started without recording current metric value
  - Baseline measured with different methodology than post-experiment measurement
  - Baseline not tied to a specific commit hash or reproducible state
- **Fix:** Before any change: run evaluation on current state. Record: metric value, timestamp, commit hash, environment details, measurement command. Baseline must be reproducible — anyone can check out the commit and reproduce the number
- **Impact:** Without a reproducible baseline, a claimed improvement cannot be told apart from a different starting state or measurement drift — the whole loop's output becomes unverifiable.
- **Source:** Scientific method, experiment design principles

### OPT-03 [MEDIUM] Isolation
Each experiment changes exactly one variable. Multi-variable changes make it impossible to attribute results.
- **Detect:**
  - Experiment modifies multiple independent aspects simultaneously
  - Configuration changes bundled with code changes
  - Infrastructure change combined with logic change in same experiment
- **Fix:** Split into separate experiments, each changing one variable. Run sequentially. If variables interact, design a factorial experiment explicitly noting the interaction hypothesis. Document which variable each experiment targets
- **Impact:** A multi-variable change hides which edit caused a regression or a gain, so the next experiment cannot build on what was actually learned — the loop wastes cycles guessing.
- **Source:** Experiment design principles, controlled experiments

### OPT-04 [MEDIUM] Rollback Safety
Every experiment can be fully reverted to pre-experiment state within minutes.
- **Detect:**
  - Experiment applied directly on main branch without a branch
  - Experiment modifies shared state (database schema, external config) without backup
  - No documented rollback procedure
  - Experiment branch deleted before results were recorded
- **Fix:** One branch per experiment. Rollback = revert the branch merge or delete the branch. For infrastructure experiments: snapshot before, document restore procedure. Never experiment on production data without a rollback plan
- **Impact:** With no fast, mechanical revert, a failed hypothesis turns into manual cleanup or leaves broken state on the branch every later experiment builds on, stalling the whole loop.
- **Source:** Git workflow best practices, feature flag patterns

### OPT-05 [MEDIUM] Statistical Significance
Improvement is real, not noise. Single measurements are not evidence.
- **Detect:**
  - Single measurement used as evidence of improvement
  - No variance or confidence interval reported
  - "Improved by 2%" based on one run (within noise range)
  - Different measurement conditions between baseline and experiment
- **Fix:** Run metric N times under identical conditions. Minimums: code benchmarks >= 3 runs, user metrics >= 30 samples, flaky metrics >= 10 runs. Report mean +/- standard deviation. Improvement must exceed 2x standard deviation to be considered real
- **Impact:** Keeping a change on a single noisy measurement ships a "win" that is actually chance, then regresses in production the moment the noise swings the other way.
- **Source:** Statistics fundamentals, benchmarking best practices

### OPT-06 [LOW] Experiment Log
All experiments documented with hypothesis, change, result, and decision. Prevents repeating failed experiments.
- **Detect:**
  - No experiment history maintained
  - Experiments run but results not recorded
  - Same experiment repeated because previous result was forgotten
  - Results recorded without the hypothesis or methodology
- **Fix:** Log each experiment with: hypothesis (what you expect and why), change (what was modified), metric before and after (with variance), decision (keep or discard and reasoning). Store in a persistent location (markdown file, issue, or dedicated tracking)
- **Impact:** Without a log, a discarded idea gets re-tried under a new name, burning experiment budget on ground the loop already covered.
- **Source:** Karpathy autoresearch pattern, Google Vizier experiment tracking

### OPT-07 [HIGH] Reward Hacking / Metric Gaming
The optimized metric is a proxy for a real goal; an experiment that moves the number while the goal stagnates or regresses is a loss, not a win. Autonomous optimizers reliably exploit scorer loopholes (Goodhart's law).
- **Detect:**
  - The eval / scorer hard-codes or special-cases specific inputs
  - Metric improves while held-out checks, correctness tests, or the underlying objective do not
  - The change targets the measurement (editing the benchmark, loosening tolerances) rather than the behavior
  - A "win" that does not reproduce on unseen data
- **Fix:** Keep a held-out check the experiment cannot see; an experiment wins only if the target improves AND held-out checks don't regress. Never special-case the scorer or hard-code expected outputs. If the metric and the real goal diverge, fix the metric, not the code.
- **Impact:** An accepted experiment that gamed the scorer ships a change that does not serve the real goal, while its false "win" blocks genuine improvements from being tried in its place.
- **Source:** Goodhart's law; [SpecBench (2026)](https://arxiv.org/abs/2605.21384), [SWE-ABS (2026)](https://arxiv.org/abs/2603.00520)
