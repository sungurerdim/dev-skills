# ds-review

Tactical file-level fixes + strategic architecture analysis + deep performance profiling. 25+ scopes.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-review ~/.claude/skills/ds-review` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-review`, or ask to review your code quality.

## Modes

| Mode | What It Does |
|------|-------------|
| **Tactical** (default) | File-level: security, hygiene, types, performance, privacy |
| **Strategic** | Architecture-level: patterns, coupling, testing, production readiness |
| **Performance** | Deep profiling: bundle size, startup time, memory, caching, Core Web Vitals |

## Features

- 9 tactical scopes (97 checks) + 8 strategic scopes (92 checks) + 8 perf scopes
- Score calculation per scope with CRITICAL/HIGH caps
- Needs-approval protocol for cross-module changes
- Loop mode: re-run until clean (max 3 iterations)
- Education per fix: why, avoid, prefer
- Performance mode: bundle, startup, runtime, caching, network, Web Vitals, mobile, DB
