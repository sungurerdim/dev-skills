# ds-commit

Smart git commits with quality gates, atomic grouping, and conventional commit format.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-commit ~/.claude/skills/ds-commit` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-commit`, or ask to commit your changes.

## Flow

1. Pre-checks: git status, branch management, conflict check
2. Quality gates: secret scan, format, lint (changed files only)
3. Analyze diff → smart grouping, amend detection
4. Execute with conventional commit format
5. Verify and summarize

## Features

- **Branch management** — suggests feature branches when on main
- **Amend detection** — auto-amends unpushed commits when appropriate
- **Smart grouping** — splits distinct changes into atomic commits
- **Quality gates** — format + lint before committing
- **Conventional commits** — litmus test for correct type classification
