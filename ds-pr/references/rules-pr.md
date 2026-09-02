# Rules: Pull Request Quality

Rules for PR creation, review readiness, and merge strategy. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **PR Quality** | PR-01–06 (3 HIGH, 2 MEDIUM, 1 LOW) | ~12 |

---

## PR Quality

### PR-01 [HIGH] Reviewable Size
PR stays under 400 lines of change. Review effectiveness drops sharply beyond this threshold.
- **Detect:**
  - PR exceeds 400 LOC changed (additions + deletions)
  - PR touches more than 10 files
  - Review time exceeds 60 minutes
  - Multiple unrelated changes bundled in one PR
- **Fix:** Split into smaller, logically grouped PRs. Strategies: separate refactor from feature, extract infrastructure changes, split by module boundary. Each PR should be independently mergeable
- **Impact:** Median review time doubles at 400+ LOC. Defect detection drops 50% at 1000+ LOC
- **Source:** Google Engineering Practices, SmartBear "Best Kept Secrets of Peer Code Review"

### PR-02 [HIGH] Net Diff Description
PR body describes final state difference from base branch, not journey of individual commits.
- **Detect:**
  - PR body lists individual commits chronologically
  - Description includes "then I changed", "next I fixed" narrative
  - Body does not explain what reviewer sees in diff
- **Fix:** Describe net effect: what changed, why, and how to verify. Structure: Summary (1-3 bullets), motivation, test plan. Commit history tells journey; PR body tells destination
- **Impact:** A commit-by-commit narrative forces the reviewer to reconstruct the final diff themselves, and pollutes the squash-commit body release-please turns into a changelog entry.
- **Source:** dev-skills ds-pr skill design

### PR-03 [HIGH] Conventional Title
PR title follows conventional commit format. Becomes squash commit message on merge.
- **Detect:**
  - PR title missing type prefix (feat, fix, docs, refactor, etc.)
  - Title uses past tense or gerund instead of imperative
  - Title exceeds 72 characters
  - Title does not describe behavioral change
- **Fix:** Format as `type(scope): imperative description`. Becomes squash merge commit message, driving changelog generation and semantic versioning
- **Impact:** A non-conventional or malformed title becomes the squash-merge commit message, breaking release-please's version-bump and changelog parsing for this release.
- **Source:** release-please, conventional-changelog, Conventional Commits 1.0

### PR-04 [MEDIUM] Test Evidence
PR includes evidence that change works and does not break existing behavior.
- **Detect:**
  - No CI status checks on PR (`gh pr checks` / `gh pr view --json statusCheckRollup` returns empty)
  - Code changes without corresponding test changes (`git diff {base}...HEAD --name-only` touches source paths with zero matching `test/`/`*.test.*`/`*.spec.*` paths)
  - Net-diff type classification is `feat` (Phase 3) with zero test files touched
  - No manual test notes for UI or behavioral changes
- **Fix:** Require passing CI as merge prerequisite. Add or update tests for changed behavior. Include test plan in PR body: what was tested, how to verify manually if applicable
- **Impact:** A merged change with no test evidence has no proof it works and no regression guard — the next refactor can break it silently.
- **Source:** Google Engineering Practices

### PR-05 [MEDIUM] Self-Review Before Submit
Author reviewed own diff before requesting review. Catches obvious issues that waste reviewer time.
- **Detect:**
  - Debug logs or console.log left in code
  - TODO or FIXME comments without linked issues
  - Commented-out code blocks
  - Unresolved merge conflict markers
  - Temporary test values or hardcoded credentials
- **Fix:** Run self-review checklist before marking ready: no debug artifacts, no commented code, no unresolved TODOs, diff reads cleanly, tests pass locally
- **Impact:** Debug artifacts and unresolved conflict markers that reach review waste reviewer time on issues the author could have caught in one read-through.
- **Source:** Code review best practices, Google Engineering Practices

### PR-06 [LOW] Linked Issues
PR references related issues for traceability and automatic issue management.
- **Detect:**
  - No issue reference in PR body or title
  - Issue reference uses wrong syntax (not recognized by GitHub's closing-keyword list)
  - PR body contains a bare issue mention (`#123`) with no closing/relating keyword in front of it
- **Fix:** Add closing keyword + issue number: "Closes #123" or "Fixes #456" in PR body. For non-closing references: "Relates to #789". Multiple issues: one keyword per issue on separate lines
- **Impact:** An unlinked PR breaks GitHub's automatic issue-closing on merge, leaving the issue open after the fix has already shipped.
- **Source:** GitHub docs on linking PRs to issues

---

## Pre-flight Check Failures

Phase 1 Setup gate — per-check error and next action when a pre-check fails.

| Failed check | Error / next action |
|-------------|---------------------|
| `git` / `gh` missing | "Install git/gh CLI and run `gh auth login`" |
| Not on a feature branch | "Checkout a feature branch first" |
| No commits ahead | "Nothing to push — commit your changes first" |
| `gh` unauthenticated | "Run `gh auth login` then retry" |
| Behind base | Offer `git rebase origin/{base}`, stop until user confirms |
