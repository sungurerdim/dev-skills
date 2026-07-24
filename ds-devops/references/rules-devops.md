# Rules: CI/CD, Workflow & Dependency Management

Applies to all project types: web, API, CLI, library, mobile, monorepo.

| Section | Rules |
|---------|-------|
| **CI/CD & Workflow** | DOP-01–07 (1 CRITICAL, 6 HIGH) |
| **Code Signing** | DOP-08–09 (2 HIGH) |
| **Dependency Management** | DOP-10–14 (1 CRITICAL, 4 HIGH) |
| **Agent & Supply-Chain Security** | DOP-15–18 (4 HIGH) |
| **Workflow Security & Lint** | DOP-19–20 (1 CRITICAL, 1 HIGH) |
| **Registry Publishing** | DOP-21 (1 HIGH) |
| **Container & Cloud Auth Hardening** | DOP-22–23 (2 HIGH) |
| **Runner & Host Hygiene** | DOP-24–25 (2 MEDIUM) |
| **Observability & SLO** | DOP-26–29 (2 HIGH, 2 MEDIUM) |
| **Backup, DR & Resilience** | DOP-30–31 (1 HIGH, 1 MEDIUM) |
| **Release Automation** | DOP-32–35 (2 HIGH, 2 MEDIUM) |
| **CI Hygiene** | DOP-36 (1 MEDIUM) |
| **Tooling** | DOP-37 (1 MEDIUM) |
| **Build Hygiene** | DOP-38–39 (2 MEDIUM) |
| **Config Hygiene** | DOP-40 (1 LOW) |

## CI/CD & Workflow

### DOP-01 [CRITICAL] CI/CD Pipeline Presence
Every project must have automated CI/CD.
- **Detect:** No CI config files found (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`, `bitrise.yml`, `azure-pipelines.yml`, `codemagic.yaml`)
- **Fix:** Create CI pipeline with stages: format → analyze/lint → test → build. Platform-specific:
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
- **Impact:** Manual builds → inconsistent releases and missed quality checks
- **GitHub Actions (2025-2026):** Use reusable workflows (`uses: ./.github/workflows/ci.yml`) for DRY pipelines. Use OIDC auth (`permissions: id-token: write`) instead of long-lived secrets for cloud deploys. Use matrix builds for multi-version testing. Pin actions by SHA, not tag.
- **Source:** GitHub Actions Reusable Workflows docs, OIDC for GitHub Actions (github.blog 2023), CI/CD best practices (martinfowler.com)

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

---

## Code Signing

### DOP-08 [HIGH] Code Signing Automation
No manual signing. Signing must be automated in CI.
- **Detect:** Manual cert install. Certs on individual machines. Signing breaks on CI.
  - iOS: no Fastlane Match or equivalent. Manual provisioning profiles.
  - Android: keystore on developer machine, not in CI secrets.
- **Fix:**
  - iOS: Fastlane Match (git or cloud). Gemfile.lock committed.
  - Android: base64 keystore in CI secrets. `keystore.properties` in `.gitignore`.
- **Impact:** Manual signing blocks releases and creates single-point-of-failure
- **Note:** Applies to mobile and desktop projects only. Skip for web/API/CLI/library.
- **Source:** Apple Code Signing Guide, Android App Signing docs, Fastlane Match docs

### DOP-09 [HIGH] Signing Security
Signing credentials must not be in source code.
- **Detect:**
  - Keystore file committed to git
  - Signing passwords/keys in plain text config files
  - CI secrets referenced but not rotated
- **Fix:** Store signing credentials in CI secret manager. Reference via environment variables. Document rotation policy.
- **Impact:** Compromised signing credentials allow malicious distribution
- **Note:** Applies to mobile and desktop projects only.
- **Source:** OWASP Mobile Security

---

## Dependency Management

### DOP-10 [CRITICAL] Breaking Change Detection
Detect and plan for breaking changes in dependencies and platform SDKs.
- **Detect:**
  - Major version bumps in dependency updates (semver breaking changes)
  - Deprecated API usage flagged by analyzer/linter
  - Platform SDK migration requirements not addressed
  - Platform-specific signals:
    - Android: AGP major updates, `targetSdkVersion` bump requirements
    - iOS: Xcode version requirements, minimum deployment target bumps
    - Flutter: Dart SDK constraints, deprecated widget/API warnings
    - Node: major version bumps in core dependencies (React, Next, Express)
    - Python: deprecated stdlib modules, major framework updates
    - RN: New Architecture migration (Fabric/TurboModules), React version bumps
    - C#/.NET: .NET major version upgrades, deprecated APIs (`Obsolete` attribute)
    - Ruby: Ruby major version deprecations, Rails upgrade guides
    - PHP: PHP major version deprecations, Laravel/Symfony upgrade guides
    - Elixir: Elixir/OTP major version changes, Phoenix upgrade guides
    - C/C++: compiler standard upgrades (C++17→20→23), deprecated headers
    - Scala: Scala 2→3 migration, sbt version bumps
- **Fix:** Read changelog and migration guide before major updates. Create separate branch. Run full test suite before merging.
- **Impact:** Undetected breaking changes → build failures and runtime crashes
- **Source:** Semantic Versioning, platform migration guides

### DOP-11 [HIGH] Outdated Dependency Detection
Detect outdated dependencies. Update to latest compatible stable versions.
- **Detect:**
  - No dependency freshness check in CI
  - Dependencies more than 2 major versions behind
  - Platform commands:
    - Flutter: `dart pub outdated`
    - Node: `npm outdated` or `npx npm-check-updates`
    - Python: `pip list --outdated`
    - Go: `go list -u -m all`
    - Rust: `cargo outdated`
    - Java: gradle-versions-plugin
    - iOS: `pod outdated` (CocoaPods) or `swift package show-dependencies` (SPM)
    - C#/.NET: `dotnet list package --outdated`
    - Ruby: `bundle outdated`
    - PHP: `composer outdated`
    - Elixir: `mix hex.outdated`
    - C/C++: `conan list` or manual review of vcpkg ports
    - Scala: `sbt dependencyUpdates` (via sbt-updates plugin)
- **Fix:** Update to latest compatible stable versions. Prefer minor/patch. Major updates require testing. Automate with Renovate or Dependabot.
- **Impact:** Outdated deps accumulate security vulnerabilities and API incompatibilities
- **Note:** CocoaPods trunk goes read-only December 2, 2026 — plan SPM migration for iOS deps
- **Source:** Platform dependency tools, Renovate docs

### DOP-12 [HIGH] Dependency Policy Configuration
Automated dependency update tool must be configured.
- **Detect:**
  - No `.github/dependabot.yml` and no `renovate.json` / `.renovaterc`
  - Existing config doesn't cover all package ecosystems in project
  - No auto-merge policy for patch/minor updates
  - Both Dependabot version updates AND Renovate configured as general-purpose updaters on the same repo → MEDIUM "conflicting update bots"
- **Fix:** Configure Dependabot or Renovate. Cover all ecosystems. Set auto-merge for patch updates, manual review for major. Both bots present → split responsibility (Dependabot = security-fix PRs only, Renovate = routine version bumps, grouping, scheduling) or consolidate on one.
- **Impact:** Without automated updates, dependencies silently become outdated and vulnerable
- **Source:** Dependabot docs, Renovate docs

### DOP-13 [HIGH] Cross-Dependency Compatibility
Dependencies must be compatible with each other. Use BOM where available.
- **Detect:**
  - Version conflicts in dependency resolution
  - Multiple versions of same transitive dependency
  - SDK version requirements not met by dependencies
  - Platform patterns:
    - Flutter: `dependency_overrides` in pubspec.yaml
    - Node: peer dependency warnings in `npm ls`
    - Android: missing BOM usage for coordinated releases (Firebase BOM, Compose BOM)
    - Python: conflicting version constraints in requirements
    - iOS: `pod install` resolution conflicts
    - C#/.NET: package downgrade warnings in `dotnet restore`
    - Ruby: `bundle install` resolution conflicts, gemspec constraints
    - PHP: `composer install` resolution conflicts
    - Elixir: `mix deps.get` resolution conflicts
    - Rust: `cargo tree -d` showing duplicate dependencies
    - Scala: eviction warnings in sbt resolution
- **Fix:** Use BOM for coordinated releases. Use overrides only temporarily with TODO comment. Commit lockfiles.
- **Impact:** Dependency conflicts → build failures and unpredictable behavior
- **Source:** Maven BOM docs, Gradle Platform docs, npm peer dependency RFC, Cargo resolver docs

### DOP-14 [HIGH] Version Pinning
Dependencies should be pinned to specific versions. Lockfiles committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile in git (pubspec.lock, package-lock.json, yarn.lock, poetry.lock, Cargo.lock, go.sum, Gemfile.lock, composer.lock, mix.lock)
  - `.gitignore` excluding lockfiles
- **Fix:** Pin versions. Commit lockfiles. Remove lockfiles from `.gitignore`.
- **Impact:** Unpinned dependencies → non-reproducible builds and surprise breakage
- **Source:** npm lockfile docs, Yarn deterministic installs, Go Module Reference (go.dev), Cargo.lock docs

## Agent & Supply-Chain Security

### DOP-15 [HIGH] MCP & Agent Tool Security
The tool/MCP layer an agent uses is an attack surface. EchoLeak (CVE-2025-32711) exfiltrated Microsoft 365 Copilot data from a single crafted email; CurXecute (CVE-2025-54135) reached RCE in Cursor by steering the agent to write `.cursor/mcp.json` — the edit landed on disk even when the user clicked reject.
- **Detect:**
  - MCP servers/tools added without pinned versions
  - Tool output fed back into the agent as instructions rather than data
  - Ambient or over-broad credentials granted to a tool
  - Approval prompts showing a model-written prose summary instead of the raw tool call
  - AI-tool config dirs (`.cursor/`, `.continue/`, `**/mcp.json`) absent from `.gitignore`
- **Fix:** Pin MCP server/tool versions and re-review on change (rug-pull). Treat tool output as untrusted data, never instructions. Least-agency: scope each tool's permissions to the task, no ambient secrets. Approval prompts must show the raw tool name + parameters. Gitignore AI-tool config dirs.
- **Source:** [OWASP Agentic Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), [EchoLeak CVE-2025-32711](https://nvd.nist.gov/vuln/detail/CVE-2025-32711), [CurXecute CVE-2025-54135](https://nvd.nist.gov/vuln/detail/CVE-2025-54135)

### DOP-16 [HIGH] Human Review for Agent-Authored CI/Infra PRs
A PR opened by an autonomous agent gets human review before merge when it touches privileged surfaces, and never auto-merges to a protected branch.
- **Detect:**
  - Auto-merge enabled on protected branches
  - Agent/bot PRs touching `.github/workflows/` (or other CI config), infrastructure-as-code, auth, or secrets merged without human approval
  - Agent dependency-bump PRs auto-merged
- **Fix:** Require human review + branch protection for agent PRs touching CI/CD, IaC, auth, or secrets. Disable auto-merge on protected branches. Treat agent dependency-bumps as a supply-chain entry point — review before merge.
- **Source:** [Agent Autonomy in Open-Source PRs — 8,031 PRs (arXiv:2601.17413, 2026)](https://arxiv.org/abs/2601.17413)

### DOP-17 [HIGH] Dependency Provenance & SCA
Beyond pinning (DOP-14): every dependency is real, vetted, and continuously scanned. ~19.7% of LLM-suggested packages are hallucinated; attackers pre-register the names ("slopsquatting").
- **Detect:**
  - No SCA / advisory scan in CI
  - A new package absent from the official registry, with near-zero downloads, or registered after the project started
  - A name one character off a popular package, or from the wrong ecosystem
  - Lockfile without integrity hashes
- **Fix:** Run SCA in CI (osv-scanner, Dependabot, Snyk, Trivy). Before adding a dependency, confirm it exists in the registry, predates the project, and has real downloads; reject near-miss / cross-ecosystem names. Commit lockfiles with integrity hashes.
- **Source:** [CSA — Slopsquatting (2026)](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/); USENIX Security '25 (19.7% package hallucination)

### DOP-18 [HIGH] Build Provenance & Artifact Attestation
Beyond pinning inputs (DOP-01 action SHA-pin, DOP-14 dependency pin): the build *output* itself needs a verifiable, signed record of how it was produced (SLSA-style provenance) so a consumer can confirm the artifact came from the claimed CI run and source commit, not a tampered build.
- **Detect:** Release artifacts (binaries, container images, packages) published without a signed provenance/attestation record; no `actions/attest-build-provenance` (or equivalent SLSA provenance generator) step in the release job; attesting job lacks `attestations: write` + `id-token: write` permissions; consumers have no way to verify artifact-to-source-commit lineage.
- **Fix:** Add a build-provenance step to the release job (GitHub: `actions/attest-build-provenance`, generates a signed SLSA-style attestation tied to the workflow run) with `permissions: attestations: write` + `id-token: write`; publish the attestation alongside the artifact; document the verification command (`gh attestation verify <artifact> -R <org>/<repo>`, requires gh 2.49.0+) in release notes. Attestation alone = SLSA v1.0 Build Level 2; isolating the build in a reusable workflow reaches Build Level 3.
- **Impact:** Without signed provenance, a compromised build step or registry can substitute a malicious artifact and no one downstream can detect it.
- **Source:** [SLSA Provenance](https://slsa.dev/spec/v1.0/provenance), [GitHub Artifact Attestations](https://docs.github.com/en/actions/security-for-github-actions/using-artifact-attestations/using-artifact-attestations-to-establish-provenance-for-builds)

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

## Registry Publishing

### DOP-21 [HIGH] Registry Publish Auth Currency (Trusted Publishing / OIDC)
Release workflows publishing to package registries must use short-lived OIDC trusted publishing, not long-lived token secrets. npm classic tokens were fully revoked 9 Dec 2025 — a publish job still referencing one is broken, not just insecure; granular npm tokens now cap at a 90-day lifetime.
- **Detect:**
  - npm publish step authenticating via a stored token secret (`NODE_AUTH_TOKEN` / `.npmrc` `_authToken`) instead of trusted publishing — classic tokens no longer authenticate at all; granular tokens expire ≤90 days and rot silently in secrets
  - PyPI publish using `password:` / long-lived API token with `twine` instead of a Trusted Publisher
  - Publish job missing `permissions: id-token: write` when trusted publishing is intended
- **Fix:** npm — configure Trusted Publishing (OIDC, GA since 31 Jul 2025 for GitHub Actions + GitLab CI; requires npm CLI ≥ 11.5.1 and `id-token: write`); provenance attestations are generated automatically, no `--provenance` flag needed. PyPI — configure a Trusted Publisher and publish via `pypa/gh-action-pypi-publish` (≥ v1.11.0 auto-generates PEP 740 attestations). Remove the long-lived token from secrets after cutover.
- **Impact:** A leaked long-lived publish token = full package-takeover; OIDC tokens are per-run and unexfiltratable at rest. On npm the classic-token path is additionally a hard availability bug since Dec 2025.
- **Source:** npm Trusted Publishing GA (github.blog, 2025-07-31); npm classic-token revocation (2025-12-09); PyPI Trusted Publishers + PEP 740

## Container & Cloud Auth Hardening

### DOP-22 [HIGH] CI-Built Container Hardening
Images the pipeline builds or runs (builder images, job containers, published artifacts) meet the hardening baseline; production-image hardening is canonical in ds-deploy DEP-17.
- **Detect:**
  - CI job/builder containers or pipeline-published images FROM a full OS base, running as root, or referenced by mutable tag instead of digest
  - Pipeline builds a production image with no hardening check step (no lint/policy against the DEP-17 baseline: distroless/minimal, non-root, read-only fs, cap-drop, digest pin)
- **Fix:** Apply the DEP-17 baseline to every image the pipeline touches; add a CI policy/lint step (hadolint + policy rules) so a non-conforming image fails the build instead of shipping. Production-image specifics (K8s securityContext, runtime mounts) → ds-deploy DEP-17 (canonical, advisory-handoff: ds-deploy absent → apply the baseline inline from this rule)
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
- **Source:** Docker builder-prune docs; depot.dev cache-management guidance

### DOP-25 [MEDIUM] Log Rotation Defaults
Every unbounded log sink has rotation configured; retention follows compliance floor, not disk size.
- **Detect:**
  - Services writing log files with no `logrotate`/journald size limits
  - Docker daemon on default `json-file` driver without `max-size`/`max-file` options (container logs grow without bound)
- **Fix:** Production baseline: daily rotation, 7–14 cycles retained, gzip compression. Docker: `--log-opt max-size=50m --log-opt max-file=7` (or daemon-wide in `daemon.json`). Compliance regimes override retention upward — HIPAA requires ≥6 years, SOX 7 years of log retention: archive to cold storage, never satisfy these by keeping logs on-host
- **Source:** logrotate/Docker logging docs; HIPAA/SOX retention requirements

## Observability & SLO

### DOP-26 [HIGH] SLO + Error-Budget Release Gate
Critical user journeys have SLOs; exhausted error budget halts non-critical releases.
- **Detect:**
  - No SLO definition (doc/config) for the service's critical user journeys; dashboards missing RED panels (rate/errors/duration) per service or USE panels (utilization/saturation/errors) per resource
  - No error-budget policy naming a rolling/calendar window and what happens when the budget is spent
- **Fix:** Define SLIs/SLOs per critical journey with an explicit window; adopt an error-budget policy per the SRE Workbook template — Google's example: budget exhausted over the preceding four-week window → all changes and releases halt except P0/security fixes until back within SLO
- **Source:** Google SRE Workbook — Implementing SLOs, Error Budget Policy

### DOP-27 [HIGH] Burn-Rate Alerting
Paging alerts fire on error-budget burn rate, not raw error counts or static thresholds.
- **Detect:** alert rules built on static error-count/error-rate thresholds for SLO-covered services; single-window alerts that either page too late (slow burn) or flap (fast burn)
- **Fix:** Multi-window, multi-burn-rate alerts per SRE Workbook Ch.5 — page on fast burn (budget gone in hours), ticket on slow burn (budget gone in days); burn rate = speed of budget consumption relative to the SLO window
- **Source:** Google SRE Workbook — Alerting on SLOs

### DOP-28 [MEDIUM] OpenTelemetry Instrumentation Standard
New instrumentation goes through the OTel API, not vendor-proprietary SDKs.
- **Detect:** vendor-locked instrumentation SDKs in new code where OTel equivalents are GA (traces, metrics, and logs are all GA across major-language OTel SDKs; CNCF-graduated May 2026); stale OTel Collector versions
- **Fix:** Instrument via OpenTelemetry SDK + Collector; keep vendor choice at the exporter/backend layer so the backend stays swappable
- **Source:** CNCF OpenTelemetry graduation announcement (2026-05-21)

### DOP-29 [MEDIUM] Alert Actionability
Every page is actionable and carries a runbook; page volume is tracked.
- **Detect:** paging alerts with no runbook link; purely informational alerts routed to the pager instead of tickets/dashboards; no tracking of pages-per-shift
- **Fix:** Downgrade non-actionable pages to tickets/dashboards; attach a runbook link to every remaining page; bound and review page volume per on-call shift
- **Source:** Google SRE Workbook — On-Call

## Backup, DR & Resilience

### DOP-30 [HIGH] Backup & DR Posture (3-2-1-1-0)
Infra-level backups follow 3-2-1-1-0 with tested recovery; DR objectives are explicit. (Database-level backup/restore checks live in ds-backend's Database scope — this rule covers the infrastructure posture.)
- **Detect:**
  - Backup config with no immutable/air-gapped tier (object-lock/WORM): 3 copies, 2 media, 1 offsite, 1 immutable, 0 errors on recovery test
  - Backup infrastructure sharing credentials/network segment with production admin accounts — backups are an active ransomware target (Veeam-reported: 89% of surveyed orgs had backup repositories specifically targeted)
  - No explicit RPO/RTO per service tier; no dated log of a DR/failover drill
- **Fix:** Add an immutable storage tier; segment backup admin identities (separate credentials, MFA, ideally separate IdP); define RPO/RTO per tier and align backup frequency/replication to them; schedule recurring restore/failover drills and log pass/fail
- **Source:** 3-2-1-1-0 rule (Veeam et al.); ransomware backup-targeting reports

### DOP-31 [MEDIUM] Failure-Injection Readiness (advisory)
Resilience assumptions are exercised, not assumed — at minimum in pre-production.
- **Detect:** services with retry/timeout/failover logic that has never been exercised by any failure injection (no chaos/fault-injection config, no game-day/tabletop record)
- **Fix:** Start minimal: kill one instance/dependency in staging and observe whether timeouts, retries, and alerts behave as designed; record the result. Full chaos-engineering platforms are optional — one exercised failure beats ten documented assumptions. Advisory only — never a blocker
- **Source:** Principles of Chaos Engineering; SRE game-day practice

## Release Automation

### DOP-32 [HIGH] Single-Command Release Runs a Deterministic Gate Chain
The one-command release pipeline replaces human memory with deterministic gates at every step.
- **Detect:** Release scripts that skip dirty-tree checks, deploy unchanged code, bump versions manually, re-implement quality checks the hooks already own, or run the full heavy suite on every deploy regardless of cost.
- **Fix:** Chain the gates: reject a dirty working tree → skip deploy when nothing changed since the last release tag → derive the semver bump from the CHANGELOG's [Unreleased] section (no real content → skip the release entirely) → trigger the existing pre-push quality gate once instead of re-coding it → age-gate the heavy layer (full E2E, link-proofing, cross-repo drift) with a timestamp file (run when older than N days, not per-deploy) → build/deploy → verify live. Allow `--emergency` to bypass gates only during a real incident.
- **Impact:** Every gate the script owns is a failure class removed from human memory — unreleased-junk deploys, empty releases, and skipped quality checks stop depending on whoever runs the command.
- **Source:** XR-085 — cross-project experience registry (2026).

### DOP-33 [HIGH] Heavy Checks Run Before the Deploy-Triggering Action
Identify which action actually triggers deployment, and sequence heavy checks strictly before it.
- **Detect:** On push-equals-deploy hosts (static-page platforms, git-integrated deploys to a protected branch), heavy validation (build health, link check, fact drift) scheduled after push — i.e. after the deploy already started.
- **Fix:** Map the deploy trigger explicitly. Where push IS the deploy, run the heavy layer pre-push — the gate and the deploy collapse onto the same action, so nothing can run "between" them. Where a separate deploy step exists, gate→push→deploy is acceptable.
- **Impact:** Heavy checks sequenced after the trigger validate what production is already serving — every failure they catch is a live incident instead of a blocked push.
- **Source:** XR-087 — cross-project experience registry (2026).

### DOP-34 [MEDIUM] A Dormant Gate's First Real Run Expects Accumulated Failures
A local gate/build pipeline that hasn't genuinely run in a long time is assumed to hide multiple independent latent failures; its re-activation is itself validated as a first real run.
- **Detect:** A gate installed or reconfigured long ago, never since exercised end-to-end, treated as "known green"; surprise when its first genuine run fails in several unrelated ways.
- **Fix:** Treat setup or reactivation of any gate as a first-real-run event: execute it fully, expect a batch of independent findings (environment drift, moved paths, stale versions), and budget for fixing them before trusting the gate. Zero findings from a long-dormant gate is a signal the gate isn't actually checking anything.
- **Impact:** Teams that assume dormant gates are green ship through a gate that silently stopped working — the accumulated failures then surface in production instead of the pipeline.
- **Source:** XR-178 — cross-project experience registry (2026).

### DOP-35 [MEDIUM] Multi-Repo Releases: Thin Orchestrator, Repo-Owned Gates
When independent repos release in sequence from one top-level script, each repo owns its gated release; the orchestrator only invokes and reports.
- **Detect:** A top-level release script re-implementing per-repo checks; one repo's failure rolling back another's completed release; repos that can no longer release independently.
- **Fix:** Keep each repo's gated release script authoritative inside that repo; the cross-platform orchestrator calls them in order and aggregates a combined summary. Each repo carries independent success/failure — a downstream failure never unwinds an upstream completed release, and every repo stays independently releasable.
- **Impact:** Fat orchestrators become a second, drifting copy of every repo's release logic, and coupled rollbacks turn one repo's flake into a multi-product outage.
- **Source:** XR-020 — cross-project experience registry (2026).

## CI Hygiene

### DOP-36 [MEDIUM] A CI Opt-Out Is Applied Consistently Across Sibling Repos
Deciding against cloud CI is applied uniformly: workflow files, CI configs, badges, and doc sections are fully removed from every sibling repo — no half-CI residue.
- **Detect:** Some sibling repos with live workflows after the opt-out decision; dead CI badges; pre-commit configs referencing removed CI; docs describing a pipeline that no longer runs.
- **Fix:** Sweep all sibling repos in one pass: delete workflow files, badges, CI-referencing configs and doc sections; note the opt-out decision (and its local-gate replacement) once in each repo's docs.
- **Impact:** Half-removed CI is worse than either state — green-looking badges and stale workflows tell contributors checks ran when nothing did.
- **Source:** XR-177 — cross-project experience registry (2026).

## Tooling

### DOP-37 [MEDIUM] Orchestration Tooling Is Preinstalled on Every Target Platform
Task-runner/orchestration scripts are written in a tool already present on all platforms the team targets.
- **Detect:** Build/release orchestration requiring a tool absent by default on a supported platform (e.g. `make` on Windows); onboarding docs whose first step is installing the runner itself.
- **Fix:** Choose the runner from the intersection of default installs across target platforms (e.g. bash where Git-for-Windows is assumed, or the language runtime the project already requires); if a non-universal tool is genuinely warranted, gate it behind an explicit documented install step, not an assumption.
- **Impact:** A runner missing on one platform silently forks the team into "can run the automation" and "pastes commands from chat" — the second group ships the mistakes the automation existed to prevent.
- **Source:** XR-176 — cross-project experience registry (2026).

## Build Hygiene

### DOP-38 [MEDIUM] Generated Artifacts Are Never Hand-Edited; Regenerated and Verified at the Gate
Generated artifacts (compiled output, SRI hashes, cache manifests, template-derived files) are produced automatically at pre-commit and verified fresh before push — hand edits are forbidden.
- **Detect:** Manual edits inside generated files; generated outputs stale relative to their sources at push time; no gate step comparing regenerated output to the committed copy.
- **Fix:** Regenerate artifacts in the pre-commit hook; verify freshness (regenerate-and-diff) in the pre-push gate; treat any manual edit to a generated file as a gate failure pointing at the true source to change.
- **Impact:** A hand-edited artifact is overwritten by the next regeneration — the "fix" silently evaporates, and stale artifacts (wrong SRI hash, old manifest) break production in ways that look like caching voodoo.
- **Source:** XR-013 — cross-project experience registry (2026).

### DOP-39 [MEDIUM] Cross-Surface Facts Come From One Canonical File With a Drift Gate
A numeric/pricing fact living on multiple independently-deployed surfaces (backend config, client, marketing site) has one canonical facts file, documented source owners, and a zero-dependency drift check wired into the gate.
- **Detect:** The same limit/TTL/price/count hardcoded in two or more surfaces; no canonical facts file; no automated check comparing the fact file to source owners and rendered copies; derived indicators (discount %, savings) as static strings.
- **Fix:** Maintain one canonical facts file; document the owning source file per fact; render values through the template engine's data access wherever possible, and mark the genuinely untemplatable remainder (e.g. numbers spelled out in prose) as WIRED vs NOT-WIRED. Wire a zero-dependency drift script into pre-push (no-op when the full workspace isn't checked out) validating the facts file against owners and rendered copies. Compute derived indicators (discount/savings) from real values at runtime, floored so the displayed figure never exceeds the true one.
- **Impact:** Fact drift across surfaces means the marketing site sells limits the backend doesn't honor — a support and legal problem discovered by customers, not tests.
- **Source:** XR-012 — cross-project experience registry (2026).

## Config Hygiene

### DOP-40 [LOW] Ambiguous YAML Strings Are Quoted or Linted
Any YAML/front-matter string value containing `: ` (colon-space) mid-string is quoted, enforced by lint.
- **Detect:** Unquoted YAML scalars with embedded `: ` (titles, descriptions, commands); front-matter parsed differently than the author intended; no yamllint (or equivalent) in the gate.
- **Fix:** Quote every string value containing `: `; add a YAML linter to the local gate so the class is caught before any build runs — this error is invisible until something consumes the parsed value.
- **Impact:** An unquoted colon silently truncates or restructures the value — the build may pass while a title, description, or command ships half-parsed.
- **Source:** XR-108 — cross-project experience registry (2026).
