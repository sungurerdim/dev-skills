---
name: ds-blueprint
description: Project health system — profile-based assessment, transformation, and progress tracking. Use when assessing overall project health, planning a transformation, or tracking improvement over time.
---

# /ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions and tells you exactly where to focus next.

**Project Health System** — Profile-based assessment, transformation, and progress tracking.

## Triggers

- User runs `/ds-blueprint`
- User asks to assess project health, quality, or overall status
- User asks for project profile, health score, or quality dashboard
- User asks "how healthy is this project" or "what should I improve"
- First time working on new project (suggest profile creation)
- A verification-infrastructure gap (no CI, no tests, no linter) surfaces during any task (suggest audit — don't auto-invoke)

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "score project health", "what should I improve first" | "fix the issues" (→ ds-review or ds-fix) |
| "create project profile", "refresh blueprint" | "research industry best practices" (→ ds-research) |
| "blueprint dashboard, 9 dimensions" | "release-candidate report" (→ ds-ship) |
| "where is this codebase weakest" | "competitor comparison" (→ ds-benchmark) |
| "project has no CI/tests — what else is missing?" | "scaffold CI from zero on a greenfield project" (→ ds-init) |

## Contract

- Scores project health across 9 dimensions — signal counting, not file:line finding lists. Only modifies the profile section of the instruction file; suggests next steps but never invokes other skills or fixes code.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **Completeness requirement (SSOT):** `ds/audit/findings.md` is the single source of truth for every fix skill. Other skills skip their own detection when blueprint findings exist. Blueprint MUST detect ALL issues in each in-scope dimension — a missing finding will not be fixed downstream.
- **SSOT runtime enforcement (W10):** Every downstream consumer (ds-review, ds-fix, ds-simplify, ds-compliance, ds-mobile, etc.) MUST defer to a fresh `ds/audit/findings.md` (`git_hash == HEAD`, age ≤ 7 days). Fresh → consumers verify + apply only; they do NOT re-detect within blueprint's owned scopes. Stale or missing → consumer invokes `/ds-blueprint --refresh` or `--preview --scope=all` and waits before continuing. Re-detection within a covered scope is a W10 violation.
- **Overwrite-only persistence (SKILL-SPEC §10.1):** state, findings, profile rewritten every run — never appended. Run history lives in `git log -- <instruction-file>`, not in profile or any `ds/audit/` file. Append-only artifacts forbidden anywhere.
- **Human-action items:** findings whose remediation requires human-only access (branch protection, CI/repo secrets, store or account setup, key rotation, purchases) are surfaced as a distinct `Human actions` block in Dashboard and repeated in Summary — never silently dropped, never marked fixed by the AI.
- **Dev-Value Gate on every profile line:** the instruction file is re-read on every AI turn — every byte costs every future model read. A profile line is written only if it makes AI engineering measurably better on every turn for the next 6 months. Anything else (timestamps, score deltas, owner info, descriptions, philosophy) goes to README / CHANGELOG / git log / terminal summary instead.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All phases, no questions, single-line summary |
| `--preview` | Analyze + dashboard, no changes |
| `--init` | Profile creation/refresh only (no analysis) |
| `--refresh` | Re-scan profile (decisions preserved) |
| `--scope={x}` | Specific area: stack, stack-fitness, deps, dx, external-tooling, structure, code, architecture, docs, spec-alignment, memory, all |
| `--resume` | Resume from `ds/audit/blueprint.json` without prompting |
| `--clean` | Delete existing state, start fresh |
| `--memory-cleanup` | Optional phase: scan AI agent memory index (`MEMORY.md`) for stale `[[link]]` references + offer consolidation. Default OFF — opt-in only |

Without flags: present mode selection.

## Profile Storage

Profile embedded in project's AI instruction file between `## Blueprint Profile` and `## End Blueprint Profile` heading markers — markdown headings are universally preserved by every tool.

**Legacy marker migration** (non-standard markers: HTML comments like `<!-- *-start -->` / `<!-- *-end -->`, or variant headings like `## X Blueprint Profile`): read content between legacy markers, replace with standard headings, preserve all existing content (scores, config, project map, run history), remove old markers.

**Instruction file detection** — search for known AI instruction files (see [references/detection.md](references/detection.md) § Instruction Files). Use first match. None found: ask which tool user uses, create appropriate file.

**Profile format** — minimal, AI-parseable, calibration-only. Run history, score deltas, status messages NEVER go here — they live in `git log -- <instruction-file>`, `ds/audit/findings.md`, terminal summaries.

```markdown
## Blueprint Profile

Type: {type} | Stack: {stack} | Target: {quality}
Priorities: {comma-list} | Constraints: {comma-list}
Data: {data-types} | Regulations: {framework-or-none}
Audience: {audience} | Deploy: {method}

Entry: {entry-point} ({framework})
Modules: {path}={role}({n}); {path}={role}({n}); ...
Data Flow: {source}→{step}→{sink}
External: {dep-1}({purpose}); {dep-2}({purpose}); ...
Toolchain: {tools} | CI: {ci} | Container: {container-or-none}

Ideal: coupling={n} cohesion={n} complexity={n} coverage={n}%

Scores: sec={n} quality={n} arch={n} perf={n} resil={n} test={n} stack={n} dx={n} docs={n} overall={n} model={model-id}

## End Blueprint Profile
```

**Format rules:** key-value pairs only, one value per line — no prose, headers, tables, or bullets inside the block; AI parses by `{key}: {value}` line-shape, every consumer reads its line in O(1). `Modules:` and `External:` use `;` separator so the block stays one line per concern. `Scores:` is a single line with short keys — dashboard renders in chat output, not in the profile; `model=` records the AI model that performed the assessment (e.g. `model=claude-fable-5`; `model=unknown` when not determinable), enabling model-uplift attribution — score deltas across model generations traceable via `git log` of this line. Context-loaded files must not accumulate: every byte costs every future read; run history + deltas + per-skill summaries forbidden — `git log -- <instruction-file>` is the trend log. The profile is calibration data, not a dashboard.

**Read/write rules:**
- Only modify content between `## Blueprint Profile` and `## End Blueprint Profile` headings — never touch anything outside.
- **Profile detection order** (check before any write):
  1. Search for standard markers: `## Blueprint Profile` ... `## End Blueprint Profile`
  2. Search for legacy markers: HTML comment pairs (`<!-- *-start -->` ... `<!-- *-end -->`) or variant headings containing "Blueprint Profile"
  3. Standard found → update in place (preserve all calibration lines, rewrite only the `Scores:` line)
  4. Legacy found → **do not touch legacy block**. Write new standard profile separately (below legacy or at end of file). Compare both line by line (Type/Stack/Target, Priorities, Constraints, Data, Audience, Deploy, Entry, Modules, Data Flow, External, Toolchain, Ideal, Scores); identify legacy content NOT covered by new (custom config notes, historical run entries, project map details). New covers everything → report "New profile covers all content from legacy block. You can safely remove the legacy block." Legacy has unique items → report "These items exist in legacy profile but not in new one: {list}. Consider preserving them before removing legacy block." Never delete or modify legacy block — user decides when to remove.
  5. NO markers found → append new profile at end of instruction file
  6. **Never write second standard profile into a file that already has one** — always detect and update.
- Instruction file does not exist: create with profile section only.
- Other skills read profile by searching for `## Blueprint Profile` heading first, then legacy markers as fallback, in known instruction file locations.
- Updating existing standard profile: preserve all `Type/Stack/Target/Priorities/Constraints/Data/Audience/Deploy/Entry/Modules/Data Flow/External/Toolchain/Ideal` lines; update only the `Scores:` line; re-detect Project Map only with `--refresh`.
- Legacy migration: profiles containing `### Last Run`, `### Run History`, `### Current Scores` (table), or any prose block → rewrite to minimal key-value format; report `{n} legacy lines rotated to git log` in summary. Information preserved in `git log -- <instruction-file>` — never re-injected.

**Deduplication on inject:** dedupe findings by file:line — same issue within 10 lines → merge, keep highest severity.

## Delegation

**Owns:** security, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs, spec-alignment, stack-fitness, external-tooling | **Delegates:** none (full-codebase SSOT producer; privacy scope produced by ds-compliance, canonical) | **Receives:** ds-review → bootstrap; ds-ship → Phase 0 bootstrap when findings absent or stale

## Execution Flow

```
Discovery → [Init Flow] → Assess → Consolidate → Dashboard → [Suggest] → Update Profile → [Needs-Approval] → Summary
```

**Mandatory phases** (always execute, always produce output): Assess, Consolidate, Dashboard, Update Profile, Summary. Skipping a mandatory phase is an execution bug.

### Phase 1: Discovery [PARALLEL]

**Recovery check:** DETECT `ds/audit/blueprint.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`; `--auto` resumes silently). Resume → RE-VERIFY `in_progress` phase (re-scan modified scopes, keep completed scopes), skip `done` phases, announce `[BP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/` in `.gitignore` on fresh start.

**State `data`:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, severity, file, line}]}, profile_written: bool, scores: {dimension: score}, instruction_file }`.

1. **Mode selection.** No flags → present a menu covering every mode, each with a one-line what-it-does: Full Analysis (recommended) — detect + analyze every dimension / Preview Only — analyze, no profile write / Init Profile — seed a fresh profile / Refresh Profile — re-score an existing profile / (Cancel). A disambiguating flag skips the menu.
2. Search for `## Blueprint Profile` heading in known instruction files; read existing profile to detect incremental vs full run.
3. Detect project via three-step process from [references/detection.md](references/detection.md): (1) stack from manifest files (pubspec.yaml, package.json, go.mod, etc.); (2) project type from secondary signals (framework deps, config, directory structure); (3) supplementary stacks (Docker, shell scripts, CI, task runners). Also: toolchain, tests, data sensitivity, git status.

**Decision tree:**
1. Profile exists + not --init/--refresh → Phase 3 (incremental)
2. Profile exists + --refresh → Phase 2 (re-ask, preserve decisions)
3. No profile + --init → Phase 2 (create, stop)
4. No profile + not --init → Phase 2 (create, ask to continue)

**Gate:** Mode selected; project type detected; instruction file located or creation path determined. If fails → type undetectable (no manifest, empty repo) + no user response to type prompt → default `generic`, mode `Full Analysis`, instruction file `CLAUDE.md`, WARN `"Project type undetected — defaulted to generic"` in state.data, proceed.

### Phase 2: Init Flow (no profile OR --init/--refresh)

**Project Identity:** Category? (auto-detected shown: Frontend / Backend / Developer Tool / Infrastructure) | Quality level? (Prototype / MVP / Production / Enterprise) | Data handled? (Personal info / Sensitive data / Auth credentials / None)

**Strategy:** Focus areas? (Security / Code Quality / Architecture / Documentation) | Constraints? (Keep framework / Preserve public APIs / Minimize new dependencies / None) | Users? (Public / Internal team / Other developers / Local-undecided)

**Data fallback:** PII/credential pattern scan finds nothing → explicitly ask: "Does this project process user data? (Yes — describe data types / No)". Ensures `Config.data` is never empty by inference alone.

**--auto Mode Defaults:**

| Question | Default |
|----------|---------|
| Project type | Auto-detected |
| Quality | Production |
| Data | PII/credential scan; nothing → "No sensitive data" + note "PII scan negative — verify manually if project handles user data indirectly (e.g. via external APIs)" |
| Priorities | Security + Code Quality |
| Constraints | Keep framework/language |
| Audience | Auto-detect (Dockerfile → container, CI → cloud, else local) |
| Deployment | Auto-detect from Docker/cloud/serverless signals |

Write profile to detected instruction file. Calculate ideal metrics from `references/weights.md`. Quality-level descriptions in [references/quality-levels.md](references/quality-levels.md).

**Gate:** Profile written with all sections. If fails → write failed (permissions, invalid path, tool doesn't support file creation) → save profile to `ds/audit/blueprint-profile-draft.md`, display full text in chat for manual paste, surface write error with target path.

### Phase 2.5: Parallel-Track Planning [PARALLEL]

Group 9 dimensions × 24 scopes by execution cost — plan concurrency consciously.

| Batch | Scopes | Concurrency | Why |
|-------|--------|-------------|-----|
| **Read-only** | hygiene, types, doc-sync, dx, docs, spec-alignment, stack, stack-fitness, external-tooling | Parallel — pure grep/file-read, no AST | Cheapest scans, no shared state |
| **AST** | architecture, patterns, cross-cutting, maintainability, simplify, ai-architecture, performance | Parallel — shared LSP/AST cache | Share parse work across detectors |
| **Cross-file** | security, privacy, ai-hygiene, robustness, production-readiness, testing, functional-completeness | Serial — each batch may modify findings index | Order matters for dedup |

Plan batches up front (`state.data.batches`) and announce before starting. AI hosts route parallelism — the spec declares which scopes are safe to run together.

**Gate:** Batches planned + announced. If fails (no detectable scopes) → mark plan empty, proceed to Summary with WARN.

### Phase 3: Assess (scan, record, score — don't fix)

Scan **entire codebase**, record every finding with file:line to `ds/audit/findings.md`, score dimensions from these findings — do NOT fix. Fix skills read `ds/audit/findings.md` and skip own detection (eliminates duplicate analysis) → blueprint must detect ALL issues within each dimension; missing finding = won't be fixed.

**Dimension → Scope mapping:**

| Dimension | Findings Scope(s) |
|-----------|------------------|
| Security & Privacy | `security`, `privacy` |
| Code Quality | `hygiene`, `types`, `simplify`, `ai-hygiene`, `doc-sync` |
| Architecture | `architecture`, `patterns`, `cross-cutting`, `maintainability`, `ai-architecture` |
| Performance | `performance` |
| Resilience | `robustness`, `production-readiness` |
| Testing | `testing`, `functional-completeness` |
| Stack Health | `stack`, `stack-fitness` |
| DX | `dx`, `external-tooling` |
| Documentation | `docs`, `spec-alignment` |

**Assessment method per dimension:**

| Dimension | Scan | Patterns |
|-----------|------|----------|
| Security & Privacy | All source | Hardcoded secrets ({api-key-shape}, {token-shape}, password literals), `eval()`/`Function()` with dynamic input, SQL string concat, missing parameterized queries, missing auth middleware on protected routes, PII in log statements, weak crypto (MD5, SHA1, DES, ECB), missing HTTPS, CORS wildcard, missing CSRF, missing input validation, missing rate limiting |
| Code Quality | All source | Unused imports/vars/functions, missing type annotations on public APIs, nesting >3, duplicated blocks >10 lines, dead code, magic numbers, functions >50 lines, files >500 lines, empty catch, stale TODO/FIXME/HACK >30 days. **ai-hygiene:** AI boilerplate (verbose wrappers, unnecessary abstractions), placeholder comments ("This function does X"), redundant error layers. **doc-sync:** inline doc contradicts signature, stale param descriptions, wrong return type. |
| Architecture | Import graph + structure | **SOLID violations ([references/principles.md §2](references/principles.md)):** SRP (module changes for >1 reason), OCP (new behavior added by editing stable code), LSP (subtype narrows postcondition or throws unhandled), ISP (consumer forced to depend on unused members), DIP (high-level imports concrete low-level). **GRASP:** Information Expert (logic away from data), Low Coupling (>7 unrelated peer imports), High Cohesion (unrelated exports same module). Plus: circular deps, god classes (>10 public methods or >300 lines), feature envy, layer violations, missing DI, inconsistent error handling, inconsistent naming. **maintainability:** change coupling, shotgun surgery (single change requires 5+ file edits), missing abstraction boundaries. **ai-architecture:** prompt templates scattered (should be centralized), missing retry/fallback for AI API, hardcoded model names, missing token budget. |
| Performance | All source | N+1 queries (DB call in loop), blocking calls in async, missing pagination on lists, missing DB indexes, large file reads without streaming, missing caching, unbounded collection growth, synchronous I/O in hot paths |
| Resilience | Source + config | Missing error handling on external calls, missing timeout config, missing retry-with-backoff, no graceful shutdown, no health check, unbounded queue/buffer, missing circuit breaker, no fallback for failed deps, missing input size limits. **production-readiness:** missing structured logging, debug endpoints exposed, missing rate limiting, no graceful degradation under load, missing deployment health checks. |
| Testing | Tests + config | **Test discipline ([references/principles.md §7](references/principles.md)):** Test Pyramid signal (unit-heavy / integration-medium / E2E-light — inverted pyramid = HIGH); AAA structure absent; non-behavior test names (`test_1` vs `should_reject_negative_quantity`); unrealistic data (`a@b.c`, `$1`, length-1 collections); coverage configured as goal (target %) rather than diagnostic. Plus: test count vs source ratio, missing runner config, missing coverage config, untested modules, missing negative/boundary cases (empty, null, max-size, concurrent, locale, timezone, Unicode, leap-day), test isolation (shared mutable state), flaky indicators (sleep/delay, time-dependent assertions). **functional-completeness:** missing error paths, missing input validation edge cases, TODO/FIXME markers for unfinished, stub/placeholder implementations. |
| Stack Health | Manifests + lockfiles | Missing lockfile, outdated deps (major versions behind), deprecated packages, known CVEs in deps (run audit), missing `.nvmrc`/`.tool-versions`, inconsistent dep versions across workspace. **stack-fitness:** every major dep evaluated vs stated goal — obsolete (unmaintained, archived, last release >24 months), oversized-for-purpose (enterprise framework for 2-module project), duplicate (two libraries serving same purpose, e.g. {alt-1} + {alt-2}), misaligned (server-side library pulled into browser-only project). Cite goal from `Config.priorities`. |
| DX | Root files + config | Missing/incomplete README, missing CONTRIBUTING.md, missing CI config, missing env.example, missing setup/dev scripts, missing Makefile/Taskfile, missing .editorconfig, inconsistent config formats. **external-tooling:** GitHub Actions workflows, PR automations (auto-merge bots, reviewer assignment), CI scripts, pre-commit hooks, release automation — each evaluated for goal-fitness. Unused workflows, workflows referencing deleted actions, duplicate workflows (two paths to same target), automations added by templates but never triggered, goal-misaligned (e.g. iOS signing workflow on non-iOS project). |
| Documentation | Doc files + source | Missing doc files vs ideal for type, README sections missing (install, usage, API, contributing), API doc gaps (undocumented public endpoints/functions), doc↔code drift (stale paths, renamed functions, changed defaults, removed features still documented), broken internal links, outdated version refs, stale dep version claims, architectural claims that don't match code. **spec-alignment:** promise census — extract every concrete capability promised in README / SPEC.md / docs/ / AI instruction file (per host — see [references/detection.md](references/detection.md) § Instruction Files) / blueprint profile. For each promise, search source for implementation. Classify: **promised-not-implemented** (doc mentions feature X; grep shows no module/function/endpoint), **implemented-not-documented** (code has X but no doc mentions), **drift** (both exist but behavior diverges — default changed, signature changed, flag removed). |

**False-positive prevention (mandatory for every signal)** — count a pattern match only if it passes ALL applicable:
- **Exclude tests:** skip matches in `test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`
- **Exclude comments:** pattern inside comment (`//`, `#`, `/* */`, `<!-- -->`), skip
- **Exclude string literals in tests:** secret patterns in test fixtures or example data, skip
- **Exclude generated:** skip files in `generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, auto-generated headers
- **Skip patterns:** `# noqa`, `# intentional`, `# safe:`, `_` prefix, `TYPE_CHECKING` blocks, test fixtures, generated files
- **Verify context:** for security signals, read 3 lines around match — value from env/config/vault → skip

**Confidence:** HIGH = match + context confirmed (full signal). MEDIUM = pattern, ambiguous context (0.5 signal). LOW = heuristic (skip). Only HIGH + MEDIUM written to `ds/audit/findings.md`.

Scoring formula from [references/scopes.md](references/scopes.md), dimension weights from [references/weights.md](references/weights.md).

**User-facing project gate:** type is web, mobile, desktop, or game → additionally check: i18n setup present (framework-native catalog, ≥1 locale file); default locales configured (minimum: en + project owner's locale); a11y basics (semantic labels on interactive elements, contrast ratio, screen reader support); responsive layout (breakpoints or adaptive layout). Flag missing items as HIGH severity. Skip for cli, library, api, iac, devtool.

**Gate:** All 9 dimensions scanned; every signal has file:line evidence; false-positive checks applied. If fails → dimension(s) un-scan-able (codebase too large, binary-only files, access denied) → mark each incomplete in state.data.findings_per_scope with `confidence: inconclusive`, continue scoring with available signals only, flag in dashboard with `[PARTIAL SCAN]` so user knows scores are lower-bound.

### Phase 3.1: Project Map

Build from Discovery + Assess:

1. **Entry point:** main entry file(s) + framework.
2. **Modules:** each top-level module dir with role, file count, key files + responsibilities — enough for a new developer to understand, not full listing.
3. **Data Flow:** trace primary user-facing flow end-to-end (e.g. {source}→auth→process→store→{sink}), including intermediate systems (queues, caches, external services).
4. **External:** runtime dependencies with purpose (not dev tools), grouped: databases, caches, queues, auth, third-party APIs.
5. **Toolchain:** format/lint, test framework, CI platform, container.

**Gate:** Project map generated with entry, modules, data flow, externals. If fails → entry or flow undeterminable (no main file, no framework signals, no import graph) → write map with `unknown` placeholders, WARN `"Project map incomplete — manual review required for: {list}"` in profile, continue with partial map.

### Phase 4: Consolidate

**Mandatory.** Always score dimensions AND write `ds/audit/findings.md`.

1. Apply dimension score aggregation + weight matrix from [references/weights.md](references/weights.md). Run calibration checks.
2. **Score calibration checks** — verify sanity before presenting: overall in 20-95 for real projects (0 or 100 suspicious — re-verify); no individual dimension at 100 (re-check for missed signals); CRITICAL finding present → overall must be < 80 (else scoring error); adjacent dimension delta < 30 (e.g. architecture 90 but code quality 50 → investigate). Any fail → re-read flagged dimension's signals + adjust.
3. Write `ds/audit/findings.md` in this format:
   ```
   <!-- findings-meta
   git_hash: {HEAD}
   timestamp: {ISO 8601}
   source: ds-blueprint
   scopes: security, privacy, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, performance, robustness, production-readiness, testing, functional-completeness, stack, stack-fitness, dx, external-tooling, docs, spec-alignment
   -->

   ## Findings

   | ID | Severity | Category | File | Line | Scope | Title |
   |----|----------|----------|------|------|-------|-------|
   | {id} | {severity} | {A|B} | {file} | {line} | {scope} | {title} |
   ```
   Every finding includes file:line so fix skills can act directly. Category A when fix conforms to current architecture/plan; B when it changes architecture/scope/capability/user-promise/dependency.
4. **Verify completeness:** count distinct scopes in `ds/audit/findings.md`. Expected: 24 (the 23 scopes above + `ideal-gap` scope produced by `/ds-benchmark` when it runs). Count < 24 → identify missing scopes and re-run assessment for those before proceeding. Missing scope = fix skills skip detection → missed issues.

**Gate:** All 9 scores calculated; calibration passed; `ds/audit/findings.md` written with all 24 scopes verified. If fails → calibration suspicious score (dimension at 100, CRITICAL with overall ≥80) → re-read flagged signals + adjust; missing scopes → re-run assessment for each before writing; write fails → surface OS error, ask user to resolve.

### Phase 5: Dashboard

**Mandatory.** Always display, even in `--auto`.

```
Project: {name} | Type: {type} | Stack: {stack} | Target: {quality}

| Dimension          | Score | Prev | Delta | Target | Gap  | Status |
|--------------------|-------|------|-------|--------|------|--------|
| {dimension}        | {n}   | {n}  | {+/-n}| {n}    | {n}  | {status}|
| Overall            | {n}   | {n}  | {+/-n}| {n}    | {n}  | {status}|

Findings written to ds/audit/findings.md ({n} signals across {n} dimensions)
```

Previous scores exist: show Prev + Delta. First run: omit those columns. When previous `model=` differs from current, label each delta column as model-attributed (e.g. `Δ vs previous (model {prev-model} → {curr-model})`) so score movement is attributable to the model change, not code change alone.

For dimensions below target, list top findings with IDs:
```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}, gap: {n}) — {n} signals
   {finding-ID} {severity}: {short description}
```

Any dimension dropped (negative delta), explain: `Score changes: {dimension} {delta}: {brief cause}`

Findings requiring human-only access exist → list them (omit block when none):
```
Human actions (AI cannot perform these):
- {finding-ID}: {action} — where: {settings-page/console/account} | why: {risk if skipped}
```

**Gate:** Dashboard displayed with all dimensions, scores, delta (if applicable), gap analysis; `ds/audit/findings.md` write confirmed. If fails → write unconfirmed (filesystem error after Phase 4) → retry once; still failing → print dashboard with `[WARN: findings.md not written]` header so user sees scores but knows downstream consumers cannot use them until resolved.

### Phase 6: Suggest [SKIP if --preview]

List dimensions below target with signal counts. No skill-specific commands — findings file is interface.

```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}) — {n} signals

→ ds/audit/findings.md written with {n} signals. Run your preferred fix tool/skill to resolve.
```

In `--auto`: print as part of summary, no interaction.

**Gate:** Suggestions generated for all below-target dimensions. If fails → all dimensions at/above target → print `"All dimensions at or above target — no suggestions needed"`, proceed.

### Phase 7: Update Profile

**Mandatory.** Always update.

1. Rewrite the `Scores:` line — single line, key-value form. Include `model={model-id}` (model performing this assessment, from host/session context; `model=unknown` if not determinable).
2. Legacy `### Last Run`, `### Run History`, `### Current Scores` (table) block exists from previous version → rewrite entire profile to current minimal key-value format. Report `{n} legacy lines rotated to git log` in summary. Never re-inject historical run data.
3. Previous scores existed: display delta table in chat (Prev / Curr / Δ). Trend over >1 run → read from `git log -- <instruction-file>`, never from accumulated block.
4. **Dev-Value Gate (SKILL-SPEC §10.1):** every existing profile line must answer "would an AI assistant, reading this on every turn for 6 months, do meaningfully better engineering because of it?" with yes. Check each line against forbidden patterns (timestamps, score deltas, run dates, owner info, descriptions, onboarding, philosophy, vendor notes, file-by-file change notes). Forbidden found → strip before write. Report `{n} dev-value-gate lines stripped`.
5. **Context-budget guard:** after write, count lines between markers. > 25 → compress: merge multi-key lines (e.g. Type + Stack + Target into one), drop External entries with no purpose, drop Modules entries with role `(0)` or zero files. Re-count. Still > 25 → surface WARN with offending line indices.

**Gate:** Profile rewritten in minimal key-value format; legacy blocks rotated; no run-history in instruction file; Dev-Value Gate applied (forbidden lines stripped); profile ≤ 25 lines. If fails → write failed or file read-only → print updated `Scores:` line in chat for manual paste, note target file + marker positions, set state.data.profile_written false so subsequent runs know profile is stale; > 25 after compression → surface overshoot as WARN with offending line indices.

### Phase 8: Needs-Approval Review [needs_approval > 0]

`--auto` → list+skip. `--force-approve` → apply all. Interactive → present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → re-present each with forced binary prompt; user declines → mark `skipped (no response)`, proceed.

### Phase 8.5: Memory Cleanup [--memory-cleanup]

Optional phase. Scans AI agent memory index (`MEMORY.md` under host's project-memory directory — Claude Code: `~/.claude/projects/<hash>/memory/MEMORY.md`; equivalent for other hosts) and surfaces stale entries.

1. Open `MEMORY.md`. Absent or under 200 lines → skip with note "Memory index under threshold — no cleanup needed".
2. Parse `[[link]]` references; check each for a matching file in the memory directory.
3. Group findings: **Broken links** (`[[name]]` with no matching file — likely deleted memory); **Stale entries** (files referenced by zero `[[link]]`s — orphans); **Truncated** (index over 200 lines — Claude Code truncation threshold).
4. Present consolidation menu: `Delete broken links / Remove orphan files / Trim index / All / Skip`. Apply only what user approves. Every change reversible (memory dir is under user's home, not the repo).

**Gate:** Cleanup applied or user declined. If fails (memory dir not found) → skip silently, note "MEMORY.md not located — pass `--memory-cleanup` only when running inside a host that uses MEMORY.md".

### Phase 9: Summary

**Mandatory.** Always print.

```
blueprint: {OK|WARN|FAIL} | Health: {before}→{after}/{target} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Score: {n}/100
```

FRC+DSC accounting.

Status: OK (overall ≥ target), WARN (gap exists but progress), FAIL (CRITICAL unfixed or regression).

Open human-action items exist → repeat them after the summary line (`Human actions open: {n} — {comma-list of IDs}`); they carry over every run until the user resolves or dismisses them.

**Gate:** Summary printed with before/after + next steps. If fails → scores uncomputable (Phase 4 produced no scores, or previous scores absent from profile) → print with available scores, substitute `N/A` for missing, status `WARN`, note which phases need re-running.

**Value Delivered:** 1-5 concrete scoring outcomes. Example shapes (placeholders, not literal):

- `Project scored across 9 dimensions ({weakest-dim} {score}, target {target}) — focus is no longer guesswork; lowest-scoring dimension is the next investment`
- `{n} signals written to ds/audit/findings.md — downstream skills (ds-review, ds-fix, ds-simplify) skip their own detection and act directly`
- `Stack-fitness: {obsolete-or-oversized-dep} flagged — replacement candidate proposed with effort estimate`

Zero-finding run: `All 9 dimensions at or above target — no investment needed this cycle`.

## Quality Gates

- Every signal cites file:line — skip signals without evidence
- Only count signals from source code — exclude test, generated, vendored files
- Score reflects verified signals only — uncertain signals reduce to 0.5 weight
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/blueprint.json` updated per scope, gitignored, deleted on successful Summary. W10: SSOT producer — writes `ds/audit/findings.md` fresh on every run; consumers MUST defer to it. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

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
