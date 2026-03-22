# Rules: Network Security

Network-level compliance rules for API security, transport layer, and DoS prevention. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Transport Security** | NET-01–04 (2 BLOCKER, 2 CRITICAL) | ~12 |
| **API Protection** | NET-05–08 (1 BLOCKER, 2 CRITICAL, 1 MAJOR) | ~55 |
| **Resilience** | NET-09–12 (1 CRITICAL, 2 MAJOR, 1 MAJOR) | ~95 |

---

## Transport Security

### NET-01 [BLOCKER] TLS Minimum Version
Enforce TLS 1.2+ for all connections. TLS 1.0/1.1 are deprecated (RFC 8996).
- **Detect:** `ssl_version`, `TLSv1`, `TLSv1_1`, `PROTOCOL_TLSv1`, `MinVersion` set below TLS 1.2, `ssl.PROTOCOL_TLS` without explicit minimum
- **Fix:** Set minimum TLS 1.2. Go: `tls.Config{MinVersion: tls.VersionTLS12}`. Node: `secureOptions: crypto.constants.SSL_OP_NO_TLSv1 | SSL_OP_NO_TLSv1_1`. Python: `ssl.PROTOCOL_TLS_CLIENT` (defaults to 1.2+)
- **Source:** NIST SP 800-52r2, PCI DSS 4.0

### NET-02 [BLOCKER] Certificate Validation
Never disable SSL/TLS certificate verification in production code.
- **Detect:** `verify=False`, `NODE_TLS_REJECT_UNAUTHORIZED=0`, `InsecureSkipVerify: true`, `CURLOPT_SSL_VERIFYPEER => false`, `ssl_verify: false`
- **Fix:** Remove verification bypass. For development/testing, use environment-specific config, not code changes. For self-signed certs in staging, add CA to trust store
- **Source:** OWASP A07:2021 (Security Misconfiguration)

### NET-03 [CRITICAL] HSTS Header
HTTP Strict Transport Security prevents protocol downgrade attacks.
- **Detect:** Missing `Strict-Transport-Security` header on HTTPS responses. `max-age` below 31536000 (1 year). Missing `includeSubDomains`
- **Fix:** Add header: `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`. For new deployments, start with lower max-age and increase
- **Source:** RFC 6797, OWASP

### NET-04 [CRITICAL] Certificate Pinning (Mobile/Desktop)
Pin certificates or public keys for sensitive API connections in native apps.
- **Detect:** Mobile/desktop apps making HTTPS calls without certificate pinning. Missing `TrustManager` override (Android), missing `URLSessionDelegate` pinning (iOS), no `CertificatePinner` (OkHttp)
- **Fix:** Pin leaf or intermediate certificate public key hash. Implement backup pins for rotation. Flutter: `SecurityContext` with `setTrustedCertificatesBytes`. React Native: `ssl-pinning` or custom `TrustManager`
- **Source:** OWASP Mobile Top 10 M3

---

## API Protection

### NET-05 [BLOCKER] Rate Limiting
All public-facing endpoints must have rate limiting to prevent abuse and DoS.
- **Detect:** API endpoints without rate limiting middleware. Missing `X-RateLimit-*` response headers. No throttle/rate-limit configuration in API gateway, reverse proxy, or application code
- **Fix:** Add rate limiting: per-IP for anonymous, per-user for authenticated. Return `429 Too Many Requests` with `Retry-After` header. Express: `express-rate-limit`. Django: `django-ratelimit`. Go: `golang.org/x/time/rate`. Use sliding window algorithm for fairness
- **Source:** OWASP API4:2023 (Unrestricted Resource Consumption)

### NET-06 [CRITICAL] Request Size Limits
Enforce maximum request body size to prevent memory exhaustion.
- **Detect:** No body size limit configured. Missing `client_max_body_size` (nginx), `LimitRequestBody` (Apache), `bodyParser.json({limit})` (Express), `DATA_UPLOAD_MAX_MEMORY_SIZE` (Django)
- **Fix:** Set reasonable limits: API JSON: 1-10MB, file uploads: explicit per-endpoint limit with streaming. Express: `app.use(express.json({limit: '1mb'}))`. Nginx: `client_max_body_size 10m;`
- **Source:** OWASP API4:2023

### NET-07 [CRITICAL] Request Timeout Configuration
All external calls must have explicit timeouts to prevent resource exhaustion.
- **Detect:** HTTP clients without timeout: `requests.get()` without `timeout=`, `fetch()` without `AbortController`, `http.Client{}` without `Timeout`, database queries without statement timeout
- **Fix:** Set connect timeout (5-10s), read timeout (30s), write timeout (30s). For long operations, use async processing with progress callbacks. Python: `requests.get(url, timeout=(5, 30))`. Go: `&http.Client{Timeout: 30 * time.Second}`
- **Source:** NIST resilience guidelines

### NET-08 [MAJOR] API Versioning
APIs must have a versioning strategy to prevent breaking changes.
- **Detect:** API routes without version prefix (`/api/users` instead of `/api/v1/users`). No `Accept` header version negotiation. No sunset/deprecation headers on old versions
- **Fix:** URL path versioning (`/api/v1/`) or header versioning (`Accept: application/vnd.api+json;version=1`). Document deprecation timeline. Add `Sunset` header to deprecated versions
- **Source:** REST API design best practices

---

## Resilience

### NET-09 [CRITICAL] Connection Pool Limits
Database and HTTP connection pools must have bounded sizes and timeouts.
- **Detect:** Connection pools without `maxPoolSize`/`pool_size`/`MaxOpenConns`. Missing `idle_timeout`/`maxIdleTime`. Unbounded connection creation in loops
- **Fix:** Set pool size based on expected concurrency (typically 10-25 for DB, 100 for HTTP). Set idle timeout (30-60s). Set max lifetime (5-10min). Go: `db.SetMaxOpenConns(25); db.SetMaxIdleConns(5); db.SetConnMaxLifetime(5 * time.Minute)`
- **Source:** Database and HTTP client documentation

### NET-10 [MAJOR] Retry with Backoff
Retries on external service failures must use exponential backoff with jitter.
- **Detect:** Retry loops without delay (`while (!success) { retry(); }`). Fixed delay retries. Missing jitter. Unlimited retry count
- **Fix:** Exponential backoff: `delay = min(base * 2^attempt + random_jitter, max_delay)`. Max 3-5 retries. Circuit breaker for persistent failures. Python: `tenacity` library. Go: custom or `cenkalti/backoff`
- **Source:** AWS architecture best practices

### NET-11 [MAJOR] Circuit Breaker Pattern
Repeated failures to external services should trip a circuit breaker to prevent cascade failures.
- **Detect:** External service calls without circuit breaker. Repeated timeout/error handling that continues calling a failing service
- **Fix:** Implement circuit breaker with three states: closed (normal), open (failing, fast-fail), half-open (testing recovery). Track failure rate over sliding window. Go: `sony/gobreaker`. Node: `opossum`. Python: `pybreaker`
- **Source:** Michael Nygard, "Release It!"

### NET-12 [MAJOR] DNS Resolution Caching
Avoid DNS lookup on every request for frequently called services.
- **Detect:** HTTP clients creating new connections per request without connection reuse. DNS resolution on every API call in hot paths
- **Fix:** Use connection pooling (reuses existing connections, avoids DNS). For custom DNS: set TTL-based cache. Node: `http.Agent({keepAlive: true})`. Go: default `http.Client` reuses connections. Python: `requests.Session()` for connection reuse
- **Source:** Performance and reliability best practices
