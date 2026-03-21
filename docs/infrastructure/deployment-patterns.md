# Deployment Patterns

Solo-dev-optimized, security-first guide to modern deployment infrastructure (2025-2026).

---

## Target Comparison: Where to Deploy

| Criteria | VPS (Hetzner/DO) | PaaS (Railway/Render) | Serverless (Lambda/CF Workers) | Edge (Fly.io) |
|---|---|---|---|---|
| Monthly cost (small app) | $4-6 | $5-20 | $0-5 | $0-7 |
| Monthly cost (prod + DB) | $6-12 | $20-50 | $15-40 | $10-35 |
| Scaling | Manual | Automatic | Automatic | Automatic |
| Cold starts | None | None | 50-500ms | None (microVMs) |
| Ops burden | High | Low | Low | Medium |
| Docker support | Full control | Supported | Limited | Native |
| Max request duration | Unlimited | 5-30 min | 10s-15 min | 5 min |
| Vendor lock-in | None | Low | Medium-High | Low-Medium |

### Platform Costs (2025-2026)

| Platform | Price | Specs |
|---|---|---|
| **Hetzner CX22** | ~$4.50/mo | 2 vCPU, 4 GB RAM, 40 GB SSD, 20 TB traffic |
| **DigitalOcean** | $6/mo | 1 vCPU, 1 GB RAM, 25 GB SSD, 1 TB traffic |
| **Railway Hobby** | $5/mo credit | Usage-based CPU/RAM, sleep-on-idle |
| **Fly.io Hobby** | $5/mo credit | ~3 VMs (256 MB each), shared CPU |
| **CF Workers Free** | $0 | 100K req/day, 10ms CPU/request |
| **CF Workers Paid** | $5/mo | 10M req/mo, 30s CPU/request |

### Decision Matrix

- **Budget-first:** Hetzner VPS + Docker + Caddy. Best cost-to-capability ratio.
- **Speed-first:** Railway or Render. Git-push deploys, managed DBs.
- **Spiky traffic:** Cloudflare Workers or AWS Lambda. Pay-per-request.
- **Global low-latency:** Fly.io. Firecracker microVMs, edge Postgres.

---

## Docker

### Multi-Stage Dockerfile

```dockerfile
FROM node:22-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build

FROM node:22-alpine AS runtime
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --from=builder --chown=app:app /app/dist ./dist
COPY --from=builder --chown=app:app /app/node_modules ./node_modules
COPY --from=builder --chown=app:app /app/package.json ./
USER app
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

**Base images:** `alpine` (~5 MB, default) | `slim` (~80 MB, glibc needed) | `distroless` (~20 MB, max security) | `ubuntu` (~75 MB, debug only)

### Security Checklist

1. Never run as root -- use `USER` directive
2. Pin base image digests in CI: `FROM node:22-alpine@sha256:abc...`
3. `--cap-drop=ALL`, add only required capabilities
4. `--security-opt=no-new-privileges` and `--read-only` where possible
5. Scan with `trivy image` or `docker scout` before deploy
6. No secrets in build args or layers -- use runtime secrets
7. Limit resources: `--memory=512m --cpus=1`

### .dockerignore

```
.git
node_modules
*.md
.env*
.vscode
coverage
tests
```

---

## Docker Compose for Production

```yaml
services:
  app:
    build: { context: ., dockerfile: Dockerfile, target: runtime }
    restart: unless-stopped
    ports: ["127.0.0.1:3000:3000"]
    env_file: [.env.production]
    deploy:
      resources:
        limits: { memory: 512M, cpus: "1.0" }
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "3" }
    networks: [internal]
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    volumes: [pgdata:/var/lib/postgresql/data]
    env_file: [.env.production]
    networks: [internal]
volumes:
  pgdata:
networks:
  internal:
```

**Key rules:** Bind ports to `127.0.0.1` (reverse proxy handles public). Named volumes for persistence. `restart: unless-stopped` everywhere. Resource limits mandatory. Never expose DB ports publicly.

**Environment files:** `.env.development` (committed, no secrets) | `.env.production` (never committed) | `.env.example` (template, committed)

**Deploy workflow:** `git pull` -> `docker compose build --no-cache app` -> `docker compose up -d --no-deps app` -> verify with `docker compose ps` -> `docker image prune -f`

---

## Reverse Proxy

| Feature | Caddy | Nginx |
|---|---|---|
| Auto HTTPS | Built-in, zero-config | Requires Certbot + cron |
| HTTP/3 | Built-in | Requires compile flag |
| Config complexity | 3-5 lines | 15-20 lines |
| Performance (10K+ RPS) | Excellent | Slightly better |
| Memory | ~20 MB | ~5 MB |
| Best for | Solo devs, small-medium | High-traffic, complex routing |

### Caddy

```
app.example.com {
    reverse_proxy localhost:3000
    header {
        Strict-Transport-Security "max-age=63072000; includeSubDomains; preload"
        X-Content-Type-Options "nosniff"
        X-Frame-Options "DENY"
        -Server
    }
    encode gzip zstd
}
```

### Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name app.example.com;
    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## SSL/TLS

**Caddy:** Automatic provisioning and renewal from Let's Encrypt. Zero config beyond domain name. Renews 30 days before expiry. TLS 1.2+ and modern ciphers by default.

**Nginx + Certbot:** `apt install certbot python3-certbot-nginx` -> `certbot --nginx -d app.example.com` -> auto-renewal via systemd timer.

**TLS hardening (Nginx):** `ssl_protocols TLSv1.2 TLSv1.3`, disable session tickets, enable OCSP stapling. Caddy applies equivalent hardening automatically.

---

## DNS and CDN

**Cloudflare setup:** Add domain -> update nameservers -> A record to VPS IP (proxied) -> CNAME `www` to `@`.

| Setting | Value | Reason |
|---|---|---|
| SSL/TLS mode | Full (Strict) | End-to-end encryption |
| Always Use HTTPS | On | Force redirects |
| Minimum TLS | 1.2 | Drop legacy protocols |
| Brotli | On | Better compression |
| Bot Fight Mode | On | Reduce abuse |

**Page rules (free tier, 3 rules):** Block `*.env*` paths | Bypass cache for `/api/*` | Cache Everything for `/assets/*` with 1-month edge TTL.

---

## Zero-Downtime Deployment

| Strategy | Resource Cost | Rollback Speed | Complexity |
|---|---|---|---|
| **Blue-Green** | 2x infra | Instant (LB switch) | Low |
| **Canary** | 1x + small % | Fast (route shift) | Medium |
| **Rolling** | 1x | Moderate (redeploy) | Low |

**Blue-green (Docker Compose):** Run two compose files (`compose.blue.yml`, `compose.green.yml`) on different ports. Deploy new version, health-check, switch Caddy/Nginx upstream, tear down old.

**Rolling:** `docker compose up -d --no-deps --build app` -- Compose replaces the container; health check gates traffic.

**Canary:** Route a percentage via Nginx `split_clients` or weighted upstreams. Monitor error rates 15-30 min before promoting.

---

## VPS Hardening: 10-Step Checklist

| # | Step | Command / Action |
|---|---|---|
| 1 | System updates | `apt update && apt upgrade -y` + enable unattended-upgrades |
| 2 | Non-root user | `adduser deploy && usermod -aG sudo deploy` |
| 3 | SSH hardening | Key-only auth, disable root, change port, `MaxAuthTries 3` |
| 4 | Firewall (UFW) | `ufw default deny incoming && ufw allow 22,80,443/tcp && ufw enable` |
| 5 | Fail2Ban | `apt install fail2ban` -- auto-bans after failed SSH attempts |
| 6 | Disable unused services | `systemctl list-units --type=service` -- stop/disable unnecessary |
| 7 | Kernel hardening | sysctl: disable IP forwarding, enable SYN cookies, no ICMP redirects |
| 8 | AppArmor | `apt install apparmor apparmor-utils && aa-enforce /etc/apparmor.d/*` |
| 9 | Audit logging | `apt install auditd` -- log privilege escalations and file access |
| 10 | Security scan | `apt install lynis && lynis audit system` -- fix findings above score 80 |

**SSH config** (`/etc/ssh/sshd_config`): `Port 2222`, `PermitRootLogin no`, `PasswordAuthentication no`, `MaxAuthTries 3`, `AllowUsers deploy`, `PubkeyAuthentication yes`.

---

## Backup Strategies

**3-2-1 rule:** 3 copies, 2 different media, 1 offsite.

### Database Backup Script

```bash
#!/bin/bash
set -euo pipefail
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/postgres"
mkdir -p "$BACKUP_DIR"
docker exec db pg_dumpall -U "$POSTGRES_USER" | gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"
[ -s "$BACKUP_DIR/db_$TIMESTAMP.sql.gz" ] || { echo "ERROR: Empty backup" >&2; exit 1; }
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +30 -delete
```

### Restic (Encrypted, Deduplicated)

```bash
restic -r s3:s3.amazonaws.com/my-backups init
restic -r s3:s3.amazonaws.com/my-backups backup /app/data /backups/postgres
restic -r s3:s3.amazonaws.com/my-backups forget --keep-daily 7 --keep-weekly 4 --keep-monthly 6 --prune
```

**Schedule** (cron): DB dump at 02:00 daily, restic backup at 03:00 daily, restic prune weekly Sunday 04:00.

---

## Monitoring and Health Checks

### Health Endpoint

```javascript
app.get('/health', async (req, res) => {
  try {
    await db.query('SELECT 1');
    res.json({ status: 'ok', uptime: process.uptime() });
  } catch (err) {
    res.status(503).json({ status: 'degraded', error: err.message });
  }
});
```

| Tool | Cost | Use Case |
|---|---|---|
| UptimeRobot | Free (50 monitors) | HTTP/ping uptime checks |
| Uptime Kuma | Free (self-hosted) | Full-featured, Docker-native |
| Sentry | Free (5K errors/mo) | Error tracking, source maps |
| Prometheus + node-exporter | Free (self-hosted) | CPU, memory, disk metrics |

**Log aggregation:** Minimal: Docker JSON driver with `max-size`/`max-file`. Medium: Loki + Grafana. Full: BetterStack or Axiom (free tiers).

**Solo dev shortcut:** `htop` + `docker stats` + UptimeRobot covers 90% of needs.

---

## Incident Response

### 5 Phases

**1. Detection:** Health check failure, error rate spike (>5x in 5 min), resource exhaustion (85%+), cert expiry alerts.

**2. Triage (first 5 min):**

```
1. Confirm issue is real           (not false positive)
2. App running?                    docker compose ps
3. Recent errors?                  docker compose logs --tail=100 app
4. Database reachable?             docker exec db pg_isready
5. Host healthy?                   free -h && df -h && uptime
6. Classify: P1 (down) / P2 (degraded) / P3 (minor)
```

**3. Mitigation:** P1 -> rollback immediately. P2 -> quick fix or scale. P3 -> schedule fix, monitor.

**4. Recovery:** Apply fix -> verify health checks -> monitor 30 min -> confirm user-facing functionality.

**5. Post-mortem:** Document date, duration, severity, timeline, root cause, what went well/wrong, and action items with owners and deadlines.

---

## Rollback Strategies

| Scenario | Strategy | Downtime |
|---|---|---|
| Bad deploy, no DB changes | Docker image rollback | < 1 min |
| Bad deploy + DB migration | Restore backup + image rollback | 5-30 min |
| Infrastructure failure | Redeploy from compose/IaC | 5-15 min |
| Corrupted data | Point-in-time DB restore | 15-60 min |
| Security breach | Full redeploy on new server | 1-4 hours |

**Docker:** `docker images myapp` -> `docker tag myapp:previous myapp:latest` -> `docker compose up -d`

**Kubernetes:** `kubectl rollout undo deployment/myapp` (or `--to-revision=N`)

**Database:** Restore from backup (`gunzip -c backup.sql.gz | psql`) or migration rollback (`prisma migrate reset`, `knex migrate:rollback`, `alembic downgrade -1`).

---

## Sources

- [Fly.io Pricing](https://fly.io/pricing/)
- [Railway vs Fly Comparison](https://docs.railway.com/platform/compare-to-fly)
- [Fly.io vs Railway 2026](https://thesoftwarescout.com/fly-io-vs-railway-2026-which-developer-platform-should-you-deploy-on/)
- [Nginx vs Caddy 2025](https://koder.ai/blog/nginx-vs-caddy)
- [Caddy as Reverse Proxy 2025](https://dev.to/hugovalters/why-caddy-is-my-favorite-reverse-proxy-in-2025-42ed)
- [Caddy vs Nginx VPS 2025](https://onidel.com/blog/caddy-vs-nginx-vps-2025)
- [Nginx vs Caddy vs Traefik 2026](https://zeonedge.com/blog/nginx-vs-caddy-vs-traefik-comparison)
- [VPS Hardening 25-Point Checklist](https://retzor.com/blog/vps-security-hardening-25-point-checklist-for-2025/)
- [Docker Security Hardening 2025](https://www.onlinehashcrack.com/guides/best-practices/docker-security-2025-hardening-containers.php)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [Docker Official Security Docs](https://docs.docker.com/engine/security/)
- [Self-Hosted Deployment Platforms 2026](https://servercompass.app/blog/best-self-hosted-deployment-platforms-2026)
