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

**Install:** Built-in with Dart/Flutter SDK. No additional install needed.
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

**Install:** `npm install -D prettier eslint typescript` (or `npm install -D @biomejs/biome` for Biome). Use `npx` prefix to run without global install.
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

**Install:** `pip install ruff mypy pyright pip-audit` (or `pip install black flake8` for alternatives). Use `pipx` for global tool installs: `pipx install ruff`.
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

**Install:** `go install golang.org/x/tools/cmd/goimports@latest` and `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest` and `go install golang.org/x/vuln/cmd/govulncheck@latest`. `gofmt` and `go vet` are built-in.
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

**Install:** `rustup component add rustfmt clippy` (built-in components). `cargo install cargo-audit cargo-deny` for security tools.
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

**Install:** Tools are Gradle/Maven plugins — add to `build.gradle(.kts)` or `pom.xml`. Example: `id("io.gitlab.arturbosch.detekt") version "1.23+"` in plugins block. OWASP: `id("org.owasp.dependencycheck") version "10+"`.
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

**Install:** `brew install swiftformat swiftlint` (macOS). SPM: add as package dependency. Swift compiler is built-in with Xcode.
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

**Install:** `dotnet format` is built-in with .NET SDK 6+. Analyzers are NuGet packages added to `.csproj`. `dotnet tool install -g dotnet-format` for older SDKs.
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

**Install:** `gem install rubocop bundler-audit` (or add to Gemfile: `gem 'rubocop', require: false`). Sorbet: `gem install sorbet sorbet-runtime`. Steep: `gem install steep`.
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

**Install:** `composer require --dev laravel/pint phpstan/phpstan` (or `composer require --dev friendsofphp/php-cs-fixer vimeo/psalm`). Tools run via `./vendor/bin/`.
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

**Install:** `apt install clang-format clang-tidy cppcheck` (Linux) or `brew install clang-format cppcheck` (macOS). Conan: `pip install conan`. On Windows: install via LLVM installer or `choco install llvm cppcheck`.
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

**Install:** `brew install shfmt shellcheck` (macOS) or `apt install shellcheck` and `go install mvdan.cc/sh/v3/cmd/shfmt@latest` (Linux). On Windows: `scoop install shfmt shellcheck`.
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

**Install:** `brew install terraform tflint trivy` (macOS) or follow official install docs. `terraform` via HashiCorp APT/YUM repos. `tflint`: `curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash`. `trivy`: `apt install trivy` (Aqua Security repo).
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

**Install:** `mix format` is built-in. Add to `mix.exs` deps: `{:credo, "~> 1.7", only: [:dev, :test], runtime: false}`, `{:dialyxir, "~> 1.4", only: [:dev, :test], runtime: false}`, `{:mix_audit, "~> 2.1", only: [:dev, :test], runtime: false}`. Then `mix deps.get`.
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

**Install:** Add to `project/plugins.sbt`: `addSbtPlugin("org.scalameta" % "sbt-scalafmt" % "2.5+")`, `addSbtPlugin("ch.epfl.scala" % "sbt-scalafix" % "0.12+")`. CLI: `cs install scalafmt` (via Coursier).
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

**Install:** `brew install hadolint trivy` (macOS) or `docker pull hadolint/hadolint` (run via Docker). `scoop install hadolint` (Windows). Trivy: see Terraform section.
**Manifest:** `Dockerfile`, `docker-compose.yml`, `docker-compose.yaml`
**Config:** `.hadolint.yaml`
**Detection:** `hadolint` separate install. `trivy` separate install.
**Note:** Docker has no formatter or type checker. Lint + security only. Trivy scans both Dockerfiles (misconfig) and built images (CVEs). For image scanning: `trivy image <image-name>`.
