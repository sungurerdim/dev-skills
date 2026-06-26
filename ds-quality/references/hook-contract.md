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
