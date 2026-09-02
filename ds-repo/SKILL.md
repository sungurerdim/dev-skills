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
- Standalone. Uses blueprint profile when available; `ds/audit/findings.md` only when fresh (`git_hash == HEAD` AND current run-cycle); own analysis otherwise.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: audit is regenerable; generated configs/fixes land in the working tree — git is the durable record.
- **publish/irreversible exception-list extension:** repo visibility changes (public↔private) and admin/permission changes are added to the exception list, citing "a business/legal decision not inferable from the repo" — these always resolve `only you can do`, never applied blind, whether or not `--ask` is set.

## Arguments

| Flag | Effect |
|------|--------|
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--preview` | Audit only, no changes |
| `--scope={x}` | Specific scope(s), comma-separated |
| `--oss-ready` | OSS-readiness mode (see `oss-readiness` scope below) — shorthand for `--scope=oss-readiness`, the same scope by its own name |

Without flags: Full Audit & Fix runs directly — every scope scanned, Category A fixes applied, Category B fixes applied by best judgment and recorded (the publish/irreversible exception list resolves `only you can do` instead of applying blind). `--ask` presents a menu: Full Audit (recommended — scan every scope, report only) / Audit & Fix / Scoped (`--scope`) / OSS-ready (`--oss-ready`) / (Cancel).

## Scopes

8 scopes, each an explicit checklist. Every check evaluated on every run — no check silently omitted. Full per-check detect/fix detail: [references/rules-repo.md](references/rules-repo.md) Scope Checklists (`security` = RPO-12–15).

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| settings | any source | — |
| protection | any source | — |
| hygiene | any source | — |
| metadata | any source | — |
| team | any source | — |
| structure | any source | — |
| security | any source | — |
| oss-readiness | `--oss-ready`, `--scope=oss-readiness`, or `public_repo=yes` | N/A — private repo and flag/scope not given |

| Scope | Reference | Loaded when |
|-------|-----------|-------------|
| settings, protection, hygiene, metadata, team, structure, security, oss-readiness | references/rules-repo.md | scope resolves to run |

**Not in scope:** CI/CD pipelines and dependency management. Code-level security audit delegated to `/ds-compliance`.

## Delegation

**Owns:** repo-settings, branch-protection, repo-hygiene, repo-metadata, team, structure, oss-readiness (`--oss-ready` mode) | **Delegates:** ds-docs → LICENSE / CONTRIBUTING / SECURITY content generation; ds-deps → transitive dependency-tree license scan + SBOM export (oss-readiness check 2) | **Receives:** ds-ship → Phase 5 repo pass

## Execution Flow

Setup → Audit → Gap Analysis → [Plan Review] → [Apply] → [Needs-Approval] → Summary

### Phase 1: Setup

1. `git --version` → exit 0 and `gh auth status` → exit 0 — `git` required; `gh` required for settings/protection scopes.
2. Detect repo info via GitHub API: name, default branch, visibility, description, topics, license, homepage, plan.
3. **Upstream artifacts:** Profile → {Type + Stack, `Constraints:`}. Findings({repo}) → verify + use. Absent → own analysis.
4. **Mode selection.** A disambiguating flag skips this step. Without one: Full Audit & Fix runs directly (the default). `--ask`: present a menu of every mode — Full Audit (recommended — scan every scope, report only) / Audit & Fix / Scoped (`--scope`) / OSS-ready (`--oss-ready`) / (Cancel).
5. **Scope selection.** `--scope={x}` → restrict to the named scopes. No `--scope` → every scope runs. `--ask` with no `--scope` → ask which scopes before proceeding.

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
| {n}| metadata  | Homepage URL         | only you can do: URL required           |
| {n}| protection| Branch protection    | N/A ({plan-or-context-limitation})  |
```

**Severity:** CRITICAL > HIGH > MEDIUM > LOW > INFO.

**Gate:** Complete checklist table — every check from every scope appears. If fails → missing rows → re-run the affected checks, reconstruct missing rows; unrecoverable → add row with `result: "ERROR: data unavailable"` rather than leaving absent.

### Phase 4: Plan Review [--ask]

Default: proceed straight to Apply, resolving each finding by best judgment — Category A fixes applied automatically; Category B applied using the same impact/effort/risk reasoning an approval block would show, recorded in the summary; needs-approval items handled in Phase 6 under its own rule. Without `--ask` this phase does not run. `--ask`: ask user Fix All / By Severity / Review Each / Report Only.

**only you can do findings:** before Apply, resolve each. Default: a value only a human can supply matches the publish/irreversible exception list — skip and record `only you can do`, never guessed. `--ask`: ask each one, e.g. "Homepage URL is empty — do you have a URL to set? (provide URL / skip)".

**Gate:** Action plan resolved (default or `--ask` selection); only you can do items resolved. If fails → `--ask` re-prompt exhausted with no selection → default Report Only (no changes); only you can do declined → record `skipped (user declined input)`, list prominently in Phase 7 summary.

### Phase 5: Apply [SKIP if --preview]

Apply fixes via GitHub API (settings, protection), git commands (hygiene), file operations (config files).

Per finding, assign disposition:

- `fixed` — applied and verified: re-run the same `gh api` read → response shows the new value, or `test -f`/`grep` on the touched file → expected content present
- `failed` — attempted but API/command returned error
- `skipped` — user declined, platform limitation, or N/A (with reason)
- `needs-approval` — protection changes affecting other contributors, CODEOWNERS modifications, visibility changes. Default: resolved immediately using the same impact/effort/risk reasoning an approval block would show — applied and disposition `fixed`, except exception-list items (repo visibility, admin/permission changes, unmerged-branch deletion, history rewrite), which resolve `only you can do`. `--ask`: held for Phase 6 instead.

**Gate:** Every finding has a disposition. `fixed + failed + skipped + needs_approval = total`. If fails → missing disposition → assign `failed (disposition not recorded)`; API call error → record `failed` with API error message and continue.

### Phase 6: Needs-Approval Review [--ask, needs_approval > 0]

Without `--ask` this phase does not run — every needs-approval item was already resolved in Phase 5 by best judgment or recorded `only you can do` per the exception list. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → record `pending-user-decision`, proceed to Summary with WARN, list unresolved in disposition table.

### Phase 7: Summary

```
repo: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

`Scopes: ran {settings, protection, hygiene, metadata, team, structure, security} · {oss-readiness: ran | N/A — public_repo=no and --oss-ready not given}`

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

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `Branch protection wired (required reviews, status checks, dismiss-stale) — accidental main-branch overwrites and unreviewed merges blocked`
- `Squash-only merge + delete-branch-on-merge enabled — commit history stays linear, stale branches no longer accumulate`
- `{n} stale + merged branches cleaned up — repo browse / clone / list-branches latency drops`
- `CODEOWNERS wired for {n} critical paths — review routing automatic, no orphaned PRs`

Zero-change run: `Repo settings already match policy — no changes applied`.

**Gate:** Summary + Effect rendered; accounting reconciles; every scope's checks present. If fails → counts don't reconcile → list all findings with dispositions inline to expose discrepancy, status `WARN` with "Disposition count mismatch — review the table above"; missing scope checks → reconstruct from state and append.

## Quality Gates

- Settings changes verified via API read-back
- **Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)), before the first repo-file write (CODEOWNERS, templates, workflow files): `git status --porcelain` → empty → proceed; a dirty path the planned write touches → default: proceed only when disjoint from every dirty path, else record `only you can do` for that write; `--ask`: Commit first (recommended) / Stash / Proceed anyway. API-side settings changes need no checkpoint — verified by read-back, reverted by the same API call.
- **Mechanical Done Gate:** resolve `{check-cmd}` once at setup — the ds-quality enforcement arm when installed, else the stack-native format → lint → type → test chain from [../core/toolchains.md](../core/toolchains.md); capture the baseline; re-run after each change batch and once in aggregate before reporting done. New red → fix (≤3 attempts, same command), then revert the offending change and record `reverted`; baseline red is reported red-at-baseline, never inherited; no tooling detectable → report the Verification-Infrastructure Gap, never skip silently.
- Scope boundary — only modify what was requested
- Every finding gets a disposition
- Every scope check evaluated and accounted for
- Destructive changes: merged-branch deletion + reversible settings resolve automatically by best judgment (Category A/B default); UNMERGED (stale) branch deletion, permission changes, and visibility changes always resolve `only you can do` by default and confirm per item under `--ask` — no flag bypasses this (the publish/irreversible exception list)
- W9: state-exempt — audit is regenerable, working tree + git are the durable record. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| GitHub API rate limited | Wait + retry once, then report partial results |
| Repository settings require admin access | Flag as needs-approval, list required permission changes |
| Branch protection rules conflict with workflow | Default: keep the stricter rule, record the conflict and reasoning. `--ask`: explain conflict, ask which takes priority. |
| Stale branch detection ambiguous (active but old) | Default: keep the 30-day threshold (hygiene scope default), record the assumption. `--ask`: ask user for a different threshold. |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Not a git repo | Stop with clear message |
| `gh` not available | Skip settings/protection scopes, warn |
| No GitHub remote | Skip API-dependent scopes |
| Fork repository | Note fork status, skip protection (forked from upstream) |
| Empty repository | Skip hygiene, minimal metadata check |
| Free private plan | Mark protection + auto-merge checks as N/A with reason |
| only you can do, default (no `--ask`) run | Record `only you can do` (a value only a human can supply, e.g. homepage URL) — list prominently in summary |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
