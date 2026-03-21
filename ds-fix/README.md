# ds-fix

Stack-agnostic code quality fixer — format, lint, type-check, l10n, and security scan.

## Install

See the [main README](../README.md#install) for install instructions per AI tool.

## Use

Run `/ds-fix`, or ask to fix code quality issues.

## Scopes

| Scope | What It Does |
|-------|-------------|
| `format` | Apply code formatter (Prettier, Ruff, gofmt, cargo fmt, etc.) |
| `lint` | Run linter with auto-fix (ESLint, Ruff, clippy, RuboCop, etc.) |
| `typecheck` | Run static type checker (tsc, Pyright, mypy, go build, etc.) |
| `l10n` | Generate/validate localization files |
| `security` | Secret pattern scan + dependency audit |

## Supported Stacks

Flutter, Node.js/TypeScript, Python, Go, Rust, JVM (Kotlin/Java), Swift, C#/.NET, Ruby, PHP, C/C++, Shell/Bash, Terraform/HCL, Elixir, Scala, Docker.

Auto-detected from project manifests. Multiple stacks supported in monorepos. React, Vue, Angular, Svelte, and other Node-based frameworks are covered under the Node.js/TypeScript stack.

## Features

- **Deterministic order** — l10n → format → typecheck → lint → security (format before lint prevents conflicts)
- **16 stacks** — auto-detects from manifest files, with per-stack toolchain lookup
- **Smart detection** — uses project config to pick the right tool variant (e.g., Biome vs Prettier)
- **Check mode** — `--check` for CI/report-only, no file modifications
- **Graceful degradation** — missing tools skipped with warning, never fails
