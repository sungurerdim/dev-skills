---
name: ds-commit
description: Smart commits — quality gates, atomic grouping, Conventional Commits formatting. Use when committing changes, grouping a working tree into atomic commits, or writing commit messages.
---

# /ds-commit

AI commits are vague ("update code"), bundle unrelated changes, and skip pre-commit checks. Skill reads diff, groups changes logically, and writes precise conventional commit messages.

**Smart Commits** — Quality gates + atomic grouping + conventional commit format.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-commit`
- User asks to commit, stage and commit, save work as a commit
- Trigger only on explicit commit request — staging alone is not a commit request

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "commit my changes", "save my work as a commit" | "create a pull request" (→ ds-pr) |
| "split this into atomic conventional commits" | "format my code" (→ ds-fix) |
| "stage and commit per logical change" | "tidy commit history of a branch" (→ ds-pr --tidy) |
| "commit + push" (commit only — push is separate) | "merge into main" (→ ds-pr) |

## Contract

**Dimensions:** none (carrier)

**Commit message describes only what `git diff` shows.** Not session discussion, not what was tried and reverted, not what was planned. Read diff, describe diff.

- Standalone. Uses blueprint profile for toolchain when available; own detection when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- **Exempt from state protocol:** atomic, git-diff-driven, seconds-long. Git staging area is the natural state. No `ds/audit/commit.json`.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Show commit plan only, don't execute |
| `--single` | Force single commit |
| `--staged-only` | Commit only staged changes |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

Default scope: all uncommitted changes (staged + unstaged + untracked).

## Delegation

**Owns:** git-commit, conventional-commits, commit-quality, commit-grouping | **Delegates:** ds-fix → format/lint/typecheck pre-commit gates | **Receives:** ds-deps → per-group upgrade commit; ds-simplify → post-approval delete commit; ds-review → fix commit; ds-issue → atomic commit grouping; ds-pr → staging before PR

## Execution Flow

Pre-checks → Analyze → Execute → Verify → [Needs-Approval] → Summary

### Phase 1: Pre-checks

**Prerequisites (1, then 2-4 parallel):**

1. Verify `git` available
2. Verify git repo: `git rev-parse --git-dir`
3. Verify not detached HEAD: `git branch --show-current` — detached → stop, suggest creating a branch first
4. `git fetch origin` (best-effort); on main/master behind upstream → announce, then `git pull --ff-only origin {branch}`; fast-forward impossible (diverged) or working tree state blocks it → skip the pull, note "behind upstream by {n} — pull after committing", never merge/rebase silently

**Branch management:**

- **On main/master:** suggest feature branch (`{type}/{short-description}`); offer commit-on-main. If `release-please-config.json`, `.release-please-manifest.json`, `.releaserc*`, or a `semantic-release` config in `package.json` is present, mark commit-on-main as "Not recommended — bypasses changelog pipeline". **Under `--auto`:** no prompt — commit on main only when the repo's own convention already does so (prior history commits directly to main, no branch-protection signal); otherwise create the feature branch.
- **On feature branch:** changes outside branch scope → ask: continue here (recommended) / create new branch. **Under `--auto`:** continue here (the recommended default), no prompt.

**Conflict check:** `UU`/`AA`/`DD` in status → stop.

**Quality Gates (changed files only):**

- **IDU:** Profile → Toolchain. Findings(commit-relevant) → context for grouping. Absent → own detection.
- **Always:** secret scan + large file check.
- **Always: repo completeness check** — untracked source files referenced by tracked code: list untracked (`git ls-files --others --exclude-standard`), filter to source extensions (`.ts/.tsx/.js/.jsx/.go/.py/.dart/.rs/.rb/.php/.ex/.scala/.cs/.c/.cpp/.h/.swift/.vue/.svelte`; exclude build output, lockfiles, generated), grep tracked files for filename references + relative path patterns. Referenced-but-untracked → ask **"Used by your code but not tracked — CI will fail. Stage them?"**: Stage all (recommended) / Review each / Skip. Approve → `git add`, include in commit. Skip → warn "CI will likely fail". **Under `--auto`:** no prompt — Stage all (the recommended default).
- **Code files:** format + lint (no tests) on changed files only. Tool unavailable → offer install, ask "Install and continue?"; decline → mark `⚠ Skipped (tool unavailable)`. **Under `--auto`:** no prompt — install and continue when installation is non-interactive and low-risk (a local dev-dependency); otherwise mark `⚠ Skipped (tool unavailable)` and continue.
- **Docs/config only:** skip code checks.
- **Format/lint modifications:** include in the same commit, not separate.
- **On failure:** ask "Fix first (recommended) / Commit anyway". **Under `--auto`:** no prompt — Fix first (the recommended default).

**Gate:** No merge conflicts; quality gates passed or user proceeded. If fails → conflicts present; stop, list conflicting files, instruct user to resolve and re-run; no partial auto-commit.

### Phase 2: Analyze

`git diff` (or `git diff --cached` for `--staged-only`) is the only input.

**Unpushed commit integration:**

- `git log @{upstream}..HEAD` — list unpushed (no upstream → all local are unpushed).
- Same-file/scope match → offer fixup:
  - HEAD commit → `git commit --amend`
  - Older unpushed → `git commit --fixup={hash}` + non-interactive autosquash: `git rebase --autosquash {base}` (git ≥2.44) or `GIT_SEQUENCE_EDITOR=: git rebase -i --autosquash {base}` — never an editor-driven interactive rebase
- Pushed commits are immutable — never fixup into them.
- Rebase conflict → abort, fall back to new commit, warn user.

**Smart grouping:**

1. **Classify each file** by role:

| File pattern | Category |
|-------------|----------|
| `package.json`, `go.mod`, `Cargo.toml`, lockfiles | `deps` |
| `*.test.*`, `*_test.*`, `test/`, `tests/`, `spec/` | `test` |
| `*.md`, `docs/`, `LICENSE`, `CHANGELOG` | `docs` |
| `.github/`, `Dockerfile`, CI configs, `.env.example` | `ci/infra` |
| `.eslintrc`, `tsconfig`, lint/build configs | `config` |
| Source code | `src` (further grouped by module/directory) |

2. **Group by logical change:** new feature = source + its tests + its docs; dep update = lockfile + config + migration; refactor = renamed/moved files; unrelated fixes split.

3. **Decision matrix:**

| Situation | Action |
|-----------|--------|
| Files serve one logical purpose | Single commit |
| `--single` flag | Force single |
| Mixed categories, no logical link | Split |
| Proposed description needs "and" to join unrelated actions | Re-split before showing the plan table |
| deps + source adaptation | Single (causally linked) |
| Format/lint auto-fixes | Include in commit they belong to |

4. **Order when splitting:** `deps` → `config` → `src` → `test` → `docs` → `ci/infra`. Each commit must leave project buildable.

5. **Display plan table:** `| # | Type | Title | Files |` — one row per planned commit; amending → append `(amend → {short-hash})` to the title.

**Gate:** Plan table displayed. If fails → empty `git diff` (no changes, no referenced-untracked); report "Nothing to commit — working tree clean" and exit.

### Phase 3: Execute (skip if --preview)

No approval question — plan table was shown.

**Secret-pattern exclusion:** when staging "all uncommitted changes" (default scope), auto-exclude files matching `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.*`, `secrets.*` before `git add`; list excluded files in the Phase 6 summary. User can override a specific file by naming it explicitly (`git add {file}` / re-run with `--staged-only` after manually staging it) — the exclusion is filename-pattern-based, not content-based, and never silently drops a file the user explicitly asked to include.

Stage files → build message → commit.

**Title format:** `{type}({scope}): {description}`

| Part | Rule | Limit |
|------|------|-------|
| Full title | `{type}({scope}): {description}` | 50 chars soft / 72 hard (CMT-04 — `git log --oneline` + GitHub UIs truncate long subjects) |
| `{scope}` | Module/directory with >50% of changes; omit if no majority | Optional |
| `{description}` | Imperative, lowercase after colon, no period | Fit within 50 |

**Conventional commit types + version bump:**

| Type | When | Bump |
|------|------|------|
| `feat` | End users gain a capability they lacked before | minor |
| `fix` | Something broken for end users now works | patch |
| `feat!` / `fix!` | Breaking change (+ `BREAKING CHANGE:` footer) | major |
| `refactor` | Internal improvement, no behavior change | none |
| `perf` | Performance, no behavior change | none |
| `test` | Test-only | none |
| `docs` | Docs-only | none |
| `style` | Formatting/whitespace only, zero logic change | none |
| `build` | Build system or external-deps changes affecting artifacts | none |
| `chore` | Tooling, deps, maintenance (no artifact impact) | none |
| `ci` | CI/CD pipeline only | none |
| `revert` | Reverts a previous commit (`revert: {original title}`) | mirrors reverted |

**Litmus test (uncertain → non-bumping type):**

| Question | YES → | NO → |
|----------|-------|------|
| End users gain a capability they **lacked**? | `feat` | `refactor`/`chore` |
| Was something **broken** and now works? | `fix` | `refactor`/`chore` |

**Common misclassifications:**

| Change | Looks like | Actually |
|--------|-----------|----------|
| Add internal helper / utility | `feat` | `refactor` |
| Improve existing feature's code (no behavior change) | `feat` | `refactor` / `perf` |
| Dev-only tooling / build tweak | `feat` | `chore` |
| Test-only fix | `fix` | `test` |
| Docs-only correction | `fix` | `docs` |

**Title pattern (placeholders, not literals):**

| Good shape | Bad shape — why |
|------------|-----------------|
| `{type}({specific-scope}): {imperative-verb} {what-changed}` (concrete subject, specific scope, ≤50 chars) | `{type}: {vague-verb}` — no scope, no specific change |
| `{type}({specific-scope}): {action} {component-or-feature}` | `{type}({scope}): {refactoring|fix|update}` — redundant noun, no information |
| `chore(deps): bump {package} from {old-version} to {new-version}` | `chore: update packages` — which package? what version? |
| `test({scope}): add {specific-test-target} tests` | `test: add tests` — for what? |

**Body — include only when** one holds: the title alone omits the "why"; a trade-off was made; a multi-file change has a non-obvious reason; a breaking change needs migration. Otherwise skip. Format: 1-3 lines, blank line after title, wrap at 72, explain WHY not WHAT; optional migration/config hint (e.g., "Requires migration {migration-id}").

**Trailers/footers:** one `Co-Authored-By: {ai-model-name} <{provider-email}>`; breaking → `BREAKING CHANGE: {description}`; references → `Closes #{issue}`, `Fixes #{issue}`.

**Message-format gate (advisory tool):** `commitlint.config.*` present → validate each proposed message with commitlint before committing; rejection → fix the message, retry. Absent → the format tables above are the fallback; repo has CI + multiple contributors → add summary note "commit format enforced only in this session — no commitlint gate for future contributors".

**Gate:** Commits created in conventional format with `Co-Authored-By:`. If fails → pre-commit hook rejected; show output, ask "Fix and retry (recommended) / Commit anyway (--no-verify, explain risk)"; bypass → add WARN note in summary. Secret-pattern file explicitly re-added by user → stage exactly that file, keep the rest of the pattern excluded. **Under `--auto`:** no prompt — fix and retry (the recommended path), never bypass via `--no-verify`; still failing after one retry → stop and report the blocker (hooks are never skipped, this is not on the irreversible-exception list).

### Phase 4: Verify

`git log` to confirm. Verify working tree clean (unless `--staged-only`).

**Gate:** `git log` shows expected commits; working tree clean. If fails → re-read `git status`, identify remaining untracked/modified, ask "Stage remaining and commit / Leave as-is". **Under `--auto`:** no prompt — leave as-is (the safer default, avoids committing unplanned drift) and note the remaining files in the summary.

### Phase 5: Needs-Approval Review [needs_approval > 0]

**Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set. **Under `--auto`:** no approval block shown — every item, including CRITICAL, resolves via the same impact/effort/risk reasoning the review step would show, applied and recorded `fixed`/`failed`; items matching the irreversible-exception list resolve `skipped (needs-human)` instead.

**Gate:** All needs_approval items resolved (applied → fixed/failed; declined → skipped). If fails → forced binary re-prompt per item (Apply / Skip); no response → mark `skipped (no response)` and proceed.

### Phase 6: Summary

`ds-commit: {OK|WARN|FAIL} | Commits: {n} | Files: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

FRC+DSC accounting. Commit hashes + branch + next-step hint (push or PR). Secret-pattern exclusions (if any): `{file}` list excluded from staging by filename pattern.

**Value Delivered:** 1-5 concrete bullets, real changes only. Example shapes (placeholders, not literal output):

- `{n} unrelated changes split into atomic commits — bisect can now isolate any regression to a single concern`
- `{n} secret patterns intercepted in commit body — credentials no longer leak into git history`
- `{n} untracked source files staged — CI will not fail on missing imports`

Zero-change run: `Nothing to commit — working tree clean`.

**Gate:** Summary line + Value Delivered emitted; FRC+DSC accounting balances. If fails → some planned commits did not land; list each (created/failed) with hashes of successes; instruct user to re-run on remaining changes.

## Quality Gates

- Commit message describes only what `git diff` shows — verified by re-reading diff
- Commit rules from [references/rules-commit.md](references/rules-commit.md)
- Every quality gate check (format, lint, secret scan) gets a disposition (FRC)
- Conventional type matches litmus test
- **Secret scan covers message body + trailers ([references/principles.md §5](references/principles.md)):** same pattern detection on proposed message + body + footer. A leak in the message is as visible as one in source.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: not applicable — exempt from state protocol (atomic, git-driven). W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No changes | Report "nothing to commit", exit |
| All untracked | Ask which files to include. Under `--auto`: stage all (matches the default scope), no prompt. |
| Merge conflict markers | Warn, do not commit until resolved |
| Untracked file referenced by tracked code | Completeness gate catches it — stage prompt |
| Untracked file with no tracked references | Ignore — not a completeness issue |
| >20 untracked source files | Show count + top 5 referenced; ask "Stage referenced (N) / Review / Skip". Under `--auto`: stage referenced, no prompt. |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
