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
**Framework alignment (advisory):** Google SRE PRR (D3, D4), OpenAPI Specification 3.1+ (A10), OWASP ASVS 5.0 (C1, released May 2025) — sourced references in SKILL-SPEC Dimension Coverage Map.

- Covers five scopes: API design, database design, authentication, data pipelines (ingest → clean → merge → store → serve), and LLM/AI features (conditional — only when the project integrates an LLM/AI provider).
- Generates specifications, not implementation — produces OpenAPI specs, migration files, auth flow diagrams.
- Only suggests well-established patterns — no experimental or untested approaches.
- Minimal liability + maximum privacy + minimum dependencies: auth recommendations prioritize managed services over DIY; data minimization in every schema (API responses expose only required fields); prefer platform-native auth over third-party SDKs where feasible.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- State-exempt: audit is regenerable from source; applied fixes land in the working tree — git is the durable record.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing API/DB/auth for issues |
| `--design` | Design new endpoints, schema, or auth flow |
| `--spec` | Generate OpenAPI spec, migration files, or auth documentation |
| `--migrate` | Generate or review database migrations |
| `--scope={x}` | Specific scope: api, db, auth, data-pipeline, llm (comma-separated) |
| `--auto` | All scopes, no questions, single-line summary |
| `--force-approve` | Apply `needs_approval` items without asking (CRITICAL still confirms per item) |

Without flags: present an up-front mode menu — Audit (recommended) / Design / (Cancel); each option's effect matches its row in the Arguments table above. A disambiguating flag (`--audit`/`--design`/`--scope`/`--auto`) skips the menu.

## Scopes

### API [Product DX]

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
| Error-channel decision (D4, advisory) | Production crash/error reporting has an explicit decision: consent-based opt-in PII-free aggregate channel (error class + app version + counter only — see ds-compliance crosscheck), or a documented acceptance of "support-mail blindness" as a risk. Missing entirely -> advisory finding, never a blocker (SKILL-SPEC §15) |
| Ecosystem openness (A11, advisory) | Webhook emission surface (versioned payload, HMAC signature verified constant-time, timestamp replay-tolerance check — industry convention ~5 min — `webhook-id` as consumer idempotency key, retry/backoff — aligned to the [Standard Webhooks](https://www.standardwebhooks.com/) spec where feasible) for state-change events; standard-format export endpoints (ICS/CSV/JSON, not just proprietary JSON) for user data; embeddable-surface posture (widget/iframe API) where the product has a natural embed use case. Product holds user data with no standard export path -> advisory portability finding (see ds-compliance crosscheck); never a blocker (SKILL-SPEC §15) |
| Security | OWASP API Security Top 10 (2023 edition — current as of 2026) checks |
| SLO baseline (advisory) | Critical user journeys have RED metrics (rate/errors/duration) exposed and an SLO defined; error-budget policy + burn-rate alerting delegated to ds-devops (advisory-handoff: absent → gap-note, never a blocker) |

### Database

| Check Area | What It Covers |
|------------|---------------|
| Schema design | Normalization, naming conventions, data types |
| Indexing | Missing indexes, over-indexing, composite order, GIN/GiST/BRIN for advanced cases |
| Migrations | Expand-contract pattern, safe vs dangerous ops, rollback tested, CI migration lint (Squawk) |
| Query patterns | N+1 detection, EXPLAIN ANALYZE review, `pg_stat_statements`, connection pooling |
| Backup | 3-2-1 rule, WAL archiving, restore testing |
| Restore-drill proof (D3, advisory) | Backup existing is not resilience — require a documented restore runbook + evidence of ≥1 executed end-to-end drill (worst case: total account/environment loss, restored to a clean target). Missing evidence -> advisory finding "backup exists, restore unproven — run a drill and record the runbook" (never a blocker, SKILL-SPEC §15) |
| Data privacy | PII classification, encryption at rest, GDPR right-to-erasure, retention |

### Data Pipeline

| Check Area | What It Covers |
|------------|---------------|
| Ingest validation | Schema/contract validation at every entry boundary, reject-by-default on malformed input |
| Idempotency | Jobs and handlers safe to re-run; dedup keys on at-least-once delivery |
| Cleaning & quality | Null/duplicate/range checks, quarantine path for bad records (never silent drop) |
| Merge & dedup | Deterministic merge keys, conflict policy, no order-dependent results |
| Incremental loads | Watermark/cursor-based increments, safe backfill, full-reload escape hatch |
| Storage & retention | Raw vs derived separation, retention/archival policy, PII minimization in intermediate stores |
| Observability | Per-job structured logs, failure alerts, row-count/freshness checks |
| Lineage | Source→transform→sink traceable; transformations documented or self-describing |
| Schema evolution | Compatibility mode chosen deliberately (BACKWARD default; FULL only where producer/consumer upgrade order must be independent); field changes additive-only — never rename/retype, add new field with default; CI compatibility gate against the schema registry where one exists |
| Data contract | Contract = schema + integrity constraints + PII metadata + enforcement policy, version-controlled like code — a bare schema alone is not a contract |

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

### LLM & AI Features [conditional — active only when an LLM/AI provider integration is detected (SDK import, API client, model config) or `--scope=llm` is passed]

| Check Area | What It Covers |
|------------|---------------|
| OWASP LLM Top 10 | v2.0 (2025) — mitigations mapped per applicable category, esp. LLM01 Prompt Injection, LLM06 Excessive Agency, LLM10 Unbounded Consumption |
| Prompt-injection defense | Retrieved/external content treated as data, never instructions (W8); privilege separation between user input and system prompt; model output validated before acting on it; tool-call surface allowlisted |
| Agentic features | Tool-using/autonomous agents additionally checked against the OWASP Agentic list (ASI:2026 — goal hijack, tool misuse, memory/context poisoning): tool permission scoping, inter-agent auth, context integrity |
| Eval harness in CI | Golden-dataset eval suite wired into CI with pass/fail thresholds (faithfulness/hallucination-rate); no eval gate on an AI feature = HIGH finding |
| Hallucination guards | Layered, never single-layer: system-prompt constraints + RAG grounding with citation enforcement + runtime faithfulness monitoring |
| Model pinning + cost budget | Exact model version pinned (never `latest`/unversioned alias); per-request and per-user/session token+cost caps with alerting — unbounded consumption is both a cost and an abuse vector |
| AI-feature UX | Streaming with stop control, deliberation display, scoped uncertainty indicators → delegate to ds-frontend (advisory-handoff: absent → note the UX checklist inline as gap-note) |

### Admin & Support Operability (D10, advisory)

Advisory only — findings here are Category B, never blockers (SKILL-SPEC §15).

| Check Area | What It Covers |
|------------|---------------|
| Admin API surface | Admin-only endpoints (user/config/feature-flag management) gated behind role-checked authz, not just authentication |
| Operator statistics | Business/usage reporting endpoints (dashboards, aggregate metrics) exist and are paginated/rate-limited, not raw DB dumps |
| Export integrity | Periodic report exports (CSV/PDF) use streaming/batched generation, not full-table loads into memory |

### Transactional Messaging (conditional)

**Activate when:** messaging SDK/provider dependency, a consent field in the schema, or reminder-scheduling code is detected (see [ds-blueprint references/detection.md § Step 5](../ds-blueprint/references/detection.md)). Zero checks when absent.

| Check | Rule |
|-------|------|
| Provider credentials | API keys/tokens via secret manager or env, never hardcoded; scoped to transactional-send permission only |
| Retry/idempotency | Send operations use an idempotency key (message/notification ID) to prevent duplicate sends on retry |
| Opt-out honored at send time | Every send checks current opt-out/consent status immediately before dispatch, not just at signup |

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint profile `Integrations` field is `google-workspace` or `apple-ecosystem`. Zero checks when absent.

| Provider | Rule | Area |
|----------|------|------|
| Google | OAuth scope minimization — request only what the integration needs | API |
| Google | Incremental authorization — request additional scopes per-feature | API |
| Google | Verification + Limited Use compliance for sensitive/restricted scopes | API |
| Google | API quota management + exponential backoff on 429 responses | API |
| Google | Refresh token security — rotate on reuse, secure storage | API |
| Apple | Token verification — validate `identityToken` (RS256, `aud`, `iss`, expiry) | API |
| Apple | Private Relay email — use `sub` as stable identifier, not email | API |

## Delegation

**Owns:** api, db, auth, data-pipeline, llm, backend-architecture | **Delegates:** ds-frontend → AI-feature UX (streaming/stop/uncertainty display) | **Receives:** ds-ship → Phase 2 backend pass; ds-productize → billing data model + webhook endpoint security pass; ds-freeze → flag-gate defer-hidden items

## Execution Flow

Setup → Discover → Analyze → [Design/Spec] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

1. Flags → proceed directly. No flags → interactive menu.
2. **IDU:** Profile → {Project Map.Modules, Config.data, Project Map.External, Type + Stack}. Findings({api, db, auth}) → verify + use. Absent → own analysis.
3. Detect project stack (framework, ORM, auth library) by scanning config files + dependencies.
4. Load relevant reference docs by detected scope: [references/rules-api.md](references/rules-api.md), [references/rules-auth.md](references/rules-auth.md), [references/rules-database.md](references/rules-database.md), [references/rules-data-pipeline.md](references/rules-data-pipeline.md).

**Gate:** Scope and mode confirmed. If fails → no flags + no menu response → default `--audit --scope=api,db,auth,data-pipeline` (+`llm` when an AI-provider integration is detected), WARN, announce defaulted scope before proceeding.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → use relevant findings. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. Search for route/endpoint definitions, controller files, middleware.
3. Search for DB schema files (migrations, models, entity definitions).
4. Search for auth configuration (JWT secret usage, session config, OAuth setup).
5. Search for pipeline surfaces: ingest jobs, ETL/transform scripts, schedulers/queues, batch scripts, data-quality checks.
6. Build inventory: endpoints list, tables/models list, auth mechanisms, pipeline stages (ingest → clean → merge → store → serve).

**Gate:** Inventory complete. No backend code found → switch to design mode. If fails → partial inventory → mark missing scopes `not-found` in the inventory, proceed with detected scopes only, note skipped scopes in report.

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

- **Architecture ([references/principles.md §2](references/principles.md)):** every API/service module vs SOLID/GRASP — SRP (handler doing >1 concern), OCP (new endpoint requires editing existing), LSP (subtype changes contract), ISP (controller injecting unused dependency), DIP (handler depending on concrete DB driver instead of repository abstraction), Information Expert (logic away from owning entity), Low Coupling (>7 unrelated peer imports), High Cohesion (one module owning unrelated concerns). Cite principle by name in finding title.
- **Reliability ([references/principles.md §4](references/principles.md)):** flag missing — timeout on every outbound call, retry-with-exponential-backoff (idempotent only — never on POST without idempotency key), circuit breaker on high-volume external deps, health checks (liveness + readiness), idempotency keys on externally-exposed write endpoints, graceful shutdown (drain → close → exit), structured logging (JSON/kv, never raw `print`), fail-fast validation at every boundary.
- **Twelve-Factor ([references/principles.md §3](references/principles.md)):** stateless processes (Factor 6 — no in-memory session/cache survives restart), backing services as URLs from env (Factor 4), config in env (Factor 3), port binding via env-provided value (Factor 7), build/release/run separation (Factor 5), logs to stdout (Factor 11), admin tasks (migrations, seeds) as one-off processes (Factor 12).

Cross-scope dedup: merge findings at same `{file}:{line}`, keep highest severity.

**Gate:** Findings collected. 0 findings → skip to summary. If fails → unanalyzable scope → re-read source once; still unanalyzable (binary, generated-only) → mark `inconclusive` in the findings list, continue, surface in report.

### Phase 4: Design [--design mode]

1. Ask user for requirements (entities, relationships, user roles).
2. Generate per scope:
   - **API:** endpoint list with methods, paths, request/response shapes, status codes
   - **DB:** ER diagram (text), table definitions, index strategy
   - **Auth:** flow diagram (text), token strategy, permission model
3. Present design for user review + iteration.

**Gate:** User approves design or requests changes. If fails → changes requested → apply, re-present; after 3 rounds with no approval → ask "Continue with current / Abort?"; honor choice, record in the generated-artifacts list.

### Phase 5: Spec [--spec mode]

1. **API:** OpenAPI 3.1+ YAML spec from analyzed/designed endpoints (current stable: 3.2.0, Sept 2025 — strictly 3.1-compatible; 4.0 "Moonwalk" has no release date, stay on 3.x).
2. **DB:** Migration files in project's ORM format, or raw SQL.
3. **Auth:** Authentication flow documentation, middleware configuration.

**Gate:** Spec files generated + syntactically valid. If fails → identify invalid spec + error location; attempt auto-correction once; still invalid → write file with inline `# SYNTAX ERROR: {description}` comment at offending line, mark artifact `partial`, surface error.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → forced binary re-prompt; no response → `skipped (no response)` and proceed.

### Phase 7: Summary

```
ds-backend: {OK|WARN|FAIL} | Scope: {api,db,auth,data-pipeline[,llm]} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

- **Audit output:** findings table grouped by scope (API / DB / Auth / Data Pipeline).
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
- OpenAPI spec validates against OpenAPI 3.1+ schema
- Migration files include both `up` + `down` operations
- Auth flows use current best practices (PKCE for all client types, not implicit flow)

| Guard | Rule |
|-------|------|
| W1 | Cite file:line; never assume |
| W2 | Check consumers after modify |
| W3 | Touch only task-required lines |
| W4 | Re-read after gap |
| W5 | Uncertain → lower severity |
| W6 | Verify all phases output |
| W7 | Dedup file:line |
| W8 | No raw shell interpolation |
| W9 | State-exempt — audit is regenerable from source; applied fixes land in the working tree; git is the durable record |
| W10 | Defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered |
| W11 | Every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason |

## Error Recovery

| Situation | Action |
|-----------|--------|
| No backend code found | Switch to design mode, ask what to build |
| Framework not recognized | Use generic patterns, warn about framework-specific optimizations |
| Multiple ORMs / auth libraries | Ask user which is primary |
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
| Stream/queue pipeline (no batch jobs) | Apply pipeline checks to consumers: idempotent handlers, DLQ present, offset/ack semantics stated |
| GraphQL only | Skip REST naming checks, focus on resolver patterns + schema design |
| SQLite project | Skip replication/clustering checks, focus on WAL mode + connection handling |
| No ORM (raw SQL) | Check for SQL injection, parameterized queries |
| Microservices | Ask which service to analyze, check inter-service auth |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
