# Reference: Gap Row Format

Consumer: ds-benchmark Phase 5 (Gap Table) — load when writing gap rows to `ds/audit/findings.md`.

## Columns

| Column | Meaning | Allowed values |
|--------|---------|-----------------|
| ID | Row identifier | `G{n}` |
| Dimension | Which resolved scope this gap belongs to | one of the scopes marked `ran` |
| Ideal | Synthesized ideal for this dimension (Phase 4) | one-paragraph text |
| Current | Current-state summary | text from blueprint/findings, or `unknown — insufficient data` |
| Gap | Type of divergence | `missing \| excess \| wrong \| partial-needs-extension` |
| Evidence | Where Current was observed | `file:line`, or `n/a — no current implementation` |
| Proposal | The closing action | one-sentence action |
| Effort | Size of the closing change | `S` — single file, mechanical change · `M` — 2-5 files, one module · `L` — 6+ files or cross-module/cross-cutting |
| Priority | Urgency of closing | `P1` — blocks core function or security · `P2` — meaningful quality gap · `P3` — nice-to-have |
| Category | Fix classification | `A` (code-level, no architecture change) \| `B` (architecture/scope change) |
| Decision | Resolution, set in Phase 6 | `close \| defer \| intentional-deviation` (absent until Phase 6 runs) |

## Row template

```
| ID    | Dimension    | Ideal              | Current            | Gap type             | Evidence            | Proposal             | Effort | Priority  | Category |
|-------|--------------|--------------------|--------------------|-----------------------|----------------------|-----------------------|--------|-----------|----------|
| G{n}  | {dim}        | {ideal-paragraph}  | {current-state}    | {gap-type}            | {file:line or n/a}  | {action-proposal}     | {S/M/L}| {P1/P2/P3}| {A/B}    |
```

`gap_type`: `missing | excess | wrong | partial-needs-extension`.

**Aggregate-score caveat:** a row whose only competitor evidence is a scorecard-style aggregate number carries the note `aggregate score = heuristic signal, not ground truth — verify high/low outliers manually` in its Ideal cell.

## Category rules

- Code-level fix not altering architecture or scope → A.
- Architecture / new dependency / new capability / user-facing promise change → B.
