# ds-blueprint

Can't improve what you don't measure. Skill scores project across 9 dimensions and tells you exactly where to focus next.

**Project health system — profile-based assessment, transformation, and progress tracking.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-blueprint ~/.claude/skills/ds-blueprint` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-blueprint`, or ask to assess your project health.

## Flow

1. Discovery: detect project type, stack, toolchain
2. Init: profile creation (type, quality, data, priorities, constraints)
3. Assess: 5-track parallel analysis (code quality, architecture, production, docs, audit)
4. Consolidate: dimension scoring with project-type weights
5. Plan and apply fixes
6. Update profile with new scores

## Features

- **9 health dimensions** — Security, Code Quality, Architecture, Performance, Resilience, Testing, Stack Health, DX, Documentation
- **14 project types** — with type-specific weight matrices
- **Score tracking** — delta and trend across runs
- **Auto-detected instruction file** — embeds profile in your AI tool's instruction file (CLAUDE.md / AGENTS.md / .cursorrules / .cursor/rules / .github/copilot-instructions.md / .windsurfrules / .aider.conf.yml — whichever your tool uses). Always in context.
- **4 quality levels** — Prototype, MVP, Production, Enterprise
- **W10 SSOT producer** — writes `ds/audit/findings.md` fresh on every run; downstream skills defer to it (no re-detection)
- **Parallel-track planning** (Phase 2.5) — scopes grouped as read-only / AST / cross-file batches so AI hosts can plan concurrency consciously
- **Penalty-based scoring** — `score = max(0, 100 - 25C - 10H - 3M - 1L)` with -50 per-dimension cap; cross-dimension coherence check (related-pair gap > 40 → re-evaluate)
- **`filters_applied` audit field** — `findings.md` meta header surfaces skipped scopes, downgraded confidence, project-type detection, user overrides
- **`--memory-cleanup` flag** (opt-in) — scans AI host memory index (`MEMORY.md`) for broken `[[link]]` references
