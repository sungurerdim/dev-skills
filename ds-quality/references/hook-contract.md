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

Resolve `{assets-dir}` to the `assets/` directory beside this SKILL.md (the installed skill's own copy); a host that exposes a `${CLAUDE_SKILL_DIR}`-style variable may use it to build that path as an optional convenience, never as the only way to find it.

```bash
mkdir -p ~/.claude/hooks
cp "{assets-dir}/ds-quality-gate.sh"   ~/.claude/hooks/ds-quality-gate.sh
cp "{assets-dir}/ds-quality-detect.sh" ~/.claude/hooks/ds-quality-detect.sh
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

---

# Other host hook contracts (verified 2026-07-15)

Verified against official docs on the dates noted; if behavior diverges, re-verify the live docs — don't guess.

## Codex CLI — `Stop` hook (stop-time; developers.openai.com/codex/hooks)

- Config: `<repo>/.codex/hooks.json` or inline `[hooks]` in `.codex/config.toml` (one representation per layer); user-level `~/.codex/hooks.json`. **Project-local hooks load only when the project layer is trusted.**
- Shape: `hooks.Stop[] = { hooks: [ { "type":"command", "command":"…", "statusMessage":"…" } ] }` — `matcher` is not used for `Stop`.
- Stdin JSON includes `stop_hook_active` (loop guard — exit 0 when `true`) and `last_assistant_message`.
- Block: exit 0 + stdout `{"decision":"block","reason":"…"}` → Codex continues, `reason` becomes the continuation prompt. Exit 2 + stderr reason also works. **Plain-text stdout is invalid for `Stop` — JSON only.** `continue:false` from any matching Stop hook overrides block decisions.

## Gemini CLI — `AfterAgent` hook (stop-time; geminicli.com/docs/hooks)

- Config: `.gemini/settings.json` (project) > `~/.gemini/settings.json` (user) > `/etc/gemini-cli/settings.json`.
- Shape: `hooks.AfterAgent[] = { matcher, hooks: [ { "name":"…", "type":"command", "command":"…", "timeout":<ms> } ] }`. Tool-event matchers are regex; `"*"` matches all.
- Exit codes: `0` = success, stdout parsed as JSON (intentional block via `{"decision":"deny"}`); `2` = critical block — the target action (tool, turn, or stop) is aborted, stderr is the rejection reason; other = warning, interaction proceeds.
- `AfterAgent` fires when the agent loop ends; impact class "Retry / Halt" — review output, force retry or halt.
- Transition note: unpaid-tier Gemini CLI is being replaced by Antigravity CLI (announced for 2026-06-18) — re-verify the config surface at install time.

## GitHub Copilot — hooks (commit-time enforcement; docs.github.com/copilot: use-hooks + hooks-configuration)

- Config: `.github/hooks/*.json` (repo; default branch required for cloud agent, cwd for CLI) or `~/.copilot/hooks/*.json` (user; `$COPILOT_HOME/hooks/` if set). Loaded at CLI start.
- Shape: `{ "version": 1, "hooks": { "<event>": [ { "type":"command", "bash":"…", "powershell":"…", "cwd":"…", "env":{…}, "timeoutSec":N } ] } }` — supply **both** `bash` and `powershell` for cross-OS.
- Events: `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `agentStop`, `subagentStop`, `errorOccurred`.
- **Only `preToolUse` blocks** — it returns a decision `allow` / `deny` / `ask`. For other events non-zero exits are logged and execution continues (`agentStop` is report-only). For `preToolUse`, crashes and non-zero exits fail-closed (deny); timeouts fail-open.
- **No matchers** — the script filters by inspecting `toolName` / `toolArgs` from stdin JSON; `toolArgs` is a JSON **string**, parse it (jq). `disableAllHooks` pauses all hooks without deleting config.
