#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Single quality entry point for dev-skills — the local gate, no CI.
# Fail-fast, in order. Exits non-zero on the first failure.
#
#   bash scripts/quality.sh                 run every check
#   bash scripts/quality.sh --install-hook  also run automatically on `git commit`
#   bash scripts/quality.sh --remove-hook   uninstall that hook
#
# This repo is markdown + two shell scripts + one python asset, so there is no
# formatter/linter/type-checker to run. What it does have is a set of consistency
# and verifier checks that must actually fire — those are the gate.
#
# The hook is not bypassed. A red gate is fixed first, then the commit goes in —
# `--no-verify` is not an option here (ds-commit/references/principles.md rule 4).
# A check you would want to skip is a check to fix or delete, not to work around.

set -uo pipefail
cd "$(dirname "$0")/.." || { echo "Cannot reach the repo root from $0 — refusing to run checks against the wrong tree." >&2; exit 2; }

HOOK=".git/hooks/pre-commit"
MARK="# dev-skills quality gate"

install_hook() {
  [ -d .git ] || { echo "Not a git working tree — nothing to install into." >&2; exit 2; }
  mkdir -p .git/hooks
  if [ -f "$HOOK" ] && ! grep -q "$MARK" "$HOOK"; then
    echo "A pre-commit hook already exists and is not ours: $HOOK" >&2
    echo "Inspect it, then either merge in 'bash scripts/quality.sh' or move it aside." >&2
    exit 2
  fi
  cat > "$HOOK" <<'HOOKEOF'
#!/usr/bin/env sh
# dev-skills quality gate — installed by scripts/quality.sh --install-hook
exec bash "$(git rev-parse --show-toplevel)/scripts/quality.sh"
HOOKEOF
  chmod +x "$HOOK"
  echo "Installed $HOOK — every commit now runs the gate first."
  echo "A failing check now blocks the commit: fix what it names, then commit again."
}

remove_hook() {
  if [ -f "$HOOK" ] && grep -q "$MARK" "$HOOK"; then
    rm -f "$HOOK"; echo "Removed $HOOK."
  else
    echo "No dev-skills hook installed at $HOOK — nothing to remove."
  fi
}

case "${1:-}" in
  --install-hook) install_hook; echo; ;;
  --remove-hook)  remove_hook;  exit 0 ;;
  "") ;;
  -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
  *) echo "Unknown flag: $1 (see --help)" >&2; exit 2 ;;
esac

step() {
  # step "<name>" "<shell command>"
  local name="$1"; shift
  local cmd="$1"
  printf '\n=== [quality] %s ===\n' "$name"
  if eval "$cmd"; then
    printf '[quality] %s: OK\n' "$name"
  else
    local code=$?
    printf '[quality] %s: FAILED (exit %s)\n' "$name" "$code" >&2
    exit "$code"
  fi
}

# --- checks -------------------------------------------------------------------

step "consistency"           "bash scripts/check-consistency.sh"
step "consistency self-test" "bash scripts/check-consistency.sh --self-test"

# The brief verifier is python3; its absence is a Verification-Infrastructure Gap,
# never a silent skip — an unrun check must not read as a passing one.
if command -v python3 >/dev/null 2>&1; then
  step "ds-brief verifier syntax"    "python3 -m py_compile ds-brief/assets/verify-brief.py && rm -rf ds-brief/assets/__pycache__"
  step "ds-brief verifier self-test" "python3 ds-brief/assets/verify-brief.py --self-test"
else
  printf '\n=== [quality] ds-brief verifier ===\n' >&2
  printf '[quality] FAILED: python3 not found.\n' >&2
  printf '[quality] Unverified as a result: the ds-brief mechanical verifier (44 checks)\n' >&2
  printf '[quality] and its self-test. Install python3, or run this gate on a host that has it.\n' >&2
  exit 127
fi

# The repo's own executable code gets the same treatment as its markdown: checked,
# or loudly unchecked. shellcheck is the only linter that applies here.
if command -v shellcheck >/dev/null 2>&1; then
  step "shellcheck" "shellcheck -S warning install.sh scripts/*.sh"
else
  printf '\n=== [quality] shellcheck ===\n' >&2
  printf '[quality] FAILED: shellcheck not found.\n' >&2
  printf '[quality] Unverified as a result: install.sh and scripts/*.sh — the only code in\n' >&2
  printf '[quality] this repo that writes to and deletes from your home directory.\n' >&2
  printf '[quality] Install it (brew install shellcheck / apt install shellcheck) and re-run.\n' >&2
  exit 127
fi

# Spell-check gates real errors now that _typos.toml holds the domain vocabulary
# (pre-allowlist it produced ~90 false hits; with it, a hit is a real typo).
if command -v typos >/dev/null 2>&1; then
  step "typos" "typos"
else
  printf '\n=== [quality] typos ===\n' >&2
  printf '[quality] FAILED: typos not found.\n' >&2
  printf '[quality] Unverified as a result: spelling across every SKILL.md, reference,\n' >&2
  printf '[quality] and doc. Install it (brew install typos-cli / cargo install typos-cli)\n' >&2
  printf '[quality] and re-run.\n' >&2
  exit 127
fi

# install.sh moves files into and out of the user's home; the round-trip test is
# the only proof that its --delete and rm -rf stay scoped to dev-skills content.
step "install.sh round-trip" "bash scripts/test-install.sh"

printf '\n[quality] all checks passed\n'
