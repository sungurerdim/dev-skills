# ds-test

Universal test skill — generate, update, run, and fix tests for any stack.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-test ~/.claude/skills/ds-test` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

Run `/ds-test`, or ask to write tests, improve coverage, or fix failing tests.

## Modes

| Mode | What It Does |
|------|-------------|
| **Generate** | Write tests for uncovered code (unit, integration, E2E) |
| **Update** | Sync tests after source code changes |
| **Run + Fix** | Execute tests, classify failures, fix test-side issues |
| **Coverage** | Analyze gaps and fill them with new tests |
| **Setup** | Install test framework and create initial config |

## Supported Stacks

Node.js (Vitest/Jest/Playwright), Python (pytest/Playwright), Go, Rust, Flutter, JVM (JUnit/Kotest), Swift (XCTest), C#/.NET (xUnit/Playwright), Ruby (RSpec/Capybara), PHP (PHPUnit/Pest), Elixir (ExUnit), C/C++ (Google Test/Catch2), Scala (ScalaTest).

## Features

- **Convention-first** — reads existing tests to learn your style, then generates matching tests
- **Behavioral naming** — test names describe what the behavior is, not how it's implemented
- **Smart classification** — distinguishes test bugs from app bugs, never weakens assertions
- **Findings integration** — app bugs found during test runs written to `.ds-findings.md` for downstream code review
- **Run-fix loop** — runs, fixes, re-runs until green (max 3 iterations)
