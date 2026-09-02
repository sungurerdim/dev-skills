# Rules: Project Scaffolding

Rules for initial project structure, configuration, and tooling setup. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Structure** | SCF-01–04 (2 HIGH, 2 MEDIUM) | ~12 |
| **Configuration** | SCF-05–10 (3 HIGH, 1 MEDIUM, 2 LOW) | ~58 |
| **Stack Scaffold Commands** | reference table (Phase 3, `--stack`) | ~140 |
| **Generation Detail** | reference (Phase 3 steps 5-6) | ~160 |

---

## Structure

### SCF-01 [HIGH] Standard Directory Layout
Project follows platform-conventional directory structure. Reviewers and tools expect standard layouts.
- **Detect:**
  - Flat structure without source/test separation
  - Source files mixed with configuration files at root
  - Test files co-located without clear convention
  - Platform conventions violated (e.g., Go code not in cmd/internal/pkg)
- **Fix:** Apply platform-specific layout:
  - **Node/TypeScript:** src/ for source, test/ or __tests__/ for tests, dist/ for output
  - **Python:** src/package_name/ for source, tests/ for tests, pyproject.toml at root
  - **Go:** cmd/ for entrypoints, internal/ for private, pkg/ for public libraries
  - **Flutter/Dart:** lib/ for source, test/ for tests, assets/ for resources
  - **Rust:** src/ for source, tests/ for integration tests, benches/ for benchmarks
  - **TS/JS monorepo:** packages/ + apps/ workspace; scaffold new packages/components with Turborepo generators (`@turbo/gen`, Plop-based) instead of ad-hoc template cloning
- **Impact:** A non-standard layout confuses IDEs and tooling that assume the platform convention, and blocks generators (e.g. Turborepo) that require it.
- **Source:** Platform project templates, official documentation, [Turborepo generators](https://vercel.com/academy/production-monorepos/turborepo-generators)

### SCF-02 [HIGH] CI From Day One
CI pipeline configured in initial commit. Catches issues before they accumulate.
- **Detect:**
  - No .github/workflows/, .gitlab-ci.yml, or equivalent CI config
  - CI config exists but does not run on pull requests
  - CI missing lint, test, or build steps
- **Fix:** Add CI pipeline triggered on PR to default branch. Minimum steps: install dependencies, lint, type-check (if applicable), test, build. Start simple, expand later
- **Platform:**
  - GitHub: .github/workflows/ci.yml with on: pull_request
  - GitLab: .gitlab-ci.yml with merge_request_pipelines
- **Impact:** Without CI from day one, broken code merges silently and defects surface in production instead of on the PR.
- **Source:** GitHub Actions documentation

### SCF-03 [MEDIUM] Editor Config
Consistent formatting across editors regardless of individual developer settings.
- **Detect:**
  - No .editorconfig file in project root
  - Inconsistent indentation across files (tabs vs spaces mixed)
  - Different line endings across files
- **Fix:** Add .editorconfig with: root = true, indent_style (space or tab per platform convention), indent_size, end_of_line = lf, charset = utf-8, trim_trailing_whitespace = true, insert_final_newline = true
- **Impact:** Mixed indentation and line endings across contributors produce noisy diffs and merge conflicts unrelated to the actual change.
- **Source:** editorconfig.org

### SCF-04 [MEDIUM] Gitignore Completeness
OS artifacts, IDE files, build outputs, and dependency directories excluded from version control.
- **Detect:**
  - No .gitignore file
  - Missing entries for: OS files (.DS_Store, Thumbs.db), IDE (.idea/, .vscode/), dependencies (node_modules/, venv/), build output (dist/, build/, *.pyc)
  - Generated files tracked in git
- **Fix:** Use gitignore.io or github/gitignore templates for project stack. Combine OS + IDE + language + framework ignores. Verify with `git status` that no generated files are tracked
- **Impact:** Tracked build output, IDE files, or OS artifacts bloat the repo and cause spurious diffs and merge conflicts across every contributor's machine.
- **Source:** github/gitignore repository

---

## Configuration

### SCF-05 [HIGH] Dependency Lock
Lockfile committed from first install. → reproducible builds across environments.
- **Detect:**
  - Lockfile listed in .gitignore
  - Lockfile missing from repository
  - Lockfile not updated after dependency changes
- **Fix:** Commit appropriate lockfile:
  - **npm:** package-lock.json
  - **yarn:** yarn.lock
  - **pnpm:** pnpm-lock.yaml
  - **Python/Poetry:** poetry.lock
  - **Python/pip:** requirements.txt (pinned) or pip-compile output
  - **Rust:** Cargo.lock (for binaries; libraries may exclude)
  - **Flutter/Dart:** pubspec.lock
  - **Go:** go.sum
- **Impact:** Without a committed lockfile, the same manifest resolves to different dependency versions across machines and CI, turning "works on my machine" into an unreproducible build.
- **Source:** Package manager documentation, 12-Factor App

### SCF-06 [HIGH] Dependency Provenance
Every dependency added during scaffolding is real and trusted. → no hallucinated or typosquatted package enters the project. ~19.7% of LLM-suggested packages don't exist; attackers pre-register the names ("slopsquatting").
- **Detect:**
  - Package absent from the official registry, or with near-zero downloads / a registration date after the project started
  - A name one character off a popular package, or from the wrong ecosystem
  - Dependency added to the manifest but missing from the lockfile
- **Fix:** Before adding, confirm the package exists in the official registry, predates the project, and has real download history; pin it in the lockfile with an integrity hash. Reject near-miss / cross-ecosystem names; prefer the maintained, widely-used option.
- **Impact:** A hallucinated or typosquatted package becomes an unreviewed code-execution path the moment it installs — the fastest-growing AI-assisted supply-chain attack vector.
- **Note:** Verify licensing/pricing state at scaffold time too, never from memory — tools go stale within a training window (e.g., Atlas moved `atlas migrate lint` out of its free tier in October 2025).
- **Source:** [CSA — Slopsquatting (2026)](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/); USENIX Security '25 (19.7% package hallucination)

### SCF-07 [HIGH] Environment Template
.env.example documents all required environment variables with placeholder values. Real .env never committed.
- **Detect:**
  - .env file tracked in git (secrets exposed)
  - No .env.example or equivalent template
  - .env.example missing variables that code references
  - Real secrets in .env.example
- **Fix:** Create .env.example with every required variable using placeholder values (DATABASE_URL=postgresql://user:pass@localhost:5432/dbname). Add .env to .gitignore. Document which variables are required vs optional
- **Impact:** Missing or undocumented env vars cause silent misconfiguration at deploy time and force new contributors to reverse-engineer required settings from source.
- **Source:** 12-Factor App (III. Config)

### SCF-08 [MEDIUM] README From Day One
README communicates project purpose, quick start, and contribution guide. Projects with quality READMEs receive significantly more engagement.
- **Detect:**
  - No README.md or empty/default README
  - README missing: purpose statement, install instructions, run command, test command
  - README contains only auto-generated boilerplate
- **Fix:** Minimum sections: project purpose (1-2 sentences), prerequisites, install, run, test. Add contribution guide for open source. Keep concise — link to docs/ for details
- **Impact:** Projects with structured READMEs receive 4x more engagement
- **Source:** GitHub research on README impact

### SCF-09 [LOW] License File
LICENSE file in repository root. Required for open source; clarifies terms for private projects.
- **Detect:**
  - No LICENSE or LICENSE.md file in root
  - License referenced in README but file missing
  - License type incompatible with dependencies
- **Fix:** Add LICENSE file. Common choices: MIT (permissive, libraries), Apache-2.0 (permissive + patent grant), GPL-3.0 (copyleft), AGPL-3.0 (copyleft + network use). Match license to project goals and dependency licenses
- **Impact:** Without a LICENSE file, the default is "all rights reserved" — external contributors and downstream users have no legal basis to use, fork, or redistribute the code.
- **Source:** choosealicense.com, OSI approved licenses

### SCF-10 [LOW] AI Skill Directory in Repo
Projects built with AI coding agents check project-level agent skills into the repo (`.claude/skills/` or `.agents/skills/`) rather than keeping them as personal dotfiles.
- **Detect:**
  - Repo intended for AI-assisted development with no committed skill/agent-config directory
  - Skill definitions living only in individual developers' home directories
- **Fix:** Scaffold `.claude/skills/` (or `.agents/skills/`) with a README stub when the user confirms AI-assisted development; commit project-level skills there so the whole team shares them
- **Impact:** Skills kept only in individual dotfiles never reach teammates or CI, so the same AI-assisted conventions get reinvented — or silently violated — per developer instead of shared once.
- **Source:** [Superpowers marketplace guide (2026)](https://pasqualepillitteri.it/en/news/215/superpowers-claude-code-complete-guide), Developers Digest 2026 skills directory

---

## Stack Scaffold Commands

Detection signal, init command, and gate command chain per `--stack` value (SKILL.md Phase 3). Format/lint/type/test tool choice within each chain follows [../../core/toolchains.md](../../core/toolchains.md); an existing config or lockfile entry always wins over these defaults.

| Stack | Detection Signal | Init Command | Gate Command Chain |
|-------|-------------------|---------------|---------------------|
| next | `next` in package.json, or user selects | `npx create-next-app@latest` | `npx prettier --check . && npx eslint . && npx tsc --noEmit && npm test` |
| react | `react` + `vite`/`react-scripts` in package.json, or user selects | `npm create vite@latest -- --template react-ts` | `npx prettier --check . && npx eslint . && npx tsc --noEmit && npm test` |
| vue | `vue` in package.json, or user selects | `npm create vue@latest` | `npx prettier --check . && npx eslint . && npx vue-tsc --noEmit && npm test` |
| svelte | `svelte` in package.json, or user selects | `npx sv create` | `npx prettier --check . && npx eslint . && npx svelte-check && npm test` |
| astro | `astro.config.mjs`/`.ts`, `astro` in package.json, or user selects | `npm create astro@latest` | `npx astro check && npx eslint . && npm test` |
| flutter | `pubspec.yaml` with `flutter:`, or user selects | `flutter create .` | `dart format --output=none --set-exit-if-changed . && flutter analyze && flutter test` |
| expo | `app.json`/`app.config.js` with an `expo` key, `expo` in package.json, or user selects | `npx create-expo-app@latest` | `npx expo-doctor && npx tsc --noEmit && npm test` |
| fastapi | `fastapi` in requirements/pyproject, or user selects | `uv init` (adds `fastapi` + `uvicorn` next) | `ruff format --check . && ruff check . && pyright && pytest -q` |
| express | `express` in package.json, or user selects | `npm init -y && npm install express` | `npx prettier --check . && npx eslint . && npx tsc --noEmit && npm test` |
| hono | `hono` in package.json, or user selects | `npm create hono@latest` | `npx prettier --check . && npx eslint . && npx tsc --noEmit && npm test` |
| bun | `bun.lock`/`bun.lockb`/`bunfig.toml`, or user selects | `bun init -y` | `npx biome check . && bunx tsc --noEmit && bun test` |
| go | `go.mod`, or user selects | `go mod init {module}` | `test -z "$(gofmt -l .)" && go vet ./... && go build ./... && go test ./...` |
| rust | `Cargo.toml`, or user selects | `cargo init` | `cargo fmt --check && cargo clippy -- -D warnings && cargo check && cargo test` |

**Bun, Hono, Astro, Expo notes:** Bun is both a package manager (detected via lockfile per `../../core/toolchains.md`) and, under `--stack=bun`, a standalone runtime project scaffolded by `bun init`. Hono targets multiple runtimes (Node, Bun, Cloudflare Workers, Deno) — `create-hono` prompts for the target; the gate chain above assumes the Node/TS default, substitute `bun test` when the Bun target is chosen. Astro's `astro check` is the framework's own type/diagnostic checker, run ahead of the generic TypeScript check. Expo's `expo-doctor` is the framework's own project-health checker; Expo/React Native projects default to Jest, so `npm test` resolves to `jest` once scaffolded.

---

## Generation Detail

Exact shape of the CI workflow and Docker files SKILL.md Phase 3 generates (steps 5-6).

**CI workflow** `[--full]`:
- Lint → Test → Build pipeline with `permissions: { contents: read }` and a `concurrency` group
- Branch protection suggestions
- Cache configuration for deps (setup-node cache, actions/cache)
- Release workflow with release-please
- SHA-pin every third-party action (`actions/checkout@<40-char-sha>`) — supply chain mitigation per [../../core/principles.md §5](../../core/principles.md). Tag references like `@v4` MUST NOT appear in generated workflows.

**Docker files** (if `--full` or API/web type):
- `Dockerfile`: multi-stage build, non-root `USER`, `HEALTHCHECK`
- `.dockerignore`: minimum `.git`, `node_modules`, `.env*`, `.vscode`, `coverage`, `tests`, `*.md`
- `docker-compose.yml` for local development
- `docker-compose.prod.yml` (if `--full`): `restart: unless-stopped`, resource limits, `127.0.0.1` port binding, log rotation
