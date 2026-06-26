# GitHub features via `gh` (ds-resolve)

ds-resolve uses `gh` for: loading the issue, posting plan/evidence comments, and closing with the right reason and a linked PR. Never interpolate issue text into a shell string — pass comment/PR bodies via `--body-file`.

## Load the issue (Phase 1)

```bash
gh issue view <#N> --repo <slug> --json number,title,body,labels,state,comments
```

Read the body's Done block (the machine-checkable signals), any `Blocked by #M`, and prior comments (a plan may already be posted).

## Plan / evidence comments (audit trail)

```bash
gh issue comment <#N> --repo <slug> --body-file <path>
```

- `--dry-run` posts the impact map + bounded plan here, then stops.
- Phase 7 posts the close evidence here (signals run + result, change site, doctrine-lockstep note).

These comments are the audit trail; `ds-issue --status` reads them but re-verifies done-ness from code regardless.

## Close with the right reason (Phase 7)

```bash
# preferred — auto-close on merge: put in the commit or PR body
Closes #<N>        # or Fixes #<N>

# explicit close when no PR carries it
gh issue close <#N> --repo <slug> --reason completed \
  --comment "$(cat <path>)"     # evidence inline, or post the comment first then close

# obsolete / superseded / won't-do (not a completion)
gh issue close <#N> --repo <slug> --reason "not planned"
```

Use `completed` only when the aggregate signal is green and (for fixes) a regression test exists. Use `not planned` for stale/superseded issues found in re-verify.

## Linked PR (when the work goes through a PR)

```bash
gh pr create --repo <slug> --title "<type>(<scope>): <summary>" --body-file <path>
# body includes "Closes #<N>" so merge auto-closes the issue
gh pr view --json number,url -q .url
```

Delegate PR creation to a dedicated PR skill if available; otherwise this is the minimal path. The issue closes when the PR merges — no separate `gh issue close` needed.

## Commit message

```
<type>(<scope>): <summary>

<what changed + why>
Closes #<N>
```

`Closes #N` in the merged commit auto-closes the issue and back-links the commit as evidence.
