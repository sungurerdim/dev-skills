# Rules: Deployment & Containerization

| Section | Rules |
|---------|-------|
| **Container Security** | DEP-01 to DEP-05, DEP-17 (2 CRITICAL, 4 HIGH) |
| **Deployment Patterns** | DEP-06 to DEP-13 (2 HIGH, 4 MEDIUM, 2 LOW) |
| **Release Engineering** | DEP-14 to DEP-16 (1 HIGH, 2 MEDIUM) |
| **Deployment Verification** | DEP-18 to DEP-19 (2 HIGH) |
| **Configuration** | DEP-20 to DEP-21 (1 CRITICAL, 1 HIGH) |
| **Architecture & Topology** | DEP-22 (1 HIGH) |
| **DNS & TLS** | DEP-23 to DEP-25, DEP-35 (4 HIGH) |
| **Image & Container Runtime Safety** | DEP-26 to DEP-28 (2 HIGH, 1 MEDIUM) |
| **Edge & Infrastructure Hardening** | DEP-29 to DEP-31, DEP-34, DEP-36 (4 HIGH, 1 MEDIUM) |
| **Incident & Rollback Runbooks** | DEP-32 to DEP-33, DEP-37 (3 MEDIUM) |

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

**Source:** Let's Encrypt docs (https://letsencrypt.org/docs/), Caddy automatic HTTPS docs (https://caddyserver.com/docs/automatic-https)

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

**Source:** Docker multi-stage build docs (https://docs.docker.com/build/building/multi-stage/)

---

### DEP-04 | HIGH | Health Check Endpoint

**Detect:** No `HEALTHCHECK` instruction in Dockerfile, no `/health` or `/healthz` endpoint in application.

**Fix:** Add `/health` returning 200 with dependency checks (DB, cache), 503 when degraded. Add `HEALTHCHECK` in Dockerfile.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
```

**Impact:** Without health checks, orchestrators route traffic to unhealthy containers. Health-gated deploys prevent bad releases from reaching users.

**Source:** Kubernetes probe patterns (https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

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

**Source:** Docker build context optimization (https://docs.docker.com/build/building/context/)

---

### DEP-07 | MEDIUM | Zero-Downtime Deployment

**Detect:** Deploying causes brief 502/503 errors because old container stops before new one is ready.

**Fix:** Use rolling updates (health check gates traffic), blue-green (two compose files, switch proxy after health check), or canary (route percentage to new version). Blue-green = instant rollback; rolling = simplest; canary = safest for large changes.

**Impact:** Users experience errors during deployment without graceful transitions. Health-gated rollouts ensure only verified containers receive traffic.

**Source:** Kubernetes rolling update strategy (https://kubernetes.io/docs/tutorials/kubernetes-basics/update/update-intro/)

---

### DEP-08 | MEDIUM | Resource Limits

**Detect:** No `memory` or `cpus` limits in Docker Compose, Kubernetes manifests, or container run commands.

**Fix:** Set `deploy.resources.limits` in compose (`memory: 512M`, `cpus: "1.0"`) or equivalent in Kubernetes.

**Impact:** Single runaway process without limits can consume all host resources and crash co-located services.

**Source:** Kubernetes resource management (https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

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

**Source:** Docker Compose docs (https://docs.docker.com/compose/how-tos/production/)

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

---

### DEP-35 | HIGH | Reverse-Proxy TLS Protocol & Session Hardening

**Detect:** Nginx/Apache/HAProxy config permitting `TLSv1`/`TLSv1.1` alongside 1.2+ (`ssl_protocols` without an explicit floor of TLSv1.2); default/weak cipher suite (no `ssl_ciphers` override, RC4/3DES/export ciphers not excluded); TLS session tickets left at server defaults with no key-rotation plan (undermines forward secrecy); OCSP stapling not enabled (`ssl_stapling on` absent) despite the CA supporting it.

**Fix:** Pin `ssl_protocols TLSv1.2 TLSv1.3;` (drop 1.0/1.1); set a modern cipher suite (Mozilla SSL Configuration Generator "Intermediate" profile for broad compatibility, "Modern" for TLS 1.3-only clients); enable `ssl_stapling on; ssl_stapling_verify on;`; either rotate session-ticket keys on a schedule or disable session tickets in favor of session-ID caching where ticket-key rotation isn't automated. Caddy applies equivalent hardening automatically — this rule targets hand-configured Nginx/Apache/HAProxy.

**Impact:** A permitted legacy protocol or export-grade cipher is a downgrade-attack surface (BEAST/POODLE-class) even when TLS 1.3 is also offered — the weakest permitted option is what an active attacker negotiates; unrotated session-ticket keys quietly defeat the forward secrecy the rest of the config assumes.

**Source:** Mozilla SSL Configuration Generator (https://ssl-config.mozilla.org/)

## Image & Container Runtime Safety

### DEP-26 | HIGH | Image Vulnerability Scan Gate in Build Pipeline

**Detect:** Build/deploy pipeline has no CVE scan step for the built image (no Trivy, Docker Scout, Grype, or registry-native scan invoked before push/deploy).

**Fix:** Add an image scan step (`trivy image {image}` or `docker scout cves {image}`) to the build pipeline, failing the build on CRITICAL/HIGH CVEs with no available fix; re-run on a schedule for already-deployed images since new CVEs land after build time.

**Impact:** An unscanned image ships whatever vulnerabilities its base layers carry on build day, and stays blind to newly-disclosed CVEs in already-deployed images.

**Source:** Trivy documentation (https://trivy.dev/), Docker Scout documentation (https://docs.docker.com/scout/)

---

### DEP-27 | HIGH | Service Ports Bound to Loopback, Not Publicly Exposed

**Detect:** Docker Compose (or equivalent) service publishes a port as `"{port}:{port}"` instead of `"127.0.0.1:{port}:{port}"` for a service meant to sit behind a reverse proxy; a database/cache port published on any host-facing interface at all.

**Fix:** Bind application ports the reverse proxy fronts to `127.0.0.1` (or the orchestrator's internal network only); never publish database/cache ports — reach them over the internal Docker/Compose network exclusively.

**Impact:** A port published on all interfaces is reachable from the public internet the moment the host's firewall allows it — this is how an unauthenticated database ends up indexed by internet scanners within hours of deploy.

**Source:** OWASP Docker Security Cheat Sheet (https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

---

### DEP-28 | MEDIUM | Container Restart Policy Configured

**Detect:** Docker Compose service (or equivalent) with no `restart:` policy set (defaults to `no` — the container stays down after any crash or host reboot).

**Fix:** Set `restart: unless-stopped` (or the orchestrator's equivalent) on every long-running service.

**Impact:** Without a restart policy, one crash or host reboot takes the service down until a human notices and manually restarts it — turning a transient fault into an extended outage.

**Source:** Docker documentation — start containers automatically (https://docs.docker.com/engine/containers/start-containers-automatically/)

## Edge & Infrastructure Hardening

### DEP-29 | HIGH | CDN/Edge Security Configuration

**Detect:** Domain proxied through a CDN/edge network (Cloudflare or equivalent) with SSL/TLS mode left at "Flexible" (edge-to-origin traffic unencrypted) instead of "Full (Strict)"; minimum TLS version not pinned at the edge; no page rule/WAF rule blocking direct requests to sensitive paths (`/.env*`, `/.git/*`).

**Fix:** Set the edge SSL/TLS mode to Full (Strict) with a valid origin certificate; pin minimum TLS to 1.2+; add a page rule or WAF rule blocking `.env*` and `.git/*` paths.

**Impact:** "Flexible" SSL mode leaves the edge-to-origin hop in plaintext even though the browser-to-edge hop shows a padlock — an attacker on the origin's network path reads everything the padlock implied was protected.

**Source:** Cloudflare SSL/TLS encryption modes documentation (https://developers.cloudflare.com/ssl/origin-configuration/ssl-modes/)

---

### DEP-30 | HIGH | VPS Hardening Baseline (10-Point)

**Detect:** `deploy=vps` project missing one or more of: automated security updates, SSH key-only auth with root login disabled, a default-deny firewall with only required ports open, fail2ban (or equivalent) on the SSH port, kernel network-hardening sysctls, mandatory access control (AppArmor/SELinux), audit logging (auditd), a scheduled security scan.

**Fix:** `PermitRootLogin no` + `PasswordAuthentication no` + `MaxAuthTries 3` in `sshd_config`; default-deny firewall (UFW/nftables) allowing only SSH + HTTP/HTTPS; install and enable fail2ban on the SSH jail; enable unattended/automatic security upgrades; apply baseline sysctl hardening (disable IP forwarding unless routing, enable SYN cookies); enable AppArmor/SELinux enforcing mode; install auditd; run a periodic security scan (e.g. Lynis) and track the score.

**Impact:** Any single missing layer (password SSH auth, no firewall, no fail2ban) is independently how automated internet-wide scanners find and compromise a fresh VPS within hours of first boot — the ten points are cheap and each closes a distinct, commonly-exploited path.

**Source:** OpenSSH `sshd_config` manual (https://man.openbsd.org/sshd_config), Ubuntu community — automatic security updates (https://help.ubuntu.com/community/AutomaticSecurityUpdates), CIS Benchmarks (industry-standard hardening baselines — consult the Linux benchmark for the distribution in use)

---

### DEP-34 | MEDIUM | Disable Unused System Services (VPS)

**Detect:** `systemctl list-units --type=service --state=running` (or distro equivalent) on a production VPS returns enabled services with no role in the deployed stack (e.g. `avahi-daemon`, `cups`, `bluetooth`, a default MTA nobody configured) — installed by the base image, never audited.

**Fix:** Enumerate running services (`systemctl list-units --type=service`), map each to a required role, `systemctl disable --now {service}` anything unmapped; re-run after every base-image or distro upgrade since upgrades can re-enable defaults.

**Impact:** Every enabled-but-unused service is a listening process or attack surface nobody is watching — the VPS-hardening baseline (DEP-30) closes the network/auth paths; this closes the one it shares with every other freshly-imaged VPS: default services nobody asked for.

**Source:** VPS Hardening 25-Point Checklist (https://retzor.com/blog/vps-security-hardening-25-point-checklist-for-2025/)

---

### DEP-31 | HIGH | Backup Integrity Verification & 3-2-1 Redundancy

**Detect:** Backup script with no post-write integrity check (does not verify the archive is non-empty/valid before considering the backup successful); only one copy of backup data, or all copies on the same physical medium/host as the source; no offsite copy.

**Fix:** After every backup write, verify the artifact is non-empty and (where feasible) restorable — e.g. `[ -s "{backup-file}" ] || { echo "ERROR: empty backup"; exit 1; }`; maintain the 3-2-1 pattern — 3 copies, on 2 different media, with 1 stored offsite (e.g. local disk + S3-compatible offsite target via restic/rclone).

**Impact:** A backup job that "succeeds" while writing a zero-byte or truncated file is silent until the moment it is needed for a real restore — which is the single worst time to discover a backup was never valid; a single-copy or single-location backup shares every failure mode (disk death, ransomware, host loss) with the data it is meant to protect.

**Source:** CISA — #StopRansomware Guide, data backup guidance (https://www.cisa.gov/stopransomware/ransomware-guide)

---

### DEP-36 | HIGH | Backup Encryption & Retention Rotation

**Detect:** Database/file backups written unencrypted (plain `pg_dump`/`tar` output with no encryption step) especially before an offsite copy; no retention/rotation policy — backup directory grows unbounded, or old backups are deleted with no `--keep-*` schedule (e.g. a bare `rm` cron with no daily/weekly/monthly tiering).

**Fix:** Encrypt backups at rest and in transit to the offsite target (restic and borg encrypt by default; for plain `pg_dump`, pipe through `gpg`/`age` before writing); apply a tiered retention policy instead of unbounded growth or single-tier deletion (restic: `restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune`); verify the encryption key/passphrase itself is stored in the secrets manager (DEP-01), never alongside the backup.

**Impact:** An unencrypted offsite backup turns a single storage-provider compromise into a full data breach independent of the primary system's own security; unbounded or ad-hoc-deleted backups either exhaust storage or silently lose the recovery points a real incident needs.

**Source:** restic documentation — encryption and retention policies (https://restic.readthedocs.io/en/stable/)

## Incident & Rollback Runbooks

### DEP-32 | MEDIUM | Incident Triage Runbook — First 5 Minutes

**Detect:** No documented, ordered triage sequence for the first minutes of a detected incident — responders improvise the check order each time.

**Fix:** Document and follow a fixed first-5-minutes sequence: (1) confirm the issue is real, not a false positive; (2) confirm the app process is running; (3) check recent error logs; (4) confirm the database/critical dependency is reachable; (5) check host resource health (memory, disk, load); (6) classify severity P1 (down) / P2 (degraded) / P3 (minor) and route accordingly.

**Impact:** An improvised triage order under incident pressure wastes the minutes that matter most and produces inconsistent severity classification between responders — a fixed sequence turns triage into a checklist instead of a judgment call made under stress.

**Source:** Google SRE Workbook — Incident Response (https://sre.google/workbook/incident-response/)

---

### DEP-33 | MEDIUM | Rollback Playbook — Scenario-to-Command Mapping

**Detect:** No documented mapping from incident scenario to the specific rollback command/procedure and its expected downtime — the rollback path is decided ad hoc during the incident.

**Fix:** Maintain a scenario table mapping each common failure to its rollback action and expected downtime, e.g.: bad deploy with no DB change → image rollback (`docker compose up -d` on the previous tag; Kubernetes: `kubectl rollout undo`), <1 min; bad deploy with a DB migration → restore backup + image rollback, 5-30 min; infrastructure failure → redeploy from compose/IaC, 5-15 min; corrupted data → point-in-time DB restore, 15-60 min; suspected security breach → full redeploy on a new host, 1-4 hours.

**Impact:** Deciding the rollback mechanism for the first time during a live incident costs the minutes a pre-agreed playbook would have saved, and risks picking a slower or riskier path than the scenario actually needs.

**Source:** Kubernetes Deployments — rolling back a deployment (https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

---

### DEP-37 | MEDIUM | Post-Mortem Required Fields for P1/P2 Incidents

**Detect:** A resolved P1/P2 incident (per DEP-32's severity classification) with no post-mortem document, or one missing required fields — no incident date/duration, no severity, no timeline of detection→mitigation→recovery, no root cause, no explicit "what went well / what went wrong," or action items with no owner or deadline.

**Fix:** Require a post-mortem template with, at minimum: date + duration + severity; a timeline of what happened and when; root cause (not just the trigger); what went well and what went wrong; action items each with a named owner and a deadline. Generate the stub at incident-close time so it isn't skipped once the fire is out.

**Impact:** An incident closed without a completed post-mortem loses the only mechanism that turns an outage into a prevention — action items with no owner or deadline are indistinguishable from action items that don't exist, and the same failure mode recurs.

**Source:** Google SRE Workbook — Postmortem Culture (https://sre.google/workbook/postmortem-culture/)
