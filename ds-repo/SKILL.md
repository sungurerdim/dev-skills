# /ds-repo

Unprotected main branches, stale branches piling up, missing CODEOWNERS, and no branch policies — most repos are misconfigured from day one. This skill audits and fixes it.

**Repository Health** — Audit and configure repo settings, branch policies, hygiene, metadata, team, and structure.

## Triggers

- User runs `/ds-repo`
- User asks to audit or configure repo settings, branch protection, or CODEOWNERS
- User asks about stale branches, repo hygiene, or team structure
- User asks to set up a new repository or fix repo configuration

## Contract

- Only manages repository settings and structure — not code quality
- Every recommendation cites specific setting or file
- Fully functional standalone — zero dependency on other skills. When blueprint profile or `.ds-findings.md` exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality.
- Every finding receives a disposition in the summary — zero silent drops (FRC)

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All scopes, no questions, fix everything |
| `--preview` | Audit only, no changes |
| `--scope=X` | Specific scope(s), comma-separated |

Without flags: present mode selection to the user.

## Scopes

Each scope defines an explicit checklist. Every check is evaluated on every run — no check is silently omitted (DSC).

### settings (5 checks)

1. **Merge strategy** — squash-only enabled (`allow_squash_merge=true`, `allow_merge_commit=false`, `allow_rebase_merge=false`)
2. **Commit title format** — PR_TITLE (`squash_merge_commit_title`)
3. **Commit message format** — PR_BODY (`squash_merge_commit_message`)
4. **Delete branch on merge** — enabled (`delete_branch_on_merge=true`)
5. **Auto-merge** — enabled (`allow_auto_merge=true`)

### protection (4 checks)

1. **Branch protection enabled** — default branch has protection rules
2. **Required reviews** — at least 1 required reviewer
3. **Required status checks** — CI must pass before merge
4. **Dismiss stale reviews** — enabled when new commits pushed

### hygiene (3 checks)

1. **Stale branches** — branches with no open PR and last commit >7 days ago
2. **Merged branches** — branches already merged into default branch but not deleted
3. **Orphan remotes** — remote-tracking refs whose upstream branch no longer exists

### metadata (7 checks)

1. **Description** — non-empty repo description
2. **Topics** — at least 3 relevant topics
3. **License** — license file present (MEDIUM on public repos, LOW on private)
4. **Homepage URL** — non-empty homepage URL
5. **README badges** — CI status badge present in README
6. **Social preview** — custom social preview image (public repos only, N/A on private)
7. **Tags/releases strategy** — semver tags, tag count matches release count

### team (2 checks)

1. **CODEOWNERS** — present for team repos (>1 contributor), N/A for solo repos
2. **CONTRIBUTING.md** — present for public repos, N/A for private solo repos

### structure (2 checks)

1. **.gitignore completeness** — IDE, OS, language-specific entries present
2. **Config file sprawl** — no multiple competing configs for same tool

**Not in scope:** CI/CD pipelines and dependency management.

## Execution Flow

Setup → Audit → Gap Analysis → Plan Review → Apply → Summary

### Phase 1: Setup

1. Verify `git` and `gh` CLI available and authenticated — `git` required, `gh` required for settings/protection scopes
2. Detect repo info via GitHub API: name, default branch, visibility, description, topics, license, homepage, plan (free/pro/enterprise)
3. **Upstream check:** Search for `## Blueprint Profile` in known instruction files. If found:
   - **Type + Stack** → suggest relevant topics for metadata scope
   - **Config.constraints** → respect stated constraints for repo settings
4. **Mode selection.** If no flags provided, ask the user:
   - **Full Audit** — audit all scopes, report findings
   - **Audit & Fix** — audit all scopes, then apply fixes
   - **Scoped** — pick specific scope(s) to audit
5. **Scope selection.** If Scoped mode or no `--scope` flag with Audit & Fix, ask which scopes to audit.

**Gate:** Repo info retrieved via API and mode/scopes selected.

### Phase 2: Audit

Run every check in every selected scope. Each check produces exactly one outcome:
- **Finding** — issue detected (with severity)
- **Pass (✅)** — check executed, no issue
- **N/A** — check cannot apply (with reason, e.g., "private repo", "solo contributor", "free plan")

Evaluate checks in order as listed in each scope definition above.

**Gate:** All checks in all selected scopes evaluated. Zero checks silently omitted.

### Phase 3: Gap Analysis

Display findings table with ALL checks accounted:

```
| # | Scope | Check | Result |
|---|-------|-------|--------|
| 1 | settings | Merge strategy | ✅ squash-only |
| 2 | settings | Commit title | MEDIUM: COMMIT_OR_PR_TITLE |
| 3 | metadata | Homepage URL | needs-input: URL required |
| 4 | protection | Branch protection | N/A (free private plan) |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW > INFO.

**Gate:** Complete checklist table produced — every check from every scope appears.

### Phase 4: Plan Review [SKIP if --auto]

Ask user: Fix All / By Severity / Review Each / Report Only.

**needs-input findings:** Before proceeding to Apply, ask the user for required input on `needs-input` items. Example: "Homepage URL is empty — do you have a URL to set? (provide URL / skip)"

**Gate:** User selected action plan. All needs-input items resolved (user provided input or explicitly declined).

### Phase 5: Apply [SKIP if --preview]

Apply fixes via GitHub API (settings, protection), git commands (hygiene), file operations (config files).

For each finding, assign a disposition:
- `fixed` — applied and verified via API read-back or file check
- `failed` — attempted but API/command returned error
- `skipped` — user declined, platform limitation, or not applicable (with reason)
- `needs-approval` — protection changes that affect other contributors, CODEOWNERS modifications, visibility changes

**Gate:** Every finding has a disposition. `fixed + failed + skipped + needs_approval = total`.

### Phase 6: Summary

```
repo: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

Display disposition table — every finding from Gap Analysis appears with its final status:

```
| # | Finding | Disposition |
|---|---------|-------------|
| 1 | Stale branch X | fixed ✅ |
| 2 | Auto-merge disabled | skipped (free plan limitation) |
| 3 | Homepage URL empty | fixed ✅ (user provided URL) |
| 4 | Branch protection | skipped (free plan limitation) |
```

Display clean checks — scopes where all checks passed:
```
Clean: settings (5/5 ✅), structure (2/2 ✅)
```

**Gate:** Summary rendered. `fixed + failed + skipped + needs_approval = total` verified. Every check from every scope accounted for.

## Quality Gates

1. Settings changes verified via API read-back
2. Scope boundary — only modify what was requested
3. Every finding gets a disposition in the summary — zero silent drops (FRC)
4. Every scope check is evaluated and accounted for — zero silent omissions (DSC)
5. Destructive changes (branch deletion, permission changes) require confirmation unless `--auto`

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Not a git repo | Stop with clear message |
| `gh` not available | Skip settings/protection scopes, warn |
| No GitHub remote | Skip API-dependent scopes |
| Fork repository | Note fork status, skip protection (forked from upstream) |
| Empty repository | Skip hygiene, minimal metadata check |
| Free private plan | Mark protection and auto-merge checks as N/A with reason |
| needs-input item in --auto mode | Skip with disposition `skipped (--auto, no user input)` |
