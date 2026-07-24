---
name: ds-deploy
description: Deployment and infrastructure — containerization, deployment, monitoring, incident response. Use when deploying an app, setting up containers/monitoring, or planning incident response.
---

# /ds-deploy

First deploy often means bloated Docker images, no health checks, no SSL, and no monitoring. This skill audits and generates production-ready infrastructure configs.

**Deployment & Infrastructure** — Containerization, deployment, monitoring, and incident response.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-deploy`, asks to deploy, containerize, or set up infrastructure, asks about Docker, VPS, SSL, monitoring, or incident response, or asks "how do I deploy this" / "review my Dockerfile"

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "deploy this to a VPS / container / k8s" | "submit app to App Store / Play Store" (→ ds-launch) |
| "configure SSL, monitoring, backups, alerts" | "audit CI pipeline" (→ ds-devops) |
| "review my Dockerfile / docker-compose" | "fix code quality" (→ ds-review / ds-fix) |
| "incident response runbook for production" | "design backend architecture" (→ ds-backend) |

## Contract

**Dimensions:** D3, D4, D7, A3 (ops), D2 (cost), D10 (diagnostics + runbooks)
**Framework alignment (advisory):** Google SRE PRR (D3, D4, D7), AWS/Azure/Google Cloud Well-Architected Cost Optimization (D2) — sourced references in SKILL-SPEC Dimension Coverage Map.

- Covers deployment, infrastructure hardening, monitoring, incident response.
- Generates configuration files and checklists — does NOT execute deployment commands.
- Minimal liability + maximum performance + minimum dependencies + maximum automation:
  - Generate configs for review — never auto-deploy to prod
  - Optimize Docker images, enable caching, configure health checks
  - Prefer minimal infra (Caddy over Nginx+certbot, SQLite over managed DB where suited)
  - Wire CI/CD integration, automated SSL, automated backups
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing deployment setup for issues |
| `--generate` | Generate Dockerfile, docker-compose, CI deploy configs |
| `--checklist` | Pre-deployment checklist for production readiness |
| `--monitor` | Set up monitoring, logging, alerting, crash reporting |
| `--incident` | Incident response: detection, triage, mitigation, post-mortem |
| `--cost` | Analyze infra costs: identify over-provisioned resources, suggest right-sizing, calculate cost at 1x/10x/100x scale |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

Without a flag: present an up-front menu covering every mode, one row each. A disambiguating flag skips the menu.

| Option | What it does |
|--------|--------------|
| Audit (recommended) | Review existing deployment setup |
| Generate | Dockerfile + CI deploy configs |
| Checklist | Production-readiness checklist |
| Monitor | Monitoring / logging / alerting setup |
| Incident | Incident response |
| Cost | Infra cost analysis |
| (Cancel) | Exit without action |

## Scopes

### Deployment

| Check Area | What It Covers |
|------------|---------------|
| Dockerfile | Multi-stage builds, image size, security (non-root user, minimal base) |
| Docker Compose | Service configuration, networking, volumes, health checks |
| Reverse proxy | SSL termination, caching, rate limiting, security headers |
| SSL/TLS | Certificate automation (Let's Encrypt / Caddy), HSTS, cipher suites |
| DNS | Record configuration, CDN setup, failover |

### Infrastructure

| Check Area | What It Covers |
|------------|---------------|
| VPS hardening | SSH config, firewall, fail2ban, unattended upgrades, kernel hardening, AppArmor, audit logging, security scan |
| Backup strategy | Database backups, file backups, backup testing, offsite storage |
| Restore-drill proof (D3, advisory) | Backup existing is not resilience — require a documented restore runbook + evidence of ≥1 executed end-to-end drill (worst case: total account/environment loss, restored to a clean target). Missing evidence -> advisory finding "backup exists, restore unproven — run a drill and record the runbook" (never a blocker, SKILL-SPEC §15) |
| Zero-downtime | Blue-green, rolling, canary deployment strategy |
| Cost optimization | Resource right-sizing, free tier usage, unnecessary spend |
| Backing services (12-Factor #4) | DB/cache/queue/mail attached as swappable resources via URL-style config (`DATABASE_URL`, `REDIS_URL`) — never hardwired to a specific instance |
| Concurrency (12-Factor #8) | Scale-out via stateless process replicas behind a load balancer/orchestrator, not vertical single-process scaling |

### Monitoring

| Check Area | What It Covers |
|------------|---------------|
| Structured logging | Log format, log levels, PII redaction in logs |
| Crash reporting | Sentry / equivalent setup, source maps, PII scrubbing |
| Error-channel decision (D4, advisory) | Production has an explicit crash/error-reporting decision: consent-based opt-in PII-free aggregate channel (error class + app version + counter only), or a documented acceptance of "support-mail blindness" as a risk. Missing entirely -> advisory finding naming the blindness risk, never a blocker (SKILL-SPEC §15) |
| Uptime monitoring | Health check endpoints, external uptime monitoring |
| Alerting | Alert thresholds, notification channels, escalation |
| Metrics | Response time, error rate, resource utilization |

### Incident

| Check Area | What It Covers |
|------------|---------------|
| Detection | Monitoring triggers, anomaly detection |
| Triage | Severity classification (P1-P3: down / degraded / minor), escalation rules |
| Mitigation | Rollback procedure, feature flags, circuit breakers |
| Recovery | Fix verification, health check confirmation, 30-min monitoring window |
| Post-mortem | Root cause analysis, timeline, action items template |

### Admin & Support Operability (D10, advisory)

Advisory only — findings here are Category B, never blockers (SKILL-SPEC §15). Distinct from Incident (above): Incident covers infra-level SRE response to outages; this covers application-level tooling for support staff handling individual user-reported errors.

| Check Area | What It Covers |
|------------|---------------|
| Diagnostic bundle | Support-facing log/diagnostic export exists (per-user or per-session bundle), scrubbed of secrets/PII before export |
| Verbose mode | A support-triggerable verbose/debug mode exists for live troubleshooting without a redeploy |
| Error-remediation runbook | Known-error records (KB-style: symptom → known cause → fix/workaround) exist for recurring user-reported errors, separate from the infra post-mortem template above |

## Delegation

**Owns:** deployment, infra, container, tls, monitoring, incident-runbook, cost | **Delegates:** ds-devops → CI pipeline structure (CI deploy step verified via ds-devops) | **Receives:** ds-devops → infra / container / TLS / monitoring; ds-ship → Phase 5 infra chain

## Execution Flow

Setup → Discover → Analyze → [Generate] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

1. **IDU:** Profile → {Config.deploy, Project Map.External, Config.constraints, Type + Stack}. Findings({deploy, infra}) → verify + use. Absent → own analysis.
2. Flags → proceed directly. No flags → interactive menu.
3. Detect deployment signals (`Dockerfile`, `docker-compose.yml`, `Procfile`, `serverless.yml`, `fly.toml`, `vercel.json`) + target: VPS, PaaS, serverless, container orchestration.

**Gate:** Mode + context confirmed. If fails → re-present interactive menu; context absent (no Dockerfile, no target detected) → "What is your deployment target? (VPS / PaaS / serverless / container)" — abort with WARN if no response after 3 prompts. **Under `--auto`:** no prompt — infer the target from repo signals (Dockerfile, PaaS config files, serverless manifests); still undetected → default `VPS`, WARN in the summary.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → use relevant findings. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. Search for deployment configs (Dockerfile, compose, CI deploy steps), monitoring configs (Sentry DSN, logging config, health endpoints), env vars + secrets management.
3. Build inventory: services, ports, volumes, external dependencies.

**Gate:** Inventory complete. If fails → undiscoverable configs logged as `{ file, status: "not_found" }`, mark inventory `partial`, continue with what was found; surface MEDIUM "incomplete inventory — some deployment configs were not located".

### Phase 3: Analyze [--audit, --checklist]

Apply rules from [references/rules-deployment.md](references/rules-deployment.md) (container security, deployment patterns, release engineering) + [references/rules-monitoring.md](references/rules-monitoring.md) (observability, alerting).

- **Dockerfile audit — deterministic tool first (advisory):** hadolint present → run it on every Dockerfile and map its findings; absent → gap-note "hadolint not installed — prose checks are this run's fallback" (never auto-install). Prose checks: base image uses specific tag (not `latest`); multi-stage build (separate build + runtime stages); non-root user in runtime stage; `.dockerignore` exists covering `.git`, `node_modules`, `.env`, test files; layer ordering — deps before source code (cache efficiency); no secrets in build args or environment (gitleaks present → run it for this check; absent → pattern-based fallback); image vulnerability scan step (Trivy or equivalent) exists in the build pipeline — absent → HIGH finding "no image CVE scan".
- **Infrastructure audit:** SSH key-only auth, no root login; firewall rules — only required ports open; backup config exists + tested; SSL/TLS A+ on SSL Labs; no exposed debug endpoints or admin panels.
- **Monitoring audit:** health check endpoint returns meaningful status; structured logging configured (not `console.log` in production); crash reporting has PII redaction; alerting on critical metrics.
- **Cost audit:** current infrastructure costs analyzed; over-provisioned resources identified; free tier alternatives suggested where applicable; cost calculated at different scale points.

**Twelve-Factor gates ([references/principles.md §3](references/principles.md)):** stateless processes (Factor 6) — no in-memory state survives restart, sessions in shared store; Build/Release/Run separation (Factor 5) — release artifact immutable, never recompiled between envs; backing services (Factor 4) — DB/cache/queue/mail attached as URL-config resources (`DATABASE_URL`, `REDIS_URL`), swappable without code change; concurrency (Factor 8) — scale-out via stateless process replicas, never vertical single-process scaling; dev/prod parity (Factor 10) — same backing service types (no SQLite-in-dev, Postgres-in-prod); logs to stdout (Factor 11) — no log file paths in app config, aggregator captures stream; port binding (Factor 7) — port from `$PORT`, never hardcoded; admin tasks (migrations, seeds) as one-off commands (Factor 12), never embedded in deploy job.

**Reliability gates ([references/principles.md §4](references/principles.md)):** timeout on every external call (DB, HTTP, queue); retry with exponential backoff on transient failures (idempotent ops only); circuit breaker on high-volume external deps; liveness + readiness probes; graceful shutdown (drain → flush → exit).

**Config & secrets gates ([references/principles.md §8](references/principles.md)):** generated configs externalize values to env vars (no hardcoded secrets, hostnames, tokens); `.env.example` stub alongside any new env var consumed; strict separation — secrets (never committed) vs config (committed, env-overridable) vs constants (immutable).

**Gate:** All applicable checks completed with file:line findings. If fails → unfinishable check area → log `{ severity: "MEDIUM", area, disposition: "inconclusive" }` with blocking reason (file unreadable, unexpected format), continue to Phase 4 with collected findings.

### Phase 4: Generate [--generate]

1. **Dockerfile:** multi-stage, non-root, optimized layers, health check.
2. **docker-compose.yml:** services, networking, volumes, health checks, restart policies.
3. **Reverse proxy config:** SSL termination, security headers, rate limiting.
4. **CI deploy step:** delegated to `/ds-devops` (OVERLAP-3). This skill does not audit or modify CI pipeline structure. Missing deploy-on-merge workflow → emit single finding `missing-ci-deploy-step → delegated to ds-devops`, continue. `/ds-devops` owns pipeline YAML; `/ds-deploy` owns deploy target (container, TLS, monitoring).
5. **Backup script:** automated DB + file backup with rotation.

Present generated files for review before writing. **Under `--auto`:** no review pause — write directly and list every generated file in the summary.

**Gate:** Generated files syntactically valid. If fails → identify invalid files, show syntax error, fix inline + re-validate; un-fixable after retry → skip writing, record `status: "failed (syntax error)"`, surface raw error for manual correction.

### Phase 5: Monitor Setup [--monitor]

Structured logging configuration (JSON format, log levels); crash reporting setup with PII redaction rules; health check endpoint implementation; uptime monitoring configuration; alert rules (error rate > 5%, response time > 2s, disk > 80%).

**Gate:** Monitoring configs valid + PII redaction configured. If fails → PII redaction missing → block writing crash-reporting config, prompt user to confirm redaction rules before proceeding; invalid config → fix inline + re-validate once; still invalid → skip, record `status: "failed (invalid config)"`, continue. **Under `--auto`:** no prompt — apply a conservative default redaction ruleset (mask email, phone, tokens, and any field named `password`/`secret`/`ssn`) and record the applied ruleset in the summary.

### Phase 6: Incident Response [--incident]

Incident severity classification (P1-P4); detection → triage → mitigate → communicate → post-mortem procedure; post-mortem template; rollback procedure documentation.

**Gate:** Procedure covers all severity levels. If fails → missing severity coverage → generate stubs with `# TODO: fill in escalation contact and mitigation steps` placeholder, record `status: "partial"`, surface HIGH finding "incomplete incident procedure — severity levels {missing} need review".

### Phase 7: Needs-Approval Review [needs_approval > 0]

**Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. **Under `--auto`:** no approval block shown — every item, including CRITICAL, resolves via the same impact/effort/risk reasoning the review step would show, applied and recorded `fixed`/`failed`; items matching the irreversible-exception list resolve `skipped (needs-human)` instead.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue to Summary; do not retry.

### Phase 8: Summary

```
ds-deploy: {OK|WARN|FAIL} | Mode: {audit|generate|checklist|monitor|incident} | Findings: {n} | Generated: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

`--auto` → append `⚠ Generated without interactive review`.

**Value Delivered:** 1-5 concrete bullets, real configuration outputs only. Every bullet's effect clause is plain everyday language a non-technical reader understands — concrete benefit, quantified when measurable ("under ~1k concurrent users, pages respond ~40% faster"), never the mechanical activity (SKILL-SPEC §5 rule 8). Example shapes (placeholders, not literal):

- `Dockerfile hardened: multi-stage build, non-root USER, HEALTHCHECK — image size reduced from {old-size} to {new-size}, attack surface narrowed`
- `SSL automation wired ({tool} handling cert renewal) — TLS expiry incidents eliminated`
- `Monitoring stack configured: {metrics} + {logs} + {alerts} — production blindness window collapses to seconds`
- `Backup + restore tested in staging — zero-data-loss target measurable, not hoped for`

Audit-only run: `{n} infra findings (severity: {breakdown}) — actionable list returned, no live config touched`.

**Gate:** Summary + Value Delivered emitted; counts balance; every finding/action has disposition. If fails → undisposed finding → assign `skipped (accounting gap)`, re-emit as WARN; report the run as incomplete so the user can re-invoke.

## Quality Gates

- Every Dockerfile uses specific base image tags (not `latest`); every docker-compose includes health checks + restart policies
- Every generated config preserves existing environment variables
- Monitoring setup includes PII redaction; SSL configuration targets A+ rating
- Backup strategy includes verification + offsite storage
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No deployment config found | Switch to generate mode |
| Unknown deployment target | Ask: VPS / PaaS / serverless / container. Under `--auto`: default `VPS`, no prompt. |
| Port conflicts in compose | Suggest alternative ports, ask user. Under `--auto`: auto-select the next available port, no prompt. |
| Secrets found in config files | Flag as CRITICAL, suggest secrets management approach |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Secrets in Docker image, no SSL, exposed debug endpoints, no backups |
| HIGH | Running as root, no health checks, `latest` tag, no monitoring |
| MEDIUM | Suboptimal layer ordering, missing `.dockerignore`, no rate limiting |
| LOW | Image size optimization, logging format consistency |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Serverless project | Skip Docker / VPS checks, focus on function config, cold start, limits |
| Static site | Minimal: CDN + SSL, skip backend monitoring |
| Monorepo | Ask which service to deploy, respect workspace boundaries. Under `--auto`: process every service with a detected deploy target (Dockerfile/manifest), no prompt. |
| Already on PaaS (Vercel / Railway) | Focus on platform-specific config, not VPS hardening |
| GPU / ML workload | Include GPU container config, model serving patterns |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
