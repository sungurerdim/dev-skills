# ds-pipeline

Plans written ad hoc skip what matters: tasks without verification criteria, specs contradicting plans, clarifications never asked — so the executor guesses, and guesses wrong.

**Spec pipeline conductor — runs the Spec Kit chain with blocking gates and hands off a commit-ready, test-gated plan.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-pipeline ~/.claude/skills/ds-pipeline` |
| **Cursor** | Copy `SKILL.md` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

[Spec Kit](https://github.com/github/spec-kit) accelerates the run when initialized (`specify init`) — absent, the skill runs the same chain natively and writes the same artifacts.

## Use

```
/ds-pipeline {one-paragraph feature idea}
/ds-pipeline --feature={slug}          # resume an existing feature's pipeline
/ds-pipeline --feature={slug} --refresh  # regenerate all artifacts (confirmed)
```

## Flags

| Flag | Effect |
|------|--------|
| `{idea}` | Fresh run — plans the described feature |
| `--feature={slug}` | Overrides the derived `specs/{slug}/` directory name |
| `--refresh` | Regenerates all artifacts after confirmation |

## Features

- **Blocking gates between every step** — zero open clarifications, 100% verify-line coverage, zero CRITICAL consistency findings; a failed gate stops the run instead of degrading it
- **Tasks-contract enforcement** — every task ships as `- [ ] T{n}: … — verify: `{command}` → {expected}`; behavioral tasks stated as EARS sentences
- **Clean handoff** — one scoped `spec({feature})` commit plus a one-line executor instruction; nothing else touched
- **Artifact-driven resume** — re-running continues from the first missing artifact; no state files
- **Planning only** — writes exclusively under `specs/` and `.specify/`; source code is never modified
- **Native mode** — Spec Kit absent → the skill performs the same chain inline, same output shape, same gates
