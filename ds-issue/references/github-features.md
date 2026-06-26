# GitHub features via `gh` (ds-issue)

All issue operations use the `gh` CLI (Issues, labels, milestones, sub-issues, comments). Projects v2 is out of scope for this skill. Never interpolate raw issue text into a shell string — pass bodies via `--body-file` so newlines and shell metacharacters are inert.

## Dedup search (Phase 2)

```bash
# whole set, all states — open AND closed AND in-progress
gh issue list --repo <slug> --state all --limit 200 --json number,title,state,labels
# keyword search across the repo — OMIT --state to search all states
# (gh search issues accepts only --state open|closed; omitting it searches both)
gh search issues "<keywords>" --repo <slug> --json number,title,state
# one issue's detail when reconciling
gh issue view <n> --repo <slug> --json number,title,body,labels,state
```

History / abandoned-decision docs (from the adapter's `historyDocs`) are read as files, not via `gh` — a superseded decision is not an issue.

## Create / refine (Phase 5)

```bash
# create — body from a file so multi-line + metacharacters are safe
gh issue create --repo <slug> --title "<title>" --body-file <path> \
  --label "<type>" --label "<priority>"   # + optional --label "<status>"

# refine an existing raw issue
gh issue edit <n> --repo <slug> --body-file <path> \
  --add-label "<type>" --add-label "<priority>"
```

Write the composed body to a temp file (e.g. `ds/audit/issue-body.md`), then pass it with `--body-file`. Delete the temp file after create.

## Labels (Phase 4)

```bash
gh label list --repo <slug> --limit 100        # live taxonomy — never assume label names
gh label create "<name>" --color "<hex>" --description "<desc>"   # only if scaffolding is approved
```

Assign exactly one type + one priority + optional status. Map type from the adapter's taxonomy; if absent, fall back to conventional-commit types (feat/fix/refactor/docs/chore/test/ci/tooling).

## Sub-issues / task-lists (Phase 4, oversized work)

GitHub sub-issues are managed through the REST/GraphQL API; a task-list in the body is the portable fallback every tool renders.

```bash
# task-list fallback (always works) — checkboxes in the parent body:
#   - [ ] #childA
#   - [ ] #childB
# native sub-issue link (when the repo has Issue Types / sub-issues enabled):
gh api repos/<slug>/issues/<parent>/sub_issues -f sub_issue_id=<child-node-or-number>
```

Split when the estimate exceeds the bounded-task threshold (≈5 files / one reviewable unit). Each child is itself a well-formed issue (its own Done).

## Comments as audit trail

```bash
gh issue comment <n> --repo <slug> --body-file <path>   # plan, evidence, decisions
```

`ds-resolve` writes close-evidence here; `ds-issue --status` reads these comments back but judges done-ness from code, not from the comment text.

## Milestones (optional)

The toolkit supports milestones but never imposes them. If the repo uses them: `gh issue edit <n> --milestone "<name>"`. If none exist, skip silently.

## Closing (reference — ds-resolve owns this)

```bash
gh issue close <n> --reason completed     # work done + verified
gh issue close <n> --reason "not planned" # obsolete / won't-do / superseded
```

`Closes #N` / `Fixes #N` in a merged commit or PR body auto-closes on merge.
