---
name: ds-release
description: Release cutter — version from the commits, dated CHANGELOG section, every version surface bumped, project check green, local release commit + annotated tag; every publishing step (push, GitHub release, registry, store) handed to the human with the exact command. Use when a release is to be cut.
---

# /ds-release

Cutting a release by hand means a version bumped in one file but not the other, a CHANGELOG still saying "Unreleased", a tag that points at the wrong commit, and a GitHub release created before the check was green. This skill derives the version from the commits, writes the changelog section, bumps every version surface consistently, proves the tree green, and tags — then stops at the boundary where work leaves the machine.

**Release Cutter** — version → changelog → bump → check → commit + tag → publish handoff → post-release verification.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-release`
- User says "cut the next release", "tag a version", "release 1.3.0", "prepare the changelog for release"
- ds-ship's release or launch mode reaches the release chain; ds-freeze's kept set is implemented and ready to ship

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "cut the next release", "bump the version and tag it" | "audit the CI pipeline" (→ ds-devops) |
| "reconcile the changelog for 1.3.0" | "write release notes for the app store listing" (→ ds-launch) |
| "verify the published release" (post-release) | "deploy to production" (→ ds-deploy) |
| "what version should the next release be" | "commit my changes" (→ ds-commit) |
| "the last release was wrong — roll it back" | "fix the failing test before we release" (→ ds-debug) |

## Contract

**Dimensions:** D6 (release engineering)

- Produces a local, verifiable release state: version files, CHANGELOG, a release commit and an annotated tag. Everything that publishes — `git push`, tags to a remote, `gh release create`, registry publish, store submission — is on the exception list ([../core/ask-exception-list.md](../core/ask-exception-list.md)): reported `only you can do` with the exact command by default; `--ask` may confirm and run it.
- Standalone. Reads git history, the changelog and the version surfaces; CI status only through `gh` when present (absent → `not verified` for anything remote).
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- **The version comes from the commits.** Conventional Commits since the last tag decide the bump (`feat` → minor, `fix`/`perf` → patch, `!` or `BREAKING CHANGE:` → major, pre-1.0 → minor for breaking); `--bump` overrides with the reason recorded. No commit-type signal → `only you can do: state the bump` (default: patch, recorded under `Decided without asking`).
- **One version, every surface.** Every version-carrying file in the repo is found and bumped together (manifest, lockfile entry, `__version__`, `pubspec.yaml`, `Cargo.toml`, `version.txt`, docs badge); a surface left behind is a finding.
- **Checkpoint** ([../core/checkpoint-protocol.md](../core/checkpoint-protocol.md)): `git status --porcelain` before the first write; a dirty tree → stop-hard (`only you can do: commit or stash first`) — a release commit must contain only the release.
- **Mechanical Done Gate:** `{check-cmd}` (ds-quality arm when installed, else the stack-native chain from [../core/toolchains.md](../core/toolchains.md)) captured at baseline and re-run after the bump; red → the release does not proceed to tagging; baseline red reported red-at-baseline and blocks the tag unless `--allow-red-baseline` is passed with the reason.
- State-exempt: the release commit, the tag and the CHANGELOG are the durable record.

## Arguments

| Flag | Effect |
|------|--------|
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |
| `--bump={x}` | `major` · `minor` · `patch` · `prerelease` · an explicit version `1.3.0` — overrides the commit-derived bump (reason recorded) |
| `--preview` | Derive version, render the changelog section and the version-file diff in chat; write nothing |
| `--notes={path}` | Additional release-notes source merged into the changelog section (e.g. `docs/release-notes/next.md`) |
| `--verify={tag}` | Post-release verification only: tag exists on the remote, CI run for it green, attestation/provenance present, registry/store shows the version |
| `--allow-red-baseline` | Tag even though `{check-cmd}` was red before the run (reported red-at-baseline in the summary); never silently |

Without flags: version derived, changelog reconciled, surfaces bumped, check green, commit + annotated tag created locally, publishing commands printed as `only you can do`. `--ask`: confirm the version, the changelog section and each publishing step.

## Scopes

5 scopes — version · changelog · tag · publish · post-release — each resolved by signal:

| Scope | What it covers |
|-------|----------------|
| version | Bump derivation and every version surface |
| changelog | `[Unreleased]` → `[x.y.z] - YYYY-MM-DD` reconciliation, links, kept-empty Unreleased |
| tag | Release commit + annotated tag on HEAD |
| publish | Push, GitHub release, registry, store — handoff only |
| post-release | `--verify`: remote tag, CI run, attestation, registry presence, smoke check |

| Scope | Runs when (signal) | Otherwise |
|-------|--------------------|-----------|
| version | any repo with ≥ 1 version surface | `N/A — no version surface` (a tag-only release: tag still created) |
| changelog | `CHANGELOG.md` (or `CHANGES.md`, `HISTORY.md`) present, or `--notes` given | created from the commits since the last tag when absent, stated in the summary |
| tag | always | — |
| publish | `git remote` non-empty | `N/A — no remote` |
| post-release | `--verify` or the previous run's tag is already on the remote | `N/A — nothing published yet` |

## Delegation

**Owns:** versioning, changelog, tagging, release-notes | **Delegates:** ds-commit → the release commit (absent → inline `git commit -m "chore(release): {version}"`); ds-devops → CI run + attestation verification after publish (absent → inline `gh run watch` + `gh attestation verify` when `gh` is present, else `not verified`); ds-launch → store submission after the tag (absent → the store step is handed to the human with the command) | **Receives:** ds-ship → Phase 5 release chain; ds-freeze → release of the kept set

## Execution Flow

Assess → Version → Changelog → Bump → Check → Commit + tag → Publish handoff → [Post-release verify] → Summary

### Phase 1: Assess

1. `git describe --tags --abbrev=0` → last tag (none → first release; the initial version comes from the manifest or `0.1.0`). `git log {last-tag}..HEAD --format='%s%n%b'` → commits since.
2. Version surfaces: search for the current version string across tracked files (`git grep -n -F '{current}'` scoped to manifests, `__version__`, `version.txt`, `pubspec.yaml`, `Cargo.toml`, `*.csproj`, docs badges); list every hit.
3. Changelog file and its `[Unreleased]` section; `--notes` source when given.
4. Remote + `gh` availability → whether publish/post-release scopes can run.
5. Resolve `{check-cmd}`, capture the baseline; Checkpoint pre-gate (dirty → stop-hard).

**Gate:** Last tag (or first-release state), commit list, every version surface and the changelog located; tree clean; baseline captured. If fails → dirty tree → `only you can do: commit or stash first`; no version surface and no changelog → proceed with tag-only and say so.

### Phase 2: Version

Derive the bump from the commits (Contract rule) → `{next}`. Pre-release (`--bump=prerelease` or a `-rc`/`-beta` current version) increments the pre-release counter. `--preview` prints `{current} → {next}` with the deciding commits. `--ask` confirms.

**Gate:** `{next}` is a valid SemVer greater than `{current}` and not an existing tag. If fails → tag exists → `only you can do: {next} already tagged — pass --bump` ; no conventional commits → default patch under `Decided without asking`.

### Phase 3: Changelog

1. Render the section from `[Unreleased]` (plus `--notes`): `## [{next}] - {YYYY-MM-DD}` with `### Added / Changed / Fixed / Removed / Security` sub-headings kept in Keep-a-Changelog order; commits since the last tag that are not reflected in Unreleased are added under the matching heading (`feat` → Added, `fix` → Fixed, `perf`/`refactor` with user-visible effect → Changed, `!` → a leading **Breaking** line).
2. Keep an empty `## [Unreleased]` above the new section; update the compare links at the bottom when the file uses them.
3. No changelog file → create `CHANGELOG.md` with the header, the empty Unreleased section and this release's section (Keep a Changelog 1.1.0 format).

**Gate:** New section present with the date, Unreleased empty, every user-visible commit since the last tag represented. If fails → a commit's user impact is unclear → listed under Changed with its subject and marked for the human to reword (`only you can do` line), the release proceeds.

### Phase 4: Bump

Rewrite every version surface found in Phase 1 to `{next}` (lockfile entries via the package manager's own command when one exists — `npm version {next} --no-git-tag-version`, `cargo set-version` when installed, `poetry version`, else a direct edit); re-run the search → zero remaining `{current}` hits in version surfaces.

**Gate:** All surfaces at `{next}`, none left behind. If fails → a surface cannot be edited (generated file) → record how it is regenerated and add it to the release commit after regeneration.

### Phase 5: Check

Run the full `{check-cmd}` → green required. Red → fix ≤ 3 attempts (same command); still red → stop before tagging, revert the bump (`git checkout -- {version files} CHANGELOG.md`), report the failing output; a red baseline blocks the tag unless `--allow-red-baseline` (then reported red-at-baseline in the summary and the changelog is untouched by that decision).

**Gate:** `{check-cmd}` green (or no new red under `--allow-red-baseline`). If fails → red → release aborted with the output; nothing committed, nothing tagged.

### Phase 6: Commit + tag

1. Release commit: only the version surfaces and the changelog — `chore(release): {next}` (ds-commit when present; hooks never bypassed).
2. Annotated tag on that commit: `git tag -a v{next} -m "v{next}"` (tag prefix follows the repo's existing tags — `v1.2.3` or `1.2.3`).
3. Verify: `git tag --points-at HEAD` lists the tag; `git log -1 --format=%s` is the release commit.

**Gate:** Commit and tag on HEAD, tree clean. If fails → hook rejects the commit → fix what it names and retry (≤ 3); tag creation fails (exists, bad name) → `only you can do` with the state, the commit stays.

### Phase 7: Publish handoff

Every publishing step is printed as a `only you can do` line with the exact command, in order, and nothing is executed: `git push origin main --follow-tags` (or the branch) · `gh release create v{next} --notes-file {rendered-section-file} --verify-tag` (or `--generate-notes`) · registry publish (`npm publish`, `cargo publish`, `dart pub publish`, `twine upload` — per stack) · store submission (ds-launch when present). `--ask`: each step is offered for confirmation and run only on an explicit yes, then verified (`git ls-remote --tags origin v{next}`, `gh release view v{next}`).

**Gate:** Handoff list printed (or, under `--ask`, each confirmed step verified). If fails → a confirmed push is rejected (protected branch, diverged) → report the exact error, no force-push ever.

### Phase 8: Post-release verify [--verify, or after a confirmed publish]

| Check | Command | Expected |
|-------|---------|----------|
| Remote tag | `git ls-remote --tags origin v{next}` | one line |
| CI run for the tag | `gh run list --branch v{next}` then `gh run watch {id}` | conclusion `success` |
| Attestation / provenance | `gh attestation verify {artifact} --repo {owner}/{repo}` (or the registry's provenance badge) | verified |
| Registry / store presence | `npm view {pkg} version` · `cargo search {crate}` · `pip index versions {pkg}` · store console (ds-launch) | `{next}` |
| Smoke | Install or fetch `{next}` into a temp dir and run its smallest real command / import | exit 0 |
| Rollback path | The previous tag and how to re-point (`git revert` of the release commit + a patch release; registries: deprecate, never unpublish) | recorded in the summary |

**Gate:** Every applicable check observed. If fails → any check red → `Post-release: FAIL` with the failing output and the rollback path; never claim a release verified without the outputs.

### Phase 9: Summary

```
ds-release: {OK|WARN|FAIL} | Version: {current} → {next} | Changelog: {section written | created | N/A} | Surfaces: {n} bumped | Tag: v{next} on {hash} | Check: {green | red-at-baseline} | Publish: {only you can do (n steps) | confirmed (n)} | Post-release: {verified | N/A | FAIL}
```

Then the verify-echo (`{check-cmd}` output, `git tag --points-at HEAD`, `git log -1`), `Decided without asking` lines, and every `only you can do` step with its command ([../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md)). Status: OK (commit + tag green, handoff printed), WARN (a surface or changelog entry needs a human), FAIL (check red or aborted).

**Gate:** Summary printed with the outputs. If fails → an output missing → re-run that command and paste it.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `Release {next} is cut consistently — {n} version surfaces agree, the changelog says what changed, the tag sits on a commit the project check proved green`
- `Publishing stays a human decision — the exact {n} commands are listed, nothing left the machine`
- `Post-release verified — the tag, CI run and registry all show {next}; the rollback path is written down`

Zero-change run: `Nothing to release — no commits since v{current}`.

## Quality Gates

- The tag is never created on a red check; the release commit contains only version surfaces and the changelog
- Nothing is pushed, published, or submitted without an explicit confirmation under `--ask`; the default prints the commands
- Version surfaces are found by search, never assumed from one manifest
- W9: state-exempt — commit, tag and changelog are the record. W10: a fresh `ds/audit/findings.md` is consumed for release-blocking findings (CRITICAL open → WARN in the summary), never re-detected.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No tags at all | First release: version from the manifest (or `0.1.0`), changelog section from the whole history, stated in the summary |
| Monorepo with several versioned packages | One release per package (`--scope={pkg}` via the request) or a coordinated bump when the repo uses a single version; never mix |
| `gh` absent for `--verify` | Remote tag via `git ls-remote`; CI/attestation/registry reported `not verified` with the commands the human can run |
| Release must be undone | Local only: `git tag -d v{next}` + `git reset --hard HEAD~1` is refused (checkpoint rule) — instead `git revert` the release commit and keep the tag history; published → deprecate/yank per registry, never rewrite the remote |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Unreleased section already has a version header by hand | Respect it when it equals `{next}`; otherwise report the mismatch and use the derived version |
| Breaking change on a pre-1.0 project | Minor bump, `**Breaking**` line kept in the changelog |
| Tag prefix mixed in history (`v1.2.0` and `1.1.0`) | Follow the most recent tag's style and report the inconsistency |
| Release notes requested for a store listing | Changelog section rendered; store copy is ds-launch's (advisory handoff) |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
