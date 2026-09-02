# ds-mobile

Mobile apps ship with permission abuse, missing accessibility, hardcoded keys, and store-blocking issues that only surface during review. This skill catches them across 181 rules before you submit.

**Audit your mobile app against 181 rules across 13 domains, fix violations, and score release readiness.**

Works with Flutter, SwiftUI, Kotlin/Compose, React Native, and Capacitor/Cordova hybrid shells.

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

## Run Types

| Run | What It Does |
|-----|-------------|
| Default | Scan, review findings, then fix — all domains |
| `--preview` | Scan all domains, report only |
| `--release-ready` | 100-point scoring, manual gates, live policy fetch, store launch kit |
| Custom (`--ask`) | Pick specific domains and run type |

## What It Checks

| Domain | Rules |
|--------|-------|
| Security | 14 |
| Privacy | 5 |
| Regulatory (GDPR, KVKK, CCPA...) | 13 |
| Store Compliance | 22 |
| UX | 27 |
| Visual Design | 24 |
| Accessibility | 12 |
| Architecture | 12 |
| Testing | 6 |
| Performance | 10 |
| Network | 7 |
| Internationalization | 5 |
| Release Readiness | 20 |

13 domains, 177 rules selectable via `--scope=`, plus 4 conditional Hybrid & WebView Bridge rules that activate only on Capacitor/Cordova projects (181 total).

## Release Readiness (`--release-ready`)

Answers: **"Can I ship this to the App Store / Play Store right now?"**

- Fetches live store requirements on every run
- Scores across 7 dimensions (100 points, dynamic weighting)
- Runs 15+ manual verification gates
- Generates persistent reports with diff against previous runs
- Store Launch Kit — metadata templates for App Store Connect + Play Console
