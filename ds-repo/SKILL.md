# /ds-repo

**Repository Health** — Audit and configure repo settings, branch policies, hygiene, metadata, team, and structure.

## Triggers

- User runs `/ds-repo`
- User asks to audit or configure repo settings, branch protection, or CODEOWNERS
- User asks about stale branches, repo hygiene, or team structure
- User asks to set up a new repository or fix repo configuration

## Contract

- Only manages repository settings and structure — not code quality
- Every recommendation cites specific setting or file
- Fully functional standalone — uses `.findings.md` for optimization when available

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All scopes, no questions, fix everything |
| `--preview` | Audit only, no changes |
| `--scope=X` | Specific scope(s), comma-separated |

Without flags: present mode selection to the user.

## Scopes

| Scope | Focus |
|-------|-------|
| settings | Squash merge, delete-on-merge, auto-merge, default branch, PR title/body format |
| protection | Branch protection rules, required reviews, status checks, dismiss stale reviews |
| hygiene | Stale branches, merged branch cleanup, orphan remotes |
| metadata | Description, topics/tags strategy, license, homepage URL, README badges, social preview |
| team | CODEOWNERS, review assignments, contributor guidelines (CONTRIBUTING.md) |
| structure | .gitignore completeness, directory conventions, config file sprawl |

**Not in scope:** CI/CD pipelines and dependency management.

## Execution Flow

Setup → Audit → Gap Analysis → Plan Review → Apply → Summary

### Phase 1: Setup

1. Verify `git` and `gh` CLI available and authenticated — `git` required, `gh` required for settings/protection scopes
2. Detect repo info via GitHub API: name, default branch, visibility, description, topics, license, homepage
3. **Mode selection.** If no flags provided, ask the user:
   - **Full Audit** — audit all scopes, report findings
   - **Audit & Fix** — audit all scopes, then apply fixes
   - **Scoped** — pick specific scope(s) to audit
4. **Scope selection.** If Scoped mode or no `--scope` flag with Audit & Fix, ask which scopes to audit.

### Phase 2: Audit

Run scope-specific checks:

- **settings:** Check merge strategy config (squash, commit title=PR_TITLE, commit msg=PR_BODY, delete-on-merge, auto-merge). Expected: squash=true, title=PR_TITLE, msg=PR_BODY, delete=true.
- **protection:** Check default branch protection: required reviews, dismiss stale reviews, required status checks, enforce for admins. No protection → HIGH finding.
- **hygiene:** Stale branches (no open PR, last commit >7 days ago). Merged branches still present. Orphan remote-tracking refs.
- **metadata:**
  - Missing description → MEDIUM
  - No topics → LOW. Suggest relevant topics based on detected stack.
  - No license on public repo → MEDIUM
  - No homepage URL → LOW
  - No README badges (CI status, version, license) → LOW
  - No social preview image → LOW (public repos only)
  - Tags strategy: check if releases use semver tags, if tag count matches release count
- **team:** CODEOWNERS for team repos (>1 contributor), CONTRIBUTING.md for public repos.
- **structure:** .gitignore completeness (IDE, OS, language-specific entries), config file sprawl (multiple competing configs for same tool).

### Phase 3: Gap Analysis

Display findings table: scope, severity, issue, current state, recommended state.

**Severity:** CRITICAL > HIGH > MEDIUM > LOW.

### Phase 4: Plan Review [SKIP if --auto]

Ask user: Fix All / By Severity / Review Each / Report Only.

### Phase 5: Apply [SKIP if --preview]

Apply fixes via GitHub API (settings, protection), git commands (hygiene), file operations (config files).

**Needs-approval items:** Protection changes that affect other contributors, CODEOWNERS modifications, visibility changes.

### Phase 6: Summary

```
repo: {OK|WARN|FAIL} | Applied: N | Failed: N | Needs Approval: N | Total: N
```

## Quality Gates

1. No destructive changes without confirmation (branch deletion, permission changes)
2. Settings changes verified via API read-back
3. Scope boundary — only modify what was requested

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Not a git repo | Stop with clear message |
| `gh` not available | Skip settings/protection scopes, warn |
| No GitHub remote | Skip API-dependent scopes |
| Fork repository | Note fork status, skip protection (forked from upstream) |
| Empty repository | Skip hygiene, minimal metadata check |
