# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-19-blue)]()

Production-grade AI skills for the full software lifecycle — from scaffolding to store launch. Self-contained, tool-agnostic, token-efficient. Built for solo developers with AI assistance.

> [!TIP]
> **Quick start:** Clone the repo, copy any skill folder to your AI tool's instructions directory (see Install below), and invoke the skill name (e.g. `/ds-compliance`). That's it.

## Core Principles

1. **Minimal liability** — legal/regulatory exposure minimized at every step
2. **Maximum privacy** — privacy-by-design, data minimization, zero unnecessary collection
3. **Maximum efficiency & automation** — automate everything automatable, no manual repetitive work
4. **Maximum performance** — fast builds, fast deploys, fast apps, fast feedback loops
5. **Minimum external dependencies** — fewer deps = fewer risks, fewer costs, fewer breakages
6. **Solo-dev optimal** — every decision optimized for one-person teams with AI assistance

## Audit Skills

| Skill | What It Does |
|-------|-------------|
| [ds-compliance](ds-compliance) | Security & regulatory compliance — OWASP, GDPR, CCPA, KVKK, HIPAA, web security, privacy, a11y. 100+ rules. |
| [ds-mobile](ds-mobile) | Audit mobile apps against 145+ rules across 13 domains. Release readiness scoring, manual gates, live policy fetch. Flutter, SwiftUI, Kotlin, React Native. |
| [ds-devops](ds-devops) | Audit CI/CD pipelines, code signing, dependency management for any project type. 14 rules. |
| [ds-repo](ds-repo) | Repository audit — settings, branch protection, hygiene, metadata, team, structure. 6 scopes. |

## Development Skills

| Skill | What It Does |
|-------|-------------|
| [ds-fix](ds-fix) | Universal code quality fixer — format, lint, type-check, l10n, security scan. 16 stacks, 5 scopes. |
| [ds-test](ds-test) | Universal test skill — generate, update, run, and fix tests. Unit, integration, E2E. 13 stacks. |
| [ds-review](ds-review) | Tactical fixes + strategic architecture + deep performance profiling. 25+ scopes. `--tactical`, `--strategic`, `--perf` modes. |
| [ds-docs](ds-docs) | Documentation gap analysis + doc↔code verification. 14 project types, 8 scopes. |
| [ds-blueprint](ds-blueprint) | Project health scoring — 9 dimensions, 14 project types. Produces `.findings.md` for other skills. |

## Git Workflow Skills

| Skill | What It Does |
|-------|-------------|
| [ds-commit](ds-commit) | Smart git commits — quality gates, atomic grouping, fixup into unpushed commits, conventional format. |
| [ds-pr](ds-pr) | Smart pull requests — history tidy, net diff analysis, quality gates, auto-merge setup, branch cleanup. |

## Research

| Skill | What It Does |
|-------|-------------|
| [ds-research](ds-research) | Multi-source research with CRAAP+ reliability scoring, source tiers, triangulation, deep mode. |

## Lifecycle Skills

| Skill | What It Does |
|-------|-------------|
| [ds-init](ds-init) | Project scaffolding — generate production-ready structure for any stack. CI, Docker, testing, env templates. |
| [ds-deploy](ds-deploy) | Deployment & infrastructure — Dockerfile audit/gen, VPS hardening, SSL, monitoring, incident response, cost analysis. |
| [ds-launch](ds-launch) | Store & release management — listing metadata, privacy labels, review preparation, staged rollout. |

## Design Skills

| Skill | What It Does |
|-------|-------------|
| [ds-backend](ds-backend) | API design + database schema + auth architecture. Audit, design, spec generation, migrations. |

## Business Skills

| Skill | What It Does |
|-------|-------------|
| [ds-market](ds-market) | Marketing & growth — strategy, copy generation, growth tactics. |
| [ds-analytics](ds-analytics) | Privacy-first analytics — event taxonomy, funnel design, metrics, tool integration, privacy audit. |
| [ds-cv](ds-cv) | Professional CV generator — ATS-compatible HTML, metric verification, LinkedIn alignment, privacy by default. |

## Documentation

Universal reference docs in [`docs/`](docs/) — templates, guides, and research for the full dev lifecycle:

| Category | Docs |
|----------|------|
| **Compliance** | DPIA template, privacy policy template, breach notification, processor registry, privacy labels, legal checklist |
| **Backend** | API architecture patterns, database design guide, auth implementation guide |
| **Frontend** | UX design guidelines, web UX patterns |
| **Mobile** | Flutter architecture patterns |
| **Infrastructure** | Deployment patterns, cost optimization |
| **DevOps** | CI/CD setup guide |
| **Business** | Monetization patterns, marketing strategy, privacy-first analytics |
| **Methodology** | AI-assisted development, solo dev workflow |

## Install

Clone, then copy the skill folder to your AI tool's skill/rules directory:

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Global install | Project-level install |
|------|---------------|---------------------|
| **Claude Code** | `cp -r /tmp/dev-skills/<skill> ~/.claude/skills/<skill>` | `cp -r /tmp/dev-skills/<skill> .claude/skills/<skill>` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` | Same, or paste `SKILL.md` into project rules |
| **GitHub Copilot** | N/A | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | N/A | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag | Add to `.aider.conf.yml` conventions |
| **Other tools** | Copy `SKILL.md` + `references/` into the tool's custom instructions location | Same |

```bash
rm -rf /tmp/dev-skills
```

## How Skills Work

Each skill is self-contained:

```
skill-name/
  SKILL.md        <- Instructions and execution flow
  README.md       <- What it does, how to use it
  references/     <- Detailed rules (loaded on demand)
```

No dependencies between skills. Each skill works fully standalone. When multiple skills are used together, they share analysis results via `.findings.md` to avoid duplicate work.

The `references/*.md` files contain detailed rules loaded on demand to minimize token usage.

## Skill Specification

All skills follow [SKILL-SPEC.md](SKILL-SPEC.md) — a universal specification for building tool-agnostic, token-efficient AI coding skills. Use it to create your own skills.

## References

- [AI Instruction Patterns](references/ai-instruction-patterns.md) — Research-backed best practices for writing effective AI agent instructions (2025-2026 sources)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding skills, reporting issues, and submitting pull requests.

## Companion: dev-rules

For universal development guardrails (scope control, complexity limits, commit classification) that work with any AI tool, see [dev-rules](https://github.com/sungurerdim/dev-rules).

## License

MIT
