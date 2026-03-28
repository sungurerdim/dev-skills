# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-22-blue)]()
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

> scaffold → code → design → test → review → commit → PR → deploy → launch → analytics

| Skill | What it does |
|-------|-------------|
| [ds-init](ds-init) | New projects start with no CI, no tests, no linting. Scaffolds all of it from day one. |
| [ds-fix](ds-fix) | AI skips formatting and ignores lint. Runs all 5 quality passes in the correct order. |
| [ds-test](ds-test) | AI tests mock everything and assert nothing. Generates tests that follow your patterns and pass. |
| [ds-review](ds-review) | Catches what tests miss — security holes, dead code, wrong abstractions. File:line precision. |
| [ds-blueprint](ds-blueprint) | Can't improve what you don't measure. Scores your project across 9 dimensions. |
| [ds-docs](ds-docs) | Docs drift from code the moment they're written. Detects gaps and verifies claims against source. |
| [ds-commit](ds-commit) | AI commits are vague and bundle unrelated changes. Reads the diff, groups logically, writes precisely. |
| [ds-pr](ds-pr) | PRs that list every commit create noise. Describes the net diff, not the journey. |
| [ds-deploy](ds-deploy) | First deploy means bloated images, no health checks, no SSL. Generates production-ready configs. |
| [ds-launch](ds-launch) | ~40% of store submissions fail for preventable errors. Scans your project and flags them. |
| [ds-compliance](ds-compliance) | One missing privacy policy or unpatched XSS means fines or rejection. 80+ rules, file:line precision. |
| [ds-frontend](ds-frontend) | Hardcoded colors, inconsistent spacing, missing focus states. Enforces design system in code. |
| [ds-mobile](ds-mobile) | Permission abuse, missing a11y, hardcoded keys surface during review. 145+ rules catch them first. |
| [ds-devops](ds-devops) | Broken CI, unsigned builds, outdated deps erode release quality. Audits your entire DevOps setup. |
| [ds-repo](ds-repo) | Unprotected branches, stale PRs, no CODEOWNERS — most repos are misconfigured. Audits and fixes. |
| [ds-backend](ds-backend) | AI APIs ship with inconsistent naming and no auth strategy. Designs all three layers correctly. |
| [ds-research](ds-research) | AI hallucinates sources and cites outdated data. Searches, scores reliability, cites everything. |
| [ds-market](ds-market) | Solo devs build great products but can't get noticed. Generates positioning, copy, and growth playbook. |
| [ds-analytics](ds-analytics) | Most apps track everything (privacy risk) or nothing (blind). Designs minimum taxonomy, maximum insight. |
| [ds-cv](ds-cv) | ATS rejects most CVs before a human sees them. Generates ones that pass. |
| [ds-solve](ds-solve) | Complex problems resist single-pass fixes. Plans, tries alternatives, backtracks, re-plans until solved. |
| [ds-tune](ds-tune) | Manual optimization: 8 experiments/day. This skill runs 100+ overnight, keeping only what improves. |

Each skill is self-contained. No dependencies between them. Install one or all.

## Recommended workflow

```
1. /ds-blueprint        Score your project health, generate .ds-findings.md
2. /ds-review --tactical  Fix code issues (uses .ds-findings.md if available)
3. /ds-fix              Format, lint, type-check
4. /ds-test             Generate missing tests, fix failing ones
5. /ds-commit           Commit with quality gates
6. /ds-pr               Create PR with net diff analysis
```

Start with `/ds-blueprint` — it scans your entire codebase and produces a `.ds-findings.md` that other skills consume, so they skip redundant analysis and jump straight to fixes.

For new projects: `/ds-init` → then the workflow above.
For deployment: `/ds-deploy` → `/ds-launch`.
For frontend: `/ds-frontend` → design system audit + fixes.
For stuck/complex problems: `/ds-solve` — adaptive retry with web research.
For audits: `/ds-compliance` or `/ds-mobile`.

## Why these are different

Most AI coding "skills" are static rule snippets (30-100 lines). dev-skills are **orchestrated execution systems**:

- **Multi-phase workflows** with quality gates, mandatory phase enforcement, and error recovery
- **8 AI weaknesses systematically addressed** — hallucination, scope creep, tunnel vision, confidence bias, memory decay, skip tendency, redundancy blindness, injection risk
- **Finding Resolution Completeness (FRC)** — every finding gets a disposition (fixed/skipped/failed), zero silent drops
- **Inter-skill coordination** via `.ds-findings.md` + blueprint profile — share analysis results and project context, avoid duplicate work
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
