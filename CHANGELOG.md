# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added — v2 invariants (2026-05-18)

- **W10 Findings-SSOT Drift gate** — downstream consumer skills MUST defer to fresh `ds/audit/findings.md` (`git_hash == HEAD`, age ≤ 7 days). Re-detection within a covered scope is a W10 violation. Stale/missing → consumer invokes blueprint refresh before continuing.
- **W11 Error Ownership Skip gate** — every detected real error (compile/lint/type/test/runtime/security) gets a concrete disposition. Reject list parses `skipped` / `needs-approval` reasons: `already existed`, `not my change`, `pre-existing`, `out of scope`, `too hard`, `will do later`, `unrelated` are not valid blockers.
- **Trigger Discipline (§2)** — every SKILL.md ships a `ÇAĞIRIR / ÇAĞIRMAZ` table (3-5 rows). Unscoped verbs (`improve`, `fix`, `clean up`, `audit`) alone are not valid triggers. Cross-skill disambiguation is bidirectional.
- **Interaction Discipline + All-Affordance Rule (§2)** — every user-facing menu offers an "all" / `tümü` / `apply-all` / `approve-all` affordance. CRITICAL findings + destructive actions still require per-item confirmation. Secret-risk files (`.env`, credentials) excluded from "all stage" flows.
- **`/ds-review --meta-quality` mode** — principle-based holistic audit covering SSOT / DRY / KISS / YAGNI / SoC (plus `overengineering`, `redundancy`, `obsolete`, `duplicate` aliases). Includes Phase 3a (Analyze-Principles), Phase 3b (Criteria-Fit), Phase 4a (Suggest-Paths). New references: `meta-quality-scopes.md`, `criteria-fit.md`, `path-proposals.md`.
- **Anti-overengineering 3-gate** — every finding (any mode) must pass: (1) breaks something currently working? (2) misleads a future reader? (3) is added complexity worth its keep? Failing any one → silent discard.
- **Cross-scope deduplication rules** — same `file:line` → merge; within 10 lines + same issue → merge; contradictory findings → keep higher confidence.
- **Needs-approval reason discipline** — `ds-review/references/principles.md §12` is the canonical reject-pattern list; `ds-fix` parses every needs-approval reason against it.
- **Parallel-track planning** — ds-blueprint Phase 2.5 and ds-review Phase 2 declare scopes as read-only / AST / cross-file batches so AI hosts can plan concurrency consciously.
- **CRITICAL escalation (second-pass verification)** in ds-fix, ds-solve, ds-review — every CRITICAL finding re-verified ±20 lines before being treated as confirmed.
- **Penalty-based scoring formula** (`ds-blueprint/references/weights.md`) — `score = max(0, 100 - 25C - 10H - 3M - 1L)` with a -50 per-dimension cap; explicit cross-dimension coherence check (related-pair gap > 40 → re-evaluate evidence).
- **`filters_applied` audit field** in `ds/audit/findings.md` meta header — surfaces `skipped_scope`, `downgraded`, `project_type` (with confidence), `overrides`.
- **`ds-fix` Educational output triple** — every applied fix emits `why:` / `avoid:` / `prefer:` next to "what changed".
- **`ds-fix --skip-if-clean` flag** — default `true` when invoked by another skill (ds-commit / ds-pr / ds-ship gates), `false` when user-invoked.
- **`ds-blueprint --memory-cleanup` flag** — optional Phase 8.5 scans AI host memory index (e.g. Claude Code `MEMORY.md`) for broken `[[link]]` references and surfaces consolidation.
- **`ds-pr` branch-protection-aware merge** — queries `gh api repos/.../branches/{base}/protection`; routes auto-merge / CI-check / hard-stop accordingly. Force-push to main is never proposed.
- **`ds-ship` milestone-gate triggers** — replaced generic "audit everything" with explicit release-candidate / pre-launch / post-incident gates. Cascade activation requires two-confirmation (intent + scope). Target-based routing table (App Store → ds-launch, server/container → ds-deploy, library → ds-repo --oss-ready).
- **ds-compliance mobile-overlap-skip runtime enforce** — mobile project signals auto-skip security/privacy/regulatory scopes (those are ds-mobile's domain). User can override with explicit `--scope=`.
- **`/full-review` self-audit slash command** — `.claude/commands/full-review.md` inspects the dev-skills repo against the v2 invariants across 8 categories × ~56 checks.
- **Overwrite-Only Persistence (SKILL-SPEC §10.1):** every state file, findings file, report, and profile section is rewritten on each run — never appended. Append-only artifacts (timestamped logs, run-N.json snapshots, session-{date} copies) are forbidden anywhere in the project. Run history lives in `git log`, period.
- **Context-Loaded File Budget — Dev-Value Gate (SKILL-SPEC §10.1):** the AI instruction file (CLAUDE.md / AGENTS.md / .cursorrules / .windsurfrules / .aider.conf.yml / Copilot instructions) is re-read on every AI turn, so every byte costs every future model read. Only Blueprint Profile section is writable by skills, hard ceiling 25 lines, every line must pass the Dev-Value Gate ("would an AI do meaningfully better engineering on every turn for 6 months because of this?"). Forbidden patterns: timestamps, score deltas, run history, owner info, descriptions, onboarding steps, philosophy, vendor changelog notes, file-by-file change notes. ds-blueprint Phase 7 enforces this with a context-budget guard that compresses or surfaces overshoot.

### Changed — v2

- **Skill count: 22 → 26** (added ds-benchmark, ds-deps, ds-simplify, ds-solve).
- **AI weakness mitigation: W1-W9 → W1-W11** (W9 State Hygiene preserved; W10 Findings-SSOT Drift and W11 Error Ownership Skip added).
- Every `ds-*/SKILL.md` Contract now contains: `Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.`
- Every `ds-*/SKILL.md` Quality Gates one-liner now lists W10 and W11 alongside W1-W9.
- `SKILL-SPEC.md §1` Section Order updated: Triggers MUST include `ÇAĞIRIR / ÇAĞIRMAZ` table; Quality Gates MUST be `W1-W11` one-liner.
- `SKILL-SPEC.md §9` Cross-Tool Verification Checklist adds 4 v2-specific checks (W1-W11 coverage, ÇAĞIRIR/ÇAĞIRMAZ presence, all-affordance presence, W11 Contract line).

### Added

- 26 production-grade, tool-agnostic AI coding skills:
  - **Discover:** ds-research (multi-source with CRAAP+), ds-benchmark (ideal-vs-current gap), ds-blueprint (project health scoring across 9 dimensions)
  - **Audit:** ds-compliance (regulatory), ds-mobile (mobile apps), ds-devops (CI/CD & deps), ds-repo (repo health)
  - **Development:** ds-fix (format/lint/typecheck), ds-test (test lifecycle), ds-review (tactical / strategic / perf / meta-quality), ds-simplify (dead-code / orphan / overengineering), ds-deps (dep upgrade loop), ds-docs (documentation)
  - **Design:** ds-backend (API + DB + auth), ds-deploy (infra + monitoring), ds-init (project scaffolding), ds-frontend (design system + a11y)
  - **Git workflow:** ds-commit (smart commits), ds-pr (pull requests)
  - **Ship:** ds-ship (orchestrator), ds-launch (store submission), ds-market (marketing strategy), ds-analytics (privacy-first analytics)
  - **Specialized:** ds-cv (ATS-proof CV generation), ds-tune (autonomous optimization loop), ds-solve (adaptive multi-plan backtracking with web research)
- SKILL-SPEC.md — universal specification for tool-agnostic AI coding skills
- Findings pipeline (`ds/audit/findings.md`) — single-file inter-skill communication standard
- Blueprint profile — project context shared across skills (type, stack, config, scores, run history)
- AI instruction patterns reference — research-backed best practices (2025-2026)
- GitHub issue and PR templates
- Contributing guidelines, security policy, and code of conduct
- Finding Resolution Completeness (FRC) — every finding gets a disposition, zero silent drops
- Deterministic Scope Checklist (DSC) — every scope check evaluated every run
- Inter-Skill Data Utilization (IDU) — skills read upstream artifacts with specific field→behavior mapping
- Mandatory phase enforcement — phases without `[CONDITION]` always execute, always produce output

### Architecture
- Tool-agnostic design — works with Claude Code, Cursor, Copilot, Windsurf, Aider, and any AI coding tool
- Findings pipeline — analyzers produce `ds/audit/findings.md`, fixers consume it, eliminating duplicate analysis
- Single findings file with append-and-dedup semantics — 4 producers, 11 consumers, scope-level dedup
- Blueprint profile — auto-detects AI instruction file, embeds project profile with markdown heading markers, legacy marker migration
- Blueprint produces 20 granular scopes mapped 1:1 to consumer scope names
- Tier-based stack detection — 12 primary + 4 supplementary stacks with false-positive prevention
- 3-step project type detection — manifest → framework deps → secondary signals
- Skill evaluation rubric — 8 criteria, 24-point scoring (FRC+DSC+IDU criteria included)
