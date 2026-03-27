# Rules: Authentication & Authorization

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Authentication** | AUTH-01 to AUTH-10 (2 CRITICAL, 3 HIGH, 2 MEDIUM, 3 LOW) | ~12 |

---

## Authentication

### AUTH-01 Password Hashing [CRITICAL]

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

**Why:** Fast hashes (MD5, SHA-family) allow billions of guesses per second on modern GPUs. Argon2id with proper memory cost limits attackers to a few hundred attempts per second per GPU.

**Source:** [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), auth-implementation-guide.md Password Security section

---

### AUTH-02 Token Storage [CRITICAL]

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

**Why:** Tokens in localStorage are readable by any JavaScript on the page, including injected XSS payloads. httpOnly cookies are inaccessible to JavaScript entirely.

**Source:** [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), auth-implementation-guide.md JWT Best Practices and Session Management sections

---

### AUTH-03 OAuth 2.0 / OIDC [HIGH]

**Detect:** Custom authentication flows instead of OIDC for third-party login. Use of deprecated OAuth grants (Implicit, ROPC). PKCE missing from Authorization Code flow.

**Fix:** Use Authorization Code + PKCE (S256) for all client types. RFC 9700 (January 2025) codifies this as the only recommended flow.

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

**Why:** Implicit and ROPC grants expose tokens in URLs or require password sharing. Authorization Code + PKCE prevents authorization code interception and works securely for all client types.

**Source:** [RFC 6749](https://www.rfc-editor.org/rfc/rfc6749), [RFC 9700 (OAuth 2.1)](https://datatracker.ietf.org/doc/rfc9700/), auth-implementation-guide.md OAuth 2.0 section

---

### AUTH-04 JWT Validation [HIGH]

**Detect:** JWTs decoded without signature verification. `alg=none` accepted. Missing validation of `exp`, `iss`, or `aud` claims. Symmetric algorithm (HS256) used when asymmetric is appropriate.

**Fix:** Validate all claims on every request. Maintain a server-side algorithm allowlist.

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
| HS256 | Symmetric (HMAC) | Only when issuer and verifier are the same service |

Keep JWT payloads small: `sub`, `iss`, `aud`, `exp`, `iat`, `jti`, and role/scope. Avoid storing PII (email, name) in JWTs -- they are base64-encoded, not encrypted.

**Why:** JWT algorithm confusion is a CRITICAL vulnerability. Accepting `alg=none` or failing to verify signatures allows token forgery.

**Source:** [RFC 7519](https://www.rfc-editor.org/rfc/rfc7519), [JWT.io best practices](https://jwt.io/introduction/), auth-implementation-guide.md JWT Best Practices section

---

### AUTH-05 CSRF Protection [HIGH]

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

- **Node/Express:** `csurf` middleware (deprecated; use `csrf-csrf` or `lusitania`) + `SameSite=Lax` cookies
- **Python/Django:** Built-in CSRF middleware (enabled by default)
- **Python/FastAPI:** Manual CSRF token in cookie + header comparison
- **Go/Gin:** `gorilla/csrf` middleware
- **Java/Spring:** Spring Security CSRF (enabled by default for server-rendered)
- **Ruby/Rails:** `protect_from_forgery` (enabled by default)

PKCE replaces CSRF tokens in OAuth flows (per RFC 9700).

**Why:** CSRF attacks trick authenticated users into performing unintended actions. A single missing CSRF check on a sensitive endpoint enables account takeover or data manipulation.

**Source:** [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), auth-implementation-guide.md Session Management section

---

### AUTH-06 RBAC / Authorization [MEDIUM]

**Detect:** Authorization checks missing on protected endpoints. All-or-nothing authentication (logged in = full access). Role checks performed only on the client side.

**Fix:** Implement middleware-based RBAC with server-side enforcement on every request. Deny by default -- require explicit grants.

| Model | Complexity | Best For |
|-------|-----------|----------|
| Flat roles | Low | MVPs, small apps (`admin`, `user`, `viewer`) |
| Hierarchical roles | Medium | Organizations (`superadmin > admin > editor > viewer`) |
| Group-based | Medium | Multi-tenant SaaS (roles scoped to org) |
| ABAC | High | Fine-grained, context-dependent rules |
| ReBAC | High | Social/collaborative apps (Google Docs-style) |

Implementation: Schema uses `users`, `organizations`, `memberships(user_id, org_id, role)`, `permissions(role, resource, action)`. Check permissions in middleware, not in route handlers.

For solo dev with fewer than 5 roles: flat RBAC with a `role` column on the user table. For multi-tenant SaaS: group-based RBAC with a `memberships` table. Avoid ABAC/ReBAC until simpler models become a demonstrable bottleneck.

**Why:** Missing server-side authorization is the most common API vulnerability (OWASP API1: BOLA accounts for 40% of all API attacks).

**Source:** [NIST RBAC Model](https://csrc.nist.gov/projects/role-based-access-control), auth-implementation-guide.md RBAC and Permission Models section

---

### AUTH-07 Auth Rate Limiting [MEDIUM]

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

**Why:** Authentication endpoints are the primary target for credential stuffing and brute-force attacks. Without rate limiting, attackers can attempt millions of passwords per hour.

**Source:** [OWASP Credential Stuffing Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Credential_Stuffing_Prevention_Cheat_Sheet.html), auth-implementation-guide.md Common Vulnerabilities section

---

### AUTH-08 Session vs JWT Decision [LOW]

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

Default for solo developers: server sessions with httpOnly cookies. Add JWT only with a concrete cross-origin or mobile requirement.

**Why:** Choosing the wrong auth mechanism leads to unnecessary complexity (JWT for a simple web app) or security gaps (sessions without shared store in a distributed system).

**Source:** [Auth0 Session vs JWT comparison](https://auth0.com/blog/), auth-implementation-guide.md Auth Decision Framework section

---

### AUTH-09 Passkey Support (WebAuthn) [LOW]

**Detect:** Auth system relies solely on passwords with no passwordless option. No WebAuthn/FIDO2 integration. Users cannot register platform authenticators (biometrics, security keys).

**Fix:** Add WebAuthn/passkey as a secondary authentication method alongside existing password auth.

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

**Why:** Passkeys eliminate phishing attacks entirely (credential is domain-bound). No password = no credential stuffing. Platform support reached critical mass in 2024-2025 (iOS 16+, Android 9+, Windows 10+, all major browsers).

**Source:** [W3C WebAuthn Specification](https://www.w3.org/TR/webauthn-2/), [FIDO Alliance Passkeys](https://fidoalliance.org/passkeys/), [OWASP WebAuthn Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Multifactor_Authentication_Cheat_Sheet.html)

---

### AUTH-10 Social Login Integration [LOW]

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
- Store provider ID + provider user ID + email in a `user_identities` table (many-to-one with users)
- Handle email conflicts: if email exists with different provider, prompt user to link accounts (never auto-merge without verification)
- Implement fallback auth (email/password or passkey) so users are not locked to a single provider

**Why:** Social login reduces signup friction (one-tap vs form-fill). Apple Sign In is mandatory for iOS apps offering any third-party login. Proper implementation prevents account fragmentation and provider lock-in.

**Source:** [Apple Sign In Guidelines](https://developer.apple.com/sign-in-with-apple/), [Google Identity Services](https://developers.google.com/identity), [App Store Review Guidelines 4.8](https://developer.apple.com/app-store/review/guidelines/#sign-in-with-apple)
