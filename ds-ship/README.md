# ds-ship

Projects accumulate gaps at every stage — broken promises in docs, outdated stacks, missing launch gates, overengineered abstractions that don't earn their keep. Picking the right ds-* skills in the right order is its own tax.

Classifies the project, plans the skill sequence, delegates each phase, consolidates `.audit/findings.md`, writes a single `.audit/report.md` (and optional offline HTML flow diagram + heatmap).

## Install

```bash
cp -r dev-skills/ds-ship ~/.claude/skills/ds-ship
```

## Use

```bash
/ds-ship                  # full orchestration with approval gates
/ds-ship --preview        # classify + plan + gap table, no mutations
/ds-ship --html           # full run + offline visual report
/ds-ship --stage=pre-launch  # override auto-classification
/ds-ship --only=ds-review,ds-compliance
/ds-ship --skip=ds-mobile
/ds-ship --auto           # list B items, skip (needs-approval)
/ds-ship --force-approve  # apply every B item — use after a Preview pass
/ds-ship --clean-all      # wipe .audit/ entirely after a completed pass
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
| 6 | Report | Write `.audit/report.md` (+ `.audit/report.html` on --html) |

## Features

- Delegates only — never re-implements another skill's checks
- Two-gate model: Category A autonomous, Category B approval-batched
- Resumable via `.audit/ship.json`
- Promise census: every concrete capability claim in docs vs source
- Stack-fitness + external-tooling scopes consumed from `/ds-blueprint`
- `--html` produces self-contained, offline, ASCII-only visual report
- Project-type-aware routing (mobile / web / backend / library / CLI)
