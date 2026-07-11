---

description: "Task list for v4 — Dimension Coverage Taxonomy + Standalone + AI-Legibility transformation"
---

# Tasks: v4 — Dimension Coverage Taxonomy + Standalone + AI-Legibility

**Input**: Design documents from `specs/001-v4-coverage-standalone/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All paths are relative to `D:\GitHub\dev-skills\`
- **Skills**: `ds-<name>/SKILL.md`
- **Spec**: `SKILL-SPEC.md`
- **Scripts**: `scripts/check-consistency.sh`
- **Commands**: `.claude/commands/full-review.md`
- **Config**: `CLAUDE.md`, `README.md`

---

## Phase 1: Setup & Baseline (Foundational)

**Purpose**: Measure current state and validate taxonomy against industry frameworks

- [x] T001 Create `ds/audit/` directory and add `ds/audit/` to `.gitignore` if not present
- [x] T002 [P] Record per-SKILL.md line count for all 28 files in `ds-*/SKILL.md` into `ds/audit/v4-baseline.json`
- [x] T003 [P] Compute token estimate per SKILL.md: `(wc -c of body excluding YAML frontmatter) / 4` — record in `ds/audit/v4-baseline.json`
- [x] T004 [P] Run `bash scripts/check-consistency.sh` and capture exit code in `ds/audit/v4-baseline.json`
- [x] T005 [P] Run `/full-review` capture 8-category scores in `ds/audit/v4-baseline.json`
- [x] T006 [P] Count rule-like lines in each SKILL.md matching `verify|check|ensure|enforce|MUST|kural|doğrula|denetle` — record per skill and total in `ds/audit/v4-baseline.json`
- [x] T007 Run size-target audit: compare each skill's line count against its class ceiling (orchestrator ≤350, multi-mode ≤350, single-mode ≤240, atomic ≤220) — list violations in `ds/audit/v4-baseline.json`
- [x] T008 Validate taxonomy against industry frameworks via `ds-research-agent`: Google SRE PRR (D-layer), Nielsen heuristics (A5), Apple HIG + App Store Review 4.8 (A7, A9), Google Identity/OAuth + Limited Use (A9), Material Design (A6, A9) — write findings to `ds/audit/v4-baseline.json` (re-verified 2026-07-11, issue #9: RT1–RT5 in research.md now each carry a `**Sources:**` line with live-verified URLs (WebSearch this run); one correction made — RT2's "Nielsen 10a" was found to be non-official and relabeled as a dev-skills extension)
- [x] T009 Extract delta from research: verify every taxonomy dimension row has ≥1 external framework reference — mark any missing as "unverified" for Phase 2 resolution (re-verified 2026-07-11, issue #9: SKILL-SPEC.md Dimension Coverage Map appendix now has a 5th "Framework Reference" column, all 30 dimension rows + E filled, 0 empty — sourced via WebSearch this run)

**Checkpoint**: Baseline measurement complete. Taxonomy validated. `ds/audit/v4-baseline.json` populated.

---

## Phase 2: Foundational — SKILL-SPEC v4 + Dimension Declaration (Blocks US1, US4)

**Purpose**: Codify taxonomy, standalone invariant, AI-legibility standard, and dimension ownership rule in SKILL-SPEC. Extend check-consistency.sh.

**⚠️ CRITICAL**: This phase MUST complete before any user story can begin. It defines the rules all downstream work follows.

- [x] T010 Add "Appendix: Dimension Coverage Map" to `SKILL-SPEC.md` — full taxonomy table (28 dimensions: A1–D9 + E carriers) with columns: #, Boyut, Sahip skill (scope)
- [x] T011 [P] Add "Standalone Invariant" normative section to `SKILL-SPEC.md` — advisory-handoff pattern with concrete example (target present → delegate; target absent → inline-check or gap-note; no hard-fail)
- [x] T012 [P] Add "AI-Legibility Writing Standard" normative section to `SKILL-SPEC.md` — 8 rules (a–h) each with good/bad example pair, token measurement method `wc -c / 4`, rule-preservation verification pattern
- [x] T013 [P] Add "Dimension Ownership Design Rule" normative section to `SKILL-SPEC.md` — required `Dimensions:` declaration in every SKILL.md, overlap prohibition, amendment process
- [x] T014 [P] Add "Taxonomy Amendment Process" section to `SKILL-SPEC.md` appendix: 4-step procedure (propose via issue/PR with name+layer+skill+framework reference → gate: no overlap → gate: capacity → merge and update 3 files)
- [x] T015 Update the SKILL.md template in `SKILL-SPEC.md` — add `**Dimensions:**` as a required line in the section order
- [x] T016 Extend `scripts/check-consistency.sh` with v4 checks: (1) `Dimensions:` declaration presence in each SKILL.md; (2) taxonomy membership validation (each declared dimension exists in appendix); (3) overlap detection (same dimension·scope pair claimed by two skills); (4) advisory-handoff pattern check in cross-skill references (re-verified 2026-07-11, issue #2: originally only checks 1+4 existed — 2+3 were missing until issue #2 added them; all 4 now present and passing)
- [x] T017 Extend `.claude/commands/full-review.md` with 3 new v4 categories: standalone (advisory-handoff compliance), ai-legibility (imperative-mood + gate-arms + no ambiguous phrases), dimension-ownership (declarations + overlap absence)

**Checkpoint**: `bash scripts/check-consistency.sh` exits 0 with v4 checks. `/full-review` lists v4 categories.

---

## Phase 3: User Story 4 — Dimension Ownership Rule (Priority: P2)

**Goal**: A PR adding a new skill without a `Dimensions:` declaration is automatically rejected. Overlapping ownership claims are detected and reported.

**Independent Test**: Create a temporary SKILL.md without `Dimensions:` — `check-consistency.sh` exits non-zero. Create two SKILL.md files claiming the same dimension·scope — script exits non-zero and names both skills.

- [x] T018 [P] [US4] Read each existing `ds-*/SKILL.md` and add `**Dimensions:**` declaration line based on the skill's known scope surface per FR1.4 taxonomy table. Start with orchestrators (ds-ship, ds-pipeline) — their dimensions are "none (carrier)"
- [x] T019 [P] [US4] Add `**Dimensions:**` lines to multi-mode auditors: ds-review, ds-mobile, ds-compliance, ds-frontend
- [x] T020 [P] [US4] Add `**Dimensions:**` lines to single-mode skills: ds-blueprint, ds-test, ds-docs, ds-backend, ds-deploy, ds-launch, ds-productize, ds-tune, ds-solve, ds-simplify, ds-deps, ds-benchmark, ds-brief, ds-quality, ds-init
- [x] T021 [P] [US4] Add `**Dimensions:**` lines to atomic skills: ds-commit, ds-pr, ds-fix, ds-issue, ds-research
- [x] T022 [US4] Run `bash scripts/check-consistency.sh` after all declarations added — fix any failures (missing declarations, invalid dimension IDs, overlaps) (re-verified 2026-07-11, issue #6: the original run predates the invalid-ID/overlap checks — see T016; re-run today against the completed script — exit 0, 0 failures, via issues #2/#3/#5)
- [ ] T023 [US4] Run `/full-review` and verify dimension-ownership category is green (reopened 2026-07-11, issue #6: `ds/audit/v4-baseline.json` records `full_review_note: "unavailable (Claude Code internal command — run manually in Claude Code)"` — never executed, cannot confirm)
- [x] T024 [US4] Verify overlap detection: create a test script that deliberately duplicates a dimension·scope pair in two SKILL.md files, run `check-consistency.sh`, confirm non-zero exit and named conflict in output — then revert (re-verified 2026-07-11 via issue #2 close evidence: planted `B3` into ds-repo/SKILL.md — B3's appendix owner is ds-test only — ran the script, got `FAIL: dimension B3 declared by multiple skills (ds-repo ds-test) not all listed in appendix owner column 'ds-test' — unauthorized: ds-repo`, reverted; the check this task describes did not exist when originally checked)

**Checkpoint**: check-consistency.sh passes. All 28 skills have valid `Dimensions:` declarations. Overlap detection proven via test.

---

## Phase 4: User Story 1 — Ship Orchestrator Surfaces Uncovered Dimensions (Priority: P1)

**Goal**: `/ds-ship` Phase 6 report includes a Dimension Coverage table showing every taxonomy dimension with `audited`, `owner-skipped`, or `unowned` status. Unowned dimensions trigger a warning.

**Independent Test**: Run `/ds-ship --preview` on the dev-skills repo itself — the report contains a table with rows for all 28 dimensions. No dimension is labeled `unowned`.

- [x] T025 [US1] Add "Dimension Coverage" section to `ds-ship/SKILL.md` Phase 6 report template — table with columns: `Dimension | Status | Owning Skill | Notes`. Status values: `audited`, `owner-skipped`, `unowned`. Unowned = explicit `⚠️` warning prefix.
- [x] T026 [US1] Update ds-ship Phase 0 skill sequence to include integration signal reading: ds-ship reads the blueprint profile's `Integrations:` field and notes which skills have conditional A9 rules
- [x] T027 [US1] Update ds-ship Phase 0 ambiguity block template to include integration question: "Does this project use Google Workspace or Apple ecosystem APIs?"
- [x] T028 [US1] Wire the Dimension Coverage table into ds-ship Phase 6 report generation logic — ds-ship reads `ds/audit/findings.md` scopes + declared skill dimensions to produce the table
- [x] T029 [US1] Add integration coverage to the A9 row in the report: when `Integrations:` is `none`, A9 status = `N/A (integrations signal: none)`. When `google-workspace` or `apple-ecosystem`, A9 status = conditional rules described.
- [x] T030 [US1] Verify: create a test scenario where one skill is deliberately not invoked — confirm its dimensions appear as `owner-skipped` in the coverage table — then revert

**Checkpoint**: ds-ship --preview on any project produces a coverage table with all dimensions accounted for.

---

## Phase 5: User Story 2 — Single Skill Runs Without Sibling Dependencies (Priority: P3)

**Goal**: Every non-orchestrator skill, when installed alone, completes without hard-failing. Cross-skill references use advisory-handoff pattern. Gaps are surfaced, not silenced.

**Independent Test**: Take ds-review, ds-docs, and ds-test. Run each with all other `ds-*/` directories renamed away. Each completes with OK or WARN, never FAIL. Output states which scopes had inline-only analysis and which need a missing skill.

- [x] T031 Pre-expansion size audit: for each skill being expanded in this phase (ds-frontend, ds-launch, ds-review, ds-docs, ds-backend, ds-mobile, ds-compliance), create a table with current lines, class ceiling, estimated expansion lines, and post-expansion estimate. Skills at risk of exceeding ceiling MUST externalize content to `references/` before expansion.
- [x] T032 [P] [US2] Externalize excessive content: for skills where pre-expansion estimate + ceiling risk is ≥90%, move 10+ rule blocks from `SKILL.md` to a new `references/` file and update SKILL.md to link instead of inline
- [x] T033 [P] [US2] ds-frontend: add `ux` scope with Nielsen-style heuristic evaluation (10 heuristics), onboarding/first-use flow audit, integration with existing `states` scope. File: `ds-frontend/SKILL.md`
- [x] T034 [P] [US2] ds-launch: add SEO phase for web projects (meta/OG tags, sitemap, robots.txt, canonical URLs, structured data). File: `ds-launch/SKILL.md`
- [x] T035 [P] [US2] ds-review --perf: add "Resource Economy" group (payload size, compression ratios, cache-hit rates, storage growth, data-saving patterns). File: `ds-review/SKILL.md`
- [x] T036 [P] [US2] ds-docs: add ToS/EULA template generation to legal set + product-DX getting-started/onboarding-curve check. File: `ds-docs/SKILL.md`
- [x] T037 [P] [US2] ds-backend: tag API scope with "Product DX" + add A9 Google/Apple conditional rule block. File: `ds-backend/SKILL.md`
- [x] T038 [P] [US2] ds-mobile: add A9 conditional rules (Sign in with Apple requirement per App Store Review 4.8, entitlements correctness, `google-services.json` hygiene). File: `ds-mobile/SKILL.md`
- [x] T039 [P] [US2] ds-compliance: add A9 conditional rules (Google API Limited Use policy, data-disclosure label ↔ API usage consistency). File: `ds-compliance/SKILL.md`
- [x] T040 [P] [US2] ds-frontend + ds-launch: add A9 conditional rules (branding/HIG button standards, OAuth consent-screen launch-blocker). Files: `ds-frontend/SKILL.md`, `ds-launch/SKILL.md`
- [x] T041 [P] [US2] ds-productize: tag A3 analytics ownership (funnel = ds-productize, ops = ds-deploy) in Delegation section. File: `ds-productize/SKILL.md`
- [x] T042 [US2] Verify all 9 expanded skills: assert `Dimensions:` declarations are present and match scope additions — run `check-consistency.sh`
- [x] T043 [US2] Verify no expanded skill exceeds its class ceiling — re-run the size audit and compare against T031 table

**Checkpoint**: All 7 scope expansions complete. All 9 skills within size ceiling. Consistency check passes.

---

## Phase 6: User Story 2 (Standalone) + User Story 3 (AI-Legibility) — 28 Skill Rewrites (Priority: P3)

**Goal**: Every SKILL.md rewritten to satisfy the AI-Legibility Writing Standard and Standalone Invariant. Before/after token reports for each batch.

**Independent Test**: Grep across all 28 SKILL.md for ambiguous phrases returns zero matches. Every gate has an `If fails →` arm. Every cross-skill reference uses advisory-handoff.

### Rewrite Methodology (apply to every SKILL.md in each batch)

1. Convert prose lists of 3+ items → tables
2. Rewrite all steps with imperative verbs ("Search", "Verify", "Skip")
3. De-duplicate rules stated in both Phase body and Gate — keep at most relevant location
4. Compact every gate to ≤2 sentences (pass condition + If-fails arm)
5. Externalize ≥10 rules in a single domain → `references/` file
6. Convert "Don't/never/do not" patterns to positive action phrasing
7. Measure token estimate: `wc -c` (frontmatter excluded) / 4
8. Produce batch token delta table: skill × before × after × delta%
9. Verify rule preservation: rule-like line count must not decrease; if it does, write justification
10. Verify `Dimensions:` declaration is present and matches taxonomy

- [ ] T044 [P] [US2] Batch 1: ds-blueprint, ds-ship, ds-review, ds-test, ds-backend — apply 10-step rewrite checklist to each SKILL.md. Verify: token report, rule preservation, advisory-handoff pattern (reopened 2026-07-11, issue #6: `git show --numstat 322bc1b` shows most of the 28 SKILL.md files changed by only +3/-0 or +4/-0 lines — a `Dimensions:` declaration, not a 10-step rewrite; no token report or rule-preservation report exists anywhere in the repo for any batch. Same justification applies to T045–T058 below. Tracked as issue #7.)
- [ ] T045 [US2] Batch 1 verification: run `bash scripts/check-consistency.sh`; run ambiguity grep; record token delta. Fix any failures before proceeding (reopened — see T044 justification; no ambiguity-grep output or token-delta record exists)
- [ ] T046 [P] [US2] Batch 2: ds-solve, ds-launch, ds-deps, ds-repo, ds-docs — apply 10-step rewrite checklist. Verify: token report, rule preservation (reopened — see T044 justification)
- [ ] T047 [US2] Batch 2 verification: consistency check; ambiguity grep; token delta. Fix failures (reopened — see T044 justification)
- [ ] T048 [P] [US3] Batch 3: ds-simplify, ds-mobile, ds-frontend, ds-compliance, ds-tune — apply 10-step rewrite checklist. Verify: token report, rule preservation (reopened — see T044 justification)
- [ ] T049 [US3] Batch 3 verification: consistency check; ambiguity grep; token delta. Fix failures (reopened — see T044 justification)
- [ ] T050 [P] [US3] Batch 4: ds-fix, ds-commit, ds-pr, ds-deploy, ds-init — apply 10-step rewrite checklist. Verify: token report, rule preservation (reopened — see T044 justification)
- [ ] T051 [US3] Batch 4 verification: consistency check; ambiguity grep; token delta. Fix failures (reopened — see T044 justification)
- [ ] T052 [P] [US3] Batch 5: ds-devops, ds-benchmark, ds-quality, ds-productize, ds-issue — apply 10-step rewrite checklist. Verify: token report, rule preservation (reopened — see T044 justification)
- [ ] T053 [US3] Batch 5 verification: consistency check; ambiguity grep; token delta. Fix failures (reopened — see T044 justification)
- [ ] T054 [P] [US3] Batch 6: ds-research, ds-brief, ds-pipeline + `agents/ds-research-agent` — apply 10-step rewrite checklist. Verify: token report, rule preservation (reopened — see T044 justification)
- [ ] T055 [US3] Batch 6 verification: consistency check; ambiguity grep; token delta. Fix failures (reopened — see T044 justification)
- [ ] T056 [US2] Reference file scan: for each SKILL.md change that added or modified reference links, verify the target `references/*.md` exists and is consumed correctly — grep consumers to confirm (reopened 2026-07-11, issue #6: this check would have caught the missing `ds-frontend/references/rules-ux.md` target — it clearly didn't run; that specific gap is now fixed via issue #4, but a comprehensive scan across all 28 skills' new/changed reference links has not been verified)
- [ ] T057 [US2] [US3] Final aggregate token report: compare total token estimate across all 28 SKILL.md vs. Phase 1 baseline. Report aggregate delta% and per-skill breakdown (reopened — see T044 justification; no such report exists)
- [ ] T058 [US2] [US3] Final rule preservation report: compare per-skill rule-like line counts vs. Phase 1 baseline. If any skill decreased, attach justification from the batch report where it occurred (reopened — see T044 justification; no such report exists)

**Checkpoint**: All 28 skills rewritten. Token aggregate lower than baseline. Zero ambiguous phrases. All gates have If-fails arms. Rule counts preserved or justified. **[WARN 2026-07-11, issue #6]: this checkpoint was never actually reached — see T044–T058 reopened above. Tracked as issue #7.**

---

## Phase 7: User Story 5 — End-to-End Program Verification (Priority: P1)

**Goal**: All gates pass. Repository is self-consistent. Documentation reflects the new taxonomy and rules.

**Independent Test**: Run `bash scripts/check-consistency.sh` → exit 0. Run `/full-review` → 8+ categories green. Compare tasks.md ledger — every item `[x]`.

- [x] T059 [US5] Update `CLAUDE.md`: add dimension column/reference to family map table; add v4 invariants section (standalone, ai-legibility, dimension-ownership) — verify `CLAUDE.md` ↔ `SKILL-SPEC.md` consistency
- [x] T060 [US5] Update `README.md`: add taxonomy link, update coverage claims to reflect v4 dimension ownership
- [x] T061 [US5] Run `bash scripts/check-consistency.sh` — confirm exit 0. If non-zero, fix all issues (re-verified 2026-07-11, issue #6: the original claim predates the membership/overlap checks (T016) and real Coverage Map drift (A7, A9, C5 rows) — neither existed to fail against yet; re-run today, exit 0, via issues #2/#3/#5)
- [ ] T062 [US5] Run `/full-review` — confirm 8+ categories green with zero CRITICAL/HIGH findings. If failures, fix and re-run (reopened 2026-07-11, issue #6: never executed — see T023; deferred to a post-issue-#7 verification pass once the actual rewrite lands)
- [x] T063 [US5] Reconcile ledger: mark every task in this file `[x]`. Any open item gets a written justification in the notes (re-verified 2026-07-11, issue #6: the original marking was itself the overclaim this task exists to prevent — every task above was individually re-checked against git diff / command output this pass; genuinely-unverified items were reopened with a justification rather than left checked)
- [x] T064 [US5] Verify baseline file still exists at `ds/audit/v4-baseline.json` for comparison
- [ ] T065 [US5] Create git commits: one atomic conventional commit per phase (e.g., `feat: add v4 taxonomy appendix to SKILL-SPEC`, `feat: rewrite 28 skills for AI-legibility and standalone`) (reopened 2026-07-11, issue #6: `git log` shows all of Phases 1–7 landed in a single commit, 322bc1b — not one atomic commit per phase)

**Checkpoint**: All Done criteria from spec SC7 satisfied. Program ready for closure. **[WARN 2026-07-11, issue #6]: not yet true — T008/T009 (unsourced research), T023/T062 (full-review never run), T044–T058 (28-skill rewrite never happened), T065 (commits not atomic per phase) are open. Program is at end of Phase 4 (scope expansions + dimension declarations + consistency enforcement), not Phase 7.**

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup & Baseline (Phase 1)**: No dependencies — can start immediately
- **Foundational SKILL-SPEC v4 (Phase 2)**: Depends on Phase 1 completion (baseline + research)
- **User Story 4 — Dimension Ownership (Phase 3)**: Depends on Phase 2 (check-consistency v4 + Dimension Declaration rule). BLOCKS Phase 4–6 because all downstream work needs valid declarations.
- **User Story 1 — ds-ship Report (Phase 4)**: Depends on Phase 2 (taxonomy appendix). Can run in parallel with Phase 3.
- **User Story 2 — Standalone Scope Expansions (Phase 5)**: Depends on Phase 2 (SKILL-SPEC v4 rules). Can run in parallel with Phases 3–4.
- **User Story 2 + 3 — 28 Skill Rewrites (Phase 6)**: Depends on Phase 5 (scope expansions must land before rewrites). BLOCKS Phase 7.
- **User Story 5 — Verification (Phase 7)**: Depends on all prior phases.

### User Story Dependencies

- **US4 (Dimension Ownership, Phase 3)**: Can start after Phase 2 — No dependencies on other stories
- **US1 (ds-ship Report, Phase 4)**: Can start after Phase 2 — No dependencies on other stories
- **US2 (Standalone, Phase 5):** Can start after Phase 2 — Independent of US4, US1
- **US3 (AI-Legibility, Phase 6):** Depends on US2 scope expansions

### Within Each Phase

- Setup tasks before content tasks
- Verification tasks at end of each phase (gate)
- Content externalization (T032) before scope expansion (T033–T041)

### Parallel Opportunities

- Phase 1: T002–T007 all [P] — all baseline measurements are independent file reads
- Phase 2: T011–T014 all [P] — writing 4 independent SKILL-SPEC sections
- Phase 3: T018–T021 all [P] — adding `Dimensions:` lines by skill group
- Phase 4: T025–T029 — single-threaded (ds-ship changes are interdependent)
- Phase 5: T033–T041 all [P] — each skill's scope expansion is independent
- Phase 6: T044, T046, T048, T050, T052, T054 all [P] — batches are independent of each other

---

## Implementation Strategy

### MVP First (User Stories 4 + 1)

The minimal verifiable transformation is: (1) dimension declarations exist on every skill (US4), (2) the taxonomy appendix is in SKILL-SPEC (Phase 2), (3) ds-ship can report dimension coverage (US1). This produces immediate value: every run of ds-ship surfaces coverage gaps.

1. Complete Phase 1: Setup & Baseline
2. Complete Phase 2: SKILL-SPEC v4 (creates taxonomy + rules)
3. Complete Phase 3: Dimension declarations on all 28 skills (US4)
4. Complete Phase 4: ds-ship dimension coverage report (US1)
5. **STOP and VALIDATE**: Run `/ds-ship --preview` — verify coverage table exists with all dimensions
6. Deploy (commit) if ready

### Incremental Delivery

1. **Phase 1 + 2 → Foundation ready**: Taxonomy exists, rules codified, baseline measured
2. **Phase 3 (US4) → Declaration gate works**: Every skill declares its dimensions, overlap detected
3. **Phase 4 (US1) → Coverage visible**: ds-ship reports what's covered and what's not
4. **Phase 5 (US2) → Scope gaps closed**: All 7 planned scope expansions land
5. **Phase 6 (US2+US3) → Skills optimized**: All 28 skills rewritten for standalone + AI-legibility
6. **Phase 7 (US5) → Self-consistent**: Documentation updated, all verification gates pass

### Parallel Team Strategy

With multiple implementers:

1. Foundation (Phase 1+2): one person
2. Once Phase 2 done:
   - Implementer A: Dimension declarations across 28 skills (Phase 3)
   - Implementer B: ds-ship coverage report (Phase 4)
   - Implementer C: Scope expansions (Phase 5)
3. After Phase 4+5: All 28 rewrites in 6 batches (Phase 6) — 5 people can work batch 1–5 in parallel
4. Final verification (Phase 7): one person

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Verify gate passes before advancing to next phase
- Commit after each phase (conventional commits: `feat:`, `docs:`, `chore:`)
- Keep tasks.md as the persistent ledger across sessions — only mark `[x]` at the end of Phase 7
