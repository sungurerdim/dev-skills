# Ask-Exception List — the only decisions an autonomous run does not make

**Consumers:** every `ds-*` skill (default autonomous mode); orchestrators forward it unchanged to delegates.

Skills run autonomously by default: every decision point resolves by best judgment against the evidence gathered (findings, code, profile, prior art in the repo), and the summary records what was decided and why. `--ask` restores the interactive flow at every decision point. **The list below is the only thing a default run does not decide** — each item is skipped, recorded `only you can do` with the concrete action needed, and never executed blind.

## (a) Irreversible — no rollback path exists

| Action | Why it is excluded |
|--------|-------------------|
| Force-push or history rewrite on a shared/remote branch | Rewrites what others hold |
| Permanent deletion of a branch, tag, or remote resource with no local backup | Nothing to restore from |
| Rotating, deleting, or transmitting a real secret/credential | Cannot be un-sent; rotation breaks consumers |
| Any action requiring a value only a human can supply | A live credential, a business/legal/financial decision not inferable from the repo, a store-console or account setting |

## (b) Publishing — moves work off the local machine

Excluded even when technically undoable, because undoing it does not un-share it.

| Action | Includes |
|--------|----------|
| `git push` of any kind, to any remote | Branches, tags, `--force`, `--mirror` |
| Opening, updating, or merging a pull/merge request | `gh pr create`, `gh pr merge`, review submission |
| Deploying to a shared, staging, or production environment | Any deploy CLI or pipeline trigger |
| Submitting to an app store, publishing to a package registry, creating a release | `npm publish`, `cargo publish`, `gh release create`, store consoles |

## Boundaries

- **Committing is not publishing.** An autonomous run commits its work locally; leaving changes uncommitted strands them. The boundary is the remote: commit freely, publish never.
- **Destructive local actions with a rollback path are decided, not asked** — a file delete on a clean tree, a `git checkout --` revert of the run's own change, a dependency bump in the lockfile — provided the Checkpoint protocol (`checkpoint-protocol.md`) has verified a clean starting state.
- **CRITICAL findings are decided, not stranded** — the run applies them with the same impact/effort/risk reasoning an approval block would show, and records that reasoning, unless the fix itself is on this list (for example a fix that needs a live credential).
- **The list does not grow ad hoc.** A skill that must add an item states it in its own Contract, citing clause (a) or (b). Everything not listed is resolved, never asked, never silently dropped.

## Under `--ask`

Every decision point asks: mode/scope menus, approval batches, per-item CRITICAL confirmation, checkpoint choices. Menus follow the interactive conventions (a `(recommended)` default, an `all` affordance beside per-category bulk options, `(Cancel)` last, every approved item shown compactly). The exception list still holds — `--ask` lets a human approve a publish step; it never makes a skill perform one on its own.
