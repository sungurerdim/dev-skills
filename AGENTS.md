# AGENTS.md

Instructions for any coding agent working **on** this repository.

dev-skills ships four Agent Skills (`ds-audit`, `ds-gate`, `ds-setup`, `ds-research`) and the shared `core/` they all load. Skills are Markdown; the only code is Python 3.8+ stdlib: `install.py`, `scripts/check.py`, `evals/*.py`, and each skill's `assets/*.py`.

## Commands

| Task | Command |
|------|---------|
| Quality gate (before every commit) | `python3 scripts/check.py` |
| Prove every gate check still catches its defect | `python3 scripts/check.py --self-test` |
| Run both on every commit | `python3 scripts/check.py --install-hook` |
| Install / check drift / uninstall | `python3 install.py` · `--check` · `--uninstall` |
| Validate the eval scorer | `python3 evals/ship_library.py validate` |

There is no CI; the gate is the only enforcement. A red gate is fixed, never bypassed (`--no-verify` is never used). A check that cannot run says so; it is never reported as passing.

## Rules that are not guessable from the code

- **One home per fact.** Shared guidance lives once in `core/`; a skill links `../core/<file>.md` and adds only what is specific to it. The gate fails on a long line repeated in two shipped files and on near-duplicate rule titles.
- **Standalone skills.** A link from a skill may resolve only inside its own directory or `core/` (what one install ships). Mentioning another skill by name in prose is fine.
- **`core/kernel.md` is loaded by every skill.** Change it only for something every skill needs; section numbers (§1-§7) are cited from skills and rule files.
- **Rules:** `### ID [CRITICAL|HIGH|MEDIUM|LOW] Title`, then Detect / Fix / Impact / Source; IDs are unique across `core/rules/`. A new rule file needs a row in `core/rules/README.md` (area, load signal, ID prefix, standards).
- **Sizes:** `SKILL.md` ≤ 8 KB; anything situational goes to the skill's `references/`.
- **A new gate check needs a self-test case** in `scripts/check.py` that injects its defect and sees it go red.
- **Versions:** `.claude-plugin/marketplace.json` and the top `CHANGELOG.md` entry must agree (semver).
- **Conventional Commits.** `feat`/`fix` only when a user-visible capability changes.
- `ds/audit/` is per-run scratch output of `ds-audit`; never commit it.
