# Rules: Repository Health & Hygiene

Rules for repo settings, branch protection, and metadata. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Settings** | RPO-01–04, RPO-09 (2 HIGH, 3 MEDIUM) | ~12 |
| **Hygiene** | RPO-05–08, RPO-10, RPO-11 (2 HIGH, 2 MEDIUM, 2 LOW) | ~58 |
| **Security** | RPO-12–15 (3 HIGH, 1 MEDIUM) | ~126 |

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
- **Impact:** An unprotected default branch lets any push bypass review and CI, so a broken or malicious commit reaches production with no gate.
- **Source:** GitHub branch protection documentation

### RPO-02 [HIGH] Squash Merge Default
Squash merge → clean linear history with one commit per PR. PR title becomes commit message, enabling conventional commit tooling.
- **Detect:**
  - Merge commits as default merge strategy (noisy history)
  - Rebase merge as default (loses PR context)
  - Squash merge not using PR title as commit message
  - Mixed merge strategies across PRs
- **Fix:** Set squash merge as default (or only) merge strategy. Configure commit title format to use PR title. → release-please, conventional-changelog, and semantic versioning from PR titles
- **Impact:** Mixed merge strategies produce a noisy, non-linear history that breaks PR-title-driven changelog and semantic-versioning tooling.
- **Source:** release-please requirements, GitHub merge settings

### RPO-03 [MEDIUM] Delete Branch on Merge
Merged branches auto-deleted to prevent branch accumulation and stale reference confusion.
- **Detect:**
  - Dozens of merged branches still present
  - Auto-delete not enabled in repository settings
  - Developers manually deleting branches inconsistently
- **Fix:** Enable "Automatically delete head branches" in repository settings (Settings > General > Pull Requests). For existing stale branches, run cleanup sweep
- **Impact:** Branches accumulate indefinitely, making the branch list unusable and stale references a constant source of confusion.
- **Source:** GitHub repository settings documentation

### RPO-04 [MEDIUM] CODEOWNERS
Critical paths have defined owners. PRs touching owned paths automatically request review from right people.
- **Detect:**
  - No CODEOWNERS file in .github/, docs/, or root
  - CODEOWNERS exists but does not cover critical paths (CI config, security, core modules)
  - CODEOWNERS references teams or users that do not exist
- **Fix:** Add .github/CODEOWNERS with path-to-owner mappings. Cover: CI/CD config, security-sensitive code, core business logic, API contracts, database migrations. Format: `/path/pattern @owner-or-team`
- **Impact:** Without owner routing, a PR touching a sensitive path sits unreviewed or gets reviewed by whoever happens to notice, not the person accountable for that code.
- **Source:** GitHub CODEOWNERS documentation

### RPO-09 [MEDIUM] Ruleset Coverage
Repository rulesets layer on top of (or replace) classic branch protection: reusable across branches/repos, bypass actors are audit-logged, evaluated non-destructively before enforcement.
- **Detect:**
  - No rulesets configured (`gh api repos/{owner}/{repo}/rulesets` empty) while only classic branch protection is active
  - Org plan supports rulesets but repo relies solely on the legacy classic protection API
- **Fix:** Where org plan supports rulesets, migrate default-branch protection to a ruleset (same required-review/status-check rules, plus bypass audit log). Free/legacy plans without ruleset support: classic branch protection remains the valid fallback — not a finding.
- **Impact:** Classic branch protection alone has no bypass audit log, so an admin override of the protection rule leaves no trace of who bypassed it or why.
- **Source:** GitHub repository rulesets documentation

---

## Hygiene

### RPO-05 [HIGH] README Quality
README is first thing visitors see. Structure for scannability and quick comprehension.
- **Detect:**
  - README leads with wall of badges
  - Feature list before explaining what project does
  - README exceeds 2000 words without clear structure
  - No quick start section in first screenful
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
- **Impact:** Dozens of untouched branches obscure which work streams are actually active and slow every branch-list and clone operation.
- **Source:** Repository hygiene best practices

### RPO-07 [MEDIUM] Security Policy
SECURITY.md defines how to report vulnerabilities. Required for responsible disclosure.
- **Detect:**
  - No SECURITY.md in root or .github/
  - Security policy exists but missing: contact method, response timeline, scope
  - Vulnerabilities reported as public issues instead of private advisories
- **Fix:** Add SECURITY.md with: supported versions table, reporting method (email or GitHub private advisory), expected response timeline (e.g., acknowledge within 48 hours, fix within 90 days), scope of policy. Enable GitHub private vulnerability reporting
- **Impact:** Without a stated disclosure channel, a researcher who finds a vulnerability has no safe path to report it — it either goes public immediately or gets dropped.
- **Source:** GitHub security advisory documentation

### RPO-08 [LOW] Social Preview
Repository has custom social preview image. Improves appearance when shared on social media and in search results.
- **Detect:**
  - No custom social preview set (Settings > Social preview)
  - Preview image is default GitHub avatar
  - Image dimensions not 1280x640px (2:1 ratio)
- **Fix:** Create 1280x640px image with: project name, tagline or one-liner, visual identity (logo or icon). Upload via Settings > Social preview. Use readable font sizes and high contrast for legibility at small sizes
- **Impact:** A missing or default preview renders as a blank generic card wherever the repo link is shared, costing click-through on every social post or PR link.
- **Source:** GitHub documentation on social preview images

### RPO-10 [LOW] A Public Repo's Backlog May Live in a Private Sibling
Public repos where roadmap visibility is unwanted (marketing site) may skip their own issue tracker; their backlog items live as single entries in a private sibling repo's tracker.
- **Detect:** Roadmap/strategy items leaking through a public repo's issues; or the opposite — a public repo with its tracker disabled and its backlog untracked anywhere.
- **Fix:** Decide tracker placement per repo by visibility: public-safe repos keep their own tracker; visibility-sensitive public repos disable theirs and register backlog items in a designated private sibling's tracker (one entry per item, labeled by source repo).
- **Impact:** Public backlogs leak competitive roadmap for zero benefit; untracked backlogs silently drop work — the private-sibling pattern avoids both.
- **Source:** XR-084 — cross-project experience registry (2026).

### RPO-11 [HIGH] Governing Artifacts Live Under Version Control, Never in a Scratch Directory
The artifacts that govern a project — rule registry, decision log, spec, generator source — live inside a repository; a working/scratch directory never becomes their home.
- **Detect:** A governing artifact resolving to a path outside any repo (a scratch or working directory, a home-relative path, an untracked folder); a pointer in a tracked file whose target is unversioned; a canonical artifact with exactly one copy and no history.
- **Fix:** Move the artifact into a repo, commit it, and repoint every reference in the same change. Derivation inputs, dumps, and backups may be archived or dropped; the canonical copy is versioned and pushed. Working directories stay working — nothing that governs the project is allowed to become a resident.
- **Impact:** A governing artifact with one unversioned copy has no history, no backup, and no second machine. Losing it loses the reasoning behind every decision derived from it, and nothing signals the loss until someone looks.
- **Source:** XR-205 — cross-project experience registry (2026).

## Security

### RPO-12 [HIGH] Secret Scanning + Push Protection
GitHub-native scanning for committed secrets, plus a push-time block before a secret ever lands in history.
- **Detect:** `gh api repos/{owner}/{repo} --jq '.security_and_analysis'` → `secret_scanning.status` or `secret_scanning_push_protection.status` not `enabled`
- **Fix:** `gh api -X PATCH repos/{owner}/{repo} --input - <<< '{"security_and_analysis":{"secret_scanning":{"status":"enabled"},"secret_scanning_push_protection":{"status":"enabled"}}}'`
- **Impact:** Without push protection, a committed secret is live in git history the moment it lands — rotation, not prevention, becomes the only remaining option.
- **Source:** GitHub secret scanning REST API documentation

### RPO-13 [HIGH] Dependabot Alerts + Security Updates
Automated vulnerable-dependency detection and automated patch PRs.
- **Detect:** `gh api repos/{owner}/{repo}/vulnerability-alerts` → 404 (disabled, expect 204); `gh api repos/{owner}/{repo}/automated-security-fixes` → `enabled: false`
- **Fix:** `gh api -X PUT repos/{owner}/{repo}/vulnerability-alerts`; `gh api -X PUT repos/{owner}/{repo}/automated-security-fixes`
- **Impact:** A known-vulnerable dependency sits unpatched indefinitely with nobody notified — the same CVE a scanner would have caught on day one instead ships to every deploy.
- **Source:** GitHub Dependabot REST API documentation

### RPO-14 [MEDIUM] Private Vulnerability Reporting
A researcher-facing private channel to report a vulnerability directly on the repository, independent of SECURITY.md's own contact method.
- **Detect:** `gh api repos/{owner}/{repo}/private-vulnerability-reporting --jq '.enabled'` → `false`
- **Fix:** `gh api -X PUT repos/{owner}/{repo}/private-vulnerability-reporting`
- **Impact:** With no in-platform private channel, a researcher without another contact path defaults to a public issue — disclosing the vulnerability before a fix exists.
- **Source:** GitHub private vulnerability reporting REST API documentation

### RPO-15 [HIGH] Code Scanning Default Setup
CodeQL analysis wired with zero workflow authoring, covering every push and PR.
- **Detect:** `gh api repos/{owner}/{repo}/code-scanning/default-setup --jq '.state'` → `not-configured`
- **Fix:** `gh api -X PATCH repos/{owner}/{repo}/code-scanning/default-setup --input - <<< '{"state":"configured","query_suite":"default","languages":["{detected-language}"]}'`
- **Impact:** Without default-setup code scanning, injection and memory-safety classes of bug ship silently — no CI job ever looks for them.
- **Source:** GitHub code scanning REST API documentation
