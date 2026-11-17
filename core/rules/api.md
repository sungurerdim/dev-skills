# API — contract, limits, server-side request safety

Loaded when the project serves an API (`api≠none`). Boundary validation is SEC-05, error bodies without internals SAR-06, object access AUTH-11, body size and timeouts NWK-06 and NWK-07, request logging with a request ID OBS-01.

### API-01 [HIGH] Verbs in REST resource paths
applies_when: api∋rest
- **Detect:** routes named for actions (`/getUsers`, `/createOrder`, `/deleteItem/5`) instead of resources with HTTP methods; singular and plural collection names mixed.
- **Mech:** T `git grep -nIE "['\"]/(api/)?(v[0-9]+/)?(get|create|update|delete|fetch|remove|add|list)[A-Z_-]" -- ':!*.md' ':!*test*'`
- **Fix:** plural nouns for collections, the method for the action (`GET /users`, `POST /orders`, `DELETE /items/5`); a non-CRUD action becomes a sub-resource or a custom method in one documented style.
- **Impact:** inconsistent paths confuse clients and defeat HTTP caching, tooling and method semantics.
- **Source:** Least astonishment; Google Cloud API Design Guide (resource-oriented design); RFC 9110 (method semantics).

### API-02 [HIGH] Error responses in several shapes
- **Detect:** different error bodies across endpoints (`{message}`, `{error}`, plain strings, HTML); a body status that disagrees with the HTTP status; validation errors without a pointer to the failing field.
- **Mech:** T `git grep -nIE 'problem\+json|ProblemDetail|HTTPException|res\.status\([45][0-9]{2}\)|status_code[[:space:]]*=[[:space:]]*[45][0-9]{2}|abort\([45][0-9]{2}' -- ':!*test*' ':!*.md'`
- **Fix:** one error handler emitting RFC 9457 `application/problem+json` (`type`, `title`, `status`, `detail`, `instance`, plus field errors) for every failure path; gRPC uses `google.rpc.Status`, GraphQL the `errors` array with `extensions.code`.
- **Impact:** clients and monitors cannot parse failures reliably, so errors are mishandled or missed.
- **Source:** Least astonishment; RFC 9457 (Problem Details for HTTP APIs).

### API-03 [HIGH] Public API changes break clients without a version
applies_when: api∋rest
- **Detect:** an API consumed outside the repo (mobile app in stores, third parties, other teams) with no versioning scheme, or several schemes mixed; breaking changes (removed field, changed type, new required field) shipped in place.
- **Mech:** M (API-08's diff output when a spec exists)
- **Fix:** one scheme (URI major version is the simplest); additive changes need no new version; a breaking change ships as a new major version while the old one stays served through an announced window (DEP-16).
- **Impact:** a deploy silently breaks clients that cannot update at once, such as installed mobile apps.
- **Source:** Semantic Versioning 2.0.0; Google Cloud API Design Guide (versioning); Stripe API versioning.

### DEP-16 [MEDIUM] API removal without Deprecation and Sunset headers
- **Detect:** a public endpoint slated for removal with no `Deprecation` header (RFC 9745) or `Sunset` header (RFC 8594), a Sunset date before the Deprecation date, or no published minimum notice before a breaking removal.
- **Mech:** T `git grep -nIiE 'deprecation|sunset' -- ':!*.md' ':!*test*'`
- **Fix:** send `Deprecation` and `Sunset` with a link to the migration guide; publish the notice window and keep version numbers honest.
- **Impact:** clients get no machine-readable warning and break on removal day.
- **Source:** RFC 9745; RFC 8594; Semantic Versioning 2.0.0.

### API-05 [HIGH] No rate limit, or a limiter that fails open
- **Detect:** public, login, signup, password reset, MFA and costly endpoints with no per-client limit; WebSocket upgrades or GraphQL operations outside the limiter; endpoints neither limited nor on an explicit exemption list; a limiter whose store error is caught and the request let through, with no decision recorded; no `429` with `Retry-After`; error messages that tell a wrong password from an unknown account (AUTH-21).
- **Mech:** T `git grep -nIiE 'rate.?limit|throttl|slowapi|express-rate-limit|rate-limiter-flexible|bucket4j|limiter' -- ':!*.md'`
- **Fix:** per-identity and per-IP limits (sliding window or token bucket) in front of handlers, tighter on auth endpoints with progressive delay; one budget shared by REST and WebSocket attempts; fail closed (`429`/`503`) on auth, payment and write paths when the store is down, fail open only on public reads with the choice written beside the config and an alert while degraded; a test asserts every route is limited or exempt-listed.
- **Impact:** credential stuffing, scraping and cost abuse run unthrottled, and a silent fail-open removes the limiter exactly during the incident it exists for.
- **Source:** Secure / private by default; OWASP API4:2023 Unrestricted Resource Consumption; OWASP Credential Stuffing Prevention Cheat Sheet; RFC 6585 (429).

### API-06 [MEDIUM] List endpoints unbounded or offset-paginated at scale
- **Detect:** list endpoints returning every row; a client-chosen `limit`/`page_size` with no server cap; offset pagination over large or actively written collections (deep pages scan skipped rows and shift under inserts).
- **Mech:** T `git grep -nIE '(limit|page_?size|per_?page|first).*(req\.|request\.|query|params)|OFFSET|\.offset\(|\.skip\(' -- ':!*test*' ':!*.md'`
- **Fix:** paginate every list with a server-side maximum page size; keyset (cursor) pagination on a stable unique ordering for large or live collections; offset only for small, static lists that need page jumps.
- **Impact:** one request for everything exhausts memory and the database; deep offsets get slower per page and return duplicates or gaps.
- **Source:** OWASP API4:2023; PostgreSQL docs, LIMIT and OFFSET (skipped rows are still computed).

### API-07 [MEDIUM] Retried writes create duplicates
- **Detect:** `POST` endpoints with side effects (payments, orders, messages, provisioning) and no idempotency key or natural unique constraint; clients that retry such calls; outbound payment-provider calls retried without the provider's idempotency key.
- **Mech:** T `git grep -nIiE 'idempotency.?key' -- ':!*.md'` · `git grep -nIE '\.(post|put|patch)\(' -- ':!*test*' ':!*.md'`
- **Fix:** accept an `Idempotency-Key` header, store it namespaced per caller with the response and a TTL, and replay the stored response; keep unique constraints and state checks as the real guard behind it; send the provider's `Idempotency-Key` on every outbound payment call that may be retried.
- **Impact:** a network retry charges a customer twice or creates duplicate records.
- **Source:** IETF draft "The Idempotency-Key HTTP Header Field" (httpapi WG); Stripe, Idempotent requests.

### API-08 [MEDIUM] No machine-readable API contract
applies_when: api∋rest or api∋graphql or api∋grpc
- **Detect:** an API consumed outside its own codebase with no OpenAPI document, GraphQL schema file or `.proto`; a spec not linted or not checked for breaking changes in the gate; a spec that disagrees with the routes.
- **Mech:** T `git ls-files | grep -qiE '(openapi|swagger)[^/]*\.(ya?ml|json)$|\.graphqls?$|\.proto$' || echo 'no OpenAPI, GraphQL schema or .proto tracked'`
- **Fix:** generate the contract from code or write it first; lint it (Spectral for OpenAPI, `buf lint` for protobuf) and diff it against the base for breaking changes (oasdiff, `buf breaking`) in the gate; a contract test checks the server against it.
- **Impact:** clients guess the contract, and breaking changes reach them unnoticed.
- **Source:** Semantic Versioning; OpenAPI Specification 3.1; Spectral (stoplight.io); oasdiff (github.com/oasdiff/oasdiff); Buf (buf.build).

### API-10 [HIGH] GraphQL queries unbounded
applies_when: api∋graphql
- **Detect:** no depth or cost limit; list fields without pagination; resolvers that query per parent (no DataLoader-style batching); introspection and field suggestions enabled on a public production endpoint; batched operations or aliases with no cap.
- **Mech:** T `git grep -nIiE 'depthLimit|depth_limit|QueryDepthLimiter|ComplexityLimit|createComplexityRule|introspection|DataLoader|maxAliases|batch' -- ':!*.md'`
- **Fix:** depth and cost limits, connection-style pagination, per-request batching, introspection off for public production clients, caps on aliases and batch size.
- **Impact:** one nested query costs the server more than a thousand ordinary requests.
- **Source:** OWASP GraphQL Cheat Sheet; OWASP API4:2023.

### API-11 [CRITICAL] Server fetches a caller-supplied URL
- **Detect:** server-side requests to a URL or host from input (webhook target, link preview, image or PDF proxy, import from URL, OAuth metadata) with no destination check; redirects followed without re-checking; schemes other than `https` allowed.
- **Mech:** T `git grep -nIE '(requests\.(get|post)|urlopen|fetch|axios(\.(get|post))?|http\.Get|HttpClient|WebClient|curl_init)\(.*(req\.|request\.|params|query|body|url)' -- ':!*test*' ':!*.md'`
- **Fix:** an allow-list of hosts where possible; otherwise resolve once, reject private, loopback, link-local and metadata addresses (`10/8`, `172.16/12`, `192.168/16`, `127/8`, `169.254/16`, `::1`, `fc00::/7`) and connect to the checked IP; `https` only; re-check every redirect hop; run fetchers without cloud credentials where possible.
- **Impact:** the server becomes a proxy into internal services and cloud metadata, leaking credentials.
- **Source:** OWASP A01:2025 (SSRF); OWASP SSRF Prevention Cheat Sheet; CWE-918.

### API-12 [HIGH] Request body bound onto a model wholesale
- **Detect:** a request body spread or bound onto a database model or entity without an allow-list of writable fields (`Model.update(req.body)`, `Model(**request.json)`, `Object.assign(entity, req.body)`, Rails `permit!`, unbound `@ModelAttribute`); response serializers that return every column. Client-asserted roles are SAR-07.
- **Mech:** T `git grep -nIE '\.(update|create|build|assign|merge|insert)\([[:space:]]*(req\.body|request\.(json|data|POST|form))|\*\*request\.(json|data|form)|Object\.assign\([^,]+,[[:space:]]*req\.body|permit!' -- ':!*test*' ':!*.md'`
- **Fix:** an explicit DTO or schema per endpoint listing writable fields; explicit response schemas that list readable fields.
- **Impact:** an attacker sets fields the UI never shows (`role`, `isAdmin`, `balance`) or reads ones it never displays.
- **Source:** Least privilege; OWASP API3:2023 Broken Object Property Level Authorization; CWE-915.

### API-16 [HIGH] Security middleware in the wrong order
- **Detect:** authorization registered before authentication; rate limiting after body parsing of large payloads or after the handler; headers or CORS applied only on success paths; routes registered before the auth middleware they rely on.
- **Mech:** T `git grep -nIE 'app\.use\(|router\.use\(|\.Use(Authentication|Authorization|Cors|RateLimiter)\(|add_middleware\(|MIDDLEWARE[[:space:]]*=|\.addFilter(Before|After)\(' -- ':!*.md'`
- **Fix:** CORS and headers → request ID and logging → size limit and parsing → authentication → rate limit by identity → authorization → handler → error handler.
- **Impact:** a control registered out of order checks an unverified identity or runs after the cost it should prevent.
- **Source:** OWASP REST Security Cheat Sheet; Express, Using middleware (order of execution).

### API-19 [HIGH] CORS allows any origin with credentials
applies_when: ui∋web or api≠none
- **Detect:** `Access-Control-Allow-Origin` reflecting the request `Origin` or `*` together with `Access-Control-Allow-Credentials: true`; origin checks by substring or suffix; `null` origin allowed.
- **Mech:** T `git grep -nIiE 'Access-Control-Allow-(Origin|Credentials)|cors\(|allow_origins|AllowAnyOrigin|allowedOrigins|origin[[:space:]]*:[[:space:]]*(true|\*)' -- ':!*.md'`
- **Fix:** an exact allow-list of origins for credentialed requests; no reflection of arbitrary origins.
- **Impact:** any website makes authenticated requests as the logged-in user and reads the responses.
- **Source:** Least privilege; OWASP API8:2023 Security Misconfiguration; OWASP HTML5 Security Cheat Sheet (CORS); CWE-942.

### API-20 [HIGH] Webhooks or third-party responses trusted unverified
applies_when: integrations≠none or api≠none
- **Detect:** incoming webhooks processed without verifying the provider's signature; the signature computed over re-serialized JSON instead of the raw body; signatures compared with `==` instead of a constant-time function; no timestamp tolerance or event-ID dedupe against replay; third-party API responses used in queries, paths or HTML without validation.
- **Mech:** T `git grep -nIiE 'webhook|x-hub-signature|stripe-signature|svix|constructEvent|hmac' -- ':!*.md'`
- **Fix:** verify with the provider SDK or HMAC over the raw body using `hmac.compare_digest` / `crypto.timingSafeEqual` / `hmac.Equal`; reject events outside a few minutes of tolerance; delivery is at-least-once, so record each processed event ID under a unique constraint in the same transaction as its state change and treat a redelivery (refunds included) as a no-op; answer 2xx fast and do slow work after; validate third-party payloads against a schema like user input.
- **Impact:** anyone who finds the endpoint forges payment or account events or replays a captured one, and a redelivered event credits or refunds twice.
- **Source:** OWASP API10:2023 Unsafe Consumption of APIs; CWE-208, CWE-345; Stripe, Check the webhook signatures and Handle duplicate events.
