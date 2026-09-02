# Checkpoint Protocol — clean tree before the first write

**Consumers:** every skill whose flow writes, deletes, reverts, or resets project files (ds-backend, ds-build, ds-compliance, ds-debug, ds-deploy, ds-deps, ds-devops, ds-docs, ds-fix, ds-frontend, ds-init, ds-issue, ds-mobile, ds-pr, ds-repo, ds-review, ds-simplify, ds-test, ds-tune). Read-only and planning-only skills are exempt.

Rationale: a revert-capable flow run over uncommitted user work is a data-loss path — `git checkout -- <file>`, `git restore`, `git reset --hard`, and `rm` all destroy edits that exist nowhere else. The protocol makes rollback one command at every point.

## Pre-gate (once, before the first project-file write)

```
git status --porcelain
```

Exclude the skill's own artifacts (`ds/audit/`, `ds/<skill>/`) from the output. Then:

| Remaining output | Default (autonomous) | `--ask` |
|------------------|----------------------|---------|
| Empty | Proceed. | Proceed. |
| Non-empty, and the planned writes are **disjoint** from every dirty path | Proceed; list the dirty paths in the summary as untouched. | Show the dirty files; ask **Commit first (recommended) / Stash / Proceed anyway** (risk stated: edits interleave with uncommitted work; single-command rollback is lost). |
| Non-empty, and a planned write **touches** a dirty path | Stop that unit; record `only you can do: uncommitted changes in {file} — commit or stash before this skill edits it`; continue with disjoint units. | Same menu; **Proceed anyway** is offered only when the flow has no revert/reset step. |

**Stop-hard skills** — flows whose failure path resets or reverts tracked files in a loop (ds-tune's experiment ratchet, ds-build's budgeted backtracking, any `reset --hard`): a dirty tree stops the loop before it starts in every mode. `Proceed anyway` is never offered; the menu is Commit first (recommended) / Stash / Abort.

## During the run

| Moment | Action |
|--------|--------|
| Before each bounded unit | Note the starting commit (`git rev-parse --short HEAD`) and the unit's file set. |
| Unit's verify signal red after ≤ 3 fix attempts | Revert exactly the unit's files (`git checkout -- {files}`; new files `rm`), never a broader path; record disposition `reverted` with the captured error. |
| Never | Revert or reset a path the run did not write. Never `reset --hard` without the pre-gate having proven a clean tree. |

## Resume

A resumed run (`--resume`, or re-entry after a context gap) re-runs the pre-gate before its first write. State from the earlier run never substitutes for the current `git status`.
