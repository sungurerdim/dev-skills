# Rules: Repository Health & Hygiene

Rules for repo settings, branch protection, and metadata. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Settings** | RPO-01–04, RPO-09 (2 HIGH, 3 MEDIUM) | ~12 |
| **Hygiene** | RPO-05–08, RPO-10, RPO-11 (2 HIGH, 2 MEDIUM, 2 LOW) | ~58 |
| **Security** | RPO-12–15 (3 HIGH, 1 MEDIUM) | ~126 |
| **Scope Checklists** | settings/protection/hygiene/metadata/team/structure/oss-readiness | ~160 |

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

---

## Scope Checklists

Per-scope enumeration for [SKILL.md](../SKILL.md) Phase 2 Audit — every check evaluated on every run, no check silently omitted. `security` is fully covered by RPO-12–15 above (no separate list).

#### settings (5 checks)

1. **Merge strategy** — squash-only (`allow_squash_merge=true`, `allow_merge_commit=false`, `allow_rebase_merge=false`)
2. **Commit title format** — `PR_TITLE` (`squash_merge_commit_title`)
3. **Commit message format** — `PR_BODY` (`squash_merge_commit_message`)
4. **Delete branch on merge** — enabled (`delete_branch_on_merge=true`)
5. **Auto-merge** — enabled (`allow_auto_merge=true`)

#### protection (9 checks)

1. **Branch protection enabled** — default branch has protection rules
2. **Required reviews** — solo repo → **N/A — solo** (detect: `git shortlog -sn | wc -l` = 1, or no CODEOWNERS/team signal); otherwise at least 1 required reviewer
3. **Required status checks** — CI must pass before merge (required solo or team)
4. **Dismiss stale reviews** — enabled when new commits pushed; N/A when check 2 is N/A (no reviewer to dismiss)
5. **Ruleset coverage** — detect via `gh api repos/{owner}/{repo}/rulesets` alongside classic branch protection (`gh api repos/{owner}/{repo}/branches/{branch}/protection`); org plan supports repository rulesets and none exist → recommend migrating to rulesets (layered enforcement, bypass audit log); no ruleset support → classic branch protection is the valid fallback, not a finding
6. **Ruleset bypass list** — ruleset lists admins/broad roles in its bypass list with no documented justification → HIGH finding; classic "do not allow bypassing" maps to an empty bypass list, and GitHub's auto-migration can pre-populate admins into it — silently weakening protection. Keep the bypass list empty unless a justification note exists. N/A when no ruleset exists
7. **Push ruleset** — ruleset-only capability with no classic counterpart: blocks restricted file paths (`.env`, secret-pattern files), extensions, and oversized files at the push layer across the entire fork network; plan supports rulesets and none exists → LOW opportunity finding (complements the oss-readiness git-secret-history check); no ruleset support → N/A
8. **Linear history** — `required_linear_history=true` on the default branch (mechanical protection — required solo or team)
9. **Force-push disabled** — `allow_force_pushes=false` on the default branch (mechanical protection — required solo or team)

#### hygiene (4 checks)

1. **Stale branches** — no open PR (`gh pr list --head {branch}` → empty output) + last commit > 30 days ago (`git log -1 --format=%cs {branch}`). UNMERGED work — deletion loses commits: always `needs-approval`, confirmed per item regardless of flags — matches the publish/irreversible exception list (permanent deletion with no backup); recorded `only you can do` by default rather than executed blind; `--ask` confirms per item; never bulk-deleted
2. **Merged branches** — already merged into default but not deleted (`git branch -r --merged {default-branch}` lists them; commits preserved in base — safe to bulk-delete after one confirmation)
3. **Orphan remotes** — remote-tracking refs whose upstream no longer exists (`git remote prune` — safe)
4. **History bloat** — blobs > 10 MB in history inflating every clone (`git rev-list --objects --all` + `git cat-file --batch-check` size sort). Finding proposes `git filter-repo --strip-blobs-bigger-than <size>` (the recommended tool — not `git filter-branch` or BFG) + post-rewrite `git gc`, with LFS migration as the keep-the-file alternative. History rewrite is destructive and breaks every existing clone: always `needs-approval` with an explicit team-coordination + backup warning, never autonomous — same rule as the git-secret-history surgery (oss-readiness check 15). Matches the publish/irreversible exception list (history rewrite on a shared branch) — recorded `only you can do` by default, `--ask` confirms per item, never executed blind

#### metadata (7 checks)

1. **Description** — non-empty repo description
2. **Topics** — at least 3 relevant topics
3. **License** — license file present (MEDIUM on public, LOW on private)
4. **Homepage URL** — non-empty
5. **README badges** — CI status badge present in README
6. **Social preview** — custom social preview image (public repos only, N/A on private)
7. **Tags/releases strategy** — semver tags, tag count matches release count

#### team (2 checks)

1. **CODEOWNERS** — present for team repos (>1 contributor), N/A for solo (detect: `git shortlog -sn | wc -l` = 1, or no team signal)
2. **CONTRIBUTING.md** — present for public repos, N/A for private solo

#### structure (3 checks)

1. **`.gitignore` completeness** — IDE, OS, language-specific entries present
2. **Config file sprawl** — no multiple competing configs for same tool
3. **Codebase (Twelve-Factor #1)** — one repo tracks one deployable app across many deploys: repo hosts multiple unrelated deployable apps without workspace/monorepo tooling boundaries, or app code is duplicated across separate repos instead of shared via a package → flag

#### oss-readiness (16 checks — activated by `--oss-ready` flag or explicit scope selection)

Content generation for checks 3-5 below: `/ds-docs` present → delegate (LICENSE/CONTRIBUTING/SECURITY content); absent → this scope's own Fix text stands alone as the inline template.

1. **LICENSE present** — file at repo root, SPDX-recognized identifier
2. **LICENSE compatibility** — dependency licenses compatible with repo license (e.g., strong-copyleft dep under MIT → finding), evaluated against an explicit allow/review/deny policy where one exists (none → propose authoring one); full transitive-tree license scan + SBOM export delegated to ds-deps (advisory-handoff: absent → direct-dep spot check inline, gap-note for the tree)
3. **CODE_OF_CONDUCT.md** — present, tailored (not stock Contributor Covenant copy with no customization)
4. **CONTRIBUTING.md** — present, covers local setup + PR expectations + testing
5. **SECURITY.md** — present, declares vulnerability reporting channel
6. **Issue templates** — `bug_report.md` + `feature_request.md` under `.github/ISSUE_TEMPLATE/`
7. **PR template** — `.github/pull_request_template.md` present
8. **CODEOWNERS** — present, maps key paths to maintainers
9. **README first impression** — problem statement, install, quick usage, screenshot/demo (where applicable), maintenance signal (last commit / release < 6 months)
10. **Discoverability — topics** — ≥3 relevant GitHub topics
11. **Discoverability — badges** — CI status + license badge minimum
12. **Short description** — repo description populated, one sentence, ≤100 chars
13. **Homepage URL** — populated when project has docs site / landing page
14. **Dependabot or renovate** — `.github/dependabot.yml` or `renovate.json` present, enabled for supported stacks
15. **Git secret history** — scan git history for hardcoded secrets (`git log -p -S"api_key"` / `git-secrets --scan-history` / `trufflehog`). Any hit → Category B finding with `git-filter-repo` surgery proposal; autonomous deletion is forbidden. Matches the publish/irreversible exception list (secret rotation/deletion + history rewrite) — recorded `only you can do` by default, never executed blind; `--ask` confirms per item.
16. **SPDX file headers** — source files carry a case-sensitive `SPDX-License-Identifier: <expr>` comment at/near the top; the declared identifier matches the LICENSE file. Missing headers → LOW finding with bulk-add proposal (Category A — mechanical, no public-facing text change)

OSS-readiness emits Category B findings for anything user-visible (README rewrites, LICENSE changes, trademark concerns). Templates, metadata, Dependabot config may be Category A when they don't alter public-facing text.

**Trademark / name collision check (part of check 10):** Brief search for project name against USPTO / EUIPO common-term lookup. Ambiguous or conflicting → HIGH finding with "consult legal counsel" suggestion.
