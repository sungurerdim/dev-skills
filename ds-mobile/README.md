# ds-mobile

Audit your mobile app against 145+ rules across 13 domains, fix violations, and score release readiness.

Works with Flutter, SwiftUI, Kotlin/Compose, and React Native.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

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
| Store Compliance | 20 |
| UX | 26 |
| Visual Design | 24 |
| Accessibility | 12 |
| Architecture | 10 |
| Testing | 6 |
| Performance | 7 |
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
