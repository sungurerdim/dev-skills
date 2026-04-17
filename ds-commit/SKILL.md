# /ds-commit

AI commits are vague ("update code"), bundle unrelated changes, and skip pre-commit checks. Skill reads diff, groups changes logically, and writes precise conventional commit messages.

**Smart Commits** — Quality gates + atomic grouping + conventional commit format.

## Triggers

- User runs `/ds-commit`
- User asks to commit changes, stage and commit, or create a commit
- User says "commit this", "commit my changes", or "save my work"
- Only trigger when user explicitly asks to commit — staging alone is not a commit request

## Contract

**Commit message describes what `git diff` shows — nothing else.** Not what you discussed in the session, not what you tried and reverted, not what you planned. Read diff, describe diff.

- Standalone. Uses blueprint profile for toolchain detection when available; own detection when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Show commit plan only, don't execute |
| `--single` | Force single commit |
| `--staged-only` | Commit only staged changes |

**Scope:** All uncommitted changes included by default (staged + unstaged + untracked). Use `--staged-only` for staged changes only.

## Execution Flow

Pre-checks → Analyze → Execute → Verify → [Needs-Approval] → Summary

### Phase 1: Pre-checks

**1.1 Prerequisites:**
1. Verify `git` available

**Steps 2-4 are independent — run in parallel:**

2. Verify git repo: `git rev-parse --git-dir`
3. Verify not detached HEAD: `git branch --show-current`
4. `git fetch origin` (best-effort)
4a. On main/master: if behind upstream → `git pull origin {branch}` silently

**1.2 Branch management:**

**On main/master:** Suggest creating feature branch. Show: 1 suggested name (`{type}/{short-description}`), option to commit on main.
If `release-please-config.json` or `.release-please-manifest.json` exists in project root, add note to commit-on-main option: "Not recommended — bypasses changelog pipeline".

**On feature branch:** Changes don't match branch scope → ask: continue here (recommended) or create new branch.

**1.3 Conflict check:** `UU`/`AA`/`DD` in status → stop.

**1.4 Quality Gates (changed files only):**

**Findings file check:** `.ds-findings.md` with fresh `git_hash` → check for relevant findings on changed files. Use as additional context for commit grouping.

- Always: secret scan + large file check
- Always: **repo completeness check** — detect untracked source files referenced by tracked code:
  1. List untracked non-ignored files: `git ls-files --others --exclude-standard`
  2. Filter to source files only (by stack extensions: `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.py`, `.dart`, `.rs`, `.rb`, `.php`, `.ex`, `.scala`, `.cs`, `.c`, `.cpp`, `.h`, `.swift`, `.vue`, `.svelte`). Exclude build output, lockfiles, generated files.
  3. Per untracked source file, grep tracked files for import/require/include references to that filename (without extension): `git grep -l "<filename>"`. Also check relative path patterns (e.g., `../lib/utils`, `./utils`).
  4. Any untracked file referenced by tracked code → list them with referencing files and ask: **"These files are used by your code but not tracked by git — CI will fail. Stage them?"** with options: Stage all (recommended) / Review each / Skip
  5. User approves → `git add` files, include in commit
  6. User skips → warn: "CI will likely fail due to missing files"
- Code files: format + lint (no tests) on changed files only
  - Detect toolchain: first search for blueprint profile (`Toolchain:` line under `## Blueprint Profile` heading in instruction files). No blueprint → auto-detect from project files (package.json, go.mod, pyproject.toml, Cargo.toml, Makefile).
  - Run formatter then linter with auto-fix. Tool unavailable → offer to install: show install command (e.g., `pip install ruff`, `npm install -D eslint`), ask "Install and continue?" User accepts → install, re-run scope. User declines → skip scope and mark as `⚠ Skipped (tool unavailable, declined install): {scope}` in summary. System-level tools (e.g., `go`, `rustfmt`) requiring manual install → show install instructions, skip scope.
- Docs/config only: skip code checks
- Format/lint modified files: include those changes in the commit
- On failure: ask "Fix first (recommended)" or "Commit anyway"

**Gate:** No merge conflicts, quality gates passed or user chose to proceed.

### Phase 2: Analyze

Run `git diff` (or `git diff --cached` for `--staged-only`). This is **only input** for building commit message.

**Unpushed commit integration:**

Check unpushed commits: `git log @{upstream}..HEAD` (no upstream → all local commits are unpushed).

- New changes touch same file or scope as unpushed commit → offer fixup:
  - HEAD commit → `git commit --amend`
  - Older unpushed commit → `git commit --fixup={hash}` + `git rebase -i --autosquash`
- Otherwise → new commit
- Only fixup into unpushed commits — pushed commits are immutable
- Rebase conflicts → abort, fall back to new commit, warn user

**Smart grouping algorithm:**

1. **Classify each changed file** by its role:

| File pattern | Category |
|-------------|----------|
| `package.json`, `go.mod`, `Cargo.toml`, lockfiles | `deps` |
| `*.test.*`, `*_test.*`, `test/`, `tests/`, `spec/` | `test` |
| `*.md`, `docs/`, `LICENSE`, `CHANGELOG` | `docs` |
| `.github/`, `Dockerfile`, CI configs, `.env.example` | `ci/infra` |
| Config files (`.eslintrc`, `tsconfig`, etc.) | `config` |
| Source code | `src` — further grouped by module/directory |

2. **Group by logical change** — files that change together for one reason:
   - New feature: source files + its tests + its docs = one commit
   - Dependency update: lockfile + config + migration = one commit
   - Pure refactor: renamed/moved files = one commit
   - Unrelated fixes in different modules = separate commits

3. **Decision matrix:**

| Situation | Action |
|-----------|--------|
| All files serve one logical purpose | Single commit |
| `--single` flag | Force single commit |
| Mixed categories with no logical link (e.g., bug fix + unrelated docs update) | Split into separate commits |
| deps change + source code adaptation | Single commit (causally linked) |
| Format/lint auto-fixes from quality gate | Include in commit they belong to, not separate |

4. **Commit ordering** (when splitting): `deps` → `config` → `src` → `test` → `docs` → `ci/infra`. Each commit must leave project in buildable state.

5. **Display commit plan table:**

```
| # | Type     | Title                              | Files |
|---|----------|------------------------------------|-------|
| 1 | {type}   | {commit description}                | {n}   |
| 2 | {type}   | {commit description}                | {n}   |
| 3 | {type}   | {commit description}                | {n}   |
```

If amending: show `(amend → {short-hash})` next to entry.

**Gate:** Commit plan table displayed with type, title, and file count per commit.

### Phase 3: Execute (skip if --preview)

No approval question — plan table was shown.

Stage files -> build message -> commit.

**Title format:** `type(scope): description`

| Part | Rule | Limit |
|------|------|-------|
| Full title | `type(scope): description` | 50 chars max (GitHub Desktop truncates beyond 50) |
| `type` | Conventional commit type (see below) | — |
| `scope` | Module/directory with >50% of changes. Omit if no clear majority. | Optional |
| `description` | Imperative mood, lowercase after colon, no period | Fit within 50 total |

**Conventional commit types:**

| Type | When to use | Version bump |
|------|------------|-------------|
| `feat` | End users can do something they couldn't before | minor |
| `fix` | Something broken for end users now works | patch |
| `feat!` / `fix!` | Breaking change (append `BREAKING CHANGE:` footer too) | major |
| `refactor` | Internal code improvement, no behavior change | none |
| `perf` | Performance improvement, no behavior change | none |
| `test` | Test-only changes | none |
| `docs` | Documentation-only changes | none |
| `chore` | Build, CI, tooling, dependency updates | none |
| `ci` | CI/CD pipeline changes only | none |

**Classification litmus test:**

| Question | YES → | NO → |
|----------|-------|------|
| Can end users do something they **couldn't** before? | `feat` | `refactor`/`chore` |
| Was something **broken** for end users and now works? | `fix` | `refactor`/`chore` |

Common misclassifications:

| Change | Looks like | Actually |
|--------|-----------|----------|
| Add internal helper/utility | feat | refactor |
| Improve existing feature's code | feat | refactor/perf |
| Dev-only tooling change | feat | chore |
| Test-only fix | fix | test |
| Docs update | fix | docs |

When uncertain → always prefer non-bumping type.

**Title examples:**

| Good | Bad | Why bad |
|------|-----|---------|
| `feat(auth): add OAuth2 login with Google provider` | `feat: update auth` | Too vague — what changed? |
| `fix(cart): prevent negative quantity on decrement` | `fix: fix bug` | Says nothing useful |
| `refactor(api): extract validation middleware from handlers` | `refactor: refactoring` | Redundant, no information |
| `chore(deps): bump express from 4.18 to 4.21` | `chore: update packages` | Which package? What version? |
| `test(payment): add Stripe webhook signature verification tests` | `test: add tests` | Tests for what? |

**Body — when to include and what to write:**

| Include body when | Skip body when |
|-------------------|---------------|
| The "why" is not obvious from title | Title fully explains change |
| There are trade-offs or alternatives considered | Simple rename/move/delete |
| Multiple files changed for non-obvious reason | Single-file change |
| Breaking change needs migration guidance | Routine dependency update |

Body format: 1-3 lines, separated from title by blank line. Explain **why**, not **what** (diff shows what). Wrap at 72 chars.

```
feat(search): add full-text search with PostgreSQL tsvector

Switch from LIKE queries to tsvector/tsquery for 10x faster search
on large datasets. Requires running migration 20240115_add_search_index.
```

**Trailer and footers:**
- Exactly one `Co-Authored-By:` line with AI model name and provider email
- Breaking changes: `BREAKING CHANGE: description` footer (in addition to `!` in title)
- References: `Closes #123`, `Fixes #456` when applicable

**Gate:** All commits created with valid conventional commit format and Co-Authored-By trailer.

### Phase 4: Verify

`git log` to confirm. Verify working tree clean (unless `--staged-only`).

**Gate:** git log confirms commit(s) and working tree is clean.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 6: Summary

Commit count, file count, branch, commit hashes. Next step: push or create pull request.

`ds-commit: {OK|WARN|FAIL} | Commits: N | Files: N | Fixed: N | Skipped: N | Failed: N | Total: N`

**Gate:** Summary includes commit count, file count, branch, and hashes.

## Quality Gates

- Commit message describes only what `git diff` shows — verified by re-reading diff
- Commit quality rules applied from [references/rules-commit.md](references/rules-commit.md)
- Every quality gate check (format, lint, secret scan) gets disposition in summary (FRC)
- Conventional commit type matches litmus test classification
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Pre-commit hook fails | Show hook output, ask: fix and retry or skip hook (explain risk) |
| Rebase conflict during fixup | Abort rebase, fall back to new commit, warn user |
| Formatter/linter unavailable | Skip silently, proceed with commit |
| Detached HEAD state | Stop, suggest creating branch first |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No changes detected | Report "nothing to commit", exit |
| All changes are untracked | Ask user which files to include |
| Merge conflict markers present | Warn user, do not commit until resolved |
| Untracked file referenced by tracked code | Repo completeness gate catches it — ask user to stage |
| Untracked file with no tracked references | Ignore — not completeness issue, just unstaged file |
| Many untracked source files (>20) | Show count + top 5 referenced, ask "Stage referenced (N) / Review / Skip" |
