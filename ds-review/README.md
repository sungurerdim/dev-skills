# ds-review

Code review catches what tests miss — security holes, dead code, wrong abstractions, and performance traps hiding in plain sight. Skill scans for all of them with file:line precision.

**Tactical fixes + strategic architecture + deep performance profiling + principle-based meta-quality (SSOT / DRY / KISS / SoC). 30+ scopes.**

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
| **Meta-Quality** | Principle audit: SSOT / DRY / KISS / SoC + criteria-fit baselines + 3 consolidation paths per finding |

## Features

- 8 tactical scopes (86 checks) + 9 strategic scopes (103 checks) + 11 perf groups + 5 meta-quality detector scopes + 1 derived alias
- Diff scoping (default when a diff exists): reviews only changed files + their direct consumers instead of the whole repo; `--diff[={ref}]` forces it explicitly, `--scope=all` forces a full-repo scan
- `yagni` / `obsolete` / `duplicate` (function-level) detection and the tactical `simplify` scope are delegated to ds-simplify
- Anti-overengineering 3-gate screens every finding before reporting (false-positive guard)
- Score calculation per scope with CRITICAL/HIGH caps
- Needs-approval protocol for cross-module changes with reason validator (rejects "pre-existing" / "out of scope" / "too hard" / "not my change")
- CRITICAL escalation: every CRITICAL finding re-verified ±20 lines before reporting
- Loop mode: re-run until clean (max 3 iterations)
- Education per fix: why, avoid, prefer
- Meta-quality: criteria-fit baselines per project type; 3-path proposals (Minimal / Moderate / Structural) with effort / impact / risk
- Cross-scope deduplication: same file:line → merge; within 10 lines + same issue → merge
