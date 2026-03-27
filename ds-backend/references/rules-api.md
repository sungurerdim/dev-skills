# Rules: API Design & Architecture

Rules for audit/design/spec modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **API Design** | API-01 to API-10 (5 HIGH, 3 MEDIUM, 2 LOW) | ~12 |

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

**Source:** [Google API Design Guide](https://cloud.google.com/apis/design), api-architecture-patterns.md Section 2

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

**Impact:** Clients parse one format. Monitoring tools detect errors reliably. The `status` field in the body must match the HTTP status code.

**Source:** [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457.html), api-architecture-patterns.md Section 6

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

**Source:** [Stripe API versioning](https://stripe.com/docs/api/versioning), api-architecture-patterns.md Section 4

---

### API-04 Request Validation [HIGH]

**Detect:** Endpoints that accept request bodies or query parameters without schema validation at the API boundary.

**Fix:** Add schema validation at the entry point of every endpoint. Reject malformed input with 422 and descriptive errors.

**Multi-stack examples:**

- **Node/Express:** `zod` schema with `.parse()` in middleware, or `joi` with `celebrate`
- **Python/FastAPI:** Pydantic models as function parameters (built-in)
- **Go/Gin:** `binding:"required"` struct tags with `go-playground/validator`
- **Java/Spring:** `@Valid` with Jakarta Bean Validation annotations
- **Ruby/Rails:** `strong_parameters` + custom validators
- **PHP/Laravel:** `FormRequest` classes with validation rules

**Impact:** Prevents invalid data from reaching business logic or the database. Reduces attack surface (injection, type confusion).

**Source:** [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), api-architecture-patterns.md Section 8 (API4)

---

### API-05 Rate Limiting [HIGH]

**Detect:** Endpoints (especially public or auth-related) with no rate limiting middleware.

**Fix:** Add per-endpoint or per-user rate limits. Return `429 Too Many Requests` with standard headers.

Response headers on every request:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1711929600
Retry-After: 30          # on 429 only
```

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

**Impact:** Protects against abuse, credential stuffing, and denial-of-service. Required by OWASP API Top 10 (API4: Unrestricted Resource Consumption).

**Source:** [IETF RFC 6585](https://www.rfc-editor.org/rfc/rfc6585), [Stripe rate limiters](https://stripe.com/blog/rate-limiters), api-architecture-patterns.md Section 7

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

**Source:** [Slack API pagination](https://api.slack.com/docs/pagination), [Zendesk cursor vs offset](https://developer.zendesk.com/documentation/api-basics/pagination/comparing-cursor-pagination-and-offset-pagination/), api-architecture-patterns.md Section 5

---

### API-07 Idempotency [MEDIUM]

**Detect:** `POST` endpoints that create resources or trigger side effects without idempotency protection. Duplicate submissions create duplicate records.

**Fix:** Accept an `Idempotency-Key: <uuid>` header on non-idempotent mutation endpoints. Store the key with the response; return the stored response on replay.

- `PUT` and `DELETE` are naturally idempotent by spec
- `POST` requires explicit idempotency keys for safety (payments, order creation)
- Store idempotency records with a TTL (24-48 hours)

**Multi-stack examples:**

- **Node/Express:** Middleware that checks Redis for `idempotency-key` before handler execution
- **Python/FastAPI:** Dependency that queries a cache/DB for prior results by key
- **Go/Gin:** Middleware with `sync.Map` or Redis-backed idempotency store
- **Java/Spring:** `HandlerInterceptor` with cache lookup

**Impact:** Enables safe client retries for network failures, especially critical for payment and order flows.

**Source:** [Stripe Idempotent Requests](https://stripe.com/docs/api/idempotent_requests), api-architecture-patterns.md Section 2

---

### API-08 OpenAPI Specification [MEDIUM]

**Detect:** API project without an `openapi.json` or `openapi.yaml` file. Endpoints undocumented in a machine-readable format.

**Fix:** Generate from code annotations or write spec-first. Lint in CI.

| Practice | Why |
|----------|-----|
| Schemas in `components/schemas` | Code generators produce clean types |
| `description` on every operation | Documentation quality |
| Request/response `examples` | Enables automated test generation |
| `tags` to group operations | Navigation in Swagger UI |
| Spec linting in CI (Spectral) | Catches naming issues, broken refs |
| Contract tests | Verify server matches spec |

Design-first (write YAML before code) produces cleaner contracts and enables frontend mocking during parallel development.

**Impact:** Machine-readable API contracts enable code generation, automated testing, and accurate documentation.

**Source:** [OpenAPI 3.1 Specification](https://swagger.io/specification/), [OpenAPI Best Practices](https://learn.openapis.org/best-practices.html), api-architecture-patterns.md Section 10

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

HATEOAS is optional for internal APIs but valuable for public APIs to reduce client coupling and enable API evolution without breaking changes.

**Impact:** Reduces client-side URL construction. Enables API evolution without breaking existing consumers.

**Source:** [Richardson Maturity Model Level 3](https://martinfowler.com/articles/richardsonMaturityModel.html), api-architecture-patterns.md Section 2

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

**Source:** [Apollo GraphQL Best Practices](https://www.apollographql.com/docs/apollo-server/performance/), api-architecture-patterns.md Sections 1 and 8
