# Rules: Path Proposals

Three-path consolidation proposals for `/ds-review --meta-quality --suggest-paths`. Every flagged finding produces exactly three paths, ordered by ascending intervention depth.

## Why three paths

Users frequently say "yes, this is duplicated — but I don't have time to refactor." A single proposed fix forces a binary (apply / skip). Three paths converts the question to "which level of effort fits this sprint?"

- **Path A — Minimal:** delete duplicates only, no abstraction. Cheapest, smallest blast radius, immediate cleanup.
- **Path B — Moderate:** extract a shared module / helper. Pays off over the next 2-3 changes in the area.
- **Path C — Structural:** unify the API or abstraction at a higher level. Pays off when the area is changing weekly.

The user picks per finding (or applies the same choice to every matching finding via the "all matching" affordance).

## Per-finding path template

Each path includes four fields:

| Field | Definition |
|-------|------------|
| **Effort** | Estimated hours of focused work (round to {0.5h, 1h, 2h, 4h, 1d}). |
| **Impact** | Scope reach — number of files modified + downstream consumers touched. |
| **Risk** | Regression surface — `LOW` (deletion only, full test coverage), `MEDIUM` (shared module, indirect callers), `HIGH` (API unification, behavior changes possible). |
| **Rollback** | The git operation to undo. Fixes land uncommitted in the working tree (the skill never commits) → `git restore -- {files}`; after the user commits → `git revert {hash}`. Multi-step paths → `manual — restore files: {list}`. |

## Templates per scope

### SSOT-ARCHITECTURAL

- **Path A:** Pick the most-referenced location as canonical. Delete the duplicate(s). Update direct call sites only.
  - Effort: 0.5h | Impact: {n} files | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Move the canonical value to a shared `config/` or `constants.ts` module. All sites import from there.
  - Effort: 1-2h | Impact: {n+m} files | Risk: MEDIUM | Rollback: `git restore -- {files}`
- **Path C:** Promote to a typed configuration object with validation at boot. All sites consume via DI / context.
  - Effort: 4h-1d | Impact: project-wide | Risk: HIGH | Rollback: `manual — restore files: {list}`

### DRY-PATTERN

- **Path A:** Delete redundant copies. Keep the most-tested version. Inline-update call sites.
  - Effort: 0.5h | Impact: {n} files | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Extract a helper function in the nearest shared module. Replace each occurrence with a call.
  - Effort: 1-2h | Impact: {n} files | Risk: MEDIUM | Rollback: `git restore -- {files}`
- **Path C:** Apply a higher-level pattern (strategy / decorator / template method). Each variant becomes a configurable strategy.
  - Effort: 4h+ | Impact: {n+downstream} files | Risk: HIGH | Rollback: `manual — restore files: {list}`

### KISS-FIT

- **Path A:** Inline-flatten the function: collapse one branching layer, eliminate one parameter.
  - Effort: 0.5-1h | Impact: 1 file | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Split the function into 2-3 smaller functions with clearer names.
  - Effort: 1-2h | Impact: 1-2 files | Risk: MEDIUM | Rollback: `git restore -- {files}`
- **Path C:** Replace the algorithm with a simpler one (e.g., remove premature optimization, swap a hand-rolled state machine for a switch).
  - Effort: 2-4h | Impact: 1 file + tests | Risk: MEDIUM | Rollback: `git restore -- {files}`

### YAGNI-USAGE

- **Path A:** Delete the unused declaration.
  - Effort: 0.5h | Impact: 1 file | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Delete + remove related plumbing (config fields, env vars, doc references).
  - Effort: 1h | Impact: 2-4 files | Risk: LOW | Rollback: `git restore -- {files}`
- **Path C:** Audit the entire feature surface for additional dead siblings (often YAGNI clusters). Delete the cluster as a batch.
  - Effort: 2-4h | Impact: 5+ files | Risk: MEDIUM | Rollback: `manual — restore files: {list}`

### SOC-ISOLATION

- **Path A:** Document the scattered responsibility in one location (e.g., a doc-comment block). No code change.
  - Effort: 0.5h | Impact: 1 file | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Extract a single owner module. Route the 3+ scattered sites through it.
  - Effort: 2-4h | Impact: {n+1} files | Risk: MEDIUM | Rollback: `git restore -- {files}`
- **Path C:** Re-architect the responsibility as a cross-cutting concern (middleware, interceptor, aspect). All sites become declarative consumers.
  - Effort: 1-2d | Impact: project-wide | Risk: HIGH | Rollback: `manual — restore files: {list}`

### OBSOLETE

- **Path A:** Delete the dead code path.
  - Effort: 0.5h | Impact: 1 file | Risk: LOW | Rollback: `git restore -- {files}`
- **Path B:** Delete + remove all related compat shims (test guards, type aliases, deprecation comments).
  - Effort: 1h | Impact: 2-4 files | Risk: LOW | Rollback: `git restore -- {files}`
- **Path C:** Migration sweep: identify everywhere the legacy contract leaked (docs, tests, CI configs) and clean uniformly.
  - Effort: 2-4h | Impact: 5+ files | Risk: MEDIUM | Rollback: `manual — restore files: {list}`

### DUPLICATE

Same as DRY-PATTERN, applied at function/module granularity.

## Presentation format

```
Finding {id}: {title} — {file:line}

Path A — Minimal
  Effort: {est} | Impact: {n} files | Risk: {LOW/MEDIUM/HIGH} | Rollback: {cmd}
  Action: {one-line description}

Path B — Moderate
  Effort: {est} | Impact: {n} files | Risk: {LOW/MEDIUM/HIGH} | Rollback: {cmd}
  Action: {one-line description}

Path C — Structural
  Effort: {est} | Impact: {n} files | Risk: {LOW/MEDIUM/HIGH} | Rollback: {cmd}
  Action: {one-line description}

Select: [A] / [B] / [C] / [Skip] / [Apply same path to all matching findings] / [Apply A to all] / [Apply B to all] / [Apply C to all]
```

The "all matching" affordance applies the same path letter to every finding with the same `(scope, severity)` pair.

## Risk caps

- A path marked `HIGH` risk MUST be classified Category B (approval-gated) regardless of `--auto`.
- A path that modifies more than 10 files MUST be classified Category B, even if scope-level risk is LOW.
- A path whose rollback is `manual` resolves under `--auto` per best judgment (applied by best judgment) unless it independently matches the rule-4 irreversible-exception list (force-push, permanent deletion, secret rotation, human-only value) — then it is `skipped (needs-human)`.
