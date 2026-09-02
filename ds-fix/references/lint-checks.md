# Lint — Stack-Specific Patterns, Complexity, Spell Check

Consumer: SKILL.md Phase 4 (Lint).

## Stack-specific extra checks (content-based, not tool-dependent)

| Stack | Pattern | Where | Suggestion |
|-------|---------|-------|------------|
| flutter | `print(` | outside test files | Use structured logger (e.g., `{logger-class}`) |
| node | `console.log` | in `src/` | Use structured logger |
| python | `print(` | in `src/` | Use `logging` module |
| go | `fmt.Println` | in non-main packages | Use structured logger (e.g., `slog`) |
| ruby | `puts` / `p ` | in `app/` / `lib/` | Use `Rails.logger` or structured logger |
| php | `var_dump` / `dd(` | in `src/` / `app/` | Use structured logger |
| c-cpp | `printf(` / `cout <<` | in `src/` (not main) | Use structured logger (e.g., `spdlog`) |
| elixir | `IO.inspect` / `IO.puts` | in `lib/` | Use `Logger` module |
| scala | `println` | in `src/main/` | Use structured logger (e.g., `slf4j`) |

## Complexity thresholds (linter-owned, not hand-audited)

Enable these in the stack's linter config (tool per [`../../core/toolchains.md`](../../core/toolchains.md)) so the check is mechanical and runs on every pass. Linter offers no complexity rule → report the gap once under Tool Install Policy and move on; never substitute a manual read-through.

| Metric | Threshold |
|--------|-----------|
| Cyclomatic complexity | ≤ 15 |
| Function / method length | ≤ 50 lines |
| File length | ≤ 500 lines |
| Nesting depth | ≤ 3 |
| Parameters | ≤ 4 |

Existing config already sets a different threshold → keep the project's value, report the delta; the project's own convention wins.

## Spell check (advisory, all stacks)

`typos` binary present → run `typos` (fix mode: `typos -w`), report correction count — its known-misspellings design keeps false positives low even on large repos; absent → skip silently (optional sub-check, exempt from Tool Install Policy prompting).
