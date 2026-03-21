# Cost Optimization Guide

A practical, solo-developer-focused guide to minimizing infrastructure costs without sacrificing reliability. All pricing is researched and noted as of 2025-2026.

---

## Mental Model: Cost Tiers

Think of your infrastructure spend in three tiers:

| Tier | Monthly Spend | Who It Fits | Philosophy |
|------|--------------|-------------|------------|
| **Zero** | $0 | Side projects, MVPs, learning | Free tiers only. Accept limits. |
| **Lean** | $5-50 | Launched product, early users | One paid compute + free everything else. |
| **Growth** | $50-200 | Revenue-generating product | Dedicated resources, monitoring, backups. |

**Rules of thumb:**

- Stay at Zero until you have real users.
- Move to Lean when free tier limits cause user-visible problems.
- Move to Growth when you have paying customers or SLA expectations.
- Every dollar should map to a user-facing outcome. If a service has no users depending on it, it should cost $0.

---

## Compute: VPS vs PaaS vs Serverless

### VPS (Self-Managed)

Best cost-per-resource ratio. You manage the OS, runtime, and deployments.

| Provider | Plan | vCPU | RAM | Storage | Price | Notes |
|----------|------|------|-----|---------|-------|-------|
| **Hetzner CX22** | Shared | 2 | 4 GB | 40 GB | ~$4.10/mo (EUR 3.79) | EU-only, 20 TB traffic included |
| **Hetzner CX32** | Shared | 4 | 8 GB | 80 GB | ~$7.40/mo (EUR 6.80) | EU-only, 20 TB traffic included |
| **Hetzner CAX11** | ARM | 2 | 4 GB | 40 GB | ~$4.10/mo | Ampere Altra, EU-only |
| **DigitalOcean** | Basic | 1 | 512 MB | 10 GB | $4/mo | 500 GB transfer |
| **DigitalOcean** | Basic | 1 | 1 GB | 25 GB | $6/mo | 1 TB transfer |
| **DigitalOcean** | Basic | 2 | 4 GB | 80 GB | $24/mo | Per-second billing since Jan 2026 |

*As of 2025-2026. Hetzner announced price increases effective April 1, 2026 (~3-30% depending on plan).*

**Tip:** Pair a Hetzner VPS with Coolify or Kamal for a self-hosted PaaS experience at VPS prices.

### PaaS (Managed)

Higher per-unit cost, but zero ops overhead for deployment, TLS, scaling.

| Provider | Free Tier | Hobby/Entry Plan | Notes |
|----------|-----------|-----------------|-------|
| **Railway** | $5 trial credit | $5/mo (includes $5 usage) | CPU: $20/vCPU, RAM: $10/GB, Storage: $0.15/GB |
| **Fly.io** | $5 one-time credit | $5/mo Hobby (includes $5 usage) | Small VM ~$3.15/mo. No free tier for new accounts. |
| **Render** | Free static sites | $7/mo (starter web service) | Free tier spins down after inactivity |

*As of 2025-2026. Both Railway and Fly.io eliminated persistent free tiers; trial credits only.*

### Serverless / Edge

Best for bursty, low-traffic workloads. Pay per invocation.

| Provider | Free Tier | Paid Pricing | Best For |
|----------|-----------|-------------|----------|
| **Cloudflare Workers** | 100K requests/day, 10ms CPU | $5/mo: 10M requests, $0.30/M after | APIs, edge logic, zero cold starts |
| **Vercel** | 100K invocations/mo, 100 GB bandwidth | $20/user/mo (Pro) | Next.js, frontend frameworks |
| **AWS Lambda** | 1M requests + 400K GB-sec/mo | $0.20/M requests + $0.0000166/GB-sec | Event-driven backends |

*As of 2025-2026.*

### Decision Matrix

| Scenario | Recommendation |
|----------|---------------|
| Learning / side project | Cloudflare Workers free or Oracle free VPS |
| MVP with <100 users | Railway Hobby or Hetzner CX22 + Coolify |
| Production SaaS | Hetzner CX32 + Kamal or Fly.io Hobby |
| High-traffic API | Cloudflare Workers paid or Hetzner CCX dedicated |

---

## Free Tier Maximization

### Always-Free (No Expiration)

These remain free indefinitely with no credit card trap:

| Service | What You Get | Catch |
|---------|-------------|-------|
| **Oracle Cloud Always Free** | 4 ARM cores, 24 GB RAM, 200 GB storage, 10 TB egress | Capacity-constrained regions; may need PAYG upgrade to provision ARM |
| **Cloudflare** | CDN, DNS, DDoS protection, Workers (100K req/day), R2 (10 GB), Pages | Must use Cloudflare DNS |
| **Neon** | 0.5 GB Postgres, 191.5 compute hours/mo, 10 branches | Scale-to-zero after 5 min inactivity |
| **Supabase** | Postgres + Auth + Storage + Realtime | Pauses after 1 week of inactivity on free tier |
| **Turso** | 5 GB storage, 500M row reads/mo, 100 databases | SQLite-based; single-writer limits |
| **PostHog** | 1M analytics events, 5K session replays, 1M feature flags | Unlimited seats |
| **Sentry** | 5K errors, 10K performance units/mo | 1 user only |
| **Grafana Cloud** | 10K metrics series, 50 GB logs, 50 GB traces | 3 users, 14-day retention |
| **Better Stack** | 10 uptime monitors | Basic features only |

### Time-Limited Free Tiers (Expire After 12 Months)

| Provider | Free Period | What You Get |
|----------|------------|-------------|
| **AWS Free Tier** | 12 months | t2.micro (750 hrs/mo), 5 GB S3, 25 GB RDS |
| **GCP Free Tier** | 12 months + $300 credit | e2-micro (always free), 30 GB storage |
| **Azure Free Tier** | 12 months + $200 credit | B1S VM (750 hrs/mo), 5 GB blob storage |

**Warning:** Time-limited tiers can generate surprise bills after expiration. Set billing alerts on day one.

### Optimal Free Stack

Combine always-free services for a $0/mo production-capable stack:

- **Compute:** Oracle Cloud ARM (4 cores, 24 GB RAM)
- **Database:** Neon free (0.5 GB Postgres) or Turso free (5 GB SQLite)
- **CDN/DNS:** Cloudflare free
- **Monitoring:** Sentry free + PostHog free
- **CI/CD:** GitHub Actions (2,000 min/mo on free plan for private repos)
- **Storage:** Cloudflare R2 free (10 GB)

---

## Database Hosting Costs

| Solution | Free Tier | Entry Paid | Cost at 50 GB | Type |
|----------|-----------|-----------|---------------|------|
| **Neon** | 0.5 GB, 191.5 CU-hrs | ~$5/mo | ~$22.50/mo (storage) + compute | Serverless Postgres |
| **Supabase** | Yes (pauses on inactivity) | $25/mo (Pro) | $25/mo (includes 8 GB, $0.125/GB after) | Postgres BaaS |
| **PlanetScale** | Removed (2024) | $5/mo (single-node) or $39/mo (Scaler) | ~$39/mo | MySQL (Vitess) |
| **Turso** | 5 GB, 500M reads | $4.99/mo | $4.99/mo (includes 10 GB) | SQLite (libSQL) |
| **Self-hosted Postgres** | N/A | $4-7/mo (on Hetzner VPS) | $4-7/mo (same VPS) | Full control |
| **SQLite (embedded)** | Always $0 | $0 | $0 | File-based, single-server |

**Key insights:**

- **SQLite is the ultimate zero-cost database.** If your app runs on a single server, SQLite with Litestream for backups costs nothing beyond your VPS. Turso extends SQLite to edge/multi-region.
- **Neon** post-Databricks acquisition (May 2025) dropped storage from $1.75 to $0.35/GB-month, making it the most cost-effective managed Postgres.
- **Supabase** is worth the $25/mo only if you use Auth, Storage, and Realtime on top of Postgres. For database-only use, Neon is cheaper.
- **PlanetScale** removed its free tier in April 2024. Only consider if you specifically need MySQL with Vitess-level horizontal scaling.

---

## GPU / AI Inference Costs

### On-Demand GPU Pricing (as of 2025-2026)

| Provider | H100 (per GPU/hr) | A100 80GB (per GPU/hr) | Notes |
|----------|-------------------|----------------------|-------|
| **RunPod Community** | ~$1.99 | ~$1.33-1.90 | Per-second billing, no minimums |
| **RunPod Secure** | ~$2.39 | ~$2.09 | Dedicated, single-tenant |
| **Lambda Labs** | ~$2.49-3.29 | ~$1.10-1.29 | Frequent capacity shortages |
| **Vast.ai** | ~$1.49-1.87 | ~$0.50 | Marketplace model, variable quality |
| **AWS (on-demand)** | ~$3.90 | ~$4.10 | Most expensive, most reliable |
| **GCP (on-demand)** | ~$3.00 | ~$3-4 | Committed use discounts available |
| **TensorDock** | ~$2.25 | N/A | No quotas or spending limits |

*Prices dropped significantly after AWS cut H100 pricing ~44% in June 2025. Expect sub-$2 universally by late 2026.*

### Cost Optimization Strategies

1. **Spot/preemptible instances:** 50-70% cheaper. Use for training, not serving.
2. **Scale-to-zero inference:** Use RunPod Serverless or Modal to pay only during requests.
3. **Smaller models:** A quantized 7B model on an RTX 4090 ($0.35-0.50/hr on Vast.ai) often beats a 70B model on an H100 for cost/quality ratio.
4. **Batch processing:** Accumulate requests and process in bulk during off-peak hours.

### Buy vs Rent Decision

| Factor | Buy (RTX 4090) | Rent (Cloud H100) |
|--------|----------------|-------------------|
| Upfront cost | ~$1,600-2,000 | $0 |
| Monthly cost | ~$30-50 (electricity) | $1,440+ (1 GPU, 24/7) |
| Break-even | ~1-2 months of 24/7 use | Never (ongoing) |
| Best for | Consistent daily usage, development | Burst training, scaling, production serving |

**Rule:** If you need a GPU more than 4 hours/day consistently, buying is cheaper within 2 months.

---

## Email Services

| Provider | Free Tier | Entry Paid | Cost at 50K/mo | Deliverability | Best For |
|----------|-----------|-----------|----------------|---------------|----------|
| **Resend** | 3,000 emails/mo | Plans available | ~$45/mo (overage-based) | Good | Modern DX, React Email templates |
| **AWS SES** | None (pay-as-you-go) | $0.10/1K emails | $5/mo | Good (DIY reputation) | High volume, technical teams |
| **Postmark** | None | $15/mo (10K emails) | ~$50/mo | Excellent | Transactional-critical apps |
| **SendGrid** | 60-day trial only (2026) | $19.95/mo (50K emails) | $19.95/mo | Good | Volume + marketing combo |

*As of 2025-2026. SendGrid eliminated its permanent free tier in May 2025.*

**Recommendations:**

- **Zero tier:** Use Resend free (3K/mo) for transactional email.
- **Lean tier:** Resend or AWS SES ($0.10/1K) depending on volume.
- **Growth tier:** Postmark ($15/mo) if deliverability is critical; SES if cost is priority.

---

## Domains and SSL

### Domain Registrar Comparison

| Registrar | .com/yr (Renewal) | .dev/yr | WHOIS Privacy | Email Forwarding |
|-----------|-------------------|---------|--------------|-----------------|
| **Cloudflare** | ~$10.44 (at-cost) | At-cost | Free | No (use ImprovMX) |
| **Porkbun** | ~$11.06 (flat) | ~$14-16 | Free | Free (20 addresses) |
| **Namecheap** | ~$13.98-15.98 | ~$16-18 | Free | Included |

*As of 2025-2026.*

**Recommendations:**

- **Best value:** Cloudflare Registrar if you already use Cloudflare DNS (~$10.44/yr .com).
- **Best standalone:** Porkbun. Flat renewal pricing, no surprise hikes.
- **Avoid:** Namecheap renewal traps (.com can jump from $10.18 promo to $18.68 renewal).

### SSL/TLS

**SSL is free.** No reason to pay for certificates in 2026:

- **Let's Encrypt:** Free, automated, 90-day certs. Use Certbot or Caddy for auto-renewal.
- **Cloudflare:** Free Universal SSL on all plans (covers your domain behind their proxy).
- **ZeroSSL:** Free alternative to Let's Encrypt with a dashboard.

---

## CDN and Bandwidth

| Service | Free Tier | Paid Pricing | Egress Cost | Best For |
|---------|-----------|-------------|-------------|----------|
| **Cloudflare CDN** | Unlimited bandwidth | $0 (free plan) | $0 | Default choice for everything |
| **Cloudflare R2** | 10 GB storage, 1M Class A ops | $0.015/GB-month storage | **$0 (zero egress)** | File storage, media serving |
| **BunnyCDN** | None | ~$0.01/GB bandwidth | Pay-per-use | Image optimization ($9.50/mo flat) |
| **AWS S3** | 5 GB (12-month free tier) | $0.023/GB-month storage | $0.09/GB | Legacy; avoid for new projects |
| **AWS CloudFront** | 1 TB/mo (always free) | $0.085/GB after | Usage-based | Only if already on AWS |

**Key insight:** Cloudflare R2 with zero egress fees is transformative. Storing 1 TB and serving 20 TB/mo costs ~$15 on R2 vs ~$1,723 on S3. Always default to R2 for new projects unless you have a specific reason for S3.

---

## Monitoring and Logging

### Free Tier Comparison

| Service | Free Includes | Paid Starts At | Best For |
|---------|--------------|---------------|----------|
| **Sentry** | 5K errors, 10K perf units, 1 user | $26/mo (Team) | Error tracking, performance |
| **PostHog** | 1M events, 5K replays, unlimited seats | Usage-based (~$0.00005/event) | Product analytics, feature flags |
| **Grafana Cloud** | 10K metrics, 50 GB logs, 3 users | $19/mo + usage | Infrastructure observability |
| **Better Stack** | 10 monitors | $21/mo (50 monitors) | Uptime monitoring, status pages |

**Recommended free monitoring stack:**

- **Errors:** Sentry free (5K errors/mo is plenty for solo dev)
- **Analytics:** PostHog free (1M events covers most early-stage apps)
- **Uptime:** Better Stack free (10 monitors) or UptimeRobot free (50 monitors)
- **Infrastructure:** Grafana Cloud free if you need metrics/logs dashboards

**When to pay:** Sentry Team ($26/mo) when you have multiple team members. PostHog paid when exceeding 1M events (roughly 50K+ MAU). Grafana Pro when you need >14 day retention.

---

## CI/CD Costs

### GitHub Actions (2026 Changes)

| Plan | Free Minutes/mo | Hosted Runner Cost | Self-Hosted Runner Cost |
|------|----------------|-------------------|----------------------|
| **Free** | 2,000 min (Linux) | Included | $0.002/min (from March 2026) |
| **Pro** | 3,000 min | Included | $0.002/min |
| **Team** | 3,000 min | Included | $0.002/min |

*GitHub reduced hosted runner prices by up to 39% on January 1, 2026. Self-hosted runner platform fee ($0.002/min) was announced for March 2026 but has been postponed pending community feedback. Public repos remain free.*

**Cost optimization tips:**

1. Cache dependencies aggressively (saves 30-60% of build time).
2. Use `paths` filters to skip CI on non-code changes.
3. Run expensive jobs (E2E tests) only on PR merge, not every push.
4. Self-hosted runner on a Hetzner VPS (~$4/mo) can replace 10,000+ GitHub Actions minutes.

### Alternatives

| Service | Free Tier | Notes |
|---------|-----------|-------|
| **Gitea Actions** | Self-hosted (free) | Compatible with GitHub Actions syntax |
| **Woodpecker CI** | Self-hosted (free) | Lightweight, Docker-native |
| **Dagger** | Open source | Portable CI pipelines, run anywhere |

---

## Cost Scaling Thresholds

When to upgrade from free to paid for each service category:

| Service | Stay Free Until... | First Paid Move | Expected Cost |
|---------|--------------------|----------------|---------------|
| **Compute** | >500 req/day or need always-on | Hetzner CX22 or Railway Hobby | $4-5/mo |
| **Database** | >0.5 GB data or need always-on | Neon Launch or Turso Developer | $5/mo |
| **Email** | >3,000 emails/mo | Resend paid or AWS SES | $5-15/mo |
| **Monitoring** | >5K errors/mo or need team access | Sentry Team | $26/mo |
| **Analytics** | >1M events/mo (~50K MAU) | PostHog paid (usage-based) | ~$50/mo |
| **CDN/Storage** | >10 GB storage on R2 | R2 paid ($0.015/GB) | $1-5/mo |
| **CI/CD** | >2,000 min/mo or slow builds | Self-hosted runner on VPS | $4-7/mo |
| **Domain** | Never free | Cloudflare or Porkbun | $10-11/yr |

---

## Monthly Budget Templates

### Zero Budget: $0/mo

For side projects, MVPs, and learning. Surprisingly capable.

| Service | Provider | Cost |
|---------|----------|------|
| Compute | Oracle Cloud Always Free (4 ARM, 24 GB) | $0 |
| Database | Neon free (0.5 GB Postgres) or SQLite | $0 |
| CDN / DNS | Cloudflare free | $0 |
| Storage | Cloudflare R2 free (10 GB) | $0 |
| Email | Resend free (3K/mo) | $0 |
| Monitoring | Sentry free + PostHog free | $0 |
| CI/CD | GitHub Actions free (2K min/mo) | $0 |
| **Total** | | **$0/mo** |

*Limitations: Oracle ARM availability is region-dependent. Neon/Supabase free pauses on inactivity. One user on Sentry.*

### Starter Budget: $15/mo

For a launched product with early users. Reliable and always-on.

| Service | Provider | Cost |
|---------|----------|------|
| Compute | Hetzner CX22 (2 vCPU, 4 GB) | ~$4/mo |
| Database | SQLite on VPS (with Litestream backup) | $0 |
| CDN / DNS | Cloudflare free | $0 |
| Storage | Cloudflare R2 free (10 GB) | $0 |
| Email | Resend free (3K/mo) | $0 |
| Monitoring | Sentry free + PostHog free + Better Stack free | $0 |
| CI/CD | GitHub Actions free | $0 |
| Domain | Cloudflare Registrar (.com) | ~$0.87/mo ($10.44/yr) |
| **Total** | | **~$5/mo** |

*Remaining budget: $10/mo buffer for traffic spikes or paid upgrades.*

### Professional Budget: $50/mo

For a revenue-generating product with hundreds of users.

| Service | Provider | Cost |
|---------|----------|------|
| Compute | Hetzner CX32 (4 vCPU, 8 GB) | ~$7/mo |
| Database | Neon Launch (10 GB, always-on) | ~$5/mo |
| CDN / DNS | Cloudflare free | $0 |
| Storage | Cloudflare R2 (50 GB) | ~$0.75/mo |
| Email | Postmark (10K emails/mo) | $15/mo |
| Monitoring | Sentry free + PostHog free | $0 |
| CI/CD | GitHub Actions free + self-hosted runner on VPS | $0 |
| Domain | Porkbun (.com + .dev) | ~$2/mo (~$25/yr) |
| Backups | Hetzner snapshots + Litestream | ~$2/mo |
| **Total** | | **~$32/mo** |

*Remaining budget: $18/mo for scaling headroom or additional services.*

### Growth Budget: $150/mo

For a product with thousands of users and SLA expectations.

| Service | Provider | Cost |
|---------|----------|------|
| Compute | Hetzner CX42 (8 vCPU, 16 GB) | ~$18/mo |
| Database | Neon Scale (50 GB, autoscaling) | ~$25/mo |
| CDN / DNS / WAF | Cloudflare Pro | $20/mo |
| Storage | Cloudflare R2 (200 GB) | ~$3/mo |
| Email | Postmark (25K emails/mo) | ~$25/mo |
| Monitoring | Sentry Team + PostHog free + Grafana free | $26/mo |
| CI/CD | GitHub Actions Pro | ~$4/mo |
| Domain | Cloudflare (.com + .dev) | ~$2/mo |
| Uptime | Better Stack free (10 monitors) | $0 |
| Backups | Automated snapshots + off-site | ~$5/mo |
| **Total** | | **~$128/mo** |

*Remaining budget: $22/mo for GPU inference bursts, additional services, or savings.*

---

## Sources

Pricing data gathered March 2026. Cloud pricing changes frequently; verify before committing.

- [Hetzner Cloud Pricing](https://www.hetzner.com/cloud) | [Price Adjustment April 2026](https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/)
- [DigitalOcean Droplet Pricing](https://www.digitalocean.com/pricing/droplets)
- [Fly.io Pricing](https://fly.io/pricing/) | [Fly.io Resource Pricing](https://fly.io/docs/about/pricing/)
- [Railway Pricing](https://railway.app/pricing)
- [Cloudflare Workers Pricing](https://developers.cloudflare.com/workers/platform/pricing/)
- [Cloudflare R2 Pricing](https://developers.cloudflare.com/r2/pricing/)
- [Vercel Pricing](https://vercel.com/pricing)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) | [Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [Neon Pricing](https://neon.tech/pricing)
- [Supabase Pricing](https://supabase.com/pricing)
- [Turso Pricing](https://turso.tech/pricing)
- [PlanetScale Pricing](https://planetscale.com/pricing)
- [RunPod Pricing](https://www.runpod.io/pricing)
- [Lambda Labs Pricing](https://lambda.ai/pricing)
- [H100 Rental Price Comparison (2026)](https://intuitionlabs.ai/articles/h100-rental-prices-cloud-comparison)
- [Resend Pricing](https://resend.com/pricing)
- [Postmark Pricing](https://postmarkapp.com/pricing)
- [SendGrid Pricing](https://sendgrid.com/en-us/pricing)
- [AWS SES Pricing](https://aws.amazon.com/ses/pricing/)
- [Sentry Pricing](https://sentry.io/pricing/)
- [PostHog Pricing](https://posthog.com/pricing)
- [Grafana Cloud Pricing](https://grafana.com/pricing/)
- [Better Stack Pricing](https://betterstack.com/pricing)
- [GitHub Actions Pricing Changes (2026)](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/)
- [Cloudflare Registrar](https://www.cloudflare.com/products/registrar/)
- [Porkbun Domain Pricing](https://porkbun.com/)
- [Namecheap Domain Pricing](https://www.namecheap.com/domains/)
