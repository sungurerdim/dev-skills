# /ds-fix

AI assistants skip formatting, ignore lint errors, and never run type checks. This skill runs all five quality passes in the correct order and verifies the result.

**Universal Code Quality Fix** — Format, lint, type-check, l10n, and security scan for any stack.

## Triggers

- User runs `/ds-fix`
- User asks to format code, run linters, fix lint errors, or fix code quality issues
- User asks to run type checker, check types, or fix type errors
- User asks to scan for secrets or audit dependencies

## Contract

- Runs automated fixers in safe, deterministic order: l10n → format → typecheck → lint → security
- Format always runs before lint so auto-formatting does not introduce new lint issues
- Only reports findings in `--check` mode — zero file modifications
- Missing tools skipped with a warning — never fails due to absent optional tooling
- Re-validates after fix to confirm fix worked
- Reports counts, not verbose output
- Does NOT perform manual code review, architecture analysis, or refactoring
- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.

## Arguments

| Flag | Effect |
|------|--------|
| (none) | Fix all scopes |
| `--check` | Report only, no modifications |
| `--scope=X,Y` | Specific scope(s), comma-separated |

## Scopes

| Scope | What It Does |
|-------|-------------|
| `format` | Apply code formatter |
| `lint` | Run linter with auto-fix |
| `typecheck` | Run static type checker |
| `l10n` | Generate/validate localization files |
| `security` | Secret pattern scan + dependency audit |

Default: all five scopes in order.

## Execution Flow

Detection → [L10n] → [Format] → [Typecheck] → [Lint] → [Security] → [Needs-Approval] → Summary

### Phase 1: Stack Detection

1. **IDU:** Profile → Toolchain, Type+Stack. Absent → own detection.

Detect stacks in two tiers. Multiple stacks may coexist (e.g., monorepo).

**Tier 1 — Primary stacks** (full toolchain: format + lint + typecheck + security):

| Manifest | Stack |
|----------|-------|
| `pubspec.yaml` | flutter |
| `package.json` | node |
| `pyproject.toml` / `setup.py` / `requirements.txt` | python |
| `go.mod` | go |
| `Cargo.toml` | rust |
| `build.gradle` / `build.gradle.kts` / `pom.xml` | jvm |
| `Package.swift` / `*.xcodeproj` | swift |
| `*.csproj` / `*.sln` | dotnet |
| `Gemfile` | ruby |
| `composer.json` | php |
| `mix.exs` | elixir |
| `build.sbt` | scala |

**Tier 2 — Supplementary stacks** (run only applicable tools, never sole detected stack):

| Signal | Stack | Condition to activate |
|--------|-------|----------------------|
| `CMakeLists.txt` or `Makefile` | c-cpp | **Only if** `.c`, `.cpp`, `.cc`, or `.h` source files exist in `src/` or project root. A `Makefile` without C/C++ sources is just a task runner — skip. |
| `*.sh` files | shell | **Only if** 3+ `.sh` files exist, or a `scripts/` directory with `.sh` files. A single `setup.sh` does not make this a shell project. |
| `*.tf` files | terraform | High confidence — `.tf` extension is unique to Terraform. Treat as primary if no other stack detected. |
| `Dockerfile` / `docker-compose.yml` | docker | **Always supplementary.** Run hadolint/trivy alongside primary stack, never as sole stack. |

**Disambiguation rules:**
- Only Tier 2 stacks detected (e.g., just Dockerfile + shell scripts): run security scope universally, run Tier 2 tools for their specific files only.
- Tier 1 + Tier 2 detected: run full toolchain for Tier 1, supplementary tools for Tier 2.
- Terraform exception: `*.tf` is only manifest → treat as primary (iac project).

Per stack: load matching toolchain from `references/toolchains.md`.

**Gate:** At least one stack detected or security-only mode.

### Phase 2: L10n [scope: l10n]

Stack-specific localization generation and validation.

1. Detect l10n framework from project config and dependencies
2. Generate localization files if stack supports it (e.g., `flutter gen-l10n`)
3. Cross-check translation keys: all locale files must have same keys as base locale
4. Check placeholder consistency: `{name}` in base must exist in all translations
5. Check for encoding issues (mojibake patterns from cp1252→UTF-8 double-encoding)
6. **Fix mode:** generate files, stage generated output
7. **Check mode:** report mismatches only

Example l10n frameworks per stack:

| Stack | Framework | Key files |
|-------|-----------|-----------|
| flutter | flutter_localizations / gen-l10n | `lib/l10n/*.arb` |
| node | i18next / react-intl / next-intl | `locales/*.json`, `messages/*.json` |
| python | gettext / babel | `*.po`, `babel.cfg` |
| jvm | Android resources / Spring messages | `res/values-*/strings.xml`, `messages_*.properties` |
| swift | NSLocalizedString / String Catalogs | `*.lproj/*.strings`, `*.xcstrings` |
| dotnet | resx | `Resources/*.resx` |
| ruby | rails-i18n | `config/locales/*.yml` |
| php | Laravel lang / Symfony translations | `lang/*.php`, `translations/*.yaml` |
| c-cpp | gettext | `*.po`, `*.pot` |
| elixir | Gettext | `priv/gettext/*.po` |
| scala | Play i18n / Java ResourceBundle | `conf/messages.*`, `*.properties` |

Skip silently if no l10n framework detected.

**Gate:** L10n files generated/validated or no l10n framework detected.

### Phase 3: Format [scope: format]

Per stack: run canonical formatter.

1. Look up format tool from `references/toolchains.md`
2. Tool unavailable → offer to install (see Error Recovery); declined or system-level tool → skip scope.
3. **Fix mode:** run fix command
4. **Check mode:** run check command, report exit code
5. Non-default formatter (e.g., Biome instead of Prettier for Node) → detect from config files and use that instead

**Gate:** Format clean before proceeding to lint.

### Phase 4: Typecheck [scope: typecheck]

Per stack: run static type checker if one is configured.

1. Look up typecheck tool from `references/toolchains.md`
2. Detect if type checking is configured (e.g., `tsconfig.json` for Node, type hints in Python)
3. No type checker configured → skip silently
4. Run type checker. Type checkers are read-only — they report but don't auto-fix.
5. Report error count and top issues

Example: Python project with `pyproject.toml` containing `[tool.mypy]` or `[tool.pyright]` → run configured checker. No config → skip.

**Gate:** Type checker reports zero errors or no type checker configured.

### Phase 5: Lint [scope: lint]

Per stack: run canonical linter with auto-fix.

1. Look up lint tool from `references/toolchains.md`
2. Tool unavailable → offer to install (see Error Recovery); declined or system-level tool → skip scope.
3. **Fix mode:** run fix command, then re-run check to verify
4. **Check mode:** run check command only, report issues
5. Non-default linter (e.g., Biome instead of ESLint) → detect from config and use that

Stack-specific extra checks (search file contents, not tool-dependent):

| Stack | Pattern | Location | Suggestion |
|-------|---------|----------|------------|
| flutter | `print(` | outside test files | Use structured logger (e.g., `AppLogger`) |
| node | `console.log` | in `src/` | Use structured logger |
| python | `print(` | in `src/` | Use `logging` module |
| go | `fmt.Println` | in non-main packages | Use structured logger (e.g., `slog`) |
| ruby | `puts` / `p ` | in `app/` / `lib/` | Use `Rails.logger` or structured logger |
| php | `var_dump` / `dd(` | in `src/` / `app/` | Use structured logger |
| c-cpp | `printf(` / `cout <<` | in `src/` (not main) | Use structured logger (e.g., `spdlog`) |
| elixir | `IO.inspect` / `IO.puts` | in `lib/` | Use `Logger` module |
| scala | `println` | in `src/main/` | Use structured logger (e.g., `slf4j`) |

**Gate:** Lint re-check passes after auto-fix or check-mode issues reported.

### Phase 6: Security [scope: security]

Two sub-phases: universal secret scan + stack-specific dependency audit.

**6a. Secret Scan (all stacks):**

Search project files for these patterns, excluding `.git/`, `node_modules/`, `build/`, `.dart_tool/`, `vendor/`, `__pycache__/`, `bin/`, `obj/`, `_build/`, `deps/`, `.terraform/`, `target/`:

| Pattern | Description |
|---------|-------------|
| `AKIA[0-9A-Z]{16}` | AWS access key |
| `(api_key\|api_secret\|secret_key\|access_token\|auth_token\|password)\s*[=:]\s*["'][^"']{8,}` | Generic secrets |
| `-----BEGIN.*PRIVATE KEY-----` | Private keys |
| `sk-[a-zA-Z0-9]{20,}` | OpenAI/Stripe key |
| `ghp_[a-zA-Z0-9]{36}` | GitHub PAT |
| `xox[baprs]-[a-zA-Z0-9-]+` | Slack token |

**6b. Dependency Audit (per stack):**

Look up audit command from `references/toolchains.md`. Tool not installed → skip with warning.

**Gate:** Secret scan and dependency audit completed with findings classified.

### Phase 7: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 8: Summary

Print a markdown table:

```
| Scope     | Status   | Details          |
|-----------|----------|------------------|
| L10n      | ✓/✗/⊘/⚠ | count or message |
| Format    | ✓/✗/⊘/⚠ | files fixed      |
| Typecheck | ✓/✗/⊘/⚠ | errors found     |
| Lint      | ✓/✗/⊘/⚠ | issues found     |
| Security  | ✓/✗/⊘/⚠ | findings         |
```

Legend: ✓ = pass, ✗ = issues found, ⊘ = not applicable, ⚠ = tool unavailable (skipped)

Output summary line:

```
ds-fix: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

FRC+DSC accounting.

**Gate:** Summary table rendered with status per scope and totals.

## Quality Gates

- Format runs before lint — never reverse this order
- After fix, re-run check to verify fix worked. Re-check fails → report as unresolved.
- Only report findings in `--check` mode — verify diff is empty after check run
- Secret findings are always CRITICAL — never auto-fix, always report
- Scope boundary: only run scopes user requested (or all if none specified)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Exposed secrets, known vulnerable dependencies |
| HIGH | Type errors, lint errors that affect correctness |
| MEDIUM | Format violations, lint warnings |
| LOW | Style suggestions, outdated dependencies without CVEs |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Unknown stack | Run security scope only (universal), skip others |
| Multiple stacks in monorepo | Detect all, run each stack's tools in its subdirectory |
| Tool not installed | Warn once per tool, skip, continue with next |
| Formatter and linter conflict | Formatter wins (runs first), linter adapts |
| No l10n framework detected | Skip l10n silently |
| No type checker configured | Skip typecheck silently |
| `--check` with `--scope=format` | Run format check only, exit code indicates pass/fail |
| Large repo (>10K files) | Run tools with default file filtering, don't override excludes |
| Pre-existing config (`.eslintrc`, `ruff.toml`, etc.) | Respect project config — never override with defaults |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Tool not installed (e.g., formatter, linter) | Offer to install: show install command (e.g., `pip install ruff`, `npm install -D eslint`), ask "Install and continue?" User accepts → install, re-run scope. User declines → skip scope, warn in summary. System-level tools (e.g., `go`, `rustfmt`) requiring manual install → show install instructions, skip scope. |
| Lock file conflict | Warn, skip dependency operations |
| Formatter and linter disagree | Run formatter first, then linter |
