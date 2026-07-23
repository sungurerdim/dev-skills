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
**Framework alignment (advisory):** OWASP SAMM Supply Chain Security (C4), SLSA v1.2 (provenance/attestation verification — Source Track added Nov 2025), Semantic Versioning (D9) — sourced references in SKILL-SPEC Dimension Coverage Map.

- Standalone; uses `ds/audit/findings.md` (stack, deps scopes) when fresh (`git_hash == HEAD` AND current run-cycle), own audit otherwise.
- **State-exempt:** per-group commits are git checkpoints; re-run continues from remaining groups.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.
- Test gate between upgrade and commit is non-negotiable. Test fail → revert batch.
- Category A: safe-patch + safe-minor (no breaking changelog) → autonomous. Category B: every major, every upgrade with breaking notes, every removal → batched approval.
- One `/ds-commit` per group. Never a single mega-commit.
- Lockfile is SSOT — every persisted upgrade carries a lockfile delta.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Classify + security scan + report only — no upgrade execution |
| `--scope={x}` | Specific group: patch, minor, major, security, all |
| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |

Without flags: present an up-front menu — Upgrade safe groups (recommended: apply safe-patch + safe-minor, surface majors), plus each mode in the Arguments table (Preview / Scoped) and (Cancel). A disambiguating flag skips the menu.

## Scopes

| Scope | What It Covers |
|-------|---------------|
| safe-patch | SemVer patch bumps with no changelog breaking entries |
| safe-minor | SemVer minor bumps with no changelog breaking entries |
| review-major | Every major bump |
| security | Versions flagged by `npm audit` / `pip-audit` / `cargo audit` / GitHub advisories |
| removal | Dependencies no longer referenced in source — candidates to drop |

## Delegation

**Owns:** deps-upgrade-execution, safe-patch, safe-minor, review-major, security-advisory-prioritization, dep-license-scan | **Delegates:** ds-test → per-group test validation; ds-commit → per-group commit | **Receives:** ds-devops → audit handoff (detection → execution); ds-fix → deps-upgrade-execution handoff; ds-ship → periodic hygiene pass; ds-repo → transitive license scan + SBOM export (oss-readiness check 2)

## Execution Flow

Setup → Discover → Classify → Plan → Execute → [Needs-Approval] → Summary

### Phase 1: Setup

1. **Detect stack + manifest:**

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

2. **Lockfile verification.** Missing lockfile → HIGH finding, abort upgrade (lockfile-first policy). `--preview` still classifies.

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

3. **Security advisories:** `npm audit --json` / `pip-audit --format=json` / `cargo audit --json` / `bundler-audit` / `pub audit`. Also Dependabot via `gh` CLI if available. Stack-native audit command unavailable → `osv-scanner` present → run it against the lockfile (V2: `osv-scanner scan --lockfile={lockfile}`; V1 syntax `osv-scanner --lockfile=` also accepted) as the cross-ecosystem fallback and record advisories per dep; absent → skip the advisory sub-step with warning `security advisories unchecked for {manifest} — no audit tool available`.
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

**Supply-chain override ([references/principles.md §5](references/principles.md)):** any package introducing/expanding `postinstall` / `preinstall` / `prepare` lifecycle scripts (or non-npm equivalents) auto-promotes to `review-major` regardless of semver delta. New executable install hooks = known supply-chain attack surface.

**Release-age cooldown (advisory, default 7 days):** target version published less than 7 days ago (registry publish timestamp) → hold it out of the safe groups this run — classification stands, execution deferred with note `held (release-age {n}d < 7d cooldown)`; the previous in-cooldown-window version applies instead when it satisfies the same bump class. Security-advisory fixes override the cooldown (patching a known CVE beats worm-window caution). Rationale: recent registry worm/compromise events were detected within days of publication (xz-utils ~3 days; Shai-Hulud npm worm — CISA alert within the week) — a short quarantine window converts "first victim" into "warned bystander".

**Provenance signal (advisory):** npm — run `npm audit signatures` (verifies registry signatures + provenance attestations; trusted-publishing/OIDC publishes carry provenance automatically since Jul 2025); PyPI — check attestation presence (PEP 740). A newly-added package with no provenance, or an upgrade where the publisher/repository identity changed vs the previous version → note as supply-chain signal, promote to `review-major`.

**License scan + SBOM (advisory, on request or via ds-repo handoff):** walk the full transitive tree from the lockfile (not just direct deps) with a scanner when present (syft / ScanCode / FOSSA class), attach a license to every package, evaluate against the project's allow/review/deny policy (strong-copyleft entering a permissive/proprietary product → HIGH finding), and export an SPDX or CycloneDX SBOM artifact where CI expects one. No scanner installed → direct-dep license spot check from registry metadata + gap-note; never install tools unasked.

**Dependency-confusion defense (advisory — active attack vector, documented May 2026 npm campaign across ≥9 organizational scopes):** when the project uses internal/private packages, check the defense stack and report gaps: (1) internal packages use a claimed registry scope/namespace (`@org/…`) — unscoped internal names are hijackable from the public registry; (2) CI installs enforce the lockfile (`npm ci` / `pnpm install --frozen-lockfile` / `pip install --require-hashes`) — a mutable install can silently resolve a public lookalike; (3) registry resolution order pins the private registry for internal scopes (`.npmrc` scoped registry / `pip.conf` index priority) so public never shadows private; (4) where infrastructure allows, build servers restrict registry egress to the approved proxy. Missing layer → HIGH gap-note in the summary, never auto-reconfigured.

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
   | python (pip) | `pip install {name}=={version}` then update the project's pin file per its own convention (pip-tools: `pip-compile`; plain pins: edit `requirements.txt` entry) — never invent a new lock filename |
   | cargo | `cargo update -p {name} --precise {version}` |

2. Invoke `/ds-test --run` (advisory handoff — target absent → stack-native fast path directly: `npm test --bail`, `go test ./...`, `pytest -x`). Pass → proceed. Fail unresolved → revert manifest + lockfile, mark group `failed (tests broke)`, continue.
3. Invoke `/ds-commit --single` with message: `chore(deps): bump {scope-or-group} ({n} packages)`. Body lists each dep `{name}: {current} → {latest}`. Record hash.

**Review-major group (requires approval):**

1. Present every entry — one line each (`name: current → proposed · breaking?`) grouped by package class with counts; state the question (`Upgrade which of these N majors?`). "All" = exactly the displayed set. Full detail (breaking notes, migration steps from changelog, rollback path) under each entry.
2. Modes: **Apply All** / **Apply all without breaking notes** (per-class bulk alongside the total — majors whose changelog shows zero breaking entries) / **Review Each** / **Skip All** / **Defer**. **Under `--auto`:** no menu shown — every major resolves per Unattended Mode rule 3 (applied using the same impact/effort/risk reasoning the menu would have shown, recorded in the summary); nothing about a major version bump matches the irreversible-exception list, so none is stranded as `needs-human`.
3. Per approved major: apply bump, run **full** test suite (not quick); fail → revert + mark failed; pass → commit.
4. One commit per major: `chore(deps): upgrade {name} to {major-version}`. Body: breaking notes + migration link.

**Removal group (requires approval):**

1. Present candidates with "0 source references" evidence.
2. Approve → remove from manifest + lockfile, run quick tests, commit `chore(deps): remove unused {name}`. **Under `--auto`:** resolves automatically per Unattended Mode rule 3 — removed, quick-tested, and committed without approval (git history keeps this fully reversible).

**Mechanical Done Gate (SKILL-SPEC §4):** the per-group test run above is the test arm — add lint/type: resolve `{check-cmd}` in Phase 1 (ds-quality enforcement arm installed — stop-hook / pre-commit hook / auto-lint → its gate command; else stack-native lint/type/test commands; none detectable → Verification-Infrastructure Gap: report it, offer `/ds-quality`, record the decision) and capture the baseline before the first group — baseline red → done condition is "no *new* red", baseline reds reported, never inherited as green. A bump can break the type graph with tests still green (e.g. a types-package minor) — run `{check-cmd}` after each group before its commit; new red → same revert path as a test failure. After the last group: run the full `{check-cmd}` once — the aggregate run's exact command + observed output is the Completion Evidence; never report `OK` with a new red.

**Gate:** Every group has a commit or `failed`/`skipped` record. Working tree clean of THIS skill's changes. If fails → dirty tree (partial apply, no commit) → revert exactly the touched files via `git restore -- {manifest} {lockfile}` — never a tree-wide `git checkout -- .`, which would destroy the user's unrelated uncommitted work — mark `failed (dirty working tree)` for the summary, continue; revert itself fails → halt + surface conflict with modified-file list.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Covers ONLY items still undecided after Phase 5 (deferred majors/removals, `--auto`-skipped items) — items already decided in Phase 5's inline approval are never re-presented (no double-asking).

**Under `--auto`:** no review step is shown — remaining items (deferred majors/removals) resolve per Unattended Mode rule 3 (`fixed` or `failed`), except items matching the irreversible-exception list, which become `skipped (needs-human)`. **Interactive:** present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** Every B item has a decision (applied → fixed/failed, or explicitly skipped). If fails → undecided after prompt (dismissed/timed out) → mark `skipped (no decision)` for the summary, continue to Summary; do not re-prompt.

### Phase 7: Summary

FRC+DSC accounting.

```
| Dep              | Bump  | Class         | Disposition                          |
|------------------|-------|---------------|--------------------------------------|
| {pkg-name}       | {bump}| {class}       | {fixed-skipped-failed} ({short-hash}) |
```

`ds-deps: {OK|WARN|FAIL} | Bumped: {n} | Majors-pending: {n} | Skipped: {n} | Failed: {n} | Total: {n} | Advisories-closed: {n}`

**Gate:** Every dep has exactly one disposition; accounting balances. If fails → undisposed dep → assign `skipped (accounting gap)`; imbalanced → status `WARN` with note "{n} deps unaccounted — re-run to pick up the remainder from the last per-group commit".

**Value Delivered:** 1-5 concrete bullets, real upgrade outcomes only. Example shapes (placeholders, not literal):

- `{n} safe-patch + {m} safe-minor upgrades applied with per-group commits + green tests — dormant repo no longer accumulating CVE backlog`
- `{n} security advisories closed (CRITICAL: {x}, HIGH: {y}) — production exposure window narrowed`
- `{n} major upgrades surfaced with migration notes — known-breaking-version-bumps are now a deliberate decision, not a surprise`
- `{n} unused deps removed — lockfile shrunk, install time + supply-chain attack surface reduced`

Zero-change run: `All deps already at safe-current — no upgrades applied`.

## Quality Gates

- Lockfile always updated alongside manifest — no orphaned version mismatch.
- **Lockfile-diff integrity:** after each group, review the lockfile diff — only the expected packages change; any resolved-URL host change (registry → unexpected host / git+http), integrity-hash removal, or surprise transitive addition with install scripts → revert the group, CRITICAL finding (motivated by 2025-2026 registry-worm incidents where tampered lockfiles carried the payload).
- Peer-dep conflicts: detect via stack-native tool output; conflict → elevate to `review-major`.
- Workspace-wide consistency: dep across multiple workspace manifests → bump to a single version across all.
- **Slopsquatting guard:** before adding or accepting any new dependency, confirm it exists in the official registry, was registered before this project began, and has real download history; a near-miss or cross-ecosystem name is a typosquat until proven (~19.7% of LLM-suggested packages are hallucinated — [CSA 2026](https://labs.cloudsecurityalliance.org/research/csa-research-note-slopsquatting-ai-supply-chain-20260419-csa/)).
- **Dependency Adoption Eligibility gate (AND, all required)** — before accepting any brand-new dependency (distinct from the slopsquatting guard above, which verifies a candidate is real; this gate decides whether it should be added at all): (1) genuinely external — not reasonably hand-written for this codebase; (2) reimplementation cost exceeds a documented time-estimate threshold, or is technically infeasible; (3) shipped/bundled size stays under a documented ceiling — exceptions require explicit sign-off recorded in the same PR/commit; (4) serves an optional/lazy feature path, never the critical/eager runtime boot path; (5) is lazy-loaded, not eagerly bundled. Additionally: license is on an explicit allowlist (reject copyleft when incompatible with the project's distribution model); a provenance record (source repo URL, pinned version/commit hash, license) is committed alongside the dependency; a documented one-command removal/rollback path exists. Flag any new-dependency addition that doesn't address all five criteria plus license + provenance as `review-major`, never `safe-minor`.
- W1: every classification cites registry metadata + changelog URL. W2: after upgrade, verify no broken import in consumers. W3: only manifest + lockfile + approved source lines change. W4: re-read manifest before commit. W5: uncertain changelog → `review-major`, not `safe-minor`. W6: every group produces output. W7: dedup — same dep across monorepo workspaces listed once per workspace. W8: quote package names with version specifiers in shell; reject names containing shell metacharacters. W9: state-exempt — per-group commits are git checkpoints; re-run continues from remaining groups. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason. W16: dependency verified present in the registry (non-trivial age + downloads) and pinned in the lockfile before add; hallucinated or typosquat names rejected.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Registry unreachable | Retry once with 10s timeout; persistent → skip dep, continue |
| Changelog URL missing | Treat as breaking unless SemVer patch with no release notes flag; classify `review-major` |
| Test command not defined | Ask user for test command; offer to skip test gate with warning (marks group `unverified`). **Under `--auto`:** no ask — skips the test gate with warning and marks the group `unverified`, recorded in the summary |
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

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing.
