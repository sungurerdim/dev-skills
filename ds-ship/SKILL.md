---
name: ds-ship
description: Ship orchestrator — classify the project, pick a mode (harden, release, launch, maintain), delegate only the skills the project's signals justify, consolidate findings, and produce an audit report. Use when running an end-to-end audit or ship pipeline across multiple skills.
---

# /ds-ship

Projects at every stage — raw idea, half-built scaffold, unlaunched, long-dormant — accumulate gaps: broken doc promises, outdated stacks, missing launch gates, abstractions that don't pay rent. Invoking the right ds-* skills in the right order is its own cognitive tax, and running launch checks on a library that will never see a store is wasted budget.

**Ship Orchestrator** — classify the project, resolve a mode, plan the skill sequence from the project's signals, delegate each phase, consolidate `ds/audit/findings.md`, produce `ds/audit/report.md` (+ optional `ds/audit/report.html`) with exactly what was done, what was skipped and why, and what's left.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

ds-ship activates at **explicit milestone gates** or as the one-command deep audit of a whole project — never as a substitute for a single skill's job.

- User runs `/ds-ship`
- **Harden** — "audit everything", "make this solid", "what's wrong with this project", resuming a dormant project
- **Release-candidate gate** — about to cut a release branch, sign an artifact, tag a version
- **Pre-launch gate** — about to push to a store, flip a feature flag, run a paid campaign, or open the product publicly
- **Post-incident gate** — full audit after a production issue, breach, or rollback
- User asks for "promise vs reality", a stack-fitness review, or a visual status report

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "is this ready to ship", "finalize the release", "pre-launch audit" | "audit my code" (→ ds-review), "audit the docs" (→ ds-docs) |
| "audit the whole project", "post-incident full audit" | "fix lint errors" (→ ds-fix) |
| "bring this dormant project back" + dormant signals (>90 days) | "improve performance" (→ ds-review --perf) |
| "promise vs reality across the whole project" | "what dependencies are outdated" (→ ds-deps) |
| "a new model is out — re-optimize the whole project" | "optimize one metric with the new model" (→ ds-tune) |
| "orchestrate the full ship cascade for this milestone" | "turn this feature idea into a plan" (→ ds-pipeline) |
| "simplify the release, then run the full cascade on the narrowed scope" | "just decide what ships now vs later, nothing else" (→ ds-freeze standalone) |

### Target-based delegation routing

Hard routing rules — ds-ship never decides between ds-deploy and ds-launch on its own:

| Deployment target (`deploy` / `platforms` signals) | Skill |
|-------------------|-------|
| App store (iOS App Store, Play Store, Mac App Store, Microsoft Store) | `/ds-launch` |
| Custom server, container, k8s, VPS, PaaS | `/ds-deploy` |
| Multi-target (e.g. mobile app + backend) | Both, in order: `/ds-deploy` first (infra), then `/ds-launch` (store) |
| Library / package registry (npm, PyPI, crates, pub.dev) | `/ds-repo --oss-ready` + `/ds-release` for the version/tag/changelog — neither ds-deploy nor ds-launch |

## Contract

**Dimensions:** none (carrier)

- Orchestrator — zero own analysis, consumes `ds/audit/findings.md` as SSOT. State: `ds/audit/ship.json`.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- **Mode is the first decision.** Every run resolves one of four modes (Arguments table); every delegation, report section and verdict is bracketed by it. A leg that does not belong to the mode is `mode-excluded`, never silently run "for completeness".
- **Signals justify delegations.** A skill runs because a resolved signal ([../core/signal-inventory.md](../core/signal-inventory.md), read from the blueprint profile or resolved in Phase 0) says its scope exists in this project; `signal-absent — {key}={value}` is the primary exclusion mechanism, the stage matrix is only the default ordering. Every delegation states the signal and the expected artifact/finding count against its cost.
- **Sequential delegation is deliberate:** one skill at a time, writes single-threaded, each delegate returning a compressed findings diff — parallel fan-out of write-owning delegates is a rejected design. Each delegation runs in an isolated context when the host offers one (a fresh sub-context per delegate: the delegate reads files, never the orchestrator's conversation); the orchestrator keeps only the delegate's summary line and findings diff.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Bootstrap is utility-guided:** `/ds-blueprint` runs first when `ds/audit/findings.md` is absent, carries a `git_hash` other than HEAD, or lacks a `Signals:` line; a fresh findings file at HEAD is consumed as-is (re-running a clean full scan buys nothing). `--refresh-findings` forces the run.
- **Re-run policy:** each invocation re-executes every mode-included, signal-justified delegation from scratch; prior-cycle artifacts are diff context only (previously-flagged → resolved? previously-clean → regressed?). Prior findings-meta with a different `skillset` stamp → `rule-set delta: {old} → {new}` in the report header; new detection under new rules is not regression.
- Artifacts: `ds/audit/findings.md` (via delegated skills) + own `ds/audit/report.md` (+ `ds/audit/report.html` under `--html`). No logs, traces, history, dumps.
- Two-gate fix: Category A autonomous, Category B reasoned and recorded (batched for approval under `--ask`).
- Project-type exclusivity: mobile → `/ds-mobile` authoritative (skip `/ds-compliance` overlap); web/backend → `/ds-compliance` authoritative; `ui=none` → skip UI-centric skills.
- Destructive ops forbidden. Approved Category B deletions → `/ds-commit` reversible commits.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `harden` (deep audit + fixes, no ship legs) · `release` (harden + release gates: devops, deploy, release, repo) · `launch` (release + store/public launch legs: benchmark, launch, productize when billing, OSS readiness) · `maintain` (periodic hygiene: deps, tune, blueprint diff). Absent → derived from stage + intent (table below) and stated in the report |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |
| `--ask` | Interactive run — mode-first menu, sequence confirmation, Category B approval batches at every decision point. Without it every decision resolves by best judgment and is recorded in the report |
| `--preview` | Phase 0 only: classification, mode, scope resolution, proposed sequence with signal reasons. No delegations, no mutations |
| `--stage={x}` | Override auto-classified stage: idea, spec-only, scaffold, implementation, review-pending, pre-launch, launched, frozen |
| `--html` | Additionally produce `ds/audit/report.html` — self-contained, mermaid flow + findings heatmap, offline, ASCII-only |
| `--skip={list}` | Comma-separated skills to skip (e.g. `--skip=ds-mobile,ds-launch`); recorded as `user-trimmed` |
| `--only={list}` | Comma-separated skills to include (override the signal-derived plan) |
| `--refresh-findings` | Force a full `/ds-blueprint` run even when `ds/audit/findings.md` is fresh at HEAD |
| `--resume` | Resume from `ds/audit/ship.json` without prompt |
| `--clean[=all]` | `--clean` deletes ds-ship's own state and starts fresh; `--clean=all` deletes `ds/audit/` entirely (every skill's state) — use after a completed ship pass |

**Mode derivation** (when `--mode` is absent):

| Stage / intent signal | Mode |
|-----------------------|------|
| idea, spec-only, scaffold, implementation, review-pending | harden |
| pre-launch with `deploy ≠ store` and no public/store intent | release |
| pre-launch with `platforms ∩ {ios, android}`, store intent, paid intent, or "open the product publicly" | launch |
| launched, frozen | maintain |
| User wording contains "release", "tag", "version" | release |
| User wording contains "launch", "store", "publish", "go public" | launch |

Without flags: mode derived, sequence derived, delegations run; the report opens with the derivation so it stays auditable. `--ask`: mode-first menu — Harden / Release / Launch / Maintain, the derived one marked `(recommended)`, then the sequence table for confirmation or trimming, then (Cancel).

**Unattended full run:** the default run performs the entire cascade — classification, all delegations, Category A + B resolution, mode-included gates — with zero prompts. It may commit, but never pushes, never opens a PR, never tags, never publishes: every publishing step is on the exception list ([../core/ask-exception-list.md](../core/ask-exception-list.md)) and is recorded `needs-human` with the exact command.

## Delegation

**Owns:** orchestration, report-consolidation, ship-readiness, stage-classification, promise-census-aggregation | **Delegates:** every ds-* skill per the mode + signal plan in references/sequences.md, optional `/ds-pr` and `/ds-issue` at the Handoff offers phase | **Receives:** none — ds-ship is the top of the stack

## Execution Flow

P0 Assess + Mode → [P1 Ideal-vs-Current — launch] → P2 Rule Audit → P3 Simplify → P4 Docs → [P5 Release + Launch gates — release/launch] → P6 Report → [Needs-Approval — --ask] → P7 Handoff offers → Summary

### Phase 0: Assess + Mode

1. **Recovery check:** DETECT `ds/audit/ship.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present + `--clean=all` → delete `ds/audit/` entirely, fresh. Present → READ, verify `git_hash`. Mismatch → resume (the next delegation re-reads findings); `--ask` → prompt `Resume anyway? [Y/n]`. Resume → skip `done` phases + delegation steps, announce `[SHP] Resuming from Phase {N}, step {K}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`.

2. **State shape:**
   ```json
   {
     "mode": "harden", "mode_reason": "stage=implementation, no store/public intent",
     "stage": "implementation", "project_type": "web", "signals": {"ui": "web", "api": "rest", "billing": "none"},
     "value_proposition": "...",
     "skill_sequence": ["ds-blueprint", "ds-review"], "current_phase": 2,
     "delegation_queue": [{"phase": 2, "step": 1, "skill": "ds-blueprint", "status": "done", "reason": "findings absent"}],
     "exclusions": [{"skill": "ds-launch", "status": "mode-excluded"}, {"skill": "ds-productize", "status": "signal-absent", "signal": "billing=none"}],
     "category_A_count": 0, "category_B_batch": [], "approvals_resolved": false, "git_hash": "..."
   }
   ```

3. **Stage classification.** Signals (idea / spec-only / scaffold / implementation / review-pending / pre-launch / launched / frozen): [references/phases.md](references/phases.md) § Phase 0. **Cite the match:** record the concrete signal(s) that fired (e.g. `stage=implementation: src/ non-trivial (47 files), tests/ present, no .github/workflows/, no Dockerfile`) in state and report — a stage label with no cited evidence is not a classification.

4. **Signals.** Read the blueprint profile's `Signals:` line; absent → resolve every key per [../core/signal-inventory.md](../core/signal-inventory.md) now (the bootstrap in Phase 2 will write it into the profile). Record the resolved line in state.

5. **Mode.** `--mode` given → use it; else derive from the table in Arguments and record `mode_reason`. `--ask` → present the mode-first menu.

6. **Document census** (table): `| Document | Status | Size | Last commit |` — one row per README.md, SPEC.md, docs/*, AI instruction file, `ds/audit/findings.md`; status ∈ fresh / stale / draft / absent.

7. **Git posture.** `git branch --show-current` · `git status --porcelain` (non-empty = uncommitted changes) · `git rev-list --count @{u}..HEAD` (unpushed; no upstream → note it) · `git log -1 --format=%cs` (older than 180 days = frozen signal).

8. **Value proposition.** Extract the project's one-paragraph concrete promise from docs; record it. `--ask` → confirm before measuring against it.

9. **Promise census.** Consumed, not re-derived: the `spec-alignment` rows in a fresh `ds/audit/findings.md` (ds-blueprint owns the scope — `promised-not-implemented`, `implemented-not-documented`, `drift`). Findings absent or stale → the census arrives with the Phase 2 bootstrap; ds-ship only aggregates the rows into the report's Promise vs Reality table.

10. **Ambiguity block** — only for items the signals leave open. Every mode: target audience (`audience`), public-vs-private intent (`public_repo`), compliance scope (`jurisdiction`, `pii`), deprecated features, renamed modules. Release/launch only: monetization intent (`billing`), performance targets, ecosystem integrations (`integrations`), release-scope reduction intent (triggers the Scope-Freeze branch). Default: resolve each from the signal with the most conservative reading when the signal is `unknown` (private, free/internal, no compliance scope beyond what is detected) and record each inferred answer in the report. `--ask`: one batched question block, wait.

11. **Skill sequence.** Mode + stage + type → default order from [references/sequences.md](references/sequences.md); then every candidate skill is kept or excluded with a recorded reason: `mode-excluded` (leg outside the mode), `signal-absent — {key}={value}` (the scope does not exist here), `project-type-exclusivity` (name the rule), `user-trimmed` (`--skip`, or the user's stated reason under `--ask`). A skill in neither the sequence nor the exclusion list is an incomplete plan — do not advance. Each kept delegation records its justification: `signal: {key}={value} · expected: {findings | artifact} · cost: {small | medium | large}`. New feature with open design → `/ds-pipeline` first (Feature-planning branch). Scope-reduction intent → `/ds-freeze` first (Scope-Freeze branch).

**Gate:** Mode recorded with its reason; stage cited; signals resolved; value proposition recorded; every candidate skill is in the sequence with a signal justification or in the exclusion list with a reason; `ds/audit/ship.json` populated. `--preview` → print the plan and stop here. If fails → abort with "ds-ship: aborted — mode, sequence, or exclusion reasons not resolved. Re-run with `--mode=X` / `--stage=X` or answer the ambiguity block." Never proceed on a plan with an unjustified delegation or an unexplained gap.

### Phase 1: Ideal-vs-Current Gap [mode = launch]

1. Delegate to `/ds-benchmark` with the confirmed problem-space (signal: `audience` + value proposition). Wait.
2. Re-read `ds/audit/findings.md` for `ideal-gap` scope.
3. Merge with the promise census: `promised-not-implemented` rows join the gap table as `missing` with `source=promise`.
4. Category B gaps: default → decided by impact/effort/risk reasoning and recorded (close / defer / intentional-deviation); `--ask` → one batch. Intentional deviations → `/ds-docs --adr` when present, else a minimal inline ADR.

Other modes: `mode-excluded` — the report's Sequence table says so; nothing runs.

**Gate:** Every Category B gap has a decision; Category A gaps queued for Phase 2. If fails (undecided B gaps) → mark `deferred` in state.data.category_B_batch, add to the report's "Awaiting User Decision" section, continue with Category A only.

### Phase 2: Rule-Based Deep Audit (via delegation only)

Sequenced per the plan. One skill at a time. Orchestration loop per delegation:

1. **Pre-delegation note** — append to `ds/audit/report.md` under `## Orchestration log`: `[P{N}.{K}] invoke {skill} — signal: {key}={value} — expected: findings update | fixes applied | metric produced — cost: {tier}`.
2. **Update state** — `delegation_queue` entry → `in_progress`.
3. **Invoke** via the host's skill-invocation mechanism, in an isolated sub-context when the host offers one. Pass only documented arguments plus the run's mode-relevant flags; `--ask` propagates to every delegate ([../core/ask-exception-list.md](../core/ask-exception-list.md) — a delegate never asks on its own behalf when the orchestrator did not).
4. **Wait for done** — complete when ANY: (a) for a state-qualifying delegate (ds-blueprint, ds-mobile, ds-frontend, ds-tune) its `ds/audit/<skill>.json` no longer exists; (b) its Summary line was emitted; (c) `ds/audit/findings.md` gained entries with that skill's `source` since the pre-delegation note. None holds within the turn → mark the delegation `failed (did not signal completion)` in the log, proceed to the next. Never block on a deletion event the orchestrator cannot observe, and never treat a missing state file as completion for a state-exempt skill.
5. **Re-read findings diff** — only entries added since the pre-delegation note are new. Classify each A or B.
6. **Route** — A entries → applied by the delegate, or inline if it did not. B entries → decided now by impact/effort/risk reasoning and recorded; `--ask` → appended to `category_B_batch` for the end-of-phase batch.
7. **Mark done** — queue entry → `done`; append `[P{N}.{K}] {skill} completed — A: {x}, B: {y}, deferred: {z}`.
8. **Advance** — next delegation → repeat from step 1. Queue empty → next phase.

**Enforcement-arm-first rule (before any code-modifying delegation):** ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint)? Installed → note it as the mechanical backstop every delegate's Mechanical Done Gate resolves against. Missing → run `/ds-quality` bootstrap as an early delegation (Category B, decided by best judgment; `--ask` offers it once); declined or absent → record `enforcement arm absent — delegate gates run instruction-only` and continue.

**Capability-tier routing (when the host supports per-delegation model selection):** read-only search/enumeration legs → fast tier; code-modifying delegations (ds-review, ds-fix, ds-test, ds-simplify, ds-deps, …) → mid tier or better; architecture verdicts, CRITICAL confirmations, and the final verdict → top tier. A below-mid-tier executor on a code-modifying delegation requires the enforcement arm installed first.

**Default Phase 2 order** (each kept only with its signal — [references/sequences.md](references/sequences.md)):

1. `/ds-blueprint` — when findings are absent, stale (hash ≠ HEAD), lack `Signals:`, or `--refresh-findings`; otherwise `skipped (findings fresh at HEAD)`
2. `/ds-review --strategic` (architecture-level) — `size ≠ small`
3. `/ds-review --tactical` (file-level) — always
4. Stack-specific: `/ds-backend` (`api ≠ none` or `db ≠ none`), `/ds-frontend` (`ui ∈ {web, desktop}`), `/ds-mobile` (`mobile ≠ none`; subsumes `/ds-compliance` security/privacy/regulatory — never both on the same scopes)
5. `/ds-compliance` — `pii=yes` or `auth ≠ none` or `ui=web` (web/backend projects)
6. `/ds-productize` — `billing ≠ none` or paid intent [mode ∈ {release, launch}]
7. `/ds-test` — always
8. `/ds-fix` — always
9. `/ds-deps` — `maintain` mode, or any mode when the stack scope reports outdated majors

**Category B at end of Phase 2.** Default: every B item already carries its recorded decision (step 6); the report lists them with the reasoning. `--ask`: present all B items — one line each (`[severity] title — file:line · impact/effort/risk · owner`) grouped by owning skill with counts; state the question (`Decide these N items?`); Apply all / per-owner bulk (`Apply all ds-review` …, CRITICAL bulk still confirms per item) / Review Each / Skip All / Defer; "all" = exactly the displayed set. Applied B fixes flow back through the owning skill.

**Gate:** Every queued delegation `done`; every B item has a decision; `ds/audit/findings.md` re-read after the final delegation with every new entry classified. If fails → log each incomplete delegation as `failed (did not signal completion)`, mark undecided B as `deferred`, continue to Phase 3; never block on a single failed delegation.

### Phase 3: Simplify

1. Delegate to `/ds-simplify` — full scan across its scopes (signal: `size ≠ empty`).
2. Wait + re-read findings (scope=simplify).
3. Every simplify finding is Category B: default → decided by best judgment (a reversible deletion on a clean tree is applied and committed by ds-simplify; anything touching a public contract is `deferred`); `--ask` → batch per scope.

**Gate:** Every simplify finding has a decision; every approved deletion committed. If fails → log `failed (simplify batch not committed)`, record affected IDs as `deferred`, continue to Phase 4.

### Phase 4: Documentation Audit & Optimization

**4a — Compact context-loaded docs.** `/ds-docs` present → delegate this pass to its harness-context-audit scope and consume its findings; absent → inline pass: for each AI instruction file, `README.md`, skill/prompt/agent definition file and large `docs/` file on a context-loading path: preserve every concrete fact, instruction, pointer; remove filler, restatements, obsolete sections; relocate misplaced information; compress (tables over prose, references over duplication); report before/after `wc -c` (bytes ÷ 4 ≈ tokens). Category A for content-preserving compaction; B when a deletion risks useful signal.

**4b — Fill documentation gaps.** Delegate to `/ds-docs`: verify every claim against source (drift), confirm every promised feature is documented (complement of the promise census), generate only missing docs that deliver concrete value. `/ds-docs --adr` for architectural decisions surfaced in Phases 1–2.

**Gate:** Every context-loading doc has before/after token count; doc drift delta reported. If fails (doc unreadable or token count unavailable) → log `skipped (unreadable)`, token count "N/A", continue; list the doc under "Documentation gaps" in the report.

### Phase 5: Release + Launch Gates [mode ∈ {release, launch}]

**Release chain (release and launch):**
1. `/ds-devops` — CI/CD integrity, signing, deps audit (signal: `ci ≠ none`; `ci=none` → the gap is a finding, the skill still runs its "no CI" branch).
2. `/ds-deploy` — container security, TLS, monitoring, incident runbook (signal: `deploy ∉ {none, store}`).
3. `/ds-release` — version, changelog, tag, release notes; publishing steps recorded `needs-human` (signal: any).
4. `/ds-repo` — branch protection, CODEOWNERS, metadata (signal: `public_repo ≠ no` or team signals).

**Launch legs (launch only):**
5. `/ds-launch` — store submission (`platforms ∩ {ios, android}`) OR web launch (`ui=web`, `deploy ≠ none`) OR library publish readiness (`platforms=library`); `--perf-budget` authored for web/api/mobile when absent.
6. `/ds-repo --oss-ready` — `audience=public` or `public_repo=yes`; every OSS-readiness finding is Category B.

Harden and maintain modes: this phase is `mode-excluded`; the report says so and the verdict line reads `Health:` instead of `Ship-ready:`.

**Gate:** Every Phase 5 delegation `done`; all B items decided. If fails (a gate skill did not signal completion) → log `failed`, mark its B items `deferred`, set ship-readiness `no` for those gates, continue.

### Phase 6: Consolidated Report

**Sequence-completeness check (before writing):** the mandated set for this run = the mode's legs (references/sequences.md) filtered by the resolved signals plus the applicable branches (Feature-planning, Monetization, Scope-Freeze, project-type exclusivity). Diff it against `delegation_queue` ∪ `exclusions`. Any mandated skill in neither is a **Sequence Gap** — a defect in the run itself; list it under `## Sequence Gaps`. A release/launch run with an unresolved Sequence Gap MUST NOT report `Ship-ready: yes`.

Write `ds/audit/report.md`, overwriting prior content — shape, section list, the sequence-status vocabulary (`ran` · `mode-excluded` · `signal-absent — {key}={value}` · `project-type-exclusivity` · `user-trimmed` · `failed` · `missing-skill`), the `## Missing skills` section, the measured instruction-token line and the Dimension Coverage matrix: [references/report-template.md](references/report-template.md). Emit every section; a section with no content says so. **Blocker classification:** a human-required finding counts toward `{K} blockers` only if it passes the mandated-blocker test (a citable external authority makes it a documented prerequisite whose omission causes rejection, legal exposure, or a broken production path); every other human-required finding goes to "Recommended Human Actions" and never blocks the verdict.

**Instruction tokens loaded (measured):** `wc -c` of every SKILL.md the run read (own + each delegate) ÷ 4, one line in the report header — the number the lean/claude install profiles are measured against.

**`--html`: additionally write `ds/audit/report.html`** — self-contained, offline, ASCII-only: stage gauge, orchestration flow (inline Mermaid rendered to static SVG), findings heatmap, A/B counters, readiness gauge, major sections in `<details>`. Structure: [references/phases.md](references/phases.md) § Phase 6. No external CDN, remote font, or script.

**Gate:** `ds/audit/report.md` written (+ `report.html` under `--html`). If fails → `report.md` unwritable → surface the error, print the full report to chat; `report.html` fails → fall back to an ASCII flow in a `<pre>` block, flag in the header — never block Phase 7.

### Phase 7: Needs-Approval Review [--ask, needs_approval > 0]

Remaining unresolved B items: state the question (`Approve these N items?`), present each compactly (`[severity] title — file:line`) grouped by severity with counts, ask Apply all / per-severity bulk (CRITICAL bulk still confirms per item) / Review Each / Skip All; "all" = exactly the displayed set. Without `--ask` this phase does not run — every B item was decided and recorded at its phase; publish/irreversible items are `skipped (needs-human)` with the command the user can run.

**Gate:** All needs-approval resolved. If fails (user declines) → mark unresolved `skipped (user declined)`, include in the report's "Awaiting User Decision" section, proceed.

### Phase 7b: Handoff offers [optional — never forces]

Two handoffs the orchestrator offers but never performs on its own:

| Handoff | Trigger (all must hold) | Default | `--ask` |
|---------|--------------------------|---------|---------|
| **PR via `/ds-pr`** | branch ≠ main/master · `git rev-list --count @{u}..HEAD` ≥ 1 · `gh auth status` exit 0 · state lacks `pr_suggestion: muted` | Never opens a PR (publishing): record `pr_suggested: needs-human` and print the branch + `/ds-pr` command in the report | `Open a PR via /ds-pr? (y/n/always-skip)` — `y` → delegate, record the URL; `n` → `declined (this run)`; `always-skip` → `pr_suggestion: muted` |
| **Durable tracking via `/ds-issue`** | ≥ 1 unresolved B item, blocker or Sequence Gap · `/ds-issue` available · state lacks `tracking_handoff: muted` | Filing an issue is reversible → delegate to `/ds-issue` per item (severity + owning skill labels), record `tracking_handoff: auto-approved` and the refs; no GitHub remote → ds-issue's local `tasks.md` fallback | `File them via /ds-issue? (y/n/always-skip)` with the same three outcomes |

Unmet trigger → silent skip. **Report lines:** `PR: {url} | needs-human ({branch}, run /ds-pr) | declined-this-run | not-applicable ({reason}) | muted` and `Tracking: {n} filed ({refs}) | declined-this-run | not-applicable (0 unresolved) | muted`.

**Gate:** Both decisions recorded in state; the phase never blocks progression. If fails (no or unrecognizable response under `--ask`) → record `no_response`, treat as `declined (this run)`, continue.

### Phase 8: Summary

Disposition accounting — totals balance. Output:

```
ds-ship: {OK|WARN|FAIL} | Mode: {mode} | Stage: {stage} | Ran: {n} | Excluded: {n} (mode {a} · signal {b} · type {c} · user {d}) | A-fixed: {n} | B-applied: {n} | B-skipped: {n} | Deferred: {n} | Blockers: {n} | {Ship-ready: yes|no  (release/launch) | Health: {before}→{after}  (harden/maintain)}
```

On success: delete `ds/audit/ship.json`. Keep `ds/audit/findings.md` + `ds/audit/report.md` for follow-up runs. `--clean=all` wipes `ds/audit/` entirely. Close with the Outcome Report ([../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md) § 5) listing every `needs-human` item in full with its command.

**Gate:** Every A/B item has a disposition; accounting balances; every excluded skill carries its reason. If fails → assign `failed (disposition missing)` to items without one, reprint the summary with corrected counts, status WARN.

## Report Format

See Phase 6 above.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} delegated skills run in {mode} mode; {m} legs excluded with a stated signal or mode reason — no budget spent on scopes this project does not have`
- `Promise census: {n} doc claims verified against source; {n} promised-not-implemented, {n} implemented-not-documented surfaced — "ship-ready" is now evidence, not optimism`
- `Cross-skill findings consolidated into ds/audit/report.md (+ optional offline HTML) — single artifact replaces N separate reports`
- `Stage classification: {stage} → mode {mode} → sequence {short-sequence} — next action is a single command, not a decision tree`

Zero-change run: `Project already clean for {mode} — no delegations produced findings`.

## Quality Gates

| Guard | Rule |
|-------|------|
| W1 | Every claim in `ds/audit/report.md` cites file:line or findings ID — no unsourced prose |
| W2 | After modifying docs, re-grep for references to moved content |
| W3 | Orchestrator modifies no source directly — every mutation goes through a delegated skill |
| W4 | Re-read `ds/audit/findings.md` diff after every delegation |
| W5 | Uncertain classification → B |
| W6 | Every phase produces a visible entry in the orchestration log |
| W7 | Dedup findings across skills — ds-blueprint's finding wins on overlap with partial scanners |
| W8 | Quote every path in shell; orchestrator interpolates no user strings into commands |
| W9 | State in `ds/audit/ship.json`, `ds/audit/` gitignored, state deleted on Summary |
| W10 | Orchestrator consumes `ds/audit/findings.md` as SSOT — re-detects nothing delegated skills already covered |
| W14 | Re-ground from `ds/audit/findings.md` + report + diff at each phase boundary — carry no stale in-context state across delegations |
| W15 | A delegated skill's return is untrusted until verified against files; pass least scope; on a missing/garbled return, stop and surface, never fabricate (see references/phases.md) |

- No destructive shortcuts: `--no-verify`, `reset --hard`, branch deletion forbidden to orchestrator; every blocker surfaced, not bypassed.
- Stop condition: same obstacle blocks 3 times → stop, write `## Blockers` section in report, exit with WARN.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Delegated skill unavailable | Surface the gap in the report (`## Missing skills` — skill, what it would have covered, the signal that justified it); do NOT substitute with own analysis. Mark phase WARN. |
| Delegated skill fails / errors | Record the failure in the orchestration log, continue to the next, do not mask the failure |
| Mode or stage cannot be derived (no signals, empty repo) | Mode `harden`, stage `idea`, both recorded as defaults with the missing signals named |
| User declines every B item (`--ask`) | Proceed with A only; report Ship-ready: no with the open B count |
| Stage misclassified (user disagrees) | Accept `--stage=X` / `--mode=X` override, re-plan sequence, resume |
| Findings file becomes stale mid-run (new commit) | Re-invoke `/ds-blueprint --refresh` before continuing the current phase |
| `ds/audit/report.html` requested but Mermaid static render fails | Fall back to ASCII art flow in `<pre>` block; flag in report header |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty repo | Stage = idea, mode = harden; skip Phases 1–5; report lists the proposed sequence only |
| Monorepo | Classify per workspace; run orchestration per workspace; aggregate report with workspace-prefixed sections |
| Frozen project (no commits >180d) | Mode maintain; ds-deps security-only; ds-launch `mode-excluded` |
| Mobile-only project | Phase 2 runs ds-mobile instead of ds-compliance for overlapping scopes |
| Library / CLI (`ui=none`) | ds-frontend `signal-absent — ui=none`; ds-launch only in launch mode with `platforms=library` (publish readiness); ds-repo --oss-ready when `audience=public` |
| Multiple value propositions in docs | Default: the one the README leads with, secondary noted as intentional scope; `--ask` → confirm the primary |
| Already clean | Phase 0 finds zero B gaps; the report becomes a snapshot; release/launch modes still run Phase 5 to confirm |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
