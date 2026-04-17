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
- **Source:** dev-skills ds-pr skill design

### PR-03 [HIGH] Conventional Title
PR title follows conventional commit format. Becomes squash commit message on merge.
- **Detect:**
  - PR title missing type prefix (feat, fix, docs, refactor, etc.)
  - Title uses past tense or gerund instead of imperative
  - Title exceeds 72 characters
  - Title does not describe behavioral change
- **Fix:** Format as `type(scope): imperative description`. Becomes squash merge commit message, driving changelog generation and semantic versioning
- **Source:** release-please, conventional-changelog, Conventional Commits 1.0

### PR-04 [MEDIUM] Test Evidence
PR includes evidence that change works and does not break existing behavior.
- **Detect:**
  - No CI status checks on PR
  - Code changes without corresponding test changes
  - New feature without any test coverage
  - No manual test notes for UI or behavioral changes
- **Fix:** Require passing CI as merge prerequisite. Add or update tests for changed behavior. Include test plan in PR body: what was tested, how to verify manually if applicable
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
- **Source:** Code review best practices, Google Engineering Practices

### PR-06 [LOW] Linked Issues
PR references related issues for traceability and automatic issue management.
- **Detect:**
  - No issue reference in PR body or title
  - Issue reference uses wrong syntax (not recognized by GitHub)
  - PR addresses an issue but does not link it
- **Fix:** Add closing keyword + issue number: "Closes #123" or "Fixes #456" in PR body. For non-closing references: "Relates to #789". Multiple issues: one keyword per issue on separate lines
- **Source:** GitHub docs on linking PRs to issues
