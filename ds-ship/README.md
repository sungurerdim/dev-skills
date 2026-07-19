# ds-ship

Projects accumulate gaps at every stage — broken promises in docs, outdated stacks, missing launch gates, overengineered abstractions that don't earn their keep. Picking the right ds-* skills in the right order is its own tax.

Classifies the project, plans the skill sequence, delegates each phase, consolidates `ds/audit/findings.md`, writes a single `ds/audit/report.md` (and optional offline HTML flow diagram + heatmap).

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
/ds-ship                  # full orchestration with approval gates
/ds-ship --preview        # classify + plan + gap table, no mutations
/ds-ship --html           # full run + offline visual report
/ds-ship --stage=pre-launch  # override auto-classification
/ds-ship --only=ds-review,ds-compliance
/ds-ship --skip=ds-mobile
/ds-ship --auto           # zero-interaction full cascade — every decision resolved by best judgment;
                          # forwarded to every delegated skill; suited to a remote/unattended caller
/ds-ship --clean-all      # wipe ds/audit/ entirely after a completed pass
```

## Phases

| # | Phase | What it does |
|---|-------|--------------|
| 0 | Assess | Stage classification, doc census, value proposition, promise census, skill-sequence proposal |
| 1 | Ideal vs Current | Delegate to `/ds-benchmark` + merge with promise census |
| 2 | Rule Audit | Delegate per project type: blueprint → review → compliance/mobile → frontend/backend → test → fix |
| 3 | Simplify | Delegate to `/ds-simplify`; every finding Category B |
| 4 | Docs | Compact context-loaded docs; fill gaps via `/ds-docs`; optional ADRs |
| 5 | Launch Gates | devops → deploy → launch → repo (--oss-ready if public) |
| 6 | Report | Write `ds/audit/report.md` (+ `ds/audit/report.html` on --html) |

## Features

- Delegates only — never re-implements another skill's checks
- Two-gate model: Category A autonomous, Category B approval-batched
- Resumable via `ds/audit/ship.json`
- Promise census: every concrete capability claim in docs vs source
- Stack-fitness + external-tooling scopes consumed from `/ds-blueprint`
- `--html` produces self-contained, offline, ASCII-only visual report
- Project-type-aware routing (mobile / web / backend / library / CLI)
- **Milestone-gate triggers** — release-candidate, pre-launch, post-incident (not generic "audit everything")
- **Two-confirmation cascade** — intent + scope must both be approved before any delegated skill runs (`--auto` records both as auto-approved)
- **Target-based delegation routing** — App Store → `/ds-launch`, server/container/k8s → `/ds-deploy`, library → `/ds-repo --oss-ready`. ds-ship never decides between ds-deploy and ds-launch on its own.
