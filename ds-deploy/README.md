# ds-deploy

Deployment, infrastructure, monitoring, and incident response — from Dockerfile to post-mortem.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-deploy ~/.claude/skills/ds-deploy` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-deploy`, or ask to deploy your project or review infrastructure.

## Modes

| Mode | What It Does |
|------|-------------|
| **Audit** | Review existing Docker/infra setup |
| **Generate** | Create Dockerfile, compose, deploy configs |
| **Checklist** | Pre-production readiness check |
| **Monitor** | Set up logging, alerting, crash reporting |
| **Incident** | Incident response procedure and templates |
| **Cost** | Infrastructure cost analysis and optimization |

## Features

- Dockerfile audit: multi-stage, non-root, optimized layers
- VPS hardening checklist (SSH, firewall, fail2ban)
- SSL/TLS automation (Let's Encrypt, Caddy)
- Zero-downtime deployment strategies
- Monitoring with PII redaction
- Incident response: P1-P4 severity, post-mortem template
- Cost optimization: free tier maximization, right-sizing
