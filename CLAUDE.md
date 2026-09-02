# dev-skills

Multi-phase AI coding assistant skills covering the full software lifecycle — gates, error recovery, and systematic mitigation of 17 known AI failure modes (W1–W11 universal + W12–W17 domain-specific) across Claude Code, OpenCode, Cursor, Copilot, Windsurf, and Aider.

**Mission:** enable a solo developer + AI to ship production-ready, high-quality products in any software project — encoding each domain's complete best practices (security, performance, privacy, accessibility, UX/UI, testing, compliance, operations) as executable gates, so quality does not depend on the developer's knowledge, attention, or available time. Target: the highest-quality, most practical skill set in its class — every critical point covered, nothing that doesn't earn its keep.

## Meta

- **Status:** active
- **Owner:** sungurerdim
- **License:** MIT
- **Stack:** Markdown only — zero runtime dependencies
- **Skill count:** 32
- **Tool support:** Claude Code, OpenCode, Cursor, Copilot, Windsurf/Devin Desktop (June 2026 rebrand — newer builds prefer `.devin/rules/`), Aider (Agent Skills spec readers; OpenCode consumes `~/.claude/skills/` directly)
- **Releases:** semver from v1.0.0 (2026-07-15); v2–v5 labels in docs/commits are spec-generation names, not release versions (see README § Versioning)
- **Active program:** cross-host (spec-gen v5) — see `docs/methodology/cross-host-program.md` (2026-07-15 research: verified findings F1–F11, gaps G1–G6, program P0–P2, ds-rig)

## Project Structure

| Path | Purpose |
|------|---------|
| `ds-<name>/` | One directory per skill (ds-init, ds-fix, ds-review, ds-deploy, etc.) |
| `SKILL-SPEC.md` | Authoritative skill format spec — every `ds-*` must conform |
| `agents/` | Shared agent definitions (`ds-research-agent` — worker for ds-research + ds-brief); install to the host agent dir, e.g. `~/.claude/agents/` |
| `docs/` | `methodology/` (research + program records, authoring checklist) and `guide.html` (interactive production-readiness guide); the former lifecycle guides were migrated into the owning skills' rules files in 2.0.0 |
| `core/` | Shared runtime references every skill links to as `../core/<file>.md` — principles, severity/score, findings + profile format, signal inventory, ask-exception list, checkpoint protocol, execution loop, report templates, secret patterns, toolchains, CRAAP, plus the `software-best-practices.md` catalog and the `experience-rules.md` XR pointer map. Shipped on every install; no SKILL.md inside |
| `scripts/` | The gate: `quality.sh` (entry point), `check-consistency.sh` (+ `--self-test`, `--mutation-test`), `test-install.sh` (installer round-trip) |
| `install.sh` · `install.cmd` | The installer (bash + coreutils + git, no rsync) and its Windows launcher; `--check`, `--status`, `--update`, `--uninstall` |
| `AGENTS.md` | Cross-host contributor instructions — the file Codex/Cursor/Copilot/Aider read; this file is the Claude-Code counterpart |
| `.github/` | Issue + PR templates only — no workflows, the gate is local by design |

## Skills (32)

**Family map** — every skill on one screen; each row is one distinct job (no overlap after the off-domain extraction):

| Family | Skills | Each one's unique job | Dimensions |
|--------|--------|-----------------------|------------|
| **Equip** | `ds-rig` | machine-level AI-dev rig — pinned toolset install/update · zero-telemetry hardening · harness allow/ask/deny permission profiles · MCP token budget | D11 |
| **Discover** | `ds-research` · `ds-benchmark` · `ds-blueprint` | multi-source research · external gap-analysis vs comparables · internal 9-dim health score | A1, B2, B4 |
| **Build** | `ds-init` · `ds-backend` · `ds-frontend` · `ds-mobile` · `ds-build` | scaffold from zero · API+DB+auth+data-pipeline design · design-system/a11y · mobile release audit · plan executor (issue / tasks.md / request → verified units) | A5–A7, A9–A10, B5, D3–D5 |
| **Improve** | `ds-review` · `ds-simplify` · `ds-fix` · `ds-quality` · `ds-test` · `ds-deps` · `ds-tune` · `ds-debug` | audit (flag) · safe deletion · format/lint/type passes (one-shot) · 3-arm quality gate — stop-time/edit-time/commit-time (enforce continuously) · real tests · dep upgrades · metric optimization loop · reproduce → root cause → red-proven fix | A8, B1, B3, C4, D1–D2, D9 |
| **Document** | `ds-docs` · `ds-brief` | doc drift+ADRs · printable sourced HTML brief | A10, B5, B6, C3, C5 |
| **Comply** | `ds-compliance` | regulatory/privacy/a11y/security audit | A7–A8, C1–C3 |
| **Monetize** | `ds-productize` | paid-product readiness — monetization/billing integrity · pricing/packaging · GTM baseline | A1–A3 |
| **Track** | `ds-issue` | GitHub issues: file · sweep · status · do (4 modes) | — (carrier) |
| **Ship** | `ds-freeze` · `ds-commit` · `ds-pr` · `ds-release` · `ds-devops` · `ds-deploy` · `ds-launch` · `ds-repo` | collaborative release-scope triage (ship/defer-hidden/defer-backlog) · atomic commits · PR description · release cut (version · changelog · tag; publishing handed back) · CI/CD audit · infra configs · store release · repo settings | A4, B4, D6–D8 |
| **Orchestrate** | `ds-ship` · `ds-pipeline` | classify stage → sequence + delegate the above · idea → gated spec/plan/tasks handoff (Spec Kit conductor) | — (carrier) |

Flat list: `ds-backend`, `ds-benchmark`, `ds-blueprint`, `ds-brief`, `ds-build`, `ds-commit`, `ds-compliance`, `ds-debug`, `ds-deploy`, `ds-deps`, `ds-devops`, `ds-docs`, `ds-fix`, `ds-freeze`, `ds-frontend`, `ds-init`, `ds-issue`, `ds-launch`, `ds-mobile`, `ds-pipeline`, `ds-pr`, `ds-productize`, `ds-quality`, `ds-release`, `ds-repo`, `ds-research`, `ds-review`, `ds-rig`, `ds-ship`, `ds-simplify`, `ds-test`, `ds-tune`

`ds-pipeline` is the spec-pipeline conductor: it runs the `specify → clarify → plan → tasks → analyze` chain natively (the external [Spec Kit](https://github.com/github/spec-kit) is optional, used when installed) with blocking gates (zero open clarifications; per-task `— verify:` contract + EARS on behavioral tasks; zero CRITICAL cross-artifact findings), then commits `specs/{feature}/` with a handoff to `/ds-build` (any executor when it is absent). Planning-only (never touches source), state-exempt (artifacts + git are the record), artifact-driven resume. Prefix `PIPE` (SKILL-SPEC appendix).

`ds-build` executes a plan (issue, `specs/{feature}/tasks.md`, or plain request) one bounded unit at a time with a verify signal per unit, red-proven regression tests and budgeted backtracking; `ds-debug` reproduces a failure, localizes it (bisect, trace), tests ≤ 3 hypotheses and lands the minimal fix behind a test seen red first; `ds-release` derives the version from the commits, reconciles the CHANGELOG, bumps every version surface, proves the check green, commits + tags locally and hands every publishing step back with the exact command. Prefixes `BLD`, `DBG`, `REL`. `ds-solve` was retired in 2.0.0 — its budgeted backtracking lives in ds-build, its hypothesis loop in ds-debug.

`ds-issue` is the single GitHub-Issues-centric skill covering the whole lifecycle in four modes: intake (default) · `--sweep` dedup · `--status` code-verified done-audit · `--do #N` issue-bound execution (re-verify → impact-map → implement → code-proven close), with `--do --all` running that flow over every open issue in priority order (confirm-per-item, skip-and-record blockers). State-exempt (zero local footprint — GitHub + git are the durable record). Reads an optional per-project `.dev-skills/issue-ops.json` adapter; standalone via auto-detect when absent. Prefix `ISS` (SKILL-SPEC appendix).

## Development

- Skills are pure Markdown; **zero runtime dependencies**
- **Quality gate — `bash scripts/quality.sh`.** The single entry point, run locally; there is no CI. It runs the consistency gate, that gate's fixture self-test, and the ds-brief verifier's self-test, fail-fast. `--install-hook` wires it to `git commit`; a red gate is fixed before the commit, never bypassed — the `--no-verify` ban is absolute (`core/principles.md` § the commit-hook row; ds-commit's contract never offers it). `python3` absent → the run fails and names what went unverified; an unrun check must never read as a passing one
- Each skill has `SKILL.md` + supporting files
- Test: install into `~/.claude/skills/` and invoke via `/ds-<name>`
- Spec compliance: every skill must satisfy `SKILL-SPEC.md` (audited 2026-05-18 for v2: W10/W11, Trigger Discipline, All-Affordance Rule; updated 2026-07-11 for v4: Standalone Invariant, AI-Legibility, Dimension Ownership)
- Dimension ownership: every SKILL.md declares its taxonomy dimensions in a `**Dimensions:**` line; see SKILL-SPEC §11 and Appendix: Dimension Coverage Map

## Git Workflow

- **Direct push to main** — no branch requirement
- **Conventional commits** — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Manual releases** — `gh release create vX.Y.Z --generate-notes`

## v2 Invariants (2026-05-18)

- **W10 Findings-SSOT Drift:** downstream consumers defer to fresh `ds/audit/findings.md`; never re-detect within blueprint's covered scopes.
- **W11 Error Ownership Skip:** detected errors get a concrete disposition; reject reasons like `pre-existing`, `not my change`, `out of scope`, `too hard`, `will do later`.
- **Trigger Discipline:** every `ds-*/SKILL.md` ships an `INVOKE / DON'T INVOKE` table. Unscoped verbs alone are not valid triggers.
- **All-Affordance Rule (under `--ask`):** every menu offers `all` / `apply-all` / `approve-all`. CRITICAL findings + destructive actions still require per-item confirmation.
- **`/ds-review --meta-quality`:** SSOT / DRY / KISS / YAGNI / SoC principle audit with 3 consolidation paths per finding.
- **Anti-overengineering 3-gate** screens every potential finding before reporting.

## v3 additions (2026-06)

- **Up-Front Mode Menu (under `--ask`):** multi-mode skills present the choice covering every scenario (with `(recommended)` + `(Cancel)`) when no disambiguating flag is passed; without `--ask` the mode is derived from the signals and recorded.
- **Category Bulk Affordance:** menus offer per-group bulk (`all CRITICAL` / `all HIGH` / `all <type>`) **alongside** the total "all" — never replacing it.
- **Selection Transparency:** every approval states the exact question and shows every item compactly (severity + title + file:line); "all" = exactly the displayed set, never a bare count.
- **Least-footprint state:** prefer no state; only `ds-tune`, `ds-ship`, `ds-blueprint`, `ds-mobile`, `ds-frontend` persist to `ds/audit/<skill>.json`. The last two qualify because their multi-scope scan progress exists nowhere else — every other skill, including the git/GitHub-backed ones (ds-commit, ds-pr, ds-issue), is state-exempt because an external record already carries the progress. `scripts/check-consistency.sh` check 5 is the guard: it fails both a non-qualifying skill that grows the protocol and a qualifying skill that loses it.

## v4 Invariants (2026-07-11)

- **Standalone Invariant:** every non-orchestrator skill works alone — cross-skill references use advisory-handoff (target present → delegate; absent → inline-check or gap-note). No hard-fail.
- **AI-Legibility Standard:** 8 rules: imperative mood, one term per concept, tables over prose, explicit IO contracts, no implicit deps, no vague conditions, if/then tables for decisions, measured token reduction.
- **Dimension Ownership Design Rule:** every SKILL.md declares `**Dimensions:**` line; no dimension unowned; overlap = spec violation; enforced by `check-consistency.sh`.
- **Taxonomy Amendment Process:** new dimensions proposed via Issue/PR with name + layer + skill + framework reference; gates: no overlap + capacity; merge updates 3 files.

## v5 Invariants (2026-07-19)

- **Mechanical Done Gate (SKILL-SPEC §4):** every code-modifying skill resolves a `{check-cmd}` (ds-quality arm when installed, else stack-native format/lint/type/test), captures a baseline, re-runs after each change batch and once in aggregate before "done" — new red → fix ≤3 attempts, then revert + record; baseline red reported red-at-baseline, never inherited; no tooling → Verification-Infrastructure Gap surfaced, never silently skipped. Rationale: prose gates degrade first on low-capability executors — enforcement must be a machine signal, not model recall. Enforced by `check-consistency.sh` check #18 (21-skill list). ds-ship adds enforcement-arm-first sequencing + capability-tier routing for delegations.

## v6 Invariants (2026-07-25)

Driven by [The new rules of context engineering for Claude 5 generation models](https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models) (Anthropic, 2026-07-24) — >80% of Claude Code's system prompt removed for Claude 5 generation models with no measurable eval loss.

- **Completion Evidence band is profile-conditional (SKILL-SPEC §1):** portable profile (repo default, six-host support) carries both copies, justified by model-family position bias (MOSAIC arXiv:2601.18554); the lean install profile (`./install.sh --profile lean` — for Claude-5-generation hosts with an always-on rules layer such as dev-rules) carries the opening copy alone, produced by an install-time strip of `<!-- portable-only -->`-marked blocks. The band itself is never optional — only the copy count is. Repo files always keep the full portable text.
- **Reference Forms (SKILL-SPEC § Reference Forms):** a reference takes the highest-fidelity form its content allows — rule list, template, rubric, working artifact (HTML mockup, fixture), or test-suite-as-spec. Every reference declares its consumer; one with no named consumer is deleted.
- **Rubrics for taste, rules for patterns:** a judgment with no greppable pattern (is this the right abstraction?) goes in a `rubric-*.md` handed whole to a verifier pass, with each level claimed only against a `file:line` example. Never a bare score range.
- **Cross-repo single home:** guidance owned by a skill here (commit grouping + message format → ds-commit, severity/skip patterns/review scope/fix quality → ds-review, complexity thresholds → ds-fix) is not re-derived in dev-rules' always-on `rules.md`; that file points at the owning skill. **One deliberate exception, stated on both sides:** `rules.md` keeps the conventional-commit *type-selection* rule inline (`feat` only for a new end-user capability, `fix` only for user-visible breakage) because it fires while work is being planned, before any skill runs — grouping, message shape, trailers and the hook policy stay ds-commit's alone. Any other inline copy is drift, and nothing mechanical guards this boundary today: the two repos' consistency scripts each check only their own side.
- **Standalone Invariant is now mechanically enforced**, not prose-asserted. `check-consistency.sh` gained check 21 (no skill references another skill's files by path) and check 22 (every relative `.md` link resolves *and* stays inside its own skill directory — a lone install ships one directory, so an escaping link is dead even when the repo layout makes it look fine). Both carry self-test fixtures. (2.0.0 folded both into `check_core_links`: a link resolves inside its own skill directory or under `../core/`.) Prose handoffs across skills remain correct and expected; only file paths are barred. Rationale: check 10 caught hard-fail *wording* but nothing caught a dangling or escaping *path*, which is the way a lone install actually breaks.

## v7 Invariants (2026-09-02, release 2.0.0)

- **Autonomous Default:** no flag = every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list (`core/ask-exception-list.md`) is skipped and recorded `only you can do`. `--ask` (canonical row, byte-exact across all skills) restores menus and approval batches at every decision point and propagates from ds-ship to its delegates. `--auto` is retired — no alias. Guards: `check_ask_row_canonical`, retired-flag list, `check_undefined_flags`.
- **Relevance First:** every skill with ≥ 2 scopes carries a `| Scope | Runs when (signal) | Otherwise |` table; scopes run on a project signal (`core/signal-inventory.md`, produced by ds-blueprint's `Signals:` line) and are otherwise `N/A — reason`. ds-ship's `--mode=improve|release|launch|maintain` decides which release/launch legs run at all. Guard: `check_scope_resolution_table`.
- **Standalone with core:** shared references live once in `core/` (no SKILL.md, shipped on every install including `--skills` subsets); skills link `../core/<file>.md`; sibling skills stay advisory (present → delegate, absent → inline or gap-note). The spec is never cited from a skill — canonical inline equivalents instead. Guards: `check_core_links`, `check_spec_citations`, `check_dead_sources`.
- **Every rule states its Impact**, every phase gate has a red branch, every README count mirrors its SKILL.md. Guards: `check_rule_impact`, `check_duplicate_rule_titles`, `check_readme_counts`.
- **Closing block shared with dev-rules:** every run ends with `Asked` / `Done` / `Effect` / `Decided without asking — say if wrong` / `Only you can do` (empty lines omitted), and every choice put to the user is recommendation-first with options in one shape. dev-rules owns the text; `core/report-and-outcome-templates.md` § 5 is the portable copy, stripped from lean/claude installs; `scripts/quality.sh` runs dev-rules' `check-cross-repo.sh` when the sibling checkout exists (visibly skipped otherwise).
- **Installer is bash + coreutils + git** (no rsync); `install.cmd` launches it from cmd.exe/PowerShell; profiles `portable` (repo default) · `lean` (strip portable-only blocks) · `claude` (lean + ds-ship delegates run as forked subagents). `scripts/test-install.sh` proves every mode.

## Philosophy

- Every dependency is a future breaking change
- Collect nothing you don't need
- If a human is doing it repeatedly, it should be automated
- Every decision minimizes YOUR legal exposure (not the vendor's)

## Blueprint Profile

Type: library | Stack: markdown | Target: production
Mission: a solo developer + AI ships production-grade software in any project, because each domain's best practices are enforced as executable gates instead of depending on the developer's knowledge, attention, or available time
Priorities: code-quality, cross-host-portability, dx, docs | Constraints: local-gate-only (no CI), single-maintainer direct-push
Red lines: zero runtime dependencies, markdown-only (no scripting language as a skill requirement), no telemetry or data collection
Integrations: none
Data: none | Regulations: none
Audience: public, other-developers | Deploy: git-clone-plus-install-sh

Entry: README.md (docs) ; install.sh (tooling)
Modules: ds-*/=skill(32); core/=shared-references(14); agents/=shared-agent(1); docs/=methodology(1-dir)+guide.html; scripts/=gate-tooling(3)
Data Flow: repo-clone→install.sh→~/.claude/skills→AI-host-invocation
External: none
Toolchain: bash scripts/quality.sh | CI: none — local gate only (git pre-commit) | Container: none

Ideal: coupling=low cohesion=high complexity=low coverage=n/a

Scores: sec=96 quality=89 arch=90 perf=90 resil=96 test=82 stack=96 dx=91 docs=88 overall=90 model=claude-opus-5

## End Blueprint Profile
