# ds-init

New projects start with no CI, no test setup, no linting, and inconsistent structure. This skill scaffolds all of it from day one.

**Generate production-ready project structure for any stack — CI, Docker, testing, editor config, env templates.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-init ~/.claude/skills/ds-init` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-init`, or ask to scaffold a new project.

## Modes

| Mode | What It Does |
|------|-------------|
| Default | Type + stack resolve from signals or the lowest-blast-radius fallback; every decision resolved by best judgment |
| **--minimal** | Bare minimum directory structure |
| **--full** | Full production setup — adds CI workflow files, Docker, docs |
| **--research** | Look up comparable scaffolds and current framework/tool versions first |
| **--preview** | Preview files without creating them |
| **--ask** | Interactive — menus and confirmations at every decision point |

## Supported Types

| Type | Example Stacks |
|------|---------------|
| Web App | Next.js, React, Vue, Svelte, SvelteKit |
| API | Express, FastAPI, Go, Rust (Axum) |
| Mobile | Flutter, React Native |
| CLI | Node.js, Python, Go, Rust |
| Library | Any language package |
| Monorepo | Turborepo, Nx, pnpm workspaces |

## Features

- Detects existing files and preserves them (no overwrites without confirmation)
- Generates `.env.example` (never real secrets)
- Local quality gate wired by default; CI pipeline (lint → test → build) generates under `--full`
- Privacy-policy stub + data-inventory file when the project handles personal data
- Docker multi-stage builds for production
- Comprehensive `.gitignore` per stack
