# ds-simplify

Codebases grow dead exports, single-caller helpers, fallback branches, orphan modules, and abstractions built on 2–3 usages. Every one earns context without earning its keep.

Detects each class with file:line evidence, presents a delete-or-keep table, applies only what you approve — each approved batch is one reversible git commit.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-simplify ~/.claude/skills/ds-simplify` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

```bash
/ds-simplify                  # full scan, every finding resolved by best judgment
/ds-simplify --ask            # full scan, interactive approval at every batch
/ds-simplify --preview        # scan + report, no approval, no deletion
/ds-simplify --scope=dead-code
```

## Scopes

| Scope | Detects |
|-------|---------|
| dead-code | Exports with 0 references |
| single-caller | Exports referenced exactly once |
| fallback | Backward-compat branches with no live hit |
| dead-branch | Feature flags whose value is constant across every config source — untaken branch is dead |
| premature-abstraction | Generics / base classes / wrappers on ≤3 usages |
| quarantine | `// removed` / `// legacy` / `// deprecated` / `_unused` markers |
| test-realism | Delegated to `/ds-test` when present; gap-noted otherwise |
| io-drift | Function signature ≠ caller signature |
| ssot-violation | Same constant / URL / regex duplicated |
| orphan | Modules / assets with zero inbound references |

## Features

- Every finding carries file:line + reference count evidence
- One batched approval block — no per-file prompts
- Each approved batch is one reversible commit (rollback = `git revert`)
- Post-delete test gate catches regressions before commit
- State-exempt — one reversible commit per approved batch is the durable record
- LSP-first, grep fallback
