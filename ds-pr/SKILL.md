# /ds-pr

PR descriptions that list every commit instead of the net change create noise, confuse reviewers, and break changelogs. This skill describes what the diff actually shows.

**Smart Pull Requests** — Conventional commit title + clean body for release-please.

## Triggers

- User runs `/ds-pr`
- User asks to create a pull request, open a PR, or prepare changes for merge
- User says "create PR", "open PR", or "submit for review"
- After a successful commit, suggest PR creation if on a feature branch

## Contract

**The PR describes the net diff between main and HEAD — nothing else.** Not the journey of individual commits, not session decisions, not what was tried and reverted. If commit A added something and commit B removed it, the net effect is zero — do not mention it.

Run `git diff {base}...HEAD` and describe what that diff shows.

- Fully functional standalone — zero dependency on other skills. When blueprint profile exists, uses toolchain info to skip detection. When absent, runs own complete detection with identical quality.
- FRC+DSC enforced.

**Pipeline:** `PR title → squash merge on main → release-please reads title → changelog + version bump`. The PR title IS the changelog entry. The PR body becomes the squash commit body. Everything must be accurate and minimal.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | No questions, auto-detect everything, create PR directly |
| `--no-auto-merge` | Skip auto-merge setup |
| `--preview` | Show PR plan without creating |
| `--draft` | Create as draft PR (implies --no-auto-merge) |
| `--no-tidy` | Skip history tidy, push commits as-is |

## Execution Flow

Validate -> History Tidy -> Quality Gates -> Analyze -> Build -> [Review] -> Create -> [Merge Setup] -> [Cleanup] -> [Needs-Approval] -> Summary

### Phase 1: Validate

**Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, note relevant findings for PR body context. If stale, ignore.

**IDU:** Profile → {Project Map.Toolchain, Type + Stack}. Findings({pr}) → verify + use. Absent → own analysis.

**Steps 1-4 are independent — run in parallel:**

1. Verify `git` and `gh` CLI available and authenticated
2. Verify git repo, detect base branch (via GitHub API, fallback: main, then master)
3. Verify not on base branch, not detached HEAD
4. `git fetch origin {base}`
5. No commits ahead → stop. Behind base → ask rebase (--auto: rebase automatically)
6. Check existing PR → show URL, ask: Update / Skip

**Gate:** All pre-checks passed. Branch has commits ahead of base and is ready for PR.

### Phase 1.5: History Tidy (skip if --no-tidy or --preview)

If >3 unpushed commits, offer to tidy: squash into logical commits based on net diff.

- Ask the user: Tidy (recommended) or Keep as-is (--auto: tidy silently)
- Execute: `git reset --mixed origin/{base}`, stage and commit per plan
- On failure: `git reset --hard $ORIG_HEAD`
- Push: `git push -u origin {branch}`

**Gate:** Commits are tidied (or skipped) and pushed to remote.

### Phase 2: Quality Gates (entire project)

Run format, lint, and test across the entire project. Auto-fix all fixable issues. Detect toolchain from config files. Skip silently if tool unavailable.

Run in order (stop on failure): Format -> Lint -> Test.
If format/lint changed files -> commit as `chore: format and lint fixes`.
If tests fail -> stop. Only create PR when all tests pass.

**Gate:** Format, lint, and tests all pass. No uncommitted fixes remain.

### Phase 3: Analyze

`git diff {base}...HEAD` is THE source of truth. PR quality rules: [references/rules-pr.md](references/rules-pr.md).

**Net diff principle:** The PR describes the final state difference, not the development journey.

**Type classification:**
1. Scan commit titles for initial signal
2. Validate against net diff — net diff overrides:
   - New user-facing capability? -> `feat`
   - Broken behavior fixed? -> `fix`
   - Neither? -> dominant non-bumping type
3. `!` in any commit type or `BREAKING CHANGE:` -> append `!`

**Title:** `{type}({scope}): {summary}` — max 70 chars.

**Body:** Summary (1-3 bullets), Changes (grouped, max 5), Breaking Changes (if any). Max 20 lines.

**Gate:** Net diff analyzed and PR title generated in conventional commit format.

### Phase 4: Review (skip if --auto)

Display: branch, title, body preview, version annotation.

**Version annotation:** Show version bump effect with each option:
- All signals agree: `version: {type} → {effect}`
- Net diff overrode commits: `version: ~{type} → {effect} (estimated)`

Effects: `feat` → minor bump, `fix` → patch bump, `feat!`/`fix!` → major bump, anything else → no bump.

Ask the user:

- **Create + Auto-merge** (recommended) — squash + delete branch when checks pass
- **Create PR only** — merge manually later
- **Create as draft** — draft PR for further work
- **Cancel**

**Gate:** User confirmed PR creation option. Title, body, and merge strategy decided.

### Phase 5: Create

`gh pr create --title "{title}" --body "{body}" [--draft]`

**Gate:** PR created successfully. `gh pr create` returned a PR URL.

### Phase 6: Merge Setup (default, skip if --no-auto-merge, --draft, or manual)

- With branch protection: `gh pr merge {number} --auto --squash`
- Without branch protection: check CI status, then `gh pr merge {number} --squash`

After merge: `git checkout {base} && git pull origin {base} && git branch -d {branch}`

**Gate:** Auto-merge enabled or merge completed. Local branch switched to base.

### Phase 6.1: Branch Cleanup [AFTER MERGE ONLY]

**Steps 1-2 are independent — run in parallel:**

1. Detect local merged branches: `git branch --merged {base}` (exclude base and current)
2. Detect remote merged branches: `git branch -r --merged origin/{base}` (exclude base and HEAD)
3. Combine results. If merged branches found:
   - Ask: Delete all (recommended) / Skip (--auto: delete all silently)
   - Delete local: `git branch -d {branch}`. Delete remote-only: `git push origin --delete {branch}`. On error: warn and continue.

**Gate:** All merged branches deleted locally and remotely, or cleanup skipped by user.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 8: Summary

PR URL, title, type -> bump effect, auto-merge status.

`pr: {OK|FAIL} | {url} | {type} -> {bump} | auto-merge: {on|off}`
`FRC: Fixed: N | Skipped: N | Failed: N | Total: N`

**Gate:** Summary line printed. PR URL returned to user.

## Quality Gates

- PR description describes the net diff — not the journey of individual commits
- Every quality gate check (format, lint, test) gets a disposition in the summary (FRC)
- Conventional commit type on PR title matches the net diff classification
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

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