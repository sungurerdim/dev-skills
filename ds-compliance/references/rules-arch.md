# Rules: Architecture Compliance

Architecture-level compliance rules focused on audit trails, input validation boundaries, information leakage, and dependency security. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Audit & Logging** | ARC-01–04 (2 BLOCKER, 2 CRITICAL) | ~12 |
| **Boundary Security** | ARC-05–08 (1 BLOCKER, 2 CRITICAL, 1 HIGH) | ~55 |
| **Dependency Security** | ARC-09–11 (1 CRITICAL, 2 HIGH) | ~95 |

---

## Audit & Logging

### ARC-01 [BLOCKER] Audit Logging for Sensitive Operations
All auth, payment, data deletion, admin, and permission-change operations must produce audit log entries.
- **Detect:** Auth endpoints (login, logout, password reset, MFA) without structured log output. Payment/billing endpoints without transaction logging. User data deletion without audit record. Admin actions without who/what/when trail
- **Fix:** Add structured audit log for every sensitive operation: `{timestamp, user_id, action, resource, ip, user_agent, result}`. Use append-only storage (not deletable by application). Separate audit logs from application logs
- **Impact:** A sensitive operation with no audit trail leaves incident response and regulatory inquiries (GDPR Art. 30, HIPAA) unable to reconstruct who did what, when.
- **Source:** SOC 2 Type II, GDPR Art. 30, HIPAA §164.312(b)

### ARC-02 [BLOCKER] No Sensitive Data in Logs
Logs must never contain passwords, tokens, credit card numbers, PII, or secrets.
- **Detect:** `log.*password`, `log.*token`, `log.*secret`, `log.*credit_card`, `console.log(req.body)` (may contain credentials), `logger.info(f"User {user}")` where user object contains PII
- **Fix:** Redact sensitive fields before logging. Use allowlists (log only known-safe fields), not blocklists. Mask PII: `email: j***@example.com`. Never log full request/response bodies — log sanitized summaries
- **Impact:** Sensitive values written to logs leak through log aggregators, dashboards, and support tooling — a log-access breach becomes a credential/PII breach.
- **Source:** OWASP Logging Cheat Sheet, GDPR Art. 5(1)(f)
- **Cross-ref:** [PRV-05](rules-compliance.md) (canonical, privacy scope) covers the same concern with a fuller PII-pattern table — when both `security`/`arch` and `privacy` scopes run together, report once under PRV-05.

### ARC-03 [CRITICAL] Structured Logging Format
Logs must be structured (JSON) with consistent fields for security analysis.
- **Detect:** `print()` or `console.log()` for application events (not debug). Unstructured log messages without timestamp, level, or context. Mixed log formats across application
- **Fix:** Use structured logging: `{timestamp, level, message, service, trace_id, user_id, ...}`. Python: `structlog` or `logging` with JSON formatter. Node: `pino` or `winston`. Go: `slog` (stdlib). Include correlation/trace ID for request tracing
- **Impact:** Unstructured logs can't be machine-parsed at scale — security analysis, alerting, and incident correlation across services becomes manual and slow, exactly when speed matters most.
- **Source:** 12-Factor App (Treat logs as event streams)

### ARC-04 [CRITICAL] Log Retention Policy
Application must define and enforce log retention periods.
- **Detect:** No log rotation configured. Logs growing unbounded. No retention policy documented. Log files older than 90 days without archival strategy
- **Fix:** Configure rotation (daily/size-based). Define retention: access logs 90 days, audit logs per regulatory requirement (GDPR: as long as necessary, HIPAA: 6 years, SOX: 7 years). Archive to cold storage after active period. Document in ops runbook
- **Impact:** Unbounded log growth exhausts disk/storage and can silently violate regulatory retention limits (GDPR Art. 5(1)(e)) in either direction — kept too long or deleted before required.
- **Source:** GDPR Art. 5(1)(e), HIPAA §164.530(j)

---

## Boundary Security

### ARC-05 [BLOCKER] Input Validation at Trust Boundaries
All external input (API requests, file uploads, webhooks, queue messages) must be validated at entry point.
- **Detect:** Controller/handler functions that pass request data directly to business logic without validation. Missing schema validation middleware. `req.body.field` used without type/format/range checks
- **Fix:** Validate at boundary: type, format, range, length, allowed values. Use schema validation: `zod` (Node), `pydantic` (Python), struct tags (Go), `jakarta.validation` (Java). Reject invalid input with 400, never attempt to sanitize and proceed
- **Impact:** Unvalidated input reaching business logic is the root cause behind most injection, deserialization, and data-corruption vulnerabilities — validating downstream is validating too late.
- **Source:** OWASP A05:2025 (Injection)

### ARC-06 [CRITICAL] Error Response Without Stack Traces
Production error responses must not expose stack traces, internal paths, or framework details.
- **Detect:** `res.status(500).send(error.stack)`, `DEBUG=True` in production config, `app.use(errorHandler)` that sends full error to client, `traceback.print_exc()` in API handlers, framework default error pages in production
- **Fix:** Return generic error with correlation ID: `{error: "Internal error", reference: "abc-123"}`. Log full details server-side with same correlation ID. Disable debug mode in production. Custom error handler that maps exceptions to safe HTTP responses
- **Impact:** A stack trace or internal path in a production error response hands an attacker the internal file layout, framework version, and code structure needed to craft a targeted exploit.
- **Source:** OWASP A06:2025 (Insecure Design)

### ARC-07 [CRITICAL] Fail-Closed Authorization
Authorization failures must deny access by default, not grant it.
- **Detect:** Auth middleware that returns `next()` on error (fail-open). Missing `else` clause in permission checks. Default case in role switch that allows access. `catch` blocks that continue request processing after auth failure
- **Fix:** Default deny: if auth check fails for any reason (error, timeout, missing data), return 401/403. Never fall through to protected resource. Use allowlists for permitted roles, not blocklists for denied roles
- **Impact:** Fail-open authorization turns any bug, timeout, or unexpected error in the auth path into an access-control bypass — the failure mode itself becomes the vulnerability.
- **Source:** OWASP A01:2025 (Broken Access Control)

### ARC-08 [HIGH] Separation of Auth from Business Logic
Authentication and authorization logic must be isolated from business logic.
- **Detect:** Auth checks (`if user.role === 'admin'`) scattered inside business functions. Permission logic mixed with data processing. Direct database role queries inside service methods
- **Fix:** Centralize auth in middleware/decorators/interceptors. Business logic receives already-authorized context. Use policy-based authorization (e.g., RBAC/ABAC middleware). Auth decisions happen once at boundary, not repeatedly in business code
- **Impact:** Auth checks scattered through business logic get missed on new routes and drift out of sync — centralized auth is the only form that's provably complete.
- **Source:** Clean Architecture, OWASP

---

## Dependency Security

### ARC-09 [CRITICAL] Known Vulnerability Check
Dependencies must be checked for known vulnerabilities.
- **Detect:** No `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, or equivalent in CI pipeline. Lock files with advisories. Dependencies with known CVEs
- **Fix:** Add vulnerability scanning to CI: `npm audit --production`, `pip-audit`, `cargo audit`, `govulncheck ./...`. Block merges on CRITICAL/HIGH findings. Set up automated dependency update tools (Dependabot, Renovate)
- **Impact:** An unscanned dependency with a known CVE ships a documented, publicly exploitable vulnerability straight into production.
- **Source:** OWASP A03:2025 (Software Supply Chain Failures)

### ARC-10 [HIGH] Dependency Freshness
Dependencies should not be severely outdated (major versions behind).
- **Detect:** Lock file with dependencies 2+ major versions behind latest. Packages with known end-of-life dates. Framework versions past their support window
- **Fix:** Update dependencies regularly (monthly cycle). Prioritize: security patches immediately, minor versions weekly, major versions with testing. Use `npm outdated`, `pip list --outdated`, `go list -m -u all`
- **Impact:** Severely outdated dependencies accumulate unpatched vulnerabilities and eventually block security updates entirely once the maintainer stops backporting fixes to that major version.
- **Source:** Software supply chain security best practices

### ARC-11 [HIGH] Minimal Dependency Surface
Avoid unnecessary dependencies that increase attack surface.
- **Detect:** Dependencies used for trivial functionality (left-pad pattern). Packages with 0 maintenance (no updates in 2+ years, archived repos). Multiple packages for same purpose (2 HTTP clients, 2 date libraries)
- **Fix:** Evaluate each dependency: can stdlib do this? Is package maintained? How many transitive deps does it add? Remove unused deps (`depcheck`, `pip-extra-reqs`). Prefer well-maintained, minimal packages
- **Impact:** Every extra dependency is an extra supply-chain trust relationship and attack surface — a single unmaintained transitive package can compromise the whole build.
- **Source:** Supply chain security, NIST SSDF
