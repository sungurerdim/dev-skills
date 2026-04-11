# /ds-deploy

First deploy often means bloated Docker images, no health checks, no SSL, and no monitoring. This skill audits and generates production-ready infrastructure configs.

**Deployment & Infrastructure** — Containerization, deployment, monitoring, and incident response.

## Triggers

- User runs `/ds-deploy`
- User asks to deploy, containerize, or set up infrastructure
- User asks about Docker, VPS, SSL, monitoring, or incident response
- User asks "how do I deploy this" or "review my Dockerfile"

## Contract

- Covers deployment, infrastructure hardening, monitoring, and incident response
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- FRC+DSC enforced.
- Generates configuration files and checklists — does NOT execute deployment commands
- **Minimal liability:** generates configs for review, never auto-deploys to production
- **Maximum performance:** optimizes Docker images, enables caching, configures health checks
- **Minimum dependencies:** prefers minimal infrastructure (Caddy over Nginx+certbot, SQLite over managed DB when appropriate)
- **Maximum automation:** CI/CD integration, automated SSL, automated backups

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing deployment setup for issues |
| `--generate` | Generate Dockerfile, docker-compose, CI deploy configs |
| `--checklist` | Pre-deployment checklist for production readiness |
| `--monitor` | Set up monitoring, logging, alerting, crash reporting |
| `--incident` | Incident response: detection, triage, mitigation, post-mortem |
| `--cost` | Analyze infrastructure costs: identify over-provisioned resources, suggest right-sizing, calculate cost at 1x/10x/100x scale |
| `--auto` | All modes, no questions, single-line summary |

Without flags: present interactive mode selection.

## Scopes

### Deployment Scope

| Check Area | What It Covers |
|------------|---------------|
| Dockerfile | Multi-stage builds, image size, security (non-root user, minimal base) |
| Docker Compose | Service configuration, networking, volumes, health checks |
| Reverse proxy | SSL termination, caching, rate limiting, security headers |
| SSL/TLS | Certificate automation (Let's Encrypt/Caddy), HSTS, cipher suites |
| DNS | Record configuration, CDN setup, failover |

### Infrastructure Scope

| Check Area | What It Covers |
|------------|---------------|
| VPS hardening | SSH config, firewall, fail2ban, unattended upgrades, kernel hardening, AppArmor, audit logging, security scan |
| Backup strategy | Database backups, file backups, backup testing, offsite storage |
| Zero-downtime | Blue-green, rolling, or canary deployment strategy |
| Cost optimization | Resource right-sizing, free tier usage, unnecessary spend |

### Monitoring Scope

| Check Area | What It Covers |
|------------|---------------|
| Structured logging | Log format, log levels, PII redaction in logs |
| Crash reporting | Sentry/equivalent setup, source maps, PII scrubbing |
| Uptime monitoring | Health check endpoints, external uptime monitoring |
| Alerting | Alert thresholds, notification channels, escalation |
| Metrics | Response time, error rate, resource utilization |

### Incident Scope

| Check Area | What It Covers |
|------------|---------------|
| Detection | Monitoring triggers, anomaly detection |
| Triage | Severity classification (P1-P3: down/degraded/minor), escalation rules |
| Mitigation | Rollback procedure, feature flags, circuit breakers |
| Recovery | Fix verification, health check confirmation, 30-min monitoring window |
| Post-mortem | Root cause analysis, timeline, action items template |

## Execution Flow

Setup → Discover → Analyze → [Generate] → Report → [Needs-Approval] → Summary

### Phase 1: Setup

**Goal:** Determine mode and deployment context.

1. **IDU:** Profile → {Config.deploy, Project Map.External, Config.constraints, Type + Stack}. Findings({deploy, infra}) → verify + use. Absent → own analysis.
2. If flags provided, proceed directly
3. If no flags, present interactive menu
4. Detect deployment signals: Dockerfile, docker-compose.yml, Procfile, serverless.yml, fly.toml, vercel.json
5. Detect target: VPS, PaaS, serverless, container orchestration

**Gate:** Mode and context confirmed.

### Phase 2: Discover

**Goal:** Map existing infrastructure.

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use relevant findings
2. Search for deployment configs (Dockerfile, compose, CI deploy steps)
3. Search for monitoring configs (Sentry DSN, logging config, health endpoints)
4. Search for environment variables and secrets management
5. Build inventory: services, ports, volumes, external dependencies

**Gate:** Inventory complete.

### Phase 3: Analyze [--audit, --checklist]

**Goal:** Identify infrastructure issues.

**Dockerfile audit:**
1. Check base image (use specific tags, not `latest`)
2. Verify multi-stage build (separate build and runtime stages)
3. Check for non-root user in runtime stage
4. Verify `.dockerignore` exists and covers: `.git`, `node_modules`, `.env`, test files
5. Check layer ordering (dependencies before source code for cache efficiency)
6. Verify no secrets in build args or environment

**Infrastructure audit:**
1. Check SSH configuration (key-only auth, no root login)
2. Verify firewall rules (only required ports open)
3. Check backup configuration exists and is tested
4. Verify SSL/TLS configuration (A+ on SSL Labs)
5. Check for exposed debug endpoints or admin panels

**Monitoring audit:**
1. Verify health check endpoint exists and returns meaningful status
2. Check structured logging is configured (not `console.log` in production)
3. Verify crash reporting has PII redaction
4. Check alerting is configured for critical metrics

**Cost audit:**
1. Analyze current infrastructure costs
2. Identify over-provisioned resources
3. Suggest free tier alternatives where applicable
4. Calculate cost at different scale points

**Gate:** All applicable checks completed with file:line findings.

### Phase 4: Generate [--generate]

**Goal:** Create deployment configuration files.

1. **Dockerfile:** Multi-stage, non-root, optimized layers, health check
2. **docker-compose.yml:** Services, networking, volumes, health checks, restart policies
3. **Reverse proxy config:** SSL termination, security headers, rate limiting
4. **CI deploy step:** Deploy-on-merge workflow, rollback capability
5. **Backup script:** Automated database + file backup with rotation

Present generated files for review before writing.

**Gate:** Generated files are syntactically valid.

### Phase 5: Monitor Setup [--monitor]

**Goal:** Configure observability stack.

1. Generate structured logging configuration (JSON format, log levels)
2. Generate crash reporting setup with PII redaction rules
3. Generate health check endpoint implementation
4. Generate uptime monitoring configuration
5. Generate alert rules (error rate > 5%, response time > 2s, disk > 80%)

**Gate:** Monitoring configs are valid and PII redaction is configured.

### Phase 6: Incident Response [--incident]

**Goal:** Define incident response procedure.

1. Generate incident severity classification (P1-P4)
2. Generate detection → triage → mitigate → communicate → post-mortem procedure
3. Generate post-mortem template
4. Generate rollback procedure documentation

**Gate:** Procedure covers all severity levels.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 8: Summary

```
ds-deploy: {OK|WARN|FAIL} | Mode: {audit|generate|checklist|monitor|incident} | Findings: N | Generated: N | Fixed: N | Skipped: N | Failed: N | Total: N
```

If `--auto` was used, append to summary: `⚠ Generated without interactive review`.

**Gate:** Summary printed with fixed/skipped/failed/total counts. Every finding/action has a disposition. Accounting verified.

## Quality Gates

- Every Dockerfile uses specific base image tags (not `latest`)
- Every docker-compose includes health checks and restart policies
- Every generated config preserves existing environment variables
- Monitoring setup includes PII redaction
- SSL configuration targets A+ rating
- Backup strategy includes verification and offsite storage
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No deployment config found | Switch to generate mode |
| Unknown deployment target | Ask user: VPS / PaaS / serverless / container |
| Port conflicts in compose | Suggest alternative ports, ask user |
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
| Serverless project | Skip Docker/VPS checks, focus on function config, cold start, limits |
| Static site | Minimal: CDN + SSL, skip backend monitoring |
| Monorepo | Ask which service to deploy, respect workspace boundaries |
| Already on PaaS (Vercel/Railway) | Focus on platform-specific config, not VPS hardening |
| GPU/ML workload | Include GPU container config, model serving patterns |
