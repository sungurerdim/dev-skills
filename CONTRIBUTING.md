# Contributing

- **Bug** — open an issue naming the skill, what you ran, what happened and what its `SKILL.md` says should happen.
- **Rule change** — edit the rule in `core/rules/`; cite a source for every fact.
- **New skill** — open an issue first: it must do a job none of the four does, and pass the decision order in `core/kernel.md` §1 (is it needed, does it exist already, could something be removed instead).

Before a PR: `python3 scripts/check.py` and `python3 scripts/check.py --self-test` green. Repository rules: [AGENTS.md](AGENTS.md). Commits follow [Conventional Commits](https://www.conventionalcommits.org/).
