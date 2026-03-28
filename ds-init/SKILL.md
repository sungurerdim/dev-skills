# /ds-init

New projects start with no CI, no test setup, no linting, and inconsistent structure. This skill scaffolds all of it from day one.

**Project Scaffolding** — Generate production-ready project structure for any stack.

## Triggers

- User runs `/ds-init`
- User asks to scaffold, bootstrap, or create a new project
- User asks "set up a new project" or "initialize project structure"
- User starts a greenfield project

## Contract

- Generates project structure, CI config, test setup, Docker stubs, editor config, env templates
- Detects intent (web app, mobile app, API, CLI, library, monorepo) from user input or codebase signals
- Generates only files relevant to the detected project type — no unnecessary boilerplate
- Respects existing files — only overwrites with explicit user confirmation
- Fully functional standalone — zero dependency on other skills. When blueprint profile exists, uses project type and stack to select scaffold template. When absent, asks user.
- **Minimal liability:** only generates standard, well-known config patterns — no custom security code
- **Minimum dependencies:** scaffolded projects start with minimal deps, documented rationale for each
- **Maximum automation:** CI, linting, formatting, testing configured from the start
- Every finding receives a disposition in the summary — zero silent drops (FRC)
- Minimize external dependencies — prefer stdlib and well-established minimal libraries.

## Arguments

| Flag | Effect |
|------|--------|
| `--type=<type>` | Project type: web, api, mobile, cli, library, monorepo, desktop |
| `--stack=<stack>` | Technology stack: next, react, vue, svelte, flutter, fastapi, express, go, rust |
| `--minimal` | Bare minimum structure only |
| `--full` | Full production structure (CI, Docker, testing, docs) |
| `--dry-run` | Show what would be created without writing files |

Without flags: present interactive menu to the user.

**Interactive menu (no flags):**
```
What type of project are you scaffolding?
- [Web App] — React/Next.js/Vue/Svelte frontend
- [API] — REST/GraphQL backend service
- [Mobile] — Flutter/React Native mobile app
- [CLI] — Command-line tool
- [Library] — Reusable package/module
- [Monorepo] — Multi-package workspace
```

## Scopes

| Type | Core Structure | CI | Docker | Test Setup |
|------|---------------|----|----|-----------|
| web | src/, public/, pages/ | lint + test + build | Multi-stage nginx | Jest/Vitest + Playwright |
| api | src/routes/, src/services/ | lint + test + build | Multi-stage runtime | pytest/Jest + integration |
| mobile | lib/features/, test/ | lint + test + build (AAB/IPA) | N/A | Unit + widget + integration |
| cli | src/commands/, bin/ | lint + test + build | Single-stage | Unit + integration |
| library | src/lib/, examples/ | lint + test + build + publish | N/A | Unit + integration |
| monorepo | packages/, apps/ | per-package + affected detection | Per-package | Per-package + E2E |

## Execution Flow

Setup → Detect → Configure → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**Goal:** Determine project type and stack.

**Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, read findings for context on existing project state. If absent, proceed with fresh scaffolding.

**Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Type + Stack** → use as default project type suggestion
   - **Project Map.Toolchain** → pre-configure detected tools in generated configs

1. If `--type` and `--stack` provided, proceed directly
2. If working directory has existing files, scan for signals (package.json, pubspec.yaml, go.mod, Cargo.toml)
3. If empty directory or no signals, present interactive menu for type selection
4. Ask for stack choice within the selected type
5. Ask: `--minimal` or `--full` structure? (default: full)

**Gate:** Project type and stack confirmed. If ambiguous → ask user.

### Phase 2: Detect Existing Setup

**Goal:** Avoid overwriting existing configuration.

1. Scan for existing config files (.eslintrc, tsconfig, Dockerfile, .github/workflows, etc.)
2. For each detected file, mark as SKIP (preserve existing)
3. Report: "Found N existing config files — these will be preserved"

**Gate:** Conflict list confirmed. If user wants to overwrite specific files → confirm each.

### Phase 3: Generate Structure

**Goal:** Create project files.

1. Create directory structure for selected type
2. Generate configuration files:
   - Editor config: `.editorconfig`, `.vscode/settings.json` (optional)
   - Linting: language-appropriate linter config
   - Formatting: language-appropriate formatter config
   - TypeScript/type config: `tsconfig.json`, `pyproject.toml`, etc.
   - Git: `.gitignore` (comprehensive for stack)
   - Environment: `.env.example` with documented variables (never `.env` with real values)
3. Generate CI workflow:
   - Lint → Test → Build pipeline with `permissions: { contents: read }` and `concurrency` group
   - Branch protection suggestions
   - Cache configuration for dependencies (setup-node cache, actions/cache)
   - Release workflow with release-please (if `--full`)
   - Comment recommending SHA-pinned third-party actions
4. Generate Docker files (if `--full` or API/web type):
   - `Dockerfile` with multi-stage build, non-root `USER`, `HEALTHCHECK`
   - `.dockerignore` (minimum: `.git`, `node_modules`, `.env*`, `.vscode`, `coverage`, `tests`, `*.md`)
   - `docker-compose.yml` for local development
   - `docker-compose.prod.yml` (if `--full`): `restart: unless-stopped`, resource limits, `127.0.0.1` port binding, log rotation
5. Generate test setup:
   - Test runner configuration
   - Example test file demonstrating patterns
   - Coverage configuration
6. Generate documentation stubs:
   - `README.md` with project name, setup instructions, scripts
   - `CONTRIBUTING.md` stub (if `--full`)
   - `LICENSE` file prompt

Files are generated in parallel where independent (configs, CI, Docker).

**Gate:** All files created. Verify no file conflicts.

### Phase 4: Post-Generate Verification

**Goal:** Ensure generated structure is valid.

1. Verify all generated files are syntactically valid (JSON parseable, YAML valid)
2. Check `.gitignore` covers: `.env*` (glob), `node_modules`/build artifacts (`dist/`, `build/`, `.next/`), `coverage/`, OS files, IDE files
3. Verify `.env.example` contains no real secrets (only placeholder values)
4. Check CI workflow references correct paths and commands

**Gate:** All verifications pass. If any fail → fix before summary.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 6: Summary

Output generated file list with tree structure:

```
ds-init: {OK|WARN|FAIL} | Generated: N | Skipped: N | Failed: N | Total: N

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
1. Copy .env.example to .env and fill in values
2. Install dependencies: {command}
3. Run tests: {command}
4. Start development: {command}
```

**Gate:** Summary printed with generated file list and next steps.

## Quality Gates

- Every generated config file is syntactically valid
- `.gitignore` covers all standard exclusions for the selected stack
- `.env.example` contains only placeholder values, never real secrets
- CI workflow is a complete lint → test → build pipeline
- Generated README includes setup and run instructions
- Verify every import, API, or dependency exists before using — state "not verified" rather than assuming. _(W1)_
- Only modify files required by the current task — leave unrelated code untouched. _(W3)_
- After context gap, re-read source files and progress artifacts before modifying. _(W4)_

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
