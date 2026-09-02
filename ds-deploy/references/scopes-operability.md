# Scopes: Infrastructure, Monitoring, Incident, Admin & Support

Loaded when the Infrastructure, Monitoring, Incident, or Admin & Support Operability scope resolves to run (see SKILL.md Scopes table). Detect/fix detail for the items below lives in [rules-deployment.md](rules-deployment.md) and [rules-monitoring.md](rules-monitoring.md).

## Infrastructure

| Check Area | What It Covers |
|------------|---------------|
| VPS hardening (`deploy=vps` only) | SSH config, firewall, fail2ban, unattended upgrades, kernel hardening, AppArmor, audit logging, security scan — see DEP-30. N/A for `deploy` ∈ {docker, k8s, serverless, paas, static} — their own hardening surface is the container/platform, not an OS the project owns |
| Backup strategy | Database backups, file backups, backup testing, offsite storage — see DEP-31 |
| Restore-drill proof (D3, advisory) | Backup existing is not resilience — require a documented restore runbook + evidence of ≥1 executed end-to-end drill (worst case: total account/environment loss, restored to a clean target). Missing evidence -> advisory finding "backup exists, restore unproven — run a drill and record the runbook" (never a blocker) |
| Zero-downtime | Blue-green, rolling, canary deployment strategy — see DEP-07, DEP-14 |
| Cost optimization | Resource right-sizing, free tier usage, unnecessary spend |
| Backing services (12-Factor #4) | DB/cache/queue/mail attached as swappable resources via URL-style config (`DATABASE_URL`, `REDIS_URL`) — never hardwired to a specific instance — see DEP-12 |
| Concurrency (12-Factor #8) | Scale-out via stateless process replicas behind a load balancer/orchestrator, not vertical single-process scaling — see DEP-13 |

## Monitoring

| Check Area | What It Covers |
|------------|---------------|
| Structured logging | Log format, log levels, PII redaction in logs — see MON-01 |
| Crash reporting | Sentry / equivalent setup, source maps, PII scrubbing |
| Error-channel decision (D4, advisory) | Production has an explicit crash/error-reporting decision: consent-based opt-in PII-free aggregate channel (error class + app version + counter only), or a documented acceptance of "support-mail blindness" as a risk. Missing entirely -> advisory finding naming the blindness risk, never a blocker |
| Uptime monitoring | Health check endpoints, external uptime monitoring — see MON-05 |
| Alerting | Alert thresholds, notification channels, escalation — see MON-03 |
| Metrics | Response time, error rate, resource utilization |
| Log aggregation tier | Matches infrastructure to project maturity — see MON-08 |

## Incident

| Check Area | What It Covers |
|------------|---------------|
| Detection | Monitoring triggers, anomaly detection |
| Triage | Severity classification (P1-P3: down / degraded / minor), escalation rules — see DEP-32 |
| Mitigation | Rollback procedure, feature flags, circuit breakers — see DEP-33 |
| Recovery | Fix verification, health check confirmation, 30-min monitoring window |
| Post-mortem | Root cause analysis, timeline, action items template |

## Admin & Support Operability (D10, advisory)

Advisory only — findings here are Category B, never blockers. Distinct from Incident (above): Incident covers infra-level SRE response to outages; this covers application-level tooling for support staff handling individual user-reported errors.

| Check Area | What It Covers |
|------------|---------------|
| Diagnostic bundle | Support-facing log/diagnostic export exists (per-user or per-session bundle), scrubbed of secrets/PII before export |
| Verbose mode | A support-triggerable verbose/debug mode exists for live troubleshooting without a redeploy |
| Error-remediation runbook | Known-error records (KB-style: symptom → known cause → fix/workaround) exist for recurring user-reported errors, separate from the infra post-mortem template above |
