---
name: ds-blueprint
description: Project health system — profile-based assessment, transformation, and progress tracking. Use when assessing overall project health, planning a transformation, or tracking improvement over time.
---

# /ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions and tells you exactly where to focus next.

**Project Health System** — Profile-based assessment, transformation, and progress tracking.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

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

**Dimensions:** B2, B4 (contributor), A9 (signal)

- Scores project health across 9 dimensions — signal counting, not file:line finding lists. Only modifies the profile section of the instruction file; suggests next steps but never invokes other skills or fixes code.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **Completeness requirement (SSOT):** `ds/audit/findings.md` is the single source of truth for every fix skill. Other skills skip their own detection when blueprint findings exist. Blueprint MUST detect ALL issues in each in-scope dimension — a missing finding will not be fixed downstream.
- **SSOT runtime enforcement (W10):** Every downstream consumer (ds-review, ds-fix, ds-simplify, ds-compliance, ds-mobile, etc.) MUST defer to a fresh `ds/audit/findings.md` — **fresh = `git_hash == HEAD` AND produced in the current run-cycle** (this invocation or the orchestration run it executes under). Fresh → consumers verify + apply only; they do NOT re-detect within blueprint's owned scopes. From a previous cycle (however recent), stale, or missing → **orchestrated** consumer invokes `/ds-blueprint --refresh` or `--preview --scope=all` and waits before continuing; **standalone** consumer announces `findings stale — running own {scopes} analysis` and runs its own scoped analysis, appending results with its own `source` + current `git_hash` (next blueprint full run dedups) — prior-cycle findings serve only as diff baseline (previously-flagged → resolved?). Re-detection within a covered scope in the same cycle is a W10 violation; skipping a re-scan because a previous cycle ran recently is a W11-class violation.
- **Overwrite-only persistence (SKILL-SPEC §10.1):** state, findings, profile rewritten every run — never appended. Run history lives in `git log -- <instruction-file>`, not in profile or any `ds/audit/` file. Append-only artifacts forbidden anywhere.
- **Human-action items:** findings whose remediation requires human-only access (branch protection, CI/repo secrets, store or account setup, key rotation, purchases) are surfaced as a distinct `Human actions` block in Dashboard and repeated in Summary — never silently dropped, never marked fixed by the AI.
- **Dev-Value Gate on every profile line:** the instruction file is re-read on every AI turn — every byte costs every future model read. A profile line is written only if it makes AI engineering measurably better on every turn for the next 6 months. Anything else (timestamps, score deltas, owner info, descriptions, philosophy) goes to README / CHANGELOG / git log / terminal summary instead.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |
| `--preview` | Analyze + dashboard, no changes |
| `--init` | Profile creation/refresh only (no analysis) — includes the Foundation pass |
| `--refresh` | Re-scan profile (decisions preserved; foundation lines untouched) |
| `--foundation` | Foundation pass alone: interrogate every normative profile decision (mission, target, priorities, constraints, red lines), propose better, perfect via user feedback |
| `--scope={x}` | Comma-separated: any findings scope name (references/scopes.md — e.g. security, testing, architecture, stack-fitness) or a dimension name (maps to its component scopes per references/weights.md); default `all`. Exclusions recorded in `filters_applied` |
| `--resume` | Resume from `ds/audit/blueprint.json` without prompting |
| `--clean` | Delete existing state, start fresh |
| `--memory-cleanup` | Optional phase: scan AI agent memory index (`MEMORY.md`) for stale `[[link]]` references + offer consolidation. Default OFF — opt-in only |

Without flags: present mode selection.

## Profile Storage

Profile embedded in project's AI instruction file between `## Blueprint Profile` and `## End Blueprint Profile` heading markers — markdown headings are universally preserved by every tool.


**Instruction file detection** — search for known AI instruction files (see [references/detection.md](references/detection.md) § Instruction Files). Use first match. None found: ask which tool user uses, create appropriate file. **Under `--auto`:** no prompt — default to `CLAUDE.md` (the most common AI instruction file) and create it.

**Profile format** — minimal, AI-parseable, calibration-only. Run history, score deltas, status messages NEVER go here — they live in `git log -- <instruction-file>`, `ds/audit/findings.md`, terminal summaries.

```markdown
## Blueprint Profile

Type: {type} | Stack: {stack} | Target: {quality}
Mission: {one line — who gets what outcome; the promise every downstream decision calibrates against}
Priorities: {comma-list} | Constraints: {comma-list}
Red lines: {comma-list of hard NOs — binding for every consumer}
Integrations: {google-workspace|apple-ecosystem|none}
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

**Format rules, read/write rules, and legacy-marker migration:** [references/profile-format.md](references/profile-format.md). Key-value pairs only, one value per line; only the `Scores:` line is rewritten on a normal run — foundation lines change only through the Foundation pass with per-line user confirmation.

## Delegation

**Owns:** security, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, contract-consistency, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs, spec-alignment, stack-fitness, external-tooling | **Delegates:** none (full-codebase SSOT producer; privacy scope produced by ds-compliance, canonical) | **Receives:** ds-review → bootstrap; ds-ship → Phase 0 bootstrap when findings absent or stale; ds-freeze → fresh promise census request

## Execution Flow

Discovery → [Init Flow] → Assess → Consolidate → Dashboard → [Suggest] → Update Profile → [Needs-Approval] → Summary

**Mandatory phases** (always execute, always produce output): Foundation Review, Assess, Consolidate, Dashboard, Update Profile, Summary. Skipping a mandatory phase is an execution bug.

### Phase 1: Discovery [PARALLEL]

**Recovery check:** DETECT `ds/audit/blueprint.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`; `--auto` resumes silently). Resume → RE-VERIFY `in_progress` phase (re-scan modified scopes, keep completed scopes), skip `done` phases, announce `[BP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/` in `.gitignore` on fresh start.

**State `data`:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, severity, file, line}]}, profile_written: bool, scores: {dimension: score}, instruction_file }`.

1. **Mode selection.** No flags → present a menu covering every mode, each with a one-line what-it-does: Full Analysis (recommended) — detect + analyze every dimension / Preview Only — analyze, no profile write / Init Profile — seed a fresh profile (includes Foundation pass) / Refresh Profile — re-score an existing profile / Foundation — interrogate + perfect the profile's normative decisions / (Cancel). A disambiguating flag skips the menu.
2. Search for `## Blueprint Profile` heading in known instruction files; read existing profile to detect incremental vs full run.
3. Detect project via three-step process from [references/detection.md](references/detection.md): (1) stack from manifest files (pubspec.yaml, package.json, go.mod, etc.); (2) project type from secondary signals (framework deps, config, directory structure); (3) supplementary stacks (Docker, shell scripts, CI, task runners). Also: toolchain, tests, data sensitivity, git status, ecosystem integrations (references/detection.md § Step 4 — feeds `Integrations:` profile field).

**Decision tree** (every route through 1-2 runs the Foundation Review first — it is mandatory on every run):
1. Profile exists + not --init/--refresh/--foundation → Foundation Review → Phase 3 (incremental)
2. Profile exists + --refresh → Phase 2 (re-ask, preserve decisions; foundation lines untouched)
3. Profile exists + --foundation → Phase 2 Foundation pass only (interrogate + perfect normative lines, stop after write)
4. No profile + --init → Phase 2 (create with Foundation pass, stop)
5. No profile + not --init → Phase 2 (create with Foundation pass, ask to continue)

**Gate:** Mode selected; project type detected; instruction file located or creation path determined. If fails → type undetectable (no manifest, empty repo) + no user response to type prompt → default `generic`, mode `Full Analysis`, instruction file `CLAUDE.md`, WARN `"Project type undetected — defaulted to generic"` in state.data, proceed.

### Phase 2: Init Flow + Foundation (no profile OR --init/--refresh/--foundation)

**Foundation pass** (full interrogation on `--init`, `--foundation`, and first-time profile creation; **every other run — full analysis, `--refresh`, `--preview` — includes the Foundation Review step below**, because a more capable model may now derive a better foundation than the one confirmed earlier — model uplift is itself new evidence). The profile's normative lines calibrate every downstream skill — they are perfected deliberately, never form-filled:

1. **Evidence sweep** — collect what the project *is* and *claims*: README/docs promises, code capabilities, git history, existing profile lines, prior user statements. Every proposed value in steps 2-3 cites its evidence; a gap is asked, never guessed.
2. **Idealized draft** — synthesize the best-supported foundation: `Mission` (one line, who-gets-what-outcome), `Target`, ranked `Priorities`, and the constraint set split honestly into `Constraints` (soft preferences) vs `Red lines` (hard NOs). Where the evidence supports a sharper mission or a stronger target than currently stated, draft the sharper version — idealize from evidence, never from invention.
3. **Decision interrogation** — for EVERY normative line (Type, Target, Mission, each Priority, each Constraint, each Red line, Audience, Deploy), existing or proposed: (a) state the current value and the rationale/evidence behind it; (b) challenge it — does the evidence still support it? does it earn its keep? A constraint with no identifiable protective value → removal proposal stating what it costs and what removing it frees; (c) when a better alternative exists, propose it with concrete rationale (what improves, at what cost). No line passes unexamined.
4. **Approval + feedback loop** — present steps 2-3 as one per-line decision table: `current → proposed | evidence | rationale`, ask per line: accept / edit / keep-current. All foundation decisions are **Category B — never auto-applied**: under `--auto` keep detected/existing values and mark `foundation: unconfirmed` in the summary instead of deciding for the user. Apply feedback, re-present only the changed lines, iterate until every line is confirmed.
5. **Decision durability** — a user-confirmed line is settled: it never silently flips, and it is re-raised only with named cause — new project evidence, or a materially better derivation from a more capable model (see Foundation Review). Re-litigating an unchanged conclusion is forbidden (W13); proposing a genuinely better one with stated rationale is the job.

**Foundation Review (every run, mandatory, ~1 minute):** re-derive the ideal foundation from current evidence with the current model, then diff against the confirmed lines. Identical or merely-reworded → print one line `Foundation holds ({n} lines, last confirmed under model {m})` and continue — both values mandatory: `{n}` = count of foundation lines diffed, `{m}` read from `git log`; a holds verdict missing either value is an execution bug (it signals the re-derivation was skipped, not performed). Materially better on any line → present only those lines as `current → proposed | what improves | why` for user decision — a proposal must articulate a concrete improvement (sharper mission, unfounded constraint found, missing red line); rewording is not a proposal. Under `--auto`: run the review, list any proposals in the summary as `foundation-proposals: {n} (pending)`, apply nothing. The reviewing model is already recorded as `model=` on the `Scores:` line — "last confirmed under model {m}" reads from `git log -- <instruction-file>` for the commit that last changed a foundation line; no extra profile line (Dev-Value Gate).

**Init questions** (fallback shell of the pass — each question's auto-detected value is the default; answers feed steps 2-3 as user evidence):

| Question | Options |
|----------|---------|
| Category | Frontend / Backend / Developer Tool / Infrastructure |
| Quality level | Prototype / MVP / Production / Enterprise |
| Data handled | Personal info / Sensitive data / Auth credentials / None |
| Focus areas | Security / Code Quality / Architecture / Documentation |
| Constraints | Keep framework / Preserve public APIs / Minimize new dependencies / None |
| Users | Public / Internal team / Other developers / Local-undecided |

**Data fallback:** PII/credential scan finds nothing → ask "Does this project process user data? (Yes — describe data types / No)" so `Config.data` is set explicitly, not by inference alone.

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

**Gate:** Profile written with all sections; every foundation line either user-confirmed or explicitly marked `foundation: unconfirmed` (`--auto`) — a foundation line is never silently auto-decided. If fails → write failed (permissions, invalid path, tool doesn't support file creation) → save profile to `ds/audit/blueprint-profile-draft.md`, display full text in chat for manual paste, surface write error with target path.

### Phase 2.5: Parallel-Track Planning [PARALLEL]

Group 9 dimensions × 24 scopes by execution cost — plan concurrency consciously.

| Batch | Scopes | Concurrency | Why |
|-------|--------|-------------|-----|
| **Read-only** | hygiene, types, doc-sync, dx, docs, spec-alignment, stack, stack-fitness, external-tooling | Parallel — pure grep/file-read, no AST | Cheapest scans, no shared state |
| **AST** | architecture, patterns, cross-cutting, maintainability, simplify, ai-architecture, contract-consistency, performance | Parallel — shared LSP/AST cache | Share parse work across detectors |
| **Cross-file** | security, privacy, ai-hygiene, robustness, production-readiness, testing, functional-completeness | Serial — each batch may modify findings index | Order matters for dedup |

Plan batches up front (`state.data.batches`) and announce before starting. AI hosts route parallelism — the spec declares which scopes are safe to run together.

**Gate:** Batches planned + announced. If fails (no detectable scopes) → mark plan empty, proceed to Summary with WARN.

### Phase 3: Assess (scan, record, score — don't fix)

Scan **entire codebase**, record every finding with file:line to `ds/audit/findings.md`, score dimensions from these findings — do NOT fix. Fix skills read `ds/audit/findings.md` and skip own detection (eliminates duplicate analysis) → blueprint must detect ALL issues within each dimension; missing finding = won't be fixed.

**Dimension → Scope mapping**, **assessment patterns per dimension**, the **churn × complexity hotspot pass**, the **external hygiene cross-check**, and the **false-positive guard** every signal must clear: [references/assessment-patterns.md](references/assessment-patterns.md). Only HIGH and MEDIUM confidence signals are written to `ds/audit/findings.md`.

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
2. **Score calibration checks** — verify sanity before presenting: overall in 20-95 for real projects (0 or 100 suspicious — re-verify); no individual dimension at 100 (re-check for missed signals); CRITICAL finding present → overall must be < 80 (else scoring error); adjacent dimension delta < 30 (e.g. architecture 90 but code quality 50 → investigate); Code Quality > 80 while Security & Privacy < 50 → re-verify both scans (the two signal sets correlate — a wide split suggests one scan missed signals). Any fail → re-read flagged dimension's signals + adjust.
3. Write `ds/audit/findings.md` in this format:
   ```
   <!-- findings-meta
   git_hash: {HEAD}
   timestamp: {ISO 8601}
   source: ds-blueprint
   skillset: {dev-skills@hash | unknown}
   scopes: security, privacy, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, contract-consistency, performance, robustness, production-readiness, testing, functional-completeness, stack, stack-fitness, dx, external-tooling, docs, spec-alignment
   -->
   ```
   `skillset:` = the rule-set version that performed this scan — read `.dev-skills-version` beside the host's installed skills directory (e.g. `~/.claude/skills/.dev-skills-version`); absent → `unknown`. Prior-cycle findings carrying a **different** `skillset` → announce `rule-set delta: {old} → {new}` in the dashboard and summary: previously-clean scopes flagging now is expected new detection under upgraded rules, not project regression — never suppress such findings as "was clean last time".
   ```

   ## Findings

   | ID | Severity | Category | File | Line | Scope | Title |
   |----|----------|----------|------|------|-------|-------|
   | {id} | {severity} | {A|B} | {file} | {line} | {scope} | {title} |
   ```
   Every finding includes file:line so fix skills can act directly. Category A when fix conforms to current architecture/plan; B when it changes architecture/scope/capability/user-promise/dependency.
4. **Verify completeness:** count distinct scopes in `ds/audit/findings.md`. Expected: the 24 blueprint-owned scopes above, minus any recorded in `filters_applied.skipped_scope` (quality-level or `--scope` exclusions — see references/detection.md § Audit Fields). `ideal-gap` is produced externally by `/ds-benchmark` — count it when present, never re-run for its absence. Blueprint-owned count below expectation → identify missing scopes and re-run assessment for those before proceeding. Missing scope = fix skills skip detection → missed issues.

**Gate:** All 9 scores calculated; calibration passed; `ds/audit/findings.md` written with all 25 scopes verified. If fails → calibration suspicious score (dimension at 100, CRITICAL with overall ≥80) → re-read flagged signals + adjust; missing scopes → re-run assessment for each before writing; write fails → surface OS error, ask user to resolve.

### Phase 5: Dashboard

**Mandatory.** Always display, even in `--auto`.

Render templates — score table, below-target findings list, score-drop explanation, human-actions block: [references/dashboard-format.md](references/dashboard-format.md). First run omits the Prev and Delta columns; the human-actions block is omitted when empty.

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

**Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. **Under `--auto`:** no approval block shown — every item, including CRITICAL, resolves via the same impact/effort/risk reasoning the review step would show, applied and recorded `fixed`/`failed`; items matching the irreversible-exception list resolve `skipped (needs-human)` instead.

**Gate:** All items resolved. If fails → unresolved → re-present each with forced binary prompt; user declines → mark `skipped (no response)`, proceed.

### Phase 8.5: Memory Cleanup [--memory-cleanup]

Optional phase. Scans AI agent memory index (`MEMORY.md` under host's project-memory directory — Claude Code: `~/.claude/projects/<hash>/memory/MEMORY.md`; equivalent for other hosts) and surfaces stale entries.

1. Open `MEMORY.md`. Absent or under 200 lines → skip with note "Memory index under threshold — no cleanup needed".
2. Parse `[[link]]` references; check each for a matching file in the memory directory.
3. Group findings: **Broken links** (`[[name]]` with no matching file — likely deleted memory); **Stale entries** (files referenced by zero `[[link]]`s — orphans); **Truncated** (index over 200 lines — Claude Code truncation threshold).
4. Present consolidation menu: `Delete broken links / Remove orphan files / Trim index / All / Skip`. Apply only what user approves. Every change reversible (memory dir is under user's home, not the repo). **Under `--auto`:** no menu — apply the full cleanup (delete broken links, remove orphans, trim index) since every change is reversible, and record it in the summary.

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

**Value Delivered:** 1-5 concrete scoring outcomes. Every bullet's effect clause is plain everyday language a non-technical reader understands — concrete benefit, quantified when measurable ("under ~1k concurrent users, pages respond ~40% faster"), never the mechanical activity (SKILL-SPEC §5 rule 8). Example shapes (placeholders, not literal):

- `Project scored across 9 dimensions ({weakest-dim} {score}, target {target}) — focus is no longer guesswork; lowest-scoring dimension is the next investment`
- `Foundation perfected: mission sharpened from evidence, {n} constraints challenged ({m} removed as unfounded), {k} red lines made explicit — every downstream skill now calibrates against a confirmed foundation instead of a form-fill`
- `{n} signals written to ds/audit/findings.md — downstream skills (ds-review, ds-fix, ds-simplify) skip their own detection and act directly`
- `Stack-fitness: {obsolete-or-oversized-dep} flagged — replacement candidate proposed with effort estimate`

Zero-finding run: `All 9 dimensions at or above target — no investment needed this cycle`.

## Quality Gates

- Every signal cites file:line — skip signals without evidence
- Only count signals from source code — exclude test, generated, vendored files
- Score reflects verified signals only — uncertain signals reduce to 0.5 weight

| Guard | Rule |
|-------|------|
| W1 | Cite file:line; never assume |
| W2 | Check consumers after modify |
| W3 | Touch only task-required lines |
| W4 | Re-read after gap |
| W5 | Uncertain → lower severity |
| W6 | Verify all phases output |
| W7 | Dedup file:line |
| W8 | No raw shell interpolation |
| W9 | `ds/audit/blueprint.json` updated per scope, gitignored, deleted on successful Summary |
| W10 | SSOT producer — writes `ds/audit/findings.md` fresh every run; consumers MUST defer to it |
| W11 | Every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason |

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
| No instruction file found | Create new profile, ask user for target file location. Under `--auto`: default to `CLAUDE.md`, no prompt. |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
