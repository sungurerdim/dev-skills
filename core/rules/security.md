# Rules: Security

Applies to every project type (web, API, mobile, CLI, library). Platform-specific detects sit in each rule; CLI/library specifics are marked.

> **Edition note (2026-07-17):** Category IDs below cite OWASP Top 10 **2025** (first revision since 2021; distinct from the API Security Top 10 2023) — verified against [owasp.org/Top10/2025](https://owasp.org/Top10/2025/). Remap applied: A02:2021→A04:2025 (Crypto), A03:2021→A05:2025 (Injection), A05:2021→A02:2025 (Misconfig), A06:2021→A03:2025 (Software Supply Chain Failures), A07:2021→A07:2025 (Authentication Failures); SSRF (A10:2021) absorbed into A01:2025.

## Security

Baseline: OWASP ASVS 5.0.0 (May 2025 — ~350 requirements, 17 categories). OSS DAST tools (ZAP, Nikto) still emit 4.0.3-tagged findings as of mid-2026 — label tool output with the tool's ASVS version; never present 4.0.3 tool findings as ASVS 5.0 coverage.

### SEC-01 [CRITICAL] Secure Credential Storage
applies_when: always
Credentials, tokens, and secrets must not be in plaintext files or unencrypted storage.
- **Detect:**
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git (not in `.gitignore`)
  - Search: passwords/tokens in config files, database connection strings with embedded credentials
  - Plaintext secrets in `application.yml`, `settings.py`, `config/*.json`
  - Exclude: `.env.example`, test fixtures with dummy values
  - Plaintext secrets in config files
- **Fix:** Use environment variables loaded at runtime. Use secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Doppler). Add `.env` to `.gitignore`. For Docker: use secrets, not ENV in Dockerfile
- **Impact:** A plaintext or committed credential is readable by anyone with repo/filesystem access, including in git history long after the file appears fixed.
- **Source:** OWASP A07:2025 (Authentication Failures)

### SEC-02 [CRITICAL] No Hardcoded Credentials
applies_when: always
Zero secrets in source code.
- **Detect:**
  - Search: `apiKey\s*[:=]`, `api_key\s*[:=]`, `secret\s*[:=]`, `password\s*[:=]`, `bearer\s`, `sk-[a-zA-Z0-9]`, `AKIA[A-Z0-9]`, base64 patterns >20 chars in string literals
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Move to environment variables or secret manager. Add to `.gitignore`. Use server-side proxy for third-party API keys
- **Impact:** A hardcoded secret ships inside the source and leaks to every clone, fork, and build artifact — rotation requires a code change, not just a config change.
- **Source:** OWASP A07:2025 (Authentication Failures)

### SEC-03 [CRITICAL] Debug Mode Off in Production
applies_when: always
No debug features exposed in production builds.
- **Detect:**
  - Python: `DEBUG = True` in settings, `FLASK_DEBUG=1`
  - Node: missing `NODE_ENV=production`, `console.log` in production paths
  - Go: `debug` flags in production configs
  - Java/Kotlin: `debug=true` in application.properties
  - Stack traces exposed in error responses
  - Verbose error output exposing internals
  - Android: `android:debuggable="true"` in AndroidManifest.xml
  - iOS: check build configuration for DEBUG symbols in release
  - Flutter: `kDebugMode` used in release-visible code paths
- **Fix:** Environment-based config. Strip debug code in production builds. Never expose stack traces to clients
- **Impact:** Debug mode in production exposes stack traces, internal routes, and in some frameworks a live code-execution console directly to attackers.
- **Source:** OWASP A02:2025 (Security Misconfiguration)

### SEC-04 [CRITICAL] TLS Enforced
applies_when: api≠none or deploy≠none
All connections over HTTPS. No plaintext HTTP in production.
- **Detect:**
  - Search: `http://` URLs in source (excluding localhost/127.0.0.1/10.0/192.168)
  - No HTTPS redirect configuration
  - Missing HSTS headers
  - Android: `android:usesCleartextTraffic="true"` in AndroidManifest.xml, or missing `network_security_config.xml`
  - iOS: `NSAllowsArbitraryLoads` = YES in Info.plist
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
  - No input validation on CLI arguments
  - Unsanitized file paths from user input (path traversal)
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
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound in pubspec.yaml/package.json/build.gradle
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

### SEC-15 [MEDIUM] Controls Scale to the Real Threat Model; No Cargo-Cult Layers
Security/resilience controls map to the actual deployment threat model: best-effort hardening where it pays, no ritual layers that deliver nothing, removals documented with rationale.
- **Detect:** Controls copied from a different deployment shape (app-layer cert pinning behind a CDN that rotates edge certs autonomously; mlockall/TLS/circuit breakers inside a same-host deployment); genuinely sensitive buffers left unzeroed; removed controls with no recorded reasoning.
- **Fix:** Match each control to the real threat model. Add best-effort defenses where the asset warrants them (zero sensitive buffers; never throw on cleanup failure, never pass silently either). Remove or decline layers with no concrete benefit in this topology, and document the rationale. Re-evaluate only when the threat model actually changes (multi-host, external network hop, shared tenancy).
- **Impact:** Cargo-cult layers consume maintenance and mask real gaps; the documented-rationale rule prevents the next audit from re-adding a deliberately removed control as a "finding".
- **Source:** XR-019 — cross-project experience registry (2026).

### SEC-16 [HIGH] Crypto Components Get One Independent External Review Before Production-Final
In products carrying sensitive/health data, cryptographic components (key wrapping, HKDF, role-bound envelopes/keyrings, OAuth PKCE implementation) are not production-final on self-assessment alone: at least one independent third-party review is obtained and its findings folded back in.
- **Detect:** Custom or assembled crypto (key hierarchies, envelope schemes) validated only by the team that built it; "audited" claims tracing to internal review; external findings received but not mapped to decisions.
- **Fix:** Commission one independent security review of the crypto layer before declaring it production-final; record the findings and the disposition of each in the security decision log. Internal review gates development; external review gates the production-final claim.
- **Impact:** Crypto is the domain where self-assessment fails silently — a subtle key-derivation flaw invalidates every guarantee built on it, and only fresh outside eyes reliably catch it.
- **Source:** XR-127 — cross-project experience registry (2026).

### SEC-17 [MEDIUM] Cross-Platform Security Asymmetry Documented Honestly
When a security control is materially stronger on one platform than another, the asymmetry is documented explicitly — never presented as equal protection.
- **Detect:** One security bullet covering all platforms while implementations differ (hard OS-enforced flag on platform A, best-effort emulation on platform B because the OS API doesn't exist); policy/marketing text asserting uniform protection.
- **Fix:** Document per-platform control strength side by side: what is enforced, what is best-effort, what is absent and why (missing OS API). Propagate the honest version into user-facing security claims.
- **Impact:** Asserted-but-absent protection on the weaker platform is a misleading security claim — discovered in an incident, it converts a technical limitation into a credibility and liability problem.
- **Source:** XR-034 — cross-project experience registry (2026).
