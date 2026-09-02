# Rules: CI/CD Pipeline, Agent & Tool Security, Workflow Lint, Runner Hygiene

Applies to all project types: web, API, CLI, library, mobile, monorepo. Loaded for the `ci` scope.

| Section | Rules |
|---------|-------|
| **CI/CD & Workflow** | DOP-01–07 (1 CRITICAL, 6 HIGH) |
| **Agent & Tool Security** | DOP-15–16 (2 HIGH) |
| **Workflow Security & Lint** | DOP-19–20 (1 HIGH, 1 CRITICAL) |
| **Container & Cloud Auth Hardening** | DOP-22–23 (2 HIGH) |
| **Runner & Host Hygiene** | DOP-24–25 (2 MEDIUM) |
| **Config Hygiene** | DOP-40 (1 LOW) |

## CI/CD & Workflow

### DOP-01 [CRITICAL] CI/CD Pipeline Presence
Every project has automated quality enforcement before merge — cloud CI, or a documented, deliberate local-only gate (pre-commit/pre-push hook) applied consistently across every sibling repo that made the same choice.
- **Detect:**
  - No CI config files found (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `bitrise.yml`, `azure-pipelines.yml`, `codemagic.yaml`) AND no local gate (pre-commit/pre-push hook, a `scripts/check*.sh`/`quality*.sh` wired to git hooks, or an equivalent documented in the repo)
  - A documented CI opt-out applied inconsistently across sibling repos in the same org/monorepo family — some still carry live workflows, CI badges, or CI-referencing configs after the decision
  - The opt-out's local-gate replacement is undocumented — no README/CONTRIBUTING/CLAUDE.md line names the decision and the replacement mechanism
- **Fix:** No CI and no local gate → create a pipeline with stages: format → analyze/lint → test → build. Platform-specific:
  - Flutter: `flutter format`, `flutter analyze`, `flutter test`, `flutter build`
  - Node: `prettier`, `eslint`, `jest/vitest`, `tsc/build`
  - Python: `ruff format`, `ruff check`, `pytest`
  - Go: `gofmt`, `go vet`, `go test`, `go build`
  - Rust: `cargo fmt`, `cargo clippy`, `cargo test`, `cargo build`
  - Java/Kotlin: `spotless`, `detekt/checkstyle`, `test`, `build`
  - C#/.NET: `dotnet format`, `dotnet build -warnaserror`, `dotnet test`, `dotnet publish`
  - Ruby: `rubocop`, `srb tc` (if Sorbet), `rspec/minitest`, `bundle exec rake`
  - PHP: `pint/php-cs-fixer`, `phpstan/psalm`, `phpunit`, `composer build`
  - Elixir: `mix format`, `mix credo`, `mix test`, `mix release`
  - C/C++: `clang-format`, `clang-tidy`, `ctest`, `cmake --build`
  - Scala: `scalafmt`, `scalafix`, `sbt test`, `sbt assembly`

  Opt-out already decided → sweep every sibling repo in one pass: delete workflow files, badges, CI-referencing configs and doc sections; document the opt-out and its local-gate replacement once in each repo's docs.
- **Impact:** Manual builds → inconsistent releases and missed quality checks; an inconsistent or undocumented opt-out leaves stale CI badges that mislead contributors into believing checks ran when nothing did.
- **GitHub Actions (2025-2026):** Use reusable workflows (`uses: ./.github/workflows/ci.yml`) for DRY pipelines. Use OIDC auth (`permissions: id-token: write`) instead of long-lived secrets for cloud deploys. Use matrix builds for multi-version testing. Pin actions by SHA, not tag.
- **Source:** GitHub Actions Reusable Workflows docs, OIDC for GitHub Actions (github.blog 2023), CI/CD best practices (martinfowler.com); XR-177 — cross-project experience registry (2026).

### DOP-02 [HIGH] Quality Gate Coverage
CI must include format, lint/analyze, test, and build stages.
- **Detect:** CI config exists but missing stages. Check for presence of format, lint/analyze, test, and build commands in workflow files.
- **Fix:** Add missing stages. Run in order: format → lint → test → build. Fail pipeline on any stage failure.
- **Impact:** Missing quality gates allow regressions to reach production
- **GitHub Actions (2025-2026):** Use `concurrency` groups to cancel redundant runs. Use `needs:` for stage ordering (format → lint → test → build). Use composite actions for shared steps.
- **Source:** GitHub Actions Workflow Syntax docs, Google DORA State of DevOps Report (2024)

### DOP-03 [HIGH] CI/Local Parity
CI checks should match local development checks.
- **Detect:**
  - CI runs different lint/test commands than package.json scripts or Makefile targets
  - CI has checks not runnable locally (or vice versa)
  - CI uses different tool versions than local (no `.tool-versions`, `.nvmrc`, or version pinning)
- **Fix:** Align CI and local commands. Use `.tool-versions` or `.nvmrc` for version pinning. Provide `make ci` or equivalent that mirrors CI exactly. The dotfile documents; the script enforces: build/release scripts detect the pinned runtime themselves — auto-prioritize it on PATH when present, warn explicitly when absent — rather than assuming the developer read the dotfile. (XR-106)
- **Impact:** "Works on my machine" issues, CI-only failures block development
- **GitHub Actions (2025-2026):** Use `actions/setup-node@v4` with `node-version-file: '.nvmrc'` for version parity. Use `act` (nektos/act) for local workflow testing.
- **Source:** 12factor.net (Dev/prod parity), nektos/act README, GitHub Actions setup-node docs

### DOP-04 [HIGH] Conventional Commits
feat:/fix:/refactor: format with automated changelog.
- **Detect:** Unstructured commit messages. No conventional prefixes. Manual changelog.
- **Fix:** `feat:`, `fix:`, `refactor:`, `ci:`, `docs:`, `chore:`. Breaking: `feat!:` or `BREAKING CHANGE:`. Integrate release-please or semantic-release.
- **Impact:** Unstructured commits make changelog generation and release automation unreliable
- **Source:** Conventional Commits v1.0

### DOP-05 [HIGH] Crash Reporting
Production apps must have crash reporting with symbolicated traces.
- **Detect:** No crash reporting integration. Missing debug symbol upload in CI.
  - Flutter: no `firebase_crashlytics` or `sentry_flutter` in pubspec
  - Node/Web: no error tracking service (Sentry, Datadog, Bugsnag)
  - Mobile: missing dSYM/mapping.txt upload in CI
- **Fix:** Add crash reporting SDK. Upload debug symbols in CI. Monitor crash-free rate.
- **Impact:** Without crash reporting, production issues go undetected until user reports
- **Source:** Sentry Best Practices Guide, Firebase Crashlytics docs, DORA Metrics (change failure rate)

### DOP-06 [HIGH] Dependency Audit CI Gate
CVE check in CI. Fail on vulnerabilities.
- **Detect:** No audit command in CI. Known CVEs in deps.
  - Flutter: no `dart pub audit` in CI
  - Node: no `npm audit` or `yarn audit` in CI
  - Python: no `pip-audit` or `safety` in CI
  - Go: no `govulncheck` in CI
  - Rust: no `cargo audit` in CI
  - Java: no `dependencyCheck` or OWASP plugin in CI
  - C#/.NET: no `dotnet list package --vulnerable` in CI
  - Ruby: no `bundle-audit` in CI
  - PHP: no `composer audit` in CI
  - Elixir: no `mix deps.audit` in CI
  - C/C++: no `conan audit` or dependency scanning in CI
  - Scala: no `sbt dependencyCheck` in CI
- **Fix:** Add audit command as CI gate. Fail on HIGH/CRITICAL advisories.
- **Impact:** Known CVEs in production expose users to security risks
- **Source:** OWASP, platform-specific audit tools

### DOP-07 [HIGH] Required Status Checks
Protected branches should require CI checks to pass before merge.
- **Detect:** Branch protection exists but no required status checks configured. Or CI jobs run but aren't required for merge.
- **Fix:** Configure required status checks for lint, test, and build jobs on default branch.
- **Impact:** PRs can merge with failing CI, bypassing quality gates
- **Source:** GitHub/GitLab branch protection docs

## Agent & Tool Security

### DOP-15 [HIGH] MCP & Agent Tool Security
The tool/MCP layer an agent uses is an attack surface. EchoLeak (CVE-2025-32711) exfiltrated Microsoft 365 Copilot data from a single crafted email; CurXecute (CVE-2025-54135) reached RCE in Cursor by steering the agent to write `.cursor/mcp.json` — the edit landed on disk even when the user clicked reject.
- **Detect:**
  - MCP servers/tools added without pinned versions
  - Tool output fed back into the agent as instructions rather than data
  - Ambient or over-broad credentials granted to a tool
  - Approval prompts showing a model-written prose summary instead of the raw tool call
  - AI-tool config dirs (`.cursor/`, `.continue/`, `**/mcp.json`) absent from `.gitignore`
- **Fix:** Pin MCP server/tool versions and re-review on change (rug-pull). Treat tool output as untrusted data, never instructions. Least-agency: scope each tool's permissions to the task, no ambient secrets. Approval prompts must show the raw tool name + parameters. Gitignore AI-tool config dirs.
- **Impact:** An unpinned or over-privileged tool/MCP layer is a direct data-exfiltration or RCE path from a single crafted input, as EchoLeak and CurXecute demonstrated in production agent products.
- **Source:** [OWASP Agentic Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), [EchoLeak CVE-2025-32711](https://nvd.nist.gov/vuln/detail/CVE-2025-32711), [CurXecute CVE-2025-54135](https://nvd.nist.gov/vuln/detail/CVE-2025-54135)

### DOP-16 [HIGH] Human Review for Agent-Authored CI/Infra PRs
A PR opened by an autonomous agent gets human review before merge when it touches privileged surfaces, and never auto-merges to a protected branch.
- **Detect:**
  - Auto-merge enabled on protected branches
  - Agent/bot PRs touching `.github/workflows/` (or other CI config), infrastructure-as-code, auth, or secrets merged without human approval
  - Agent dependency-bump PRs auto-merged
- **Fix:** Require human review + branch protection for agent PRs touching CI/CD, IaC, auth, or secrets. Disable auto-merge on protected branches. Treat agent dependency-bumps as a supply-chain entry point — review before merge.
- **Impact:** An unreviewed agent PR merged into CI/IaC/auth/secrets is a supply-chain entry point with no human checkpoint before it runs with production-adjacent privilege.
- **Source:** [Agent Autonomy in Open-Source PRs — 8,031 PRs (arXiv:2601.17413, 2026)](https://arxiv.org/abs/2601.17413)

## Workflow Security & Lint

### DOP-19 [HIGH] Workflow Lint Layers (actionlint + zizmor)
CI workflow files get two deterministic lint layers: actionlint for correctness (syntax, expression types, action inputs, embedded shell) and zizmor for security anti-patterns. Complementary, not interchangeable — run both.
- **Detect:**
  - `.github/workflows/` exists but neither actionlint nor zizmor runs in CI or pre-commit
  - Only one layer present (correctness without security, or the reverse)
- **Fix:** Tool present → run it and merge its findings into the report. Absent → recommend adding both as CI steps (user confirms — never auto-install); the prose rules in this file are the fallback for this run.
- **Impact:** Hand-rolled workflow review re-derives, on every run, checks these scanners encode deterministically — misses accumulate.
- **Source:** [Unpacking Security Scanners for GitHub Actions Workflows (arXiv 2601.14455)](https://arxiv.org/html/2601.14455v2); [WordPress Coding Standards Handbook — GitHub Actions](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/github-actions/) (adopts both)

### DOP-20 [CRITICAL] `pull_request_target` With Untrusted Code
`pull_request_target` workflows run with the base repository's secrets and write token. Combined with a checkout or execution of the PR's untrusted head code, a fork PR can exfiltrate secrets. March 2026: attackers exploited exactly this misconfiguration in the aquasecurity/trivy-action GitHub Action to exfiltrate organization and repository secrets, then used those credentials to backdoor LiteLLM on PyPI.
- **Detect:**
  - Workflow triggered on `pull_request_target` checks out the PR's head (untrusted fork) code
  - The same workflow runs build / install / test steps over that checked-out code
- **Fix:** Use `pull_request` for anything that executes PR code. Reserve `pull_request_target` for metadata-only jobs (labels, comments) with no checkout of PR code; when PR content must be read, treat it as data, never execute it. zizmor detects this pattern deterministically (DOP-19).
- **Impact:** Secret exfiltration → downstream supply-chain compromise of everything those credentials can publish.
- **Source:** [We hardened zizmor's GitHub Actions static analyzer — Security Boulevard (2026-05)](https://securityboulevard.com/2026/05/we-hardened-zizmors-github-actions-static-analyzer/); [Harden your GitHub Actions workflows with zizmor — mattsch.com (2026-03-28)](https://mattsch.com/blog/2026/03/28/harden-your-github-actions-workflows-with-zizmor-dependency-pinning-and-dependency-cooldowns/)

## Container & Cloud Auth Hardening

### DOP-22 [HIGH] CI-Built Container Hardening
Images the pipeline builds or runs (builder images, job containers, published artifacts) meet the hardening baseline; production-image hardening is canonical in ds-deploy DEP-17.
- **Detect:**
  - CI job/builder containers or pipeline-published images FROM a full OS base, running as root, or referenced by mutable tag instead of digest
  - Pipeline builds a production image with no hardening check step (no lint/policy against the ds-deploy DEP-17 baseline: distroless/minimal, non-root, read-only fs, cap-drop, digest pin)
- **Fix:** Apply the ds-deploy DEP-17 baseline to every image the pipeline touches; add a CI policy/lint step (hadolint + policy rules) so a non-conforming image fails the build instead of shipping. Production-image specifics (K8s securityContext, runtime mounts) → ds-deploy DEP-17 (canonical, advisory-handoff: ds-deploy absent → apply the baseline inline from this rule)
- **Impact:** A root, full-OS builder container is the highest-value target in the supply chain — it holds source, credentials, and publish rights simultaneously
- **Source:** ds-deploy DEP-17 (canonical baseline); Google distroless docs; Kubernetes Pod Security Standards

### DOP-23 [HIGH] CI Cloud Auth via OIDC Federation
CI jobs obtain cloud credentials via OIDC federation, not long-lived keys stored as secrets.
- **Detect:**
  - Long-lived cloud keys in CI secrets: `AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_SECRET`, GCP service-account JSON keyfile
  - Workflow missing `permissions:` block — `GITHUB_TOKEN` gets the broad default instead of read-only
- **Fix:** Federate: `aws-actions/configure-aws-credentials` with role assumption, `azure/login` with federated credentials, `google-github-actions/auth` with Workload Identity Federation — issued credentials are scoped and short-lived (typically ≤1 hour). Set `permissions: contents: read` at workflow level and elevate per-job only where needed (GitHub's own hardening guidance). Delete the long-lived keys after cutover
- **Impact:** A leaked long-lived cloud key is valid until rotated — often months; a leaked OIDC-issued credential dies within the hour and is scoped to one role
- **Source:** GitHub Actions OIDC hardening docs; cloud-vendor WIF/federation docs

## Runner & Host Hygiene

### DOP-24 [MEDIUM] Build-Cache Eviction Policy
Shared/self-hosted runners evict Docker build cache on a schedule — age-based or size-capped, never indiscriminate.
- **Detect:**
  - Self-hosted CI runners with no scheduled build-cache pruning (disk fills silently until builds fail)
  - Cleanup implemented as full `docker system prune -a` on shared runners — destroys warm caches for every project on the host
- **Fix:** Scheduled job (weekly cron): `docker builder prune --filter "until=168h" -f` (age-based, 7 days) or `--keep-storage <size>` (size-capped). Run `docker buildx du` first to see what is actually consuming space before choosing the policy
- **Impact:** An unpruned build cache fills shared-runner disk silently until every project's builds start failing at once; indiscriminate full pruning destroys warm caches for every other project on the host.
- **Source:** Docker builder-prune docs; depot.dev cache-management guidance

### DOP-25 [MEDIUM] Log Rotation Defaults
Every unbounded log sink has rotation configured; retention follows compliance floor, not disk size.
- **Detect:**
  - Services writing log files with no `logrotate`/journald size limits
  - Docker daemon on default `json-file` driver without `max-size`/`max-file` options (container logs grow without bound)
- **Fix:** Production baseline: daily rotation, 7–14 cycles retained, gzip compression. Docker: `--log-opt max-size=50m --log-opt max-file=7` (or daemon-wide in `daemon.json`). Compliance regimes override retention upward — HIPAA requires ≥6 years, SOX 7 years of log retention: archive to cold storage, never satisfy these by keeping logs on-host
- **Impact:** Unbounded log growth fills host disk until the service itself fails to write — a self-inflicted outage with no external trigger.
- **Source:** logrotate/Docker logging docs; HIPAA/SOX retention requirements

## Config Hygiene

### DOP-40 [LOW] Ambiguous YAML Strings Are Quoted or Linted
Any YAML/front-matter string value containing `: ` (colon-space) mid-string is quoted, enforced by lint.
- **Detect:** Unquoted YAML scalars with embedded `: ` (titles, descriptions, commands); front-matter parsed differently than the author intended; no yamllint (or equivalent) in the gate.
- **Fix:** Quote every string value containing `: `; add a YAML linter to the local gate so the class is caught before any build runs — this error is invisible until something consumes the parsed value.
- **Impact:** An unquoted colon silently truncates or restructures the value — the build may pass while a title, description, or command ships half-parsed.
- **Source:** XR-108 — cross-project experience registry (2026).
