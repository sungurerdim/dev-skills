# /ds-blueprint

**Project Health System** — Profile-based assessment, transformation, and progress tracking.

## Triggers

- User runs `/ds-blueprint`
- User asks to assess project health, quality, or overall status
- User asks for a project profile, health score, or quality dashboard
- User asks "how healthy is this project" or "what should I improve"
- First time working on a new project (suggest profile creation)

## Contract

- Fully functional standalone. Produces `.findings.md` for other skills to consume.
- Scores project health across 9 dimensions — signal counting, not file:line finding lists
- Only modifies the instruction file's blueprint profile section — never touches other content
- Suggests next steps but does NOT invoke other skills or fix code directly

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All phases, no questions, single-line summary |
| `--preview` | Analyze + dashboard, no changes |
| `--init` | Profile creation/refresh only (no analysis) |
| `--refresh` | Re-scan profile (decisions preserved) |
| `--scope=X` | Specific area: stack, deps, dx, structure, code, architecture, docs, memory, all |

Without flags: present mode selection to the user.

## Profile Storage

Profile embedded in the project's AI instruction file between `## Blueprint Profile` and `## End Blueprint Profile` heading markers. Markdown headings are universally preserved by every tool — no risk of being stripped during processing.

**Instruction file detection** — check in order, use the first match:

| File | Tool |
|------|------|
| `CLAUDE.md` | Claude Code |
| `.cursorrules` | Cursor |
| `.cursor/rules/*.md` | Cursor (rules directory) |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurfrules` | Windsurf |
| `.aider.conf.yml` | Aider |

If none found: create the most common one for the platform, or ask the user which tool they use.

**Profile format:**

```markdown
## Blueprint Profile

**Project:** {name} | **Type:** {type} | **Stack:** {stack} | **Target:** {quality}

### Config
- **Priorities:** {list}
- **Constraints:** {list}
- **Data:** {data types} | **Regulations:** {if applicable}
- **Audience:** {audience} | **Deploy:** {deploy method}

### Project Map
Entry: {entry point} -> {framework}
Modules: {module -> role mapping}
External: {external dependencies}
Toolchain: {tools} | {CI} | {container}

### Ideal Metrics
| Metric | Target |
|--------|--------|
| Coupling | {value} |
| Cohesion | {value} |
| Complexity | {value} |
| Coverage | {value} |

### Current Scores
| Dimension | Score | Status |
|-----------|-------|--------|
| Security & Privacy | {n} | {OK/WARN} |
| Code Quality | {n} | {OK/WARN} |
| Architecture | {n} | {OK/WARN} |
| Performance | {n} | {OK/WARN} |
| Resilience | {n} | {OK/WARN} |
| Testing | {n} | {OK/WARN} |
| Stack Health | {n} | {OK/WARN} |
| DX | {n} | {OK/WARN} |
| Documentation | {n} | {OK/WARN} |
| Overall | {n} | {OK/WARN} |

## End Blueprint Profile
```

**Read/write rules:**
- Only modify content between `## Blueprint Profile` and `## End Blueprint Profile` headings — never touch anything outside them
- If instruction file exists but has no profile headings: run deduplication check (see below), then append profile section
- If instruction file does not exist: create it with profile section only
- Other skills read profile by searching for `## Blueprint Profile` heading in known instruction file locations
**Deduplication on inject:**

Deduplicate findings by file:line — same issue within 10 lines → merge, keep highest severity.

## Execution Flow

Discovery → [Init Flow] → Assess → Consolidate → Dashboard → [Suggest] → Update Profile → Summary

### Phase 1: Discovery [PARALLEL]

1. **Mode selection.** If no flags provided, ask the user:
   - **Full Analysis** — assess all dimensions, score, dashboard, suggest next steps
   - **Preview Only** — analyze + dashboard, no changes
   - **Init Profile** — create/refresh project profile only
   - **Refresh Profile** — re-scan profile, preserve decisions
2. Recovery check: if progress artifact exists from prior run, ask: Resume / Start fresh (--auto: resume silently)
3. Search for `## Blueprint Profile` heading in known instruction files (see Profile Storage detection table).
4. Detect project using three-step process from [references/detection.md](references/detection.md):
   - Step 1: Identify stack from manifest files (pubspec.yaml, package.json, go.mod, etc.)
   - Step 2: Determine project type from secondary signals (framework deps, config files, directory structure)
   - Step 3: Note supplementary stacks (Docker, shell scripts, CI platform, task runners)
   - Also detect: toolchain, tests, data sensitivity, git status

**Decision tree:**
1. Profile exists AND not --init/--refresh: Phase 3 (incremental)
2. Profile exists AND --refresh: Phase 2 (re-ask, preserve decisions)
3. No profile AND --init: Phase 2 (create profile, stop)
4. No profile AND not --init: Phase 2 (create profile, ask to continue)

### Phase 2: Init Flow (no profile OR --init/--refresh)

Ask the user two sets of questions:

**Project Identity:**
- What category best describes this project? (auto-detected type shown, options: Frontend, Backend, Developer Tool, Infrastructure)
- What quality level? (Prototype, MVP, Production, Enterprise)
- What kind of data does it handle? (Personal info, Sensitive data, Auth credentials, No sensitive data)

**Strategy:**
- Focus areas for improvement? (Security, Code Quality, Architecture, Documentation)
- Constraints? (Keep framework, Don't break public APIs, No new dependencies, No restrictions)
- Who uses this project? (Public users, Internal team, Other developers, Local/undecided)

**--auto Mode Defaults:**

| Question | Default |
|----------|---------|
| Project type | Auto-detected |
| Quality | Production |
| Data | Search for PII/credential patterns |
| Priorities | Security + Code Quality |
| Constraints | Keep framework/language |
| Audience | Auto-detect (Dockerfile → container, CI → cloud, else local) |
| Deployment | Auto-detect from Docker/cloud/serverless signals |

Write profile to the detected instruction file (see Profile Storage). Calculate ideal metrics from `references/weights.md` based on detected project type. Quality-level descriptions in [references/quality-levels.md](references/quality-levels.md).

### Phase 3: Assess (scan, record, score — don't fix)

Blueprint scans the **entire codebase** and records every finding with file:line to `.findings.md`. It scores dimensions from these findings but does NOT fix anything. Other skills read `.findings.md` and handle fixes — this eliminates duplicate analysis.

**Completeness requirement:** Since fix skills skip their own detection when `.findings.md` exists, blueprint must detect ALL issues within each dimension. Missing a finding means it won't be fixed.

**Assessment method per dimension:**

| Dimension | What to scan | Patterns to detect |
|-----------|-------------|-------------------|
| Security & Privacy | All source files | Hardcoded secrets (API keys, tokens, passwords in string literals), `eval()`/`Function()` with dynamic input, SQL string concatenation, missing parameterized queries, missing auth middleware on protected routes, PII in log statements, weak crypto (MD5, SHA1, DES, ECB), missing HTTPS enforcement, CORS wildcard in production, missing CSRF protection, missing input validation/sanitization, missing rate limiting |
| Code Quality | All source files | Unused imports/vars/functions, missing type annotations on public APIs, deep nesting (>3 levels), duplicated code blocks (>10 lines), dead code (unreachable branches), magic numbers, overly long functions (>50 lines), overly long files (>500 lines), empty catch/except blocks, TODO/FIXME/HACK comments older than 30 days |
| Architecture | Import graph + structure | Circular dependencies, god classes (>10 public methods or >300 lines), feature envy (class using another class's data more than its own), layer violations (UI importing DB directly), missing dependency injection, tightly coupled modules, inconsistent error handling patterns across modules, inconsistent naming conventions |
| Performance | All source files | N+1 queries (DB call inside loop), blocking calls in async context, missing pagination on list endpoints, missing database indexes (query patterns without matching index), large file reads without streaming, missing caching on repeated expensive operations, unbounded collection growth, synchronous I/O in hot paths |
| Resilience | All source + config | Missing error handling on external calls, missing timeout configuration, missing retry with backoff, no graceful shutdown handler, no health check endpoint, unbounded queue/buffer growth, missing circuit breaker on external services, no fallback for failed dependencies, missing input size limits |
| Testing | Test files + config | Test file count vs source count ratio, missing test runner config, missing coverage config, untested modules (source files with 0 corresponding test files), missing negative/boundary test cases (only happy-path assertions), test isolation issues (shared mutable state), flaky test indicators (sleep/delay in tests, time-dependent assertions) |
| Stack Health | Manifests + lockfiles | Missing lockfile, outdated dependencies (major versions behind), deprecated packages, known CVEs in dependencies (run audit command), missing `.nvmrc`/`.tool-versions`, inconsistent dependency versions across workspace packages |
| DX | Root files + config | Missing/incomplete README, missing CONTRIBUTING.md, missing CI config, missing env.example, missing setup/dev scripts, missing Makefile/Taskfile, missing .editorconfig, inconsistent config file formats |
| Documentation | Doc files + source | Missing doc files vs ideal for project type, README sections missing (install, usage, API, contributing), API doc gaps (undocumented public endpoints/functions), doc↔code drift (stale paths, renamed functions, changed defaults, removed features still documented), broken internal links, outdated version references, stale dependency version claims, architectural claims that don't match code |

**False positive prevention (mandatory for every signal):**

Before counting any pattern match as a signal, verify it passes ALL applicable checks:
- **Exclude test files:** Skip matches in `test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`
- **Exclude comments:** If the pattern is inside a comment (`//`, `#`, `/* */`, `<!-- -->`), skip
- **Exclude string literals in tests:** Secret patterns in test fixtures or example data, skip
- **Exclude generated files:** Skip files in `generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, auto-generated headers
- **Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures, generated files
- **Verify context:** For security signals, read 3 lines around the match — if value is from env/config/vault, skip

**Confidence:** HIGH = verified match + context confirmed (count as full signal), MEDIUM = pattern match, ambiguous context (count as 0.5 signal), LOW = heuristic only (skip, do not count). Only HIGH and MEDIUM written to `.findings.md`.

Scoring formula from [references/scopes.md](references/scopes.md), dimension weights from [references/weights.md](references/weights.md). For user-facing types (web, mobile, desktop): also check i18n setup and a11y basics.

### Phase 3.1: Project Map

Build from Discovery + Assess results. Generated from directory structure, entry points, import patterns, dependency files, toolchain.

### Phase 4: Consolidate

1. Apply dimension score aggregation and weight matrix from [references/weights.md](references/weights.md). Run score calibration checks.
2. Write `.findings.md` in this format:
   ```
   <!-- findings-meta
   git_hash: {HEAD}
   timestamp: {ISO 8601}
   source: ds-blueprint
   scopes: security, code-quality, architecture, performance, resilience, testing, stack, dx, docs
   -->

   ## Findings

   | ID | Severity | File | Line | Scope | Title |
   |----|----------|------|------|-------|-------|
   | F001 | CRITICAL | src/auth.ts | 42 | security | Hardcoded API secret |
   ```
   Every finding must include file:line so fix skills can act on it directly.
3. Verify completeness: every dimension must have its findings written. A missing scope in `.findings.md` means fix skills will skip their own detection for that scope — resulting in missed issues.

### Phase 5: Dashboard

Display blueprint dashboard:

```
Project: {name} | Type: {type} | Stack: {stack} | Target: {quality}

| Dimension          | Score | Target | Gap  | Status |
|--------------------|-------|--------|------|--------|
| Security & Privacy |  65   |   85   | -20  | ALERT  |
| Code Quality       |  80   |   85   |  -5  | WARN   |
| Architecture       |  75   |   80   |  -5  | WARN   |
| ...                |       |        |      |        |
| Overall            |  72   |   82   | -10  | WARN   |

Findings written to .findings.md (38 signals across 9 dimensions)
```

### Phase 6: Suggest (skip if --preview)

List dimensions below target with signal counts. No skill-specific commands — findings file is the interface. Any fix tool or skill can consume it.

```
Dimensions below target:

1. Security & Privacy (score: 65, target: 85) — 12 signals
2. Code Quality (score: 80, target: 85) — 8 signals
3. Documentation (score: 70, target: 80) — 5 signals

→ .findings.md written with 38 signals. Run your preferred fix tool/skill to resolve.
```

In `--auto` mode: print as part of summary, no interaction.

### Phase 7: Update Profile

Update Current Scores in the instruction file's blueprint section (between markers).

**Score History:** If profile has previous scores, display delta table with trend (up/stable/down based on +/-3 threshold).

### Phase 8: Summary

Before/After delta table (9 dimensions), next steps.

`blueprint: {OK|WARN|FAIL} | Health: {before}->{after}/{target} | Findings: {n} | Score: {n}/100`

Status: OK (overall >= target), WARN (gap exists but progress), FAIL (CRITICAL unfixed or regression).

## Quality Gates

- Every signal cites file:line — skip signals without evidence
- Only count signals from source code — exclude test, generated, vendored files
- Score reflects verified signals only — uncertain signals reduce to 0.5 weight

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project | Report baseline scores, note no code to assess |
| Monorepo | Score each workspace independently, aggregate in summary |
| No instruction file found | Create new profile, ask user for target file location |

