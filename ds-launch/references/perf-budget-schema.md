# Perf Budget Schema (`--perf-budget`)

Loaded when `--perf-budget` runs. Written to `ds/launch/perf-budget.json` (committed; `ds/<skill>/` operational namespace). Keep only the sections fitting the project type; default values come from blueprint profile `Priorities:` + industry baselines.

```json
{
  "web":    { "lcp_ms": 2500, "inp_ms": 200, "cls": 0.1, "ttfb_ms": 600, "bundle_js_kb": 300, "bundle_css_kb": 60 },
  "api":    { "p50_ms": 50, "p95_ms": 200, "p99_ms": 500, "error_rate_pct": 0.5 },
  "mobile": { "cold_start_ms": 2000, "warm_start_ms": 800, "app_size_mb": 40, "jank_pct": 1.0 }
}
```

**CI enforcement:** delegate to `/ds-devops` to add a CI step running the project's native perf tool (Lighthouse CI, k6, Firebase Test Lab, etc.) + compare to `ds/launch/perf-budget.json`; over-budget → CI fails with the offending metric(s) named. Budget authoring is Category B (commits the project to enforceable numbers); CI wiring is Category A once the budget exists.
