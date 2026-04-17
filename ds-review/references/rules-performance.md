# Rules: Performance & Network

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Performance** | PRF-01–07 (1 CRITICAL, 6 MAJOR) | ~12 |
| **Client-Side Performance** | PRF-08–10 (3 MAJOR) | ~78 |
| **Network & API** | NET-01–05, NET-07 (6 MAJOR) | ~115 |

---

## Performance

### PRF-01 [MAJOR] Response Time Targets
API: p95 < 200ms. Page load: < 3s. Background jobs: bounded timeout.
- **Detect:** No response time monitoring. Slow queries without indexes. Synchronous processing of heavy operations
- **Fix:** Profile with APM tools. Add database indexes for frequent queries. Move heavy work to background queues. Set timeouts on all external calls
- **Impact:** 100ms delay = 1% conversion loss (Amazon). p95 > 500ms = poor user experience
- **Source:** Google Web Vitals, Amazon Latency Study (100ms = 1% conversion loss)

### PRF-02 [MAJOR] Startup Time
Application cold start < 5s. Serverless cold start < 1s. Defer non-critical initialization.
- **Detect:** Heavy initialization on startup (loading all configs, prewarming all caches). Blocking I/O during boot. Large dependency trees slowing startup
- **Fix:** Lazy-load non-critical modules. Defer cache warming. Use connection pooling (not connect-on-boot). Minimize dependency tree for serverless
- **Source:** AWS Lambda Performance Optimization, Google Cloud Functions Cold Start Guide

### PRF-03 [MAJOR] Bundle/Binary Size
Track and optimize output size. Remove unused dependencies.
- **Detect:** No bundle analysis. Unused dependencies in lockfile. Large imports where tree-shaking possible
- **Fix:**
  - Node/Web: `webpack-bundle-analyzer` or `source-map-explorer`. Tree-shake. Dynamic imports for code splitting
  - Python: remove unused packages from requirements
  - Go: `go build -ldflags="-s -w"` for smaller binaries
  - Docker: multi-stage builds, distroless/alpine base images
- **Source:** webpack Bundle Analysis Guide, esbuild/Vite Optimization, Docker Multi-Stage Builds

### PRF-04 [MAJOR] Lazy Loading
Load resources on demand. Defer non-critical work.
- **Detect:** All modules imported eagerly. All images loaded at page init. Full dataset loaded when only summary needed
- **Fix:** Dynamic imports for routes/features. Lazy load images (Intersection Observer). Paginate database queries. Stream large responses
- **Source:** MDN Lazy Loading Guide, Intersection Observer API, HTTP Range Requests (RFC 7233)

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
- **Source:** Use The Index Luke (SQL Indexing), Django ORM N+1 Guide, Prisma Query Optimization

### PRF-06 [CRITICAL] Memory Leak Prevention
All subscriptions, connections, and resources properly cleaned up.
- **Detect:**
  - Node: event listeners not removed, streams not closed, intervals not cleared, database connections not returned to pool
  - Python: circular references without weak refs, file handles not closed (no `with` statement), unclosed database connections
  - Go: goroutine leaks (no context cancellation), unclosed channels, deferred close missing
  - Web: `addEventListener` without `removeEventListener`, `setInterval` without `clearInterval` in components
- **Fix:** Use cleanup patterns: `finally` blocks, `with` statements (Python), `defer` (Go), cleanup functions in useEffect (React). Monitor with heap snapshots. Use connection pooling with max limits
- **Impact:** Memory leaks → OOM crashes, degraded performance, increased infrastructure costs
- **Source:** Node.js Memory Leak Debugging Guide, Python gc Module, Go pprof, Chrome DevTools Heap Snapshot

### PRF-07 [MAJOR] Resource Optimization
Bounded concurrency, connection pooling, file handle limits.
- **Detect:**
  - Unbounded parallel operations (Promise.all on unlimited array)
  - New database connection per request instead of pooling
  - File handles not closed after read/write
  - No timeout on HTTP client requests
- **Fix:** Limit concurrency (p-limit, semaphore). Use connection pools (pg pool, SQLAlchemy pool). Set timeouts on all I/O operations. Close resources in finally/defer/with blocks
- **Source:** Node.js p-limit, PostgreSQL Connection Pooling Guide, Go Context and Cancellation

---

## Client-Side Performance

### PRF-08 [MAJOR] Unnecessary UI Rebuilds
UI components with unchanged inputs must not rebuild on every state change.
- **Detect:**
  - UI component eligible for immutability/memoization but not marked as such
  - State observation triggering full-tree rebuild instead of targeted update (watching entire state object instead of specific fields)
  - Leaf components (spacers, padding, icons, static text) recreated every render cycle
- **Fix:**
  - Mark immutable components: `const` (Flutter), `React.memo` (React/RN), `@Stable`/`@Immutable` (Compose), `EquatableView` (SwiftUI), `v-once` (Vue)
  - Use selective state observation: watch only needed fields, not entire state objects (Riverpod `select()`, Redux `useSelector`, Compose `derivedStateOf`, SwiftUI `@Observable` with access tracking)
  - Move expensive computations outside render/build cycle into memoized values or computed properties
- **Source:** React.memo API Reference, Flutter const Widget Optimization, Jetpack Compose Stability, Vue v-once Directive

### PRF-09 [MAJOR] Animation Layer Promotion
Animations must not trigger expensive layout recalculations or rebuild entire subtrees.
- **Detect:**
  - Animating layout-triggering properties (width, height, margin, padding) instead of compositor-only properties (transform, opacity)
  - Opacity/transparency changes wrapping complex subtrees (forces full-layer recomposite)
  - Animation callbacks rebuilding expensive children every frame instead of extracting static children
  - Animation lifecycle not synced with display refresh
- **Fix:**
  - Animate compositor-only properties via platform GPU path:
    - Flutter: `FadeTransition` instead of `Opacity`; `AnimatedBuilder(child:)` to build child once
    - iOS: animate `CALayer` properties (opacity, transform) instead of view layout
    - Android/Compose: `Modifier.graphicsLayer { alpha }` instead of `Modifier.alpha()` on complex subtrees
    - RN: `useNativeDriver: true`; `Reanimated` worklets for gesture-driven animations
    - Web: animate `transform`/`opacity` only; `will-change` hint for known targets; `requestAnimationFrame` for frame sync
  - Extract static children outside animation scope
  - Sync animation lifecycle with display refresh (vsync, CADisplayLink, Choreographer, requestAnimationFrame)
- **Source:** CSS Triggers (compositor-only properties), Flutter Animations Overview, Chrome Rendering Performance Guide

### PRF-10 [MAJOR] Cold Start Optimization
First meaningful frame must render within 2 seconds on target devices.
- **Detect:**
  - Heavy initialization (analytics, crash reporting, non-critical services) blocking first frame
  - Synchronous database migration or large file reads on main thread at startup
  - All feature modules loaded eagerly instead of on-demand
- **Fix:**
  - Defer non-critical init to after first frame:
    - Flutter: `WidgetsBinding.instance.addPostFrameCallback()`
    - iOS: `DispatchQueue.main.async` after `viewDidAppear`
    - Android: `Handler(Looper.getMainLooper()).post {}`; Compose: `LaunchedEffect`
    - RN: `InteractionManager.runAfterInteractions()`
    - Web: `requestIdleCallback()` or `setTimeout(fn, 0)`
  - Lazy-load feature modules
  - Run database migrations on background thread
- **Impact:** 49% of users expect <2s, 53% abandon >3s
- **Source:** Google Think with Google (53% abandon >3s), Flutter Deferred Components, requestIdleCallback MDN

---

## Network & API

### NET-01 [MAJOR] Data Source Strategy
Clear primary data source. Cache layers explicit and invalidatable.
- **Detect:** UI/client reads from multiple inconsistent sources. No caching strategy. Cache invalidation undefined
- **Fix:** Define source of truth per data type (DB, cache, external API). Cache with explicit TTL. Invalidate on writes. Document cache strategy
- **Source:** HTTP Caching (MDN), Redis Caching Patterns, Stale-While-Revalidate (RFC 5861)

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
- **Source:** OpenTelemetry Specification, Google SRE Book (Monitoring Distributed Systems), Datadog APM Guide
