# Specification: v4 — Dimension Coverage Taxonomy + Standalone + AI-Legibility

**Feature directory:** `specs/001-v4-coverage-standalone`
**Source plan:** `tasks.md` (2026-07-11)
**Status:** Draft
**Input:** Transform the 28-skill dev-skills suite into a production-grade dimension taxonomy with standalone operation and AI-optimized instruction text.

---

## Overview

### Problem Statement

The dev-skills suite (28 skills) lacks a complete quality/coverage dimension taxonomy. Four product-quality dimensions have no dedicated owner (partial coverage), one dimension has zero coverage, and no skill reports which dimensions it covers and which it leaves unattended. When a user runs the orchestrator (`/ds-ship`), the final report cannot answer: "Were all dimensions of my product audited? What was missed?"

Additionally, skills are not standalone — they assume sibling skills are installed. Skill instruction text is verbose, contains ambiguous phrasing, and imposes unnecessary token cost on every invocation. These issues compound as new models (with different instruction-following characteristics) enter the ecosystem.

### Value Proposition

After this transformation:

1. A user running `/ds-ship` receives a **dimension coverage report** showing exactly which dimensions were audited, which were skipped, and which have no owner
2. Every skill runs correctly **alone** — no hard dependency on sibling skills
3. Skill instruction text is **token-optimized** and **unambiguous** — a low-capability model can execute it without deviation
4. Future skills and scopes are governed by a documented **design rule** that prevents dimension ownership gaps

### Scope

**In scope:**
- SKILL-SPEC.md — the authoritative format spec
- 28 SKILL.md files — one per skill
- Referenced `references/*.md` files affected by skill changes
- CLAUDE.md — project instruction file (blueprint profile, family map)
- README.md — coverage claims
- `.claude/commands/full-review.md` — quality check updates
- `scripts/check-consistency.sh` — automated conformance checks

**Out of scope:**
- New skill creation (decision: not needed — existing 28 skills are sufficient)
- `install.sh` / CI pipeline architecture changes
- Any source code changes (repo is Markdown-only)

---

## User Scenarios & Testing

### U1: Ship orchestrator surfaces uncovered dimensions

**Persona:** Developer running `/ds-ship` before a release

**Scenario:** The user invokes `/ds-ship` on a project. After delegated skills complete their audits, the Phase 6 report includes a **Dimension Coverage** table listing every known dimension with status: `audited` / `owner-skipped` / `unowned`. A dimension marked `unowned` is accompanied by an explicit warning.

**Acceptance:**
- Report contains a complete dimension × status table
- Every dimension in the taxonomy appears in the table
- `unowned` rows are visually distinct (warning prefix)
- The table is readable in a plain markdown terminal (no HTML required)

### U2: Single skill runs without sibling dependencies

**Persona:** Developer who installed only `ds-review` (not full suite)

**Scenario:** The user runs `/ds-review --tactical` on a project. No other ds-* skills are installed. The skill detects missing sibling skills but does not hard-fail. It runs its own complete analysis for any scope that a missing skill would normally provide. If a scope is partially covered (the skill can do a basic check but cannot match the absent skill's depth), it reports the gap openly rather than silently omitting it.

**Acceptance:**
- `/ds-review` completes with status `OK` or `WARN` — never crashes with "skill not found"
- Output states which scopes were fully analyzed, which were basic-only (with inline reason), and which delegated skill would provide deeper analysis if installed
- No silent scope omission — every scope is either analyzed or reported as gap

### U3: AI-legible skill text is unambiguous for low-capability models

**Persona:** Model evaluation — a Haiku-class agent (low reasoning capability) executes a rewritten skill

**Scenario:** A skill's SKILL.md is passed to a model with limited reasoning. The model follows each numbered step in order, never encountering a decision point where it must choose between two plausible interpretations. Every condition is an explicit `if/then` table row. Every gate has exactly two arms: pass condition + failure recovery action. The model produces identical output to a high-capability model on the same codebase.

**Acceptance:**
- Zero ambiguous phrases ("if appropriate", "consider", "may want to", "as needed")
- Every condition is stated as a concrete threshold or testable predicate
- Every gate line has an `If fails →` arm
- Rewritten skill produces identical findings on the same codebase when run by a reasoning model and a non-reasoning model

### U4: New skill contribution governed by dimension ownership rule

**Persona:** Open-source contributor proposing a new skill

**Scenario:** A contributor opens a PR adding a new skill. The PR body declares which taxonomy dimension(s) the skill owns. An automated check (`check-consistency.sh` v4) verifies: the dimension exists in the taxonomy appendix, no other skill claims the same dimension surface, and the new skill does not exceed its size ceiling. A PR without a `Dimensions:` declaration is rejected at the gate.

**Acceptance:**
- `check-consistency.sh` exits non-zero when a SKILL.md lacks a `Dimensions:` declaration
- The script detects dimension surface overlaps between two skills
- The script reports which dimension is in conflict and which two skills claim it
- A new skill's SKILL.md template includes the `Dimensions:` field

### U5: End-to-end program verification

**Persona:** Program maintainer after all phases complete

**Scenario:** After Phase 6 reconciliation, the maintainer runs `/full-review` and `check-consistency.sh`. Both produce green results. The dimension taxonomy in SKILL-SPEC appendix matches the taxonomy in tasks.md. Every SKILL.md declares its dimensions. The CLAUDE.md family map includes a dimension reference column. README.md links to the taxonomy.

**Acceptance:**
- `bash scripts/check-consistency.sh` → exit 0
- `/full-review` → 8+ categories green, zero CRITICAL or HIGH findings
- Every TODO item in tasks.md is `[x]`
- Git log shows atomic conventional commits per phase

---

## Functional Requirements

### FR1: Dimension Coverage Taxonomy

FR1.1 The system MUST define a complete taxonomy of quality/coverage dimensions grouped into five layers:
- **A — Product & Market** (10 dimensions: A1 through A10)
- **B — Engineering** (6 dimensions: B1 through B6)
- **C — Trust & Compliance** (5 dimensions: C1 through C5)
- **D — Operations** (9 dimensions: D1 through D9)
- **E — Process carriers** (not dimensions — skills that orchestrate, commit, or plan)

FR1.2 Every dimension MUST have exactly one primary owning skill (or skill pair with clearly divided surfaces). No dimension may be unowned.

FR1.3 The taxonomy MUST be stored in SKILL-SPEC.md as a normative appendix ("Dimension Coverage Map") with columns: dimension number, name, owning skill(s), and scope surface.

FR1.4 The taxonomy MUST include these dimensions (minimum set):

| Layer | ID | Dimension | Owner |
|-------|-----|-----------|-------|
| A | A1 | Market positioning & competitive advantage | ds-benchmark + ds-productize |
| A | A2 | Monetization (pricing/billing/entitlements) | ds-productize |
| A | A3 | Analytics/telemetry | ds-productize + ds-deploy |
| A | A4 | Discoverability (SEO + ASO + repo topics) | ds-launch |
| A | A5 | Usability / onboarding / intuitiveness | ds-frontend (ux scope) |
| A | A6 | UI visual quality & consistency | ds-frontend |
| A | A7 | Accessibility (a11y) | ds-frontend (impl) + ds-compliance (regulatory) |
| A | A8 | i18n/l10n | ds-fix (mechanical) + ds-compliance (rules) |
| A | A9 | Ecosystem integration (Google + Apple) | blueprint signal + conditional rules (5 skills) |
| A | A10 | API reference quality (OpenAPI/SDK/examples) | ds-docs + ds-backend |
| B | B1 | Code quality & simplicity | ds-review, ds-fix, ds-simplify, ds-quality |
| B | B2 | Architectural health | ds-blueprint + ds-review --strategic |
| B | B3 | Testing & verification | ds-test |
| B | B4 | DX — contributor | ds-blueprint + ds-repo |
| B | B5 | DX — product (devtool/API products) | ds-backend + ds-docs |
| B | B6 | Documentation | ds-docs |
| C | C1 | Security | ds-compliance (canonical) + 4 execution skills |
| C | C2 | Privacy & data protection | ds-compliance (canonical) |
| C | C3 | Legal (ToS/EULA, license, regulation) | ds-compliance + ds-docs + ds-repo |
| C | C4 | Supply chain / dependencies | ds-deps |
| C | C5 | Deprecation management (sunset/migration guides) | ds-docs + ds-repo |
| D | D1 | Performance & efficiency | ds-review --perf + ds-launch --perf-budget + ds-tune |
| D | D2 | Resource economy (payload/bandwidth/storage) | ds-review --perf + ds-deploy --cost |
| D | D3 | Resilience/reliability (retry/DR/backup) | ds-backend + ds-deploy |
| D | D4 | Observability/monitoring | ds-deploy + ds-backend |
| D | D5 | Data management (schema/migration/retention) | ds-backend |
| D | D6 | CI/CD & release engineering | ds-devops + ds-launch |
| D | D7 | Deploy/infra & incident response | ds-deploy |
| D | D8 | Repo governance | ds-repo |
| D | D9 | Breaking-change management (semver/schema/contract) | ds-deps + ds-review |
| E | — | Process carriers | ds-ship, ds-pipeline, ds-commit, ds-pr, ds-issue, ds-init, ds-solve, ds-tune, ds-research, ds-brief |

FR1.5 The taxonomy MUST be verified against industry frameworks before freezing: Google SRE production-readiness (PRR), Nielsen usability heuristics (current edition), Apple HIG + App Store Review Guidelines (specifically 4.8 login), Google Identity/OAuth verification + Limited Use, and Material Design.

FR1.6 A taxonomy amendment process MUST be documented in SKILL-SPEC: to add a new dimension, a contributor proposes via issue/PR with dimension name, layer, owning skill, and at least one industry framework reference; two gates apply (no existing skill covers this surface; owning skill has capacity under its size ceiling); after merge the owning skill's SKILL.md, the SKILL-SPEC appendix, and the ds-ship report are updated.

### FR2: Standalone Operation

FR2.1 Every non-orchestrator skill MUST function correctly when installed alone — zero hard dependencies on sibling skills.

FR2.2 Cross-skill references MUST use the "advisory handoff" pattern: if the target skill is present → delegate; if absent → either (a) perform a minimal inline check, or (b) emit an explicit gap note. The skill MUST NOT hard-fail or silently skip a scope.

FR2.3 Orchestrator skills (ds-ship, ds-pipeline) MUST surface missing skills in a `## Missing skills` section of their report.

FR2.4 The standalone invariant MUST be added to SKILL-SPEC as a normative rule with a concrete example of the advisory-handoff pattern.

### FR3: AI-Legibility

FR3.1 Every SKILL.md MUST satisfy the AI-Legibility Writing Standard:
- (a) Single-interpretation imperative sentences
- (b) One term per concept — synonym drift prohibited
- (c) Tables preferred over prose for multi-item lists
- (d) Every phase has explicit input/output contract
- (e) Implicit context dependencies prohibited
- (f) Vague quantities/conditions prohibited — every condition is stated explicitly
- (g) Decision points use explicit if/then tables (no model inference required)
- (h) Token reduction is measured (before/after count) while preserving or improving work quality

FR3.2 Token count MUST be measured using the standard: `(wc -c of SKILL.md body excluding YAML frontmatter) / 4`. Before/after reports use the format `N → M (delta%)`.

FR3.3 Each skill rewrite MUST preserve all existing behavioral rules. Rule preservation is verified by counting lines matching the pattern `verify|check|ensure|enforce|MUST|kural|doğrula|denetle` before and after rewrite. Any decrease requires a written justification.

FR3.4 The AI-Legibility standard MUST be added to SKILL-SPEC as a normative section with good/bad example pairs for each of the 8 rules.

### FR4: Dimension Ownership Design Rule

FR4.1 Every SKILL.md MUST declare which taxonomy dimension(s) it owns, using a `Dimensions:` line or section.

FR4.2 No dimension may be left unowned. Two skills MUST NOT own the same surface of the same dimension (overlap = specification violation).

FR4.3 The `check-consistency.sh` script MUST verify dimension declarations, taxonomy validity, and overlap absence. A SKILL.md without a `Dimensions:` declaration MUST cause the script to exit non-zero.

FR4.4 The SKILL.md template in SKILL-SPEC MUST include the `Dimensions:` field as a required section.

### FR5: Dimension Coverage in ds-ship Report

FR5.1 The `/ds-ship` Phase 6 report MUST include a "Dimension Coverage" section: a table with columns `Dimension | Status | Owning Skill | Notes`. Status values: `audited` (skill ran and produced findings), `owner-skipped` (skill exists but was not invoked or skipped the dimension), `unowned` (no skill claims this dimension).

FR5.2 Any dimension with status `unowned` MUST be accompanied by an explicit warning in the report summary.

FR5.3 ds-ship Phase 0 MUST read the blueprint profile's `Integrations:` field. When Google or Apple ecosystem signals are active, ds-ship MUST note which skills have conditional A9 rules that will be triggered, and include this in the Phase 6 coverage table under A9.

### FR6: Ecosystem Integration (A9) Detection

FR6.1 The blueprint profile MUST include an `Integrations:` field with values: `google-workspace | apple-ecosystem | none`.

FR6.2 Detection signals for Google: `google_sign_in`, `googleapis`, GIS/GSI script references. For Apple: `Sign in with Apple` entitlement, `StoreKit`, `CloudKit`, `AuthenticationServices`.

FR6.3 Five skills receive conditional rule blocks triggered by the integrations signal:
- ds-backend: OAuth scope minimization, incremental authorization, Google verification + Limited Use, API quota/backoff, refresh-token security; Apple token verification, private relay email handling
- ds-mobile: Sign in with Apple requirement (App Store Review 4.8), entitlements correctness, `google-services.json` hygiene
- ds-compliance: Google API Limited Use policy, data-disclosure label ↔ API usage consistency
- ds-launch: Store requirements + OAuth consent screen production approval as launch-blocker
- ds-frontend: Official button/flow standards (Google Identity branding, Apple HIG Sign-in)

FR6.4 ds-blueprint MUST provide a `--test-integrations=google|apple|both` flag to simulate integration signals for testing. This flag is test-only and not intended for production use.

### FR7: Scope Expansions (Gap Closure)

FR7.1 ds-frontend MUST gain a `ux` scope covering: Nielsen-style heuristic evaluation (10 heuristics adapted for dev tools), onboarding/first-use flow audit, and integration with the existing `states` scope.

FR7.2 ds-launch MUST gain an SEO phase for web projects: meta/OG tags, sitemap, robots.txt, canonical URLs, structured data.

FR7.3 ds-review `--perf` MUST gain a "Resource Economy" group: payload size, compression ratios, cache-hit rates, storage growth trends, data-saving patterns.

FR7.4 ds-docs MUST gain a ToS/EULA template (completing the legal documentation set alongside the existing Privacy Policy template) and a product-DX getting-started/onboarding-curve check.

FR7.5 ds-backend MUST gain a "Product DX" tag on its API scope and the A9 conditional rule block.

FR7.6 ds-mobile, ds-compliance, ds-frontend, and ds-launch MUST gain their respective A9 conditional rule blocks.

FR7.7 Before any scope expansion, a size capacity audit MUST verify that the expanded skill does not exceed its class ceiling (orchestrator ≤350 lines, multi-mode auditor ≤350, single-mode ≤240, atomic ≤220). Skills at risk of exceeding the ceiling MUST externalize existing content to `references/` before adding new scope.

### FR8: Baseline, Measurement, and Verification

FR8.1 Before any transformation begins, a baseline MUST be recorded in `ds/audit/v4-baseline.json` containing: per-skill line count, total reference file line count, per-skill token estimate, size-target violation list, `check-consistency.sh` exit code, `/full-review` score, and approximate rule count per skill.

FR8.2 Every Phase 5 rewrite batch MUST produce a before/after token report comparing current state against the baseline.

FR8.3 At program completion, all three verification gates MUST pass:
- `bash scripts/check-consistency.sh` → exit 0
- `/full-review` → 8+ categories green, zero CRITICAL or HIGH findings
- All tasks.md items marked `[x]`

---

## Success Criteria

### SC1: Zero Uncovered Dimensions

After Phase 4 completion, every taxonomy dimension (A1–D9) has an owning skill with a documented scope. The `check-consistency.sh` script verifies this automatically. No dimension is flagged `unowned` in ds-ship's Dimension Coverage report.

### SC2: Standalone Operation Verified

A random sample of 3 non-orchestrator skills, each installed alone (no sibling skills), completes a full run on a test project without hard-failing. Each produces either `OK` or `WARN` status — never a crash, never a silent scope skip.

### SC3: Token Reduction Measurable

The total token estimate across all 28 SKILL.md files after Phase 5 is lower than the Phase 0.5 baseline, with zero behavioral rule loss. The aggregate delta is reported as percentage reduction.

### SC4: Ambiguity Eliminated

After Phase 5, zero ambiguous phrases remain across all 28 SKILL.md files. A grep for `if appropriate`, `consider`, `may want to`, `as needed`, `might`, `possibly`, `could`, `should consider`, `it is recommended` returns zero matches in instruction text (not in examples or placeholder text).

### SC5: Dimension Ownership Enforced Automatically

A PR adding a new skill without a `Dimensions:` declaration is rejected by `check-consistency.sh`. A PR where two skills claim the same dimension surface is rejected. This is tested by creating a deliberately violating skill and confirming the script exits non-zero.

### SC6: ds-ship Report Contains Dimension Coverage

Running `/ds-ship --preview` on any project produces a report containing the Dimension Coverage table. The table has a row for every taxonomy dimension. Unowned dimensions are marked with a warning.

### SC7: Full Program Self-Consistency

After Phase 6:
- `check-consistency.sh` exits 0
- `/full-review` reports 8+ categories green
- No CRITICAL or HIGH findings remain
- Every tasks.md item is `[x]`
- The baseline measurement file still exists for comparison

---

## Key Entities

| Entity | Description | Location |
|--------|-------------|----------|
| **Dimension** | A named quality/coverage area with a layer (A–D), an owning skill, and a defined scope surface | SKILL-SPEC appendix "Dimension Coverage Map" |
| **Taxonomy** | The complete set of 28 dimensions across 4 layers, plus the E carrier list | SKILL-SPEC appendix (normative SSOT) |
| **Skill** | A self-contained markdown instruction file (SKILL.md) that performs a specific quality task | `ds-<name>/SKILL.md` |
| **Dimension Declaration** | A `Dimensions:` line in each SKILL.md listing which taxonomy dimensions the skill owns | Each SKILL.md |
| **Advisory Handoff** | A cross-skill reference pattern: delegate if target exists, else inline-fallback or gap-note | SKILL-SPEC "Standalone Invariant" section |
| **Blueprint Profile** | Project metadata (type, stack, priorities, constraints, integrations) between `## Blueprint Profile` markers | AI instruction file (CLAUDE.md) |
| **Baseline** | Pre-transformation metrics snapshot: line counts, token estimates, rule counts, conformance scores | `ds/audit/v4-baseline.json` |
| **Integration Signal** | Detected Google or Apple ecosystem presence, stored in blueprint profile's `Integrations:` field | Blueprint profile |
| **Conditional Rule Block** | Skill rules that activate only when a specific integration signal is present; zero noise when absent | A9-owning skills |

---

## Assumptions

1. The existing 28 skills are sufficient — no new skills need to be created. Gaps are closed through scope expansion into existing skills.
2. The taxonomy dimensions cover all quality concerns relevant to a production software project. Dimensions not in the taxonomy are considered out of scope for this program.
3. Token measurement using `wc -c / 4` is an adequate approximation for cross-model token counting without requiring a specific tokenizer.
4. The `check-consistency.sh` script is the authoritative automated conformance gate; manual `/full-review` is the complementary human-readable audit.
5. The AI-legibility rewrite preserves behavioral rules. The pattern-matching rule counter (`verify|check|ensure|enforce|MUST|kural|doğrula|denetle`) is a reasonable proxy, not an exact rule inventory.
6. The Google/Apple ecosystem integration (A9) rules are conditional and produce zero noise when the integrations signal is absent — this is verified by the `--test-integrations` flag.
7. Size ceilings (orchestrator 350, multi-mode 350, single-mode 240, atomic 220 lines) are defined in SKILL-SPEC v2 and remain valid for v4.
8. The program is implemented across multiple sessions — `tasks.md` serves as the persistent ledger between sessions and is deleted upon completion.

---

## Dependencies

- **SKILL-SPEC.md** (v2, 1883 lines): The authoritative format spec — must be updated to v4 with the taxonomy appendix, standalone invariant, AI-legibility standard, and dimension ownership rule.
- **28 SKILL.md files** (8545 total lines): Primary transformation target — must receive scope expansions (Phase 4) and AI-legibility rewrites (Phase 5).
- **87 reference files**: Must be scanned for redundancy and updated where consuming skills changed.
- **`.claude/commands/full-review.md`**: Quality checklist — must be updated with v4 categories (standalone, ai-legibility, dimension-ownership).
- **`scripts/check-consistency.sh`**: Automated conformance script — must be extended with v4 dimension ownership and overlap checks.
- **`ds-research-agent`**: Shared agent — used in Phase 1 to validate taxonomy against industry frameworks.
- **Industry frameworks** (externally referenced): Google SRE PRR, Nielsen heuristics, Apple HIG + App Store Review Guidelines, Google Identity/OAuth, Material Design.

---

## Out of Scope

- Creating new skills (existing 28 are sufficient)
- Modifying `install.sh` or CI pipeline architecture
- Changing the `ds/audit/` state file schema
- Adding runtime dependencies (repo remains Markdown-only)
- Updating store listings or external documentation beyond the repo itself
- Implementing the actual scope expansions or rewrites — this spec covers only the design and plan, not execution
