# Rules: Authentication & Authorization

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Authentication** | AUTH-01 to AUTH-25 (3 CRITICAL, 10 HIGH, 8 MEDIUM, 4 LOW) | ~12 |

---

## Authentication

### AUTH-01 [CRITICAL] Password Hashing
**Detect:** Passwords hashed with MD5, SHA-1, SHA-256, or any unsalted/fast hash. Plaintext password storage. Custom hashing schemes.

**Fix:** Use Argon2id (preferred) or bcrypt (legacy systems) with OWASP-recommended parameters.

| Algorithm | Priority | Parameters | Notes |
|-----------|----------|------------|-------|
| Argon2id | 1st (default) | `m=47104 (46 MiB), t=1, p=1` or `m=19456 (19 MiB), t=2, p=1` | PHC 2015 winner; resists GPU + side-channel |
| scrypt | 2nd | `N=2^17, r=8, p=1` | When Argon2 unavailable |
| bcrypt | 3rd (legacy) | cost=12 minimum | 72-byte input limit; legacy systems only |
| PBKDF2 | 4th (FIPS) | 600K+ iterations | FIPS-140 compliance only |

**Multi-stack examples:**

- **Node:** `argon2.hash(password, { type: argon2.argon2id, memoryCost: 47104, timeCost: 1 })`
- **Python:** `argon2-cffi` with `PasswordHasher(memory_cost=47104, time_cost=1)`
- **Go:** `golang.org/x/crypto/argon2` with `IDKey(password, salt, 1, 47104, 1, 32)`
- **Java/Spring:** `Argon2PasswordEncoder(1, 47104, 1, 32, 1)` or `BCryptPasswordEncoder(12)`
- **Ruby:** `argon2` gem with `Argon2::Password.create(password)`
- **PHP:** `password_hash($password, PASSWORD_ARGON2ID)` (PHP 7.3+)

**Impact:** Fast hashes (MD5, SHA-family) allow billions of guesses per second on modern GPUs. Argon2id with proper memory cost limits attackers to few hundred attempts per second per GPU.

**Source:** [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
---

### AUTH-02 [CRITICAL] Token Storage
**Detect:** Auth tokens (JWTs, session IDs) stored in `localStorage`, `sessionStorage`, or cookies without `HttpOnly`/`Secure`/`SameSite` flags. Mobile apps storing tokens in plaintext shared preferences.

**Fix:** Web: `httpOnly + Secure + SameSite` cookies. Mobile: platform keychain/keystore.

| Location | XSS Safe | CSRF Safe | Recommendation |
|----------|----------|-----------|----------------|
| httpOnly cookie | Yes | Needs CSRF protection | Best for web apps |
| Memory (JS variable) | Short-lived exposure | Yes | Acceptable for SPAs with short-lived tokens |
| localStorage | No | Yes | Avoid for auth tokens |
| sessionStorage | No | Yes | Avoid for auth tokens |

Cookie configuration:
```
Set-Cookie: session_id=<value>;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/;
  Max-Age=86400
```

| Token | Lifetime | Storage |
|-------|----------|---------|
| Access token | 5-15 minutes | Memory (SPA) or httpOnly cookie |
| Refresh token | 7-30 days | httpOnly, Secure, SameSite=Strict cookie |
| ID token (OIDC) | Match access token | Memory; used once to establish session |

**Impact:** Tokens in localStorage are readable by any JavaScript on the page, including injected XSS payloads. httpOnly cookies inaccessible to JavaScript entirely.

**Source:** [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
---

### AUTH-03 [HIGH] OAuth 2.0 / OIDC
**Detect:** Custom authentication flows instead of OIDC for third-party login. Deprecated OAuth grants (Implicit, ROPC). PKCE missing from Authorization Code flow.

**Fix:** Use Authorization Code + PKCE (S256) for all client types. RFC 9700 (January 2025) codifies this as only recommended flow.

PKCE flow summary:
1. Client generates `code_verifier` (43-128 char random string)
2. Client computes `code_challenge = BASE64URL(SHA256(code_verifier))`
3. Authorization request includes `code_challenge` + `code_challenge_method=S256`
4. Token exchange includes `code_verifier` (server verifies against stored challenge)

RFC 9700 compliance checklist:
- Use PKCE with S256 for all client types (including confidential)
- Enforce exact redirect URI matching (no wildcards)
- Rotate refresh tokens on every use (one-time use)
- Set access token lifetimes to 5-15 minutes
- Validate `iss` claim when using multiple authorization servers

**Impact:** Implicit and ROPC grants expose tokens in URLs or require password sharing. Authorization Code + PKCE prevents authorization code interception and works securely for all client types.

**Source:** [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749), [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://datatracker.ietf.org/doc/rfc9700/) (OAuth 2.1 remains an IETF draft consolidating the same rules)
---

### AUTH-04 [HIGH] JWT Validation
**Detect:** JWTs decoded without signature verification. `alg=none` accepted. Missing validation of `exp`, `iss`, or `aud` claims. Symmetric algorithm (HS256) used when asymmetric is appropriate.

**Fix:** Validate all claims on every request. Maintain server-side algorithm allowlist.

Required validations per request:
- **`alg`**: Match against server-side allowlist (RS256, ES256, EdDSA). Reject `none`.
- **`exp`**: Reject expired tokens.
- **`iss`**: Match expected issuer.
- **`aud`**: Match your API's audience identifier.
- **`nbf`**: Reject tokens used before their "not before" time.

Signing algorithm selection:

| Algorithm | Type | Use Case |
|-----------|------|----------|
| ES256 | Asymmetric (ECDSA) | Preferred for new systems (smaller tokens, fast) |
| RS256 | Asymmetric (RSA) | Default; public key verification without shared secrets |
| EdDSA | Asymmetric (Ed25519) | Best performance, smallest keys |
| HS256 | Symmetric (HMAC) | Only when issuer and verifier are same service |

Keep JWT payloads small: `sub`, `iss`, `aud`, `exp`, `iat`, `jti`, and role/scope. Avoid storing PII (email, name) in JWTs -- they are base64-encoded, not encrypted.

**Impact:** JWT algorithm confusion is CRITICAL vulnerability. Accepting `alg=none` or failing to verify signatures allows token forgery.

**Source:** [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519), [RFC 8725 — JWT Best Current Practices](https://datatracker.ietf.org/doc/html/rfc8725) (a bis revision adding algorithm-confusion + JWE compression-DoS defenses is in IETF draft as of mid-2026)
---

### AUTH-05 [HIGH] CSRF Protection
**Detect:** State-changing endpoints (`POST`, `PUT`, `DELETE`) that accept requests without CSRF token validation or SameSite cookie protection.

**Fix:** Use `SameSite=Lax` cookies (modern approach) combined with CSRF tokens for defense-in-depth.

| Protection | Coverage | Notes |
|------------|----------|-------|
| `SameSite=Lax` | Blocks most CSRF | Allows top-level GET navigations |
| `SameSite=Strict` | Blocks all cross-site | Breaks OAuth redirects; use carefully |
| Synchronizer Token | Full | Traditional; required for legacy browser support |
| Double Submit Cookie | Full | Stateless alternative to synchronizer |
| Origin/Referer check | Defense-in-depth | Verify on all state-changing requests |

**Multi-stack examples:**

- **Node/Express:** `csurf` middleware (deprecated; use `csrf-csrf` or `csrf-sync`) + `SameSite=Lax` cookies
- **Python/Django:** Built-in CSRF middleware (enabled by default)
- **Python/FastAPI:** Manual CSRF token in cookie + header comparison
- **Go/Gin:** `gorilla/csrf` middleware
- **Java/Spring:** Spring Security CSRF (enabled by default for server-rendered)
- **Ruby/Rails:** `protect_from_forgery` (enabled by default)

PKCE replaces CSRF tokens in OAuth flows (per RFC 9700).

**Impact:** CSRF attacks trick authenticated users into performing unintended actions. Single missing CSRF check on sensitive endpoint enables account takeover or data manipulation.

**Source:** [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
---

### AUTH-06 [MEDIUM] RBAC / Authorization
**Detect:** Authorization checks missing on protected endpoints. All-or-nothing authentication (logged in = full access). Role checks performed only on client side.

**Fix:** Implement middleware-based RBAC with server-side enforcement on every request. Deny by default — require explicit grants.

| Model | Complexity | Best For |
|-------|-----------|----------|
| Flat roles | Low | MVPs, small apps (`admin`, `user`, `viewer`) |
| Hierarchical roles | Medium | Organizations (`superadmin > admin > editor > viewer`) |
| Group-based | Medium | Multi-tenant SaaS (roles scoped to org) |
| ABAC | High | Fine-grained, context-dependent rules |
| ReBAC | High | Social/collaborative apps (Google Docs-style) |

Implementation: Schema uses `users`, `organizations`, `memberships(user_id, org_id, role)`, `permissions(role, resource, action)`. Check permissions in middleware, not in route handlers.

For solo dev with fewer than 5 roles: flat RBAC with `role` column on user table. For multi-tenant SaaS: group-based RBAC with `memberships` table. Avoid ABAC/ReBAC until simpler models become demonstrable bottleneck.

**Impact:** Missing server-side authorization is most common API vulnerability (OWASP API1: BOLA accounts for 40% of all API attacks).

**Source:** [NIST RBAC Model](https://csrc.nist.gov/projects/role-based-access-control)
---

### AUTH-07 [MEDIUM] Auth Rate Limiting
**Detect:** Login, registration, password reset, and MFA endpoints without rate limiting. No account lockout or progressive delay on failed attempts.

**Fix:** Apply per-endpoint rate limits with progressive delay on auth-related routes.

| Measure | Implementation |
|---------|---------------|
| Login attempts | Max 5 failures per 15 minutes per account, then progressive delay |
| Registration | Max 3 accounts per IP per hour |
| Password reset | Max 3 requests per email per hour |
| MFA attempts | Max 5 failures per 15 minutes, then temporary lockout |
| API key auth | Per-key and per-IP sliding window counters |

Return `429 Too Many Requests` with `Retry-After` header. Use sliding window counters (Redis `INCR` + `EXPIRE` or equivalent).

Error messages must be generic: "Invalid credentials" rather than "Wrong password" or "User not found". This prevents user enumeration.

**Impact:** Authentication endpoints are primary target for credential stuffing and brute-force attacks. Without rate limiting, attackers can attempt millions of passwords per hour.

**Source:** [OWASP Credential Stuffing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html)
---

### AUTH-08 [LOW] Session vs JWT Decision
**Detect:** JWT used where server sessions would be simpler, or sessions used where JWT is required. Architecture mismatch between auth mechanism and application type.

**Fix:** Use this decision tree:

| Scenario | Recommended Auth | Rationale |
|----------|-----------------|-----------|
| Server-rendered web app | Server sessions + httpOnly cookies | Instant revocation, small payload, low XSS risk |
| SPA calling same-origin API | Server sessions + httpOnly cookies (proxy) | Same benefits via BFF pattern |
| SPA calling cross-origin API | Hybrid: session for BFF, short-lived JWT for downstream | Best of both approaches |
| Mobile app or third-party API | JWT with refresh token rotation | Stateless, cross-origin compatible |
| Microservices inter-service | JWT (5 min expiry) + mTLS | Stateless verification, transport security |

| Criteria | Sessions | JWT |
|----------|----------|-----|
| State storage | Server-side (Redis/DB) | Client-side (token) |
| Scalability | Requires shared store | Scales horizontally |
| Revocation | Instant (delete session) | Requires blocklist or short expiry |
| Payload size | ~32 bytes cookie | ~800+ bytes |
| XSS risk | Low (httpOnly) | High if in localStorage |

Default for solo developers: server sessions with httpOnly cookies. Add JWT only with concrete cross-origin or mobile requirement.

**Impact:** Wrong auth mechanism → unnecessary complexity (JWT for simple web app) or security gaps (sessions without shared store in distributed system).

**Source:** [Auth0 Session vs JWT comparison](https://auth0.com/blog/)
---

### AUTH-09 [LOW] Passkey Support (WebAuthn)
**Detect:** Auth system relies solely on passwords with no passwordless option. No WebAuthn/FIDO2 integration. Users cannot register platform authenticators (biometrics, security keys).

**Fix:** Add WebAuthn/passkey as secondary authentication method alongside existing password auth.

| Aspect | Detail |
|--------|--------|
| Protocol | WebAuthn Level 2 (W3C) / FIDO2 |
| Authenticator types | Platform (biometric: Touch ID, Face ID, Windows Hello) + Roaming (security keys) |
| Registration flow | Server generates challenge -> client calls `navigator.credentials.create()` -> server stores public key |
| Auth flow | Server generates challenge -> client calls `navigator.credentials.get()` -> server verifies signature |
| Credential storage | Store credential ID + public key server-side. Never store private key (it never leaves the authenticator) |

**Multi-stack examples:**

- **Node:** `@simplewebauthn/server` + `@simplewebauthn/browser`
- **Python:** `py_webauthn`
- **Go:** `go-webauthn/webauthn`
- **Java/Spring:** Spring Security WebAuthn support (Spring Security 6.4+)
- **Ruby:** `webauthn-ruby` gem

Implementation priority: offer passkeys as optional upgrade during login, not mandatory. Support credential syncing (iCloud Keychain, Google Password Manager) for cross-device passkeys.

**Impact:** Passkeys eliminate phishing attacks entirely (credential is domain-bound). No password = no credential stuffing. Platform support reached critical mass in 2024-2025 (iOS 16+, Android 9+, Windows 10+, all major browsers).

**Source:** [W3C WebAuthn Specification](https://www.w3.org/TR/webauthn-2/), [FIDO Alliance Passkeys](https://fidoalliance.org/passkeys/), [OWASP WebAuthn Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

---

### AUTH-10 [LOW] Social Login Integration
**Detect:** Custom social login flow not using standard OIDC/OAuth 2.0. Social auth implemented without platform SDK. Missing email scope in social login (no fallback identifier). Social login as sole auth method without account linking.

**Fix:** Use platform SDKs with Authorization Code + PKCE flow. Require email scope minimum for account identification.

| Provider | SDK | Required Scopes | Notes |
|----------|-----|-----------------|-------|
| Apple | Sign in with Apple JS / AuthenticationServices | `email`, `name` | Required for iOS apps with any social login (App Store Review Guideline 4.8). Email may be relayed (private relay). |
| Google | Google Identity Services (GIS) | `openid`, `email`, `profile` | One Tap + FedCM for web. Credential Manager API for Android. |
| GitHub | OAuth App / GitHub App | `user:email` | Good for developer tools. Use GitHub App for fine-grained permissions. |

Implementation rules:
- Always request `email` scope (primary account identifier for linking)
- Support account linking: user logs in with Google, later with Apple -> same email = same account
- Store provider ID + provider user ID + email in `user_identities` table (many-to-one with users)
- Handle email conflicts: if email exists with different provider, prompt user to link accounts (never auto-merge without verification)
- Implement fallback auth (email/password or passkey) so users are not locked to single provider

**Impact:** Social login reduces signup friction (one-tap vs form-fill). Apple Sign In mandatory for iOS apps offering any third-party login. Proper implementation prevents account fragmentation and provider lock-in.

**Source:** [Apple Sign In Guidelines](https://developer.apple.com/sign-in-with-apple/), [Google Identity Services](https://developers.google.com/identity), [App Store Review Guidelines 4.8](https://developer.apple.com/app-store/review/guidelines/#sign-in-with-apple)

### AUTH-11 [CRITICAL] Object-Level Authorization (BOLA) — Cross-User Test
**Detect:** A handler loads a resource by an ID from the request without confirming it belongs to the authenticated user. Search: lookups by `id`/`uuid` from params/body with no ownership guard (`WHERE user_id = :current_user`) or policy check. This is the most common AI-introduced access flaw (OWASP API1).

**Fix:** Enforce ownership (or RBAC/ABAC) on every object access, server-side. Add the cross-user regression test: as user A, create resource `R`; as user B, request `R` by its ID; assert `403`/`404`, never `200`. Apply equally to indirect references (filenames, storage keys, sequential IDs).

**Impact:** Missing ownership checks let any authenticated user read or modify another user's data by guessing or incrementing an ID — the single most common access-control flaw AI-generated APIs introduce.

**Source:** [OWASP API1: BOLA](https://owasp.org/API-Security/editions/2023/en/0xa1-broken-object-level-authorization/), [CVE-2025-48757](https://nvd.nist.gov/vuln/detail/CVE-2025-48757)

### AUTH-12 [MEDIUM] All Provider Binding Converges on One Post-Login Connect Hook
Every post-authentication provider-binding step (token storage, workspace discovery, initial sync kick-off) runs through one canonical connect hook.

**Detect:** Provider-binding side effects scattered across login callbacks, route guards, and ad-hoc init code; a second login path (re-auth, added provider) that skips steps the first path performs.

**Fix:** Define one canonical `onConnect`-style hook that every successful auth flow — first login, re-login, re-consent, added scope — funnels through; keep binding side effects only there.

**Impact:** Scattered binding logic makes re-auth paths silently skip initialization steps, producing "works on first login only" bugs.

**Source:** XR-027 — cross-project experience registry (2026); complements AUTH-03 (PKCE).

### AUTH-13 [HIGH] OAuth Robustness Envelope Is Pinned by Tests
The OAuth client's operational envelope — provider-directed rate limiting, retry policy, scope minimization, token refresh — is enforced and protected by tests.

**Detect:** Token-refresh logic with no test exercising expiry/refresh/failure paths; retry against the provider without backoff or budget; requested scopes exceeding what code actually uses.

**Fix:** Implement rate limiting and bounded retry toward the provider, request the minimal scope set, and cover token refresh and rate-limit behavior with regression tests so the envelope cannot silently regress.

**Impact:** An untested refresh path fails exactly when tokens expire in production — locking every user out at once; over-broad scopes inflate breach blast radius and store-review friction.

**Source:** XR-148 — cross-project experience registry (2026).

### AUTH-14 [HIGH] Routine Key Rotation Uses a Dual-Key Overlap Window
Routine admin/API key rotation is zero-downtime via dual-key overlap; confirmed leaks skip the overlap.

**Detect:** Key rotation implemented as replace-in-place (old key dies the moment the new one lands); no secondary-key slot; or a leaked key rotated with an overlap window left open.

**Fix:** For routine rotation: add the new key as a secondary (both valid), migrate all callers, then remove the old. For a CONFIRMED leak: replace immediately with no overlap — never leave a compromised key valid.

**Impact:** Replace-in-place rotation causes an outage on every routine rotation, which teaches teams to never rotate; overlap on a leaked key extends the attacker's window.

**Source:** XR-033 — cross-project experience registry (2026).

### AUTH-15 [HIGH] Fine-Grained Roles Persist in an SSOT, Never Re-Derived at Login
Role assignments live in one persistent store; login never recomputes roles from a coarser signal.

**Detect:** Roles derived at login from storage-provider permissions or group membership; fine-grained roles (manager, receptionist) that silently collapse to a coarse default after re-login.

**Fix:** Persist role assignments in a single SSOT (e.g. a members registry); on login, read roles from it — provider permissions may gate access but never define the role.

**Impact:** Re-derived roles silently demote users on every session start; the bug looks like "settings randomly reset" and erodes trust in the permission system.

**Source:** XR-142 — cross-project experience registry (2026).

### AUTH-16 [MEDIUM] Role Taxonomies Stay Separate: Access Roles ≠ Domain Roles ≠ Per-Record Roles
System RBAC roles, domain/service roles, and per-record contact roles are distinct taxonomies and are never conflated.

**Detect:** A settings surface spawns a second taxonomy overlapping an existing one; one enum mixing access control (admin/member) with domain function (provider/client) or per-record tags; users unable to tell whether two role screens describe the same thing.

**Fix:** Keep the three taxonomies in separate data structures with distinct naming in both model and UI; where they interact, map explicitly. Every taxonomy screen states its own scope and how it differs from its siblings.

**Impact:** Conflated role taxonomies produce both privilege bugs (domain role accidentally grants access) and duplicate-taxonomy drift (two lists of "roles" no one dares edit).

**Source:** XR-144 — cross-project experience registry (2026).

---

### AUTH-17 [MEDIUM] Session ID Regeneration (Fixation)
**Detect:** Session ID unchanged across the login boundary (same cookie value before and after authentication) or across a privilege-escalation event (role/permission change mid-session). Session IDs generated with fewer than 128 bits of entropy or from a non-CSPRNG source.

**Fix:** Generate session IDs with a CSPRNG at ≥128 bits of entropy (e.g. `crypto.randomBytes(32)` or equivalent). Regenerate the session ID immediately after successful authentication and again after any privilege escalation, invalidating the pre-escalation ID server-side.

**Impact:** An attacker who fixes a victim's pre-auth session ID (or predicts a low-entropy one) inherits the authenticated session the moment the victim logs in, bypassing credential theft entirely.

**Source:** [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
---

### AUTH-18 [HIGH] Password Policy Follows NIST 800-63B-4
**Detect:** Password fields enforcing composition rules ("must include uppercase/number/symbol"), periodic forced rotation with no compromise signal, a maximum length under 64 characters, or no check against known-breached password lists. Distinct from AUTH-01 (hashing algorithm) — this rule covers the *policy*, not the hash.

**Fix:** Apply NIST SP 800-63B-4 digital identity guidelines: minimum length 15 characters (8 with MFA enabled), support at least 64 characters and full Unicode/printable ASCII including spaces, do NOT enforce composition rules, do NOT require periodic rotation absent compromise evidence, screen new/changed passwords against a breached-password list (e.g. HaveIBeenPwned k-anonymity API or a bundled corpus), and prohibit password hints and security questions.

**Impact:** Composition and rotation rules that contradict current NIST guidance push users toward predictable patterns (`Password1!` → `Password2!`) and password reuse, which is measurably weaker than a longer unrestricted passphrase — enforcing the outdated policy actively reduces security.

**Source:** [NIST SP 800-63B-4 Digital Identity Guidelines](https://pages.nist.gov/800-63-4/sp800-63b.html)
---

### AUTH-19 [HIGH] TOTP/MFA Implementation Correctness
**Detect:** TOTP verification with no clock-skew tolerance (exact-window match only) or a non-standard digit/period configuration undocumented to the user; MFA recovery codes stored in plaintext or without single-use enforcement; MFA failure messages that reveal which factor was wrong (e.g. "Invalid OTP" vs generic "Invalid credentials"); no phishing-resistant factor (WebAuthn/passkey) offered alongside OTP-based MFA.

**Fix:** Implement TOTP per RFC 6238 (SHA-1, 6 digits, 30-second step) accepting the current window ±1 to absorb clock skew. Generate 8-10 single-use recovery codes at enrollment and store them hashed like passwords. Rate-limit MFA attempts (e.g. 5 failures per 15 minutes) and return generic failure messages that do not disclose which factor failed. Offer at least one phishing-resistant option (see AUTH-09) alongside OTP methods, and issue a fresh TOTP secret on any re-enrollment — never reuse an old seed.

**Impact:** A missing clock-skew window locks out legitimate users on minor clock drift; plaintext or reusable recovery codes turn the MFA bypass path into the weakest link in the system; factor-specific error messages leak enumeration data to an attacker probing which second factor a target has configured.

**Source:** [RFC 6238 — TOTP: Time-Based One-Time Password Algorithm](https://www.rfc-editor.org/rfc/rfc6238), [OWASP Multifactor Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)
---

### AUTH-20 [MEDIUM] API Key Lifecycle Hygiene
**Detect:** API keys stored in plaintext in the database; a single key per account with no rotation path (revoking it breaks every integration at once); keys with no identifying prefix, making leaked-key triage or scoping impossible from the value alone; full key value logged or displayed after initial creation.

**Fix:** Prefix keys by environment/type (e.g. `sk_live_`, `sk_test_`, `pk_live_`); store only a hash of the key server-side (like a password) and show the full value exactly once at creation; support multiple concurrent keys per account so rotation never requires downtime; log only the key's prefix plus last 4 characters in audit trails; scope each key to the minimum permissions it needs.

**Impact:** A key that cannot be identified from its prefix or rotated without breaking every caller forces an all-or-nothing incident response the moment one leaks — the exact failure mode key prefixing and multi-key support exist to avoid.

**Source:** [OWASP REST Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html)
---

### AUTH-21 [HIGH] Password Reset Token Integrity
**Detect:** Password-reset tokens with no expiry or an expiry longer than ~15 minutes; a reset token accepted more than once (not invalidated after use); a reset token passed in a URL query parameter that a browser would log to history/referrer/analytics rather than consumed via a POST body; a reset flow that reveals whether an email address has an account (different response for "found" vs "not found").

**Fix:** Issue single-use, time-limited (≤15 minute) reset tokens sent only to the account's verified email address; invalidate the token immediately on use or expiry; accept the token via a POST request body, never rely on it living only in a GET query string; return an identical response regardless of whether the email exists, to prevent user enumeration.

**Impact:** A long-lived or multi-use reset token is a standing account-takeover credential the moment it leaks via logs, browser history, or a referrer header; an enumerable reset endpoint hands attackers a list of valid accounts to target.

**Source:** [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
---

### AUTH-22 [MEDIUM] Auth Event Audit Logging
**Detect:** No durable log of authentication events (login success/failure, MFA challenge, password change, session revocation); failed-login volume with no alerting threshold, so a credential-stuffing spike is invisible until a user reports account takeover.

**Fix:** Log every authentication event (login, failure, MFA challenge/result, password change, token issuance/revocation) with timestamp, actor/account identifier, source IP, and outcome — never the credential itself. Wire an alert on anomalous patterns (e.g. 100+ failures/minute across accounts, or repeated failures against one account).

**Impact:** Without an auth event trail, a breach is discovered only when a user notices unauthorized activity, and the incident-response team has no record to establish scope, timeline, or affected accounts.

**Source:** [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
---

### AUTH-23 [MEDIUM] Open Redirect Prevention
**Detect:** A post-login, post-logout, or OAuth `redirect_uri`/`return_to`-style parameter accepted from client input and used to build a redirect without validation against an allowlist; partial-match or prefix-match redirect validation (`startswith`) instead of exact match.

**Fix:** Validate every redirect target against a server-side allowlist of exact, fully-qualified URIs — no wildcards, no partial/prefix matching, no trusting a client-supplied hostname. Reject or fall back to a fixed default path when the target does not match exactly.

**Impact:** An unvalidated redirect parameter turns the application's own trusted domain into a phishing launchpad — the victim clicks a link to a real, trusted URL that silently forwards them to an attacker-controlled page after authenticating.

**Source:** [OWASP Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html)
---

### AUTH-24 [HIGH] Refresh Token Reuse Triggers Family Revocation
**Detect:** Refresh token rotation implemented (AUTH-03) but a reused/replayed prior refresh token is silently accepted or merely rejected without revoking its sibling tokens; no mechanism ties a chain of rotated refresh tokens back to one "family" for revocation.

**Fix:** On detecting reuse of an already-rotated refresh token, revoke the entire token family (every token descended from the same original grant) and force re-authentication — reuse of a superseded token is a reliable signal of token theft, not a race condition to tolerate.

**Impact:** Without family revocation, a stolen refresh token lets an attacker and the legitimate user both stay silently logged in on parallel token chains indefinitely, since simple one-token rejection doesn't cut off the attacker's already-rotated copy.

**Source:** [RFC 9700 — Best Current Practice for OAuth 2.0 Security](https://datatracker.ietf.org/doc/rfc9700/)
---

### AUTH-25 [LOW] Sender-Constrained Tokens (DPoP) for High-Value APIs
**Detect:** Bearer tokens used for high-value operations (payments, admin actions, financial data) with no proof-of-possession binding — a stolen bearer token is fully usable by whoever holds it, from any client.

**Fix:** For high-value scopes, issue DPoP-bound (RFC 9449) or mTLS-bound access tokens instead of plain bearer tokens, so a stolen token is unusable without the corresponding private key. Bearer tokens remain acceptable for lower-value, general-purpose API access.

**Impact:** A plain bearer token is a bare credential — anyone who intercepts or exfiltrates it can replay it from anywhere; sender-constraining ties the token to the possessing client, closing the replay window even after leakage.

**Source:** [RFC 9449 — OAuth 2.0 Demonstrating Proof of Possession (DPoP)](https://www.rfc-editor.org/rfc/rfc9449)