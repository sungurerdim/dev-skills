# ds-pr

PR descriptions that list every commit instead of net change create noise, confuse reviewers, and break changelogs. This skill describes what the diff actually shows.

**Prepare pull requests with conventional commit titles for clean release-please changelogs.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-pr ~/.claude/skills/ds-pr` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-pr`, or ask to open a pull request.

## Flow

1. Validate: git, gh, branch, upstream status
2. History tidy: collapse WIP commits into clean atomic commits
3. Quality gates: format, lint, test (PR's changed files only)
4. Analyze net diff → conventional commit type classification
5. Review the prepared title + body + version annotation
6. Push and Create — each recorded `needs-human` by default, confirmed under `--ask`

## Features

- **History tidy** — collapses WIP commits before publishing
- **Net diff principle** — PR describes final state, not development journey
- **Quality gates** — format + lint + test on changed files before preparing the PR
- **Push and PR-create are needs-human by default** — publishing is never silent; `--ask` confirms and runs both
- **Version annotation** — shows bump effect (feat → minor, fix → patch)
