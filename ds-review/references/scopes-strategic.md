# Review Scopes

For concrete Detect/Fix patterns: architecture and testing scopes use `rules-quality.md`. Other scopes use structural analysis described in Focus column.

Strategic, architecture-level analysis scopes. 9 scopes, 103 checks.

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| architecture | ARC-01 to ARC-12 | Coupling/cohesion scores, circular deps, layer violations, god classes, feature envy, dependency direction |
| patterns | PAT-01 to PAT-15 | Inconsistent error handling/logging/async, SOLID/DRY violations, primitive obsession, data clumps, framework anti-patterns |
| testing | TST-01 to TST-10 | Coverage by module, critical path test existence, test-to-code ratio, missing negative/boundary tests, test isolation, mock balance, flaky indicators |
| maintainability | MNT-01 to MNT-12 | Cyclomatic complexity >15, cognitive complexity >20, methods >50 lines, >4 parameters, nesting >3, magic numbers, hardcoded config, boolean flags, temporal coupling |
| ai-architecture | AIA-01 to AIA-14 | Over-engineering (interface with 1 impl, abstract class with 1 subclass, factory for 1 type), local-only solutions presented as reusable, architectural drift, pattern inconsistency; product-facing LLM features (matches ds-blueprint's producer definition): untrusted input concatenated into prompts (injection surface), model output consumed without schema validation, no eval/regression set for prompt changes, no per-call cost tracking |
| functional-completeness | FUN-01 to FUN-18 | Missing CRUD/pagination/filter, incomplete error handling, state transition gaps, caching/indexing strategy |
| production-readiness | PRD-01 to PRD-07 | Health/readiness probes, graceful shutdown, config validation, secret injection method, container/deployment hygiene, observability, scaling bottlenecks |
| cross-cutting | XCT-01 to XCT-05 | Decision impact tracing: how one architectural choice affects other areas. Only report concrete cross-area impacts with evidence at file:line |
| contract-consistency | CON-01 to CON-10 | System-wide lexicon + contract uniformity: same concept same name (one verb per operation class; domain terms uniform across layers), same word same meaning, analogous functions share parameter order + options shape, consistent units/formats (time, IDs, dates, boundary casing), one return/error shape per layer, same operation with divergent signatures across modules (contract-drift twin of W17) |

## Gap Thresholds

Per-project-type ideal values for Phase 3 gap analysis (current vs ideal). Consumer: SKILL.md Phase 3 (strategic mode) — loaded when computing the Current vs Ideal table.

| Type | Coupling | Cohesion | Complexity | Coverage |
|------|----------|----------|------------|----------|
| cli | <40% | >75% | <10 | 70%+ |
| library | <30% | >80% | <8 | 85%+ |
| api | <50% | >70% | <12 | 80%+ |
| web | <60% | >65% | <15 | 70%+ |
| mobile | <55% | >65% | <12 | 65%+ |
| devtool | <35% | >75% | <10 | 80%+ |

## Score Calculation, Severity & Skip Patterns

One home: [`../../core/severity-score-categories.md`](../../core/severity-score-categories.md). Scopes without countable findings (architecture, patterns) score on structural health using the same CRITICAL/HIGH/MEDIUM/LOW judgment — the 100-point formula's cap rules still bound the range, applied by judgment rather than a per-finding sum. Evidence discipline: every finding cites `file:line`, read actual code before reporting; 3+ examples before concluding a systemic pattern.
