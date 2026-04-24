# /ds-ship

End-to-end project perfection and ship-readiness orchestrator. Takes a project at any stage — raw idea, partial implementation, or feature-complete codebase — and drives it toward a state where every concrete value promised in its own docs is delivered, every audit dimension passes, and nothing exists in the codebase that doesn't earn its presence.

Orchestration only: delegates to the specialized ds-* skills, never re-analyzes what another skill already covers, keeps `.ds-findings.md` as the single source of truth.

## Triggers

- User runs `/ds-ship`
- User asks whether the project is production-ready, shippable, or complete
- User asks to audit, finalize, or bring a project up to professional standards
- User is preparing an OSS release or public launch
- User asks to optimize project context documents (instruction files, README, skill definitions)
- User wants to resume a long-untouched project and doesn't remember where to continue

## Contract

- Orchestrator — never reimplements what another ds-* skill already does
- Two-gate fix model: autonomous for current-architecture-conforming fixes, approval-gated for architectural/scope/capability changes
- Reads `.ds-findings.md` when present and fresh; delegates to `/ds-blueprint` to produce it when absent or stale
- Emits exactly two artifacts: updates to `.ds-findings.md` (via delegated skills) and `.ds-ship-report.md` (own)
- No logs, traces, history files, debug dumps, or analytics of its own runs
- Respects project-type exclusivity rules — e.g. on mobile projects, uses `/ds-mobile` authoritative scopes and does not also run `/ds-compliance` for the same concerns

## Audit dimensions covered

Security, performance, UX, DX, privacy, confidentiality, regulatory compliance, accessibility, code optimization, operational efficiency, documentation completeness, feature completeness (spec-vs-code), overengineering/dead-weight removal, OSS readiness.

---

## Non-Negotiable Behavioral Frame

- **No assumptions.** Gather every ambiguous detail into ONE question block, ask
  the user, wait for answers, then start. No code touches while the plan is
  unresolved.

- **Two finding categories, two gates:**
  - **Category A (autonomous):** Missing/broken items that violate the *current,
    agreed* architecture or plan. Fix without asking.
  - **Category B (approval-gated):** Anything that changes architecture, adds a
    new capability, introduces a new dependency, alters a user-facing promise, or
    shifts product scope. NEVER apply without explicit user approval. Present
    these in a single batched approval block with impact/effort/risk.

- **No snake oil.** Only propose changes with a concrete, measurable benefit.
  "Cosmetic refactor" and "abstract for elegance" are banned. Three similar lines
  beat a premature abstraction. No design for hypothetical future requirements.

- **Software principles apply only where they produce concrete benefit:**
  KISS, DRY, SSOT, SoC, YAGNI, singleton — each evaluated on merit for the
  specific case, not mechanically.

- **Never re-analyze.** If `.ds-findings.md` exists and is fresh (check mtime
  against git HEAD), read it. If stale or missing, delegate to `/ds-blueprint`
  and let it produce the file. Every subsequent skill consumes the same file.
  You are the orchestrator, not a redundant analyzer.

- **Report format for every finding and every fix:**
  `what was missing → which concrete problem it caused (or risked) → what was
  done or is proposed → which measurable benefit was achieved`. No filler. Tables
  over prose.

- **Output language:** respond in the user's primary language (read from
  conversation or system config). Technical terms and code identifiers stay in
  their original form.

- **Token discipline:** progressive loading. Do not pull content you don't need
  this phase. Summarize before storing. Cite file:line, not file contents, when
  possible.

- **Stop condition:** if the same obstacle blocks you three times, stop and
  report what was tried and what's blocking. Never use destructive shortcuts
  (`--no-verify`, `reset --hard`, branch deletion) to get past a gate.

---

## Phase 0 — Situation Assessment (always first)

Classify the project, surface its current state, and agree on what "done" means
for this pass.

1. **Stage classification** (pick one):
   `idea | spec-only | scaffold | implementation | review-pending | pre-launch
   | launched | frozen`
   Signals: presence of code, tests, CI, README, spec docs, recent commits,
   deployment artifacts, open issues.

2. **Document census.** Table every existing doc (README, SPEC/PRD, docs/, ADRs,
   the project's AI-context instruction file if present, `.ds-findings.md`,
   blueprint profile, skill/prompt definition files, runbooks): status (fresh /
   stale / draft / empty), size, last-touched commit.

3. **Git posture.** Active branch, uncommitted changes, unpushed commits, date
   of last activity, frozen vs. active signal.

4. **Stated value proposition.** From the docs, extract the project's concrete
   promise in one paragraph. What problem does it solve? What benefits does it
   claim to deliver? Surface this to the user for confirmation — every later
   phase measures against this.

5. **Question block.** Every ambiguity you noticed — project goals, scope,
   target audience, public-vs-private intent, performance targets, compliance
   requirements, deprecation of features, renamed projects — goes into ONE block.
   Ask. Wait.

6. **Proposed skill sequence.** Based on stage + user answers, propose the
   phase-by-phase plan: which ds-* skills will be invoked, in what order, which
   phases can be skipped. The user approves or trims the sequence.

**Gate:** do not proceed to Phase 1 without a confirmed value proposition AND an
approved skill sequence.

---

## Phase 1 — Ideal-vs-Current Gap

Before any rule-based audit. Goal: know the right destination before measuring
the gap.

1. **Research the problem space.** Invoke `/ds-research` to find 5–10 reputable
   comparable/competing projects or solutions. CRAAP+ tier the sources. Extract
   what each does well and where each fails.

2. **Synthesize the ideal.** Given the project's stated value proposition and
   the research, draft the ideal architecture, stack, data model, UX flow,
   security posture, privacy posture, operational model. Short, decisive, no
   hedging.

3. **Gap table:**

   | Dimension | Ideal | Current | Gap type | Proposal | Category |
   |---|---|---|---|---|---|

   Gap type: `missing | excess | wrong | partial-needs-extension`.
   Category: `A` (autonomous) or `B` (approval-gated).

4. **Approval block.** Every Category B gap gets one batched question:
   *"These gaps change architecture. Close which, keep which as intentional
   deviations, defer which?"* Record the user's reasoning in the updated plan
   (optionally as ADRs via `/ds-docs --adr` if available).

**Gate:** the architectural plan is updated and approved before any Phase 2
writes happen.

---

## Phase 2 — Rule-Based Deep Audit (via delegation only)

This phase is executed by specialized ds-* skills. You orchestrate the order and
consolidate findings. You do NOT re-implement any skill's checks.

### Orchestration loop (per delegated skill)

For every skill you invoke, follow this loop exactly. This is how control
returns to ds-ship after each delegation.

1. **Pre-delegation note** — append one line to `.ds-ship-report.md` under a
   `## Orchestration log` section: `[phase N, step K] invoking <skill> — reason:
   <one sentence> — expected output: <findings file update | fixes applied |
   metric produced>`.
2. **Update the task tracker** — mark the task "invoke <skill>" as
   `in_progress` via TaskUpdate.
3. **Invoke** the skill through the host tool's skill-invocation mechanism.
   Provide only the arguments the skill documents; do not pre-load context.
4. **Wait for the skill's done signal.** Every ds-* skill ends by updating
   `.ds-findings.md` (or its own documented artifact) and returning. When the
   skill stops emitting new activity and its artifact reflects a completed run,
   delegation is done.
5. **Re-read state.** Read the updated `.ds-findings.md` (only the diff against
   what you saw before delegation). Compare against the skill's documented
   exit criteria. If exit criteria aren't met, do not move on — escalate to
   the user with what's missing.
6. **Classify new entries** as Category A or B using Phase 0 rules.
7. **Route entries:** Category A → autonomous-fix queue; Category B → batched
   approval block for the end of this phase.
8. **Mark the task `completed`** in TaskList. Append a one-line result to the
   `## Orchestration log`: `[phase N, step K] <skill> completed — A: <x>, B: <y>,
   deferred: <z>`.
9. **Advance.** Look at the remaining task list for this phase. If more
   delegations queued, return to step 1 with the next one. If the phase is
   complete, move to the next phase's gate (approval block if any, then
   the next phase's entry point).

**Resume discipline.** If the session is interrupted between any two steps,
the next ds-ship invocation reads the `## Orchestration log` and TaskList,
determines the last completed step, and continues from there. The log and the
task list are the ONLY truth about "where we are."

**Invocation rules (adapt to project type; skip inapplicable skills):**

- `/ds-blueprint` — full 22-scope scan. Always first if `.ds-findings.md` is
  absent or stale. Produces the SSOT findings file.
- `/ds-review --strategic` — 8-scope architectural review.
- `/ds-review --tactical` — 9-scope, 97-check code review.
- Stack-specific: `/ds-backend`, `/ds-frontend`, `/ds-mobile`.
  (For mobile projects, `/ds-mobile` subsumes `/ds-compliance` on security +
  privacy + regulatory scopes. Do not run both on the same codebase — duplicate
  findings.)
- `/ds-compliance` — security + privacy + regulatory (GDPR/KVKK/CCPA/etc.) +
  a11y (WCAG 2.2 AA) + i18n. Authoritative for web/backend.
- `/ds-test` — coverage, regression tests, edge cases. Generates/updates tests.
- `/ds-fix` — format, typecheck, lint, l10n, secret scan.
- `/ds-analytics --privacy-audit` — event property PII scan (if analytics exist).

**Consolidation table (you maintain this):**

| Source skill | Severity | Finding | File:line | Category (A/B) | Fix status |
|---|---|---|---|---|---|

Category A findings flow to the autonomous-fix queue. Category B findings batch
into the pre-Phase-3 approval block.

---

## Phase 3 — Overengineering, Duplication & Dead Weight

Systematic hygiene across the codebase. **No silent deletions.** Every finding
surfaces a remove/keep proposal with a reason; the user approves.

**Search for:**
- Dead code (LSP `findReferences` returns zero for exported symbols).
- Helpers called exactly once (inline candidates).
- Fallback / backward-compat code (unless the user explicitly preserved it).
- Feature flag branches with only one path ever taken.
- Abstractions built on top of three or fewer similar concrete usages.
- Quarantine markers: `// removed`, `// legacy`, `// deprecated`, `_unused`.
- Tests that use unrealistic data (`a@b.c`, `$1`) instead of production-shaped
  data.
- Input/output drift: every function's signature vs. every call site — mismatch
  is a finding.
- SSOT violations: the same constant or rule duplicated across files.
- Orphan files: modules/assets with zero references.

**Output:** a single delete-or-keep table with reasoning. User approval moves
them to Category A execution.

---

## Phase 4 — Documentation Audit & Optimization

Two directions, executed in this order:

### 4a — Simplify existing context-loaded documents

Target any document that acts as persistent context for the AI assistant or for
humans reading the project. Examples (inclusive, not exhaustive): the project's
AI-context instruction file if one exists (e.g. `CLAUDE.md`, `AGENTS.md`,
`.cursorrules`, `.windsurfrules`, or the host tool's equivalent), user-level
equivalents of the same, project `README.md`, skill/prompt/agent definition
files, and any large document in `docs/` that is referenced from context-loading
paths or pinned in instructions.

For each such doc:
1. **Preserve every concrete fact, instruction, and pointer.** No loss of
   information, no loss of function.
2. **Remove:** filler prose, redundant restatements, obsolete sections,
   preamble/wrap-up paragraphs that restate the obvious, examples that add no
   clarity beyond existing ones, verbose formatting when compact equivalents
   exist.
3. **Relocate:** information in the wrong file (e.g. runtime data notes in
   CLAUDE.md that belong in `docs/runtime.md`). Move it; leave a one-line
   pointer if the original location is frequently loaded.
4. **Compress:** prefer tables to prose lists, bullets to paragraphs, single
   sentences to multi-sentence elaborations. Use references over duplication
   (one line: "see docs/X.md" beats re-explaining X).
5. **Measure:** report before/after token estimate for each rewritten doc. Flag
   any doc whose token weight does not justify its informational density.

Category: **A** (autonomous) for pure compaction that provably preserves
content. **B** (approval) if any deletion could plausibly remove useful signal.
When in doubt, category B.

### 4b — Fill documentation gaps

Invoke `/ds-docs` to:
- Verify every claim in the docs against the source code (drift detection).
- Confirm every feature promised in the spec is implemented (feature
  completeness — spec-vs-code gap).
- Generate only the missing documents that deliver concrete value. Do NOT
  generate a doc because "it's usually there." Each new doc justifies itself.

**Ideal doc set reference** (include only what delivers value for this project):
README, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT, CHANGELOG, API reference,
ops/runbook, privacy policy, architectural overview, ADRs.

---

## Phase 5 — Launch Readiness Gates

Triggered when stage is `pre-launch` or user explicitly requests ship prep.

**Infrastructure chain:**
- `/ds-devops` — CI/CD integrity, signing, dependency hygiene.
- `/ds-deploy` — container security, TLS, monitoring, incident runbook.
- `/ds-launch` — store submission / privacy labels / rollout (pick mode by
  project type: mobile / desktop / web).
- `/ds-repo` — branch protection, CODEOWNERS, metadata.

### Phase 5b — OSS Readiness Sub-Phase

Triggered when the project will be (or is) public. Validates:
- `LICENSE` present, valid, compatible with all dependency licenses.
- `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, issue+PR templates,
  `CODEOWNERS` — present and tailored to the project.
- README delivers a strong first impression: problem statement, install, quick
  usage, screenshot/demo where applicable, maintenance-signal freshness.
- Git history audited for leaked secrets (propose `git-filter-repo` surgery if
  found — category B, explicit approval).
- Project name: brief web check for trademark collision.
- Discoverability: GitHub topics, badges, short description, homepage URL.
- Dependabot / renovate configured where supported.

Category B proposals dominate this sub-phase — most OSS-readiness moves are
user-visible.

---

## Phase 6 — Consolidated Report

Produce or update `.ds-ship-report.md` in the repo root:

```markdown
## Summary
- Stage: <classified stage>
- Autonomous fixes applied (Category A): <N>
- Awaiting user decision (Category B): <M>
- Ship-ready: yes | no (N blockers remain)
- Doc token reduction: <before> → <after> (<%>)

## Architectural Changes (approved and applied)
| Change | Rationale | Concrete benefit |

## Autonomous Fixes (Category A)
| Fix | File:line | Which problem it solved |

## Awaiting User Decision (Category B)
| Proposal | Why needed | Risk / effort | Priority |

## Intentional Deviations (kept as-is)
| Item | Why it stays |

## Next Trigger
When should `ds-ship` next run? (e.g. "after feature X lands",
"before 2026-Q3 public release", "quarterly hygiene").
```

---

## Skill Chaining Rules

- You invoke other ds-* skills through the host tool's skill-invocation
  mechanism. You never reimplement their logic.
- Skills write to `.ds-findings.md`; you read from it.
- If two skills would produce overlapping findings on the same project type
  (see `docs/ds-skills-gap-analysis-*.md` for the overlap matrix), run only the
  authoritative one for that project type. Do not run both.
- If a skill fails or is unavailable, surface the gap — do not substitute with
  your own analysis.

## Explicit Non-Goals

- You do not replace `/ds-review`, `/ds-compliance`, `/ds-test`, or any other
  specialized skill.
- You do not maintain a project-specific database or state across sessions
  beyond `.ds-findings.md` and `.ds-ship-report.md`.
- You do not create logs, traces, history files, debug dumps, or analytics of
  your own runs.
- You do not perform destructive operations. Even approved Category B deletions
  go through git in small, reversible commits.

## Done Criteria

This orchestration is "done" when:
1. Category A queue is empty and every applied fix survives the test suite.
2. Category B queue is either applied (user approved) or explicitly deferred.
3. `.ds-findings.md` and `.ds-ship-report.md` reflect current reality.
4. Stage is re-classified and the next trigger is documented.

Anything short of all four remains `in_progress`. Never mark complete on a
partial pass.
