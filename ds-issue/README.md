# ds-issue

AI assistants file issues from memory — unverified `file:line` anchors, duplicates of issues that already exist, verbose dead content, "done" claims nobody proved, and decisions buried in comments nobody re-reads. This skill makes the tracker trustworthy: nothing is created until the symptom is reproduced against current code and checked for duplicates, every issue **body** is a standalone brief with its gates and their baselines named, and "what's done" is answered from the codebase.

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
| `/ds-issue --do #N` | Execute issue #N end-to-end (re-verify → impact map → implement → code-proven close) |
| `/ds-issue --do --all` | Execute every open issue end-to-end, in priority order; confirm each per item; skip-and-record blockers, continue |
| `/ds-issue --do #N --preview` | Plan only — impact map + plan written into the issue body; no source files changed |
| `/ds-issue --auto` | Zero-interaction run — every decision (including `--do --all`) resolved by best judgment |

## Project adapter (optional)

Drop `.dev-skills/issue-ops.json` in the repo to sharpen the skill with your repo slug, doctrine doc paths, label taxonomy, audit→issue-type map, done-signal command, and hazard checklist. Absent → the skill auto-detects repo, done-signal, and criteria. See `references/adapter.md`.

## Features

- **Body is the single source of truth** — decisions, criteria, gate baselines, deferrals and closure evidence are written into the issue body with `gh issue edit --body-file -`, never into a comment; a comment is read only to promote someone else's requirement out of it. An issue body is a standalone brief: an agent with no access to the originating conversation can open it and work it
- **Current state vs target state** — two separate blocks: what the code does today, proved by `file:line` or pasted command output, against what will be observably true when done. The difference between them is the declared work
- **Gates named with their baselines** — every gate carries its exact command, its expected output, and the value measured at intake, so an executor can tell an inherited red from one it caused
- **Red proof and mutation proof** — a fix's regression test is observed red before the fix and green after; a newly added gate is proven red under a realistic deviation and green after revert. Both outputs live in the body
- **Dedup-before-create, with real output** — searches open + closed + history docs, and pastes the commands' actual output into the body; a verdict without its output blocks create
- **False-positive gate** — reproduces the symptom against current code; unreproducible → no issue, reports the missing evidence
- **Grounded anchors** — every `file:line`/symbol in the body is read this run, never assumed
- **Epic + sub-issues** — multi-step work splits into a natively linked hierarchy (`--parent`, `--add-blocked-by`); the epic owns the whole's state and the binding order, each sub-issue is workable without opening the epic, and nothing is duplicated between them
- **Decisions and handoffs stay visible** — an owner call blocks progress → an Open decision block (question, options, recommendation) that is resolved in place; an item deferred to another issue appears in both bodies
- **Code-verified status** — `--status` answers done-ness from the codebase, not from the closed flag or "done" comments; it runs each gate against its recorded baseline and flags body health (a criterion living in a comment, a gate with no baseline, a one-sided handoff)
- **End-to-end execution** — `--do #N` first promotes comment-borne requirements into the body (or rejects them explicitly with a two-sided handoff — an undispositioned comment-criterion blocks close), re-verifies the root cause (stale → stops), maps the full impact surface (callers/consumers/sync/schema/i18n + project hazards), implements in bounded units, and closes by writing the evidence into the body; `--do --all` runs that same flow over the whole open backlog in priority order, confirming each issue, skipping blockers, and ending with a per-issue outcome table
- **Bounded work** — over-large issues split into an epic + sub-issues; execution units stay ≤5 files
- **No dead content** — body is functional only, and every Done criterion resolves to a command's output or an observed effect ("improved", "reviewed", "cleaned up" are rejected)
- **Confirm-before-create/close** — nothing is created, edited, or closed without explicit confirmation
- **Zero local footprint (GitHub mode)** — writes no files; the GitHub issue body + git are the durable record (no `ds/audit/`, no temp files). No GitHub remote at all → last-resort local mode (root `tasks.md`), never chosen just for a missed `gh auth login`
- **Standalone** — works with or without a project adapter
