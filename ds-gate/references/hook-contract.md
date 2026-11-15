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

`cwd` is **not** the project directory: per the official hooks reference it is "the current
working directory when the hook is invoked" and "the new directory after Claude runs `cd`".
The project root is the environment variable `CLAUDE_PROJECT_DIR` ("the project root where
the session started"). Anchor the marker lookup and the gate command on `CLAUDE_PROJECT_DIR`;
fall back to `cwd` only when the variable is absent (manual invocation, other harnesses), and
use `cwd` when it is a worktree of the same repository. Verified 2026-09-05: a session started
in a non-repo parent directory whose shell had `cd`-ed into an unrelated clean repo ran that
repo's test suite and blocked the stop on failures the session never touched.

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
      { "hooks": [ { "type": "command", "command": "\"/usr/bin/python3\" \"/home/me/.claude/hooks/ds-gate.py\" gate", "timeout": 300 } ] }
    ]
  }
}
```

- Add to `~/.claude/settings.json` for system-wide, or `<repo>/.claude/settings.json` for repo-local.
- `timeout` is seconds (default 600). Merge with `ds-gate.py install --register`; it never clobbers existing `hooks.Stop` entries.
- Idempotency: one ds-gate entry; `install --register` replaces older ds-gate entries (incl. pre-3.0 `ds-quality-gate.sh`) and keeps all others.

## Global install (idempotent)

`python3 "{assets-dir}/ds-gate.py" install --register` (add `--dry-run` to preview): copies `ds-gate.py` to `~/.claude/hooks/` (or `$CLAUDE_CONFIG_DIR/hooks/`), removes pre-3.0 shell launchers, writes `ds-gate.config.json` only if absent, and registers the Stop hook with the absolute interpreter and script paths after backing up `settings.json`. Re-running is a no-op once current.

## Project marker schema — `.claude/ds-gate.json`

```json
{
  "enabled": true,
  "command": "make quality",
  "stack": ["node"],
  "checks": ["format", "lint", "type", "test"],
  "createdBy": "ds-gate"
}
```

`command` is the source of truth the hook runs. `checks` is informational. `enabled:false` makes the hook a no-op for this repo.

---

# Other host hook contracts (verified 2026-07-15; Copilot is served by the git pre-commit arm)

Verified against official docs on the dates noted; if behavior diverges, re-verify the live docs — don't guess.

## Codex CLI — `Stop` hook (before-done; developers.openai.com/codex/hooks)

- Config: `<repo>/.codex/hooks.json` or inline `[hooks]` in `.codex/config.toml` (one representation per layer); user-level `~/.codex/hooks.json`. **Project-local hooks load only when the project layer is trusted.**
- Shape: `hooks.Stop[] = { hooks: [ { "type":"command", "command":"…", "statusMessage":"…" } ] }` — `matcher` is not used for `Stop`.
- Stdin JSON includes `stop_hook_active` (loop guard — exit 0 when `true`) and `last_assistant_message`.
- Block: exit 0 + stdout `{"decision":"block","reason":"…"}` → Codex continues, `reason` becomes the continuation prompt. Exit 2 + stderr reason also works. **Plain-text stdout is invalid for `Stop` — JSON only.** `continue:false` from any matching Stop hook overrides block decisions.

## Gemini CLI — `AfterAgent` hook (before-done; geminicli.com/docs/hooks)

- Config: `.gemini/settings.json` (project) > `~/.gemini/settings.json` (user) > `/etc/gemini-cli/settings.json`.
- Shape: `hooks.AfterAgent[] = { matcher, hooks: [ { "name":"…", "type":"command", "command":"…", "timeout":<ms> } ] }`. Tool-event matchers are regex; `"*"` matches all.
- Exit codes: `0` = success, stdout parsed as JSON (intentional block via `{"decision":"deny"}`); `2` = critical block — the target action (tool, turn, or stop) is aborted, stderr is the rejection reason; other = warning, interaction proceeds.
- `AfterAgent` fires when the agent loop ends; impact class "Retry / Halt" — review output, force retry or halt.
- Transition note: unpaid-tier Gemini CLI is being replaced by Antigravity CLI (announced for 2026-06-18) — re-verify the config surface at install time.
