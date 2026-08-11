---
name: ds-ship
description: Ship orchestrator — classify the project, plan and delegate the skill sequence, consolidate findings, and produce an audit report. Use when running an end-to-end ship/audit pipeline across multiple skills.
---

# /ds-ship

Projects at every stage — raw idea, half-built scaffold, unlaunched, long-dormant — accumulate gaps: broken doc promises, outdated stacks, missing launch gates, abstractions that don't pay rent. Invoking the right ds-* skills in the right order is its own cognitive tax.

**Ship Orchestrator** — classify the project, plan the skill sequence, delegate each phase, consolidate `ds/audit/findings.md`, produce `ds/audit/report.md` (+ optional `ds/audit/report.html`) with exactly what was done and what's left.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

ds-ship activates at **explicit milestone gates**, not as a generic "audit everything" command. Cascade activation MUST be confirmed twice (intent + scope) before any delegated skill runs.

- User runs `/ds-ship`
- **Release-candidate gate** — about to cut a release branch, sign an artifact, or push to a store
- **Pre-launch gate** — about to flip a feature flag, run a paid campaign, or open the product publicly
- **Post-incident gate** — full audit after a production issue, breach, or rollback
- User preparing an OSS release
- User resuming a long-untouched project and doesn't remember the next step
- User asks for "promise vs reality", a stack-fitness review, or a visual status report

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "is this ready to ship", "finalize the release", "pre-launch audit" | "audit my code" (→ ds-review), "audit the docs" (→ ds-docs) |
| "post-incident full audit" | "fix lint errors" (→ ds-fix) |
| "bring this dormant project back" + dormant signals (>90 days) | "improve performance" (→ ds-review --perf) |
| "promise vs reality across the whole project" | "what dependencies are outdated" (→ ds-deps) |
| "a new model is out — re-optimize the whole project" | "optimize one metric with the new model" (→ ds-tune) |
| "orchestrate the full ship cascade for this milestone" | "turn this feature idea into a plan" (→ ds-pipeline) |
| "simplify the release, then run the full cascade on the narrowed scope" | "just decide what ships now vs later, nothing else" (→ ds-freeze standalone) |

### Cascade activation — two-confirmation gate

1. **Intent** — restate the milestone: "You're invoking ds-ship for {milestone}. Cascade may invoke {N} delegated skills. Proceed? [Y/n]"
2. **Scope** — show proposed sequence + estimated delegation count + Category B approval batch projection: "Approve this plan? [Y / edit / n]"

Both required unless `--auto`; `--auto` skips prompts but records both as `auto-approved` in `ds/audit/ship.json`. Cancelling either aborts cascade without invoking any delegated skill.

### Target-based delegation routing

Hard routing rules — ds-ship never decides between ds-deploy and ds-launch on its own:

| Deployment target | Skill |
|-------------------|-------|
| App store (iOS App Store, Play Store, Mac App Store, Microsoft Store) | `/ds-launch` |
| Custom server, container, k8s, VPS, PaaS | `/ds-deploy` |
| Multi-target (e.g. mobile app + backend) | Both, in order: `/ds-deploy` first (infra), then `/ds-launch` (store) |
| Library / package registry (npm, PyPI, crates, pub.dev) | `/ds-repo --oss-ready` + manual publish — neither ds-deploy nor ds-launch |

## Contract

**Dimensions:** none (carrier)

- Orchestrator — zero own analysis, consumes `ds/audit/findings.md` as SSOT. State: `ds/audit/ship.json`.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- **Sequential delegation is deliberate:** one skill at a time, writes single-threaded, each delegate returning a compressed findings diff — the shape that holds for coupled, source-mutating work; keep it — parallel fan-out of write-owning delegates is a rejected design, not a pending optimization. Cost scales linearly with delegation count, not combinatorially.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- `/ds-blueprint` full run is always the first delegation — never skipped, never conditioned on findings freshness: a new ds-ship invocation is a new run-cycle, so prior-cycle findings are stale by definition (W10) and serve only as diff baseline. Foundation Review runs inside it every cycle.
- **Re-run policy (every invocation = a new cycle):** each `/ds-ship` run re-executes every scan in its sequence from scratch — a previous run minutes or days ago is never a reason to skip a phase, delegate, or scope ("already ran recently" is a W11-class rejected reason). Prior-cycle `ds/audit/` artifacts and reports are consumed only as diff context: previously-flagged → resolved or still present? previously-clean → regressed? A re-run also picks up improved skill versions — repeating the full sweep is the point, not waste. **Anti-anchoring:** scan coverage derives from the codebase inventory + each skill's current rule tables, never from the prior findings list; prior artifacts are consulted only AFTER the fresh scan, for diffing. Prior findings-meta carries a different `skillset` stamp → state `rule-set delta: {old} → {new}` in the report header; previously-clean areas flagging under the new rules is expected new detection, not regression.
- Artifacts: `ds/audit/findings.md` (via delegated skills) + own `ds/audit/report.md` (+ `ds/audit/report.html` under `--html`). No logs, traces, history, dumps.
- Two-gate fix: Category A autonomous, Category B batched approval.
- Project-type exclusivity: mobile → `/ds-mobile` authoritative (skip `/ds-compliance` overlap); web/backend → `/ds-compliance` authoritative; library/CLI → skip UI-centric skills.
- Destructive ops forbidden. Approved Category B deletions → `/ds-commit` reversible commits.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Phase 0–1 only: classification, doc census, gap table, proposed sequence. No mutations. |
| `--stage={x}` | Override auto-classified stage: idea, spec-only, scaffold, implementation, review-pending, pre-launch, launched, frozen |
| `--html` | Additionally produce `ds/audit/report.html` — self-contained, mermaid flow + findings heatmap, offline, ASCII-only |
| `--skip={list}` | Comma-separated skills to skip (e.g. `--skip=ds-mobile,ds-launch`) |
| `--only={list}` | Comma-separated skills to include (override classification defaults) |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |
| `--resume` | Resume from `ds/audit/ship.json` without prompt |
| `--clean[=all]` | `--clean` deletes ds-ship's own state and starts fresh; `--clean=all` deletes `ds/audit/` entirely (every skill's state) — use after a completed ship pass |

**Unattended full run:** `/ds-ship --auto` runs the entire cascade — classification, all delegations (each receiving `--auto`), Category A+B resolution, launch gates — with zero prompts, suitable for a remote/no-interaction caller. It may commit, but never pushes and never opens a PR: opening a PR is a human decision and is always recorded `needs-human`. Other items matching the Unattended Mode rule-4 exception list (force-push, branch/history deletion, secret rotation, human-only values) are likewise skipped and recorded `needs-human` in the final report.

Without flags: present an up-front menu covering every mode, each with a one-line what-it-does — Full (recommended) — full ship cascade across phases / Preview — plan only, no delegated changes / Resume — continue from saved state / (Cancel). A disambiguating flag skips the menu.

## Project Type ↔ Skill Sequence (Phase 0 default plan)

Default sequence per stage signal, the stage-independent branches (feature-planning → ds-pipeline, monetization → ds-productize, scope-freeze → ds-freeze), and the per-project-type overrides: [references/sequences.md](references/sequences.md). The plan is a default, not a mandate — Phase 0 states the sequence it chose and why.

## Delegation

**Owns:** orchestration, report-consolidation, ship-readiness, stage-classification, promise-census-aggregation | **Delegates:** every ds-* skill per the sequence matrix above + optional `/ds-pr` at Phase 5c when branch state warrants + optional `/ds-issue` at Phase 7b when unresolved items would otherwise only survive in gitignored `ds/audit/` state | **Receives:** none — ds-ship is the top of the stack

## Execution Flow

P0 Assess → P1 Ideal-vs-Current → P2 Rule Audit → P3 Simplify → P4 Docs → P5 Launch Gates → [P5c PR Suggestion] → P6 Report → [Needs-Approval] → [P7b Durable Tracking] → Summary

### Phase 0: Assess

1. **Recovery check:** DETECT `ds/audit/ship.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present + `--clean=all` → delete `ds/audit/` entirely, fresh. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`; under `--auto`, resume automatically — no prompt). Resume → skip `done` phases + delegation steps, announce `[SHP] Resuming from Phase {N}, step {K}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`.

2. **State shape:**
   ```json
   {
     "stage": "implementation", "project_type": "web", "value_proposition": "...",
     "promise_census": [{"source": "README.md#L23", "promise": "...", "implementation": "src/foo.ts:42 | absent"}],
     "skill_sequence": ["ds-blueprint", "ds-review"], "current_phase": 2,
     "delegation_queue": [{"phase": 2, "step": 1, "skill": "ds-blueprint", "status": "done"}],
     "category_A_count": 0, "category_B_batch": [], "approvals_resolved": false, "git_hash": "..."
   }
   ```

3. **Stage classification.** Signals:
   - idea: no source files, only `.md` / idea dump
   - spec-only: SPEC.md / PRD.md / detailed README but minimal source
   - scaffold: source present but entry point stub / TODO-only bodies
   - implementation: non-trivial source, tests may or may not exist, no CI yet
   - review-pending: source + tests + CI but no deploy artifacts, recent commits
   - pre-launch: review-pending + deploy config (Dockerfile, CI deploy step, hosting config)
   - launched: pre-launch + `CHANGELOG.md` with released versions / git tags
   - frozen: launched + no commits in past 180 days

   **Cite the match:** record which concrete signal(s) fired for the chosen stage (e.g. `stage=implementation: src/ non-trivial (47 files), tests/ present, no .github/workflows/, no Dockerfile`) in `ds/audit/ship.json` and the report — a stage label with no cited file/command evidence is not a valid classification; re-derive it before proceeding.

4. **Document census** (table): `| Document | Status | Size | Last commit |` — one row per README.md, SPEC.md, docs/*, AI instruction file, `ds/audit/findings.md`; status ∈ fresh / stale / draft / absent.

5. **Git posture.** Active branch, uncommitted changes, unpushed commits, last-activity date, frozen vs active signal.

6. **Value proposition extraction.** Extract the project's one-paragraph concrete promise from docs. Interactive: surface "I read this as: {paragraph}. Confirm before I measure everything against it? [Y/n]". `--auto`: accept the extracted paragraph as-is, no prompt.

7. **Promise census.** Extract every concrete capability claim from README / SPEC / docs/ / AI instruction file (per host — see ds-blueprint `references/detection.md` § Instruction Files) / blueprint profile. For each, query source (grep + LSP if available) for implementation. Classify:
   - `promised-not-implemented` — doc claims X; no matching module/function/endpoint
   - `implemented-not-documented` — code has X; no doc mentions it
   - `drift` — both exist; behavior diverges (default changed, signature changed, removed flag still listed)

8. **Ambiguity question block.** One block, every unclear aspect: target audience, public-vs-private intent, monetization intent (free / paid product / internal), performance targets, compliance scope, deprecated features, renamed modules, **ecosystem integrations (Google Workspace / Apple ecosystem / none)**, **release scope reduction intent (full backlog vs frozen MVP set — triggers the Scope-Freeze branch)**. Interactive: ask, wait. `--auto`: resolve every item from repo signals (package.json/manifest audience hints, existing license/visibility, detected billing surfaces, blueprint profile) with the most conservative reading when signal is absent (private, free/internal, no compliance scope beyond what's detected) — record each inferred answer in the report so it stays auditable.

9. **Integration signal reading.** Read blueprint profile's `Integrations:` field. If `google-workspace` or `apple-ecosystem`, note which skills have conditional A9 rules (ds-backend, ds-mobile, ds-compliance, ds-launch, ds-frontend) and include these in the Dimension Coverage table as `conditional (integrations active)`. If absent or `none`, note A9 as `N/A (integrations signal: none)`.

10. **Skill sequence proposal.** Stage + type → propose sequence per matrix, adjusted by user answers. New feature with open design → insert `/ds-pipeline` first per the Feature-planning branch above. Interactive: show plan, user confirms or trims. `--auto`: accept the matrix-derived sequence as-is, no prompt. **Every matrix-mandated skill for this stage+type that does NOT end up in the approved sequence gets a recorded exclusion reason in `ds/audit/ship.json` right here** — one of: `project-type-exclusivity` (name the rule, e.g. "mobile → ds-mobile subsumes ds-compliance"), `signal-absent` (name the Phase 0 signal, e.g. "no billing surface, no paid intent stated"), or `user-trimmed` (interactive only — the user's stated reason, or "no reason given" verbatim if none was offered — never silently inferred). A skill missing from both the approved sequence AND this exclusion list is an incomplete plan, not a decision — do not advance the gate below on it.

**Gate:** Value proposition confirmed; skill sequence approved; every matrix-mandated skill is either in the sequence or carries a recorded exclusion reason; `ds/audit/ship.json` populated with stage + type + promise census + sequence + exclusions. No execution past this gate without approval (under `--auto`, "approval" is the recorded best-judgment resolution of steps 6/8/10 above — the gate still holds, nothing proceeds unrecorded). If fails → abort with "ds-ship: aborted — value proposition, skill sequence, or exclusion reasons not confirmed. Re-run after clarifying purpose or use `--stage=X` to override." Never proceed on a vague or unconfirmed plan, and never drop a mandated skill without a reason attached.

### Phase 1: Ideal-vs-Current Gap

1. Delegate to `/ds-benchmark` with confirmed problem-space. Wait.
2. Re-read `ds/audit/findings.md` for `ideal-gap` scope after benchmark completes.
3. Merge with promise census: `promised-not-implemented` entries join gap table as `missing` with `source=promise`.
4. Approval batch: present all Category B gaps in one block — close / defer / intentional-deviation. Intentional deviations → optionally invoke `/ds-docs --adr` to record rationale.

**Gate:** Every Category B gap has a decision; Category A gaps queued for Phase 2. If fails (undecided B gaps) → mark `deferred` in state.data.category_B_batch, add to report's "Awaiting User Decision" section, continue to Phase 2 with Category A only.

### Phase 2: Rule-Based Deep Audit (via delegation only)

Sequenced per approved plan. One skill at a time. Orchestration loop per delegation:

1. **Pre-delegation note** — append to `ds/audit/report.md` under `## Orchestration log`: `[P{N}.{K}] invoke {skill} — reason: {one sentence} — expected: findings update | fixes applied | metric produced`.
2. **Update state** — `delegation_queue` entry → `in_progress`.
3. **Invoke** via host's skill-invocation mechanism. Pass only documented arguments. If ds-ship itself was invoked with `--auto`, append `--auto` to the delegated invocation's arguments (Orchestration Contract §10.3 rule 4) — a delegate never runs interactively just because it's a child call.
4. **Wait for done** — complete when ANY: (a) its `ds/audit/<skill>.json` no longer exists, (b) its Summary line emitted in chat, (c) `ds/audit/findings.md` has new entries with that skill's `source` since pre-delegation. None holds within the user-driven turn → mark delegation `failed` in orchestration log (`delegated skill {name} did not signal completion`), proceed to next. Never block waiting for a deletion event the orchestrator cannot observe.
5. **Re-read findings diff** — only entries added since pre-delegation are new. Classify each A or B per Phase 0 rules.
6. **Route** — A entries → apply inline if the delegated skill did not already apply. B entries → append to `category_B_batch`.
7. **Mark done** — queue entry → `done`; append `[P{N}.{K}] {skill} completed — A: {x}, B: {y}, deferred: {z}`.
8. **Advance** — next delegation → repeat from step 1. Queue empty → next phase.

**Enforcement-arm-first rule (before any code-modifying delegation):** check whether a ds-quality enforcement arm is installed (stop-hook / pre-commit hook / auto-lint). Installed → note it in the orchestration log as the mechanical backstop every delegate's Mechanical Done Gate resolves against. Missing → offer `/ds-quality` bootstrap once as an early delegation (Category B; under `--auto` → installed per Unattended Mode rule 3); declined → record the gap in the report (`enforcement arm absent — delegate gates run instruction-only`) and continue. Rationale: prose gates inside delegated skills depend on the executing model obeying them; the arm makes red-blocks mechanical regardless of executor capability.

**Capability-tier routing (when the host supports per-delegation model selection):** set the tier explicitly, never rely on defaults — read-only search/enumeration legs → fast tier; code-modifying delegations (ds-review, ds-fix, ds-test, ds-simplify, ds-deps, …) → mid tier or better; architecture verdicts, CRITICAL confirmations, and the final ship-readiness call → top tier. A below-mid-tier executor on a code-modifying delegation requires the enforcement arm installed first (rule above) — instruction-following degrades first on low-capability models, so the mechanical arm is the non-negotiable backstop, not the skill text.

**Default Phase 2 delegation order (adjusted by stage + type):**

1. `/ds-blueprint` — always first, full run every cycle (a new invocation = a new run-cycle; prior-cycle findings are stale by definition, diff baseline only)
2. `/ds-review --strategic` (architecture-level, 9 scopes)
3. `/ds-review --tactical` (file-level, 9 scopes)
4. Stack-specific: `/ds-backend`, `/ds-frontend`, `/ds-mobile` — on mobile projects `/ds-mobile` subsumes `/ds-compliance` security/privacy/regulatory; never run both on the same scopes
5. `/ds-compliance` (web/backend projects)
6. `/ds-productize` (paid-product intent only — see Monetization branch)
7. `/ds-test`
8. `/ds-fix`

**Category B batch at end of Phase 2.** Present all B items — one line each (`[severity] title — file:line · impact/effort/risk · owner`) grouped by owning skill with counts; state the question (`Decide these N items?`). Interactive: Apply all / per-owner bulk (`Apply all ds-review` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All / Defer (`approve-all` excludes CRITICAL; "all" = exactly the displayed set). `--auto`: no prompt — every B item resolved per Unattended Mode rule 3 (applied, using the same impact/effort/risk reasoning), except items matching the rule-4 exception list, which become `skipped (needs-human)`. Applied B fixes flow back through the owning skill (ds-review for code-level, ds-backend for API, etc.).

**Gate:** Every queued delegation `done`; every B item has a decision; `ds/audit/findings.md` reflects current state. If fails → log each incomplete delegation as `failed (did not signal completion)`, mark undecided B as `deferred`, continue to Phase 3 with collected findings; never block on a single failed delegation.

### Phase 3: Simplify

1. Delegate to `/ds-simplify` — full scan across dead-code / single-caller / fallback / premature-abstraction / quarantine / test-realism / io-drift / ssot-violation / orphan.
2. Wait + re-read findings (scope=simplify).
3. Every simplify finding is Category B — present batch, user approves per scope.
4. Approved items handled by ds-simplify (deletion + commit per batch).

**Gate:** Every simplify finding has a decision; every approved deletion committed. If fails → log `failed (simplify batch not committed)`, record affected IDs as `deferred` in state.data.category_B_batch, continue to Phase 4.

### Phase 4: Documentation Audit & Optimization

**4a — Compact existing context-loaded docs.** Targets: AI instruction files (per host — see ds-blueprint `references/detection.md` § Instruction Files), `README.md`, skill/prompt/agent definition files, large `docs/` files on context-loading paths. Per-file pass: (1) preserve every concrete fact, instruction, pointer; (2) remove filler prose, redundant restatements, obsolete sections; (3) relocate misplaced information; (4) compress — tables over prose, bullets over paragraphs, references over duplication; (5) report before/after token estimate per rewritten doc. Category: **A** for pure compaction that provably preserves content; **B** when a deletion risks removing useful signal.

**4b — Fill documentation gaps.** Delegate to `/ds-docs`: verify every claim against source (drift detection); confirm every promised feature is documented (complement of Phase 0 promise census); generate only missing docs that deliver concrete value — never because "it's usually there". Optionally `/ds-docs --adr` for architectural decisions surfaced in Phase 1–2.

**Gate:** Every context-loading doc has before/after token count; doc drift delta reported. If fails (doc unreadable or token count unavailable) → log `skipped (unreadable)` in orchestration log, token count "N/A", continue; list doc under "Documentation gaps" in the Phase 6 report.

### Phase 5: Launch Gates

Triggered when `stage ∈ {pre-launch, launched}` or user explicitly requested ship prep.

**Infrastructure chain:**
1. `/ds-devops` — CI/CD integrity, signing, deps audit.
2. `/ds-deploy` — container security, TLS, monitoring, incident runbook.
3. `/ds-launch` — store submission OR web launch OR library publish, per project type. `--perf-budget` authored if web/api/mobile and not yet present.
4. `/ds-repo` — branch protection, CODEOWNERS, metadata.

**5b — OSS Readiness.** Project will be public (user-confirmed or `public: true` in blueprint) → invoke `/ds-repo --oss-ready`. Every OSS-readiness finding is Category B (most are user-visible).

**Gate:** Every Phase 5 delegation `done`; all B items have decisions. If fails (a launch-gate skill didn't signal completion) → log `failed`, mark its B items `deferred`, set ship-readiness `no` in state for those gates, continue to Phase 5c.

### Phase 5c: PR Suggestion [optional — suggestion only, never forces]

Orchestrator never pushes or opens a PR on its own; user is always free to keep working main-only.

**Trigger conditions (all must hold — any unmet → silent skip, no prompt, no noise):**
1. Current branch is not `main` / `master`.
2. Branch ahead of upstream by ≥1 commit (no upstream or up-to-date → skip).
3. `gh` CLI available + authenticated.
4. State does not show `pr_suggestion: muted` (a persisted prior decision, honored even under `--auto`).

**When triggered — interactive:** `Branch {name} is ahead of upstream by {N} commits with applied fixes from this run. Open a PR via /ds-pr? (y/n/always-skip)` — `y` → invoke `/ds-pr`, record result hash in state, include PR URL in Phase 6 report; `n` → record `pr_suggested: declined (this run)`, next run asks again; `always-skip` → record `pr_suggestion: muted` in `ds/audit/ship.json`, subsequent runs skip until `--clean` or manual edit.

**When triggered — `--auto`:** never opens a PR. Opening a PR is a human decision, so it is treated as an Unattended Mode rule-4 exception: skip the invocation, record `pr_suggested: needs-human`, and surface one line in the Phase 6 report naming the branch and the command the user can run (`/ds-pr`). An unattended run may commit, but never pushes and never opens a PR on the user's behalf.

**Report note:** Phase 6 report includes one line: `PR: {url} | declined-this-run | not-applicable ({reason}) | muted`.

**Gate:** Decision recorded in state (yes / declined / not-applicable / muted); step never blocks progression. If fails (no or unrecognizable response) → record `pr_suggested: no_response`, treat as `declined (this run)`, continue without further prompting.

### Phase 6: Consolidated Report

**Sequence-completeness check (run before writing the report):** compute the full mandated skill set for this run — the stage/type matrix row (Project Type ↔ Skill Sequence table) plus every applicable conditional branch (Feature-planning, Monetization, Scope-Freeze, project-type-exclusivity, and the per-type "Additional rules" row). Diff it against `delegation_queue` (skills that actually ran) unioned with the exclusion-reason list from Phase 0 step 10. Any mandated skill in neither set is a **Sequence Gap** — this is a defect in the run itself, not a finding about the target project; list it in the `## Sequence Gaps` report section with the missing skill + which rule/branch mandated it. A pre-launch or launched-stage run with an unresolved Sequence Gap MUST NOT report `Ship-ready: yes` — go back and either run the missing skill or attach a concrete exclusion reason first.

Write `ds/audit/report.md` overwriting prior content. **Blocker classification:** a human-required finding counts toward `{K} blockers` only if it passes the mandated-blocker test (external mandate + citable source + rejection/legal/production risk if skipped) — every other human-required finding goes to "Recommended Human Actions" and never blocks the verdict.

Report shape — every section, including the Dimension Coverage matrix and its status vocabulary: [references/report-template.md](references/report-template.md). Emit every section; a section with no content says so rather than disappearing.

**`--html`: additionally write `ds/audit/report.html`** — self-contained, offline, ASCII-only. Sections: (1) header with stage gauge; (2) orchestration flow — inline Mermaid diagram, nodes per phase + delegated skill, edges for ordering, approval gates as diamonds; (3) findings heatmap — severity × scope grid, background color by count, ASCII-safe hex; (4) Category A/B counters (bar); (5) ship-readiness gauge 0–100 from open CRITICAL + open B count; (6) major sections in `<details>` (collapsed). Inline CSS + inline SVG + statically rendered Mermaid SVG (not JavaScript-rendered). No external CDN, remote font, or remote script.

**Gate:** `ds/audit/report.md` written; `ds/audit/report.html` written if `--html`. If fails → `report.md` unwritable → surface error, print full report to chat as fallback; `report.html` fails (Mermaid render or write error) → fall back to ASCII art flow in `<pre>` block, flag in report header — never block Phase 7.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Remaining unresolved B items (rare — most resolved inline per phase). Interactive: state the question (`Approve these N items?`) and present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. `--auto`: no prompt — resolved per Unattended Mode rule 3, except rule-4 exception-list items, which become `skipped (needs-human)`.

**Gate:** All needs-approval resolved. If fails (user declines) → mark unresolved `skipped (user declined)`, include in report's "Awaiting User Decision" section, proceed.

### Phase 7b: Durable Tracking Handoff [optional — suggestion only, never forces]

Every unresolved item at run's end (deferred Category B, open blockers, Sequence Gaps) lives only in `ds/audit/` — gitignored, single-run, gone on `--clean=all`. This phase offers it a durable home via `/ds-issue` (GitHub Issues, or its own last-resort local `tasks.md` when no GitHub remote exists — same delegation either way, ds-issue resolves which).

**Trigger conditions (all must hold — any unmet → silent skip, no prompt, no noise):**
1. At least one unresolved Category B item, blocker, or Sequence Gap remains after Phase 7.
2. `/ds-issue` is available (any repo shape — it handles both GitHub and local-fallback mode itself).
3. State does not show `tracking_handoff: muted` (a persisted prior decision, honored even under `--auto`).

**When triggered — interactive:** `{n} unresolved items would otherwise only survive in ds/audit/report.md (gitignored, cleared by --clean=all). File them via /ds-issue? (y/n/always-skip)` — `y` → delegate to `/ds-issue` (default intake) once per item, labeled with severity + owning skill; record filed issue URLs (or `tasks.md` line refs in local mode) in the report; `n` → record `tracking_handoff: declined (this run)`, next run asks again; `always-skip` → record `tracking_handoff: muted` in `ds/audit/ship.json`, subsequent runs skip until `--clean` or manual edit.

**When triggered — `--auto`:** no prompt — filing an issue is reversible (closable) and not on the Unattended Mode rule-4 exception list, so it resolves like any other Category B item: delegate to `/ds-issue` for each, record `tracking_handoff: auto-approved`, include the filed references in the report.

**Report note:** Phase 6 report gains one line: `Tracking: {n} filed ({refs}) | declined-this-run | not-applicable (0 unresolved) | muted`.

**Gate:** Decision recorded in state (filed / declined / not-applicable / muted); step never blocks progression. If fails (no or unrecognizable response) → record `tracking_handoff: no_response`, treat as `declined (this run)`, continue without further prompting.

### Phase 8: Summary

Disposition accounting — totals balance. Output:

```
ds-ship: {OK|WARN|FAIL} | Stage: {stage} | A-fixed: {n} | B-applied: {n} | B-skipped: {n} | Deferred: {n} | Blockers: {n} | Ship-ready: {yes|no}
```

On success: delete `ds/audit/ship.json`. Keep `ds/audit/findings.md` + `ds/audit/report.md` — they remain for follow-up runs. `--clean=all` wipes `ds/audit/` entirely.

**Gate:** Every A/B item has disposition; accounting balances. If fails → assign `failed (disposition missing)` to items without disposition, reprint summary with corrected counts, status WARN.

## Report Format

See Phase 6 above.

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `{n} delegated skills run in milestone-correct order; {n} A items applied autonomously, {n} B items batched — sequencing tax eliminated`
- `Promise census: {n} doc claims verified against source; {n} promised-not-implemented, {n} implemented-not-documented surfaced — "ship-ready" is now evidence, not optimism`
- `Cross-skill findings consolidated into ds/audit/report.md (+ optional offline HTML) — single artifact replaces N separate reports`
- `Stage classification: {stage} → recommended sequence: {short-sequence} — next action is a single command, not a decision tree`

Zero-change run: `Project already ship-ready for {stage} — no delegations triggered`.

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
| Delegated skill unavailable | Surface gap in report (`## Missing skills`); do NOT substitute with own analysis. Mark phase WARN. |
| Delegated skill fails / errors | Record failure in orchestration log, continue to next, do not mask the failure |
| Phase 0 ambiguity unresolved | Block — orchestrator will not proceed without value proposition and approved sequence |
| User declines every B item | Proceed with A only; report Ship-ready: no with open B count |
| Stage misclassified (user disagrees) | Accept `--stage=X` override, re-plan sequence, resume |
| Findings file becomes stale mid-run (new commit) | Re-invoke `/ds-blueprint --refresh` before continuing current phase |
| `ds/audit/report.html` requested but Mermaid static render fails | Fall back to ASCII art flow in `<pre>` block; flag in report header |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty repo | Stage = idea; skip Phase 2–5; report lists proposed sequence only |
| Monorepo | Classify per workspace; run orchestration per workspace; aggregate report with workspace-prefixed sections |
| Frozen project (no commits >180d) | Phase 0 flags frozen; default skip of ds-launch; run ds-deps security-only |
| Mobile-only project | Phase 2 runs ds-mobile instead of ds-compliance for overlapping scopes |
| Library/CLI (no UI) | Skip ds-frontend, ds-launch; include ds-repo --oss-ready if public intent |
| Multiple value propositions in docs | Ask user to confirm primary vp; note secondary as intentional scope |
| Ship-ready already | Phase 0 detects zero B gaps, report becomes maintenance snapshot — Phase 5 still runs launch checks to confirm |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
