---
name: ds-ship
description: Ship orchestrator — classify the project, plan and delegate the skill sequence, consolidate findings, and produce an audit report. Use when running an end-to-end ship/audit pipeline across multiple skills.
---

# /ds-ship

Projects at every stage — raw idea, half-built scaffold, unlaunched, long-dormant — accumulate gaps: broken doc promises, outdated stacks, missing launch gates, abstractions that don't pay rent. Invoking the right ds-* skills in the right order is its own cognitive tax.

**Ship Orchestrator** — classify the project, plan the skill sequence, delegate each phase, consolidate `ds/audit/findings.md`, produce `ds/audit/report.md` (+ optional `ds/audit/report.html`) with exactly what was done and what's left.

## Triggers

ds-ship activates at **explicit milestone gates**, not as a generic "audit everything" command. Cascade activation MUST be confirmed twice (intent + scope) before any delegated skill runs.

- User runs `/ds-ship`
- **Release-candidate gate** — about to cut a release branch, sign an artifact, or push to a store
- **Pre-launch gate** — about to flip a feature flag, run a paid campaign, or open the product publicly
- **Post-incident gate** — full audit after a production issue, breach, or rollback
- User preparing an OSS release
- User resuming a long-untouched project and doesn't remember the next step
- User asks for "promise vs reality", a stack-fitness review, or a visual status report
- **Model-uplift gate** — a significantly more capable model is now in use; re-audit with score deltas attributed to the model change (`--uplift`)

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "is this ready to ship", "finalize the release", "pre-launch audit" | "audit my code" (→ ds-review), "audit the docs" (→ ds-docs) |
| "post-incident full audit" | "fix lint errors" (→ ds-fix) |
| "bring this dormant project back" + dormant signals (>90 days) | "improve performance" (→ ds-review --perf) |
| "promise vs reality across the whole project" | "what dependencies are outdated" (→ ds-deps) |
| "a new model is out — re-optimize the whole project" (`--uplift`) | "optimize one metric with the new model" (→ ds-tune) |
| "orchestrate the full ship cascade for this milestone" | "turn this feature idea into a plan" (→ ds-pipeline) |

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
| `--preview` | Phase 0–1 only: classification, doc census, gap table, proposed sequence. No mutations. |
| `--stage={x}` | Override auto-classified stage: idea, spec-only, scaffold, implementation, review-pending, pre-launch, launched, frozen |
| `--uplift` | Model-uplift run: force `/ds-blueprint --refresh` as first delegation regardless of findings freshness; Phase 6 report adds model-attributed Score Delta line — previous vs current `Scores:` line via `git log` of the instruction file |
| `--html` | Additionally produce `ds/audit/report.html` — self-contained, mermaid flow + findings heatmap, offline, ASCII-only |
| `--skip={list}` | Comma-separated skills to skip (e.g. `--skip=ds-mobile,ds-launch`) |
| `--only={list}` | Comma-separated skills to include (override classification defaults) |
| `--auto` | Run every phase; Category B items listed and skipped (needs-approval) |
| `--force-approve` | Apply every Category B item without asking |
| `--resume` | Resume from `ds/audit/ship.json` without prompt |
| `--clean` | Delete existing state, start fresh |
| `--clean-all` | Delete `ds/audit/` entirely (every skill's state) — use after a completed ship pass |
| `--no-pr-suggest` | Skip Phase 5c PR suggestion (solo-dev main-only workflow) |

Without flags: present an up-front menu covering every mode, each with a one-line what-it-does — Full (recommended) — full ship cascade across phases / Preview — plan only, no delegated changes / Resume — continue from saved state / (Cancel). A disambiguating flag skips the menu.

## Project Type ↔ Skill Sequence (Phase 0 default plan)

| Stage signal | Default sequence |
|--------------|------------------|
| idea | ds-research → ds-benchmark → ds-init |
| spec-only | ds-init → ds-blueprint → ds-benchmark |
| scaffold | ds-blueprint → ds-init → ds-fix |
| implementation | ds-blueprint → ds-review → ds-test → ds-simplify → ds-fix |
| review-pending | ds-review → ds-compliance OR ds-mobile → ds-frontend/backend → ds-simplify |
| pre-launch | ds-devops → ds-deploy → ds-launch → ds-repo (--oss-ready on public intent) |
| launched | ds-tune → ds-deps (periodic hygiene) |
| frozen | ds-blueprint → ds-deps (security-only) |

**Feature-planning branch (independent of stage):** if the user's immediate ask is a new feature whose design is still open (no `specs/{feature}/spec.md` or equivalent plan exists) → route the planning leg to `/ds-pipeline {idea}` first, ahead of any implementation-oriented skill in the default sequence; resume the stage's default sequence once `specs/{feature}/tasks.md` exists.

**Monetization branch (independent of stage):** if paid-product intent holds (stated in the Phase 0 ambiguity block, or billing/paywall surfaces detected in source) → insert `/ds-productize --audit` into Phase 2 after the stack-specific skills; no billing surface yet (greenfield) → `/ds-productize --plan` instead. Free/internal intent → skip entirely.

| Project type | Additional rules |
|--------------|------------------|
| mobile | ds-mobile authoritative for security/privacy/regulatory; ds-frontend only for UI/UX where applicable; skip ds-compliance on scopes ds-mobile owns |
| web (SSR/SPA) | ds-frontend + ds-backend + ds-compliance all run |
| backend-only | ds-backend + ds-devops + ds-deploy; skip ds-frontend |
| library | ds-test (high coverage) + ds-docs (API-heavy) + ds-repo --oss-ready; skip ds-launch |
| CLI | ds-test + ds-docs + ds-repo; skip ds-frontend, ds-launch |
| paid product / SaaS intent | ds-productize joins Phase 2 per the Monetization branch; store execution stays with ds-launch, canonical privacy with ds-compliance |

## Delegation

**Owns:** orchestration, report-consolidation, ship-readiness, stage-classification, promise-census-aggregation | **Delegates:** every ds-* skill per the sequence matrix above + optional `/ds-pr` at Phase 5c when branch state warrants | **Receives:** none — ds-ship is the top of the stack

## Execution Flow

P0 Assess → P1 Ideal-vs-Current → P2 Rule Audit → P3 Simplify → P4 Docs → P5 Launch Gates → [P5c PR Suggestion] → P6 Report → [Needs-Approval] → Summary

### Phase 0: Assess

1. **Recovery check:** DETECT `ds/audit/ship.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present + `--clean-all` → delete `ds/audit/` entirely, fresh. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → skip `done` phases + delegation steps, announce `[SHP] Resuming from Phase {N}, step {K}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`.

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

4. **Document census** (table): `| Document | Status | Size | Last commit |` — one row per README.md, SPEC.md, docs/*, AI instruction file, `ds/audit/findings.md`; status ∈ fresh / stale / draft / absent.

5. **Git posture.** Active branch, uncommitted changes, unpushed commits, last-activity date, frozen vs active signal.

6. **Value proposition extraction.** Extract the project's one-paragraph concrete promise from docs. Surface: "I read this as: {paragraph}. Confirm before I measure everything against it? [Y/n]".

7. **Promise census.** Extract every concrete capability claim from README / SPEC / docs/ / AI instruction file (per host — see ds-blueprint `references/detection.md` § Instruction Files) / blueprint profile. For each, query source (grep + LSP if available) for implementation. Classify:
   - `promised-not-implemented` — doc claims X; no matching module/function/endpoint
   - `implemented-not-documented` — code has X; no doc mentions it
   - `drift` — both exist; behavior diverges (default changed, signature changed, removed flag still listed)

8. **Ambiguity question block.** One block, every unclear aspect: target audience, public-vs-private intent, monetization intent (free / paid product / internal), performance targets, compliance scope, deprecated features, renamed modules, **ecosystem integrations (Google Workspace / Apple ecosystem / none)**. Ask. Wait.

9. **Integration signal reading.** Read blueprint profile's `Integrations:` field. If `google-workspace` or `apple-ecosystem`, note which skills have conditional A9 rules (ds-backend, ds-mobile, ds-compliance, ds-launch, ds-frontend) and include these in the Dimension Coverage table as `conditional (integrations active)`. If absent or `none`, note A9 as `N/A (integrations signal: none)`.

10. **Skill sequence proposal.** Stage + type → propose sequence per matrix, adjusted by user answers. New feature with open design → insert `/ds-pipeline` first per the Feature-planning branch above. Show plan; user confirms or trims.

**Gate:** Value proposition confirmed; skill sequence approved; `ds/audit/ship.json` populated with stage + type + promise census + sequence. No execution past this gate without approval. If fails → abort with "ds-ship: aborted — value proposition or skill sequence not confirmed. Re-run after clarifying purpose or use `--stage=X` to override." Never proceed on a vague or unconfirmed plan.

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
3. **Invoke** via host's skill-invocation mechanism. Pass only documented arguments.
4. **Wait for done** — complete when ANY: (a) its `ds/audit/<skill>.json` no longer exists, (b) its Summary line emitted in chat, (c) `ds/audit/findings.md` has new entries with that skill's `source` since pre-delegation. None holds within the user-driven turn → mark delegation `failed` in orchestration log (`delegated skill {name} did not signal completion`), proceed to next. Never block waiting for a deletion event the orchestrator cannot observe.
5. **Re-read findings diff** — only entries added since pre-delegation are new. Classify each A or B per Phase 0 rules.
6. **Route** — A entries → apply inline if the delegated skill did not already apply. B entries → append to `category_B_batch`.
7. **Mark done** — queue entry → `done`; append `[P{N}.{K}] {skill} completed — A: {x}, B: {y}, deferred: {z}`.
8. **Advance** — next delegation → repeat from step 1. Queue empty → next phase.

**Default Phase 2 delegation order (adjusted by stage + type):**

1. `/ds-blueprint` (if findings absent or stale — always first)
2. `/ds-review --strategic` (architecture-level, 9 scopes)
3. `/ds-review --tactical` (file-level, 9 scopes)
4. Stack-specific: `/ds-backend`, `/ds-frontend`, `/ds-mobile` — on mobile projects `/ds-mobile` subsumes `/ds-compliance` security/privacy/regulatory; never run both on the same scopes
5. `/ds-compliance` (web/backend projects)
6. `/ds-productize` (paid-product intent only — see Monetization branch)
7. `/ds-test`
8. `/ds-fix`

**Category B batch at end of Phase 2.** Present all B items — one line each (`[severity] title — file:line · impact/effort/risk · owner`) grouped by owning skill with counts; state the question (`Decide these N items?`). Modes: interactive → Apply all / per-owner bulk (`Apply all ds-review` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All / Defer (`approve-all` excludes CRITICAL; "all" = exactly the displayed set); `--auto` without `--force-approve` → list + skip; `--force-approve` → apply all. Applied B fixes flow back through the owning skill (ds-review for code-level, ds-backend for API, etc.).

**Gate:** Every queued delegation `done`; every B item has a decision; `ds/audit/findings.md` reflects current state. If fails → log each incomplete delegation as `failed (did not signal completion)`, mark undecided B as `deferred`, continue to Phase 3 with collected findings; never block on a single failed delegation.

### Phase 3: Simplify

1. Delegate to `/ds-simplify` — full scan across dead-code / single-caller / fallback / premature-abstraction / quarantine / test-realism / io-drift / ssot-violation / orphan.
2. Wait + re-read findings (scope=simplify).
3. Every simplify finding is Category B — present batch, user approves per scope.
4. Approved items handled by ds-simplify (deletion + commit per batch).

**Gate:** Every simplify finding has a decision; every approved deletion committed. If fails → log `failed (simplify batch not committed)`, record affected IDs as `deferred` in state.data.category_B_batch, continue to Phase 4.

### Phase 4: Documentation Audit & Optimization

**4a — Compact existing context-loaded docs.** Targets: AI instruction files (per host — see ds-blueprint `references/detection.md` § Instruction Files), `README.md`, skill/prompt/agent definition files, large `docs/` files on context-loading paths. Per-file pass: (1) preserve every concrete fact, instruction, pointer; (2) remove filler prose, redundant restatements, obsolete sections; (3) relocate misplaced information; (4) compress — tables over prose, bullets over paragraphs, references over duplication; (5) report before/after token estimate per rewritten doc. Category: **A** for pure compaction that provably preserves content; **B** if any deletion could plausibly remove useful signal.

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
4. `--no-pr-suggest` absent.
5. State does not show `pr_suggestion: muted`.

**When triggered:** `Branch {name} is ahead of upstream by {N} commits with applied fixes from this run. Open a PR via /ds-pr? (y/n/always-skip)` — `y` → invoke `/ds-pr`, record result hash in state, include PR URL in Phase 6 report; `n` → record `pr_suggested: declined (this run)`, next run asks again; `always-skip` → record `pr_suggestion: muted` in `ds/audit/ship.json`, subsequent runs skip until `--clean` or manual edit.

**Report note:** Phase 6 report includes one line: `PR: {url} | declined-this-run | not-applicable ({reason}) | muted`.

**Gate:** Decision recorded in state (yes / declined / not-applicable / muted); step never blocks progression. If fails (no or unrecognizable response) → record `pr_suggested: no_response`, treat as `declined (this run)`, continue without further prompting.

### Phase 6: Consolidated Report

Write `ds/audit/report.md` overwriting prior content. **Blocker classification (SKILL-SPEC §15):** a human-required finding counts toward `{K} blockers` only if it passes the mandated-blocker test (external mandate + citable source + rejection/legal/production risk if skipped) — every other human-required finding goes to "Recommended Human Actions" and never blocks the verdict.

```markdown
# Ship Report — {repo-name}

<!-- meta
generated: {ISO 8601} | git_hash: {HEAD} | stage: {classified-stage} | type: {project-type}
-->

## Summary

- Stage: {stage}
- Value proposition: {paragraph}
- Autonomous fixes applied (Category A): {N}
- Awaiting user decision (Category B): {M}
- Ship-ready: yes | no ({K} mandated blockers remain — cited sources in Awaiting User Decision; advisory items never counted)
- Doc token reduction: {before} → {after} ({%})
- Score delta (`--uplift` runs only): overall {prev} → {now} (model {prev-model} → {curr-model})
- Security baseline ([references/principles.md §5](references/principles.md)): {n} secret-scan runs across delegated skills (ds-fix, ds-compliance, ds-pr); 0 unresolved leaks | gap: {skill X did not run secret scan}
- PR: {url} | declined-this-run | not-applicable ({reason}) | muted

## Architectural Changes (approved + applied)
| Change | Rationale | Concrete benefit |

## Autonomous Fixes (Category A)
| Fix | File:line | Problem solved |

## Awaiting User Decision (Category B)
| Proposal | Why needed | Risk / effort | Priority |

## Recommended Human Actions (advisory — not blocking)
| Action | Why | Where |

Every human-required finding that fails the mandated-blocker test (SKILL-SPEC §15) lands here instead of Category B/blockers — cite the mandating source for any item kept as a blocker in Category B or Summary; omit this section when empty.

## Intentional Deviations (kept as-is)
| Item | Why it stays |

## Promise vs Reality
| Promise | Source | Status |
| ... | README#L23 | implemented at src/foo.ts:42 |

## Orchestration log
- [P0] Stage classified: {stage}. Type: {type}. Sequence approved: ...
- [P{N}.{K}] invoke {skill} — completed — findings: {n} (A: {x}, B: {y})

## Next Trigger
{When should ds-ship next run — e.g. "after feature X lands", "quarterly hygiene", "next frontier-model upgrade (--uplift)"}

## Dimension Coverage
| Dimension | Status | Owning Skill | Notes |
|-----------|--------|-------------|-------|
| A1 | {audited | owner-skipped | unowned} | ds-benchmark + ds-productize |
| A2 | {audited | owner-skipped | unowned} | ds-productize |
| A3 | {audited | owner-skipped | unowned} | ds-productize + ds-deploy |
| A4 | {audited | owner-skipped | unowned} | ds-launch |
| A5 | {audited | owner-skipped | unowned} | ds-frontend (ux) |
| A6 | {audited | owner-skipped | unowned} | ds-frontend |
| A7 | {audited | owner-skipped | unowned} | ds-frontend (impl) + ds-compliance (regulatory) |
| A8 | {audited | owner-skipped | unowned} | ds-fix (mechanical) + ds-compliance (rules) |
| A9 | {N/A — integrations none | conditional — integrations active | unowned} | blueprint signal + conditional rules (5 skills) |
| A10 | {audited | owner-skipped | unowned} | ds-docs + ds-backend |
| B1 | {audited | owner-skipped | unowned} | ds-review, ds-fix, ds-simplify, ds-quality |
| B2 | {audited | owner-skipped | unowned} | ds-blueprint + ds-review --strategic |
| B3 | {audited | owner-skipped | unowned} | ds-test |
| B4 | {audited | owner-skipped | unowned} | ds-blueprint + ds-repo |
| B5 | {audited | owner-skipped | unowned} | ds-backend + ds-docs |
| B6 | {audited | owner-skipped | unowned} | ds-docs |
| C1 | {audited | owner-skipped | unowned} | ds-compliance + 4 execution skills |
| C2 | {audited | owner-skipped | unowned} | ds-compliance |
| C3 | {audited | owner-skipped | unowned} | ds-compliance + ds-docs + ds-repo |
| C4 | {audited | owner-skipped | unowned} | ds-deps |
| C5 | {audited | owner-skipped | unowned} | ds-docs + ds-repo |
| D1 | {audited | owner-skipped | unowned} | ds-review --perf + ds-launch --perf-budget + ds-tune |
| D2 | {audited | owner-skipped | unowned} | ds-review --perf + ds-deploy --cost |
| D3 | {audited | owner-skipped | unowned} | ds-backend + ds-deploy |
| D4 | {audited | owner-skipped | unowned} | ds-deploy + ds-backend |
| D5 | {audited | owner-skipped | unowned} | ds-backend |
| D6 | {audited | owner-skipped | unowned} | ds-devops + ds-launch |
| D7 | {audited | owner-skipped | unowned} | ds-deploy |
| D8 | {audited | owner-skipped | unowned} | ds-repo |
| D9 | {audited | owner-skipped | unowned} | ds-deps + ds-review |
| E | N/A (carrier) | ds-ship, ds-pipeline, etc. | Process carriers — not quality dimensions |

Status values: `audited` (skill ran and produced findings), `owner-skipped` (skill exists but was not invoked), `unowned` (no skill claims this dimension). ⚠️ Unowned dimensions MUST be flagged with an explicit warning prefix in the report summary.
```

**`--html`: additionally write `ds/audit/report.html`** — self-contained, offline, ASCII-only. Sections: (1) header with stage gauge; (2) orchestration flow — inline Mermaid diagram, nodes per phase + delegated skill, edges for ordering, approval gates as diamonds; (3) findings heatmap — severity × scope grid, background color by count, ASCII-safe hex; (4) Category A/B counters (bar); (5) ship-readiness gauge 0–100 from open CRITICAL + open B count; (6) major sections in `<details>` (collapsed). Inline CSS + inline SVG + statically rendered Mermaid SVG (not JavaScript-rendered). No external CDN, remote font, or remote script.

**Gate:** `ds/audit/report.md` written; `ds/audit/report.html` written if `--html`. If fails → `report.md` unwritable → surface error, print full report to chat as fallback; `report.html` fails (Mermaid render or write error) → fall back to ASCII art flow in `<pre>` block, flag in report header — never block Phase 7.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Remaining unresolved B items (rare — most resolved inline per phase). Modes: `--auto` → list+skip; `--force-approve` → apply all; interactive → state the question (`Approve these N items?`) and present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All needs-approval resolved. If fails (user declines) → mark unresolved `skipped (user declined)`, include in report's "Awaiting User Decision" section, proceed.

### Phase 8: Summary

FRC+DSC accounting. Output:

```
ds-ship: {OK|WARN|FAIL} | Stage: {stage} | A-fixed: {n} | B-applied: {n} | B-skipped: {n} | Deferred: {n} | Blockers: {n} | Ship-ready: {yes|no}
```

On success: delete `ds/audit/ship.json`. Keep `ds/audit/findings.md` + `ds/audit/report.md` — they remain for follow-up runs. `--clean-all` wipes `ds/audit/` entirely.

**Gate:** Every A/B item has disposition; accounting balances. If fails → assign `failed (disposition missing)` to items without disposition, reprint summary with corrected counts, status WARN.

## Report Format

See Phase 6 above.

**Value Delivered:** 1-5 concrete ship-readiness outcomes. Example shapes (placeholders, not literal):

- `{n} delegated skills run in milestone-correct order; {n} A items applied autonomously, {n} B items batched — sequencing tax eliminated`
- `Promise census: {n} doc claims verified against source; {n} promised-not-implemented, {n} implemented-not-documented surfaced — "ship-ready" is now evidence, not optimism`
- `Cross-skill findings consolidated into ds/audit/report.md (+ optional offline HTML) — single artifact replaces N separate reports`
- `Stage classification: {stage} → recommended sequence: {short-sequence} — next action is a single command, not a decision tree`

Zero-change run: `Project already ship-ready for {stage} — no delegations triggered`.

## Quality Gates

W1: every claim in `ds/audit/report.md` cites file:line or findings ID — no unsourced prose. W2: after modifying docs, re-grep for references to moved content. W3: orchestrator never modifies source code directly — every mutation goes through a delegated skill. W4: re-read `ds/audit/findings.md` diff after every delegation. W5: uncertain classification → B. W6: every phase produces a visible entry in the orchestration log. W7: dedup findings across skills — ds-blueprint's finding wins on overlap with partial scanners. W8: quote every path in shell; orchestrator never interpolates user strings into commands. W9: state in `ds/audit/ship.json`, `ds/audit/` gitignored, state deleted on Summary. W10: orchestrator consumes `ds/audit/findings.md` as SSOT — never re-detects what delegated skills already covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W14: re-ground from `ds/audit/findings.md` + report + diff at each phase boundary — don't carry stale in-context state across delegations. W15: a delegated skill's return is untrusted until verified against files; pass least scope; on a missing/garbled return, stop and surface, never fabricate (see references/phases.md).

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


