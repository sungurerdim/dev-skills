# ds-issue

AI assistants file issues from memory — unverified `file:line` anchors, duplicates of issues that already exist, verbose dead content, and "done" claims nobody proved. This skill makes the tracker trustworthy: nothing is created until the symptom is reproduced against current code and checked for duplicates, and "what's done" is answered from the codebase.

**GitHub-Issues-centric issue manager — verified intake, dedup sweep, code-verified status.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-issue ~/.claude/skills/ds-issue` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

Requires the `gh` CLI, authenticated (`gh auth login`).

## Use

| Command | What it does |
|---------|--------------|
| `/ds-issue <raw note>` | Intake: turn a raw note/bug/idea into a verified, deduped, confirmed issue |
| `/ds-issue --sweep` | Sweep the whole tracker for duplicate/overlap/redundant/obsolete clusters |
| `/ds-issue --status` | Code-verified done-audit (read-only) — what's done, claimed-but-unproven, in-progress, blocked |

## Project adapter (optional)

Drop `.dev-skills/issue-ops.json` in the repo to sharpen the skill with your repo slug, doctrine doc paths, label taxonomy, audit→issue-type map, done-signal command, and hazard checklist. Absent → the skill auto-detects repo, done-signal, and criteria. See `references/adapter.md`.

## Features

- **Dedup-before-create** — searches open + closed + history docs; a candidate that duplicates #N is never filed twice
- **False-positive gate** — reproduces the symptom against current code; unreproducible → no issue, reports the missing evidence
- **Grounded anchors** — every `file:line`/symbol in the body is read this run, never assumed
- **Code-verified status** — `--status` answers done-ness from the codebase, not from the closed flag or comments
- **Bounded issues** — over-large work is split into sub-issues, not one mega-issue
- **No dead content** — body is functional only: Problem, Scope + non-goals, machine-checkable Done
- **Confirm-before-create** — nothing is created or edited without explicit confirmation
- **Standalone** — works with or without a project adapter

## Pairs with

`ds-resolve` — execute an issue end-to-end (re-verify → impact map → plan → implement → code-verified close). `ds-issue --status` reads the close-evidence comments `ds-resolve` leaves.
