# Scope Detail: API, Database, Data Pipeline, Auth, LLM, and Conditional Checks

Loaded by `/ds-backend` Phase 1 per the scope-resolution table in SKILL.md. Full check-area tables for every scope, plus the cross-cutting checks that activate on their own signal independent of `--scope`.

## API [Product DX]

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
| Error-channel decision (D4, advisory) | Production crash/error reporting has an explicit decision: consent-based opt-in PII-free aggregate channel (error class + app version + counter only — see ds-compliance crosscheck), or a documented acceptance of "support-mail blindness" as a risk. Missing entirely -> advisory finding, never a blocker |
| Ecosystem openness (A11, advisory) | Webhook emission surface (versioned payload, HMAC signature verified constant-time, timestamp replay-tolerance check — industry convention ~5 min — `webhook-id` as consumer idempotency key, retry/backoff — aligned to the [Standard Webhooks](https://www.standardwebhooks.com/) spec where feasible) for state-change events; standard-format export endpoints (ICS/CSV/JSON, not just proprietary JSON) for user data; embeddable-surface posture (widget/iframe API) where the product has a natural embed use case. Product holds user data with no standard export path -> advisory portability finding (see ds-compliance crosscheck); never a blocker |
| Security | OWASP API Security Top 10 (2023 edition — current as of 2026) checks |
| SLO baseline (advisory) | Critical user journeys have RED metrics (rate/errors/duration) exposed and an SLO defined; error-budget policy + burn-rate alerting delegated to ds-devops (absent → gap-note, never a blocker) |
| Destructive-operation response integrity | Multi-scope destructive endpoints (reset/delete/purge) are split into clearly-named, narrowly-scoped, idempotent operations behind escalating confirmation — never one ambiguous "clear all". Every destructive response compares expected-vs-actual outcome (e.g. `{deleted: 0}` when records were expected) and returns a warning/conflict status, never a bare 200/success, on divergence — silent false-success on a no-op delete is CRITICAL |

## Database

| Check Area | What It Covers |
|------------|---------------|
| Schema design | Normalization, naming conventions, data types |
| Indexing | Missing indexes, over-indexing, composite order, GIN/GiST/BRIN for advanced cases |
| Migrations | Expand-contract pattern, safe vs dangerous ops, rollback tested, CI migration lint (Squawk) |
| Query patterns | N+1 detection, EXPLAIN ANALYZE review, `pg_stat_statements`, connection pooling |
| Backup | 3-2-1 rule, WAL archiving, restore testing |
| Restore-drill proof (D3, advisory) | Backup existing is not resilience — require a documented restore runbook + evidence of ≥1 executed end-to-end drill (worst case: total account/environment loss, restored to a clean target). Missing evidence -> advisory finding "backup exists, restore unproven — run a drill and record the runbook" (never a blocker) |
| Data privacy | PII classification, encryption at rest, GDPR right-to-erasure, retention |
| Local cache reconstructibility (conditional — offline-first/cached-client architecture) | Every client-side cache/store classified as server-native (recoverable via re-fetch), derived (recoverable by re-parsing another artifact), or justified-transient (device-only, documented reason) — an unclassified local-only store that can't be reconstructed after a device wipe is a data-loss risk, flag HIGH. Cross-device write conflicts resolve via server-side ordering (ETag/If-Match/revision), never device wall-clock last-write-wins |
| Bulk restore/import safety | Bulk write/restore/import/migration operations enqueue in bounded batches (drain-before-next-batch) through the normal write pipeline, never exceeding its hard queue-depth cap; default mode is dry-run (diff of new-vs-existing, no writes) with an explicit force/second-confirm flag required for the destructive path |
| Schema vs. form-layer enforcement | A new required-field/business-rule constraint on data that also flows through a lenient boundary-schema parse (legacy records, external sync, historical imports) is enforced at the write/form (application) layer, not added to the boundary schema validator — a stricter schema would reject pre-existing valid records on read |

## Data Pipeline

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
| Sync round-trip integrity | Every field synced with an external system has: an internal write path, an outbound field mapping, an inbound field mapping, and a schema/field-list constant referencing it — plus a `roundtrip` regression test (write→sync-out→reload→sync-in→assert). Flag any synced field missing one of the four or its regression test — the sneakiest bug class here shows data, appears to sync, then silently drops the field only after reload |
| Retry/outbox semantics | Retry-queue results are three-valued: succeeded / failed (real error, increments attempt counter, eventually quarantines) / not-ready (precondition unmet — auth, scope, flag — does NOT increment attempt counter). Flag any retry loop with only success/failure that would quarantine a job purely because a precondition was temporarily unmet |

## Auth

| Check Area | What It Covers |
|------------|---------------|
| Flow design | OAuth2 / OIDC correctness, PKCE required for all client types per RFC 9700 |
| Token handling | JWT signing (RS256/ES256), expiry, refresh rotation, storage (never localStorage) |
| Session management | Cookie security (HttpOnly, Secure, SameSite), CSRF, session fixation |
| RBAC | Role/permission model, authorization middleware, least privilege |
| Password security | Argon2id (primary), NIST 800-63B policy (min length, breached check, no complexity rules) |
| Social login | Provider integration, account linking, `sub` as stable identifier — used everywhere identity is a key: cross-device data binding, audit-log attribution, encryption derivation, never the mutable email address |
| MFA | TOTP, WebAuthn / passkeys, recovery codes (hashed, single-use), SMS OTP deprecation |
| API keys | Prefixed keys, hash-only storage, scoped permissions, rotation support |
| Crypto-enforced separation of duties (conditional — active when a sensitive-data encryption key is distributed to a subset of roles) | Recipient set for the key derives from a static seed/allowlist, never from a generic `Role.can()`/`hasPermission()` call — such helpers commonly short-circuit true for admin, silently handing the key to the role the design meant to exclude. Flag any key-distribution path that calls a general permission-check function instead of a dedicated allowlist |

## LLM & AI Features [conditional — active only when an LLM/AI provider integration is detected (SDK import, API client, model config) or `--scope=llm` is passed]

| Check Area | What It Covers |
|------------|---------------|
| OWASP LLM Top 10 | v2.0 (2025) — mitigations mapped per applicable category, esp. LLM01 Prompt Injection, LLM06 Excessive Agency, LLM10 Unbounded Consumption |
| Prompt-injection defense | Retrieved/external content treated as data, never instructions (W8); privilege separation between user input and system prompt; model output validated before acting on it; tool-call surface allowlisted |
| Agentic features | Tool-using/autonomous agents additionally checked against the OWASP Agentic list (ASI:2026 — goal hijack, tool misuse, memory/context poisoning): tool permission scoping, inter-agent auth, context integrity |
| Eval harness in CI | Golden-dataset eval suite wired into CI with pass/fail thresholds (faithfulness/hallucination-rate); no eval gate on an AI feature = HIGH finding |
| Hallucination guards | Layered, never single-layer: system-prompt constraints + RAG grounding with citation enforcement + runtime faithfulness monitoring |
| Model pinning + cost budget | Exact model version pinned (never `latest`/unversioned alias); per-request and per-user/session token+cost caps with alerting — unbounded consumption is both a cost and an abuse vector |
| AI-feature UX | Streaming with stop control, deliberation display, scoped uncertainty indicators → delegate to ds-frontend (present → delegate; absent → note the UX checklist inline as gap-note) |

## Admin & Support Operability (D10, advisory)

Advisory only — findings here are Category B, never blockers.

| Check Area | What It Covers |
|------------|---------------|
| Admin API surface | Admin-only endpoints (user/config/feature-flag management) gated behind role-checked authz, not just authentication |
| Operator statistics | Business/usage reporting endpoints (dashboards, aggregate metrics) exist and are paginated/rate-limited, not raw DB dumps |
| Export integrity | Periodic report exports (CSV/PDF) use streaming/batched generation, not full-table loads into memory |
| Audit-log undo/restore | If an audit/change-log entry already stores the full before-state of a mutation, verify a corresponding single-record "undo/restore this entry" action exists (read before-state → recreate/rewrite, with conflict handling). An audit trail with full state capture but no restore path is a missed high-value/low-risk feature — flag MEDIUM, not a blocker |

## Multi-Tenant / Org Configuration (conditional)

**Activate when:** the project has an org/workspace/team concept with more than one config-affecting or authorization layer (detected via a multi-tenant schema pattern, an `organizations`/`workspaces` table joined to user settings, or an admin-settings/member-role UI). Zero checks when absent.

| Check | Rule |
|-------|------|
| Config layering | Config split into four ownership layers with defined precedence: deployment bootstrap (code, never runtime-writable) → system defaults (code, read-only fallback) → org/workspace config (admin-writable, shared) → per-user preferences (personal). Every enforceable key supports an explicit lock/override flag at the org layer (`{default, enforced}`) — `enforced=true` beats the user's personal preference deterministically. Flag a flat config surface mixing deployment secrets, org-wide settings, and per-user preferences with no override precedence |
| Resource ownership & entitlement | Org/resource "owner" is an explicit, transferable designation field — never inferred from creator identity or current payer (subscription receipts are often non-transferable, which would lock the whole org to one person's billing status). Removing/deleting a designated owner without a prior mandatory transfer is blocked (sole-owner guard). Paid-tier entitlement anchors to a stable org/workspace ID, not the purchasing individual's account — flag any entitlement check keyed on a personal user ID for a multi-seat product |
| Authorization fan-out SSOT | A single grant/revoke action (assign or remove a role/membership) updates every authorization layer it touches — app-level RBAC, storage/file ACL, and any sensitive-data encryption-key access — in one atomic path. Flag any system where RBAC, storage sharing, and crypto-key distribution for the same grant are configured through separate, independently-callable admin actions |

## Transactional Messaging (conditional)

**Activate when:** messaging SDK/provider dependency, a consent field in the schema, or reminder-scheduling code is detected — those three signals are the whole activation contract, evaluated here. Zero checks when absent. `/ds-blueprint` present → delegate for its fuller provider-signal catalog; absent → the three signals above stand alone, no capability lost.

| Check | Rule |
|-------|------|
| Provider credentials | API keys/tokens via secret manager or env, never hardcoded; scoped to transactional-send permission only |
| Retry/idempotency | Send operations use an idempotency key (message/notification ID) to prevent duplicate sends on retry |
| Opt-out honored at send time | Every send checks current opt-out/consent status immediately before dispatch, not just at signup |

## A9 — Google / Apple Ecosystem Rules (conditional)

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
