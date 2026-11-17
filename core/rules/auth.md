# Auth — identity, sessions, tokens, access model

Loaded when the project authenticates users (`auth≠none`). Deny-by-default enforcement at the server boundary is SAR-07; auth events in the audit trail are SAR-01; rate limits on login, reset and MFA endpoints are API-05. Rules marked for app-held credentials do not apply when a hosted provider (Firebase, Clerk, Auth0, Supabase, Cognito) stores and checks the passwords.

### AUTH-01 [CRITICAL] Passwords stored with a fast or no hash
applies_when: auth∋session or auth∋jwt or auth∋other
- **Detect:** passwords stored in plaintext, encrypted reversibly, or hashed with MD5, SHA-1/SHA-2, an unsalted hash or a custom scheme; bcrypt below cost 12 or PBKDF2 far below the OWASP iteration count.
- **Mech:** T `git grep -nIiE '(md5|sha-?1|sha256|sha512|createHash|hashlib\.).*pass(word|wd)|pass(word|wd).*(md5|sha-?1|sha256|sha512|createHash|hashlib\.)' -- ':!*.md'`
- **Fix:** Argon2id (OWASP: 19 MiB memory, 2 iterations, 1 lane as the floor), else scrypt, else bcrypt (cost 12 or more, mind its 72-byte input limit); PBKDF2-HMAC-SHA256 only where FIPS requires it. Rehash on the next login when parameters change.
- **Impact:** a leaked fast-hash table is cracked at billions of guesses per second on commodity GPUs.
- **Source:** OWASP Password Storage Cheat Sheet; CWE-916.

### AUTH-02 [CRITICAL] Tokens readable by scripts or kept too long
- **Detect:** session IDs, access or refresh tokens in `localStorage`/`sessionStorage`, in a URL, or in a cookie missing `HttpOnly`, `Secure` or `SameSite`; tokens or personal data in plaintext mobile storage (`SharedPreferences`, `UserDefaults`, a file, an unencrypted SQLite column) instead of the Keychain or Keystore; access tokens living hours or more; refresh tokens that never rotate; logout or password change that leaves the server-side session or refresh token valid.
- **Mech:** T `git grep -nIiE '(localStorage|sessionStorage)\.setItem\(.*(token|jwt|session|auth)|SharedPreferences.*token|UserDefaults.*token|httpOnly[[:space:]]*:[[:space:]]*false|HttpOnly[[:space:]]*=[[:space:]]*False|secure[[:space:]]*:[[:space:]]*false|SameSite[[:space:]]*=[[:space:]]*None' -- ':!*.md'`
- **Fix:** web: a `__Host-`-prefixed `HttpOnly; Secure; SameSite=Lax; Path=/` cookie (the prefix forbids `Domain`, blocking subdomain cookie tossing; `Strict` where no inbound cross-site navigation must keep the session), or a backend-for-frontend holding the tokens; mobile: platform secure storage. Access tokens 5–15 minutes; refresh tokens rotated on every use (AUTH-24); logout and credential change revoke the server-side session and its refresh tokens.
- **Impact:** any injected script exfiltrates a readable token, and a long-lived or unrevoked one keeps working after the user signs out.
- **Source:** Least privilege; OWASP Session Management Cheat Sheet; OWASP MASVS-STORAGE-1; RFC 9700.

### AUTH-17 [MEDIUM] Session ID not regenerated or guessable
applies_when: auth∋session or auth∋other
- **Detect:** the same session identifier before and after login or a privilege change; session IDs under 128 bits of randomness or from a non-cryptographic generator.
- **Mech:** T `git grep -nIE 'session_regenerate_id|regenerate\(|cycle_key|changeSessionId|sessionFixation|renew_session|reset_session' -- ':!*.md'`
- **Fix:** issue a fresh CSPRNG session ID on login and on every privilege change and invalidate the old one server-side; prefer the framework's session store over a hand-made one.
- **Impact:** an attacker who plants or predicts a pre-login session ID inherits the victim's authenticated session.
- **Source:** OWASP Session Management Cheat Sheet (session ID entropy, renewal); CWE-384.

### AUTH-03 [HIGH] OAuth or OIDC flow without PKCE or exact redirects
applies_when: auth∋oauth or auth∋other
- **Detect:** the Implicit grant (`response_type=token`) or Resource Owner Password grant (`grant_type=password`); an authorization-code flow without PKCE S256; redirect URIs matched by prefix, wildcard or substring; missing `state`/`nonce` handling; `iss` not checked when several authorization servers are used; scopes requested beyond what the code uses.
- **Mech:** T `git grep -nIiE 'response_type=token|grant_type=password|code_challenge|redirect_uri|response_type' -- ':!*.md'`
- **Fix:** authorization code + PKCE (S256) for every client type through a maintained library; exact string redirect matching; validate `state`, `nonce` and `iss`; request the smallest scope set.
- **Impact:** intercepted codes, leaked tokens in URLs and redirect manipulation all lead to account takeover.
- **Source:** RFC 9700 (OAuth 2.0 Security Best Current Practice); RFC 7636 (PKCE).

### AUTH-24 [HIGH] Refresh token reuse not detected
applies_when: auth∋jwt or auth∋oauth or auth∋other
- **Detect:** the app issues rotating refresh tokens but accepts, or merely rejects, an already-rotated token without revoking its family.
- **Mech:** M
- **Fix:** link rotated refresh tokens to one family; reuse of a superseded token revokes the family and forces sign-in; public clients use rotation or sender-constrained tokens (DPoP, RFC 9449).
- **Impact:** a stolen refresh token keeps an attacker signed in alongside the user indefinitely.
- **Source:** RFC 9700 (refresh token protection).

### AUTH-04 [HIGH] JWT accepted without full validation
applies_when: auth∋jwt or auth∋oauth or auth∋other
- **Detect:** tokens decoded without signature verification (`jwt.decode` with verification off, `ParseUnverified`); `alg` taken from the token or `none` accepted; `exp`, `nbf`, `iss` or `aud` unchecked; an HMAC key shared with services that only need to verify; personal data placed in the payload.
- **Mech:** T `git grep -nIE 'jwt\.decode\(|ParseUnverified|verify_signature|verify[[:space:]]*=[[:space:]]*False|algorithms[[:space:]]*=|"none"|ignoreExpiration|decode\(.*complete' -- ':!*.md'`
- **Fix:** verify with a server-side algorithm allow-list (ES256, EdDSA or RS256 across services; HS256 only when issuer and verifier are one service) and check `exp`, `nbf`, `iss`, `aud` on every request; keep claims minimal.
- **Impact:** algorithm confusion or skipped checks let anyone forge a token for any user.
- **Source:** Fail fast; RFC 8725 (JWT Best Current Practices); RFC 7519; CWE-347.

### AUTH-05 [HIGH] State-changing requests without CSRF protection
applies_when: ui∋web
- **Detect:** cookie-authenticated `POST`/`PUT`/`PATCH`/`DELETE` handlers with no CSRF token, no `SameSite` cookie attribute and no Origin check; CSRF middleware disabled or exempted per route; state changes on `GET`.
- **Mech:** T `git grep -nIiE 'csrf_exempt|@csrf\.exempt|skip_before_action :verify_authenticity_token|csrf[[:space:]]*:[[:space:]]*false|\.csrf\(\)\.disable|ignoringRequestMatchers'` · `git grep -nIiE 'csrf|SameSite' -- ':!*.md'`
- **Fix:** `SameSite=Lax` cookies plus the framework's CSRF token (synchronizer or signed double-submit) on every unsafe method; verify `Origin`; keep `GET` safe. Token-in-header APIs with no cookie auth are exempt.
- **Impact:** any site the user visits can perform actions in their name.
- **Source:** OWASP CSRF Prevention Cheat Sheet; CWE-352.

### AUTH-06 [MEDIUM] No authorization model beyond "logged in"
- **Detect:** every authenticated user can reach every protected operation; roles or permissions checked only in the client; role names compared ad hoc across handlers with no single definition of who may do what; a model heavier than the product needs (ABAC or relationship-based access with a handful of roles).
- **Mech:** M (route list against the role or permission definitions)
- **Fix:** one permission table (role → actions) enforced by the central policy layer of SAR-07; flat roles until a concrete need for groups, attributes or relationships; per-tenant roles in a membership table for multi-tenant products.
- **Impact:** any account reaches admin functions, and ad-hoc checks drift until one route is forgotten.
- **Source:** DRY / single source of truth; Least privilege; OWASP API5:2023 Broken Function Level Authorization; NIST RBAC model (csrc.nist.gov).

### AUTH-11 [CRITICAL] Object or tenant access not tied to the caller
- **Detect:** a handler loading, updating or deleting a record, file or storage key by an ID from the request with no ownership or tenant filter (`WHERE owner_id = :me`, a policy check); tenant ID taken from the request body instead of the session; queries in a multi-tenant schema missing the tenant column; row-level security disabled or open (`USING (true)`), Firebase/Supabase rules that allow any signed-in user; no cross-user test.
- **Mech:** T `git grep -nIE '(findById|findByPk|find_by_id|findUnique|findOne|get_object_or_404|objects\.get|\.get)\(([[:space:]]*[a-z_]+[[:space:]]*=)?[[:space:]]*(req\.(params|query|body)|request\.(args|GET|POST|json)|params\[|ctx\.params)' -- ':!*test*' ':!*.md'` · `git grep -nIE 'USING[[:space:]]*\([[:space:]]*true[[:space:]]*\)|allow read, write: if (true|request\.auth != null)|DISABLE ROW LEVEL SECURITY'`
- **Fix:** scope every lookup by the caller (owner or tenant from the session) or pass it through a policy check; enable row-level security or database rules that encode the same; add the cross-user test: user A creates R, user B requests R by ID, expect 403 or 404.
- **Impact:** any signed-in user reads or changes other users' or tenants' data by changing an ID.
- **Source:** Least privilege; OWASP API1:2023 Broken Object Level Authorization; CWE-639; CVE-2025-48757 (open Supabase RLS).

### AUTH-18 [HIGH] Password policy contradicts NIST SP 800-63B-4
applies_when: auth∋session or auth∋jwt or auth∋other
- **Detect:** composition rules (must include upper case, digit, symbol); forced periodic change without evidence of compromise; a minimum below 15 characters for password-only accounts (8 with MFA); a maximum below 64 characters or rejected spaces and Unicode; no check against a breached-password list; password hints or security questions.
- **Mech:** T `git grep -nIiE 'AUTH_PASSWORD_VALIDATORS|PasswordValidator|minlength|min_length|minLength|max_?length.*pass|(uppercase|special char|symbol).*(required|must)|password_expir|security_question' -- ':!*.md'`
- **Fix:** length-based policy per SP 800-63B-4; screen new passwords against a breached list (a bundled corpus or a k-anonymity range lookup); allow paste and password managers; remove rotation, composition rules, hints and questions.
- **Impact:** outdated rules push users to predictable patterns and reuse, which is weaker than a long free-form passphrase.
- **Source:** NIST SP 800-63B-4 (pages.nist.gov/800-63-4/sp800-63b.html).

### AUTH-19 [HIGH] MFA weaker than it looks
applies_when: auth∋session or auth∋jwt or auth∋other
- **Detect:** TOTP checked with no ±1 step skew window, or with replay of a used code allowed; recovery codes stored in plaintext or reusable; factor-specific failure messages; no attempt limit on the second factor; a re-enrolment that reuses the old seed; SMS as the only second factor where account value is high.
- **Mech:** T `git grep -nIiE 'totp|otpauth|pyotp|otplib|speakeasy|recovery.?codes?|backup.?codes?' -- ':!*.md'`
- **Fix:** RFC 6238 TOTP accepting the current step ±1 and rejecting reuse; 8–10 single-use recovery codes stored hashed; generic failure messages and an attempt limit (API-05); a fresh seed on re-enrolment; offer a phishing-resistant factor (WebAuthn passkey) where the account guards money or sensitive data.
- **Impact:** the bypass path (recovery codes, unlimited guesses) becomes the weakest link of the account.
- **Source:** RFC 6238; OWASP Multifactor Authentication Cheat Sheet; NIST SP 800-63B-4 (authenticator types).

### AUTH-21 [HIGH] Account enumeration or weak reset tokens
applies_when: auth∋session or auth∋jwt or auth∋other
- **Detect:** login, signup or reset responses that differ (message, status or timing) between existing and unknown accounts; reset tokens with no expiry, longer than about an hour, reusable after use, not invalidated by a newer one, or guessable; a reset that does not end other sessions.
- **Mech:** T `git grep -nIiE 'reset.?(password|token)|forgot.?password|user not found|no account|wrong password|email (already )?(exists|registered)' -- ':!*.md'`
- **Fix:** one generic response and similar timing for every case; single-use CSPRNG reset tokens stored hashed, short-lived and sent only to the verified address; redeem via POST and revoke other sessions on success.
- **Impact:** an enumerable endpoint hands attackers a list of real accounts; a lingering reset token is a standing takeover credential.
- **Source:** OWASP Forgot Password Cheat Sheet; OWASP Authentication Cheat Sheet (authentication and error messages); CWE-204, CWE-640.

### AUTH-20 [MEDIUM] API keys stored or rotated unsafely
applies_when: api≠none
- **Detect:** API keys the product issues stored in plaintext; one key per account so rotation breaks every integration; keys with no type or environment prefix; the full key logged or shown after creation; keys with all permissions; a routine rotation that kills the old key at once, or a leaked key left valid during an overlap window.
- **Mech:** T `git grep -nIiE 'api_?key' -- ':!*test*' ':!*.md' ':!*lock*'`
- **Fix:** prefixed keys (`live_`/`test_`), stored as a hash and shown once; several active keys per account with scopes; routine rotation adds the new key, migrates callers, then revokes the old; a confirmed leak is revoked immediately with no overlap; logs carry the prefix and last four characters only.
- **Impact:** a leaked key that cannot be identified, scoped or rotated forces an all-or-nothing incident response.
- **Source:** Least privilege; OWASP REST Security Cheat Sheet (API keys); OWASP API2:2023 Broken Authentication.

### AUTH-23 [MEDIUM] Open redirect after login, logout or OAuth
- **Detect:** a `next`, `return_to`, `returnUrl`, `redirect` or `redirect_uri` value from the request used to redirect without exact allow-list matching; validation by `startsWith`, substring or regex on the host.
- **Mech:** T `git grep -nIiE 'redirect\((req|request)\.(query|args|params|GET|body)|(next|return_?to|returnUrl|redirect_?(uri|url|to))[[:space:]]*=[[:space:]]*(req|request|params|query|searchParams)' -- ':!*.md'`
- **Fix:** accept only relative paths or an exact allow-list of absolute URIs; otherwise fall back to a fixed default.
- **Impact:** the trusted domain becomes a phishing launchpad and can leak OAuth codes to an attacker.
- **Source:** OWASP Unvalidated Redirects and Forwards Cheat Sheet; CWE-601.
