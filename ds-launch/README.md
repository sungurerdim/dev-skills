# ds-launch

~40% of iOS submissions get delayed or rejected for preventable errors. This skill scans your project and flags them before you submit.

**Store submission, ASO (App Store Optimization), release management, and post-launch monitoring.**

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
| **Review** | Pre-review active-detection scan (rejection prevention, jurisdiction-aware IAP/external-payment check) |
| **Submission-Notes** | Proactive App Review notes generator (eliminates 24-48h reviewer round-trips) |
| **ASO** | Keyword research, search ranking optimization, A/B testing |
| **SEO** | Web discoverability: meta/OG, sitemap, robots, canonicals, JSON-LD; llms.txt honestly labeled speculative |
| **Email** | Deliverability: SPF/DKIM/DMARC + alignment, RFC 8058 one-click unsubscribe, spam-rate posture |
| **Release** | Version management, release notes, staged rollout |
| **Post-Launch** | Monitoring and update strategy |
| **Perf-Budget** | Formal perf budget (LCP/INP/p99/bundle) + CI enforcement wiring |

## Features

- Pre-review rejection prevention as an active codebase scan (file:line evidence), incl. post-Epic jurisdiction-split external-payment rules, 4.3(b) clone-category risk, 4.5.3 Live Activities misuse
- Privacy label generation by scanning actual code
- Email deliverability gate before launch sends (bulk-sender authentication + one-click unsubscribe + 0.3%/0.08% spam-rate thresholds)
- Staged rollout strategy (1% → 5% → 20% → 50% → 100%)
- Release notes generation from commit history
- Cross-platform support: iOS, Android, Web
- Force-update mechanism guidance
