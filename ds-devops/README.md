# ds-devops

Audit CI/CD pipelines, code signing, and dependency management for any project type. 14 rules across 3 domains.

Works with Flutter, Node.js, Python, Go, Rust, Java/Kotlin, and more.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-devops ~/.claude/skills/ds-devops` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-devops`, or ask to review your CI/CD setup.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| ci | Pipeline presence, quality gates, CI/local parity, required checks |
| signing | Code signing automation, credential security (mobile/desktop) |
| deps | Dependency policy, outdated detection, compatibility, vulnerability audit |
| release-pipeline | Release automation, version bump workflow |

## Modes

| Mode | What It Does |
|------|-------------|
| **Full Audit** | Scan all scopes, report findings |
| **Audit & Fix** | Scan, review findings, then fix |
| **Quick Fix** | Scan and auto-fix, minimal review |
