# ds-quality

Deterministic, **local-only** (no CI) quality enforcement for any repo. Installs a single quality
entry point (format → lint → type → test) and a Claude Code **Stop hook** that blocks "done" until
that entry point passes green. Quality becomes a mechanism, not a hope.

## How it works

**One always-active global gate, installed once. No per-project hook or marker needed.**

- `~/.claude/hooks/ds-quality-gate.sh` registered in `~/.claude/settings.json` `.hooks.Stop`.
- On Stop it resolves a command in priority: **marker** (`.claude/ds-quality.json`, `enabled:false` =
  per-repo off) → **auto-arm** (no marker, repo under a trusted root: `ds-quality-detect.sh` runs the
  tools that already exist) → **inert** (nothing to check / outside roots → no-op).
- Green → allow; red → block with the failing output, forcing the agent to fix it. The gate never
  edits your code. Loop-guarded (`stop_hook_active`) so it can't spin.
- Config `~/.claude/ds-quality.config.json`: `{ "mode":"auto"|"off", "roots":["~/projects"] }`.

Mature repos (already have format/lint/test) are enforced **with zero per-repo steps**. You only run
`/ds-quality` in a repo to **bootstrap missing tooling** — it won't silently scatter configs/tests
everywhere. Prefer a repo-local hook over the global one? `--project-hook`.

## Usage

```
/ds-quality --install      # one-time: install gate+detector, register hook, auto config (do this once)
/ds-quality                # bootstrap THIS repo's missing tooling so auto-arm has something to enforce
/ds-quality --run          # run this repo's resolved quality command now
/ds-quality --status       # show mode/roots + what auto-arm resolves here + global state
/ds-quality --disable      # per-repo kill switch (.claude/ds-quality.json enabled:false)
/ds-quality --project-hook # register the hook in THIS repo's .claude/settings.json
/ds-quality --uninstall    # remove the global hook + scripts + config
```

## Supported stacks

JS/TS (node), Dart/Flutter, Python, Go, Rust, Makefile-driven, plus a generic fallback that wires
universally-available checks and flags coverage gaps. Exact commands: `references/toolchains.md`.

## Requires

`jq` (payload parsing + JSON emit). Install with `brew install jq` if missing.

## Files

- `SKILL.md` — full procedure (Phases 1–5) and contracts.
- `references/toolchains.md` — per-stack commands + minimal bootstrap.
- `references/hook-contract.md` — verified Claude Code Stop-hook contract.
- `assets/ds-quality-gate.sh` — the global Stop hook (auto-arming).
- `assets/ds-quality-detect.sh` — toolchain detector → quality command (used by auto-arm, `--run`, `--status`).
- `assets/quality.sh.tmpl` — template for a per-project entry point (bootstrap).
