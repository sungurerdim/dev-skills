---
name: ds-blueprint
description: Project health system — profile-based assessment, transformation, and progress tracking. Use when assessing overall project health, planning a transformation, or tracking improvement over time.
---

# /ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions, writes the signal inventory every other skill scopes itself by, and tells you exactly where to focus next.

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
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent. Shared formats: [../core/findings-and-profile-format.md](../core/findings-and-profile-format.md); signal keys and detection: [../core/signal-inventory.md](../core/signal-inventory.md); severity and score: [../core/severity-score-categories.md](../core/severity-score-categories.md).
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Completeness requirement (SSOT):** `ds/audit/findings.md` is the single source of truth for every fix skill. Other skills skip their own detection when blueprint findings exist. Blueprint MUST detect ALL issues in each in-scope dimension — a missing finding will not be fixed downstream.
- **SSOT runtime enforcement (W10):** every downstream consumer (ds-review, ds-fix, ds-simplify, ds-compliance, ds-mobile, …) defers to a fresh `ds/audit/findings.md` — **fresh = `git_hash == HEAD` AND produced in the current run-cycle** (this invocation or the orchestration run it executes under). Fresh → consumers verify + apply only; they do NOT re-detect within blueprint's owned scopes. Prior cycle, stale, or missing → an **orchestrated** consumer invokes `/ds-blueprint --refresh` and waits; a **standalone** consumer announces `findings stale — running own {scopes} analysis`, runs its own scoped analysis and appends with its own `source` + current `git_hash` — prior-cycle findings serve only as diff baseline. Re-detection within a covered scope in the same cycle is a W10 violation; skipping a re-scan because a previous cycle ran recently is a W11-class violation.
- **Privacy has one owner.** `privacy` findings are produced by ds-compliance (canonical). Blueprint consumes them for the Security & Privacy dimension when present; absent → the dimension is scored from `security` alone and the dashboard says `privacy: not scanned (ds-compliance)`. Blueprint never writes `privacy` rows.
- **Overwrite-only persistence:** state, findings, profile rewritten every run — never appended. Run history lives in `git log -- <instruction-file>`, not in profile or any `ds/audit/` file.
- **Human-action items:** findings whose remediation requires human-only access (branch protection, CI/repo secrets, store or account setup, key rotation, purchases) are surfaced as a distinct `Human actions` block in Dashboard and repeated in Summary — never silently dropped, never marked fixed by the AI.
- **Dev-Value Gate on every profile line:** the instruction file is re-read on every AI turn. A profile line is written only if it makes AI engineering measurably better on every turn for the next 6 months; timestamps, deltas, owner info, descriptions, philosophy go to README / CHANGELOG / git log / terminal summary instead.
- State: `ds/audit/blueprint.json` (a full 9-dimension scan holds its progress nowhere else; an interruption would restart it from zero).

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |
| `--ask` | Interactive run — mode menu, per-line Foundation interrogation, and approval prompts at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary. |
| `--preview` | Analyze + dashboard in chat only — writes nothing: no profile, no `ds/audit/findings.md`, no state |
| `--init` | Profile creation (or re-creation) with the Foundation pass; no dimension analysis |
| `--refresh` | Fast path: re-detect Type/Stack/Toolchain/`Signals:`, rescore, rewrite `Scores:` + `Signals:`; foundation lines untouched, no interrogation |
| `--scope={x}` | Comma-separated: any findings scope name (references/scopes.md — e.g. security, testing, architecture, stack-fitness) or a dimension name (maps to its component scopes per references/weights.md); default = the scope-resolution table below. Exclusions recorded in `filters_applied` |
| `--resume` | Resume from `ds/audit/blueprint.json` without prompting |
| `--clean` | Delete existing state, start fresh |

Without flags: profile absent → create it (Foundation derived from evidence, marked `derived`) and run Full Analysis; profile present → Full Analysis (incremental). `--ask` presents the mode menu instead: Full Analysis (recommended) / Preview only / Init profile / Refresh profile / (Cancel).

## Profile Storage

Profile embedded in project's AI instruction file between `## Blueprint Profile` and `## End Blueprint Profile` heading markers — markdown headings are universally preserved by every tool.

**Instruction file selection** (first match wins): an existing file from the list in [references/detection.md](references/detection.md) § Instruction Files. None found → pick by host evidence: `.claude/` directory or `~/.claude` present → `CLAUDE.md`; `.cursor/` → `.cursor/rules/blueprint.md`; `.github/` with Copilot signals → `.github/copilot-instructions.md`; `.windsurf/` or `.devin/` → that rules directory; otherwise `AGENTS.md` (the cross-tool standard). `--ask` → ask which tool the user runs before creating anything. The chosen file and the evidence for it are recorded in the summary.

**Profile format** — minimal, AI-parseable, calibration-only. Run history, score deltas, status messages NEVER go here — they live in `git log -- <instruction-file>`, `ds/audit/findings.md`, terminal summaries.

```markdown
## Blueprint Profile

Type: {type} | Stack: {stack} | Target: {quality}
Mission: {one line — who gets what outcome; the promise every downstream decision calibrates against}
Signals: ui={…} api={…} db={…} auth={…} billing={…} pii={yes|no} i18n={yes|no} tests={…} ci={…} deploy={…} platforms={…} audience={…} jurisdiction={…} integrations={…} mobile={…}
Priorities: {comma-list} | Constraints: {comma-list}
Red lines: {comma-list of hard NOs — binding for every consumer}
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

`Integrations:` is the comma list from detection.md § Step 4 (`none` when nothing matches); it is also mirrored inside `Signals:` as `integrations=`. Format rules, read/write rules, the 25-line ceiling and legacy-marker migration: [references/profile-format.md](references/profile-format.md). Only `Scores:` and `Signals:` are rewritten on a normal run — foundation lines change only through the Foundation pass.

## Delegation

**Owns:** security, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, contract-consistency, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs, spec-alignment, stack-fitness, external-tooling | **Delegates:** none (full-codebase SSOT producer; privacy scope produced by ds-compliance, canonical) | **Receives:** ds-review → bootstrap; ds-ship → Phase 0 bootstrap when findings absent or stale; ds-freeze → fresh promise census request

## Execution Flow

Discovery → [Foundation] → Assess → Consolidate → Dashboard → [Suggest] → [Update Profile] → [Needs-Approval] → Summary

**Mandatory phases** (always execute, always produce output): Discovery, Assess, Consolidate, Dashboard, Summary. Update Profile is mandatory except under `--preview`. Skipping a mandatory phase is an execution bug.

### Phase 1: Discovery [PARALLEL]

**Recovery check:** DETECT `ds/audit/blueprint.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, compare state `git_hash` against `git rev-parse HEAD` output. Mismatch → resume anyway (the in-progress phase re-verifies); `--ask` → prompt `Resume anyway? [Y/n]`. Resume → RE-VERIFY `in_progress` phase (re-scan modified scopes, keep completed scopes), skip `done` phases, announce `[BP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. On fresh start: `grep -qxF 'ds/audit/' .gitignore` → exit 0; non-zero → append the `ds/audit/` line (never under `--preview`).

**State `data`:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, severity, file, line}]}, signals: {key: value}, profile_written: bool, scores: {dimension: score}, instruction_file }`.

1. **Mode.** Resolve from flags and profile presence (Arguments table); `--ask` → menu.
2. **Profile read.** Search for `## Blueprint Profile` in the known instruction files; existing profile → incremental run (Type/Stack/Toolchain reused, foundation lines reused), else full detection.
3. **Detection** via [references/detection.md](references/detection.md): (1) stack from manifests; (2) project type from secondary signals; (3) supplementary stacks (Docker, shell, CI, task runners); (4) ecosystem integrations (§ Step 4) and transactional messaging (§ Step 5); toolchain, tests, data sensitivity, git posture.
4. **Signal inventory.** Resolve every key in [../core/signal-inventory.md](../core/signal-inventory.md) from the detection results; unresolvable → `unknown`, never guessed. This is the `Signals:` line, and it drives the scope-resolution table in Phase 3.
5. **Skillset stamp.** Read `.dev-skills-version` beside the host's installed skills directory (e.g. `~/.claude/skills/.dev-skills-version`); absent → `unknown`.

**Decision tree:**
1. Profile exists + no `--init`/`--refresh` → Phase 3 (incremental); foundation lines missing from the profile → Phase 2 first, `derived` mode.
2. Profile exists + `--refresh` → Phase 3 with fresh detection; Phase 7 rewrites `Scores:` + `Signals:` only.
3. `--init` (profile present or not) → Phase 2 (Foundation pass), then stop after the profile write.
4. No profile + no `--init` → Phase 2 in `derived` mode, then continue to Phase 3.

**Gate:** Mode resolved; project type detected; every signal key resolved or `unknown`; instruction file located or its creation path determined with evidence. If fails → type undetectable (no manifest, empty repo) → default `generic`, mode Full Analysis, instruction file per the host-evidence rule, WARN `"Project type undetected — defaulted to generic"` in state.data, proceed.

### Phase 2: Foundation [--init | profile lacks foundation lines]

The profile's normative lines (`Mission`, `Target`, `Priorities`, `Constraints`, `Red lines`, `Audience`, `Deploy`) calibrate every downstream skill — they are derived deliberately, never form-filled.

1. **Evidence sweep** — what the project *is* and *claims*: README/docs promises, code capabilities, git history, existing profile lines, prior user statements. Every proposed value cites its evidence.
2. **Idealized draft** — `Mission` (one line, who-gets-what-outcome), `Target`, ranked `Priorities`, constraints split honestly into `Constraints` (soft) vs `Red lines` (hard NOs). Where the evidence supports a sharper mission or a stronger target than stated, draft the sharper version — from evidence, never from invention.
3. **Decision interrogation** — for every normative line: (a) current value + evidence; (b) does the evidence still support it, does it earn its keep (a constraint with no protective value → removal proposal stating what it costs and what removing it frees); (c) a better alternative with concrete rationale when one exists.
4. **Resolution.** Default (`derived` mode): write the best-evidenced value for every line, mark the profile write `foundation: derived-from-evidence` in the summary, and list every line whose evidence was thin as `needs-human: confirm {line}` — a thin-evidence line is written with the most conservative reading (private, free/internal, keep framework) and never invented. `--ask`: present one per-line table `current → proposed | evidence | rationale`, ask per line accept / edit / keep-current, iterate until every line is confirmed.
5. **Decision durability** — a user-confirmed line is settled: it never silently flips, and it is re-raised only with named cause (new project evidence, or a materially better derivation on `--init --ask`). Re-litigating an unchanged conclusion is forbidden (W13).

**Data fallback:** PII/credential scan finds nothing → `pii=no` with the note "PII scan negative — verify manually if the project handles user data indirectly (e.g. via external APIs)"; `--ask` → ask "Does this project process user data?".

Write the profile to the selected instruction file (`--preview` → print it in chat instead). Calculate ideal metrics from [references/weights.md](references/weights.md). Quality-level descriptions: [references/quality-levels.md](references/quality-levels.md).

**Gate:** Profile block present between the markers with every line; every foundation line either user-confirmed (`--ask`) or marked `derived-from-evidence` with its evidence — never silently auto-decided. If fails → write failed (permissions, invalid path, tool cannot create files) → save the profile to `ds/audit/blueprint-profile-draft.md`, display the full text in chat for manual paste, surface the write error with the target path.

### Phase 3: Assess (scan, record, score — don't fix)

**Scope resolution — signals decide what runs.** Every scope resolves before scanning and is echoed in the dashboard and summary as `ran` / `N/A — {signal}=none` / `unknown → ran`. `--scope=` overrides the table for the named scopes; an `unknown` signal never excludes a scope.

| Scope(s) | Runs when | Otherwise |
|----------|-----------|-----------|
| security, hygiene, types, doc-sync, maintainability, patterns, architecture, cross-cutting, contract-consistency, simplify, robustness, testing, functional-completeness, stack, stack-fitness, docs, spec-alignment, dx | source files present (`size` ≠ empty) | N/A — no source |
| ai-hygiene | always (AI-authored residue exists in every codebase touched by an assistant) | — |
| ai-architecture | integrations contain an LLM SDK (`openai`, `anthropic`, `gemini`, `ollama`, `langchain`, `vercel/ai`) or prompt templates exist | N/A — no LLM surface |
| performance | api ≠ none or db ≠ none or ui ≠ none | N/A — pure library/CLI without I/O paths (still scanned when `size=large`) |
| production-readiness | deploy ≠ none or api ≠ none | N/A — nothing is deployed |
| external-tooling | ci ≠ none or `.github/`/`.gitlab-ci.yml`/hooks present | N/A — no automation surface |
| privacy | never here — consumed from ds-compliance findings when present | `privacy: not scanned (ds-compliance)` |

Scan the **entire codebase** for every resolved scope, record every finding with file:line, score dimensions from these findings — do NOT fix. Fix skills read `ds/audit/findings.md` and skip their own detection, so blueprint must detect ALL issues within each dimension; a missing finding = won't be fixed.

**Concurrency batches** — read-only (pure grep/file-read), AST (shared parse cache), cross-file (serial; each pass may modify the findings index): [references/scopes.md](references/scopes.md). Plan the batches in `state.data.batches` and announce them before starting.

**Dimension → scope mapping**, the **assessment patterns per dimension**, the **churn × complexity hotspot pass**, the **external hygiene cross-check**, and the **false-positive guard** every signal must clear: [references/assessment-patterns.md](references/assessment-patterns.md). Only HIGH and MEDIUM confidence signals are written to `ds/audit/findings.md`. Principles behind the architecture, reliability, security and testing detectors: [../core/principles.md](../core/principles.md) §2, §4, §5, §7.

Scoring formula from [references/scopes.md](references/scopes.md), dimension weights from [references/weights.md](references/weights.md).

**User-facing project gate:** `ui` ≠ none → additionally check: i18n setup present (framework-native catalog, ≥1 locale file); default locales configured (minimum: en + project owner's locale); a11y basics (semantic labels on interactive elements, contrast ratio, screen-reader support); responsive layout (breakpoints or adaptive layout). Flag missing items as HIGH severity. `ui=none` → N/A.

**Gate:** Every resolved scope scanned; every signal has file:line evidence; false-positive checks applied. If fails → scope un-scan-able (codebase too large, binary-only files, access denied) → mark it `confidence: inconclusive` in state.data.findings_per_scope, continue scoring with available signals only, flag `[PARTIAL SCAN]` in the dashboard so scores read as lower bounds.

### Phase 3.1: Project Map

Build from Discovery + Assess:

1. **Entry point:** main entry file(s) + framework.
2. **Modules:** each top-level module dir with role, file count, key files + responsibilities — enough for a new developer to understand, not a full listing.
3. **Data Flow:** trace the primary user-facing flow end-to-end (e.g. {source}→auth→process→store→{sink}), including intermediate systems (queues, caches, external services).
4. **External:** runtime dependencies with purpose (not dev tools), grouped: databases, caches, queues, auth, third-party APIs.
5. **Toolchain:** format/lint, test framework, CI platform, container.

**Gate:** Project map generated with entry, modules, data flow, externals. If fails → entry or flow undeterminable → write the map with `unknown` placeholders, WARN `"Project map incomplete — manual review required for: {list}"` in the summary, continue with the partial map.

### Phase 4: Consolidate

**Mandatory.** Always score dimensions; write `ds/audit/findings.md` unless `--preview`.

1. Apply dimension score aggregation + weight matrix from [references/weights.md](references/weights.md). Run calibration checks.
2. **Score calibration checks** — overall in 20-95 for real projects (0 or 100 suspicious — re-verify); no individual dimension at 100 (re-check for missed signals); CRITICAL finding present → overall < 80 (else scoring error); adjacent dimension delta < 30; Code Quality > 80 while Security & Privacy < 50 → re-verify both scans. Any fail → re-read the flagged dimension's signals + adjust.
3. Write `ds/audit/findings.md` in the shared format ([../core/findings-and-profile-format.md](../core/findings-and-profile-format.md) § 1): meta `git_hash`, `timestamp`, `source: ds-blueprint`, `skillset: {dev-skills@hash | unknown}`, `scopes:` = every scope that **ran** (Phase 3 table), `signals:` = the resolved Signals line, `filters_applied:` = N/A scopes with their signal reason + `--scope` exclusions. Every row carries file:line and Category A (conforms to the current architecture/plan) or B (changes architecture/scope/capability/user-promise/dependency). Prior-cycle findings carrying a **different** `skillset` → announce `rule-set delta: {old} → {new}` in the dashboard and summary: previously-clean scopes flagging now is expected new detection, not project regression.
4. **Verify completeness mechanically:** `awk -F'|' '/^\|/{gsub(/ /,"",$7); print $7}' ds/audit/findings.md | sort -u` → the distinct Scope-column values (drop the header's literal `Scope`). Expected: exactly the scopes that ran. `ideal-gap` (ds-benchmark) and `privacy` (ds-compliance) are counted when present, never re-run for their absence. A scope that ran but is absent → re-run its assessment before proceeding.

**Gate:** All 9 scores calculated; calibration passed; `ds/audit/findings.md` written with every ran scope verified (or, under `--preview`, the same table printed in chat). If fails → calibration suspicious → re-read flagged signals + adjust; missing scopes → re-run each before writing; write fails → surface the OS error, print the table in chat.

### Phase 5: Dashboard

**Mandatory.** Always display.

Render the score table, the scope-resolution line (`Scopes: ran {n} · N/A {m} ({scope}={signal}=none …)`), below-target findings, score-drop explanation, and the human-actions block: [references/dashboard-format.md](references/dashboard-format.md). First run omits the Prev and Delta columns; the human-actions block is omitted when empty.

**Gate:** Dashboard displayed with all dimensions, scores, delta (if applicable), gap analysis, scope resolution; `test -s ds/audit/findings.md` → exit 0 (skipped under `--preview`). If fails → write unconfirmed → retry once; still failing → print the dashboard with `[WARN: findings.md not written]` so the user sees scores but knows downstream consumers cannot use them until resolved.

### Phase 6: Suggest [SKIP if --preview]

List dimensions below target with signal counts. No skill-specific commands — the findings file is the interface.

```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}) — {n} signals

→ ds/audit/findings.md written with {n} signals. Run your preferred fix tool/skill to resolve.
```

**Gate:** Suggestions generated for all below-target dimensions. If fails → all dimensions at/above target → print `"All dimensions at or above target — no suggestions needed"`, proceed.

### Phase 7: Update Profile [SKIP if --preview]

1. Rewrite the `Scores:` line (single line, key-value; `model={model-id}` = the model performing this assessment, `model=unknown` when not determinable) and the `Signals:` line. `--refresh` also rewrites `Type`/`Stack`/`Toolchain`/`Integrations` from fresh detection.
2. Legacy `### Last Run`, `### Run History`, `### Current Scores` (table) blocks from a previous version → rewrite the entire profile to the minimal key-value format; report `{n} legacy lines rotated to git log`. Never re-inject historical run data.
3. Previous scores existed → display the delta table in chat (Prev / Curr / Δ). Trend over >1 run → `git log -- <instruction-file>`, never an accumulated block.
4. **Dev-Value Gate:** strip every forbidden line class (timestamps, deltas, run dates, owner info, descriptions, onboarding, philosophy, vendor notes, file-by-file notes) before the write; report `{n} dev-value-gate lines stripped`.
5. **Context-budget guard:** `sed -n '/^## Blueprint Profile/,/^## End Blueprint Profile/p' {instruction-file} | wc -l` → ≤ 27 (25 content lines + 2 markers). Over → compress (merge multi-key lines, drop External entries without a purpose, drop Modules entries with role `(0)` or zero files), re-count; still over → WARN with the offending line indices.

**Gate:** Profile rewritten in minimal key-value format with fresh `Scores:` + `Signals:`; legacy blocks rotated; Dev-Value Gate applied; ≤ 25 lines. If fails → write failed or file read-only → print the updated lines in chat for manual paste, note the target file + marker positions, set state.data.profile_written false so subsequent runs know the profile is stale.

### Phase 8: Needs-Approval Review [--ask, needs_approval > 0]

Present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. Without `--ask` this phase does not run: every item resolves by the same impact/effort/risk reasoning, is recorded `fixed`/`failed` in the summary, and items on the publish/irreversible exception list ([../core/ask-exception-list.md](../core/ask-exception-list.md)) resolve `skipped (needs-human)`.

**Gate:** All items resolved. If fails → unresolved → re-present each with a forced binary prompt; user declines → mark `skipped (no response)`, proceed.

### Phase 9: Summary

**Mandatory.** Always print.

```
blueprint: {OK|WARN|FAIL} | Health: {before}→{after}/{target} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Score: {n}/100
Scopes: ran {n} · N/A {m} · Signals: {the resolved line} · Profile: {file} ({written | preview — not written}) · Foundation: {confirmed | derived-from-evidence | unchanged}
```

Disposition accounting — totals balance. Status: OK (overall ≥ target), WARN (gap exists but progress), FAIL (CRITICAL unfixed or regression). Open human-action items → `Human actions open: {n} — {comma-list of IDs}`; they carry over every run until the user resolves or dismisses them. Thin-evidence foundation lines → `needs-human: confirm {line}` listed in full. Closing shape: [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Gate:** Summary printed with before/after + next steps + scope resolution. If fails → scores uncomputable → print with available scores, `N/A` for missing, status `WARN`, note which phases need re-running.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `Project scored across 9 dimensions ({weakest-dim} {score}, target {target}) — focus is no longer guesswork; the lowest-scoring dimension is the next investment`
- `Signal inventory written ({n} keys resolved, {m} unknown) — every later skill scans only the scopes this project actually has instead of everything`
- `{n} signals written to ds/audit/findings.md — downstream skills (ds-review, ds-fix, ds-simplify) skip their own detection and act directly`
- `Stack-fitness: {obsolete-or-oversized-dep} flagged — replacement candidate proposed with effort estimate`

Zero-finding run: `All 9 dimensions at or above target — no investment needed this cycle`.

## Quality Gates

- Every signal cites file:line — skip signals without evidence
- Only count signals from source code — exclude test, generated, vendored files
- Score reflects verified signals only — uncertain signals reduce to 0.5 weight
- `--preview` writes nothing — no profile, no findings, no state, no `.gitignore` edit; a preview that left a file behind is a bug
- W9: `ds/audit/blueprint.json` updated per scope, gitignored, deleted on successful Summary
- W10: SSOT producer — writes `ds/audit/findings.md` fresh every run; consumers MUST defer to it
- W1: Cite file:line; never assume. W2: Check consumers after modify. W3: Touch only task-required lines. W4: Re-read after gap. W5: Uncertain → lower severity. W6: Verify all phases output. W7: Dedup file:line. W8: No raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Codebase too large for full scan | Apply saturation gate after 3 dimensions, extrapolate remaining, mark `[PARTIAL SCAN]` |
| Blueprint profile write fails | Save to `ds/audit/blueprint-profile-draft.md`, warn user, suggest manual placement |
| Previous profile format incompatible | Write new profile alongside, let user decide when to remove old |
| Scoring dimension has zero signals | Score as N/A, exclude from overall calculation |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project | Report baseline scores, note no code to assess; every signal `none` or `unknown` |
| Monorepo | Score each workspace independently, aggregate in summary; one `Signals:` line per workspace joined with `;` when they differ |
| No instruction file found | Create the file chosen by the host-evidence rule (Profile Storage); `--ask` → ask which tool first |
| Profile from an older version without `Signals:` | Add the line on the next run (a `--refresh` is not required) |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
