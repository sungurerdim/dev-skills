# Rules: Commit Quality

Rules for commit message quality and atomic grouping. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Message Quality** | CMT-01–06 (3 HIGH, 2 MEDIUM, 1 LOW) | ~12 |

---

## Message Quality

### CMT-01 [HIGH] Conventional Format
Commit message follows `type(scope): description` per Conventional Commits 1.0. Valid types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert.
- **Detect:**
  - Commits without recognized type prefix
  - Missing colon separator between type and description
  - Scope containing spaces or special characters
  - Search: commit titles not matching `^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?: .+`
- **Fix:** Classify change by type. Add scope if change is localized to a module. Format: `type(scope): lowercase imperative description`
- **Source:** conventionalcommits.org v1.0.0

### CMT-02 [HIGH] Descriptive Title
Title describes WHAT changed in system's behavior, not a vague label.
- **Detect:**
  - Vague titles: "fix bug", "update code", "changes", "wip", "misc", "stuff"
  - Titles that name files instead of behavior: "update utils.ts"
  - Titles that describe activity instead of outcome: "working on auth"
- **Fix:** Describe behavioral change. "fix(auth): prevent token refresh loop on expired sessions" instead of "fix bug". Reader should understand impact without reading diff
- **Source:** Chris Beams "How to Write a Git Commit Message"

### CMT-03 [HIGH] Atomic Commits
One logical change per commit. Commit can be reverted independently without breaking unrelated functionality.
- **Detect:**
  - Commit touching unrelated files or features (e.g., auth fix + UI color change)
  - Commit mixing refactor with behavior change
  - Commit combining formatting with logic changes
  - Multiple "and" clauses needed to describe commit
- **Fix:** Split into separate commits, each with single purpose. Use `git add -p` for partial staging. Formatting changes go in dedicated commit
- **Source:** Git best practices, Conventional Commits rationale

### CMT-04 [MEDIUM] Title Length
Title stays within 50 characters (72 absolute max). GitHub Desktop and `git log --oneline` truncate beyond this.
- **Detect:**
  - Title exceeds 50 characters
  - Title exceeds 72 characters (hard limit)
  - Details crammed into title instead of body
- **Fix:** Shorten title to essential description. Move details, context, and reasoning to commit body. Use scope to reduce title words: `fix(parser): handle empty input` instead of `fix: handle empty input in the parser module`
- **Source:** Git documentation, GitHub UI constraints

### CMT-05 [MEDIUM] Body Explains Why
Commit body explains motivation and context. Diff shows what changed; body explains why.
- **Detect:**
  - Body repeating file-level changes ("updated foo.ts, changed bar.py")
  - Body describing diff instead of reasoning
  - No body on commits where the "why" is non-obvious
- **Fix:** Explain: Why was change needed? What alternatives were considered? What trade-offs were made? Link to issues or discussions. Wrap body at 72 characters
- **Source:** Chris Beams "How to Write a Git Commit Message"

### CMT-06 [LOW] Imperative Mood
Title uses imperative mood: "add feature" not "added feature" or "adding feature". Reads as command: "If applied, this commit will [your title]."
- **Detect:**
  - Past tense in title: "added", "fixed", "removed", "updated"
  - Gerund in title: "adding", "fixing", "removing", "updating"
  - Third person: "adds", "fixes", "removes"
- **Fix:** Rewrite in imperative: "add" not "added", "fix" not "fixed". Test with: "If applied, this commit will [title]" — should read naturally
- **Source:** Git documentation, git's own generated messages (Merge branch, Revert)
