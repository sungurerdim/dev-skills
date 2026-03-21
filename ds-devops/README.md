# ds-devops

Audit CI/CD pipelines, code signing, and dependency management for any project type. 14 rules across 3 domains.

Works with Flutter, Node.js, Python, Go, Rust, Java/Kotlin, and more.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-devops`, or ask to review your CI/CD setup.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| ci | Pipeline presence, quality gates, CI/local parity, required checks |
| signing | Code signing automation, credential security (mobile/desktop) |
| deps | Dependency policy, outdated detection, compatibility, vulnerability audit |
| deploy | Crash reporting, conventional commits, changelog automation |

## Modes

| Mode | What It Does |
|------|-------------|
| **Full Audit** | Scan all scopes, report findings |
| **Audit & Fix** | Scan, review findings, then fix |
| **Quick Fix** | Scan and auto-fix, minimal review |
