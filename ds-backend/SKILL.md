---
name: ds-backend
description: Backend architecture — API design, database schema, authentication, data pipelines. Use when designing or reviewing a backend, REST/GraphQL APIs, data models, auth flows, or ingest/ETL pipelines.
---

# /ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, schemas that don't survive first migration, and data pipelines that double-process on retry. Skill designs all four layers correctly from start.

**Backend Design** — API design, database schema, authentication, and data-pipeline architecture in a single skill.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

User runs `/ds-backend`, or asks to design/review an API, database schema, auth flow, or data pipeline.

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "design REST API", "design database schema" | "implement the endpoint code" (→ manual / ds-fix) |
| "review OpenAPI spec", "audit DB migration" | "audit OWASP / regulatory security" (→ ds-compliance --security) |
| "design auth flow with OAuth/RBAC" | "deploy auth service to production" (→ ds-deploy) |
| "audit the data pipeline (ingest/ETL/cleaning/retention)" | "optimize one pipeline metric via experiments" (→ ds-tune) |
| "audit API/DB/auth/data-pipeline design conformance" | "generic code quality review (readability, duplication)" (→ ds-review) |

## Contract

**Dimensions:** B5 (API ergonomics), D3, D4, D5, A10 (OpenAPI spec), A9 (conditional ecosystem rules), C1 (secure-by-design, conditional messaging), D10 (admin API + stats), A11 (webhook/export/embed)
**Framework alignment (advisory):** Google SRE PRR (D3, D4), OpenAPI Specification 3.1+ (A10), OWASP ASVS 5.0 (C1).

- Covers five scopes: API design, database design, authentication, data pipelines (ingest → clean → merge → store → serve), and LLM/AI features (conditional — only when the project integrates an LLM/AI provider).
- Generates specifications, not implementation — produces OpenAPI specs, migration files, auth flow diagrams.
- Only well-established patterns — no experimental or untested approaches.
- Minimal liability + maximum privacy + minimum deps: auth prioritizes managed services over DIY; data minimization in every schema (responses expose only required fields); prefer platform-native auth over third-party SDKs.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- State-exempt: audit is regenerable from source; applied fixes land in the working tree — git is the record.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing API/DB/auth for issues |
| `--design` | Design new endpoints, schema, or auth flow |
| `--spec` | Generate OpenAPI spec, migration files, or auth documentation (includes migration generation/review — no separate flag) |
| `--scope={x}` | Specific scope: api, db, auth, data-pipeline, llm (comma-separated) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default: Audit (recommended); the choice is recorded in the summary. A disambiguating flag (`--audit`/`--design`/`--scope`) selects that mode directly. `--ask` with no disambiguating flag: present the up-front mode menu — Audit (recommended) / Design / (Cancel); each option's effect matches its row in the Arguments table above.

## Scopes

An `unknown` signal never excludes a scope — it runs the scope and reports the signal as unresolved. `--scope=` overrides this table for the named scopes; `--ask` shows the resolved table before running.

| Scope | Runs when (signal) | Otherwise | Covers | Reference (loaded when scope ran) |
|-------|---------------------|-----------|--------|-------------------------------------|
| `api` | api ≠ none | N/A — no API surface detected | API design — naming, versioning, status codes, pagination, errors, rate limiting, caching, idempotency, security (OWASP API Top 10) | [references/rules-api.md](references/rules-api.md) |
| `db` | db ≠ none | N/A — no database detected | Database design — schema, indexing, migrations, query patterns, backup, PII/privacy, multi-tenant isolation | [references/rules-database.md](references/rules-database.md) |
| `auth` | auth ≠ none | N/A — no auth mechanism detected | Authentication — OAuth2/OIDC, JWT/session, RBAC, MFA, API keys, social login | [references/rules-auth.md](references/rules-auth.md) |
| `data-pipeline` | pipeline surfaces found in Discover (ingest jobs, ETL/transform scripts, schedulers/queues), or integrations include an ingest/ETL signal | N/A — no pipeline surfaces detected | Ingest → clean → merge → store → serve — idempotency, quality gates, retention, lineage, sync round-trip integrity | [references/rules-data-pipeline.md](references/rules-data-pipeline.md) |
| `llm` | integrations contain an LLM/AI provider (`OPENAI_`, `ANTHROPIC_`, or an SDK import), or `--scope=llm` passed | N/A — no LLM/AI integration detected | LLM/AI features — conditional, active only when detected or requested | — |

Four checks activate independent of `--scope`, gated on their own signal: Admin & Support Operability (D10, advisory — any endpoint surface), Multi-Tenant/Org Configuration (an org/workspace concept with more than one config layer), Transactional Messaging (a messaging SDK, a consent field, or reminder-scheduling code), A9 Google/Apple Ecosystem Rules (blueprint `Integrations` is `google-workspace` or `apple-ecosystem`). Full check-area tables for every scope plus these four, and for `llm`: [references/scopes.md](references/scopes.md) (loaded when that detail is needed beyond the rule files, or a conditional cross-cutting check activates).

## Delegation

**Owns:** api, db, auth, data-pipeline, llm, backend-architecture | **Delegates:** ds-frontend → AI-feature UX | **Receives:** ds-ship → Phase 2 backend pass; ds-productize → billing model + webhook security; ds-freeze → flag-gate defer-hidden items

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → default to Audit, recorded in the summary; `--ask` → mode menu (see Arguments).
2. **Upstream artifacts:** Profile → {Project Map.Modules, Config.data, Project Map.External, Type + Stack}. Findings({api, db, auth}) → verify + use. Absent → own analysis.
3. Detect project stack (framework, ORM, auth library) by scanning config files + dependencies.
4. Resolve scopes against the scope-resolution table above; load each ran scope's reference file.

**Gate:** Scope and mode confirmed. If fails → `--ask` menu with no response: default `--audit --scope=api,db,auth,data-pipeline` (+`llm` when detected), WARN, announce the defaulted scope before proceeding.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` fresh (meta `git_hash` equals `git rev-parse HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → use relevant findings. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. Search for route/endpoint definitions, controller files, middleware.
3. Search for DB schema files (migrations, models, entity definitions).
4. Search for auth configuration (JWT secret usage, session config, OAuth setup).
5. Search for pipeline surfaces: ingest jobs, ETL/transform scripts, schedulers/queues, batch scripts, data-quality checks.
6. Build inventory: endpoints, tables/models, auth mechanisms, pipeline stages (ingest → clean → merge → store → serve).

**Gate:** Inventory built — endpoints, tables/models, auth mechanisms, and pipeline stages each populated or marked `not-found`. No backend code found → switch to design mode. If fails → partial inventory: mark missing scopes `not-found`, proceed with detected scopes only, note skipped scopes in report.

### Phase 3: Analyze [--audit mode]

**Per-scope rules:** run every rule in each ran scope's already-loaded reference file — `api`: API-01..20 (naming, status codes, pagination, error consistency, input validation, OWASP API Top 10). `db`: DB-01..24 (indexes, N+1, migration safety, PII/encryption, timestamps). `auth`: AUTH-01..25 (token signing, refresh rotation, CSRF, password hashing, redirect URI validation). `data-pipeline`: DP-01..26 (schema-at-boundary, idempotency, data-quality gates, watermarks/backfill, retention, structured logging + alerting).

**Cross-cutting checks:**

- **Architecture ([../core/principles.md §2](../core/principles.md)):** every API/service module vs SOLID/GRASP — SRP (handler doing >1 concern), OCP (new endpoint requires editing existing), LSP (subtype changes contract), ISP (controller injecting unused dependency), DIP (handler depending on a concrete DB driver instead of a repository abstraction, or a dispatcher with an `if (type === '<literal>')` branch per integration instead of a registered adapter exposing a standard interface — cross-cutting concerns like auth-refresh/rate-limit/retry live once in the dispatcher, never per adapter), Information Expert, Low Coupling (>7 unrelated peer imports), High Cohesion. Cite principle by name in the finding title.
- **Reliability ([../core/principles.md §4](../core/principles.md)):** flag missing — timeout on every outbound call, retry-with-exponential-backoff (idempotent only), circuit breaker on high-volume deps, health checks (liveness + readiness), idempotency keys on externally-exposed writes, graceful shutdown (drain → close → exit), structured logging (never raw `print`), fail-fast validation at every boundary.
- **Twelve-Factor ([../core/principles.md §3](../core/principles.md)):** stateless processes (Factor 6), backing services as URLs from env (Factor 4), config in env (Factor 3), env-provided port binding (Factor 7), build/release/run separation (Factor 5), logs to stdout (Factor 11), admin tasks as one-off processes (Factor 12).

Cross-scope dedup: merge findings at same `{file}:{line}`, keep highest severity.

**Gate:** Findings collected. 0 findings → skip to summary. If fails → unanalyzable scope → re-read source once; still unanalyzable (binary, generated-only) → mark `inconclusive` in the findings list, continue, surface in report.

### Phase 4: Design [--design mode]

1. Default: infer requirements from the blueprint profile, existing schema/spec files, and prior art in the codebase; no context found → proceed with minimal conventional CRUD defaults and record every assumption in the summary. `--ask`: ask the user for requirements (entities, relationships, user roles).
2. Generate per scope:
   - **API:** endpoint list with methods, paths, request/response shapes, status codes
   - **DB:** ER diagram (text), table definitions, index strategy
   - **Auth:** flow diagram (text), token strategy, permission model
3. Default: finalize on the first best-judgment pass, recorded directly in the generated-artifacts list. `--ask`: present design for user review + iteration.

**Gate:** Design finalized (default) or user approves / requests changes (`--ask`). If fails → `--ask` changes requested → apply, re-present; after 3 rounds with no approval → ask "Continue with current / Abort?"; honor choice, record in the generated-artifacts list.

### Phase 5: Spec [--spec mode]

1. **API:** OpenAPI 3.1+ YAML spec from analyzed/designed endpoints (current stable: 3.2.0, Sept 2025 — strictly 3.1-compatible; 4.0 "Moonwalk" has no release date, stay on 3.x).
2. **DB:** Migration files in project's ORM format, or raw SQL.
3. **Auth:** Authentication flow documentation, middleware configuration.

**Gate:** Spec files generated + syntactically valid — per YAML/JSON artifact: `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" {file}` → exit 0 (no `python3` → record the check unrun, validate by re-reading). If fails → identify invalid spec + error location; attempt auto-correction once; still invalid → write file with inline `# SYNTAX ERROR: {description}` at the offending line, mark artifact `partial`, surface error.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Default: every item, including CRITICAL, resolves via the same impact/effort/risk reasoning an approval review would show, applied and recorded `fixed`/`failed`; items matching the publish/irreversible exception list resolve `skipped (only you can do)` instead. `--ask`: present each item compactly (`[severity] title — file:line`) grouped by severity with counts, state the question (`Approve these N items?`); ask Apply all / per-severity bulk (alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = the displayed set.

**Gate:** All items resolved. If fails → forced binary re-prompt; no response → `skipped (no response)` and proceed.

### Mechanical Done Gate [any project file modified — applied fixes, flag-gate tasks from ds-freeze]

Resolve `{check-cmd}` in Phase 1: ds-quality enforcement arm installed → use its gate command; else stack-native format/lint/type/test commands; none detectable → Verification-Infrastructure Gap, offer `/ds-quality`, record the decision. Checkpoint, before this skill's first write: `git status --porcelain` → non-empty: default proceeds only when pre-existing dirty files stay untouched by this skill's writes; overlap → those items `skipped (only you can do)`. `--ask`: ask Commit first (recommended) / Stash / Proceed anyway (`git checkout -- {file}` also discards pre-existing edits in that file). Never run a fix batch over uncommitted unrelated changes silently. Capture the baseline before the first modification; baseline red → done means "no *new* red", baseline reds reported as findings, never inherited as green. After each fix batch: run `{check-cmd}` on the touched scope — new red → repair and re-run (≤3 attempts); still red → revert via `git checkout -- {file}`, disposition `failed (mechanical gate)` with the captured error. Before Phase 7: run the full `{check-cmd}` once — its command + output is the Completion Evidence; never report `OK` with a new red. Spec/design-only runs (no working-tree modification) → gate N/A, state `no files modified — mechanical gate N/A`.

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth,data-pipeline[,llm]} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

- **Audit output:** findings table grouped by scope (API / DB / Auth / Data Pipeline).
- **Design output:** generated artifacts list with locations.
- **Spec output:** generated specification files with locations.

Disposition accounting — totals balance.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `OpenAPI spec for {n} endpoints with RFC 9457 error format — frontend / mobile clients can generate type-safe SDKs from one source of truth`
- `DB schema reviewed: {n} missing indexes added, {n} N+1 query risks flagged — query latency expected to drop on hot paths`
- `Auth flow designed: {provider}-based OAuth + RBAC matrix — credential storage and session handling no longer hand-rolled`

Zero-change run: `No design changes — existing API/DB/auth meets reviewed scope`.

**Gate:** Summary + Effect printed; every generated artifact confirmed on disk (`test -f {path}` → exit 0, per artifact). If fails → unconfirmable artifact (file not written / spec invalid) → list missing artifacts with intended paths + status (`partial`/`failed`), status `WARN`, instruct user which phases to re-run.

## Quality Gates

Per-finding citation is W1 below; spec validity, migration up/down, and PKCE are enforced by Phase 5's Gate and rules DB-03/AUTH-03 — not restated here.

- W10: Defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes
- W1: Cite file:line, never assume. W2: Check consumers after modify. W3: Touch only task-required lines. W4: Re-read after gap. W5: Uncertain → lower severity. W6: Verify all phases output. W7: Dedup file:line. W8: No raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No backend code found | Switch to design mode, ask what to build |
| Framework not recognized | Use generic patterns, warn about missing framework-specific optimization |
| Multiple ORMs / auth libraries | Default: infer the primary from usage frequency/config and record the assumption. `--ask`: ask the user which is primary. |
| Migration would cause data loss | Default: still generated with the CRITICAL flag retained and a safer expand-contract alternative proposed alongside it — never silently applied to a live database (spec files only). `--ask`: flag CRITICAL, require explicit approval. |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | SQL injection, broken auth, exposed secrets, data loss in migration |
| HIGH | Missing auth on endpoint, N+1 in hot path, no input validation |
| MEDIUM | Inconsistent naming, missing pagination, suboptimal index |
| LOW | Convention deviation, missing documentation |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Serverless functions | Adapt checks for function-based routing |
| Stream/queue pipeline (no batch jobs) | Apply pipeline checks to consumers: idempotent handlers, DLQ present, offset/ack semantics stated |
| GraphQL only | Skip REST naming checks, focus on resolver patterns + schema design |
| SQLite project | Skip replication/clustering checks, focus on WAL mode + connection handling |
| No ORM (raw SQL) | Check for SQL injection, parameterized queries |
| Microservices | Ask which service to analyze, check inter-service auth |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
