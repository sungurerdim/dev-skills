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
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **Exempt from state protocol:** atomic, git-diff-driven, seconds-long. Git staging area is the natural state. No `ds/audit/commit.json`.
- **A commit never touches the remote.** No fetch, no pull, no push — this skill's write surface stops at the local repository.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Show commit plan only, don't execute |
| `--single` | Force single commit |
| `--staged-only` | Commit only staged changes |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default scope: all uncommitted changes (staged + unstaged + untracked).

## Delegation

**Owns:** git-commit, conventional-commits, commit-quality, commit-grouping | **Delegates:** ds-fix → format/lint/typecheck pre-commit gates | **Receives:** ds-deps → per-group upgrade commit; ds-simplify → post-approval delete commit; ds-review → fix commit; ds-issue → atomic commit grouping; ds-pr → staging before PR; ds-build → per-unit commits; ds-debug → the fix commit; ds-release → the release commit (chore(release): x.y.z)

## Execution Flow

Pre-checks → Analyze → Execute → Verify → Summary

### Phase 1: Pre-checks

**Prerequisites (1, then 2-3 parallel):**

1. `git --version` → version string printed (git available)
2. `git rev-parse --git-dir` → exit 0 (inside a git repo)
3. `git branch --show-current` → non-empty branch name; empty output = detached HEAD → stop, suggest creating a branch first

**Branch management:**

- **On main/master:** Default: commit on main only when the repo's own convention already does so (prior history commits directly to main, no branch-protection signal); otherwise create the feature branch (`{type}/{short-description}`) — no prompt. `--ask`: offer feature branch (recommended) / commit-on-main; if `release-please-config.json`, `.release-please-manifest.json`, `.releaserc*`, or a `semantic-release` config in `package.json` is present, mark commit-on-main "Not recommended — bypasses changelog pipeline".
- **On feature branch:** Default: continue here (the recommended default) — no prompt. `--ask`: changes outside branch scope → ask continue here (recommended) / create new branch.

**Conflict check:** `git status --porcelain` shows `UU`/`AA`/`DD` entries → stop.

**Quality Gates (changed files only):**

- **Upstream artifacts:** Profile → Toolchain. Findings(commit-relevant) → context for grouping. Absent → own detection.
- **Always: secret scan + large-file check.** Content scan of the staged diff against the regexes in [../core/secret-patterns.md](../core/secret-patterns.md): `git diff --cached -U0 | grep -nE '{pattern}'` run once per regex in that file (AWS keys, generic `api_key`/`secret`/`password` assignments, private-key blocks, provider tokens, connection-string passwords, JWTs). Filename exclusion (always excluded from bulk staging, listed in the summary): `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.*`, `secrets.*`. Large-file check: `git diff --cached --numstat` lists changed files, then `wc -c` each against a 1,000,000-byte (1 MB) threshold — well above any hand-written source file, catching accidentally committed binaries, archives, and build artifacts; files over it are unstaged (`git restore --staged {file}`) and reported in the summary as `only you can do: {file} ({size} bytes) — exceeds the 1 MB commit threshold, use Git LFS or split the change`. A confirmed secret match is never auto-fixed — rotate the credential, then add the variable name with a placeholder to `.env.example`; the run's status is FAIL until the owner acts.
- **Always: repo completeness check** — untracked source files referenced by tracked code: list untracked (`git ls-files --others --exclude-standard`), filter to source extensions (`.ts/.tsx/.js/.jsx/.go/.py/.dart/.rs/.rb/.php/.ex/.scala/.cs/.c/.cpp/.h/.swift/.vue/.svelte`; exclude build output, lockfiles, generated), grep tracked files for filename references + relative path patterns. Referenced-but-untracked → Default: Stage all (the recommended default) — no prompt. `--ask`: ask "Used by your code but not tracked — CI will fail. Stage them?": Stage all (recommended) / Review each / Skip. Approve → `git add`, include in commit. Skip → warn "CI will likely fail".
- **Code files:** format + lint (no tests) on changed files only. Default: install and continue when installation is non-interactive and low-risk (a local dev-dependency); otherwise mark `⚠ Skipped (tool unavailable)` and continue — no prompt. `--ask`: tool unavailable → ask "Install and continue?"; decline → mark `⚠ Skipped (tool unavailable)`.
- **Docs/config only:** skip code checks.
- **Format/lint modifications:** include in the same commit, not separate.
- **Mechanical Done Gate:** ds-quality enforcement arm installed (stop-hook / pre-commit hook / auto-lint) → its gate command IS the pre-commit check: run it on the changed files instead of the ad-hoc format+lint pass, and never bypass its hook. No arm → the format+lint pass above stands, falling back to the stack-native chain from [../core/toolchains.md](../core/toolchains.md); no check tooling at all → Verification-Infrastructure Gap — note it once in the summary, offer `/ds-quality`.
- **On failure:** Default: Fix first (the recommended default) — no prompt. `--ask`: ask "Fix first (recommended) / Commit anyway" — "Commit anyway" records WARN + the red check output in the summary; a red commit is never reported as clean.

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

**Secret-pattern exclusion:** when staging "all uncommitted changes" (default scope), auto-exclude files matching `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.*`, `secrets.*` before `git add`; list excluded files in the Phase 5 summary. User can override a specific file by naming it explicitly (`git add {file}` / re-run with `--staged-only` after manually staging it) — the exclusion is filename-pattern-based, not content-based, and never silently drops a file the user explicitly asked to include.

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

**Trailers/footers:** `Co-Authored-By: {ai-model-name} <{provider-email}>` only when the repository already uses the trailer — `git log -20 --format=%b | grep -c 'Co-Authored-By'` > 0; count is 0 → no trailer. Breaking → `BREAKING CHANGE: {description}`; references → `Closes #{issue}`, `Fixes #{issue}`.

**Message-format gate (advisory tool):** `commitlint.config.*` present → validate each proposed message with commitlint before committing; rejection → fix the message, retry. Absent → the format tables above are the fallback; repo has CI + multiple contributors → add summary note "commit format enforced only in this session — no commitlint gate for future contributors".

**Gate:** Commits created in conventional format (`Co-Authored-By:` included only when the repository-convention check above found it). If fails → pre-commit hook rejected; show its output, fix the cause it names, retry (≤3 attempts); still rejected → stop and report the blocker with that output — the same recovery path in every mode; hooks are never skipped, and this is not on the publish/irreversible exception list. **`--no-verify` is never offered and never used** — this skill has no bypass path in any mode; a hook that blocks the commit is a finding to fix, not a flag to add ([../core/principles.md §1](../core/principles.md), theme 4). Secret-pattern file explicitly re-added by user → stage exactly that file, keep the rest of the pattern excluded.

### Phase 4: Verify

`git log --oneline -n {planned-count}` → every planned commit listed. `git status --porcelain` → empty output (unless `--staged-only`).

**Gate:** `git log --oneline` shows the planned commits; `git status --porcelain` → empty. If fails → Default: leave as-is (the safer default, avoids committing unplanned drift) and note the remaining files in the summary — no prompt. `--ask`: re-read `git status --porcelain` output, identify remaining untracked/modified, ask "Stage remaining and commit / Leave as-is".

### Phase 5: Summary

`ds-commit: {OK|WARN|FAIL} | Commits: {n} | Files: {n} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Disposition accounting — totals balance. Commit hashes + branch + next-step hint (push or PR). Secret-pattern exclusions (if any): `{file}` list excluded from staging by filename pattern.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} unrelated changes split into atomic commits — bisect can now isolate any regression to a single concern`
- `{n} secret patterns intercepted in commit body — credentials no longer leak into git history`
- `{n} untracked source files staged — CI will not fail on missing imports`

Zero-change run: `Nothing to commit — working tree clean`.

**Gate:** Summary line + Effect emitted; disposition accounting balances. If fails → some planned commits did not land; list each (created/failed) with hashes of successes; instruct user to re-run on remaining changes.

## Quality Gates

- Commit message describes only what `git diff` shows — verified by re-reading diff
- Commit rules from [references/rules-commit.md](references/rules-commit.md)
- Every quality gate check (format, lint, secret scan) gets a disposition
- Conventional type matches litmus test
- **Secret scan covers message body + trailers ([../core/principles.md §5](../core/principles.md)):** same pattern detection on proposed message + body + footer. A leak in the message is as visible as one in source.
- W10: defer finding detection to a fresh `ds/audit/findings.md` when present — own scan only for scopes it does not cover.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No changes | Report "nothing to commit", exit |
| All untracked | Default: stage all (matches the default scope) — no prompt. `--ask`: ask which files to include. |
| Merge conflict markers | Warn, do not commit until resolved |
| Untracked file referenced by tracked code | Completeness gate catches it — stage prompt |
| Untracked file with no tracked references | Ignore — not a completeness issue |
| >20 untracked source files | Default: stage referenced (N) — no prompt. `--ask`: show count + top 5 referenced; ask "Stage referenced (N) / Review / Skip". |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
