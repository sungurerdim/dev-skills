# /ds-ship

Projects at every stage — raw idea, half-built scaffold, feature-complete but unlaunched, long-dormant — accumulate gaps: broken promises in the docs, outdated stacks, missing launch gates, obsolete automations, overengineered abstractions that don't pay rent. Invoking the right ds-* skills in the right order is its own cognitive tax.

**Ship Orchestrator** — classify the project, plan the skill sequence, delegate each phase, consolidate `ds/audit/findings.md`, produce `ds/audit/report.md` (and optional `ds/audit/report.html`) with exactly what was done and what's left.

## Triggers

- User runs `/ds-ship`
- User asks "is this ready to ship", "bring this up to professional standards", "audit everything", or "finalize"
- User wants to resume a long-untouched project and doesn't remember the next step
- User preparing an OSS release
- User asks for "promise vs reality" of the project, a stack-fitness review, or a visual status report

## Contract

- Orchestrator — zero own analysis, consumes `ds/audit/findings.md` as SSOT. FRC+DSC enforced. State: `ds/audit/ship.json`.
- Findings absent or stale → invoke `/ds-blueprint` before any other delegation.
- Artifacts: `ds/audit/findings.md` (via delegated skills) + own `ds/audit/report.md` (+ `ds/audit/report.html` under `--html`). No logs, traces, history, dumps.
- Two-gate fix: Category A autonomous, Category B batched approval.
- Project-type exclusivity: mobile → `/ds-mobile` authoritative (skip `/ds-compliance` overlap scopes); web/backend → `/ds-compliance` authoritative; library/CLI → skip UI-centric skills.
- Destructive ops forbidden. Approved Category B deletions → `/ds-commit` reversible commits.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Run Phase 0–1 only: classification, doc census, gap table, proposed sequence. No mutations. |
| `--stage=X` | Override auto-classified stage: idea, spec-only, scaffold, implementation, review-pending, pre-launch, launched, frozen |
| `--html` | Additionally produce `ds/audit/report.html` — self-contained, mermaid flow + findings heatmap, offline, ASCII-only |
| `--skip=X` | Comma-separated skills to skip (e.g., `--skip=ds-mobile,ds-analytics`) |
| `--only=X` | Comma-separated skills to include (override classification defaults) |
| `--auto` | Run every phase; Category B items listed and skipped (needs-approval) |
| `--force-approve` | Apply every Category B item without asking |
| `--resume` | Resume from `ds/audit/ship.json` without prompt |
| `--clean` | Delete existing state, start fresh |
| `--clean-all` | Delete `ds/audit/` entirely (every skill's state) — use after a completed ship pass |
| `--no-pr-suggest` | Skip Phase 5c PR suggestion for this run (solo-dev main-only workflow) |

Without flags: present mode menu (full / preview / resume).

## Project Type ↔ Skill Sequence (Phase 0 default plan)

| Stage signal | Default sequence |
|--------------|------------------|
| idea | ds-research → ds-benchmark → ds-init |
| spec-only | ds-init → ds-blueprint → ds-benchmark |
| scaffold | ds-blueprint → ds-init → ds-fix |
| implementation | ds-blueprint → ds-review → ds-test → ds-simplify → ds-fix |
| review-pending | ds-review → ds-compliance OR ds-mobile → ds-frontend/backend → ds-simplify |
| pre-launch | ds-devops → ds-deploy → ds-launch → ds-repo (--oss-ready on public intent) |
| launched | ds-tune → ds-analytics → ds-deps (periodic hygiene) |
| frozen | ds-blueprint → ds-deps (security-only) |

| Project type | Additional rules |
|--------------|------------------|
| mobile | ds-mobile authoritative for security/privacy/regulatory; ds-frontend only for UI/UX where applicable; skip ds-compliance on the scopes ds-mobile already owns |
| web (SSR/SPA) | ds-frontend + ds-backend + ds-compliance all run |
| backend-only | ds-backend + ds-devops + ds-deploy; skip ds-frontend |
| library | ds-test (high coverage) + ds-docs (API-heavy) + ds-repo --oss-ready; skip ds-launch, ds-market |
| CLI | ds-test + ds-docs + ds-repo; skip ds-frontend, ds-launch |

## Delegation

**Owns:** orchestration, report-consolidation, ship-readiness, stage-classification, promise-census-aggregation | **Delegates:** every ds-* skill per the sequence matrix above + optional `/ds-pr` at Phase 5c when branch state warrants | **Receives:** none — ds-ship is the top of the stack

## Execution Flow

P0 Assess → P1 Ideal-vs-Current → P2 Rule Audit → P3 Simplify → P4 Docs → P5 Launch Gates → [P5c PR Suggestion] → P6 Report → [Needs-Approval] → Summary

### Phase 0: Assess

1. **Recovery check:** DETECT `ds/audit/ship.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present + `--clean-all` → delete `ds/audit/` entirely, fresh. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → skip `done` phases + delegation steps, announce `[SHP] Resuming from Phase {N}, step {K}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`; add if missing.

2. **State shape:**
```json
{
  "stage": "implementation",
  "project_type": "web",
  "value_proposition": "...",
  "promise_census": [{"source": "README.md#L23", "promise": "...", "implementation": "src/foo.ts:42 | absent"}],
  "skill_sequence": ["ds-blueprint", "ds-review", "..."],
  "current_phase": 2,
  "delegation_queue": [{"phase": 2, "step": 1, "skill": "ds-blueprint", "status": "done"}, ...],
  "category_A_count": 0,
  "category_B_batch": [],
  "approvals_resolved": false,
  "git_hash": "..."
}
```

3. **Stage classification.** Signals:
   - idea: no source files, only `.md` / idea dump → stage = idea
   - spec-only: SPEC.md / PRD.md / detailed README but minimal source → stage = spec-only
   - scaffold: source files present but entry point stub / TODO-only bodies → stage = scaffold
   - implementation: non-trivial source, tests may or may not exist, no CI yet → stage = implementation
   - review-pending: source + tests + CI but no deploy artifacts, recent commits → stage = review-pending
   - pre-launch: review-pending + deploy config present (Dockerfile, CI deploy step, hosting config) → stage = pre-launch
   - launched: pre-launch + `CHANGELOG.md` with released versions / git tags → stage = launched
   - frozen: launched + no commits in past 180 days → stage = frozen

4. **Document census** (table):
```
| Document                     | Status  | Size      | Last commit |
|------------------------------|---------|-----------|-------------|
| README.md                    | fresh   | 120 lines | 3 days ago  |
| SPEC.md                      | stale   | 450 lines | 180 days ago|
| docs/api.md                  | draft   | 30 lines  | 5 days ago  |
| {AI instruction file}        | fresh   | 200 lines | 1 day ago   |
| ds/audit/findings.md         | absent  | -         | -           |
```

5. **Git posture.** Active branch, uncommitted changes, unpushed commits, last-activity date, frozen vs active signal.

6. **Value proposition extraction.** From docs, extract the project's one-paragraph concrete promise. Surface to user: "I read this as: {paragraph}. Confirm before I measure everything against it? [Y/n]".

7. **Promise census.** Extract every concrete capability claim from README / SPEC / docs/ / AI instruction file (per host — see ds-blueprint `references/detection.md` § Instruction Files) / blueprint profile. For each, query source (grep + LSP if available) for implementation. Classify:
   - `promised-not-implemented` — doc claims X; no matching module/function/endpoint
   - `implemented-not-documented` — code has X; no doc mentions it
   - `drift` — both exist; behavior diverges (default changed, signature changed, removed flag still listed)

8. **Ambiguity question block.** One block, every unclear aspect: target audience, public-vs-private intent, performance targets, compliance scope, deprecated features, renamed modules. Ask. Wait.

9. **Skill sequence proposal.** Combine stage + project type → propose the sequence per the matrix, adjusted by user answers. Show the plan; user confirms or trims.

**Gate:** Value proposition confirmed. Skill sequence approved. `ds/audit/ship.json` has populated stage + type + promise census + sequence. No execution past this gate without approval. If fails (user cannot confirm value proposition or does not approve the sequence) → abort orchestration with message "ds-ship: aborted — value proposition or skill sequence not confirmed. Re-run after clarifying the project's purpose or use --stage=X to override classification." Do not proceed with vague or unconfirmed plan.

### Phase 1: Ideal-vs-Current Gap

1. **Delegate to `/ds-benchmark`** with the confirmed problem-space. Wait.
2. **Re-read `ds/audit/findings.md`** for the `ideal-gap` scope after benchmark completes.
3. **Merge with promise census.** `promised-not-implemented` entries join the gap table as `missing` with `source=promise`.
4. **Approval batch.** Present all Category B gaps in one block — close / defer / intentional-deviation. For each intentional deviation, optionally invoke `/ds-docs --adr` to record the rationale.

**Gate:** Every Category B gap has a decision. Category A gaps queued for Phase 2 execution. If fails (user declines to decide on one or more B gaps) → mark undecided gaps as `deferred` in state.data.category_B_batch, add them to the report's "Awaiting User Decision" section, and continue to Phase 2 with Category A gaps only.

### Phase 2: Rule-Based Deep Audit (via delegation only)

Sequenced per the approved plan. One skill at a time. Orchestration loop per delegation:

1. **Pre-delegation note.** Append one line to `ds/audit/report.md` under `## Orchestration log`:
   `[P{N}.{K}] invoke {skill} — reason: {one sentence} — expected: findings update | fixes applied | metric produced`.

2. **Update state.** `delegation_queue` entry → `in_progress`.

3. **Invoke** the skill via the host tool's skill-invocation mechanism. Pass only documented arguments.

4. **Wait for done.** A delegated skill is considered complete when ANY of these holds: (a) its `ds/audit/<skill>.json` state file no longer exists, OR (b) its Summary line was emitted in chat output, OR (c) `ds/audit/findings.md` has new entries with the delegated skill's `source` since pre-delegation. If none holds within the user-driven turn (skill never reported back) → mark delegation as `failed` in the orchestration log, log `delegated skill {name} did not signal completion`, and proceed to next delegation. Never block waiting for a deletion event the orchestrator cannot observe.

5. **Re-read findings diff.** Only entries added since pre-delegation are new. Classify each as A or B using Phase 0 rules.

6. **Route.** A entries → apply inline if the delegated skill did not already apply. B entries → append to `category_B_batch`.

7. **Mark done.** `delegation_queue` entry → `done`. Append result line to `## Orchestration log`:
   `[P{N}.{K}] {skill} completed — A: {x}, B: {y}, deferred: {z}`.

8. **Advance.** Next delegation in the queue → repeat from step 1. Queue empty → advance to next phase.

**Default Phase 2 delegation order (adjusted by stage + type):**

1. `/ds-blueprint` (if findings absent or stale — always first)
2. `/ds-review --strategic` (architecture-level, 8 scopes)
3. `/ds-review --tactical` (file-level, 9 scopes)
4. Stack-specific: `/ds-backend`, `/ds-frontend`, `/ds-mobile` — but on mobile projects, `/ds-mobile` subsumes `/ds-compliance` security/privacy/regulatory; do not run both on the same scopes
5. `/ds-compliance` (web/backend projects)
6. `/ds-test`
7. `/ds-fix`
8. `/ds-analytics --privacy-audit` (only if analytics present)

**Category B batch at end of Phase 2.** Present all B items with impact / effort / risk. Modes: interactive → Apply All / Review Each / Skip All / Defer. `--auto` without `--force-approve` → list + skip. `--force-approve` → apply all. Applied B fixes flow back through the owning skill (ds-review for code-level, ds-backend for API, etc.).

**Gate:** Every queued delegation `done`. Every B item has a decision. `ds/audit/findings.md` reflects current state. If fails (a delegated skill did not signal completion or a B item has no decision) → log each incomplete delegation as `failed` in the orchestration log with reason "did not signal completion", mark undecided B items as `deferred`, and continue to Phase 3 with whatever findings were collected; do not block the orchestration on a single failed delegation.

### Phase 3: Simplify

1. **Delegate to `/ds-simplify`.** Full scan across dead-code / single-caller / fallback / premature-abstraction / quarantine / test-realism / io-drift / ssot-violation / orphan.
2. **Wait + re-read findings (scope=simplify).**
3. **Every simplify finding is Category B.** Present batch, user approves per scope.
4. Approved items handled by ds-simplify (deletion + commit per batch).

**Gate:** Every simplify finding has a decision; every approved deletion committed. If fails (ds-simplify delegation did not complete or a batch commit failed) → log the incomplete delegation in the orchestration log as `failed (simplify batch not committed)`, record affected simplify finding IDs in state.data.category_B_batch as `deferred`, and continue to Phase 4.

### Phase 4: Documentation Audit & Optimization

**4a — Compact existing context-loaded docs.**

Target any doc that acts as persistent context for the AI assistant or human readers: AI instruction files (per host — see ds-blueprint `references/detection.md` § Instruction Files for the full list); `README.md`; skill/prompt/agent definition files; large `docs/` files referenced from context-loading paths.

For each such doc, per-file pass:
1. Preserve every concrete fact, instruction, pointer.
2. Remove filler prose, redundant restatements, obsolete sections, verbose formatting where compact equivalents exist.
3. Relocate misplaced information (e.g., runtime notes in the AI instruction file that belong in `docs/runtime.md`).
4. Compress: tables over prose, bullets over paragraphs, references over duplication.
5. Measure: report before/after token estimate per rewritten doc.

Category: **A** for pure compaction that provably preserves content. **B** if any deletion could plausibly remove useful signal.

**4b — Fill documentation gaps.**

Delegate to `/ds-docs`:
- Verify every claim against source (drift detection).
- Confirm every feature promised in the spec is documented (feature-completeness complement of Phase 0's promise census).
- Generate only the missing docs that deliver concrete value. No doc generated because "it's usually there."

Optionally invoke `/ds-docs --adr` to record architectural decisions surfaced in Phase 1 or Phase 2.

**Gate:** Every context-loading doc has before/after token count. Doc drift delta reported. If fails (a doc could not be read or token count tool is unavailable) → log the unprocessed doc as `skipped (unreadable)` in the orchestration log, estimate token count as "N/A", and continue; report the doc name in the Phase 6 report under a "Documentation gaps" note.

### Phase 5: Launch Gates

Triggered when `stage ∈ {pre-launch, launched}` or user explicitly requested ship prep.

**Infrastructure chain:**
1. `/ds-devops` — CI/CD integrity, signing, deps audit.
2. `/ds-deploy` — container security, TLS, monitoring, incident runbook.
3. `/ds-launch` — store submission OR web launch OR library publish, depending on project type. `--perf-budget` authored if web/api/mobile and not yet present.
4. `/ds-repo` — branch protection, CODEOWNERS, metadata.

**5b — OSS Readiness.** Triggered when project will be public (user-confirmed or `public: true` in blueprint).
- Invoke `/ds-repo --oss-ready`.
- Every OSS-readiness finding is Category B (most are user-visible).

**Gate:** Every Phase 5 delegation `done`. All B items have decisions. If fails (a launch-gate skill — ds-devops, ds-deploy, ds-launch, or ds-repo — did not signal completion) → log the delegation as `failed` in the orchestration log, mark its B items as `deferred`, set ship-readiness flag to `no` in state for those gates, and continue to Phase 5c.

### Phase 5c: PR Suggestion [optional — suggestion only, never forces]

Orchestrator never pushes or opens a PR on its own. This step **only suggests** when the git state makes a PR plausible; the user is always free to keep working main-only.

**Trigger conditions (all must hold):**
1. Current branch is not `main` / `master` (user is already on a feature branch).
2. Branch is ahead of its upstream by ≥1 commit (there is something to PR).
3. `gh` CLI available and authenticated (otherwise skipping is automatic — no PR is possible).
4. `--no-pr-suggest` flag absent.

**When triggered:**

> `Branch {name} is ahead of upstream by {N} commits with applied fixes from this run. Open a PR via /ds-pr? (y/n/always-skip)`

Response handling:
- `y` → invoke `/ds-pr`, record result hash in state, include PR URL in Phase 6 report.
- `n` → record `pr_suggested: declined (this run)` in state, continue to Phase 6. Next run will ask again.
- `always-skip` → record `pr_suggestion: muted` in `ds/audit/ship.json`; subsequent runs skip this step until `--clean` or manual edit.

**When NOT triggered (silent skip — no prompt, no noise):**

| Situation | Rationale |
|-----------|-----------|
| On `main` / `master` with direct commits | Solo-dev main-only workflow is a valid style — don't nag |
| No upstream configured | Nothing to PR against |
| Branch is up-to-date with upstream | Nothing new to PR |
| `gh` unavailable | Can't open a PR anyway |
| `--no-pr-suggest` flag set | User opted out this run |
| State shows `pr_suggestion: muted` | User muted previously |

**Report note:** Phase 6 report includes one line: `PR: {url} | declined-this-run | not-applicable ({reason}) | muted`.

**Gate:** Decision recorded in state (yes / declined / not-applicable / muted). Step never blocks progression. If fails (user does not respond or response is unrecognizable) → record `pr_suggested: no_response` in state, treat as `declined (this run)`, and continue to Phase 6 without further prompting.

### Phase 6: Consolidated Report

Write `ds/audit/report.md` overwriting prior content:

```markdown
# Ship Report — {repo-name}

<!-- meta
generated: {ISO 8601}
git_hash: {HEAD}
stage: {classified-stage}
type: {project-type}
-->

## Summary

- Stage: {stage}
- Value proposition: {paragraph}
- Autonomous fixes applied (Category A): {N}
- Awaiting user decision (Category B): {M}
- Ship-ready: yes | no ({K} blockers remain)
- Doc token reduction: {before} → {after} ({%})
- Security baseline ([references/principles.md §5](references/principles.md)): {n} secret-scan runs across delegated skills (ds-fix, ds-compliance, ds-pr); 0 unresolved leaks | gap: {skill X did not run secret scan}
- PR: {url} | declined-this-run | not-applicable ({reason}) | muted

## Architectural Changes (approved + applied)

| Change | Rationale | Concrete benefit |
|--------|-----------|------------------|
| ...    |           |                  |

## Autonomous Fixes (Category A)

| Fix | File:line | Problem solved |
|-----|-----------|----------------|

## Awaiting User Decision (Category B)

| Proposal | Why needed | Risk / effort | Priority |
|----------|-----------|---------------|----------|

## Intentional Deviations (kept as-is)

| Item | Why it stays |
|------|--------------|

## Promise vs Reality

| Promise | Source | Status          |
|---------|--------|-----------------|
| ...     | README#L23 | implemented at src/foo.ts:42 |
| ...     | SPEC#L88   | not implemented (gap G04)     |

## Orchestration log

- [P0] Stage classified: implementation. Type: web. Sequence approved: ...
- [P1.1] invoke ds-benchmark — completed — gaps: 8 (A: 2, B: 6)
- [P2.1] invoke ds-blueprint — completed — findings: 47 (A: 30, B: 17)
- ...

## Next Trigger

{When should ds-ship next run — e.g., "after feature X lands", "before 2026-Q3 public release", "quarterly hygiene".}
```

**`--html` flag: additionally write `ds/audit/report.html`.**

Self-contained, offline, ASCII-only. Sections:
1. Header with stage gauge.
2. Orchestration flow (Mermaid diagram, inline: nodes per phase, nodes per delegated skill, edges for ordering, approval gates marked with diamonds).
3. Findings heatmap (severity × scope grid, background color by count; ASCII-safe hex).
4. Category A / B counters (bar).
5. Ship-readiness gauge (0–100; based on open CRITICAL count + open B count).
6. Each major section wrapped in `<details>` (collapsed by default).

Inline CSS + inline SVG + inline Mermaid (statically rendered SVG, not JavaScript-rendered — so offline opens render instantly). No external CDN, no remote font, no remote script.

**Gate:** `ds/audit/report.md` written. `ds/audit/report.html` written if `--html`. If fails → if `ds/audit/report.md` cannot be written (e.g., path unwritable), surface the error to the user and print the full report to chat output as fallback; if `ds/audit/report.html` fails (Mermaid render error or write failure), fall back to ASCII art flow in a `<pre>` block and flag in the report header — do not block Phase 7.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Remaining unresolved B items (rare — most resolved inline per phase). Present. Modes: --auto → list+skip, --force-approve → apply all, interactive → Apply All / Review Each / Skip All.

**Gate:** All needs-approval resolved. If fails (user declines to resolve one or more items) → mark unresolved items as `skipped (user declined)` in state, include them in the Phase 6 report's "Awaiting User Decision" section, and proceed to Phase 8 summary.

### Phase 8: Summary

FRC+DSC accounting. Output:

`ds-ship: {OK|WARN|FAIL} | Stage: {stage} | A-fixed: N | B-applied: N | B-skipped: N | Deferred: N | Blockers: N | Ship-ready: {yes|no}`

On success: delete `ds/audit/ship.json`. Keep `ds/audit/findings.md` and `ds/audit/report.md` — they remain for follow-up runs. Use `--clean-all` to wipe `ds/audit/` entirely.

**Gate:** Every A/B item has a disposition. Accounting balances. If fails (accounting does not balance) → identify items without a disposition, assign `failed (disposition missing)` to each, reprint the summary line with corrected counts, and set status to WARN so the imbalance is visible in the output.

## Report Format

See Phase 6 above.

## Quality Gates

W1: every claim in `ds/audit/report.md` cites file:line or findings ID — no unsourced prose. W2: after modifying docs, re-grep for references to moved content. W3: orchestrator never modifies source code directly — every mutation goes through a delegated skill. W4: re-read `ds/audit/findings.md` diff after every delegation. W5: uncertain classification → B. W6: every phase produces a visible entry in the orchestration log. W7: dedup findings across skills — ds-blueprint's finding wins on overlap with partial scanners. W8: quote every path in shell; orchestrator never interpolates user strings into commands. W9: state in `ds/audit/ship.json`, `ds/audit/` gitignored, state deleted on Summary.

- No destructive shortcuts: `--no-verify`, `reset --hard`, branch deletion are forbidden to the orchestrator; every blocker is surfaced, not bypassed.
- Stop condition: same obstacle blocks 3 times → stop, write `## Blockers` section in report, exit with WARN.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Delegated skill unavailable | Surface the gap in report (`## Missing skills`), do NOT substitute with own analysis. Mark phase WARN. |
| Delegated skill fails / errors | Record failure in orchestration log, continue to next delegation, do not mask the failure |
| Phase 0 ambiguity unresolved | Block — orchestrator will not proceed without value proposition and approved sequence |
| User declines every B item | Proceed with A only; report Ship-ready: no with open B count |
| Stage misclassified (user disagrees) | Accept `--stage=X` override, re-plan sequence, resume |
| Findings file becomes stale mid-run (new commit) | Re-invoke `/ds-blueprint --refresh` before continuing the current phase |
| `ds/audit/report.html` requested but Mermaid static render fails | Fall back to ASCII art flow in `<pre>` block; flag in report header |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty repo | Stage = idea; skip Phase 2–5; report lists proposed sequence only |
| Monorepo | Classify per workspace; run orchestration per workspace; aggregate report with workspace-prefixed sections |
| Frozen project (no commits >180d) | Phase 0 flags frozen; default skip of ds-launch; run ds-deps security-only |
| Mobile-only project | Phase 2 runs ds-mobile instead of ds-compliance for overlapping scopes |
| Library/CLI (no UI) | Skip ds-frontend, ds-launch, ds-market; include ds-repo --oss-ready if public intent |
| Multiple value propositions in docs | Ask user to confirm primary vp; note secondary as intentional scope |
| Ship-ready already | Phase 0 detects zero B gaps, report becomes a maintenance snapshot — Phase 5 still runs launch checks to confirm |
