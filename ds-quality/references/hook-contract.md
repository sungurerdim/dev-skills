# Claude Code Stop hook contract (verified)

Verified against the official docs (https://code.claude.com/docs/en/hooks.md and
.../hooks-guide.md), June 2026. This skill ships its own copy so it stays self-contained — but if
behavior ever diverges, re-verify the live docs; don't guess.

## Blocking semantics (Stop hook)

| Exit code | Behavior |
|-----------|----------|
| `0` | Success. Claude parses **stdout JSON** for `decision`. `{"decision":"block","reason":"…"}` → stop is **blocked**, agent continues, `reason` is shown to it. No JSON / no `decision` → stop proceeds. |
| `2` | Blocking error (legacy). Blocks + feeds stderr back. **Prefer `exit 0` + JSON** for clarity. |
| other | Non-blocking error. stderr surfaced; stop is NOT blocked. |

**Use:** `exit 0` with `{"decision":"block","reason":"<why + what to fix>"}` to force continuation.

## Loop guard — `stop_hook_active`

- Lives in the **stdin JSON** the hook receives (not output).
- `true` once this hook has already blocked without the agent making progress.
- The hook MUST check it first and `exit 0` when `true`, so it can never infinite-loop.
- Claude also auto-caps consecutive blocks (~8) and force-allows the stop;
  `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP=<n>` overrides the cap.

## Stdin JSON shape (Stop event)

```json
{
  "session_id": "…",
  "transcript_path": "…/transcript.jsonl",
  "cwd": "/abs/project/dir",
  "permission_mode": "default",
  "hook_event_name": "Stop",
  "stop_hook_active": false
}
```

`cwd` is the project directory at stop time — use it to locate the project marker.

## Output JSON (to block)

```json
{ "decision": "block", "reason": "Quality gate failed: … Fix the cause, then finish." }
```

To allow the stop: emit nothing and `exit 0`.

## settings.json registration — Stop hooks take NO matcher

```json
{
  "hooks": {
    "Stop": [
      { "hooks": [ { "type": "command", "command": "~/.claude/hooks/ds-quality-gate.sh", "timeout": 300 } ] }
    ]
  }
}
```

- Add to `~/.claude/settings.json` for system-wide, or `<repo>/.claude/settings.json` for repo-local.
- `timeout` is seconds (default 600). Merge with `jq`; never clobber existing `hooks.Stop` entries.
- Idempotency: only append if no existing entry's `command` already equals the script path.

## Global install script (idempotent)

Copy both scripts, write the default config, and register the hook once, without clobbering existing hooks:

```bash
mkdir -p ~/.claude/hooks
cp ~/.claude/skills/ds-quality/assets/ds-quality-gate.sh   ~/.claude/hooks/ds-quality-gate.sh
cp ~/.claude/skills/ds-quality/assets/ds-quality-detect.sh ~/.claude/hooks/ds-quality-detect.sh
chmod +x ~/.claude/hooks/ds-quality-gate.sh ~/.claude/hooks/ds-quality-detect.sh

# default auto config (only if absent — never overwrite the user's roots)
CFG="$HOME/.claude/ds-quality.config.json"
[ -f "$CFG" ] || printf '{\n  "mode": "auto",\n  "roots": ["~/projects"]\n}\n' > "$CFG"

HOOK="$HOME/.claude/hooks/ds-quality-gate.sh"; S="$HOME/.claude/settings.json"
[ -f "$S" ] || echo '{}' > "$S"
cp "$S" "$S.bak.$(date +%Y%m%d%H%M%S)"
tmp=$(mktemp)
jq --arg cmd "$HOOK" '
  .hooks //= {} | .hooks.Stop //= [] |
  if any(.hooks.Stop[]?; ((.hooks // [])[]?.command) == $cmd)
  then .
  else .hooks.Stop += [{hooks:[{type:"command", command:$cmd, timeout:300}]}] end
' "$S" > "$tmp" && mv "$tmp" "$S"
jq -e . "$S" >/dev/null   # validate
```

Re-running is a no-op when the entry already exists (only refreshes scripts). `jq` is required; if absent, stop and tell the user to install it (`brew install jq`). The scripts are **bash 3.2 compatible** (macOS default).

## `--project-hook` registration (repo-local, idempotent)

Same `jq` merge, but against `<repo>/.claude/settings.json`, with the command pointing at the
copied-in script (`.claude/hooks/ds-quality-gate.sh` inside the repo) so it travels with the repo.

## Project marker schema — `.claude/ds-quality.json`

```json
{
  "enabled": true,
  "command": "make quality",
  "stack": ["node"],
  "checks": ["format", "lint", "type", "test"],
  "createdBy": "ds-quality"
}
```

`command` is the source of truth the hook runs. `checks` is informational. `enabled:false` makes the hook a no-op for this repo.
