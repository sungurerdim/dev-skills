# Implementation Plan: v4 — Dimension Coverage Taxonomy + Standalone + AI-Legibility

**Branch**: `001-v4-coverage-standalone` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-v4-coverage-standalone/spec.md`

---

## Summary

Transform the 28-skill dev-skills suite from an implicit collection with partial dimension coverage into an explicit, automated, production-grade dimension taxonomy. The program has 6 phases plus a baseline phase: (0.5) measure current state → (1) validate taxonomy against industry frameworks → (2) codify dimension ownership, standalone invariant, AI-legibility standard in SKILL-SPEC → (3) add blueprint integrations signal + ds-ship dimension coverage report → (4) close 7 scope gaps across 9 skills with pre-expansion size audit → (5) rewrite all 28 SKILL.md files for AI-legibility using a uniform 10-step checklist → (6) reconcile CLAUDE.md, README.md, run final verification gates.

---

## Technical Context

**Format/Version**: Markdown (GFM) — plain text, zero runtime. All 28 SKILL.md files follow the SKILL-SPEC v2 format standard.

**Primary Dependencies**: None — the repo is pure Markdown with zero runtime dependencies. The only tooling dependency is:
- `bash scripts/check-consistency.sh` — automated conformance checking (shell script)
- `.claude/commands/full-review.md` — local Claude Code command for human-readable quality audit

**Storage**: Files on disk under git. No database, no cache, no state (except `ds/audit/` for transient run artifacts, already gitignored).

**Testing/Verification**: Two automated gates:
- `bash scripts/check-consistency.sh` — format conformance + dimension ownership + overlap detection
- `/full-review` — Claude Code command checking 8+ quality categories

**Target Platform**: AI instruction host platforms — Claude Code, Cursor, Copilot, Windsurf, Aider. Skills are consumed by AI models (Claude 4.x, GPT-5.x, Gemini 3, Llama 4, Mistral).

**Project Type**: Documentation/library — skill definitions are Markdown instruction files consumed at runtime by AI agents.

**Performance Goals**:
- Each SKILL.md: as specified by class ceiling (orchestrator ≤350, multi-mode ≤350, single-mode ≤240, atomic ≤220 lines)
- Consistency script runtime: <30s on the full repo
- Token budget per skill: ≤10K tokens including loaded references (existing SKILL-SPEC invariant)

**Constraints**:
- Zero new runtime dependencies — repo remains Markdown-only
- No new skills can be created (decision: existing 28 are sufficient)
- Every cross-skill reference uses advisory-handoff pattern (no hard dependencies)
- AI-legibility rewrite must preserve all behavioral rules (verified by rule-line counting)
- Taxonomy must be verified against ≥1 external industry framework per dimension

**Scale/Scope**:
- 28 SKILL.md files (8,545 lines total baseline)
- 87 reference files
- SKILL-SPEC.md (1,883 lines)
- CLAUDE.md, README.md, `.claude/commands/full-review.md`, `scripts/check-consistency.sh`

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The `.specify/memory/constitution.md` file is a template with placeholder values (e.g., `[PRINCIPLE_1_NAME]`, `[PRINCIPLE_1_DESCRIPTION]`) and contains no project-specific governance constraints, technology stack requirements, or review process rules. No constitution-based gates apply.

**Status: PASS** — no violations to evaluate.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-v4-coverage-standalone/
├── spec.md              # Feature specification (/speckit.specify output)
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output — industry framework validation
├── data-model.md        # Phase 1 output — entity definitions and relationships
├── quickstart.md        # Phase 1 output — validation scenarios
├── contracts/           # Phase 1 output — interface contracts
│   ├── dimension-declaration.md
│   ├── advisory-handoff.md
│   ├── findings-file.md
│   └── blueprint-profile.md
├── checklists/          # Quality checklists
│   └── requirements.md
└── tasks.md             # Phase 2 output (/speckit.tasks command — NOT created by /speckit.plan)
```

### Source Code (repository root)

This is a Markdown-only meta-project. The "source code" is the skill definitions and specifications that AI agents consume. The existing structure is preserved and enhanced:

```text
ds-<name>/                # 28 skill directories (one per skill)
├── SKILL.md              # Skill instruction file (transformation target)
├── README.md             # Skill usage documentation
└── references/           # Reference rule files (loaded on demand)

.claude/
├── commands/
│   └── full-review.md    # Quality audit command (update target)

scripts/
└── check-consistency.sh  # Automated conformance (update target)

SKILL-SPEC.md             # Authoritative format spec (major update target)
CLAUDE.md                 # Project instruction file (update target)
README.md                 # Project overview (update target)
tasks.md                  # Transformation ledger (delete at completion)

references/               # 87 shared reference files
docs/                     # Topic-organized documentation
agents/                   # Shared agent definitions
```

**Structure Decision**: The existing project structure is preserved. No new directories are created at the repo root. New content goes into existing files (scope expansions, AI-legibility rewrites) and into `ds/audit/` for transient baseline artifacts. The `specs/` directory is the only addition for this planning session.

---

## Complexity Tracking

Not needed. Constitution Check has no violations. The transformation is well-scoped with clear phase boundaries, gates, and verification criteria.
