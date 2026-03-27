# Test Frameworks Reference

Per-stack test framework detection and commands. Load only the section matching the detected stack.

---

## Node.js / TypeScript

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit/Integration (default) | Vitest | `npx vitest run` | `vitest.config.ts` |
| Unit/Integration (alt) | Jest | `npx jest` | `jest.config.*` |
| Unit/Integration (alt) | Mocha | `npx mocha` | `.mocharc.*` |
| Unit/Integration (Bun) | bun:test | `bun test` | `bunfig.toml` (optional) |
| E2E (default) | Playwright | `npx playwright test` | `playwright.config.ts` |
| E2E (alt) | Cypress | `npx cypress run` | `cypress.config.*` |
| Coverage | c8 / istanbul | `npx vitest run --coverage` | `vitest.config.ts` |

**Detection:** `vitest` in deps → Vitest. `jest` in deps → Jest. `@playwright/test` in deps → Playwright. `cypress` in deps → Cypress. `bun.lock` or `bunfig.toml` present → Bun test available.
**Recommended (new projects):** Vitest (unit) + Playwright (E2E). For Bun projects: bun:test (unit) + Playwright (E2E).
**Test directory:** `__tests__/`, `test/`, or co-located `*.test.ts` / `*.spec.ts`.

**2025-2026 Notes:**
- **Vitest** is the dominant test runner in the Vite ecosystem, ~3x faster than Jest due to native ESM and Vite's transform pipeline. Jest-compatible API makes migration straightforward.
- **bun:test** is the fastest option for Bun-native projects. Built-in, zero-config, Jest-compatible API. Use when the project already runs on Bun.
- **Playwright** has overtaken Cypress in market share for browser E2E testing (2025). Better multi-browser support, auto-wait, and trace viewer. Cypress remains viable for existing projects but new projects should prefer Playwright.
- **Mocha** is in maintenance mode. Migrate to Vitest for new projects.
- **Jest** remains widely used but new projects in the Vite ecosystem should prefer Vitest for better performance and native ESM support.

---

## Python

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit/Integration | pytest | `pytest` | `pyproject.toml [tool.pytest]`, `pytest.ini` |
| Unit/Integration (alt) | unittest | `python -m unittest discover` | N/A |
| E2E | Playwright | `pytest --browser chromium` | `conftest.py` with playwright fixtures |
| E2E (alt) | Selenium | `pytest` (with selenium fixtures) | `conftest.py` |
| Coverage | coverage.py / pytest-cov | `pytest --cov=src` | `.coveragerc`, `pyproject.toml` |

**Detection:** `pytest` in deps → pytest. `playwright` in deps → Playwright E2E. `selenium` in deps → Selenium.
**Recommended:** pytest + pytest-cov + playwright.
**Test directory:** `tests/`, or co-located `test_*.py` / `*_test.py`.

---

## Go

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit/Integration | go test | `go test ./...` | N/A (built-in) |
| Assertions (opt) | testify | `go test ./...` | N/A |
| E2E | chromedp / rod | `go test -tags=e2e ./...` | Build tags |
| Coverage | go test | `go test -coverprofile=cover.out ./...` | N/A |

**Detection:** Built-in. `testify` in go.mod → testify assertions.
**Test directory:** Co-located `*_test.go` (Go convention).

---

## Rust

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit/Integration | cargo test | `cargo test` | N/A (built-in) |
| Integration | tests/ dir | `cargo test --test '*'` | `tests/` directory |
| E2E | (custom) | `cargo test -p e2e` | Workspace member |
| Coverage | cargo-tarpaulin | `cargo tarpaulin` | `tarpaulin.toml` |

**Detection:** Built-in. `tarpaulin` installed → coverage available.
**Test directory:** Unit: inline `#[cfg(test)]` modules. Integration: `tests/`.

---

## Flutter / Dart

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit/Widget | flutter test | `flutter test` | N/A (built-in) |
| Integration | integration_test | `flutter test integration_test/` | `integration_test/` directory |
| E2E | patrol / maestro | `patrol test` | `patrol.yaml` |
| Coverage | flutter test | `flutter test --coverage` | N/A |

**Detection:** Built-in. `patrol` in pubspec → Patrol E2E. `integration_test` dir → integration tests.
**Test directory:** `test/` (unit/widget), `integration_test/` (integration).

---

## JVM (Kotlin / Java)

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (Java) | JUnit 5 | `./gradlew test` | `build.gradle*` |
| Unit (Kotlin) | Kotest | `./gradlew test` | `build.gradle.kts` |
| Unit (alt) | TestNG | `./gradlew test` | `build.gradle*` |
| Android UI | Espresso | `./gradlew connectedAndroidTest` | `build.gradle*` |
| E2E (web) | Selenium | `./gradlew test -Ptag=e2e` | Test tags |
| Coverage | JaCoCo | `./gradlew jacocoTestReport` | `build.gradle*` |

**Detection:** `junit` in deps → JUnit. `kotest` → Kotest. `espresso` → Android UI tests.
**Test directory:** `src/test/java/`, `src/test/kotlin/`, `src/androidTest/`.

---

## Swift / iOS

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit | XCTest | `swift test` or `xcodebuild test` | Built-in |
| UI | XCUITest | `xcodebuild test -scheme UITests` | Xcode scheme |
| E2E (alt) | EarlGrey | `xcodebuild test` | Pod/SPM dep |
| Coverage | xcodebuild | `xcodebuild test -enableCodeCoverage YES` | Xcode |

**Detection:** Built-in. `XCUITest` target → UI tests available.
**Test directory:** `Tests/`, `*Tests/` (SPM), `*Tests` target (Xcode).

---

## C# / .NET

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (default) | xUnit | `dotnet test` | `*.csproj` with xUnit ref |
| Unit (alt) | NUnit | `dotnet test` | `*.csproj` with NUnit ref |
| Unit (alt) | MSTest | `dotnet test` | `*.csproj` with MSTest ref |
| E2E | Playwright | `dotnet test --filter Category=E2E` | `Microsoft.Playwright` ref |
| Coverage | coverlet | `dotnet test --collect:"XPlat Code Coverage"` | `coverlet.runsettings` |

**Detection:** `xunit` in csproj → xUnit. `NUnit` → NUnit. `Microsoft.Playwright` → E2E.
**Test directory:** `*.Tests/` project, or `test/` directory.

---

## Ruby

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (default) | RSpec | `bundle exec rspec` | `.rspec`, `spec/` |
| Unit (alt) | Minitest | `bundle exec rake test` | `test/` |
| E2E | Capybara | `bundle exec rspec spec/features/` | `spec/features/` |
| E2E (system) | Rails system tests | `rails test:system` | `test/system/` |
| Coverage | SimpleCov | (auto-loaded in test helper) | `spec/spec_helper.rb` |

**Detection:** `rspec` in Gemfile → RSpec. `capybara` → Capybara E2E.
**Test directory:** `spec/` (RSpec), `test/` (Minitest).

---

## PHP

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (default) | PHPUnit | `./vendor/bin/phpunit` | `phpunit.xml` |
| Unit (alt) | Pest | `./vendor/bin/pest` | `phpunit.xml` (Pest wraps PHPUnit) |
| E2E (Laravel) | Laravel Dusk | `php artisan dusk` | `tests/Browser/` |
| E2E (generic) | Codeception | `./vendor/bin/codecept run` | `codeception.yml` |
| Coverage | PHPUnit | `./vendor/bin/phpunit --coverage-html coverage/` | `phpunit.xml` |

**Detection:** `phpunit` in composer.json → PHPUnit. `pestphp/pest` → Pest. `laravel/dusk` → Dusk.
**Test directory:** `tests/Unit/`, `tests/Feature/`, `tests/Browser/`.

---

## Elixir

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit | ExUnit | `mix test` | Built-in |
| E2E (Phoenix) | Wallaby | `mix test --only e2e` | `test/` with tags |
| Coverage | excoveralls | `mix coveralls` | `coveralls.json` |

**Detection:** Built-in. `wallaby` in deps → Wallaby E2E.
**Test directory:** `test/`.

---

## C / C++

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (default) | Google Test | `ctest --test-dir build` | `CMakeLists.txt` with GTest |
| Unit (alt) | Catch2 | `ctest --test-dir build` | `CMakeLists.txt` with Catch2 |
| Coverage | gcov / lcov | `gcov *.gcno && lcov --capture -d . -o coverage.info` | Compile with `--coverage` |

**Detection:** `GTest` or `gtest` in CMakeLists.txt → Google Test. `Catch2` → Catch2.
**Test directory:** `test/`, `tests/`.

---

## Scala

| Category | Tool | Run Command | Config |
|----------|------|-------------|--------|
| Unit (default) | ScalaTest | `sbt test` | `build.sbt` with scalatest dep |
| Unit (alt) | MUnit | `sbt test` | `build.sbt` with munit dep |
| Coverage | scoverage | `sbt coverage test coverageReport` | sbt-scoverage plugin |

**Detection:** `scalatest` in build.sbt → ScalaTest. `munit` → MUnit.
**Test directory:** `src/test/scala/`.
