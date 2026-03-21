# Authentication Implementation Guide

A framework-agnostic, privacy-first reference for solo developers building production authentication systems. Covers the full stack from password hashing to passkeys, with decision matrices for every major choice.

---

## Auth Decision Framework

### Session vs JWT vs Hybrid

| Criteria | Server Sessions | JWT (Stateless) | Hybrid |
|---|---|---|---|
| **State storage** | Server-side (Redis/DB) | Client-side (token) | Session + short-lived JWT |
| **Scalability** | Requires shared store | Scales horizontally | Moderate complexity |
| **Revocation** | Instant (delete session) | Hard (needs blocklist) | Instant for sessions |
| **Payload size** | Small cookie (~32 B) | Large (~800 B+) | Both |
| **XSS risk** | Low (httpOnly cookie) | High if in localStorage | Low |
| **Best for** | SSR web apps, monoliths | Microservices, APIs | Web app + API backend |

### Decision Tree

1. **Server-rendered web app only?** Use server sessions with httpOnly cookies.
2. **SPA calling same-origin API?** Use server sessions with httpOnly cookies (proxy API calls).
3. **SPA calling cross-origin API?** Use hybrid: session cookie for the BFF, short-lived JWT for downstream APIs.
4. **Mobile app or third-party API consumers?** Use JWT with refresh token rotation.
5. **Microservices needing inter-service auth?** Use JWT with short expiry (5 min) + mTLS between services.

**Default recommendation for solo devs:** Server sessions with httpOnly cookies. Add JWT only when you have a concrete cross-origin or mobile requirement.

---

## OAuth 2.0 / OIDC with Authorization Code + PKCE

RFC 9700 (January 2025) codifies this as the only recommended flow for all client types. Implicit and ROPC grants are deprecated.

### Step-by-Step Flow

```
1. Client generates code_verifier (43-128 char random string)
2. Client computes code_challenge = BASE64URL(SHA256(code_verifier))
3. Client redirects user to authorization server:
   GET /authorize?
     response_type=code&
     client_id=CLIENT_ID&
     redirect_uri=https://app.example.com/callback&
     scope=openid profile email&
     state=RANDOM_STATE&
     code_challenge=CODE_CHALLENGE&
     code_challenge_method=S256

4. User authenticates and consents
5. Authorization server redirects back:
   GET /callback?code=AUTH_CODE&state=RANDOM_STATE

6. Client verifies state matches
7. Client exchanges code for tokens:
   POST /token
     grant_type=authorization_code&
     code=AUTH_CODE&
     redirect_uri=https://app.example.com/callback&
     client_id=CLIENT_ID&
     code_verifier=CODE_VERIFIER

8. Server returns: access_token, id_token (OIDC), refresh_token
```

### RFC 9700 Compliance Checklist

- Always use PKCE with S256 (not plain) for all client types including confidential clients
- Enforce exact redirect URI matching (no wildcards)
- Validate `iss` claim in tokens when using multiple authorization servers
- Use sender-constrained tokens (DPoP) where possible
- Rotate refresh tokens on every use (one-time use)
- Set short access token lifetimes (5-15 minutes)
- Never use Implicit or ROPC grants

---

## JWT Best Practices

### Signing Algorithms

| Algorithm | Type | Use Case |
|---|---|---|
| **RS256** | Asymmetric (RSA) | Default choice; public key verification without sharing secrets |
| **ES256** | Asymmetric (ECDSA) | Smaller tokens, faster verification, preferred for new systems |
| **EdDSA** | Asymmetric (Ed25519) | Best performance, smallest keys; growing library support |
| **HS256** | Symmetric (HMAC) | Only when issuer and verifier are the same service |

**Rule:** Never use `none`. Always validate `alg` header against an allowlist server-side.

### Expiry and Refresh Strategy

| Token | Lifetime | Storage |
|---|---|---|
| Access token | 5-15 minutes | Memory (SPA) or httpOnly cookie |
| Refresh token | 7-30 days | httpOnly, Secure, SameSite=Strict cookie |
| ID token (OIDC) | Match access token | Memory; used once to establish session |

- Implement refresh token rotation: each use issues a new refresh token and invalidates the old one.
- On refresh token reuse detection, revoke the entire token family (indicates theft).

### Claims Best Practices

- Keep payloads small: `sub`, `iss`, `aud`, `exp`, `iat`, `jti`, and role/scope.
- Never store PII (email, name, address) in JWTs — they are base64-encoded, not encrypted.
- Always validate `iss`, `aud`, `exp`, and `nbf` on every request.
- Use `jti` (JWT ID) for revocation tracking when needed.

### Token Storage

| Location | XSS Safe | CSRF Safe | Recommendation |
|---|---|---|---|
| httpOnly cookie | Yes | No (needs CSRF protection) | Best for web apps |
| Memory (JS variable) | No (but short-lived) | Yes | Acceptable for SPAs with short-lived tokens |
| localStorage | No | Yes | Never use for auth tokens |
| sessionStorage | No | Yes | Avoid |

---

## Session Management

### Cookie Attributes

```
Set-Cookie: session_id=<value>;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/;
  Max-Age=86400;
  Domain=.example.com
```

| Attribute | Value | Rationale |
|---|---|---|
| `HttpOnly` | Required | Prevents JavaScript access (XSS mitigation) |
| `Secure` | Required | Transmit only over HTTPS |
| `SameSite` | `Lax` (default) or `Strict` | CSRF protection; `Strict` breaks OAuth redirects |
| `Path` | `/` | Scope to entire application |
| `Max-Age` | <=86400 (24h) | NIST 800-63B-4: reauthentication within 24h at AAL2 |

### Session ID Requirements

- Minimum 128 bits of entropy (use `crypto.randomBytes(32)` or equivalent)
- Regenerate session ID after authentication (prevents session fixation)
- Regenerate after privilege escalation
- Store server-side in Redis/DB with TTL matching cookie Max-Age

### CSRF Protection

- **SameSite=Lax** cookies block most CSRF but not top-level GET navigations
- For state-changing operations: use Synchronizer Token Pattern or Double Submit Cookie
- PKCE replaces CSRF tokens in OAuth flows (per RFC 9700)
- Always verify `Origin` and `Referer` headers as defense-in-depth

### Inactivity Timeout

- Sliding window: reset TTL on each authenticated request
- NIST 800-63B-4 recommends no more than 1 hour idle timeout at AAL2

---

## Password Security

### Algorithm Comparison (OWASP 2025)

| Algorithm | Priority | Memory | Time Cost | Output | Notes |
|---|---|---|---|---|---|
| **Argon2id** | 1st (default) | 19-46 MiB | 1-2 iterations | 32 B | Winner of PHC 2015; resists GPU + side-channel |
| **scrypt** | 2nd | N=2^17, r=8 | p=1 | 32 B | Good when Argon2 unavailable |
| **bcrypt** | 3rd (legacy) | Fixed ~4 KB | cost=12-14 | 24 B | 72-byte input limit; legacy systems only |
| **PBKDF2** | 4th (FIPS) | None | 600K+ iterations | Variable | FIPS-140 compliance only |

#### Recommended Argon2id Configurations

- **Option A:** `m=47104` (46 MiB), `t=1`, `p=1` (higher memory, fewer passes)
- **Option B:** `m=19456` (19 MiB), `t=2`, `p=1` (lower memory, more passes)

### NIST 800-63B-4 Password Policy

| Rule | Requirement |
|---|---|
| Min length (password only) | 15 characters |
| Min length (with MFA) | 8 characters |
| Max length | Support at least 64 characters |
| Character set | All printable ASCII + Unicode + spaces |
| Complexity rules | Do NOT enforce (no "must include uppercase/symbol") |
| Periodic rotation | Do NOT require (change only on compromise evidence) |
| Breached password check | Required — screen against known breached password lists |
| Password hints | Prohibited |
| Security questions | Prohibited |

### Implementation Checklist

- [ ] Hash with Argon2id using OWASP-recommended parameters
- [ ] Screen passwords against HaveIBeenPwned API (k-anonymity model) or bundled breach list
- [ ] Enforce minimum length (8 with MFA, 15 without)
- [ ] Accept Unicode, spaces, and all printable characters
- [ ] Never log or expose passwords in error messages
- [ ] Use a pepper stored in environment variable or HSM (not in database)

---

## Multi-Factor Authentication

### Method Comparison

| Method | Phishing Resistant | UX | Cost | NIST AAL |
|---|---|---|---|---|
| **WebAuthn / Passkeys** | Yes | Excellent | Free | AAL2-AAL3 |
| **TOTP (Authenticator App)** | No | Good | Free | AAL2 |
| **Hardware Security Key** | Yes | Fair | $25-70/key | AAL3 |
| **SMS OTP** | No | Fair | $0.01-0.05/msg | AAL1 |
| **Email OTP** | No | Poor | Free | AAL1 |
| **Push Notification** | No | Good | Vendor-dependent | AAL2 |

**2025-2026 reality:** Multiple governments are banning SMS OTP for financial services (UAE by March 2026, India by April 2026, Philippines by June 2026). Design new systems without SMS as a primary factor.

### Implementation Checklist

- [ ] Offer at least one phishing-resistant option (WebAuthn/passkeys)
- [ ] TOTP: use SHA-1 with 6 digits, 30-second window (RFC 6238 standard)
- [ ] TOTP: accept current window +/- 1 to handle clock skew
- [ ] Generate and display recovery codes (8-10 single-use codes) at enrollment
- [ ] Store recovery codes hashed (same as passwords)
- [ ] Rate-limit MFA attempts (max 5 failures per 15 minutes)
- [ ] Do not reveal which factor failed ("Invalid credentials" not "Wrong OTP")
- [ ] Require MFA re-enrollment creates a new secret (never reuse old TOTP seeds)

---

## Passkeys and WebAuthn

### How It Works

Passkeys use the FIDO2/WebAuthn standard. A public-private key pair is generated on the user's device. The private key never leaves the device (or is synced via the platform's secure cloud). Authentication works by signing a server challenge with the private key — no shared secret is transmitted.

**Phishing resistance:** The credential is domain-bound. A phishing site on a different domain cannot trigger the passkey. This is a cryptographic guarantee, not a user training measure.

### Registration Flow

```
1. Server generates a challenge + user info
2. navigator.credentials.create({publicKey: options})
3. Device generates key pair, stores private key in secure enclave
4. Browser returns attestation object with public key
5. Server stores: credential ID, public key, sign count, user handle
```

### Authentication Flow

```
1. Server generates a challenge + allowed credential IDs
2. navigator.credentials.get({publicKey: options})
3. User verifies via biometric/PIN (local to device)
4. Device signs challenge with private key
5. Browser returns assertion with signature
6. Server verifies signature with stored public key, checks sign count
```

### Browser and Platform Support (2026)

| Platform | Passkey Support | Sync |
|---|---|---|
| iOS 16+ / macOS Ventura+ | Full | iCloud Keychain |
| Android 9+ | Full | Google Password Manager |
| Windows 10+ | Full (Windows Hello) | Microsoft Account |
| Chrome 108+ | Full | Cross-platform via sync provider |
| Firefox 122+ | Full | Platform-dependent |
| Safari 16+ | Full | iCloud Keychain |

### Deployment Strategy

1. **Phase 1:** Offer passkeys as optional MFA alongside existing methods
2. **Phase 2:** Prompt passkey enrollment on login for eligible devices
3. **Phase 3:** Allow passkey-only accounts for new registrations
4. **Fallback:** Always maintain a recovery path (recovery codes, verified email)

---

## Social Login

### Provider Comparison

| Provider | Protocol | ID Token | Unique ID | Free Tier |
|---|---|---|---|---|
| **Google** | OIDC | JWT | `sub` claim | Unlimited |
| **Apple** | OIDC | JWT | `sub` claim (opaque) | Unlimited |
| **GitHub** | OAuth 2.0 | None (use /user API) | `id` field | Unlimited |
| **Microsoft** | OIDC | JWT | `oid` claim | Unlimited |

### Implementation Pattern

1. Use Authorization Code + PKCE (same flow for all providers)
2. Store the provider's stable user ID (`sub` / `id`) — never use email as primary key
3. Link social accounts to internal user records via a `user_identities` table
4. On first login: create user record + identity link
5. On subsequent login: look up identity, return existing user
6. Allow users to link multiple social providers to one account

### Security Checklist

- [ ] Validate `id_token` signature using provider's JWKS endpoint
- [ ] Verify `iss`, `aud`, `exp` claims in every ID token
- [ ] For Apple Sign-In: handle the "email relay" (privaterelay.appleid.com)
- [ ] Apple only sends user info on first authorization — persist it immediately
- [ ] Never trust email from social providers as verified unless provider confirms it
- [ ] Implement account linking carefully: require proof of ownership before merging
- [ ] Support account unlinking in user settings

---

## RBAC and Permission Models

### Model Comparison

| Model | Complexity | Best For | Example |
|---|---|---|---|
| **Flat roles** | Low | MVPs, small apps | `admin`, `user`, `viewer` |
| **Hierarchical roles** | Medium | Organizations with clear hierarchy | `superadmin > admin > editor > viewer` |
| **Group-based** | Medium | Multi-tenant SaaS | Users belong to orgs; roles scoped to org |
| **Attribute-based (ABAC)** | High | Fine-grained, context-dependent rules | "Editors can edit docs in their department" |
| **Relationship-based (ReBAC)** | High | Social/collaborative apps | Google Docs-style sharing |

### When to Use Each

- **Solo dev, <5 roles:** Flat RBAC with a `role` column on the user table.
- **Multi-tenant SaaS:** Group-based RBAC with a `memberships` table (`user_id`, `org_id`, `role`).
- **Complex permissions:** Start with group-based RBAC, add permission flags as needed. Avoid ABAC/ReBAC until flat/hierarchical becomes a demonstrable bottleneck.

### Implementation Pattern (Group-Based RBAC)

Schema: `users`, `organizations`, `memberships(user_id, org_id, role)`, `permissions(role, resource, action)`. Check permissions in middleware, not in route handlers. Deny by default — require explicit grants.

---

## API Authentication

### Decision Matrix

| Method | Auth Type | Best For | Rotation | Revocation |
|---|---|---|---|---|
| **Bearer token (JWT)** | User/service | SPAs, mobile apps | Short-lived + refresh | Blocklist or short expiry |
| **API key** | Service/integration | Webhooks, server-to-server | Manual rotation | Instant (delete key) |
| **mTLS** | Service | Internal microservices | Certificate rotation | CRL/OCSP |
| **HMAC signature** | Service | Webhooks (verification) | Rotate shared secret | Instant |
| **OAuth 2.0 Client Credentials** | Service | Third-party API access | Token expiry | Revoke client |

### API Key Best Practices

- Prefix keys for identification: `sk_live_`, `sk_test_`, `pk_live_`
- Store only the hash of the key in the database (like a password)
- Show the full key exactly once at creation
- Support multiple keys per account (for rotation without downtime)
- Log key prefix + last 4 chars in audit logs (never the full key)
- Scope keys to specific permissions when possible

### Rate Limiting

- Apply per-key and per-IP rate limits
- Return `429 Too Many Requests` with `Retry-After` header
- Use sliding window counters (Redis `INCR` + `EXPIRE`)

---

## Managed vs DIY Decision Matrix

### Provider Comparison (2026 Pricing)

| Feature | Clerk | Auth0 | Supabase Auth | Firebase Auth |
|---|---|---|---|---|
| **Free MAU** | 10,000 | 7,500 | 50,000 | 50,000 |
| **Cost/MAU after free** | $0.02 | ~$0.07 | $0.00325 | $0.0025-0.0055 |
| **Cost at 100K MAU** | ~$1,800/mo | ~$2,400/mo | ~$187/mo | ~$125/mo |
| **Social login** | Yes | Yes | Yes | Yes |
| **Passkeys** | Yes | Yes | Community | Yes (Identity Platform) |
| **RBAC** | Yes | Yes | Via RLS | Custom only |
| **Pre-built UI** | Yes (React) | Yes (Universal Login) | Community | FirebaseUI |
| **SAML/Enterprise SSO** | Paid | Yes | No | Paid (Identity Platform) |
| **SOC 2** | Yes | Yes | Yes | Yes |
| **HIPAA BAA** | No | Yes | No | Yes |
| **Best DX** | React/Next.js | Framework-agnostic | Full-stack Supabase | Google ecosystem |

### Decision Guide

| Scenario | Recommendation |
|---|---|
| React/Next.js SaaS, budget available | Clerk |
| Enterprise with SAML/compliance needs | Auth0 |
| Already using Supabase DB, cost-sensitive | Supabase Auth |
| High MAU, cost is primary concern | Firebase Auth or Supabase Auth |
| Full control, privacy-first, no vendor lock-in | DIY with proven libraries |
| Prototype / MVP (< 10K users) | Any managed provider (all have free tiers) |

### DIY: When It Makes Sense

- Strict data residency requirements (GDPR, sovereignty)
- Auth is a core product differentiator
- Budget cannot absorb per-MAU costs at scale
- **Use proven libraries:** Lucia, Auth.js (NextAuth), Passport.js, Apache Shiro — never hand-roll crypto

---

## Common Vulnerabilities

### OWASP Authentication Vulnerabilities

| Vulnerability | Risk | Mitigation |
|---|---|---|
| **Credential stuffing** | HIGH | Breached password check, rate limiting, MFA |
| **Brute force** | HIGH | Account lockout (progressive delay), rate limiting, CAPTCHA after N failures |
| **Session fixation** | HIGH | Regenerate session ID after authentication |
| **JWT algorithm confusion** | CRITICAL | Validate `alg` against server-side allowlist; never accept `none` |
| **Insecure token storage** | HIGH | httpOnly cookies only; never localStorage |
| **Missing CSRF protection** | MEDIUM | SameSite cookies + CSRF tokens for state-changing operations |
| **Open redirect** | MEDIUM | Allowlist redirect URIs; exact match only |
| **Insufficient logging** | MEDIUM | Log all auth events (login, failure, MFA, password change) with timestamp and IP |
| **Broken password reset** | HIGH | Time-limited tokens (15 min), single-use, sent only to verified email |
| **Privilege escalation** | CRITICAL | Server-side role checks on every request; never trust client-sent roles |
| **Token leakage in URLs** | MEDIUM | Use POST for token exchange; never send tokens as query parameters |
| **Weak recovery flows** | HIGH | Recovery codes must not bypass MFA policy; verify identity before reset |

### Defense-in-Depth Checklist

- [ ] All auth endpoints behind rate limiting
- [ ] All passwords hashed with Argon2id
- [ ] All sessions regenerated post-authentication
- [ ] All tokens validated server-side on every request
- [ ] All sensitive actions require re-authentication
- [ ] Audit log for every authentication event
- [ ] Automated alerts on anomalous auth patterns (e.g., 100+ failures/min)

---

## Testing Patterns

### Auth Test Matrix

| Test Category | What to Test | Method |
|---|---|---|
| **Happy path** | Registration, login, logout, token refresh | Integration test |
| **Credential validation** | Reject weak passwords, accept valid ones | Unit test |
| **MFA enrollment** | TOTP setup, verification, recovery codes | Integration test |
| **Session lifecycle** | Creation, expiry, regeneration, revocation | Integration test |
| **Authorization** | Role enforcement on every protected endpoint | Integration test |
| **Rate limiting** | Lockout after N failures, unlock after timeout | Integration test |
| **Token validation** | Expired, malformed, wrong audience, wrong issuer | Unit test |
| **CSRF** | State-changing requests without valid CSRF token | Integration test |
| **OAuth flow** | Callback handling, state validation, PKCE verification | Integration test (mock IdP) |
| **Password reset** | Token expiry, single-use, email delivery | Integration test |
| **Account linking** | Social + password accounts, duplicate prevention | Integration test |
| **Privilege escalation** | User A accessing User B's resources | Integration test |

### Integration Test Examples

**Expired token rejected:** Issue token with 1s expiry, wait 2s, request, assert 401.

**Refresh token rotation:** Get RT1, use it to get RT2, reuse RT1, assert rejected + entire family revoked.

**RBAC enforcement:** For each protected endpoint, test authorized role (200), unauthorized role (403), no auth (401).

**PKCE flow (mock IdP):** Initiate with code_challenge, exchange with correct verifier (success), wrong verifier (400), missing verifier (400).

### Testing Recommendations

- Use a real database (not mocks) for auth integration tests — auth bugs often involve state
- Spin up a disposable test database per test suite (Docker, testcontainers)
- Mock external IdPs (Google, Apple) with a local OIDC server (e.g., `oidc-provider` for Node.js)
- Test clock-dependent logic by injecting a clock abstraction, not by using `setTimeout`
- Include negative tests: malformed tokens, missing headers, expired sessions, tampered cookies

---

## Sources

- [RFC 9700 - Best Current Practice for OAuth 2.0 Security (IETF)](https://datatracker.ietf.org/doc/rfc9700/)
- [OAuth Best Practices: RFC 9700 Summary (WorkOS)](https://workos.com/blog/oauth-best-practices)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Password Hashing Guide 2025: Argon2 vs Bcrypt vs Scrypt vs PBKDF2](https://guptadeepak.com/the-complete-guide-to-password-hashing-argon2-vs-bcrypt-vs-scrypt-vs-pbkdf2-2026/)
- [NIST SP 800-63B-4 Digital Identity Guidelines](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [NIST 2025 Password Policy Updates](https://blogs.reliablepenguin.com/2025/10/22/your-password-policy-is-due-for-a-2025-refresh-what-nist-now-recommends)
- [Phishing-Resistant MFA Buyer's Guide (NIST SP 800-63-4)](https://www.wwpass.com/blog/phishing-resistant-mfa-in-2025-buyer-s-guide-to-nist-sp-800-63-4-omb-m-22-09/)
- [Authorization Code Flow with PKCE (Auth0)](https://auth0.com/docs/get-started/authentication-and-authorization-flow/authorization-code-flow-with-pkce)
- [Authentication Trends in 2026: Passkeys, OAuth3, and WebAuthn](https://www.c-sharpcorner.com/article/authentication-trends-in-2026-passkeys-oauth3-and-webauthn/)
- [Passwordless Authentication in 2025: The Year Passkeys Went Mainstream](https://www.authsignal.com/blog/articles/passwordless-authentication-in-2025-the-year-passkeys-went-mainstream)
- [Modern Authentication in 2025: OAuth2, MFA, and the Shift to Passwordless](https://dev.to/oneentry/modern-authentication-in-2025-oauth2-mfa-and-the-shift-to-passwordless-4d9o)
- [Auth Pricing Comparison: Cognito vs Auth0 vs Firebase vs Supabase (Zuplo)](https://zuplo.com/learning-center/api-authentication-pricing)
- [Clerk vs Auth0 vs Supabase: Pricing and DX Compared](https://designrevision.com/blog/auth-providers-compared)
- [Firebase Auth Pricing 2026](https://www.metacto.com/blogs/the-complete-guide-to-firebase-auth-costs-setup-integration-and-maintenance)
- [OAuth 2.0 Security Best Practices for Developers (DEV Community)](https://dev.to/kimmaida/oauth-20-security-best-practices-for-developers-2ba5)
- [OAuth 2.0 Best Practices to Secure Your APIs: RFC 9700 (Scalekit)](https://www.scalekit.com/blog/oauth-2-0-best-practices-rfc9700)
