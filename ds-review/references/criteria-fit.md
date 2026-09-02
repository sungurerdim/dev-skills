# Rules: Criteria-Fit Baselines

Project-type-specific baselines for `/ds-review --meta-quality --criteria-fit`. Compare meta-quality finding counts against these baselines; counts above baseline trigger a criteria-mismatch question to the user.

## Why baselines

A monorepo web-app and a 200-line CLI tool have different reasonable expectations. Reporting "you have 4 SSOT violations" is meaningless without a yardstick. Baselines convert raw counts into "above/at/below expected for this project type."

The baselines below are calibrated against the project-type definitions in ds-blueprint's `references/weights.md` (https://github.com/sungurerdim/dev-skills/blob/main/ds-blueprint/references/weights.md). Same taxonomy, same calibration.

## Baselines

| Project Type | SSOT | DRY-Pattern | KISS | SoC | Notes |
|--------------|------|-------------|------|-----|-------|
| `small-cli` (<2k LOC) | 0-2 | 0-3 | 0-2 | 0-1 | Strict — small scope makes duplication visible fast |
| `cli` (2k-20k LOC) | 0-3 | 0-5 | 0-3 | 0-2 | Moderate — some duplication is acceptable for ergonomics |
| `library` | 0-1 | 0-2 | 0-2 | 0-1 | Strictest — public surface must be deliberate |
| `web-app` | 0-3 | 0-5 | 0-4 | 0-3 | Web stack tolerates more boilerplate; framework-required patterns dilute strictness |
| `api` | 0-3 | 0-5 | 0-4 | 0-2 | Similar to web-app; backend logic should be more disciplined |
| `mobile` | 0-4 | 0-6 | 0-5 | 0-3 | Platform abstractions create duplication by necessity |
| `devtool` | 0-2 | 0-3 | 0-3 | 0-2 | Author-quality codebase; expectations match small-cli |
| `monorepo` | 0-5 | 0-10 | 0-6 | 0-5 | Multi-package context; baselines scale with workspace count |
| `iac` (Terraform / Pulumi / Bicep) | 0-2 | 0-5 | 0-3 | 0-2 | DSL-driven; repeated module blocks are expected |

## How baselines are applied

After Phase 3a produces per-scope counts:

1. Detect project type from blueprint profile. Absent → ask user once.
2. Look up baselines for that type from the table above.
3. For each scope, compare count vs baseline maximum:
   - At or below max → no criteria-fit note, scope passes
   - 1-2× above max → mark `criteria-mismatch (above-baseline)` — soft signal
   - >2× above max → mark `criteria-mismatch (significantly above-baseline)` — hard signal, prompt user

## Mismatch prompt

When a hard signal triggers, ask exactly once per scope:

```
{scope} count ({n}) significantly exceeds {type} baseline ({max}).
- Tighten codebase — proceed with consolidation paths for these findings
- Loosen criteria — set project-specific override (recorded in blueprint profile)
- Defer — note the mismatch in report, decide later
- All matching (recommended) — apply the same choice to every scope with mismatch
```

User choice (if `loosen` selected) is surfaced as a recommendation to update the blueprint profile's `Constraints:` directly — no intermediate state file.

## Override semantics

A user may explicitly raise a baseline by setting `Constraints:` in the blueprint profile. Example:

```
Constraints: keep framework, SSOT-baseline: 8 (mono-package monorepo by design)
```

The `--criteria-fit` phase reads this and uses the overridden max instead of the table value. Recorded overrides MUST cite a reason — the override without a reason is itself a finding (vague constraint).

## When baselines do not apply

- Project type is `generic` (undetectable from manifests + user declined to clarify) → skip criteria-fit, mark all scopes `low-confidence assessment`
- Project under 200 LOC → criteria-fit is meaningless at this scale; report raw counts only
- Project actively under heavy migration (HEAD has 100+ uncommitted lines) → criteria-fit deferred, prompt user to commit first
