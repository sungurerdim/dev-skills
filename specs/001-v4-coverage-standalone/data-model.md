# Data Model: Dimension Coverage Taxonomy Entities

**Phase**: Phase 1 — Design & Contracts
**Feature**: v4 Dimension Coverage Taxonomy + Standalone + AI-Legibility
**Date**: 2026-07-11

---

## Entity: Dimension

A named quality/coverage area that a project should be audited against. Dimensions are organized into layers by concern domain.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | string (2-3 chars) | Unique identifier: layer letter + sequence number (e.g., `A1`, `D9`) | Pattern: `[A-D]\d{1,2}`. Must be unique across the taxonomy. |
| `layer` | enum | Concern domain layer | One of: `A` (Product & Market), `B` (Engineering), `C` (Trust & Compliance), `D` (Operations). Layer `E` is not a dimension layer — it contains process carriers. |
| `name` | string (max 100 chars) | Human-readable dimension name | Should be unique; should not conflict with other dimension names |
| `owning_skills` | array of skill tokens | One or more skill tokens that own this dimension, with optional scope qualifier | At least one owner required. Two skills claiming the same dimension·scope pair is an overlap violation. Format: `ds-<name>` optionally followed by ` (scope)` |
| `status` | enum | Coverage status in a given audit | `audited` (skill ran and reported), `owner-skipped` (skill exists but didn't run), `unowned` (no skill claims this dimension) |
| `framework_references` | array of string | Industry frameworks that validate this dimension's existence | At least one per dimension recommended |

**State transitions (dimension status in a ship report):**

```
[initial] → unowned (no owner defined)
[initial] → owner-skipped (owner exists but skill not invoked)
[owner-skipped] → audited (invoked skill reported findings or clean pass)
```

---

## Entity: Taxonomy

The complete set of dimensions spanning all product/engineering/trust/operations concerns. Acts as the SSOT (Single Source of Truth) for dimension definitions and ownership.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `version` | string | Taxonomy version identifier | Semantic versioning (e.g., `1.0.0`). Incremented on dimension additions or ownership changes. |
| `layers` | map of layer → dimension list | Organization of dimensions by concern domain | Exactly 4 layers: A, B, C, D. Layer E carriers excluded from dimension count. |
| `dimensions` | array of Dimension | Complete list | Must cover every quality concern. No two dimensions should overlap in scope. |
| `carriers` | array of skill token | Process orchestrator skills (not dimensions) | ds-ship, ds-pipeline, ds-commit, ds-pr, ds-issue, ds-init, ds-solve, ds-tune, ds-research, ds-brief |

**Rules**:
- The taxonomy is stored as a normative appendix in SKILL-SPEC.md
- The taxonomy is frozen during Phase 1 and modified only through the amendment process (FR1.6)
- Layer E is documented alongside the taxonomy but state "these are carriers, not dimensions"

---

## Entity: Skill

A self-contained Markdown instruction file that performs a specific quality task. Skills are the atomic unit of work in the dev-skills system.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `token` | string | Unique skill identifier | Pattern: `ds-<name>` (e.g., `ds-review`, `ds-frontend`). Must match directory name. |
| `dimensions` | array of dimension ID | Which taxonomy dimensions this skill owns | Must exist in the taxonomy. Must not overlap with another skill's same-dimension·scope pair. |
| `type` | enum | Skill classification | `orchestrator` (ds-ship, ds-pipeline), `multi-mode` (ds-review, ds-mobile, ds-compliance), `single-mode`, `atomic` (ds-commit, ds-pr, ds-fix, ds-init) |
| `size_ceiling` | integer | Maximum SKILL.md line count | Depends on type: orchestrator ≤350, multi-mode auditor ≤350, single-mode ≤240, atomic ≤220 |
| `standalone_capable` | boolean | Whether the skill can run without sibling skills | True for all non-orchestrator skills. Orchestrators surface gaps. |
| `conditional_rules` | map of integration type → rule block | Rules that activate only when a specific integration signal is present | Optional. Currently only defined for A9 (Google/Apple). |
| `declaration_line` | string | The `Dimensions:` line in the SKILL.md | Required by FR4.1. Checked by `check-consistency.sh`. |

**Skill type determination:**
- **Orchestrator**: Delegates to other skills. Never does its own analysis. (ds-ship, ds-pipeline)
- **Multi-mode auditor**: Has 3+ modes/scopes and significant analysis logic. (ds-review, ds-mobile, ds-compliance, ds-frontend)
- **Single-mode**: One mode, focused task. (ds-blueprint, ds-test, ds-docs, ds-simplify, etc.)
- **Atomic**: Git-driven, seconds-long, no state persistence. (ds-commit, ds-pr, ds-fix, ds-init)

---

## Entity: Dimension Declaration

A machine-checkable statement in each SKILL.md declaring which taxonomy dimensions the skill owns.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `skill` | skill token | Owning skill | Must match the skill's directory name |
| `declared_dimensions` | array of `layer + id : scope` | Dimension-surface pairs this skill claims | Each pair must exist in the taxonomy. If two skills declare the same dimension·scope, it's an overlap violation. |
| `format` | string | The literal line format in SKILL.md | `**Dimensions:** A1, B3, C1 (regulatory), D5` | (comma-separated, optional scope in parentheses) |

**Example valid declarations:**
```
**Dimensions:** A6 (UI), A7 (implementation), A5 (new ux scope)
```
```
**Dimensions:** C1 (canonical), C2 (canonical), C3 (regulatory), C7, C8, A7 (regulatory), A8 (rules)
```

---

## Entity: Advisory Handoff

A cross-skill reference pattern that preserves standalone operation. Defined as a behavioral contract between skills.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `source_skill` | skill token | The skill making the handoff | Must exist in the skill inventory |
| `target_skill` | skill token (optional) | The skill that would normally handle this scope | May be absent (if no skill owns this scope in-depth) |
| `handoff_type` | enum | How the handoff is executed | `delegate` (target exists → invoke), `inline_check` (target absent → do basic check), `gap_note` (target absent → report gap) |
| `scope` | string | The scope surface being handed off | Should be mappable to a taxonomy dimension |

**Rules**:
- A skill MUST NOT hard-fail when a target skill is absent
- A skill MUST NOT silently skip a scope that has no target — either perform an inline check or emit a gap note
- The handoff type is determined at runtime based on skill availability

---

## Entity: Blueprint Profile

A metadata block in the AI instruction file that describes project characteristics. Used as a configuration input by all analyzing skills.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `type` | string | Project type | `library`, `cli`, `web`, `api`, `mobile`, `monorepo` |
| `stack` | string | Technology stack | Free text, used for detection |
| `target` | string | Deployment target | `production`, `prototype`, `enterprise` |
| `integrations` | enum | Ecosystem integration status | `google-workspace \| apple-ecosystem \| none` |
| `priorities` | array | Quality priorities | Used for scope ordering |
| `constraints` | array | Project-specific constraints | Used for severity calibration |
| `scores` | map of dimension → score | Current health scores (from blueprint scan) | Used for focus targeting |

**Location**: Between `## Blueprint Profile` and `## End Blueprint Profile` markers in the AI instruction file (CLAUDE.md). Read-only for all skills except ds-blueprint.

---

## Entity: Baseline

A pre-transformation snapshot of measurable project metrics. Used as the comparison reference for Phase 5 token reports.

| Field | Type | Description |
|-------|------|-------------|
| `per_skill_line_counts` | map of skill → integer | Line count per SKILL.md (total: 8,545) |
| `total_reference_file_lines` | integer | Sum of all reference file lines |
| `per_skill_token_estimates` | map of skill → integer | `wc -c / 4` (frontmatter excluded) per skill |
| `size_target_violations` | array of (skill, current, ceiling) | Skills exceeding their class size ceiling |
| `consistency_script_exit_code` | integer | `bash scripts/check-consistency.sh` exit code |
| `full_review_score` | string | `/full-review` result summary |
| `per_skill_rule_count` | map of skill → integer | Lines matching `verify|check|ensure|enforce|MUST|kural|doğrula|denetle` |

**Storage**: `ds/audit/v4-baseline.json`. Created during Phase 0.5, read during Phase 5 batch reports, retained through program completion.

---

## Entity: Integration Signal

A detected ecosystem presence indicator that triggers conditional rule blocks in A9-owning skills.

| Field | Type | Description | Detection Pattern |
|-------|------|-------------|-------------------|
| `type` | enum | Integration type | `google-workspace`, `apple-ecosystem` |
| `detection_signals` | array of string | Source patterns that indicate presence | Google: `google_sign_in`, `googleapis`, GIS/GSI script; Apple: `Sign in with Apple`, `StoreKit`, `CloudKit`, `AuthenticationServices` |
| `storage_location` | string | Where the signal is persisted | Blueprint profile `Integrations:` field |

**Usage**: ds-blueprint detects signals → writes `Integrations:` field → downstream skills read the field → activate conditional rule blocks only when matching. The `--test-integrations` flag allows simulation.

---

## Entity: Conditional Rule Block

A set of skill rules that activate only when a specific integration signal is detected. Produces zero noise when the signal is absent.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `skill` | skill token | The skill containing the conditional block | Must be one of the 5 A9-owning skills (ds-backend, ds-mobile, ds-compliance, ds-launch, ds-frontend) |
| `trigger_signal` | enum | Which integration activates this block | `google-workspace`, `apple-ecosystem`, or both |
| `rule_count` | integer | Number of conditional rules in the block | Should be minimal — rules that always apply should not be conditional |
| `scope` | string | Which dimension scope these rules serve | Always A9 for this feature |

---

## Relationships

```
Taxonomy (1) ──has many──▶ Dimension (28)
     │                          │
     │                          │ owned by
     │                          ▼
     │                   Skill (28) ──declares──▶ Dimension Declaration (1 per skill)
     │                          │
     │                          │ references
     │                          ▼
     │                   Advisory Handoff (cross-skill edges)
     │
     └──stores in──▶ SKILL-SPEC appendix

Blueprint Profile (1 per project) ──contains──▶ Integration Signal (0-2)
     │                                                   │
     ▼                                                   ▼
Skill ──reads──▶ Blueprint Profile ──triggers──▶ Conditional Rule Block (per skill)
                                                     │
                                                     ▼
                                             Skill execution path
```
