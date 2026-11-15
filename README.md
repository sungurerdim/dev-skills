# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-4-blue)]()

Agent Skills that let one developer and an AI assistant ship production-quality software: a whole-project audit that fixes what is safe, a machine-enforced quality gate, a hardened AI-dev rig, and fact-checked research briefs. Plain Markdown plus Python 3.8+ stdlib scripts; no runtime dependencies, no telemetry.

## Skills

| Skill | Use it to |
|-------|-----------|
| `/ds-audit` | Audit and improve a project: detect what it is, check every area that applies against named standards, fix what is safe, verify with the project's own checks, report. By default it checks only what your branch changes against the remote; `all` audits the whole project, `sec a11y` narrows to those areas, `dry` only reports. |
| `/ds-gate` | Make format, lint, type and test checks block "done" (Claude Code, Codex, Gemini), every edit (Aider) or every commit (git hook — Copilot, Cursor, Windsurf, terminal). `inv "<rule>"` turns one custom rule into a red-proven gate; `checks`, `arm`, `prove`, `run`, `status` run one part. |
| `/ds-setup` | Set up the machine: pinned tools, telemetry off in every tool and harness, permission profiles where risk-free work never prompts and dangerous commands are denied (wrappers such as `rtk` included), MCP budget. `tools`, `update`, `privacy`, `perms`, `mcp` run one part. |
| `/ds-research` | Research a topic into one offline, printable HTML brief: every datum confirmed by two independent sources or flagged, primary sources for load-bearing facts, checked by a verifier script. `quick` gives a sourced answer with a DO / AVOID / CONDITIONAL verdict in the chat instead. |

Every skill works alone. Arguments are plain words in any order (`/ds-audit all sec dry`): no word runs everything, a part's word runs that part alone, `dry` only reports and `ask` turns each decision into a question with a recommended answer. Without `ask`, each run decides from evidence and records its decisions. Pushing, publishing and anything that needs a human-only value are always left to you, with the exact command.

## How it works

```
core/kernel.md        loaded by every skill: decision order, working rules, evidence, severity, autonomy, report,
                      and the named principles every finding cites (YAGNI, KISS, SOLID, Chesterton's fence, …)
core/signals.md       what the project is (ui, api, db, pii, mobile, …), detected from files
core/rules/README.md  area → rule files → when they load → the standards they check against (OWASP, WCAG, GDPR, …)
core/rules/*.md       the rules, unique IDs, each with Detect / Fix / Impact / Source
core/toolchains.md    per-stack format, lint, type and test commands
ds-*/SKILL.md         one job per skill, ≤ 8 KB, details in its own references/
```

The decision order is the base of everything, applied to the run itself, each need it finds, and each fix it plans: **question** the need → **reuse** what exists → **delete** instead of adding → **simplify** → **accelerate** only against a measurement → **automate** last. A skill loads only the rule files whose project signal holds.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git
cd dev-skills
python3 install.py                      # ~/.claude/skills (Claude Code; OpenCode reads it too)
python3 install.py --dir ~/.codex/skills  # any other Agent Skills directory
python3 install.py --skills ds-audit     # a subset; core/ always ships
python3 install.py --check              # drift between this checkout and the install
python3 install.py --uninstall
```

On Windows use `py install.py`. Updating is `git pull && python3 install.py`: every install first removes everything earlier dev-skills versions installed (all retired skills, old `core/` files, the pre-3.0 shell hook launchers), so nothing old can shadow the new files. Skills you added yourself are never touched.

Hosts without a skills loader (Aider, Windsurf) can reference a `SKILL.md` directly; `ds-gate` still wires its Aider and git-hook arms there.

## Upgrading from 2.x

3.0.0 keeps four skills and folds the rest into `ds-audit` and the shared rules. The other 28 skills are removed; their rules live in `core/rules/`, and `/ds-audit <area>` replaces running one domain skill (for example `/ds-audit a11y` for ds-frontend's accessibility pass, `/ds-audit privacy` for ds-compliance, plain `/ds-audit` for ds-review); the old chat-answer ds-research is `/ds-research quick`, and ds-ship, ds-quality, ds-rig and ds-brief are now ds-audit, ds-gate, ds-setup and ds-research. `--flag` spellings still work. Commit, PR and release conventions belong to an always-on rules layer such as [dev-rules](https://github.com/sungurerdim/dev-rules). See [CHANGELOG.md](CHANGELOG.md).

## Contributing

`python3 scripts/check.py` is the only gate (there is no CI): skill format and size, links, unique rule IDs, no near-duplicate rules, no line repeated across files, every core file has a consumer, version agreement, the five asset self-tests, and spelling when `typos` is installed. `python3 scripts/check.py --self-test` proves each check catches the defect it exists for; `--install-hook` runs both on every commit. Details: [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md).

## License

MIT
