# ds-deps

Dormant projects rot dependencies. Security advisories pile up, minors become majors, majors become migration gauntlets. Manual upgrade is slow; `npm update` without tests breaks production.

Classifies every dep as safe-patch / safe-minor / review-major / removal, applies safe groups autonomously with a test gate, commits one group at a time, surfaces majors with migration notes for approval.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-deps ~/.claude/skills/ds-deps` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

```bash
/ds-deps                  # full classify + execute with approval
/ds-deps --preview        # classify + security scan + report, no writes
/ds-deps --auto           # zero-interaction — safe groups + majors resolved by best judgment
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

- **Release-age cooldown (7d default)** — versions published <7 days ago held out of safe groups (worm-window quarantine); security fixes override
- **Provenance signal** — npm `audit signatures` / PyPI PEP 740 attestation check; missing/changed publisher identity promotes to review-major
- **Lockfile-diff integrity gate** — resolved-URL host changes or integrity-hash removals revert the group as CRITICAL

- Every upgrade has a changelog URL and breaking-change summary
- Safe groups applied autonomously with test gate + one commit per group
- Majors always approval-gated — no surprise breakage
- Security advisories elevated to front of the queue
- Removal candidates flagged (0 source references)
- Monorepo workspace-aware
- State-exempt — per-group commits are the resume checkpoints
