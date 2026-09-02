# Scopes: Deployment & Container-less Targets

Loaded when the Deployment or Container-less targets scope resolves to run (see SKILL.md Scopes table). Detect/fix detail for the Deployment table's rows lives in [rules-deployment.md](rules-deployment.md).

## Deployment

| Check Area | What It Covers |
|------------|---------------|
| Dockerfile | Multi-stage builds, image size, security (non-root user, minimal base) |
| Docker Compose | Service configuration, networking, volumes, health checks |
| Reverse proxy | SSL termination, caching, rate limiting, security headers |
| SSL/TLS | Certificate automation (Let's Encrypt / Caddy), HSTS, cipher suites |
| DNS | Record configuration, CDN setup, failover |

## Container-less targets

Not every deploy has an image, a host, or a process you own. When Phase 1 resolves the target to one of these, the Dockerfile / VPS-hardening / reverse-proxy areas are **N/A** — state that explicitly in the report instead of emitting "no Dockerfile" or "no firewall" as findings, and run this table instead. Everything below still applies: secrets, config separation, backups, and the failure path.

| Target | Detected by | What replaces the container checks |
|--------|-------------|-------------------------------------|
| Cloudflare Workers | `wrangler.toml` / `wrangler.jsonc` with `main` | Build proven without publishing (`npx wrangler deploy --dry-run --outdir dist`) as the pre-deploy gate; `compatibility_date` pinned to a real date, never floating; every binding (KV, D1, R2, Queues, Durable Objects) declared per environment and mirrored in a committed `.dev.vars.example`; secrets set via `wrangler secret put` only — the config file is committed, so a secret in it is a leak; `observability` enabled or its absence recorded as accepted blindness; routes and cron triggers reviewed for catch-all patterns that capture traffic nobody intended |
| Cloudflare Pages (+ Functions) | `wrangler.toml` with `pages_build_output_dir`, or a `functions/` directory in a Pages project | Same secrets and bindings rules; `npx wrangler pages functions build --outdir dist` as the build gate; preview and production environment variables separated (a preview deploy reaching production data is the recurring failure here); `_headers` and `_redirects` reviewed — on Pages the security headers live in `_headers`, not in a reverse proxy that does not exist |
| Static site on any CDN | `index.html` + no server process | TLS + cache headers + immutable asset names + one rollback path; backend monitoring, health endpoints, and process supervision are N/A |
| Localhost, single user | No remote target — the "deploy" is the user starting the app on their own machine | Reverse proxy, TLS, uptime monitoring, alerting, and rate limiting are N/A. What stays and is usually missing: a reproducible one-command start, an explicit statement of where the data lives, a backup that is not on the same disk, a tested restore path, the update procedure, and the documented behavior when the machine is simply off |
