# Stack Commands — ds-deps

Per-stack manifest detection, outdated-check, security-audit, bump, and lockfile-integrity commands. JVM (gradle/maven), .NET, and Swift carry the same weight as every other ecosystem — never skip these rows. Loaded when Phase 1, 2, or 5 needs a stack-specific command.

## Manifest detection (Phase 1)

| Manifest | Stack |
|----------|-------|
| `package.json` | npm / pnpm / yarn |
| `go.mod` | go |
| `pyproject.toml` / `requirements*.txt` | python (poetry / pip) |
| `Cargo.toml` | rust |
| `Gemfile` | ruby |
| `pubspec.yaml` | dart |
| `composer.json` | php |
| `build.gradle*` / `pom.xml` | jvm (gradle / maven) |
| `*.csproj` / `*.sln` | dotnet |
| `Package.swift` | swift (spm) |

Record every manifest — monorepos include all workspaces.

## Latest-stable check (Phase 2)

| Stack | Command |
|-------|---------|
| npm | `npm outdated --json` |
| pnpm | `pnpm outdated --format json` |
| yarn | `yarn outdated --json` |
| go | `go list -u -m all` |
| python | `pip list --outdated --format=json` / `poetry show --outdated` |
| rust | `cargo outdated --format json` |
| ruby | `bundle outdated` |
| dart | `dart pub outdated --json` |
| jvm (gradle) | `./gradlew dependencyUpdates` (needs the `com.github.ben-manes.versions` plugin; absent → gap-note) |
| jvm (maven) | `mvn versions:display-dependency-updates` (needs the versions-maven-plugin) |
| dotnet | `dotnet list package --outdated` |
| swift (spm) | no native outdated command — compare `Package.resolved` pinned versions against the registry; `swift package update` applies updates within `Package.swift`'s declared ranges |

## Security advisories (Phase 2)

`npm audit --json` / `pip-audit --format=json` / `cargo audit --json` / `bundler-audit` / `pub audit` / `./gradlew dependencyCheckAnalyze` (jvm/gradle) / `mvn verify -P owasp` (jvm/maven) / `dotnet list package --vulnerable` (dotnet). Also Dependabot via `gh` CLI if available. Stack-native audit command unavailable → `osv-scanner` present → run it against the lockfile (V2: `osv-scanner scan --lockfile={lockfile}`; V1 syntax `osv-scanner --lockfile=` also accepted) as the cross-ecosystem fallback and record advisories per dep; absent → skip the advisory sub-step with warning `security advisories unchecked for {manifest} — no audit tool available`.

## Version bump commands (Phase 5)

| Stack | Command |
|-------|---------|
| npm | `npm install {name}@{version}` then `npm install` to refresh lockfile |
| pnpm | `pnpm update {name} --latest` |
| yarn | `yarn upgrade {name}@{version}` |
| go | `go get {name}@{version}` then `go mod tidy` |
| python (poetry) | `poetry add {name}@{version}` |
| python (pip) | `pip install {name}=={version}` then update the project's pin file per its own convention (pip-tools: `pip-compile`; plain pins: edit `requirements.txt` entry) — never invent a new lock filename |
| cargo | `cargo update -p {name} --precise {version}` |
| jvm (maven) | `mvn versions:use-latest-releases` (scope to one package via `-Dincludes={groupId}:{artifactId}`) |
| jvm (gradle) | edit the version literal in `build.gradle(.kts)` or the `gradle/libs.versions.toml` catalog entry directly — no native single-package bump command |
| dotnet | `dotnet add package {name} --version {version}` |
| swift (spm) | edit the version requirement in `Package.swift`, then `swift package resolve` |

## Lockfile-integrity command (Phase 5, run after each group before its commit)

| Ecosystem | Command |
|-----------|---------|
| npm | `npm ls --depth=0` + `git diff --quiet package-lock.json` |
| pnpm | `pnpm install --frozen-lockfile` |
| yarn | `yarn install --immutable --mode=skip-build` |
| pip | `pip check` (+ `uv lock --check` when uv-managed) |
| cargo | `cargo tree --locked` |
| go | `go mod verify` |
| dart | `dart pub get --enforce-lockfile` |
| bundler | `bundle check` |
| composer | `composer validate --no-check-publish` + `composer install --dry-run` |
