# ds-release

Cutting a release by hand means a version bumped in one file but not the other, a CHANGELOG still saying "Unreleased", and a tag on a commit nobody checked.

**Release cutter — version from the commits, dated changelog section, every version surface bumped, project check green, local commit + annotated tag; publishing handed to the human with the exact commands.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git && cd dev-skills && ./install.sh
```

Any Agent Skills host: `./install.sh --target <that host's skills dir>` (ships `core/` beside the skill).

## Use

```bash
/ds-release                        # derive version, reconcile changelog, bump, check, commit + tag locally
/ds-release --preview              # show current → next, the changelog section and the diff; write nothing
/ds-release --bump=minor           # override the commit-derived bump (major · minor · patch · prerelease · 1.3.0)
/ds-release --notes=docs/next.md   # merge extra release notes into the section
/ds-release --ask                  # confirm version, changelog, and each publishing step (push, gh release, registry)
/ds-release --verify=v1.3.0        # post-release: remote tag, CI run, attestation, registry presence, smoke, rollback path
```

## Flow

1. Assess — last tag, commits since, every version surface, changelog, remote/`gh`, check baseline, clean tree
2. Version — Conventional Commits decide the bump (`feat` minor · `fix` patch · `!` major)
3. Changelog — `[Unreleased]` → `[x.y.z] - date`, Unreleased kept empty, links updated (file created when absent)
4. Bump — all surfaces together, re-search proves none left behind
5. Check — the project's own chain green, else the release aborts and the bump is reverted
6. Commit + tag — `chore(release): x.y.z` + annotated `vx.y.z` on HEAD
7. Publish handoff — push / `gh release create` / registry / store printed as `only you can do`
8. Post-release verify — tag on remote, CI green, attestation, registry shows the version, smoke, rollback path
9. Summary — verify-echo, assumptions, every human step with its command

## Scopes

5 scopes: version, changelog, tag, publish, post-release — each resolved by signal (no remote → publish `N/A`).

## Features

- **Version from evidence** — commits decide; overrides are recorded with a reason
- **One version, every surface** — found by search, not assumed from one manifest
- **Never tags red** — the check gate sits before the tag; a red baseline blocks unless explicitly allowed
- **Publishing stays human** — nothing leaves the machine without an explicit yes under `--ask`
- **Post-release proof** — remote tag, CI run, attestation, registry, smoke; rollback path written down
- **Checkpoint stop-hard** — a release commit contains only the release
