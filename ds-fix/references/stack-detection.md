# Stack Detection — Tiers & Disambiguation

Consumer: SKILL.md Phase 1 (Stack Detection). Multiple stacks may coexist (e.g., monorepo).

## Tier 1 — Primary stacks (full toolchain: format + lint + typecheck + security)

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

## Tier 2 — Supplementary stacks (applicable tools only, never sole detected stack)

| Signal | Stack | Activation condition |
|--------|-------|----------------------|
| `CMakeLists.txt` / `Makefile` | c-cpp | Only if `.c/.cpp/.cc/.h` source exists in `src/` or root. `Makefile` without C/C++ sources = task runner only — skip. |
| `*.sh` files | shell | Only if 3+ `.sh` files OR `scripts/` with `.sh` files. A single `setup.sh` does not make this a shell project. |
| `*.tf` files | terraform | High confidence — unique extension. Treat as primary if no other stack. |
| `Dockerfile` / `docker-compose.yml` | docker | Always supplementary. Run hadolint/trivy alongside primary stack. |

## Disambiguation

| Detected | Action |
|----------|--------|
| Tier 2 only (e.g., Dockerfile + shell) | Run security scope universally; Tier 2 tools for their files only |
| Tier 1 + Tier 2 | Full toolchain for Tier 1; supplementary tools for Tier 2 |
| `*.tf` only | Treat as primary (IaC project) |
