# Rules: Performance Compliance

Performance rules focused on resource safety, DoS prevention, and service continuity — compliance-relevant subset of performance. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Resource Exhaustion Prevention** | PRF-01–04 (2 CRITICAL, 2 HIGH) | ~12 |
| **Query Safety** | PRF-05–07 (1 BLOCKER, 1 CRITICAL, 1 HIGH) | ~55 |
| **Resource Cleanup** | PRF-08–10 (1 CRITICAL, 2 HIGH) | ~85 |

---

## Resource Exhaustion Prevention

### PRF-01 [CRITICAL] Unbounded Collection Growth
In-memory collections (caches, maps, lists) must have size limits to prevent OOM.
- **Detect:** `Map`/`dict`/`HashMap` used as cache without eviction policy. Lists that grow per-request without bounds. Global caches without TTL or max size. `static Map<>` or module-level dicts that accumulate entries
- **Fix:** Add max size + eviction: LRU cache with bounded size. Python: `functools.lru_cache(maxsize=1000)` or `cachetools.TTLCache`. Node: `lru-cache`. Go: `groupcache` or manual with sync.Map + size check. Set TTL for time-sensitive data
- **Impact:** An unbounded in-memory collection grows until it exhausts available memory and crashes the process — a slow, then sudden, outage.
- **Source:** OWASP API4:2023 (Resource Consumption)

### PRF-02 [CRITICAL] Memory Leak in Event Listeners
Event listeners, subscriptions, and callbacks must be cleaned up to prevent memory leaks.
- **Detect:** `addEventListener` without corresponding `removeEventListener`. Observable subscriptions without `unsubscribe` in cleanup. `setInterval`/`setTimeout` without `clearInterval`/`clearTimeout`. React: missing cleanup in `useEffect` return. Flutter: missing `dispose()` in `StatefulWidget`
- **Fix:** Always clean up: React `useEffect(() => { ...; return () => cleanup(); }, [])`. Flutter: `@override void dispose() { controller.dispose(); super.dispose(); }`. Node: `emitter.removeListener()` or `AbortController`
- **Impact:** Uncleaned listeners/subscriptions/timers keep referenced objects alive after they should be freed — memory grows with every mount/unmount cycle until the app slows or crashes.
- **Source:** Web performance, mobile memory management

### PRF-03 [HIGH] Unbounded Pagination
API endpoints returning lists must enforce pagination limits.
- **Detect:** List endpoints without `limit`/`pageSize` parameter. Default page size > 100. No maximum page size enforced. `SELECT *` without `LIMIT` on user-facing queries
- **Fix:** Default page size: 20-50. Max page size: 100. Always enforce server-side: `Math.min(requested, MAX_PAGE_SIZE)`. Return pagination metadata: `{data, total, page, pageSize, hasNext}`. Use cursor-based pagination for large datasets
- **Impact:** An endpoint that returns unbounded lists lets one request (or one attacker) force the server to load and serialize an arbitrarily large result set, exhausting memory or bandwidth.
- **Source:** OWASP API4:2023, REST API best practices

### PRF-04 [HIGH] Background Job Timeout
Background jobs, workers, and scheduled tasks must have execution timeouts.
- **Detect:** Worker functions without timeout. Queue consumers that can run indefinitely. Cron jobs without max execution time. `while(true)` processing loops without heartbeat/timeout
- **Fix:** Set job-level timeout: Bull/BullMQ `timeout` option, Celery `time_limit`, Go `context.WithTimeout`. Add heartbeat for long-running jobs. Dead letter queue for failed/timed-out jobs
- **Impact:** A job or worker with no timeout can hang indefinitely, holding its slot/resources and starving the queue behind it.
- **Source:** Distributed systems best practices

---

## Query Safety

### PRF-05 [BLOCKER] SQL Injection via String Concatenation
Database queries must never use string concatenation with user input.
- **Detect:** `f"SELECT * FROM users WHERE id = {user_id}"`, `"SELECT * FROM users WHERE id = " + id`, template literals in SQL strings, `cursor.execute("... " + variable)`
- **Fix:** Use parameterized queries: Python `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`. Node `db.query("SELECT * FROM users WHERE id = $1", [userId])`. Go `db.Query("SELECT * FROM users WHERE id = ?", userID)`. Use ORM query builders
- **Impact:** String-concatenated SQL is the textbook SQL-injection vector — an attacker-controlled value can read, modify, or delete arbitrary data.
- **Source:** OWASP A05:2025 (Injection), CWE-89

### PRF-06 [CRITICAL] N+1 Query Detection
Loops that execute database queries per iteration indicate N+1 problems.
- **Detect:** Database query inside `for`/`forEach`/`map` loop. ORM lazy loading in iteration (`user.posts` accessed per user in loop). Multiple identical queries in single request trace
- **Fix:** Use eager loading/joins: Django `select_related`/`prefetch_related`. SQLAlchemy `joinedload`. TypeORM `relations`/`leftJoinAndSelect`. Go: single query with `IN` clause. Batch queries: load all related records in one query, then map in memory
- **Impact:** A query per loop iteration turns an O(1) page load into O(n) database round-trips — latency and DB load scale with result-set size instead of staying flat.
- **Source:** Database performance best practices

### PRF-07 [HIGH] Missing Database Indexes
Columns used in WHERE, JOIN, ORDER BY, and foreign keys should have indexes.
- **Detect:** Queries filtering on columns without indexes. Foreign key columns without indexes. Frequent `ORDER BY` columns without indexes. Slow query logs showing full table scans
- **Fix:** Add indexes for frequently queried columns. Composite indexes for multi-column queries (leftmost prefix rule). Partial indexes for filtered subsets. Monitor: `EXPLAIN ANALYZE` for PostgreSQL, `EXPLAIN` for MySQL. Avoid over-indexing (each index has write cost)
- **Impact:** A frequently filtered/joined column with no index forces a full table scan on every query — response times degrade sharply as the table grows.
- **Source:** Database performance tuning

---

## Resource Cleanup

### PRF-08 [CRITICAL] Unclosed Resources
File handles, database connections, and network sockets must be explicitly closed.
- **Detect:** `open()` without `with` statement (Python). `fs.open()` without `.close()` (Node). `sql.Open()` without `defer db.Close()` (Go). JDBC `Connection` without `try-with-resources` (Java). `File.open` without `ensure` block (Ruby)
- **Fix:** Use language-specific resource management: Python `with open() as f:`. Go `defer file.Close()`. Java `try (var conn = ...) {}`. Node: `using` (with Symbol.dispose) or explicit finally block. Rust: RAII handles cleanup automatically
- **Impact:** An unclosed file handle, connection, or socket leaks a limited OS/pool resource on every call — the process eventually hits the descriptor or connection ceiling and starts failing unrelated requests.
- **Source:** CWE-404 (Resource Release)

### PRF-09 [HIGH] Streaming for Large Data
Large file/data processing must use streaming, not load-all-into-memory.
- **Detect:** `readFileSync` / `read()` for files > 10MB. `response.json()` for large API responses. Loading entire database table into memory. Image/video processing without streaming; hash/parse/transcode of user files running on the main/UI thread
- **Fix:** Use streams: Node `createReadStream`. Python: iterate file object or `response.iter_content()`. Go: `io.Copy` or `bufio.Scanner`. For databases: cursor-based iteration, not `.fetchall()`. For APIs: paginate or use streaming responses. Run unbounded-size file operations off the main thread (worker/isolate) as well as streamed — the failure mode is a crash or frozen UI (OOM/ANR), not slowness, so this is a hard requirement, not an optimization. (XR-025)
- **Impact:** Loading a large file or dataset fully into memory before processing it scales memory use with input size — a large-enough file OOMs the process regardless of how much RAM is provisioned.
- **Source:** Memory safety best practices

### PRF-10 [HIGH] Graceful Shutdown
Services must handle shutdown signals (SIGTERM, SIGINT) and drain active requests.
- **Detect:** No signal handler for SIGTERM/SIGINT. Server process that kills active requests on shutdown. Missing health check endpoint. No drain period before termination
- **Fix:** Handle SIGTERM: stop accepting new connections, drain active requests (30s timeout), close database connections, then exit. Node: `process.on('SIGTERM', ...)`. Go: `signal.NotifyContext`. Python: `signal.signal(signal.SIGTERM, handler)`. Add `/health` endpoint for orchestrator checks
- **Impact:** Killing in-flight requests on shutdown drops user-visible work mid-transaction and can leave data in a half-written state on every deploy or scale-down.
- **Source:** 12-Factor App, Kubernetes best practices
