# Dashboard Output Format (Phase 5)

Render templates for the mandatory dashboard: the score table, the below-target findings list, score-drop explanations, and the human-actions block. Loaded when Phase 5 renders.

```
Project: {name} | Type: {type} | Stack: {stack} | Target: {quality}

| Dimension          | Score | Prev | Delta | Target | Gap  | Status |
|--------------------|-------|------|-------|--------|------|--------|
| {dimension}        | {n}   | {n}  | {+/-n}| {n}    | {n}  | {status}|
| Overall            | {n}   | {n}  | {+/-n}| {n}    | {n}  | {status}|

Findings written to ds/audit/findings.md ({n} signals across {n} dimensions)
```

Previous scores exist: show Prev + Delta. First run: omit those columns. When previous `model=` differs from current, label each delta column as model-attributed (e.g. `Δ vs previous (model {prev-model} → {curr-model})`) so score movement is attributable to the model change, not code change alone.

For dimensions below target, list top findings with IDs:
```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}, gap: {n}) — {n} signals
   {finding-ID} {severity}: {short description}
```

Any dimension dropped (negative delta), explain: `Score changes: {dimension} {delta}: {brief cause}`

Findings requiring human-only access exist → list them (omit block when none):
```
Human actions (AI cannot perform these):
- {finding-ID}: {action} — where: {settings-page/console/account} | why: {risk if skipped}
```
