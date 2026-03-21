# API Architecture Patterns

A practical, tool-agnostic reference for solo developers building production-grade HTTP APIs.

---

## Table of Contents

1. [REST vs GraphQL Decision Matrix](#1-rest-vs-graphql-decision-matrix)
2. [REST Design Fundamentals](#2-rest-design-fundamentals)
3. [HTTP Status Codes Reference](#3-http-status-codes-reference)
4. [API Versioning](#4-api-versioning)
5. [Pagination: Cursor vs Offset](#5-pagination-cursor-vs-offset)
6. [Error Responses: RFC 9457 Problem Details](#6-error-responses-rfc-9457-problem-details)
7. [Middleware Patterns](#7-middleware-patterns)
8. [API Security: OWASP API Top 10 (2023)](#8-api-security-owasp-api-top-10-2023)
9. [HTTP Caching](#9-http-caching)
10. [OpenAPI / Swagger](#10-openapi--swagger)
11. [API Testing Patterns](#11-api-testing-patterns)
12. [Sources](#12-sources)

---

## 1. REST vs GraphQL Decision Matrix

REST remains dominant (83% of enterprises as of 2025), but GraphQL is preferred for complex, multi-client data needs. Neither replaces the other — they are complementary.

### Decision Table

| Factor | REST | GraphQL |
|---|---|---|
| Data fetching | Fixed endpoints; risk of over/under-fetching | Client requests exactly what it needs |
| HTTP caching | Native — CDN, browser, proxy caches work out of the box | Complex; requires Apollo Client or persisted queries |
| Error handling | Standard HTTP status codes | Always returns `200 OK`; errors embedded in JSON body |
| Learning curve | Low — widely understood | Higher — schema, resolvers, query language required |
| Real-time support | Polling or SSE; WebSocket add-on | Subscriptions built into spec |
| Security surface | Endpoint-based (simpler to audit) | Requires depth limiting, cost analysis, query allow-listing |
| Public/third-party APIs | Strongly preferred | Rarely appropriate |
| Mobile / multi-client UIs | Works; may require multiple round-trips | Excels — single query fetches exactly the UI's data shape |
| Team familiarity | Baseline for most developers | Requires investment to ramp up |
| Tooling maturity | Extremely mature | Growing rapidly (Apollo, Relay, Hasura) |

### When to Choose REST

- Public API surface consumed by unknown third parties
- Simple CRUD resources with predictable access patterns
- Team is small and HTTP expertise is the baseline
- Caching at the edge (CDN) is critical to your performance strategy
- Integrating with existing ecosystem tooling (Swagger, Postman, etc.)

### When to Choose GraphQL

- 3+ client types (web, mobile, IoT) need the same data in different shapes
- A single screen must aggregate data from multiple domain entities
- Highly relational data where traversals are common
- Reducing mobile payload size is a hard requirement
- Building a product where the frontend team iterates faster than the backend

### Hybrid Pattern (Recommended for Solo Dev)

Use REST for well-defined CRUD resources and expose a GraphQL endpoint only for complex aggregation queries. Keep the public-facing integration API as REST; use GraphQL internally.

---

## 2. REST Design Fundamentals

### URL Naming Conventions

```
GET    /orders              # list collection
POST   /orders              # create in collection
GET    /orders/{id}         # single resource
PUT    /orders/{id}         # full replace (idempotent)
PATCH  /orders/{id}         # partial update
DELETE /orders/{id}         # delete

GET    /customers/{id}/orders   # sub-collection (max 2 levels deep)
```

**Rules:**
- Use nouns, never verbs (`/orders` not `/create-order`)
- Plural nouns for collections (`/users`, `/products`)
- Lowercase with hyphens, never camelCase (`/blog-posts` not `/blogPosts`)
- Never expose database structure or internal implementation details
- Stop nesting at `collection/item/collection` — deeper nesting becomes brittle

### HTTP Method Semantics

| Method | Safe? | Idempotent? | Use case |
|---|---|---|---|
| `GET` | Yes | Yes | Read resource or collection |
| `POST` | No | No | Create new resource; server assigns URI |
| `PUT` | No | Yes | Full replacement of existing resource |
| `PATCH` | No | No | Partial update (JSON Merge Patch or JSON Patch) |
| `DELETE` | No | Yes | Remove resource |
| `HEAD` | Yes | Yes | Same as GET but no body; check existence/cache |
| `OPTIONS` | Yes | Yes | CORS preflight; introspect allowed methods |

**Idempotency note:** Sending the same `PUT` or `DELETE` multiple times must produce the same result. `POST` is not idempotent — duplicate submissions create duplicate resources. Use an idempotency key header (`Idempotency-Key: <uuid>`) for retry-safe `POST` operations (e.g., payments).

### HATEOAS

Include hypermedia links in responses to allow clients to discover available actions without out-of-band documentation:

```json
{
  "orderId": 3,
  "status": "pending",
  "links": [
    { "rel": "self",   "href": "/orders/3",        "method": "GET" },
    { "rel": "cancel", "href": "/orders/3/cancel",  "method": "POST" },
    { "rel": "customer","href": "/customers/12",    "method": "GET" }
  ]
}
```

HATEOAS is optional for internal APIs but valuable for public APIs to reduce client coupling.

---

## 3. HTTP Status Codes Reference

### Core Codes per Method

| Code | When to use |
|---|---|
| `200 OK` | GET, PUT, PATCH succeeded with body |
| `201 Created` | POST created resource; include `Location` header with new URI |
| `204 No Content` | DELETE or PUT/PATCH succeeded with no body to return |
| `301 Moved Permanently` | Resource URI changed permanently; include `Location` |
| `304 Not Modified` | Conditional GET; cached response is still valid |
| `400 Bad Request` | Malformed request syntax, invalid parameters |
| `401 Unauthorized` | Missing or invalid authentication credential |
| `403 Forbidden` | Authenticated but not authorized for this resource |
| `404 Not Found` | Resource does not exist |
| `405 Method Not Allowed` | HTTP method not supported on this endpoint |
| `409 Conflict` | State conflict (duplicate create, optimistic lock failure) |
| `415 Unsupported Media Type` | Content-Type not accepted |
| `422 Unprocessable Entity` | Syntactically valid but semantically invalid (validation errors) |
| `429 Too Many Requests` | Rate limit exceeded |
| `500 Internal Server Error` | Unexpected server-side failure |
| `503 Service Unavailable` | Server overloaded or in maintenance; include `Retry-After` |

**Do not** return `200 OK` with an error body — this breaks clients and monitoring tools.

---

## 4. API Versioning

### Strategy Comparison

| Strategy | Format | Cacheable | Pros | Cons |
|---|---|---|---|---|
| URI path | `/v1/orders` | Yes | Explicit; works with all tools | URL changes per version |
| Query string | `/orders?version=1` | Partial | No URL change | Easy to forget; cache issues |
| Header | `Accept: application/vnd.api+json;version=1` | No | Clean URLs | Hard to test in browser |

**Recommendation:** URI path versioning (`/v1/`) is the default for solo developers. It is explicit, cache-friendly, and compatible with all load balancers and API gateways.

### Versioning Rules

- Increment the major version only for breaking changes
- Non-breaking additions (new fields, new optional parameters) require no version bump
- Support at least two major versions simultaneously during transitions
- Announce deprecation timelines explicitly in response headers: `Deprecation: Sun, 01 Jan 2027 00:00:00 GMT`
- Never silently remove or rename fields in an existing version

---

## 5. Pagination: Cursor vs Offset

### Comparison Table

| Feature | Offset (`?limit=20&offset=40`) | Cursor (`?after=eyJ...&limit=20`) |
|---|---|---|
| Implementation complexity | Low | Moderate |
| Performance at scale | Degrades — DB must skip N rows | Constant — seeks directly to cursor position |
| Data consistency | Inserts/deletes during paging cause duplicates or skipped rows | Stable; immune to concurrent mutations |
| Random page access | Yes (`page=7`) | No — sequential only |
| Total count | Cheap (COUNT query) | Expensive or omitted |
| Best for | Admin UIs, small/static datasets, search results | Feeds, timelines, large tables, infinite scroll |

Cursor pagination shows a ~17x speedup over offset pagination on a 1 million-row PostgreSQL table at deep pages.

**Rule of thumb:** Use cursor pagination for any table expected to exceed 10,000 rows or any dataset with real-time inserts.

---

## 6. Error Responses: RFC 9457 Problem Details

RFC 9457 (IETF, July 2023) standardizes HTTP API error responses under the media type `application/problem+json`.

### Standard Fields

| Field | Required | Description |
|---|---|---|
| `type` | No (defaults to `about:blank`) | URI identifying the problem type; should link to documentation |
| `status` | No | HTTP status code integer (must match the actual HTTP status) |
| `title` | No | Short, stable, human-readable summary |
| `detail` | No | Specific explanation of this occurrence |
| `instance` | No | URI identifying this specific error occurrence |

### Example

```json
{
  "type": "https://api.example.com/problems/validation-error",
  "title": "Validation Error",
  "status": 422,
  "detail": "The request body contains invalid fields.",
  "instance": "/logs/requests/d24b2953",
  "errors": [
    { "pointer": "/email", "detail": "Must be a valid email address" },
    { "pointer": "/age",   "detail": "Must be 18 or older" }
  ]
}
```

### Key Rules

- The `status` field in the body **must match** the actual HTTP status code
- Clients **must ignore** unrecognized extension fields (forward-compatible)
- Use a consistent `type` URI per error class across your entire API
- Define a shared registry of error `type` URIs in your API documentation

---

## 7. Middleware Patterns

### Recommended Middleware Order

```
Request
  └─► CORS
  └─► Security headers (HSTS, X-Content-Type-Options, etc.)
  └─► Request ID injection
  └─► Request logging (structured)
  └─► Body parsing / content negotiation
  └─► Authentication (verify token/key → attach identity)
  └─► Rate limiting (per identity or IP)
  └─► Authorization (check permissions for route)
  └─► Route handler
  └─► Error handler (catches thrown errors, formats RFC 9457)
Response
```

### Rate Limiting

**Algorithms:**

| Algorithm | Burst handling | Best for |
|---|---|---|
| Fixed window | Spike at window boundary | Simple quotas |
| Sliding window | Smooth distribution | Fair rate enforcement |
| Token bucket | Yes — accumulate tokens | APIs that allow short bursts |
| Leaky bucket | No — constant drain rate | Strict throughput control |

**Stripe's four-layer approach:**
1. Request rate limiter — per user, per second
2. Concurrent request limiter — cap simultaneous in-flight requests
3. Fleet load shedder — reject non-critical traffic when near capacity
4. Worker utilization shedder — progressively shed lower-priority traffic

**Response headers:**
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 742
X-RateLimit-Reset: 1711929600
Retry-After: 30          # on 429 only
```

### Structured Logging

Log every request with a consistent schema:

| Field | Example |
|---|---|
| `request_id` | `"d24b2953-ce05-488e-bf31-67de50d3d085"` |
| `method` | `"POST"` |
| `path` | `"/v1/orders"` |
| `status` | `201` |
| `duration_ms` | `47` |
| `user_id` | `"usr_123"` (omit if unauthenticated) |

Return `X-Request-ID` in every response so clients can correlate with server logs.

---

## 8. API Security: OWASP API Top 10 (2023)

95% of organizations have experienced an API security incident (Salt Security).

| # | Risk | One-line mitigation |
|---|---|---|
| API1 | **Broken Object Level Authorization (BOLA)** — 40% of all API attacks | Validate caller owns the requested object on every endpoint |
| API2 | **Broken Authentication** | Use OAuth 2.1, JWT; enforce MFA; rate-limit auth endpoints |
| API3 | **Broken Object Property Level Authorization** | Return only authorized fields; whitelist writable properties |
| API4 | **Unrestricted Resource Consumption** | Rate limit; enforce max page size, body size, timeouts |
| API5 | **Broken Function Level Authorization** | Enforce role/scope checks on every function |
| API6 | **Unrestricted Access to Sensitive Business Flows** | Per-workflow rate limits; behavioral anomaly detection |
| API7 | **Server Side Request Forgery (SSRF)** | Validate and whitelist user-supplied URIs; block internal IPs |
| API8 | **Security Misconfiguration** | Strip stack traces; audit CORS; disable debug endpoints |
| API9 | **Improper Inventory Management** | Maintain live API inventory; sunset old versions |
| API10 | **Unsafe Consumption of APIs** | Validate third-party API data as you would user input |

**BOLA is the most critical** — it has held the #1 spot since 2019.

---

## 9. HTTP Caching

### Cache-Control Directives

| Directive | Meaning |
|---|---|
| `max-age=N` | Resource is fresh for N seconds |
| `no-cache` | Store but revalidate before reuse |
| `no-store` | Do not store at all |
| `public` | Shared caches (CDN, proxies) may store |
| `private` | Only browser cache may store |
| `immutable` | Do not revalidate on soft reload |
| `s-maxage=N` | Like `max-age` but for shared caches only |

### Caching by Resource Type

| Resource | Recommended directive |
|---|---|
| Static assets (hashed filename) | `public, max-age=31536000, immutable` |
| HTML pages | `no-cache, private` + ETag |
| Public API responses (stable) | `public, max-age=60, s-maxage=300` |
| Authenticated API responses | `private, no-cache` + ETag |
| Sensitive data | `no-store` |

### ETag Validation Flow

```
First request:
  Client  → GET /orders/1
  Server  ← 200 OK, ETag: "abc123"

Cache expired, revalidation:
  Client  → GET /orders/1, If-None-Match: "abc123"
  Server  ← 304 Not Modified  (no body — saves bandwidth)
         OR
  Server  ← 200 OK, ETag: "xyz789" (resource changed)
```

---

## 10. OpenAPI / Swagger

### Design-First vs Code-First

| Approach | Description | Recommended? |
|---|---|---|
| Design-first | Write the `.yaml` spec before writing code | Yes — cleaner contracts, enables mocking |
| Code-first | Generate spec from annotations after implementation | Acceptable for rapid prototyping |

### Best Practices

| Practice | Why |
|---|---|
| Define all schemas in `components/schemas`, not inline | Code generators produce friendlier names |
| Add `description` to every operation and field | Drives documentation quality |
| Include request and response `examples` | Enables automated test generation |
| Use `tags` to group operations | Navigation in Swagger UI |
| Version the spec file in source control | Treat as first-class source artifact |
| Run spec linting in CI (e.g., Spectral) | Catches naming inconsistencies, broken `$ref` |
| Implement contract tests | Verify running server matches the spec |

---

## 11. API Testing Patterns

### Test Layers

| Layer | What it validates | Tool examples |
|---|---|---|
| Unit | Individual handler/controller logic | Any test framework |
| Integration | Handler + database + middleware stack | Real DB, test containers |
| Contract | Running server matches OpenAPI spec | Dredd, Schemathesis |
| End-to-end | Full request/response cycle | Postman, Bruno |
| Load | Throughput, latency under load | k6, Locust |

### Example Test Matrix for `POST /v1/orders`

| Scenario | Expected status | Verified claim |
|---|---|---|
| Valid payload, authenticated | 201 | `Location` header present |
| Valid payload, unauthenticated | 401 | RFC 9457 body |
| Missing required field | 422 | `errors` array in body |
| Duplicate `Idempotency-Key` | 200 | Returns existing resource |
| Rate limit exceeded | 429 | `Retry-After` header present |
| Server error (injected fault) | 500 | No stack trace in body |

---

## 12. Sources

- [Web API Design Best Practices — Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
- [REST API Best Practices — Postman Blog](https://blog.postman.com/rest-api-best-practices/)
- [RESTful API Design Guide — Strapi](https://strapi.io/blog/restful-api-design-guide-principles-best-practices)
- [GraphQL vs REST API: Comparison 2025 — API7.ai](https://api7.ai/blog/graphql-vs-rest-api-comparison-2025)
- [GraphQL vs REST — Postman Blog](https://blog.postman.com/graphql-vs-rest/)
- [OWASP API Security Top 10 – 2023 (official)](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [OWASP API Security Top 10 Explained — Salt Security](https://salt.security/blog/owasp-api-security-top-10-explained)
- [RFC 9457: Problem Details for HTTP APIs (IETF)](https://www.rfc-editor.org/rfc/rfc9457.html)
- [Problem Details RFC 9457 — Swagger.io](https://swagger.io/blog/problem-details-rfc9457-doing-api-errors-well/)
- [Scaling Your API with Rate Limiters — Stripe Engineering](https://stripe.com/blog/rate-limiters)
- [10 Best Practices for API Rate Limiting 2025 — Zuplo](https://zuplo.com/learning-center/10-best-practices-for-api-rate-limiting-in-2025)
- [Comparing Cursor and Offset Pagination — Zendesk Developer Docs](https://developer.zendesk.com/documentation/api-basics/pagination/comparing-cursor-pagination-and-offset-pagination/)
- [Understanding Cursor Pagination Deep Dive — Milan Jovanovic](https://www.milanjovanovic.tech/blog/understanding-cursor-pagination-and-why-its-so-fast-deep-dive)
- [HTTP Caching — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [ETag Header — MDN Web Docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/ETag)
- [OpenAPI Best Practices — Official OpenAPI Documentation](https://learn.openapis.org/best-practices.html)
- [OpenAPI Specification Best Practices — Gravitee](https://www.gravitee.io/blog/openapi-specification-structure-best-practices)
- [OpenAPI Specification v3.1.0 — Swagger](https://swagger.io/specification/)
