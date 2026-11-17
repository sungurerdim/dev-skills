# Scope

Purpose: "Agent Skills that let one developer and an AI assistant ship production-quality software: a whole-project audit that fixes what is safe, a machine-enforced quality gate, a hardened AI-dev rig, and fact-checked research briefs." (README.md)

Done when: "Every skill works alone" (README.md) — each of the four skills installs with `python3 install.py` and runs on its own, and `python3 scripts/check.py` plus `python3 scripts/check.py --self-test` are green.

The product is the Markdown (`ds-*/SKILL.md`, `references/`, `core/`); the rows below are the Python units `audit.py lean` measures.

| Unit | Tier | Serves | Evidence |
|------|------|--------|----------|
| `core` | T0 | signal detection and the check command every skill uses | `core/ds_detect.py`, imported by ds-audit and ds-gate assets |
| `ds-audit/assets` | T0 | ds-audit mechanics | `ds-audit/SKILL.md` Mechanics |
| `ds-gate/assets` | T0 | the quality gate hook | `ds-gate/SKILL.md` |
| `ds-setup/assets` | T0 | permissions, probe and rc deny hook | `ds-setup/SKILL.md` |
| `ds-research/assets` | T0 | the brief verifier | `ds-research/SKILL.md` |
| `.` | T0 | install, drift check and uninstall | README.md Install; `install.py` |
| `scripts` | T1 | the only gate (`check.py`) and claude.ai packaging (`package.py`) | AGENTS.md Commands; README.md Install |
| `evals` | T1 | scorer for skill-behaviour evals | AGENTS.md Commands; `evals/README.md` |

Budget: units ≤ 9 · deps ≤ 0 · docs ≤ 745 KB

Budget set to the `audit.py lean` budget line (2026-11-17): measured + 10 %; the zero-headroom budget turned lean-check red on the next doc commit.

Rules reviewed: 2026-11-17 (74d03eb)
