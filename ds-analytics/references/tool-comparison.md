# Analytics Tool Comparison

Privacy-first analytics tools for solo developers. Updated March 2026.

## Decision Matrix

| Tool | Privacy | Self-Host | Free Tier | Best For | GDPR | Source |
|------|---------|-----------|-----------|----------|------|--------|
| Plausible | No cookies, no PII | Yes (Docker) | Paid only ($9/mo) | Privacy-first web | Compliant | plausible.io |
| Umami | No cookies, no PII | Yes (Docker/Vercel) | Self-host free | Budget web analytics | Compliant | umami.is |
| PostHog | Configurable | Yes (Docker) | 1M events free | Product analytics + session replay | Configurable | posthog.com |
| Mixpanel | Requires consent | No | 20M events free | Mobile + web event tracking | With consent | mixpanel.com |
| Amplitude | Requires consent | No | 50K MTU free | Growth/retention analysis | With consent | amplitude.com |
| Google Analytics | Requires consent | No | Unlimited free | SEO integration, enterprise | Contested EU | analytics.google.com |
| Cabin | No cookies, no PII | No | Free (500 events/day) | Minimal web analytics | Compliant | withcabin.com |
| Fathom | No cookies, no PII | No | Paid ($14/mo) | Simple privacy analytics | Compliant | usefathom.com |

## Recommendation by Project Type

### Web SPA / Static Sites

| Priority | Tool | Reason |
|----------|------|--------|
| 1st | Umami (self-hosted) | Free, privacy-first, lightweight script (~1KB), easy Docker deploy |
| 2nd | Plausible | Best UX for simple dashboards, no consent banner needed in EU |
| 3rd | Cabin | Zero-config, good for personal sites with low traffic |

### Mobile Apps

| Priority | Tool | Reason |
|----------|------|--------|
| 1st | PostHog | Session replay, feature flags, event tracking in one SDK |
| 2nd | Mixpanel | Strong mobile SDKs (iOS/Android/Flutter/RN), generous free tier |
| 3rd | Amplitude | Best for retention/cohort analysis, growth experiments |

### Enterprise / Team Products

| Priority | Tool | Reason |
|----------|------|--------|
| 1st | Amplitude | Advanced behavioral analytics, experiment platform, team collaboration |
| 2nd | PostHog (cloud) | All-in-one: analytics + flags + replay + surveys |
| 3rd | Mixpanel | Strong funnel/retention analysis, data governance features |

### API / Backend Services

| Priority | Tool | Reason |
|----------|------|--------|
| 1st | PostHog | Server-side SDKs, event-based model fits API tracking |
| 2nd | Mixpanel | Server-side SDKs, good for tracking API usage per customer |

## Self-Hosting Guide

### Umami (Recommended for Web)

```yaml
# docker-compose.yml
version: '3'
services:
  umami:
    image: ghcr.io/umami-software/umami:postgresql-latest
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgresql://umami:umami@db:5432/umami
      DATABASE_TYPE: postgresql
      APP_SECRET: <replace-with-random-secret>
    depends_on:
      db:
        condition: service_healthy
    restart: always

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: umami
      POSTGRES_USER: umami
      POSTGRES_PASSWORD: umami
    volumes:
      - umami-db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U umami"]
      interval: 5s
      timeout: 5s
      retries: 5
    restart: always

volumes:
  umami-db-data:
```

**Setup:** `docker compose up -d` then visit `http://localhost:3000` (default login: admin/umami).

### PostHog (Recommended for Product Analytics)

```yaml
# Use the official PostHog Helm chart or Docker setup
# Quickstart: https://posthog.com/docs/self-host
# Minimum requirements: 4GB RAM, 2 CPU cores, 50GB storage
```

**Note:** PostHog self-host is resource-intensive. For solo devs, the free cloud tier (1M events/mo) is often sufficient.

### Plausible

```yaml
# Clone the official hosting repo
# git clone https://github.com/plausible/community-edition
# Follow setup: https://github.com/plausible/community-edition
# Requires: ClickHouse + PostgreSQL (included in compose)
```

## Integration Checklist

- [ ] Choose tool based on project type (see recommendations above)
- [ ] For self-hosted: set up reverse proxy (Caddy/nginx) with HTTPS
- [ ] Add tracking script/SDK to application
- [ ] Define 3-5 key events aligned to business goals
- [ ] Verify no PII leaks in event properties
- [ ] Set data retention policy (90 days default for self-hosted)
- [ ] Configure backup for self-hosted database volumes
