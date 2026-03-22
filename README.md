# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-19-blue)]()
[![Tool](https://img.shields.io/badge/works_with-Claude_Code_·_Cursor_·_Copilot_·_Windsurf_·_Aider-green)]()

Production-grade AI skills for the full software lifecycle — from scaffolding to store launch. Self-contained, tool-agnostic, token-efficient. Built for solo developers with AI assistance.

> **scaffold → code → test → review → commit → PR → deploy → launch → marketing → analytics**
>
> 19 orchestrated skills. One system. Any AI coding tool.

> [!TIP]
> **Quick start:** Clone the repo, copy any skill folder to your AI tool's instructions directory (see Install below), and invoke the skill name (e.g. `/ds-cv`). That's it.

## Core Principles

1. **Minimal liability** — legal/regulatory exposure minimized at every step
2. **Maximum privacy** — privacy-by-design, data minimization, zero unnecessary collection
3. **Maximum efficiency & automation** — automate everything automatable, no manual repetitive work
4. **Maximum performance** — fast builds, fast deploys, fast apps, fast feedback loops
5. **Minimum external dependencies** — fewer deps = fewer risks, fewer costs, fewer breakages
6. **Solo-dev optimal** — every decision optimized for one-person teams with AI assistance

## Why dev-skills

Most AI coding "skills" are static rule snippets (30-100 lines) or link collections. dev-skills are **orchestrated execution systems**:

- **Multi-phase workflows** with quality gates and error recovery — not "do X, then Y" instructions
- **8 AI weaknesses systematically addressed** — hallucination, scope creep, confidence bias, tunnel vision, memory decay, skip tendency, redundancy blindness, injection risk. Output templates use `{placeholder}` syntax to prevent AI from copying example data as real findings
- **Inter-skill coordination** via `.findings.md` — skills share analysis results to avoid duplicate work
- **Token-efficient** — 10K token budget per skill, references loaded on demand
- **Full lifecycle coverage** — the only skill set covering scaffold → launch → analytics in one system
- **Tool-agnostic** — works with Claude Code, Cursor, GitHub Copilot, Windsurf, Aider, and any tool that accepts markdown instructions

19 deep skills cover more of the software lifecycle than 1,000 shallow playbooks.

## Audit Skills

| Skill | What It Does |
|-------|-------------|
| [ds-compliance](ds-compliance) | Security & regulatory compliance — OWASP, GDPR, CCPA, KVKK, HIPAA, web security, network, architecture, privacy, i18n. 80+ rules. |
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

## Business & Career Skills

| Skill | What It Does |
|-------|-------------|
| [ds-cv](ds-cv) | Professional CV generator — ATS-compatible HTML, metric verification, LinkedIn alignment, privacy by default. |
| [ds-market](ds-market) | Marketing & growth — strategy, copy generation, growth tactics. |
| [ds-analytics](ds-analytics) | Privacy-first analytics — event taxonomy, funnel design, metrics, tool integration, privacy audit. |

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

Each skill is a multi-phase execution system (not a static rule snippet). Phases have explicit entry conditions, quality gates, and error recovery — ensuring the AI follows a structured workflow rather than free-form interpretation.

The `references/*.md` files contain detailed rules loaded on demand to minimize token usage. Total skill overhead stays within a 10K token budget, leaving maximum context for the actual codebase.

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
