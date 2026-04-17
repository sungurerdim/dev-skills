# Rules: Performance Compliance

Performance rules focused on resource safety, DoS prevention, and service continuity — compliance-relevant subset of performance. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Resource Exhaustion Prevention** | PRF-01–04 (2 CRITICAL, 2 MAJOR) | ~12 |
| **Query Safety** | PRF-05–07 (1 BLOCKER, 1 CRITICAL, 1 MAJOR) | ~55 |
| **Resource Cleanup** | PRF-08–10 (1 CRITICAL, 2 MAJOR) | ~85 |

---

## Resource Exhaustion Prevention

### PRF-01 [CRITICAL] Unbounded Collection Growth
In-memory collections (caches, maps, lists) must have size limits to prevent OOM.
- **Detect:** `Map`/`dict`/`HashMap` used as cache without eviction policy. Lists that grow per-request without bounds. Global caches without TTL or max size. `static Map<>` or module-level dicts that accumulate entries
- **Fix:** Add max size + eviction: LRU cache with bounded size. Python: `functools.lru_cache(maxsize=1000)` or `cachetools.TTLCache`. Node: `lru-cache`. Go: `groupcache` or manual with sync.Map + size check. Set TTL for time-sensitive data
- **Source:** OWASP API4:2023 (Resource Consumption)

### PRF-02 [CRITICAL] Memory Leak in Event Listeners
Event listeners, subscriptions, and callbacks must be cleaned up to prevent memory leaks.
- **Detect:** `addEventListener` without corresponding `removeEventListener`. Observable subscriptions without `unsubscribe` in cleanup. `setInterval`/`setTimeout` without `clearInterval`/`clearTimeout`. React: missing cleanup in `useEffect` return. Flutter: missing `dispose()` in `StatefulWidget`
- **Fix:** Always clean up: React `useEffect(() => { ...; return () => cleanup(); }, [])`. Flutter: `@override void dispose() { controller.dispose(); super.dispose(); }`. Node: `emitter.removeListener()` or `AbortController`
- **Source:** Web performance, mobile memory management

### PRF-03 [MAJOR] Unbounded Pagination
API endpoints returning lists must enforce pagination limits.
- **Detect:** List endpoints without `limit`/`pageSize` parameter. Default page size > 100. No maximum page size enforced. `SELECT *` without `LIMIT` on user-facing queries
- **Fix:** Default page size: 20-50. Max page size: 100. Always enforce server-side: `Math.min(requested, MAX_PAGE_SIZE)`. Return pagination metadata: `{data, total, page, pageSize, hasNext}`. Use cursor-based pagination for large datasets
- **Source:** OWASP API4:2023, REST API best practices

### PRF-04 [MAJOR] Background Job Timeout
Background jobs, workers, and scheduled tasks must have execution timeouts.
- **Detect:** Worker functions without timeout. Queue consumers that can run indefinitely. Cron jobs without max execution time. `while(true)` processing loops without heartbeat/timeout
- **Fix:** Set job-level timeout: Bull/BullMQ `timeout` option, Celery `time_limit`, Go `context.WithTimeout`. Add heartbeat for long-running jobs. Dead letter queue for failed/timed-out jobs
- **Source:** Distributed systems best practices

---

## Query Safety

### PRF-05 [BLOCKER] SQL Injection via String Concatenation
Database queries must never use string concatenation with user input.
- **Detect:** `f"SELECT * FROM users WHERE id = {user_id}"`, `"SELECT * FROM users WHERE id = " + id`, template literals in SQL strings, `cursor.execute("... " + variable)`
- **Fix:** Use parameterized queries: Python `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`. Node `db.query("SELECT * FROM users WHERE id = $1", [userId])`. Go `db.Query("SELECT * FROM users WHERE id = ?", userID)`. Use ORM query builders
- **Source:** OWASP A03:2021 (Injection), CWE-89

### PRF-06 [CRITICAL] N+1 Query Detection
Loops that execute database queries per iteration indicate N+1 problems.
- **Detect:** Database query inside `for`/`forEach`/`map` loop. ORM lazy loading in iteration (`user.posts` accessed per user in loop). Multiple identical queries in single request trace
- **Fix:** Use eager loading/joins: Django `select_related`/`prefetch_related`. SQLAlchemy `joinedload`. TypeORM `relations`/`leftJoinAndSelect`. Go: single query with `IN` clause. Batch queries: load all related records in one query, then map in memory
- **Source:** Database performance best practices

### PRF-07 [MAJOR] Missing Database Indexes
Columns used in WHERE, JOIN, ORDER BY, and foreign keys should have indexes.
- **Detect:** Queries filtering on columns without indexes. Foreign key columns without indexes. Frequent `ORDER BY` columns without indexes. Slow query logs showing full table scans
- **Fix:** Add indexes for frequently queried columns. Composite indexes for multi-column queries (leftmost prefix rule). Partial indexes for filtered subsets. Monitor: `EXPLAIN ANALYZE` for PostgreSQL, `EXPLAIN` for MySQL. Avoid over-indexing (each index has write cost)
- **Source:** Database performance tuning

---

## Resource Cleanup

### PRF-08 [CRITICAL] Unclosed Resources
File handles, database connections, and network sockets must be explicitly closed.
- **Detect:** `open()` without `with` statement (Python). `fs.open()` without `.close()` (Node). `sql.Open()` without `defer db.Close()` (Go). JDBC `Connection` without `try-with-resources` (Java). `File.open` without `ensure` block (Ruby)
- **Fix:** Use language-specific resource management: Python `with open() as f:`. Go `defer file.Close()`. Java `try (var conn = ...) {}`. Node: `using` (with Symbol.dispose) or explicit finally block. Rust: RAII handles cleanup automatically
- **Source:** CWE-404 (Resource Release)

### PRF-09 [MAJOR] Streaming for Large Data
Large file/data processing must use streaming, not load-all-into-memory.
- **Detect:** `readFileSync` / `read()` for files > 10MB. `response.json()` for large API responses. Loading entire database table into memory. Image/video processing without streaming
- **Fix:** Use streams: Node `createReadStream`. Python: iterate file object or `response.iter_content()`. Go: `io.Copy` or `bufio.Scanner`. For databases: cursor-based iteration, not `.fetchall()`. For APIs: paginate or use streaming responses
- **Source:** Memory safety best practices

### PRF-10 [MAJOR] Graceful Shutdown
Services must handle shutdown signals (SIGTERM, SIGINT) and drain active requests.
- **Detect:** No signal handler for SIGTERM/SIGINT. Server process that kills active requests on shutdown. Missing health check endpoint. No drain period before termination
- **Fix:** Handle SIGTERM: stop accepting new connections, drain active requests (30s timeout), close database connections, then exit. Node: `process.on('SIGTERM', ...)`. Go: `signal.NotifyContext`. Python: `signal.signal(signal.SIGTERM, handler)`. Add `/health` endpoint for orchestrator checks
- **Source:** 12-Factor App, Kubernetes best practices
