# Review Scopes

For concrete Detect/Fix patterns: architecture and testing scopes use `rules-quality.md`. Other scopes use structural analysis described in Focus column.

Strategic, architecture-level analysis scopes. 9 scopes, 110 checks.

## Scope Groups

| Group | Scopes |
|-------|--------|
| Structure | architecture, patterns, cross-cutting, contract-consistency |
| Quality | testing, maintainability |
| Production Readiness | production-readiness |
| Completeness | functional-completeness, ai-architecture |

## Scope Definitions

| Scope | ID Range | Focus |
|-------|----------|-------|
| architecture | ARC-01 to ARC-15 | Coupling/cohesion scores, circular deps, layer violations, god classes, feature envy, dependency direction |
| patterns | PAT-01 to PAT-15 | Inconsistent error handling/logging/async, SOLID/DRY violations, primitive obsession, data clumps, framework anti-patterns |
| testing | TST-01 to TST-14 | Coverage by module, critical path test existence, test-to-code ratio, missing negative/boundary tests, test isolation, mock balance, flaky indicators |
| maintainability | MNT-01 to MNT-12 | Cyclomatic complexity >15, cognitive complexity >20, methods >50 lines, >4 parameters, nesting >3, magic numbers, hardcoded config, boolean flags, temporal coupling |
| ai-architecture | AIA-01 to AIA-14 | Over-engineering (interface with 1 impl, abstract class with 1 subclass, factory for 1 type), local-only solutions presented as reusable, architectural drift, pattern inconsistency; product-facing LLM features (matches ds-blueprint's producer definition): untrusted input concatenated into prompts (injection surface), model output consumed without schema validation, no eval/regression set for prompt changes, no per-call cost tracking |
| functional-completeness | FUN-01 to FUN-18 | Missing CRUD/pagination/filter, incomplete error handling, state transition gaps, caching/indexing strategy |
| production-readiness | PRD-01 to PRD-07 | Health/readiness probes, graceful shutdown, config validation, secret injection method, container/deployment hygiene, observability, scaling bottlenecks |
| cross-cutting | XCT-01 to XCT-05 | Decision impact tracing: how one architectural choice affects other areas. Only report concrete cross-area impacts with evidence at file:line |
| contract-consistency | CON-01 to CON-10 | System-wide lexicon + contract uniformity: same concept same name (one verb per operation class; domain terms uniform across layers), same word same meaning, analogous functions share parameter order + options shape, consistent units/formats (time, IDs, dates, boundary casing), one return/error shape per layer, same operation with divergent signatures across modules (contract-drift twin of W17) |

## Per-Scope Principle Sets

Consumer: SKILL.md Strategic Scopes section. Each scope is evaluated against a named principle set, and the finding title cites the principle it violates:

| Scope | Principle set |
|-------|---------------|
| architecture, patterns | SOLID + GRASP — [../../core/principles.md §2](../../core/principles.md) |
| production-readiness | Reliability patterns — [../../core/principles.md §4](../../core/principles.md) |
| testing | Testing discipline — [../../core/principles.md §7](../../core/principles.md) |
| contract-consistency | One concept → one name across the codebase; flag only after 3+ concrete examples of the same lexicon drift |

**Taste-dependent judgment → rubric, not rules.** Where a scope turns on "is this the right abstraction" there is no pattern to grep, so the strategic pass is closed by a verifier run against [rubric-architecture.md](rubric-architecture.md): five dimensions, a level per dimension, each level claimed only with a `file:line` example of the named signal. Delegate it as its own pass with the rubric as the whole contract; the returned levels are untrusted until the cited lines are re-read. Rule-shaped findings stay in `rules-quality.md` — the rubric covers only what a rule cannot express.

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

## Check IDs (per scope)

Every scope's checks are individually identified so a run can report exactly which ran. `architecture` and `testing` list their checks in `rules-quality.md` (ARC-*, TST-*) — already fully enumerated there. The remaining scopes ds-review owns outright enumerate below; IDs beyond the last row of each table are reserved headroom in the declared range — not yet split into an individually named check, so they fall back to the Focus description above until split out.

### patterns (PAT-01 to PAT-15)

| ID | Severity | Check |
|----|----------|-------|
| PAT-01 | HIGH | Inconsistent error handling |
| PAT-02 | MEDIUM | Inconsistent logging |
| PAT-03 | MEDIUM | Inconsistent async patterns |
| PAT-04 | HIGH | SOLID violations |
| PAT-05 | HIGH | DRY violations |
| PAT-06 | MEDIUM | Primitive obsession |
| PAT-07 | MEDIUM | Data clumps |
| PAT-08 | MEDIUM | Framework anti-patterns |

### maintainability (MNT-01 to MNT-12)

| ID | Severity | Check |
|----|----------|-------|
| MNT-01 | MEDIUM | Cyclomatic complexity > 15 |
| MNT-02 | MEDIUM | Cognitive complexity > 20 |
| MNT-03 | MEDIUM | Method length > 50 lines |
| MNT-04 | LOW | Parameters > 4 |
| MNT-05 | MEDIUM | Nesting depth > 3 |
| MNT-06 | LOW | Magic numbers |
| MNT-07 | MEDIUM | Hardcoded config |
| MNT-08 | LOW | Boolean flag parameters |
| MNT-09 | MEDIUM | Temporal coupling |

### ai-architecture (AIA-01 to AIA-14)

| ID | Severity | Check |
|----|----------|-------|
| AIA-01 | MEDIUM | Over-engineered interface (1 implementation) |
| AIA-02 | MEDIUM | Over-engineered abstract class (1 subclass) |
| AIA-03 | MEDIUM | Over-engineered factory (1 type) |
| AIA-04 | MEDIUM | Local-only solution presented as reusable |
| AIA-05 | MEDIUM | Architectural drift |
| AIA-06 | MEDIUM | Pattern inconsistency |
| AIA-07 | HIGH | Untrusted input concatenated into prompts — injection surface (product-facing LLM only) |
| AIA-08 | HIGH | Model output consumed without schema validation (product-facing LLM only) |
| AIA-09 | MEDIUM | No eval/regression set for prompt changes (product-facing LLM only) |
| AIA-10 | MEDIUM | No per-call cost tracking (product-facing LLM only) |

### functional-completeness (FUN-01 to FUN-18)

| ID | Severity | Check |
|----|----------|-------|
| FUN-01 | HIGH | Missing CRUD operation |
| FUN-02 | MEDIUM | Missing pagination |
| FUN-03 | MEDIUM | Missing filter support |
| FUN-04 | HIGH | Incomplete error handling |
| FUN-05 | HIGH | State transition gaps |
| FUN-06 | MEDIUM | Caching/indexing strategy gap |

### production-readiness (PRD-01 to PRD-07)

| ID | Severity | Check |
|----|----------|-------|
| PRD-01 | HIGH | Health/readiness probes |
| PRD-02 | HIGH | Graceful shutdown |
| PRD-03 | MEDIUM | Config validation |
| PRD-04 | HIGH | Secret injection method |
| PRD-05 | MEDIUM | Container/deployment hygiene |
| PRD-06 | MEDIUM | Observability |
| PRD-07 | MEDIUM | Scaling bottlenecks |

### cross-cutting (XCT-01 to XCT-05)

| ID | Severity | Check |
|----|----------|-------|
| XCT-01 | MEDIUM | Cross-area decision impact tracing — report only concrete impacts, evidenced at file:line |

### contract-consistency (CON-01 to CON-10)

| ID | Severity | Check |
|----|----------|-------|
| CON-01 | MEDIUM | Same concept, same name (one verb per operation class; uniform domain terms across layers) |
| CON-02 | MEDIUM | Same word, same meaning |
| CON-03 | MEDIUM | Analogous functions share parameter order + options shape |
| CON-04 | MEDIUM | Consistent units/formats (time, IDs, dates, boundary casing) |
| CON-05 | MEDIUM | One return/error shape per layer |
| CON-06 | HIGH | Same operation, divergent signatures across modules (contract-drift, twin of W17) |

## Score Calculation, Severity & Skip Patterns

One home: [`../../core/severity-score-categories.md`](../../core/severity-score-categories.md). Scopes without countable findings (architecture, patterns) score on structural health using the same CRITICAL/HIGH/MEDIUM/LOW judgment — the 100-point formula's cap rules still bound the range, applied by judgment rather than a per-finding sum. Evidence discipline: every finding cites `file:line`, read actual code before reporting; 3+ examples before concluding a systemic pattern.
