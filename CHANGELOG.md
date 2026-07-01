# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added — ds-pipeline: spec pipeline conductor (2026-07)

- **ds-pipeline** (new skill, prefix `PIPE`) — conducts the external [Spec Kit](https://github.com/github/spec-kit) chain (`specify → clarify → plan → tasks → analyze`) with blocking gates: zero open clarifications; deterministic tasks-contract (`- [ ] T{n}: … — verify: \`{command}\` → {expected}` on every task, `Gate:` per phase, EARS sentences on behavioral tasks); zero CRITICAL cross-artifact findings — then a scoped `spec({feature})` commit plus a one-line executor handoff. Planning-only (writes exclusively under `specs/` + `.specify/`), state-exempt (artifacts + git are the durable record), artifact-driven resume, `--fresh` regeneration with confirmation. Catalog 26 → 27.

### Added — ds-issue `--do --all`: batch execution over the open backlog (2026-06)

- **`ds-issue --do --all`** — runs the existing per-issue `--do` flow (re-verify → impact-surface map → bounded plan → implement+verify → code-proven close) over **every open issue in priority order** (CRITICAL→LOW, then ascending number). Surfaces the queue transparently (`#N · priority · title`) and confirms it once; each issue's changes are still confirmed **per item** (destructive — All-Affordance rule 2). A stale / blocked / aggregate-red issue is recorded and skipped, the queue continues (never aborts on one issue), and the run ends with a per-issue outcome table (`closed · skipped-stale · skipped-blocked · red`). After 3 consecutive same-cause failures the queue stops with the systemic blocker. `--do --all --dry-run` plans every issue without changing files. The up-front mode menu stays 4 rows: `--do #N` and `--do --all` collapse into one `Do issue(s) end-to-end` row, with the one/all scope picked in a target sub-selection (where the "all" affordance lives). Triggers/Arguments/Phase 6/Report/Edge-Cases coverage; README + CLAUDE updated.

### Added — ds-quality: deterministic local quality gate (2026-06)

- **ds-quality** (prefix `QAL`) — adopted into the core suite (was a standalone skill): installs a local, no-CI Stop-hook verify-loop that BLOCKS "done" until one quality entry point (format → lint → type → test) passes green; bootstraps missing tooling, idempotent, non-destructive. Distinct from ds-fix (which *runs* the passes once) — ds-quality owns the always-on *enforcement mechanism* and delegates one-shot fixing to ds-fix. Brought to current SKILL-SPEC conformance (Contract, FRC+DSC, Quality-Gates W1–W11, Report Format, Edge Cases, state-exempt). Catalog 25 → 26.

### Changed — catalog focus: extract off-domain skills (2026-06)

- **ds-cv, ds-market, ds-analytics moved out** to a separate companion repo (`dev-skills-extra`, private) — these career/marketing/product-analytics workflows diluted the core coding-toolkit identity. dev-skills is now 25 coding-lifecycle skills, each with a distinct concrete benefit. All cross-references (README, CLAUDE, SKILL-SPEC ownership/boundary/prefix tables, ds-ship sequences, sibling DON'T-INVOKE pointers, `docs/guide.html` plan map) updated so nothing dangles; DON'T-INVOKE pointers to the moved skills now read `→ external / manual`.

### Added — ds-issue: GitHub-Issues lifecycle in one skill (2026-06)

- **ds-issue** (new skill, prefix `ISS`) — the full GitHub-Issues loop, record side and work side, in four modes:
  - `(default)` **intake** — a raw note becomes one well-formed issue only after a dedup sweep (open + closed + history docs) and a false-positive gate (symptom reproduced against code read this run) both pass. Conditional-block body (no dead content), machine-checkable Done, exactly 1 type + 1 priority from the live label set, sub-issue split over the bounded threshold.
  - `--sweep` — duplicate/overlap/redundant/obsolete clusters across the whole set, with recommended merges/closures.
  - `--status` — done-ness audited **from code** (buckets: done & code-verified · claimed-done-but-unproven · in-progress · not-started · blocked), read-only.
  - `--do #N` — execute one issue end-to-end: re-verify root cause (stale → stop, never "fix" a non-problem) → impact-surface map (callers · consumers · serialization · schema · i18n/a11y/compliance · project hazard checklist) → internal bounded plan → implement + verify each unit → aggregate done-signal green + regression test for fixes → close with code-proven evidence + doctrine-lockstep note. `--dry-run` posts the plan as a comment, changes no files.
- **Zero local footprint** — state-exempt: writes no `ds/audit/` state and no temp files; the GitHub issue + its comments + git are the durable record (`gh` bodies pass via heredoc). The audit trail is the issue's comments, not a local log.
- **Project adapter** — optional committed `.dev-skills/issue-ops.json` (repo slug, doctrine doc paths, label taxonomy, audit→issue-type map, done-signal, hazard checklist, history docs); absent → auto-detect repo/done-signal/criteria. Self-contained `references/` (github-features, verification, issue-template, impact-surface, adapter).
- **SKILL-SPEC** — registered prefix `ISS`; ds-issue carries W13 + W14/W15/W17 *Applies to*.

### Added — model-uplift workflow + coverage-gap closure (2026-06)

- **ds-ship `--uplift`** — model-uplift gate: new trigger + flag; forces `/ds-blueprint --refresh` as the first delegation; Phase 6 report gains a model-attributed Score Delta line; "next frontier-model upgrade" added to Next Trigger examples.
- **ds-blueprint `model=` key** — `Scores:` line now records the assessing model (`model={model-id}`, fallback `unknown`); dashboard labels deltas as model-attributed when the model changed; score history stays attributable via `git log` of the line.
- **ds-review Cost scope** — `--perf` gains a Cost category; `references/rules-performance.md` gains COST-01–06 (paid-API caching/batching/model right-sizing, cloud egress, oversized infra defaults, missing lifecycle policies, polling-vs-push, pay-per-use amplification).
- **ds-launch active store checks** — 6 new active detections: IAP external-payment (Guideline 3.1.1, CRITICAL), restore purchases (3.1.2), Sign in with Apple (4.8), reviewer-access gap, app completeness / remote gating (2.1), content-vs-rating consistency.
- **ds-test `--baseline`** — characterization-baseline mode (Phase 2e): capture current actual behavior of a legacy module before refactoring; apparent bugs asserted as-is with `// characterization:` tag + Category B finding; nondeterminism and no-public-surface edge cases covered.
- **ds-tune cost metrics** — `{cost_per_run}`, `{tokens_per_request}` added to the example metric list.

### Added — domain-specific weaknesses W12–W17 (2026-06)

- **SKILL-SPEC §3 W12–W17** — six domain-specific AI weaknesses added alongside the universal W1–W11, each carried only by the skills named in its *Applies to* list:
  - **W12 Specification Gaming / Reward Hacking** (ds-test, ds-tune, ds-benchmark) — never special-case known test inputs or hard-code expected outputs; a metric is a proxy.
  - **W13 Sycophancy / Authority Deference** (ds-review, ds-research, ds-pr) — re-verify from source on pushback; judge code by behavior, not PR/comment/authority claims.
  - **W14 Context Rot** (ds-ship, ds-solve) — re-ground every ~20 tool calls from files, not conversation memory; front-load constraints.
  - **W15 Subagent / Handoff Failure** (ds-ship, ds-solve) — subagent returns are untrusted until `file:line`-verified; explicit handoff contracts; least scope on delegation.
  - **W16 Dependency Hallucination / Slopsquatting** (ds-deps, ds-init) — registry existence + registration age + download history + lockfile pin before any dependency is added.
  - **W17 Slop / Duplication Drift** (ds-review, ds-simplify) — grep for an existing implementation before generating; consolidate clones to a single source of truth.
- **ds-backend API security rules** — SSRF prevention, server-side validation enforcement, and a BOLA cross-user access test.
- **ds-devops MCP/agent-era rules** — MCP server & agent supply-chain checks, agent-authored-PR review discipline, and SCA (software composition analysis) coverage.
- **ds-deploy / ds-compliance** — insecure-defaults audit rules and license/IP compliance rules.
- **2026 research refresh** — updated stats and AI-failure-mode sections across skill references (SWE-ABS, SpecBench, GitClear 2025, USENIX '25 slopsquatting, Chroma context-rot, MASFT).
- **W12/W13 Quality-Gate one-liners + OPT-07** wired into the remaining skills' gates.

### Changed — 2026-06-10 quality pass

- **Triggers table renamed to English** — `ÇAĞIRIR / ÇAĞIRMAZ` → `INVOKE / DON'T INVOKE` across all 26 SKILL.md files, SKILL-SPEC.md, README.md, and CLAUDE.md. The `tümü` alias was dropped from the All-Affordance Rule (`all` / `apply-all` / `approve-all` remain). Historical changelog entries below keep the original names.
- `ds-launch/references/app-store-submission-template.md` — Turkish body sections translated to English.
- `docs/devops/cicd-setup-guide.md` — workflow examples now follow the guide's own rule: actions pinned to full commit SHAs (`uses: owner/action@<sha> # vX`), Node version bumped to the current LTS.
- `ds-fix/references/toolchains.md` — `curl | bash` install instruction for tflint replaced with package-manager / official-release-binary instructions.
- `ds-compliance/references/rules-web.md` — `csurf` recommendation now carries its deprecation notice and the same maintained alternatives as `ds-backend/references/rules-auth.md`.
- `ds-fix/references/principles.md` — gained §12 (Needs-Approval Reason Discipline) so `ds-fix/SKILL.md` no longer live-links into `ds-review/` (SKILL-SPEC §6 self-containment).
- `SKILL-SPEC.md` — findings-poisoning note strengthened: `ds/audit/findings.md` content is classified as untrusted data under W14/W15 re-verification rules; layout diagram comment corrected from `append-merge-dedup` to overwrite-only (§10.1 consistency).
- `ds-deps` — `--force-approve` documentation now states the breaking-change risk of auto-approved major upgrades explicitly.

### Removed — 2026-06-10 quality pass

- `.github/` — issue/PR templates and CI dropped (solo, direct-push-to-main workflow); CONTRIBUTING.md now asks for plain issues/PRs.
- `docs/archive/` — two obsolete draft/analysis documents (672 lines) not linked from anywhere.

### Fixed — 2026-06-10 quality pass

- `ds-backend/references/rules-auth.md` — hallucinated npm package name in the CSRF guidance replaced with registry-verified packages.
- `ds-frontend/references/aesthetics-presets.md` — removed a stray private-project reference from a preset description.
- `ds-docs/references/rules-writing.md` — broken `.launch-research.md` source citations now point to the repo's `references/launch-research.md`.
- `ds-solve/references/backtrack-logic.md` — hardcoded example timestamp replaced with a `{timestamp}` placeholder (SKILL-SPEC placeholder rule).
- `ds-review/references/criteria-fit.md` — live relative link into `ds-blueprint/` converted to a prose/GitHub-URL attribution (no runtime cross-skill dependency).
- CONTRIBUTING.md / CLAUDE.md / SECURITY.md — dead `.github/` template links, stale `Bash (install)` stack claim, nonexistent `Announce.md`/`Video.md` structure entries, and "installation scripts" wording removed.

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
- Single findings file, overwrite-only with scope-level dedup — producers rewrite their scope sections on each run (run history lives in `git log`)
- Blueprint profile — auto-detects AI instruction file, embeds project profile with markdown heading markers, legacy marker migration
- Blueprint produces 20 granular scopes mapped 1:1 to consumer scope names
- Tier-based stack detection — 12 primary + 4 supplementary stacks with false-positive prevention
- 3-step project type detection — manifest → framework deps → secondary signals
- Skill evaluation rubric — 8 criteria, 24-point scoring (FRC+DSC+IDU criteria included)
