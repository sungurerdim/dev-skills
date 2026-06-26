# Toolchains — exact quality commands + minimal bootstrap

For each detected stack: the **check-mode** commands wired into the single entry point, and the
minimal standard config to create ONLY if missing. Prefer tools already in the lockfile. All
commands are fail-fast and exit non-zero on problems. Never invent a check whose tool isn't present.

> Detection precedence when multiple manifests exist: run the gate for each present stack
> (monorepo / polyglot), each as its own ordered block. Skip a check whose tool is absent and
> note the gap; don't fail the gate for a missing optional type-checker.

---

## JS / TS (node)
**Detect:** `package.json` (+ lockfile: `package-lock.json` → npm, `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn). Use the matching runner.

| Check | Command (npm shown) | Present when |
|-------|---------------------|--------------|
| format | `npx prettier --check .` | `prettier` in deps OR a `.prettierrc*`/`prettier.config.*` |
| lint | `npx eslint .` | `eslint` in deps OR an eslint config |
| type | `npx tsc --noEmit` | `tsconfig.json` present |
| test | `npm test` | `scripts.test` exists AND isn't the `"Error: no test specified"` placeholder |

**Bootstrap if missing (only configs, prefer existing deps):**
- No formatter but you add one → `prettier` (devDep) + empty `.prettierrc.json` `{}`.
- No linter → `eslint` flat config `eslint.config.js` with `@eslint/js` recommended. Don't over-configure.
- No tests → create one real test with the project's runner (vitest/jest if present; else add `vitest` as devDep) asserting a core module's actual behavior + boundary cases. Mark coverage thin.

---

## Dart / Flutter
**Detect:** `pubspec.yaml`. If it contains `flutter:` → Flutter; else plain Dart.

| Check | Flutter | Dart |
|-------|---------|------|
| format | `dart format --output=none --set-exit-if-changed .` | same |
| lint+type | `flutter analyze` | `dart analyze` |
| test | `flutter test` | `dart test` |

> Dart is statically typed; `analyze` is both the type-check and the linter — no separate type step.

**Bootstrap if missing:** create `analysis_options.yaml`:
```yaml
include: package:flutter_lints/flutter.yaml   # Flutter
# include: package:lints/recommended.yaml     # plain Dart
```
Add `flutter_lints` (or `lints`) to `dev_dependencies` if not present. No tests → create a real `test/` smoke + boundary test (`expect` on actual behavior).

---

## Python
**Detect:** `pyproject.toml` / `requirements*.txt` / `setup.py`.

| Check | Command | Notes |
|-------|---------|-------|
| format | `ruff format --check .` | or `black --check .` if black is the configured formatter |
| lint | `ruff check .` | or `flake8` if that's what's configured |
| type | `mypy .` or `pyright` | ONLY if already configured/typed — see below |
| test | `pytest -q` | or `python -m unittest` if that's the suite |

**Bootstrap if missing:** prefer **ruff** (one tool = format + lint). Add minimal `[tool.ruff]` to `pyproject.toml` only if no formatter/linter exists. **Do not force a type-checker onto an untyped project** — if mypy/pyright isn't configured, mark "type-check: not configured (gap)" rather than adding heavy typing. No tests → create a real `tests/test_*.py` with pytest asserting a core function + boundary cases.

---

## Go
**Detect:** `go.mod`. Toolchain is built-in — no config to bootstrap.

| Check | Command |
|-------|---------|
| format | `test -z "$(gofmt -l .)"` (fails if any file is unformatted; prints the offending files) |
| vet/lint | `go vet ./...` |
| type/build | `go build ./...` |
| test | `go test ./...` |

Optional, only if present: `staticcheck ./...`. No tests → create a real `_test.go` with table-driven cases incl. boundaries.

---

## Rust
**Detect:** `Cargo.toml`. Toolchain built-in.

| Check | Command |
|-------|---------|
| format | `cargo fmt --check` |
| lint | `cargo clippy -- -D warnings` |
| type/build | `cargo check` |
| test | `cargo test` |

No tests → add a real `#[test]` (or `tests/`) asserting actual behavior + boundaries.

---

## Makefile-driven
**Detect:** `Makefile` with relevant targets. If targets like `fmt`/`lint`/`test` exist, the entry
point's `quality:` target chains them fail-fast (`set -e` semantics / `&&`). Reuse existing targets;
don't duplicate their logic.

---

## Generic / unknown stack
None of the above manifests present. You cannot fabricate a test suite for an unknown language.
1. Wire any **universally available** checks that apply to files actually present and whose tools
   exist: `shellcheck` for `*.sh`, `prettier --check` for `*.json/*.md/*.yaml` if prettier is
   installed, etc.
2. **Report the gap explicitly** ("no recognized language toolchain; established only <X>; tests
   not established — human decision needed") and ask the user which toolchain to standardize on.
3. Do NOT mark the task green with an empty gate. An empty quality command that always passes is a
   false signal — flag it.
