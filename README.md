# dev-skills

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-4-blue)]()

Agent Skills that let one developer and an AI assistant ship production-quality software: a whole-project audit that fixes what is safe, a machine-enforced quality gate, a hardened AI-dev rig, and fact-checked research briefs. Plain Markdown plus Python 3.8+ stdlib scripts; no runtime dependencies, no telemetry.

## Skills

| Skill | Use it to |
|-------|-----------|
| `/ds-audit` | Audit and improve a project in five phases (lean, build, safe, surface, ship): detect what it is, cut what its purpose does not need (purpose, unit tiers and budget in `SCOPE.md`), read every file in scope (in parallel review groups, tracked file by file: an unread file makes the run INCOMPLETE), check every area that applies against named standards, fix every finding a test or check can prove, verify with the project's own checks, report in `ds/audit/report.md` and a printable `report.html`, ending with the decisions only you can make, each with options and a recommendation. By default it checks only what your branch changes against the remote; `all` audits the whole project on a review branch `ds/audit` that it pushes, without force, for you to merge (`local` keeps it unpushed); `sec a11y` or a phase word narrows the run, `dry` only reports, `auto` takes even the scope decisions itself. A project program it needs to see run goes through `audit.py probe`: temporary HOME, no network. |
| `/ds-gate` | Make format, lint, type and test checks block "done" (Claude Code, Codex, Gemini), every edit (Aider) or every commit (git hook — Copilot, Cursor, Windsurf, terminal). `inv "<rule>"` turns one custom rule into a red-proven gate; `checks`, `arm`, `prove`, `run`, `status` run one part. |
| `/ds-setup` | Set up the machine: pinned tools, telemetry off in every tool and harness, permission profiles where risk-free work never prompts and dangerous commands are denied (wrappers such as `rtk` included), MCP budget. `tools`, `update`, `privacy`, `perms`, `mcp` run one part. |
| `/ds-research` | Research a topic into one offline, printable HTML brief: every datum confirmed by two independent sources or flagged, primary sources for load-bearing facts, checked by a verifier script. `quick` gives a sourced answer with a DO / AVOID / CONDITIONAL verdict in the chat instead. |

Every skill works alone. Arguments are plain words in any order (`/ds-audit all sec dry`): no word runs everything, a part's word runs that part alone, `dry` only reports and `ask` turns each decision into a question with a recommended answer. Without `ask`, each run decides from evidence and records its decisions. Merging, publishing, releasing and anything that needs a human-only value are always left to you, with the exact command; the one push a skill makes is ds-audit's own review branch, without force.

## How it works

```
core/kernel.md        loaded by every skill: decision order, working rules, evidence, severity, autonomy, report,
                      and the named principles every finding cites (YAGNI, KISS, SOLID, Chesterton's fence, …)
core/signals.md       what the project is (ui, api, db, pii, mobile, …), detected from files
core/rules/README.md  area → rule files → when they load → the standards they check against (OWASP, WCAG, GDPR, …)
core/rules/*.md       the rules, unique IDs, each with Detect / Mech / Fix / Impact / Source (S and T rules also Fixture)
core/ds_detect.py     stack, check command and signal detection shared by ds-audit and ds-gate
core/toolchains.md    per-stack format, lint, type and test commands
ds-*/SKILL.md         one job per skill, ≤ 8 KB, details in its own references/
ds-audit/assets       audit.py: every countable step of a run (init, scan, validate, phase, report, lean, probe, …)
```

The decision order is the base of everything, applied to the run itself, each need it finds, and each fix it plans: **question** the need → **reuse** what exists → **delete** instead of adding → **simplify** → **accelerate** only against a measurement → **automate** last. A skill loads only the rule files whose project signal holds. Every rule has a `Mech:` command, run offline with POSIX regex; the gate runs each one on a fixture.

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

**claude.ai:** `python3 scripts/package.py` writes one self-contained zip per skill to `dist/` (the shared `core/` is copied into each, links rewritten and checked). Upload each under Customize > Skills > Upload a skill; scripts need code execution turned on.

Hosts without a skills loader (Aider, Windsurf) can reference a `SKILL.md` directly; `ds-gate` still wires its Aider and git-hook arms there.

## Upgrading from 2.x

3.0.0 keeps four skills and folds the rest into `ds-audit` and the shared rules. The other 28 skills are removed; their rules live in `core/rules/`, and `/ds-audit <area>` replaces running one domain skill (for example `/ds-audit a11y` for ds-frontend's accessibility pass, `/ds-audit privacy` for ds-compliance, plain `/ds-audit` for ds-review); the old chat-answer ds-research is `/ds-research quick`, and ds-ship, ds-quality, ds-rig and ds-brief are now ds-audit, ds-gate, ds-setup and ds-research. `--flag` spellings still work. Commit, PR and release conventions belong to an always-on rules layer: your global or project `AGENTS.md`. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

`python3 scripts/check.py` is the only gate (there is no CI): skill format and size, links, rule headings, unique IDs, no near-duplicate rules, `Mech:` lines run on their fixtures, every kernel principle cited by a rule, no line repeated across files, every core file has a consumer, version agreement, every Python file compiles, every asset's self-test (`install.py --self-test` included, run hook-safe), and spelling when `typos` is installed. `python3 scripts/check.py --self-test` proves each check catches the defect it exists for; `--install-hook` runs both on every commit. Details: [AGENTS.md](AGENTS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md).

## License

MIT
