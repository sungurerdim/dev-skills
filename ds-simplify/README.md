# ds-simplify

Codebases grow dead exports, single-caller helpers, fallback branches, orphan modules, and abstractions built on 2–3 usages. Every one earns context without earning its keep.

Detects each class with file:line evidence, presents a delete-or-keep table, applies only what you approve — each approved batch is one reversible git commit.

## Install

```bash
cp -r dev-skills/ds-simplify ~/.claude/skills/ds-simplify
```

## Use

```bash
/ds-simplify                  # full scan, interactive approval
/ds-simplify --preview        # scan + report, no approval, no deletion
/ds-simplify --scope=dead-code
/ds-simplify --auto           # list findings, skip every deletion (needs-approval)
/ds-simplify --force-approve  # apply every finding — dangerous, use sparingly
```

## Scopes

| Scope | Detects |
|-------|---------|
| dead-code | Exports with 0 references |
| single-caller | Exports referenced exactly once |
| fallback | Backward-compat branches with no live hit |
| dead-branch | Feature flags with only one path ever taken |
| premature-abstraction | Generics / base classes / wrappers on ≤3 usages |
| quarantine | `// removed` / `// legacy` / `// deprecated` / `_unused` markers |
| test-realism | `a@b.c`, `$1`, length-1 "collections" |
| io-drift | Function signature ≠ caller signature |
| ssot-violation | Same constant / URL / regex duplicated |
| orphan | Modules / assets with zero inbound references |

## Features

- Every finding carries file:line + reference count evidence
- One batched approval block — no per-file prompts
- Each approved batch is one reversible commit (rollback = `git revert`)
- Post-delete test gate catches regressions before commit
- Resumable via `.audit/simplify.json`
- LSP-first, grep fallback
