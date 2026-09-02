# Rules: Monitoring & Observability

| Section | Rules |
|---------|-------|
| **Observability** | MON-01 to MON-09 (4 HIGH, 4 MEDIUM, 1 LOW) |

## Observability

### MON-01 | HIGH | Structured JSON Logging

**Detect:** Unstructured `console.log`, `print`, `fmt.Println`, or `System.out.println` calls in production code paths. Log output lacks machine-parseable format.

**Fix:** Use a structured logger outputting JSON with consistent fields: timestamp, level, message, request_id, and relevant context.

```javascript
// Node.js — Winston
const logger = winston.createLogger({
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [new winston.transports.Console()]
});
logger.info('Request processed', { request_id: req.id, duration_ms: 42 });
```

```python
# Python — structlog
import structlog
logger = structlog.get_logger()
logger.info("request_processed", request_id=req_id, duration_ms=42)
```

```go
// Go — slog (stdlib, Go 1.21+)
slog.Info("request processed",
    slog.String("request_id", reqID),
    slog.Int("duration_ms", 42))
```

**Impact:** Structured logs → filtering, aggregation, and alerting in log management tools (Loki, Betterstack, Axiom). Unstructured text requires regex parsing and breaks on format changes.

**Source:** OpenTelemetry Logging specification (https://opentelemetry.io/docs/specs/otel/logs/)

---

### MON-02 | HIGH | Liveness and Readiness Endpoints

**Detect:** Application exposes single `/health` endpoint (or none), with no distinction between "process is alive" and "process can serve traffic."

**Fix:** Implement two separate endpoints:

- `/healthz` (liveness): Returns 200 if process is running. Minimal checks only (avoids cascading restarts).
- `/readyz` (readiness): Returns 200 if process can serve traffic. Checks database connectivity, cache availability, and critical dependencies. Returns 503 when degraded.

```javascript
app.get('/healthz', (req, res) => res.json({ status: 'alive' }));

app.get('/readyz', async (req, res) => {
  try {
    await db.query('SELECT 1');
    await redis.ping();
    res.json({ status: 'ready' });
  } catch (err) {
    res.status(503).json({ status: 'not_ready', error: err.message });
  }
});
```

**Impact:** Liveness failures → container restarts; readiness failures → remove instance from load balancer. Combining into one endpoint → unnecessary restarts when a dependency is temporarily unavailable.

**Source:** Kubernetes probe best practices (https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

### MON-03 | HIGH | Error Alerting

**Detect:** Errors logged but no alerting or notification configured. Team learns about outages from users instead of automated systems.

**Fix:** Integrate error tracking with a notification channel:

- **Error tracking:** Sentry (free: 5K errors/mo) or Betterstack
- **Notification:** Email, Slack webhook, or PagerDuty
- **Alert triggers:** Error rate spike (>5x baseline in 5 minutes), 5xx rate exceeding 1%, health check failure sustained >1 minute

```python
# Sentry — Python example
import sentry_sdk
sentry_sdk.init(dsn="https://...@sentry.io/...", traces_sample_rate=0.1)
```

**Impact:** Mean time to detection (MTTD) directly impacts mean time to recovery (MTTR). Automated alerts cut MTTD from hours to seconds for solo developers who cannot monitor dashboards continuously.

**Source:** Sentry alerting docs (https://docs.sentry.io/product/alerts/)

---

### MON-04 | MEDIUM | Distributed Tracing

**Detect:** Multi-service architecture with no trace context propagation. Debugging cross-service issues requires correlating logs manually by timestamp.

**Fix:** For multi-service systems, integrate OpenTelemetry SDK with W3C Trace Context propagation. For single-service applications, a `request_id` header passed through all log entries provides sufficient correlation.

```javascript
// OpenTelemetry — Node.js auto-instrumentation
const { NodeTracerProvider } = require('@opentelemetry/sdk-trace-node');
const { registerInstrumentations } = require('@opentelemetry/instrumentation');
const provider = new NodeTracerProvider();
provider.register();
registerInstrumentations({ instrumentations: [/* http, express, pg, etc. */] });
```

**Impact:** Without trace propagation, a single user request touching 3 services generates 3 unconnected log streams. Tracing connects them into a single timeline, reducing debugging time from hours to minutes.

**Source:** OpenTelemetry specification, W3C Trace Context standard

---

### MON-05 | MEDIUM | External Uptime Monitoring

**Detect:** No external monitoring configured. Downtime detection relies on internal health checks (which fail when entire host is unreachable) or user reports.

**Fix:** Configure an external uptime service to check production endpoints at intervals of 5 minutes or less:

| Service | Free Tier | Check Interval |
|---------|-----------|----------------|
| UptimeRobot | 50 monitors | 5 min |
| Better Stack | 10 monitors | 3 min |
| Checkly | 5 monitors | 10 min |

Alert on downtime sustained longer than 1 minute. Configure a status page for transparency with users.

**Impact:** Internal health checks cannot detect network-level, DNS, or full-host failures. External monitoring provides user's perspective on availability.

**Source:** UptimeRobot (https://uptimerobot.com/), Better Stack (https://betterstack.com/uptime)

---

### MON-06 | LOW | Cost Monitoring and Budget Alerts

**Detect:** No cost alerts configured on cloud provider accounts. Monthly spending reviewed manually or discovered via invoice surprise.

**Fix:** Set budget alerts at 80% and 100% of expected monthly cost on every cloud provider account. Review spending monthly. Document which services use free tiers and their limits so upgrades are anticipated.

| Service | Free Tier Limit | Alert When |
|---------|----------------|------------|
| Sentry | 5K errors/mo | 4K errors reached |
| PostHog | 1M events/mo | 800K events reached |
| GitHub Actions | 2,000 min/mo | 1,600 min reached |
| Cloudflare R2 | 10 GB storage | 8 GB reached |

**Impact:** Cloud services with usage-based pricing can generate unexpected bills. Free tier limits change without notice (SendGrid removed its free tier in May 2025, PlanetScale in April 2024). Proactive monitoring prevents surprise costs.

**Source:** AWS Budgets docs (https://aws.amazon.com/aws-cost-management/aws-budgets/)

---

### MON-07 | HIGH | Health Signals Measure Queue-Head Staleness, Not Just Liveness

A queue-consuming service's health endpoint checks the age of the oldest queued item against a threshold and returns 503 when exceeded — catching "process up, work stuck".

**Detect:** Health checks asserting only process liveness/port response on queue-driven services; stuck-worker incidents discovered by users while health stayed green; no documented first-look signal for operations.

**Fix:** Extend the health endpoint to compare queue-head wait time against a threshold (e.g. 180s) and return 503 on breach; document it as operations' first-look signal. Liveness says the process exists; queue-head staleness is the only cheap signal that work is actually flowing.

**Impact:** A wedged worker behind a green liveness check is an invisible outage — jobs pile up for hours while every dashboard says healthy.

**Source:** XR-079 — cross-project experience registry (2026).

### MON-08 | MEDIUM | Log Aggregation Tier Matches Project Maturity

**Detect:** Production logs going only to the container's local JSON-file driver (or stdout with no collector) on a project with multiple services or real production traffic — debugging an incident requires SSHing into the host and grepping raw log files.

**Fix:** Adopt an aggregation tier matching project maturity: single-host/solo-dev → Docker JSON driver with `max-size`/`max-file` is sufficient; multi-service or team project → self-hosted Loki + Grafana; production SaaS with paying users → managed BetterStack or Axiom (both have usable free tiers).

**Impact:** Without aggregation, a cross-service incident forces the responder to correlate raw log files by hand across every host — the exact work an aggregation tier exists to eliminate, and the reason MTTR stays high even after MON-01 structured logging is in place.

**Source:** Grafana Loki documentation (https://grafana.com/docs/loki/latest/)

### MON-09 | MEDIUM | Infrastructure Resource Metrics Monitored With Alert Thresholds

**Detect:** No CPU/memory/disk-usage monitoring configured beyond uptime pings (MON-05) and log aggregation (MON-08) — resource exhaustion is discovered only when it causes an outage, not before; no alert threshold set on disk usage specifically (the resource most likely to fail slowly and silently until full).

**Fix:** Add infrastructure resource metrics: self-hosted (Prometheus + `node_exporter`) or managed (Grafana Cloud free tier, provider-native VPS metrics) reporting CPU, memory, and disk usage; alert at a resource-exhaustion threshold (e.g. 85% sustained) before it becomes an incident, distinct from the uptime/error-rate alerts MON-03/05 already cover.

**Impact:** Uptime and error-rate monitoring both fire only after user-visible failure; resource metrics are the only signal that catches a disk filling up or memory climbing toward OOM while there's still time to act instead of react.

**Source:** Google SRE Book — Monitoring Distributed Systems / Four Golden Signals (https://sre.google/sre-book/monitoring-distributed-systems/)
