# Toolchains Reference

Per-stack toolchain lookup for ds-fix. Load only the section matching the detected stack.

---

## Flutter / Dart

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | dart format | `dart format .` | `dart format --set-exit-if-changed --output=none .` |
| Lint | dart fix + dart analyze | `dart fix --apply` | `dart analyze --no-fatal-infos` |
| Typecheck | dart analyze | (included in lint) | (included in lint) |
| Dep Audit | pub outdated | `dart pub outdated` | `dart pub outdated` |

**Manifest:** `pubspec.yaml`
**Config:** `analysis_options.yaml`

---

## Node.js / TypeScript

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format (default) | Prettier | `npx prettier --write .` | `npx prettier --check .` |
| Format (alt) | Biome | `npx biome format --write .` | `npx biome format .` |
| Lint (default) | ESLint | `npx eslint --fix .` | `npx eslint .` |
| Lint (alt) | Biome | `npx biome lint --write .` | `npx biome lint .` |
| Lint+Format (unified) | Biome | `npx biome check --write .` | `npx biome check .` |
| Typecheck | TypeScript | N/A (read-only) | `npx tsc --noEmit` |
| Dep Audit | npm audit | `npm audit fix` | `npm audit --audit-level=moderate` |

**Manifest:** `package.json`
**Detection:** `biome.json` → use Biome. `.eslintrc*` / `eslint.config.*` → use ESLint. `.prettierrc*` → use Prettier. `tsconfig.json` → enable typecheck.
**Package managers:** Detect from lockfile: `pnpm-lock.yaml` → pnpm, `yarn.lock` → yarn, `package-lock.json` → npm, `bun.lockb` → bun. Use detected manager for audit (e.g., `pnpm audit`, `yarn audit`).

---

## Python

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format (default) | Ruff | `ruff format .` | `ruff format --check .` |
| Format (alt) | Black | `black .` | `black --check .` |
| Lint (default) | Ruff | `ruff check --fix .` | `ruff check .` |
| Lint (alt) | Flake8 | N/A | `flake8 .` |
| Typecheck (default) | Pyright | N/A (read-only) | `pyright` |
| Typecheck (alt) | mypy | N/A (read-only) | `mypy .` |
| Dep Audit (default) | pip-audit | N/A | `pip-audit` |
| Dep Audit (alt) | safety | N/A | `safety check` |

**Manifest:** `pyproject.toml`, `setup.py`, `requirements.txt`
**Detection:** `[tool.ruff]` in pyproject.toml → Ruff. `[tool.black]` → Black. `[tool.mypy]` → mypy. `[tool.pyright]` or `pyrightconfig.json` → Pyright. No type config → skip typecheck.

---

## Go

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | gofmt | `gofmt -w .` | `gofmt -l .` (non-empty = fail) |
| Format (imports) | goimports | `goimports -w .` | `goimports -l .` |
| Lint | golangci-lint | `golangci-lint run --fix` | `golangci-lint run` |
| Vet | go vet | N/A (read-only) | `go vet ./...` |
| Typecheck | go build | N/A | `go build ./...` (compiler is the type checker) |
| Dep Audit | govulncheck | N/A | `govulncheck ./...` |

**Manifest:** `go.mod`
**Detection:** `.golangci.yml` / `.golangci.yaml` → golangci-lint config. `goimports` available → prefer over `gofmt`.
**Note:** `go vet` runs as part of lint phase alongside golangci-lint.

---

## Rust

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | cargo fmt | `cargo fmt` | `cargo fmt -- --check` |
| Lint | cargo clippy | `cargo clippy --fix --allow-dirty` | `cargo clippy -- -D warnings` |
| Typecheck | cargo check | N/A | `cargo check` |
| Dep Audit | cargo audit | N/A | `cargo audit` |
| Dep Policy | cargo deny | N/A | `cargo deny check` |

**Manifest:** `Cargo.toml`
**Config:** `rustfmt.toml`, `clippy.toml`, `deny.toml`

---

## JVM (Kotlin / Java)

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format (Gradle) | Spotless | `./gradlew spotlessApply` | `./gradlew spotlessCheck` |
| Lint (Kotlin) | detekt | `./gradlew detekt` | `./gradlew detekt` |
| Lint (Java) | Checkstyle | N/A (report-only) | `./gradlew checkstyleMain` |
| Lint (Java alt) | PMD | N/A (report-only) | `./gradlew pmdMain` |
| Format (Maven) | Spotless | `mvn spotless:apply` | `mvn spotless:check` |
| Dep Audit | OWASP Dep-Check | N/A | `./gradlew dependencyCheckAnalyze` or `mvn verify -P owasp` |

**Manifest:** `build.gradle`, `build.gradle.kts`, `pom.xml`
**Detection:** `build.gradle*` → Gradle. `pom.xml` → Maven. `detekt.yml` → detekt configured. Spotless in build config → Spotless available.
**Note:** On Windows, use `gradlew.bat` instead of `./gradlew`.

---

## Swift / iOS

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | SwiftFormat | `swiftformat .` | `swiftformat --lint .` |
| Lint | SwiftLint | `swiftlint --fix` | `swiftlint` |
| Typecheck | Swift compiler | N/A | `swift build` |
| Dep Audit | (manual) | N/A | N/A |

**Manifest:** `Package.swift`, `Podfile`, `*.xcodeproj`
**Config:** `.swiftformat`, `.swiftlint.yml`

---

## C# / .NET

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | dotnet format | `dotnet format` | `dotnet format --verify-no-changes` |
| Lint | .NET Analyzers | (built into build) | `dotnet build -warnaserror` |
| Typecheck | C# compiler | N/A | `dotnet build --no-restore` |
| Dep Audit | dotnet list | N/A | `dotnet list package --vulnerable` |

**Manifest:** `*.csproj`, `*.sln`
**Config:** `.editorconfig`, `Directory.Build.props`

---

## Ruby

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format/Lint | RuboCop | `rubocop -a` (safe) / `rubocop -A` (aggressive) | `rubocop` |
| Typecheck (default) | Sorbet | N/A (read-only) | `srb tc` |
| Typecheck (alt) | Steep | N/A (read-only) | `steep check` |
| Dep Audit | bundler-audit | N/A | `bundle-audit check --update` |

**Manifest:** `Gemfile`
**Config:** `.rubocop.yml`
**Detection:** `sorbet/config` → Sorbet. `Steepfile` → Steep. No type config → skip typecheck.
**Note:** Use `rubocop -a` (safe auto-correct) by default. Only use `-A` if user explicitly requests aggressive fixes.

---

## PHP

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format (default) | Pint | `./vendor/bin/pint` | `./vendor/bin/pint --test` |
| Format (alt) | PHP-CS-Fixer | `./vendor/bin/php-cs-fixer fix` | `./vendor/bin/php-cs-fixer fix --dry-run` |
| Lint (default) | PHPStan | N/A (read-only) | `./vendor/bin/phpstan analyze` |
| Lint (alt) | Psalm | `./vendor/bin/psalm --alter` | `./vendor/bin/psalm` |
| Dep Audit | Composer | N/A | `composer audit` |

**Manifest:** `composer.json`
**Config:** `pint.json`, `.php-cs-fixer.php`, `phpstan.neon`, `psalm.xml`
**Detection:** `pint.json` → Pint. `.php-cs-fixer.php` → PHP-CS-Fixer. `phpstan.neon` → PHPStan. `psalm.xml` → Psalm.

---

## C / C++

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | clang-format | `find src -name '*.cpp' -o -name '*.c' -o -name '*.h' \| xargs clang-format -i` | `find src -name '*.cpp' -o -name '*.c' -o -name '*.h' \| xargs clang-format --dry-run -Werror` |
| Lint | clang-tidy | `clang-tidy src/*.cpp --fix -- -I./include` | `clang-tidy src/*.cpp -- -I./include` |
| Static Analysis | cppcheck | N/A (read-only) | `cppcheck --enable=all --error-exitcode=1 src/` |
| Typecheck | compiler | N/A | `cmake --build build` or `make` (compiler is the type checker) |
| Dep Audit | conan audit | N/A | `conan audit scan .` |

**Manifest:** `CMakeLists.txt`, `Makefile` (with `.c`/`.cpp` source files)
**Config:** `.clang-format`, `.clang-tidy`
**Detection:** `.clang-format` → clang-format configured. `.clang-tidy` → clang-tidy configured. `conanfile.py` / `conanfile.txt` → Conan available. `compile_commands.json` → use with clang-tidy for accurate analysis.
**Note:** Prefer `compile_commands.json` for clang-tidy (generated by CMake with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`).

---

## Shell / Bash

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | shfmt | `shfmt -w .` | `shfmt -d .` (diff = fail) |
| Lint | shellcheck | N/A (read-only) | `shellcheck -x *.sh scripts/*.sh` |

**Manifest:** Detected by presence of `*.sh` files in project root or `scripts/` directory.
**Config:** `.editorconfig` (for shfmt indent style), `.shellcheckrc` (for shellcheck directives)
**Detection:** `shfmt` and `shellcheck` are separate installs. Skip silently if not available.
**Note:** `shellcheck -x` follows `source` directives. Use `-e SC1090` to suppress "can't follow non-constant source" if needed.

---

## Terraform / HCL

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | terraform fmt | `terraform fmt -recursive .` | `terraform fmt -check -recursive .` |
| Validate | terraform validate | N/A (read-only) | `terraform validate` |
| Lint | tflint | `tflint --fix` | `tflint --init && tflint` |
| Security | trivy | N/A (read-only) | `trivy config .` |

**Manifest:** `*.tf` files, `*.tfvars`
**Config:** `.tflint.hcl`, `.trivy.yaml`
**Detection:** `terraform` CLI required for fmt/validate. `tflint` separate install. `trivy` separate install (replaces deprecated `tfsec`).
**Note:** Run `terraform init` before `terraform validate` if providers not yet initialized. Trivy replaces tfsec for IaC scanning (tfsec is deprecated, merged into Trivy).

---

## Elixir

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | mix format | `mix format` | `mix format --check-formatted` |
| Lint | credo | N/A (read-only) | `mix credo --strict` |
| Typecheck | dialyzer (via dialyxir) | N/A (read-only) | `mix dialyzer` |
| Dep Audit | mix_audit | N/A | `mix deps.audit` |

**Manifest:** `mix.exs`
**Config:** `.formatter.exs`, `.credo.exs`
**Detection:** `{:credo, ...}` in mix.exs deps → credo available. `{:dialyxir, ...}` → dialyzer available. `{:mix_audit, ...}` → deps.audit available.
**Note:** First `mix dialyzer` run builds PLT (Persistent Lookup Table) which can take several minutes. Subsequent runs are fast.

---

## Scala

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Format | scalafmt | `scalafmt .` | `scalafmt --check .` |
| Lint | scalafix | `sbt scalafixAll` | `sbt "scalafixAll --check"` |
| Lint (alt) | WartRemover | N/A (compile-time warnings) | `sbt compile` (warts reported as warnings/errors) |
| Dep Audit | sbt-dependency-check | N/A | `sbt dependencyCheck` |

**Manifest:** `build.sbt`
**Config:** `.scalafmt.conf`, `.scalafix.conf`
**Detection:** `build.sbt` → Scala/sbt project. `.scalafmt.conf` → scalafmt configured. `.scalafix.conf` → scalafix configured. `sbt-wartremover` in `project/plugins.sbt` → WartRemover enabled.
**Note:** Scala builds can be slow. Run `sbt compile` first to warm the build cache, then lint tools run faster.

---

## Docker

| Category | Tool | Fix Command | Check Command |
|----------|------|-------------|---------------|
| Lint | hadolint | N/A (read-only) | `hadolint Dockerfile` |
| Security | trivy | N/A (read-only) | `trivy config .` |

**Manifest:** `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml`
**Config:** `.hadolint.yaml`
**Detection:** `hadolint` separate install. `trivy` separate install.
**Note:** Docker has no formatter or type checker. Lint + security only. Trivy scans both Dockerfiles (misconfig) and built images (CVEs). For image scanning: `trivy image <image-name>`.
