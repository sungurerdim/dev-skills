# ds-research

AI models hallucinate sources, cite outdated data, can't distinguish blog post from peer-reviewed study. Skill searches, scores source reliability, synthesizes with citations.

**Multi-source research with CRAAP+ reliability scoring and tiered synthesis.**

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-research ~/.claude/skills/ds-research` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-research`, or ask to research a topic.

## Flow

1. Resolve scope areas: local codebase / security-CVE / changelog-releases / dependencies
2. Parallel web search across multiple source categories, widening past T1/T2 only when they don't converge
3. Score each source using CRAAP+ methodology (Currency, Relevance, Authority, Accuracy, Purpose)
4. Synthesize findings with citation and contradiction resolution
5. Output with confidence level and recommendation

## Features

- **CRAAP+ scoring** — 5-dimension reliability assessment for every source
- **Source tiers** — T1 (official docs) through T6 (unverified), auto-classified
- **Saturation gate** — stops searching once top-tier sources converge, widens automatically when they don't — no manual depth dial
- **Dependency mode** — registry lookups for version/CVE checking
- **Triangulation** — no claim without 2+ independent sources
