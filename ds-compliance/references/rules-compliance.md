# Rules: Security & Privacy

> **Currency rule:** the dated facts in this file (policy names, thresholds, fines, dates, review guidelines) are a verified seed map, never the authority. At run time, re-verify any fact that affects a finding against the live official source (store guideline page, regulator text, platform changelog); the live source wins on conflict. Web access unavailable → apply the seed and mark the finding `unverified-currency`.

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | SEC-01–14 (4 BLOCKER, 5 CRITICAL, 5 HIGH) | ~20 |
| **Privacy** | PRV-01–05, PRV-26–45, PRV-56, PRV-59, PRV-60 (3 BLOCKER, 2 CRITICAL, 14 HIGH, 9 MEDIUM) | ~185 |
| **Regulatory Compliance** | PRV-06–19, PRV-21–25, PRV-46–55, PRV-57, PRV-58 (15 BLOCKER, 9 CRITICAL, 7 HIGH) | ~461 |
| **Advisory (Non-Blocking)** | PRV-20 (1 ADVISORY) | ~841 |

Every rule below carries an `applies_when:` line under its heading — a signal condition from [../../core/signal-inventory.md](../../core/signal-inventory.md) (or `always`) gating whether the rule is evaluated for a given project. `unknown` signal values never silently exclude a rule — the scan still runs and reports the signal as unresolved.

---

## Security

Baseline: OWASP ASVS 5.0.0 (May 2025 — ~350 requirements, 17 categories). OSS DAST tools (ZAP, Nikto) still emit 4.0.3-tagged findings as of mid-2026 — label tool output with the tool's ASVS version; never present 4.0.3 tool findings as ASVS 5.0 coverage.

### SEC-01 [BLOCKER] Secure Credential Storage
applies_when: always
Credentials, tokens, and secrets must not be in plaintext files or unencrypted storage.
- **Detect:**
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git (not in `.gitignore`)
  - Search: passwords/tokens in config files, database connection strings with embedded credentials
  - Plaintext secrets in `application.yml`, `settings.py`, `config/*.json`
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Use environment variables loaded at runtime. Use secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Doppler). Add `.env` to `.gitignore`. For Docker: use secrets, not ENV in Dockerfile
- **Impact:** A plaintext or committed credential is readable by anyone with repo/filesystem access, including in git history long after the file appears fixed.
- **Source:** OWASP A07:2025 (Authentication Failures)

### SEC-02 [BLOCKER] No Hardcoded Credentials
applies_when: always
Zero secrets in source code.
- **Detect:**
  - Search: `apiKey\s*[:=]`, `api_key\s*[:=]`, `secret\s*[:=]`, `password\s*[:=]`, `bearer\s`, `sk-[a-zA-Z0-9]`, `AKIA[A-Z0-9]`, base64 patterns >20 chars in string literals
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Move to environment variables or secret manager. Add to `.gitignore`. Use server-side proxy for third-party API keys
- **Impact:** A hardcoded secret ships inside the source and leaks to every clone, fork, and build artifact — rotation requires a code change, not just a config change.
- **Source:** OWASP A07:2025 (Authentication Failures)

### SEC-03 [BLOCKER] Debug Mode Off in Production
applies_when: always
No debug features exposed in production builds.
- **Detect:**
  - Python: `DEBUG = True` in settings, `FLASK_DEBUG=1`
  - Node: missing `NODE_ENV=production`, `console.log` in production paths
  - Go: `debug` flags in production configs
  - Java/Kotlin: `debug=true` in application.properties
  - Stack traces exposed in error responses
- **Fix:** Environment-based config. Strip debug code in production builds. Never expose stack traces to clients
- **Impact:** Debug mode in production exposes stack traces, internal routes, and in some frameworks a live code-execution console directly to attackers.
- **Source:** OWASP A02:2025 (Security Misconfiguration)

### SEC-04 [BLOCKER] TLS Enforced
applies_when: api≠none or deploy≠none
All connections over HTTPS. No plaintext HTTP in production.
- **Detect:**
  - Search: `http://` URLs in source (excluding localhost/127.0.0.1/10.0/192.168)
  - No HTTPS redirect configuration
  - Missing HSTS headers
- **Fix:** Redirect HTTP to HTTPS. Set HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`. Use TLS 1.2+ only
- **Impact:** Plaintext HTTP lets any network intermediary read or alter traffic in transit — credentials, session tokens, and personal data travel exposed.
- **Source:** OWASP A04:2025 (Cryptographic Failures)

### SEC-05 [CRITICAL] Input Validation & Injection Prevention
applies_when: always
All user input validated and sanitized. No raw interpolation in queries or commands.
- **Detect:**
  - Search: string concatenation in SQL queries (`"SELECT.*" +`, f-strings in queries, template literals in SQL)
  - Raw user input in shell commands (`exec`, `os.system`, `child_process.exec`)
  - No input validation middleware/decorators on route handlers
  - Search: `eval(`, `Function(`, `innerHTML =` with user input
- **Fix:** Parameterized queries (prepared statements). Input validation with schemas (Zod, Pydantic, Joi). Never interpolate user input into SQL/shell/HTML. Use ORM for queries
- **Impact:** SQL injection is still #1 web vulnerability. Single unparameterized query = full database compromise
- **Source:** OWASP A05:2025 (Injection)

### SEC-06 [CRITICAL] Strong Cryptography
applies_when: always
AES-256-GCM symmetric. No MD5/SHA-1 for security. No custom crypto.
- **Detect:**
  - Search: `MD5`, `SHA1`, `SHA-1` in non-checksum context, `ECB` mode, `DES`, `RC4`, hardcoded IV/nonce
  - Custom crypto implementations
  - Weak password hashing (plain SHA-256 without salt/iteration)
- **Fix:** Use platform crypto libraries. Password hashing: bcrypt/scrypt/argon2. Encryption: AES-256-GCM. Use random IV/nonce per operation
- **Impact:** Weak or custom cryptography (MD5/SHA-1, ECB mode, hand-rolled ciphers) is breakable with known techniques and protects nothing against a motivated attacker.
- **Source:** OWASP A04:2025 (Cryptographic Failures)

### SEC-07 [CRITICAL] Secure HTTP Headers
applies_when: api≠none or ui=web
Security headers set on all responses.
- **Detect:**
  - No `helmet` (Express), `django-csp` (Django), security middleware
  - Missing any of the 2026 baseline header set for HTTPS sites: HSTS, Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, CSP `frame-ancestors` (or legacy X-Frame-Options)
- **Fix:** Use security middleware (helmet, django-secure, secure-headers). Set the six-header baseline: HSTS, CSP (strict — see WEB-01), X-Content-Type-Options: nosniff, Referrer-Policy: strict-origin-when-cross-origin, Permissions-Policy (deny unused features), `frame-ancestors 'none'` (preferred over X-Frame-Options: DENY). Add the cross-origin isolation trio (COOP/COEP/CORP) only when the app needs SharedArrayBuffer/high-resolution timers — not as a blanket default
- **Impact:** Missing security headers enable XSS, clickjacking, and MIME-sniffing attacks
- **Source:** OWASP Secure Headers Project

### SEC-08 [CRITICAL] Supply Chain Security
applies_when: always
Dependencies audited, versions pinned, lockfile committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile (package-lock.json, yarn.lock, pnpm-lock.yaml, Pipfile.lock, poetry.lock, go.sum) in git
- **Fix:** Pin exact versions. Commit lockfiles. Run `npm audit` / `pip audit` / `safety check` regularly
- **Impact:** An unpinned dependency can silently pull a compromised or backdoored version on the next install — the exact supply-chain vector behind several major incidents.
- **Source:** OWASP A03:2025 (Software Supply Chain Failures)

### SEC-09 [CRITICAL] Server-Side Auth & Authorization
applies_when: auth≠none
Auth validated server-side on every request. No client-only auth checks.
- **Detect:**
  - API endpoints without auth middleware
  - Authorization based on client-provided role/permission without server verification
  - Missing token validation on protected routes
- **Fix:** Auth middleware on all protected routes. Validate JWT/session server-side. Check permissions per resource, not just authentication. Use RBAC or ABAC
- **Impact:** A client-asserted role or permission is trivially forged — without server-side verification, any user can claim to be an admin.
- **Source:** OWASP A01:2025 (Broken Access Control)

### SEC-10 [HIGH] Session Management
applies_when: auth≠none
Secure session configuration. Token rotation. Proper logout.
- **Detect:**
  - Session cookies without `Secure`, `HttpOnly`, `SameSite` flags
  - No token expiry or rotation
  - Logout doesn't invalidate server-side session
  - Long-lived tokens without refresh mechanism
- **Fix:** Set cookie flags: `Secure; HttpOnly; SameSite=Strict`. Short-lived access tokens (15min) + refresh token rotation. Server-side session invalidation on logout. Regenerate session ID after auth state change
- **Impact:** A session with no rotation or secure flags stays hijackable for its full lifetime, and a logout that doesn't invalidate the server-side session leaves a stolen token valid after the user thinks they're signed out.
- **Source:** OWASP Session Management Cheat Sheet

### SEC-11 [HIGH] Rate Limiting (API/Web)
applies_when: api≠none
API endpoints protected against abuse.
- **Detect:**
  - No rate limiting middleware on auth endpoints (login, register, password reset)
  - No rate limiting on API endpoints
  - No brute-force protection
- **Fix:** Rate limit auth endpoints (5-10 req/min). General API rate limiting (100-1000 req/min per user). Use `express-rate-limit`, `slowapi`, or API gateway rate limiting. Return `429 Too Many Requests` with `Retry-After` header
- **Impact:** Unprotected auth endpoints enable credential stuffing and brute-force attacks
- **Source:** OWASP API Security Top 10
- **Cross-ref:** Same check as [NET-05](rules-network.md) (canonical, network scope) — when both `security` and `network` scopes run together, report once under NET-05.

### SEC-12 [HIGH] License & IP Contamination
applies_when: always
AI assistants can emit near-verbatim third-party or copyleft code without attribution.
- **Detect:**
  - No license / SCA scan on AI-assisted PRs
  - Copyleft (GPL/AGPL) code entering a permissively-licensed project
  - Large verbatim blocks of unknown provenance
  - AI assistance not recorded where org or licensing policy requires it
- **Fix:** Run a license/SCA scan (FOSSA, ScanCode) on AI-assisted PRs; flag copyleft entering permissive code. Verify provenance of large verbatim AI output before merge; prefer generating from your own interfaces. Record AI assistance where policy requires an authorship/provenance note.
- **Impact:** In *Doe v. GitHub* most claims were dismissed but an open-source-license-violation claim survives; the EU AI Act (Reg. 2024/1689) GPAI transparency duties applied 2 Aug 2025; general enforcement and penalties apply 2 Aug 2026, while high-risk obligations shifted under the Digital Omnibus — timeline in PRV-21.
- **Source:** [Doe v. GitHub case updates](https://githubcopilotlitigation.com/case-updates.html); [EU AI Act (EC)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

### SEC-13 [HIGH] Identity/Session Storage Tier & Token-Refresh Re-hydration
applies_when: auth≠none
Session/identity data used for a boot-time decision (per-account storage selection, cache partitioning) persists in cold-start-durable storage, not storage that's cleared on process/tab restart.
- **Detect:**
  - Identity/auth-claim data (a stable user ID, session claims) required at boot for a storage/partition decision is kept in session-scoped storage (cleared on tab/process restart) rather than persistent storage
  - A token-refresh flow that renews only the access token without re-fetching/re-validating the identity claims the app's boot logic depends on
- **Fix:** Move boot-critical identity/session data to storage that survives a cold start (persistent local storage, not session-scoped); make token-refresh re-hydrate the full identity payload, not just the access token.
- **Impact:** Mobile WebViews and app-kill scenarios routinely wipe session-scoped storage — the real-world failure mode is "logged in, no data": the app boots, authentication looks fine, but the wrong (or no) data partition loads because the boot-time identity read came back empty. A refresh path that renews the token but never re-hydrates identity reintroduces the same bug after every refresh.
- **Source:** Mobile WebView storage-lifetime documentation (session vs. persistent storage semantics)

### SEC-14 [HIGH] Dependency License Compliance Scanning
applies_when: always
Every dependency's license is known, scanned automatically, and compatible with the project's distribution model.
- **Detect:**
  - No SBOM (SPDX/CycloneDX) generated and no automated license scanner (FOSSA, Snyk, `license-checker`, ScanCode) configured in CI/pre-commit
  - GPL/AGPL-licensed dependency present in a proprietary or permissively-licensed distribution with no compliance review recorded
  - LGPL dependency statically linked into proprietary code (dynamic linking required to avoid copyleft propagation)
  - Apache 2.0 dependency distributed without its NOTICE file; MIT/BSD dependency distributed without copyright/license text preserved
- **Fix:** Generate and maintain an SBOM (SPDX or CycloneDX format); wire a license scanner into CI/pre-commit that fails the build on a disallowed license; use LGPL dependencies via dynamic linking only; preserve NOTICE/copyright/license files in every distribution; document any borderline license decision before merge.
- **Impact:** An unreviewed GPL/AGPL dependency in a proprietary build, or a statically-linked LGPL dependency, converts a routine install into a license violation discoverable by the rights-holder at any time, with remedies up to source disclosure or a distribution injunction.
- **Source:** [SPDX specification](https://spdx.dev/); [OpenChain ISO/IEC 5230](https://www.openchainproject.org/); complements SEC-12 and PRV-43

---

## Privacy

### PRV-01 [BLOCKER] Runtime Consent UI
applies_when: pii=yes
Equal-weight Accept/Reject. Purpose-level granularity. Data deletion mechanism.
- **Detect:**
  - No consent dialog/banner (search for consent/gdpr/privacy in codebase)
  - Accept button larger or more prominent than Reject
  - No account/data deletion flow
- **Fix:** Consent UI with equal-sized buttons. Per-purpose toggles. Account deletion endpoint and UI
- **Note:** For KVKK-specific consent requirements, see PRV-11
- **Impact:** Without equal-weight consent and a deletion path, consent is legally defective under GDPR Art. 7 and users have no way to exercise the erasure right the rest of the audit assumes exists.
- **Source:** GDPR Art. 7, CNIL 2025

### PRV-02 [BLOCKER] Privacy Policy
applies_when: pii=yes or audience=public
Accessible on website/app. AI service usage disclosed. Content complete, not just present.
- **Detect:**
  - No privacy policy link accessible to users
  - Third-party AI services (OpenAI, Anthropic, Google AI) used without disclosure
  - Policy omits any of: controller identity/contact, categories of data + purpose + legal basis per activity, retention periods or criteria, categories of recipients, international transfer mechanism, the full data-subject-rights list, the right to lodge a complaint with a supervisory authority, automated-decision-making/profiling disclosure (if applicable), or a prominent last-updated date
- **Fix:** Add privacy policy link in footer/settings. Disclose AI providers and data processing purposes. Fill every content gap listed above — each maps directly to a GDPR Art. 13-14 disclosure item
- **Impact:** Undisclosed AI-provider data processing and an unreachable privacy policy are themselves GDPR Art. 13-14 transparency violations, independent of what the processing actually does. A policy that exists but omits a required disclosure item (e.g. the supervisory-authority complaint right) is the same violation in a harder-to-spot form.
- **Source:** GDPR Art. 13-14

### PRV-56 [HIGH] Terms of Service Required Clauses & App-Type Additions
applies_when: audience=public
A Terms of Service exists, is reachable, and its clause set matches what the product actually does — a generic template with unfilled app-type-specific clauses is a gap, not a pass.
- **Detect:**
  - No ToS/Terms of Use document reachable from the app/site
  - ToS missing any of the eleven baseline clauses: acceptance of terms, license grant/restrictions, user obligations/conduct, IP ownership, limitation of liability, disclaimer of warranties, termination/suspension (with notice period + data-export window), governing law/dispute resolution, modification clause, severability, contact information
  - Subscription/auto-renewal product with no auto-renewal disclosure or cancellation path in the ToS (US: FTC Negative Option Rule)
  - User-generated-content product with no content-license grant and no DMCA/takedown procedure
  - Marketplace product with no seller/buyer responsibility split, commission terms, or dispute process
  - Payment-handling product with no PCI-DSS reference or chargeback policy
  - AI/ML-feature product with no output-accuracy disclaimer or prohibited-use-cases list
- **Fix:** Publish a ToS covering the eleven baseline clauses; add the app-type-specific clause set that matches the product's actual features (subscription → auto-renewal + cancellation terms; UGC → content license + DMCA safe-harbor procedure per 17 U.S.C. §512; marketplace → responsibilities + commission + dispute process; payments → PCI-DSS reference + chargeback policy; AI/ML → accuracy disclaimer + prohibited uses). Link it from the same footer/settings surface as the Privacy Policy (PRV-02).
- **Impact:** A missing cancellation/auto-renewal disclosure is an active FTC enforcement target under the Negative Option Rule; a missing DMCA takedown procedure forfeits the safe-harbor protection that shields a UGC platform from liability for user-posted content — both are concrete legal exposure, not just incompleteness.
- **Source:** FTC Negative Option Rule (https://www.ftc.gov/legal-library/browse/rules/negative-option-rule); 17 U.S.C. §512 DMCA safe harbor (https://www.law.cornell.edu/uscode/text/17/512)

### PRV-03 [CRITICAL] Data Minimization
applies_when: pii=yes
Collect only necessary data. No unnecessary tracking.
- **Detect:**
  - Collecting data beyond feature requirements
  - Device fingerprinting without consent
  - Tracking scripts loaded before consent
- **Fix:** Remove unnecessary data collection. Replace fingerprinting with privacy-preserving identifiers
- **Impact:** Collecting more than the feature needs expands breach blast radius and violates the minimization principle regardless of how well the excess data is secured.
- **Source:** GDPR Art. 25

### PRV-04 [CRITICAL] Right to Erasure
applies_when: pii=yes
Complete data deletion including databases and third-party services. Every subject-access-request (DSAR) path — access, rectification, erasure, portability, restriction, objection — verifies the requester's identity and is logged.
- **Detect:** No data deletion endpoint/UI. Deletion removes access but retains backend data. DSAR intake with no requester-identity verification step. No log of DSAR submissions, processing steps, and responses (timestamps + outcome)
- **Fix:** Implement complete erasure: databases, backups (schedule), third-party services. Provide deletion UI in account settings. Verify requester identity before acting on any DSAR. Log every DSAR (type, timestamp, verification method, outcome) so the response-time obligation (30 days GDPR, extendable 60; 45 days CCPA) is demonstrable
- **Impact:** Deletion that removes access but leaves the underlying record defeats the erasure right — the data is still there for the next breach or subpoena to expose. An unverified DSAR is a social-engineering vector for exfiltrating someone else's data; an unlogged one leaves no evidence the statutory deadline was met.
- **Source:** GDPR Art. 17, Art. 12(6)

### PRV-05 [HIGH] Data Logging Hygiene
applies_when: pii=yes
No PII in logs, error reports, or analytics.
- **Detect:**
  - Search: logging statements containing `email`, `password`, `token`, `ssn`, `phone` variables
  - User input logged without sanitization
  - Full request/response bodies logged including auth headers
  - Session-replay tooling (PostHog, Sentry Replay, FullStory, Hotjar) initialized without input-masking enabled by default
  - URLs sent to analytics/error tools with query-string tokens or PII left unstripped (session IDs, email addresses, auth codes in the query string)
  - **Common PII patterns to scan for in log/error output:**

    | Pattern | Target | Regex |
    |---------|--------|-------|
    | Email | user@domain.com | `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}` |
    | Phone | +901234567890 | `\+?[0-9]{10,15}` |
    | IPv4 | 192.168.1.1 | `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b` |
    | File path | /home/user/... | `[/\\][a-zA-Z].*[/\\]` |
    | Auth token | Bearer xxx | `(Bearer\|token)\s+[A-Za-z0-9\-_.]+` |
    | UUID | 550e8400-... | `[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}` |

- **Fix:** Sanitize logs. Redact PII fields. Never log auth tokens or passwords. Use structured logging with field-level redaction. Implement redaction filter in logging/error-reporting pipeline — apply before data leaves process (e.g., Sentry `beforeSend`, Winston transport, Python `logging.Filter`, Go middleware, Java `LoggingFilter`). Test redaction with sample PII strings to verify patterns catch real-world formats
- **Limits:** Regex catches structured PII only (emails, IPs, cards); unstructured PII (names, locations, free text) needs ML/NER-based scanning — treat regex-only pipelines as partial coverage, not proof of absence. For LLM interactions, exclude message content from logs entirely rather than relying on scrubbing — models emit sensitive data without keyword patterns
- **Impact:** PII written to logs, error trackers, or analytics spreads personal data into systems with weaker access control than the primary database, multiplying the breach surface.
- **Source:** OWASP Logging Cheat Sheet; Elastic PII detection guidance; Pydantic Logfire LLM-logging guidance

### PRV-26 [HIGH] Pseudonymization & Identifier Separation
applies_when: pii=yes
Raw identifiers replaced with stable pseudonymous tokens; the mapping table lives in a separate, access-controlled store.
- **Detect:**
  - Raw user identifiers (email, phone, national ID) used as keys or foreign keys across analytics/reporting tables
  - Identifier↔pseudonym mapping stored in the same database/schema as the pseudonymized data
  - Schema fields collecting PII with no consuming feature (schema-level minimization gap — cross-check each PII column against actual reads)
- **Fix:** Introduce a pseudonymization layer: generate stable tokens mapped to user IDs; store the mapping table in a separate access-controlled system that only identity-sensitive operations can query. Drop PII columns with no consuming feature. GDPR Art. 5(1)(c) makes minimization a legal obligation, not a preference
- **Impact:** Raw identifiers keyed directly into analytics let anyone with query access re-identify individuals — pseudonymization is the control that forces a second, access-controlled lookup instead.
- **Source:** GDPR Art. 4(5), Art. 5(1)(c); AWS prescriptive guidance (pseudonymized identifiers over raw personal data)

### PRV-27 [HIGH] Retention TTL in Code
applies_when: pii=yes
Retention periods are enforced by automated deletion in code/config — not by a policy document alone.
- **Detect:**
  - Privacy policy declares retention periods but no TTL index, scheduled deletion job, or lifecycle rule implements them
  - Tables holding personal data with no `created_at`-based purge path
  - Backups/exports excluded from the deletion pipeline (PRV-04 erasure gap)
- **Fix:** Declare retention per data class in code/config and enforce it mechanically: DB TTL indexes (Mongo TTL, Postgres `pg_cron` purge jobs), object-store lifecycle rules (S3 Lifecycle), log retention settings. A stated policy without an executing mechanism is a finding, not compliance
- **Impact:** A retention period stated only in a policy document with no enforcing job means data is kept exactly as long as nobody remembers to delete it — indefinitely, in practice.
- **Source:** GDPR Art. 5(1)(e) storage limitation

### PRV-28 [HIGH] Analytics Privacy Floor
applies_when: pii=yes or integrations resolved (analytics SDK present)
Server-side/cookieless analytics still meets consent obligations; aggregate outputs resist re-identification.
- **Detect:**
  - Server-side analytics treated as consent-exempt — a first-party cookie set server-side is still a cookie under ePrivacy-style rules
  - Consent state not propagated to the server-side tag pipeline (events fire regardless of consent)
  - Aggregate analytics exposing small cohorts (user counts below a minimum group size) in dashboards/exports
- **Fix:** Enforce consent centrally in the server-side pipeline — event dispatch conditional on consent status. For aggregate outputs, suppress small cohorts: practical k-anonymity thresholds range k=3–5 (basic suppression) up to k=10–30+ in regulated contexts — no formal consensus exists, so document the chosen k rather than hard-coding an industry claim; pure k-anonymity is vulnerable to differencing attacks, so combine with noise for sensitive metrics
- **Impact:** Server-side analytics that skips consent, or aggregate exports that expose small cohorts, defeats the purpose of consent gating and can re-identify individuals from 'anonymous' rollups.
- **Source:** ePrivacy Directive (first-party cookies in scope); k-anonymity literature (no formal threshold standard — contested/verify-current)

### PRV-60 [MEDIUM] Analytics-Specific Data Minimization: IP Truncation & Type-Specific Retention
applies_when: pii=yes or integrations resolved (analytics SDK present)
- **Detect:**
  - Analytics/logging pipeline storing full IPv4/IPv6 addresses when only coarse geolocation (country/region/city) is derived from them, with no truncation step
  - A single retention setting applied to every analytics data type instead of type-specific limits (raw event stream vs. aggregated metrics vs. session recordings vs. error/crash data have materially different useful lifetimes)
- **Fix:** Truncate IPs before persistence when only geo-level resolution is needed (IPv4: zero the last octet /24; IPv6: zero to a /64) — resolve geo at ingest, discard the raw address rather than storing it "just in case." Set retention per analytics data type rather than one blanket period: representative ranges are raw events ~12 months, aggregated/rolled-up metrics ~36 months, session recordings ~30 days, error/crash payloads ~90 days — enforced the same mechanical way PRV-27 requires for any other retention TTL.
- **Impact:** A full IP address is itself personal data under GDPR (Breyer, CJEU C-582/14) — storing it unretouched when only a city-level signal is ever used is exactly the minimization gap Art. 5(1)(c) targets, and one blanket retention period either deletes short-lived data too late or deletes long-lived aggregates that should have survived.
- **Source:** Plausible Analytics data policy — IP-address handling (https://plausible.io/data-policy); NIST SP 800-122 — De-Identifying PII (https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-122.pdf)

### PRV-29 [HIGH] Field-Sensitivity Registry SSOT
applies_when: pii=yes
Data classification (PII/sensitive, external-sync target, access-role restriction) is defined once per field in a single declarative registry — every consumer derives from it, never from a hand-synced parallel list.
- **Detect:**
  - Two or more independently-maintained lists classifying the same fields as sensitive/PII (e.g. an encryption-whitelist array and a separate redaction-filter list that a comment claims "mirrors" the other, with no shared source)
  - A new schema field added with no corresponding entry in the sensitivity registry, and no mechanical gate that fails on that omission
- **Fix:** Define one declarative registry (`{field, sensitivity, syncTarget, accessRoles}`); make every consumer — encryption whitelist, redaction filter, access-control check — derive from it; add a gate that hard-fails when a new schema field has no registry entry.
- **Impact:** Hand-synced parallel classification lists drift silently — a field marked sensitive in one list but missing from another means it's inconsistently encrypted, redacted, or access-controlled depending on which code path checks which list.
- **Source:** Single-source-of-truth data-classification practice (extends the general SSOT principle to the PII/sensitivity axis specifically)

### PRV-30 [HIGH] Data-Residency Invariant Covers Every Export Path
applies_when: pii=yes
When the product states a data-residency/data-locality invariant ("user data lives only in X," "nothing leaves the audited store"), every write/export path is checked against it — including secondary, opt-in, or admin-only features — not just the primary storage/sync path the invariant was originally written for.
- **Detect:** A documented or asserted residency rule that holds for the primary storage path, while an opt-in secondary feature (report export, third-party integration sync, admin tooling, "export to spreadsheet") writes the same class of data to a location the invariant doesn't cover. Found by cross-referencing every write/export call site against the stated invariant directly — not by trusting the invariant's own documentation, which describes intent, not the audited call sites.
- **Fix:** Move the export target inside the covered boundary, replace it with a residency-neutral alternative (local file download instead of a third-party write), or record an explicit, documented exception with its own compensating control (audit log entry, opt-in confirmation UI) — never leave a write path silently uncovered by the stated invariant. Every export/create call names the shared-workspace target (parent folder/container) explicitly — never trust the API default (the acting user's personal root); verify this default-target behavior as part of shipping every new export feature. The single shared workspace itself follows discover-before-join: clients search for the existing canonical workspace before ever creating one. (XR-005)
- **Impact:** A residency invariant that's true for the primary path but silently false for one opt-in feature undermines the compliance claim made about the whole system — exactly the kind of gap that surfaces first in a breach investigation or customer audit, after the claim has already been relied on.
- **Source:** Data-flow-mapping / data-residency-audit practice (GDPR Art. 30 records-of-processing methodology, generalized beyond GDPR specifically); companion to PRV-29 and ds-backend DB-11 — same "declared invariant, gate every path" shape applied to the residency axis

### PRV-31 [BLOCKER] Special-Category Data Never Reaches the Sync Provider
applies_when: pii=yes
Special-category/health data and national ID numbers never leave the local encrypted store — no sync provider (contacts, calendar, cloud workspace) ever receives them; the red line is mechanically locked.
- **Detect:** Sensitive fields (health notes, national ID, special-category attributes) present in any provider-bound payload, mapping, or export; sync field lists that grow by default when the schema grows; no negative-pattern test asserting sensitive fields are absent from outbound payloads.
- **Fix:** Share only the minimum operational fields (name, phone, maybe company) required for sync and communication; keep everything special-category in the local encrypted store with need-to-know access. Enforce the "no transfer" red line systemically — an allowlist-based outbound mapper (fields not listed cannot leave) — and seal it with a mechanical regression lock: a negative-pattern test that fails the build if a sensitive field ever appears in an outbound payload.
- **Impact:** One accidental field mapping turns a KVKK/GDPR special-category violation into every synced contact — fines scale per record, and the provider copy is unrecoverable.
- **Source:** XR-036 — cross-project experience registry (2026); KVKK Art. 6, GDPR Art. 9.

### PRV-32 [HIGH] Every Deletion Flow Runs From One Canonical Key List
applies_when: pii=yes
All user-data deletion flows (self-service, admin-forced, regulatory) execute against a single shared function defining the canonical list of keys/PII fields to delete.
- **Detect:** Two or more deletion code paths each maintaining their own list of keys/tables/fields; a PII field added to one flow but not the others.
- **Fix:** Define the deletion key list once in one shared function; every deletion flow calls it. Adding a PII field means adding it in exactly one place.
- **Impact:** Divergent deletion lists guarantee partial erasure — a compliance violation that surfaces only when a regulator or user audits what "deleted" actually left behind.
- **Source:** XR-038 — cross-project experience registry (2026); GDPR Art. 17.

### PRV-33 [HIGH] Consent Is Versioned; a Schema Bump Triggers Re-Consent
applies_when: pii=yes
User consent carries a schema version; any change to consent text or scope increments it, and the increment automatically routes previously-consented users back through consent.
- **Detect:** Consent stored as a bare boolean; consent text/scope edited with no version change; existing users grandfathered silently onto new consent terms.
- **Fix:** Store consent with a schema version number; bump it on every text/scope change; on login/next use, users whose stored version is lower re-consent before processing continues.
- **Impact:** Un-versioned consent silently goes stale the day the policy text changes — every subsequent processing act rests on consent the user never gave.
- **Source:** XR-040 — cross-project experience registry (2026); GDPR Art. 7.

### PRV-59 [HIGH] Consent Events Logged Immutably With Timestamp, Scope, and Method
applies_when: pii=yes
- **Detect:**
  - Consent state stored as a bare current-value column (boolean/enum) with no accompanying event log — the current state is known but not when/how/for-what-scope it was given or withdrawn
  - Consent-change events absent from the audit-logging scope that already covers auth/payment/deletion ([ARC-01](rules-arch.md))
  - No way to reconstruct, for a given user and date, what they had actually consented to
- **Fix:** Log every consent grant/change/withdrawal as an immutable, append-only event (timestamp, purpose/scope, method — banner/settings-toggle/API, consent-schema version per PRV-33) separate from the current-state column the application reads at runtime. Route consent events through the same append-only audit-log mechanism [ARC-01](rules-arch.md) already requires for auth/payment/deletion.
- **Impact:** Without a consent event log, "prove you had consent for this processing on this date" — the exact question a regulator or DSAR response asks under GDPR Art. 7(1)'s demonstrability requirement — has no answer; a current-value-only column can't show whether today's "yes" is the same "yes" a user gave two policy versions ago.
- **Source:** GDPR Art. 7(1) demonstrable consent (https://eur-lex.europa.eu/eli/reg/2016/679/oj); ICO guidance on consent records (https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/lawful-basis/consent/)

### PRV-34 [HIGH] Breach First-Notification Ships on Deadline, Even Incomplete
applies_when: pii=yes
When breach assessment cannot finish inside the regulatory window, a first notification goes out with available information and a committed follow-up — never delayed for completeness.
- **Detect:** Breach runbook that sequences "complete investigation" before "notify regulator"; no template for a partial first notification; severity classification that defaults down under uncertainty.
- **Fix:** If full assessment won't complete within the deadline (e.g. 72h), send the first notification with what is known and commit to a follow-up. Classify severity upward under uncertainty: "unknown whether personal data was accessed" is at least P2, never P4-pending-analysis.
- **Impact:** A late-but-complete notification is a separate violation on top of the breach itself; regulators penalize the delay independently of the incident.
- **Source:** XR-042 — cross-project experience registry (2026); complements PRV-17 timelines.

### PRV-35 [MEDIUM] Ephemeral Personal Content Lives RAM-Only With a Failsafe TTL
applies_when: pii=yes
Transient sensitive content (audio, transcripts, uploaded documents) never touches disk: RAM-backed storage only, explicit deletion after use, plus a hard upper-bound TTL as the second line of defense.
- **Detect:** Temp files of sensitive content written to disk-backed paths; RAM-store keys without TTL; deletion handled only by explicit cleanup steps that a crash or skipped branch can bypass.
- **Fix:** Hold transient sensitive content only in RAM-backed stores (Redis on tmpfs-class storage, in-memory buffers); delete explicitly as each stage completes; AND set a failsafe maximum TTL on every PII key so a missed deletion step cannot make data immortal. Explicit deletion is primary; TTL is the backstop, not the mechanism.
- **Impact:** One skipped cleanup path without a TTL backstop means sensitive content persists indefinitely — turning a processing pipeline into unintended long-term storage of user PII.
- **Source:** XR-024 — cross-project experience registry (2026).

### PRV-36 [MEDIUM] Demo/Sample Data Is Structurally Unable to Reach the Real Cloud
applies_when: pii=yes
Onboarding demo data stays local and justified-transient; writing it to the user's real cloud account is structurally impossible, and one click clears it completely.
- **Detect:** Sample records created through the same write path as real data (and thus syncable); demo content appearing in the user's real provider account; no single-action full cleanup of demo data.
- **Fix:** Create demo data only in a local, flagged, sync-excluded store — the sync layer must be structurally unable to pick it up (type-level exclusion, not an if-check); provide one-click complete removal. Prefer a persistent guided checklist card over a one-shot tour for onboarding guidance.
- **Impact:** Demo records synced into a real account pollute the user's actual contacts/calendar with fake entries — a first-run experience that reads as data corruption and is genuinely hard to undo.
- **Source:** XR-120 — cross-project experience registry (2026).

### PRV-37 [MEDIUM] App-Generated Files Deleted by Naming Pattern; No Absolute Wipe Claims
applies_when: pii=yes
Deletability of temp/derived files is decided by the app's own fixed naming pattern — never by contextual state — and "secure delete" is presented as best-effort, not a guarantee.
- **Detect:** Cleanup routines deciding deletability from state/context (source directory, session flags) such that a user-chosen file could match; marketing or UI text promising absolute secure wipe on copy-on-write filesystems.
- **Fix:** Name every app-generated temp/derived file with a fixed, predictable pattern and delete only pattern matches — a user-selected file can then never be swept up. Implement secure delete as best-effort (zero-overwrite then unlink) and describe it as such; never claim absolute wipe where copy-on-write storage makes that unverifiable.
- **Impact:** State-based deletion heuristics eventually delete a user's own file — irreversible and trust-ending; overclaimed wipe guarantees create legal exposure the filesystem cannot honor.
- **Source:** XR-109 — cross-project experience registry (2026).

### PRV-38 [HIGH] Diagnostics Are User-Triggered, Structurally PII-Free, Preview == Payload
applies_when: pii=yes
In a zero-telemetry product, the only diagnostic channel is user-initiated, allowlist-only in content, with a mandatory pre-send preview that is byte-identical to the sent payload, and fail-closed without configured infrastructure.
- **Detect:** Any automatic/background error telemetry; diagnostic payloads assembled from free-form context (potential PII); preview rendered by different code than the sender; network requests fired without user action; channel silently active without configured endpoint.
- **Fix:** Reject background telemetry entirely. Build the support/feedback channel as: user-triggered only; payload fields from a structural allowlist (nothing else can enter); full pre-send preview generated by the SAME function that produces the sent payload (preview == payload, byte-identical); zero network activity without the user's send action; fail-closed when infrastructure is unconfigured.
- **Impact:** A diagnostics channel that sends more than it shows — or sends without being asked — converts a privacy-positioned product into a covert data collector; one such discovery destroys the product's core claim.
- **Source:** XR-121 — cross-project experience registry (2026).

### PRV-39 [MEDIUM] Deletion Promises Are Backed by Client-Verifiable Proof
applies_when: pii=yes
A "we don't keep your data / deleted within X" promise is backed by a mechanism the user can independently verify, not documentation alone.
- **Detect:** Deletion/retention promises with no user-facing verification path; verification UI that shows reassuring text in pending/error states.
- **Fix:** After deletion confirmation plus a short settling window, issue a live status query; render the provider's 404/absent response as the proof of deletion. Pending or errored checks show nothing reassuring; a manual "Verify" button remains the authoritative fallback.
- **Impact:** An unverifiable deletion promise is marketing; a verifiable one is a defensible compliance position — and the only version privacy-conscious users believe.
- **Source:** XR-039 — cross-project experience registry (2026).

### PRV-40 [MEDIUM] Thresholds Chosen Above the Legal Minimum Carry Documented Rationale
applies_when: pii=yes
Any compliance threshold set differently from the legal minimum (age gate, retention period, consent scope) is documented with its rationale and the jurisdictions evaluated.
- **Detect:** A stricter-than-required threshold with no recorded reason; nobody able to say whether a value is legal necessity or product choice; thresholds silently relaxed later because their origin was unknown.
- **Fix:** For each such threshold, record: the legal minimum per relevant jurisdiction, the chosen value, and whether the delta is deliberate product policy or legal necessity. Keep it with the compliance docs so audits and future changes read intent, not archaeology.
- **Impact:** Undocumented strictness gets "optimized away" by a future change that unknowingly drops below a legal floor in one jurisdiction — the worst possible way to discover why the threshold existed.
- **Source:** XR-041 — cross-project experience registry (2026).

### PRV-41 [HIGH] Regulatory Values Verified Against Primary Legal Text, Corrections Logged
applies_when: pii=yes
Every documented regulatory period, threshold, or statute reference is verified against the primary legal text for the data's actual legal category — never copied from memory or a similar-looking clause.
- **Detect:** Retention periods, notification deadlines, or statute citations without a primary-source reference; values inherited from a previous doc version unverified; a discovered transcription error fixed silently in place.
- **Fix:** Verify each legal value against the primary legislation matching the data's real legal character (e.g. the correct statute of limitations for that record type); cite the source. When a previously mis-transcribed value is found, correct it AND record the correction in a dated revision history (what changed, why).
- **Impact:** A retention schedule built on a mis-copied clause systematically deletes too early (destroying legally required records) or too late (unlawful retention) — at scale, in both directions.
- **Source:** XR-043 — cross-project experience registry (2026).

### PRV-42 [HIGH] Outward Claims Match the Real Architecture Line by Line
applies_when: audience=public
Security/retention/status claims in marketing copy, structured data, and policy pages match the actual architecture exactly.
- **Detect:** "E2E encryption" where reality is TLS + at-rest; "InStock"/available structured data for an unreleased product; "no copies remain" while DR snapshots exist; retention claims that don't enumerate every held copy with duration and purpose.
- **Fix:** Audit each outward claim against the real implementation line by line: name the actual encryption model; use truthful availability states (PreOrder, not InStock); disclose every retained copy (backups, PITR, DR snapshots) with its duration and purpose; strike absolute phrasings the architecture cannot honor.
- **Impact:** Overclaimed security/retention is simultaneously a regulatory violation (misleading commercial practice, GDPR transparency) and the fastest possible credibility loss when a researcher or journalist checks.
- **Source:** XR-154 — cross-project experience registry (2026).

### PRV-43 [MEDIUM] Copyleft Obligations Mapped Clause-by-Clause in One Document
applies_when: always
Every copyleft dependency (e.g. LGPL) has a single document mapping each license clause to how the product satisfies it, updated in the same change as any version bump.
- **Detect:** Copyleft dependencies with no obligation mapping (attribution, license-text access, source availability, relink right, no-added-restrictions); dependency upgrades that touch neither the mapping doc nor the in-app license screen.
- **Fix:** Maintain one clause-by-clause mapping document per copyleft dependency: clause → concrete mechanism in the product. Make updating it (and the in-app license screen, if present) an explicit item on the dependency-upgrade checklist, landed in the same change.
- **Impact:** An unmapped copyleft clause is a latent distribution violation; discovered by a rights-holder, it can force product recalls or source disclosure on their schedule, not yours.
- **Source:** XR-044 — cross-project experience registry (2026); complements SEC-12.

### PRV-44 [MEDIUM] Legal-Document Inclusion Managed From One SSOT
applies_when: audience=public
Which legal documents a generated site/surface includes is decided by one SSOT rule set: the privacy set always; the commerce set only when selling is enabled.
- **Detect:** Legal docs copy-pasted per generated site; privacy policy present on some generated surfaces but not others; distance-selling/refund documents appearing on sites that sell nothing (or missing where sales are enabled).
- **Fix:** Centralize the inclusion policy: privacy/data-protection set unconditionally included on every generated surface; sales-related legal set (distance selling, refund terms) included exactly when the sales mode is active. Generation reads this policy; nobody hand-assembles legal page sets.
- **Impact:** Hand-assembled legal sets guarantee some generated site ships without a legally required document — and the operator, not the platform vendor, carries that liability.
- **Source:** XR-193 — cross-project experience registry (2026).

### PRV-45 [MEDIUM] Public Unauthenticated Surfaces Are Isolated and PII-Free
applies_when: auth≠none
A public (no-login) surface (booking page, contact form landing) is an isolated entry point with PII-free routing, separate from the authenticated app.
- **Detect:** Public pages served from the authenticated app shell (shared bundles exposing internal routes/state); URLs or client-visible payloads on the public surface carrying internal IDs or personal data of other parties.
- **Fix:** Isolate the public surface as its own entry point (separate bundle/shell); keep its routing and payloads free of PII and internal identifiers; the public surface knows only what an anonymous visitor may know.
- **Impact:** A public page sharing the app shell leaks internal structure and, worst case, other users' data to anonymous visitors — an unauthenticated breach surface indexed by search engines.
- **Source:** XR-114 — cross-project experience registry (2026).

---

## Regulatory Compliance (Framework-Tagged)

Rules in this section only checked when corresponding framework is in `ACTIVE_FRAMEWORKS`. Tag format: `[FRAMEWORK: X,Y]` means check only if X or Y is active.

US context (2026): ~20 states have comprehensive privacy laws in effect (IN/KY/RI joined 1 Jan 2026; CT/AR/UT amendments 1 Jul 2026). The CCPA/CPRA rule below covers the strictest baseline (CA); most other state laws follow the Virginia template with lighter obligations.

### PRV-06 [BLOCKER] CCPA/CPRA Compliance [FRAMEWORK: CCPA]
applies_when: jurisdiction∋us-ca
California Consumer Privacy Act + California Privacy Rights Act. Amended CPPA regulations effective 1 Jan 2026. Dark-pattern and risk-assessment amendments in the same package are PRV-50/PRV-51.
- **Detect:**
  - No "Do Not Sell or Share My Personal Information" link
  - No opt-out mechanism for data sale/sharing
  - GPC signal processed silently — no visible confirmation shown to the user
  - ADMT (automated decision-making technology) in use without disclosure + opt-out (existing uses must comply by 1 Jan 2027)
  - Neural data collected but not classified as sensitive personal information
  - No 12-month data collection disclosure
  - Search: absence of `doNotSell`, `optOut`, `gpc`, `ccpa`, `cpra` in settings/privacy pages
- **Fix:** Add "Do Not Sell/Share" toggle. Implement opt-out API. Detect and honor Global Privacy Control (GPC) signals as valid opt-out requests with **visible confirmation**, not background-only processing (silent GPC handling drew a record $1.35M fine, Sept 2025). Disclose ADMT use with an opt-out path. Respond within 45 days. Schedule the phased cybersecurity audit: gross revenue >$100M in 2026 → audit by 1 Apr 2028; >$50M in 2027 → by 1 Apr 2029; all remaining covered businesses → by 1 Apr 2030
- **GPC scope note:** GPC is a legally binding opt-out signal in California (Civ. Code §1798.135 + 11 CCR §7025) and in a growing set of other US states — the exact count is contested between sources; check the current enforcement list rather than hard-coding a number. California AB 566 ("Opt Me Out Act") additionally mandates browser-level GPC support from 1 Jan 2027
- **Impact:** Missing opt-out/GPC handling is an active California enforcement target (a $1.35M fine already levied for silent GPC processing) and denies residents a right the statute guarantees.
- **Source:** CCPA 1798.120; CPPA amended regulations, effective 1 Jan 2026; Cal. Civ. Code §1798.135

### PRV-07 [BLOCKER] LGPD Compliance [FRAMEWORK: LGPD]
applies_when: jurisdiction∋br
Brazil Lei Geral de Protecao de Dados.
- **Detect:**
  - No legal basis declaration per processing activity
  - No DPO (Encarregado) contact in privacy policy
  - Cross-border transfer without safeguards
  - Search: absence of `lgpd`, `encarregado` in privacy files
- **Fix:** Declare legal basis per activity. Appoint DPO. Per-purpose consent granularity. Cross-border SCCs
- **Impact:** Processing without a declared legal basis or DPO contact is a direct LGPD violation exposing the business to ANPD fines the moment a data subject or auditor asks the question this rule checks.
- **Source:** LGPD Lei 13.709/2018

### PRV-08 [BLOCKER] PIPL Compliance [FRAMEWORK: PIPL]
applies_when: jurisdiction∋cn
China Personal Information Protection Law.
- **Detect:**
  - No separate consent per processing purpose
  - Data stored outside China without SCIA or Standard Contract
  - Search: absence of `pipl`, `scia` in compliance files
- **Fix:** Separate consent per purpose. Store data in China or complete SCIA. Explicit consent for sensitive data
- **Impact:** Cross-border transfer without SCIA/Standard Contract, or bundled consent, is a PIPL violation under one of the strictest cross-border enforcement regimes globally.
- **Source:** PIPL 2021

### PRV-09 [BLOCKER] UK GDPR Compliance [FRAMEWORK: UK_GDPR]
applies_when: jurisdiction∋uk
UK General Data Protection Regulation (post-Brexit).
- **Detect:**
  - No ICO registration
  - No UK representative (if processing UK data from outside UK)
  - AADC not implemented for child-accessible services
  - Search: absence of `uk_gdpr`, `aadc`, `ico_registration` in compliance files
- **Fix:** Register with ICO. Designate UK representative. Implement AADC for child-accessible services
- **DUAA 2025 note:** the Data (Use and Access) Act (Royal Assent 19 Jun 2025) AMENDS — does not replace — UK GDPR/DPA 2018/PECR, phased Jun 2025→Jun 2026: new "recognised legitimate interests" basis (no balancing test for listed purposes), loosened automated-decision-making rules, transfers test now "not materially lower" protection, statutory complaint right to controllers (30-day acknowledgment — privacy-notice/complaint-handling updates due 19 Jun 2026), low-risk cookies (security, analytics) permitted on opt-out, PECR fines raised to GDPR level (£17.5M / 4%)
- **Impact:** No ICO registration or UK representative leaves the business unreachable by the regulator and non-compliant with a registration duty independent of any breach.
- **Source:** UK GDPR 2018, ICO AADC, ICO — DUAA 2025 guidance

### PRV-10 [BLOCKER] ePrivacy Compliance [FRAMEWORK: EPRIVACY]
applies_when: jurisdiction∋eu
EU ePrivacy Directive (Cookie Law).
- **Detect:**
  - Tracking cookies/scripts loaded before consent
  - No cookie consent mechanism
  - Search: tracking SDK init before consent check
- **Fix:** Block non-essential tracking until consent. Categorize: necessary, analytics, marketing. Granular opt-in. Re-consent annually
- **Status note (2026):** the 2002 Directive remains the binding law. The ePrivacy *Regulation* replacement is effectively abandoned; the Digital Omnibus proposal (tabled 19 Nov 2025) would move cookie-consent rules into GDPR (new Arts. 88a/88b) but is an UNADOPTED proposal as of mid-2026 — do not audit against it as law
- **Impact:** Loading tracking scripts before consent is captured is the single most commonly cited ePrivacy/cookie-law violation and the easiest for a regulator to detect from the outside.
- **Source:** ePrivacy Directive 2002/58/EC; EP Legislative Train — Digital Omnibus package

### PRV-11 [BLOCKER] KVKK Compliance [FRAMEWORK: KVKK]
applies_when: jurisdiction∋tr
Turkey Kisisel Verilerin Korunmasi Kanunu — cross-border regime rewritten by Law 7499, effective 1 Jun 2024 (implementing Yönetmelik: Official Gazette 32598, 10 Jul 2024).
- **Detect:**
  - No VERBIS registration reference
  - No explicit consent (acik riza)
  - Cross-border transfer with no mechanism from the post-2024 tiered regime: (1) Board adequacy decision, (2) appropriate safeguards (standard contract / binding corporate rules), (3) statutory exception — consent-only transfer is the pre-2024 model
  - Standard contract signed but not notified to the Board within 5 business days (independently fined violation — 2026 ceiling TRY 90,308–1,806,177)
  - Search: absence of `kvkk`, `verbis`, `acik_riza` in compliance files
- **Fix:** Register with VERBIS. Obtain explicit consent for processing. Cross-border: use the tiered regime in order (adequacy → standard contract/BCR with 5-business-day Board notification → statutory exception); document which tier applies per transfer
- **Impact:** Skipping VERBIS registration or the tiered cross-border regime carries independently fined violations in Turkey — missing the 5-business-day Board notification alone is its own penalty line.
- **Source:** KVKK 6698 as amended by Law 7499 (Art. 9); kvkk.gov.tr cross-border transfer guideline (Rehber No. 48); 2026 fine indexation (Tebliğ No. 585, RG 27 Nov 2025)

### PRV-12 [BLOCKER] PIPA Compliance [FRAMEWORK: PIPA]
applies_when: jurisdiction∋kr
South Korea Personal Information Protection Act.
- **Detect:**
  - No separate consent per collection purpose
  - Third-party sharing without separate consent
  - Search: absence of `pipa`, `pipc` in compliance files
- **Fix:** Separate opt-in consent per purpose before collection. Mandatory privacy impact assessment for large-scale processing
- **Impact:** Bundled consent instead of per-purpose opt-in is a PIPA violation, and large-scale processing with no privacy impact assessment skips a mandatory Korean regulatory step.
- **Source:** PIPA 2011 (amended 2023)

### PRV-13 [BLOCKER] PDPA Compliance [FRAMEWORK: PDPA]
applies_when: jurisdiction∋th or jurisdiction∋sg
Thailand/Singapore Personal Data Protection Act.
- **Detect:**
  - No consent mechanism
  - No DPO appointed
  - No breach notification mechanism
  - Search: absence of `pdpa`, `pdpc` in compliance files
- **Fix:** Consent before collection. Appoint DPO. Breach notification within 72 hours (Singapore) / without delay (Thailand)
- **Impact:** No consent mechanism, DPO, or breach-notification path leaves the business unable to meet Thailand/Singapore's statutory notification windows when an incident occurs.
- **Source:** Thailand PDPA 2019, Singapore PDPA 2012

### PRV-14 [BLOCKER] HIPAA Compliance [FRAMEWORK: HIPAA]
applies_when: pii=yes and jurisdiction∋us
US Health Insurance Portability and Accountability Act — Protected Health Information (PHI).
- **Detect:**
  - PHI data (patient names, medical records, insurance IDs, diagnosis codes) without encryption at rest and in transit
  - Missing access control logging (audit trail) for PHI access
  - PHI shared with third parties without Business Associate Agreement (BAA)
  - Search: absence of `hipaa`, `phi`, `baa`, `audit_trail` in compliance/security files
  - Missing minimum necessary rule: code accesses full patient records when only subset needed
  - Backup/disaster recovery not documented for systems containing PHI
- **Fix:** Encrypt PHI at rest (AES-256) and in transit (TLS 1.2+). Implement access logging with who/what/when for every PHI access. BAA with all third parties processing PHI. Apply minimum necessary principle. Document backup/DR procedures. Annual risk assessment.
- **Impact:** Unencrypted PHI, missing access logging, or PHI shared without a BAA are each independently reportable HIPAA violations that trigger OCR enforcement and breach-notification duties.
- **Source:** HIPAA Privacy Rule (45 CFR Part 164), HITECH Act 2009

### PRV-15 [CRITICAL] Data Processing Agreement [FRAMEWORK: GDPR,UK_GDPR,LGPD,KVKK]
applies_when: jurisdiction∋eu or jurisdiction∋uk or jurisdiction∋br or jurisdiction∋tr
Written DPA with all data processors.
- **Detect:**
  - Third-party services processing personal data without documented DPA
  - No processor list maintained
  - Executed DPA missing any Art. 28(3) required clause (see below)
- **Fix:** Execute DPA with every processor. Maintain processor registry. Review annually
- **DPA required clauses (GDPR Art. 28(3)):** subject matter, duration, nature, and purpose of processing; types of personal data and categories of data subjects; processor obligations and rights of the controller; processing only on documented controller instructions; confidentiality obligations for processing personnel; technical and organizational security measures; sub-processor engagement rules (prior authorization or general with notification); assistance with DSARs and DPIAs; data return or deletion at end of engagement; audit rights for the controller; breach notification to the controller (48h is common practice, not a statutory floor)
- **Processor registry entry must include:**
  - Service name and legal entity
  - Location (country/region)
  - Data categories processed and explicitly NOT processed
  - Legal basis per applicable framework (GDPR, KVKK, CCPA, etc.)
  - User control mechanism (opt-out toggle, consent, uninstall)
  - DPA/SCC status and expiry date
  - Transfer mechanism (adequacy decision, SCCs, DPF)
  - Data retention policy
- **Annual review checklist:**
  1. All listed processors still in active use
  2. DPA/SCC agreements current (not expired)
  3. Transfer mechanisms still legally valid (check adequacy decisions)
  4. Data minimization verified (no scope creep since last review)
  5. User opt-out/control mechanisms functional
  6. Retention policies aligned with stated periods
- **Impact:** An undocumented or unreviewed data processor is an unmanaged compliance liability — if that processor mishandles data, the controller inherits the violation with no paper trail showing due diligence.
- **Source:** GDPR Art. 28

### PRV-58 [CRITICAL] Special-Category Data Never Rests on Legitimate Interest
applies_when: pii=yes and (jurisdiction∋eu or jurisdiction∋uk)
- **Detect:**
  - GDPR Art. 9 special-category data (health, biometric, genetic, racial/ethnic origin, religious/philosophical belief, sexual orientation, trade-union membership, political opinion) processed under a "legitimate interest" (Art. 6(1)(f)) legal basis instead of an Art. 9(2) exemption (explicit consent, employment/social-security law, vital interests, etc.)
  - No per-activity legal-basis documentation distinguishing ordinary personal data (Art. 6) from special-category data (Art. 9)
  - A Legitimate Interest Assessment (LIA) balancing test on file for a processing activity that actually touches special-category fields
- **Fix:** For every processing activity touching special-category data, document the specific Art. 9(2) exemption relied on — explicit consent is the default absent a narrower exemption; never cite Art. 6(1)(f) legitimate interest as the basis for special-category processing. Keep the legal-basis field in the ROPA (PRV-52) granular enough to show Art. 6 vs. Art. 9 basis per data category, not one blanket basis for the whole activity.
- **Impact:** Legitimate interest is structurally unavailable for special-category data under GDPR — a LIA on file for this data doesn't cure the violation, it documents it; this is a favorite finding of DPAs specifically because it's checkable from the ROPA alone, no breach required.
- **Source:** GDPR Art. 9 (https://eur-lex.europa.eu/eli/reg/2016/679/oj)

### PRV-16 [CRITICAL] Data Protection Impact Assessment [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL]
applies_when: jurisdiction∋eu or jurisdiction∋uk or jurisdiction∋br or jurisdiction∋cn
DPIA required for high-risk processing.
- **Detect:**
  - Large-scale processing of sensitive data without documented DPIA
  - Automated decision-making with legal effects
- **Fix:** Conduct DPIA following this structure (GDPR Art. 35 compliant):
  1. **Processing Description:** Nature, scope, context, purpose. Data category table (data type, source, storage location, retention period)
  2. **Necessity & Proportionality:** Lawful basis per processing activity per applicable framework. Data subject rights implementation (access, rectification, erasure, portability, objection)
  3. **Risk Assessment:** Risk matrix (Risk ID, description, likelihood [Low/Medium/High], severity [Low/Medium/High], inherent risk level). Mitigation table (Risk ID, control measure, implementation status, residual risk)
  4. **Consultation:** DPO/legal review record. Data subject notification plan
  5. **Decision:** Approved/Rejected. Residual risk summary. Review date (max 12 months). Consult DPA if high residual risk remains after mitigations
- **Impact:** Skipping the DPIA for high-risk processing is itself a GDPR Art. 35 violation, separate from whatever risk the assessment would have caught.
- **Source:** GDPR Art. 35

### PRV-17 [CRITICAL] Breach Notification [FRAMEWORK: GDPR,CCPA,LGPD,PIPL,UK_GDPR,KVKK,PIPA,PDPA]
applies_when: pii=yes
Timely notification upon data breach.
- **Detect:**
  - No breach notification procedure documented
  - No incident response plan
  - No severity classification for incidents
- **Fix:** GDPR/UK: 72h to authority. CCPA: AG if 500+ CA residents. KVKK: as soon as possible to Board. LGPD: reasonable timeframe. PIPA: without delay. PDPA: 72h (Singapore) / without delay (Thailand). Implement detection + response plan
- **Severity classification:**

  | Level | Criteria | Containment | Notification |
  |-------|----------|-------------|--------------|
  | P1 Critical | Active exfiltration, auth bypass, unencrypted PII exposed | Immediate | 24h to authority, same-day to users |
  | P2 High | Potential data access, encrypted data exposed | 4h | 48h to authority |
  | P3 Medium | Limited exposure, no evidence of access | 24h | 72h to authority |
  | P4 Low | No personal data involved (service outage, non-PII config) | Document only | No external notification |

- **Response phases:**
  1. **Detection & Triage (0–1h):** Assign severity, assemble incident team, begin documentation
  2. **Containment (1–4h):** Isolate affected systems, preserve evidence/logs, assess scope, apply immediate mitigations
  3. **Authority Notification (per framework timelines above):** File with relevant authority using framework-specific forms/systems
  4. **User Notification (when required):** In-app + email, plain language, user's preferred language, recommended protective actions
  5. **Remediation (1–4 weeks):** Root cause analysis, permanent fix, update security controls, post-incident report
- **Impact:** A missing or undocumented breach response plan turns a routine incident into a missed 72-hour notification deadline — a penalty layered on top of the breach itself.
- **Source:** GDPR Art. 33-34

### PRV-18 [CRITICAL] Data Portability [FRAMEWORK: GDPR,CCPA,UK_GDPR,LGPD,PIPA]
applies_when: pii=yes
Users can export their data in machine-readable format.
- **Detect:**
  - No data export feature
  - Search: absence of `data_export`, `download_my_data`, `portability` in account/settings
  - A9/A11 crosscheck: a stated privacy-policy portability *promise* with no matching real endpoint/button in code (policy says "you can export your data" but no `data_export`/`download_my_data` implementation found) — CRITICAL, not just MEDIUM gap, since this is a legal claim contradicted by the product
- **Fix:** Data export in JSON/CSV. "Download My Data" button. Response within 30 days (GDPR) or 45 days (CCPA)
- **Impact:** No export path denies users the portability right GDPR/CCPA guarantee, and a policy that promises export with no working implementation is a false legal claim on top of the gap.
- **Source:** GDPR Art. 20; extends A11 (ecosystem openness — ds-backend's standard-format export surface is the technical implementation this rule verifies)

### PRV-19 [CRITICAL] Consent Withdrawal [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL,KVKK,PIPA,PDPA]
applies_when: pii=yes
Withdrawal as easy as giving consent.
- **Detect:**
  - No withdrawal mechanism
  - Withdrawal harder than consent
- **Fix:** Toggle per purpose in settings. One-tap withdrawal. Stop processing immediately. Log withdrawal timestamp
- **Impact:** Withdrawal harder than consent (or missing entirely) is itself a GDPR Art. 7(3) violation, and processing continues on consent the user tried to revoke.
- **Source:** GDPR Art. 7(3)

### PRV-21 [BLOCKER] EU AI Act Obligations & Timeline [FRAMEWORK: EU_AI_ACT]
applies_when: jurisdiction∋eu
EU AI Act (Reg. 2024/1689) — obligations phase in on the Digital-Omnibus-on-AI dates (formally adopted: Parliament 16 Jun 2026, Council final green light 29 Jun 2026; OJ publication expected Jul 2026), not the original schedule.
- **Detect:**
  - AI system / GPAI integration shipped to EU users without transparency disclosure (PRV-02 crosscheck)
  - Generative capability without a control blocking non-consensual intimate imagery / CSAM output
  - High-risk (Annex III / Annex I) exposure assessed against the superseded 2 Aug 2026 / 2 Aug 2027 dates
- **Timeline (post-Digital-Omnibus):**

  | Obligation | Applies |
  |------------|---------|
  | GPAI model provider obligations | 2 Aug 2025 (in force) |
  | General enforcement, penalties, prohibitions, transparency | 2 Aug 2026 |
  | New prohibition: non-consensual intimate imagery / CSAM generation | 2 Dec 2026 |
  | High-risk AI systems — Annex III (use-based) | 2 Dec 2027 (was 2 Aug 2026) |
  | High-risk AI embedded in Annex I regulated products | 2 Aug 2028 (was 2 Aug 2027) |

- **Fix:** Disclose AI providers + processing purpose (PRV-02). Block NCII/CSAM generation paths before 2 Dec 2026. Classify high-risk exposure against the 2027/2028 dates — flagging Annex III urgency against 2 Aug 2026 over-flags by 16 months. Penalty tiers: up to €35M or 7% of worldwide turnover (most serious); up to €15M or 3% (transparency violations)
- **Impact:** Missing transparency disclosure or an unblocked NCII/CSAM generation path exposes the business to penalties up to €35M or 7% of global turnover once general enforcement starts.
- **Source:** EU AI Act Service Desk implementation timeline (ai-act-service-desk.ec.europa.eu); Digital Omnibus provisional agreement, 7 May 2026

### PRV-22 [BLOCKER] COPPA Compliance [FRAMEWORK: COPPA]
applies_when: jurisdiction∋us and audience=public
US Children's Online Privacy Protection Rule — FTC amended rule effective 23 Jun 2025; full compliance due 22 Apr 2026. Active enforcement: $20M Cognosphere (Jan 2025), $10M Disney (Sept 2025).
- **Detect:**
  - Child-directed or "mixed audience" service signals (kids category, age gate, child-oriented content/branding) with no verifiable parental consent (VPC) flow
  - Third-party data disclosure (ads SDKs, analytics) without SEPARATE parental consent — distinct from the base collection consent (new in the 2025 rule)
  - Biometric identifiers (face templates, fingerprints, voiceprints) or government-issued IDs collected from children — now "personal information" under the amended rule
  - No written data-security program or retention limits for children's data
  - Search: absence of `coppa`, `parental_consent`, `vpc`, age-gate logic in child-facing flows
- **Fix:** Implement VPC before collection; add a second, separate consent step for any third-party disclosure; treat biometrics/IDs as personal information; write retention limits + security program. Note: FTC Policy Statement (25 Feb 2026) grants discretionary relief for age-verification-related collection only — the rest of the rule is enforced
- **Impact:** Collecting from children without verifiable parental consent is an active FTC enforcement target — $20M and $10M settlements already levied in 2025 for exactly this gap.
- **Source:** FTC amended COPPA Rule (Federal Register 2025-05904, 22 Apr 2025); FTC Policy Statement 25 Feb 2026

### PRV-23 [CRITICAL] EU Data Act [FRAMEWORK: EU_DATA_ACT]
applies_when: jurisdiction∋eu
Regulation (EU) 2023/2854 — applicable since 12 Sept 2025. Hits cloud/SaaS providers and connected-product makers.
- **Detect:**
  - Cloud/data-processing service (SaaS/PaaS/IaaS) whose contract/ToS lacks switching terms: termination on max 2 months' notice, migration completed within 30 days of switching start, switching-fee disclosure (fees must be cost-based now and eliminated entirely from 12 Jan 2027)
  - No transparency notice on switching/porting procedures or on international government data-access exposure
  - Connected-product/related-service data not accessible to the user or their designated third party
  - Crosscheck PRV-18/A11: no machine-readable export path defeats the switching right technically
- **Fix:** Add switching clauses to ToS/contracts; publish switching/porting documentation; implement export in a structured, machine-readable format; plan for enhanced interoperability requirements (from 12 Sept 2026)
- **Impact:** Missing switching/porting terms locks customers into the service in violation of a regulation specifically written to prevent cloud lock-in — exposure applies from 12 Sept 2025.
- **Source:** EU Data Act (Reg. 2023/2854), applicable 12 Sept 2025

### PRV-24 [CRITICAL] EU Cyber Resilience Act Readiness [FRAMEWORK: EU_CRA]
applies_when: jurisdiction∋eu
Products with digital elements sold in the EU. First hard deadline is imminent: vulnerability/incident reporting from 11 Sept 2026 — applies even to products already on the market.
- **Detect:**
  - No coordinated vulnerability disclosure policy or security contact (`SECURITY.md`, `security.txt`)
  - No incident-reporting runbook capable of the CRA cascade: 24h early warning → 72h full notification → 14-day final report, to ENISA/national CSIRT via the Single Reporting Platform
  - No SBOM or dependency inventory (needed for the Dec 2027 CE/security-by-design obligations)
- **Fix:** Publish a vulnerability-disclosure policy + security contact now; write the 24h/72h/14d reporting runbook before 11 Sept 2026; start SBOM generation. Full obligations (CE marking, technical documentation, security-by-design) apply 11 Dec 2027; penalties up to €15M or 2.5% of global turnover
- **Impact:** No vulnerability-disclosure policy or incident-reporting runbook misses a hard deadline (11 Sept 2026) that applies even to products already shipped, independent of whether a vulnerability is ever found.
- **Source:** EU CRA (in force 10 Dec 2024) — digital-strategy.ec.europa.eu/policies/cyber-resilience-act + /cra-reporting

### PRV-25 [CRITICAL] PCI DSS Scope Check [FRAMEWORK: PCI_DSS]
applies_when: billing≠none
Card data handling. Active version: PCI DSS v4.0.1 (sole version since 31 Dec 2024); all 51 future-dated v4 requirements mandatory since 31 Mar 2025. v5.0 has no confirmed date (2027+ estimate).
- **Detect:**
  - Card PAN/CVV fields rendered or posted to own backend (raw card data touching own servers) instead of a PSP-hosted checkout/iframe/SDK (Stripe Checkout/Elements, Braintree Drop-in, etc.)
  - Card numbers in logs, database columns, or analytics events
  - Payment forms without SRI/CSP protection on payment-page scripts (v4 requirements 6.4.3 / 11.6.1 — script inventory + change detection on payment pages)
- **Fix:** Prefer full PSP delegation so scope collapses to SAQ-A (never store/process/transmit raw PAN). Raw card data unavoidable → full v4.0.1 assessment applies; never log PAN/CVV; add payment-page script integrity monitoring
- **Impact:** Raw card data touching own servers pulls the business into full PCI DSS v4.0.1 scope instead of SAQ-A — an assessment and liability burden most businesses can avoid by delegating to a PSP.
- **Source:** PCI SSC — v4.0.1; future-dated requirements effective 31 Mar 2025 (PCI SSC blog)

### PRV-46 [BLOCKER] European Accessibility Act Obligations [FRAMEWORK: EAA]
applies_when: jurisdiction∋eu and ui≠none
EU Directive 2019/882 — accessibility requirements for products and services sold or offered to EU consumers (e-commerce, banking, e-books, passenger transport, telecom), in force since 28 Jun 2025.
- **Detect:** e-commerce checkout flows, banking/payment services, e-book readers/platforms, passenger-transport ticketing or self-service terminals, or telecom/electronic-communications services marketed to EU consumers, with no WCAG 2.1 AA conformance evidence and no published accessibility statement; no member-state complaint-handling contact identified. Exemption: a micro-enterprise providing services (fewer than 10 persons and annual turnover or balance sheet ≤ €2 million, Art. 4(5)) is out of scope for the service obligations — record the exemption with the headcount/turnover evidence instead of flagging.
- **Fix:** Conform the covered service's core user journeys to WCAG 2.1 AA (technical checks: [rules-a11y.md](rules-a11y.md) A11Y-01–08); publish a per-service accessibility statement naming the standard met and any known gaps; identify the designated market-surveillance/enforcement body for each EU member state the service operates in. A gap that cannot be closed immediately still needs the accessibility statement disclosing it — silence is worse than a disclosed gap.
- **Impact:** EAA is in active enforcement, not a future deadline — the first court ruling (France/Carrefour) rejected 71% RGAA conformance as a defense and imposed daily penalties; NL/SE/DK market-surveillance audits are already running.
- **Source:** Directive (EU) 2019/882 (European Accessibility Act) — https://eur-lex.europa.eu/eli/dir/2019/882/oj

### PRV-47 [BLOCKER] Digital Services Act — Transparency & Notice-and-Action [FRAMEWORK: DSA]
applies_when: jurisdiction∋eu and audience=public
EU Regulation 2022/2065 — applies to intermediary/hosting/online-platform services offering services to EU users; obligations phased in from Aug 2023 (very large platforms), fully applicable to all covered services since 17 Feb 2024.
- **Detect:** a hosting/platform service with user-generated or third-party content and no notice-and-action mechanism for illegal content (Art. 16); no statement of reasons issued on content removal/restriction/account action (Art. 17); no published point of contact for authorities (Art. 11) or for users (Art. 12); recommender-system-driven feeds with no plain-language parameter disclosure (Art. 27); ads targeted using special-category-data profiling (Art. 26(3)) or any profiling-based ad targeting a known minor (Art. 28).
- **Fix:** Implement a notice-and-action flow any user can trigger, producing a timely decision; issue a statement of reasons for every content/account restriction; publish electronic points of contact for both authorities and users; disclose recommender-system main parameters in the terms and in-product; never target ads using special-category-data profiling, and never target profiling-based ads at a user known to be a minor.
- **Impact:** Non-compliance penalties reach up to 6% of global annual turnover, and the notice-and-action gap specifically is the duty regulators check first — it is directly observable from outside the company with no internal access needed.
- **Source:** Regulation (EU) 2022/2065 (Digital Services Act) — https://eur-lex.europa.eu/eli/reg/2022/2065/oj

### PRV-48 [BLOCKER] Age Verification / Age-Appropriate Design [FRAMEWORK: AGE_VERIFICATION]
applies_when: audience=public
A service likely to be accessed by children (UK AADC standard), or hosting age-restricted content in a US state with an age-verification statute — SCOTUS upheld Texas-style age-verification laws for sexual content in *Free Speech Coalition v. Paxton* (Jun 2025) — needs age assurance proportionate to risk. COPPA's separate federal under-13 parental-consent regime is PRV-22. State-level app-store age-signal integration is PRV-55.
- **Detect:** a service likely to be accessed by children with no age-assurance mechanism and adult-default settings (high-privacy-by-default absent, geolocation on by default, nudge techniques toward oversharing); age-restricted content (sexually explicit or similar state-defined categories) served in a jurisdiction with an age-verification statute using self-declared age only (a birthdate field with no verification); no documented age-assurance method proportionate to the content risk; an age-of-digital-consent check for GDPR Art. 8 purposes hardcoded to a single value (e.g. 13) applied uniformly to EU users, instead of the 13-16 range that varies per member state.
- **Fix:** For services likely accessed by children, apply the UK AADC's core standards regardless of jurisdiction as a baseline (high privacy by default, geolocation off by default, no nudge techniques toward weakening privacy, minimal data collection); for age-restricted content in a state with a verification statute, implement verification proportionate to the risk (document check, third-party age-estimation, or equivalent assurance) rather than self-declaration alone. Route under-13 US flows to the full COPPA VPC flow (PRV-22). For GDPR Art. 8 consent-capacity gating, resolve the threshold per EU member state (13-16) rather than one hardcoded value.
- **Impact:** This is a live, enforceable requirement in multiple regimes at once — the UK ICO has issued enforcement action under AADC since 2020, and the US Supreme Court has now upheld state age-verification mandates for adult content, removing the strongest prior legal argument against them.
- **Source:** ICO Age Appropriate Design Code — https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/ ; *Free Speech Coalition, Inc. v. Paxton*, 606 U.S. ___ (2025) — https://www.supremecourt.gov/opinions/24pdf/23-1122_3e04.pdf

### PRV-49 [BLOCKER] Quebec Law 25 Compliance [FRAMEWORK: QUEBEC_LOI25]
applies_when: jurisdiction∋ca-qc
Quebec's Act to modernize legislative provisions as regards the protection of personal information ("Law 25") — staged obligations since Sept 2022, fully in force since Sept 2024; enforced by the Commission d'accès à l'information (CAI).
- **Detect:** personal information of Quebec residents processed with no designated, named privacy officer (undocumented default is a gap in itself); no privacy impact assessment on file for a new system/project involving personal information, or for a transfer of information outside Quebec; consent collected without Law 25's granularity (bundled into general terms, non-specific, or pre-ticked); no confidentiality-incident register maintained; automated-decision-making with no notice to the affected individual.
- **Fix:** Formally designate a privacy officer (title + contact published); run and document a privacy impact assessment before any new personal-information project and before any transfer of information outside Quebec; collect clear, specific, granular consent separate from general terms of service; maintain an incident register recording every confidentiality incident regardless of whether it met the notification threshold; disclose automated-decision-making and provide an explanation channel.
- **Impact:** Law 25 penalties reach the higher of C$25M or 4% of worldwide turnover for the most serious violations, and Quebec grants a private right of action with statutory damages that PIPEDA does not — exposure materially larger than most other regimes in this file.
- **Source:** Commission d'accès à l'information du Québec — Law 25 obligations summary — https://www.cai.gouv.qc.ca/protection-renseignements-personnels/sujets-et-domaines-dinteret/principaux-changements-loi-25

### PRV-50 [HIGH] Consent Dark-Pattern Prohibitions [FRAMEWORK: CCPA]
applies_when: jurisdiction∋us-ca
CPRA dark-pattern rules (effective 1 Jan 2026) prohibit consent-flow designs that impair a consumer's ability to make an informed choice, beyond PRV-01's equal-weight-button check.
- **Detect:** asymmetric choice architecture beyond button size (extra steps or friction added only to the decline/opt-out path); confusing language designed to steer toward sharing; a closed/dismissed consent banner treated as consent; repeated re-prompts after a user has already declined; bundled consent covering multiple distinct purposes behind one toggle.
- **Fix:** Make decline exactly as easy as accept in step count and visual weight; use plain, unambiguous choice language; treat a dismissed banner as no decision (does not enable processing); never re-prompt a user who declined within the same consent version; split consent into one toggle per distinct purpose.
- **Impact:** A dark pattern makes consent legally invalid even when a banner was technically shown — the CPPA treats the flow, not the checkbox, as the object of the rule, and non-compliance risk applies from the point of interaction, not just storage.
- **Source:** Cal. Civ. Code §1798.140(h) (dark pattern definition) — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.140.&lawCode=CIV

### PRV-51 [HIGH] CPRA Risk Assessment Obligations [FRAMEWORK: CCPA]
applies_when: jurisdiction∋us-ca
Businesses conducting risk-triggering processing (sale/sharing of PI, processing sensitive PI, automated decision-making technology) must complete and retain a risk assessment, phased in from 1 Jan 2026.
- **Detect:** risk-triggering processing (data sale/sharing, sensitive-PI processing, ADMT) with no risk assessment on file; assessment missing purpose, data categories, benefits, risks, or mitigations; no re-assessment cadence (every 3 years or within 45 days of material change) tracked; third-party vendors in scope not evaluated.
- **Fix:** Conduct a risk assessment before starting risk-triggering processing: document purpose, data categories, benefits, risks, and mitigations; include vendor evaluation; schedule re-assessment every 3 years or on material change; retain records for the CPPA's phased submission deadlines (first submissions due 1 Apr 2028).
- **Impact:** Missing risk assessments are independently enforceable regardless of whether the underlying processing itself caused harm — the assessment is the compliance artifact regulators ask for first.
- **Source:** Cal. Civ. Code §1798.185(a)(15) (CPPA rulemaking mandate for risk assessments) — https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.185.&lawCode=CIV

### PRV-52 [HIGH] Records of Processing Activities (ROPA) & Compliance-Record Retention [FRAMEWORK: GDPR,UK_GDPR,LGPD,KVKK]
applies_when: jurisdiction∋eu or jurisdiction∋uk or jurisdiction∋br or jurisdiction∋tr
A written record of every processing activity (controller identity, purposes, data/subject categories, recipients, transfer safeguards, retention periods, security measures) is maintained and kept current — distinct from PRV-15's per-processor DPA registry, which covers third parties only. The compliance records themselves (not user data) follow their own retention schedule.
- **Detect:** no ROPA covering all processing activities (not just third-party processors); ROPA not updated when a new processing activity is added; compliance records (DPIAs, consent logs, breach register, DSAR log) with no stated retention period, or discarded before the applicable evidentiary window closes (indicative ranges: DPIAs ~3y post-processing, consent records ~5y, breach register ~5y, DSAR correspondence ~3y — verify current guidance per jurisdiction, PRV-41).
- **Fix:** Maintain one ROPA covering every processing activity per GDPR Art. 30: name/contact of controller, purposes, categories of data subjects and data, categories of recipients (including third countries), transfer safeguards, retention periods, and a description of technical/organizational security measures. Update it in the same change that adds or alters a processing activity. Assign each compliance-record type its own retention period and enforce it like any other TTL (PRV-27).
- **Impact:** No ROPA is itself an Art. 30 violation independent of any breach, and it is typically the first document a DPA or auditor requests — its absence signals no processing inventory exists at all.
- **Source:** GDPR Art. 30 — https://eur-lex.europa.eu/eli/reg/2016/679/oj

### PRV-53 [HIGH] International Transfer Mechanism & Impact Assessment [FRAMEWORK: GDPR,UK_GDPR]
applies_when: jurisdiction∋eu or jurisdiction∋uk
Every transfer of personal data to a third country has an identified legal mechanism (adequacy decision, SCCs, BCRs, or a narrow Art. 49 derogation) and, where risk warrants it, a documented Transfer Impact Assessment (TIA) — this generalizes the KVKK-specific tiered regime in PRV-11 to the GDPR/UK GDPR baseline.
- **Detect:** a third-country data flow (hosting, SaaS vendor, analytics/error-reporting tool) with no identified transfer mechanism; reliance on the EU-US Data Privacy Framework (DPF) with no verification the specific processor is currently certified, and no SCCs held as fallback; SCCs on file using a pre-2021 template; no TIA for a transfer into a jurisdiction without an adequacy decision; transfer mechanisms not reassessed since the last material legal change (e.g. an adequacy decision under challenge). Common concrete case: Google Analytics (GA4) or another US-hosted analytics/ad tool active for EU users with no DPF certification check and no EU-only processing configuration — multiple EU DPAs (Austria, France, Italy, Denmark) have found this specific pattern unlawful under GDPR Chapter V.
- **Fix:** For every third-country recipient, record which mechanism applies (adequacy, SCCs, BCRs, derogation) and its current validity. For DPF reliance, verify the processor's certification status directly rather than assuming; hold SCCs (2021 version) as a fallback. Run a TIA before any transfer lacking adequacy, and document supplementary measures if the TIA finds a gap. Re-assess annually or on legal/political change (adequacy challenges, DPF status).
- **Impact:** A transfer with no valid mechanism is unlawful from the first byte sent, independent of whether the recipient ever mishandles the data — and it is exactly the failure mode multiple EU DPAs have already fined over for the single most common case (US-hosted analytics).
- **Source:** GDPR Chapter V (Art. 44-49) — https://eur-lex.europa.eu/eli/reg/2016/679/oj ; EDPB Recommendations 01/2020 (transfer supplementary measures) — https://edpb.europa.eu/our-work-tools/our-documents/recommendations/recommendations-012020-measures-supplement-transfer_en

### PRV-54 [HIGH] ADA Title III — Public-Accommodation Digital Accessibility [FRAMEWORK: ADA]
applies_when: jurisdiction∋us and audience=public
US ADA Title III ("places of public accommodation") is increasingly read by courts to cover commercial websites and apps, independent of PRV-46's EU-specific EAA obligation. No statutory technical standard is mandated, but WCAG 2.1 AA is the de facto benchmark DOJ references in settlements and consent decrees.
- **Detect:** a commercial (non-government) website or app with a public/customer-facing surface and no accessibility conformance evidence against WCAG 2.1 AA or later, and no published accessibility statement; reliance on an overlay/widget tool as the sole remediation with no underlying conformance testing.
- **Fix:** Conform core commercial user journeys to WCAG 2.2 AA (technical checks: [rules-a11y.md](rules-a11y.md) A11Y-01–08, which satisfies 2.1 AA with margin); publish an accessibility statement; do not substitute an automated overlay for real conformance testing.
- **Impact:** Title III carries no statutory damages cap in some circuits, and DOJ has referenced WCAG 2.1 AA directly in enforcement settlements — private litigation risk exists today, independent of any future rulemaking.
- **Source:** 42 U.S.C. §12181 et seq. — https://www.law.cornell.edu/uscode/text/42/12181 ; DOJ ADA web accessibility guidance — https://www.ada.gov/resources/web-guidance/

### PRV-55 [HIGH] US State App-Store Age-Assurance Laws (ASA) [FRAMEWORK: AGE_VERIFICATION]
applies_when: jurisdiction∋us and (platforms∋ios or platforms∋android)
A growing set of US states (Texas SB 2420 effective 1 Jan 2026, Utah 6 May 2026, Louisiana 1 Jul 2026) require age verification via the mobile platform's own API rather than in-app self-declaration, with parental consent required for minors.
- **Detect:** a mobile app targeting US users with age-gated features or content and no integration of the platform age-signal API; age category treated as binary adult/minor instead of the tiered bands (<13, 13-15, 16-17, 18+) these statutes use; no parental-consent flow triggered by the returned age category.
- **Fix:** Integrate Apple's Declared Age Range API (iOS) and Google Play's Age Signals API (Android); branch content/feature availability on the returned age tier; route consent flows for minors accordingly; treat this as additive to, not a replacement for, the federal COPPA under-13 VPC flow (PRV-22).
- **Impact:** Missing platform age-signal integration misses a hard per-state compliance deadline starting 1 Jan 2026, with more states following the same template.
- **Source:** Texas SB 2420 — https://capitol.texas.gov/BillLookup/Text.aspx?LegSess=89R&Bill=SB2420 ; Apple Declared Age Range — https://developer.apple.com/documentation/declaredagerange ; Google Play Age Signals — https://developer.android.com/google/play/age-signals/overview

### PRV-57 [HIGH] Apple App Tracking Transparency (ATT) Consent Before IDFA Access
applies_when: platforms∋ios
- **Detect:**
  - iOS app reading or transmitting IDFA, or initializing an ad-attribution/analytics SDK that accesses `AppTrackingTransparency`-gated identifiers, before calling `ATTrackingManager.requestTrackingAuthorization` and receiving `.authorized`
  - No pre-permission/value screen shown before the system ATT prompt
  - Tracking proceeding on `.denied`/`.notDetermined`/`.restricted`
- **Fix:** Gate every IDFA read and every tracking-capable SDK init behind `ATTrackingManager.requestTrackingAuthorization`; only proceed with cross-app tracking on `.authorized`. Show a pre-permission screen explaining the value exchange before the system prompt fires (raises opt-in from the ~35% blended baseline) — but the pre-permission screen must not itself collect tracking data. On any non-authorized status, fall back to SKAdNetwork/AdAttributionKit-based aggregate attribution instead of IDFA.
- **Impact:** Accessing IDFA without an authorized ATT status is an App Store Review Guideline 5.1.2 violation that blocks release outright, independent of any GDPR/CCPA exposure the same tracking would separately create.
- **Source:** Apple App Tracking Transparency documentation (https://developer.apple.com/documentation/apptrackingtransparency)

---

## Advisory (Non-Blocking, D4 crosscheck)

### PRV-20 [ADVISORY] Error-Channel Consent + Payload Minimization
applies_when: integrations resolved (error/crash-reporting SDK present)
Never a blocker (mandated-blocker test: a citable external authority makes it a documented prerequisite whose omission causes rejection, legal exposure, or a broken production path) — crosschecks the error-channel decision that ds-deploy/ds-backend surface under D4. A no-PII stance that removes error telemetry entirely trades user privacy for production blindness; the compliant middle ground is a consent-based, PII-free, aggregate channel.
- **Detect:**
  - An error/crash-reporting channel exists (Sentry, Crashlytics, or equivalent) with no opt-in consent gate before initialization — same pattern as PRV-01/EPRIVACY tracking-init check, applied to error reporting specifically
  - Error payload includes fields beyond the allowlist: error class/type, app/build version, and an aggregate counter only — no user ID, email, IP, free-text stack-trace-with-PII, or request body
  - No error-reporting channel exists at all and no documented risk acceptance for "support-mail blindness" is present (this half of the check is informational, not a compliance gap — routed to ds-deploy/ds-backend's advisory finding, not duplicated here)
- **Fix:** Gate error-reporting SDK init behind the same consent flow as analytics (PRV-01). Scrub payload to the allowlist (class, version, counter) before send — strip stack traces of literal values, user identifiers, and request/response bodies.
- **Impact:** An error channel with no consent gate, or one that leaks stack-trace PII, silently converts a debugging tool into an unconsented personal-data pipeline — undermining the trust a zero-telemetry product is built on.
- **Source:** GDPR Art. 5(1)(c) data minimization, applied to error telemetry; extends D4 (dimension coverage map)
