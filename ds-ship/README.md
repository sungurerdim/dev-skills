# ds-ship

Projects accumulate gaps at every stage — broken promises in docs, outdated stacks, missing launch gates, overengineered abstractions that don't earn their keep. Picking the right ds-* skills in the right order is its own tax.

Classifies the project, resolves a mode (harden / release / launch / maintain), plans the skill sequence from the project's signals, delegates each phase, consolidates `ds/audit/findings.md`, writes a single `ds/audit/report.md` (and optional offline HTML flow diagram + heatmap).

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-ship ~/.claude/skills/ds-ship` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

```bash
/ds-ship                  # mode derived from stage + intent, sequence from signals, every decision by best judgment
/ds-ship --mode=harden    # deep audit + fixes, no release/launch legs (also: release · launch · maintain)
/ds-ship --ask            # mode-first menu, sequence confirmation, approval batches
/ds-ship --preview        # classify + mode + plan with signal reasons, no delegations
/ds-ship --html           # full run + offline visual report
/ds-ship --stage=pre-launch  # override auto-classification
/ds-ship --only=ds-review,ds-compliance
/ds-ship --skip=ds-mobile
/ds-ship --refresh-findings  # force a full /ds-blueprint run even when findings are fresh
/ds-ship --clean=all      # wipe ds/audit/ entirely after a completed pass
```

## Phases

| # | Phase | What it does |
|---|-------|--------------|
| 0 | Assess + Mode | Stage classification, signals, mode derivation, doc census, value proposition, sequence with a signal reason per skill |
| 1 | Ideal vs Current (launch) | Delegate to `/ds-benchmark` + merge with the promise census |
| 2 | Rule Audit | Delegate by signal: blueprint (when findings stale) → review → backend/frontend/mobile → compliance → productize (billing) → test → fix |
| 3 | Simplify | Delegate to `/ds-simplify`; every finding Category B |
| 4 | Docs | Compact context-loaded docs; fill gaps via `/ds-docs`; optional ADRs |
| 5 | Release + Launch gates (release/launch) | devops → deploy → release → repo; launch adds ds-launch and --oss-ready |
| 6 | Report | Write `ds/audit/report.md` (+ `ds/audit/report.html` on --html) with every excluded skill and its reason |
| 7 | Handoff offers | PR via `/ds-pr` (needs-human by default), durable tracking via `/ds-issue` |

## Features

- Delegates only — never re-implements another skill's checks
- Two-gate model: Category A autonomous, Category B approval-batched
- Resumable via `ds/audit/ship.json`
- Promise census: every concrete capability claim in docs vs source
- Stack-fitness + external-tooling scopes consumed from `/ds-blueprint`
- `--html` produces self-contained, offline, ASCII-only visual report
- Project-type-aware routing (mobile / web / backend / library / CLI)
- **Milestone-gate triggers** — release-candidate, pre-launch, post-incident (not generic "audit everything")
- **Mode axis** — harden / release / launch / maintain decides which legs exist; a leg outside the mode is `mode-excluded`, never run for completeness
- **Signal-justified delegation** — every delegated skill states the signal that gives it a scope here (`billing=stripe`, `ui=none`); `signal-absent` is the primary exclusion, the stage matrix only orders what remains
- **Measured instruction tokens** — the report states how many instruction tokens the run loaded (`wc -c` of every SKILL.md read ÷ 4)
- **Target-based delegation routing** — App Store → `/ds-launch`, server/container/k8s → `/ds-deploy`, library → `/ds-repo --oss-ready`. ds-ship never decides between ds-deploy and ds-launch on its own.
