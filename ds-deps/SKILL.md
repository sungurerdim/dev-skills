# /ds-deps

Dormant projects rot dependencies: security advisories accumulate, majors pile up, minors become major deltas. Manual upgrade is slow and error-prone; skipping it multiplies later migration cost.

**Dependency Upgrade Loop** — classify each dep as safe-patch / safe-minor / review-major, apply the safe groups with a commit per group, surface majors with migration notes + rollback plan.

## Triggers

- User runs `/ds-deps`
- User asks to upgrade dependencies, check for outdated libs, or "is anything obsolete"
- User says "bring this project back to life" on a dormant repo
- After `npm audit` / `pip-audit` / `cargo audit` surfaces advisories

## Contract

- Standalone; uses `ds/audit/findings.md` (stack, deps scopes) when fresh, own audit otherwise. FRC+DSC enforced. State: `ds/audit/deps.json`.
- Test gate between upgrade and commit is non-negotiable. Test fail → revert batch.
- Category A: safe-patch + safe-minor (no changelog breaking entries) → autonomous. Category B: every major, every upgrade with breaking notes, every removal → batched approval.
- One `/ds-commit` per group. Never a single mega-commit.
- Lockfile is SSOT — no upgrade persists without a lockfile delta.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Classify + report, no upgrade |
| `--scope=X` | Specific group: patch, minor, major, security, all |
| `--auto` | Apply safe-patch + safe-minor; list majors, skip without asking |
| `--force-approve` | Apply every classified upgrade including majors |
| `--dry-run` | Run the classifier + security scan, skip the upgrade execution |
| `--resume` | Resume from `ds/audit/deps.json` without prompt |
| `--clean` | Delete existing state, start fresh |

Without flags: present mode menu.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| safe-patch | SemVer patch bumps with no changelog breaking entries |
| safe-minor | SemVer minor bumps with no changelog breaking entries |
| review-major | Every major bump |
| security | Versions flagged by `npm audit` / `pip-audit` / `cargo audit` / GitHub advisories |
| removal | Dependencies no longer referenced in source — candidates to drop |

## Delegation

**Owns:** deps-upgrade-execution, safe-patch, safe-minor, review-major, security-advisory-prioritization | **Delegates:** ds-test → per-group test validation; ds-commit → per-group commit | **Receives:** ds-devops → audit handoff (detection → execution); ds-ship → periodic hygiene pass

## Execution Flow

Setup → Discover → Classify → Plan → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Recovery check:** DETECT `ds/audit/deps.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete state. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` group, skip `done` groups, announce `[DEP] Resuming from Phase {N}`. On successful Summary, delete state; remove `ds/audit/` if empty. Verify `ds/audit/` in `.gitignore`; add if missing.

2. **State shape:** `{ mode, stack, manifest_paths[], deps: [{name, current, latest_stable, bump_type, advisory?, classification, changelog_url?, breaking_notes?}], groups: {patch: [ids], minor: [ids], major: [ids], security: [ids], removal: [ids]}, group_status: {id: pending|applied|failed|skipped}, commits: [{group, hash}], git_hash }`.

3. **Detect stack + manifest.** Signals: `package.json` (npm/pnpm/yarn), `go.mod` (go), `pyproject.toml` / `requirements*.txt` (python, ruff/poetry/pip), `Cargo.toml` (rust), `Gemfile` (ruby), `pubspec.yaml` (dart), `composer.json` (php). Record every discovered manifest — monorepos include all workspaces.

4. **Lockfile verification.** Missing lockfile → HIGH finding, abort upgrade phase (lockfile-first policy). `--preview` still classifies.

**Gate:** Stack(s) detected, manifests listed, lockfile present.

### Phase 2: Discover

For each manifest:

1. **Current versions:** parse manifest + lockfile.
2. **Latest stable:** query registry via native tooling.
   - npm: `npm outdated --json`
   - pnpm: `pnpm outdated --format json`
   - yarn: `yarn outdated --json`
   - go: `go list -u -m all`
   - python: `pip list --outdated --format=json` or `poetry show --outdated`
   - rust: `cargo outdated --format json`
   - ruby: `bundle outdated`
   - dart: `dart pub outdated --json`
3. **Security advisories:** `npm audit --json` / `pip-audit --format=json` / `cargo audit --json` / `bundler-audit` / `pub audit` (where available). Also check GitHub Dependabot alerts if `gh` CLI is available.
4. **Removal candidates:** for each dep, grep source + config for `import ... from 'name'` / `require('name')` / stack-native equivalents. Zero in-source references → removal candidate.
5. **Record** each dep in state with current/latest/advisory.

Parallelize per manifest, max 3 concurrent registry calls.

**Gate:** Every dep has current, latest, and advisory status recorded.

### Phase 3: Classify

Per dep, determine `bump_type` and `classification`.

| Bump | Current → Latest | Classification logic |
|------|-----------------|---------------------|
| patch | 1.2.3 → 1.2.7 | No changelog breaking entries → `safe-patch`. With breaking entries → `review-major` |
| minor | 1.2.3 → 1.5.0 | No changelog breaking entries + no deprecations → `safe-minor`. Otherwise → `review-major` |
| major | 1.2.3 → 2.0.0 | Always `review-major` |
| pre-1.0 | 0.1.x → 0.2.x | Treat minor bump as `review-major` (semver pre-1.0 treats minor as breaking by convention) |

**Changelog extraction:**

1. Registry page provides changelog URL (npm `repository` field, PyPI `Project URLs`, crates.io / pub.dev / rubygems → GitHub URL).
2. Fetch `CHANGELOG.md` + release notes for versions between current and latest.
3. Scan for keywords: `breaking`, `BREAKING CHANGE`, `removed`, `deprecated`, `migration`, `drops support`, `requires X`.
4. None found → safe. Any found → `breaking_notes` populated and classification elevated.

**Security priority override:** Dep with advisory → group includes `security`, priority ahead of plain safe groups. Security patch that passes the safe-patch criteria stays `safe-patch` but marked `priority=security`.

**Removal candidates:** classification = `removal` (Category B).

**Gate:** Every dep classified with `safe-patch | safe-minor | review-major | removal`.

### Phase 4: Plan

Display plan table:

```
| Dep             | Current  | Latest   | Bump  | Class         | Priority | Breaking notes                |
|-----------------|----------|----------|-------|---------------|----------|-------------------------------|
| express         | 4.18.2   | 4.21.0   | minor | safe-minor    | security | -                             |
| react           | 17.0.2   | 19.0.0   | major | review-major  | -        | New JSX transform, removed... |
| lodash.get      | 4.4.2    | -        | -     | removal       | -        | 0 source references           |
| ...             |          |          |       |               |          |                               |
```

Per-group summary: `Safe-patch: 8 deps | Safe-minor: 3 deps | Review-major: 2 deps | Removal: 1 dep | Security: 2 (overlaps above)`.

Write findings to `ds/audit/findings.md` with `scope=deps` and `category` column: A for safe groups, B for review-major + removal.

**Gate:** Plan table displayed, every dep accounted for.

### Phase 5: Execute [skip if --preview or --dry-run]

Per group, in order: **security** → **safe-patch** → **safe-minor** → (approval) → **review-major** → **removal**.

**Safe group execution:**

1. Apply the version bumps (manifest + lockfile) via native command:
   - npm: `npm install {name}@{version}` then `npm install` to refresh lockfile
   - pnpm: `pnpm update {name} --latest`
   - yarn: `yarn upgrade {name}@{version}`
   - go: `go get {name}@{version}` then `go mod tidy`
   - python (poetry): `poetry add {name}@{version}`
   - python (pip): `pip install {name}=={version}` then `pip freeze > requirements.lock`
   - cargo: `cargo update -p {name} --precise {version}`
2. Invoke `/ds-test --quick` (or stack-native fast path: `npm test --bail`, `go test ./...`, `pytest -x`). All tests pass → proceed. Any fail → revert manifest + lockfile, mark group `failed (tests broke)`, continue to next group.
3. Invoke `/ds-commit --single` with message: `chore(deps): bump {scope-or-group} ({n} packages)`. Body lists each dep with `{name}: {current} → {latest}`. Record hash.

**Review-major group (requires approval):**

1. Present every review-major entry with: current → proposed, breaking notes, migration steps (from changelog), rollback path.
2. Modes: **Apply All** / **Review Each** / **Skip All** / **Defer**. `--auto` without `--force-approve` → skip all, mark needs-approval. `--force-approve` → apply all.
3. Per approved major: apply version bump, run **full** test suite (not quick), on fail revert + mark failed, on pass commit.
4. One commit per major: `chore(deps): upgrade {name} to {major-version}`. Body: breaking notes + migration link.

**Removal group (requires approval):**

1. Present candidate list with "0 source references" evidence.
2. User approves → remove from manifest + lockfile, run quick tests, commit as `chore(deps): remove unused {name}`.

**Gate:** Every group has either a commit or a clear `failed` / `skipped` record. Working tree clean.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Dominant in this skill. Present all Category B items (every review-major, every removal) in one block. Modes: --auto → list+skip, --force-approve → apply all, interactive → Apply All / Review Each / Skip All.

**Gate:** Every B item has a decision. Every approved B item either applied (fixed/failed) or explicitly skipped.

### Phase 7: Summary

FRC+DSC accounting.

```
| Dep              | Bump  | Class         | Disposition                     |
|------------------|-------|---------------|---------------------------------|
| express          | minor | safe-minor    | fixed (bumped in c1a2b3f)       |
| lodash           | patch | safe-patch    | failed (tests broke, reverted)  |
| react            | major | review-major  | skipped (user declined)         |
| lodash.get       | -     | removal       | fixed (removed in d4e5f6g)      |
```

Summary line:

`ds-deps: {OK|WARN|FAIL} | Bumped: N | Majors-pending: N | Skipped: N | Failed: N | Total: N | Advisories-closed: N`

On success: delete `ds/audit/deps.json`. If `ds/audit/` empties, remove the directory.

**Gate:** Every dep has exactly one disposition. Accounting balances.

## Quality Gates

W1: every classification cites registry metadata + changelog URL. W2: after upgrade, verify no broken import in consumers. W3: only manifest + lockfile + approved source lines change. W4: re-read manifest before commit. W5: uncertain changelog → `review-major`, not `safe-minor`. W6: every group produces output. W7: dedup — same dep across monorepo workspaces listed once per workspace. W8: quote package names with version specifiers in shell; reject names containing shell metacharacters. W9: state in `ds/audit/deps.json`, `ds/audit/` gitignored, state deleted on Summary.

- Lockfile always updated alongside manifest — no orphaned version mismatch.
- Peer-dep conflicts: detect via stack-native tool output; conflict → elevate to `review-major`.
- Workspace-wide consistency: if dep appears in multiple workspace manifests, bump to a single version across all.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Registry unreachable | Retry once with 10s timeout; persistent failure → skip that dep, continue |
| Changelog URL missing | Treat as breaking unless SemVer patch with no release notes flag; classify as `review-major` |
| Test command not defined | Ask user for test command; offer to skip test gate with warning (marks group as `unverified`) |
| Lockfile conflict after upgrade | Revert, mark `failed (lockfile conflict)`, continue |
| Peer-dep incompatibility | Mark `failed (peer-dep conflict)` with the conflicting pair in evidence |
| Advisory with no fixed version | Report HIGH finding, mark as `blocked (no fix available)` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project (no manifest) | Report "nothing to upgrade", exit |
| Monorepo with mixed stacks | Iterate each workspace independently; aggregate report |
| Pinned-by-intent dep (comment `# pinned`) | Skip classification, mark `skipped (intentional pin)` |
| Pre-release version (1.0.0-beta) | Treat any bump as `review-major` |
| Git-sourced dep (no registry) | Skip, list as `skipped (git dep, manual upgrade only)` |
| Dep used only in devDependencies | Standard classification applies; note `dev-only` in plan |
| Major with seamless migration (no breaking notes found) | Still `review-major` — majors are always B regardless of changelog |
