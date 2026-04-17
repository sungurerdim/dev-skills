# Rules: Autonomous Optimization

Rules for experiment design, metric selection, and result validation. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Experiment Design** | OPT-01–06 (2 HIGH, 3 MEDIUM, 1 LOW) | ~12 |

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
- **Source:** Karpathy autoresearch pattern, A/B testing fundamentals

### OPT-02 [HIGH] Baseline Measurement
Record baseline before any experiment. Without baseline, improvement cannot be measured.
- **Detect:**
  - Experiment started without recording current metric value
  - Baseline measured with different methodology than post-experiment measurement
  - Baseline not tied to a specific commit hash or reproducible state
- **Fix:** Before any change: run evaluation on current state. Record: metric value, timestamp, commit hash, environment details, measurement command. Baseline must be reproducible — anyone can check out the commit and reproduce the number
- **Source:** Scientific method, experiment design principles

### OPT-03 [MEDIUM] Isolation
Each experiment changes exactly one variable. Multi-variable changes make it impossible to attribute results.
- **Detect:**
  - Experiment modifies multiple independent aspects simultaneously
  - Configuration changes bundled with code changes
  - Infrastructure change combined with logic change in same experiment
- **Fix:** Split into separate experiments, each changing one variable. Run sequentially. If variables interact, design a factorial experiment explicitly noting the interaction hypothesis. Document which variable each experiment targets
- **Source:** Experiment design principles, controlled experiments

### OPT-04 [MEDIUM] Rollback Safety
Every experiment can be fully reverted to pre-experiment state within minutes.
- **Detect:**
  - Experiment applied directly on main branch without a branch
  - Experiment modifies shared state (database schema, external config) without backup
  - No documented rollback procedure
  - Experiment branch deleted before results were recorded
- **Fix:** One branch per experiment. Rollback = revert the branch merge or delete the branch. For infrastructure experiments: snapshot before, document restore procedure. Never experiment on production data without a rollback plan
- **Source:** Git workflow best practices, feature flag patterns

### OPT-05 [MEDIUM] Statistical Significance
Improvement is real, not noise. Single measurements are not evidence.
- **Detect:**
  - Single measurement used as evidence of improvement
  - No variance or confidence interval reported
  - "Improved by 2%" based on one run (within noise range)
  - Different measurement conditions between baseline and experiment
- **Fix:** Run metric N times under identical conditions. Minimums: code benchmarks >= 3 runs, user metrics >= 30 samples, flaky metrics >= 10 runs. Report mean +/- standard deviation. Improvement must exceed 2x standard deviation to be considered real
- **Source:** Statistics fundamentals, benchmarking best practices

### OPT-06 [LOW] Experiment Log
All experiments documented with hypothesis, change, result, and decision. Prevents repeating failed experiments.
- **Detect:**
  - No experiment history maintained
  - Experiments run but results not recorded
  - Same experiment repeated because previous result was forgotten
  - Results recorded without the hypothesis or methodology
- **Fix:** Log each experiment with: hypothesis (what you expect and why), change (what was modified), metric before and after (with variance), decision (keep or discard and reasoning). Store in a persistent location (markdown file, issue, or dedicated tracking)
- **Source:** Karpathy autoresearch pattern, Google Vizier experiment tracking
