# Perf — measured speed, bounded resources, cost

Every finding names its measurement or the code that makes the cost grow; nothing is optimized without a baseline (kernel §2). Queries, indexes, N+1 and pagination are DB-02, DB-06 and API-06; timeouts, retries and pool limits are NWK-07, NWK-09 and NWK-10.

### PRF-12 [HIGH] Performance work without a measurement
- **Detect:** optimization commits or PRs with no before/after numbers; caching, memoization or pooling added with no profile behind it; no latency, size or startup budget anywhere, or a budget no gate checks or one already exceeded at adoption; a public web UI with lab scores tracked and field data (real-user p75) not.
- **Mech:** T `git log --since=90.days -i -E --grep='perf|optimi[sz]|faster|speed' --format='%h %s'`
- **Fix:** baseline, change, the same measurement again; a budget is the measured current value plus a margin, warned on drift in the gate; keep lab data for regressions and field data for user truth.
- **Impact:** unmeasured optimization targets the wrong bottleneck, and a fictional budget teaches everyone to ignore budgets.
- **Source:** Knuth, "Structured Programming with go to Statements" (1974); web.dev, performance budgets and lab vs field data (https://web.dev/articles/lab-and-field-data-differences).

### PRF-02 [HIGH] Startup does work the first screen or request does not need
- **Detect:** analytics, crash reporting, cache warming, migrations, large file reads or every feature module initialized before the first frame or first request; blocking I/O on the main or UI thread at start; all routes imported eagerly; a full dataset loaded where a page or a summary is shown.
- **Mech:** M (a startup trace or profile)
- **Fix:** defer non-critical init until after the first frame or request (the platform's post-frame or idle callback); lazy-load routes and features; paginate or stream data.
- **Impact:** users wait or abandon before the first screen, and every serverless cold start pays the full cost.
- **Source:** web.dev, Largest Contentful Paint (https://web.dev/articles/lcp); Android, App startup time (https://developer.android.com/topic/performance/vitals/launch-time); Apple, Reducing your app's launch time.

### PRF-03 [HIGH] Shipped size not tracked
applies_when: ui≠none
- **Detect:** no bundle or binary size measurement; a whole library imported where a subpath or tree-shaken import exists; no code splitting between routes.
- **Mech:** M (the bundler's analyzer or build output sizes)
- **Fix:** measure with the bundler's analyzer (source-map-explorer, the build tool's stats); import narrowly; split per route; set the size budget per PRF-12.
- **Impact:** every page load and update downloads code most sessions never run.
- **Source:** web.dev, Performance budgets 101 (https://web.dev/articles/performance-budgets-101).

### PRF-06 [CRITICAL] Resource not released
- **Detect:** listeners, subscriptions, timers or observers with no removal on teardown (`addEventListener` without `removeEventListener`, an effect without cleanup, a controller without `dispose()`); files, sockets or connections opened outside the language's scoped form (Python `with`, Java try-with-resources, Kotlin `use`, C# `using`, Go `defer Close()`, JS `try/finally`, PHP `finally`; Rust RAII handles it); closures or long-lived objects holding short-lived UI objects strongly.
- **Mech:** T `ruff check --select SIM115 --output-format concise .` · `git grep -nIE 'addEventListener\(|\.subscribe\(' -- ':!*test*' ':!*.md'`
- **Fix:** release in the scoped form or the teardown hook of the framework; confirm with a heap snapshot or descriptor count over repeated mount/unmount or requests.
- **Impact:** memory or descriptors grow with every cycle until the process slows, hits its limit and crashes.
- **Source:** CWE-401; CWE-404.

### PRF-07 [HIGH] Unbounded concurrency or connections
- **Detect:** `Promise.all`, `gather` or goroutines over an input-sized collection with no limit; one task per item on a burst workload calling a metered API; a new database or HTTP connection per request; a pool size never set or never sized against measured concurrency.
- **Mech:** T `git grep -nIE 'Promise\.all\(|asyncio\.gather\(\*|go func\(' -- ':!*test*' ':!*.md'`
- **Fix:** a semaphore or worker pool sized from the downstream's measured capacity; one shared pool per process with an explicit maximum (NWK-09).
- **Impact:** a traffic spike exhausts connections and descriptors and becomes an outage for every consumer of the same resource.
- **Source:** CWE-770 (Allocation of Resources Without Limits or Throttling).

### RTP-01 [CRITICAL] Unbounded in-memory growth
- **Detect:** a map, dict or list used as a cache with no maximum size or TTL; module-level or static collections that gain entries per request; memoization with no bound.
- **Mech:** T `git grep -nIE '@(functools\.)?cache([^[:alnum:]_]|$)|lru_cache\(maxsize=None\)|static .*Map<|(const|let|var) [[:alnum:]_]+ = new Map\(\)' -- ':!*test*' ':!*.md'`
- **Fix:** a maximum size plus eviction (LRU or TTL) using the platform's bounded cache.
- **Impact:** the process grows until it runs out of memory and crashes — slowly, then suddenly.
- **Source:** CWE-770; OWASP API4:2023 Unrestricted Resource Consumption.

### RTP-04 [HIGH] Background job without a time limit
applies_when: api≠none or deploy≠none
- **Detect:** workers, queue consumers or scheduled jobs with no execution timeout; `while true` processing loops with no heartbeat; failed jobs retried forever with no dead-letter queue.
- **Mech:** M
- **Fix:** a job-level timeout in the queue library or a context deadline; a heartbeat for long jobs; a dead-letter queue for jobs that fail or time out.
- **Impact:** one hung job holds its slot forever and starves the queue behind it.
- **Source:** Nygard, *Release It!* (timeouts, steady state).

### RTP-09 [HIGH] Large input loaded whole or on the UI thread
- **Detect:** whole-file reads, full response bodies or full query results (`readFileSync`, `.read()`, `fetchall()`, `io.ReadAll`, `readAllBytes`) on input whose size the user or data controls; hashing, parsing or transcoding user files on the main or UI thread.
- **Mech:** T `git grep -nIE 'readFileSync\(|\.read\(\)|fetchall\(\)|io\.ReadAll\(|readAllBytes\(|ReadAllBytes\(' -- ':!*test*' ':!*.md'`
- **Fix:** stream or iterate (file streams, cursors, paginated or streamed responses); run unbounded-size work off the UI thread.
- **Impact:** a large enough input runs out of memory or freezes the UI whatever the hardware.
- **Source:** CWE-400 (Uncontrolled Resource Consumption).

### PRF-11 [HIGH] Per-item I/O on a bulk path
- **Detect:** per-row INSERT or write loops in import or bulk-load paths; a flush or fsync per record; allocation inside a profiler-confirmed hot loop.
- **Mech:** M
- **Fix:** the platform's bulk API (Postgres `COPY`, multi-row inserts, batch endpoints) in one transaction; coalesced flushes; pooled allocation only where the profiler points.
- **Impact:** n records cost n round-trips or syscalls, and allocation churn shows up as tail-latency spikes.
- **Source:** PostgreSQL, Populating a Database (COPY).

### PRF-08 [HIGH] UI rebuilds parts whose inputs did not change
applies_when: ui≠none
- **Detect:** components watching a whole state object instead of the fields they use; leaf components rebuilt every render that the framework could keep (`const` in Flutter, `React.memo`, Compose stability, `v-once`); memoized components receiving new inline objects or functions every render; one app-wide context whose every change re-renders all consumers; memoization the profiler cannot justify.
- **Mech:** M (the framework's profiler)
- **Fix:** select only the fields used; stabilize prop identity before memoizing; split contexts by change frequency; mark constant leaves constant; remove memoization with no profile behind it.
- **Impact:** unchanged subtrees burn CPU and battery and drop frames on lower-end devices.
- **Source:** React, `memo` and Profiler docs; Flutter, performance best practices; Jetpack Compose, stability.

### PRF-09 [HIGH] Animation or layout reads force layout every frame
applies_when: ui≠none
- **Detect:** animating layout properties (width, height, top, margin) instead of transform and opacity; layout reads (`offsetHeight`, `getBoundingClientRect`) right after writes or inside loops and scroll handlers; opacity animated over a large subtree; animation callbacks rebuilding static children.
- **Mech:** T `git grep -nIE 'offset(Height|Width|Top|Left)([^[:alnum:]_]|$)|getBoundingClientRect\(' -- '*.js' '*.ts' '*.jsx' '*.tsx' '*.vue' '*.svelte'`
- **Fix:** animate compositor-only properties through the platform's GPU path; batch reads before writes in one frame; build static children once outside the animation.
- **Impact:** each forced layout re-runs style and layout mid-frame — the main cause of visible jank in lists, drags and animations.
- **Source:** web.dev, Avoid large, complex layouts and layout thrashing; Flutter, performance best practices.

### PRF-14 [HIGH] Offscreen content rendered
applies_when: ui∋web
- **Detect:** lists of 100+ items fully rendered with no virtualization; long below-the-fold sections without `content-visibility: auto`; dense, periodically refreshed grids that measure or lay out twice per frame.
- **Mech:** M
- **Fix:** virtualize long lists (viewport plus overscan); `content-visibility: auto` with `contain-intrinsic-size`; one layout pass per frame.
- **Impact:** render and interaction cost scale with data size instead of the viewport.
- **Source:** web.dev, content-visibility (https://web.dev/articles/content-visibility).

### PRF-16 [HIGH] Interaction blocks the main thread
applies_when: ui∋web
- **Detect:** heavy synchronous work (large loops, JSON parsing, render batches) in input handlers; long tasks over 50 ms during interactions; field INP p75 above 200 ms.
- **Mech:** M (Performance panel or long-task observer)
- **Fix:** paint the visual response first; split work with `scheduler.yield()` (chunked `setTimeout` as fallback); move pure computation to a worker.
- **Impact:** every click waits for the next paint, which users feel as a laggy app.
- **Source:** web.dev, Interaction to Next Paint (https://web.dev/articles/inp).

### NET-04 [HIGH] Cache without an owner, a TTL or invalidation
- **Detect:** a cache in front of data with no stated source of truth, no TTL and no invalidation on write; clients reading the same data from several sources that disagree; a cache added where no measurement showed the need.
- **Mech:** M
- **Fix:** one source of truth per data type; cache-aside with an explicit TTL; invalidate or update on write; write the strategy beside the cache.
- **Impact:** stale or inconsistent reads that are hard to reproduce.
- **Source:** RFC 9111 (HTTP Caching); RFC 5861 (stale-while-revalidate).

### NET-07 [HIGH] HTTP cache directives do not match the content
applies_when: ui∋web or api≠none
- **Detect:** fingerprinted assets without `immutable` and a long `max-age`; tolerant dynamic responses without `stale-while-revalidate`; no `ETag` or `Last-Modified`, so no 304 path; a service worker using one strategy for static and dynamic content.
- **Mech:** M
- **Fix:** hashed assets `max-age=31536000, immutable`; tolerant dynamic responses `stale-while-revalidate`; send validators; cache-first for static, network-first for navigations.
- **Impact:** unchanged bytes are downloaded on every visit, or stale data is served as fresh.
- **Source:** RFC 9110; RFC 9111 (https://www.rfc-editor.org/rfc/rfc9111).

### NET-08 [HIGH] Cache miss that amplifies
- **Detect:** a hot key expiring under concurrent load with every request recomputing it; identical TTLs on keys filled together; repeated lookups of known-absent records hitting the primary store.
- **Mech:** M
- **Fix:** request coalescing (single-flight) on cold or expired hot keys; jittered TTLs; cache not-found results with a short TTL.
- **Impact:** one expired key becomes a thundering herd against the primary store.
- **Source:** RFC 5861; Nygard, *Release It!* (dogpile).

### COST-01 [HIGH] Paid API calls repeated, unbatched or oversized
applies_when: integrations≠none
- **Detect:** the same input sent to a paid API (LLM, geocoding, search) several times without a cache; a long static prompt prefix without the provider's prompt caching; single-item calls where a batch endpoint exists and latency allows; the largest model used for classification or extraction; no per-call cost record.
- **Mech:** M
- **Fix:** memoize by a hash of the input; enable prompt caching on static prefixes; batch non-interactive work; route simple tasks to a smaller model; log tokens or cost per call.
- **Impact:** spend multiplies with traffic for no extra result, and nobody can say which feature costs what.
- **Source:** provider docs on prompt caching and batch APIs (Anthropic, OpenAI, Google Maps); FinOps Framework.

### COST-05 [HIGH] Polling where push exists
- **Detect:** a timer or sleep loop calling an API or database to check for changes when the provider offers webhooks, server-sent events, change streams or `LISTEN/NOTIFY`; mobile apps polling for push-like data.
- **Mech:** T `git grep -nIE 'setInterval\(|time\.sleep\(|Timer\.periodic\(|time\.NewTicker\(' -- ':!*test*' ':!*.md'`
- **Fix:** subscribe to the push channel (webhook, SSE, WebSocket, change stream, FCM/APNs); where polling is unavoidable, back off and poll at the minimum acceptable staleness.
- **Impact:** requests, battery and metered calls grow with clients × time instead of with events.
- **Source:** PostgreSQL `LISTEN`/`NOTIFY`; Stripe webhooks guide.
