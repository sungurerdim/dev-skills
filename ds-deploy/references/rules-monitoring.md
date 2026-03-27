# Rules: Monitoring & Observability

Rules for audit/generate/monitor modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Observability** | MON-01 to MON-06 (3 HIGH, 2 MEDIUM, 1 LOW) | ~12 |

---

## Observability

### MON-01 | HIGH | Structured JSON Logging

**Detect:** Unstructured `console.log`, `print`, `fmt.Println`, or `System.out.println` calls used in production code paths. Log output lacks machine-parseable format.

**Fix:** Use a structured logger that outputs JSON with consistent fields: timestamp, level, message, request_id, and relevant context.

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

**Why:** Structured logs enable filtering, aggregation, and alerting in log management tools (Loki, Betterstack, Axiom). Unstructured text requires regex parsing and breaks on format changes.

**Source:** OpenTelemetry Logging specification, deployment-patterns.md (Log aggregation)

---

### MON-02 | HIGH | Liveness and Readiness Endpoints

**Detect:** Application exposes a single `/health` endpoint (or none at all), with no distinction between "process is alive" and "process can serve traffic."

**Fix:** Implement two separate endpoints:

- `/healthz` (liveness): Returns 200 if the process is running. Minimal checks only (avoids cascading restarts).
- `/readyz` (readiness): Returns 200 if the process can serve traffic. Checks database connectivity, cache availability, and critical dependencies. Returns 503 when degraded.

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

**Why:** Liveness failures trigger container restarts; readiness failures remove the instance from the load balancer. Combining them into one endpoint causes unnecessary restarts when a dependency is temporarily unavailable.

**Source:** Kubernetes probe best practices, deployment-patterns.md (Health Endpoint)

---

### MON-03 | HIGH | Error Alerting

**Detect:** Errors are logged but no alerting or notification is configured. Team learns about outages from users instead of automated systems.

**Fix:** Integrate error tracking with a notification channel:

- **Error tracking:** Sentry (free: 5K errors/mo) or Betterstack
- **Notification:** Email, Slack webhook, or PagerDuty
- **Alert triggers:** Error rate spike (>5x baseline in 5 minutes), 5xx rate exceeding 1%, health check failure sustained >1 minute

```python
# Sentry — Python example
import sentry_sdk
sentry_sdk.init(dsn="https://...@sentry.io/...", traces_sample_rate=0.1)
```

**Why:** Mean time to detection (MTTD) directly impacts mean time to recovery (MTTR). Automated alerts cut MTTD from hours to seconds for solo developers who cannot monitor dashboards continuously.

**Source:** Sentry alerting docs, deployment-patterns.md (Incident Response: Detection phase)

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

**Why:** Without trace propagation, a single user request that touches 3 services generates 3 unconnected log streams. Tracing connects them into a single timeline, reducing debugging time from hours to minutes.

**Source:** OpenTelemetry specification, W3C Trace Context standard

---

### MON-05 | MEDIUM | External Uptime Monitoring

**Detect:** No external monitoring configured. Downtime detection relies on internal health checks (which fail when the entire host is unreachable) or user reports.

**Fix:** Configure an external uptime service to check production endpoints at intervals of 5 minutes or less:

| Service | Free Tier | Check Interval |
|---------|-----------|----------------|
| UptimeRobot | 50 monitors | 5 min |
| Better Stack | 10 monitors | 3 min |
| Checkly | 5 monitors | 10 min |

Alert on downtime sustained longer than 1 minute. Configure a status page for transparency with users.

**Why:** Internal health checks cannot detect network-level, DNS, or full-host failures. External monitoring provides the user's perspective on availability.

**Source:** UptimeRobot, Better Stack, cost-optimization.md (Monitoring section)

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

**Why:** Cloud services with usage-based pricing can generate unexpected bills. Free tier limits change without notice (SendGrid removed its free tier in May 2025, PlanetScale in April 2024). Proactive monitoring prevents surprise costs.

**Source:** Cloud provider cost management docs, cost-optimization.md (Cost Scaling Thresholds)
