---
name: ds-pr
description: Smart pull requests — Conventional Commit title and clean body for release-please. Use when opening or formatting a pull request.
---

# /ds-pr

PR descriptions that list every commit instead of net change create noise, confuse reviewers, and break changelogs. This skill describes what the diff actually shows.

**Smart Pull Requests** — Conventional commit title + clean body for release-please.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-pr`
- User asks to create a pull request, open a PR, or prepare changes for merge
- User says "create PR", "open PR", or "submit for review"
- After successful commit, suggest PR creation if on a feature branch

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "open a pull request", "create PR for this branch" | "commit my changes" (→ ds-commit) |
| "tidy commit history before PR + push" | "format my code" (→ ds-fix) |
| "PR title + description from net diff" | "release notes for App Store" (→ ds-launch --release) |
| "prepare the push and PR-create commands" | "merge straight to main on solo project" (→ git merge, manual) |

## Contract

**Dimensions:** none (carrier)

**PR describes net diff between main and HEAD — nothing else.** Not journey of individual commits, not session decisions, not what was tried and reverted. If commit A added something and commit B removed it, net effect is zero — do not mention it.

Run `git diff {base}...HEAD` and describe what that diff shows.

- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- **Push and PR-create are publishing — only you can do by default.** No flag: the skill validates, tidies, runs quality gates, and analyzes the net diff, then stops before Push with the prepared title, body, and the exact commands recorded `only you can do`. It never pushes, creates, updates, or merges a PR on its own. `--ask`: same preparation, then a confirmation at Push and again at Create before either command runs.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** git history is the natural state — `git diff {base}...HEAD` always provides full context. No `ds/audit/pr.json` written.

**Pipeline:** `PR title → squash merge on main → release-please reads title → changelog + version bump`. PR title IS changelog entry; PR body becomes squash commit body.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Show PR plan without creating |
| `--draft` | Create as draft PR |
| `--no-tidy` | Skip history tidy, push commits as-is |
| `--request-review` | After creation, request an automated Copilot review (`gh pr edit --add-reviewer "@copilot"`) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

## Delegation

**Owns:** pull-request, net-diff-analysis, pr-title, pr-description | **Delegates:** ds-fix → pre-PR gates; ds-commit → staging before PR | **Receives:** ds-issue → PR after issue execution

## Execution Flow

Validate → History Tidy → Quality Gates → Analyze → [Review Disposition] → Review → Push → Create → [Needs-Approval] → Summary

### Phase 1: Validate

**Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → note relevant findings for PR body context. Stale → ignore.

**Upstream artifacts:** Profile → {`Toolchain:`, Type + Stack}. Findings({pr}) → verify + use. Absent → own analysis.

**Steps 1-4 are independent — run in parallel:**

1. `git --version` and `gh auth status` → both exit 0, the latter showing `Logged in`
2. Git repo confirmed (`git rev-parse --is-inside-work-tree` → `true`); detect base branch (via GitHub API, fallback: main, then master)
3. `git branch --show-current` → non-empty (not detached) and ≠ `{base}`
4. `git fetch origin {base}`
5. `git rev-list --count origin/{base}..HEAD` → `0` → stop. `git rev-list --count HEAD..origin/{base}` → >0 (behind base) → Default: rebase automatically, no prompt. `--ask`: ask rebase.
6. `gh pr view --json url,number,state` → URL printed (existing PR) → Default: show the URL, update automatically, no prompt. `--ask`: show URL, ask Update / Skip. Non-zero exit → no existing PR, continue.
7. **Update path — canonical PR read:** `gh pr view {n} --json url,number,state,body,comments,reviews` **plus** the line-level threads (`gh api repos/{owner}/{repo}/pulls/{n}/comments`) — not optional: a body-only read leaves a reviewer's requested change unanswered. Hand the result to Phase 3.5.

**Gate:** All pre-checks passed; branch has commits ahead of base. If fails → stop, name the failed check, and show its next action from [references/rules-pr.md](references/rules-pr.md) Pre-flight Check Failures.

### Phase 1.5: History Tidy (skip if --no-tidy or --preview)

If `git rev-list --count origin/{base}..HEAD` → >3 unpushed commits, tidy: squash into logical commits based on net diff.

- **Checkpoint pre-gate (stop-hard, [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)):** `git status --porcelain` → non-empty → the tidy does not start in any mode: its failure path is `git reset --hard $ORIG_HEAD`, which would destroy uncommitted work. Default: skip the tidy, record `skipped (dirty working tree — commit or stash before tidying)`, continue with the PR as-is — no prompt. `--ask`: show the dirty files, ask Commit first (recommended) / Stash / Skip tidy. Empty output → record `$ORIG_HEAD=$(git rev-parse HEAD)` and proceed.
- Default: tidy silently (the recommended default) — no prompt. `--ask`: ask Tidy (recommended) / Keep as-is.
- Execute: `git reset --mixed origin/{base}`, stage and commit per plan.
- On failure: `git reset --hard $ORIG_HEAD` (safe only because the pre-gate proved a clean tree).
- The tidied commits stay local — publishing them is the Push phase's job (below), never this one.

**Gate:** Commits tidied (or skipped) locally. If fails → the tidy (`git reset --mixed`) fails → run `git reset --hard $ORIG_HEAD` to restore the branch to its pre-tidy state, continue with the original commits as-is, and note the fallback in the summary.

### Phase 2: Quality Gates (changed files only)

Run format, lint, and test scoped to the PR's changed files (`git diff {base}...HEAD --name-only`) — a full-project pass is `/ds-fix`'s job, not this skill's. Auto-fix all fixable issues on that file set. Detect toolchain from config files. Skip silently if tool unavailable.

Run in order (stop on failure): Format → Lint → Secret scan → Test.
Format/lint changed files → commit as `chore: format and lint fixes`.
Tests fail → stop. Only prepare a PR when tests covering the changed files pass.

**Secret scan ([../core/principles.md §5](../core/principles.md)):** Run secret-pattern detection on all changed files (same patterns as ds-fix security scope) before preparing the PR. Any match → FAIL the gate. A PR must not put credentials in front of human reviewers.

**Gate:** Format + lint + secret scan + tests all pass; no uncommitted fixes. If fails → hard stop, never prepare a PR:

- **Secret hit** → stop, output `{file}:{line}`, instruct user to remove secret + rotate credentials before retry.
- **Test failure** → stop, show failing test names.
- **Format/lint unfixable** → stop, list violations.

### Phase 3: Analyze

`git diff {base}...HEAD` is THE source of truth. PR quality rules: [references/rules-pr.md](references/rules-pr.md).

**Net diff principle:** PR describes final state difference, not development journey.

**Type classification:**
1. Scan commit titles for initial signal
2. Validate against net diff — net diff overrides:
   - New user-facing capability? → `feat`
   - Broken behavior fixed? → `fix`
   - Neither? → dominant non-bumping type
3. `!` in any commit type or `BREAKING CHANGE:` → append `!`

**Title:** `{type}({scope}): {summary}` — max 70 chars (`printf '%s' "{title}" | wc -c` → ≤ 70).

**Body:** Summary (1-3 bullets), Changes (grouped, max 5), Breaking Changes (if any). Max 20 lines (`wc -l` on the body → ≤ 20).

**Size note:** net diff exceeds PR-01 thresholds ([references/rules-pr.md](references/rules-pr.md): `git diff {base}...HEAD --shortstat` → >400 changed lines, or `git diff {base}...HEAD --name-only | wc -l` → >10 files) → append body note "Large PR — consider splitting for reviewability" (MEDIUM, informational — never blocks preparation).

**Gate:** `git diff {base}...HEAD` read with non-empty output; PR title generated in conventional commit format (`printf '%s' "{title}" | wc -c` → ≤ 70). If fails → empty `git diff {base}...HEAD` (commits exist but net = 0) → stop with "Net diff is empty — all changes reverted in later commits. Nothing to describe."; ambiguous classification after net-diff override → default to most conservative non-bumping type, append WARN in PR body.

### Phase 3.5: Review Disposition [Update path only] [GATE]

Runs on the Update path (Phase 1); skipped for a first-time PR — nothing has been reviewed yet.

1. From the Phase 1 step 7 read, list every reviewer-borne item the update has to answer: `CHANGES_REQUESTED` reviews, unresolved review threads, and comment-borne requests (items posted after the last push are the prime suspects). This skill's own prior comments are not requirements.
2. Each item gets exactly one disposition **before** the PR is updated or pushed: **addressed** — the net diff already carries it, cited `file:line`; **rejected** — replied to on its own thread with the reason (per-item confirm); **deferred** — a follow-up issue filed, its number quoted in the reply. Leaving an item with none of the three and still updating the PR is FORBIDDEN. Default: each item's disposition resolves by best judgment from the evidence (net diff, thread content) and is recorded — no prompt; the run still stops before Push, so the human reviews everything before anything publishes. `--ask`: confirm each item's disposition individually before the PR body is finalized.
3. The rebuilt PR body states what changed since the last review round, one line per addressed item.

**Gate:** every reviewer-borne item carries one of the three dispositions with its evidence. If fails → an item left undispositioned → stop before the update, list those items with their thread URLs, and ask for a decision; `gh api …/pulls/{n}/comments` unavailable (older `gh`, permissions) → disposition the review-level items, record the line-level gap in the summary, and mark the run WARN.

### Phase 4: Review

Display: branch, title, body preview, version annotation.

**Version annotation:** Show version bump effect:
- All signals agree: `version: {type} → {effect}`
- Net diff overrode commits: `version: ~{type} → {effect} (estimated)`

Effects:

| Type | Version effect |
|------|----------------|
| `feat` | minor bump |
| `fix` | patch bump |
| `feat!` / `fix!` | major bump |
| anything else | no bump |

Default: the prepared title, body, and version annotation print as-is; the branch is not yet pushed and no PR exists yet — both are handled by the next two phases, each recorded `only you can do` unless confirmed under `--ask` — no prompt here. `--ask`: same preview, plus a chance to change it before Push runs — Accept as shown (recommended) / Edit / (Cancel).

**Gate:** Title, body, and version annotation prepared and shown. If fails → net diff produced no usable title (Phase 3's gate already covers an empty net diff) → stop, nothing to review; under `--ask`, the user selects Cancel → exit cleanly without pushing or creating a PR.

### Phase 5: Push

Pushing publishes local commits to the remote — the publish clause of the ask-exception list.

Default: record `push: only you can do` with the exact command — `git push -u origin {branch}` — and stop before Create, no prompt. `--ask`: ask Push now (recommended) / Skip; confirmed → run `git push -u origin {branch}`.

**Gate:** Branch pushed, or `push: only you can do` recorded with the exact command. If fails → push rejected (remote diverged, no permission) → stop, show the `git push` error, suggest `git pull --rebase origin {branch}` then retry; never proceed to Create with an unpushed branch.

### Phase 6: Create

Creating or updating a PR publishes it to reviewers — the publish clause of the ask-exception list.

1. Default: record `pr: only you can do` with the exact command shown, stop — no `gh pr create` call made. Push above recorded `only you can do` (branch not yet pushed) → the recorded command is prefixed with the push command it depends on. `--ask`: confirm, then create with the body passed via heredoc — never interpolated into the shell string (W8):
   ``bash
   gh pr create --title "{title}" [--draft] --body-file - <<'EOF'
   {body}
   EOF
   ``
2. `--request-review` → `gh pr edit {number} --add-reviewer "@copilot"`; command fails (Copilot review unavailable) → warn, continue.
3. **Title-enforcement scaffold (advisory):** no workflow under `.github/workflows/` references `amannn/action-semantic-pull-request` → this skill validates only its own titles; a CI gate catches non-agent PRs before they break the squash-merge → release-please chain. Default: generate the workflow file (reversible via git) and note it in the summary. `--ask`: accept → generate for review; decline → gap-note.

**Auto-merge and post-merge cleanup are out of scope.** "Create PR only" is the only outcome this skill produces — merging is the human's decision (GitHub UI, `gh pr merge`, or a branch-protection auto-merge rule); what happens after merge is the human's call or a release workflow's (e.g. `/ds-release`).

**Gate:** PR created (`--ask`, confirmed), or `pr: only you can do` recorded with the exact command (default). If fails → `gh pr create` returned an error → stop, show the error, suggest checking `gh auth status` and that the branch was pushed; never fabricate a PR URL.

### Phase 7: Needs-Approval Review [needs_approval > 0]

Default: every item resolves by best judgment using the same impact/effort/risk reasoning an approval block would show, recorded in the summary; items matching the publish/irreversible exception list are skipped and recorded `only you can do` instead — no review step shown. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → record unresolved item as `pending-user-decision`, proceed to Summary with WARN, list unresolved items.

### Phase 8: Summary

`pr: {OK|FAIL} | {pr-url-or-only you can do} | {type} → {bump-effect}`

`Dispositions: Fixed: {n} | Skipped: {n} | Failed: {n} | Only you can do: {n} | Total: {n}`

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `PR prepared from net-diff analysis ({type} → {bump-effect}) — release-please will produce a clean changelog entry without journey noise`
- `{n} secret patterns intercepted in pre-PR scan — credentials never reached human reviewers`
- `Push and PR-create commands prepared and verified — one confirmation away from publishing, with zero risk of an unreviewed push`

**Gate:** Summary line + Effect emitted. If fails → PR created → print its URL on its own line; PR not created (`only you can do`) → print the exact push + create commands the human can run; list any incomplete phases with the user's next manual action.

## Quality Gates

- PR description describes net diff — not journey of individual commits
- **Update path: every reviewer-borne item dispositioned** (addressed with `file:line` / rejected with a thread reply / deferred to a filed issue) before the PR is updated — an unanswered requested change blocks the update (Phase 3.5)
- Every quality gate check (format, lint, test) gets a disposition in summary
- **Mechanical Done Gate:** resolve `{check-cmd}` once at setup — the ds-quality enforcement arm when installed, else the stack-native format → lint → type → test chain from [../core/toolchains.md](../core/toolchains.md); capture the baseline; re-run after each change batch and once in aggregate before reporting done. New red → fix (≤3 attempts, same command), then revert the offending change and record `reverted`; baseline red is reported red-at-baseline, never inherited; no tooling detectable → report the Verification-Infrastructure Gap, never skip silently.
- Conventional commit type on PR title matches net diff classification
- W9: not applicable — exempt from state protocol (atomic, git-driven, see Contract). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W13: PR description reflects the verified net diff, never softened to match the PR narrative or reviewer authority.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| CI checks failing after PR creation | Warn user, suggest fixing and re-running — merging is the human's call regardless of CI state |
| Remote branch already deleted | Create fresh remote branch from local, continue |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| PR already exists for branch | Update path (Phase 1 step 6): show URL, update automatically; `--ask` offers Skip. Phase 3.5 dispositions every reviewer item first. |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
