# /ds-ship

Projects at every stage — raw idea, half-built scaffold, feature-complete but unlaunched, long-dormant — accumulate gaps: broken promises in docs, outdated stacks, missing launch gates, obsolete automations, overengineered abstractions that don't pay rent. Invoking the right ds-* skills in the right order is its own cognitive tax.

**Ship Orchestrator** — classify the project, plan the skill sequence, delegate each phase, consolidate `ds/audit/findings.md`, produce `ds/audit/report.md` (and optional `ds/audit/report.html`) with exactly what was done and what's left.

## Triggers

ds-ship activates at **explicit milestone gates**, not as a generic "audit everything" command. Cascade activation MUST be confirmed twice (intent + scope) before any delegated skill runs.

- User runs `/ds-ship`
- **Release-candidate gate** — user about to cut a release branch, sign an artifact, or push to a store
- **Pre-launch gate** — user about to flip a feature flag, run a paid campaign, or open the product publicly
- **Post-incident gate** — user wants a full audit after a production issue, breach, or rollback
- User preparing an OSS release
- User wants to resume a long-untouched project and doesn't remember the next step
- User asks for "promise vs reality", a stack-fitness review, or a visual status report

### Triggers — ÇAĞIRIR / ÇAĞIRMAZ

| ÇAĞIRIR | ÇAĞIRMAZ |
|---------|----------|
| "is this ready to ship", "finalize the release", "pre-launch audit" | "audit my code" (→ ds-review), "audit the docs" (→ ds-docs) |
| "post-incident full audit" | "fix lint errors" (→ ds-fix) |
| "bring this dormant project back" + dormant signals (>90 days) | "improve performance" (→ ds-review --perf) |
| "promise vs reality across the whole project" | "what dependencies are outdated" (→ ds-deps) |

### Cascade activation — two-confirmation gate

1. **Intent confirmation** — restate the milestone and ask: "You're invoking ds-ship for {milestone}. Cascade may invoke {N} delegated skills. Proceed? [Y/n]"
2. **Scope confirmation** — show proposed sequence + estimated delegation count + Category B approval batch projection. Ask: "Approve this plan? [Y / edit / n]"

Both required unless `--auto` set; `--auto` skips prompts but records both as `auto-approved` in `ds/audit/ship.json`. Cancelling either aborts cascade without invoking any delegated skill.

### Target-based delegation routing

Hard routing rules — ds-ship never decides between ds-deploy and ds-launch on its own:

| Deployment target | Skill |
|-------------------|-------|
| App store (iOS App Store, Play Store, Mac App Store, Microsoft Store) | `/ds-launch` |
| Custom server, container, k8s, VPS, PaaS | `/ds-deploy` |
| Multi-target (e.g. mobile app + backend) | Both, in order: `/ds-deploy` first (infra), then `/ds-launch` (store) |
| Library / package registry (npm, PyPI, crates, pub.dev) | `/ds-repo --oss-ready` + manual publish — neither ds-deploy nor ds-launch |

## Contract

- Orchestrator — zero own analysis, consumes `ds/audit/findings.md` as SSOT. FRC+DSC enforced. State: `ds/audit/ship.json`.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- Findings absent or stale → invoke `/ds-blueprint` before any other delegation.
- Artifacts: `ds/audit/findings.md` (via delegated skills) + own `ds/audit/report.md` (+ `ds/audit/report.html` under `--html`). No logs, traces, history, dumps.
- Two-gate fix: Category A autonomous, Category B batched approval.
- Project-type exclusivity: mobile → `/ds-mobile` authoritative (skip `/ds-compliance` overlap); web/backend → `/ds-compliance` authoritative; library/CLI → skip UI-centric skills.
- Destructive ops forbidden. Approved Category B deletions → `/ds-commit` reversible commits.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Run Phase 0–1 only: classification, doc census, gap table, proposed sequence. No mutations. |
| `--stage={x}` | Override auto-classified stage: idea, spec-only, scaffold, implementation, review-pending, pre-launch, launched, frozen |
| `--html` | Additionally produce `ds/audit/report.html` — self-contained, mermaid flow + findings heatmap, offline, ASCII-only |
| `--skip={list}` | Comma-separated skills to skip (e.g. `--skip=ds-mobile,ds-analytics`) |
| `--only={list}` | Comma-separated skills to include (override classification defaults) |
| `--auto` | Run every phase; Category B items listed and skipped (needs-approval) |
| `--force-approve` | Apply every Category B item without asking |
| `--resume` | Resume from `ds/audit/ship.json` without prompt |
| `--clean` | Delete existing state, start fresh |
| `--clean-all` | Delete `ds/audit/` entirely (every skill's state) — use after a completed ship pass |
| `--no-pr-suggest` | Skip Phase 5c PR suggestion (solo-dev main-only workflow) |

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

```
P0 Assess → P1 Ideal-vs-Current → P2 Rule Audit → P3 Simplify → P4 Docs → P5 Launch Gates → [P5c PR Suggestion] → P6 Report → [Needs-Approval] → Summary
```

### Phase 0: Assess

1. **Recovery check:** DETECT `ds/audit/ship.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present + `--clean-all` → delete `ds/audit/` entirely, fresh. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → skip `done` phases + delegation steps, announce `[SHP] Resuming from Phase {N}, step {K}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`.

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
   - scaffold: source present but entry point stub / TODO-only bodies → stage = scaffold
   - implementation: non-trivial source, tests may or may not exist, no CI yet → stage = implementation
   - review-pending: source + tests + CI but no deploy artifacts, recent commits → stage = review-pending
   - pre-launch: review-pending + deploy config (Dockerfile, CI deploy step, hosting config) → stage = pre-launch
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

6. **Value proposition extraction.** Extract project's one-paragraph concrete promise from docs. Surface: "I read this as: {paragraph}. Confirm before I measure everything against it? [Y/n]".

7. **Promise census.** Extract every concrete capability claim from README / SPEC / docs/ / AI instruction file (per host — see ds-blueprint `references/detection.md` § Instruction Files) / blueprint profile. For each, query source (grep + LSP if available) for implementation. Classify:
   - `promised-not-implemented` — doc claims X; no matching module/function/endpoint
   - `implemented-not-documented` — code has X; no doc mentions it
   - `drift` — both exist; behavior diverges (default changed, signature changed, removed flag still listed)

8. **Ambiguity question block.** One block, every unclear aspect: target audience, public-vs-private intent, performance targets, compliance scope, deprecated features, renamed modules. Ask. Wait.

9. **Skill sequence proposal.** Combine stage + type → propose sequence per matrix, adjusted by user answers. Show plan; user confirms or trims.

**Gate:** Value proposition confirmed; skill sequence approved; `ds/audit/ship.json` populated with stage + type + promise census + sequence. No execution past this gate without approval. If fails (user cannot confirm vp or doesn't approve sequence) → abort orchestration with "ds-ship: aborted — value proposition or skill sequence not confirmed. Re-run after clarifying purpose or use `--stage=X` to override." Do not proceed with vague or unconfirmed plan.

### Phase 1: Ideal-vs-Current Gap

1. **Delegate to `/ds-benchmark`** with confirmed problem-space. Wait.
2. **Re-read `ds/audit/findings.md`** for `ideal-gap` scope after benchmark completes.
3. **Merge with promise census.** `promised-not-implemented` entries join gap table as `missing` with `source=promise`.
4. **Approval batch.** Present all Category B gaps in one block — close / defer / intentional-deviation. For each intentional deviation, optionally invoke `/ds-docs --adr` to record rationale.

**Gate:** Every Category B gap has a decision; Category A gaps queued for Phase 2. If fails (user declines to decide on one or more B gaps) → mark undecided as `deferred` in state.data.category_B_batch, add to report's "Awaiting User Decision" section, continue to Phase 2 with Category A only.

### Phase 2: Rule-Based Deep Audit (via delegation only)

Sequenced per approved plan. One skill at a time. Orchestration loop per delegation:

1. **Pre-delegation note.** Append one line to `ds/audit/report.md` under `## Orchestration log`:
   `[P{N}.{K}] invoke {skill} — reason: {one sentence} — expected: findings update | fixes applied | metric produced`.

2. **Update state.** `delegation_queue` entry → `in_progress`.

3. **Invoke** the skill via host tool's skill-invocation mechanism. Pass only documented arguments.

4. **Wait for done.** Delegated skill complete when ANY: (a) its `ds/audit/<skill>.json` no longer exists, OR (b) its Summary line emitted in chat output, OR (c) `ds/audit/findings.md` has new entries with delegated skill's `source` since pre-delegation. None holds within user-driven turn (skill never reported back) → mark delegation `failed` in orchestration log, log `delegated skill {name} did not signal completion`, proceed to next. Never block waiting for a deletion event the orchestrator cannot observe.

5. **Re-read findings diff.** Only entries added since pre-delegation are new. Classify each A or B using Phase 0 rules.

6. **Route.** A entries → apply inline if delegated skill did not already apply. B entries → append to `category_B_batch`.

7. **Mark done.** `delegation_queue` entry → `done`. Append result line:
   `[P{N}.{K}] {skill} completed — A: {x}, B: {y}, deferred: {z}`.

8. **Advance.** Next delegation in queue → repeat from step 1. Queue empty → advance to next phase.

**Default Phase 2 delegation order (adjusted by stage + type):**

1. `/ds-blueprint` (if findings absent or stale — always first)
2. `/ds-review --strategic` (architecture-level, 8 scopes)
3. `/ds-review --tactical` (file-level, 9 scopes)
4. Stack-specific: `/ds-backend`, `/ds-frontend`, `/ds-mobile` — on mobile projects, `/ds-mobile` subsumes `/ds-compliance` security/privacy/regulatory; do not run both on the same scopes
5. `/ds-compliance` (web/backend projects)
6. `/ds-test`
7. `/ds-fix`
8. `/ds-analytics --privacy-audit` (only if analytics present)

**Category B batch at end of Phase 2.** Present all B items with impact / effort / risk. Modes: interactive → Apply All / Review Each / Skip All / Defer (`approve-all` excludes CRITICAL); `--auto` without `--force-approve` → list + skip; `--force-approve` → apply all. Applied B fixes flow back through owning skill (ds-review for code-level, ds-backend for API, etc.).

**Gate:** Every queued delegation `done`; every B item has decision; `ds/audit/findings.md` reflects current state. If fails (delegated skill did not signal completion or B item has no decision) → log each incomplete as `failed` in orchestration log with reason "did not signal completion", mark undecided B as `deferred`, continue to Phase 3 with collected findings; do not block on single failed delegation.

### Phase 3: Simplify

1. **Delegate to `/ds-simplify`.** Full scan across dead-code / single-caller / fallback / premature-abstraction / quarantine / test-realism / io-drift / ssot-violation / orphan.
2. **Wait + re-read findings (scope=simplify).**
3. **Every simplify finding is Category B.** Present batch, user approves per scope.
4. Approved items handled by ds-simplify (deletion + commit per batch).

**Gate:** Every simplify finding has decision; every approved deletion committed. If fails (ds-simplify delegation didn't complete or batch commit failed) → log incomplete delegation as `failed (simplify batch not committed)`, record affected IDs in state.data.category_B_batch as `deferred`, continue to Phase 4.

### Phase 4: Documentation Audit & Optimization

**4a — Compact existing context-loaded docs.**

Target any doc acting as persistent context for AI assistant or human readers: AI instruction files (per host — see ds-blueprint `references/detection.md` § Instruction Files); `README.md`; skill/prompt/agent definition files; large `docs/` files referenced from context-loading paths.

Per-file pass:
1. Preserve every concrete fact, instruction, pointer.
2. Remove filler prose, redundant restatements, obsolete sections, verbose formatting where compact equivalents exist.
3. Relocate misplaced information (e.g. runtime notes in AI instruction file that belong in `docs/runtime.md`).
4. Compress: tables over prose, bullets over paragraphs, references over duplication.
5. Measure: report before/after token estimate per rewritten doc.

Category: **A** for pure compaction that provably preserves content. **B** if any deletion could plausibly remove useful signal.

**4b — Fill documentation gaps.**

Delegate to `/ds-docs`:
- Verify every claim against source (drift detection).
- Confirm every feature promised in spec is documented (feature-completeness complement of Phase 0 promise census).
- Generate only the missing docs that deliver concrete value. No doc generated because "it's usually there."

Optionally invoke `/ds-docs --adr` to record architectural decisions surfaced in Phase 1 or Phase 2.

**Gate:** Every context-loading doc has before/after token count; doc drift delta reported. If fails (doc unreadable or token count tool unavailable) → log unprocessed doc as `skipped (unreadable)` in orchestration log, estimate token count as "N/A", continue; report doc name in Phase 6 report under "Documentation gaps".

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

**Gate:** Every Phase 5 delegation `done`; all B items have decisions. If fails (a launch-gate skill — ds-devops, ds-deploy, ds-launch, or ds-repo — didn't signal completion) → log as `failed` in orchestration log, mark its B items `deferred`, set ship-readiness flag `no` in state for those gates, continue to Phase 5c.

### Phase 5c: PR Suggestion [optional — suggestion only, never forces]

Orchestrator never pushes or opens a PR on its own. This step **only suggests** when git state makes a PR plausible; user always free to keep working main-only.

**Trigger conditions (all must hold):**
1. Current branch is not `main` / `master` (user already on feature branch).
2. Branch is ahead of upstream by ≥1 commit (something to PR).
3. `gh` CLI available + authenticated (otherwise skip automatic — no PR possible).
4. `--no-pr-suggest` flag absent.

**When triggered:**

> `Branch {name} is ahead of upstream by {N} commits with applied fixes from this run. Open a PR via /ds-pr? (y/n/always-skip)`

Response handling:
- `y` → invoke `/ds-pr`, record result hash in state, include PR URL in Phase 6 report.
- `n` → record `pr_suggested: declined (this run)` in state, continue. Next run asks again.
- `always-skip` → record `pr_suggestion: muted` in `ds/audit/ship.json`; subsequent runs skip this step until `--clean` or manual edit.

**When NOT triggered (silent skip — no prompt, no noise):**

| Situation | Rationale |
|-----------|-----------|
| On `main` / `master` with direct commits | Solo-dev main-only is a valid style — don't nag |
| No upstream configured | Nothing to PR against |
| Branch is up-to-date with upstream | Nothing new to PR |
| `gh` unavailable | Can't open a PR anyway |
| `--no-pr-suggest` flag set | User opted out this run |
| State shows `pr_suggestion: muted` | User muted previously |

**Report note:** Phase 6 report includes one line: `PR: {url} | declined-this-run | not-applicable ({reason}) | muted`.

**Gate:** Decision recorded in state (yes / declined / not-applicable / muted). Step never blocks progression. If fails (user doesn't respond or response unrecognizable) → record `pr_suggested: no_response`, treat as `declined (this run)`, continue without further prompting.

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

{When should ds-ship next run — e.g. "after feature X lands", "before 2026-Q3 public release", "quarterly hygiene".}
```

**`--html` flag: additionally write `ds/audit/report.html`.**

Self-contained, offline, ASCII-only. Sections:
1. Header with stage gauge.
2. Orchestration flow (Mermaid diagram, inline: nodes per phase, nodes per delegated skill, edges for ordering, approval gates marked with diamonds).
3. Findings heatmap (severity × scope grid, background color by count; ASCII-safe hex).
4. Category A / B counters (bar).
5. Ship-readiness gauge (0–100; based on open CRITICAL count + open B count).
6. Each major section wrapped in `<details>` (collapsed by default).

Inline CSS + inline SVG + inline Mermaid (statically rendered SVG, not JavaScript-rendered — offline opens render instantly). No external CDN, no remote font, no remote script.

**Gate:** `ds/audit/report.md` written; `ds/audit/report.html` written if `--html`. If fails → `report.md` unwritable → surface error, print full report to chat as fallback; `report.html` fails (Mermaid render error or write failure) → fall back to ASCII art flow in `<pre>` block, flag in report header — do not block Phase 7.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Remaining unresolved B items (rare — most resolved inline per phase). Present. Modes: `--auto` → list+skip; `--force-approve` → apply all; interactive → Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All needs-approval resolved. If fails (user declines to resolve) → mark unresolved `skipped (user declined)`, include in Phase 6 report's "Awaiting User Decision" section, proceed.

### Phase 8: Summary

FRC+DSC accounting. Output:

```
ds-ship: {OK|WARN|FAIL} | Stage: {stage} | A-fixed: {n} | B-applied: {n} | B-skipped: {n} | Deferred: {n} | Blockers: {n} | Ship-ready: {yes|no}
```

On success: delete `ds/audit/ship.json`. Keep `ds/audit/findings.md` and `ds/audit/report.md` — they remain for follow-up runs. Use `--clean-all` to wipe `ds/audit/` entirely.

**Gate:** Every A/B item has disposition; accounting balances. If fails (accounting doesn't balance) → identify items without disposition, assign `failed (disposition missing)`, reprint summary with corrected counts, status WARN.

## Report Format

See Phase 6 above.

**Value Delivered:** 1-5 concrete ship-readiness outcomes. Example shapes (placeholders, not literal):

- `{n} delegated skills run in milestone-correct order; {n} A items applied autonomously, {n} B items batched for approval — sequencing tax eliminated`
- `Promise census: {n} claims in docs / README / SPEC verified against source; {n} promised-not-implemented, {n} implemented-not-documented surfaced — "ship-ready" is now evidence, not optimism`
- `Cross-skill findings consolidated into ds/audit/report.md (+ optional offline HTML) — single artifact replaces N separate reports`
- `Stage classification: {stage} → recommended sequence: {short-sequence} — next action is a single command, not a decision tree`

Zero-change run: `Project already ship-ready for {stage} — no delegations triggered`.

## Quality Gates

W1: every claim in `ds/audit/report.md` cites file:line or findings ID — no unsourced prose. W2: after modifying docs, re-grep for references to moved content. W3: orchestrator never modifies source code directly — every mutation goes through a delegated skill. W4: re-read `ds/audit/findings.md` diff after every delegation. W5: uncertain classification → B. W6: every phase produces a visible entry in the orchestration log. W7: dedup findings across skills — ds-blueprint's finding wins on overlap with partial scanners. W8: quote every path in shell; orchestrator never interpolates user strings into commands. W9: state in `ds/audit/ship.json`, `ds/audit/` gitignored, state deleted on Summary. W10: orchestrator consumes `ds/audit/findings.md` as SSOT — never re-detects what delegated skills already covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

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
| Library/CLI (no UI) | Skip ds-frontend, ds-launch, ds-market; include ds-repo --oss-ready if public intent |
| Multiple value propositions in docs | Ask user to confirm primary vp; note secondary as intentional scope |
| Ship-ready already | Phase 0 detects zero B gaps, report becomes maintenance snapshot — Phase 5 still runs launch checks to confirm |
