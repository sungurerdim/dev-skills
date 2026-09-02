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
  if have golangci-lint && { [ -f .golangci.yml ] || [ -f .golangci.yaml ] || [ -f .golangci.toml ] || [ -f .golangci.json ]; }; then
    add "golangci-lint run"
  fi
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

# JVM (Kotlin/Java) via Gradle wrapper (Maven skipped: no cheap, reliable plugin-presence signal)
if [ -f gradlew ] && { [ -f build.gradle ] || [ -f build.gradle.kts ]; }; then
  grep -q spotless build.gradle* 2>/dev/null && add "./gradlew spotlessCheck"
  { [ -f detekt.yml ] || [ -f config/detekt/detekt.yml ]; } && add "./gradlew detekt"
  add "./gradlew test"
fi

# Swift
if [ -f Package.swift ] && have swift; then
  have swiftformat && add "swiftformat --lint ."
  have swiftlint && add "swiftlint"
  add "swift build"
  add "swift test"
fi

# C# / .NET
if { ls ./*.sln >/dev/null 2>&1 || ls ./*.csproj >/dev/null 2>&1; } && have dotnet; then
  add "dotnet format --verify-no-changes"
  add "dotnet build --no-restore"
  add "dotnet test"
fi

# Ruby
if [ -f Gemfile ]; then
  have rubocop && add "rubocop"
  grep -q rspec Gemfile 2>/dev/null && have bundle && add "bundle exec rspec"
fi

# PHP (vendor/bin binaries only — never invents a check whose tool wasn't installed)
if [ -f composer.json ]; then
  [ -x vendor/bin/pint ] && add "./vendor/bin/pint --test"
  [ -x vendor/bin/phpstan ] && add "./vendor/bin/phpstan analyze"
  [ -x vendor/bin/phpunit ] && add "./vendor/bin/phpunit"
fi

# Elixir (dialyzer skipped: first run builds the PLT, minutes-long — unfit for a per-Stop hook)
if [ -f mix.exs ] && have mix; then
  add "mix format --check-formatted"
  grep -q credo mix.exs 2>/dev/null && add "mix credo --strict"
  add "mix test"
fi

# Scala
if [ -f build.sbt ] && have sbt; then
  have scalafmt && [ -f .scalafmt.conf ] && add "scalafmt --check ."
  add "sbt compile test"
fi

# C/C++ — static analysis only. Format/build are skipped here: matching the source-file glob
# safely in POSIX sh needs find+xargs (fragile with zero matches on some xargs builds), and
# `cmake --build` needs a pre-configured out-of-source build/ dir this detector cannot safely
# assume or create inside a Stop hook.
if have cppcheck && [ -d src ] && { ls src/*.c src/*.cpp src/*.cc >/dev/null 2>&1; }; then
  add "cppcheck --enable=warning,performance --error-exitcode=1 src/"
fi

# Terraform / HCL — fmt only. validate/tflint/trivy need `terraform init`, a network
# provider-plugin download, unsuitable for a credential-free, offline auto-gate.
if ls ./*.tf >/dev/null 2>&1 && have terraform; then
  add "terraform fmt -check -recursive ."
fi

# Shell / Bash
if have shellcheck; then
  SH_TARGETS=""
  ls ./*.sh >/dev/null 2>&1 && SH_TARGETS="$SH_TARGETS ./*.sh"
  ls scripts/*.sh >/dev/null 2>&1 && SH_TARGETS="$SH_TARGETS scripts/*.sh"
  SH_TARGETS="${SH_TARGETS# }"
  [ -n "$SH_TARGETS" ] && add "shellcheck -S warning $SH_TARGETS"
fi

# Docker — lint only, no format/type/test step exists for a Dockerfile
[ -f Dockerfile ] && have hadolint && add "hadolint Dockerfile"

# Vanilla JS — no bundler, no package.json (node:test, Node >= 20)
if [ ! -f package.json ] && have node && { [ -d test ] || ls ./*.test.js >/dev/null 2>&1; }; then
  add "node --test"
fi

# Not added, by design (core/toolchains.md sections with no safe zero-config auto-detect path):
#   Google Apps Script (clasp) / Cloudflare Workers (wrangler) — their checks
#   (`clasp show-file-status`, `wrangler deploy --dry-run`) need an authenticated,
#   networked call; a credential-free Stop hook must never attempt one.
#   Generic/unknown stack's ad-hoc prettier/py_compile sweep — no manifest to key off of;
#   left to the explicit `/ds-quality` bootstrap flow, not the silent auto-arm.

printf '%s' "$CMDS"
