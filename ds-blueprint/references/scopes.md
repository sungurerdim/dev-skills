# Blueprint Scopes

Blueprint uses these scopes for signal counting and scoring. Per scope, blueprint searches codebase for described patterns and counts matches. Detailed pattern definitions in SKILL.md Phase 3 assessment table.

The 23 scopes `/ds-blueprint` owns, grouped into the 3 execution batches Phase 3 plans. Two more scopes appear in `ds/audit/findings.md` when their owners have run and are consumed, never scanned here: `privacy` (ds-compliance, canonical — it feeds the Security & Privacy dimension) and `ideal-gap` (ds-benchmark). Phase 4's completeness check expects exactly the scopes that ran this cycle (Phase 3 scope-resolution table), plus those two when present.

## Read-Only Batch (parallel — pure grep/file-read, no AST)

| Scope | ID Range | Focus |
|-------|----------|-------|
| hygiene | HYG-01 to HYG-20 | Unused imports/vars/functions, dead code, orphan files, duplicates, stale TODOs |
| types | TYP-01 to TYP-10 | Type errors, missing annotations, untyped args, type:ignore without reason |
| doc-sync | DCS-01 to DCS-06 | Inline doc contradicts signature, stale param descriptions, wrong return type |
| dx | DX-01 to DX-10 | Missing/incomplete README, missing CONTRIBUTING.md, missing CI config, missing env.example, missing setup/dev scripts, missing Makefile/Taskfile, missing .editorconfig, inconsistent config formats |
| docs | ds-docs:DOC-01 to DOC-10 | Missing doc files vs ideal for type, README sections missing (install, usage, API, contributing), API doc gaps, doc↔code drift (stale paths, renamed functions, changed defaults, removed features), broken internal links, outdated version refs, stale dep version claims, architectural claims that don't match code |
| spec-alignment | SPA-01 to SPA-06 | Promise census across README / SPEC.md / docs/ / AI instruction file / blueprint profile: promised-not-implemented, implemented-not-documented, drift (behavior diverges from doc) |
| stack | STK-01 to STK-10 | Missing lockfile, outdated deps (major versions behind), deprecated packages, known CVEs, missing `.nvmrc`/`.tool-versions`, inconsistent dep versions across workspace, runtime currency |
| stack-fitness | SFT-01 to SFT-08 | Every major dep evaluated vs stated goal — obsolete (unmaintained, archived, last release >24mo), oversized-for-purpose, duplicate (two libs serving same purpose), misaligned (server-side lib pulled into browser-only project) |
| external-tooling | EXT-01 to EXT-08 | GitHub Actions workflows, PR automations, CI scripts, pre-commit hooks, release automation evaluated for goal-fitness — unused workflows, workflows referencing deleted actions, duplicate workflows, template automations never triggered, goal-misaligned workflows |

## AST Batch (parallel — shared LSP/AST cache)

| Scope | ID Range | Focus |
|-------|----------|-------|
| architecture | ds-review:ARC-01 to ARC-15 | Coupling/cohesion, circular deps, layer violations, god classes, SOLID/GRASP violations |
| patterns | PAT-01 to PAT-15 | Inconsistent error handling/logging, SOLID/DRY violations, framework anti-patterns |
| cross-cutting | XCT-01 to XCT-05 | Decision impact tracing across areas |
| maintainability | MNT-01 to MNT-12 | Cyclomatic complexity, cognitive complexity, method length, nesting, change coupling, shotgun surgery, churn×complexity hotspots (git-history behavioral pass — SKILL.md Phase 3) |
| simplify | SIM-01 to SIM-11 | Deep nesting, duplicate code, unnecessary abstractions, single-use wrappers |
| ai-architecture | AIA-01 to AIA-14 | Prompt templates scattered (should be centralized), missing retry/fallback for AI API, hardcoded model names, missing token budget; product-facing LLM features: untrusted input concatenated into prompts (injection surface), model output consumed without schema/shape validation, no eval or regression set for prompt changes, no per-call cost/usage tracking |
| contract-consistency | CON-01 to CON-10 | System-wide lexicon + contract uniformity: same concept → same name (one verb per operation class across modules; domain terms uniform across layers), same word → same meaning, analogous functions share parameter order + options shape, consistent units/formats (time units, ID types, dates, boundary serialization casing), one return/error shape per layer (throw vs Result vs null never mixed within a layer), same operation with divergent signatures across modules (contract-drift twin of W17 duplication) |
| performance | ds-compliance:PRF-01 to PRF-10 | N+1 queries, blocking in async, large file reads, missing pagination/cache/pool |

## Cross-File Batch (serial — each pass may modify the findings index, order matters for dedup)

| Scope | ID Range | Focus |
|-------|----------|-------|
| security | ds-compliance:SEC-01 to SEC-12 | Secrets, injection, unsafe deserialization, eval, debug endpoints, weak crypto, CORS, path traversal, SSRF, auth bypass |
| privacy (consumed) | ds-compliance:PRV-01 to PRV-08 | Not scanned here — rows come from ds-compliance; absent → Security & Privacy scored from `security` alone, dashboard says `privacy: not scanned (ds-compliance)` |
| ai-hygiene | AIH-01 to AIH-08 | AI boilerplate (verbose wrappers, unnecessary abstractions), placeholder comments ("This function does X"), redundant error layers, hallucinated APIs, dead feature flags, stale mocks |
| robustness | ROB-01 to ROB-10 | Missing timeout/retry, unbounded collections, null checks, resource cleanup |
| production-readiness | PRD-01 to PRD-07 | Health probes, graceful shutdown, config validation, observability, debug endpoints exposed |
| testing | ds-review:TST-01 to TST-10 | Coverage, critical path tests, test isolation, flaky indicators, test pyramid signal |
| functional-completeness | FUN-01 to FUN-18 | Missing CRUD/pagination, incomplete error handling, state gaps, TODO/FIXME markers for unfinished work, stub/placeholder implementations |

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
- Skip patterns, confidence bands and the score formula are the shared ones in [../../core/severity-score-categories.md](../../core/severity-score-categories.md).
