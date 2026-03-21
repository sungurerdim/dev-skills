# ds-repo

Repository structure, settings, and team configuration — audit and setup. 6 scopes.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

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

CI/CD and dependency management are handled by `/ds-devops`.
