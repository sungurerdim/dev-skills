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
| "auto-merge setup with branch protection" | "merge straight to main on solo project" (→ git merge, manual) |

## Contract

**Dimensions:** none (carrier)

**PR describes net diff between main and HEAD — nothing else.** Not journey of individual commits, not session decisions, not what was tried and reverted. If commit A added something and commit B removed it, net effect is zero — do not mention it.

Run `git diff {base}...HEAD` and describe what that diff shows.

- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- **Unattended carve-out (Unattended Mode rule 4, clause (b) — publishing):** under `--auto` this skill
  runs Phases 1–3 only (validate, tidy, quality gates, net-diff analysis) and then stops. It never pushes,
  never creates or updates a PR, and never merges — every one of those publishes. It prints the prepared
  title and body, records `pr: needs-human`, and names the command the user can run.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / needs-human); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** git history is the natural state — `git diff {base}...HEAD` always provides full context. No `ds/audit/pr.json` written.

**Pipeline:** `PR title → squash merge on main → release-please reads title → changelog + version bump`. PR title IS changelog entry. PR body becomes squash commit body. Everything must be accurate and minimal.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto-merge` | Opt in to auto-merge setup after the PR is created (off by default — merging is a human decision) |
| `--preview` | Show PR plan without creating |
| `--draft` | Create as draft PR (auto-merge never applies) |
| `--no-tidy` | Skip history tidy, push commits as-is |
| `--request-review` | After creation, request an automated Copilot review (`gh pr edit --add-reviewer "@copilot"`) |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

## Delegation

**Owns:** pull-request, net-diff-analysis, pr-title, pr-description | **Delegates:** ds-fix → pre-PR gates; ds-commit → staging before PR | **Receives:** ds-issue → PR opening after issue execution

## Execution Flow

Validate → History Tidy → Quality Gates → Analyze → Build → [Review] → Create → [Merge Setup] → [Cleanup] → [Needs-Approval] → Summary

### Phase 1: Validate

**Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → note relevant findings for PR body context. Stale → ignore.

**IDU:** Profile → {Project Map.Toolchain, Type + Stack}. Findings({pr}) → verify + use. Absent → own analysis.

**Steps 1-4 are independent — run in parallel:**

1. `git --version` and `gh auth status` → both exit 0, the latter showing `Logged in`
2. Git repo confirmed (`git rev-parse --is-inside-work-tree` → `true`); detect base branch (via GitHub API, fallback: main, then master)
3. `git branch --show-current` → non-empty (not detached) and ≠ `{base}`
4. `git fetch origin {base}`
5. `git rev-list --count origin/{base}..HEAD` → `0` → stop. `git rev-list --count HEAD..origin/{base}` → >0 (behind base) → ask rebase (--auto: rebase automatically)
6. `gh pr view --json url` → URL printed (existing PR) → show URL, ask: Update / Skip (`--auto`: Update automatically); non-zero exit → no existing PR, continue

**Gate:** All pre-checks passed; branch has commits ahead of base. If fails → stop with the specific check that failed:

| Failed check | Error / next action |
|-------------|---------------------|
| `git` / `gh` missing | "Install git/gh CLI and run `gh auth login`" |
| Not on a feature branch | "Checkout a feature branch first" |
| No commits ahead | "Nothing to push — commit your changes first" |
| `gh` unauthenticated | "Run `gh auth login` then retry" |
| Behind base | Offer `git rebase origin/{base}`, stop until user confirms |

### Phase 1.5: History Tidy (skip if --no-tidy or --preview)

If `git rev-list --count origin/{base}..HEAD` → >3 unpushed commits, offer to tidy: squash into logical commits based on net diff.

- Ask user: Tidy (recommended) or Keep as-is (--auto: tidy silently)
- Execute: `git reset --mixed origin/{base}`, stage and commit per plan
- On failure: `git reset --hard $ORIG_HEAD`
- Push: `git push -u origin {branch}`

**Gate:** Commits tidied (or skipped) and pushed to remote. If fails → if the tidy (git reset --mixed) fails, run `git reset --hard $ORIG_HEAD` to restore the branch and push the original commits as-is with a warning; if the push fails (rejected, no upstream), stop with error "Push failed — run `git push -u origin {branch}` manually and then retry /ds-pr".

### Phase 2: Quality Gates (changed files only)

Run format, lint, and test scoped to the PR's changed files (`git diff {base}...HEAD --name-only`) — a full-project pass is `/ds-fix`'s job, not this skill's. Auto-fix all fixable issues on that file set. Detect toolchain from config files. Skip silently if tool unavailable.

Run in order (stop on failure): Format → Lint → Secret scan → Test.
Format/lint changed files → commit as `chore: format and lint fixes`.
Tests fail → stop. Only create PR when tests covering the changed files pass.

**Secret scan ([references/principles.md §5](references/principles.md)):** Run secret-pattern detection on all changed files (same patterns as ds-fix security scope) before opening the PR. Any match → FAIL the gate. PR creation must not put credentials in front of human reviewers.

**Gate:** Format + lint + secret scan + tests all pass; no uncommitted fixes. If fails → hard stop, never create PR:

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

**Size note:** net diff exceeds PR-01 thresholds ([references/rules-pr.md](references/rules-pr.md): `git diff {base}...HEAD --shortstat` → >400 changed lines, or `git diff {base}...HEAD --name-only | wc -l` → >10 files) → append body note "Large PR — consider splitting for reviewability" (MEDIUM, informational — never blocks creation).

**Gate:** `git diff {base}...HEAD` read with non-empty output; PR title generated in conventional commit format (`printf '%s' "{title}" | wc -c` → ≤ 70). If fails → empty `git diff {base}...HEAD` (commits exist but net = 0) → stop with "Net diff is empty — all changes reverted in later commits. Nothing to describe."; ambiguous classification after net-diff override → default to most conservative non-bumping type, append WARN in PR body.

### Phase 4: Review (under `--auto`: stop here, see below)

Display: branch, title, body preview, version annotation.

**Version annotation:** Show version bump effect with each option:
- All signals agree: `version: {type} → {effect}`
- Net diff overrode commits: `version: ~{type} → {effect} (estimated)`

Effects:

| Type | Version effect |
|------|----------------|
| `feat` | minor bump |
| `fix` | patch bump |
| `feat!` / `fix!` | major bump |
| anything else | no bump |

Ask user:

- **Create + Auto-merge** (recommended) — squash + delete branch when checks pass
- **Create PR only** — merge manually later
- **Create as draft** — draft PR for further work
- **Cancel**

Under `--auto`: do NOT skip and do NOT proceed. Print the prepared title, body, and version annotation, record `pr: needs-human`, and stop before Phase 5 — creating a PR is on the irreversible-exception list because it is a human decision, not because it is unrecoverable. The summary names the branch and the command the user can run (`/ds-pr`).

**Gate:** User confirmed PR creation option. Title, body, and merge strategy decided. If fails → if the user selects Cancel, exit cleanly without creating a PR and without modifying the branch; if the user provides no response after one re-prompt, exit with "PR creation cancelled — re-run /ds-pr when ready."

### Phase 5: Create

1. Create with the body passed via heredoc — never interpolated into the shell string (W8):
   ```bash
   gh pr create --title "{title}" [--draft] --body-file - <<'EOF'
   {body}
   EOF
   ```
2. `--request-review` → `gh pr edit {number} --add-reviewer "@copilot"`; command fails (Copilot review unavailable) → warn, continue.
3. **Title-enforcement scaffold (advisory):** no workflow under `.github/workflows/` references `amannn/action-semantic-pull-request` → offer once: this skill validates only its own PR titles — a CI title gate catches non-agent PRs before they break the squash-merge → release-please changelog chain. Accept → generate the workflow file for review; decline → gap-note in summary. Never write without confirmation. Under `--auto`: resolves automatically per Unattended Mode rule 3 — the workflow file is generated (reversible via git, not on the irreversible-exception list) and noted in the summary.

**Gate:** PR created successfully. `gh pr create` returned PR URL. If fails → stop with explicit error from `gh pr create` output; do not proceed to Merge Setup; suggest: check `gh auth status`, verify the branch was pushed, and re-run /ds-pr --no-tidy to skip the tidy step if the branch state changed.

### Phase 6: Merge Setup [opt-in — only when `--auto-merge` is passed; never under `--draft` or `--auto`]

**Branch protection detection (first step):**

1. Query protection state: `gh api repos/{owner}/{repo}/branches/{base}/protection` (suppress 404)
2. **HTTP 200** (protection enabled) → `gh pr merge {number} --auto --squash`. Auto-merge will fire when CI passes.
3. **HTTP 404** (no protection) → check CI status via `gh run list --branch={branch} --limit=1`:
   - CI green → `gh pr merge {number} --squash`
   - CI pending → warn user, suggest manual merge after CI, exit without auto-merge
   - CI red → stop, do NOT merge, surface the failing run URL
4. **Force-push to main is never proposed**, regardless of protection state — flag in summary if user manually requests it.

After merge: `git checkout {base} && git pull origin {base} && git branch -d {branch}`

**Gate:** Auto-merge enabled or merge completed. Local branch switched to base. If fails → if `gh pr merge --auto` fails (no branch protection, CI not configured), warn the user and skip auto-merge — PR was already created; if the local checkout to base fails (`git checkout {base}`), warn and leave the user on the current branch; do not attempt branch cleanup in Phase 6.1 if checkout failed.

### Phase 6.1: Branch Cleanup [AFTER MERGE ONLY]

**Steps 1-2 are independent — run in parallel:**

1. Detect local merged branches: `git branch --merged {base}` (exclude base and current)
2. Detect remote merged branches: `git branch -r --merged origin/{base}` (exclude base and HEAD)
3. Combine results. Merged branches found:
   - Ask: Delete all (recommended) / Skip (--auto: delete all silently)
   - Delete local: `git branch -d {branch}`. Delete remote-only: `git push origin --delete {branch}`. On error: warn and continue.

**Gate:** All merged branches deleted locally and remotely, or cleanup skipped by user. If fails → for any individual branch deletion that errors (`git branch -d` or `git push origin --delete`), warn and continue with the remaining branches; surface all failed deletions in the Phase 8 summary so the user can clean them up manually.

### Phase 7: Needs-Approval Review [needs_approval > 0]

**Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. **Under `--auto`:** no review step is shown — every item resolves automatically using the same impact/effort/risk reasoning the interactive block would show, recorded in the summary; items matching the Unattended Mode rule-4 exception list are skipped and recorded `needs-human` instead.

**Gate:** All items resolved (applied → fixed/failed; declined → skipped). If fails → record unresolved item as `pending-user-decision`, proceed to Summary with WARN, list unresolved items.

### Phase 8: Summary

`pr: {OK|FAIL} | {pr-url} | {type} → {bump-effect} | auto-merge: {on|off}`

`Dispositions: Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

**Value Delivered:** 1-5 concrete bullets, real changes only — each states the effect in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity. Example shapes (placeholders, not literal output):

- `PR opened from net-diff analysis ({type} → {bump-effect}) — release-please will produce a clean changelog entry without journey noise`
- `{n} unpushed commits tidied into {m} logical groups — bisect can isolate any regression`
- `{n} secret patterns intercepted in pre-PR scan — credentials never reached human reviewers`
- `Auto-merge wired to branch protection — PR lands as soon as CI is green, no manual gatekeeping`

**Gate:** Summary line + PR URL + Value Delivered emitted. If fails → print PR URL on its own line (gh returned it); list incomplete phases (merge setup, cleanup) with the user's next manual action.

## Quality Gates

- PR description describes net diff — not journey of individual commits
- Every quality gate check (format, lint, test) gets a disposition in summary
- Conventional commit type on PR title matches net diff classification
- W9: not applicable — exempt from state protocol (atomic, git-driven, see Contract). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W13: the PR description reflects the verified net diff, not the author's claims about it; don't soften or inflate findings to match the PR narrative or reviewer authority.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| `gh` CLI not authenticated | Stop with clear error: "Run `gh auth login` first" |
| Rebase conflict during history tidy | Abort rebase (`git reset --hard $ORIG_HEAD`), push as-is, warn user |
| CI checks failing after PR creation | Warn user, skip auto-merge setup, suggest fixing and re-running |
| Remote branch already deleted | Create fresh remote branch from local, continue |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No commits ahead of base | Report "nothing to push", exit |
| PR already exists for branch | Show existing PR URL, ask if update needed |
| CI checks failing | Warn user, create PR but skip auto-merge setup |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
