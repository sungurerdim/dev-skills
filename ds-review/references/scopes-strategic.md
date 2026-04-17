# Review Scopes

For concrete Detect/Fix patterns: architecture and testing scopes use `rules-quality.md`. Other scopes use structural analysis described in Focus column.

Strategic, architecture-level analysis scopes. 8 scopes, 92 checks.

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| architecture | ARC-01 to ARC-15 | Coupling/cohesion scores, circular deps, layer violations, god classes, feature envy, dependency direction |
| patterns | PAT-01 to PAT-15 | Inconsistent error handling/logging/async, SOLID/DRY violations, primitive obsession, data clumps, framework anti-patterns |
| testing | TST-01 to TST-10 | Coverage by module, critical path test existence, test-to-code ratio, missing negative/boundary tests, test isolation, mock balance, flaky indicators |
| maintainability | MNT-01 to MNT-12 | Cyclomatic complexity >15, cognitive complexity >20, methods >50 lines, >4 parameters, nesting >3, magic numbers, hardcoded config, boolean flags, temporal coupling |
| ai-architecture | AIA-01 to AIA-10 | Over-engineering (interface with 1 impl, abstract class with 1 subclass, factory for 1 type), local-only solutions presented as reusable, architectural drift, pattern inconsistency |
| functional-completeness | FUN-01 to FUN-18 | Missing CRUD/pagination/filter, incomplete error handling, state transition gaps, caching/indexing strategy |
| production-readiness | PRD-01 to PRD-07 | Health/readiness probes, graceful shutdown, config validation, secret injection method, container/deployment hygiene, observability, scaling bottlenecks |
| cross-cutting | XCT-01 to XCT-05 | Decision impact tracing: how one architectural choice affects other areas. Only report concrete cross-area impacts with evidence at file:line |

## Score Calculation

For review scopes without fixable findings (architecture, patterns), score reflects structural health:
- 90-100: No significant issues, patterns are consistent
- 70-89: Minor inconsistencies, 1-2 structural concerns
- 50-69: Notable issues, multiple inconsistencies
- 30-49: Significant structural problems
- 0-29: Fundamental architectural issues

These ranges are guidelines, not formulas. Use judgment within range based on finding severity and count.

For scopes with countable findings:

```
base_score = 100
penalty_per_CRITICAL = -25
penalty_per_HIGH = -10
penalty_per_MEDIUM = -3
penalty_per_LOW = -1

scope_score = max(0, base_score + sum(penalties))
```

Cap rules:
- Any CRITICAL finding → scope score max 40
- 3+ HIGH findings → scope score max 60

## Judgment Rules

| Rule | Detail |
|------|--------|
| Evidence | Every finding cites `file:line`. Read actual code before reporting. |
| Conservative | Uncertain → lower severity. Style → max LOW. |
| Pattern threshold | 3+ examples before concluding systemic pattern. |
| CRITICAL validation | Analyze as "this is a bug" AND "this might be intentional". Both agree → include. Disagree → downgrade. |

## Skip Patterns

Never flag intentionally marked code: `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, platform guards, test fixtures.
