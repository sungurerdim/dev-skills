# /ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions and tells you exactly where to focus next.

**Project Health System** — Profile-based assessment, transformation, and progress tracking.

## Triggers

- User runs `/ds-blueprint`
- User asks to assess project health, quality, or overall status
- User asks for project profile, health score, or quality dashboard
- User asks "how healthy is this project" or "what should I improve"
- First time working on new project (suggest profile creation)

## Contract

- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.
- Scores project health across 9 dimensions — signal counting, not file:line finding lists
- Only modifies instruction file's blueprint profile section — never touches other content
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

Profile embedded in project's AI instruction file between `## Blueprint Profile` and `## End Blueprint Profile` heading markers. Markdown headings are universally preserved by every tool — no risk of being stripped during processing.

**Legacy marker migration:** If profile exists with non-standard markers (HTML comments like `<!-- *-start -->` / `<!-- *-end -->`, or variant headings like `## X Blueprint Profile`), migrate it:
1. Read existing content between legacy markers
2. Replace markers with standard `## Blueprint Profile` / `## End Blueprint Profile` headings
3. Preserve all existing content (scores, config, project map, run history)
4. Remove old markers

**Instruction file detection** — search for known AI instruction files (see [references/detection.md](references/detection.md) § Instruction Files for full list). Use first match. None found: ask user which tool they use, then create appropriate file.

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
```
Entry: {entry point} → {framework}

Modules:
  {path}/  → {role} ({n} files)
    {key_file}  → {responsibility}
    ...

Data Flow:
  {source} → {step (action)} → {step} → ... → {sink}

External: {dependency list with purpose}

Toolchain: {tools} | {CI} | {container}
```

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

### Run History
- {YYYY-MM-DD}: {skill} {mode} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Overall {before}→{after}
- {YYYY-MM-DD}: {skill} {mode} | Applied {n} ({finding-IDs or short descriptions for significant fixes}) | Overall {before}→{after}

## End Blueprint Profile
```

**Run History format:**
- Each entry records: date, skill name (e.g., `ds-blueprint`, `ds-review --tactical`), mode, finding counts by disposition (FRC), and overall score delta
- Skill name identifies which command produced the run — essential for traceability
- For targeted fix runs: include finding IDs or short descriptions of significant fixes (aids future analysis of what improved which score)
- Append new entries — never overwrite or rewrite existing history
- Two entry formats (use whichever fits the run):
  - Assessment: `- {YYYY-MM-DD}: {skill} {mode} | Findings: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Overall {n}→{n}`
  - Targeted fix: `- {YYYY-MM-DD}: {skill} {mode} | Applied {n} ({short descriptions}) | Overall {n}→{n}`

**Read/write rules:**
- Only modify content between `## Blueprint Profile` and `## End Blueprint Profile` headings — never touch anything outside them
- **Profile detection order** (check before any write):
  1. Search for standard markers: `## Blueprint Profile` ... `## End Blueprint Profile`
  2. Search for legacy markers: HTML comment pairs (`<!-- *-start -->` ... `<!-- *-end -->`) or variant headings containing "Blueprint Profile"
  3. Standard markers found → update in place (preserve all sections, only update Current Scores and append Run History)
  4. Legacy markers found → **do not touch legacy block**. Write new standard profile separately (below legacy block or at end of file). Then compare:
     - Read both profiles section by section (Config, Project Map, Ideal Metrics, Current Scores, Run History)
     - Identify content in legacy profile NOT covered by new profile (e.g., custom config notes, historical run entries, project map details)
     - Report to user:
       - New profile covers everything: "New profile covers all content from legacy block. You can safely remove the legacy block."
       - Legacy has unique content: "These items exist in legacy profile but not in new one: {list}. Consider preserving them before removing legacy block."
     - Never delete or modify legacy block — user decides when to remove it
  5. NO markers found → append new profile section at end of instruction file
  6. **Never write second standard profile into file that already has one** — always detect and update existing standard profile
- Instruction file does not exist: create it with profile section only
- Other skills read profile by searching for `## Blueprint Profile` heading first, then legacy markers as fallback, in known instruction file locations
- When updating existing standard profile: preserve Config, Project Map, Ideal Metrics, and full Run History. Only update Current Scores and append to Run History. Re-detect Project Map only with `--refresh` flag.
**Deduplication on inject:**

Deduplicate findings by file:line — same issue within 10 lines → merge, keep highest severity.

## Execution Flow

Discovery → [Init Flow] → Assess → Consolidate → Dashboard → [Suggest] → Update Profile → [Needs-Approval] → Summary

**Mandatory phases** (no brackets — always execute, always produce output):
- **Assess** — scan codebase, record findings
- **Consolidate** — score dimensions, write `.ds-findings.md`
- **Dashboard** — display score table with delta and gap analysis
- **Update Profile** — update Current Scores and append Run History
- **Summary** — print summary line with FRC accounting

Skipping any mandatory phase is an execution bug. Every mandatory phase produces user-visible output.

### Phase 1: Discovery [PARALLEL]

1. **Mode selection.** No flags provided → ask user:
   - **Full Analysis** — assess all dimensions, score, dashboard, suggest next steps
   - **Preview Only** — analyze + dashboard, no changes
   - **Init Profile** — create/refresh project profile only
   - **Refresh Profile** — re-scan profile, preserve decisions
2. Recovery check: if progress artifact exists from prior run, ask: Resume / Start fresh (--auto: resume silently)
3. Search for `## Blueprint Profile` heading in known instruction files (see Profile Storage detection table). Read existing profile to detect incremental vs full run.
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

**Gate:** Mode selected, project type detected, instruction file located or creation path determined.

### Phase 2: Init Flow (no profile OR --init/--refresh)

Ask user two sets of questions:

**Project Identity:**
- What category best describes this project? (auto-detected type shown, options: Frontend, Backend, Developer Tool, Infrastructure)
- What quality level? (Prototype, MVP, Production, Enterprise)
- What kind of data does it handle? (Personal info, Sensitive data, Auth credentials, No sensitive data)

**Strategy:**
- Focus areas for improvement? (Security, Code Quality, Architecture, Documentation)
- Constraints? (Keep framework, Preserve public APIs, Minimize new dependencies, No restrictions)
- Who uses this project? (Public users, Internal team, Other developers, Local/undecided)

**Data fallback:** PII/credential pattern scan finds nothing → explicitly ask: "Does this project process user data? (Yes — describe data types / No)". Ensures `Config.data` is never empty by inference alone.

**--auto Mode Defaults:**

| Question | Default |
|----------|---------|
| Project type | Auto-detected |
| Quality | Production |
| Data | Search for PII/credential patterns. Scan finds nothing → default to "No sensitive data" but add note: "PII scan negative — verify manually if project handles user data indirectly (e.g., via external APIs)" |
| Priorities | Security + Code Quality |
| Constraints | Keep framework/language |
| Audience | Auto-detect (Dockerfile → container, CI → cloud, else local) |
| Deployment | Auto-detect from Docker/cloud/serverless signals |

Write profile to detected instruction file (see Profile Storage). Calculate ideal metrics from `references/weights.md` based on detected project type. Quality-level descriptions in [references/quality-levels.md](references/quality-levels.md).

**Gate:** Profile written to instruction file with all sections populated.

### Phase 3: Assess (scan, record, score — don't fix)

Blueprint scans **entire codebase** and records every finding with file:line to `.ds-findings.md`. Scores dimensions from these findings but does NOT fix anything. Other skills read `.ds-findings.md` and handle fixes — eliminates duplicate analysis.

**Completeness requirement:** Fix skills skip their own detection when `.ds-findings.md` exists, so blueprint must detect ALL issues within each dimension. Missing finding = won't be fixed.

**Dimension → Scope mapping:** Blueprint scores 9 dimensions but writes findings with granular scope names so consumers can filter precisely:

| Dimension | Findings Scope(s) |
|-----------|------------------|
| Security & Privacy | `security`, `privacy` |
| Code Quality | `hygiene`, `types`, `simplify`, `ai-hygiene`, `doc-sync` |
| Architecture | `architecture`, `patterns`, `cross-cutting`, `maintainability`, `ai-architecture` |
| Performance | `performance` |
| Resilience | `robustness`, `production-readiness` |
| Testing | `testing`, `functional-completeness` |
| Stack Health | `stack` |
| DX | `dx` |
| Documentation | `docs` |

**Assessment method per dimension:**

| Dimension | What to scan | Patterns to detect |
|-----------|-------------|-------------------|
| Security & Privacy | All source files | Hardcoded secrets (API keys, tokens, passwords in string literals), `eval()`/`Function()` with dynamic input, SQL string concatenation, missing parameterized queries, missing auth middleware on protected routes, PII in log statements, weak crypto (MD5, SHA1, DES, ECB), missing HTTPS enforcement, CORS wildcard in production, missing CSRF protection, missing input validation/sanitization, missing rate limiting |
| Code Quality | All source files | Unused imports/vars/functions, missing type annotations on public APIs, deep nesting (>3 levels), duplicated code blocks (>10 lines), dead code (unreachable branches), magic numbers, overly long functions (>50 lines), overly long files (>500 lines), empty catch/except blocks, TODO/FIXME/HACK comments older than 30 days. **ai-hygiene:** AI-generated boilerplate (verbose wrappers, unnecessary abstractions, over-engineered helpers), placeholder comments ("This function does X"), redundant error handling layers. **doc-sync:** Inline doc comments that contradict actual function signature, stale parameter descriptions, wrong return type in docstrings. |
| Architecture | Import graph + structure | Circular dependencies, god classes (>10 public methods or >300 lines), feature envy (class using another class's data more than its own), layer violations (UI importing DB directly), missing dependency injection, tightly coupled modules, inconsistent error handling patterns across modules, inconsistent naming conventions. **maintainability:** High change coupling (files that always change together but aren't co-located), shotgun surgery patterns (single logical change requires edits in 5+ files), missing abstraction boundaries. **ai-architecture:** AI-specific patterns: prompt templates scattered across modules (should be centralized), missing retry/fallback for AI API calls, hardcoded model names, missing token budget management. |
| Performance | All source files | N+1 queries (DB call inside loop), blocking calls in async context, missing pagination on list endpoints, missing database indexes (query patterns without matching index), large file reads without streaming, missing caching on repeated expensive operations, unbounded collection growth, synchronous I/O in hot paths |
| Resilience | All source + config | Missing error handling on external calls, missing timeout configuration, missing retry with backoff, no graceful shutdown handler, no health check endpoint, unbounded queue/buffer growth, missing circuit breaker on external services, no fallback for failed dependencies, missing input size limits. **production-readiness:** Missing structured logging, debug endpoints exposed, missing rate limiting on public endpoints, no graceful degradation under load, missing deployment health checks. |
| Testing | Test files + config | Test file count vs source count ratio, missing test runner config, missing coverage config, untested modules (source files with 0 corresponding test files), missing negative/boundary test cases (only happy-path assertions), test isolation issues (shared mutable state), flaky test indicators (sleep/delay in tests, time-dependent assertions). **functional-completeness:** Missing error paths (only happy path implemented), missing input validation edge cases, TODO/FIXME markers indicating unfinished features, stub/placeholder implementations. |
| Stack Health | Manifests + lockfiles | Missing lockfile, outdated dependencies (major versions behind), deprecated packages, known CVEs in dependencies (run audit command), missing `.nvmrc`/`.tool-versions`, inconsistent dependency versions across workspace packages |
| DX | Root files + config | Missing/incomplete README, missing CONTRIBUTING.md, missing CI config, missing env.example, missing setup/dev scripts, missing Makefile/Taskfile, missing .editorconfig, inconsistent config file formats |
| Documentation | Doc files + source | Missing doc files vs ideal for project type, README sections missing (install, usage, API, contributing), API doc gaps (undocumented public endpoints/functions), doc↔code drift (stale paths, renamed functions, changed defaults, removed features still documented), broken internal links, outdated version references, stale dependency version claims, architectural claims that don't match code |

**False positive prevention (mandatory for every signal):**

Before counting any pattern match as signal, verify it passes ALL applicable checks:
- **Exclude test files:** Skip matches in `test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`
- **Exclude comments:** Pattern inside comment (`//`, `#`, `/* */`, `<!-- -->`), skip
- **Exclude string literals in tests:** Secret patterns in test fixtures or example data, skip
- **Exclude generated files:** Skip files in `generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, auto-generated headers
- **Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures, generated files
- **Verify context:** For security signals, read 3 lines around match — value from env/config/vault → skip

**Confidence:** HIGH = verified match + context confirmed (count as full signal), MEDIUM = pattern match, ambiguous context (count as 0.5 signal), LOW = heuristic only (skip, do not count). Only HIGH and MEDIUM written to `.ds-findings.md`.

Scoring formula from [references/scopes.md](references/scopes.md), dimension weights from [references/weights.md](references/weights.md). For user-facing types (web, mobile, desktop): also check i18n setup and a11y basics.

**User-facing project gate:** Project type is web, mobile, desktop, or game — additionally check:
- i18n setup present (framework-native catalog, at least 1 locale file)
- Default locales configured (minimum: en + project owner's locale)
- a11y basics (semantic labels on interactive elements, contrast ratio, screen reader support)
- Responsive layout (breakpoints or adaptive layout)

Flag missing items as HIGH severity. Skip this gate for cli, library, api, iac, devtool project types.

**Gate:** All 9 dimensions scanned. Every signal has file:line evidence. False positive checks applied.

### Phase 3.1: Project Map

Build from Discovery + Assess results:

1. **Entry point:** Identify main entry file(s) and framework
2. **Modules:** List each top-level module directory with role, file count, and key files with their responsibilities. Depth: enough for new developer to understand architecture, not full file listing.
3. **Data Flow:** Trace primary user-facing flow end-to-end (e.g., request → auth → process → store → respond). Include intermediate systems (queues, caches, external services).
4. **External:** List runtime dependencies with purpose (not dev tools). Group: databases, caches, queues, auth providers, third-party APIs.
5. **Toolchain:** Format/lint tools, test framework, CI platform, container setup.

**Gate:** Project map generated with entry points, modules, data flow, and external dependencies.

### Phase 4: Consolidate

**Mandatory.** Always score dimensions AND write `.ds-findings.md` — never skip.

1. Apply dimension score aggregation and weight matrix from [references/weights.md](references/weights.md). Run score calibration checks.
2. **Score calibration checks** — verify scoring sanity before presenting:
   - Overall score range 20-95 for real projects (0 or 100 suspicious — re-verify)
   - No individual dimension at 100 (re-check for missed signals)
   - CRITICAL finding present → overall must be < 80 (if not, scoring error)
   - Adjacent dimension delta < 30 (e.g., architecture 90 but code quality 50 → investigate)
   - Any check fails → re-read flagged dimension's signals and adjust
3. Write `.ds-findings.md` in this format:
   ```
   <!-- findings-meta
   git_hash: {HEAD}
   timestamp: {ISO 8601}
   source: ds-blueprint
   scopes: security, privacy, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs
   -->

   ## Findings

   | ID | Severity | File | Line | Scope | Title |
   |----|----------|------|------|-------|-------|
   | {id} | {severity} | {file} | {line} | {scope} | {title} |
   ```
   Every finding must include file:line so fix skills can act on it directly.
4. **Verify completeness:** Count distinct scope values in `.ds-findings.md`. Expected count is 22 (security, privacy, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs). Count < 22 → identify missing scopes and re-run assessment for those scopes before proceeding. Missing scope = fix skills skip detection for that scope → missed issues.

**Gate:** All 9 dimension scores calculated. Calibration checks passed. `.ds-findings.md` written with all 22 scopes verified present.

### Phase 5: Dashboard

**Mandatory.** Always display dashboard — never skip, even in `--auto` mode.

Display blueprint dashboard:

```
Project: {name} | Type: {type} | Stack: {stack} | Target: {quality}

| Dimension          | Score | Prev | Delta | Target | Gap  | Status |
|--------------------|-------|------|-------|--------|------|--------|
| {dimension}        | {n}   | {n}  | {+/-n}| {n}   | {n}  | {status}|
| ...                |       |      |       |        |      |        |
| Overall            | {n}   | {n}  | {+/-n}| {n}   | {n}  | {status}|

Findings written to .ds-findings.md ({n} signals across {n} dimensions)
```

Previous scores exist in profile: show Prev and Delta columns. First run: omit Prev/Delta columns.

For dimensions below target, list top priority findings with IDs:
```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}, gap: {n}) — {n} signals
   {finding-ID} {severity}: {short description}
```

Any dimension dropped (negative delta), explain why:
```
Score changes: {dimension} {delta}: {brief cause}
```

**Gate:** Dashboard displayed with all dimensions, scores, delta (if applicable), and gap analysis. `.ds-findings.md` write confirmed.

### Phase 6: Suggest (skip if --preview)

List dimensions below target with signal counts. No skill-specific commands — findings file is interface. Any fix tool or skill can consume it.

```
Dimensions below target:

1. {dimension} (score: {n}, target: {n}) — {n} signals
2. ...


→ .ds-findings.md written with {n} signals. Run your preferred fix tool/skill to resolve.
```

In `--auto` mode: print as part of summary, no interaction.

**Gate:** Suggestions generated for all below-target dimensions.

### Phase 7: Update Profile

**Mandatory.** Always update profile — never skip.

1. Update Current Scores in instruction file's blueprint section (between markers)
2. Append Run History entry with: date, skill name (`ds-blueprint`), mode, finding counts, overall score delta
3. Profile has previous scores: display delta table with trend (up/stable/down based on +/-3 threshold)

**Gate:** Profile updated with current scores. Run History entry appended. Score history preserved.

### Phase 8: Needs-Approval Review [needs_approval > 0]

Present needs_approval items with risk context. Modes: --auto → list+skip, --force-approve → apply all, interactive → Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved.

### Phase 9: Summary

**Mandatory.** Always print summary line — never skip.

`blueprint: {OK|WARN|FAIL} | Health: {before}->{after}/{target} | Fixed: N | Skipped: N | Failed: N | Total: N | Score: {n}/100`

FRC+DSC accounting.

Status: OK (overall >= target), WARN (gap exists but progress), FAIL (CRITICAL unfixed or regression).

**Gate:** Summary printed with before/after scores and next steps.

## Quality Gates

- Every signal cites file:line — skip signals without evidence
- Only count signals from source code — exclude test, generated, vendored files
- Score reflects verified signals only — uncertain signals reduce to 0.5 weight

## Error Recovery

| Situation | Action |
|-----------|--------|
| Codebase too large for full scan | Apply saturation gate after 3 dimensions, extrapolate remaining |
| Blueprint profile write fails | Save to temporary file, warn user, suggest manual placement |
| Previous profile format incompatible | Write new profile alongside, let user decide when to remove old |
| Scoring dimension has zero signals | Score as N/A, exclude from overall calculation |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project | Report baseline scores, note no code to assess |
| Monorepo | Score each workspace independently, aggregate in summary |
| No instruction file found | Create new profile, ask user for target file location |
