# ds-benchmark

Teams drift toward internal tastes. Without an external benchmark, the project's "ideal" is whatever the last contributor felt.

Researches 5–10 comparable projects, synthesizes the ideal architecture, produces a dimension-by-dimension gap table, lets the user choose which gaps to close, defer, or record as intentional deviations.

## Install

```bash
cp -r dev-skills/ds-benchmark ~/.claude/skills/ds-benchmark
```

## Use

```bash
/ds-benchmark                 # full benchmark across every dimension
/ds-benchmark --preview       # research + synthesis + gap table, no approval
/ds-benchmark --competitors=10
/ds-benchmark --scope=architecture
```

## Dimensions

| Dimension | Compared |
|-----------|----------|
| architecture | Module layout, layering, entry points, data flow |
| stack | Language, framework, persistence, queue, cache, auth |
| data-model | Entities, relationships, normalization, indexing |
| ux | Core flows, latency posture, platform split |
| security | AuthN/AuthZ, session storage, secret handling |
| privacy | Data collection, retention, consent model |
| operational | Deploy target, observability, incident runbook |

## Features

- Delegates research to `/ds-research` (CRAAP+ tiered sources)
- Honors stated constraints — ideal never proposes a pinned-out change
- Gap table with category (A: code-level / B: architecture-level)
- Every B gap requires approval — no surprise refactors
- Intentional deviations recorded as ADRs via `/ds-docs --adr`
- Resumable via `.audit/benchmark.json`
