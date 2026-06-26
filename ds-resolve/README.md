# ds-resolve

AI assistants "fix" issues that are already stale, touch one file and miss the callers that break, and close on a self-declared "done" with no proof. This skill is issue-bound: one issue in, `Closes #N` out — re-verified before any edit, impact-mapped before any plan, closed only on a green aggregate check with code-proven evidence.

**Issue-bound executor — re-verify, impact-map, plan, implement, code-verified close.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-resolve ~/.claude/skills/ds-resolve` |
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
| `/ds-resolve <#N>` | Execute issue #N end-to-end and close it with code-proven evidence |
| `/ds-resolve <#N> --dry-run` | Plan only — impact map + bounded plan posted as a comment; no files changed |

## Project adapter (optional)

Drop `.dev-skills/issue-ops.json` in the repo to supply the repo slug, done-signal command, audit→issue-type map, and a hazard checklist (project-specific data-loss/invariant traps surfaced in the impact map). Absent → the skill auto-detects repo + done-signal and relies on the six generic impact axes. See `references/adapter.md`.

## Features

- **Re-verify before edit** — confirms the issue's problem still holds; stale → stops, never "fixes" a non-problem
- **Impact-surface map** — enumerates touched/linked/affected across callers, consumers, serialization, schema, i18n/a11y/compliance, and project hazards before any code changes
- **Bounded plan (internal)** — ≤5 files per unit; each names the gap it closes and its verify signal
- **Per-unit then aggregate verify** — each unit proven before the next; full done-signal green before close
- **Regression test for fixes** — a fix closes only with a test exercising the fixed path
- **Code-proven close** — evidence comment cites signals run + change site + doctrine-lockstep note; the audit trail `ds-issue --status` reads back
- **Standalone** — works with or without a project adapter

## Pairs with

`ds-issue` — produces the well-formed issue this skill executes, and reads the close-evidence comments back via `ds-issue --status`.
