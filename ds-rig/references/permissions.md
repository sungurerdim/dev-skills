# Rules: Harness Permission Surfaces & Safe-Default Profile

Per-harness allow/ask/deny surfaces verified 2026-07-15 against official docs (sources in `docs/methodology/cross-host-program.md`). **Surfaces drift — re-verify against the harness's live docs at apply time; this file is the starting map, not the authority.** All writes: backup first, additive merge only, parse-validate after, diff must show only additions.

## Safe-default profile (harness-independent intent)

| Class | Policy | Examples |
|-------|--------|----------|
| Destructive | **deny** | recursive delete outside workspace, `git push --force`, unpinned `curl\|bash`/`npx -y`, `sudo`, disk/partition ops |
| Outward | **ask** | `git push`, package publish, network fetch to new hosts, package installs, opening PRs/issues |
| Read-only + rig tools | **allow** | file reads, `git status/log/diff`, `{rig tool} --version`, rtk-wrapped read commands, LSP queries |
| Loosening an existing deny | **never automatic** | flag as needs-user-decision |

## Per-harness surfaces (verified state, 2026-07-15)

| Harness | Surface | Mechanism | Notes |
|---------|---------|-----------|-------|
| Claude Code | `settings.json` permissions (allow/deny/ask lists) + `PreToolUse` hooks | declarative lists + blocking hooks (exit 2 / decision JSON) | merge with jq; never clobber `hooks.*` entries |
| Codex CLI | `permission_mode` + `PermissionRequest`/`PreToolUse` hooks (`~/.codex/hooks.json`) | hook decisions; project hooks need trusted project | hooks are hash-pin trusted per user |
| Gemini CLI | `settings.json` hooks — `BeforeTool` block/rewrite | exit 0+`{"decision":"deny"}` or exit 2 | Antigravity-CLI transition for unpaid tiers — re-verify surface |
| GitHub Copilot | `.github/hooks/*.json` / `~/.copilot/hooks/` — `preToolUse` returns allow/deny/ask | only blocking event; no matchers — filter in script; provide bash+powershell | `toolArgs` is a JSON string — parse |
| Kilo Code | `kilo.jsonc` `permission` key — allow/ask/deny, last-match-wins | declarative patterns | plus OS-level Kilo Sandbox write-confinement |
| OpenCode | plugin hooks + config | verify current docs at apply time (block semantics UNVERIFIED at catalog time) | reads `~/.claude/skills/` for skills |
| Cursor / Windsurf (Devin Desktop) | no scriptable deny surface confirmed | — | gap-note; compensating control: ds-quality pre-commit arm |
| Aider | none | — | gap-note; compensating control: ds-quality Aider arm (edit-time) + git hooks |

## Apply procedure (every harness)

1. Read the live permission doc for the harness; confirm the surface still matches the table.
2. Backup the target config with a timestamped copy.
3. Merge additively: new deny/ask/allow entries for the safe-default classes + this run's installed tools. Existing user entries always win on conflict — show the conflict, ask.
4. Validate: host's own config check when available, else strict JSON/TOML parse.
5. Prove: diff backup→new shows only additions; record the diff summary in the manifest.
