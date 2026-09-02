# Toolchains — detect, check, fix, test, and the composed `{check-cmd}` per stack

**Consumers:** ds-fix (fix commands), ds-quality (gate wiring), ds-test (runners), ds-init (scaffold defaults), ds-build / ds-debug / ds-issue / ds-commit and every Mechanical Done Gate (`{check-cmd}` resolution). Load only the section matching the detected stack.

**Rules that hold for every section**

| Rule | Detail |
|------|--------|
| Detect from manifests | Polyglot/monorepo → one ordered block per present stack. Never invent a check whose tool is absent; note the gap. |
| Prefer what is already there | A tool in the lockfile or a config file beats the default column. Never introduce a second formatter, linter, or test framework. |
| `{check-cmd}` | Check-mode commands only (no writes), fail-fast, chained with `&&` in the order format → lint → type → test. A missing optional type-checker is a gap-note, not a failure. |
| Fix commands | Only in a fix-mode skill (ds-fix) on a clean tree (`checkpoint-protocol.md`); never inside `{check-cmd}`. |
| Empty gate is a false signal | A `{check-cmd}` that runs nothing never passes green — report the Verification-Infrastructure Gap. |
| Windows | `./gradlew` → `gradlew.bat`; `./vendor/bin/x` → `vendor\bin\x.bat`; `npx` works unchanged. |

**Ownership note (2026):** Astral tooling (Ruff, uv, ty) was acquired by OpenAI (2026-03); Bun by Anthropic (2025-12). Licenses stay MIT/Apache-2.0 — forkable, low continuity risk; re-verify the defaults here if stewardship changes.

---

## Node.js / TypeScript

**Detect:** `package.json`. Runner from the lockfile: `package-lock.json` → npm · `pnpm-lock.yaml` → pnpm · `yarn.lock` → yarn · `bun.lock`/`bun.lockb` → bun. Tool from config: `biome.json` → Biome · `.oxlintrc.json` → Oxlint · `eslint.config.*`/`.eslintrc*` → ESLint · `.prettierrc*`/`prettier.config.*` → Prettier · `tsconfig.json` → typecheck on.

| Step | Default | Alternatives | Check | Fix |
|------|---------|--------------|-------|-----|
| format | Prettier | Biome | `npx prettier --check .` / `npx biome format .` | `npx prettier --write .` / `npx biome format --write .` |
| lint | ESLint | Biome, Oxlint | `npx eslint .` / `npx biome lint .` / `npx oxlint` | `npx eslint --fix .` / `npx biome lint --write .` / `npx oxlint --fix` |
| lint+format (unified) | Biome | — | `npx biome check .` | `npx biome check --write .` |
| type | TypeScript | — | `npx tsc --noEmit` | — (read-only) |
| test | Vitest | Jest, Mocha (maintenance mode), bun:test | `npx vitest run` / `npx jest` / `npx mocha` / `bun test` | — |
| e2e | Playwright | Cypress | `npx playwright test` / `npx cypress run` | — |
| coverage | c8 / istanbul | — | `npx vitest run --coverage` | — |
| dep audit | npm audit | pnpm/yarn/bun audit | `npm audit --audit-level=moderate` | `npm audit fix` |

**`{check-cmd}`:** `npx prettier --check . && npx eslint . && npx tsc --noEmit && npm test` — drop any step whose "present when" fails (`prettier` dep or config · `eslint` dep or config · `tsconfig.json` · `scripts.test` that is not the `"Error: no test specified"` placeholder).
**Bootstrap if missing (configs only, existing deps first):** no formatter and one is wanted → `prettier` devDep + `{}` in `.prettierrc.json`; no linter → `eslint.config.js` with `@eslint/js` recommended; no lint/format config at all → Biome (`npx biome check --write .`) is the fastest single-tool choice; no tests → one real test with the runner already present (vitest/jest), else `vitest` devDep, asserting a core module's behavior plus boundary cases.
**Detection notes:** `vitest` in deps → Vitest · `jest` → Jest · `@playwright/test` → Playwright · `cypress` → Cypress · `bunfig.toml` or `bun.lock` → bun:test available. Test dirs: `__tests__/`, `test/`, co-located `*.test.ts`/`*.spec.ts`. New projects: Vitest + Playwright (bun:test on Bun).

---

## Vanilla JS — no bundler, no build step

**Detect:** `.js` served directly (`index.html` with `<script src>`, `public/`/`static/`, a Worker or Apps Script entry) and no test-framework dep, often no `package.json`. Not "untestable", not a reason to add a bundler.

| Step | Tool | Check |
|------|------|-------|
| syntax | node | `for f in src/*.js; do node --check "$f" || exit 1; done` |
| unit | node:test (Node ≥ 20, zero deps) | `node --test` (discovers `test/`, `*.test.js`, `*_test.js`); one file: `node --test test/parser.test.js` |
| coverage | node:test | `node --test --experimental-test-coverage` |
| DOM without a browser | jsdom (most complete) · linkedom / happy-dom (lighter) | `node --test --import ./test/dom-setup.js` |
| real browser | Playwright | `npx playwright test` |

**`{check-cmd}`:** syntax loop `&& node --test` (plus `npx prettier --check .` when prettier is installed).
**Module shape first:** a `<script src>` file is a classic script, not a module — `import`ing it from a test fails or tests a different shape. Preferred: extract the unit into an ESM module both the page and the test import. Fallback: evaluate the file text in a `vm` context with fake globals, recording that the test proves *evaluated text*, not the page's load path. Check which browser globals the Node version provides (`node -p "typeof localStorage"`) and stub the missing ones by name. Layout, CSS cascade, focus order, and cross-frame event order are not observable in jsdom — those claims belong to Playwright or are not made.

---

## Python

**Detect:** `pyproject.toml` / `requirements*.txt` / `setup.py`. `[tool.ruff]` → Ruff · `[tool.black]` → Black · `[tool.mypy]` → mypy · `[tool.pyright]`/`pyrightconfig.json` → Pyright · no type config → no typecheck (never force typing onto an untyped project; report `type-check: not configured (gap)`).

| Step | Default | Alternatives | Check | Fix |
|------|---------|--------------|-------|-----|
| format | Ruff | Black | `ruff format --check .` / `black --check .` | `ruff format .` / `black .` |
| lint | Ruff | Flake8 | `ruff check .` / `flake8 .` | `ruff check --fix .` |
| type | Pyright | mypy | `pyright` / `mypy .` | — |
| test | pytest | unittest | `pytest -q` / `python -m unittest discover` | — |
| e2e | Playwright | Selenium | `pytest --browser chromium` | — |
| coverage | pytest-cov | coverage.py | `pytest --cov=src` | — |
| dep audit | pip-audit | safety | `pip-audit` / `safety check` | — |
| source security | Bandit | — | `bandit -r {source-dir}` (report-only) | — |
| property tests | Hypothesis | — | only when already a dep | — |

**`{check-cmd}`:** `ruff format --check . && ruff check . && pyright && pytest -q` (type step only when configured).
**Install:** `pip install ruff pyright pip-audit bandit` (or `pipx install ruff`). **Bootstrap if missing:** prefer Ruff (one tool = format + lint), minimal `[tool.ruff]` only when no formatter/linter exists; no tests → a real `tests/test_*.py` asserting a core function plus boundary cases. Test dirs: `tests/`, co-located `test_*.py`.

---

## Go

**Detect:** `go.mod`. Toolchain built in; `.golangci.{yml,yaml,toml,json}` + binary present → golangci-lint; `goimports` available → prefer it over `gofmt` for fixes.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | gofmt | `test -z "$(gofmt -l .)"` — exit 1 when any file is unformatted; `gofmt -l .` alone exits 0 and lists files, so it must be wrapped | `gofmt -w .` |
| imports | goimports | `test -z "$(goimports -l .)"` | `goimports -w .` |
| vet | go vet | `go vet ./...` | — |
| lint | golangci-lint | `golangci-lint run` (only with binary + config; optional `staticcheck ./...` otherwise) | `golangci-lint run --fix` |
| type/build | go build | `go build ./...` | — |
| test | go test | `go test ./...`; coverage `go test -coverprofile=cover.out ./...` | — |
| e2e | chromedp / rod | `go test -tags=e2e ./...` | — |
| dep audit | govulncheck | `govulncheck ./...` | — |
| property tests | rapid | only when `pgregory.net/rapid` is in `go.mod` | — |

**`{check-cmd}`:** `test -z "$(gofmt -l .)" && go vet ./... && go build ./... && go test ./...` (+ `golangci-lint run` when opted in).
**Install:** `go install golang.org/x/tools/cmd/goimports@latest`, `go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest`, `go install golang.org/x/vuln/cmd/govulncheck@latest`. Tests are co-located `*_test.go`, table-driven with boundary rows; `testify` in `go.mod` → its assertions.

---

## Rust

**Detect:** `Cargo.toml`. Config: `rustfmt.toml`, `clippy.toml`, `deny.toml`.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | cargo fmt | `cargo fmt --check` | `cargo fmt` |
| lint | cargo clippy | `cargo clippy -- -D warnings` | `cargo clippy --fix --allow-dirty` |
| type | cargo check | `cargo check` | — |
| test | cargo test | `cargo test`; integration `cargo test --test '*'`; coverage `cargo tarpaulin` | — |
| dep audit | cargo audit / cargo deny | `cargo audit` / `cargo deny check` | — |
| property tests | proptest | only when in `Cargo.toml` | — |
| mutation | cargo-mutants | `cargo mutants` | — |

**`{check-cmd}`:** `cargo fmt --check && cargo clippy -- -D warnings && cargo check && cargo test`.
**Install:** `rustup component add rustfmt clippy`; `cargo install cargo-audit cargo-deny`. Unit tests inline `#[cfg(test)]`; integration in `tests/`.

---

## Dart / Flutter

**Detect:** `pubspec.yaml`; contains `flutter:` → Flutter, else plain Dart. `analysis_options.yaml` configures analyze (lint + type in one step).

| Step | Flutter | Dart | Fix |
|------|---------|------|-----|
| format | `dart format --output=none --set-exit-if-changed .` | same | `dart format .` |
| lint+type | `flutter analyze` | `dart analyze` (`--no-fatal-infos` when infos are noise) | `dart fix --apply` |
| test | `flutter test`; integration `flutter test integration_test/`; coverage `flutter test --coverage` | `dart test` | — |
| e2e | patrol (`patrol test`) / maestro | — | — |
| dep audit | `dart pub outdated` | same | — |

**`{check-cmd}`:** `dart format --output=none --set-exit-if-changed . && flutter analyze && flutter test`.
**Bootstrap if missing:** `analysis_options.yaml` with `include: package:flutter_lints/flutter.yaml` (Flutter) or `include: package:lints/recommended.yaml` (Dart), the matching `dev_dependency`; no tests → a real `test/` smoke + boundary test. `patrol` in pubspec → Patrol E2E; `integration_test/` → integration tests.

---

## JVM (Kotlin / Java)

**Detect:** `build.gradle*` → Gradle · `pom.xml` → Maven. `detekt.yml` → detekt; Spotless plugin in build config → Spotless; `junit`/`kotest`/`testng` deps → runner; `espresso` → Android UI tests.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | Spotless | `./gradlew spotlessCheck` / `mvn spotless:check` | `./gradlew spotlessApply` / `mvn spotless:apply` |
| lint (Kotlin) | detekt | `./gradlew detekt` | `./gradlew detekt` (auto-correct when configured) |
| lint (Java) | Checkstyle / PMD | `./gradlew checkstyleMain` / `./gradlew pmdMain` | — |
| type/build | compiler | `./gradlew compileKotlin compileJava` / `mvn compile` | — |
| test | JUnit 5 / Kotest / TestNG | `./gradlew test` / `mvn test`; coverage `./gradlew jacocoTestReport`; Android UI `./gradlew connectedAndroidTest` | — |
| dep audit | OWASP Dependency-Check | `./gradlew dependencyCheckAnalyze` / `mvn verify -P owasp` | — |
| property tests | jqwik | only when in build config | — |
| mutation | PIT | `./gradlew pitest` | — |

**`{check-cmd}`:** `./gradlew spotlessCheck detekt test` (Gradle) — drop steps whose plugin is absent.
**Install:** plugins in `build.gradle(.kts)`/`pom.xml`, e.g. `id("io.gitlab.arturbosch.detekt") version "1.23+"`, `id("org.owasp.dependencycheck") version "10+"`. Test dirs `src/test/java|kotlin/`, `src/androidTest/`.

---

## Swift / iOS

**Detect:** `Package.swift`, `Podfile`, `*.xcodeproj`/`*.xcworkspace`. Config `.swiftformat`, `.swiftlint.yml`.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | SwiftFormat | `swiftformat --lint .` | `swiftformat .` |
| lint | SwiftLint | `swiftlint` | `swiftlint --fix` |
| type/build | swift compiler | `swift build` / `xcodebuild build -scheme {scheme}` | — |
| test | XCTest / Swift Testing | `swift test` / `xcodebuild test -scheme {scheme}`; UI `xcodebuild test -scheme UITests`; coverage `-enableCodeCoverage YES` | — |
| dep audit | manual (SPM has no audit) | review `Package.resolved` against advisories | — |

**`{check-cmd}`:** `swiftformat --lint . && swiftlint && swift build && swift test`.
**Install:** `brew install swiftformat swiftlint`; compiler with Xcode. Test dirs `Tests/`, `*Tests/`.

---

## C# / .NET

**Detect:** `*.csproj`, `*.sln`. Config `.editorconfig`, `Directory.Build.props`. `xunit`/`NUnit`/`MSTest` refs → runner; `Microsoft.Playwright` → E2E.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | dotnet format | `dotnet format --verify-no-changes` | `dotnet format` |
| lint | .NET analyzers | `dotnet build -warnaserror` | — |
| type/build | compiler | `dotnet build --no-restore` | — |
| test | xUnit / NUnit / MSTest | `dotnet test`; coverage `dotnet test --collect:"XPlat Code Coverage"`; E2E `dotnet test --filter Category=E2E` | — |
| dep audit | dotnet | `dotnet list package --vulnerable` | — |
| property tests | FsCheck | only when referenced | — |
| mutation | Stryker.NET | `dotnet stryker` | — |

**`{check-cmd}`:** `dotnet format --verify-no-changes && dotnet build -warnaserror && dotnet test`.
Test projects `*.Tests/` or `test/`.

---

## Ruby

**Detect:** `Gemfile`. `.rubocop.yml` → RuboCop; `sorbet/config` → Sorbet; `Steepfile` → Steep; `rspec` in Gemfile → RSpec else Minitest; `capybara` → E2E.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format+lint | RuboCop | `rubocop` | `rubocop -a` (safe; `-A` only on explicit request) |
| type | Sorbet / Steep | `srb tc` / `steep check` (only when configured) | — |
| test | RSpec / Minitest | `bundle exec rspec` / `bundle exec rake test`; E2E `bundle exec rspec spec/features/`, `rails test:system` | — |
| dep audit | bundler-audit | `bundle-audit check --update` | — |
| mutation | mutant | `bundle exec mutant run` | — |

**`{check-cmd}`:** `rubocop && bundle exec rspec`. **Install:** `gem install rubocop bundler-audit` (or in the Gemfile). SimpleCov loads from the test helper.

---

## PHP

**Detect:** `composer.json`. `pint.json` → Pint · `.php-cs-fixer.php` → PHP-CS-Fixer · `phpstan.neon` → PHPStan · `psalm.xml` → Psalm · `phpunit`/`pestphp/pest`/`laravel/dusk` → runners.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | Pint | `./vendor/bin/pint --test` | `./vendor/bin/pint` |
| format (alt) | PHP-CS-Fixer | `./vendor/bin/php-cs-fixer fix --dry-run` | `./vendor/bin/php-cs-fixer fix` |
| lint/static | PHPStan / Psalm | `./vendor/bin/phpstan analyze` / `./vendor/bin/psalm` | `./vendor/bin/psalm --alter` |
| test | PHPUnit / Pest | `./vendor/bin/phpunit` / `./vendor/bin/pest`; coverage `--coverage-html coverage/`; E2E `php artisan dusk`, `./vendor/bin/codecept run` | — |
| dep audit | Composer | `composer audit` | — |
| mutation | Infection | `./vendor/bin/infection` | — |

**`{check-cmd}`:** `./vendor/bin/pint --test && ./vendor/bin/phpstan analyze && ./vendor/bin/phpunit`. **Install:** `composer require --dev laravel/pint phpstan/phpstan`. Test dirs `tests/Unit/`, `tests/Feature/`, `tests/Browser/`.

---

## Elixir

**Detect:** `mix.exs`. `{:credo, …}` → credo · `{:dialyxir, …}` → dialyzer · `{:mix_audit, …}` → deps.audit · `wallaby` → E2E.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | mix format | `mix format --check-formatted` | `mix format` |
| lint | credo | `mix credo --strict` | — |
| type | dialyzer | `mix dialyzer` (first run builds the PLT — minutes) | — |
| test | ExUnit | `mix test`; coverage `mix coveralls`; E2E `mix test --only e2e` | — |
| dep audit | mix_audit | `mix deps.audit` | — |
| property tests | StreamData | only when in deps | — |

**`{check-cmd}`:** `mix format --check-formatted && mix credo --strict && mix test`.

---

## C / C++

**Detect:** `CMakeLists.txt` or `Makefile` with `.c`/`.cpp` sources. `.clang-format`/`.clang-tidy` → configured; `conanfile.*` → Conan; `compile_commands.json` → accurate clang-tidy (generate with `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON`); `GTest`/`Catch2` in CMake → runner.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | clang-format | `find src -name '*.cpp' -o -name '*.c' -o -name '*.h' \| xargs clang-format --dry-run -Werror` | `… \| xargs clang-format -i` |
| lint | clang-tidy | `clang-tidy src/*.cpp -- -I./include` | `clang-tidy src/*.cpp --fix -- -I./include` |
| static | cppcheck | `cppcheck --enable=all --error-exitcode=1 src/` | — |
| type/build | compiler | `cmake --build build` / `make` | — |
| test | Google Test / Catch2 | `ctest --test-dir build`; coverage via `--coverage` + `gcov`/`lcov` | — |
| dep audit | conan | `conan audit scan .` | — |

**`{check-cmd}`:** format dry-run `&& cmake --build build && ctest --test-dir build`. **Install:** `apt install clang-format clang-tidy cppcheck` / `brew install clang-format cppcheck` / `choco install llvm cppcheck`; Conan via `pip install conan`.

---

## Scala

**Detect:** `build.sbt`. `.scalafmt.conf` → scalafmt · `.scalafix.conf` → scalafix · `sbt-wartremover` in `project/plugins.sbt` → WartRemover · `scalatest`/`munit` deps → runner.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | scalafmt | `scalafmt --check .` | `scalafmt .` |
| lint | scalafix | `sbt "scalafixAll --check"` | `sbt scalafixAll` |
| type/build | sbt | `sbt compile` (warm the cache first; WartRemover reports here) | — |
| test | ScalaTest / MUnit | `sbt test`; coverage `sbt coverage test coverageReport` | — |
| dep audit | sbt-dependency-check | `sbt dependencyCheck` | — |

**`{check-cmd}`:** `scalafmt --check . && sbt compile test`. Plugins in `project/plugins.sbt` (`sbt-scalafmt` 2.5+, `sbt-scalafix` 0.12+).

---

## Shell / Bash

**Detect:** `*.sh` at repo root or under `scripts/`. Config `.editorconfig` (shfmt indent), `.shellcheckrc`.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | shfmt | `shfmt -d .` | `shfmt -w .` |
| lint | shellcheck | `shellcheck -x *.sh scripts/*.sh` (`-e SC1090` for non-constant `source`) | — |

**`{check-cmd}`:** `shellcheck -S warning *.sh scripts/*.sh` (+ `shfmt -d .` when installed). **Install:** `brew install shfmt shellcheck` / `apt install shellcheck` + `go install mvdan.cc/sh/v3/cmd/shfmt@latest` / `winget install koalaman.shellcheck`.

---

## Terraform / HCL

**Detect:** `*.tf`, `*.tfvars`. Config `.tflint.hcl`, `.trivy.yaml`. `terraform init` before `validate` when providers are not initialized.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | terraform fmt | `terraform fmt -check -recursive .` | `terraform fmt -recursive .` |
| validate | terraform | `terraform validate` | — |
| lint | tflint | `tflint --init && tflint` | `tflint --fix` |
| security | trivy (replaces the deprecated tfsec) | `trivy config .` | — |

**`{check-cmd}`:** `terraform fmt -check -recursive . && terraform validate && tflint && trivy config .` — drop absent tools.

---

## Docker

**Detect:** `Dockerfile`, `docker-compose.y*ml`. Config `.hadolint.yaml`.

| Step | Tool | Check |
|------|------|-------|
| lint | hadolint | `hadolint Dockerfile` |
| security | trivy | `trivy config .`; built image `trivy image {name}` |

No formatter or type step. **Install:** `brew install hadolint trivy` / `scoop install hadolint` / `docker pull hadolint/hadolint`.

---

## Google Apps Script (clasp)

**Detect:** `.clasp.json` (`scriptId`, `rootDir`) or `appsscript.json` at repo root. Lint and format the `rootDir` subtree — that is what gets pushed.

| Step | Tool | Check | Fix |
|------|------|-------|-----|
| format | Prettier | `npx prettier --check .` | `npx prettier --write .` |
| lint | ESLint + `eslint-plugin-googleappsscript` | `npx eslint .` | `npx eslint --fix .` |
| type | TypeScript over checked JS | `npx tsc --noEmit --allowJs --checkJs` | — |
| remote parity | clasp | `npx clasp show-file-status --json` (clasp 2.x: `clasp status`) | never `clasp push`/`pull` in a fix chain |

**Install:** `npm install -D @google/clasp eslint eslint-plugin-googleappsscript prettier typescript @types/google-apps-script`.
**V8 lint path:** Apps Script runs on V8 but is not Node — no `require`, no ESM, no `process`; every service (`SpreadsheetApp`, `UrlFetchApp`, `DriveApp`, `Logger`) is an implicit global. Without the plugin's globals `no-undef` fires on every service call and gets switched off, hiding real misspellings. eslintrc: `"plugins": ["googleappsscript"]` + `"env": { "googleappsscript/googleappsscript": true }`; flat config: spread `require('eslint-plugin-googleappsscript').environments.googleappsscript.globals` into `languageOptions.globals`. Set `sourceType: "script"`; keep `no-undef` and `no-unused-vars` on (an unused function is often an orphaned trigger handler).
**Typecheck path:** clasp 3.x no longer transpiles TypeScript — a TS project bundles (Rollup/esbuild) before `clasp push`, so typecheck runs on the pre-bundle source with the project's `tsc`; plain JS gets `// @ts-check` headers + `@types/google-apps-script` + the command above.
**Push is a deploy:** `clasp push` overwrites the live script, `clasp pull` overwrites the working tree — both sit on the ask-exception list. Repo-vs-remote parity = `clasp pull` into a scratch clone plus a diff, never over the working tree.

---

## Cloudflare Workers / Pages (wrangler)

**Detect:** `wrangler.toml` / `wrangler.jsonc`; `functions/` beside a Pages project → Pages Functions build; `compatibility_date` → runtime types generated from it.

| Step | Tool | Check |
|------|------|-------|
| format / lint | the repo's JS/TS chain | see Node.js / TypeScript |
| binding types | wrangler | `npx wrangler types --check` (exit 1 = `worker-configuration.d.ts` stale); regenerate with `npx wrangler types` |
| type | TypeScript | `npx tsc --noEmit` |
| build validation | wrangler | `npx wrangler deploy --dry-run --outdir dist` (compiles without publishing — the only build check that never touches the live Worker); Pages Functions `npx wrangler pages functions build --outdir dist` |

**`{check-cmd}`:** JS/TS chain `&& npx wrangler types --check && npx wrangler deploy --dry-run --outdir dist`. Bare `wrangler deploy` is a publish (ask-exception list). The Worker runtime is not Node — scope Node globals (`process`, `Buffer`, `fs`) to build tooling, never to Worker source. **Install:** `npm install -D wrangler` (local install over global, per Cloudflare).

---

## Makefile / script-driven repos (repo-native check is the done-signal)

**Detect (first hit wins):** `package.json` `scripts.check` with no test-framework dep → `npm run check` · `Makefile` with `check`/`test` targets → `make check` / `make test` · `scripts/check*.sh` (e.g. `scripts/check-consistency.sh`, `scripts/quality.sh`) → `bash scripts/{name}.sh` · `Taskfile.yml` / `Justfile` with a check task → `task check` / `just check`.

The script **is** the project's `{check-cmd}` and its test command. Generate/coverage modes are N/A — report "no test framework; repo check script `{cmd}` is the done-signal". A consistency-gate failure is an application bug in the repo's own terms. Reuse existing targets; never duplicate their logic.

---

## Generic / unknown stack

No manifest above matched. A test suite cannot be fabricated for an unknown language.

1. Wire only universally available checks that apply to files present and whose tools exist: `shellcheck` for `*.sh`, `prettier --check` for `*.json`/`*.md`/`*.yaml` when prettier is installed, `python3 -m py_compile` for stray `*.py`.
2. Report the gap explicitly: "no recognized language toolchain; established only {X}; tests not established — human decision needed", and ask (or, autonomously, record `needs-human`) which toolchain to standardize on.
3. Never mark the task green with an empty gate.

---

## Property-based testing (generates the boundary cases you did not enumerate)

| Stack | Library | Present when |
|-------|---------|--------------|
| JS / TS | fast-check | `fast-check` in deps |
| Python | Hypothesis | `hypothesis` in deps |
| Go | rapid | `pgregory.net/rapid` in `go.mod` |
| Rust | proptest | `proptest` in `Cargo.toml` |
| JVM | jqwik | in build config |
| C# / .NET | FsCheck | in csproj |
| Elixir | StreamData | `stream_data` in `mix.exs` |

Use for pure functions with algebraic properties: roundtrip, idempotence, invariant preservation, commutativity. Offer only when the library is already a dependency; absent → gap-note once, hand-enumerated boundary cases stand. Every property test still names the concrete failure it guards against.

## Mutation testing (verifies the suite, not the coverage)

| Stack | Tool | Run |
|-------|------|-----|
| JS / TS | Stryker | `npx stryker run` |
| Python | mutmut / cosmic-ray | `mutmut run` |
| Go | gremlins | `gremlins unleash` |
| Rust | cargo-mutants | `cargo mutants` |
| JVM | PIT | `./gradlew pitest` |
| C# / .NET | Stryker.NET | `dotnet stryker` |
| Ruby | mutant | `bundle exec mutant run` |
| PHP | Infection | `./vendor/bin/infection` |

Coverage proves a line executed; a survived mutant proves no test would fail if the behavior broke. On touched critical code the mutation score must not regress; a survived mutant means a missing assertion — add the test that kills it, never whitelist the mutant. Sources: Stryker Mutator (https://stryker-mutator.io/), PIT (https://pitest.org/).
