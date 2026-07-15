# dev-skills

Multi-phase AI coding assistant skills covering the full software lifecycle — gates, error recovery, and systematic mitigation of 17 known AI failure modes (W1–W11 universal + W12–W17 domain-specific) across Claude Code, OpenCode, Cursor, Copilot, Windsurf, and Aider.

## Meta

- **Status:** active
- **Owner:** sungurerdim
- **License:** MIT
- **Stack:** Markdown only — zero runtime dependencies
- **Skill count:** 28
- **Tool support:** Claude Code, OpenCode, Cursor, Copilot, Windsurf, Aider (Agent Skills spec readers; OpenCode consumes `~/.claude/skills/` directly)
- **Active program:** v5 cross-host — see `docs/methodology/cross-host-program.md` (2026-07-15 research: verified findings F1–F10, gaps G1–G6, program P0–P2)

## Project Structure

| Path | Purpose |
|------|---------|
| `ds-<name>/` | One directory per skill (ds-init, ds-fix, ds-review, ds-deploy, etc.) |
| `SKILL-SPEC.md` | Authoritative skill format spec — every `ds-*` must conform |
| `agents/` | Shared agent definitions (`ds-research-agent` — worker for ds-research + ds-brief); install to the host agent dir, e.g. `~/.claude/agents/` |
| `docs/` | Topic-organized references (backend, frontend, devops, compliance, business, launch, methodology, infrastructure) |
| `references/` | Source material (`software-best-practices.md`, `launch-research.md`) |

## Skills (28)

**Family map** — every skill on one screen; each row is one distinct job (no overlap after the off-domain extraction):

| Family | Skills | Each one's unique job | Dimensions |
|--------|--------|-----------------------|------------|
| **Discover** | `ds-research` · `ds-benchmark` · `ds-blueprint` | multi-source research · external gap-analysis vs comparables · internal 9-dim health score | A1, B2, B4 |
| **Build** | `ds-init` · `ds-backend` · `ds-frontend` · `ds-mobile` | scaffold from zero · API+DB+auth+data-pipeline design · design-system/a11y · mobile release audit | A5–A7, A9–A10, B5, D3–D5 |
| **Improve** | `ds-review` · `ds-simplify` · `ds-fix` · `ds-quality` · `ds-test` · `ds-deps` · `ds-tune` · `ds-solve` | audit (flag) · safe deletion · format/lint/type passes (one-shot) · 3-arm quality gate — stop-time/edit-time/commit-time (enforce continuously) · real tests · dep upgrades · metric optimization loop · hard-problem backtracking | A8, B1, B3, C4, D1–D2, D9 |
| **Document** | `ds-docs` · `ds-brief` | doc drift+ADRs · printable sourced HTML brief | A10, B5, B6, C3, C5 |
| **Comply** | `ds-compliance` | regulatory/privacy/a11y/security audit | A7–A8, C1–C3 |
| **Monetize** | `ds-productize` | paid-product readiness — monetization/billing integrity · pricing/packaging · GTM baseline | A1–A3 |
| **Track** | `ds-issue` | GitHub issues: file · sweep · status · do (4 modes) | — (carrier) |
| **Ship** | `ds-commit` · `ds-pr` · `ds-devops` · `ds-deploy` · `ds-launch` · `ds-repo` | atomic commits · PR description · CI/CD audit · infra configs · store release · repo settings | A4, B4, D6–D8 |
| **Orchestrate** | `ds-ship` · `ds-pipeline` | classify stage → sequence + delegate the above · idea → gated spec/plan/tasks handoff (Spec Kit conductor) | — (carrier) |

Flat list: `ds-backend`, `ds-benchmark`, `ds-blueprint`, `ds-brief`, `ds-commit`, `ds-compliance`, `ds-deploy`, `ds-deps`, `ds-devops`, `ds-docs`, `ds-fix`, `ds-frontend`, `ds-init`, `ds-issue`, `ds-launch`, `ds-mobile`, `ds-pipeline`, `ds-pr`, `ds-productize`, `ds-quality`, `ds-repo`, `ds-research`, `ds-review`, `ds-ship`, `ds-simplify`, `ds-solve`, `ds-test`, `ds-tune`

`ds-pipeline` is the spec-pipeline conductor: it runs the external [Spec Kit](https://github.com/github/spec-kit) chain (`specify → clarify → plan → tasks → analyze`) with blocking gates (zero open clarifications; per-task `— verify:` contract + EARS on behavioral tasks; zero CRITICAL cross-artifact findings), then commits `specs/{feature}/` with an executor handoff line. Planning-only (never touches source), state-exempt (artifacts + git are the record), artifact-driven resume. Prefix `PIPE` (SKILL-SPEC appendix).

`ds-issue` is the single GitHub-Issues-centric skill covering the whole lifecycle in four modes: intake (default) · `--sweep` dedup · `--status` code-verified done-audit · `--do #N` issue-bound execution (re-verify → impact-map → implement → code-proven close), with `--do --all` running that flow over every open issue in priority order (confirm-per-item, skip-and-record blockers). State-exempt (zero local footprint — GitHub + git are the durable record). Reads an optional per-project `.dev-skills/issue-ops.json` adapter; standalone via auto-detect when absent. Prefix `ISS` (SKILL-SPEC appendix).

## Development

- Skills are pure Markdown; **zero runtime dependencies**
- Each skill has `SKILL.md` + supporting files
- Test: install into `~/.claude/skills/` and invoke via `/ds-<name>`
- Spec compliance: every skill must satisfy `SKILL-SPEC.md` (audited 2026-05-18 for v2: W10/W11, Trigger Discipline, All-Affordance Rule; updated 2026-07-11 for v4: Standalone Invariant, AI-Legibility, Dimension Ownership)
- Self-audit: run `/full-review` (local command, not in repo) — 11 categories (v2 + v4) × ~80 checks against the spec
- Dimension ownership: every SKILL.md declares its taxonomy dimensions in a `**Dimensions:**` line; see SKILL-SPEC §11 and Appendix: Dimension Coverage Map

## Git Workflow

- **Direct push to main** — no branch requirement
- **Conventional commits** — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Manual releases** — `gh release create vX.Y.Z --generate-notes`

## v2 Invariants (2026-05-18)

- **W10 Findings-SSOT Drift:** downstream consumers defer to fresh `ds/audit/findings.md`; never re-detect within blueprint's covered scopes.
- **W11 Error Ownership Skip:** detected errors get a concrete disposition; reject reasons like `pre-existing`, `not my change`, `out of scope`, `too hard`, `will do later`.
- **Trigger Discipline:** every `ds-*/SKILL.md` ships an `INVOKE / DON'T INVOKE` table. Unscoped verbs alone are not valid triggers.
- **All-Affordance Rule:** every menu offers `all` / `apply-all` / `approve-all`. CRITICAL findings + destructive actions still require per-item confirmation.
- **`/ds-review --meta-quality`:** SSOT / DRY / KISS / YAGNI / SoC principle audit with 3 consolidation paths per finding.
- **Anti-overengineering 3-gate** screens every potential finding before reporting.

## v3 additions (2026-06)

- **Up-Front Mode Menu:** multi-mode skills present the choice covering every scenario (with `(recommended)` + `(Cancel)`) when no disambiguating flag is passed.
- **Category Bulk Affordance:** menus offer per-group bulk (`all CRITICAL` / `all HIGH` / `all <type>`) **alongside** the total "all" — never replacing it.
- **Selection Transparency:** every approval states the exact question and shows every item compactly (severity + title + file:line); "all" = exactly the displayed set, never a bare count.
- **Least-footprint state:** prefer no state; only `ds-tune`, `ds-solve`, `ds-ship`, `ds-blueprint` persist to `ds/audit/<skill>.json`. Every other skill — including git/GitHub-backed ones (ds-commit, ds-pr, ds-issue) — is state-exempt.

## v4 Invariants (2026-07-11)

- **Standalone Invariant:** every non-orchestrator skill works alone — cross-skill references use advisory-handoff (target present → delegate; absent → inline-check or gap-note). No hard-fail.
- **AI-Legibility Standard:** 8 rules: imperative mood, one term per concept, tables over prose, explicit IO contracts, no implicit deps, no vague conditions, if/then tables for decisions, measured token reduction.
- **Dimension Ownership Design Rule:** every SKILL.md declares `**Dimensions:**` line; no dimension unowned; overlap = spec violation; enforced by `check-consistency.sh`.
- **Taxonomy Amendment Process:** new dimensions proposed via Issue/PR with name + layer + skill + framework reference; gates: no overlap + capacity; merge updates 3 files.

## Philosophy

- Every dependency is a future breaking change
- Collect nothing you don't need
- If a human is doing it repeatedly, it should be automated
- Every decision minimizes YOUR legal exposure (not the vendor's)

## Blueprint Profile

Type: library | Stack: markdown | Target: production
Priorities: code-quality, dx, docs | Constraints: zero-new-dependencies, keep-markdown-only
Integrations: none
Data: none | Regulations: none
Audience: public, other-developers | Deploy: git-clone-plus-install-sh

Entry: README.md (docs) ; install.sh (tooling)
Modules: ds-*/=skill(28); agents/=shared-agent(1); docs/=reference-docs(9-dirs); references/=source-material(2); scripts/=ci-tooling(1)
Data Flow: repo-clone→install.sh→~/.claude/skills→AI-host-invocation
External: rsync(sync-tool, system-only)
Toolchain: bash scripts/check-consistency.sh | CI: github-actions (consistency-only) | Container: none

Ideal: coupling=low cohesion=high complexity=low coverage=n/a

Scores: sec=92 quality=72 arch=65 perf=90 resil=45 test=55 stack=88 dx=78 docs=68 overall=73 model=claude-sonnet-5

## End Blueprint Profile
