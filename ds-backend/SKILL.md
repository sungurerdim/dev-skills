---
name: ds-backend
description: Backend architecture — API design, database schema, authentication, data pipelines. Use when designing or reviewing a backend, REST/GraphQL APIs, data models, auth flows, or ingest/ETL pipelines.
---

# /ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, schemas that don't survive first migration, and data pipelines that double-process on retry. Skill designs all four layers correctly from start.

**Backend Design** — API design, database schema, authentication, and data-pipeline architecture in a single skill.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-backend`
- User asks to design an API, review database schema, or implement auth
- User asks about REST/GraphQL design, migration strategy, or RBAC
- User asks "review my API" or "design my database schema"

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
**Framework alignment (advisory):** Google SRE PRR (D3, D4), OpenAPI Specification 3.1+ (A10), OWASP ASVS 5.0 (C1, released May 2025).

- Covers five scopes: API design, database design, authentication, data pipelines (ingest → clean → merge → store → serve), and LLM/AI features (conditional — only when the project integrates an LLM/AI provider).
- Generates specifications, not implementation — produces OpenAPI specs, migration files, auth flow diagrams.
- Only suggests well-established patterns — no experimental or untested approaches.
- Minimal liability + maximum privacy + minimum dependencies: auth recommendations prioritize managed services over DIY; data minimization in every schema (API responses expose only required fields); prefer platform-native auth over third-party SDKs where feasible.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- State-exempt: audit is regenerable from source; applied fixes land in the working tree — git is the durable record.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing API/DB/auth for issues |
| `--design` | Design new endpoints, schema, or auth flow |
| `--spec` | Generate OpenAPI spec, migration files, or auth documentation (includes migration generation/review — no separate flag) |
| `--scope={x}` | Specific scope: api, db, auth, data-pipeline, llm (comma-separated) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `needs-human`. |

Default: Audit (recommended); the choice is recorded in the summary. A disambiguating flag (`--audit`/`--design`/`--scope`) selects that mode directly. `--ask` with no disambiguating flag: present the up-front mode menu — Audit (recommended) / Design / (Cancel); each option's effect matches its row in the Arguments table above.

## Scopes

| Scope | Covers |
|-------|--------|
| `api` | API design — naming, versioning, status codes, pagination, errors, rate limiting, caching, idempotency, security (OWASP API Top 10) |
| `db` | Database design — schema, indexing, migrations, query patterns, backup, PII/privacy, multi-tenant isolation |
| `auth` | Authentication — OAuth2/OIDC, JWT/session, RBAC, MFA, API keys, social login |
| `data-pipeline` | Ingest → clean → merge → store → serve — idempotency, quality gates, retention, lineage, sync round-trip integrity |
| `llm` | LLM/AI features — conditional, active only when an LLM/AI provider integration is detected or `--scope=llm` is passed |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| `api` | api ≠ none | N/A — no API surface detected |
| `db` | db ≠ none | N/A — no database detected |
| `auth` | auth ≠ none | N/A — no auth mechanism detected |
| `data-pipeline` | pipeline surfaces found in Discover (ingest jobs, ETL/transform scripts, schedulers/queues), or integrations include an ingest/ETL signal | N/A — no pipeline surfaces detected |
| `llm` | integrations contain an LLM/AI provider (`OPENAI_`, `ANTHROPIC_`, or an SDK import), or `--scope=llm` passed | N/A — no LLM/AI integration detected |

An `unknown` signal never excludes a scope — it runs the scope and reports the signal as unresolved. `--scope=` overrides this table for the named scopes; `--ask` shows the resolved table before running.

Four checks activate independent of `--scope`, gated on their own signal: Admin & Support Operability (D10, advisory — any endpoint surface), Multi-Tenant/Org Configuration (an org/workspace concept with more than one config layer), Transactional Messaging (a messaging SDK, a consent field, or reminder-scheduling code), A9 Google/Apple Ecosystem Rules (blueprint `Integrations` is `google-workspace` or `apple-ecosystem`). Full check-area tables for every scope plus these four: [references/scopes.md](references/scopes.md).

| Scope | Reference File | Loaded when |
|-------|-----------------|-------------|
| `api` | [references/rules-api.md](references/rules-api.md) | scope `api` ran |
| `db` | [references/rules-database.md](references/rules-database.md) | scope `db` ran |
| `auth` | [references/rules-auth.md](references/rules-auth.md) | scope `auth` ran |
| `data-pipeline` | [references/rules-data-pipeline.md](references/rules-data-pipeline.md) | scope `data-pipeline` ran |
| all scopes | [references/scopes.md](references/scopes.md) | full check-area detail needed beyond the rule files, or a conditional cross-cutting check activates |

## Delegation

**Owns:** api, db, auth, data-pipeline, llm, backend-architecture | **Delegates:** ds-frontend → AI-feature UX (streaming/stop/uncertainty display) | **Receives:** ds-ship → Phase 2 backend pass; ds-productize → billing data model + webhook endpoint security pass; ds-freeze → flag-gate defer-hidden items

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → default to Audit, recorded in the summary; `--ask` → mode menu (see Arguments).
2. **Upstream artifacts:** Profile → {Project Map.Modules, Config.data, Project Map.External, Type + Stack}. Findings({api, db, auth}) → verify + use. Absent → own analysis.
3. Detect project stack (framework, ORM, auth library) by scanning config files + dependencies.
4. Resolve scopes against the scope-resolution table above; load each ran scope's reference file.

**Gate:** Scope and mode confirmed. If fails → `--ask` menu shown with no response → default `--audit --scope=api,db,auth,data-pipeline` (+`llm` when an AI-provider integration is detected), WARN, announce defaulted scope before proceeding.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` fresh (its meta `git_hash` equals `git rev-parse HEAD` output AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → use relevant findings. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. Search for route/endpoint definitions, controller files, middleware.
3. Search for DB schema files (migrations, models, entity definitions).
4. Search for auth configuration (JWT secret usage, session config, OAuth setup).
5. Search for pipeline surfaces: ingest jobs, ETL/transform scripts, schedulers/queues, batch scripts, data-quality checks.
6. Build inventory: endpoints list, tables/models list, auth mechanisms, pipeline stages (ingest → clean → merge → store → serve).

**Gate:** Inventory built — endpoints list, tables/models list, auth mechanisms, and pipeline stages each populated or marked `not-found`. No backend code found → switch to design mode. If fails → partial inventory → mark missing scopes `not-found` in the inventory, proceed with detected scopes only, note skipped scopes in report.

### Phase 3: Analyze [--audit mode]

**API:**

1. Naming conventions vs REST best practices.
2. Status code usage (200 GET, 201 POST create, 204 DELETE).
3. Missing pagination on list endpoints.
4. Error response consistency.
5. Input validation on all mutation endpoints.
6. OWASP API Top 10 (BOLA, broken auth, excessive data exposure).

**Database:**

1. Missing indexes on FKs + frequently-queried columns.
2. N+1 query patterns in ORM usage.
3. Migration safety (no `DROP COLUMN` without data backup).
4. PII columns without encryption or access controls.
5. Missing `created_at`/`updated_at` timestamps.

**Auth:**

1. Token signing uses asymmetric keys or strong secrets.
2. Refresh token rotation implemented.
3. CSRF protection on session-based auth.
4. Password hashing uses bcrypt or argon2 (not MD5/SHA).
5. OAuth redirect URIs strictly validated.

**Data pipeline:**

1. Every ingest boundary validates schema/contract; malformed input rejected or quarantined, never silently dropped.
2. Every job/handler idempotent — re-run produces identical state; dedup keys on at-least-once delivery.
3. Data-quality checks (null/duplicate/range) present between clean and merge stages.
4. Incremental loads use watermarks/cursors; backfill path exists and is bounded.
5. Retention policy per store; PII absent from intermediate/derived stores unless required (delegate canonical privacy to ds-compliance).
6. Per-job structured logging + failure alerting; row-count or freshness check on critical sinks.

**Cross-cutting checks:**

- **Architecture ([../core/principles.md §2](../core/principles.md)):** every API/service module vs SOLID/GRASP — SRP (handler doing >1 concern), OCP (new endpoint requires editing existing), LSP (subtype changes contract), ISP (controller injecting unused dependency), DIP (handler depending on concrete DB driver instead of repository abstraction, or a central dispatcher containing an `if (type === '<literal>')` branch per external integration instead of a registered adapter/strategy object exposing a standard interface — cross-cutting concerns like auth-refresh/rate-limit/retry/ID-rewriting live once in the dispatcher, never duplicated per adapter), Information Expert (logic away from owning entity), Low Coupling (>7 unrelated peer imports), High Cohesion (one module owning unrelated concerns). Cite principle by name in finding title.
- **Reliability ([../core/principles.md §4](../core/principles.md)):** flag missing — timeout on every outbound call, retry-with-exponential-backoff (idempotent only — never on POST without idempotency key), circuit breaker on high-volume external deps, health checks (liveness + readiness), idempotency keys on externally-exposed write endpoints, graceful shutdown (drain → close → exit), structured logging (JSON/kv, never raw `print`), fail-fast validation at every boundary.
- **Twelve-Factor ([../core/principles.md §3](../core/principles.md)):** stateless processes (Factor 6 — no in-memory session/cache survives restart), backing services as URLs from env (Factor 4), config in env (Factor 3), port binding via env-provided value (Factor 7), build/release/run separation (Factor 5), logs to stdout (Factor 11), admin tasks (migrations, seeds) as one-off processes (Factor 12).

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

**Gate:** Spec files generated + syntactically valid — per YAML/JSON spec artifact: `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" {file}` → exit 0 (no `python3` in-session → record the parse check as unrun, validate by re-reading the file). If fails → identify invalid spec + error location; attempt auto-correction once; still invalid → write file with inline `# SYNTAX ERROR: {description}` comment at offending line, mark artifact `partial`, surface error.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Default: every item, including CRITICAL, resolves via the same impact/effort/risk reasoning an approval review would show, applied and recorded `fixed`/`failed`; items matching the publish/irreversible exception list resolve `skipped (needs-human)` instead. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → forced binary re-prompt; no response → `skipped (no response)` and proceed.

### Mechanical Done Gate [any project file modified — applied fixes, flag-gate tasks from ds-freeze]

Resolve `{check-cmd}` in Phase 1: ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint) → use its gate command; else stack-native format/lint/type/test commands; none detectable → Verification-Infrastructure Gap — report it, offer `/ds-quality`, record the decision. Checkpoint pre-step, before this skill's first write to a project file: `git status --porcelain` → non-empty: default — proceed only when the pre-existing dirty files stay untouched by this skill's writes; overlap → resolve those items `skipped (needs-human)`. `--ask`: ask Commit first (recommended) / Stash / Proceed anyway (the revert path `git checkout -- {file}` also discards pre-existing edits in that file). Never run a fix batch over uncommitted unrelated changes silently. Capture the baseline before the first modification; baseline red → done condition is "no *new* red", baseline reds reported as findings, never inherited as green. After each applied fix batch: run `{check-cmd}` on the touched scope — new red → repair and re-run the same command (≤3 attempts); still red → revert via `git checkout -- {file}`, disposition `failed (mechanical gate)` with the captured error. Before Phase 7: run the full `{check-cmd}` once; its command + observed output is the Completion Evidence. Never report `OK` with a new red. Spec-only/design-only runs (no working-tree modification) → gate not applicable, state `no files modified — mechanical gate N/A`.

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth,data-pipeline[,llm]} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

- **Audit output:** findings table grouped by scope (API / DB / Auth / Data Pipeline).
- **Design output:** generated artifacts list with locations.
- **Spec output:** generated specification files with locations.

Disposition accounting — totals balance.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `OpenAPI spec for {n} endpoints with RFC 9457 error format — frontend / mobile clients can generate type-safe SDKs from one source of truth`
- `DB schema reviewed: {n} missing indexes added, {n} N+1 query risks flagged — query latency expected to drop on hot paths`
- `Auth flow designed: {provider}-based OAuth + RBAC matrix — credential storage and session handling no longer hand-rolled`

Zero-change run: `No design changes — existing API/DB/auth meets reviewed scope`.

**Gate:** Summary + Value Delivered printed; every generated artifact confirmed on disk (`test -f {path}` → exit 0, per artifact). If fails → unconfirmable artifact (file not written / spec invalid) → list missing artifacts with intended paths + status (`partial`/`failed`), status `WARN`, instruct user which phases to re-run.

## Quality Gates

- Every API finding cites specific endpoint + HTTP method
- Every DB finding cites specific table/column or migration file
- Every auth finding cites specific file + configuration
- OpenAPI spec validates against OpenAPI 3.1+ schema
- Migration files include both `up` + `down` operations
- Auth flows use current best practices (PKCE for all client types, not implicit flow)
- W10: Defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered
- W1: Cite file:line; never assume. W2: Check consumers after modify. W3: Touch only task-required lines. W4: Re-read after gap. W5: Uncertain → lower severity. W6: Verify all phases output. W7: Dedup file:line. W8: No raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No backend code found | Switch to design mode, ask what to build |
| Framework not recognized | Use generic patterns, warn about framework-specific optimizations |
| Multiple ORMs / auth libraries | Default: infer the primary from usage frequency/config and record the assumption in the summary. `--ask`: ask the user which is primary. |
| Migration would cause data loss | Default: still generated with the CRITICAL flag retained and a safer expand-contract alternative proposed alongside it — never silently applied to a live database (this skill generates spec files only). `--ask`: flag as CRITICAL and require explicit approval before proceeding. |

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
