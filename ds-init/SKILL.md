---
name: ds-init
description: Project scaffolding — generate production-ready project structure for any stack. Use when starting a new project or bootstrapping a repo skeleton.
---

# /ds-init

New projects start with no CI, no test setup, no linting, and inconsistent structure. This skill scaffolds all of it from day one.

**Project Scaffolding** — Generate production-ready project structure for any stack.

## Triggers

- User runs `/ds-init`
- User asks to scaffold, bootstrap, or create a new project
- User says "set up a new project" or "initialize project structure"
- User starts a greenfield project

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "scaffold a new {framework} project" | "audit existing project for health" (→ ds-blueprint) |
| "create CI / Docker / test boilerplate from zero" | "deploy the app" (→ ds-deploy) |
| "initialize project structure for {type}" | "add a feature to existing app" (→ implement directly) |
| "bootstrap with sensible defaults" | "research which framework to pick" (→ ds-research) |

## Contract

**Dimensions:** none (carrier)

- Generates project structure, CI config, test setup, Docker stubs, editor config, env templates
- Detects intent (web / api / mobile / cli / library / monorepo) from user input or codebase signals
- Generates only files relevant to detected type — no unnecessary boilerplate
- Respects existing files — overwrites only with explicit user confirmation
- Standalone. Uses blueprint when available to select scaffold template; asks user when absent.
- Minimal liability + minimum dependencies + maximum automation: standard well-known config patterns, no custom security code, scaffolded projects start with minimal deps (rationale documented), CI/lint/format/test configured from day one. Prefer stdlib and well-established minimal libraries.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **Exempt from state protocol:** idempotent scaffolding — re-running on the same project naturally resumes because existing files are skipped. No `ds/audit/init.json`.

## Arguments

| Flag | Effect |
|------|--------|
| `--type={type}` | Project type: web, api, mobile, cli, library, monorepo, desktop |
| `--stack={stack}` | Technology stack: next, react, vue, svelte, flutter, fastapi, express, go, rust |
| `--minimal` | Bare minimum structure only |
| `--full` | Full production structure (CI, Docker, testing, docs) |
| `--dry-run` | Show what would be created without writing files |

No flags → up-front interactive menu covering every project type, each with a one-line what-it-does (no default — type is user-driven): "What type of project are you scaffolding?" — [Web App] React/Next.js/Vue/Svelte frontend / [API] REST/GraphQL backend service / [Mobile] Flutter/React Native mobile app / [CLI] command-line tool / [Library] reusable package/module / [Monorepo] multi-package workspace / (Cancel). A disambiguating flag (`--type`) skips the menu.

## Scopes

| Type | Core Structure | CI | Docker | Test Setup |
|------|---------------|----|----|-----------|
| web | `src/`, `public/`, `pages/` | lint + test + build | Multi-stage nginx | Jest/Vitest + Playwright |
| api | `src/routes/`, `src/services/` | lint + test + build | Multi-stage runtime | pytest/Jest + integration |
| mobile | `lib/features/`, `test/` | lint + test + build (AAB/IPA) | N/A | Unit + widget + integration |
| cli | `src/commands/`, `bin/` | lint + test + build | Single-stage | Unit + integration |
| library | `src/lib/`, `examples/` | lint + test + build + publish | N/A | Unit + integration |
| monorepo | `packages/`, `apps/` | per-package + affected detection | Per-package | Per-package + E2E |

## Delegation

**Owns:** scaffolding, project-init, ci-bootstrap, editor-config | **Delegates:** none | **Receives:** ds-ship → idea/spec-only/scaffold stage sequencing

## Execution Flow

Setup → Detect → Configure → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**IDU:** Profile → Type + Stack, Project Map.Toolchain. Findings() → verify + use. Absent → own analysis.

1. `--type` and `--stack` provided → proceed directly.
2. Working directory has existing files → scan for signals (`package.json`, `pubspec.yaml`, `go.mod`, `Cargo.toml`).
3. Empty directory or no signals → interactive type-selection menu.
4. Ask for stack choice within selected type.
5. Ask: `--minimal` or `--full`? (default: full).

**Gate:** Project type and stack confirmed. If fails → no response after two attempts → exit cleanly with "ds-init: ABORTED — project type required"; generate no files.

### Phase 2: Detect Existing Setup

1. Scan for existing config files (`.eslintrc`, `tsconfig`, `Dockerfile`, `.github/workflows`, etc.) → mark as SKIP.
2. Report: "Found {n} existing config files — these will be preserved."

**Gate:** Conflict list confirmed. If fails → no response to overwrite confirmation → default SKIP for that file, announce, continue scanning; re-run after resolving conflicts.

### Phase 3: Generate Structure

Per [references/rules-scaffold.md](references/rules-scaffold.md). Generate independent files in parallel.

1. **Directory structure** for selected type (see Scopes table above).
2. **Per-stack tool config** (primary tool for each stack):

   | Stack | Formatter | Linter | Type checker |
   |-------|-----------|--------|-------------|
   | node | prettier (or biome if present) | eslint (or biome if present) | tsc (when `tsconfig.json`) |
   | python | ruff format (or black) | ruff (or flake8 + pylint) | mypy or pyright |
   | go | gofmt | go vet + golangci-lint | built-in |
   | rust | rustfmt | clippy | built-in |
   | flutter / dart | dart format | dart analyze | built-in |
   | ruby | rubocop --format | rubocop | sorbet (if present) |
   | jvm | google-java-format / ktlint | spotbugs / detekt | compiler |
   | swift | swift-format | swiftlint | compiler |
   | dotnet | dotnet format | built-in | compiler |

3. **Generated files per stack:**
   - Editor config: `.editorconfig`, optional `.vscode/settings.json`
   - Linter + formatter configs (from table above)
   - Type config: `tsconfig.json` (node), `pyproject.toml [tool.mypy]` (python), etc.
   - Git: `.gitignore` (comprehensive per stack)
   - Environment: `.env.example` with documented variables — NEVER `.env` with real values

4. **CI workflow:**
   - Lint → Test → Build pipeline with `permissions: { contents: read }` and `concurrency` group
   - Branch protection suggestions
   - Cache configuration for deps (setup-node cache, actions/cache)
   - Release workflow with release-please (if `--full`)
   - SHA-pin every third-party action (`actions/checkout@<40-char-sha>`) — supply chain mitigation per [references/principles.md §5](references/principles.md). Tag references like `@v4` MUST NOT appear in generated workflows.

5. **Docker files** (if `--full` or API/web type):
   - `Dockerfile`: multi-stage build, non-root `USER`, `HEALTHCHECK`
   - `.dockerignore`: minimum `.git`, `node_modules`, `.env*`, `.vscode`, `coverage`, `tests`, `*.md`
   - `docker-compose.yml` for local development
   - `docker-compose.prod.yml` (if `--full`): `restart: unless-stopped`, resource limits, `127.0.0.1` port binding, log rotation

6. **Test setup:** test runner config + example test file (pattern demonstration) + coverage config.

7. **Documentation stubs:** `README.md` (project name, setup, scripts); `CONTRIBUTING.md` stub (if `--full`); `LICENSE` file prompt.

**Gate:** All files created. If fails → per-file write error: skip that file, record `failed (write error)` in generated list, surface the error, continue with remaining files; re-run after resolving permissions (idempotent — existing files preserved).

### Phase 4: Post-Generate Verification

1. All generated files syntactically valid (JSON, YAML).
2. `.gitignore` covers `.env*`, `node_modules`/build artifacts, `coverage/`, OS/IDE files.
3. `.env.example` has no real secrets.
4. CI workflow references correct paths and commands.
5. **Twelve-Factor checks** on generated artifacts ([references/principles.md §3](references/principles.md)): `Dockerfile` logs to stdout (no `--logfile=` paths), binds via `$PORT` env var (no hardcoded ports), runs as non-root `USER`, has `HEALTHCHECK`. `docker-compose.yml` uses `restart: unless-stopped`, externalizes config via `environment:` from `.env`. Every CI action is SHA-pinned.

**Gate:** All verifications pass. If fails → fix inline (correct YAML, add missing `.gitignore` entry, remove hardcoded port), re-verify once; if not auto-fixable (e.g., SHA-pin needs network lookup), insert `# TODO: SHA-pin this action` comment, mark `partial`, surface HIGH finding — do not block summary.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → forced binary re-prompt per item; no response → mark `skipped (no response)`, proceed.

### Phase 6: Summary

```
ds-init: {OK|WARN|FAIL} | Generated: {n} | Skipped: {n} | Failed: {n} | Total: {n}

{project-name}/
├── .github/workflows/ci.yml
├── .gitignore
├── .editorconfig
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── src/
│   └── ...
├── test/
│   └── example.test.{ext}
├── README.md
└── {config files}

Next steps:
1. Copy `.env.example` to `.env` and fill in values
2. Install dependencies: {install-command}
3. Run tests: {test-command}
4. Start development: {dev-command}
```

**Value Delivered:** 1-5 concrete bullets, real generations only. Example shapes (placeholders, not literal):

- `{n} config files generated — lint/format/typecheck run on every commit, no manual setup`
- `CI pipeline (lint → test → build) wired with SHA-pinned actions — supply chain hardening from day one`
- `Dockerfile with non-root USER + HEALTHCHECK — production-readiness baked into first image`
- `.env.example documented + .env in .gitignore — no secret ever lands in git history`

**Gate:** Summary printed with file list + next steps + Value Delivered. If fails → file missing from tree → re-read list and add; totals imbalanced (gen + skip + fail ≠ total) → assign unaccounted to `skipped (accounting gap)`, re-emit `WARN`; re-run skill to regenerate failed files.

## Quality Gates

- Every generated config file is syntactically valid
- `.gitignore` covers all standard exclusions for selected stack
- `.env.example` contains only placeholder values, never real secrets
- CI workflow is a complete lint → test → build pipeline
- Generated `README.md` includes setup + run instructions
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: not applicable — exempt from state protocol (idempotent scaffolding). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W16: every scaffolded dependency exists in its registry (non-trivial age + downloads) and is pinned in the lockfile; hallucinated or typosquat names rejected.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Unknown project type | Present type selection menu |
| Stack not recognized | List supported stacks, ask user to choose |
| File conflict detected | Show diff, ask: overwrite / skip / merge |
| Write permission denied | Report error, suggest checking permissions |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Non-empty directory | Scan existing files, only add missing pieces |
| Monorepo detected | Ask which package to scaffold, respect workspace config |
| Multiple stacks | Ask user to choose primary, note secondary |
| Custom stack not listed | Generate generic structure with user-specified conventions |

