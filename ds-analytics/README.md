# ds-analytics

Privacy-first analytics setup — event taxonomy design, funnel definition, metrics, and user insights.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-analytics ~/.claude/skills/ds-analytics` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-analytics`, or ask about analytics, metrics, or event tracking.

## Modes

| Mode | What It Does |
|------|-------------|
| **Design** | Event taxonomy, funnels, metrics definition |
| **Setup** | Analytics tool integration guide |
| **Audit** | Review existing analytics for gaps and privacy issues |

## Features

- Privacy-first: maximum insights with minimum data collection
- Event taxonomy with naming conventions and PII prevention
- AARRR funnel framework (Acquisition → Activation → Retention → Revenue → Referral)
- Tool comparison: Plausible, PostHog, Matomo, Mixpanel, Amplitude, GA4
- Consent mechanism integration guidance
- Zero PII in event properties by design
