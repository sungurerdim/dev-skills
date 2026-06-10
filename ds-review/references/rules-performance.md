# Rules: Performance & Network

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Performance** | PRF-01–07 (1 CRITICAL, 6 MAJOR) | ~12 |
| **Client-Side Performance** | PRF-08–10 (3 MAJOR) | ~78 |
| **Network & API** | NET-01–05, NET-07 (6 MAJOR) | ~115 |
| **Cost** | COST-01–06 (6 MAJOR) | ~185 |

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

---

## Cost

### COST-01 [MAJOR] Unbatched/Uncached Paid API Calls
Repeated identical calls to paid APIs without memoization or batching waste budget and increase latency.
- **Detect:**
  - Same prompt or input sent to LLM/geocoding/search API multiple times within a request or session without a cache layer
  - LLM calls with long, static system prompts and no prompt-caching header (Anthropic: `cache_control`, OpenAI: prompt caching)
  - Batch API available (LLM batch inference, geocoding batch endpoint) but single-item requests used where latency allows
  - Largest model (e.g. GPT-4o, Claude Opus) called for classification, extraction, or short summarization tasks a smaller model handles
- **Fix:** Add memoization keyed on request content (hash of prompt + params). Enable provider prompt-caching headers on static system-prompt prefixes. Route classification/extraction/short-gen tasks to a cheaper model tier. Use batch endpoints for bulk, non-interactive workloads
- **Impact:** LLM prompt caching typically reduces cost 50–90% on static prefix; model right-sizing 5–20×; missed batching can multiply per-item cost 10–100×
- **Source:** Anthropic Prompt Caching Docs, OpenAI Batch API, Google Maps Geocoding Batch

### COST-02 [MAJOR] Cloud Egress Waste
Cross-region/cross-AZ data transfer and origin-served assets generate avoidable egress charges.
- **Detect:**
  - Service A (region us-east-1) calls Service B (region eu-west-1) on every request — cross-region transfer billed per GB
  - Static assets (images, JS, CSS) served from compute origin (EC2, Cloud Run, App Engine) instead of CDN or object storage
  - Database read replica in a different AZ/region than the application, fetching large result sets on hot paths
  - Large binary blobs stored in DB and served via API response body instead of pre-signed object-storage URLs
- **Fix:** Co-locate services that exchange high-volume data in the same region/AZ. Serve static/media assets from CDN (CloudFront, Cloud CDN, Fastly) or object storage with direct pre-signed URLs. Move read replicas to the same AZ as the application tier. Return pre-signed URLs instead of proxying blobs through compute
- **Impact:** Cross-region egress typically $0.02–$0.09/GB; CDN origin-pull is a one-time cost, subsequent cache hits are free or near-free
- **Source:** AWS Data Transfer Pricing, GCP Network Egress Pricing, CDN Best Practices (MDN)

### COST-03 [MAJOR] Oversized Infra Defaults
Instance sizes or provisioned capacity far above observed load incur idle spend.
- **Detect:**
  - CPU utilization consistently < 20% on provisioned instances (check CloudWatch, Cloud Monitoring, Datadog)
  - RDS/Cloud SQL provisioned IOPS at maximum with actual IOPS < 30% of provisioned
  - Always-on staging/dev/preview environments running 24/7 without a shutdown schedule
  - Kubernetes requests/limits set to defaults (1 CPU, 512Mi) without profiling — either over-provisioned or a future OOM
- **Fix:** Right-size instances to next tier down when p95 CPU < 20% and p95 memory < 50% for 7+ days. Set RDS to autoscaling storage + gp3 instead of provisioned IOPS unless throughput-bound. Add start/stop schedules to non-prod environments (AWS Instance Scheduler, GCP resource policies). Profile containers under load and set requests/limits to observed p99 + 20% headroom
- **Impact:** Idle EC2/GCE instances at m5.2xlarge vs m5.large = 4× cost; dev environments running nights/weekends = ~66% waste
- **Source:** AWS Compute Optimizer, GCP Recommender, FinOps Foundation Right-Sizing Guide

### COST-04 [MAJOR] Missing Lifecycle Policies
Objects, logs, artifacts, and backups retained indefinitely accumulate unbounded storage cost.
- **Detect:**
  - S3/GCS/Azure Blob buckets with no lifecycle rule (check bucket policy or IaC)
  - CloudWatch Logs / Cloud Logging log groups with retention set to "Never expire"
  - CI/CD artifact stores (S3, GCS, Artifactory) retaining every build artifact with no TTL
  - Database backups kept beyond documented retention window with no automated deletion
  - Docker image registry (ECR, GCR, Docker Hub) accumulating all tags with no deletion policy
- **Fix:** Set S3/GCS lifecycle rules: transition to Infrequent Access after 30 days, Glacier after 90 days, delete after retention window. Set log group retention to ≤ 90 days for non-compliance workloads (adjust for regulatory requirements). Add CI artifact expiration (e.g., keep last 10 builds or 30 days). Define and automate backup retention (typically 7–35 days). Add ECR/GCR lifecycle policy to delete untagged images and old non-production tags
- **Impact:** S3 Standard ~$0.023/GB/month; Glacier ~$0.004/GB/month; logs with no TTL on a busy service can accumulate hundreds of GB/month
- **Source:** AWS S3 Lifecycle Policies, GCP Object Lifecycle Management, AWS CloudWatch Logs Retention, ECR Lifecycle Policies

### COST-05 [MAJOR] Polling Where Push Exists
Interval polling against APIs that offer webhooks, server-sent events, or streams wastes requests and budget.
- **Detect:**
  - `setInterval` / `sleep` loop calling a REST endpoint to check for state changes when the provider documents a webhook or event subscription
  - Database polling loop (`SELECT … WHERE status = 'pending'` on a timer) when a DB-level notification (`LISTEN/NOTIFY` in Postgres, change streams in MongoDB/DynamoDB) is available
  - Mobile app polling a backend for push-like data instead of using FCM/APNs/WebSocket
  - Third-party API (GitHub, Stripe, Twilio, SendGrid) polled for event status when the provider offers webhooks
- **Fix:** Replace polling loops with webhook receivers or event subscriptions for provider APIs. Use `LISTEN/NOTIFY` (Postgres), DynamoDB Streams, or Change Data Capture for DB-level events. Switch mobile to push notifications (FCM/APNs) or a persistent WebSocket/SSE channel. Where polling is unavoidable (no push available), apply exponential backoff and cap frequency to the minimum acceptable staleness
- **Impact:** 1-second polling = 86,400 API calls/day per client; webhook = 1 call per event. At $0.0004/1k calls (Twilio, SendGrid tiers), high-frequency polling can add hundreds of dollars/month
- **Source:** Webhook.site Best Practices, Stripe Webhooks Guide, PostgreSQL LISTEN/NOTIFY, Google FCM

### COST-06 [MAJOR] Pay-Per-Use Amplification
N+1 patterns, unthrottled retries, and unbounded fan-out multiply metered API calls.
- **Detect:**
  - Loop calling a paid API once per item (geocoding every address individually, enriching each record separately) when a batch endpoint exists
  - Retry logic on a metered endpoint with no backoff or jitter — failed requests retried immediately at full rate
  - Fan-out job that spawns one worker/task per input item with no concurrency cap, triggering unbounded parallel API calls on a burst workload
  - Event consumer that re-processes the same message multiple times due to missing idempotency key on the downstream paid API call
- **Fix:** Batch paid API calls to the provider's batch endpoint (geocoding, enrichment, LLM). Add exponential backoff + jitter on all retries against metered endpoints (delay * 2^attempt + random(0, delay)). Cap worker fan-out concurrency (semaphore, p-limit, bounded thread pool). Add idempotency keys on paid API calls inside event consumers to prevent double-billing on redelivery
- **Impact:** N+1 against a $0.005/call API on 10,000 records = $50 vs $0.05 with batching; unbounded retry storm on a metered endpoint can exhaust a monthly budget in minutes
- **Source:** AWS SQS Exactly-Once Processing, Stripe Idempotency Keys, Google Maps Batching Guide, Exponential Backoff and Jitter (AWS Architecture Blog)
