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
- Generates only files relevant to detected project type — no unnecessary boilerplate
- Respects existing files — only overwrites with explicit user confirmation
- Standalone. Uses blueprint when available to select scaffold template; asks user when absent.
- **Minimal liability:** only generates standard, well-known config patterns — no custom security code
- **Minimum dependencies:** scaffolded projects start with minimal deps, documented rationale for each
- **Maximum automation:** CI, linting, formatting, testing configured from the start
- FRC+DSC enforced.
- Minimize external dependencies — prefer stdlib and well-established minimal libraries.
- **Exempt from state protocol:** idempotent scaffolding — re-running on the same project naturally resumes because existing files are skipped. No `ds/audit/init.json` written.

## Arguments

| Flag | Effect |
|------|--------|
| `--type=<type>` | Project type: web, api, mobile, cli, library, monorepo, desktop |
| `--stack=<stack>` | Technology stack: next, react, vue, svelte, flutter, fastapi, express, go, rust |
| `--minimal` | Bare minimum structure only |
| `--full` | Full production structure (CI, Docker, testing, docs) |
| `--dry-run` | Show what would be created without writing files |

No flags → present interactive menu.

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

## Delegation

**Owns:** scaffolding, project-init, ci-bootstrap, editor-config | **Delegates:** none | **Receives:** none

## Execution Flow

Setup → Detect → Configure → Generate → Verify → [Needs-Approval] → Summary

### Phase 1: Setup

**Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → read for context; absent → proceed fresh.

**IDU:** Profile → Type + Stack, Project Map.Toolchain. Findings() → verify + use. Absent → own analysis.

1. `--type` and `--stack` provided → proceed directly
2. Working directory has existing files → scan for signals (package.json, pubspec.yaml, go.mod, Cargo.toml)
3. Empty directory or no signals → present interactive menu for type selection
4. Ask for stack choice within selected type
5. Ask: `--minimal` or `--full`? (default: full)

**Gate:** Project type and stack confirmed. Ambiguous → ask user. If fails → if the user does not respond to the type/stack prompt after two attempts, exit cleanly with "ds-init: ABORTED — project type required to proceed"; do not generate any files.

### Phase 2: Detect Existing Setup

1. Scan for existing config files (.eslintrc, tsconfig, Dockerfile, .github/workflows, etc.) → mark as SKIP.
2. Report: "Found N existing config files — these will be preserved."

**Gate:** Conflict list confirmed. User wants to overwrite specific files → confirm each. If fails → if the user does not respond to an overwrite confirmation prompt, default to SKIP for that file, announce the skip, and continue scanning; re-run the skill after resolving conflicts to regenerate skipped files.

### Phase 3: Generate Structure

Create project files following [references/rules-scaffold.md](references/rules-scaffold.md).

1. Create directory structure for selected type
2. Generate configuration files. Per-stack tool selection (use the primary tool for each detected stack):

   | Stack | Formatter | Linter | Type checker |
   |-------|-----------|--------|-------------|
   | node | prettier (or biome if present) | eslint (or biome if present) | tsc (when tsconfig.json) |
   | python | ruff format (or black) | ruff (or flake8 + pylint) | mypy or pyright |
   | go | gofmt | go vet + golangci-lint | (built-in) |
   | rust | rustfmt | clippy | (built-in) |
   | flutter / dart | dart format | dart analyze | (built-in) |
   | ruby | rubocop --format | rubocop | sorbet (if present) |
   | jvm | google-java-format / ktlint | spotbugs / detekt | (compiler) |
   | swift | swift-format | swiftlint | (compiler) |
   | dotnet | dotnet format | (built-in) | (compiler) |

   Generated files per stack:
   - Editor config: `.editorconfig`, `.vscode/settings.json` (optional)
   - Linter + formatter configs from the table above
   - TypeScript/type config: `tsconfig.json` (node), `pyproject.toml` `[tool.mypy]` (python), etc.
   - Git: `.gitignore` (comprehensive for stack)
   - Environment: `.env.example` with documented variables (never `.env` with real values)
3. Generate CI workflow:
   - Lint → Test → Build pipeline with `permissions: { contents: read }` and `concurrency` group
   - Branch protection suggestions
   - Cache configuration for dependencies (setup-node cache, actions/cache)
   - Release workflow with release-please (if `--full`)
   - SHA-pin every third-party action (e.g., `actions/checkout@<40-char-sha>`) — supply chain mitigation per [references/principles.md §5](references/principles.md). Tag references like `@v4` MUST NOT appear in generated workflows.
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

Generate independent files in parallel (configs, CI, Docker).

**Gate:** All files created. Verify no file conflicts. If fails → for each file that could not be created (permission error, write failure, unexpected conflict): skip that file, record it as `failed (write error)` in the generated list, surface the error with the file path, and continue generating the remaining files; re-run the skill after resolving permissions to generate the skipped files (idempotent — existing files are preserved).

### Phase 4: Post-Generate Verification

1. Verify all generated files syntactically valid (JSON, YAML).
2. Check `.gitignore` covers: `.env*`, `node_modules`/build artifacts, `coverage/`, OS/IDE files.
3. Verify `.env.example` has no real secrets.
4. Check CI workflow references correct paths and commands.
5. Twelve-Factor checks on generated artifacts ([references/principles.md §3](references/principles.md)): generated `Dockerfile` logs to stdout (no `--logfile=` paths), binds via `$PORT` env var (no hardcoded ports), runs as non-root `USER`, has `HEALTHCHECK`. Generated `docker-compose.yml` uses `restart: unless-stopped`, externalizes config via `environment:` from `.env`. Every CI workflow action is SHA-pinned (no `@v4` style tag references).

**Gate:** All verifications pass. Any fail → fix before summary. If fails → for each verification failure: fix the issue inline (e.g., correct YAML syntax, add missing `.gitignore` entry, remove hardcoded port), re-verify once; if the fix cannot be applied automatically (e.g., SHA-pinning requires network lookup), add a `# TODO: SHA-pin this action` comment in the generated file, mark it `partial`, and surface it as a HIGH finding in the summary — do not block summary output.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → any item left unresolved after user interaction: mark it `skipped (no decision)` and proceed to Summary; do not retry the prompt; re-run the skill to revisit skipped items.

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

**Gate:** Summary printed with generated file list and next steps. If fails → if any generated file is missing from the tree output, re-read the file list and add it; if totals do not balance (generated + skipped + failed ≠ total files attempted), assign unaccounted files to `skipped (accounting gap)` and re-emit as `WARN`; since ds-init is exempt from state protocol, re-run the skill to regenerate any failed files.

## Quality Gates

- Every generated config file is syntactically valid
- `.gitignore` covers all standard exclusions for selected stack
- `.env.example` contains only placeholder values, never real secrets
- CI workflow is a complete lint → test → build pipeline
- Generated README includes setup and run instructions
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: not applicable — exempt from state protocol (idempotent scaffolding, see Contract).

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
