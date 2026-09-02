# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [2.0.0] - 2026-09-02

Program: issue #38 (v7 — one-key autonomy, tailored scope, shared core, measured on two Claude tiers). Baseline commit `69e7bd4`.

### Breaking

- **Autonomous default.** No flag = every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list (`core/ask-exception-list.md`) is skipped and recorded `only you can do`. `--ask` restores menus, approval batches and confirmations at every decision point and propagates from ds-ship to its delegates. **`--auto` is removed without an alias**; the Up-Front Mode Menu, All-Affordance and Selection Transparency rules apply only under `--ask`.
- **`core/` is the single home for shared references** (principles, severity/score categories, findings + profile format, signal inventory, ask-exception list, checkpoint protocol, execution loop, report + outcome templates, secret patterns, toolchains, CRAAP, best practices, experience rules). The 22 per-skill `references/principles.md` copies and the toolchain / CRAAP / secret-pattern duplicates are gone; skills link `../core/<file>.md`. A manual copy of one skill directory must now copy `core/` beside it — `install.sh` (including `--skills` subsets and `--target`) always does.
- **ds-solve removed.** Its budgeted backtracking lives in ds-build, its hypothesis loop in ds-debug.
- **ds-ship gains `--mode=harden|release|launch|maintain`.** Benchmark, launch, productize and Ship-ready legs run only in `release`/`launch`; every delegate is justified by a project signal (`signal-absent — key=value`, `skipped — not part of this mode`, `skipped — another skill owns it for this project type`, `skipped — removed by you`, `failed`, `skipped — not installed`).
- **Closing block shares dev-rules' labels:** `Asked` / `Done` / `Effect` / `Decided without asking — say if wrong` / `Only you can do` (empty lines omitted); every choice put to the user is recommendation-first with options in one shape. `core/report-and-outcome-templates.md` § 5 is the portable copy; the `lean` and `claude` install profiles strip it because the always-on layer owns it.
- **Installer rewritten without rsync** (bash + coreutils + git); `install.cmd` launches it from cmd.exe/PowerShell; profiles `portable` · `lean` · `claude` (lean + ds-ship delegates run as forked subagents on Claude Code); `--status`; profile-aware `--check`.
- **Spec Kit artifacts removed** (`specs/`, `.specify/`, `.opencode/`); ds-pipeline runs `specify → clarify → plan → tasks → analyze` natively, Spec Kit optional when installed, and hands `tasks.md` to ds-build.
- **`docs/` lifecycle guides removed** after a delta migration into the owning skills' rules files (every actionable item became a rule with Detect/Fix/Impact/Source, templates moved into ds-docs references); `docs/methodology/` and `docs/guide.html` remain.
- **Spec citations banned inside skills** (`SKILL-SPEC`, `Unattended Mode rule`, `rule-4 exception`, `IDU`, `DSC`, `OVERLAP-n`, `VAR`) — 143 citations replaced by the canonical inline equivalents; a lone install has nowhere to resolve them.
- Contributor-facing: `check-consistency.sh` checks 21/22/23 folded into `check_core_links`, check 28 removed; new checks `check_spec_citations`, `check_dead_sources`, `check_undefined_flags` (+ retired-flag list), `check_readme_counts`, `check_ask_row_canonical`, `check_scope_resolution_table`, `check_rule_impact`, `check_duplicate_rule_titles`, each with a self-test fixture and a mutation case.

### Added

- **ds-build** (prefix `BLD`) — plan executor: issue / `specs/{feature}/tasks.md` / plain request → bounded units, a verify signal per unit, regression tests seen red first, ≤ 3 attempts × ≤ 3 approaches with recorded causes, per-unit commits, code-proven close; `ds-issue --do`, ds-pipeline and ds-freeze hand off to it.
- **ds-debug** (`DBG`) — reproduce the red → localize (`git bisect run`, trace, temporary logging, flaky split 3× isolated + 1× shuffled) → ≤ 3 falsifiable hypotheses → minimal fix behind a red-proven regression test; `not reproduced` is an honest outcome; tests are never weakened.
- **ds-release** (`REL`) — version from Conventional Commits, dated CHANGELOG section with Unreleased kept, every version surface found by search and bumped together, check green before the tag, local release commit + annotated tag; push / GitHub release / registry / store handed back with the exact commands; `--verify` post-release (remote tag, CI run, attestation, registry, smoke, rollback path).
- **Relevance First:** ds-blueprint produces a `Signals:` line (`has_ui`, `has_api`, `has_db`, `has_auth`, `has_billing`, `has_pii`, `platforms`, `audience`, `jurisdiction`, `integrations`, …; `core/signal-inventory.md`); every multi-scope skill carries a `| Scope | Runs when (signal) | Otherwise |` table; the three largest rules files tag every rule `applies_when:`.
- **Mechanical Done Gate + Checkpoint** in ds-pr (closes the `reset --hard`-over-uncommitted-work path with an explicit Push phase), ds-repo, ds-devops, ds-docs; 21 code-modifying skills gated.
- **Rules:** Impact line on every rule (≈ 400 added); ds-mobile Expo + Kotlin Multiplatform detection, per-platform release rules, staged rollout; ds-deps JVM/.NET/Swift rows, lockfile-integrity table, SBOM (`syft`); ds-init Bun/Hono/Astro/Expo; ds-frontend Svelte 5/Astro/Solid/htmx; ds-compliance EAA, DSA, age verification, Quebec Loi 25 (+ analytics-privacy and legal-checklist deltas); ds-productize chargeback and external-purchase-link rules; ds-deploy DNS/TLS/HSTS rules; ds-repo GitHub security toggles (secret scanning + push protection, Dependabot, private vulnerability reporting, code scanning) via `gh api`; ds-review gitleaks/semgrep as optional detectors with enumerated per-scope checklists; ds-test contract tests on API boundary artifacts.
- **Evals:** 13 tasks (5 new: fix-autonomy-no-prompt, ship-harden-no-launch, build-tasks-md, debug-reproduce-fix, release-tag-changelog); `evals/validate-scorers.sh` proves every scorer red-before / green-after; results on #38.
- **Gate:** `scripts/quality.sh` adds `typos`, the installer round-trip (32 assertions) and dev-rules' `check-cross-repo.sh` when a sibling `../dev-rules` checkout exists (visibly SKIPPED otherwise); `.gitattributes` pins LF; `_typos.toml` domain vocabulary.

### Changed

- ds-review: `--diff` is the default scope, bootstrap is an if/then table, simplify/yagni/duplicate detection handed to ds-simplify, `discarded (no harm signal): n` in the summary. ds-fix: `--diff` default, tracked secret = CRITICAL / untracked = HIGH via `git ls-files`. ds-test: input-state decision table, findings.md write scope, red-proof + flaky gate. ds-commit: secret/size commands stated, no fetch/pull, `Co-Authored-By` only when the repo already uses it. ds-devops: rules split into ci / signing / deps / release-pipeline, `actionlint` + `zizmor` in the done gate, monitoring owned by ds-deploy. ds-launch: SEO/email handed to ds-compliance, integrations audit keyed on the `integrations` signal, `ds/launch/` metadata directory. ds-compliance: ds-mobile and ds-frontend absence branches (no silently dropped scopes). ds-frontend: three fully defined presets. ds-blueprint: `--preview` writes nothing, Foundation questions only under `--init`/`--ask`, privacy single-owned. ds-brief: slot manifest, verifier path from the dispatcher. ds-research-agent: normative Contract split from the operating procedure. Frontmatter descriptions ≤ 300 chars; SKILL.md byte ceilings per skill with per-scope reference loading.

### Measurements

{{MEASURE}}


## [1.2.0] - 2026-07-28

### Added — release-cycle hardening: installer test, shell lint, path-citation check (2026-07-28)

- **`scripts/test-install.sh`** — 12-assertion round-trip test for `install.sh`, the only code here that writes into and deletes from a user's home directory. Runs entirely in a temp dir via `--target`: install → version stamp → `--check` clean → drift detection on a mutated file → drift detection on a deleted file → re-install repair → scoped `--uninstall` that leaves non-dev-skills content untouched. Proven by defect injection, not by passing on the first run.
- **`scripts/quality.sh`** — two new gate arms on the same fail-loud pattern as the python3 arm: `shellcheck -S warning` over `install.sh` + `scripts/*.sh`, and the installer round-trip test. A missing tool now names what went unverified instead of passing quietly.
- **`check-consistency.sh` check 23 (`check_bare_repo_paths`)** — closes a hole in the Standalone Invariant's mechanical enforcement: checks 21/22 catch cross-skill and link-shaped path references, but a skill could still cite an in-repo file in plain prose, which a lone install cannot follow either. Scoped to `docs/`/`specs/` files that exist in this repo, exempting URL-carrying lines and user-project directory layouts. Ships with its own fixture; the self-test now covers 7 checks.
- **Byte ceiling on `SKILL.md`** — check 2 gained a 48000-byte ceiling beside the 500-line one. A 45KB file sitting on 285 long lines previously passed a line-only check.
- **`AGENTS.md`** — root cross-host contributor instructions (commands, non-guessable conventions, gotchas) for the ~45 Agent-Skills-reading tools whose contributors never see `CLAUDE.md`.
- **`.claude-plugin/marketplace.json`** — installable via `/plugin marketplace add sungurerdim/dev-skills`, written against the schema in the official Claude Code plugin-marketplace docs.
- **`_typos.toml`** — allowlist for the repo's domain vocabulary (ASO, BRIN, Hashi, Wonderous, …); `typos` went from ~90 false hits to 0, making spell-check a usable signal for the first time.
- **SPDX headers** — `SPDX-License-Identifier: MIT` added to all five executable files.

### Fixed — documentation claims that did not match the repo (2026-07-28)

- **`README.md`** — the token budget was restated from measurement (median SKILL.md ≈ 5K tokens, largest ≈ 11K, gate ceiling ≈ 12K); the previous "~4–9K, total within 10K" was exceeded by `ds-brief`. The host-support section was rewritten into two verified tiers — tools that load skills natively (checked 2026-07-28 against the Agent Skills client showcase: Claude Code, OpenCode, Cursor, GitHub Copilot, VS Code, OpenAI Codex, Gemini CLI, Amp, Goose, Roo Code, Kiro, Factory, Junie, ~45 in total) versus Aider and Windsurf/Devin, which have no skills loader and reference `SKILL.md` on demand. The differentiator is now stated as depth per skill rather than host count.
- **`docs/methodology/cross-host-program.md`** — P0.2 claimed a README `AGENTS.md` pointer had shipped on 2026-07-15; it never did. Stale present-tense counts re-measured: 28 → 30 skills, SKILL.md bodies ~129K → ~180K tokens (the ~2K frontmatter figure verified as still accurate).
- **`CLAUDE.md`** — Project Structure table gained the five tracked path groups it omitted (`scripts/`, `AGENTS.md`, `.github/`, `specs/`, `.specify`+`.opencode`); the tool-support line now carries the Windsurf → Devin Desktop rebrand that README already documented.
- **Five unresolvable in-repo citations repointed to GitHub URLs** — `ds-frontend/references/rules-ux.md` (×3) and `ds-rig/references/{permissions,privacy}.md` cited repo paths absent from a lone install.
- **`specs/001-v4-coverage-standalone/`** — Phase 6 marked superseded with verified evidence. Its 18 open tasks target a six-batch rewrite of "all 28 SKILL.md"; the repo has 30, and `git show --stat ced87a7` shows #29 touched 5 skills, not 30. Checkboxes left unchecked rather than falsely flipped.
- **`scripts/*.sh`** — `cd` guards added (shellcheck SC2164) and an unquoted expansion fixed (SC2086); `shellcheck -S warning` is now clean.


### Changed — SKILL-SPEC: plain-language Value Delivered mandate (2026-07)

- **SKILL-SPEC.md §5** — new rule 8: every Value Delivered bullet's benefit clause must be plain, everyday language a non-technical reader understands — the concrete effect, quantified when measurable, never the mechanical activity performed. Applied to all 30 skills' Value Delivered sections.

### Added — Experience Rules (XR) registry rollout: 198 rules across all 30 skills (2026-07)

- **XR registry integration** — 198 XR-numbered rules (140 integrated + 6 merged + 45 pre-existing + 7 skipped with recorded reasons) rolled out across every skill's rule files: `ds-backend` (AUTH/DB/API/DP, 30 rules + 13 generalized architecture-ADR rules + DB-11 duplicate-prevention registry), `ds-compliance` (PRV/NET/I18N/CSEC, 26 rules + CSP allowlist-completeness + PRV-30 data-residency export-path extend, 109→138 rules), `ds-frontend` (UX/CMP/TOK/THM/RSP, 14 rules + new `references/rules-scheduling.md` + 13 generalized UI/UX rules + UX-ON-04 deep-link/auto-resume, 111→149 across 6 files), `ds-mobile`/`ds-launch`/`ds-productize` (REL/DEV/PRF/MON/PRC release-and-billing rules including crypto-bound high-value paid data, mobile 174→179), `ds-devops`/`ds-deploy`/`ds-quality`/`ds-deps` (DOP/DEP/MON release-deploy-config rules + ds-quality two-tier hooks/denylist arm + ds-deps pin-rationale and formal dependency-adoption eligibility gate), `ds-docs`/`ds-review`/`ds-simplify`/`ds-repo`/`ds-pipeline` (DOC-18..24, ARC-12..15 including god-module strangler-fig decomposition, TST-07..10, ds-simplify pre-release residue discipline, ds-repo private-sibling backlog, ds-pipeline canonicalize-before-implement gate), and XR-199 breaking-first principle folded into all 22 shared `principles.md` copies.
- `references/experience-rules.md` — new pointer-style registry mapping all 198 XR rules to their dev-skills home (no content duplication; source of truth stays in each skill's own rule files).
- Root README mobile rule count corrected 174→179 to match `ds-mobile`.

### Added — targeted rule and gate additions (2026-07)

- **Mechanical Done Gate rollout** — SKILL-SPEC §4 gained a normative Mechanical Done Gate for code-modifying skills ({check-cmd} resolution, red-at-baseline handling, ≤3 fix attempts then revert); enforced in all 15 code-modifying skills and mechanically checked by `check-consistency.sh` #18.
- **`ds-ship`** — sequence-completeness gate (every excluded skill needs a recorded, evidence-based reason) + durable tracking handoff of unresolved findings to `/ds-issue`.
- **`ds-test`** — critical-flow wiring check for mock-hides-integration bugs (money/auth/data-deleting flows need one test against the real dispatch path) and unreproduced-bug triage guidance (W12 extension).
- **`ds-issue`** — last-resort local `tasks.md` fallback for repos with no GitHub remote at all.
- **`ds-deps`** — formal 5-criteria dependency-adoption eligibility gate plus license allowlist and provenance record.
- **`ds-brief`** — competitive-analysis upgrade (claim-to-quote popovers, cross-reference links, comparison matrix, disputed-claim badges, validated dark theme) and a scenario-branching/obligation-badge visual polish layer.

### Changed — unified unattended mode (`--auto`) + flag vocabulary simplification (2026-07)

- **SKILL-SPEC.md** — new canonical **Unattended Mode (`--auto`)** section (§2): a single universal flag for zero-interaction runs across all 30 skills and both orchestrators. Every decision (mode, scope, approval, Category A/B findings, CRITICAL findings) resolves via the skill's own best judgment; only a small fixed **irreversible-exception list** (force-push/history-rewrite on shared branches, permanent branch/tag/resource deletion with no backup, secret rotation/deletion/transmission, values only a human can supply) auto-skips and is recorded `needs-human` — never executed blind, never silently dropped. New **Flag Vocabulary** section fixes one small, consistent flag language (`--auto`, `--preview`, `--scope=`, `--mode=`, `--resume`, `--clean`, `--status`) and bans bare positional subcommands.
- **`--force-approve` removed everywhere** (~26 skills) — fully subsumed by `--auto`, which now resolves Category B (and CRITICAL) findings automatically instead of merely listing and skipping them.
- **`ds-solve`** — inverted its default/`--confirm` polarity to match every other skill: the no-flag default now pauses for confirmation after Setup and after Plan (where `--confirm` used to add that pause); `--confirm` is removed; `--auto` skips both checkpoints.
- **`ds-ship` / `ds-pipeline`** — `--auto` now explicitly propagates to every delegated skill invocation (new Orchestration Contract §10.3 rule 4), so `/ds-ship --auto` runs the entire cascade — including PR opening — with zero prompts, suited to a remote/unattended caller. `ds-ship`'s `--no-pr-suggest` removed (subsumed by `--auto`); `ds-pipeline` gained `--auto` (previously had none).
- **`ds-brief`** — `--no-interactive` renamed to `--static` (its function — static/print-pure HTML output — was unrelated to interaction suppression; the old name collided with the `--auto` concept).
- **`ds-tune`** — bare `run`/`status` subcommands converted to `--run`/`--status` to match the suite-wide flag convention.
- **`--dry-run` retired** — merged into `--preview` (the sole canonical no-mutation-preview flag) across every skill that had it (`ds-deps`, `ds-init`, `ds-issue`, `ds-solve`).
- **`ds-rig` / `ds-repo`** — each documents an explicit, spec-cited extension to the irreversible-exception list (unpinned installs, credential-passthrough servers, unmerged-branch deletion, visibility/permission changes) so their existing "never silent" floors compose correctly with `--auto` instead of contradicting it.
- `scripts/check-consistency.sh` — flag-integrity check updated to reject the retired flags and to require every skill's Arguments table to define `--auto`.

## [1.1.0] - 2026-07-17

### Added — harness-context-file audit scope (2026-07)

- **`ds-docs` `harness` scope** — audits/trims AI-harness context files (CLAUDE.md, AGENTS.md, `.cursor/rules/`, Windsurf/Devin rules, Copilot instructions, GEMINI.md, Aider conventions) against 8 sourced rules (DOC-10..17: secrets, code-derivable content, generic advice, pasted reference material, length budget, missing recommended content, negative framing, monorepo nesting); gated behind user approval since a harness file shapes every future session. Research basis: ETH Zurich AgentBench, an independent 1,188-test benchmark, and official Anthropic/Cursor/Windsurf/Aider guidance — static hand-written context files usually add little or measurably hurt task success.

### Changed — versioning: semver from v1.0.0 (2026-07)

- Release tags now follow semver starting at **v1.0.0**; the v2-v5 labels used throughout docs/commit messages remain historical spec-generation names, explicitly decoupled from release versions (an initial v5.2.0 tag was retracted with zero consumers before v1.0.0 was cut).

### Added — ds-rig hardening (2026-07)

- **`ds-rig`** — OS-agnostic risk-class taxonomy instantiated per detected OS (POSIX + Windows cmd/PowerShell seeds); explicit protected-path map (system dirs, credential dirs, browser profiles, harness/rig configs, persistence paths, WSL dual coverage); workspace-autonomy rule (prompt-free full permissions inside the harness-detected project root, command-class risks still enforced even inside); privacy scope extended to harnesses with a verified seed map.

### Added — ds-rig: 29th skill, Equip family (2026-07)

- **`ds-rig`** (new skill, Equip family, taxonomy dimension **D11**) — machine-level AI-dev rig: pinned toolset install/update with a re-run drift table, zero-telemetry hardening proven by config read-back, additive allow/ask/deny permission profiles per harness, MCP tool-count token budget (~20-30 net-negative threshold). Catalog 28 → 29.

### Changed — v5.1 optimization program: 6 batches (2026-07)

- Every skill in the catalog passed through a per-skill optimization rubric (R1-R6) across 6 batches — Ship family (ds-commit, ds-pr, ds-devops, ds-deploy, ds-launch, ds-repo), Improve family (7 skills), Build family currency (ds-init, ds-backend, ds-frontend, ds-mobile), Document/Comply/Monetize/Track (ds-docs, ds-compliance, ds-productize, ds-issue), Discover/Orchestrate (ds-research, ds-benchmark, ds-blueprint, ds-brief, ds-ship, ds-pipeline). Program ledger closed with all 6 batches shipped.

### Added — cross-host research program (2026-07)

- Three verified research passes (competitor tools, harness system prompts, model failure modes) produced findings F1-F11, gaps G1-G6, and a P0-P2 roadmap. **OpenCode** added as a 6th supported host (reads `~/.claude/skills` directly, no install step). Stale install-path guidance corrected (`.cursorrules` ignored in Cursor Agent mode; `.windsurfrules` superseded); paste-vs-reference warning added with evidence. Completion Evidence anti-false-completion band added to every skill (P0.1); `install.sh --target` for installing into any Agent Skills host (P0.2); ds-quality gained Copilot/Gemini CLI/Codex CLI arms (P0.3).

## [1.0.0] - 2026-07-15

### Added — contract-consistency scope + principle hardening (2026-07)

- **`ds-blueprint` `contract-consistency` scope (CON-01..10, 24th analysis scope)** — system-wide lexicon + contract uniformity: same concept same name (one verb per operation class, domain terms uniform across layers), same word same meaning, analogous functions share parameter order/options shape, consistent units/formats (time, IDs, dates, boundary casing), one return/error shape per layer, divergent duplicate contracts (contract-drift twin of W17). AST batch; Architecture dimension re-weighted (25/20/15/10/15/15). `ds-review --strategic` is the verified consumer (9 scopes, 102 checks).
- **Principle hardening (§11)** — ds-productize now carries `references/principles.md` with targeted cites (§5 billing-surface security, §6 KISS/YAGNI on plan recommendations, §8 price/config externalization); ds-pipeline enforces YAGNI at planning time (every task traces to a spec requirement — speculative tasks never enter the committed queue); ds-docs flags **SSOT-copy** (docs duplicating code-owned facts instead of referencing the owning source); SKILL-SPEC §11.1/§11.6 name the new enforcement points.

### Added — paid-product coverage (2026-07)

- **`ds-productize` (28th skill, prefix PTZ)** — paid-product readiness in three owned scopes: `monetization` (model fit, server-side entitlement enforcement, webhook signature verification, subscription lifecycle, cancellation parity), `pricing` (tier/decoy structure, annual framing, price externalization, commission/MoR fit), `gtm` (value proposition cross-checked against code, persona, conversion surface, privacy-first funnel events, launch plan). `--plan` produces the committed deliverable `ds/productize/plan.md`. Every benchmark cited per rule (`references/rules-monetization.md`, `references/rules-gtm.md`); business decisions are Category B; state-exempt.
- **`ds-backend` `data-pipeline` scope (4th layer)** — ingest validation, idempotent jobs, silent-drop quarantine, stage quality gates, deterministic merges, incremental loads, retention/PII minimization, job observability, bounded backfills (`references/rules-data-pipeline.md`, DP-01..DP-10).
- **`ds-blueprint` `ai-architecture` extended (AIA-01..14)** — product-facing LLM feature checks: prompt-injection surface on untrusted input, unvalidated model output, missing eval/regression set for prompt changes, missing per-call cost/usage tracking.
- **`ds-ship` Monetization branch** — Phase 0 ambiguity block now asks monetization intent (free / paid / internal); paid intent inserts `/ds-productize --audit` (greenfield: `--plan`) into Phase 2 after stack-specific skills. Store execution stays with ds-launch, canonical privacy with ds-compliance.

### Added — installer + consistency CI (2026-07)

- **`install.sh`** — one-command install/sync/verify: copies only runtime files (skill dirs + `agents/`) into `~/.claude` (or `--project DIR`); per-skill `--skills a,b` selection; `--check` reports drift against the repo (version-stamped via `.dev-skills-version`); `--uninstall`; idempotent, `rsync --delete` per skill so removed files never linger in the installed copy.
- **`scripts/check-consistency.sh` + GitHub Actions CI** — zero-dependency consistency gate on every push/PR: skill count == README badge, SKILL.md ≤500 / README ≤80, exactly one spec-parseable Delegation line per skill, no duplicate `Owns:` tokens, state recovery protocol only in the 4 qualifying skills, no W-numbers beyond W17, INVOKE/DON'T INVOKE table present everywhere, canonical `ds/audit/` gitignore pattern.

### Changed — repo-wide consistency overhaul (2026-07)

- **SKILL-SPEC contradictions resolved** — `findings.md` scoped-overwrite semantics clarified; single authoritative producer per scope + verified-consumer model; frontmatter `name`+`description` legalized; ownership/utilization tables completed to all 27 skills; FRC disposition tokens normalized.
- **State protocol narrowed** — only `ds-tune`, `ds-solve`, `ds-ship`, `ds-blueprint` persist to `ds/audit/<skill>.json`; resumable-state machinery removed from the ~16 other skills that had carried it.
- **Delegation matrix symmetry restored** — 13 line fixes across cross-skill delegation references.
- **ds-quality rebuilt as a 3-arm hybrid** — Claude Code Stop-hook (stop-time) / Aider auto-lint+auto-test (edit-time) / universal git pre-commit (commit-time); golangci-lint coverage gap closed.
- **ds-blueprint reference taxonomy regenerated** — 23-scope taxonomy.
- **W18/W19 contamination removed** from ds-research, ds-brief, and shared agent definitions.
- **ds-brief HTML template ASCII-neutralized.**
- **ds-research artifactPath handoff gate added.**
- **Verified rule counts corrected everywhere** — ds-compliance 98, ds-mobile 171, ds-frontend 48, engineering principles 110.
- **Domain gaps closed** — multi-tenant DB rule, 12-Factor 1/4/8, SLSA provenance, GitHub Rulesets, ds-commit filename-based secret exclusion, ds-pr changed-files scope, ds-tune statistical significance, ds-test mode menu, `ds-ship` → `ds-pipeline` routing.
- Root docs (README, CLAUDE, `docs/guide.html`, this file, `references/software-best-practices.md`) synced to the verified numbers above.

### Added — ds-issue: implementation-contract intake (2026-07)

- **ds-issue intake** — issue body now carries an Evidence/repro block (required for fix-type issues), EARS-phrased Done criteria on behavioral tasks, a per-step verify contract (`command → expected`), and anchored impact-surface hints.
- **ds-issue `--do`** — plan-coverage check ensures every Done item is owned by ≥1 plan unit; close evidence maps 1:1 to Done items, an uncovered item blocks the close.
- Design-open features now route to `ds-pipeline` instead of becoming a mega-issue.
- Stale phase numbers fixed in references (self-check Phase 5→4, status-audit Phase 6→5).

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
