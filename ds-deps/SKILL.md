---
name: ds-deps
description: Dependency upgrade loop — classify each dependency as safe-patch/safe-minor/review-major, apply safe groups with per-group commits, surface majors with migration notes and rollback. Use when upgrading dependencies or auditing for outdated/vulnerable packages.
---

# /ds-deps

Dormant projects rot dependencies: security advisories accumulate, majors pile up, minors become major deltas. Manual upgrade is slow and error-prone; skipping it multiplies later migration cost.

**Dependency Upgrade Loop** — classify each dep as safe-patch / safe-minor / review-major, apply safe groups with per-group commits, surface majors with migration notes + rollback plan.

## Triggers

- User runs `/ds-deps`
- User asks to upgrade dependencies, check for outdated libs, "is anything obsolete"
- User says "bring this project back to life" on a dormant repo
- After `npm audit` / `pip-audit` / `cargo audit` surfaces advisories

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "upgrade my dependencies", "is anything outdated" | "audit code quality" (→ ds-review) |
| "security advisory upgrade" (npm/pip/cargo audit triage) | "audit full CI pipeline" (→ ds-devops) |
| "bring this dormant project back" (dep angle) | "what new dependencies should I add" (→ ds-research) |
| "classify deps as patch/minor/major" | "review my package.json for design" (→ ds-backend) |

## Contract

- Standalone; uses `ds/audit/findings.md` (stack, deps scopes) when fresh, own audit otherwise. State: `ds/audit/deps.json`.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- Test gate between upgrade and commit is non-negotiable. Test fail → revert batch.
- Category A: safe-patch + safe-minor (no breaking changelog) → autonomous. Category B: every major, every upgrade with breaking notes, every removal → batched approval.
- One `/ds-commit` per group. Never a single mega-commit.
- Lockfile is SSOT — no upgrade persists without a lockfile delta.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Classify + report, no upgrade |
| `--scope={x}` | Specific group: patch, minor, major, security, all |
| `--auto` | Apply safe-patch + safe-minor; list majors, skip without asking |
| `--force-approve` | Apply every classified upgrade including majors — majors can ship breaking changes; expect to fix call sites |
| `--dry-run` | Classifier + security scan only, skip upgrade execution |
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

1. **Recovery check:** DETECT `ds/audit/deps.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete. Present → READ, verify `git_hash`. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` group, skip `done` groups, announce `[DPS] Resuming from Phase {N}`. On Summary success, delete state. Verify `ds/audit/` in `.gitignore`.

2. **State `data`:** `{ mode, stack, manifest_paths[], deps: [{name, current, latest_stable, bump_type, advisory?, classification, changelog_url?, breaking_notes?}], groups: {patch, minor, major, security, removal: [ids]}, group_status: {id: pending|applied|failed|skipped}, commits: [{group, hash}], git_hash }`.

3. **Detect stack + manifest:**

   | Manifest | Stack |
   |----------|-------|
   | `package.json` | npm / pnpm / yarn |
   | `go.mod` | go |
   | `pyproject.toml` / `requirements*.txt` | python (poetry / pip) |
   | `Cargo.toml` | rust |
   | `Gemfile` | ruby |
   | `pubspec.yaml` | dart |
   | `composer.json` | php |

   Record every manifest — monorepos include all workspaces.

4. **Lockfile verification.** Missing lockfile → HIGH finding, abort upgrade (lockfile-first policy). `--preview` still classifies.

**Gate:** Stack(s) detected, manifests listed, lockfile present. If fails → no recognized manifest → exit cleanly; missing lockfile → HIGH finding "missing lockfile — upgrade aborted (lockfile-first)", instruct user to commit a lockfile first; `--preview` may continue classification without lockfile.

### Phase 2: Discover

Per manifest:

1. **Current versions:** parse manifest + lockfile.
2. **Latest stable** via stack-native tooling:

   | Stack | Command |
   |-------|---------|
   | npm | `npm outdated --json` |
   | pnpm | `pnpm outdated --format json` |
   | yarn | `yarn outdated --json` |
   | go | `go list -u -m all` |
   | python | `pip list --outdated --format=json` / `poetry show --outdated` |
   | rust | `cargo outdated --format json` |
   | ruby | `bundle outdated` |
   | dart | `dart pub outdated --json` |

3. **Security advisories:** `npm audit --json` / `pip-audit --format=json` / `cargo audit --json` / `bundler-audit` / `pub audit`. Also Dependabot via `gh` CLI if available.
4. **Removal candidates:** grep source + config for `import {name}` / `require('{name}')` / stack equivalents. Zero in-source references → removal candidate.
5. Record each dep in state with current / latest / advisory.

Parallelize per manifest, max 3 concurrent registry calls.

**Gate:** Every dep has current + latest + advisory recorded. If fails → registry query failed (network, rate limit, package not found) → record `{ name, current, latest: "unknown", advisory: "unknown" }`, mark `skipped (registry unreachable)`, continue; surface WARN "{n} deps could not be queried — skipped from classification".

### Phase 3: Classify

Per dep, determine `bump_type` + `classification`:

| Bump | Current → Latest | Classification |
|------|-----------------|----------------|
| patch | `{x}.{y}.{z}` → `{x}.{y}.{z+n}` | No breaking changelog → `safe-patch`. With breaking entries → `review-major` |
| minor | `{x}.{y}.{z}` → `{x}.{y+n}.0` | No breaking changelog + no deprecations → `safe-minor`. Otherwise → `review-major` |
| major | `{x}.{y}.{z}` → `{x+n}.0.0` | Always `review-major` |
| pre-1.0 | `0.{x}.{y}` → `0.{x+n}.{y}` | Treat minor bump as `review-major` (semver pre-1.0 convention) |

**Supply-chain override ([references/principles.md §5](references/principles.md)):** any package introducing/expanding `postinstall` / `preinstall` / `prepare` lifecycle scripts (or non-npm equivalents) auto-promotes to `review-major` regardless of semver delta. New executable install hooks = known supply-chain attack surface.

**Changelog extraction:**

1. Registry page provides changelog URL (npm `repository`, PyPI `Project URLs`, crates.io / pub.dev / rubygems → GitHub).
2. Fetch `CHANGELOG.md` + release notes for versions between current and latest.
3. Scan keywords: `breaking`, `BREAKING CHANGE`, `removed`, `deprecated`, `migration`, `drops support`, `requires X`.
4. None → safe. Any found → populate `breaking_notes`, elevate classification.

**Security priority override:** dep with advisory → group includes `security`, priority ahead of safe groups. Security patch passing safe-patch criteria stays `safe-patch` but marked `priority=security`.

**Removal candidates:** classification = `removal` (Category B).

**Gate:** Every dep classified. If fails → changelog unfetchable/unparseable → elevate to `review-major` (W5: uncertain → conservative), record `breaking_notes: "changelog unavailable — classified conservatively"`, continue; never leave a dep unclassified.

### Phase 4: Plan

Display plan table:

```
| Dep              | Current  | Latest   | Bump  | Class         | Priority | Breaking notes        |
|------------------|----------|----------|-------|---------------|----------|-----------------------|
| {pkg-name}       | {curr}   | {latest} | {bump}| {class}       | {prio}   | {notes-or-dash}       |
| {pkg-name}       | {curr}   | -        | -     | removal       | -        | 0 source references   |
```

Per-group summary: `Safe-patch: {n} | Safe-minor: {n} | Review-major: {n} | Removal: {n} | Security: {n} (overlaps above)`.

Write findings to `ds/audit/findings.md` with `scope=deps` and `category` column: A for safe groups, B for review-major + removal.

**Gate:** Plan table displayed, every dep accounted for. If fails → missing dep → re-read state, add row with `class: "unknown"` + `notes: "classification failed — manual review required"`; do not proceed to Execute until table is complete or missing dep is explicitly user-skipped.

### Phase 5: Execute [skip if --preview or --dry-run]

Per group, in order: **security** → **safe-patch** → **safe-minor** → (approval) → **review-major** → **removal**.

**Safe group execution:**

1. Apply version bumps (manifest + lockfile) via native command:

   | Stack | Command |
   |-------|---------|
   | npm | `npm install {name}@{version}` then `npm install` to refresh lockfile |
   | pnpm | `pnpm update {name} --latest` |
   | yarn | `yarn upgrade {name}@{version}` |
   | go | `go get {name}@{version}` then `go mod tidy` |
   | python (poetry) | `poetry add {name}@{version}` |
   | python (pip) | `pip install {name}=={version}` then `pip freeze > requirements.lock` |
   | cargo | `cargo update -p {name} --precise {version}` |

2. Invoke `/ds-test --quick` (or stack-native fast path: `npm test --bail`, `go test ./...`, `pytest -x`). Pass → proceed. Fail → revert manifest + lockfile, mark group `failed (tests broke)`, continue.
3. Invoke `/ds-commit --single` with message: `chore(deps): bump {scope-or-group} ({n} packages)`. Body lists each dep `{name}: {current} → {latest}`. Record hash.

**Review-major group (requires approval):**

1. Present every entry with: current → proposed, breaking notes, migration steps (from changelog), rollback path.
2. Modes: **Apply All** / **Review Each** / **Skip All** / **Defer**. `--auto` without `--force-approve` → skip all, mark needs-approval. `--force-approve` → apply all.
3. Per approved major: apply bump, run **full** test suite (not quick); fail → revert + mark failed; pass → commit.
4. One commit per major: `chore(deps): upgrade {name} to {major-version}`. Body: breaking notes + migration link.

**Removal group (requires approval):**

1. Present candidates with "0 source references" evidence.
2. Approve → remove from manifest + lockfile, run quick tests, commit `chore(deps): remove unused {name}`.

**Gate:** Every group has a commit or `failed`/`skipped` record. Working tree clean. If fails → dirty tree (partial apply, no commit) → revert via `git checkout -- .` on affected manifest + lockfile, mark `failed (dirty working tree)` in state.group_status, continue; revert itself fails → halt + surface conflict with modified-file list.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Dominant in this skill. Present all Category B items (every review-major + every removal) in one block.

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** Every B item has a decision (applied → fixed/failed, or explicitly skipped). If fails → undecided after prompt (dismissed/timed out) → mark `skipped (no decision)` in state.group_status, continue to Summary; do not re-prompt.

### Phase 7: Summary

FRC+DSC accounting.

```
| Dep              | Bump  | Class         | Disposition                          |
|------------------|-------|---------------|--------------------------------------|
| {pkg-name}       | {bump}| {class}       | {fixed-skipped-failed} ({short-hash}) |
```

`ds-deps: {OK|WARN|FAIL} | Bumped: {n} | Majors-pending: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Advisories-closed: {n}`

On success: delete `ds/audit/deps.json`. If `ds/audit/` empties, remove directory.

**Gate:** Every dep has exactly one disposition; accounting balances. If fails → undisposed dep → assign `skipped (accounting gap)`; imbalanced → status `WARN` with note "{n} deps unaccounted — state file preserved for --resume"; do not delete state.

**Value Delivered:** 1-5 concrete bullets, real upgrade outcomes only. Example shapes (placeholders, not literal):

- `{n} safe-patch + {m} safe-minor upgrades applied with per-group commits + green tests — dormant repo no longer accumulating CVE backlog`
- `{n} security advisories closed (CRITICAL: {x}, HIGH: {y}) — production exposure window narrowed`
- `{n} major upgrades surfaced with migration notes — known-breaking-version-bumps are now a deliberate decision, not a surprise`
- `{n} unused deps removed — lockfile shrunk, install time + supply-chain attack surface reduced`

Zero-change run: `All deps already at safe-current — no upgrades applied`.

## Quality Gates

- Lockfile always updated alongside manifest — no orphaned version mismatch.
- Peer-dep conflicts: detect via stack-native tool output; conflict → elevate to `review-major`.
- Workspace-wide consistency: dep across multiple workspace manifests → bump to a single version across all.
- **Slopsquatting guard:** before adding or accepting any new dependency, confirm it exists in the official registry, was registered before this project began, and has real download history; a near-miss or cross-ecosystem name is a typosquat until proven (~19.7% of LLM-suggested packages are hallucinated — [CSA 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/)).
- W1: every classification cites registry metadata + changelog URL. W2: after upgrade, verify no broken import in consumers. W3: only manifest + lockfile + approved source lines change. W4: re-read manifest before commit. W5: uncertain changelog → `review-major`, not `safe-minor`. W6: every group produces output. W7: dedup — same dep across monorepo workspaces listed once per workspace. W8: quote package names with version specifiers in shell; reject names containing shell metacharacters. W9: state in `ds/audit/deps.json`, `ds/audit/` gitignored, state deleted on Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W16: dependency verified present in the registry (non-trivial age + downloads) and pinned in the lockfile before add; hallucinated or typosquat names rejected.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Registry unreachable | Retry once with 10s timeout; persistent → skip dep, continue |
| Changelog URL missing | Treat as breaking unless SemVer patch with no release notes flag; classify `review-major` |
| Test command not defined | Ask user for test command; offer to skip test gate with warning (marks group `unverified`) |
| Lockfile conflict after upgrade | Revert, mark `failed (lockfile conflict)`, continue |
| Peer-dep incompatibility | Mark `failed (peer-dep conflict)` with conflicting pair in evidence |
| Advisory with no fixed version | Report HIGH finding, mark `blocked (no fix available)` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project (no manifest) | Report "nothing to upgrade", exit |
| Monorepo with mixed stacks | Iterate each workspace independently; aggregate report |
| Pinned-by-intent dep (comment `# pinned`) | Skip classification, mark `skipped (intentional pin)` |
| Pre-release version (`{x}.{y}.{z}-beta`) | Treat any bump as `review-major` |
| Git-sourced dep (no registry) | Skip, list as `skipped (git dep, manual upgrade only)` |
| Dep used only in devDependencies | Standard classification; note `dev-only` in plan |
| Major with seamless migration (no breaking notes) | Still `review-major` — majors are always B regardless of changelog |
