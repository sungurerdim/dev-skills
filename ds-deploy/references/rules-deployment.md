# Rules: Deployment & Containerization

Rules for audit/generate/checklist modes. Each rule: ID, severity, detect pattern, fix action, source.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Container Security** | DEP-01 to DEP-05 (2 CRITICAL, 3 HIGH) | ~12 |
| **Deployment Patterns** | DEP-06 to DEP-10 (1 HIGH, 2 MEDIUM, 2 LOW) | ~75 |

---

## Container Security

### DEP-01 | CRITICAL | No Secrets in Image

**Detect:** `COPY` of `.env` files, `ARG` with secret values, hardcoded credentials in Dockerfile layers.

**Fix:** Use `--mount=type=secret` at build time, environment variables or `env_file` at runtime, or an external secret manager (Vault, AWS SSM, Doppler).

```dockerfile
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
```

**Why:** Secrets in images persist in every layer and every registry. A single leaked image exposes all credentials.

**Source:** Docker security best practices, OWASP Docker Security Cheat Sheet

---

### DEP-02 | CRITICAL | SSL/TLS Termination

**Detect:** Application serving HTTP directly on a public port without a TLS-terminating reverse proxy.

**Fix:** Place Caddy (auto-HTTPS, zero config) or Nginx + Certbot as a reverse proxy.

```
# Caddy: automatic HTTPS
app.example.com { reverse_proxy localhost:3000 }
```

**Why:** Unencrypted traffic exposes credentials, session tokens, and user data. Modern browsers flag HTTP as insecure.

**Source:** Let's Encrypt, Caddy docs, deployment-patterns.md

---

### DEP-03 | HIGH | Multi-Stage Build

**Detect:** Single-stage Dockerfile with build tools (compilers, dev dependencies, source code) present in the final image.

**Fix:** Use multi-stage builds: `FROM builder` stage compiles, `FROM runtime` stage copies only production artifacts.

```dockerfile
FROM node:22-alpine AS builder       # Go: golang:1.23-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts
COPY . .
RUN npm run build                     # Go: CGO_ENABLED=0 go build -o server .

FROM node:22-alpine AS runtime        # Go: gcr.io/distroless/static-debian12
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
```

**Why:** Reduces image size 60-90%, shrinks attack surface by excluding build tools, and speeds up pulls and deploys.

**Source:** Docker multi-stage build docs, deployment-patterns.md

---

### DEP-04 | HIGH | Health Check Endpoint

**Detect:** No `HEALTHCHECK` instruction in Dockerfile, no `/health` or `/healthz` endpoint in the application.

**Fix:** Add `/health` returning 200 with dependency checks (DB, cache), 503 when degraded. Add `HEALTHCHECK` in Dockerfile.

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1
```

**Why:** Without health checks, orchestrators route traffic to unhealthy containers. Health-gated deploys prevent bad releases from reaching users.

**Source:** Kubernetes probe patterns, deployment-patterns.md (Monitoring section)

---

### DEP-05 | HIGH | Non-Root Container User

**Detect:** Dockerfile has no `USER` directive (defaults to root).

**Fix:** `RUN addgroup -S app && adduser -S app -G app` then `USER app` before `CMD`.

**Why:** A compromised root container gives attackers root-level filesystem access and potential host escape via privilege escalation.

**Source:** CIS Docker Benchmark, Docker security best practices

---

## Deployment Patterns

### DEP-06 | HIGH | Comprehensive .dockerignore

**Detect:** Missing `.dockerignore`, or it fails to exclude `.git`, `node_modules`, `.env*`, test files, IDE configs.

**Fix:** Create `.dockerignore`: `.git`, `node_modules`, `*.md`, `.env*`, `.vscode`, `coverage`, `tests`, `__pycache__`, `.idea`, `dist`, `build`.

**Why:** Without `.dockerignore`, the build context includes everything (`.git` alone can be hundreds of MB). Reduces build time, image size, and secret leakage risk.

**Source:** Docker build context optimization, deployment-patterns.md

---

### DEP-07 | MEDIUM | Zero-Downtime Deployment

**Detect:** Deploying causes brief 502/503 errors because the old container stops before the new one is ready.

**Fix:** Use rolling updates (health check gates traffic), blue-green (two compose files, switch proxy after health check), or canary (route percentage to new version). Blue-green = instant rollback; rolling = simplest; canary = safest for large changes.

**Why:** Users experience errors during deployment without graceful transitions. Health-gated rollouts ensure only verified containers receive traffic.

**Source:** Kubernetes rolling update strategy, deployment-patterns.md (Zero-Downtime section)

---

### DEP-08 | MEDIUM | Resource Limits

**Detect:** No `memory` or `cpus` limits in Docker Compose, Kubernetes manifests, or container run commands.

**Fix:** Set `deploy.resources.limits` in compose (`memory: 512M`, `cpus: "1.0"`) or equivalent in Kubernetes.

**Why:** A single runaway process without limits can consume all host resources and crash co-located services.

**Source:** Kubernetes resource management, deployment-patterns.md (Docker Compose section)

---

### DEP-09 | LOW | Dockerfile Layer Optimization

**Detect:** `COPY . .` appears before dependency installation, busting the cache on every code change.

**Fix:** Copy dependency manifests first, install, then copy application code:

```dockerfile
COPY package.json package-lock.json ./   # or requirements.txt, go.mod
RUN npm ci                                # install deps (cached layer)
COPY . .                                  # source code (changes frequently)
```

**Why:** Proper layer ordering means dependency installation is cached across builds. Rebuilds drop from minutes to seconds when only source code changes.

**Source:** Docker layer caching best practices

---

### DEP-10 | LOW | Docker Compose for Development

**Detect:** No `docker-compose.yml` for local development, or local setup diverges significantly from production.

**Fix:** Provide `docker-compose.yml` mirroring production: same services, named volumes, networks, env files. New contributors run `docker compose up` for the full stack.

**Why:** Dev/prod parity catches environment-specific bugs early. New contributors can run the full stack with a single command.

**Source:** Docker Compose docs, deployment-patterns.md (Docker Compose for Production)
