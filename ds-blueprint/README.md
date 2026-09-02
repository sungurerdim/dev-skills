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
2. Foundation (`--init`, or a profile without foundation lines): every normative decision (mission, target, priorities, constraints, red lines) is evidence-drafted and interrogated ("does it earn its keep? what would be better?"); by default the best-evidenced value is written and marked `derived-from-evidence`, `--ask` confirms it per line
3. Assess: 23 owned scopes in 3 concurrency batches (read-only / AST / cross-file), each resolved by the project's signals first (`N/A — {signal}=none` is a valid outcome) — scan, record, score; never fix
4. Consolidate: dimension scoring with project-type weights + calibration checks
5. Suggest: `ds/audit/findings.md` is the interface — downstream fix skills act on it
6. Update profile with new scores

## Features

- **9 health dimensions** — Security, Code Quality, Architecture, Performance, Resilience, Testing, Stack Health, DX, Documentation
- **Signal inventory** — a `Signals:` line (ui, api, db, auth, billing, pii, i18n, tests, ci, deploy, platforms, audience, jurisdiction, integrations, mobile) written into the profile and the findings meta; every other skill scopes itself by it instead of scanning everything
- **Foundation pass (`--init`)** — the profile's normative core (Mission + Red lines + Priorities/Constraints) is the calibration every dev-skill runs on; the pass idealizes it from evidence, challenges each constraint's right to exist, and locks confirmed decisions against silent flips (`--ask` confirms per line; default writes the best-evidenced value, marked as derived)
- **14 project types** — with type-specific weight matrices
- **Score tracking** — delta and trend across runs
- **Auto-detected instruction file** — embeds profile in your AI tool's instruction file (CLAUDE.md / AGENTS.md / .cursorrules / .cursor/rules / .github/copilot-instructions.md / .windsurfrules / .aider.conf.yml — whichever your tool uses). Always in context.
- **4 quality levels** — Prototype, MVP, Production, Enterprise
- **W10 SSOT producer** — writes `ds/audit/findings.md` fresh on every run; downstream skills defer to it (no re-detection)
- **Parallel-track planning** (Phase 2.5) — scopes grouped as read-only / AST / cross-file batches so AI hosts can plan concurrency consciously
- **Penalty-based scoring** — `score = max(0, 100 - 25C - 10H - 3M - 1L)` with -50 per-dimension cap; cross-dimension coherence check (related-pair gap > 40 → re-evaluate)
- **`filters_applied` audit field** — `findings.md` meta header surfaces skipped scopes, downgraded confidence, project-type detection, user overrides
- **`--preview` writes nothing** — dashboard and findings table in chat only; no profile, no `ds/audit/`, no `.gitignore` edit
