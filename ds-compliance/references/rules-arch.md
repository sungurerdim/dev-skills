# Rules: Architecture Compliance

Architecture-level compliance rules focused on audit trails, input validation boundaries, information leakage, and dependency security. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Audit & Logging** | ARC-01–04 (2 BLOCKER, 2 CRITICAL) | ~12 |
| **Boundary Security** | ARC-05–08 (1 BLOCKER, 2 CRITICAL, 1 MAJOR) | ~55 |
| **Dependency Security** | ARC-09–11 (1 CRITICAL, 2 MAJOR) | ~95 |

---

## Audit & Logging

### ARC-01 [BLOCKER] Audit Logging for Sensitive Operations
All auth, payment, data deletion, admin, and permission-change operations must produce audit log entries.
- **Detect:** Auth endpoints (login, logout, password reset, MFA) without structured log output. Payment/billing endpoints without transaction logging. User data deletion without audit record. Admin actions without who/what/when trail
- **Fix:** Add structured audit log for every sensitive operation: `{timestamp, user_id, action, resource, ip, user_agent, result}`. Use append-only storage (not deletable by application). Separate audit logs from application logs
- **Source:** SOC 2 Type II, GDPR Art. 30, HIPAA §164.312(b)

### ARC-02 [BLOCKER] No Sensitive Data in Logs
Logs must never contain passwords, tokens, credit card numbers, PII, or secrets.
- **Detect:** `log.*password`, `log.*token`, `log.*secret`, `log.*credit_card`, `console.log(req.body)` (may contain credentials), `logger.info(f"User {user}")` where user object contains PII
- **Fix:** Redact sensitive fields before logging. Use allowlists (log only known-safe fields), not blocklists. Mask PII: `email: j***@example.com`. Never log full request/response bodies — log sanitized summaries
- **Source:** OWASP Logging Cheat Sheet, GDPR Art. 5(1)(f)

### ARC-03 [CRITICAL] Structured Logging Format
Logs must be structured (JSON) with consistent fields for security analysis.
- **Detect:** `print()` or `console.log()` for application events (not debug). Unstructured log messages without timestamp, level, or context. Mixed log formats across the application
- **Fix:** Use structured logging: `{timestamp, level, message, service, trace_id, user_id, ...}`. Python: `structlog` or `logging` with JSON formatter. Node: `pino` or `winston`. Go: `slog` (stdlib). Include correlation/trace ID for request tracing
- **Source:** 12-Factor App (Treat logs as event streams)

### ARC-04 [CRITICAL] Log Retention Policy
Application must define and enforce log retention periods.
- **Detect:** No log rotation configured. Logs growing unbounded. No retention policy documented. Log files older than 90 days without archival strategy
- **Fix:** Configure rotation (daily/size-based). Define retention: access logs 90 days, audit logs per regulatory requirement (GDPR: as long as necessary, HIPAA: 6 years, SOX: 7 years). Archive to cold storage after active period. Document in ops runbook
- **Source:** GDPR Art. 5(1)(e), HIPAA §164.530(j)

---

## Boundary Security

### ARC-05 [BLOCKER] Input Validation at Trust Boundaries
All external input (API requests, file uploads, webhooks, queue messages) must be validated at the entry point.
- **Detect:** Controller/handler functions that pass request data directly to business logic without validation. Missing schema validation middleware. `req.body.field` used without type/format/range checks
- **Fix:** Validate at the boundary: type, format, range, length, allowed values. Use schema validation: `zod` (Node), `pydantic` (Python), struct tags (Go), `jakarta.validation` (Java). Reject invalid input with 400, never attempt to sanitize and proceed
- **Source:** OWASP A03:2021 (Injection)

### ARC-06 [CRITICAL] Error Response Without Stack Traces
Production error responses must not expose stack traces, internal paths, or framework details.
- **Detect:** `res.status(500).send(error.stack)`, `DEBUG=True` in production config, `app.use(errorHandler)` that sends full error to client, `traceback.print_exc()` in API handlers, framework default error pages in production
- **Fix:** Return generic error with correlation ID: `{error: "Internal error", reference: "abc-123"}`. Log full details server-side with the same correlation ID. Disable debug mode in production. Custom error handler that maps exceptions to safe HTTP responses
- **Source:** OWASP A04:2021 (Insecure Design)

### ARC-07 [CRITICAL] Fail-Closed Authorization
Authorization failures must deny access by default, not grant it.
- **Detect:** Auth middleware that returns `next()` on error (fail-open). Missing `else` clause in permission checks. Default case in role switch that allows access. `catch` blocks that continue request processing after auth failure
- **Fix:** Default deny: if auth check fails for any reason (error, timeout, missing data), return 401/403. Never fall through to the protected resource. Use allowlists for permitted roles, not blocklists for denied roles
- **Source:** OWASP A01:2021 (Broken Access Control)

### ARC-08 [MAJOR] Separation of Auth from Business Logic
Authentication and authorization logic must be isolated from business logic.
- **Detect:** Auth checks (`if user.role === 'admin'`) scattered inside business functions. Permission logic mixed with data processing. Direct database role queries inside service methods
- **Fix:** Centralize auth in middleware/decorators/interceptors. Business logic receives already-authorized context. Use policy-based authorization (e.g., RBAC/ABAC middleware). Auth decisions happen once at the boundary, not repeatedly in business code
- **Source:** Clean Architecture, OWASP

---

## Dependency Security

### ARC-09 [CRITICAL] Known Vulnerability Check
Dependencies must be checked for known vulnerabilities.
- **Detect:** No `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, or equivalent in CI pipeline. Lock files with advisories. Dependencies with known CVEs
- **Fix:** Add vulnerability scanning to CI: `npm audit --production`, `pip-audit`, `cargo audit`, `govulncheck ./...`. Block merges on CRITICAL/HIGH findings. Set up automated dependency update tools (Dependabot, Renovate)
- **Source:** OWASP A06:2021 (Vulnerable Components)

### ARC-10 [MAJOR] Dependency Freshness
Dependencies should not be severely outdated (major versions behind).
- **Detect:** Lock file with dependencies 2+ major versions behind latest. Packages with known end-of-life dates. Framework versions past their support window
- **Fix:** Update dependencies regularly (monthly cycle). Prioritize: security patches immediately, minor versions weekly, major versions with testing. Use `npm outdated`, `pip list --outdated`, `go list -m -u all`
- **Source:** Software supply chain security best practices

### ARC-11 [MAJOR] Minimal Dependency Surface
Avoid unnecessary dependencies that increase attack surface.
- **Detect:** Dependencies used for trivial functionality (left-pad pattern). Packages with 0 maintenance (no updates in 2+ years, archived repos). Multiple packages for the same purpose (2 HTTP clients, 2 date libraries)
- **Fix:** Evaluate each dependency: can stdlib do this? Is the package maintained? How many transitive deps does it add? Remove unused deps (`depcheck`, `pip-extra-reqs`). Prefer well-maintained, minimal packages
- **Source:** Supply chain security, NIST SSDF
