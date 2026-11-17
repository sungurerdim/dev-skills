# CI — gate, dependencies, signing, release

A local gate (a git hook or one check command) counts as CI; no rule here assumes a hosted pipeline. Rules with `applies_when: ci∋github` read GitHub Actions workflows. Per-stack format, lint, type, test and audit commands: [toolchains.md](../toolchains.md).

## Gate

### DOP-01 [CRITICAL] No automated gate before merge
- **Detect:** no hosted pipeline and no local gate (pre-commit or pre-push hook, `make check`, a check script a hook calls); a gate that skips format, lint, type check (where the language has one) or test; local and hosted runs calling different commands or unpinned tool versions; a gate needing a tool a supported OS lacks (`make` on Windows); a CI opt-out that left workflows, badges or docs claiming checks still run.
- **Mech:** T `git ls-files | grep -E '^\.github/workflows/|^\.gitlab-ci\.yml$|^\.circleci/|^azure-pipelines\.yml$|^Jenkinsfile$|^bitrise\.yml$|^codemagic\.yaml$|^\.pre-commit-config\.yaml$|^lefthook\.ya?ml$|^\.husky/'` · `git config --get core.hooksPath` · `find .git/hooks -type f ! -name '*.sample'`
- **Fix:** one entry point runs the check-mode commands of toolchains.md in the order format → lint → type → test; the hook and any hosted pipeline call that same entry point (ds-gate installs one); tool versions pinned in a file the entry point reads (`.tool-versions`, `.nvmrc`, `.python-version`, `rust-toolchain.toml`). Dropping hosted CI: delete its workflows, badges and docs in one change and name the local gate in README or CONTRIBUTING.
- **Impact:** regressions merge unseen; a stale badge tells contributors checks ran when none did.
- **Source:** Fowler, "Continuous Integration"; Twelve-Factor X (dev/prod parity); DORA capabilities (continuous integration).

### DOP-04 [MEDIUM] Commit messages release tooling cannot read
- **Detect:** recent commit subjects without a Conventional Commits type while the project derives its changelog or version from commits or states the convention in its docs.
- **Mech:** T `git log -50 --no-merges --format=%s | grep -vE '^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: '`
- **Fix:** `type(scope): summary`, with `!` or a `BREAKING CHANGE:` footer for breaks; a commit-msg hook (commitlint or one regex) enforces it.
- **Impact:** release tooling picks the wrong version bump and the changelog misses changes.
- **Source:** Conventional Commits 1.0.0; Semantic Versioning 2.0.0.

### DOP-38 [MEDIUM] Generated file edited by hand or stale
- **Detect:** a committed generated file (`DO NOT EDIT`, `@generated`, SRI hashes, bindings, manifests) changed without its source or generator in the same commit, or no gate step that regenerates and diffs it.
- **Mech:** T `git grep -lIE 'DO NOT EDIT|@generated|[Aa]uto-?generated' -- ':!*.md'`
- **Fix:** the gate regenerates and fails on `git diff --exit-code`; a fix goes into the source or the generator.
- **Impact:** the next regeneration silently drops the hand edit; a stale hash or binding breaks production.
- **Source:** DRY / single source of truth; Go `go generate` convention ("Code generated … DO NOT EDIT."); Reproducible Builds (reproducible-builds.org).

### DOP-40 [LOW] YAML that does not parse as written
- **Detect:** YAML that fails to parse, usually an unquoted value containing `: ` or starting with `*`, `&`, `!`, `%` or `@`; no YAML check in the gate.
- **Mech:** S `git ls-files -z '*.yml' '*.yaml' | xargs -0 yamllint -d '{rules: {}}' -f parsable`
- **Fix:** quote such values; add `yamllint` to the gate.
- **Impact:** the build may pass while a title, description or command ships half-parsed.
- **Source:** Fail fast; YAML 1.2.2 specification (plain scalars); yamllint.

### DOP-50 [MEDIUM] Script unsafe to re-run, failing silently or over-granting
- **Detect:** a tracked setup, install, bootstrap or helper script (shell, Makefile recipe) that breaks or duplicates on a second run — `mkdir` without `-p`, `ln -s` without `-f`, a line appended (`>>`) to an rc, profile or config file with no check that it is already there, a user, key or resource created without an exists-check; a shell script without `set -e` (or `errexit`) that runs on after a failed step and exits 0; `chmod 777`, `a+w` or `o+w`.
- **Mech:** T `git grep -nIE '(^|[;&|[:space:]])mkdir[[:space:]]+[^-[:space:]]|(^|[;&|[:space:]])ln[[:space:]]+-s[[:space:]]|>>[[:space:]]*[^[:space:]]*(rc|profile|\.conf|config)([^[:alnum:]_]|$)' -- '*.sh' '*.bash' 'Makefile' '*.mk'` · `git grep -LE 'set -[a-z]*e|errexit' -- '*.sh' '*.bash'` · `git grep -nIE 'chmod[[:space:]]+(-R[[:space:]]+)?(0?777|a\+w|o\+w)' -- ':!*.md'`
- **Fix:** every step checks before it acts or uses its idempotent form (`mkdir -p`, `ln -sf`, append only when `grep -qxF` finds no such line, create-if-absent); `set -eu` at the top, plus `pipefail` where the shell has it; the narrowest mode that works (`755` directories, `644` or `600` files).
- **Impact:** the documented re-run after an error fails half-way or doubles every appended line; a silently failed step leaves a "successful" setup missing a piece; a world-writable file lets any local user replace what the script runs.
- **Source:** Fail fast; Idempotency; Least privilege; Bash Reference Manual, The Set Builtin (`errexit`); CWE-732.

## Coding agents

### DOP-15 [HIGH] Coding-agent tools and agent changes unchecked
- **Detect:** MCP servers or agent tools in committed config started unpinned (`npx -y pkg`, `uvx pkg`, `@latest`); agent config granting broad shell, network or credential access by default; tool output fed back to an agent as instructions; agent-opened changes to CI config, infrastructure, auth, secrets or dependencies merged without a human reading them; auto-merge on a protected branch.
- **Mech:** T `git grep -nIE '"(npx|uvx|bunx|pipx)"|@latest' -- '*mcp*.json' '.cursor/*' '.vscode/*.json' '.claude/*.json' '.continue/*'`
- **Fix:** pin every tool to a version and re-review on change; scope each tool to the task with no ambient secrets; approval prompts show the raw call; agent changes to CI, infrastructure, auth, secrets and dependencies get a human review; no auto-merge on protected branches.
- **Impact:** one crafted input to an over-privileged or silently updated tool exfiltrates data or runs code (EchoLeak CVE-2025-32711, CurXecute CVE-2025-54135).
- **Source:** Least privilege; OWASP Top 10 for Agentic Applications (2026); NVD CVE-2025-32711 and CVE-2025-54135.

## Dependencies

### DOP-06 [HIGH] Known-vulnerable dependencies or images
- **Detect:** the one home of dependency advisory scanning. The stack's audit (toolchains.md `dep audit` row, or `osv-scanner scan source -r .` for any lockfile) reports an advisory at HIGH or above, or no audit runs in the gate or release step; a built container image never scanned (`trivy image {image}`); host advisory alerts (RPO-12) left open. Audits query advisory databases over the network, so the scan below only finds where an audit is wired.
- **Mech:** T `git grep -nIE 'npm audit|pnpm audit|yarn (npm )?audit|pip-audit|govulncheck|cargo (audit|deny)|osv-scanner|bundle-?audit|composer audit|mix deps\.audit|dependencyCheck|list package --vulnerable|trivy|grype' -- ':!*.md'`
- **Fix:** run the audit in the gate or release step and fail on HIGH or CRITICAL with a fix available; upgrade, or record an accepted advisory with its reason and expiry in the tool's ignore file; rescan the shipped image on each release.
- **Impact:** a published exploit for a shipped dependency reaches every user of every deploy.
- **Source:** OWASP A03:2025 Software Supply Chain Failures; NIST SSDF (SP 800-218) PW.4, RV.1; OSV (osv.dev).

### DOP-10 [CRITICAL] Major upgrade merged without its migration
- **Detect:** a manifest change since {base} that crosses a major version of a dependency, SDK or toolchain (Android target SDK, Xcode minimum, language runtime); deprecation warnings from the build or analyzer left in place.
- **Mech:** T `git diff -U0 {base} -- '*package.json' '*pyproject.toml' '*Cargo.toml' '*go.mod' '*pubspec.yaml' '*Gemfile' '*composer.json' '*.csproj' '*build.gradle*' '*pom.xml' '*Package.swift' | grep -E '^[-+][^-+]'`
- **Fix:** read the changelog and migration guide, upgrade one major per change on its own branch, run the full gate, fix every deprecation the upgrade reports.
- **Impact:** a skipped migration step surfaces as a build failure or a runtime crash after release.
- **Source:** Semantic Versioning 2.0.0; each platform's migration guide.

### DOP-11 [HIGH] Dependencies drift with no update process
- **Detect:** dependencies a major version or more behind, or past end of life, with no update process: neither one update bot (Dependabot, Renovate) covering every ecosystem in the repo nor a written cadence; two general-purpose update bots on one repo. The outdated commands read the registry: `npm outdated`, `pip list --outdated`, `cargo outdated`, `go list -u -m all`, `dart pub outdated`, `bundle outdated`, `composer outdated`, `dotnet list package --outdated`. CocoaPods trunk becomes read-only on 2 Dec 2026: Pods projects plan the move to Swift Package Manager.
- **Mech:** T `git ls-files | grep -E '(^|/)(dependabot\.ya?ml|renovate\.json5?|\.renovaterc(\.json)?)$'`
- **Fix:** one bot, or one written cadence (each release), covering every ecosystem; patch and minor grouped, majors through DOP-10; hold a version published under 7 days unless it fixes an advisory (Renovate `minimumReleaseAge`); a human merges after the gate passes.
- **Impact:** the gap to current grows until one upgrade is a rewrite, and security fixes cannot be taken quickly.
- **Source:** Renovate docs; GitHub Docs, Dependabot version updates; NIST SSDF (SP 800-218) PW.4.

### DOP-13 [HIGH] Conflicting dependency versions forced together
- **Detect:** resolver conflicts or peer-dependency warnings, several versions of one transitive package, forced overrides (`dependency_overrides`, `overrides`, `resolutions`) with no reason or removal condition, coordinated libraries (Firebase, Compose, Spring) versioned one by one where a BOM exists.
- **Mech:** T `git grep -nE 'dependency_overrides|"overrides"|"resolutions"' -- '*pubspec.yaml' '*package.json'`
- **Fix:** a BOM or platform for coordinated libraries; every override carries its reason and the version that lets it go.
- **Impact:** forced versions build but fail at runtime where the two sides disagree.
- **Source:** Maven BOM and Gradle platforms docs; npm peer dependencies; Cargo resolver docs.

### DOP-14 [HIGH] Builds not reproducible from a lockfile
- **Detect:** an application without a committed lockfile, or with its lockfile in `.gitignore`; installs in CI, Dockerfiles or scripts that may rewrite the lockfile (`npm install`, `pnpm install` without `--frozen-lockfile`, `pip install -r` without hashes or a lock); lockfiles without integrity hashes. Libraries keep version ranges in the manifest and are not findings for that.
- **Mech:** T `git check-ignore --no-index package-lock.json pnpm-lock.yaml yarn.lock bun.lock poetry.lock uv.lock Pipfile.lock Cargo.lock go.sum Gemfile.lock composer.lock mix.lock pubspec.lock Package.resolved` · `git grep -nE '(npm|pnpm|yarn) install|pip install -r' -- '.github' '.gitlab-ci.yml' '*Dockerfile*' 'Makefile' '*.sh'`
- **Fix:** commit the lockfile; install with `npm ci`, `pnpm install --frozen-lockfile`, `uv sync --locked`, `pip install --require-hashes`, `cargo build --locked`.
- **Impact:** two builds of one commit pull different code; a compromised new release is installed silently.
- **Source:** Twelve-Factor; npm Docs (package-lock.json, npm ci); The Cargo Book (Cargo.lock); Go Modules Reference (go.sum); pip secure installs.

### DOP-17 [HIGH] New dependency not proven real, or resolvable from the wrong registry
- **Detect:** a dependency added since {base} that is absent from its registry, has near-zero downloads, was first published recently, is one character off a popular name or comes from another ecosystem (19.7% of LLM-suggested package names do not exist; attackers register them); a new or upgraded package adding install scripts (`preinstall`, `postinstall`, `prepare`); a publisher or source repository that changed between versions, or a missing attestation (`npm audit signatures`, PEP 740); unscoped internal package names, no private registry pinned for the internal scope, or installs that ignore the lockfile (dependency confusion). Registry checks need the network.
- **Mech:** M (the manifest diff since {base} plus registry metadata)
- **Fix:** before adding a package confirm it exists, predates the need and has real use; reject near-miss and cross-ecosystem names; disable install scripts by default (`ignore-scripts=true`, pnpm `onlyBuiltDependencies`) and allow them per package; scope internal packages (`@org/…`) and pin that scope to the private registry in `.npmrc` or `pip.conf`; frozen installs (DOP-14).
- **Impact:** a fake or hijacked package runs with full trust at install time on every developer machine and build.
- **Source:** USENIX Security 2025 (package hallucination, 19.7%); OWASP A03:2025; Birsan, "Dependency Confusion" (2021); npm provenance; PEP 740.

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
- **Impact:** a copyleft dependency found after release forces a source release or a rewrite of the parts that use it.
- **Source:** [SPDX specification](https://spdx.dev/); [OpenChain ISO/IEC 5230](https://www.openchainproject.org/)

## Signing and release

### DOP-08 [HIGH] App signing tied to one machine or a plaintext secret
applies_when: mobile≠none or platforms∋desktop or platforms∋ios or platforms∋android
- **Detect:** signing passwords in build files (`storePassword`, `keyPassword`) or tracked properties; signing that works on one developer machine only, with no written, repeatable path; no offline backup of the Android upload key and no Play App Signing; a macOS build distributed outside the App Store without notarization; a Windows binary or installer without an Authenticode signature. Key files in git are SEC-01.
- **Mech:** T `git grep -nIE 'storePassword|keyPassword|keyAlias|CODE_SIGN_IDENTITY|PROVISIONING_PROFILE|notarytool|signtool|codesign' -- ':!*.md'`
- **Fix:** passwords from the environment or the OS keychain; keys in a secret store with an offline backup; enrol in Play App Signing; one documented command signs and notarizes (`xcrun notarytool`) or Authenticode-signs (`signtool`) on any release machine — fastlane match or the CI secret store where CI builds.
- **Impact:** a lost upload key blocks every update; a leaked one lets someone else ship as you; the OS blocks or warns on unsigned desktop builds.
- **Source:** Apple Developer, Notarizing macOS software; Android Developers, Play App Signing; Microsoft Learn, SignTool; OWASP MASVS-CODE.

### DOP-18 [HIGH] Published binaries cannot be verified
applies_when: platforms∋cli or platforms∋desktop or deploy=docker
- **Detect:** release binaries, archives or images published without a checksum file and a signature (minisign, Sigstore cosign, GPG); where CI builds the release, no provenance attestation (`actions/attest-build-provenance` with `attestations: write` and `id-token: write`, or another SLSA provenance generator); release notes without a verify command.
- **Mech:** T `git grep -nIE 'sha256sum|shasum -a 256|SHA256SUMS|checksums\.txt|minisign|cosign|attest-build-provenance|gpg --detach-sign' -- ':!*.md'`
- **Fix:** the release step writes `SHA256SUMS`, signs it (minisign, or cosign keyless), publishes both beside the artifacts and states the verify command; CI-built releases add a provenance attestation (SLSA Build L2; L3 from an isolated reusable workflow).
- **Impact:** an artifact swapped on a compromised account, mirror or build step reaches users undetected.
- **Source:** SLSA v1.0 (Build track, Provenance); Sigstore cosign; minisign; GitHub Docs, Artifact attestations.

### DOP-21 [HIGH] Registry publish with a long-lived token
applies_when: platforms∋library or platforms∋cli
- **Detect:** a publish step authenticating with a stored token (`NODE_AUTH_TOKEN`, `.npmrc` `_authToken`, `TWINE_PASSWORD`, `CARGO_REGISTRY_TOKEN`) where the registry offers trusted publishing from CI; a local publish from an account without 2FA or with a token that never expires. npm classic tokens stopped working in Dec 2025 and granular write tokens last at most 90 days, so a stored npm token is also an availability bug.
- **Mech:** T `git grep -nIE 'NODE_AUTH_TOKEN|_authToken|TWINE_PASSWORD|PYPI_(API_)?TOKEN|CARGO_REGISTRY_TOKEN|GEM_HOST_API_KEY' -- ':!*.md'`
- **Fix:** CI publish: trusted publishing (OIDC, `id-token: write`) on npm (CLI ≥ 11.5.1), PyPI, crates.io and RubyGems, then delete the stored token; local publish: 2FA on the account and a short-lived, package-scoped token never written to the repo.
- **Impact:** a leaked publish token is a full package takeover for every downstream user.
- **Source:** Least privilege; npm Docs, Trusted publishing; PyPI Docs, Trusted Publishers; Rust Blog, crates.io development update (2025-07); RubyGems Guides, Trusted publishing.

### DOP-32 [HIGH] Release depends on memory
- **Detect:** releasing takes several hand-typed steps; the release path does not refuse a dirty tree, publishes without the gate, bumps the version by hand, or runs heavy checks after the action that triggers deploy (on push-to-deploy hosts the push is the deploy); "released" or "deployed" assumed from a successful push instead of observed (host build status, health endpoint version equal to the released commit); a hybrid (Capacitor) release path that runs `cap copy` after a dependency change or `cap sync` before the web build, so native plugin registration ships stale.
- **Mech:** T `git ls-files | grep -iE '(^|/)(release|publish|deploy)[^/]*\.(sh|py|js|mjs|ts)$|(^|/)(Makefile|justfile|Taskfile\.ya?ml)$'`
- **Fix:** one command: refuse a dirty tree → stop when nothing changed since the last tag → version from the changelog's Unreleased section (DOP-48) → run the gate once → build (hybrid: web build → `npx cap sync` → native build) → publish or deploy → poll the host until it reports the pushed commit, or fail loudly at a timeout → then tag. Heavy checks run before the triggering action; an emergency bypass is explicit and logged.
- **Impact:** each manual step is a release that can ship untested, unversioned or not at all while every marker says it shipped.
- **Source:** Fail fast; Humble and Farley, *Continuous Delivery* (deployment pipeline); DORA capabilities (deployment automation); Capacitor CLI, `sync` (copy plus update).

### DOP-48 [MEDIUM] Version disagrees across manifest, tag and changelog
- **Detect:** a versioned project whose manifest version, latest release tag and top changelog entry name different versions, or a tag with no changelog entry.
- **Mech:** T `git tag --sort=-v:refname | head -n 3` · `git grep -m1 -nE '^## ' -- CHANGELOG.md` · `git grep -nE '^version[[:space:]]*[=:]|"version"[[:space:]]*:|<Version>' -- package.json pyproject.toml Cargo.toml pubspec.yaml '*.csproj'`
- **Fix:** one source for the version (the manifest, or the changelog the release command reads); the release command writes the others and tags in one step.
- **Impact:** users and tools cannot tell which build they run or what changed in it.
- **Source:** DRY / single source of truth; Semantic Versioning 2.0.0; Keep a Changelog 1.1.0.

### DOP-49 [MEDIUM] No way back from a bad published release
applies_when: platforms∋library or platforms∋cli
- **Detect:** release docs or scripts with no step for withdrawing a broken version; a broken version deleted or unpublished (breaking every lockfile that pinned it) instead of yanked or deprecated.
- **Mech:** T `git grep -nIiE 'yank|deprecate|unpublish' -- '*.md' '*.sh' 'Makefile' 'justfile'`
- **Fix:** document the withdrawal beside the release command — `cargo yank --version {v}`, PyPI yank (PEP 592), `npm deprecate {pkg}@{v} "{reason}"`, `gem yank` — then ship a fixed patch release; never reuse a version number.
- **Impact:** a broken release keeps installing for every new user until someone finds out how to stop it.
- **Source:** Reversibility; PEP 592; The Cargo Book (cargo yank); npm Docs (npm deprecate); Semantic Versioning 2.0.0 (item 3).

## Hosted pipelines

### DOP-19 [HIGH] Workflows not linted for correctness and security
applies_when: ci∋github
- **Detect:** workflows with neither actionlint (syntax, expressions, embedded shell) nor zizmor (injection, excessive permissions, dangerous triggers, credential persistence) in the gate; third-party actions referenced by tag instead of a full commit SHA.
- **Mech:** T `actionlint` · `zizmor --offline .github/workflows` · `git grep -nE 'uses:[[:space:]]*[^.[:space:]][^@[:space:]]*@' -- .github | grep -vE '@[0-9a-f]{40}'`
- **Fix:** add both to the gate; pin actions by SHA with the tag in a comment and let the update bot (DOP-11) move them.
- **Impact:** a broken expression fails only at run time; an injectable step or a moved tag runs attacker code with the repo's token.
- **Source:** actionlint; zizmor; GitHub Docs, Security hardening for GitHub Actions (pin actions to a full-length commit SHA).

### DOP-20 [CRITICAL] `pull_request_target` runs untrusted code with secrets
applies_when: ci∋github
- **Detect:** a workflow on `pull_request_target`, or a `workflow_run` chained from one, that checks out the PR head and builds, installs or tests it.
- **Mech:** T `git grep -nE 'pull_request_target|workflow_run' -- .github/workflows`
- **Fix:** run PR code under `pull_request`; keep `pull_request_target` for metadata-only jobs that never check out or execute PR content.
- **Impact:** a fork PR exfiltrates repository secrets and publish rights; the March 2026 trivy-action compromise that backdoored LiteLLM on PyPI began this way.
- **Source:** Least privilege; GitHub Security Lab, "Preventing pwn requests"; zizmor audit `dangerous-triggers`.

### DOP-23 [HIGH] CI holds long-lived cloud keys or a broad token
applies_when: ci≠none
- **Detect:** long-lived cloud keys stored as CI secrets (`AWS_SECRET_ACCESS_KEY`, `AZURE_CLIENT_SECRET`, a GCP service-account JSON) where the provider supports OIDC federation; workflows with no `permissions:` block, so `GITHUB_TOKEN` keeps the broad default.
- **Mech:** T `git grep -nE 'AWS_SECRET_ACCESS_KEY|AZURE_CLIENT_SECRET|GOOGLE_CREDENTIALS|credentials_json' -- .github .gitlab-ci.yml .circleci azure-pipelines.yml` · `git grep -L -E '^permissions:' -- '.github/workflows/*.yml' '.github/workflows/*.yaml'`
- **Fix:** federate (AWS role assumption, Azure federated credentials, GCP Workload Identity Federation, GitLab `id_tokens`) and delete the stored keys; `permissions: contents: read` at the top, raised per job only where needed.
- **Impact:** a leaked stored key works until someone rotates it; a federated credential expires within the hour and is scoped to one role.
- **Source:** Least privilege; GitHub Docs, Security hardening with OpenID Connect; GitLab Docs, OpenID Connect in GitLab CI/CD.

### DOP-44 [HIGH] CI secrets can reach logs or outlive a leak
applies_when: ci≠none
- **Detect:** a step printing a secret or a value derived from it (base64, substring and concatenation defeat log masking); `set -x` or step debug logging on a job that holds secrets; an organization-level secret only one repo needs; long-lived secrets with no rotation note.
- **Mech:** T `git grep -nE 'set -x|ACTIONS_STEP_DEBUG|CI_DEBUG_TRACE|echo[^#]*secrets\.' -- .github/workflows .gitlab-ci.yml`
- **Fix:** never print secrets; mask every derived value (`::add-mask::`) before anything can print it; no trace logging on secret-holding jobs; the narrowest scope (environment over repository over organization); a rotation note for each secret that cannot move to OIDC (DOP-23).
- **Impact:** a logged secret is exposed to everyone who can read the log, and an unrotated one stays usable after an unnoticed leak.
- **Source:** Least privilege; GitHub Docs, Security hardening for GitHub Actions; CWE-532.

### DOP-41 [MEDIUM] CI minutes spent on work that need not run
applies_when: ci≠none
- **Detect:** dependency installs and image builds without a cache (setup actions without `cache:`, Docker builds without `cache-from`, `actions/cache` below v4); a monorepo running every job on every change with no affected-package filter; lint and shared tests on macOS runners, or macOS jobs not path-filtered to Apple code (macOS minutes bill at a multiple of Linux); a PR-blocking test job over about 15 minutes, unsharded.
- **Mech:** T `git grep -nE 'runs-on:[[:space:]]*macos|actions/cache@v[123]([^0-9]|$)|setup-(node|python|java|go)@|docker/build-push-action' -- .github/workflows`
- **Fix:** cache keyed on OS, lockfile hash and tool version; `cache-from`/`cache-to type=gha` for images; affected-only runs (`turbo --filter`, `nx affected`, path filters) with a full run before release; Linux for everything not Apple-specific; shard slow suites (Playwright `--shard`) and keep end-to-end runs off the PR path.
- **Impact:** CI time and cost grow with repo size instead of change size, and slow feedback teaches merging without waiting.
- **Source:** GitHub Docs, Caching dependencies and Actions runner pricing; Docker Docs, GitHub Actions cache backend; Fowler, "TestPyramid".

### DOP-43 [HIGH] Release chain waits on a `GITHUB_TOKEN` event
applies_when: ci∋github
- **Detect:** a workflow whose tag, release or push (release-please, semantic-release, changesets) should start another workflow, authenticated only with `GITHUB_TOKEN`; events created with that token start no new runs, so the follow-up never happens and nothing errors.
- **Mech:** T `git grep -nE 'release-please|semantic-release|changesets/action|gh release create|git push' -- .github/workflows`
- **Fix:** one workflow for both steps, an explicit `workflow_run` chain, or a GitHub App token for the triggering step.
- **Impact:** releases ship without their publish or deploy step, discovered only when someone looks.
- **Source:** GitHub Docs, Triggering a workflow from a workflow.

### DOP-47 [HIGH] Deploy workflow cancels itself or ships unreviewed
applies_when: ci∋github
- **Detect:** a deploy workflow with `cancel-in-progress: true` (a second push stops the first deploy halfway); a production job with no `environment:` or an environment with no protection; staging and production in one job with no separate gate.
- **Mech:** T `git grep -nE 'cancel-in-progress:[[:space:]]*true|environment:' -- .github/workflows`
- **Fix:** `cancel-in-progress: false` (queue) on deploys; production behind a protected environment or `workflow_dispatch`; staging may deploy on every push.
- **Impact:** a half-applied deploy leaves production mixed with no clean rollback point; any trigger, a bug included, ships to users.
- **Source:** GitHub Docs, Using concurrency and Managing environments for deployment.
