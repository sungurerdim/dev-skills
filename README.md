# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-19-blue)]()
[![Tool](https://img.shields.io/badge/works_with-Claude_Code_·_Cursor_·_Copilot_·_Windsurf_·_Aider-green)]()

Your AI coding assistant will hallucinate an API that doesn't exist, break file B while fixing file A, weaken your tests until they pass, and silently drop fields during data conversion. Most AI "skills" are 50-line rule snippets that can't prevent any of this.

dev-skills are multi-phase execution systems — with quality gates, error recovery, and systematic mitigation of 8 known AI weaknesses — covering the entire software lifecycle from project scaffolding to store launch.

<!-- TODO: Add demo GIF/video here — 30-60s silent demo of ds-cv or ds-review -->

> **Quick start:** `git clone https://github.com/sungurerdim/dev-skills.git /tmp/ds && cp -r /tmp/ds/ds-review ~/.claude/skills/ds-review && rm -rf /tmp/ds`
> Then: `/ds-review`

## What we believe

- **Every dependency is a future breaking change.** Fewer deps = fewer risks, fewer costs, fewer breakages.
- **Collect nothing you don't need.** Privacy-by-design, data minimization, zero unnecessary collection.
- **If a human is doing it repeatedly, it should be automated.** No manual repetitive work.
- **Every decision minimizes YOUR legal exposure.** Not the vendor's.
- **One developer + AI should ship what a team of five ships.** Every skill optimized for solo devs with AI.

## The skills

> scaffold → code → test → review → commit → PR → deploy → launch → analytics

| Skill | What it does |
|-------|-------------|
| [ds-init](ds-init) | Scaffold production-ready projects — CI, Docker, testing, env templates. Any stack. |
| [ds-fix](ds-fix) | Format, lint, type-check, l10n, secret scan. 16 stacks, 5 scopes. |
| [ds-test](ds-test) | Generate, update, run, and fix tests. Unit, integration, E2E. 13 stacks. |
| [ds-review](ds-review) | Tactical fixes + strategic architecture + deep performance profiling. 25+ scopes. |
| [ds-blueprint](ds-blueprint) | Project health scoring — 9 dimensions, 14 project types. |
| [ds-docs](ds-docs) | Documentation gap analysis + doc↔code verification. |
| [ds-commit](ds-commit) | Smart commits — quality gates, atomic grouping, conventional format. |
| [ds-pr](ds-pr) | Smart PRs — history tidy, net diff analysis, auto-merge setup. |
| [ds-deploy](ds-deploy) | Dockerfile audit/gen, VPS hardening, SSL, monitoring, cost analysis. |
| [ds-launch](ds-launch) | ~40% of store submissions fail for preventable errors. Scans your project and flags them. |
| [ds-compliance](ds-compliance) | Security & regulatory audit — OWASP, GDPR, CCPA, KVKK, HIPAA. 80+ rules. |
| [ds-mobile](ds-mobile) | Mobile app audit — 145+ rules across 13 domains. Flutter, SwiftUI, Kotlin, RN. |
| [ds-devops](ds-devops) | CI/CD pipelines, code signing, dependency management. |
| [ds-repo](ds-repo) | Repository audit — settings, branch protection, hygiene, structure. |
| [ds-backend](ds-backend) | API design + database schema + auth architecture. |
| [ds-research](ds-research) | Multi-source research with CRAAP+ reliability scoring. |
| [ds-market](ds-market) | Solo devs build great products but can't get noticed. Generates positioning, copy, and growth playbook. |
| [ds-analytics](ds-analytics) | Privacy-first analytics — event taxonomy, funnels, metrics. |
| [ds-cv](ds-cv) | ATS rejects most CVs before a human sees them. Generates ones that pass. |

Each skill is self-contained. No dependencies between them. Install one or all.

## Recommended workflow

```
1. /ds-blueprint        Score your project health, generate .findings.md
2. /ds-review --tactical  Fix code issues (uses .findings.md if available)
3. /ds-fix              Format, lint, type-check
4. /ds-test             Generate missing tests, fix failing ones
5. /ds-commit           Commit with quality gates
6. /ds-pr               Create PR with net diff analysis
```

Start with `/ds-blueprint` — it scans your entire codebase and produces a `.findings.md` that other skills consume, so they skip redundant analysis and jump straight to fixes.

For new projects: `/ds-init` → then the workflow above.
For deployment: `/ds-deploy` → `/ds-launch`.
For audits: `/ds-compliance` or `/ds-mobile`.

## Why these are different

Most AI coding "skills" are static rule snippets (30-100 lines). dev-skills are **orchestrated execution systems**:

- **Multi-phase workflows** with quality gates and error recovery
- **8 AI weaknesses systematically addressed** — hallucination, scope creep, tunnel vision, confidence bias, memory decay, skip tendency, redundancy blindness, injection risk
- **Inter-skill coordination** via `.findings.md` — share analysis results, avoid duplicate work
- **Token-efficient** — 10K token budget per skill, references loaded on demand
- **Tool-agnostic** — works with any AI tool that accepts markdown instructions

## Install

Copy any skill folder to your AI tool's instructions directory:

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/<skill> ~/.claude/skills/<skill>` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## How skills work

```
skill-name/
  SKILL.md        ← Instructions and execution flow
  README.md       ← What it does, how to use it
  references/     ← Detailed rules (loaded on demand)
```

Each skill is a multi-phase execution system. Phases have explicit entry conditions, quality gates, and error recovery. The `references/` files contain detailed rules loaded on demand — total skill overhead stays within 10K tokens.

## Build your own

All skills follow [SKILL-SPEC.md](SKILL-SPEC.md) — a universal specification for building tool-agnostic, token-efficient AI coding skills.

See also: [AI Instruction Patterns](references/ai-instruction-patterns.md) — research-backed best practices for writing effective AI agent instructions.

## Companion: dev-rules

Always-on behavioral guardrails that prevent mistakes between skill invocations — scope control, complexity limits, security gates, operational awareness. One file, any AI tool: [dev-rules](https://github.com/sungurerdim/dev-rules).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
