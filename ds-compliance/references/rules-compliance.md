# Rules: Security & Privacy

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | SEC-01–12 (4 BLOCKER, 5 CRITICAL, 3 MAJOR) | ~12 |
| **Privacy** | PRV-01–05 (2 BLOCKER, 2 CRITICAL, 1 MAJOR) | ~120 |
| **Regulatory Compliance** | PRV-06–19, PRV-21 (10 BLOCKER, 5 CRITICAL) | ~165 |
| **Advisory (Non-Blocking)** | PRV-20 (1 ADVISORY) | ~390 |

---

## Security

Baseline: OWASP ASVS 5.0.0 (May 2025 — ~350 requirements, 17 categories). OSS DAST tools (ZAP, Nikto) still emit 4.0.3-tagged findings as of mid-2026 — label tool output with the tool's ASVS version; never present 4.0.3 tool findings as ASVS 5.0 coverage.

### SEC-01 [BLOCKER] Secure Credential Storage
Credentials, tokens, and secrets must not be in plaintext files or unencrypted storage.
- **Detect:**
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git (not in `.gitignore`)
  - Search: passwords/tokens in config files, database connection strings with embedded credentials
  - Plaintext secrets in `application.yml`, `settings.py`, `config/*.json`
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Use environment variables loaded at runtime. Use secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Doppler). Add `.env` to `.gitignore`. For Docker: use secrets, not ENV in Dockerfile
- **Source:** OWASP A07:2021

### SEC-02 [BLOCKER] No Hardcoded Credentials
Zero secrets in source code.
- **Detect:**
  - Search: `apiKey\s*[:=]`, `api_key\s*[:=]`, `secret\s*[:=]`, `password\s*[:=]`, `bearer\s`, `sk-[a-zA-Z0-9]`, `AKIA[A-Z0-9]`, base64 patterns >20 chars in string literals
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Move to environment variables or secret manager. Add to `.gitignore`. Use server-side proxy for third-party API keys
- **Source:** OWASP A07:2021

### SEC-03 [BLOCKER] Debug Mode Off in Production
No debug features exposed in production builds.
- **Detect:**
  - Python: `DEBUG = True` in settings, `FLASK_DEBUG=1`
  - Node: missing `NODE_ENV=production`, `console.log` in production paths
  - Go: `debug` flags in production configs
  - Java/Kotlin: `debug=true` in application.properties
  - Stack traces exposed in error responses
- **Fix:** Environment-based config. Strip debug code in production builds. Never expose stack traces to clients
- **Source:** OWASP A05:2021

### SEC-04 [BLOCKER] TLS Enforced
All connections over HTTPS. No plaintext HTTP in production.
- **Detect:**
  - Search: `http://` URLs in source (excluding localhost/127.0.0.1/10.0/192.168)
  - No HTTPS redirect configuration
  - Missing HSTS headers
- **Fix:** Redirect HTTP to HTTPS. Set HSTS header: `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`. Use TLS 1.2+ only
- **Source:** OWASP A02:2021

### SEC-05 [CRITICAL] Input Validation & Injection Prevention
All user input validated and sanitized. No raw interpolation in queries or commands.
- **Detect:**
  - Search: string concatenation in SQL queries (`"SELECT.*" +`, f-strings in queries, template literals in SQL)
  - Raw user input in shell commands (`exec`, `os.system`, `child_process.exec`)
  - No input validation middleware/decorators on route handlers
  - Search: `eval(`, `Function(`, `innerHTML =` with user input
- **Fix:** Parameterized queries (prepared statements). Input validation with schemas (Zod, Pydantic, Joi). Never interpolate user input into SQL/shell/HTML. Use ORM for queries
- **Impact:** SQL injection is still #1 web vulnerability. Single unparameterized query = full database compromise
- **Source:** OWASP A03:2021

### SEC-06 [CRITICAL] Strong Cryptography
AES-256-GCM symmetric. No MD5/SHA-1 for security. No custom crypto.
- **Detect:**
  - Search: `MD5`, `SHA1`, `SHA-1` in non-checksum context, `ECB` mode, `DES`, `RC4`, hardcoded IV/nonce
  - Custom crypto implementations
  - Weak password hashing (plain SHA-256 without salt/iteration)
- **Fix:** Use platform crypto libraries. Password hashing: bcrypt/scrypt/argon2. Encryption: AES-256-GCM. Use random IV/nonce per operation
- **Source:** OWASP A02:2021

### SEC-07 [CRITICAL] Secure HTTP Headers
Security headers set on all responses.
- **Detect:**
  - No `helmet` (Express), `django-csp` (Django), security middleware
  - Missing headers: Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy
- **Fix:** Use security middleware (helmet, django-secure, secure-headers). Set CSP, X-Content-Type-Options: nosniff, X-Frame-Options: DENY, Referrer-Policy: strict-origin-when-cross-origin
- **Impact:** Missing security headers enable XSS, clickjacking, and MIME-sniffing attacks
- **Source:** OWASP Secure Headers Project

### SEC-08 [CRITICAL] Supply Chain Security
Dependencies audited, versions pinned, lockfile committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile (package-lock.json, yarn.lock, pnpm-lock.yaml, Pipfile.lock, poetry.lock, go.sum) in git
- **Fix:** Pin exact versions. Commit lockfiles. Run `npm audit` / `pip audit` / `safety check` regularly
- **Source:** OWASP A06:2021

### SEC-09 [CRITICAL] Server-Side Auth & Authorization
Auth validated server-side on every request. No client-only auth checks.
- **Detect:**
  - API endpoints without auth middleware
  - Authorization based on client-provided role/permission without server verification
  - Missing token validation on protected routes
- **Fix:** Auth middleware on all protected routes. Validate JWT/session server-side. Check permissions per resource, not just authentication. Use RBAC or ABAC
- **Source:** OWASP A01:2021

### SEC-10 [MAJOR] Session Management
Secure session configuration. Token rotation. Proper logout.
- **Detect:**
  - Session cookies without `Secure`, `HttpOnly`, `SameSite` flags
  - No token expiry or rotation
  - Logout doesn't invalidate server-side session
  - Long-lived tokens without refresh mechanism
- **Fix:** Set cookie flags: `Secure; HttpOnly; SameSite=Strict`. Short-lived access tokens (15min) + refresh token rotation. Server-side session invalidation on logout. Regenerate session ID after auth state change
- **Source:** OWASP Session Management Cheat Sheet

### SEC-11 [MAJOR] Rate Limiting
API endpoints protected against abuse.
- **Detect:**
  - No rate limiting middleware on auth endpoints (login, register, password reset)
  - No rate limiting on API endpoints
  - No brute-force protection
- **Fix:** Rate limit auth endpoints (5-10 req/min). General API rate limiting (100-1000 req/min per user). Use `express-rate-limit`, `slowapi`, or API gateway rate limiting. Return `429 Too Many Requests` with `Retry-After` header
- **Impact:** Unprotected auth endpoints enable credential stuffing and brute-force attacks
- **Source:** OWASP API Security Top 10
- **Cross-ref:** Same check as [NET-05](rules-network.md) (canonical, network scope) — when both `security` and `network` scopes run together, report once under NET-05.

### SEC-12 [MAJOR] License & IP Contamination
AI assistants can emit near-verbatim third-party or copyleft code without attribution.
- **Detect:**
  - No license / SCA scan on AI-assisted PRs
  - Copyleft (GPL/AGPL) code entering a permissively-licensed project
  - Large verbatim blocks of unknown provenance
  - AI assistance not recorded where org or licensing policy requires it
- **Fix:** Run a license/SCA scan (FOSSA, ScanCode) on AI-assisted PRs; flag copyleft entering permissive code. Verify provenance of large verbatim AI output before merge; prefer generating from your own interfaces. Record AI assistance where policy requires an authorship/provenance note.
- **Impact:** In *Doe v. GitHub* most claims were dismissed but an open-source-license-violation claim survives; the EU AI Act (Reg. 2024/1689) GPAI transparency duties applied 2 Aug 2025; general enforcement and penalties apply 2 Aug 2026, while high-risk obligations shifted under the Digital Omnibus — timeline in PRV-21.
- **Source:** [Doe v. GitHub case updates](https://githubcopilotlitigation.com/case-updates.html); [EU AI Act (EC)](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)

---

## Privacy

### PRV-01 [BLOCKER] Runtime Consent UI
Equal-weight Accept/Reject. Purpose-level granularity. Data deletion mechanism.
- **Detect:**
  - No consent dialog/banner (search for consent/gdpr/privacy in codebase)
  - Accept button larger or more prominent than Reject
  - No account/data deletion flow
- **Fix:** Consent UI with equal-sized buttons. Per-purpose toggles. Account deletion endpoint and UI
- **Note:** For KVKK-specific consent requirements, see PRV-11
- **Source:** GDPR Art. 7, CNIL 2025

### PRV-02 [BLOCKER] Privacy Policy
Accessible on website/app. AI service usage disclosed.
- **Detect:**
  - No privacy policy link accessible to users
  - Third-party AI services (OpenAI, Anthropic, Google AI) used without disclosure
- **Fix:** Add privacy policy link in footer/settings. Disclose AI providers and data processing purposes
- **Source:** GDPR Art. 13-14

### PRV-03 [CRITICAL] Data Minimization
Collect only necessary data. No unnecessary tracking.
- **Detect:**
  - Collecting data beyond feature requirements
  - Device fingerprinting without consent
  - Tracking scripts loaded before consent
- **Fix:** Remove unnecessary data collection. Replace fingerprinting with privacy-preserving identifiers
- **Source:** GDPR Art. 25

### PRV-04 [CRITICAL] Right to Erasure
Complete data deletion including databases and third-party services.
- **Detect:** No data deletion endpoint/UI. Deletion removes access but retains backend data
- **Fix:** Implement complete erasure: databases, backups (schedule), third-party services. Provide deletion UI in account settings
- **Source:** GDPR Art. 17

### PRV-05 [MAJOR] Data Logging Hygiene
No PII in logs, error reports, or analytics.
- **Detect:**
  - Search: logging statements containing `email`, `password`, `token`, `ssn`, `phone` variables
  - User input logged without sanitization
  - Full request/response bodies logged including auth headers
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
- **Source:** OWASP Logging Cheat Sheet

---

## Regulatory Compliance (Framework-Tagged)

Rules in this section only checked when corresponding framework is in `ACTIVE_FRAMEWORKS`. Tag format: `[FRAMEWORK: X,Y]` means check only if X or Y is active.

### PRV-06 [BLOCKER] CCPA/CPRA Compliance [FRAMEWORK: CCPA]
California Consumer Privacy Act + California Privacy Rights Act. Amended CPPA regulations effective 1 Jan 2026.
- **Detect:**
  - No "Do Not Sell or Share My Personal Information" link
  - No opt-out mechanism for data sale/sharing
  - GPC signal processed silently — no visible confirmation shown to the user
  - ADMT (automated decision-making technology) in use without disclosure + opt-out (existing uses must comply by 1 Jan 2027)
  - Neural data collected but not classified as sensitive personal information
  - No 12-month data collection disclosure
  - Search: absence of `doNotSell`, `optOut`, `gpc`, `ccpa`, `cpra` in settings/privacy pages
- **Fix:** Add "Do Not Sell/Share" toggle. Implement opt-out API. Detect and honor Global Privacy Control (GPC) signals as valid opt-out requests with **visible confirmation**, not background-only processing (silent GPC handling drew a record $1.35M fine, Sept 2025). Disclose ADMT use with an opt-out path. Respond within 45 days. Schedule the phased cybersecurity audit: gross revenue >$100M in 2026 → audit by 1 Apr 2028; >$50M in 2027 → by 1 Apr 2029; all remaining covered businesses → by 1 Apr 2030
- **Source:** CCPA 1798.120; CPPA amended regulations, effective 1 Jan 2026

### PRV-07 [BLOCKER] LGPD Compliance [FRAMEWORK: LGPD]
Brazil Lei Geral de Protecao de Dados.
- **Detect:**
  - No legal basis declaration per processing activity
  - No DPO (Encarregado) contact in privacy policy
  - Cross-border transfer without safeguards
  - Search: absence of `lgpd`, `encarregado` in privacy files
- **Fix:** Declare legal basis per activity. Appoint DPO. Per-purpose consent granularity. Cross-border SCCs
- **Source:** LGPD Lei 13.709/2018

### PRV-08 [BLOCKER] PIPL Compliance [FRAMEWORK: PIPL]
China Personal Information Protection Law.
- **Detect:**
  - No separate consent per processing purpose
  - Data stored outside China without SCIA or Standard Contract
  - Search: absence of `pipl`, `scia` in compliance files
- **Fix:** Separate consent per purpose. Store data in China or complete SCIA. Explicit consent for sensitive data
- **Source:** PIPL 2021

### PRV-09 [BLOCKER] UK GDPR Compliance [FRAMEWORK: UK_GDPR]
UK General Data Protection Regulation (post-Brexit).
- **Detect:**
  - No ICO registration
  - No UK representative (if processing UK data from outside UK)
  - AADC not implemented for child-accessible services
  - Search: absence of `uk_gdpr`, `aadc`, `ico_registration` in compliance files
- **Fix:** Register with ICO. Designate UK representative. Implement AADC for child-accessible services
- **Source:** UK GDPR 2018, ICO AADC

### PRV-10 [BLOCKER] ePrivacy Compliance [FRAMEWORK: EPRIVACY]
EU ePrivacy Directive (Cookie Law).
- **Detect:**
  - Tracking cookies/scripts loaded before consent
  - No cookie consent mechanism
  - Search: tracking SDK init before consent check
- **Fix:** Block non-essential tracking until consent. Categorize: necessary, analytics, marketing. Granular opt-in. Re-consent annually
- **Source:** ePrivacy Directive 2002/58/EC

### PRV-11 [BLOCKER] KVKK Compliance [FRAMEWORK: KVKK]
Turkey Kisisel Verilerin Korunmasi Kanunu.
- **Detect:**
  - No VERBIS registration reference
  - No explicit consent (acik riza)
  - Data transfer abroad without KVKK Board approval
  - Search: absence of `kvkk`, `verbis`, `acik_riza` in compliance files
- **Fix:** Register with VERBIS. Obtain explicit consent. Cross-border only to adequate countries or with Board approval
- **Source:** KVKK 6698

### PRV-12 [BLOCKER] PIPA Compliance [FRAMEWORK: PIPA]
South Korea Personal Information Protection Act.
- **Detect:**
  - No separate consent per collection purpose
  - Third-party sharing without separate consent
  - Search: absence of `pipa`, `pipc` in compliance files
- **Fix:** Separate opt-in consent per purpose before collection. Mandatory privacy impact assessment for large-scale processing
- **Source:** PIPA 2011 (amended 2023)

### PRV-13 [BLOCKER] PDPA Compliance [FRAMEWORK: PDPA]
Thailand/Singapore Personal Data Protection Act.
- **Detect:**
  - No consent mechanism
  - No DPO appointed
  - No breach notification mechanism
  - Search: absence of `pdpa`, `pdpc` in compliance files
- **Fix:** Consent before collection. Appoint DPO. Breach notification within 72 hours (Singapore) / without delay (Thailand)
- **Source:** Thailand PDPA 2019, Singapore PDPA 2012

### PRV-14 [BLOCKER] HIPAA Compliance [FRAMEWORK: HIPAA]
US Health Insurance Portability and Accountability Act — Protected Health Information (PHI).
- **Detect:**
  - PHI data (patient names, medical records, insurance IDs, diagnosis codes) without encryption at rest and in transit
  - Missing access control logging (audit trail) for PHI access
  - PHI shared with third parties without Business Associate Agreement (BAA)
  - Search: absence of `hipaa`, `phi`, `baa`, `audit_trail` in compliance/security files
  - Missing minimum necessary rule: code accesses full patient records when only subset needed
  - Backup/disaster recovery not documented for systems containing PHI
- **Fix:** Encrypt PHI at rest (AES-256) and in transit (TLS 1.2+). Implement access logging with who/what/when for every PHI access. BAA with all third parties processing PHI. Apply minimum necessary principle. Document backup/DR procedures. Annual risk assessment.
- **Source:** HIPAA Privacy Rule (45 CFR Part 164), HITECH Act 2009

### PRV-15 [CRITICAL] Data Processing Agreement [FRAMEWORK: GDPR,UK_GDPR,LGPD,KVKK]
Written DPA with all data processors.
- **Detect:**
  - Third-party services processing personal data without documented DPA
  - No processor list maintained
- **Fix:** Execute DPA with every processor. Maintain processor registry. Review annually
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
- **Source:** GDPR Art. 28

### PRV-16 [CRITICAL] Data Protection Impact Assessment [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL]
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
- **Source:** GDPR Art. 35

### PRV-17 [CRITICAL] Breach Notification [FRAMEWORK: GDPR,CCPA,LGPD,PIPL,UK_GDPR,KVKK,PIPA,PDPA]
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
- **Source:** GDPR Art. 33-34

### PRV-18 [CRITICAL] Data Portability [FRAMEWORK: GDPR,CCPA,UK_GDPR,LGPD,PIPA]
Users can export their data in machine-readable format.
- **Detect:**
  - No data export feature
  - Search: absence of `data_export`, `download_my_data`, `portability` in account/settings
  - A9/A11 crosscheck: a stated privacy-policy portability *promise* with no matching real endpoint/button in code (policy says "you can export your data" but no `data_export`/`download_my_data` implementation found) — CRITICAL, not just MEDIUM gap, since this is a legal claim contradicted by the product
- **Fix:** Data export in JSON/CSV. "Download My Data" button. Response within 30 days (GDPR) or 45 days (CCPA)
- **Source:** GDPR Art. 20; extends A11 (ecosystem openness — ds-backend's standard-format export surface is the technical implementation this rule verifies)

### PRV-19 [CRITICAL] Consent Withdrawal [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL,KVKK,PIPA,PDPA]
Withdrawal as easy as giving consent.
- **Detect:**
  - No withdrawal mechanism
  - Withdrawal harder than consent
- **Fix:** Toggle per purpose in settings. One-tap withdrawal. Stop processing immediately. Log withdrawal timestamp
- **Source:** GDPR Art. 7(3)

### PRV-21 [BLOCKER] EU AI Act Obligations & Timeline [FRAMEWORK: EU_AI_ACT]
EU AI Act (Reg. 2024/1689) — obligations phase in on the Digital Omnibus dates (provisional agreement 7 May 2026), not the original schedule.
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
- **Source:** EU AI Act Service Desk implementation timeline (ai-act-service-desk.ec.europa.eu); Digital Omnibus provisional agreement, 7 May 2026

---

## Advisory (Non-Blocking, D4 crosscheck)

### PRV-20 [ADVISORY] Error-Channel Consent + Payload Minimization
Never a blocker (SKILL-SPEC §15) — crosschecks the error-channel decision that ds-deploy/ds-backend surface under D4. A no-PII stance that removes error telemetry entirely trades user privacy for production blindness; the compliant middle ground is a consent-based, PII-free, aggregate channel.
- **Detect:**
  - An error/crash-reporting channel exists (Sentry, Crashlytics, or equivalent) with no opt-in consent gate before initialization — same pattern as PRV-01/EPRIVACY tracking-init check, applied to error reporting specifically
  - Error payload includes fields beyond the allowlist: error class/type, app/build version, and an aggregate counter only — no user ID, email, IP, free-text stack-trace-with-PII, or request body
  - No error-reporting channel exists at all and no documented risk acceptance for "support-mail blindness" is present (this half of the check is informational, not a compliance gap — routed to ds-deploy/ds-backend's advisory finding, not duplicated here)
- **Fix:** Gate error-reporting SDK init behind the same consent flow as analytics (PRV-01). Scrub payload to the allowlist (class, version, counter) before send — strip stack traces of literal values, user identifiers, and request/response bodies.
- **Source:** GDPR Art. 5(1)(c) data minimization, applied to error telemetry; extends D4 (SKILL-SPEC Dimension Coverage Map)
