# GitHub features via `gh` (ds-issue)

All issue operations use the `gh` CLI (Issues, labels, milestones, sub-issues, comments). Projects v2 is out of scope for this skill. Never interpolate raw issue text into a shell string — pass bodies via `--body-file` so newlines and shell metacharacters are inert.

**Zero local footprint.** This skill writes no files. Pass multi-line bodies to `gh` with a heredoc through process substitution — no temp file on disk, nothing to clean up:

```bash
gh issue create --repo <slug> --title "<title>" --body-file - <<'EOF'
<composed body>
EOF
# or, where --body-file - is unsupported, process substitution:
gh issue comment <n> --repo <slug> --body-file <(cat <<'EOF'
<body>
EOF
)
```

The durable record is the GitHub issue + its comments + git — not a local `ds/audit/` file.

**Version gate (once per run):** `gh --version` ≥ 2.94.0 → native sub-issue / issue-type / dependency flags and their JSON fields are available (GitHub.com and GHES 3.17+; blocked-by/blocking relationships need GHES 3.19+). Below 2.94.0 → use the REST/task-list fallbacks marked below and recommend upgrading.

**Read-phase command allowlist:** `--status`, `--sweep` classification, and every `--dry-run` restrict `gh` to `issue view` / `issue list` / `search issues` / `label list` (+ `repo view` for the slug). Mutating commands (`issue create/edit/close/comment`, `label create`) run only after the per-item confirmation the SKILL gates require.

## Dedup search (Phase 2)

```bash
# whole set, all states — open AND closed AND in-progress
# gh ≥ 2.94.0: read hierarchy/type/dependencies as JSON fields — never re-derive them from labels or body text
gh issue list --repo <slug> --state all --limit 200 --json number,title,state,labels,issueType,parent,subIssues,blockedBy,blocking
# gh < 2.94.0 fallback: --json number,title,state,labels (hierarchy from task-list checkboxes in bodies)
# keyword search across the repo — OMIT --state to search all states
# (gh search issues accepts only --state open|closed; omitting it searches both)
gh search issues "<keywords>" --repo <slug> --json number,title,state
# one issue's detail when reconciling (gh ≥ 2.94.0: append ,parent,subIssues,blockedBy,blocking)
gh issue view <n> --repo <slug> --json number,title,body,labels,state
```

`--sweep` and `--status` consume these JSON fields directly for hierarchy and blocked-by state.

History / abandoned-decision docs (from the adapter's `historyDocs`) are read as files, not via `gh` — a superseded decision is not an issue.

## Create / refine (Phase 5)

```bash
# create — body via heredoc (no temp file)
gh issue create --repo <slug> --title "<title>" --body-file - \
  --label "<type>" --label "<priority>" <<'EOF'   # + optional --label "<status>"
<composed body>
EOF

# refine an existing raw issue
gh issue edit <n> --repo <slug> --body-file - \
  --add-label "<type>" --add-label "<priority>" <<'EOF'
<composed body>
EOF
```

## Labels (Phase 4)

```bash
gh label list --repo <slug> --limit 100        # live taxonomy — never assume label names
gh label create "<name>" --color "<hex>" --description "<desc>"   # only if scaffolding is approved
```

Assign exactly one type + one priority + optional status. Map type from the adapter's taxonomy; if absent, fall back to conventional-commit types (feat/fix/refactor/docs/chore/test/ci/tooling).

## Sub-issues / issue types / dependencies (Phase 4, oversized work)

Native `gh` flags (≥ 2.94.0) are the primary path; a task-list in the body is the portable fallback every tool renders.

```bash
# native (gh ≥ 2.94.0)
gh issue create --repo <slug> --title "<child>" --parent <parent>   # link parent on create
gh issue edit <n> --repo <slug> --set-parent <parent>               # re-parent; --remove-parent to unlink
gh issue edit <n> --repo <slug> --add-blocked-by <m>                # dependency; --add-blocking / --remove-* variants
gh issue create ... --type "<Type>"                                 # native issue type, when the repo defines types

# fallback (gh < 2.94.0) — REST sub-issue link:
gh api repos/<slug>/issues/<parent>/sub_issues -f sub_issue_id=<child-node-or-number>
# fallback (always works) — task-list checkboxes in the parent body:
#   - [ ] #childA
#   - [ ] #childB
```

The label taxonomy (1 type + 1 priority) stays the portable default; native issue types complement labels when the repo defines them — never replace the labels.

Split when the estimate exceeds the bounded-task threshold (≈5 files / one reviewable unit). Each child is itself a well-formed issue (its own Done).

## Comments as audit trail

```bash
gh issue comment <n> --repo <slug> --body-file - <<'EOF'   # plan, evidence, decisions
<body>
EOF
```

The `--do` mode posts its plan (under `--dry-run`) and its close-evidence here; `--status` reads these comments back but judges done-ness from code, not from the comment text. These comments ARE the run's audit trail — there is no local log.

## Milestones (optional)

The toolkit supports milestones but never imposes them. If the repo uses them: `gh issue edit <n> --milestone "<name>"`. If none exist, skip silently.

## Closing with evidence (Phase 6, `--do`)

```bash
# preferred — auto-close on merge: put in the commit or PR body
Closes #<N>        # or Fixes #<N>

# explicit close when no PR carries it — evidence comment first, then close
gh issue comment <N> --repo <slug> --body-file - <<'EOF'
<code-proven evidence: signals run + result, change site> + <doctrine-lockstep note>
EOF
gh issue close <N> --repo <slug> --reason completed       # done + verified
gh issue close <N> --repo <slug> --reason "not planned"   # obsolete / superseded / stale
```

Use `completed` only when the aggregate signal is green and (for fixes) a regression test exists. Use `not planned` for the stale/superseded issues found in re-verify.

## Linked PR (when the work goes through a PR)

```bash
gh pr create --repo <slug> --title "<type>(<scope>): <summary>" --body-file - <<'EOF'
<what changed + why>
Closes #<N>
EOF
```

The issue closes when the PR merges (`Closes #N` in the body) — no separate `gh issue close`. Delegate PR creation to ds-pr when available.

## Commit message

```
<type>(<scope>): <summary>

<what changed + why>
Closes #<N>
```

`Closes #N` in the merged commit auto-closes the issue and back-links the commit as evidence.
