# dev-skills

[![CI](https://github.com/sungurerdim/dev-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/sungurerdim/dev-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-30-blue)]()
[![Tool](https://img.shields.io/badge/works_with-Claude_Code_·_OpenCode_·_Cursor_·_Copilot_·_Windsurf_(Devin_Desktop)_·_Aider-green)]()

Your AI coding assistant will hallucinate an API that doesn't exist, break file B while fixing file A, weaken your tests until they pass, and silently drop fields during data conversion. Most AI "skills" are 50-line rule snippets that can't prevent any of this.

**dev-skills are multi-phase execution systems** — quality gates, error recovery, systematic mitigation of 17 known AI weaknesses — covering the entire software lifecycle from project scaffolding to store launch.

### Proof

| Number | Meaning |
|--------|---------|
| **30 skills** | One per real lifecycle moment — equip, discover, build, improve, document, comply, monetize, track, ship. Each skill owns defined [taxonomy dimensions](SKILL-SPEC.md#appendix-dimension-coverage-map) (A1–D11: product, engineering, trust, operations) with automated coverage tracking in `/ds-ship` reports |
| **110 engineering principles** | Drawn from 24 authoritative sources (12-Factor, SOLID + GRASP, Clean Code, Pragmatic Programmer, Martin Fowler, Google SRE, DORA, OWASP) and encoded as gates — see [`references/software-best-practices.md`](references/software-best-practices.md) |
| **17 AI failure modes** | W1–W11 universal — hallucination, tunnel vision, scope creep, memory decay, confidence bias, skip tendency, redundancy blindness, injection risk, state hygiene, findings-SSOT drift, error-ownership skip. W12–W17 domain-specific — spec-gaming, sycophancy, context rot, subagent-handoff, dependency hallucination, duplication drift. Every skill carries the applicable mitigations (W1–W17) |
| **0 runtime dependencies** | Skills are markdown — they run inside your AI tool, not as services |
| **6 AI tools supported** | Claude Code, OpenCode, Cursor, GitHub Copilot, Windsurf (now Devin Desktop, 2026-06-02), Aider — skills follow the open [Agent Skills spec](https://agentskills.io) (`SKILL.md`), so any host that reads it works |
| **2 namespaces, 1 root** | `ds/audit/` (gitignored, transient state) + `ds/<skill>/` (committed operational tooling) — nothing else leaks to your repo root |

> **Quick start:** `git clone https://github.com/sungurerdim/dev-skills.git && cd dev-skills && ./install.sh`
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

### Equip — set up the machine before the project

| Question | Skill |
|----------|-------|
| "Set up/refresh my AI dev environment — tools current, zero telemetry, safe permissions, MCP budget." | [`/ds-rig`](ds-rig) — pinned installs, proven privacy opt-outs, additive allow/ask/deny profiles, symmetric uninstall |

### Discover — understand before you build

| Question | Skill |
|----------|-------|
| "Has someone else solved this? What does the literature say?" | [`/ds-research`](ds-research) — searches, scores source reliability, cites file:line |
| "What do the best projects in this space look like? Where do we fall short?" | [`/ds-benchmark`](ds-benchmark) — synthesizes the ideal from 5–10 comparables, produces gap table |
| "How healthy is this codebase? What's the lowest-hanging fruit?" | [`/ds-blueprint`](ds-blueprint) — scores 9 dimensions, writes findings every other skill consumes |
| "I have a feature idea — get me an executable, test-gated plan." | [`/ds-pipeline`](ds-pipeline) — conducts the Spec Kit chain with blocking gates; every task ships with a verify command |

### Build — start something new

| Question | Skill |
|----------|-------|
| "Empty repo. Get me to a real project from zero." | [`/ds-init`](ds-init) — scaffold, CI, lint, tests from day one |
| "Design my API + database + auth + data pipeline, end-to-end." | [`/ds-backend`](ds-backend) — four-layer design, no inconsistent naming, no double-processing jobs |
| "I need design tokens, component states, theming, a11y baseline." | [`/ds-frontend`](ds-frontend) — design system audit + generation |
| "Audit my mobile app before submitting to a store." | [`/ds-mobile`](ds-mobile) — 171 rules, 13 domains, release-readiness scoring |

### Improve — fix what's already there

| Question | Skill |
|----------|-------|
| "Run a deep code audit — security, hygiene, architecture, perf." | [`/ds-review`](ds-review) — tactical + strategic + perf + meta-quality (SSOT / DRY / KISS / YAGNI / SoC) scopes, file:line precision |
| "Strip dead code, single-caller helpers, premature abstractions." | [`/ds-simplify`](ds-simplify) — approved deletion, one reversible commit per group |
| "Catch up on dependency upgrades safely." | [`/ds-deps`](ds-deps) — patch/minor automatic + major-with-migration approval |
| "Format, lint, type-check, security-gate — in the right order." | [`/ds-fix`](ds-fix) — five quality passes, no skipping |
| "Make quality automatic — block 'done' until checks pass, no CI." | [`/ds-quality`](ds-quality) — local Stop-hook verify-loop (format→lint→type→test), enforced by mechanism |
| "Tests are missing or asserting nothing. Generate real ones." | [`/ds-test`](ds-test) — patterns matched, mocks rejected, real bugs surfaced |
| "Optimize a measurable metric autonomously — 100 experiments overnight." | [`/ds-tune`](ds-tune) — git ratchet, only improvements survive |
| "Hard problem resists a single-pass fix." | [`/ds-solve`](ds-solve) — plan → try → backtrack → re-plan, with web research |

### Document

| Question | Skill |
|----------|-------|
| "Detect doc drift, fill gaps, verify claims against source, write ADRs." | [`/ds-docs`](ds-docs) — drift detection + generation + Architecture Decision Records |
| "Turn a topic or URLs into a sourced, printable, single-file HTML brief." | [`/ds-brief`](ds-brief) — every datum 2×-confirmed or visibly flagged |

### Comply — privacy & regulatory

| Question | Skill |
|----------|-------|
| "Am I privacy/regulatory compliant? GDPR, KVKK, CCPA, accessibility law?" | [`/ds-compliance`](ds-compliance) — 98 rules, file:line precision |

### Monetize — turn it into a paid product

| Question | Skill |
|----------|-------|
| "Make this a paid SaaS — model, pricing, billing integrity, GTM baseline." | [`/ds-productize`](ds-productize) — cited benchmarks, entitlement/webhook CRITICAL gates, decision-ready plan |

### Track — manage work as GitHub issues

| Question | Skill |
|----------|-------|
| "Turn this note/bug/idea into a real issue — verified, deduped, no dead content." | [`/ds-issue`](ds-issue) — reproduces the symptom against code, sweeps open+closed for duplicates, machine-checkable Done |
| "Which issues are actually done — proven from code — and which are claimed but unproven?" | [`/ds-issue --status`](ds-issue) — code-verified done-audit, read-only |
| "Do issue #N end-to-end and close it with proof." | [`/ds-issue --do #N`](ds-issue) — re-verify root cause → impact-surface map → bounded plan → implement → code-proven close |
| "Work through every open issue and close each with proof." | [`/ds-issue --do --all`](ds-issue) — same flow over the whole open backlog in priority order; confirm each, skip-and-record blockers, per-issue outcome table |

### Ship — get changes out the door

| Question | Skill |
|----------|-------|
| "Too much to perfect before release — cut scope, decide what ships now vs later." | [`/ds-freeze`](ds-freeze) — collaborative ship/defer-hidden/defer-backlog triage, GitHub-issue-backed backlog, implements only the kept set, syncs docs |
| "Group my diff into atomic, conventional commits." | [`/ds-commit`](ds-commit) — reads diff, groups logically, writes precise messages |
| "Write a PR description that reflects the net diff, not the journey." | [`/ds-pr`](ds-pr) — net-diff analysis, no commit-by-commit narrative |
| "Audit my CI/CD — broken steps, unsigned builds, dep audits." | [`/ds-devops`](ds-devops) — pipeline integrity, signing, caching |
| "First production deploy — container, TLS, health checks, runbook." | [`/ds-deploy`](ds-deploy) — generates production-ready configs + monitoring |
| "App store / web release / library publish — what gates do I need?" | [`/ds-launch`](ds-launch) — store metadata, perf budgets, release prep |
| "Repo settings, CODEOWNERS, branch protection, OSS readiness." | [`/ds-repo`](ds-repo) — full repo metadata audit |

## Recommended sequences

**Interactive version:** [Production-Readiness Guide](docs/guide.html) — pick project type + stage, get the exact skill sequence with what each does, what you gain, and which gap it closes. Self-contained HTML, works offline.

| Goal | Order |
|------|-------|
| **Resume any project** | `/ds-ship` (lets it pick the order for you) |
| **New project** | `ds-init` → `ds-quality` → `ds-blueprint` → `ds-test` → `ds-commit` |
| **Existing project hygiene** | `ds-blueprint` → `ds-review --tactical` → `ds-simplify` → `ds-fix` → `ds-test` → `ds-commit` |
| **Pre-launch** | `ds-devops` → `ds-deploy` → `ds-launch` → `ds-repo` |
| **Pre-launch, scope too big** | `ds-freeze` → `ds-devops` → `ds-deploy` → `ds-launch` → `ds-repo` |
| **Paid product / SaaS** | `ds-productize` → `ds-devops` → `ds-deploy` → `ds-launch` → `ds-repo` |
| **Solo-dev daily loop** | `ds-fix` → `ds-test` → `ds-commit` → `ds-pr` |
| **Stuck on a hard bug** | `ds-solve` |
| **Idea → executable plan** | `ds-pipeline` → hand `specs/{feature}/tasks.md` to your executor |
| **Public OSS release** | `ds-docs` → `ds-repo --oss-ready` → `ds-launch` |

`/ds-blueprint` is the recommended first run on any unfamiliar codebase — it writes `ds/audit/findings.md` that every later skill reads to skip redundant scans.

## Shared artifact namespace — `ds/`

Least footprint by default: **most skills write nothing.** A skill creates a file only when it genuinely needs one — git/GitHub-backed skills (ds-commit, ds-pr, ds-issue) keep no local state at all. Anything that *is* produced lives under one top-level directory:

```
<repo-root>/
  ds/
    audit/                ← gitignored, transient (deleted on success)
      findings.md         ← shared findings across skills
      report.md           ← ds-ship consolidated report
      report.html         ← optional, ds-ship --html
      <skill>.json        ← state ONLY for long autonomous skills (ds-tune, ds-solve, ds-ship, ds-blueprint)
    <skill>/              ← committed — genuine user deliverables only (scripts/configs/outputs the user keeps), never logs
      ...                 ← e.g. ds/tune/, ds/mobile/, ds/launch/
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
- **Trigger Discipline** — every skill ships an INVOKE / DON'T INVOKE table; unscoped verbs (`improve`, `fix`, `audit`) alone are not valid triggers
- **All-Affordance Rule** — every menu (scope, fix, approve, alternative path) offers an "all" option; CRITICAL findings + destructive actions still require per-item confirmation
- **Inter-skill coordination** via `ds/audit/findings.md` + blueprint profile — share analysis, avoid duplicate work
- **Token-efficient** — 10K token budget per skill, references loaded on demand
- **Tool-agnostic** — works with any AI tool that accepts markdown instructions

## Install

**Claude Code — one command (install, update, verify):**

```bash
git clone https://github.com/sungurerdim/dev-skills.git && cd dev-skills
./install.sh                                # all 30 skills + shared agent -> ~/.claude
./install.sh --skills ds-review,ds-commit  # or only the ones you want
./install.sh --project /path/to/other-repo  # install into that repo's .claude instead of ~/.claude
./install.sh --check                        # later: installed copy in sync with the repo?
./install.sh --uninstall                    # remove installed dev-skills content
```

The installer copies **only runtime files** (skill dirs + agents) — spec and docs never enter your context path. Re-running syncs: files removed from a skill in the repo are removed from the installed copy too. Update = `git pull && ./install.sh`.

**OpenCode — nothing extra:** OpenCode reads `.claude/skills/` directly, so `./install.sh` covers it too.

**Other tools — copy any skill folder manually:**

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code / OpenCode** | `./install.sh` (both read `~/.claude/skills/`) |
| **Any Agent Skills host** | `./install.sh --target <that host's skills dir>` — same sync/check/uninstall flow, skills only |
| **Cursor** | `./install.sh --target` your build's Agent Skills dir if it reads them; otherwise reference `SKILL.md` on demand. Do **not** use legacy `.cursorrules` — it is silently ignored in Agent mode |
| **GitHub Copilot** | `./install.sh --target` where your Copilot build reads skills, or add a path-scoped pointer in `.github/instructions/` — never paste full SKILL.md into `copilot-instructions.md` |
| **Windsurf / Devin Desktop** | Reference `SKILL.md` from a `.windsurf/rules/` file (still read after the June 2026 Devin Desktop rebrand; newer builds prefer `.devin/rules/`) |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

> **Why "reference", not "paste":** a SKILL.md is ~4–9K tokens. Pasting it into an always-on rules file loads it on every request and measurably degrades instruction-following as rules accumulate ([IFScale](https://arxiv.org/abs/2507.11538)); skills are designed to load only when invoked. See [docs/methodology/cross-host-program.md](docs/methodology/cross-host-program.md) for the research and the per-host plan.

Install one skill, several, or all 28 — they are independent.

## Host support

All 30 skills are capability-abstracted markdown following the open [Agent Skills spec](https://agentskills.io) — same instructions, any of the 6 hosts (and any other host that reads the spec). The one exception is `ds-quality`, whose enforcement mechanism differs by host because each host exposes a different hook point: stop-time on Claude Code, edit-time on Aider, commit-time via git pre-commit elsewhere. See [`ds-quality/README.md`](ds-quality/README.md) for the host matrix, and [docs/methodology/cross-host-program.md](docs/methodology/cross-host-program.md) for the research-backed cross-host roadmap (v5).

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

## Versioning

Releases use semantic versioning starting at **v1.0.0** (2026-07-15) — the point where the skill set reached release maturity. The `v2`–`v5` labels in older docs and commit messages are **spec-generation names** (internal design-doc lineage: v2 2026-05 → v5 2026-07-15), not release versions; they predate the release line and stay as historical labels.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Community standards: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Report a vulnerability: [SECURITY.md](SECURITY.md).

## License

MIT
