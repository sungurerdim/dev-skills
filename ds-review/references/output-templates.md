# Output Templates — Tactical & Strategic

Consumer: SKILL.md Phase 7 (Summary) — render the template matching the mode that ran.

## Tactical output

```
refactor complete (tactical)
============================
| Scope          | Findings | Fixed | Skipped | Failed |
|----------------|----------|-------|---------|--------|
| {scope}        |   {n}    |  {n}  |   {n}   |  {n}   |
| Total          |   {n}    |  {n}  |   {n}   |  {n}   |

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```

Disposition accounting — totals balance.

## Strategic output

```
refactor complete (strategic)
=============================
| Metric     | Current | Ideal | Gap  |
|------------|---------|-------|------|
| {metric}   | {n}     | {n}   | {n}  |

Recommendations by effort:
  Quick Win:  [{id}] {title}
  Moderate:   [{id}] {title}
  Complex:    [{id}] {title}

Fixed: {n} | Skipped: {n} | Failed: {n} | Needs Approval: {n} | Total: {n}
```
