# Rules: Repository Health & Hygiene

Rules for repo settings, branch protection, and metadata. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Settings** | RPO-01–04 (2 HIGH, 2 MEDIUM) | ~12 |
| **Hygiene** | RPO-05–08 (1 HIGH, 2 MEDIUM, 1 LOW) | ~58 |

---

## Settings

### RPO-01 [HIGH] Branch Protection
Default branch requires PR review and passing CI before merge. Prevents direct pushes that bypass quality gates.
- **Detect:**
  - No branch protection rules on default branch
  - Direct push to main/master permitted
  - Required status checks not configured
  - Required reviewers set to 0
- **Fix:** Enable branch protection on default branch: require at least 1 approving review, require status checks to pass (CI pipeline), disable direct push, require branches to be up to date before merging
- **Source:** GitHub branch protection documentation

### RPO-02 [HIGH] Squash Merge Default
Squash merge produces clean linear history with one commit per PR. PR title becomes the commit message, enabling conventional commit tooling.
- **Detect:**
  - Merge commits as default merge strategy (noisy history)
  - Rebase merge as default (loses PR context)
  - Squash merge not using PR title as commit message
  - Mixed merge strategies across PRs
- **Fix:** Set squash merge as default (or only) merge strategy. Configure commit title format to use PR title. This enables release-please, conventional-changelog, and semantic versioning from PR titles
- **Source:** release-please requirements, GitHub merge settings

### RPO-03 [MEDIUM] Delete Branch on Merge
Merged branches auto-deleted to prevent branch accumulation and stale reference confusion.
- **Detect:**
  - Dozens of merged branches still present
  - Auto-delete not enabled in repository settings
  - Developers manually deleting branches inconsistently
- **Fix:** Enable "Automatically delete head branches" in repository settings (Settings > General > Pull Requests). For existing stale branches, run cleanup sweep
- **Source:** GitHub repository settings documentation

### RPO-04 [MEDIUM] CODEOWNERS
Critical paths have defined owners. PRs touching owned paths automatically request review from the right people.
- **Detect:**
  - No CODEOWNERS file in .github/, docs/, or root
  - CODEOWNERS exists but does not cover critical paths (CI config, security, core modules)
  - CODEOWNERS references teams or users that do not exist
- **Fix:** Add .github/CODEOWNERS with path-to-owner mappings. Cover: CI/CD config, security-sensitive code, core business logic, API contracts, database migrations. Format: `/path/pattern @owner-or-team`
- **Source:** GitHub CODEOWNERS documentation

---

## Hygiene

### RPO-05 [HIGH] README Quality
README is the first thing visitors see. Structure for scannability and quick comprehension.
- **Detect:**
  - README leads with a wall of badges
  - Feature list before explaining what the project does
  - README exceeds 2000 words without clear structure
  - No quick start section in the first screenful
  - Missing: one-liner description, proof/demo, install steps
- **Fix:** Structure: hook sentence -> one-liner description -> proof (screenshot/demo/benchmark) -> quick start (install + run in <60 seconds) -> philosophy/why -> feature overview -> contributing. Front-load value; details go in docs/
- **Impact:** READMEs with this structure receive 4x more engagement
- **Source:** GitHub analysis, rivereditor.com launch research

### RPO-06 [MEDIUM] Stale Branch Cleanup
Branches without commits for 30+ days deleted. Prevents confusion about active work streams.
- **Detect:**
  - Branches with last commit older than 30 days
  - More than 20 remote branches
  - Branches named with dates or sprint numbers from past quarters
- **Fix:** Delete stale branches (merged and unmerged with no recent activity). Automate: GitHub Actions scheduled workflow or quarterly manual review. Protect branches with open PRs from cleanup
- **Source:** Repository hygiene best practices

### RPO-07 [MEDIUM] Security Policy
SECURITY.md defines how to report vulnerabilities. Required for responsible disclosure.
- **Detect:**
  - No SECURITY.md in root or .github/
  - Security policy exists but missing: contact method, response timeline, scope
  - Vulnerabilities reported as public issues instead of private advisories
- **Fix:** Add SECURITY.md with: supported versions table, reporting method (email or GitHub private advisory), expected response timeline (e.g., acknowledge within 48 hours, fix within 90 days), scope of policy. Enable GitHub private vulnerability reporting
- **Source:** GitHub security advisory documentation

### RPO-08 [LOW] Social Preview
Repository has a custom social preview image. Improves appearance when shared on social media and in search results.
- **Detect:**
  - No custom social preview set (Settings > Social preview)
  - Preview image is the default GitHub avatar
  - Image dimensions not 1280x640px (2:1 ratio)
- **Fix:** Create a 1280x640px image with: project name, tagline or one-liner, visual identity (logo or icon). Upload via Settings > Social preview. Use readable font sizes and high contrast for legibility at small sizes
- **Source:** GitHub documentation on social preview images