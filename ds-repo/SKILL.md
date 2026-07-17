---
name: ds-repo
description: Repository health — audit and configure repo settings, branch policies, hygiene, metadata, team, and structure. Use when setting up or auditing repository configuration.
---

# /ds-repo

Unprotected main branches, stale branches piling up, missing CODEOWNERS, no branch policies — most repos are misconfigured from day one. This skill audits and fixes it.

**Repository Health** — Audit and configure repo settings, branch policies, hygiene, metadata, team, and structure.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-repo`
- User asks to audit or configure repo settings, branch protection, or CODEOWNERS
- User asks about stale branches, repo hygiene, or team structure
- User asks to set up a new repository or fix repo configuration

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit repo settings", "set up branch protection" | "audit code quality inside the repo" (→ ds-review) |
| "configure CODEOWNERS, OSS-ready files" | "license / regulatory research" (→ ds-research) |
| "clean up stale / merged branches" | "tidy commit history of a branch" (→ ds-pr --tidy) |
| "configure squash-only merge + delete-on-merge" | "audit CI workflows" (→ ds-devops) |

## Contract

**Dimensions:** B4 (contributor), D8

- Only manages repository settings and structure — not code quality.
- Every recommendation cites a specific setting or file.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | All scopes, no questions, fix everything |
| `--preview` | Audit only, no changes |
| `--scope={x}` | Specific scope(s), comma-separated |
| `--oss-ready` | OSS-readiness mode (see `oss-readiness` scope below) |
| `--force-approve` | Apply `needs_approval` items without asking (CRITICAL + unmerged-branch deletion still confirm per item) |

No flags → present mode selection.

## Scopes

Each scope defines an explicit checklist. Every check evaluated on every run — no check silently omitted (DSC).

### settings (5 checks)

1. **Merge strategy** — squash-only (`allow_squash_merge=true`, `allow_merge_commit=false`, `allow_rebase_merge=false`)
2. **Commit title format** — `PR_TITLE` (`squash_merge_commit_title`)
3. **Commit message format** — `PR_BODY` (`squash_merge_commit_message`)
4. **Delete branch on merge** — enabled (`delete_branch_on_merge=true`)
5. **Auto-merge** — enabled (`allow_auto_merge=true`)

### protection (7 checks)

1. **Branch protection enabled** — default branch has protection rules
2. **Required reviews** — at least 1 required reviewer
3. **Required status checks** — CI must pass before merge
4. **Dismiss stale reviews** — enabled when new commits pushed
5. **Ruleset coverage** — detect via `gh api repos/{owner}/{repo}/rulesets` alongside classic branch protection (`gh api repos/{owner}/{repo}/branches/{branch}/protection`); org plan supports repository rulesets and none exist → recommend migrating to rulesets (layered enforcement, bypass audit log); no ruleset support → classic branch protection is the valid fallback, not a finding
6. **Ruleset bypass list** — ruleset lists admins/broad roles in its bypass list with no documented justification → HIGH finding; classic "do not allow bypassing" maps to an empty bypass list, and GitHub's auto-migration can pre-populate admins into it — silently weakening protection. Keep the bypass list empty unless a justification note exists. N/A when no ruleset exists
7. **Push ruleset** — ruleset-only capability with no classic counterpart: blocks restricted file paths (`.env`, secret-pattern files), extensions, and oversized files at the push layer across the entire fork network; plan supports rulesets and none exists → LOW opportunity finding (complements the oss-readiness git-secret-history check); no ruleset support → N/A

### hygiene (4 checks)

1. **Stale branches** — no open PR + last commit > 30 days ago. UNMERGED work — deletion loses commits: always `needs-approval`, confirmed per item even under `--auto`/`--force-approve`; never bulk-deleted
2. **Merged branches** — already merged into default but not deleted (commits preserved in base — safe to bulk-delete after one confirmation)
3. **Orphan remotes** — remote-tracking refs whose upstream no longer exists (`git remote prune` — safe)
4. **History bloat** — blobs > 10 MB in history inflating every clone (`git rev-list --objects --all` + `git cat-file --batch-check` size sort). Finding proposes `git filter-repo --strip-blobs-bigger-than <size>` (the recommended tool — not `git filter-branch` or BFG) + post-rewrite `git gc`, with LFS migration as the keep-the-file alternative. History rewrite is destructive and breaks every existing clone: always `needs-approval` with an explicit team-coordination + backup warning, never autonomous — same rule as the git-secret-history surgery (oss-readiness check 15)

### metadata (7 checks)

1. **Description** — non-empty repo description
2. **Topics** — at least 3 relevant topics
3. **License** — license file present (MEDIUM on public, LOW on private)
4. **Homepage URL** — non-empty
5. **README badges** — CI status badge present in README
6. **Social preview** — custom social preview image (public repos only, N/A on private)
7. **Tags/releases strategy** — semver tags, tag count matches release count

### team (2 checks)

1. **CODEOWNERS** — present for team repos (>1 contributor), N/A for solo
2. **CONTRIBUTING.md** — present for public repos, N/A for private solo

### structure (3 checks)

1. **`.gitignore` completeness** — IDE, OS, language-specific entries present
2. **Config file sprawl** — no multiple competing configs for same tool
3. **Codebase (Twelve-Factor #1)** — one repo tracks one deployable app across many deploys: repo hosts multiple unrelated deployable apps without workspace/monorepo tooling boundaries, or app code is duplicated across separate repos instead of shared via a package → flag

### oss-readiness (16 checks — activated by `--oss-ready` flag or explicit scope selection)

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
15. **Git secret history** — scan git history for hardcoded secrets (`git log -p -S"api_key"` / `git-secrets --scan-history` / `trufflehog`). Any hit → Category B finding with `git-filter-repo` surgery proposal; autonomous deletion is forbidden.
16. **SPDX file headers** — source files carry a case-sensitive `SPDX-License-Identifier: <expr>` comment at/near the top; the declared identifier matches the LICENSE file. Missing headers → LOW finding with bulk-add proposal (Category A — mechanical, no public-facing text change)

OSS-readiness emits Category B findings for anything user-visible (README rewrites, LICENSE changes, trademark concerns). Templates, metadata, Dependabot config may be Category A when they don't alter public-facing text.

**Trademark / name collision check (part of check 10):** Brief search for project name against USPTO / EUIPO common-term lookup. Ambiguous or conflicting → HIGH finding with "consult legal counsel" suggestion.

**Not in scope:** CI/CD pipelines and dependency management. Code-level security audit delegated to `/ds-compliance`.

## Delegation

**Owns:** repo-settings, branch-protection, repo-hygiene, repo-metadata, team, structure, oss-readiness (`--oss-ready` mode) | **Delegates:** ds-docs → LICENSE / CONTRIBUTING / SECURITY content generation; ds-deps → transitive dependency-tree license scan + SBOM export (oss-readiness check 2) | **Receives:** ds-ship → Phase 5 repo pass

## Execution Flow

Setup → Audit → Gap Analysis → Plan Review → Apply → [Needs-Approval] → Summary

### Phase 1: Setup

1. Verify `git` + `gh` CLI available and authenticated — `git` required; `gh` required for settings/protection scopes.
2. Detect repo info via GitHub API: name, default branch, visibility, description, topics, license, homepage, plan.
3. **IDU:** Profile → {Type + Stack, Config.constraints}. Findings({repo}) → verify + use. Absent → own analysis.
4. **Mode selection.** No flags → present a menu of every mode: Full Audit (recommended — scan every scope, report only), Audit & Fix (`--auto`), Scoped (`--scope`), OSS-ready (`--oss-ready`), (Cancel). A disambiguating flag skips the menu.
5. **Scope selection.** Scoped mode or no `--scope` with Audit & Fix → ask which scopes.

**Gate:** Repo info retrieved + mode/scopes selected. If fails → `gh` unavailable/unauthenticated → skip settings + protection scopes, warn, proceed with hygiene/metadata/structure/team using local git only; API error → record what was retrievable, continue; no mode/scope selection → default Full Audit across all scopes.

### Phase 2: Audit

Run every check in every selected scope per [references/rules-repo.md](references/rules-repo.md). Each check produces exactly one outcome:

- **Finding** — issue detected (with severity)
- **Pass (✅)** — check executed, no issue
- **N/A** — check cannot apply (with reason: "private repo", "solo contributor", "free plan")

Evaluate checks in order as listed in each scope.

**Gate:** All checks in all selected scopes evaluated; zero silently omitted. If fails → unevaluable check (API unavailable, permissions, unsupported plan) → record `N/A` with explicit reason; surface all N/A in Phase 3 gap table so they remain visible.

### Phase 3: Gap Analysis

Display findings table with ALL checks accounted:

```
| # | Scope      | Check                | Result                              |
|---|------------|----------------------|-------------------------------------|
| {n}| settings  | Merge strategy       | ✅ squash-only                      |
| {n}| settings  | Commit title         | MEDIUM: {expected-format-not-set}   |
| {n}| metadata  | Homepage URL         | needs-input: URL required           |
| {n}| protection| Branch protection    | N/A ({plan-or-context-limitation})  |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW > INFO.

**Gate:** Complete checklist table — every check from every scope appears. If fails → missing rows → re-run the affected checks, reconstruct missing rows; unrecoverable → add row with `result: "ERROR: data unavailable"` rather than leaving absent.

### Phase 4: Plan Review [SKIP if --auto]

Ask user: Fix All / By Severity / Review Each / Report Only.

**needs-input findings:** before Apply, resolve each. Example: "Homepage URL is empty — do you have a URL to set? (provide URL / skip)".

**Gate:** User selected action plan; needs-input items resolved. If fails → no action selection after re-prompt → default Report Only (no changes); needs-input declined → record `skipped (user declined input)`, list prominently in Phase 7 summary.

### Phase 5: Apply [SKIP if --preview]

Apply fixes via GitHub API (settings, protection), git commands (hygiene), file operations (config files).

Per finding, assign disposition:

- `fixed` — applied and verified via API read-back or file check
- `failed` — attempted but API/command returned error
- `skipped` — user declined, platform limitation, or N/A (with reason)
- `needs-approval` — protection changes affecting other contributors, CODEOWNERS modifications, visibility changes

**Gate:** Every finding has a disposition. `fixed + failed + skipped + needs_approval = total`. If fails → missing disposition → assign `failed (disposition not recorded)`; API call error → record `failed` with API error message and continue.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → record `pending-user-decision`, proceed to Summary with WARN, list unresolved in disposition table.

### Phase 7: Summary

```
repo: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

Disposition table — every finding from Gap Analysis appears with final status:

```
| # | Finding                  | Disposition                              |
|---|--------------------------|------------------------------------------|
| {n}| {finding-title}         | {fixed-✅ / skipped (reason) / failed}    |
```

Clean checks — scopes where all checks passed:

```
Clean: settings ({n}/{n} ✅), structure ({n}/{n} ✅)
```

**Value Delivered:** 1-5 concrete bullets, real repo-config outcomes only. Example shapes (placeholders, not literal):

- `Branch protection wired (required reviews, status checks, dismiss-stale) — accidental main-branch overwrites and unreviewed merges blocked`
- `Squash-only merge + delete-branch-on-merge enabled — commit history stays linear, stale branches no longer accumulate`
- `{n} stale + merged branches cleaned up — repo browse / clone / list-branches latency drops`
- `CODEOWNERS wired for {n} critical paths — review routing automatic, no orphaned PRs`

Zero-change run: `Repo settings already match policy — no changes applied`.

**Gate:** Summary + Value Delivered rendered; accounting reconciles; every scope's checks present. If fails → counts don't reconcile → list all findings with dispositions inline to expose discrepancy, status `WARN` with "Disposition count mismatch — review the table above"; missing scope checks → reconstruct from state and append.

## Quality Gates

- Settings changes verified via API read-back
- Scope boundary — only modify what was requested
- Every finding gets a disposition (FRC)
- Every scope check evaluated and accounted for (DSC)
- Destructive changes: merged-branch deletion + reversible settings may batch under `--auto`; UNMERGED (stale) branch deletion, permission changes, and visibility changes always confirm per item — no flag bypasses this (All-Affordance rule 2)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| GitHub API rate limited | Wait + retry once, then report partial results |
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
| Free private plan | Mark protection + auto-merge checks as N/A with reason |
| needs-input in `--auto` mode | Skip with `⚠ SKIPPED (requires input)` — list prominently in summary |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
