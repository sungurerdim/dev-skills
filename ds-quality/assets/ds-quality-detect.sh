#!/usr/bin/env bash
# ds-quality-detect — print the quality command for a repo dir, or nothing if none detectable.
#
# Emits ONLY checks whose tools/configs actually exist (fail-fast, joined with &&), in order
# format -> lint -> type -> test. Used by the gate (auto mode), and by /ds-quality --run / --status.
# Prints nothing when there is nothing to check -> the gate stays inert (no false blocks).
#
# bash 3.2 compatible (macOS default): no mapfile, no associative arrays.
set -uo pipefail

DIR="${1:-.}"
cd "$DIR" 2>/dev/null || exit 0

have(){ command -v "$1" >/dev/null 2>&1; }
emit(){ printf '%s' "$1"; exit 0; }

# --- 1) Explicit single entry points win (fast path) -------------------------
[ -f scripts/quality.sh ] && emit "bash scripts/quality.sh"
if [ -f Makefile ] && grep -qE '^quality:' Makefile 2>/dev/null; then emit "make quality"; fi
if [ -f package.json ] && grep -qE '"quality"[[:space:]]*:' package.json 2>/dev/null; then
  if   [ -f pnpm-lock.yaml ]; then emit "pnpm run quality"
  elif [ -f yarn.lock ];      then emit "yarn quality"
  else                              emit "npm run quality"; fi
fi

# --- 2) Stack-native detection (only tools/configs that exist) ---------------
CMDS=""
add(){ [ -n "$CMDS" ] && CMDS="$CMDS && $1" || CMDS="$1"; }

# Dart / Flutter
if [ -f pubspec.yaml ]; then
  if grep -qE '^[[:space:]]*flutter:' pubspec.yaml 2>/dev/null; then RUN=flutter; else RUN=dart; fi
  add "dart format --output=none --set-exit-if-changed ."
  add "$RUN analyze"
  { [ -d test ] || ls ./*_test.dart >/dev/null 2>&1; } && add "$RUN test"
fi

# JS / TS
if [ -f package.json ]; then
  PM=npm; [ -f pnpm-lock.yaml ] && PM=pnpm; [ -f yarn.lock ] && PM=yarn
  if ls .prettierrc* prettier.config.* >/dev/null 2>&1 || grep -q '"prettier"' package.json 2>/dev/null; then
    add "npx --no-install prettier --check ."
  fi
  if ls .eslintrc* eslint.config.* >/dev/null 2>&1 || grep -q '"eslint"' package.json 2>/dev/null; then
    add "npx --no-install eslint ."
  fi
  [ -f tsconfig.json ] && add "npx --no-install tsc --noEmit"
  if grep -qE '"test"[[:space:]]*:' package.json 2>/dev/null && ! grep -q 'no test specified' package.json 2>/dev/null; then
    case "$PM" in pnpm) add "pnpm test";; yarn) add "yarn test";; *) add "npm test";; esac
  fi
fi

# Python
if [ -f pyproject.toml ] || [ -f setup.py ] || ls requirements*.txt >/dev/null 2>&1; then
  if   have ruff;  then add "ruff format --check ."; add "ruff check ."
  elif have black; then add "black --check ."; fi
  if have mypy && { [ -f mypy.ini ] || grep -q '\[tool.mypy\]' pyproject.toml 2>/dev/null; }; then add "mypy ."; fi
  have pytest && add "pytest -q"
fi

# Go (toolchain built-in)
if [ -f go.mod ]; then
  add 'test -z "$(gofmt -l .)"'
  add "go vet ./..."
  add "go build ./..."
  add "go test ./..."
fi

# Rust (toolchain built-in)
if [ -f Cargo.toml ]; then
  add "cargo fmt --check"
  add "cargo clippy -- -D warnings"
  add "cargo test"
fi

printf '%s' "$CMDS"
