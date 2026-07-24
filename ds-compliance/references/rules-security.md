# Rules: Security

CLI/library-specific security subset. These rules apply to non-web, non-API projects (CLIs, libraries, dev tools). For full security rules including web and API, see `rules-compliance.md`.

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

> **Edition note (2026-07-17):** Category IDs below cite OWASP Top 10 **2025** (first revision since 2021; distinct from the API Security Top 10 2023) — verified against [owasp.org/Top10/2025](https://owasp.org/Top10/2025/). Remap applied: A02:2021→A04:2025 (Crypto), A03:2021→A05:2025 (Injection), A05:2021→A02:2025 (Misconfig), A06:2021→A03:2025 (Software Supply Chain Failures), A07:2021→A07:2025 (Authentication Failures); SSRF (A10:2021) absorbed into A01:2025.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | CSEC-01–03, CSEC-05, CSEC-06, CSEC-08–11 (3 BLOCKER, 3 CRITICAL, 1 HIGH, 2 MEDIUM) | ~12 |

---

## Security

### CSEC-01 [BLOCKER] Secure Credential Storage
Credentials, tokens, and secrets must not be in plaintext files or unencrypted storage.
- **Detect:**
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git (not in `.gitignore`)
  - Search: passwords/tokens in config files, database connection strings with embedded credentials
  - Plaintext secrets in config files
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Use environment variables loaded at runtime. Use secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Doppler). Add `.env` to `.gitignore`
- **Source:** OWASP A07:2025 (Authentication Failures)

### CSEC-02 [BLOCKER] No Hardcoded Credentials
Zero secrets in source code.
- **Detect:**
  - Search: `apiKey\s*[:=]`, `api_key\s*[:=]`, `secret\s*[:=]`, `password\s*[:=]`, `bearer\s`, `sk-[a-zA-Z0-9]`, `AKIA[A-Z0-9]`, base64 patterns >20 chars in string literals
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Move to environment variables or secret manager. Add to `.gitignore`
- **Source:** OWASP A07:2025 (Authentication Failures)

### CSEC-03 [BLOCKER] Debug Mode Off in Production
No debug features exposed in production builds.
- **Detect:**
  - Python: `DEBUG = True` in settings, `FLASK_DEBUG=1`
  - Node: missing `NODE_ENV=production`, verbose logging in production
  - Go: `debug` flags in production configs
  - Verbose error output exposing internals
- **Fix:** Environment-based config. Strip debug code in production builds. Never expose stack traces to users
- **Source:** OWASP A02:2025 (Security Misconfiguration)

### CSEC-05 [CRITICAL] Input Validation & Injection Prevention
All user input validated and sanitized. No raw interpolation in queries or commands.
- **Detect:**
  - Raw user input in shell commands (`exec`, `os.system`, `child_process.exec`)
  - No input validation on CLI arguments
  - Search: `eval(`, `Function(` with user input
  - Unsanitized file paths from user input (path traversal)
- **Fix:** Input validation with schemas (Zod, Pydantic). Never interpolate user input into shell commands. Use subprocess with argument lists (not shell=True). Validate and sanitize file paths
- **Impact:** Command injection through CLI arguments = full system compromise
- **Source:** OWASP A05:2025 (Injection)

### CSEC-06 [CRITICAL] Strong Cryptography
AES-256-GCM symmetric. No MD5/SHA-1 for security. No custom crypto.
- **Detect:**
  - Search: `MD5`, `SHA1`, `SHA-1` in non-checksum context, `ECB` mode, `DES`, `RC4`, hardcoded IV/nonce
  - Custom crypto implementations
  - Weak password hashing (plain SHA-256 without salt/iteration)
- **Fix:** Use platform crypto libraries. Password hashing: bcrypt/scrypt/argon2. Encryption: AES-256-GCM. Use random IV/nonce per operation
- **Source:** OWASP A04:2025 (Cryptographic Failures)

### CSEC-08 [CRITICAL] Supply Chain Security
Dependencies audited, versions pinned, lockfile committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile (package-lock.json, yarn.lock, pnpm-lock.yaml, Pipfile.lock, poetry.lock, go.sum) in git
- **Fix:** Pin exact versions. Commit lockfiles. Run `npm audit` / `pip audit` / `safety check` regularly
- **Source:** OWASP A03:2025 (Software Supply Chain Failures)

### CSEC-09 [MEDIUM] Controls Scale to the Real Threat Model; No Cargo-Cult Layers
Security/resilience controls map to the actual deployment threat model: best-effort hardening where it pays, no ritual layers that deliver nothing, removals documented with rationale.
- **Detect:** Controls copied from a different deployment shape (app-layer cert pinning behind a CDN that rotates edge certs autonomously; mlockall/TLS/circuit breakers inside a same-host deployment); genuinely sensitive buffers left unzeroed; removed controls with no recorded reasoning.
- **Fix:** Match each control to the real threat model. Add best-effort defenses where the asset warrants them (zero sensitive buffers; never throw on cleanup failure, never pass silently either). Remove or decline layers with no concrete benefit in this topology, and document the rationale. Re-evaluate only when the threat model actually changes (multi-host, external network hop, shared tenancy).
- **Impact:** Cargo-cult layers consume maintenance and mask real gaps; the documented-rationale rule prevents the next audit from re-adding a deliberately removed control as a "finding".
- **Source:** XR-019 — cross-project experience registry (2026).

### CSEC-10 [HIGH] Crypto Components Get One Independent External Review Before Production-Final
In products carrying sensitive/health data, cryptographic components (key wrapping, HKDF, role-bound envelopes/keyrings, OAuth PKCE implementation) are not production-final on self-assessment alone: at least one independent third-party review is obtained and its findings folded back in.
- **Detect:** Custom or assembled crypto (key hierarchies, envelope schemes) validated only by the team that built it; "audited" claims tracing to internal review; external findings received but not mapped to decisions.
- **Fix:** Commission one independent security review of the crypto layer before declaring it production-final; record the findings and the disposition of each in the security decision log. Internal review gates development; external review gates the production-final claim.
- **Impact:** Crypto is the domain where self-assessment fails silently — a subtle key-derivation flaw invalidates every guarantee built on it, and only fresh outside eyes reliably catch it.
- **Source:** XR-127 — cross-project experience registry (2026).

### CSEC-11 [MEDIUM] Cross-Platform Security Asymmetry Documented Honestly
When a security control is materially stronger on one platform than another, the asymmetry is documented explicitly — never presented as equal protection.
- **Detect:** One security bullet covering all platforms while implementations differ (hard OS-enforced flag on platform A, best-effort emulation on platform B because the OS API doesn't exist); policy/marketing text asserting uniform protection.
- **Fix:** Document per-platform control strength side by side: what is enforced, what is best-effort, what is absent and why (missing OS API). Propagate the honest version into user-facing security claims.
- **Impact:** Asserted-but-absent protection on the weaker platform is a misleading security claim — discovered in an incident, it converts a technical limitation into a credibility and liability problem.
- **Source:** XR-034 — cross-project experience registry (2026).
