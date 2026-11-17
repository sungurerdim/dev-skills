# Rules: Dependency Management & Supply-Chain Provenance

Applies to all project types with a dependency manifest. Loaded for the `deps` scope.

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

## Supply-Chain Provenance

### DOP-17 [HIGH] Dependency Provenance & SCA
Beyond pinning (DOP-14): every dependency is real, vetted, and continuously scanned. ~19.7% of LLM-suggested packages are hallucinated; attackers pre-register the names ("slopsquatting").
- **Detect:**
  - No SCA / advisory scan in CI
  - A new package absent from the official registry, with near-zero downloads, or registered after the project started
  - A name one character off a popular package, or from the wrong ecosystem
  - Lockfile without integrity hashes
- **Fix:** Run SCA in CI (osv-scanner, Dependabot, Snyk, Trivy). Before adding a dependency, confirm it exists in the registry, predates the project, and has real downloads; reject near-miss / cross-ecosystem names. Commit lockfiles with integrity hashes.
- **Impact:** A hallucinated or slopsquatted package name gets installed with full code-execution trust the moment it resolves — the same trust a legitimate dependency earns only after years of scrutiny.
- **Source:** [CSA — Slopsquatting (2026)](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/); USENIX Security '25 (19.7% package hallucination)

### SEC-14 [HIGH] Dependency License Compliance Scanning
Every dependency's license is known, scanned automatically, and compatible with the project's distribution model.
- **Detect:**
  - No SBOM (SPDX/CycloneDX) generated and no automated license scanner (FOSSA, Snyk, `license-checker`, ScanCode) configured in CI/pre-commit
  - GPL/AGPL-licensed dependency present in a proprietary or permissively-licensed distribution with no compliance review recorded
  - LGPL dependency statically linked into proprietary code (dynamic linking required to avoid copyleft propagation)
  - Apache 2.0 dependency distributed without its NOTICE file; MIT/BSD dependency distributed without copyright/license text preserved
  - Large verbatim blocks of unknown provenance (often AI-generated) carrying third-party or copyleft code without attribution
- **Mech:** M (the license scanner's output when present)
- **Fix:** Generate and maintain an SBOM (SPDX or CycloneDX format); wire a license scanner into CI/pre-commit that fails the build on a disallowed license; use LGPL dependencies via dynamic linking only; preserve NOTICE/copyright/license files in every distribution; verify provenance of large verbatim blocks before merge; document any borderline license decision before merge.
- **Impact:** An unreviewed GPL/AGPL dependency in a proprietary build, or a statically-linked LGPL dependency, converts a routine install into a license violation discoverable by the rights-holder at any time, with remedies up to source disclosure or a distribution injunction.
- **Source:** [SPDX specification](https://spdx.dev/); [OpenChain ISO/IEC 5230](https://www.openchainproject.org/)
