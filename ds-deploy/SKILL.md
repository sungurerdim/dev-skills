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
**Framework alignment (advisory):** Google SRE PRR (D3, D4, D7), AWS/Azure/Google Cloud Well-Architected Cost Optimization (D2).

- Covers deployment, infrastructure hardening, monitoring, incident response.
- Generates configuration files and checklists — does NOT execute deployment commands.
- Minimal liability + maximum performance + minimum dependencies + maximum automation:
  - Generate configs for review — never auto-deploy to prod
  - Optimize Docker images, enable caching, configure health checks
  - Prefer minimal infra (Caddy over Nginx+certbot, SQLite over managed DB where suited)
  - Wire CI/CD integration, automated SSL, automated backups
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--audit` | Review existing deployment setup for issues |
| `--generate` | Generate Dockerfile, docker-compose, CI deploy configs |
| `--checklist` | Pre-deployment checklist for production readiness |
| `--monitor` | Set up monitoring, logging, alerting, crash reporting |
| `--incident` | Incident response: detection, triage, mitigation, post-mortem |
| `--cost` | Analyze infra costs — requires a stated input: a billing export path, or monthly usage figures given in the request. Without one the cost scope reports `N/A — no billing data` (never estimated from nothing). Identifies over-provisioned resources, suggests right-sizing, calculates cost at 1x/10x/100x scale from the supplied baseline. |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Without a flag: Audit runs directly (the default — review existing deployment setup, report findings; any finding needing a decision resolves by best judgment and is recorded). `--ask` presents an up-front menu covering every mode, one row each.

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

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| Deployment | `deploy` ∈ {docker, k8s, vps} — has a container/host target | N/A — container-less branch below covers this `deploy` value instead |
| Container-less targets | `deploy` ∈ {serverless, paas, static, none} or no container signal detected | N/A — `deploy` ∈ {docker, k8s, vps} |
| Infrastructure | any source (VPS hardening row further narrows to `deploy=vps`) | — |
| Monitoring | any source | — |
| Incident | `--incident` | N/A — mode not selected |
| Admin & Support Operability | any source (advisory) | — |
| Cost | `--cost` with a stated billing input | N/A — mode not selected, or `N/A — no billing data` when the mode runs with no input |

| Scope | Reference | Loaded when |
|-------|-----------|-------------|
| Deployment, Container-less targets | [references/scopes-deployment.md](references/scopes-deployment.md) | either scope resolves to run |
| Infrastructure, Monitoring, Incident, Admin & Support | [references/scopes-operability.md](references/scopes-operability.md) | any of the four scopes resolves to run |

## Delegation

**Owns:** deployment, infra, container, tls, monitoring, incident-runbook, cost | **Delegates:** ds-devops → CI pipeline structure (CI deploy step verified via ds-devops) | **Receives:** ds-devops → infra / container / TLS / monitoring; ds-ship → Phase 5 infra chain; ds-productize → analytics (ops telemetry)

## Execution Flow

Setup → Discover → [Analyze] → [Generate] → [Monitor Setup] → [Incident Response] → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Upstream artifacts:** Profile → {Config.deploy, Project Map.External, Config.constraints, Type + Stack}. Findings({deploy, infra}) → verify + use. Absent → own analysis.
2. A disambiguating flag skips this step. Without one: Audit runs directly (the default). `--ask` with no other flag: present the mode menu.
3. Detect deployment signals (`Dockerfile`, `docker-compose.yml`, `Procfile`, `serverless.yml`, `fly.toml`, `vercel.json`, `wrangler.toml`, `wrangler.jsonc`) + target: VPS, PaaS, serverless, container orchestration, or a container-less target (edge platform, static site, localhost-only — see [references/scopes-deployment.md](references/scopes-deployment.md) § Container-less targets). Absence of a container signal is itself a signal: it selects the container-less branch, it does not make the run a Docker audit with everything missing.

**Gate:** Mode selected (flag or menu response); deployment target identified. If fails → default: infer the target from the `deploy` signal ([../core/signal-inventory.md](../core/signal-inventory.md)) and repo evidence (Dockerfile, PaaS config files, serverless manifests, `wrangler.*`, a static `index.html` with no server process) — `deploy` ∈ {docker, k8s, serverless, paas, static}; `deploy=vps` or the request explicitly names a VPS/host → `vps`. Signal `unknown` and no repo evidence → report the deployment-target scope `N/A — no deploy target detected`, never default to `vps`, continue with target-independent scopes only (monitoring, incident, cost). `--ask`: ask "What is your deployment target? (VPS / PaaS / serverless / container / edge / static / localhost-only)" — abort with WARN if no response after 3 prompts.

### Phase 2: Discover

1. **Findings file check:** `ds/audit/findings.md` fresh (its meta `git_hash` equals `git rev-parse HEAD` output AND produced in the current run-cycle; prior-cycle — however recent — is stale, diff context only) → use relevant findings. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
2. Search for deployment configs (Dockerfile, compose, CI deploy steps), monitoring configs (Sentry DSN, logging config, health endpoints), env vars + secrets management.
3. Build inventory: services, ports, volumes, external dependencies.

**Gate:** Inventory lists services, ports, volumes, and external dependencies. If fails → undiscoverable configs logged as `{ file, status: "not_found" }`, mark inventory `partial`, continue with what was found; surface MEDIUM "incomplete inventory — some deployment configs were not located".

### Phase 3: Analyze [--audit, --checklist]

Apply rules from [references/rules-deployment.md](references/rules-deployment.md) (container security, deployment patterns, release engineering) + [references/rules-monitoring.md](references/rules-monitoring.md) (observability, alerting).

- **Dockerfile audit — deterministic tool first (advisory):** hadolint present → run it on every Dockerfile and map findings to DEP-IDs; absent → gap-note "hadolint not installed — prose checks are this run's fallback" (never auto-install), then apply DEP-01, DEP-03, DEP-05, DEP-06, DEP-09, DEP-17, DEP-26 from [references/rules-deployment.md](references/rules-deployment.md) (secrets check: gitleaks present → run it; absent → pattern-based fallback).
- **Container-less audit (target from Phase 1 is edge / static / localhost-only):** run the detected target's row in [references/scopes-deployment.md](references/scopes-deployment.md) § Container-less targets instead of the Dockerfile and VPS-hardening bullets, and mark those two areas `not_applicable` with the target as the reason. Build-validation command for the target exists and is wired to the deploy path → evidence; missing → HIGH "deploys without a build gate". Secret found in a committed platform config (`wrangler.toml`, `vercel.json`, `_headers`) → CRITICAL, same as a secret in a Docker image.
- **Infrastructure audit:** apply DEP-02, DEP-11, DEP-24, DEP-25, DEP-30, DEP-31 from rules-deployment.md, plus the restore-drill-proof advisory row ([references/scopes-operability.md](references/scopes-operability.md) § Infrastructure).
- **Monitoring audit:** apply DEP-04, MON-01, MON-02, MON-03, MON-08 from rules-deployment.md / rules-monitoring.md, plus the error-channel-decision advisory row (references/scopes-operability.md § Monitoring).
- **Cost audit (requires a stated input):** a billing export path, or monthly usage figures given in the request — present → current infrastructure costs analyzed against the supplied figures, over-provisioned resources identified, free tier alternatives suggested where applicable, cost calculated at different scale points from the supplied baseline; absent → cost scope reports `N/A — no billing data`, never estimated from nothing.

**Twelve-Factor gates ([core principles §3](../core/principles.md)):** stateless processes (Factor 6) — no in-memory state survives restart, sessions in shared store; Build/Release/Run separation (Factor 5) — release artifact immutable, never recompiled between envs; backing services (Factor 4) — DB/cache/queue/mail attached as URL-config resources (`DATABASE_URL`, `REDIS_URL`), swappable without code change; concurrency (Factor 8) — scale-out via stateless process replicas, never vertical single-process scaling; dev/prod parity (Factor 10) — same backing service types (no SQLite-in-dev, Postgres-in-prod); logs to stdout (Factor 11) — no log file paths in app config, aggregator captures stream; port binding (Factor 7) — port from `$PORT`, never hardcoded; admin tasks (migrations, seeds) as one-off commands (Factor 12), never embedded in deploy job.

**Reliability gates ([core principles §4](../core/principles.md)):** timeout on every external call (DB, HTTP, queue); retry with exponential backoff on transient failures (idempotent ops only); circuit breaker on high-volume external deps; liveness + readiness probes; graceful shutdown (drain → flush → exit).

**Config & secrets gates ([core principles §8](../core/principles.md)):** generated configs externalize values to env vars (no hardcoded secrets, hostnames, tokens); `.env.example` stub alongside any new env var consumed; strict separation — secrets (never committed) vs config (committed, env-overridable) vs constants (immutable).

**Gate:** All applicable checks completed with file:line findings. If fails → unfinishable check area → log `{ severity: "MEDIUM", area, disposition: "inconclusive" }` with blocking reason (file unreadable, unexpected format), continue to Phase 4 with collected findings.

### Phase 4: Generate [--generate]

0. **Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)), before the first file write: `git status --porcelain` → empty → proceed. Non-empty → default: write only paths untouched by the pre-existing dirty state; a planned write targeting a dirty path resolves `only you can do`. `--ask`: Commit first (recommended) / Stash / Proceed anyway (risk stated). Tree cannot be checkpointed → generate nothing over uncommitted unrelated changes; report the blocker.
0b. **Target branch (before any generation).** Container-less target → steps 1-3 below do not apply; generate the platform's own equivalents instead and record steps 1-3 `not_applicable` with the target as the reason: Workers/Pages → `wrangler.toml` binding + environment skeleton with a committed `.dev.vars.example` stub (secret *names* only, never values) and the build-gate command wired into the repo's check chain; Pages/static → `_headers` carrying the security header set the missing reverse proxy would have supplied; localhost-only → a one-command start script plus a backup script with its matching restore command, both runnable by the single user who owns the machine.
1. **Dockerfile:** multi-stage, non-root, optimized layers, health check.
2. **docker-compose.yml:** services, networking, volumes, health checks, restart policies.
3. **Reverse proxy config:** SSL termination, security headers, rate limiting.
4. **CI deploy step:** `/ds-devops` present → delegate (pipeline audit belongs to ds-devops; this skill does not audit or modify CI pipeline structure). Absent → basic inline check: a deploy-on-merge workflow file exists at all (`.github/workflows/*.yml` / equivalent with a deploy job) — present, not analyzed further; absent → gap-note `[ci-deploy-step] not analyzed — requires /ds-devops`. Missing deploy-on-merge workflow (either branch) → emit single finding `missing-ci-deploy-step`, continue. `/ds-devops` owns pipeline YAML; `/ds-deploy` owns deploy target (container, TLS, monitoring).
5. **Backup script:** automated DB + file backup with rotation.

Default: no review pause — write directly and list every generated file in the summary. `--ask`: present generated files for review before writing.

**Gate:** Generated files syntactically valid — compose files: `docker compose -f {file} config -q` → exit 0 (docker absent → in-session YAML parse → no error); Dockerfiles: hadolint when present (Phase 3 tool rule) → exit 0; container-less outputs: Workers/Pages config → `npx wrangler deploy --dry-run --outdir dist` (Pages: `npx wrangler pages functions build --outdir dist`) exit 0, wrangler absent → in-session TOML/JSONC parse; shell scripts → `bash -n {file}` exit 0. If fails → identify invalid files, show syntax error, fix inline + re-run the same validation; un-fixable after retry → skip writing, record `status: "failed (syntax error)"`, surface raw error for manual correction.

### Phase 5: Monitor Setup [--monitor]

Structured logging configuration (JSON format, log levels); crash reporting setup with PII redaction rules; health check endpoint implementation; uptime monitoring configuration; alert rules (error rate > 5%, response time > 2s, disk > 80%).

**Gate:** Monitoring configs valid + PII redaction configured (`grep -niE 'redact|scrub|beforeSend' {crash-config}` → ≥1 match). If fails → PII redaction missing → default: apply a conservative redaction ruleset (mask email, phone, tokens, and any field named `password`/`secret`/`ssn`) and record the applied ruleset in the summary; `--ask`: block writing crash-reporting config, prompt user to confirm redaction rules before proceeding. Invalid config → fix inline + re-validate once; still invalid → skip, record `status: "failed (invalid config)"`, continue.

### Phase 6: Incident Response [--incident]

Incident severity classification (P1-P4); detection → triage → mitigate → communicate → post-mortem procedure; post-mortem template; rollback procedure documentation.

**Gate:** Procedure covers all severity levels. If fails → missing severity coverage → generate stubs with `# TODO: fill in escalation contact and mitigation steps` placeholder, record `status: "partial"`, surface HIGH finding "incomplete incident procedure — severity levels {missing} need review".

### Phase 7: Needs-Approval Review [--ask, needs_approval > 0]

Without `--ask` this phase does not run — every item, including CRITICAL, was already resolved via the same impact/effort/risk reasoning the review step would show, applied and recorded `fixed`/`failed`; items matching the irreversible-exception list resolved `skipped (only you can do)` instead. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue to Summary; do not retry.

### Phase 8: Summary

```
ds-deploy: {OK|WARN|FAIL} | Mode: {audit|generate|checklist|monitor|incident} | Findings: {n} | Generated: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

`Scopes: ran {deployment|container-less, infrastructure, monitoring, admin-support} · N/A — {deploy=value} · {incident: N/A — mode not selected} · {cost: N/A — no billing data | N/A — mode not selected}`

Default run (no `--ask`) → append `⚠ Generated without interactive review`.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `Dockerfile hardened: multi-stage build, non-root USER, HEALTHCHECK — image size reduced from {old-size} to {new-size}, attack surface narrowed`
- `SSL automation wired ({tool} handling cert renewal) — TLS expiry incidents eliminated`
- `Monitoring stack configured: {metrics} + {logs} + {alerts} — production blindness window collapses to seconds`
- `Backup + restore tested in staging — zero-data-loss target measurable, not hoped for`

Audit-only run: `{n} infra findings (severity: {breakdown}) — actionable list returned, no live config touched`.

**Gate:** Summary + Effect emitted; counts balance; every finding/action has disposition. If fails → undisposed finding → assign `skipped (accounting gap)`, re-emit as WARN; report the run as incomplete so the user can re-invoke.

## Quality Gates

- Every Dockerfile uses specific base image tags (not `latest`); every docker-compose includes health checks + restart policies
- Every generated config preserves existing environment variables
- Monitoring setup includes PII redaction; SSL configuration targets A+ rating
- Backup strategy includes verification + offsite storage
- W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No deployment config found | Switch to generate mode |
| Unknown deployment target | Default: resolve from the `deploy` signal and repo evidence; still unknown → `N/A — no deploy target detected`, never assume `vps`. `--ask`: ask VPS / PaaS / serverless / container. |
| Port conflicts in compose | Default: auto-select the next available port, record the choice. `--ask`: suggest alternative ports, ask user. |
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
| Edge platform (Cloudflare Workers / Pages) | Container-less branch: build-gate + bindings + secrets + `_headers`; Dockerfile and VPS scopes reported `not_applicable`, not as findings |
| Localhost-only, single user | Container-less branch: reproducible start, data location, off-machine backup, tested restore, update path; TLS / uptime / alerting reported `not_applicable` |
| Monorepo | Default: process every service with a detected deploy target (Dockerfile/manifest), respecting workspace boundaries. `--ask`: ask which service to deploy. |
| Already on PaaS (Vercel / Railway) | Focus on platform-specific config, not VPS hardening |
| GPU / ML workload | Include GPU container config, model serving patterns |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
