# /ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, and schemas that don't survive first migration. Skill designs all three layers correctly from start.

**Backend Design** — API design, database schema, and authentication architecture in a single skill.

## Triggers

- User runs `/ds-backend`
- User asks to design an API, review database schema, or implement auth
- User asks about REST/GraphQL design, migration strategy, or RBAC
- User asks "review my API" or "design my database schema"

## Contract

- Covers three scopes: API design, database design, and authentication
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.
- Generates specifications, not implementation — produces OpenAPI specs, migration files, auth flow diagrams
- Only suggests well-established patterns — no experimental or untested approaches
- **Minimal liability:** auth recommendations prioritize managed services over DIY
- **Maximum privacy:** data minimization in every schema, API responses expose only required fields
- **Minimum dependencies:** prefer platform-native auth over third-party SDKs where feasible

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing API/DB/auth for issues |
| `--design` | Design new endpoints, schema, or auth flow |
| `--spec` | Generate OpenAPI spec, migration files, or auth documentation |
| `--migrate` | Generate or review database migrations |
| `--scope=<scope>` | Specific scope: api, db, auth (comma-separated) |
| `--auto` | All scopes, no questions, single-line summary |
| `--resume` | Resume from `ds/audit/backend.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present interactive mode selection.

## Scopes

### API Scope

| Check Area | What It Covers |
|------------|---------------|
| Naming | RESTful naming conventions, resource vs action endpoints |
| Versioning | URL vs header versioning strategy |
| Status codes | Correct HTTP status code usage |
| Pagination | Cursor vs offset pagination, page size limits |
| Error format | RFC 9457 Problem Details structure (`application/problem+json`) |
| Input validation | Request validation, sanitization |
| Rate limiting | Rate limit headers, algorithm selection (token bucket, sliding window) |
| Caching | HTTP caching headers, ETag, Cache-Control directives |
| Idempotency | Idempotency-Key header for non-idempotent POST endpoints |
| Logging | Structured request logging (request ID, duration, status) |
| Security | OWASP API Top 10 checks |

### Database Scope

| Check Area | What It Covers |
|------------|---------------|
| Schema design | Normalization, naming conventions, data types |
| Indexing | Missing indexes, over-indexing, composite index order, GIN/GiST/BRIN for advanced use cases |
| Migrations | Expand-contract pattern, safe vs dangerous operations, rollback tested |
| Query patterns | N+1 detection, EXPLAIN ANALYZE review, pg_stat_statements, connection pooling |
| Backup | 3-2-1 backup rule, WAL archiving, restore testing |
| Data privacy | PII classification, encryption at rest, GDPR right-to-erasure, retention policies |

### Auth Scope

| Check Area | What It Covers |
|------------|---------------|
| Flow design | OAuth2/OIDC correctness, PKCE required for all client types per RFC 9700 |
| Token handling | JWT signing (RS256/ES256), expiry, refresh rotation, storage (never localStorage) |
| Session management | Cookie security (HttpOnly, Secure, SameSite), CSRF protection, session fixation |
| RBAC | Role/permission model, authorization middleware, least privilege |
| Password security | Argon2id (primary), NIST 800-63B policy (min length, breached check, no complexity rules) |
| Social login | Provider integration, account linking, `sub` as stable identifier |
| MFA | TOTP, WebAuthn/passkeys, recovery codes (hashed, single-use), SMS OTP deprecation |
| API keys | Prefixed keys, hash-only storage, scoped permissions, rotation support |

## Delegation

**Owns:** api, db, auth, backend-architecture | **Delegates:** none | **Receives:** ds-ship → Phase 2 backend pass

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/backend.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-check endpoints/schemas inventory, discard stale findings), skip `done` phases, announce `[BE] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

**State `data` shape:** `{ mode, scopes_selected, inventory: {endpoints[], tables[], auth_flows[]}, scopes_done[], findings[{id, severity, scope, disposition}], artifacts_generated[] }`.

1. Flags provided → proceed directly
2. No flags → present interactive menu
3. **IDU:** Profile → {Project Map.Modules, Config.data, Project Map.External, Type + Stack}. Findings({api, db, auth}) → verify + use. Absent → own analysis.
4. Detect project stack (framework, ORM, auth library) by scanning config files and dependencies
5. Load relevant reference docs based on detected scope: [references/rules-api.md](references/rules-api.md), [references/rules-auth.md](references/rules-auth.md), [references/rules-database.md](references/rules-database.md)

**Gate:** Scope and mode confirmed.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → use relevant findings
2. Search for route/endpoint definitions, controller files, middleware
3. Search for database schema files (migrations, models, entity definitions)
4. Search for auth configuration (JWT secret usage, session config, OAuth setup)
5. Build inventory: endpoints list, tables/models list, auth mechanisms

**Gate:** Inventory complete. No backend code found → switch to design mode.

### Phase 3: Analyze [--audit mode]

**API analysis:**
1. Check naming conventions against REST best practices
2. Verify status code usage (200 for GET, 201 for POST create, 204 for DELETE)
3. Check for missing pagination on list endpoints
4. Verify error response consistency
5. Check input validation presence on all mutation endpoints
6. OWASP API Top 10 check (BOLA, broken auth, excessive data exposure)

**Database analysis:**
1. Check schema for missing indexes on foreign keys and frequently-queried columns
2. Detect N+1 query patterns in ORM usage
3. Check migration safety (no `DROP COLUMN` without data backup)
4. Identify PII columns without encryption or access controls
5. Check for missing `created_at`/`updated_at` timestamps

**Auth analysis:**
1. Verify token signing uses asymmetric keys or strong secrets
2. Check refresh token rotation is implemented
3. Verify CSRF protection on session-based auth
4. Check password hashing uses bcrypt or argon2 (not MD5/SHA)
5. Verify OAuth redirect URIs are strictly validated

**Architecture checks ([references/principles.md §2](references/principles.md)):** Evaluate every API/service module against SOLID/GRASP — SRP (handler doing >1 concern: validation + business + persistence), OCP (new endpoint requires editing existing handler), LSP (subtype changes contract), ISP (controller injecting dependency it never calls), DIP (handler depending on concrete DB driver instead of repository abstraction), Information Expert (logic placed away from owning entity), Low Coupling (>7 unrelated peer imports), High Cohesion (one module owning unrelated concerns). Cite principle by name in finding title.

**Reliability checks ([references/principles.md §4](references/principles.md)):** Flag missing — timeout on every outbound HTTP/DB/queue call, retry-with-exponential-backoff (idempotent operations only — never on POST without idempotency key), circuit breaker on high-volume external dependencies, health checks (liveness + readiness endpoints), idempotency keys on externally-exposed write endpoints, graceful shutdown handler (drain → close → exit), structured logging (JSON / kv-pair, never raw `print`), fail-fast input validation at every boundary.

**Twelve-Factor checks ([references/principles.md §3](references/principles.md)):** Stateless processes (no in-memory session/cache survives restart — Factor 6), backing services as URLs from environment (Factor 4), config in environment never in code (Factor 3), port binding via env-provided value (Factor 7), build/release/run separation (Factor 5), logs to stdout (Factor 11), admin tasks (migrations, seeds) as one-off processes against the same code (Factor 12).

Cross-scope dedup: merge findings at same file:line, keep highest severity.

**Gate:** Findings collected. 0 findings → skip to summary.

### Phase 4: Design [--design mode]

1. Ask user for requirements (entities, relationships, user roles)
2. Generate based on scope:
   - **API:** endpoint list with methods, paths, request/response shapes, status codes
   - **DB:** entity-relationship diagram (text), table definitions, index strategy
   - **Auth:** flow diagram (text), token strategy, permission model
3. Present design for user review and iteration

**Gate:** User approves design or requests changes.

### Phase 5: Spec [--spec mode]

1. **API:** OpenAPI 3.0+ YAML spec from analyzed or designed endpoints
2. **DB:** Migration files in project's ORM format, or raw SQL
3. **Auth:** Authentication flow documentation, middleware configuration

**Gate:** Spec files generated and syntactically valid.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth} | Findings: N | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Audit output:** Findings table grouped by scope (API / DB / Auth).

**Design output:** Generated artifacts list with locations.

**Spec output:** Generated specification files with locations.

FRC+DSC accounting.

**Gate:** Summary printed with all design artifacts listed.

## Quality Gates

- Every API finding cites specific endpoint and HTTP method
- Every DB finding cites specific table/column or migration file
- Every auth finding cites specific file and configuration
- OpenAPI spec validates against OpenAPI 3.0+ schema
- Migration files include both `up` and `down` operations
- Auth flows use current best practices (PKCE for public clients, not implicit flow)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/backend.json` updated per scope, gitignored, deleted on successful Summary.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No backend code found | Switch to design mode, ask what to build |
| Framework not recognized | Use generic patterns, warn about framework-specific optimizations |
| Multiple ORMs/auth libraries | Ask user which is primary |
| Migration would cause data loss | Flag as CRITICAL, require explicit approval |

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
| GraphQL only | Skip REST naming checks, focus on resolver patterns, schema design |
| SQLite project | Skip replication/clustering checks, focus on WAL mode, connection handling |
| No ORM (raw SQL) | Check for SQL injection, parameterized queries |
| Microservices | Ask which service to analyze, check inter-service auth |
