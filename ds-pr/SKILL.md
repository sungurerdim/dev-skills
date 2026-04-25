# /ds-pr

PR descriptions that list every commit instead of net change create noise, confuse reviewers, and break changelogs. This skill describes what the diff actually shows.

**Smart Pull Requests** — Conventional commit title + clean body for release-please.

## Triggers

- User runs `/ds-pr`
- User asks to create a pull request, open a PR, or prepare changes for merge
- User says "create PR", "open PR", or "submit for review"
- After successful commit, suggest PR creation if on a feature branch

## Contract

**PR describes net diff between main and HEAD — nothing else.** Not journey of individual commits, not session decisions, not what was tried and reverted. If commit A added something and commit B removed it, net effect is zero — do not mention it.

Run `git diff {base}...HEAD` and describe what that diff shows.

- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.
- **Exempt from state protocol:** git history is the natural state — `git diff {base}...HEAD` always provides full context. No `ds/audit/pr.json` written.

**Pipeline:** `PR title → squash merge on main → release-please reads title → changelog + version bump`. PR title IS changelog entry. PR body becomes squash commit body. Everything must be accurate and minimal.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | No questions, auto-detect everything, create PR directly |
| `--no-auto-merge` | Skip auto-merge setup |
| `--preview` | Show PR plan without creating |
| `--draft` | Create as draft PR (implies --no-auto-merge) |
| `--no-tidy` | Skip history tidy, push commits as-is |

## Delegation

**Owns:** pull-request, net-diff-analysis, pr-title, pr-description | **Delegates:** ds-fix → pre-PR gates; ds-commit → staging before PR | **Receives:** none

## Execution Flow

Validate -> History Tidy -> Quality Gates -> Analyze -> Build -> [Review] -> Create -> [Merge Setup] -> [Cleanup] -> [Needs-Approval] -> Summary

### Phase 1: Validate

**Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → note relevant findings for PR body context. Stale → ignore.

**IDU:** Profile → {Project Map.Toolchain, Type + Stack}. Findings({pr}) → verify + use. Absent → own analysis.

**Steps 1-4 are independent — run in parallel:**

1. Verify `git` and `gh` CLI available and authenticated
2. Verify git repo, detect base branch (via GitHub API, fallback: main, then master)
3. Verify not on base branch, not detached HEAD
4. `git fetch origin {base}`
5. No commits ahead → stop. Behind base → ask rebase (--auto: rebase automatically)
6. Check existing PR → show URL, ask: Update / Skip

**Gate:** All pre-checks passed. Branch has commits ahead of base and is ready for PR. If fails → stop with an explicit error identifying which check failed: `git`/`gh` not found → "Install git/gh CLI and run `gh auth login`"; not on a feature branch → "Checkout a feature branch first"; no commits ahead → "Nothing to push — commit your changes first"; `gh` unauthenticated → "Run `gh auth login` then retry"; behind base → offer `git rebase origin/{base}` and stop until user confirms.

### Phase 1.5: History Tidy (skip if --no-tidy or --preview)

If >3 unpushed commits, offer to tidy: squash into logical commits based on net diff.

- Ask user: Tidy (recommended) or Keep as-is (--auto: tidy silently)
- Execute: `git reset --mixed origin/{base}`, stage and commit per plan
- On failure: `git reset --hard $ORIG_HEAD`
- Push: `git push -u origin {branch}`

**Gate:** Commits tidied (or skipped) and pushed to remote. If fails → if the tidy (git reset --mixed) fails, run `git reset --hard $ORIG_HEAD` to restore the branch and push the original commits as-is with a warning; if the push fails (rejected, no upstream), stop with error "Push failed — run `git push -u origin {branch}` manually and then retry /ds-pr".

### Phase 2: Quality Gates (entire project)

Run format, lint, and test across entire project. Auto-fix all fixable issues. Detect toolchain from config files. Skip silently if tool unavailable.

Run in order (stop on failure): Format -> Lint -> Secret scan -> Test.
Format/lint changed files → commit as `chore: format and lint fixes`.
Tests fail → stop. Only create PR when all tests pass.

**Secret scan ([references/principles.md §5](references/principles.md)):** Run secret-pattern detection on all changed files (same patterns as ds-fix security scope) before opening the PR. Any match → FAIL the gate. PR creation must not put credentials in front of human reviewers.

**Gate:** Format, lint, secret scan, and tests all pass. No uncommitted fixes remain. If fails → secret scan hit: stop immediately, do not create PR, output the matching file:line and instruct user to remove the secret and rotate credentials before retrying; test failure: stop, show failing test names, do not create PR; format/lint failure that could not be auto-fixed: stop, list the unfixed violations, do not create PR — all three cases are hard stops with no bypass.

### Phase 3: Analyze

`git diff {base}...HEAD` is THE source of truth. PR quality rules: [references/rules-pr.md](references/rules-pr.md).

**Net diff principle:** PR describes final state difference, not development journey.

**Type classification:**
1. Scan commit titles for initial signal
2. Validate against net diff — net diff overrides:
   - New user-facing capability? -> `feat`
   - Broken behavior fixed? -> `fix`
   - Neither? -> dominant non-bumping type
3. `!` in any commit type or `BREAKING CHANGE:` -> append `!`

**Title:** `{type}({scope}): {summary}` — max 70 chars.

**Body:** Summary (1-3 bullets), Changes (grouped, max 5), Breaking Changes (if any). Max 20 lines.

**Gate:** Net diff analyzed and PR title generated in conventional commit format. If fails → if `git diff {base}...HEAD` returns empty (commits exist but net diff is zero), stop with "Net diff is empty — all changes were reverted in later commits. Nothing to describe in a PR."; if type classification is ambiguous after applying the net-diff override, default to the most conservative non-bumping type and append a WARN in the PR body.

### Phase 4: Review (skip if --auto)

Display: branch, title, body preview, version annotation.

**Version annotation:** Show version bump effect with each option:
- All signals agree: `version: {type} → {effect}`
- Net diff overrode commits: `version: ~{type} → {effect} (estimated)`

Effects: `feat` → minor bump, `fix` → patch bump, `feat!`/`fix!` → major bump, anything else → no bump.

Ask user:

- **Create + Auto-merge** (recommended) — squash + delete branch when checks pass
- **Create PR only** — merge manually later
- **Create as draft** — draft PR for further work
- **Cancel**

**Gate:** User confirmed PR creation option. Title, body, and merge strategy decided. If fails → if the user selects Cancel, exit cleanly without creating a PR and without modifying the branch; if the user provides no response after one re-prompt, exit with "PR creation cancelled — re-run /ds-pr when ready."

### Phase 5: Create

`gh pr create --title "{title}" --body "{body}" [--draft]`

**Gate:** PR created successfully. `gh pr create` returned PR URL. If fails → stop with explicit error from `gh pr create` output; do not proceed to Merge Setup; suggest: check `gh auth status`, verify the branch was pushed, and re-run /ds-pr --no-tidy to skip the tidy step if the branch state changed.

### Phase 6: Merge Setup (default, skip if --no-auto-merge, --draft, or manual)

- With branch protection: `gh pr merge {number} --auto --squash`
- Without branch protection: check CI status, then `gh pr merge {number} --squash`

After merge: `git checkout {base} && git pull origin {base} && git branch -d {branch}`

**Gate:** Auto-merge enabled or merge completed. Local branch switched to base. If fails → if `gh pr merge --auto` fails (no branch protection, CI not configured), warn the user and skip auto-merge — PR was already created; if the local checkout to base fails (`git checkout {base}`), warn and leave the user on the current branch; do not attempt branch cleanup in Phase 6.1 if checkout failed.

### Phase 6.1: Branch Cleanup [AFTER MERGE ONLY]

**Steps 1-2 are independent — run in parallel:**

1. Detect local merged branches: `git branch --merged {base}` (exclude base and current)
2. Detect remote merged branches: `git branch -r --merged origin/{base}` (exclude base and HEAD)
3. Combine results. Merged branches found:
   - Ask: Delete all (recommended) / Skip (--auto: delete all silently)
   - Delete local: `git branch -d {branch}`. Delete remote-only: `git push origin --delete {branch}`. On error: warn and continue.

**Gate:** All merged branches deleted locally and remotely, or cleanup skipped by user. If fails → for any individual branch deletion that errors (`git branch -d` or `git push origin --delete`), warn and continue with the remaining branches; surface all failed deletions in the Phase 8 summary so the user can clean them up manually.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → record the unresolved item with disposition `pending-user-decision`, proceed to Summary with status WARN, and list all unresolved needs_approval items so the user can address them.

### Phase 8: Summary

PR URL, title, type -> bump effect, auto-merge status.

`pr: {OK|FAIL} | {url} | {type} -> {bump} | auto-merge: {on|off}`
`FRC: Fixed: N | Skipped: N | Failed: N | Total: N`

**Gate:** Summary line printed. PR URL returned to user. If fails → print the PR URL on its own line regardless (it was returned by `gh pr create`), then list any phases that could not complete (merge setup, branch cleanup), with the user's next manual action clearly stated.

## Quality Gates

- PR description describes net diff — not journey of individual commits
- Every quality gate check (format, lint, test) gets a disposition in summary (FRC)
- Conventional commit type on PR title matches net diff classification
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: not applicable — exempt from state protocol (atomic, git-driven, see Contract).

## Error Recovery

| Situation | Action |
|-----------|--------|
| `gh` CLI not authenticated | Stop with clear error: "Run `gh auth login` first" |
| Rebase conflict during history tidy | Abort rebase (`git reset --hard $ORIG_HEAD`), push as-is, warn user |
| CI checks failing after PR creation | Warn user, skip auto-merge setup, suggest fixing and re-running |
| Remote branch already deleted | Create fresh remote branch from local, continue |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No commits ahead of base | Report "nothing to push", exit |
| PR already exists for branch | Show existing PR URL, ask if update needed |
| CI checks failing | Warn user, create PR but skip auto-merge setup |
