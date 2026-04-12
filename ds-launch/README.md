# ds-launch

Store submission, ASO (App Store Optimization), release management, and post-launch monitoring.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-launch ~/.claude/skills/ds-launch` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-launch`, or ask to prepare your app for store submission.

## Modes

| Mode | What It Does |
|------|-------------|
| **Setup** | Store account setup checklists |
| **Listing** | Store metadata, description, keywords, screenshots |
| **Privacy** | Privacy label and data safety declarations |
| **Review** | Pre-review checklist (rejection prevention) |
| **ASO** | Keyword research, search ranking optimization, A/B testing |
| **Release** | Version management, release notes, staged rollout |
| **Post-Launch** | Monitoring and update strategy |

## Features

- Pre-review rejection prevention checklist
- Privacy label generation by scanning actual code
- Staged rollout strategy (1% → 5% → 20% → 50% → 100%)
- Release notes generation from commit history
- Cross-platform support: iOS, Android, Web
- Force-update mechanism guidance
