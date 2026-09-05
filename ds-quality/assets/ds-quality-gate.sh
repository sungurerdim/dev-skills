#!/usr/bin/env bash
# ds-quality-gate — deterministic local quality Stop hook (always-active, auto-arming).
#
# Installed once at ~/.claude/hooks/ds-quality-gate.sh and registered in settings.json
# under .hooks.Stop. Behaviour per project, in priority order:
#   1. .claude/ds-quality.json marker present  -> run its `command` (enabled:false => off).
#   2. else, "auto" mode + repo under a trusted root -> auto-detect existing tools and run them.
#   3. else / nothing detectable               -> exit 0 (inert: never blocks where there's
#                                                 nothing to check, never runs untrusted repos).
#
# Contract (verified, see references/hook-contract.md):
#   stop_hook_active -> exit 0 (loop guard) | green -> exit 0 | red -> {"decision":"block",...}.
#
# Config: ~/.claude/ds-quality.config.json  { "mode": "auto"|"off", "roots": ["~/projects"] }
# Defaults (no config): mode=auto, roots=[~/projects].
# LOCAL ONLY. No network. No CI. The gate never edits your code — it blocks so the fix gets made.
#
# bash 3.2 compatible (macOS default): no mapfile, no associative arrays.
set -uo pipefail

INPUT="$(cat)"
command -v jq >/dev/null 2>&1 || exit 0

# Loop guard: already blocked once without progress -> let the agent stop.
if [ "$(printf '%s' "$INPUT" | jq -r '.stop_hook_active // false')" = "true" ]; then
  exit 0
fi

# Anchor on the session's project root, not the shell's current directory.
# Hook input `cwd` follows the agent's last `cd` (see hook-contract.md), so a session
# started in ~/projects that wandered into ~/projects/foo must NOT gate foo. Claude Code
# exports CLAUDE_PROJECT_DIR = "the project root where the session started"; prefer it.
# Exception: a worktree of the same repository (EnterWorktree) is gated where the work is.
CWD="$(printf '%s' "$INPUT" | jq -r '.cwd // "."')"
ANCHOR="${CLAUDE_PROJECT_DIR:-$CWD}"
if [ -n "${CLAUDE_PROJECT_DIR:-}" ] && [ -d "$CWD" ]; then
  cwd_common="$(cd "$CWD" 2>/dev/null && git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
  prj_common="$(cd "$CLAUDE_PROJECT_DIR" 2>/dev/null && git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
  [ -n "$cwd_common" ] && [ "$cwd_common" = "$prj_common" ] && ANCHOR="$CWD"
fi
cd "$ANCHOR" 2>/dev/null || exit 0

# Resolve the repo root so marker + detection are anchored at the project, not a subdir.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null || printf '%s' "$PWD")"

# --- load config (defaults: auto + ~/projects) -------------------------------
CONFIG="$HOME/.claude/ds-quality.config.json"
MODE="auto"
ROOTS="$HOME/projects"
if [ -f "$CONFIG" ]; then
  MODE="$(jq -r '.mode // "auto"' "$CONFIG" 2>/dev/null || echo auto)"
  R="$(jq -r '.roots[]? // empty' "$CONFIG" 2>/dev/null)"
  [ -n "$R" ] && ROOTS="$R"
fi

# --- resolve the quality command for this repo -------------------------------
CMD=""
MARKER="$ROOT/.claude/ds-quality.json"
if [ -f "$MARKER" ]; then
  [ "$(jq -r '.enabled // true' "$MARKER" 2>/dev/null)" = "true" ] || exit 0   # explicit opt-out wins
  CMD="$(jq -r '.command // empty' "$MARKER" 2>/dev/null)"
elif [ "$MODE" = "auto" ]; then
  # Only auto-arm inside a trusted root (your own code), never arbitrary dirs.
  inroot=0
  while IFS= read -r r; do
    [ -z "$r" ] && continue
    case "$r" in "~"*) r="$HOME${r#\~}";; esac
    case "$ROOT/" in "$r"/*) inroot=1; break;; esac
  done <<EOF
$ROOTS
EOF
  [ "$inroot" = "1" ] || exit 0
  CMD="$("$HOME/.claude/hooks/ds-quality-detect.sh" "$ROOT" 2>/dev/null)"
fi

[ -n "$CMD" ] || exit 0   # nothing to check -> inert

# --- run the gate ------------------------------------------------------------
OUT="$(cd "$ROOT" && eval "$CMD" 2>&1)"
STATUS=$?
[ "$STATUS" -eq 0 ] && exit 0   # green -> allow stop

TRIMMED="$(printf '%s' "$OUT" | tail -c 4000)"
REASON="$(printf 'Quality gate FAILED (exit %s) for: %s\n\n%s\n\nFix the cause — do NOT weaken or skip checks/tests — then finish.' \
  "$STATUS" "$CMD" "$TRIMMED")"
jq -n --arg reason "$REASON" '{decision:"block", reason:$reason}'
exit 0
