# CI/CD Setup Guide

A GitHub Actions-focused CI/CD reference for solo developers and small teams. Every recommendation optimizes for three principles: fail fast, cache aggressively, only run what changed.

## Pipeline Philosophy for Solo Devs

Solo developers cannot afford 20-minute feedback loops or flaky pipelines. Design around these constraints:

- **Fail fast.** Put linting and type-checking first. If code style is wrong, skip everything else.
- **Cache aggressively.** Every dependency fetch, every Docker layer, every build artifact should survive across runs.
- **Only run what changed.** Use path filters, affected-package detection, or `dorny/paths-filter` to skip unrelated work.
- **Keep it simple.** One workflow file per concern (CI, deploy, release). Avoid over-abstracting with reusable workflows until you genuinely have duplication.

## GitHub Actions Core Concepts

**Workflow structure:** Every workflow needs `on` (trigger), `permissions` (least-privilege), `concurrency` (dedup), and `jobs`. See the templates below for the full pattern.

**Security defaults:**
- Declare `permissions` at the top level. Default to `contents: read`.
- Never use `pull_request_target` without understanding its write-access implications.
- Pin third-party actions to full commit SHAs, not tags.
- Use `GITHUB_TOKEN` with minimal scopes. Avoid PATs unless required (e.g., release-please downstream triggers).

**Concurrency:** Use `concurrency: { group: "${{ github.workflow }}-${{ github.ref }}", cancel-in-progress: true }` on PR workflows. Set `cancel-in-progress: false` on deploy workflows to avoid partial deploys.

## Workflow Templates

### Lint / Test / Build

Chain jobs with `needs` so failures short-circuit early:

```yaml
name: CI
on: [push, pull_request]
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
permissions: { contents: read }

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run lint
  test:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm test
  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npm run build
```

### Auto-Deploy Staging / Manual Production Deploy

```yaml
# staging: triggers on push to main
name: Deploy Staging
on: { push: { branches: [main] } }
permissions: { contents: read, id-token: write }
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run build && ./scripts/deploy.sh staging
```

```yaml
# production: manual trigger with version input
name: Deploy Production
on:
  workflow_dispatch:
    inputs:
      version: { description: "Release tag", required: true }
permissions: { contents: read, id-token: write }
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with: { ref: "${{ github.event.inputs.version }}" }
      - run: npm ci && npm run build && ./scripts/deploy.sh production
```

### Matrix Builds

Use `fail-fast: true` so a failure in one cell cancels the rest immediately:

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    strategy: { fail-fast: true, matrix: { node-version: [20, 22] } }
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "${{ matrix.node-version }}", cache: npm }
      - run: npm ci && npm test
```

## Caching Strategies

All major setup actions have built-in caching via the `cache` parameter:

| Language | Action | Cache Config |
|----------|--------|-------------|
| Node.js | `actions/setup-node@v4` | `cache: npm` (or `pnpm`, `yarn`). Set `cache-dependency-path` for monorepos. |
| Python | `actions/setup-python@v5` | `cache: pip`, `cache-dependency-path: requirements*.txt` |
| Go | `actions/setup-go@v5` | `cache: true` (module + build caches automatic) |
| Gradle | `actions/setup-java@v4` | `cache: gradle`. For Android, also cache `~/.android/avd` with `actions/cache@v4`. |

### General Guidance

GitHub Actions cache has a **10 GB limit per repository**. Cache keys should include OS, lockfile hash, and tool version. Use `restore-keys` for partial hits but avoid overly broad patterns. Require `actions/cache@v4` -- older versions hit the deprecated Cache API v1.

## Docker Build Pipelines

### Multi-Stage Dockerfile

Use three stages: deps (production only), build (full dev + compile), runtime (minimal final image). Copy `--from=deps` and `--from=build` into the final stage to keep the image small and cache-friendly.

### Full Docker Build Workflow with GHA Cache

Use `mode=max` to cache all stages, not just the final one:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.ref == 'refs/heads/main' }}
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Registry cache fallback:** When GHA cache hits the 10 GB limit, switch to `type=registry,ref=ghcr.io/${{ github.repository }}:cache`.

**Multiple images:** Set `scope` per image to prevent cache collisions: `cache-from: type=gha,scope=api`.

## Automated Testing in CI

### Test Pyramid

Structure your CI to match the test pyramid:

| Layer | Speed | Scope | When to Run |
|-------|-------|-------|-------------|
| Unit tests | < 5 min | Functions, modules | Every PR |
| Integration tests | 5-15 min | API, database | Every PR |
| E2E tests | 15-30 min | Full user flows | Main branch, pre-deploy |

### Service Containers for Integration Tests

```yaml
jobs:
  integration:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env: { POSTGRES_PASSWORD: test, POSTGRES_DB: testdb }
        ports: ["5432:5432"]
        options: --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm run test:integration
        env:
          DATABASE_URL: postgres://postgres:test@localhost:5432/testdb
          REDIS_URL: redis://localhost:6379
```

### Playwright Sharding

Split E2E tests across parallel runners to stay under 15 minutes:

```yaml
jobs:
  e2e:
    runs-on: ubuntu-latest
    strategy: { fail-fast: false, matrix: { shard: [1/4, 2/4, 3/4, 4/4] } }
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npx playwright install --with-deps chromium
      - run: npx playwright test --shard=${{ matrix.shard }}
      - uses: actions/upload-artifact@v4
        if: failure()
        with: { name: "playwright-report-${{ strategy.job-index }}", path: playwright-report/ }
```

## Secrets Management and OIDC

### GitHub Secrets Hierarchy

Resolution order (most specific wins): **Environment secrets** > **Repository secrets** > **Organization secrets**. Never log secrets (string manipulation can bypass masking). Rotate on schedule. Prefer OIDC over stored secrets for cloud access.

### OIDC for Cloud Providers

OIDC eliminates long-lived cloud credentials. GitHub mints a short-lived JWT for each job, and your cloud provider validates it.

All examples require `permissions: { id-token: write, contents: read }` at the job or workflow level.

| Provider | Action | Key Parameter |
|----------|--------|---------------|
| AWS | `aws-actions/configure-aws-credentials@v4` | `role-to-assume: arn:aws:iam::ACCOUNT:role/GitHubActions` |
| GCP | `google-github-actions/auth@v2` | `workload_identity_provider: projects/ID/locations/global/...` |
| Azure | `azure/login@v2` | `client-id`, `tenant-id`, `subscription-id` (from secrets) |

OIDC rules: always set `id-token: write`. On GCP, use attribute conditions to restrict by org/repo (GitHub uses a single issuer URL). Scope roles to least privilege -- one role per repo, one identity per environment. Tokens are short-lived; do not cache or pass between jobs.

## Branch Protection and Deployment Triggers

### Branch Protection Rules

Configure on `main`: require status checks to pass, require branches to be up to date, disallow force pushes and deletions. Optionally require signed commits.

### Environment Gates

Use GitHub Environments: `staging` (auto-deploy on push to `main`, no approval) and `production` (require manual approval via `workflow_dispatch` or environment reviewers). Set `environment: { name: production, url: https://myapp.com }` on deploy jobs.

### Trigger Strategy

| Event | Use Case |
|-------|----------|
| `push` to `main` | Run CI, deploy staging |
| `pull_request` | Run CI (lint, test, build) |
| `workflow_dispatch` | Manual production deploy |
| `release: published` | Publish packages, deploy prod |
| `schedule` | Nightly full test suite, dependency updates |

## Release Automation

### Conventional Commits

Both tools require Conventional Commits: `feat:` (minor), `fix:` (patch), `feat!:` or `BREAKING CHANGE` footer (major). Enforce with commitlint in CI:

```yaml
name: Commitlint
on: [pull_request]
jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: 22 }
      - run: npm install @commitlint/cli @commitlint/config-conventional
      - run: npx commitlint --from ${{ github.event.pull_request.base.sha }}
```

### release-please vs semantic-release

| Aspect | release-please | semantic-release |
|--------|---------------|-----------------|
| **Workflow** | Opens a Release PR; you merge when ready | Fully automated on every push to main |
| **Control** | Human-in-the-loop | Hands-off |
| **Language support** | Multi-language (Node, Python, Go, Java, etc.) | Primarily JS/npm ecosystem |
| **Plugin ecosystem** | Limited | Extensive |
| **Commit format** | Flexible Conventional Commits | Strict Conventional Commits |
| **GitHub integration** | Native (first-class Action) | Needs extra configuration |
| **npm weekly downloads** | ~108K | ~2.2M |
| **Best for** | Solo devs, web apps, multi-language | Libraries, full automation pipelines |

**Recommendation for solo devs:** Use release-please. The PR-based workflow gives you a review checkpoint without slowing you down.

### release-please Workflow

```yaml
name: Release
on: { push: { branches: [main] } }
permissions: { contents: write, pull-requests: write }
jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: googleapis/release-please-action@v4
        id: release
        with: { release-type: node }
      - uses: actions/checkout@v4
        if: ${{ steps.release.outputs.release_created }}
      - run: npm ci && npm publish
        if: ${{ steps.release.outputs.release_created }}
        env: { NODE_AUTH_TOKEN: "${{ secrets.NPM_TOKEN }}" }
```

Note: `GITHUB_TOKEN`-created resources will not trigger other workflows. Use a PAT for downstream triggers.

## Mobile CI/CD with Fastlane

### Fastfile Structure

```ruby
default_platform(:ios)
platform :ios do
  lane :test do run_tests(scheme: "MyApp") end
  lane :beta do
    setup_ci
    match(type: "appstore", readonly: true)
    build_app(scheme: "MyApp")
    upload_to_testflight(skip_waiting_for_build_processing: true)
  end
end
platform :android do
  lane :test do gradle(task: "test") end
  lane :beta do
    gradle(task: "bundleRelease")
    upload_to_play_store(track: "internal", aab: "app/build/outputs/bundle/release/app-release.aab")
  end
end
```

### iOS Code Signing with match

Fastlane `match` manages certificates and provisioning profiles via a private Git repo. Configure `Matchfile` with `git_url`, `storage_mode("git")`, `type("appstore")`, and `app_identifier`. Store the match passphrase and App Store Connect API key in GitHub Secrets.

### Full iOS Workflow

```yaml
name: iOS Beta
on: { push: { branches: [main], paths: ["ios/**", "shared/**"] } }
jobs:
  ios-beta:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - uses: ruby/setup-ruby@v1
        with: { ruby-version: "3.3", bundler-cache: true }
      - run: bundle exec fastlane ios beta
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          APP_STORE_CONNECT_API_KEY: ${{ secrets.ASC_API_KEY }}
          MATCH_GIT_BASIC_AUTHORIZATION: ${{ secrets.MATCH_GIT_AUTH }}
```

### Android Keystore Signing

Store the keystore as a base64-encoded secret (`base64 -i my-release-key.jks | pbcopy`, then save as `ANDROID_KEYSTORE_BASE64`).

```yaml
name: Android Beta
on: { push: { branches: [main], paths: ["android/**", "shared/**"] } }
jobs:
  android-beta:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17, cache: gradle }
      - run: echo "${{ secrets.ANDROID_KEYSTORE_BASE64 }}" | base64 -d > android/app/release.jks
      - run: bundle exec fastlane android beta
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
```

## Monorepo CI

### Tool Comparison

| Feature | Turborepo | Nx | dorny/paths-filter |
|---------|-----------|----|--------------------|
| **Affected detection** | `--filter='...[origin/main]'` | `nx affected` + `nrwl/nx-set-shas@v4` | Glob path matching |
| **Remote cache** | Vercel (free tier) | Nx Cloud (free tier) | N/A |
| **Task orchestration** | Parallel by default | Parallel with dep graph | Manual job deps |
| **Distributed execution** | No | Yes (Nx Agents) | Manual matrix |
| **Complexity** | Low | Medium-High | Minimal |
| **Best for** | Small-medium JS monorepos | Large monorepos, enterprise | Simple multi-project repos |

### Turborepo Example

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npx turbo run lint test build --filter='...[origin/main]'
        env: { TURBO_TOKEN: "${{ secrets.TURBO_TOKEN }}", TURBO_TEAM: "${{ vars.TURBO_TEAM }}" }
```

### Nx Example

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: nrwl/nx-set-shas@v4
      - uses: actions/setup-node@v4
        with: { node-version: 22, cache: npm }
      - run: npm ci && npx nx affected -t lint test build
```

### paths-filter Example

For repos without a build orchestrator, use `dorny/paths-filter@v3` to conditionally skip jobs:

```yaml
jobs:
  detect:
    runs-on: ubuntu-latest
    outputs:
      api: ${{ steps.filter.outputs.api }}
      web: ${{ steps.filter.outputs.web }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            api: ['packages/api/**', 'packages/shared/**']
            web: ['packages/web/**', 'packages/shared/**']
  test-api:
    needs: detect
    if: needs.detect.outputs.api == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd packages/api && npm ci && npm test
  test-web:
    needs: detect
    if: needs.detect.outputs.web == 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd packages/web && npm ci && npm test
```

Always use `fetch-depth: 0` so tools can compare against the base branch. Run affected-only on PRs; run full builds nightly as a safety net.

## Cost Model and Runner Selection

### Per-Minute Pricing (as of January 2026)

| Runner | Per Minute | Multiplier | Notes |
|--------|-----------|------------|-------|
| Linux (2-core) | ~$0.006 | 1x | Default, cheapest option |
| Windows (2-core) | ~$0.010 | 2x | Use only when you must |
| macOS (3-core) | ~$0.062 | 10x | iOS builds only |

Free tier (included with GitHub Free/Pro): 2,000 minutes/month (Linux equivalent). Windows and macOS consume minutes at their multiplier rate.

**Larger runners:** Team/Enterprise plans only. No free tier. Per-minute billing, no idle cost. Up to 64 vCPUs. Worth it when builds exceed 15 minutes on standard runners.

**macOS cost reduction:** Cache CocoaPods/SPM/Xcode derived data. Run linting and shared-code tests on Linux. Use `paths` filters to only trigger iOS builds on `ios/**` changes. Avoid macOS matrix builds -- test on one version, use TestFlight for device coverage. Prefer `macos-15` (Apple Silicon) for faster builds.

**Self-hosted runners:** Starting March 2026, $0.002/min platform fee (~$0.12/hr) applies. Public repos remain exempt.

### Concurrency Limits

| Plan | Standard Concurrent | macOS Concurrent |
|------|---------------------|-----------------|
| Free | 20 | 5 |
| Team | 60 | 5 |
| Enterprise | 500 | 50 |

## Sources

- [Actions Runner Pricing](https://docs.github.com/en/billing/reference/actions-runner-pricing) | [2026 Pricing Changes](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/) | [Jan 2026 Price Reduction](https://github.blog/changelog/2026-01-01-reduced-pricing-for-github-hosted-runners-usage/)
- [actions/cache](https://github.com/actions/cache) | [Docker GHA Cache](https://docs.docker.com/build/cache/backends/gha/) | [Docker Cache in GHA](https://docs.docker.com/build/ci/github-actions/cache/)
- [GitHub OIDC Docs](https://docs.github.com/en/actions/concepts/security/openid-connect)
- [release-please](https://github.com/googleapis/release-please) | [release-please-action](https://github.com/googleapis/release-please-action) | [vs semantic-release](https://www.hamzak.xyz/blog-posts/release-please-vs-semantic-release)
- [Fastlane + GitHub Actions](https://docs.fastlane.tools/best-practices/continuous-integration/github/) | [Mobile CI/CD Blueprint](https://developersvoice.com/blog/mobile/mobile-cicd-blueprint/)
- [Monorepo GHA Guide](https://www.warpbuild.com/blog/github-actions-monorepo-guide) | [Path Filters](https://oneuptime.com/blog/post/2025-12-20-monorepo-path-filters-github-actions/view)
- [GHA Breaking Changes 2025](https://github.blog/changelog/2025-04-15-upcoming-breaking-changes-and-releases-for-github-actions/)
