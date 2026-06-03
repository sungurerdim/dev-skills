# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-26-blue)]()
[![Tool](https://img.shields.io/badge/works_with-Claude_Code_·_Cursor_·_Copilot_·_Windsurf_·_Aider-green)]()

Your AI coding assistant will hallucinate an API that doesn't exist, break file B while fixing file A, weaken your tests until they pass, and silently drop fields during data conversion. Most AI "skills" are 50-line rule snippets that can't prevent any of this.

**dev-skills are multi-phase execution systems** — quality gates, error recovery, systematic mitigation of 17 known AI weaknesses — covering the entire software lifecycle from project scaffolding to store launch.

### Proof

| Number | Meaning |
|--------|---------|
| **26 skills** | One per real lifecycle moment — discover, build, improve, document, audit, ship |
| **110 engineering principles** | Drawn from 24 authoritative sources (12-Factor, SOLID + GRASP, Clean Code, Pragmatic Programmer, Martin Fowler, Google SRE, DORA, OWASP) and encoded as gates — see [`references/software-best-practices.md`](references/software-best-practices.md) |
| **17 AI failure modes** | W1–W11 universal — hallucination, tunnel vision, scope creep, memory decay, confidence bias, skip tendency, redundancy blindness, injection risk, state hygiene, findings-SSOT drift, error-ownership skip. W12–W17 domain-specific — spec-gaming, sycophancy, context rot, subagent-handoff, dependency hallucination, duplication drift. Every skill carries the applicable mitigations (W1–W17) |
| **0 runtime dependencies** | Skills are markdown — they run inside your AI tool, not as services |
| **5 AI tools supported** | Claude Code, Cursor, GitHub Copilot, Windsurf, Aider — same skill, every host |
| **2 namespaces, 1 root** | `ds/audit/` (gitignored, transient state) + `ds/<skill>/` (committed operational tooling) — nothing else leaks to your repo root |

> **Quick start:** `git clone https://github.com/sungurerdim/dev-skills.git /tmp/ds && cp -r /tmp/ds/ds-review ~/.claude/skills/ds-review && rm -rf /tmp/ds`
> Then run `/ds-review` in Claude Code (or copy into your tool of choice — see [Install](#install)).

## What we believe

- **Every dependency is a future breaking change.** Fewer deps = fewer risks, fewer breakages.
- **Collect nothing you don't need.** Privacy-by-design, data minimization.
- **If a human is doing it repeatedly, it should be automated.**
- **Every decision minimizes YOUR legal exposure.** Not the vendor's.
- **One developer + AI should ship what a team of five ships.**

## When to reach for which skill

Each row picks one skill for one moment. Pick by the question, not by the noun.

### One skill that runs all the others — `/ds-ship`

| When you don't know where to start | Use |
|-----------------------------------|-----|
| Idea, scaffold, half-built, feature-complete-but-unlaunched, or dormant project | [`/ds-ship`](ds-ship) — classifies the stage, plans the skill sequence, delegates each phase, consolidates one report. **The fastest path through the whole catalog.** |

### Discover — understand before you build

| Question | Skill |
|----------|-------|
| "Has someone else solved this? What does the literature say?" | [`/ds-research`](ds-research) — searches, scores source reliability, cites file:line |
| "What do the best projects in this space look like? Where do we fall short?" | [`/ds-benchmark`](ds-benchmark) — synthesizes the ideal from 5–10 comparables, produces gap table |
| "How healthy is this codebase? What's the lowest-hanging fruit?" | [`/ds-blueprint`](ds-blueprint) — scores 9 dimensions, writes findings every other skill consumes |

### Build — start something new

| Question | Skill |
|----------|-------|
| "Empty repo. Get me to a real project from zero." | [`/ds-init`](ds-init) — scaffold, CI, lint, tests from day one |
| "Design my API + database + auth, end-to-end." | [`/ds-backend`](ds-backend) — three-layer design, no inconsistent naming |
| "I need design tokens, component states, theming, a11y baseline." | [`/ds-frontend`](ds-frontend) — design system audit + generation |
| "Audit my mobile app before submitting to a store." | [`/ds-mobile`](ds-mobile) — 145+ rules, 13 domains, release-readiness scoring |
| "Build me a CV/portfolio site that gets past ATS." | [`/ds-cv`](ds-cv) — single-page HTML + GitHub Pages deploy |

### Improve — fix what's already there

| Question | Skill |
|----------|-------|
| "Run a deep code audit — security, hygiene, architecture, perf." | [`/ds-review`](ds-review) — tactical + strategic + perf + meta-quality (SSOT / DRY / KISS / YAGNI / SoC) scopes, file:line precision |
| "Strip dead code, single-caller helpers, premature abstractions." | [`/ds-simplify`](ds-simplify) — approved deletion, one reversible commit per group |
| "Catch up on dependency upgrades safely." | [`/ds-deps`](ds-deps) — patch/minor automatic + major-with-migration approval |
| "Format, lint, type-check, security-gate — in the right order." | [`/ds-fix`](ds-fix) — five quality passes, no skipping |
| "Tests are missing or asserting nothing. Generate real ones." | [`/ds-test`](ds-test) — patterns matched, mocks rejected, real bugs surfaced |
| "Optimize a measurable metric autonomously — 100 experiments overnight." | [`/ds-tune`](ds-tune) — git ratchet, only improvements survive |
| "Hard problem resists a single-pass fix." | [`/ds-solve`](ds-solve) — plan → try → backtrack → re-plan, with web research |

### Document

| Question | Skill |
|----------|-------|
| "Detect doc drift, fill gaps, verify claims against source, write ADRs." | [`/ds-docs`](ds-docs) — drift detection + generation + Architecture Decision Records |

### Audit & decide

| Question | Skill |
|----------|-------|
| "Am I privacy/regulatory compliant? GDPR, KVKK, CCPA, accessibility law?" | [`/ds-compliance`](ds-compliance) — 80+ rules, file:line precision |
| "Design event taxonomy that's privacy-respecting and actually useful." | [`/ds-analytics`](ds-analytics) — minimum-collection schema, PII scan |
| "I have a product but no positioning, no copy, no growth plan." | [`/ds-market`](ds-market) — marketing strategy + draft copy |

### Ship — get changes out the door

| Question | Skill |
|----------|-------|
| "Group my diff into atomic, conventional commits." | [`/ds-commit`](ds-commit) — reads diff, groups logically, writes precise messages |
| "Write a PR description that reflects the net diff, not the journey." | [`/ds-pr`](ds-pr) — net-diff analysis, no commit-by-commit narrative |
| "Audit my CI/CD — broken steps, unsigned builds, dep audits." | [`/ds-devops`](ds-devops) — pipeline integrity, signing, caching |
| "First production deploy — container, TLS, health checks, runbook." | [`/ds-deploy`](ds-deploy) — generates production-ready configs + monitoring |
| "App store / web release / library publish — what gates do I need?" | [`/ds-launch`](ds-launch) — store metadata, perf budgets, release prep |
| "Repo settings, CODEOWNERS, branch protection, OSS readiness." | [`/ds-repo`](ds-repo) — full repo metadata audit |

## Recommended sequences

| Goal | Order |
|------|-------|
| **Resume any project** | `/ds-ship` (lets it pick the order for you) |
| **New project** | `ds-init` → `ds-blueprint` → `ds-test` → `ds-commit` |
| **Existing project hygiene** | `ds-blueprint` → `ds-review --tactical` → `ds-simplify` → `ds-fix` → `ds-test` → `ds-commit` |
| **Pre-launch** | `ds-devops` → `ds-deploy` → `ds-launch` → `ds-repo` |
| **Solo-dev daily loop** | `ds-fix` → `ds-test` → `ds-commit` → `ds-pr` |
| **Stuck on a hard bug** | `ds-solve` |
| **Public OSS release** | `ds-docs` → `ds-repo --oss-ready` → `ds-launch` |

`/ds-blueprint` is the recommended first run on any unfamiliar codebase — it writes `ds/audit/findings.md` that every later skill reads to skip redundant scans.

## Shared artifact namespace — `ds/`

Everything dev-skills produces lives under one top-level directory:

```
<repo-root>/
  ds/
    audit/                ← gitignored, transient (deleted on success)
      findings.md         ← shared findings across skills
      report.md           ← ds-ship consolidated report
      report.html         ← optional, ds-ship --html
      <skill>.json        ← per-skill state for resumable skills
    <skill>/              ← committed, user-facing operational tooling
      ...                 ← scripts, configs, audit logs (only skills that need them — e.g. ds/tune/, ds/mobile/, ds/launch/, ds/cv/)
  .gitignore              ← contains the line `ds/audit/`
```

Add to `.gitignore` once: `ds/audit/`. Nothing leaks to repo root, no per-skill dotfiles, no append-only history files. See [SKILL-SPEC §10.1](SKILL-SPEC.md#101-artifact-discipline) for the full contract.

## Why these are different

Most AI "skills" are static 30–100 line rule snippets. dev-skills are **orchestrated execution systems**:

- **Multi-phase workflows** with explicit gates, mandatory-phase enforcement, error recovery
- **17 AI weaknesses systematically addressed** — W1–W11 universal (hallucination, scope creep, tunnel vision, confidence bias, memory decay, skip tendency, redundancy blindness, injection risk, state hygiene, findings-SSOT drift, error-ownership skip) + W12–W17 domain-specific (spec-gaming, sycophancy, context rot, subagent-handoff, dependency hallucination, duplication drift)
- **Finding Resolution Completeness (FRC)** — every finding gets a disposition (fixed/skipped/failed), zero silent drops
- **Error Ownership Gate (W11)** — detected errors get a concrete disposition; "pre-existing" / "out of scope" / "not my change" are never valid skip reasons
- **Findings-SSOT Gate (W10)** — downstream skills defer to fresh `ds/audit/findings.md`, never re-detect what blueprint already covered
- **Trigger Discipline** — every skill ships a ÇAĞIRIR / ÇAĞIRMAZ table; unscoped verbs (`improve`, `fix`, `audit`) alone are not valid triggers
- **All-Affordance Rule** — every menu (scope, fix, approve, alternative path) offers an "all" option; CRITICAL findings + destructive actions still require per-item confirmation
- **Inter-skill coordination** via `ds/audit/findings.md` + blueprint profile — share analysis, avoid duplicate work
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

Install one skill, several, or all 26 — they are independent.

## How skills work

```
skill-name/
  SKILL.md        ← Instructions and execution flow (≤500 lines)
  README.md       ← What it does, how to use it (≤80 lines)
  references/     ← Detailed rules, loaded on demand
```

Each skill is a multi-phase execution system. Phases have explicit entry conditions, quality gates, and error recovery. References are loaded on demand — total active skill overhead stays within 10K tokens.

## Build your own

All skills follow [SKILL-SPEC.md](SKILL-SPEC.md) — a universal specification for building tool-agnostic, token-efficient AI coding skills.

See also: [AI Instruction Patterns](references/ai-instruction-patterns.md) — research-backed best practices for writing effective AI agent instructions.

## Companion: dev-rules

Always-on behavioral guardrails that prevent mistakes between skill invocations — scope control, complexity limits, security gates. One file, any AI tool: [dev-rules](https://github.com/sungurerdim/dev-rules).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
