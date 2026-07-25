# Performance Scopes (`--perf`)

Deep performance analysis beyond the tactical `performance` scope. Loaded only when `--perf` runs.

| Group | Checks |
|-------|--------|
| Bundle | Bundle size, tree-shaking, unused deps, dynamic imports |
| Startup | Cold start, critical rendering path, lazy init, deferred loading |
| Runtime | Memory leaks, event listener cleanup, layout thrashing, jank |
| Caching | HTTP cache headers, service worker, API response cache, memoization |
| Network | Request waterfall, redundant requests, payload size, compression, prefetching |
| Web Vitals | LCP, INP, CLS for web projects |
| Mobile | Widget rebuild optimization, const constructors, image sizing, list virtualization |
| Database | Query performance, N+1 detection, connection pooling, index usage |
| Cost | Paid API/LLM call efficiency, cloud egress/cross-region transfer, oversized infra defaults, storage/log lifecycle policies, polling-vs-webhook waste |
| Resource Economy | Payload size (API response, assets, HTML), compression ratio (gzip/brotli enabled), cache-hit rate (CDN, service worker, API cache), storage growth trend, data-saving patterns (lazy loading, image optimization, bundle splitting) |
| Scale Envelope (D1, advisory) | Does the project document a measured scale limit for its critical flows — "works up to N users / M records on X architecture" — backed by a cited synthetic-fixture method (see ds-test scale-envelope fixture pattern)? No documented envelope → advisory finding "no declared scale envelope — measure critical flows against a synthetic max-size fixture and document the limit" (never a blocker, SKILL-SPEC §15) |

**Scope boundary:** performance-specific deep dive. Produces optimization recommendations with estimated impact. Fixes only low-risk items (const constructors, unused imports, memoization); high-impact changes (architecture, caching strategy) → `needs_approval`.

**Measure before claiming.** Every reported optimization names the measurement that established the baseline and the same measurement re-run after. No measured improvement → revert rather than ship the claim.
