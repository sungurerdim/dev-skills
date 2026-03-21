# Rules: Security

CLI/library-specific security subset. These rules apply to non-web, non-API projects (CLIs, libraries, dev tools). For full security rules including web and API, see `rules-compliance.md`.

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Security** | SEC-01–03, SEC-05, SEC-06, SEC-08 (2 BLOCKER, 2 CRITICAL, 2 CRITICAL) | ~12 |

---

## Security

### SEC-01 [BLOCKER] Secure Credential Storage
Credentials, tokens, and secrets must not be in plaintext files or unencrypted storage.
- **Detect:**
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git (not in `.gitignore`)
  - Search: passwords/tokens in config files, database connection strings with embedded credentials
  - Plaintext secrets in config files
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Use environment variables loaded at runtime. Use secret managers (Vault, AWS Secrets Manager, GCP Secret Manager, Doppler). Add `.env` to `.gitignore`
- **Source:** OWASP A07:2021

### SEC-02 [BLOCKER] No Hardcoded Credentials
Zero secrets in source code.
- **Detect:**
  - Search: `apiKey\s*[:=]`, `api_key\s*[:=]`, `secret\s*[:=]`, `password\s*[:=]`, `bearer\s`, `sk-[a-zA-Z0-9]`, `AKIA[A-Z0-9]`, base64 patterns >20 chars in string literals
  - Files: `**/.env`, `**/credentials*`, `**/secrets*` committed to git
  - Exclude: `.env.example`, test fixtures with dummy values
- **Fix:** Move to environment variables or secret manager. Add to `.gitignore`
- **Source:** OWASP A07:2021

### SEC-03 [BLOCKER] Debug Mode Off in Production
No debug features exposed in production builds.
- **Detect:**
  - Python: `DEBUG = True` in settings, `FLASK_DEBUG=1`
  - Node: missing `NODE_ENV=production`, verbose logging in production
  - Go: `debug` flags in production configs
  - Verbose error output exposing internals
- **Fix:** Environment-based config. Strip debug code in production builds. Never expose stack traces to users
- **Source:** OWASP A05:2021

### SEC-05 [CRITICAL] Input Validation & Injection Prevention
All user input validated and sanitized. No raw interpolation in queries or commands.
- **Detect:**
  - Raw user input in shell commands (`exec`, `os.system`, `child_process.exec`)
  - No input validation on CLI arguments
  - Search: `eval(`, `Function(` with user input
  - Unsanitized file paths from user input (path traversal)
- **Fix:** Input validation with schemas (Zod, Pydantic). Never interpolate user input into shell commands. Use subprocess with argument lists (not shell=True). Validate and sanitize file paths
- **Impact:** Command injection through CLI arguments = full system compromise
- **Source:** OWASP A03:2021

### SEC-06 [CRITICAL] Strong Cryptography
AES-256-GCM symmetric. No MD5/SHA-1 for security. No custom crypto.
- **Detect:**
  - Search: `MD5`, `SHA1`, `SHA-1` in non-checksum context, `ECB` mode, `DES`, `RC4`, hardcoded IV/nonce
  - Custom crypto implementations
  - Weak password hashing (plain SHA-256 without salt/iteration)
- **Fix:** Use platform crypto libraries. Password hashing: bcrypt/scrypt/argon2. Encryption: AES-256-GCM. Use random IV/nonce per operation
- **Source:** OWASP A02:2021

### SEC-08 [CRITICAL] Supply Chain Security
Dependencies audited, versions pinned, lockfile committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile (package-lock.json, yarn.lock, pnpm-lock.yaml, Pipfile.lock, poetry.lock, go.sum) in git
- **Fix:** Pin exact versions. Commit lockfiles. Run `npm audit` / `pip audit` / `safety check` regularly
- **Source:** OWASP A06:2021
