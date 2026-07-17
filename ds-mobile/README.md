# ds-mobile

Mobile apps ship with permission abuse, missing accessibility, hardcoded keys, and store-blocking issues that only surface during review. This skill catches them across 174 rules before you submit.

**Audit your mobile app against 174 rules across 13 domains, fix violations, and score release readiness.**

Works with Flutter, SwiftUI, Kotlin/Compose, and React Native.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-mobile ~/.claude/skills/ds-mobile` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-mobile`, or ask to review your mobile app.

## Modes

| Mode | What It Does |
|------|-------------|
| **Audit Only** | Scan all domains, report only |
| **Audit & Fix** | Scan, review findings, then fix |
| **Quick Fix** | Scan and auto-fix, minimal review |
| **Release Ready** | 100-point scoring, manual gates, live policy fetch, store launch kit |
| **Custom** | Pick specific domains and mode |

## What It Checks

| Domain | Rules |
|--------|-------|
| Security | 11 |
| Privacy | 5 |
| Regulatory (GDPR, KVKK, CCPA...) | 13 |
| Store Compliance | 21 |
| UX | 27 |
| Visual Design | 25 |
| Accessibility | 12 |
| Architecture | 10 |
| Testing | 6 |
| Performance | 9 |
| Network | 7 |
| Internationalization | 4 |
| Release Readiness | 21 |

## Release Ready Mode

Answers: **"Can I ship this to the App Store / Play Store right now?"**

- Fetches live store requirements on every run
- Scores across 7 dimensions (100 points, dynamic weighting)
- Runs 15+ manual verification gates
- Generates persistent reports with diff against previous runs
- Store Launch Kit — metadata templates for App Store Connect + Play Console
