# ds-freeze

Every feature stays "in scope" by default, so a release grows until every corner needs polishing and nothing ships. Deciding what to defer is a judgment call nobody makes explicit until it's too late to matter.

Turns "we're trying to perfect everything" into a deliberate release scope: inventory every feature and open issue, decide ship/defer with the user, implement only the kept set, file the rest as tracked backlog, and sync docs so nothing overclaims.

## Install

```bash
./install.sh --skills ds-freeze
```

Or run the full installer — `ds-freeze` ships with every other skill.

## Use

```
/ds-freeze                          # full flow: inventory → triage → manifest → implement → doc sync
/ds-freeze --ask                    # interactive: menus and confirmations at every decision point
/ds-freeze --preview                # candidate inventory only, no mutation
/ds-freeze --milestone=v1.0         # label the release manifest / tracking issue
/ds-freeze --skip-implement         # triage + file backlog, skip implementation
/ds-freeze --resume=#142            # continue an existing tracking issue
```

Also runs automatically inside `/ds-ship`'s Scope-Freeze branch when the ask signals scope reduction ("simplify the release", "cut to an MVP") — the frozen `ship` set becomes the working scope for every later ship-cascade phase.

## Modes / Scopes

| Mode | What it does |
|------|---------------|
| (default) | Full loop: inventory, collaborative triage, release manifest, implement kept set, sync docs |
| `--preview` | Inventory only — see the candidate list before committing to a triage session |
| `--skip-implement` | Stop after filing — hand implementation to a separate `/ds-build` or `/ds-issue --do` pass |
| `--resume=#N` | Continue a triage session from its tracking issue |

## Features

- **Three-way disposition, not a binary cut** — `ship` (release-critical), `defer-hidden` (built, gated off for now), `defer-backlog` (not now) — so complex-but-real features get hidden, not deleted or half-shipped
- **GitHub-issue-backed backlog** — every deferred item becomes a real, filed, deduped issue via `/ds-issue`, not a lost decision in a chat transcript
- **Only touches the kept set** — implementation delegates to `/ds-build` (or `/ds-issue --do`, or an inline loop when both are absent) one item at a time; deferred items get zero code changes beyond an optional flag gate
- **Doc sync on exit** — delegates to `/ds-docs` so the README/spec never claims a feature that got deferred, and never omits one that shipped
- **State-exempt** — the tracking issue (or `docs/release/*.md` fallback) plus git are the durable record; resuming re-reads it *with its comments*, so a scope decision made in the thread is folded into the checklists instead of being dropped
