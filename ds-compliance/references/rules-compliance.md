# Rules: Security & Privacy

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | SEC-01–11 (4 BLOCKER, 5 CRITICAL, 2 MAJOR) | ~12 |
| **Privacy** | PRV-01–05 (2 BLOCKER, 2 CRITICAL, 1 MAJOR) | ~120 |
| **Regulatory Compliance** | PRV-06–19 (9 BLOCKER, 5 CRITICAL) | ~165 |

---

## Security

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
- **Impact:** SQL injection is still the #1 web vulnerability. Single unparameterized query = full database compromise
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
- **Fix:** Sanitize logs. Redact PII fields. Never log auth tokens or passwords. Use structured logging with field-level redaction
- **Source:** OWASP Logging Cheat Sheet

---

## Regulatory Compliance (Framework-Tagged)

Rules in this section are only checked when the corresponding framework is in `ACTIVE_FRAMEWORKS`. Tag format: `[FRAMEWORK: X,Y]` means check only if X or Y is active.

### PRV-06 [BLOCKER] CCPA/CPRA Compliance [FRAMEWORK: CCPA]
California Consumer Privacy Act + California Privacy Rights Act.
- **Detect:**
  - No "Do Not Sell or Share My Personal Information" link
  - No opt-out mechanism for data sale/sharing
  - No 12-month data collection disclosure
  - Search: absence of `doNotSell`, `optOut`, `ccpa`, `cpra` in settings/privacy pages
- **Fix:** Add "Do Not Sell/Share" toggle. Implement opt-out API. Honor Global Privacy Control (GPC) signal. Respond within 45 days
- **Source:** CCPA 1798.120, CPRA 2023

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
- **Source:** GDPR Art. 28

### PRV-16 [CRITICAL] Data Protection Impact Assessment [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL]
DPIA required for high-risk processing.
- **Detect:**
  - Large-scale processing of sensitive data without documented DPIA
  - Automated decision-making with legal effects
- **Fix:** Conduct DPIA: describe processing, assess necessity, identify risks, define mitigations. Consult DPA if high residual risk
- **Source:** GDPR Art. 35

### PRV-17 [CRITICAL] Breach Notification [FRAMEWORK: GDPR,CCPA,LGPD,PIPL,UK_GDPR,KVKK,PIPA,PDPA]
Timely notification upon data breach.
- **Detect:**
  - No breach notification procedure documented
  - No incident response plan
- **Fix:** GDPR/UK: 72h to authority. CCPA: AG if 500+ CA residents. KVKK: as soon as possible to Board. Implement detection + response plan
- **Source:** GDPR Art. 33-34

### PRV-18 [CRITICAL] Data Portability [FRAMEWORK: GDPR,CCPA,UK_GDPR,LGPD,PIPA]
Users can export their data in machine-readable format.
- **Detect:**
  - No data export feature
  - Search: absence of `data_export`, `download_my_data`, `portability` in account/settings
- **Fix:** Data export in JSON/CSV. "Download My Data" button. Response within 30 days (GDPR) or 45 days (CCPA)
- **Source:** GDPR Art. 20

### PRV-19 [CRITICAL] Consent Withdrawal [FRAMEWORK: GDPR,UK_GDPR,LGPD,PIPL,KVKK,PIPA,PDPA]
Withdrawal as easy as giving consent.
- **Detect:**
  - No withdrawal mechanism
  - Withdrawal harder than consent
- **Fix:** Toggle per purpose in settings. One-tap withdrawal. Stop processing immediately. Log withdrawal timestamp
- **Source:** GDPR Art. 7(3)
