# Rules: API Design & Architecture

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **API Design** | API-01 to API-14 (1 CRITICAL, 7 HIGH, 3 MEDIUM, 3 LOW) | ~12 |

---

## API Design

### API-01 RESTful Resource Naming [HIGH]

**Detect:** Verb-based URL paths (`/getUsers`, `/createOrder`, `/deleteItem`, `/fetchProducts`).

**Fix:** Rename to noun-based resource paths. Use HTTP methods for actions, plural nouns for collections.

| Before | After |
|--------|-------|
| `GET /getUsers` | `GET /users` |
| `POST /createOrder` | `POST /orders` |
| `DELETE /deleteItem/5` | `DELETE /items/5` |
| `GET /fetchProduct/3` | `GET /products/3` |

**Multi-stack examples:**

- **Node/Express:** `router.get('/users', listUsers)` with `router.post('/users', createUser)`
- **Python/FastAPI:** `@app.get("/users")` and `@app.post("/users")`
- **Go/Gin:** `r.GET("/users", listUsers)` and `r.POST("/users", createUser)`
- **Java/Spring:** `@GetMapping("/users")` and `@PostMapping("/users")`

**Impact:** Consistent resource naming reduces client confusion, improves cacheability, and aligns with tooling expectations (Swagger, Postman).

**Note (2026):** For complex parameterized reads that outgrow GET's URL limits, `POST`-as-safe-read was the historical workaround — the HTTP `QUERY` method ([RFC 10008](https://datatracker.ietf.org/doc/rfc10008/), June 2026; safe, idempotent, cacheable, with a request body) is now the standard replacement. Adopt where the framework/infrastructure supports it; OpenAPI 3.2 models it natively.

**Source:** [Google API Design Guide](https://cloud.google.com/apis/design), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 2

---

### API-02 Consistent Error Response [HIGH]

**Detect:** Different error shapes across endpoints (e.g., `{ message: "..." }` on one route, `{ error: "..." }` on another, raw strings on a third).

**Fix:** Standardize all error responses to RFC 9457 Problem Details format:

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/logs/requests/d24b2953",
  "errors": [
    { "pointer": "/email", "detail": "Must be a valid email address" }
  ]
}
```

**Multi-stack examples:**

- **Node/Express:** Global error handler middleware that formats all thrown errors to RFC 9457
- **Python/FastAPI:** Custom `HTTPException` handler returning `application/problem+json`
- **Go/Gin:** `ErrorHandler` middleware wrapping all errors into a `ProblemDetail` struct
- **Java/Spring:** `@ControllerAdvice` with `ProblemDetail` (Spring 6+ has built-in support)

**Impact:** Clients parse one format. Monitoring tools detect errors reliably. `status` field in body must match HTTP status code.

**Source:** [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 6

---

### API-03 API Versioning [HIGH]

**Detect:** Endpoints with no version prefix, or mixed versioning strategies (some URL-based, some header-based).

**Fix:** Use URI path versioning (`/v1/users`). One strategy, applied consistently.

| Strategy | Format | Cacheable | Recommendation |
|----------|--------|-----------|----------------|
| URI path | `/v1/orders` | Yes | Preferred for simplicity |
| Query string | `/orders?version=1` | Partial | Avoid |
| Header | `Accept: ...;version=1` | No | Avoid for solo projects |

Rules: Increment major version only for breaking changes. Support at least two major versions during transitions. Announce deprecation via `Deprecation` response header. Adding new optional fields requires no version bump.

**Impact:** Prevents breaking existing clients on deploy. Enables parallel migration windows.

**Source:** [Stripe API versioning](https://stripe.com/docs/api/versioning), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 4

---

### API-04 Request Validation [HIGH]

**Detect:** Endpoints that accept request bodies or query parameters without schema validation at API boundary.

**Fix:** Add schema validation at entry point of every endpoint. Reject malformed input with 422 and descriptive errors.

**Multi-stack examples:**

- **Node/Express:** `zod` schema with `.parse()` in middleware, or `joi` with `celebrate`
- **Python/FastAPI:** Pydantic models as function parameters (built-in)
- **Go/Gin:** `binding:"required"` struct tags with `go-playground/validator`
- **Java/Spring:** `@Valid` with Jakarta Bean Validation annotations
- **Ruby/Rails:** `strong_parameters` + custom validators
- **PHP/Laravel:** `FormRequest` classes with validation rules

**Impact:** Prevents invalid data from reaching business logic or database. Reduces attack surface (injection, type confusion).

**Source:** [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 8 (API4)

---

### API-05 Rate Limiting [HIGH]

**Detect:** Endpoints (especially public or auth-related) with no rate limiting middleware. Also: a limiter whose backing-store error is swallowed (`try`/`catch` around the check that continues on failure), a limiter with no test covering "store unavailable", and a documented limit whose failure behaviour is written down nowhere.

**Fix:** Add per-endpoint or per-user rate limits. Return `429 Too Many Requests` with standard headers.

Response headers on every request:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1711929600
Retry-After: 30          # on 429 only
```

The `X-RateLimit-*` family is the de-facto convention. The IETF standardization (`RateLimit-Policy` + `RateLimit` fields, draft-ietf-httpapi-ratelimit-headers) is still an Internet-Draft as of mid-2026 — emit the de-facto headers today, adopt the IETF names when the RFC lands.

| Algorithm | Burst | Best for |
|-----------|-------|----------|
| Fixed window | Spike at boundary | Simple quotas |
| Sliding window | Smooth | Fair enforcement |
| Token bucket | Yes | APIs allowing short bursts |
| Leaky bucket | No | Strict throughput |

**Multi-stack examples:**

- **Node/Express:** `express-rate-limit` or `rate-limiter-flexible` with Redis
- **Python/FastAPI:** `slowapi` (wraps `limits` library)
- **Go/Gin:** `ulule/limiter` or `tollbooth`
- **Java/Spring:** `bucket4j-spring-boot-starter` or Spring Cloud Gateway filters

**Limiter failure is a design decision, not an accident.** The backing store (Redis, KV, a shared counter) goes away eventually; what the limiter does in that minute is part of the rule. Default **fail-closed** — reject with `429`/`503` — on auth, payment, signup, and every write endpoint. **Fail-open** is legal only where availability outweighs abuse (public read paths), and only when the choice is written beside the config: which endpoint class it covers, why, and the alert that fires while the limiter is degraded. An unhandled limiter exception that silently lets every request through is the same finding as having no limiter — and it takes effect precisely during the incident the limiter existed for. This is ds-compliance ARC-07 (fail-closed authorization) applied one layer out, to throttling.

**Impact:** Protects against abuse, credential stuffing, and denial-of-service. Required by OWASP API Top 10 (API4: Unrestricted Resource Consumption).

**Source:** [IETF RFC 6585](https://www.rfc-editor.org/rfc/rfc6585), [Stripe rate limiters](https://stripe.com/blog/rate-limiters), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 7

---

### API-06 Cursor Pagination [MEDIUM]

**Detect:** Offset-based pagination (`?limit=20&offset=40`) on tables expected to exceed 10,000 rows or with real-time inserts.

**Fix:** Switch to cursor-based pagination with consistent ordering.

| Feature | Offset | Cursor |
|---------|--------|--------|
| Performance at scale | Degrades (DB skips N rows) | Constant (seeks to cursor) |
| Data consistency | Duplicates/skips on concurrent writes | Stable |
| Random page access | Yes | No (sequential) |

Cursor pagination shows ~17x speedup over offset on 1M-row PostgreSQL tables at deep pages.

**Impact:** Eliminates performance degradation on large, actively-written tables. Prevents duplicate or skipped rows in paginated results.

**Source:** [Slack API pagination](https://api.slack.com/docs/pagination), [Zendesk cursor vs offset](https://developer.zendesk.com/documentation/api-basics/pagination/comparing-cursor-pagination-and-offset-pagination/), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 5

---

### API-07 Idempotency [MEDIUM]

**Detect:** `POST` endpoints that create resources or trigger side effects without idempotency protection. Duplicate submissions create duplicate records.

**Fix:** Accept `Idempotency-Key: <uuid>` header on non-idempotent mutation endpoints. Store key with response; return stored response on replay. Layering: hash the client-supplied key and namespace it per user before storage; treat the Idempotency-Key layer as an optional shield IN FRONT OF endpoint-specific server-side protections (unique constraints, state checks) — never as their replacement. (XR-194)

- `PUT` and `DELETE` are naturally idempotent by spec
- `POST` requires explicit idempotency keys for safety (payments, order creation)
- Store idempotency records with TTL (24-48 hours)

**Multi-stack examples:**

- **Node/Express:** Middleware that checks Redis for `idempotency-key` before handler execution
- **Python/FastAPI:** Dependency that queries a cache/DB for prior results by key
- **Go/Gin:** Middleware with `sync.Map` or Redis-backed idempotency store
- **Java/Spring:** `HandlerInterceptor` with cache lookup

**Impact:** Enables safe client retries for network failures, especially critical for payment and order flows.

**Source:** [Stripe Idempotent Requests](https://stripe.com/docs/api/idempotent_requests), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 2

---

### API-08 OpenAPI Specification [MEDIUM]

**Detect:** API project without `openapi.json` or `openapi.yaml`. Endpoints undocumented in machine-readable format.

**Fix:** Generate from code annotations or write spec-first. Lint in CI.

| Practice | Why |
|----------|-----|
| Schemas in `components/schemas` | Code generators produce clean types |
| `description` on every operation | Documentation quality |
| Request/response `examples` | Enables automated test generation |
| `tags` to group operations | Navigation in Swagger UI |
| Spec linting in CI (Spectral: `spectral:oas` + `@stoplight/spectral-owasp-ruleset`) | Catches naming issues, broken refs, OWASP API risks |
| Breaking-change detection in CI (oasdiff) | Blocks incompatible spec changes before release |
| Contract tests | Verify server matches spec |

Design-first (write YAML before code) produces cleaner contracts and enables frontend mocking during parallel development — serve the spec as a live mock (Prism or WireMock) so clients build against the contract before the backend exists.

**Impact:** Machine-readable API contracts enable code generation, automated testing, and accurate documentation.

**Source:** [OpenAPI 3.1 Specification](https://swagger.io/specification/), [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 10

---

### API-09 HATEOAS Links [LOW]

**Detect:** API responses without navigation links. Clients must hard-code endpoint URLs.

**Fix:** Add `_links` or `links` with `rel` types for discoverability:

```json
{
  "orderId": 3,
  "status": "pending",
  "links": [
    { "rel": "self",   "href": "/orders/3",       "method": "GET" },
    { "rel": "cancel", "href": "/orders/3/cancel", "method": "POST" },
    { "rel": "customer","href": "/customers/12",   "method": "GET" }
  ]
}
```

HATEOAS optional for internal APIs but valuable for public APIs to reduce client coupling and enable API evolution without breaking changes.

**Impact:** Reduces client-side URL construction. Enables API evolution without breaking existing consumers.

**Source:** [Richardson Maturity Model Level 3](https://martinfowler.com/articles/richardsonMaturityModel.html), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Section 2

---

### API-10 GraphQL Best Practices [LOW]

**Detect:** GraphQL endpoint without query depth limiting or complexity analysis. Resolvers without batching (N+1 queries).

**Fix:** Add query complexity analysis and depth limiting. Use DataLoader for batched resolution.

| Issue | Fix |
|-------|-----|
| Unbounded depth | Set max depth (e.g., 10 levels) |
| Unbounded complexity | Assign cost per field, reject over threshold |
| N+1 queries | DataLoader (batches per-request) |
| Introspection in production | Disable introspection on public endpoints |
| Large responses | Pagination on list fields (connections pattern) |

**Multi-stack examples:**

- **Node/Apollo:** `depthLimit` + `createComplexityRule` + `DataLoader`
- **Python/Strawberry:** `QueryDepthLimiter` extension + `aiodataloader`
- **Go/gqlgen:** `extension.FixedComplexityLimit` + custom dataloaders
- **Java/Spring GraphQL:** `DataFetcherInterceptor` for depth + `BatchLoader`

**Impact:** Prevents denial-of-service via deeply nested or expensive queries. Eliminates N+1 database access patterns in resolvers.

**Source:** [Apollo GraphQL Best Practices](https://www.apollographql.com/docs/apollo-server/performance/), [api-architecture-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/backend/api-architecture-patterns.md) Sections 1 and 8

### API-11 SSRF Protection on URL Fetches [CRITICAL]

**Detect:** Server-side fetch of a user-supplied URL (webhook, link preview, image/PDF proxy, "import from URL") without host validation. Search: `requests.get(`, `fetch(`, `axios.get(`, `http.get(`, `URL(` with a host taken from request input. Every agent in Tenzai's 2026 study introduced SSRF in a URL-preview feature (100% rate).

**Fix:** Validate the target before fetching:
- Block private / loopback / link-local + cloud-metadata ranges: RFC 1918 (`10/8`, `172.16/12`, `192.168/16`), `127/8`, `169.254/16`, `::1`, and `169.254.169.254`.
- Prefer a host allowlist; allow `https` only; disable `file:`/`gopher:`/`ftp:` schemes.
- Re-validate after every redirect; resolve DNS once and connect to that resolved IP (defeats DNS rebinding).

**Source:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html), [Tenzai 2026](https://blog.tenzai.com/bad-vibes-comparing-the-secure-coding-capabilities-of-popular-coding-agents/)

### API-12 Server-Side Input Validation [HIGH]

**Detect:** Validation only on the client. Handlers consuming request body/query/params without a schema validator. Request fields mass-assigned to a model/entity.

**Fix:** Validate every external input against an explicit schema at the boundary (zod / pydantic / JSON Schema / Bean Validation); reject by default; allowlist writable fields. Re-check authorization server-side regardless of UI state.

**Source:** [OWASP API Security Top 10 — API3/API4](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)

---

### API-13 API Style Selection [LOW]

**Detect:** API style adopted without evaluating client requirements — GraphQL introduced for a single-client API, or tRPC exposed as a public API.

**Fix:** Default to REST; adopt an alternative only when its condition holds:

| Style | Choose when | Avoid when |
|-------|-------------|------------|
| REST | Default — public APIs, single dominant client shape | — |
| GraphQL | Multiple client types with genuinely different data needs for the same resources | Single client, uniform data shapes |
| tRPC | TypeScript-first monorepo, internal services — pair with REST for the public surface | Public API or polyglot consumers |

**Impact:** Matching style to demonstrated client needs avoids GraphQL operational complexity where REST suffices, and avoids over-/under-fetching where client shapes genuinely diverge.

**Source:** [Fern API design guide (2026)](https://buildwithfern.com/post/api-design-best-practices-guide), [Complete guide to API design in 2026](https://dev.to/zny10289/the-complete-guide-to-api-design-in-2026-rest-graphql-and-trpc-in-production-4ib2), [API design trends 2026](https://calmops.com/backend/api-design-trends-2026/)

### API-14 Long-Lived Connections Ship With a Stateless Fallback Transport [HIGH]
Critical realtime updates delivered over a persistent connection (WebSocket/SSE) automatically fall back to stateless polling with exponential backoff.

**Detect:** WS/SSE as the only delivery path for critical state; no automatic downgrade when the persistent connection dies; auth/permanent errors funneled into the same silent-retry loop as transient drops.

**Fix:** Layer a stateless HTTP-polling fallback with exponential backoff under the persistent transport — mobile-network proxies and captive portals silently kill long-lived connections routinely, so this is resilience, not duplication. Exclude authentication and other permanent errors from the fallback path: rethrow them immediately instead of retrying forever.

**Impact:** Without fallback, users behind common mobile/corporate middleboxes see a permanently frozen app; with auth errors swallowed by retry, a revoked session spins silently instead of re-prompting login.

**Source:** XR-077 — cross-project experience registry (2026).
