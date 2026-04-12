# ds-repo

Repository structure, settings, and team configuration — audit and setup. 6 scopes.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-repo ~/.claude/skills/ds-repo` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-repo`, or ask to audit your repo settings.

## Scopes

| Scope | What It Checks |
|-------|---------------|
| settings | Squash merge, delete-on-merge, auto-merge, PR format |
| protection | Branch protection rules, required reviews, status checks |
| hygiene | Stale branches, merged branch cleanup |
| metadata | Description, topics, license, homepage, badges, social preview |
| team | CODEOWNERS, contributor guidelines |
| structure | .gitignore, directory conventions |

## Modes

| Mode | What It Does |
|------|-------------|
| **Full Audit** | Scan all scopes, report findings |
| **Audit & Fix** | Scan and apply fixes |
| **Scoped** | Pick specific areas to audit |

