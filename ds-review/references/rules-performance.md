# Rules: Performance & Network

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Performance** | PRF-01–07 (1 CRITICAL, 6 MAJOR) | ~12 |
| **Network & API** | NET-01–05, NET-07 (6 MAJOR) | ~80 |

---

## Performance

### PRF-01 [MAJOR] Response Time Targets
API: p95 < 200ms. Page load: < 3s. Background jobs: bounded timeout.
- **Detect:** No response time monitoring. Slow queries without indexes. Synchronous processing of heavy operations
- **Fix:** Profile with APM tools. Add database indexes for frequent queries. Move heavy work to background queues. Set timeouts on all external calls
- **Impact:** 100ms delay = 1% conversion loss (Amazon). p95 > 500ms = poor user experience
- **Source:** Web performance best practices

### PRF-02 [MAJOR] Startup Time
Application cold start < 5s. Serverless cold start < 1s. Defer non-critical initialization.
- **Detect:** Heavy initialization on startup (loading all configs, prewarming all caches). Blocking I/O during boot. Large dependency trees slowing startup
- **Fix:** Lazy-load non-critical modules. Defer cache warming. Use connection pooling (not connect-on-boot). Minimize dependency tree for serverless
- **Source:** Serverless optimization, Application performance

### PRF-03 [MAJOR] Bundle/Binary Size
Track and optimize output size. Remove unused dependencies.
- **Detect:** No bundle analysis. Unused dependencies in lockfile. Large imports where tree-shaking possible
- **Fix:**
  - Node/Web: `webpack-bundle-analyzer` or `source-map-explorer`. Tree-shake. Dynamic imports for code splitting
  - Python: remove unused packages from requirements
  - Go: `go build -ldflags="-s -w"` for smaller binaries
  - Docker: multi-stage builds, distroless/alpine base images
- **Source:** Build optimization guides

### PRF-04 [MAJOR] Lazy Loading
Load resources on demand. Defer non-critical work.
- **Detect:** All modules imported eagerly. All images loaded at page init. Full dataset loaded when only summary needed
- **Fix:** Dynamic imports for routes/features. Lazy load images (Intersection Observer). Paginate database queries. Stream large responses
- **Source:** Performance best practices

### PRF-05 [MAJOR] Efficient Data Queries
No N+1 queries. Paginate large results. Select only needed fields.
- **Detect:**
  - ORM queries in loops (N+1 pattern)
  - `SELECT *` on tables with many columns
  - No pagination on list endpoints
  - Missing database indexes on filtered/sorted columns
  - Search: query calls inside `for`/`forEach`/`map` loops
- **Fix:** Use eager loading/joins for related data. Select specific fields. Paginate with cursor or offset. Add indexes for WHERE/ORDER BY columns. Use `EXPLAIN` to verify query plans
- **Impact:** N+1 with 100 items = 101 queries instead of 2. Linear performance degradation
- **Source:** Database performance, ORM best practices

### PRF-06 [CRITICAL] Memory Leak Prevention
All subscriptions, connections, and resources properly cleaned up.
- **Detect:**
  - Node: event listeners not removed, streams not closed, intervals not cleared, database connections not returned to pool
  - Python: circular references without weak refs, file handles not closed (no `with` statement), unclosed database connections
  - Go: goroutine leaks (no context cancellation), unclosed channels, deferred close missing
  - Web: `addEventListener` without `removeEventListener`, `setInterval` without `clearInterval` in components
- **Fix:** Use cleanup patterns: `finally` blocks, `with` statements (Python), `defer` (Go), cleanup functions in useEffect (React). Monitor with heap snapshots. Use connection pooling with max limits
- **Impact:** Memory leaks cause OOM crashes, degraded performance, and increased infrastructure costs
- **Source:** Platform memory management guides

### PRF-07 [MAJOR] Resource Optimization
Bounded concurrency, connection pooling, file handle limits.
- **Detect:**
  - Unbounded parallel operations (Promise.all on unlimited array)
  - New database connection per request instead of pooling
  - File handles not closed after read/write
  - No timeout on HTTP client requests
- **Fix:** Limit concurrency (p-limit, semaphore). Use connection pools (pg pool, SQLAlchemy pool). Set timeouts on all I/O operations. Close resources in finally/defer/with blocks
- **Source:** Resource management best practices

---

## Network & API

### NET-01 [MAJOR] Data Source Strategy
Clear primary data source. Cache layers explicit and invalidatable.
- **Detect:** UI/client reads from multiple inconsistent sources. No caching strategy. Cache invalidation undefined
- **Fix:** Define source of truth per data type (DB, cache, external API). Cache with explicit TTL. Invalidate on writes. Document cache strategy
- **Source:** Caching best practices

### NET-02 [MAJOR] Exponential Backoff + Jitter
Retry transient failures with backoff. Cap retries.
- **Detect:** Fixed-interval retries. Immediate retry flooding. No max retry limit. No distinction between transient and permanent errors
- **Fix:** delay * 2^attempt + random jitter. Max 3-5 retries. Cap at 30-60s. Only retry on transient errors (5xx, timeout, connection refused). Don't retry 4xx
- **Source:** AWS Architecture Blog, Resilience Patterns

### NET-03 [MAJOR] Circuit Breaker
Stop calling failing services after threshold.
- **Detect:** Repeated calls to failing endpoint without protection. No failure tracking. Cascading failures across services
- **Fix:** Track failure rate. Open circuit after N failures. Half-open on cooldown. Close on success. Return fallback/cached data during open state
- **Source:** Release It! (Michael Nygard), Resilience Patterns

### NET-04 [MAJOR] Cache Strategy
Multi-layer caching with clear TTL and invalidation.
- **Detect:** No caching. Full DB query every request. No HTTP cache headers. No in-memory cache for hot data
- **Fix:** L1: in-memory (LRU) for hot data. L2: Redis/Memcached for shared cache. L3: HTTP cache headers (Cache-Control, ETag). Stale-while-revalidate where appropriate. Cache invalidation on write
- **Source:** HTTP Caching MDN, Redis Caching Patterns

### NET-05 [MAJOR] API Design Consistency
Consistent URL patterns, HTTP methods, error responses, and pagination across all endpoints.
- **Detect:**
  - Mixed naming: `/getUsers` and `/users` in same API
  - POST used for reads, GET used for writes
  - Inconsistent error response shapes across endpoints
  - No pagination on list endpoints
  - No API versioning strategy
- **Fix:** RESTful conventions: nouns for resources, HTTP verbs for actions. Consistent error shape: `{ error: { code, message, details } }`. Cursor-based pagination for large datasets. URL or header-based versioning. Document with OpenAPI/Swagger
- **Impact:** Inconsistent API design multiplies integration effort and bugs for every consumer
- **Source:** REST API Design Guidelines, JSON:API

### NET-07 [MAJOR] Request/Response Observability
Structured logging with correlation IDs. Request tracing across services.
- **Detect:**
  - No request ID/correlation ID in logs
  - Unstructured log messages
  - No request duration tracking
  - No error rate monitoring
- **Fix:** Generate unique request ID per request. Pass through all service calls. Log: request_id, method, path, status, duration, user_id (hashed). Use structured JSON logging. Integrate with APM (Datadog, New Relic, OpenTelemetry)
- **Source:** Observability best practices, OpenTelemetry
