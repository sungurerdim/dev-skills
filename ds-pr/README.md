# ds-pr

Create pull requests with conventional commit titles for clean release-please changelogs.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-pr`, or ask to create a pull request.

## Flow

1. Validate: git, gh, branch, upstream status
2. History tidy: collapse WIP commits into clean atomic commits
3. Quality gates: format, lint, test (entire project)
4. Analyze net diff → conventional commit type classification
5. Build PR title + body from net diff
6. Create + optional auto-merge setup

## Features

- **History tidy** — collapses WIP commits before publishing
- **Net diff principle** — PR describes final state, not development journey
- **Quality gates** — format + lint + test before creating PR
- **Auto-merge** — squash merge + branch cleanup when CI passes
- **Version annotation** — shows bump effect (feat → minor, fix → patch)
