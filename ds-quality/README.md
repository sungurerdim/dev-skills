# ds-quality

Agents promise "done" without proof; code quality ends up depending on whether an instruction
was followed, not on a mechanism. This skill installs a single quality entry point (format →
lint → type → test) and wires it into a host-appropriate enforcement arm that blocks "done" (or
the commit) until it passes green. Quality becomes a mechanism, not a hope.

## Install

One command per host — each wires the same Phase-3 entry point into that host's own enforcement point:

| Host | Install | Arm | When it fires | Strength |
|------|---------|-----|----------------|----------|
| Claude Code | `/ds-quality --install` (once, global) | Stop hook (`~/.claude/hooks/ds-quality-gate.sh`) | Every Stop | Full — blocks "done" itself |
| Codex CLI | `/ds-quality --arm codex` | `.codex/hooks.json` `Stop` hook | Every Stop | Full — blocks "done" itself (loop-guarded) |
| Gemini CLI | `/ds-quality --arm gemini` | `.gemini/settings.json` `AfterAgent` hook | Agent loop end | Full — forces retry/halt on red |
| Aider | `/ds-quality --arm aider` | `.aider.conf.yml` `auto-lint`/`auto-test` + `lint-cmd`/`test-cmd` | After every edit | Full — Aider re-runs it inline |
| GitHub Copilot | `/ds-quality --arm copilot` | `.github/hooks/*.json` `preToolUse` commit-deny + `agentStop` report | `git commit` tool call | Before-commit — `agentStop` cannot block, stated honestly |
| Cursor, Windsurf, any other host | `/ds-quality --arm git-hook` | git `pre-commit` hook | `git commit` | Before-commit only — an agent can still claim "done" between an edit and the commit |

## How it works

**Claude Code (default arm):** one always-active global gate, installed once. On Stop it resolves
a command in priority: **marker** (`.claude/ds-quality.json`, `enabled:false` = per-repo off) →
**auto-arm** (no marker, repo under a trusted root: `ds-quality-detect.sh` runs the tools that
already exist) → **inert** (nothing to check / outside roots → no-op). Green → allow; red → block
with the failing output. Never edits your code. Loop-guarded (`stop_hook_active`).

**Aider:** the same entry point is wired into Aider's built-in `auto-lint`/`auto-test`, so it reruns
after every edit — no Claude Code hook involved.

**Any other host:** a git `pre-commit` hook runs the same entry point before every commit.

Mature repos (already have format/lint/test) are enforced **with zero per-repo steps** once the
Claude Code arm is globally installed. You only run `/ds-quality` in a repo to **bootstrap missing
tooling** — it won't silently scatter configs/tests everywhere.

## Usage

```
/ds-quality --install       # one-time: install the Claude Code arm globally (do this once)
/ds-quality                 # bootstrap THIS repo's missing tooling, then select/wire an arm
/ds-quality --arm aider     # force the Aider arm instead of auto-detecting the host
/ds-quality --run           # run this repo's resolved quality command now
/ds-quality --status        # show mode/roots + what auto-arm resolves here + wired arm(s)
/ds-quality --invariant "…" # build a custom gate from a described invariant (parity, absence,
                            #   generated-file sync, floor, docs↔code) — red-proven + chain-wired
/ds-quality --disable       # per-repo kill switch (.claude/ds-quality.json enabled:false)
/ds-quality --project-hook  # register the Claude Code hook in THIS repo's .claude/settings.json
/ds-quality --uninstall     # remove the installed arm(s) + scripts + config
```

## Supported stacks

JS/TS (node), vanilla JS (`node:test`, no bundler), Dart/Flutter, Python, Go (incl.
golangci-lint when configured), Rust, JVM (Gradle), Swift, C#/.NET, Ruby, PHP, Elixir,
Scala, C/C++ (static analysis), Terraform (format check), Shell/Bash, Docker (lint),
Makefile-driven, plus a generic fallback that wires universally-available checks and flags
coverage gaps. Exact commands: `../core/toolchains.md`. Google Apps Script (clasp) and
Cloudflare Workers (wrangler) are documented in core but excluded from the lightweight
auto-arm detector specifically — their checks need an authenticated network call, unsafe
for a credential-free Stop hook; the full `/ds-quality` bootstrap flow still covers them
via `../core/toolchains.md`.

## Requires

`jq` for the Claude Code arm (payload parsing + JSON emit). Install with `brew install jq` if missing.

## Files

- `SKILL.md` — full procedure (Phases 1–5) and contracts.
- `../core/toolchains.md` — per-stack commands + minimal bootstrap (shipped beside every skill).
- `references/hook-contract.md` — verified Claude Code Stop-hook contract + global install script.
- `references/invariant-patterns.md` — nine field-proven invariant-gate patterns for `--invariant` mode.
- `assets/ds-quality-gate.sh` — the Claude Code Stop hook (auto-arming).
- `assets/ds-quality-detect.sh` — toolchain detector → quality command (used by every arm).
- `assets/quality.sh.tmpl` — template for a per-project entry point (bootstrap).
