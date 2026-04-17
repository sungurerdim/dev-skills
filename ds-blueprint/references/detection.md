# Project Detection Reference

Two-step detection: identify stack from manifests, then determine project type from secondary signals.

## Instruction Files

AI instruction files where the Blueprint Profile is written. Check in order, use first match:

| File | Tool |
|------|------|
| `CLAUDE.md` | Claude Code |
| `.cursorrules` | Cursor |
| `.cursor/rules/*.md` | Cursor (rules directory) |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurfrules` | Windsurf |
| `.aider.conf.yml` | Aider |

None found: ask user which tool they use, then create appropriate file.

## Step 1: Stack Detection

Scan project root for manifest files. Multiple may coexist.

| Manifest | Stack |
|----------|-------|
| `pubspec.yaml` | flutter |
| `package.json` | node |
| `pyproject.toml` / `setup.py` / `requirements.txt` | python |
| `go.mod` | go |
| `Cargo.toml` | rust |
| `build.gradle` / `build.gradle.kts` | jvm-gradle |
| `pom.xml` | jvm-maven |
| `Package.swift` / `*.xcodeproj` | swift |
| `*.csproj` / `*.sln` | dotnet |
| `Gemfile` | ruby |
| `composer.json` | php |
| `CMakeLists.txt` | cmake |
| `mix.exs` | elixir |
| `build.sbt` | scala |
| `*.tf` | terraform |

## Step 2: Project Type from Secondary Signals

Once stack identified, use framework dependencies, config files, and directory structure to determine project type.

### Node (`package.json`)

| Signal | Type |
|--------|------|
| `next.config.*` / `nuxt.config.*` / `svelte.config.*` / `vite.config.*` with React/Vue/Svelte dep | **web** |
| `express` / `fastify` / `koa` / `hono` / `nest` in deps | **api** |
| `bin` field in package.json | **cli** |
| `main` / `exports` field, no `bin`, no framework dep | **library** |
| `workspaces` field in package.json, or `lerna.json` / `nx.json` / `turbo.json` | **monorepo** |
| `electron` / `tauri` in deps | **desktop** |
| `react-native` in deps | **mobile** |
| `manifest.json` with `content_scripts` or `background` | **extension** |

**Disambiguation priority:** monorepo > extension > mobile > desktop > web > api > cli > library

### Flutter (`pubspec.yaml`)

| Signal | Type |
|--------|------|
| `flutter` SDK dependency present | **mobile** (default) |
| `flutter_web` or web-specific platform folder (`web/`) | **web** |
| No `flutter` SDK dep, Dart-only | **cli** or **library** (check for `bin/` directory) |

### Python (`pyproject.toml` / `setup.py`)

| Signal | Type |
|--------|------|
| `django` / `flask` / `fastapi` / `starlette` / `litestar` in deps | **api** (or **web** if template dirs present) |
| `click` / `typer` / `argparse` in deps, or `[project.scripts]` | **cli** |
| `torch` / `tensorflow` / `jax` / `transformers` in deps | **ml** |
| `pandas` / `dask` / `spark` / `airflow` / `dbt` in deps | **data** |
| `src/` layout with only library exports, no entry point | **library** |
| `Dockerfile` + `celery` / `dramatiq` | **api** (worker) |

### Go (`go.mod`)

| Signal | Type |
|--------|------|
| `cobra` / `urfave/cli` / `kong` in deps | **cli** |
| `net/http` / `gin` / `echo` / `fiber` / `chi` in imports | **api** |
| `cmd/` directory with multiple mains | **devtool** or **cli** |
| No `main` package, exported packages only | **library** |
| `terraform-provider-*` module name | **extension** |

### Rust (`Cargo.toml`)

| Signal | Type |
|--------|------|
| `clap` / `structopt` in deps, `src/main.rs` | **cli** |
| `actix-web` / `axum` / `rocket` / `warp` in deps | **api** |
| `src/lib.rs` without `src/main.rs` | **library** |
| `bevy` / `ggez` / `macroquad` in deps | **game** |
| `embedded-hal` / `cortex-m` in deps | **embedded** |
| `[workspace]` in Cargo.toml | **monorepo** |
| `tauri` in deps | **desktop** |

### JVM — Gradle / Maven

| Signal | Type |
|--------|------|
| `android { }` block in build.gradle | **mobile** |
| `spring-boot` / `quarkus` / `micronaut` / `ktor` in deps | **api** |
| `application` plugin with `mainClass` | **cli** |
| `java-library` / `kotlin("jvm")` plugin, no application | **library** |
| Multi-module with `settings.gradle` listing subprojects | **monorepo** |
| `spark` / `flink` in deps | **data** |

### Swift (`Package.swift` / `*.xcodeproj`)

| Signal | Type |
|--------|------|
| `*.xcodeproj` with iOS target | **mobile** |
| `*.xcodeproj` with macOS target + GUI framework | **desktop** |
| `vapor` / `hummingbird` in deps | **api** |
| `Package.swift` only, executable product | **cli** |
| `Package.swift` only, library product | **library** |

### C# / .NET (`*.csproj` / `*.sln`)

| Signal | Type |
|--------|------|
| `<Project Sdk="Microsoft.NET.Sdk.Web">` | **api** or **web** |
| `Microsoft.AspNetCore` in deps | **api** |
| `<OutputType>Exe</OutputType>` without web SDK | **cli** |
| `<OutputType>Library</OutputType>` | **library** |
| `Microsoft.Maui` / `Avalonia` / WPF refs | **desktop** |
| `Xamarin` / `Microsoft.Maui` with mobile targets | **mobile** |
| `*.sln` with multiple `*.csproj` | check if **monorepo** (multiple independent apps) |

### Ruby (`Gemfile`)

| Signal | Type |
|--------|------|
| `rails` in deps | **web** (or **api** if `--api` mode / no views) |
| `sinatra` / `grape` / `hanami` in deps | **api** or **web** |
| `thor` / `gli` in deps, or `exe/` directory | **cli** |
| `*.gemspec` file present | **library** |

### PHP (`composer.json`)

| Signal | Type |
|--------|------|
| `laravel/framework` in deps | **web** (or **api** if no Blade views) |
| `symfony/framework-bundle` in deps | **web** or **api** |
| `slim/slim` / `api-platform` in deps | **api** |
| `symfony/console` in deps with `bin/` | **cli** |
| No framework, library-style exports | **library** |
| WordPress plugin/theme structure | **extension** |

### Elixir (`mix.exs`)

| Signal | Type |
|--------|------|
| `phoenix` in deps | **web** or **api** |
| `nerves` in deps | **embedded** |
| `escript` build | **cli** |
| No framework, library-style | **library** |

### Scala (`build.sbt`)

| Signal | Type |
|--------|------|
| `play` / `akka-http` / `http4s` / `zio-http` in deps | **api** or **web** |
| `spark` / `flink` in deps | **data** |
| Multi-project build | **monorepo** |
| Library-only | **library** |

### Terraform (`*.tf`)

Always **iac**.

### CMake (`CMakeLists.txt`)

| Signal | Type |
|--------|------|
| Targets link against GUI frameworks (Qt, GTK, wxWidgets) | **desktop** |
| Targets link against game engines (SDL, SFML, Ogre) | **game** |
| Cross-compile toolchain for ARM/RISC-V, RTOS references | **embedded** |
| `add_executable` with CLI-style main | **cli** |
| `add_library` only | **library** |

## Step 3: Supplementary Stack Detection

These coexist with primary stack. Detect but do not use for project type classification.

| File | Supplementary Stack | Action |
|------|---------------------|--------|
| `Dockerfile` / `docker-compose.yml` | Docker | Note in profile (Deploy: container) |
| `*.sh` in root or `scripts/` | Shell | Note in profile (Toolchain: shell scripts) |
| `.github/workflows/*.yml` | GitHub Actions | Note in profile (CI: GitHub Actions) |
| `.gitlab-ci.yml` | GitLab CI | Note in profile (CI: GitLab CI) |
| `Makefile` (without C/C++ sources) | Make (build tool) | Note in profile (Toolchain: Make) |
| `Justfile` | just (task runner) | Note in profile (Toolchain: just) |
| `Taskfile.yml` | Task (task runner) | Note in profile (Toolchain: Task) |

## Conflict Resolution

| Scenario | Resolution |
|----------|------------|
| Multiple primary stacks (e.g., `package.json` + `pyproject.toml`) | Monorepo if workspace config exists. Otherwise, determine primary by source file count — stack with more source files is primary. |
| Framework ambiguity (e.g., Rails could be web or api) | Check for view templates (`app/views/`, `templates/`). Present → **web**. Absent → **api**. |
| Multiple types match (e.g., cli + library) | Use disambiguation priority: monorepo > mobile > desktop > web > api > cli > library > devtool |
| `Makefile` present — is it C/C++ or just task runner? | Check if `Makefile` references `gcc`, `g++`, `clang`, `$(CC)`, or `$(CXX)`. Also check for `.c`/`.cpp`/`.h` source files. Both present → c-cpp. Otherwise → supplementary build tool. |
