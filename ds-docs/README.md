# ds-docs

Documentation drifts from code the moment it's written, decisions evaporate with no paper trail, and AI-harness context files silently bloat past the point they help. This skill detects the gaps, verifies claims against source code, tracks architecture decisions, and keeps harness context files signal-dense.

**Documentation & decision integrity — doc-drift verification, gap generation, ADR tracking, harness-context-file curation.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-docs ~/.claude/skills/ds-docs` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-docs`, or ask to check your documentation.

## Scopes

| Scope | What It Generates |
|-------|------------------|
| readme | Project overview, quick start |
| api | Endpoint/function reference |
| dev | Developer onboarding guide |
| user | End-user guides |
| ops | Deployment, operations |
| support | Error-remediation runbooks, known-error KB, support escalation guide |
| changelog | Version history |
| compliance | Privacy policy, DPIA, breach plan, processor registry |
| adr | Architecture Decision Records, numbered under `docs/adr/` |
| harness | Audit/trim AI-harness context files (CLAUDE.md, AGENTS.md, .cursor/rules/, etc.) |
| refine | Quality improvement for existing docs |
| verify | Verify doc claims against source code |

## Features

- **Gap analysis** — ideal docs by project type vs current state, across 12 scopes
- **Source-verified** — every documented flag/endpoint verified from code
- **ADR tracking** — proposes and maintains numbered decision records, flags drift and stale supersedence
- **Harness-file curation** — cuts code-derivable/generic content from CLAUDE.md/AGENTS.md-class files, enforces per-vendor length budgets, flags secrets
- **Refine mode** — improve scannability, clarity, conciseness of existing docs
- **Verify mode** — cross-reference doc claims against actual source
