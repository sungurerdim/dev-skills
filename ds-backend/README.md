# ds-backend

API design, database schema review, and authentication architecture — audit, design, and spec generation.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-backend ~/.claude/skills/ds-backend` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-backend`, or ask to review your API, database schema, or auth flow.

## Modes

| Mode | What It Does |
|------|-------------|
| **Audit** | Review existing API/DB/auth for issues |
| **Design** | Design new endpoints, schema, or auth flow |
| **Spec** | Generate OpenAPI spec, migration files, auth docs |
| **Migrate** | Generate or review database migrations |

## Scopes

| Scope | What It Covers |
|-------|---------------|
| **API** | REST/GraphQL design, naming, status codes, pagination, OWASP API Top 10 |
| **Database** | Schema design, indexing, migrations, query optimization, PII handling |
| **Auth** | OAuth2/OIDC flows, JWT/session management, RBAC, social login, MFA |

## Features

- Three backend domains in one skill (API + DB + Auth)
- OpenAPI 3.0+ spec generation
- Migration safety checks (no silent data loss)
- OWASP API Top 10 security checks
- Privacy-first: flags PII without encryption, excessive data exposure
