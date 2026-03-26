# /ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, and schemas that don't survive the first migration. This skill designs all three layers correctly from the start.

**Backend Design** — API design, database schema, and authentication architecture in a single skill.

## Triggers

- User runs `/ds-backend`
- User asks to design an API, review database schema, or implement auth
- User asks about REST/GraphQL design, migration strategy, or RBAC
- User asks "review my API" or "design my database schema"

## Contract

- Covers three scopes: API design, database design, and authentication
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every finding receives a disposition in the summary — zero silent drops (FRC)
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

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

**Goal:** Determine scope and mode.

1. If flags provided, proceed directly
2. If no flags, present interactive menu
3. **Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Project Map.Modules** → know API structure, skip architecture discovery
   - **Config.data** → know auth and data protection requirements
   - **Project Map.External** → know existing DB, cache, queue, auth providers
   - **Type + Stack** → skip own project detection
4. Detect project stack (framework, ORM, auth library) by scanning config files and dependencies
5. Load relevant reference docs based on detected scope

**Gate:** Scope and mode confirmed.

### Phase 2: Discover

**Goal:** Map existing backend architecture.

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use relevant findings
2. Search for route/endpoint definitions, controller files, middleware
3. Search for database schema files (migrations, models, entity definitions)
4. Search for auth configuration (JWT secret usage, session config, OAuth setup)
5. Build inventory: endpoints list, tables/models list, auth mechanisms

**Gate:** Inventory complete. If no backend code found → switch to design mode.

### Phase 3: Analyze [--audit mode]

**Goal:** Identify issues in existing code.

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

Cross-scope dedup: merge findings at same file:line, keep highest severity.

**Gate:** Findings collected. If 0 → skip to summary.

### Phase 4: Design [--design mode]

**Goal:** Generate new API/DB/auth design.

1. Ask user for requirements (entities, relationships, user roles)
2. Generate based on scope:
   - **API:** endpoint list with methods, paths, request/response shapes, status codes
   - **DB:** entity-relationship diagram (text), table definitions, index strategy
   - **Auth:** flow diagram (text), token strategy, permission model
3. Present design for user review and iteration

**Gate:** User approves design or requests changes.

### Phase 5: Spec [--spec mode]

**Goal:** Generate specification artifacts.

1. **API:** OpenAPI 3.0+ YAML spec from analyzed or designed endpoints
2. **DB:** Migration files in project's ORM format, or raw SQL
3. **Auth:** Authentication flow documentation, middleware configuration

**Gate:** Spec files generated and syntactically valid.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Items flagged `needs_approval` (cross-module changes, destructive actions, architectural decisions):
- **--auto without --force-approve:** List items, skip them, note in summary
- **--force-approve:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items with risk context. Ask: Apply All / Review Each / Skip All

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth} | Findings: N | Fixed: N | Skipped: N | Failed: N | Total: N
```

**Audit output:** Findings table grouped by scope (API / DB / Auth).

**Design output:** Generated artifacts list with locations.

**Spec output:** Generated specification files with locations.

**FRC accounting:** Every finding appears with a disposition. `fixed + failed + skipped + needs_approval + not_applicable = total`.

**Gate:** Summary printed with all design artifacts listed.

## Quality Gates

- Every API finding cites specific endpoint and HTTP method
- Every DB finding cites specific table/column or migration file
- Every auth finding cites specific file and configuration
- OpenAPI spec validates against OpenAPI 3.0+ schema
- Migration files include both `up` and `down` operations
- Auth flows use current best practices (PKCE for public clients, not implicit flow)
- Every finding gets a disposition in the summary — zero silent drops (FRC)

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
