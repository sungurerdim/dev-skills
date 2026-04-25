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
- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All scopes, no questions, fix everything |
| `--preview` | Audit only, no changes |
| `--scope=X` | Specific scope(s), comma-separated |
| `--oss-ready` | OSS-readiness mode (see `oss-readiness` scope below) |
| `--resume` | Resume from `ds/audit/repo.json` without prompting |
| `--clean` | Delete existing state and start fresh |

No flags → present mode selection.

## Scopes

Each scope defines an explicit checklist. Every check evaluated on every run — no check silently omitted (DSC).

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

### oss-readiness (15 checks — activated by `--oss-ready` flag or when scope is explicitly selected)

1. **LICENSE present** — file at repo root, SPDX-recognized identifier
2. **LICENSE compatibility** — dependency licenses compatible with repo license (e.g., GPL dep under MIT project → finding)
3. **CODE_OF_CONDUCT.md** — present, tailored (not stock Contributor Covenant copy with no customization)
4. **CONTRIBUTING.md** — present, covers local setup + PR expectations + testing
5. **SECURITY.md** — present, declares vulnerability reporting channel
6. **Issue templates** — at least `bug_report.md` + `feature_request.md` under `.github/ISSUE_TEMPLATE/`
7. **PR template** — `.github/pull_request_template.md` present
8. **CODEOWNERS** — present, maps key paths to maintainers
9. **README first impression** — has: problem statement, install, quick usage, screenshot/demo (where applicable), maintenance signal (last commit / release < 6 months)
10. **Discoverability — topics** — ≥3 relevant GitHub topics on the repo
11. **Discoverability — badges** — at least CI status badge + license badge
12. **Short description** — repo description populated, one sentence, ≤100 chars
13. **Homepage URL** — populated when project has docs site / landing page
14. **Dependabot or renovate** — `.github/dependabot.yml` or `renovate.json` present, enabled for supported stacks
15. **Git secret history** — scan git history for hardcoded secrets (`git log -p -S"api_key"` / `git-secrets --scan-history` / `trufflehog`). Any hit → Category B finding with `git-filter-repo` surgery proposal; autonomous deletion is forbidden.

OSS-readiness emits Category B findings for anything user-visible (README rewrites, LICENSE changes, trademark concerns). Templates, metadata, and Dependabot config may be Category A when they don't alter public-facing text.

**Trademark / name collision check (part of check 10):** Brief web search for project name against USPTO / EUIPO common-term lookup. Ambiguous or conflicting → HIGH finding with suggestion to consult legal counsel.

**Not in scope:** CI/CD pipelines and dependency management. Code-level security audit delegated to `/ds-compliance`.

## Delegation

**Owns:** repo-settings, branch-protection, repo-hygiene, repo-metadata, team, structure, oss-readiness (--oss-ready mode) | **Delegates:** ds-docs → LICENSE / CONTRIBUTING / SECURITY content generation | **Receives:** ds-ship → Phase 5 repo pass

## Execution Flow

Setup → Audit → Gap Analysis → Plan Review → Apply → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/repo.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-query GitHub API for changed settings), skip `done` phases, announce `[RPO] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

**State `data` shape:** `{ repo_info: {name, default_branch, visibility, plan}, scopes_selected, scopes_done[], checks_run[], findings[{id, severity, scope, check, disposition}], fixes_applied[] }`.

1. Verify `git` and `gh` CLI available and authenticated — `git` required, `gh` required for settings/protection scopes
2. Detect repo info via GitHub API: name, default branch, visibility, description, topics, license, homepage, plan (free/pro/enterprise)
3. **IDU:** Profile → {Type + Stack, Config.constraints}. Findings({repo}) → verify + use. Absent → own analysis.
4. **Mode selection.** No flags → ask user:
   - **Full Audit** — audit all scopes, report findings
   - **Audit & Fix** — audit all scopes, then apply fixes
   - **Scoped** — pick specific scope(s) to audit
5. **Scope selection.** Scoped mode or no `--scope` flag with Audit & Fix → ask which scopes to audit.

**Gate:** Repo info retrieved via API and mode/scopes selected. If fails → if `gh` CLI is unavailable or unauthenticated, skip settings and protection scopes, warn the user, and proceed with hygiene/metadata/structure/team scopes using only local git commands; if the GitHub API returns an error, record `state.data.repo_info` with whatever was retrievable and continue; if the user provides no mode/scope selection, default to Full Audit across all scopes.

### Phase 2: Audit

Run every check in every selected scope following [references/rules-repo.md](references/rules-repo.md). Each check produces exactly one outcome:
- **Finding** — issue detected (with severity)
- **Pass (✅)** — check executed, no issue
- **N/A** — check cannot apply (with reason, e.g., "private repo", "solo contributor", "free plan")

Evaluate checks in order as listed in each scope definition above.

**Gate:** All checks in all selected scopes evaluated. Zero checks silently omitted. If fails → if a specific check cannot be evaluated (API unavailable, insufficient permissions, unsupported plan), record it as `N/A` in `state.data.checks_run` with an explicit reason rather than omitting it; surface all N/A checks in the Phase 3 gap analysis table so they are visible and not silently lost.

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

**Gate:** Complete checklist table produced — every check from every scope appears. If fails → identify which scope's checks are missing from the table, re-query `state.data.checks_run` to reconstruct the missing rows, and re-render the table; if a scope's check data is unrecoverable, add a row for each missing check with result "ERROR: data unavailable" rather than leaving it absent.

### Phase 4: Plan Review [SKIP if --auto]

Ask user: Fix All / By Severity / Review Each / Report Only.

**needs-input findings:** Before proceeding to Apply, ask user for required input on `needs-input` items. Example: "Homepage URL is empty — do you have a URL to set? (provide URL / skip)"

**Gate:** User selected action plan. All needs-input items resolved (user provided input or explicitly declined). If fails → if the user provides no action plan selection after one re-prompt, default to Report Only (no changes applied); for each needs-input item where the user provides no response or declines, record it in `state.data.findings` with disposition `skipped (user declined input)` and list it prominently in the Phase 7 summary.

### Phase 5: Apply [SKIP if --preview]

Apply fixes via GitHub API (settings, protection), git commands (hygiene), file operations (config files).

Per finding, assign disposition:
- `fixed` — applied and verified via API read-back or file check
- `failed` — attempted but API/command returned error
- `skipped` — user declined, platform limitation, or not applicable (with reason)
- `needs-approval` — protection changes that affect other contributors, CODEOWNERS modifications, visibility changes

**Gate:** Every finding has a disposition. `fixed + failed + skipped + needs_approval = total`. If fails → for any finding missing a disposition, assign `failed` with reason "disposition not recorded during apply", re-run the count; if a GitHub API call to apply a fix returns an error, record the finding as `failed` in `state.data.findings[].disposition` with the API error message and continue with the next finding.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped). If fails → record the unresolved item in `state.data.findings[].disposition` as `pending-user-decision`, proceed to Summary with status WARN, and list all unresolved needs_approval items in the disposition table so the user can take action outside this session.

### Phase 7: Summary

```
repo: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

Display disposition table — every finding from Gap Analysis appears with final status:

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

**Gate:** Summary rendered. `fixed + failed + skipped + needs_approval = total` verified. Every check from every scope accounted for. If fails → if the count does not reconcile, list all findings with their dispositions inline to expose the discrepancy, mark summary status as WARN with "Disposition count mismatch — review the table above"; if any scope's checks are missing from the final table, reconstruct from `state.data.checks_run` and append them.

## Quality Gates

1. Settings changes verified via API read-back
2. Scope boundary — only modify what was requested
3. Every finding gets a disposition in summary — zero silent drops (FRC)
4. Every scope check evaluated and accounted for — zero silent omissions (DSC)
5. Destructive changes (branch deletion, permission changes) require confirmation unless `--auto`
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/repo.json` updated per scope + per API call, gitignored, deleted on successful Summary.

## Error Recovery

| Situation | Action |
|-----------|--------|
| GitHub API rate limited | Wait and retry once, then report partial results |
| Repository settings require admin access | Flag as needs-approval, list required permission changes |
| Branch protection rules conflict with workflow | Explain conflict, ask which takes priority |
| Stale branch detection ambiguous (active but old) | Ask user for staleness threshold |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Not a git repo | Stop with clear message |
| `gh` not available | Skip settings/protection scopes, warn |
| No GitHub remote | Skip API-dependent scopes |
| Fork repository | Note fork status, skip protection (forked from upstream) |
| Empty repository | Skip hygiene, minimal metadata check |
| Free private plan | Mark protection and auto-merge checks as N/A with reason |
| needs-input item in --auto mode | Skip with disposition `⚠ SKIPPED (requires input)` — list all skipped needs-input items prominently in summary section so they are not silently lost |
