# Blueprint Scopes

Blueprint uses these scopes for signal counting and scoring. Per scope, blueprint searches codebase for described patterns and counts matches. Detailed pattern definitions in SKILL.md Phase 3 assessment table.

All analysis scopes used by /blueprint across 5 assessment tracks.

## Optimize Scopes (Track A: Code Quality)

| Scope | ID Range | Focus |
|-------|----------|-------|
| security | SEC-01 to SEC-12 | Secrets, injection, unsafe deserialization, eval, debug endpoints, weak crypto, CORS, path traversal, SSRF, auth bypass |
| hygiene | HYG-01 to HYG-20 | Unused imports/vars/functions, dead code, orphan files, duplicates, stale TODOs |
| types | TYP-01 to TYP-10 | Type errors, missing annotations, untyped args, type:ignore without reason |
| simplify | SIM-01 to SIM-11 | Deep nesting, duplicate code, unnecessary abstractions, single-use wrappers |
| performance | PRF-01 to PRF-10 | N+1 queries, blocking in async, large file reads, missing pagination/cache/pool |
| robustness | ROB-01 to ROB-10 | Missing timeout/retry, unbounded collections, null checks, resource cleanup |
| privacy | PRV-01 to PRV-08 | PII exposure/logging, missing masking/consent/retention |

## Review Scopes (Track B: Architecture, Track C: Production)

| Scope | ID Range | Focus |
|-------|----------|-------|
| architecture | ARC-01 to ARC-15 | Coupling/cohesion, circular deps, layer violations, god classes |
| patterns | PAT-01 to PAT-15 | Inconsistent error handling/logging, SOLID/DRY violations, framework anti-patterns |
| cross-cutting | XCT-01 to XCT-05 | Decision impact tracing across areas |
| testing | TST-01 to TST-10 | Coverage, critical path tests, test isolation, flaky indicators |
| maintainability | MNT-01 to MNT-12 | Cyclomatic complexity, cognitive complexity, method length, nesting |
| production-readiness | PRD-01 to PRD-07 | Health probes, graceful shutdown, config validation, observability |
| functional-completeness | FUN-01 to FUN-18 | Missing CRUD/pagination, incomplete error handling, state gaps |
| ai-architecture | AIA-01 to AIA-10 | Over-engineering, architectural drift, pattern inconsistency |

## Audit Scopes (Track D: Documentation, Track E: Audit)

| Scope | ID Range | Focus |
|-------|----------|-------|
| doc-sync | DOC-01 to DOC-08 | README drift, API mismatch, deprecated refs, broken links |
| stack-assessment | STK-01 to STK-10 | Framework fitness, runtime currency, build tool match, redundant deps |
| dependency-health | DEP-01 to DEP-10 | Abandoned packages, license conflicts, pinning, CVEs, supply chain |
| dx-quality | DXQ-01 to DXQ-10 | Setup friction, env docs, script discoverability, CI/local parity |
| project-structure | PST-01 to PST-10 | Directory conventions, naming consistency, config sprawl, gitignore |

## Score Calculation

For scopes with countable findings:
```
base_score = 100
penalty_per_CRITICAL = -25
penalty_per_HIGH = -10
penalty_per_MEDIUM = -3
penalty_per_LOW = -1

scope_score = max(0, base_score + sum(penalties))
```

Caps: CRITICAL → max 40, 3+ HIGH → max 60.

For structural scopes (architecture, patterns): score reflects health on 0-100 scale using judgment.

## Judgment & Skip Rules

- Every finding cites file:line. Read actual code before reporting.
- Uncertain → lower severity. Style → max LOW.
- 3+ examples before concluding systemic pattern.
- Skip: # noqa, # intentional, # safe:, _ prefix, TYPE_CHECKING, platform guards, test fixtures.
