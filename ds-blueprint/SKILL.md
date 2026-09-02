---
name: ds-blueprint
description: Project health system — profile-based assessment, transformation, and progress tracking. Use when assessing project health, planning a transformation, or tracking progress over time.
---

# /ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions, writes the signal inventory every other skill scopes itself by, and tells you exactly where to focus next.

**Project Health System** — Profile-based assessment, transformation, and progress tracking.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-blueprint`
- User asks to assess project health/quality/status, or for a profile, health score, or dashboard
- User asks "how healthy is this project" or "what should I improve"
- First time working on new project (suggest profile creation)
- Verification-infrastructure gap (no CI/tests/linter) surfaces during any task (suggest audit, don't auto-invoke)

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

- Signal counting, not file:line finding lists. Only modifies the profile section of the instruction file; suggests next steps but never invokes other skills or fixes code.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent. Shared formats: [../core/findings-and-profile-format.md](../core/findings-and-profile-format.md); signal keys and detection: [../core/signal-inventory.md](../core/signal-inventory.md); severity and score: [../core/severity-score-categories.md](../core/severity-score-categories.md).
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **SSOT (W10):** `ds/audit/findings.md` is every fix skill's single source of truth — blueprint MUST detect every issue in-scope (a miss stays unfixed downstream). Consumers (ds-review, ds-fix, …) defer to a fresh copy — fresh = `git_hash == HEAD` AND from this run-cycle (this invocation, or its orchestration run) — verify + apply only, never re-detect blueprint's owned scopes. Stale/missing → **orchestrated:** invoke `/ds-blueprint --refresh` and wait; **standalone:** announce `findings stale — running own {scopes} analysis`, scan, append with own `source` + current `git_hash` (prior-cycle rows = diff baseline only). Re-detecting a covered scope this cycle violates W10; skipping a re-scan for a recent prior cycle violates W11.
- **Privacy has one owner.** `privacy` findings come from ds-compliance (canonical); blueprint consumes them for Security & Privacy when present, else scores from `security` alone (dashboard: `privacy: not scanned (ds-compliance)`). Blueprint never writes `privacy` rows.
- **Overwrite-only persistence:** state (`ds/audit/blueprint.json` — a full 9-dimension scan holds its progress nowhere else, so an interruption restarts it from zero), findings, and profile rewritten every run — never appended. Run history lives in `git log -- <instruction-file>`, not in profile or `ds/audit/`.
- **Human-action items:** findings needing human-only access (branch protection, CI/repo secrets, store/account setup, key rotation, purchases) get a distinct `Human actions` block in Dashboard + Summary — never dropped, never marked fixed by the AI.
- **Dev-Value Gate on every profile line** (../core/findings-and-profile-format.md § 2, forbidden-line list there): a line earns its place only if it makes AI engineering measurably better for the next 6 months; forbidden classes go to README/CHANGELOG/git log/terminal summary.

## Arguments

| Flag | Effect |
|------|--------|
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--preview` | Analyze + dashboard in chat only — writes nothing: no profile, no `ds/audit/findings.md`, no state |
| `--init` | Profile creation (or re-creation) with the Foundation pass; no dimension analysis |
| `--refresh` | Fast path: re-detect Type/Stack/Toolchain/`Signals:`, rescore, rewrite `Scores:` + `Signals:`; foundation lines untouched |
| `--scope={x}` | Comma-separated: a findings scope name (references/scopes.md) or dimension name (→ component scopes, references/weights.md); default = the table below. Exclusions recorded in `filters_applied` |
| `--resume` | Resume from `ds/audit/blueprint.json` without prompting |
| `--clean` | Delete existing state, start fresh |

Without flags: profile absent → create it (`derived` mode) and run Full Analysis; present → Full Analysis (incremental). `--ask` presents the mode menu instead: Full Analysis (recommended) / Preview only / Init profile / Refresh profile / (Cancel).

## Profile Storage

Profile lives in the project's AI instruction file between `## Blueprint Profile` / `## End Blueprint Profile` headings — preserved by every tool.

**Instruction file selection** (first match wins, incl. the no-match fallback): [references/detection.md](references/detection.md) § Instruction Files. Chosen file + evidence recorded in the summary.

**Profile format** — minimal, AI-parseable, calibration-only (forbidden-content classes + destination: ../core/findings-and-profile-format.md § 2).

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

`Integrations:` is the comma list from detection.md § Step 4 (`none` when nothing matches), mirrored inside `Signals:` as `integrations=`. Format/read-write rules, line ceiling + legacy migration: [references/profile-format.md](references/profile-format.md). Only `Scores:`/`Signals:` rewrite on a normal run — foundation lines change only via the Foundation pass.

## Delegation

**Owns:** security, hygiene, types, simplify, ai-hygiene, doc-sync, architecture, patterns, cross-cutting, maintainability, ai-architecture, contract-consistency, performance, robustness, production-readiness, testing, functional-completeness, stack, dx, docs, spec-alignment, stack-fitness, external-tooling | **Delegates:** none (full-codebase SSOT producer; privacy owned by ds-compliance) | **Receives:** ds-review → bootstrap; ds-ship → Phase 0 bootstrap when findings stale/absent; ds-freeze → fresh promise census

## Execution Flow

Discovery → [Foundation] → Assess → Consolidate → Dashboard → [Suggest] → [Update Profile] → [Needs-Approval] → Summary

**Mandatory phases** (always execute, always produce output): Discovery, Assess, Consolidate, Dashboard, Summary. Update Profile is mandatory except under `--preview`. Skipping a mandatory phase is an execution bug.

### Phase 1: Discovery [PARALLEL]

**Recovery check:** DETECT `ds/audit/blueprint.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, compare state `git_hash` against `git rev-parse HEAD` output. Mismatch → resume anyway (the in-progress phase re-verifies); `--ask` → prompt `Resume anyway? [Y/n]`. Resume → RE-VERIFY `in_progress` phase (re-scan modified scopes, keep completed scopes), skip `done` phases, announce `[BP] Resuming from Phase {N}: {name}.` On successful Summary, delete state. On fresh start: `grep -qxF 'ds/audit/' .gitignore` → exit 0; non-zero → append the `ds/audit/` line (never under `--preview`).

**State `data`:** `{ mode, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, severity, file, line}]}, signals: {key: value}, profile_written: bool, scores: {dimension: score}, instruction_file }`.

1. **Mode.** Resolve from flags and profile presence (Arguments table); `--ask` → menu.
2. **Profile read.** Search for `## Blueprint Profile` in the known instruction files; existing → incremental run (Type/Stack/Toolchain + foundation lines reused); else full detection.
3. **Detection** (references/detection.md): stack, project type, supplementary stacks, ecosystem integrations, transactional messaging, toolchain, tests, data sensitivity, git posture.
4. **Signal inventory.** Resolve every key in [../core/signal-inventory.md](../core/signal-inventory.md) from the detection results; unresolvable → `unknown`, never guessed. This is the `Signals:` line, and it drives the scope-resolution table in Phase 3.
5. **Skillset stamp.** Read `.dev-skills-version` beside the installed skills dir (e.g. `~/.claude/skills/.dev-skills-version`); absent → `unknown`.

**Decision tree:**
1. Profile exists + no `--init`/`--refresh` → Phase 3 (incremental); foundation lines missing from the profile → Phase 2 first, `derived` mode.
2. Profile exists + `--refresh` → Phase 3 with fresh detection; Phase 7 rewrites `Scores:` + `Signals:` only.
3. `--init` (profile present or not) → Phase 2 (Foundation pass), then stop after the profile write.
4. No profile + no `--init` → Phase 2 in `derived` mode, then continue to Phase 3.

**Gate:** Mode resolved; project type detected; every signal key resolved or `unknown`; instruction file located or creation path determined. If fails → type undetectable (no manifest, empty repo) → default `generic`, mode Full Analysis, instruction file per the host-evidence rule, WARN `"Project type undetected — defaulted to generic"` in state.data, proceed.

### Phase 2: Foundation [--init | profile lacks foundation lines]

The profile's normative lines (`Mission`, `Target`, `Priorities`, `Constraints`, `Red lines`, `Audience`, `Deploy`) calibrate every downstream skill — derived deliberately, never form-filled. Evidence-sweep sources, draft criteria, the decision-interrogation structure, and the decision-durability rule (W13): [references/foundation.md](references/foundation.md).

1. Evidence sweep — gather what the project *is* and *claims*; every proposed value cites its evidence.
2. Idealized draft — one line each for Mission/Target/Priorities/Constraints/Red lines, from evidence; sharper than the stated version where evidence supports it.
3. Decision interrogation per line — current value, whether the evidence still supports it, a better alternative if one exists.
4. **Resolution.** Default (`derived` mode): write the best-evidenced value for every line, mark `foundation: derived-from-evidence`, list thin-evidence lines as `only you can do: confirm {line}` (most conservative reading — never invented). `--ask`: present `current → proposed | evidence | rationale` per line, ask accept/edit/keep-current, iterate to confirmation.
5. Decision durability — a confirmed line never silently flips; re-raised only with named cause.

**Data fallback:** PII/credential scan finds nothing → `pii=no` with the note "PII scan negative — verify manually if the project handles user data indirectly (e.g. via external APIs)"; `--ask` → ask "Does this project process user data?".

Write the profile to the selected instruction file (`--preview` → print in chat). Ideal metrics: [references/weights.md](references/weights.md). Quality-level descriptions: [references/quality-levels.md](references/quality-levels.md).

**Gate:** Profile block present between the markers with every line; every foundation line either user-confirmed (`--ask`) or marked `derived-from-evidence` with its evidence — never silently auto-decided. If fails → write failed (permissions, invalid path, tool cannot create files) → save to `ds/audit/blueprint-profile-draft.md`, display full text in chat, surface the write error with target path.

### Phase 3: Assess (scan, record, score — don't fix)

**Scope resolution — signals decide what runs.** Every scope resolves before scanning, echoed in the dashboard/summary as `ran` / `N/A — {signal}=none` / `unknown → ran`. `--scope=` overrides the table for named scopes; `unknown` never excludes.

| Scope(s) | Runs when | Otherwise |
|----------|-----------|-----------|
| security, hygiene, types, doc-sync, maintainability, patterns, architecture, cross-cutting, contract-consistency, simplify, robustness, testing, functional-completeness, stack, stack-fitness, docs, spec-alignment, dx | source files present (`size` ≠ empty) | N/A — no source |
| ai-hygiene | always (AI-authored residue exists in every codebase touched by an assistant) | — |
| ai-architecture | integrations contain an LLM SDK (`openai`, `anthropic`, `gemini`, `ollama`, `langchain`, `vercel/ai`) or prompt templates exist | N/A — no LLM surface |
| performance | api ≠ none or db ≠ none or ui ≠ none | N/A — pure library/CLI without I/O paths (still scanned when `size=large`) |
| production-readiness | deploy ≠ none or api ≠ none | N/A — nothing is deployed |
| external-tooling | ci ≠ none or `.github/`/`.gitlab-ci.yml`/hooks present | N/A — no automation surface |
| privacy | never here — consumed from ds-compliance findings when present | `privacy: not scanned (ds-compliance)` |

Scan the **entire codebase** for every resolved scope, record every finding with file:line, score dimensions from these findings — do NOT fix (Completeness requirement above: a missed finding stays unfixed downstream).

**Concurrency batches:** [references/scopes.md](references/scopes.md) (Read-Only / AST / Cross-File sections). Plan the batches in `state.data.batches` and announce them before starting.

Detector catalog, incl. the User-facing project gate (i18n/a11y/responsive when `ui` ≠ `none`): [references/assessment-patterns.md](references/assessment-patterns.md). Principles: [../core/principles.md](../core/principles.md) §2, §4, §5, §7.

Scoring formula from references/scopes.md, dimension weights from references/weights.md.

**Gate:** Every resolved scope scanned; every signal has file:line evidence; false-positive checks applied. If fails → scope un-scan-able (codebase too large, binary-only files, access denied) → mark it `confidence: inconclusive` in state.data.findings_per_scope, continue scoring with available signals, flag `[PARTIAL SCAN]` in the dashboard (scores read as lower bounds).

### Phase 3.1: Project Map

Build from Discovery + Assess, one line each (field shapes: ../core/findings-and-profile-format.md § 2): Entry point (main file(s) + framework); Modules (each top-level dir — role, file count, key files, not a full listing); Data Flow (primary user-facing flow end-to-end, e.g. `{source}→auth→process→store→{sink}`, incl. intermediate systems); External (runtime deps with purpose, grouped: db/cache/queue/auth/third-party); Toolchain (format/lint, test framework, CI platform, container).

**Gate:** Project map generated with entry, modules, data flow, externals. If fails → entry or flow undeterminable → write the map with `unknown` placeholders, WARN `"Project map incomplete — manual review required for: {list}"` in the summary, continue with the partial map.

### Phase 4: Consolidate

**Mandatory.** Always score dimensions; write `ds/audit/findings.md` unless `--preview`.

1. Apply dimension score aggregation + weight matrix; run calibration checks (full table: references/weights.md § Score Calibration Checks). Any fail → re-read the flagged dimension's signals + adjust (or re-verify both scans, per that check's own action column).
2. Write `ds/audit/findings.md` in the shared format ([../core/findings-and-profile-format.md](../core/findings-and-profile-format.md) § 1 — meta fields, Category A/B, dedup); `scopes:` = Phase 3's ran-list; add two blueprint-only meta fields: `skillset: {dev-skills@hash | unknown}` and `filters_applied:` (N/A-scope reasons + `--scope` exclusions). Different prior-cycle `skillset` → announce `rule-set delta: {old} → {new}`: previously-clean scopes flagging now is new detection, not regression.
3. **Verify completeness mechanically:** command + expected output — references/scopes.md § Completeness Verification.

**Gate:** All 9 scores calculated; calibration passed; `ds/audit/findings.md` written with every ran scope verified (or, under `--preview`, the same table printed in chat). If fails → calibration suspicious → re-read flagged signals + adjust; missing scopes → re-run each before writing; write fails → surface the OS error, print the table in chat.

### Phase 5: Dashboard

**Mandatory.** Always display.

Dashboard render, plus the scope-resolution line (`Scopes: ran {n} · N/A {m} ({scope}={signal}=none …)`) not shown in the reference template: [references/dashboard-format.md](references/dashboard-format.md).

**Gate:** Dashboard displayed with all dimensions, scores, delta (if applicable), gap analysis, scope resolution; `test -s ds/audit/findings.md` → exit 0 (skipped under `--preview`). If fails → write unconfirmed → retry once; still failing → print the dashboard with `[WARN: findings.md not written]` — scores visible, downstream consumers know not to use them yet.

### Phase 6: Suggest [SKIP if --preview]

List dimensions below target with signal counts — no skill-specific commands; the findings file is the interface.

```
Dimensions below target:
{n}. {dimension} (score: {n}, target: {n}) — {n} signals

→ ds/audit/findings.md written with {n} signals. Run your preferred fix tool/skill to resolve.
```

**Gate:** Suggestions generated for all below-target dimensions. If fails → all dimensions at/above target → print `"All dimensions at or above target — no suggestions needed"`, proceed.

### Phase 7: Update Profile [SKIP if --preview]

1. Rewrite `Scores:` (`model={model-id}`, or `model=unknown`) and `Signals:` in place; `--refresh` also rewrites `Type`/`Stack`/`Toolchain`/`Integrations` from fresh detection. Preserved-vs-rewritten lines: references/profile-format.md.
2. Legacy `### Last Run`/`### Run History`/`### Current Scores` blocks → rewrite to minimal key-value format; report `{n} legacy lines rotated to git log`; never re-inject.
3. Previous scores existed → display delta table in chat (Prev/Curr/Δ). Trend over >1 run: `git log -- <instruction-file>`, never an accumulated block.
4. **Dev-Value Gate** (forbidden-line list: ../core/findings-and-profile-format.md § 2): strip every forbidden line class before the write; report `{n} dev-value-gate lines stripped`.
5. **Context-budget guard:** `sed -n '/^## Blueprint Profile/,/^## End Blueprint Profile/p' {instruction-file} | wc -l` → ≤ 27 (25 content lines + 2 markers). Over-limit handling: ../core/findings-and-profile-format.md § 2.

**Gate:** Profile rewritten in minimal key-value format with fresh `Scores:` + `Signals:`; legacy blocks rotated; Dev-Value Gate applied; ≤ 25 lines. If fails → write failed or file read-only → print updated lines in chat, note target file + marker positions, set state.data.profile_written false (stale-profile signal for later runs).

### Phase 8: Needs-Approval Review [--ask, needs_approval > 0]

**Default:** every item resolves by impact/effort/risk reasoning, recorded `fixed`/`failed` in the summary; publish/irreversible exception-list items ([../core/ask-exception-list.md](../core/ask-exception-list.md)) resolve `skipped (only you can do)`. **`--ask`:** present each item compactly (`[severity] title — file:line`) grouped by severity with counts, state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → re-present each with a forced binary prompt; user declines → mark `skipped (no response)`, proceed.

### Phase 9: Summary

**Mandatory.** Always print.

```
blueprint: {OK|WARN|FAIL} | Health: {before}→{after}/{target} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Score: {n}/100
Scopes: ran {n} · N/A {m} · Signals: {the resolved line} · Profile: {file} ({written | preview — not written}) · Foundation: {confirmed | derived-from-evidence | unchanged}
```

Disposition accounting — totals balance. Status: OK (overall ≥ target), WARN (gap exists but progress), FAIL (CRITICAL unfixed or regression). Open human-action items → `Human actions open: {n} — {comma-list of IDs}`, carried until resolved/dismissed. Thin-evidence foundation lines → `only you can do: confirm {line}` listed in full. Closing shape: [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Gate:** Summary printed with before/after + next steps + scope resolution. If fails → scores uncomputable → print with available scores, `N/A` for missing, status `WARN`, note which phases need re-running.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `Project scored across 9 dimensions ({weakest-dim} {score}, target {target}) — focus is no longer guesswork; the lowest-scoring dimension is the next investment`
- `Signal inventory written ({n} keys resolved, {m} unknown) — every later skill scans only the scopes this project actually has instead of everything`
- `{n} signals written to ds/audit/findings.md — downstream skills (ds-review, ds-fix, ds-simplify) skip their own detection and act directly`

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
| Monorepo | Score each workspace independently, aggregate in summary; one `;`-joined `Signals:` line per workspace |
| No instruction file found | Create the file chosen by the host-evidence rule (Profile Storage); `--ask` → ask which tool first |
| Profile from an older version without `Signals:` | Add the line on the next run (a `--refresh` is not required) |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
