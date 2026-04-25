# dev-skills

Multi-phase AI coding assistant skills covering the full software lifecycle — gates, error recovery, and systematic mitigation of 8 known AI failure modes across Claude Code, Cursor, Copilot, Windsurf, and Aider.

## Meta

- **Status:** active
- **Owner:** sungurerdim
- **License:** MIT
- **Stack:** Markdown (skills) + Bash (install)
- **Skill count:** 26
- **Tool support:** Claude Code, Cursor, Copilot, Windsurf, Aider

## Project Structure

| Path | Purpose |
|------|---------|
| `ds-<name>/` | One directory per skill (ds-init, ds-fix, ds-review, ds-deploy, etc.) |
| `SKILL-SPEC.md` | Authoritative skill format spec — every `ds-*` must conform |
| `docs/` | Topic-organized references (backend, frontend, devops, compliance, business, launch, methodology, infrastructure) |
| `references/` | Source material (`software-best-practices.md`, `launch-research.md`) |
| `Announce.md` | Launch copy |
| `Video.md` | Demo video script |

## Skills (26)

`ds-analytics`, `ds-backend`, `ds-benchmark`, `ds-blueprint`, `ds-commit`, `ds-compliance`, `ds-cv`, `ds-deploy`, `ds-deps`, `ds-devops`, `ds-docs`, `ds-fix`, `ds-frontend`, `ds-init`, `ds-launch`, `ds-market`, `ds-mobile`, `ds-pr`, `ds-repo`, `ds-research`, `ds-review`, `ds-ship`, `ds-simplify`, `ds-solve`, `ds-test`, `ds-tune`

## Development

- Skills are pure Markdown; **zero runtime dependencies**
- Each skill has `SKILL.md` + supporting files
- Test: install into `~/.claude/skills/` and invoke via `/ds-<name>`
- Spec compliance: every skill must satisfy `SKILL-SPEC.md` (audited 2026-04-25)

## Git Workflow

- **Direct push to main** — no branch requirement
- **Conventional commits** — `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`
- **Manual releases** — `gh release create vX.Y.Z --generate-notes`

## Philosophy

- Every dependency is a future breaking change
- Collect nothing you don't need
- If a human is doing it repeatedly, it should be automated
- Every decision minimizes YOUR legal exposure (not the vendor's)
