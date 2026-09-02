# Rules: Deployment & Containerization

| Section | Rules |
|---------|-------|
| **Container Security** | DEP-01 to DEP-05, DEP-17 (2 CRITICAL, 4 HIGH) |
| **Deployment Patterns** | DEP-06 to DEP-13 (2 HIGH, 4 MEDIUM, 2 LOW) |
| **Release Engineering** | DEP-14 to DEP-16 (1 HIGH, 2 MEDIUM) |
| **Deployment Verification** | DEP-18 to DEP-19 (2 HIGH) |
| **Configuration** | DEP-20 to DEP-21 (1 CRITICAL, 1 HIGH) |
| **Architecture & Topology** | DEP-22 (1 HIGH) |
| **DNS & TLS** | DEP-23 to DEP-25 (3 HIGH) |

## Container Security

### DEP-01 | CRITICAL | No Secrets in Image

**Detect:** `COPY` of `.env` files, `ARG` with secret values, hardcoded credentials in Dockerfile layers.

**Fix:** Use `--mount=type=secret` at build time, environment variables or `env_file` at runtime, or an external secret manager (Vault, AWS SSM, Doppler).

```dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
```

**Impact:** Secrets in images persist in every layer and every registry. Single leaked image exposes all credentials.

**Source:** Docker security best practices, OWASP Docker Security Cheat Sheet

---

### DEP-02 | CRITICAL | SSL/TLS Termination

**Detect:** Application serving HTTP directly on a public port without a TLS-terminating reverse proxy.

**Fix:** Place Caddy (auto-HTTPS, zero config) or Nginx + Certbot as a reverse proxy.

```
# Caddy: automatic HTTPS
app.example.com { reverse_proxy localhost:3000 }
```

**Impact:** Unencrypted traffic exposes credentials, session tokens, and user data. Modern browsers flag HTTP as insecure.

**Source:** Let's Encrypt, Caddy docs, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md)

---

### DEP-03 | HIGH | Multi-Stage Build

**Detect:** Single-stage Dockerfile with build tools (compilers, dev dependencies, source code) present in final image.

**Fix:** Use multi-stage builds: `FROM builder` stage compiles, `FROM runtime` stage copies only production artifacts.

```dockerfile
FROM node:22-alpine AS builder       # Go: golang:1.23-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build                     # Go: CGO_ENABLED=0 go build -o server .

FROM node:22-alpine AS runtime        # Go: gcr.io/distroless/static-debian12
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
```

**Impact:** Reduces image size 60-90%, shrinks attack surface by excluding build tools, speeds up pulls and deploys.

**Source:** Docker multi-stage build docs, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md)

---

### DEP-04 | HIGH | Health Check Endpoint

**Detect:** No `HEALTHCHECK` instruction in Dockerfile, no `/health` or `/healthz` endpoint in application.

**Fix:** Add `/health` returning 200 with dependency checks (DB, cache), 503 when degraded. Add `HEALTHCHECK` in Dockerfile.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
```

**Impact:** Without health checks, orchestrators route traffic to unhealthy containers. Health-gated deploys prevent bad releases from reaching users.

**Source:** Kubernetes probe patterns, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md) (Monitoring section)

---

### DEP-05 | HIGH | Non-Root Container User

**Detect:** Dockerfile has no `USER` directive (defaults to root).

**Fix:** `RUN addgroup -S app && adduser -S app -G app` then `USER app` before `CMD`.

**Impact:** Compromised root container gives attackers root-level filesystem access and potential host escape via privilege escalation.

**Source:** CIS Docker Benchmark, Docker security best practices

### DEP-17 | HIGH | Container Hardening Baseline (canonical)

**Detect:** Production image FROM a full OS base (`ubuntu:*`, `debian:*` non-slim) instead of distroless/minimal; runtime specs (K8s/compose) missing `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, or capability drop; base images referenced by mutable tag (`:latest`, bare `:20`) instead of digest.

**Fix:** Distroless or minimal base (scanner-reported CVE counts routinely drop 80–95% vs full-OS bases; pair with DEP-03 multi-stage). `readOnlyRootFilesystem: true` with explicit writable mounts (`emptyDir`/tmpfs) where needed. Drop all capabilities, add back only the required minimum. Pin base images by digest (`@sha256:…`). Non-root user is DEP-05.

**Impact:** Writable filesystem + full OS toolchain + broad capabilities turn any RCE into a fully-equipped attack platform; a mutable base tag lets the image change under you.

**Note:** Canonical home for production-container hardening — the CI-side counterpart (images the pipeline builds/runs) is ds-devops DOP-22, which defers here for production images.

**Source:** Google distroless docs, Kubernetes Pod Security Standards (restricted profile), CIS Docker Benchmark

## Deployment Patterns

### DEP-06 | HIGH | Comprehensive .dockerignore

**Detect:** Missing `.dockerignore`, or it fails to exclude `.git`, `node_modules`, `.env*`, test files, IDE configs.

**Fix:** Create `.dockerignore`: `.git`, `node_modules`, `*.md`, `.env*`, `.vscode`, `coverage`, `tests`, `__pycache__`, `.idea`, `dist`, `build`.

**Impact:** Without `.dockerignore`, build context includes everything (`.git` alone can be hundreds of MB). Reduces build time, image size, and secret leakage risk.

**Source:** Docker build context optimization, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md)

---

### DEP-07 | MEDIUM | Zero-Downtime Deployment

**Detect:** Deploying causes brief 502/503 errors because old container stops before new one is ready.

**Fix:** Use rolling updates (health check gates traffic), blue-green (two compose files, switch proxy after health check), or canary (route percentage to new version). Blue-green = instant rollback; rolling = simplest; canary = safest for large changes.

**Impact:** Users experience errors during deployment without graceful transitions. Health-gated rollouts ensure only verified containers receive traffic.

**Source:** Kubernetes rolling update strategy, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md) (Zero-Downtime section)

---

### DEP-08 | MEDIUM | Resource Limits

**Detect:** No `memory` or `cpus` limits in Docker Compose, Kubernetes manifests, or container run commands.

**Fix:** Set `deploy.resources.limits` in compose (`memory: 512M`, `cpus: "1.0"`) or equivalent in Kubernetes.

**Impact:** Single runaway process without limits can consume all host resources and crash co-located services.

**Source:** Kubernetes resource management, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md) (Docker Compose section)

---

### DEP-09 | LOW | Dockerfile Layer Optimization

**Detect:** `COPY . .` appears before dependency installation, busting cache on every code change.

**Fix:** Copy dependency manifests first, install, then copy application code:

```dockerfile
COPY package.json package-lock.json ./   # or requirements.txt, go.mod
RUN npm ci                                # install deps (cached layer)
COPY . .                                  # source code (changes frequently)
```

**Impact:** Proper layer ordering means dependency installation is cached across builds. Rebuilds drop from minutes to seconds when only source code changes.

**Source:** Docker layer caching best practices

---

### DEP-10 | LOW | Docker Compose for Development

**Detect:** No `docker-compose.yml` for local development, or local setup diverges significantly from production.

**Fix:** Provide `docker-compose.yml` mirroring production: same services, named volumes, networks, env files. New contributors run `docker compose up` for full stack.

**Impact:** Dev/prod parity catches environment-specific bugs early. New contributors can run full stack with single command.

**Source:** Docker Compose docs, [deployment-patterns.md](https://github.com/sungurerdim/dev-skills/blob/main/docs/infrastructure/deployment-patterns.md) (Docker Compose for Production)

### DEP-11 | HIGH | Insecure Production Defaults

**Detect:** Permissive or debug-friendly configuration shipped to production:
- `Access-Control-Allow-Origin: *` together with credentials
- IAM `"Action": "*"` or a security group open to `0.0.0.0/0`
- `verify=False` / `rejectUnauthorized: false` / disabled certificate checks
- Missing security headers (CSP, HSTS, `X-Content-Type-Options`, `X-Frame-Options`)
- `DEBUG=true` or stack traces returned in responses

Veracode 2026 found ~45% of AI-generated samples carried a known weakness; Tenzai 2026 found 0 of 15 AI-built apps set basic security headers.

**Fix:** Least-privilege IAM with specific resource ARNs + restricted CIDR; explicit CORS origin allowlist (never `*` with credentials); keep TLS verification on; set security headers on every response; debug off, with structured errors that don't leak internals.

**Impact:** Any one of these defaults is independently exploitable in production — an open CORS+credentials combination or a wildcard IAM action turns a single compromised endpoint into full account or cross-origin data access.

**Source:** [Veracode GenAI 2026](https://www.veracode.com/blog/genai-security-and-vibe-coding/), [Tenzai 2026](https://blog.tenzai.com/bad-vibes-comparing-the-secure-coding-capabilities-of-popular-coding-agents/)

---

### DEP-12 | MEDIUM | Backing Services as Attached Resources (12-Factor #4)

**Detect:** Database/cache/queue/mail connection hardwired to a specific host/instance in code or config (e.g., a literal hostname or local socket path) instead of a URL-style env var (`DATABASE_URL`, `REDIS_URL`, `SMTP_URL`).

**Fix:** Attach every backing service via a URL-style config value read from the environment; swapping a local Postgres for a managed instance requires an env-var change only, no code change.

**Impact:** Hardwired backing services block environment promotion (dev → staging → prod) and make disaster recovery (swap to a standby) a code change instead of a config change.

**Source:** *The Twelve-Factor App* — Factor IV: Backing Services (https://12factor.net/backing-services)

---

### DEP-13 | MEDIUM | Concurrency via Process Model (12-Factor #8)

**Detect:** Scaling plan relies on a single larger process/instance (vertical scaling) rather than running more stateless replicas; no `replicas`/`scale` config in compose, Kubernetes, or PaaS manifest.

**Fix:** Design the process stateless so it can run as N identical replicas behind a load balancer or orchestrator; set an explicit replica/scale count in the deployment manifest.

**Impact:** Vertical-only scaling has a hard ceiling and a single point of failure; horizontal scale-out via the process model is what makes zero-downtime deploys and elastic capacity possible.

**Source:** *The Twelve-Factor App* — Factor VIII: Concurrency (https://12factor.net/concurrency)

---

## Release Engineering

### DEP-14 | HIGH | Canary With Automated Rollback Thresholds

**Detect:** Canary/staged rollout exists but rollback is a manual watch-and-decide process — no metric-bound automated trigger; or big-bang 100% deploys on a service with meaningful traffic.

**Fix:** Stage traffic in weighted steps (e.g. 1 → 5 → 10 → 25 → 50 → 100%) with automated metric checks at each stage; roll back automatically when error-rate or p99-latency thresholds are breached (Flagger, Argo Rollouts, or platform equivalent). DEP-07 covers the zero-downtime mechanics; this rule covers the automated decision.

**Impact:** A human watching dashboards is the slowest, least reliable rollback trigger — the incident is already user-visible before the decision is made.

**Source:** Flagger/Argo Rollouts progressive-delivery docs; SRE Workbook canarying chapter

### DEP-15 | MEDIUM | Feature-Flag Lifecycle Governance

**Detect:** Flag definitions with no owner, purpose, or planned removal date; flags older than their intended lifetime still active; an old flag key reused for a new purpose.

**Fix:** Require owner + purpose + expiry metadata at flag creation; sweep stale flags on a recurring cadence; ban flag-key reuse. (Code-level dead-branch/stale-flag detection lives in ds-simplify — this rule covers the release-process governance.)

**Impact:** Every stale flag is an untested code path and a config surface that can be flipped in production; reused keys inherit stale targeting rules.

**Source:** LaunchDarkly/CloudBees flag-lifecycle guidance

### DEP-16 | MEDIUM | API Deprecation Signaling (Sunset / Deprecation Headers)

**Detect:** Public API endpoint slated for removal without machine-readable signaling: no `Deprecation` header (RFC 9745) and/or no `Sunset` header (RFC 8594); Sunset date earlier than Deprecation date; package/API without a published SemVer + minimum-deprecation-window policy.

**Fix:** Add `Deprecation` (deprecation effective date) and `Sunset` (date the endpoint stops responding) headers with a published migration deadline — per RFC 8594 the Sunset timestamp MUST NOT be earlier than the Deprecation timestamp. Publish a deprecation-window policy (minimum notice before breaking removal) and keep version bumps SemVer-honest.

**Impact:** Consumers can automate migration warnings only when deprecation is machine-readable; silent removals break integrations without recourse.

**Source:** RFC 8594 (Sunset header); RFC 9745 (Deprecation header); semver.org

## Deployment Verification

### DEP-18 | HIGH | Static-Host Deploys Verified via the Host's Build API, SHA-Matched

Push may start the deploy, but success is never assumed: the host's build-status API is polled until the reported commit SHA equals the pushed HEAD and the status is built.

**Detect:** Release scripts that treat a successful push as a successful deploy; no poll of the host's builds/latest endpoint; "deployed" markers (tags) advanced before host confirmation; polls that wait forever.

**Fix:** After push, poll the host's build API with a timeout: require status=built AND returned commit hash == pushed HEAD before advancing the deployed marker (git tag); on failure or timeout, fail immediately and loudly — no infinite wait, no optimistic tagging.

**Impact:** An unverified "deploy" that actually failed leaves production on the old build while every marker says otherwise — the worst debugging scenario: correct-looking state, wrong reality.

**Source:** XR-088 — cross-project experience registry (2026).

### DEP-19 | HIGH | Single-Node Restarts Follow the Safe Sequence

Where true rolling update is impossible (one node), restarts follow: build → drain → queue-empty → backup → dependency-ordered stop/start → undrain → live-verify.

**Detect:** Single-node restart scripts that stop services with jobs in flight, skip pre-restart backup of persistent data, stop/start in arbitrary order, or verify nothing after start.

**Fix:** Sequence: build new images first → set a TTL'd drain flag blocking new work → wait for queues to empty → back up persistent data → stop in dependency order (writers first, infrastructure last), start in reverse → clear the drain flag → verify live via the health endpoint's git_sha matching the deployed build. The drain flag's TTL self-clears if the operator forgets it.

**Impact:** An unordered single-node restart truncates in-flight jobs and races services against their dependencies — turning a 30-second restart into data repair; the TTL'd flag prevents the classic "forgot to undrain" total outage.

**Source:** XR-179 — cross-project experience registry (2026).

## Configuration

### DEP-20 | CRITICAL | Fail Fast on Missing or Placeholder Critical Config

Security/compliance/finance-critical configuration has no code-level defaults; missing, placeholder, or wrong-environment values abort startup loudly.

**Detect:** Code defaults for salts, mock/debug flags, connection params, TTLs, pricing, rate limits, API endpoints, OAuth client IDs; prod boots pointing at localhost; `.env.example` placeholder secrets accepted because they pass length checks; validation only at runtime OR only at build, not both.

**Fix:** Validate all critical config at startup and fail immediately and loudly on missing or invalid values; explicitly reject known placeholder values from `.env.example` even when they satisfy format/length checks — booting with a public example salt makes every derived identity guessable. Ideal: two independent catch points, runtime fail-fast AND a release-build check.

**Impact:** A service silently running on placeholder or wrong-environment config is a breach (public salt), a finance bug (default pricing), or a data leak (wrong endpoint) wearing a green health check.

**Source:** XR-081 — cross-project experience registry (2026).

### DEP-21 | HIGH | Dev-Override Config Cannot Leak Into Production

Auto-merged development override files (docker-compose.override.yml, .env.local, dev webpack config) are neutralized on production hosts by explicit production-file invocation, not by hoping the file is absent.

**Detect:** Production operational commands relying on default file resolution (bare `docker-compose up`) on hosts where an override file could exist; override files carrying relaxed security flags (ENVIRONMENT=development disabling fail-fast checks).

**Fix:** Every production operational command names its files explicitly (e.g. `-f docker-compose.yml -f docker-compose.prod.yml`) so presence of a dev override changes nothing; document and enforce this invocation convention rather than deleting/hiding the override file.

**Impact:** One auto-merged dev override on a prod host silently disables the exact fail-fast checks that guard production — the config equivalent of leaving the alarm system in test mode.

**Source:** XR-082 — cross-project experience registry (2026).

## Architecture & Topology

### DEP-22 | HIGH | Account-Boundary Invariant: Customer-Owned and Product-Owned Infrastructure Never Mix

Customer-owned server-side functions run only in the customer's own provider account; the product's central functions run only in the product's own account. The boundary is a named, documented red line — mechanically gated where possible.

**Detect:** A customer-owned function (integration runtime, worker, script) deployed into the product vendor's account; product-central services (licensing, OAuth broker, OTA, support) holding a customer's business data or credentials; deploy tooling that can target either account from one undifferentiated config.

**Fix:** Enforce both directions: customer-owned runtimes deploy only to the customer's account; product-central functions never store customer business data/credentials. Name the invariant in the architecture docs as a permanent red line, and guard it mechanically where the tooling allows (per-target deploy configs that cannot cross, account-ID assertions in deploy scripts).

**Impact:** Crossing this boundary converts an isolated single-tenant incident into a platform-wide breach — and contractually converts the vendor into a data processor for data it was never supposed to hold.

**Source:** XR-197 — cross-project experience registry (2026).

## DNS & TLS

### DEP-23 | HIGH | DNS Records Complete and Correct

Production domains resolve correctly and are protected against unauthorized certificate issuance.

**Detect:** Missing or stale A/AAAA records for the apex/subdomains actually in use; a CNAME at the zone apex (invalid per RFC 1912 — an apex needs an ALIAS/ANAME or the registrar's flattening equivalent); no CAA record restricting certificate issuance to the CA actually used; DNSSEC offered by the registrar/DNS host and left unsigned.

**Fix:** `nslookup -type=A {domain}` / `nslookup -type=AAAA {domain}` / `nslookup -type=CNAME {subdomain}` against the intended targets (`dig +short A/AAAA/CNAME {domain}` where `dig` is installed); add a CAA record naming the issuing CA (`nslookup -type=CAA {domain}` or `dig +short CAA {domain}`, e.g. `0 issue "letsencrypt.org"`); enable DNSSEC signing where the registrar and DNS host both support it.

**Impact:** A wrong or missing DNS record is silent downtime that looks like a code bug; a missing CAA record lets any public CA issue a certificate for the domain without the owner's knowledge.

**Source:** RFC 1912 (Common DNS Operational and Configuration Errors), RFC 6844 (CAA)

### DEP-24 | HIGH | TLS Certificate Automation, Renewal and Expiry Alerting

Certificates renew unattended, well before expiry, with a failure alert if renewal itself fails.

**Detect:** Manual/one-off certificate issuance with no renewal automation (no certbot timer/systemd unit, no Caddy/ACME auto-renewal, no platform-managed certificate); no monitoring of certificate expiry date; a renewal job exists but its failure is not wired to any alert channel.

**Fix:** Automate issuance + renewal (Caddy's built-in ACME, `certbot renew` via systemd timer or cron with `--deploy-hook` to reload the proxy, or the platform's managed-certificate feature); add an expiry check to the monitoring scope (`echo | openssl s_client -servername {domain} -connect {domain}:443 2>/dev/null | openssl x509 -noout -enddate`, alert at 14 days remaining); the renewal job's exit code feeds the same alerting channel as other cron failures.

**Impact:** An expired certificate is a hard outage — every client refuses the connection — and unlike most outages it is entirely predictable days in advance, so hitting it is always an alerting gap, never a surprise.

**Source:** Let's Encrypt integration guide, Caddy automatic HTTPS documentation

### DEP-25 | HIGH | HSTS Enabled With a Safe Preload Path

`Strict-Transport-Security` served on every HTTPS response, with `max-age` raised gradually before `preload` is submitted.

**Detect:** No `Strict-Transport-Security` header on the production response; `max-age` below 300 (effectively disabled); `includeSubDomains` or `preload` set before every subdomain is confirmed HTTPS-only.

**Fix:** Set `Strict-Transport-Security: max-age=63072000; includeSubDomains` once every subdomain is verified HTTPS-only; add `preload` and submit to hstspreload.org only after that has held with no HTTP fallback need. New domains start at a short `max-age` (e.g. 300) and raise it once HTTPS is confirmed stable.

**Impact:** Missing HSTS leaves every first visit vulnerable to SSL-stripping; a `preload` submission made too early is effectively irreversible for months (browser-list removal is slow), locking out any subdomain that still needs plain HTTP.

**Source:** MDN Strict-Transport-Security, hstspreload.org submission requirements
