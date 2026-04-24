# ds-deps

Dormant projects rot dependencies. Security advisories pile up, minors become majors, majors become migration gauntlets. Manual upgrade is slow; `npm update` without tests breaks production.

Classifies every dep as safe-patch / safe-minor / review-major / removal, applies safe groups autonomously with a test gate, commits one group at a time, surfaces majors with migration notes for approval.

## Install

```bash
cp -r dev-skills/ds-deps ~/.claude/skills/ds-deps
```

## Use

```bash
/ds-deps                  # full classify + execute with approval
/ds-deps --preview        # classify only, no upgrade
/ds-deps --dry-run        # classify + security scan, no writes
/ds-deps --auto           # apply safe groups, skip majors (needs-approval)
/ds-deps --force-approve  # apply every classified upgrade including majors
/ds-deps --scope=security # security advisories only
```

## Supports

| Stack | Tool |
|-------|------|
| npm / pnpm / yarn | `npm outdated`, `npm audit` |
| go | `go list -u`, native audit |
| python | `pip list --outdated` or `poetry show --outdated`, `pip-audit` |
| rust | `cargo outdated`, `cargo audit` |
| ruby | `bundle outdated`, `bundler-audit` |
| dart | `dart pub outdated`, `pub audit` |
| php | `composer outdated`, `composer audit` |

## Features

- Every upgrade has a changelog URL and breaking-change summary
- Safe groups applied autonomously with test gate + one commit per group
- Majors always approval-gated — no surprise breakage
- Security advisories elevated to front of the queue
- Removal candidates flagged (0 source references)
- Monorepo workspace-aware
- Resumable via `.audit/deps.json`
