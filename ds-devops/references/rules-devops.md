# Rules: CI/CD, Workflow & Dependency Management

Rules for audit/fix modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

Applies to all project types: web, API, CLI, library, mobile, monorepo.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **CI/CD & Workflow** | DOP-01–07 (1 CRITICAL, 6 HIGH) | ~16 |
| **Code Signing** | DOP-08–09 (2 HIGH) | ~89 |
| **Dependency Management** | DOP-10–14 (1 CRITICAL, 4 HIGH) | ~115 |

---

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
- **Impact:** Manual builds cause inconsistent releases and missed quality checks
- **Source:** Industry standard CI/CD practices

### DOP-02 [HIGH] Quality Gate Coverage
CI must include format, lint/analyze, test, and build stages.
- **Detect:** CI config exists but missing stages. Check for presence of format, lint/analyze, test, and build commands in workflow files.
- **Fix:** Add missing stages. Run in order: format → lint → test → build. Fail pipeline on any stage failure.
- **Impact:** Missing quality gates allow regressions to reach production
- **Source:** CI/CD best practices

### DOP-03 [HIGH] CI/Local Parity
CI checks should match local development checks.
- **Detect:**
  - CI runs different lint/test commands than package.json scripts or Makefile targets
  - CI has checks not runnable locally (or vice versa)
  - CI uses different tool versions than local (no `.tool-versions`, `.nvmrc`, or version pinning)
- **Fix:** Align CI and local commands. Use `.tool-versions` or `.nvmrc` for version pinning. Provide `make ci` or equivalent that mirrors CI exactly.
- **Impact:** "Works on my machine" issues, CI-only failures block development
- **Source:** DevOps best practices

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
- **Source:** Industry standard

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
- **Fix:** Configure required status checks for lint, test, and build jobs on the default branch.
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
- **Source:** Platform deployment guides

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
- **Impact:** Undetected breaking changes cause build failures and runtime crashes
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
  - Existing config doesn't cover all package ecosystems in the project
  - No auto-merge policy for patch/minor updates
- **Fix:** Configure Dependabot or Renovate. Cover all ecosystems. Set auto-merge for patch updates, manual review for major.
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
- **Impact:** Dependency conflicts cause build failures and unpredictable behavior
- **Source:** Platform dependency management docs

### DOP-14 [HIGH] Version Pinning
Dependencies should be pinned to specific versions. Lockfiles committed.
- **Detect:**
  - Unpinned versions: `^`, `~`, `latest`, `>=` without upper bound
  - Missing lockfile in git (pubspec.lock, package-lock.json, yarn.lock, poetry.lock, Cargo.lock, go.sum, Gemfile.lock, composer.lock, mix.lock)
  - `.gitignore` excluding lockfiles
- **Fix:** Pin versions. Commit lockfiles. Remove lockfiles from `.gitignore`.
- **Impact:** Unpinned dependencies cause non-reproducible builds and surprise breakage
- **Source:** Dependency management best practices
