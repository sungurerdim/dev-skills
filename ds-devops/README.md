# ds-devops

Broken CI pipelines, unsigned builds, and outdated dependencies silently erode release quality. This skill audits your entire DevOps setup and flags what needs fixing.

**Audit CI/CD pipelines, code signing, and dependency management for any project type. 42 rules across 15 domains.**

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

```bash
/ds-devops               # full scan + fix — best judgment, recorded in the summary
/ds-devops --ask         # full scan with interactive approval
/ds-devops --preview     # dry run — show what would be checked, no scanning or fixes
/ds-devops --scope=ci    # single domain
```

## Scopes

| Scope | What It Checks |
|-------|---------------|
| ci | Pipeline presence, quality gates, workflow lint (actionlint + zizmor), `pull_request_target` misuse, CI/local parity, required checks, caching, monorepo affected-detection, secrets hygiene, runner cost |
| signing | Code signing automation, credential security (mobile/desktop) |
| deps | Dependency policy, outdated detection, compatibility, vulnerability audit |
| release-pipeline | Release automation, version bump workflow, deploy safety gates |
