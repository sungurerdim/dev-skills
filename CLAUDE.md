# dev-skills

Multi-phase AI coding assistant skills covering the full software lifecycle — gates, error recovery, and systematic mitigation of 17 known AI failure modes (W1–W11 universal + W12–W17 domain-specific) across Claude Code, Cursor, Copilot, Windsurf, and Aider.

## Meta

- **Status:** active
- **Owner:** sungurerdim
- **License:** MIT
- **Stack:** Markdown only — zero runtime dependencies
- **Skill count:** 26
- **Tool support:** Claude Code, Cursor, Copilot, Windsurf, Aider

## Project Structure

| Path | Purpose |
|------|---------|
| `ds-<name>/` | One directory per skill (ds-init, ds-fix, ds-review, ds-deploy, etc.) |
| `SKILL-SPEC.md` | Authoritative skill format spec — every `ds-*` must conform |
| `docs/` | Topic-organized references (backend, frontend, devops, compliance, business, launch, methodology, infrastructure) |
| `references/` | Source material (`software-best-practices.md`, `launch-research.md`) |

## Skills (26)

`ds-analytics`, `ds-backend`, `ds-benchmark`, `ds-blueprint`, `ds-commit`, `ds-compliance`, `ds-cv`, `ds-deploy`, `ds-deps`, `ds-devops`, `ds-docs`, `ds-fix`, `ds-frontend`, `ds-init`, `ds-launch`, `ds-market`, `ds-mobile`, `ds-pr`, `ds-repo`, `ds-research`, `ds-review`, `ds-ship`, `ds-simplify`, `ds-solve`, `ds-test`, `ds-tune`

## Development

- Skills are pure Markdown; **zero runtime dependencies**
- Each skill has `SKILL.md` + supporting files
- Test: install into `~/.claude/skills/` and invoke via `/ds-<name>`
- Spec compliance: every skill must satisfy `SKILL-SPEC.md` (audited 2026-05-18 for v2: W10/W11, Trigger Discipline, All-Affordance Rule)
- Self-audit: run `/full-review` (local command, not in repo) — 8 categories × ~56 checks against the v2 invariants

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

## Philosophy

- Every dependency is a future breaking change
- Collect nothing you don't need
- If a human is doing it repeatedly, it should be automated
- Every decision minimizes YOUR legal exposure (not the vendor's)
