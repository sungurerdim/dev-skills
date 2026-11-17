#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Project facts every dev-skills skill reads the same way — Python 3.8+ stdlib only, no network.

  ds_detect.py check [DIR]      the fail-fast quality command (format -> lint -> type -> test); empty = none found
  ds_detect.py signals [DIR]    the Signals line keys as JSON: {key: {"value": ..., "by": "file|tool|judge"}}
  ds_detect.py --self-test      fixture checks on temp repos

`by` says how a value was reached: `file` (a file or manifest fact), `tool` (an installed CLI answered), `judge`
(a heuristic the model confirms by reading: auth, pii, audience). Imported by ds-gate (hook) and ds-audit; ds-gate's
installer copies this file next to its hook so the hook stays one directory.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKIP = re.compile(r"(^|/)(vendor|node_modules|third_party|dist|build|target|\.git|Pods|\.dart_tool|\.venv|venv|ds|testdata|fixtures|__fixtures__)(/|$)"
                  r"|\.(pb|gen|g|freezed|generated|min)\.\w+$|_pb2\.py$")
SRC = {".go", ".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".vue", ".svelte", ".rs", ".java", ".kt", ".kts",
       ".swift", ".m", ".dart", ".cs", ".fs", ".php", ".rb", ".c", ".h", ".cc", ".cpp", ".hpp", ".scala", ".ex", ".exs",
       ".erl", ".clj", ".lua", ".sh", ".ps1", ".sql", ".zig", ".nim", ".hs", ".ml", ".r", ".jl"}
MANIFESTS = ("package.json", "go.mod", "pyproject.toml", "Cargo.toml", "pubspec.yaml", "composer.json", "Gemfile",
             "build.gradle", "build.gradle.kts", "pom.xml", "Package.swift", "mix.exs", "build.sbt")


def git(root, *args, timeout=60) -> str:
    try:
        r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return r.stdout if r.returncode == 0 else ""


def files(root) -> list:
    """Tracked + untracked-not-ignored files (git), else a directory walk; vendored and generated files skipped."""
    root = Path(root)
    out = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    if out:
        names = [n for n in out.split("\0") if n]
    else:
        names = [(Path(d) / f).relative_to(root).as_posix() for d, _, fs in os.walk(root) for f in fs]
    return sorted(n for n in names if not SKIP.search(n) and (root / n).is_file())


GIT_LOCAL = ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
             "GIT_COMMON_DIR", "GIT_PREFIX")


def isolate_git(env=None) -> dict:
    """Drop the repo-location variables git sets for a hook (a pre-commit of `commit --only` points GIT_INDEX_FILE at a
    temporary index); a self-test's temp repo would otherwise write into the outer commit. Returns what was removed."""
    env = os.environ if env is None else env
    return {k: env.pop(k) for k in GIT_LOCAL if k in env}


def read(path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# --- dependencies -----------------------------------------------------------------------------------------

def deps(root, names=None) -> list:
    """Direct dependencies from the common manifests; kind = runtime | dev."""
    root = Path(root)
    names = files(root) if names is None else names
    found = []

    def add(manifest, name, kind="runtime"):
        found.append({"manifest": manifest, "name": name, "kind": kind})

    for n in names:
        base, text = n.rsplit("/", 1)[-1], None
        if base == "go.mod":
            text = read(root / n)
            for m in re.finditer(r"^\s*(?:require\s+)?([\w.\-]+\.[\w.\-/]+)\s+v[\w.\-+]+(\s*//\s*indirect)?", text, re.M):
                if not m.group(2):
                    add(n, m.group(1))
        elif base == "package.json":
            try:
                data = json.loads(read(root / n))
            except ValueError:
                continue
            for key, kind in (("dependencies", "runtime"), ("peerDependencies", "runtime"), ("devDependencies", "dev")):
                for name in (data.get(key) or {}):
                    add(n, name, kind)
        elif re.match(r"requirements.*\.txt$", base):
            for line in read(root / n).splitlines():
                m = re.match(r"\s*([A-Za-z0-9][\w.\-\[\]]*)", line)
                if m and not line.lstrip().startswith(("#", "-")):
                    add(n, m.group(1), "dev" if "dev" in base or "test" in base else "runtime")
        elif base == "pyproject.toml":
            text = read(root / n)
            m = re.search(r"^dependencies\s*=\s*\[(.*?)\]", text, re.M | re.S)
            for name in re.findall(r"[\"']([A-Za-z0-9][\w.\-]*)", m.group(1) if m else ""):
                add(n, name)
            for block in re.findall(r"^\[tool\.poetry\.dependencies\]\n(.*?)(?=^\[|\Z)", text, re.M | re.S):
                for name in re.findall(r"^([A-Za-z0-9][\w.\-]*)\s*=", block, re.M):
                    if name != "python":
                        add(n, name)
        elif base in ("Cargo.toml", "pubspec.yaml"):
            text = read(root / n)
            sep = "=" if base == "Cargo.toml" else ":"
            head = r"^\[(dev-)?dependencies\]\n" if base == "Cargo.toml" else r"^(dev_)?dependencies:\n"
            for m in re.finditer(head + r"(.*?)(?=^\S|\Z)" if base == "pubspec.yaml" else head + r"(.*?)(?=^\[|\Z)",
                                 text, re.M | re.S):
                for name in re.findall(r"^\s{0,2}([A-Za-z0-9][\w\-]*)\s*" + sep, m.group(2), re.M):
                    if name not in ("flutter", "sdk"):
                        add(n, name, "dev" if m.group(1) else "runtime")
        elif base == "composer.json":
            try:
                data = json.loads(read(root / n))
            except ValueError:
                continue
            for key, kind in (("require", "runtime"), ("require-dev", "dev")):
                for name in (data.get(key) or {}):
                    if "/" in name:
                        add(n, name, kind)
        elif base == "Gemfile":
            for name in re.findall(r"^\s*gem\s+['\"]([^'\"]+)", read(root / n), re.M):
                add(n, name)
        elif base.endswith(".csproj"):
            for name in re.findall(r"<PackageReference\s+Include=\"([^\"]+)\"", read(root / n)):
                add(n, name)
        elif base in ("build.gradle", "build.gradle.kts"):
            for kind, name in re.findall(r"^\s*(\w+)\s*\(?\s*[\"']([\w.\-]+:[\w.\-]+)", read(root / n), re.M):
                if kind in ("implementation", "api", "runtimeOnly", "compileOnly"):
                    add(n, name)
                elif kind.startswith("test"):
                    add(n, name, "dev")
        elif base == "pom.xml":
            for block in re.findall(r"<dependency>(.*?)</dependency>", read(root / n), re.S):
                a = re.search(r"<artifactId>([^<]+)", block)
                if a:
                    add(n, a.group(1), "dev" if "<scope>test" in block else "runtime")
    return found


# --- quality command --------------------------------------------------------------------------------------

def check_cmd(root) -> str:
    """The fail-fast quality command for `root`: only checks whose tools/configs exist, format -> lint -> type -> test."""
    root = Path(root)

    def has(name):  # an executable on PATH
        return shutil.which(name) is not None

    def exists(*names):
        return any((root / n).exists() for n in names)

    def glob(pattern):
        return any(root.glob(pattern))

    def text(name) -> str:
        try:
            return (root / name).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""

    def grep(name, pattern, flags=0) -> bool:
        return re.search(pattern, text(name), flags) is not None

    # 1) explicit single entry points win
    if exists("scripts/quality.sh"):
        return "bash scripts/quality.sh"
    if exists("Makefile") and grep("Makefile", r"^quality:", re.M):
        return "make quality"
    if exists("package.json") and grep("package.json", r'"quality"\s*:'):
        return "pnpm run quality" if exists("pnpm-lock.yaml") else "yarn quality" if exists("yarn.lock") else "npm run quality"

    cmds: list[str] = []

    def add(c):
        cmds.append(c)

    # Dart / Flutter
    if exists("pubspec.yaml"):
        run = "flutter" if grep("pubspec.yaml", r"^\s*flutter:", re.M) else "dart"
        add("dart format --output=none --set-exit-if-changed .")
        add(f"{run} analyze")
        if exists("test") or glob("*_test.dart"):
            add(f"{run} test --exclude-tags integration")  # integration tags need live services a local gate cannot supply

    # JS / TS
    if exists("package.json"):
        pm = "pnpm" if exists("pnpm-lock.yaml") else "yarn" if exists("yarn.lock") else "npm"
        if glob(".prettierrc*") or glob("prettier.config.*") or grep("package.json", r'"prettier"'):
            add("npx --no-install prettier --check .")
        if glob(".eslintrc*") or glob("eslint.config.*") or grep("package.json", r'"eslint"'):
            add("npx --no-install eslint .")
        if exists("tsconfig.json"):
            add("npx --no-install tsc --noEmit")
        if grep("package.json", r'"test"\s*:') and not grep("package.json", r"no test specified"):
            add({"pnpm": "pnpm test", "yarn": "yarn test"}.get(pm, "npm test"))

    # Python (a uv project runs its tools from its own environment: a global pytest cannot import the project's deps)
    if exists("pyproject.toml", "setup.py") or glob("requirements*.txt"):
        uv = exists("uv.lock") and has("uv")
        prefix = "uv run " if uv else ""

        def pyhave(tool):
            return exists(f".venv/bin/{tool}", f".venv/Scripts/{tool}.exe") if uv else has(tool)

        if pyhave("ruff"):
            add(f"{prefix}ruff format --check .")
            add(f"{prefix}ruff check .")
        elif pyhave("black"):
            add(f"{prefix}black --check .")
        if pyhave("mypy") and (exists("mypy.ini") or grep("pyproject.toml", r"\[tool\.mypy\]")):
            add(f"{prefix}mypy .")
        if pyhave("pytest"):
            add(f"{prefix}pytest -q")

    # Go (toolchain built-in)
    if exists("go.mod"):
        add('test -z "$(gofmt -l .)"')
        if has("golangci-lint") and exists(".golangci.yml", ".golangci.yaml", ".golangci.toml", ".golangci.json"):
            add("golangci-lint run")
        add("go vet ./...")
        add("go build ./...")
        add("go test ./...")

    # Rust (toolchain built-in)
    if exists("Cargo.toml"):
        add("cargo fmt --check")
        add("cargo clippy -- -D warnings")
        add("cargo test")

    # JVM via the Gradle wrapper (Maven skipped: no cheap, reliable plugin-presence signal)
    if exists("gradlew") and exists("build.gradle", "build.gradle.kts"):
        if any("spotless" in text(n) for n in ("build.gradle", "build.gradle.kts")):
            add("./gradlew spotlessCheck")
        if exists("detekt.yml", "config/detekt/detekt.yml"):
            add("./gradlew detekt")
        add("./gradlew test")

    # Swift
    if exists("Package.swift") and has("swift"):
        if has("swiftformat"):
            add("swiftformat --lint .")
        if has("swiftlint"):
            add("swiftlint")
        add("swift build")
        add("swift test")

    # C# / .NET
    if (glob("*.sln") or glob("*.csproj")) and has("dotnet"):
        add("dotnet format --verify-no-changes")
        add("dotnet build --no-restore")
        add("dotnet test")

    # Ruby
    if exists("Gemfile"):
        if has("rubocop"):
            add("rubocop")
        if grep("Gemfile", r"rspec") and has("bundle"):
            add("bundle exec rspec")

    # PHP (vendor/bin binaries only — never invents a check whose tool wasn't installed)
    if exists("composer.json"):
        for tool, c in (("pint", "./vendor/bin/pint --test"), ("phpstan", "./vendor/bin/phpstan analyze"),
                        ("phpunit", "./vendor/bin/phpunit")):
            if exists(f"vendor/bin/{tool}"):
                add(c)

    # Elixir (dialyzer skipped: the first run builds the PLT, minutes-long — unfit for a per-Stop hook)
    if exists("mix.exs") and has("mix"):
        add("mix format --check-formatted")
        if grep("mix.exs", r"credo"):
            add("mix credo --strict")
        add("mix test")

    # Scala
    if exists("build.sbt") and has("sbt"):
        if has("scalafmt") and exists(".scalafmt.conf"):
            add("scalafmt --check .")
        add("sbt compile test")

    # C/C++ — static analysis only (format/build need a pre-configured out-of-source build dir)
    if has("cppcheck") and exists("src") and (glob("src/*.c") or glob("src/*.cpp") or glob("src/*.cc")):
        add("cppcheck --enable=warning,performance --error-exitcode=1 src/")

    # Terraform — fmt only (validate/tflint need `terraform init` and a network provider download)
    if glob("*.tf") and has("terraform"):
        add("terraform fmt -check -recursive .")

    # Shell
    if has("shellcheck"):
        targets = [t for t, ok in (("./*.sh", glob("*.sh")), ("scripts/*.sh", glob("scripts/*.sh"))) if ok]
        if targets:
            add("shellcheck -S warning " + " ".join(targets))

    # Docker — lint only
    if exists("Dockerfile") and has("hadolint"):
        add("hadolint Dockerfile")

    # Vanilla JS — no bundler, no package.json (node:test, Node >= 20)
    if not exists("package.json") and has("node") and (exists("test") or glob("*.test.js")):
        add("node --test")

    # Not added, by design: clasp / wrangler checks need an authenticated networked call, and a generic ad-hoc sweep has
    # no manifest to key off — both stay with the explicit /ds-gate bootstrap, never the silent auto-arm.
    return " && ".join(cmds)


# --- signals ----------------------------------------------------------------------------------------------

DEPS = {  # dependency-name fragment -> (key, value); matched against manifest text, lowercase
    "ui": [("electron", "desktop"), ("@tauri-apps", "desktop"), ("tauri", "desktop"), ("bubbletea", "cli-tui"),
           ("tview", "cli-tui"), ("ratatui", "cli-tui"), ("textual", "cli-tui"), ("urwid", "cli-tui"),
           ("prompt_toolkit", "cli-tui"), ("blessed", "cli-tui"), ('"ink"', "cli-tui"), ("crossterm", "cli-tui")],
    "db": [("postgres", "postgres"), ("psycopg", "postgres"), ("jackc/pgx", "postgres"), ("lib/pq", "postgres"),
           ('"pg"', "postgres"), ("asyncpg", "postgres"), ("npgsql", "postgres"), ("mysql", "mysql"),
           ("mariadb", "mysql"), ("sqlite", "sqlite"), ("sqflite", "sqlite"), ("drift", "sqlite"),
           ("mongo", "mongodb"), ("redis", "redis"), ("dynamodb", "dynamodb"), ("firestore", "firestore"),
           ("firebase-admin", "firestore"), ("prisma", "other"), ("typeorm", "other"), ("sqlalchemy", "other"),
           ("gorm.io", "other"), ("diesel", "other"), ("hibernate", "other"), ("entityframework", "other")],
    "auth": [("next-auth", "oauth"), ("@auth/", "oauth"), ("passport", "session"), ("express-session", "session"),
             ("flask-login", "session"), ("devise", "session"), ("jsonwebtoken", "jwt"), ("pyjwt", "jwt"),
             ("golang-jwt", "jwt"), ("jose", "jwt"), ("oauth", "oauth"), ("authlib", "oauth"),
             ("firebase_auth", "firebase"), ("firebase/auth", "firebase"), ("@clerk", "clerk"), ("auth0", "auth0"),
             ("supabase", "supabase")],
    "billing": [("stripe", "stripe"), ("paddle", "paddle"), ("lemonsqueezy", "lemonsqueezy"),
                ("revenuecat", "revenuecat"), ("purchases_flutter", "revenuecat"),
                ("react-native-purchases", "revenuecat"), ("in_app_purchase", "store-iap"),
                ("billingclient", "store-iap"), ("storekit", "store-iap")],
    "mobile": [("react-native", "react-native"), ("expo", "expo"), ("@capacitor/core", "capacitor"),
               ("androidx.compose", "compose"), ("kotlin-multiplatform", "kmp")],
    "i18n": [("i18next", "yes"), ("react-intl", "yes"), ("formatjs", "yes"), ("vue-i18n", "yes"),
             ("flutter_localizations", "yes"), ("intl", "yes"), ("gettext", "yes"), ("babel", "yes"),
             ("go-i18n", "yes"), ("fluent", "yes")],
    "pii": [("segment", "yes"), ("mixpanel", "yes"), ("amplitude", "yes"), ("posthog", "yes"),
            ("google-analytics", "yes"), ("firebase_analytics", "yes"), ("sentry", "yes")],
    "api": [("graphql", "graphql"), ("grpc", "grpc"), ("@trpc", "rpc"), ("jsonrpc", "rpc"), ("json-rpc", "rpc")],
}
INTEGRATIONS = ("stripe", "sentry", "firebase", "twilio", "sendgrid", "openai", "anthropic", "supabase", "auth0",
                "clerk", "posthog", "mixpanel", "segment", "algolia", "cloudinary", "mailgun", "postmark", "resend",
                "slack", "github", "aws", "gcp", "azure", "datadog", "launchdarkly", "paddle", "revenuecat")
ROUTES = re.compile(r"\bapp\.(get|post|put|delete|patch)\(|@app\.(route|get|post)|@(Rest)?Controller\b|\brouter\.(get|"
                    r"post|put|delete|patch|Handle)|http\.HandleFunc|\bmux\.Handle|@(Get|Post|Put|Delete)(Mapping)?\(|"
                    r"\bFastAPI\(|\bexpress\(\)|Route::(get|post)|\bgin\.(Default|New)\(|\becho\.New\(|"
                    r"\bactix_web\b|\baxum::Router|\bflask\.Flask\(|\bFlask\(__name__\)")
PII_FIELDS = re.compile(r"\b(e_?mail|phone(_?number)?|address|birth_?date|dob|ssn|national_?id|tax_?id|ip_?address|"
                        r"passport|iban)\b", re.I)


def signals(root) -> dict:
    root = Path(root)
    names = files(root)
    low = [n.lower() for n in names]
    dep_names = [d["name"].lower() for d in deps(root, names)]
    manifest = "\n".join(dep_names)  # one dependency name per line: fragments match names, never module paths
    env = "\n".join(read(root / n) for n in names if re.search(r"(^|/)\.env\.(example|sample|template)$", n)).lower()
    # this detector's own copy is skipped: its patterns and self-test fixtures match themselves (api=rest, auth=other)
    src = [n for n in names if Path(n).suffix.lower() in SRC and Path(n).name != Path(__file__).name]
    out = {}

    def put(key, value, by="file"):
        out[key] = {"value": value, "by": by}

    def dep(key):
        return sorted({v for frag, v in DEPS[key] if any(frag.strip('"') == n or frag.strip('"') in n.split("/")[-1]
                                                          if frag.startswith('"') else frag in n for n in dep_names)})

    def any_path(pattern):
        rx = re.compile(pattern)
        return any(rx.search(n) for n in low)

    def grep_src(rx, limit=4000):
        return any(rx.search(read(root / n)) for n in src[:limit])

    ui = set()
    if any_path(r"\.(html|jsx|tsx|vue|svelte|css|scss)$"):
        ui.add("web")
    if any_path(r"\.xcodeproj(/|$)") or any_path(r"(^|/)info\.plist$"):
        ui.add("ios")
    if any_path(r"(^|/)androidmanifest\.xml$"):
        ui.add("android")
    ui |= set(dep("ui"))
    if "pubspec.yaml" in low and any_path(r"^(macos|windows|linux)/"):
        ui.add("desktop")
    put("ui", ",".join(sorted(ui)) or "none")

    api = set(dep("api"))
    if any_path(r"\.(graphql|gql)$"):
        api.add("graphql")
    if any(n.endswith(".proto") and re.search(r"^\s*service\s+\w+", read(root / n), re.M) for n in names):
        api.add("grpc")
    if grep_src(ROUTES):
        api.add("rest")
    put("api", ",".join(sorted(api)) or "none")

    db = set(dep("db"))
    for scheme, value in (("postgres", "postgres"), ("mysql", "mysql"), ("mongodb", "mongodb"), ("redis", "redis"),
                          ("sqlite", "sqlite")):
        if scheme + "://" in env or scheme + ":" in env:
            db.add(value)
    if any_path(r"(^|/)(migrations?|db/migrate|alembic)/"):
        db.add("other") if not db else None
    put("db", ",".join(sorted(db - ({"other"} if len(db) > 1 else set()))) or "none")

    auth = dep("auth")
    if not auth and grep_src(re.compile(r"Authorization|/login\b|signIn|sign_in", re.I), limit=1500):
        auth = ["other"]
    put("auth", ",".join(auth) or "none", "judge")

    billing = dep("billing")
    put("billing", ",".join(billing) or "none")

    pii = bool(dep("pii")) or any(PII_FIELDS.search(read(root / n)) for n in names
                                   if re.search(r"(model|schema|entity|migration|\.sql$|\.prisma$)", n.lower()))
    put("pii", "yes" if pii else "no", "judge")

    i18n = any_path(r"(^|/)(locales?|i18n|l10n|translations)/") or any_path(r"\.(arb|po|xliff|strings)$") or dep("i18n")
    put("i18n", "yes" if i18n else "no")

    runners = []
    for frag, runner in (("pytest", "pytest"), ("vitest", "vitest"), ("jest", "jest"), ("mocha", "mocha"),
                         ("flutter_test", "flutter_test"), ("rspec", "rspec"), ("phpunit", "phpunit"),
                         ("junit", "junit"), ("xunit", "xunit"), ("nunit", "nunit"), ("playwright", "playwright")):
        if frag in manifest:
            runners.append(runner)
    if any(n.endswith("_test.go") for n in low):
        runners.append("go-test")
    if "cargo.toml" in low and (any_path(r"^tests/") or grep_src(re.compile(r"#\[test\]"), limit=800)):
        runners.append("cargo-test")
    if not runners and any_path(r"(^|/)(tests?|__tests__|spec)/|(_test|\.test|\.spec)\.\w+$|(^|/)test_[^/]+\.py$"):
        runners.append("other")
    put("tests", ",".join(runners) or "none")

    ci = [v for p, v in ((r"^\.github/workflows/.+\.ya?ml$", "github"), (r"^\.gitlab-ci\.yml$", "gitlab"),
                         (r"^\.circleci/", "circle"), (r"^azure-pipelines\.yml$", "azure"),
                         (r"^(jenkinsfile|\.travis\.yml|bitbucket-pipelines\.yml|\.woodpecker)", "other")) if any_path(p)]
    put("ci", ",".join(ci) or "none")

    deploy = [v for p, v in ((r"(^|/)dockerfile$|(^|/)(docker-)?compose\.ya?ml$", "docker"),
                             (r"^(k8s|kubernetes|helm|charts)/|(^|/)chart\.yaml$", "k8s"),
                             (r"(^|/)(serverless\.yml|wrangler\.(toml|jsonc?)|vercel\.json|netlify\.toml)$", "serverless"),
                             (r"(^|/)(procfile|fly\.toml|render\.yaml|app\.yaml)$", "paas"),
                             (r"(^|/)(fastlane/|eas\.json$)", "store")) if any_path(p)]
    put("deploy", ",".join(deploy) or "none")

    mobile = set(dep("mobile"))
    if "pubspec.yaml" in low and re.search(r"^\s*flutter:", read(root / "pubspec.yaml"), re.M):
        mobile.add("flutter")
    if any_path(r"\.swift$") and grep_src(re.compile(r"^import SwiftUI", re.M), limit=800):
        mobile.add("swiftui")
    if any_path(r"(^|/)capacitor\.config\.(json|ts|js)$"):
        mobile.add("capacitor")
    put("mobile", ",".join(sorted(mobile)) or "none")

    platforms = {p for p in ui if p in ("web", "ios", "android", "desktop")}
    bin_field = any('"bin"' in read(root / n) for n in names if n.endswith("package.json"))
    if "cli-tui" in ui or (not platforms and any(re.search(r"(^|/)(cmd/[^/]+/main\.go|__main__\.py|bin/)", n)
                                                  for n in low)) or bin_field:
        platforms.add("cli")
    if not platforms and api == set():
        platforms.add("library")
    put("platforms", ",".join(sorted(platforms)) or "none")

    integ = sorted({i for i in INTEGRATIONS if any(i in n.split("/")[-1] or n.startswith("@" + i) or n.startswith(i)
                                                    for n in dep_names) or re.search(r"^\s*" + i + r"_", env, re.M)})
    put("integrations", ",".join(integ) or "none")

    public = "unknown"
    if shutil.which("gh") and git(root, "remote"):
        try:
            r = subprocess.run(["gh", "repo", "view", "--json", "visibility", "-q", ".visibility"], cwd=str(root),
                               capture_output=True, text=True, timeout=20)
            public = {"PUBLIC": "yes", "PRIVATE": "no", "INTERNAL": "no"}.get(r.stdout.strip().upper(), "unknown")
        except (OSError, subprocess.TimeoutExpired):
            pass
    put("public_repo", public, "tool")

    put("audience", "developers" if platforms <= {"cli", "library"} and platforms else
        "public" if public == "yes" else "unknown", "judge")

    sm = "env" if env else "none"
    if re.search(r"vault|doppler|1password|infisical", manifest):  # dependency names only
        sm = "vault"
    if re.search(r"secretmanager|secrets-manager|secretsmanager|keyvault", manifest):
        sm = "cloud-sm"
    put("secrets_mgmt", sm)

    put("size", "small" if len(src) < 200 else "medium" if len(src) < 2000 else "large")
    return out


def line(sig: dict) -> str:
    """The `Signals:` line; a judged value carries `?` until the model confirms it."""
    return "Signals: " + " ".join(f"{k}={v['value']}{'?' if v['by'] == 'judge' else ''}" for k, v in sig.items())


# --- self-test --------------------------------------------------------------------------------------------

def self_test() -> int:
    fails = []
    saved = isolate_git()
    tmp = Path(tempfile.mkdtemp(prefix="ds-detect-"))
    try:
        def w(rel, body=""):
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(body, encoding="utf-8")

        empty = signals(tmp)
        if empty["ui"]["value"] != "none" or empty["tests"]["value"] != "none" or empty["size"]["value"] != "small":
            fails.append(f"empty repo: {line(empty)}")
        w("core/ds_detect.py", Path(__file__).read_text(encoding="utf-8"))  # its regexes and fixtures are not the project's
        own = signals(tmp)
        if own["api"]["value"] != "none" or own["auth"]["value"] != "none":
            fails.append(f"detector matched its own source: api={own['api']['value']} auth={own['auth']['value']}")
        w("package.json", '{"dependencies": {"express": "4", "stripe": "1", "pg": "8"}, "devDependencies": {"vitest": "1"}}')
        w("src/server.ts", "const app = express();\napp.get('/x', h)\n")
        w("src/App.tsx", "export const A = 1\n")
        w("src/models/user.ts", "export type User = { email: string }\n")
        w(".github/workflows/ci.yml", "on: push\n")
        w("Dockerfile", "FROM node\n")
        w(".env.example", "STRIPE_KEY=\nDATABASE_URL=postgres://x\n")
        w("node_modules/x/index.html", "<html>")
        s = signals(tmp)
        want = {"ui": "web", "api": "rest", "db": "postgres", "billing": "stripe", "pii": "yes", "tests": "vitest",
                "ci": "github", "deploy": "docker", "secrets_mgmt": "env"}
        for k, v in want.items():
            if s[k]["value"] != v:
                fails.append(f"{k}: {s[k]['value']} != {v}")
        if "stripe" not in s["integrations"]["value"]:
            fails.append("integrations misses stripe")
        if "pii=yes?" not in line(s):
            fails.append("judged value not marked with ?")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        os.environ.update(saved)
    for f in fails:
        print("  FAIL", f)
    print("ds_detect self-test:", "all checks passed" if not fails else f"{len(fails)} failed")
    return 1 if fails else 0


def main(argv) -> int:
    cmd = argv[0] if argv else ""
    root = argv[1] if len(argv) > 1 else "."
    if cmd == "check":
        print(check_cmd(root), end="")
        return 0
    if cmd == "signals":
        sig = signals(root)
        print(json.dumps(sig, indent=1))
        print(line(sig), file=sys.stderr)
        return 0
    if cmd == "--self-test":
        return self_test()
    print(__doc__)
    return 0 if cmd in ("-h", "--help") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
