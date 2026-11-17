# Ops — images, deploy, config, domains, backups, observability, infra cost

Loaded when the project deploys somewhere (`deploy≠none`); server and container rules narrow further with `applies_when`. TLS versions, certificate checks and security headers are NWK and SEC rules; secrets in tracked files are SEC-01.

## Images

### DEP-01 [CRITICAL] Secrets or the whole repo copied into an image
applies_when: deploy=docker or deploy=k8s
- **Detect:** a Dockerfile that `COPY`s or `ADD`s `.env` files or keys, or passes secrets through `ARG` or `ENV` (both stay in the image history); a build context copied with no `.dockerignore` excluding `.git`, `.env*`, keys and local build output.
- **Mech:** T `git grep -nIE '^(COPY|ADD)[^#]*\.env|^(ARG|ENV)[[:space:]]+[A-Za-z_]*(TOKEN|SECRET|PASSWORD|PASSWD|API_KEY)' -- '*Dockerfile*' '*.dockerfile'` · `git ls-files '*Dockerfile*' '.dockerignore' '*/.dockerignore'`
- **Fix:** build secrets through `RUN --mount=type=secret`; runtime secrets from the environment or a secret manager; a `.dockerignore` listing `.git`, `.env*`, keys, dependency folders and build output.
- **Impact:** anyone who can pull the image reads every layer; deleting a file in a later layer does not remove it.
- **Source:** Docker Docs, Build secrets and Build context (.dockerignore); OWASP Docker Security Cheat Sheet.

### DEP-17 [HIGH] Image runs as root, on a full OS, from a moving tag
applies_when: deploy=docker or deploy=k8s
- **Detect:** a final stage with no `USER` (root); a single-stage build shipping compilers and dev dependencies; a full-OS base (`ubuntu`, non-slim `debian`) where a minimal or distroless base works; `FROM` by tag instead of digest; runtime specs without `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false` and dropped capabilities. Covers images the CI builds or runs as well.
- **Mech:** T `hadolint Dockerfile` · `git ls-files -z '*Dockerfile*' | xargs -0 grep -L '^USER'` · `git grep -nE '^FROM[[:space:]]+[^@[:space:]]+([[:space:]]|$)' -- '*Dockerfile*'`
- **Fix:** a multi-stage build copying only runtime artifacts; a minimal or distroless base pinned by `@sha256:`; `USER` a non-root id; a read-only root filesystem with explicit writable mounts; `cap_drop: [ALL]`, adding back only what is needed.
- **Impact:** code execution in a root, full-OS, writable container comes with a toolchain and an easier host escape; a moving tag changes the image under you.
- **Source:** CIS Docker Benchmark; Kubernetes Pod Security Standards (restricted); Docker Docs, Multi-stage builds; hadolint.

### DEP-09 [LOW] Dependency install re-runs on every source change
applies_when: deploy=docker or deploy=k8s
- **Detect:** `COPY . .` before the dependency install step of a Dockerfile.
- **Mech:** T `git grep -nE '^(COPY|ADD)[[:space:]]+\.[[:space:]]|^RUN[[:space:]].*(npm (ci|install)|pip install|uv sync|go mod download|bundle install|composer install)' -- '*Dockerfile*'`
- **Fix:** copy the manifest and lockfile, install, then copy the source.
- **Impact:** every code change rebuilds the dependency layer: minutes per build instead of seconds.
- **Source:** Docker Docs, Optimize cache usage in builds.

## Deploy and runtime

### DEP-07 [MEDIUM] Deploy drops requests or rolls back by hand
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** a deploy that stops the old instance before the new one passes readiness (502 or 503 during deploys); with real traffic, an all-at-once rollout and a person watching dashboards as the rollback trigger; on a single node, a restart that kills in-flight jobs, skips the pre-restart backup or starts services in arbitrary order.
- **Mech:** M (deploy scripts and manifests)
- **Fix:** rolling or blue-green behind readiness (OBS-02); with real traffic, staged weights with automatic rollback on error-rate or latency thresholds (Argo Rollouts, Flagger, the platform's equivalent); on one node: build first → drain new work (a flag with a TTL so it clears itself) → wait for queues to empty → back up → stop writers first, start in reverse → undrain → confirm the health endpoint reports the new version.
- **Impact:** every deploy becomes a small outage, and a bad release stays live until someone notices.
- **Source:** Kubernetes Docs, Performing a rolling update; Google SRE Workbook, Canarying releases.

### DEP-08 [MEDIUM] Service without resource limits or restart policy
applies_when: deploy=docker or deploy=k8s
- **Detect:** compose services or pods without memory and CPU limits, or without a restart policy (compose defaults to `no`: a crash or reboot leaves the service down).
- **Mech:** T `git grep -nE 'restart:|mem_limit|limits:|resources:' -- '*compose*.y*ml' '*.yaml'` · `kube-linter lint .`
- **Fix:** limits from measured use plus headroom (`deploy.resources.limits` in compose, `resources.limits` in Kubernetes); `restart: unless-stopped` or the orchestrator's equivalent on every long-running service.
- **Impact:** one runaway process starves its neighbours; one crash becomes an outage that lasts until someone notices.
- **Source:** Docker Docs, Start containers automatically; Kubernetes Docs, Resource management for pods and containers; kube-linter.

### DEP-11 [HIGH] Infrastructure open wider than needed
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** IAM policies with `"Action": "*"` or `"Resource": "*"` beyond read-only; ingress open to `0.0.0.0/0` or `::/0` on ports other than 80 and 443; compose ports published on every interface for a service behind a reverse proxy (`"8080:8080"`, not `"127.0.0.1:8080:8080"`); any database or cache port published at all.
- **Mech:** T `git grep -nIE '"(Action|Resource)"[[:space:]]*:[[:space:]]*"\*"|0\.0\.0\.0/0|::/0' -- '*.tf' '*.json' '*.yaml' '*.yml'` · `git grep -nE '^[[:space:]]*-[[:space:]]*"?[0-9]+:[0-9]+' -- '*compose*.y*ml'`
- **Fix:** least-privilege roles naming actions and resources; ingress limited to the ports and sources needed; proxied ports bound to `127.0.0.1`; datastores reached only over the internal network.
- **Impact:** internet scanners find an open datastore port within hours; a wildcard role turns one compromised component into the whole account.
- **Source:** OWASP Docker Security Cheat Sheet; AWS IAM best practices (least privilege); CIS Benchmarks.

### DEP-16 [MEDIUM] API removal without Deprecation and Sunset headers
applies_when: api≠none
- **Detect:** a public endpoint slated for removal with no `Deprecation` header (RFC 9745) or `Sunset` header (RFC 8594), a Sunset date before the Deprecation date, or no published minimum notice before a breaking removal.
- **Mech:** T `git grep -nIiE 'deprecation|sunset' -- ':!*.md' ':!*test*'`
- **Fix:** send `Deprecation` and `Sunset` with a link to the migration guide; publish the notice window and keep version numbers honest.
- **Impact:** clients get no machine-readable warning and break on removal day.
- **Source:** RFC 9745; RFC 8594; Semantic Versioning 2.0.0.

### DEP-20 [CRITICAL] Critical config defaulted, placeholder or overridable in production
- **Detect:** code defaults for salts, secrets, connection strings, prices, rate limits, endpoints or debug and mock switches (`process.env.X || 'value'`, `os.getenv('X', 'value')`); startup that accepts the `.env.example` placeholder; backing services (database, cache, queue, mail) hard-wired to a host instead of a URL from the environment; production commands relying on default file resolution where a dev override can exist (`docker compose up` beside a `compose.override.yml`).
- **Mech:** T `git grep -nIE "process\.env\.[A-Z_]+[[:space:]]*(\|\||\?\?)|getenv\([^)]*,|environ\.get\([^)]*," -- ':!*test*' ':!*.md'` · `git ls-files '*compose.override*' '*.env.local' '*.env.development'`
- **Fix:** no code default for security-, money- or environment-critical values: validate them at startup and exit with a clear message when missing or equal to a known placeholder; every backing service attached by a URL from the environment; production commands name their files (`-f compose.yml -f compose.prod.yml`).
- **Impact:** a service on a public example salt, a default price or a wrong-environment endpoint passes its health check while it leaks or bills wrong.
- **Source:** Twelve-Factor III (Config) and IV (Backing services); CWE-1188 (insecure default initialization).

## Domains and TLS

### DEP-23 [HIGH] Domain can lapse, or any CA can issue for it
- **Detect:** a production domain without auto-renew or registrar lock; missing or stale A/AAAA records; a CNAME at the zone apex; no CAA record naming the CA in use; DNSSEC offered and left unsigned. Read with `whois {domain}` and `dig +short CAA {domain}` (network).
- **Mech:** M (registrar and DNS state)
- **Fix:** auto-renew and registrar lock with renewal notices to a monitored address; the apex through ALIAS/ANAME or flattening; `CAA 0 issue "{ca}"`; DNSSEC where registrar and DNS host both support it.
- **Impact:** a lapsed domain takes the site, mail and every login link down and can be bought by someone else; without CAA any public CA can issue for it.
- **Source:** RFC 8659 (CAA); RFC 1912; ICANN, Expired Registration Recovery Policy.

### DEP-24 [HIGH] TLS not end to end, or not renewed unattended
- **Detect:** an app serving plain HTTP on a public port with no TLS-terminating proxy or platform; certificates issued by hand with no automatic renewal, or renewal failures that alert no one; a CDN in "Flexible" mode (edge to origin in plaintext) instead of full verification. Read with `openssl s_client -connect {domain}:443` (network).
- **Mech:** M (proxy, platform and CDN configuration)
- **Fix:** terminate TLS at a proxy or platform that renews itself (Caddy, cert-manager, managed certificates, certbot's packaged timer); an external check alerts 14 days before expiry (OBS-05); edge to origin encrypted and verified (Cloudflare "Full (strict)" or equivalent).
- **Impact:** an expired certificate is a full, predictable outage; a plaintext origin hop exposes what the padlock promised to protect.
- **Source:** Let's Encrypt, Integration guide; Caddy, Automatic HTTPS; Cloudflare Docs, SSL/TLS encryption modes.

### DEP-25 [HIGH] HSTS preload before every subdomain serves HTTPS
applies_when: ui∋web or api≠none
- **Detect:** `includeSubDomains` or `preload` set, or the domain submitted to hstspreload.org, while a subdomain still needs plain HTTP; preload with `max-age` below 31536000. The header itself is NWK-03.
- **Mech:** T `git grep -nIE 'includeSubDomains|preload' -- ':!*.md' ':!*.lock'`
- **Fix:** confirm every subdomain serves HTTPS, raise `max-age` in steps, add `includeSubDomains`, then `preload`.
- **Impact:** removal from the preload list takes months; a subdomain that still needs HTTP is unreachable in browsers meanwhile.
- **Source:** hstspreload.org submission requirements; RFC 6797.

## Hosts and backups

### DEP-30 [HIGH] VPS left at image defaults
applies_when: deploy=vps
- **Detect:** in provisioning scripts or on the host: SSH password or root login allowed, no default-deny firewall, no brute-force throttling on SSH, no automatic security updates, running services the stack does not use (`systemctl list-units --type=service --state=running`), no mandatory access control and no audit log.
- **Mech:** T `git grep -nIE 'PermitRootLogin|PasswordAuthentication|ufw|nftables|iptables|fail2ban|unattended-upgrades|dnf-automatic' -- ':!*.md'`
- **Fix:** `PermitRootLogin no` and `PasswordAuthentication no`; a default-deny firewall allowing SSH and HTTP(S) only; fail2ban or equivalent; unattended security upgrades; disable unmapped services; AppArmor or SELinux enforcing; run a hardening scan (Lynis) after setup and after each distribution upgrade.
- **Impact:** scanners find and try a fresh VPS within hours; each missing layer is a known entry path.
- **Source:** CIS Benchmarks (Linux distributions); OpenBSD manual, sshd_config(5); Lynis.

### DEP-31 [HIGH] Backups unverified, single-copy, or reachable from production
applies_when: db≠none
- **Detect:** no backup of persistent data; a backup step that never checks its output is non-empty and restorable; every copy on the source host or medium, none offsite and none immutable (object lock, WORM); backups unencrypted or deletable with production admin credentials; no retention tiers (unbounded growth or ad-hoc deletes); no recorded restore test, recovery point or recovery time target.
- **Mech:** T `git grep -nIE 'pg_dump|pg_basebackup|mysqldump|mongodump|restic|borg|rclone|litestream|wal-g|pgbackrest|\.backup' -- ':!*.md'`
- **Fix:** 3-2-1-1-0: three copies, two media, one offsite, one immutable, zero errors on a restore test; encrypt before a copy leaves the host (restic and borg do by default; else `age` or `gpg`), key in the secret manager and never beside the backup; separate credentials for the backup target; tiered retention (`restic forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune`); a provider's managed point-in-time backup or continuous replication (Litestream, WAL archiving) counts; restore into a scratch environment before each major release and record the result.
- **Impact:** a backup that silently wrote nothing, shares the host, or dies with stolen production credentials is gone the day it is needed; an unencrypted offsite copy is a breach of its own.
- **Source:** CISA #StopRansomware Guide (backups); restic documentation; GDPR Art. 32(1)(c).

### DEP-33 [MEDIUM] Incident response improvised
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** no written first-minutes triage order, no map from failure to rollback command with its expected downtime, or major incidents closed without a post-mortem carrying a timeline, root cause and owned, dated action items.
- **Mech:** T `git ls-files | grep -iE 'runbook|playbook|incident|post-?mortem'`
- **Fix:** one runbook: triage (real or false alarm, process up, recent errors, dependencies reachable, host resources) → severity (down, degraded, minor); rollback per scenario (bad deploy → previous image or `kubectl rollout undo`; bad migration → restore plus previous image; host loss → redeploy from IaC; bad data → point-in-time restore); a post-mortem stub created when an incident closes.
- **Impact:** the slowest or riskiest rollback gets chosen under pressure, and the same failure comes back.
- **Source:** Google SRE Workbook, Incident response and Postmortem culture.

## Observability

### OBS-01 [HIGH] Logs are free text
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** production code paths logging with `print`, `console.log`, `fmt.Println`, `System.out.println` or format strings instead of a structured logger; log lines without timestamp, level and a request or trace ID.
- **Mech:** T `git grep -nE 'console\.log\(|^[[:space:]]*print\(|fmt\.Print(ln|f)?\(|System\.out\.print' -- ':!*test*' ':!*.md' ':!scripts/*'`
- **Fix:** one structured logger writing JSON to stdout (structlog, pino, `log/slog`, Serilog) with timestamp, level, message, request ID and context fields; personal data per SAR-02.
- **Impact:** free-text logs cannot be filtered, correlated or alerted on, and parsers break when the wording changes.
- **Source:** OpenTelemetry Logs data model; Twelve-Factor XI (Logs).

### OBS-02 [HIGH] One health check for liveness and readiness
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** no health endpoint or container `HEALTHCHECK`; one endpoint that both restarts the process and checks dependencies; a queue consumer whose health ignores how long the oldest job has waited; no build version in the health response.
- **Mech:** T `git grep -nIE 'healthz|readyz|livez|/health|HEALTHCHECK|livenessProbe|readinessProbe' -- ':!*.md'`
- **Fix:** liveness (`/healthz`) answers 200 while the process runs and checks nothing else; readiness (`/readyz`) checks database, cache and critical dependencies and returns 503 when degraded, and for a queue consumer compares the oldest item's wait with a threshold; both report the deployed version; probes and `HEALTHCHECK` point at them.
- **Impact:** a dependency blip restarts healthy instances, while a wedged worker stays green and jobs pile up unseen.
- **Source:** Kubernetes Docs, Configure liveness, readiness and startup probes.

### OBS-03 [HIGH] Errors and crashes reach no one
- **Detect:** servers with no alert on error-rate spikes, sustained 5xx or failing health; shipped apps with no crash reporting, or crash reports without symbols (dSYM, `mapping.txt` or PDB not uploaded at release); a third-party crash SDK sending personal data unscrubbed, with no opt-in where personal data flows.
- **Mech:** T `git grep -nIiE 'sentry|crashlytics|bugsnag|rollbar|honeybadger|glitchtip|alertmanager|opsgenie|pagerduty' -- ':!*.md' ':!*.lock'`
- **Fix:** choose deliberately, lightest first: the platform's own crash reports (App Store Connect, Play Console Android vitals, Windows Error Reporting) or a self-hosted collector, a third-party SDK only for a need those miss, with scrubbing and opt-in where personal data flows; symbols uploaded by the release step; one alert channel the developer reads.
- **Impact:** outages and crashes are learned from users, hours or days late.
- **Source:** Google SRE Book, Monitoring distributed systems; GDPR Art. 25 (data protection by default).

### OBS-04 [MEDIUM] Requests across services cannot be followed
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** several services calling each other with no trace context propagation; a single service whose logs carry no request ID.
- **Mech:** T `git grep -nIiE 'opentelemetry|traceparent|x-request-id|request_id|correlation.?id' -- ':!*.md' ':!*.lock'`
- **Fix:** one service: a request ID created at the edge and logged on every line; several: the OpenTelemetry SDK with W3C Trace Context.
- **Impact:** one user request becomes unconnected log streams, and debugging means matching timestamps by hand.
- **Source:** W3C Trace Context; OpenTelemetry specification.

### OBS-05 [MEDIUM] Downtime seen only from inside
applies_when: deploy≠store
- **Detect:** no external check of production endpoints at 5-minute intervals or less; reliance on internal checks that go silent with the host, DNS or network.
- **Mech:** M (monitoring account)
- **Fix:** an external uptime monitor on the public URL and the health endpoint, alerting after about a minute down and checking certificate expiry (DEP-24).
- **Impact:** host, DNS and network failures go unnoticed until users report them.
- **Source:** Google SRE Book, Monitoring distributed systems (black-box monitoring).

### OBS-06 [LOW] Spend discovered on the invoice
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** usage-billed accounts (cloud, error tracking, analytics, email, CI) with no budget alert; free-tier limits the product relies on that nobody tracks.
- **Mech:** M (provider billing settings)
- **Fix:** budget alerts at 80% and 100% of the expected month on every account; each relied-on free-tier limit listed beside its account.
- **Impact:** a runaway loop or a withdrawn free tier surfaces as a bill weeks later.
- **Source:** FinOps Foundation, FinOps Framework (budgeting); AWS Budgets docs.

### OBS-08 [MEDIUM] Logs fill the disk or stay on one host
applies_when: api≠none or deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** the app writing and rotating its own log files instead of stdout; Docker's `json-file` driver without `max-size` and `max-file`, journald without size limits, or log files without logrotate; several services or real traffic with logs only on each host.
- **Mech:** T `git grep -nIE 'max-size|max-file|log-opts|logrotate|SystemMaxUse|RotatingFileHandler|FileHandler|transports\.File' -- ':!*.md'`
- **Fix:** the app writes one event stream to stdout; the runtime bounds it (`--log-opt max-size=50m --log-opt max-file=5`, or daemon-wide in `daemon.json`; journald `SystemMaxUse`); with several services or real traffic, ship to one aggregator (Loki or a managed service) with a set retention (COST-04).
- **Impact:** unbounded logs fill the disk and stop the service; logs spread over hosts turn a cross-service incident into hand-correlation.
- **Source:** Twelve-Factor XI (Logs); Docker Docs, JSON File logging driver.

### OBS-09 [MEDIUM] Disk and memory exhaustion seen only as an outage
applies_when: deploy=vps or deploy=docker or deploy=k8s
- **Detect:** no CPU, memory and disk metrics with an alert before exhaustion; uptime and error alerts are the only signals.
- **Mech:** M (monitoring configuration)
- **Fix:** host metrics (node_exporter with Prometheus, or the provider's metrics) with an alert at about 85% sustained, disk first.
- **Impact:** a slowly filling disk or a leaking process fails all at once, with no warning to act on.
- **Source:** Google SRE Book, The four golden signals (saturation).

## Infrastructure cost

### COST-02 [HIGH] Cloud egress paid on every request
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** services exchanging high volume across regions or zones on every request; static and media assets served from compute instead of a CDN or object storage; blobs stored in the database and streamed through the API.
- **Mech:** M (topology and IaC)
- **Fix:** co-locate chatty services and their replicas; serve assets from a CDN or object storage; return pre-signed URLs instead of proxying blobs.
- **Impact:** transfer is billed per GB on every request, where a CDN or co-location pays it once or never.
- **Source:** AWS data transfer pricing; Google Cloud network pricing; FinOps Framework.

### COST-03 [HIGH] Capacity far above observed load
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** instances under 20% CPU (p95) for a week; provisioned IOPS far above use; non-production environments running around the clock; container requests and limits left at defaults without profiling.
- **Mech:** M (provider metrics)
- **Fix:** one tier down when p95 CPU < 20% and memory < 50%; autoscaling storage over provisioned IOPS unless throughput-bound; non-production scales to zero or is torn down when idle; requests and limits from measured p99 plus 20%; reserved capacity only for the measured baseline.
- **Impact:** idle capacity is paid for every hour.
- **Source:** FinOps Foundation, Rightsizing; AWS Compute Optimizer.

### COST-04 [HIGH] Storage that never expires
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** buckets without lifecycle rules; log groups set to never expire; CI artifacts and container registries keeping every build and tag. Backup retention is DEP-31.
- **Mech:** T `git grep -nIE 'lifecycle_rule|LifecycleConfiguration|retention_in_days|RetentionInDays|lifecyclePolicy|retention-days' -- ':!*.md'`
- **Fix:** lifecycle rules (infrequent-access tier after 30 days, archive after 90, delete at the retention window); log retention set explicitly; CI artifacts kept for N builds or days; registry policies deleting untagged and old non-production images.
- **Impact:** storage with no expiry grows every month and is paid for forever.
- **Source:** AWS S3 Lifecycle; Google Cloud Object Lifecycle Management; Amazon ECR lifecycle policies.

### COST-07 [HIGH] Spend cannot be attributed
applies_when: deploy=docker or deploy=k8s or deploy=serverless or deploy=paas or deploy=vps
- **Detect:** IaC resources without the cost tags the project uses (service and environment at least) and nothing enforcing them at creation.
- **Mech:** T `git ls-files '*.tf' '*.tf.json' 'Pulumi.yaml' '*.template.yaml' '*.template.json'`
- **Fix:** default tags in the provider block, or a policy rule (tflint, the cloud's tag policies); untagged spend is a finding.
- **Impact:** nobody can say which service or environment a cost line belongs to, so nothing gets cut.
- **Source:** FinOps Foundation, Cost allocation.
