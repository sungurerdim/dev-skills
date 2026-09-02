---
name: ds-deps
description: Dependency upgrade loop — classify each dependency as safe-patch/safe-minor/review-major, apply safe groups with per-group commits, surface majors with migration notes and rollback. Use when upgrading dependencies or auditing for outdated/vulnerable packages.
---

# /ds-deps

Dormant projects rot dependencies: security advisories accumulate, majors pile up, minors become major deltas. Manual upgrade is slow and error-prone; skipping it multiplies later migration cost.

**Dependency Upgrade Loop** — classify each dep as safe-patch / safe-minor / review-major, apply safe groups with per-group commits, surface majors with migration notes + rollback plan.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

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

**Dimensions:** C4, D9 (semver)
**Framework alignment (advisory):** OWASP SAMM Supply Chain Security (C4), SLSA v1.2 (provenance/attestation verification — Source Track added Nov 2025), Semantic Versioning (D9).

- Standalone; uses `ds/audit/findings.md` (stack, deps scopes) when fresh (`git_hash == HEAD` AND current run-cycle), own audit otherwise.
- **State-exempt:** per-group commits are git checkpoints; re-run continues from remaining groups.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- Test gate between upgrade and commit is non-negotiable. Test fail → revert batch.
- Category A: safe-patch + safe-minor (no breaking changelog) → autonomous. Category B: every major, every upgrade with breaking notes, every removal → batched approval.
- One commit per group (`/ds-commit` when present, else committed inline). Never a single mega-commit; never leave an approved group uncommitted.
- Lockfile is SSOT — every persisted upgrade carries a lockfile delta.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Classify + security scan + report only — no upgrade execution |
| `--scope={x}` | Specific group: patch, minor, major, security, all |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Without flags: default — apply safe-patch + safe-minor, surface majors, recorded in the summary. `--ask`: shows an up-front menu — Upgrade safe groups (recommended), plus each mode in the Arguments table (Preview / Scoped) and (Cancel).

## Scopes

| Scope | What It Covers |
|-------|---------------|
| safe-patch | SemVer patch bumps with no changelog breaking entries |
| safe-minor | SemVer minor bumps with no changelog breaking entries |
| review-major | Every major bump |
| security | Versions flagged by `npm audit` / `pip-audit` / `cargo audit` / GitHub advisories |
| removal | Dependencies no longer referenced in source — candidates to drop |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| safe-patch | a manifest + lockfile detected (Phase 1) | N/A — no manifest detected |
| safe-minor | a manifest + lockfile detected | N/A — no manifest detected |
| review-major | a manifest + lockfile detected | N/A — no manifest detected |
| security | an audit tool available for the detected stack, or `osv-scanner` present | N/A — no audit tool available (gap-noted, not silently skipped) |
| removal | any source | — |

`--scope=` overrides the table for the named scope; `--ask` shows the resolved table before running.

| Reference | Loaded when |
|-----------|-------------|
| [references/stack-commands.md](references/stack-commands.md) | Phase 1, 2, or 5 needs a stack-specific command (npm/pnpm/yarn/go/python/rust/ruby/dart/php/jvm/dotnet/swift) |
| [references/classify-advisories.md](references/classify-advisories.md) | Phase 3 runs |

## Delegation

**Owns:** deps-upgrade-execution, safe-patch, safe-minor, review-major, security-advisory-prioritization, dep-license-scan | **Delegates:** ds-test → per-group test validation; ds-commit → per-group commit | **Receives:** ds-devops → audit handoff (detection → execution); ds-fix → deps-upgrade-execution handoff; ds-ship → periodic hygiene pass; ds-repo → transitive license scan + SBOM export (oss-readiness check 2)

## Execution Flow

Setup → Discover → Classify → Plan → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Detect stack + manifest:** per-stack manifest patterns (npm/go/python/rust/ruby/dart/php/jvm/dotnet/swift) in [references/stack-commands.md](references/stack-commands.md) § Manifest detection. Record every manifest — monorepos include all workspaces.

2. **Lockfile verification.** Missing lockfile → HIGH finding, abort upgrade (lockfile-first policy). `--preview` still classifies.

**Gate:** Stack(s) detected, manifests listed, lockfile present. If fails → no recognized manifest → exit cleanly; missing lockfile → HIGH finding "missing lockfile — upgrade aborted (lockfile-first)", instruct user to commit a lockfile first; `--preview` may continue classification without lockfile.

### Phase 2: Discover

Per manifest:

1. **Current versions:** parse manifest + lockfile.
2. **Latest stable** via stack-native tooling: [references/stack-commands.md](references/stack-commands.md) § Latest-stable check.
3. **Security advisories:** stack-native audit commands + `osv-scanner` cross-ecosystem fallback: [references/stack-commands.md](references/stack-commands.md) § Security advisories. No audit tool available → skip the advisory sub-step with warning `security advisories unchecked for {manifest} — no audit tool available`.
4. **Removal candidates:** grep source + config for `import {name}` / `require('{name}')` / stack equivalents. Zero in-source references → removal candidate.
5. Record each dep's current / latest / advisory for the plan table.

Parallelize per manifest, max 3 concurrent registry calls.

**Gate:** Every dep has current + latest + advisory recorded. If fails → registry query failed (network, rate limit, package not found) → record `{ name, current, latest: "unknown", advisory: "unknown" }`, mark `skipped (registry unreachable)`, continue; surface WARN "failed to query {n} deps — skipped from classification".

### Phase 3: Classify

Per dep, determine `bump_type` + `classification`:

| Bump | Current → Latest | Classification |
|------|-----------------|----------------|
| patch | `{x}.{y}.{z}` → `{x}.{y}.{z+n}` | No breaking changelog → `safe-patch`. With breaking entries → `review-major` |
| minor | `{x}.{y}.{z}` → `{x}.{y+n}.0` | No breaking changelog + no deprecations → `safe-minor`. Otherwise → `review-major` |
| major | `{x}.{y}.{z}` → `{x+n}.0.0` | Always `review-major` |
| pre-1.0 | `0.{x}.{y}` → `0.{x+n}.{y}` | Treat minor bump as `review-major` (semver pre-1.0 convention) |

**Advisory classification signals:** five checks beyond the semver bump table — supply-chain lifecycle-script override (auto-promotes to `review-major`), release-age cooldown (default 7 days, holds a dep out of the safe groups), provenance signal (`npm audit signatures` / PEP 740), license scan + SBOM (syft/ScanCode/FOSSA class), dependency-confusion defense (scope claiming, lockfile-enforced installs, registry resolution order, egress restriction). Full thresholds, commands, and rationale: [references/classify-advisories.md](references/classify-advisories.md).

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

**Gate:** Plan table displayed, every dep accounted for. If fails → missing dep → re-check Phase 2/3 output, add row with `class: "unknown"` + `notes: "classification failed — manual review required"`; do not proceed to Execute until table is complete or missing dep is explicitly user-skipped.

### Phase 5: Execute [skip if --preview]

**Checkpoint pre-step (before the first bump):** `git status --porcelain` — record the output as the baseline; clean, or every planned write is disjoint from dirty paths → proceed; manifest or lockfile dirty at baseline → stop, record `only you can do`. Full protocol: [../core/checkpoint-protocol.md](../core/checkpoint-protocol.md). Never run a bulk upgrade over uncommitted unrelated changes silently.

Per group, in order: **security** → **safe-patch** → **safe-minor** → (approval) → **review-major** → **removal**.

**Safe group execution:**

1. Apply version bumps (manifest + lockfile) via native command: [references/stack-commands.md](references/stack-commands.md) § Version bump commands.
2. Invoke `/ds-test --run` (advisory handoff — target absent → stack-native fast path directly: `npm test --bail`, `go test ./...`, `pytest -x`). Pass → proceed. Fail unresolved → revert manifest + lockfile, mark group `failed (tests broke)`, continue.
3. `/ds-commit` present → invoke `/ds-commit --single` with message `chore(deps): bump {scope-or-group} ({n} packages)` (body lists each dep `{name}: {current} → {latest}`); absent → commit inline: `git add {manifest} {lockfile}` then `git commit -m "chore(deps): bump {scope-or-group} ({n} packages)"` with the same body. Record hash either way — never leave an approved group uncommitted.

**Review-major group (requires approval):**

1. Present every entry — one line each (`name: current → proposed · breaking?`) grouped by package class with counts; state the question (`Upgrade which of these N majors?`). "All" = exactly the displayed set. Full detail (breaking notes, migration steps from changelog, rollback path) under each entry.
2. Default: no menu shown — every major resolves by best judgment (applied using the same impact/effort/risk reasoning a menu would show, recorded in the summary); nothing about a major version bump matches the irreversible-exception list, so none is stranded as `only you can do`. `--ask`: modes — **Apply All** / **Apply all without breaking notes** (per-class bulk alongside the total — majors whose changelog shows zero breaking entries) / **Review Each** / **Skip All** / **Defer**.
3. Per approved major: apply bump, run **full** test suite (not quick); fail → revert + mark failed; pass → commit.
4. One commit per major. `/ds-commit` present → invoke `/ds-commit --single` with message `chore(deps): upgrade {name} to {major-version}` (body: breaking notes + migration link); absent → commit inline: `git add {manifest} {lockfile}` then `git commit -m "chore(deps): upgrade {name} to {major-version}"` with the same body.

**Removal group (requires approval):**

1. Present candidates with "0 source references" evidence.
2. Default: resolves automatically by best judgment — removed, quick-tested, and committed without approval (git history keeps this fully reversible). `--ask`: approve → remove from manifest + lockfile, run quick tests. Either way, commit: `/ds-commit` present → invoke `/ds-commit --single` with message `chore(deps): remove unused {name}`; absent → commit inline: `git add {manifest} {lockfile}` then `git commit -m "chore(deps): remove unused {name}"`.

**Mechanical Done Gate:** the per-group test run above is the test arm — add lint/type: resolve `{check-cmd}` in Phase 1 (ds-quality enforcement arm installed — stop-hook / pre-commit hook / auto-lint → its gate command; else stack-native lint/type/test commands; none detectable → Verification-Infrastructure Gap: report it, offer `/ds-quality`, record the decision) and capture the baseline before the first group — baseline red → done condition is "no *new* red", baseline reds reported, never inherited as green. A bump can break the type graph with tests still green (e.g. a types-package minor) — run `{check-cmd}` after each group before its commit; new red → same revert path as a test failure. After the last group: run the full `{check-cmd}` once — the aggregate run's exact command + observed output is the Completion Evidence; never report `OK` with a new red.

**Lockfile-integrity command** (per ecosystem, run after each group before its commit): [references/stack-commands.md](references/stack-commands.md) § Lockfile-integrity command. Non-zero exit → same revert path as a failed `{check-cmd}` run: restore the group's manifest + lockfile, mark `failed (lockfile integrity)`, continue to the next group.

**Gate:** Every group has a commit or `failed`/`skipped` record. `git status --porcelain` output matches the checkpoint baseline (this skill's changes all committed or reverted). If fails → dirty tree (partial apply, no commit) → revert exactly the touched files via `git restore -- {manifest} {lockfile}` — never a tree-wide `git checkout -- .`, which would destroy the user's unrelated uncommitted work — mark `failed (dirty working tree)` for the summary, continue; revert itself fails → halt + surface conflict with modified-file list.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Covers ONLY items still undecided after Phase 5 (deferred majors/removals) — items already decided in Phase 5's inline resolution are never re-presented (no double-asking).

**Default:** no review step is shown — remaining items (deferred majors/removals) resolve by best judgment (`fixed` or `failed`), except items matching the irreversible-exception list, which become `skipped (only you can do)`. **`--ask`:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** Every B item has a decision (applied → fixed/failed, or explicitly skipped). If fails → undecided after prompt (dismissed/timed out) → mark `skipped (no decision)` for the summary, continue to Summary; do not re-prompt.

### Phase 7: Summary

Disposition accounting — totals balance.

```
| Dep              | Bump  | Class         | Disposition                          |
|------------------|-------|---------------|--------------------------------------|
| {pkg-name}       | {bump}| {class}       | {fixed-skipped-failed} ({short-hash}) |
```

`ds-deps: {OK|WARN|FAIL} | Bumped: {n} | Majors-pending: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Advisories-closed: {n}`

Closing shape (`Decided without asking` lines, every `only you can do` item in full): [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md).

**Gate:** Every dep has exactly one disposition; accounting balances. If fails → undisposed dep → assign `skipped (accounting gap)`; imbalanced → status `WARN` with note "{n} deps unaccounted — re-run to pick up the remainder from the last per-group commit".

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} safe-patch + {m} safe-minor upgrades applied with per-group commits + green tests — dormant repo no longer accumulating CVE backlog`
- `{n} security advisories closed (CRITICAL: {x}, HIGH: {y}) — production exposure window narrowed`
- `{n} major upgrades surfaced with migration notes — known-breaking-version-bumps are now a deliberate decision, not a surprise`
- `{n} unused deps removed — lockfile shrunk, install time + supply-chain attack surface reduced`

Zero-change run: `All deps already at safe-current — no upgrades applied`.

## Quality Gates

- Lockfile always updated alongside manifest — no orphaned version mismatch.
- **Lockfile-diff integrity:** after each group, review `git diff -- {lockfile}` — only the expected packages change; any resolved-URL host change (registry → unexpected host / git+http), integrity-hash removal, or surprise transitive addition with install scripts → revert the group, CRITICAL finding (motivated by 2025-2026 registry-worm incidents where tampered lockfiles carried the payload).
- Peer-dep conflicts: detect via stack-native tool output; conflict → elevate to `review-major`.
- Workspace-wide consistency: dep across multiple workspace manifests → bump to a single version across all.
- **Slopsquatting guard:** before adding or accepting any new dependency, confirm it exists in the official registry, was registered before this project began, and has real download history; a near-miss or cross-ecosystem name is a typosquat until proven (~19.7% of LLM-suggested packages are hallucinated — [CSA 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/)).
- **Stdlib-extraction check:** when the language runtime moves a module out of the standard library into a separate package (Ruby `csv`, Python `distutils`), verify every dependency still importing it declares the package explicitly in the manifest (Gemfile/requirements) — never rely on implicit stdlib presence. Detect: runtime upgrade notes list extracted modules; transitive deps import them; manifest lacks them. (XR-195)
- **Dependency Adoption Eligibility gate:** a brand-new dependency needs 5 AND-criteria plus license + provenance before acceptance, else it classifies `review-major`, never `safe-minor`: [references/classify-advisories.md](references/classify-advisories.md) § Dependency Adoption Eligibility gate.
- W1: every classification cites registry metadata + changelog URL. W2: after upgrade, verify no broken import in consumers. W3: only manifest + lockfile + approved source lines change. W4: re-read manifest before commit. W5: uncertain changelog → `review-major`, not `safe-minor`. W6: every group produces output. W7: dedup — same dep across monorepo workspaces listed once per workspace. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W16: dependency verified present in the registry (non-trivial age + downloads) and pinned in the lockfile before add; hallucinated or typosquat names rejected.
- W8: quote package names with version specifiers in shell; reject names containing shell metacharacters. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Registry unreachable | Retry once with 10s timeout; persistent → skip dep, continue |
| Changelog URL missing | Treat as breaking unless SemVer patch with no release notes flag; classify `review-major` |
| Test command not defined | Default: skips the test gate with warning and marks the group `unverified`, recorded in the summary. `--ask`: asks for the test command, offers to skip the gate with warning instead |
| Lockfile conflict after upgrade | Revert, mark `failed (lockfile conflict)`, continue |
| Peer-dep incompatibility | Mark `failed (peer-dep conflict)` with conflicting pair in evidence |
| Advisory with no fixed version | Report HIGH finding, mark `blocked (no fix available)` |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Empty project (no manifest) | Report "nothing to upgrade", exit |
| Monorepo with mixed stacks | Iterate each workspace independently; aggregate report |
| Pinned-by-intent dep (comment `# pinned`) | Skip classification, mark `skipped (intentional pin)`; record rationale beside the pin — (1) pinned below a known-bad auto-transform (formatter/linter bug at a target version): last unaffected version + reason, validate the full quality pipeline before any upgrade; (2) version CAP declared in two places (app manifest + Docker base image): pin both atomically with cross-referencing comments; (3) pinned for an empirically-verified property (e.g. page alignment): record the property + verification method next to the pin, re-verify as an explicit upgrade-checklist step. (XR-107) |
| Pre-release version (`{x}.{y}.{z}-beta`) | Treat any bump as `review-major` |
| Git-sourced dep (no registry) | Skip, list as `skipped (git dep, manual upgrade only)` |
| Dep used only in devDependencies | Standard classification; note `dev-only` in plan |
| Major with seamless migration (no breaking notes) | Still `review-major` — majors are always B regardless of changelog |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
