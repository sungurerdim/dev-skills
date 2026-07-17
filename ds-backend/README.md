# ds-backend

AI-generated APIs ship with inconsistent naming, missing pagination, no auth strategy, schemas that don't survive first migration, and data pipelines that double-process on retry. Skill designs all four layers correctly from start.

**API design, database schema review, authentication architecture, and data-pipeline audit — audit, design, and spec generation.**

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
| **Data Pipeline** | Ingest validation, idempotent jobs, quality gates, retention, backfill safety, observability |

## Features

- Four backend domains in one skill (API + DB + Auth + Data Pipeline)
- OpenAPI 3.1+ spec generation (3.2-aware — QUERY method, device-flow, streaming payloads)
- Migration safety checks (no silent data loss)
- OWASP API Top 10 security checks
- Privacy-first: flags PII without encryption, excessive data exposure
