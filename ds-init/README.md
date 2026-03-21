# ds-init

Generate production-ready project structure for any stack — CI, Docker, testing, editor config, env templates.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-init`, or ask to scaffold a new project.

## Modes

| Mode | What It Does |
|------|-------------|
| **Interactive** (default) | Guide through type + stack selection |
| **--minimal** | Bare minimum directory structure |
| **--full** | Full production setup (CI, Docker, testing, docs) |
| **--dry-run** | Preview files without creating them |

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
- CI pipeline: lint → test → build
- Docker multi-stage builds for production
- Comprehensive `.gitignore` per stack
