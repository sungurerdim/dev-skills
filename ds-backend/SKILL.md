---
name: ds-backend
description: Backend architecture — API design, database schema, authentication. Use when designing or reviewing a backend, REST/GraphQL APIs, data models, or auth flows.
---

# /ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, and schemas that don't survive first migration. Skill designs all three layers correctly from start.

**Backend Design** — API design, database schema, and authentication architecture in a single skill.

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
| "review my API for REST conformance" | "fix lint errors in handlers" (→ ds-fix) |

## Contract

- Covers three scopes: API design, database design, authentication.
- Generates specifications, not implementation — produces OpenAPI specs, migration files, auth flow diagrams.
- Only suggests well-established patterns — no experimental or untested approaches.
- Minimal liability + maximum privacy + minimum dependencies: auth recommendations prioritize managed services over DIY; data minimization in every schema (API responses expose only required fields); prefer platform-native auth over third-party SDKs where feasible.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing API/DB/auth for issues |
| `--design` | Design new endpoints, schema, or auth flow |
| `--spec` | Generate OpenAPI spec, migration files, or auth documentation |
| `--migrate` | Generate or review database migrations |
| `--scope={x}` | Specific scope: api, db, auth (comma-separated) |
| `--auto` | All scopes, no questions, single-line summary |
| `--resume` | Resume from `ds/audit/backend.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present interactive mode selection.

## Scopes

### API

| Check Area | What It Covers |
|------------|---------------|
| Naming | RESTful naming, resource vs action endpoints |
| Versioning | URL vs header versioning strategy |
| Status codes | Correct HTTP status code usage |
| Pagination | Cursor vs offset, page size limits |
| Error format | RFC 9457 Problem Details (`application/problem+json`) |
| Input validation | Request validation, sanitization |
| Rate limiting | Headers, algorithm selection (token bucket, sliding window) |
| Caching | HTTP caching headers, ETag, Cache-Control |
| Idempotency | `Idempotency-Key` header for non-idempotent POST |
| Logging | Structured request logging (request ID, duration, status) |
| Security | OWASP API Top 10 checks |

### Database

| Check Area | What It Covers |
|------------|---------------|
| Schema design | Normalization, naming conventions, data types |
| Indexing | Missing indexes, over-indexing, composite order, GIN/GiST/BRIN for advanced cases |
| Migrations | Expand-contract pattern, safe vs dangerous ops, rollback tested |
| Query patterns | N+1 detection, EXPLAIN ANALYZE review, `pg_stat_statements`, connection pooling |
| Backup | 3-2-1 rule, WAL archiving, restore testing |
| Data privacy | PII classification, encryption at rest, GDPR right-to-erasure, retention |

### Auth

| Check Area | What It Covers |
|------------|---------------|
| Flow design | OAuth2 / OIDC correctness, PKCE required for all client types per RFC 9700 |
| Token handling | JWT signing (RS256/ES256), expiry, refresh rotation, storage (never localStorage) |
| Session management | Cookie security (HttpOnly, Secure, SameSite), CSRF, session fixation |
| RBAC | Role/permission model, authorization middleware, least privilege |
| Password security | Argon2id (primary), NIST 800-63B policy (min length, breached check, no complexity rules) |
| Social login | Provider integration, account linking, `sub` as stable identifier |
| MFA | TOTP, WebAuthn / passkeys, recovery codes (hashed, single-use), SMS OTP deprecation |
| API keys | Prefixed keys, hash-only storage, scoped permissions, rotation support |

## Delegation

**Owns:** api, db, auth, backend-architecture | **Delegates:** none | **Receives:** ds-ship → Phase 2 backend pass

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/backend.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-check endpoints/schemas inventory, discard stale findings), skip `done` phases, announce `[BE] Resuming from Phase {N}: {name}.` On Summary success, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ mode, scopes_selected, inventory: {endpoints[], tables[], auth_flows[]}, scopes_done[], findings[{id, severity, scope, disposition}], artifacts_generated[] }`.

1. Flags → proceed directly. No flags → interactive menu.
2. **IDU:** Profile → {Project Map.Modules, Config.data, Project Map.External, Type + Stack}. Findings({api, db, auth}) → verify + use. Absent → own analysis.
3. Detect project stack (framework, ORM, auth library) by scanning config files + dependencies.
4. Load relevant reference docs by detected scope: [references/rules-api.md](references/rules-api.md), [references/rules-auth.md](references/rules-auth.md), [references/rules-database.md](references/rules-database.md).

**Gate:** Scope and mode confirmed. If fails → no flags + no menu response → default `--audit --scope=api,db,auth` with WARN in state.data.mode; announce defaulted scope before proceeding.

### Phase 2: Discover

1. **Findings file check:** fresh `git_hash` → use relevant findings.
2. Search for route/endpoint definitions, controller files, middleware.
3. Search for DB schema files (migrations, models, entity definitions).
4. Search for auth configuration (JWT secret usage, session config, OAuth setup).
5. Build inventory: endpoints list, tables/models list, auth mechanisms.

**Gate:** Inventory complete. No backend code found → switch to design mode. If fails → partial inventory → mark missing scopes `not-found` in state.data.inventory, proceed with detected scopes only, note skipped scopes in report.

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

**Cross-cutting checks:**

- **Architecture ([references/principles.md §2](references/principles.md)):** every API/service module vs SOLID/GRASP — SRP (handler doing >1 concern), OCP (new endpoint requires editing existing), LSP (subtype changes contract), ISP (controller injecting unused dependency), DIP (handler depending on concrete DB driver instead of repository abstraction), Information Expert (logic away from owning entity), Low Coupling (>7 unrelated peer imports), High Cohesion (one module owning unrelated concerns). Cite principle by name in finding title.
- **Reliability ([references/principles.md §4](references/principles.md)):** flag missing — timeout on every outbound call, retry-with-exponential-backoff (idempotent only — never on POST without idempotency key), circuit breaker on high-volume external deps, health checks (liveness + readiness), idempotency keys on externally-exposed write endpoints, graceful shutdown (drain → close → exit), structured logging (JSON/kv, never raw `print`), fail-fast validation at every boundary.
- **Twelve-Factor ([references/principles.md §3](references/principles.md)):** stateless processes (Factor 6 — no in-memory session/cache survives restart), backing services as URLs from env (Factor 4), config in env (Factor 3), port binding via env-provided value (Factor 7), build/release/run separation (Factor 5), logs to stdout (Factor 11), admin tasks (migrations, seeds) as one-off processes (Factor 12).

Cross-scope dedup: merge findings at same `{file}:{line}`, keep highest severity.

**Gate:** Findings collected. 0 findings → skip to summary. If fails → unanalyzable scope → re-read source once; still unanalyzable (binary, generated-only) → mark `inconclusive` in state.data.findings, continue, surface in report.

### Phase 4: Design [--design mode]

1. Ask user for requirements (entities, relationships, user roles).
2. Generate per scope:
   - **API:** endpoint list with methods, paths, request/response shapes, status codes
   - **DB:** ER diagram (text), table definitions, index strategy
   - **Auth:** flow diagram (text), token strategy, permission model
3. Present design for user review + iteration.

**Gate:** User approves design or requests changes. If fails → changes requested → apply, re-present; after 3 rounds with no approval → ask "Continue with current / Abort?"; honor choice, record in state.data.artifacts_generated.

### Phase 5: Spec [--spec mode]

1. **API:** OpenAPI 3.0+ YAML spec from analyzed/designed endpoints.
2. **DB:** Migration files in project's ORM format, or raw SQL.
3. **Auth:** Authentication flow documentation, middleware configuration.

**Gate:** Spec files generated + syntactically valid. If fails → identify invalid spec + error location; attempt auto-correction once; still invalid → write file with inline `# SYNTAX ERROR: {description}` comment at offending line, mark artifact `partial`, surface error.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved. If fails → forced binary re-prompt; no response → `skipped (no response)` and proceed.

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

- **Audit output:** findings table grouped by scope (API / DB / Auth).
- **Design output:** generated artifacts list with locations.
- **Spec output:** generated specification files with locations.

FRC+DSC accounting.

**Value Delivered:** 1-5 concrete bullets, real design outputs only. Example shapes (placeholders, not literal):

- `OpenAPI spec for {n} endpoints with RFC 9457 error format — frontend / mobile clients can generate type-safe SDKs from one source of truth`
- `DB schema reviewed: {n} missing indexes added, {n} N+1 query risks flagged — query latency expected to drop on hot paths`
- `Auth flow designed: {provider}-based OAuth + RBAC matrix — credential storage and session handling no longer hand-rolled`

Zero-change run: `No design changes — existing API/DB/auth meets reviewed scope`.

**Gate:** Summary + Value Delivered printed; artifact paths confirmed. If fails → unconfirmable artifact (file not written / spec invalid) → list missing artifacts with intended paths + status (`partial`/`failed`), status `WARN`, instruct user which phases to re-run.

## Quality Gates

- Every API finding cites specific endpoint + HTTP method
- Every DB finding cites specific table/column or migration file
- Every auth finding cites specific file + configuration
- OpenAPI spec validates against OpenAPI 3.0+ schema
- Migration files include both `up` + `down` operations
- Auth flows use current best practices (PKCE for public clients, not implicit flow)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/backend.json` updated per scope, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | SQL injection, broken auth, exposed secrets, data loss in migration |
| HIGH | Missing auth on endpoint, N+1 in hot path, no input validation |
| MEDIUM | Inconsistent naming, missing pagination, suboptimal index |
| LOW | Convention deviation, missing documentation |

## Error Recovery

| Situation | Action |
|-----------|--------|
| No backend code found | Switch to design mode, ask what to build |
| Framework not recognized | Use generic patterns, warn about framework-specific optimizations |
| Multiple ORMs / auth libraries | Ask user which is primary |
| Migration would cause data loss | Flag as CRITICAL, require explicit approval |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Serverless functions | Adapt checks for function-based routing |
| GraphQL only | Skip REST naming checks, focus on resolver patterns + schema design |
| SQLite project | Skip replication/clustering checks, focus on WAL mode + connection handling |
| No ORM (raw SQL) | Check for SQL injection, parameterized queries |
| Microservices | Ask which service to analyze, check inter-service auth |
