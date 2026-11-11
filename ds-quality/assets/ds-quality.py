#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""ds-quality — deterministic, local, no-CI quality gate for AI coding hosts.

Stdlib only (Python 3.8+), identical on macOS, Linux and Windows. No jq, no network.

  ds-quality.py gate                  Claude Code Stop hook: stdin JSON -> stdout JSON (launched by ds-quality-gate.sh)
  ds-quality.py detect [DIR]          print the quality command for DIR; nothing printed = nothing detectable
  ds-quality.py install [--register] [--project DIR] [--dry-run]
                                      copy the hook files into ~/.claude/hooks (or DIR/.claude/hooks), write the default
                                      config if absent; --register merges the Stop hook into settings.json (idempotent,
                                      backed up). Honors CLAUDE_CONFIG_DIR.
  ds-quality.py --self-test           fixture checks (temp repos); exit 0 = green

Resolution per Stop, in priority order:
  1. <root>/.claude/ds-quality.json marker -> its `command` (enabled:false = kill switch; optional `timeout` seconds,
     `cache:false`)
  2. else mode=auto and the repo is under a trusted root (config `roots`, default ~/projects) -> detect()
  3. else / nothing detectable -> inert (exit 0, no output)

A green result is remembered per repo fingerprint (HEAD + working-tree status + file stamps + command): an unchanged
tree is not re-checked on the next Stop. Never edits your code — it blocks so the fix gets made.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WINDOWS = os.name == "nt"
TAIL_CHARS = 4000
DEFAULT_TIMEOUT = 270  # seconds; under the 300 s hook timeout so a slow gate reports instead of being killed
DEFAULT_CONFIG = {"mode": "auto", "roots": ["~/projects"]}
HOOK_FILES = ("ds-quality.py", "ds-quality-gate.sh", "ds-quality-detect.sh")


# --- small helpers ----------------------------------------------------------------------------------------

def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude").expanduser()


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return None


def git(args, cwd) -> str | None:
    try:
        r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=15,
                           encoding="utf-8", errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def norm(p) -> str:
    return os.path.normcase(os.path.realpath(os.path.expandvars(os.path.expanduser(str(p)))))


def find_bash() -> str | None:
    if not WINDOWS:
        return shutil.which("bash") or shutil.which("sh")
    for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)"), os.environ.get("LOCALAPPDATA")):
        if base:
            for sub in ("Git/bin/bash.exe", "Programs/Git/bin/bash.exe"):
                cand = Path(base) / sub
                if cand.is_file():
                    return str(cand)
    found = shutil.which("bash")  # System32\bash.exe is the WSL launcher, not Git Bash
    return found if found and "system32" not in found.lower() else None


def run_shell(cmd: str, cwd: Path, timeout: float):
    """Run `cmd` through a POSIX shell (bash on Windows too). -> (exit_code | None on timeout, combined output)."""
    shell = find_bash()
    argv = [shell, "-c", cmd] if shell else (["cmd", "/c", cmd] if WINDOWS else ["/bin/sh", "-c", cmd])
    kw = {"start_new_session": True} if not WINDOWS else {}
    env = dict(os.environ, DS_QUALITY="1")
    try:
        p = subprocess.Popen(argv, cwd=str(cwd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, **kw)
    except OSError as e:
        return 127, f"cannot start the shell: {e}"
    try:
        out, _ = p.communicate(timeout=timeout)
        return p.returncode, out.decode("utf-8", "replace")
    except subprocess.TimeoutExpired:
        if WINDOWS:
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
        else:
            try:
                os.killpg(p.pid, 9)
            except OSError:
                p.kill()
        out, _ = p.communicate()
        return None, out.decode("utf-8", "replace")


# --- detect -----------------------------------------------------------------------------------------------

def detect(root) -> str:
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
    # no manifest to key off — both stay with the explicit /ds-quality bootstrap, never the silent auto-arm.
    return " && ".join(cmds)


# --- gate -------------------------------------------------------------------------------------------------

def anchor_dir(payload: dict) -> Path | None:
    """The session's project root, not the shell's drifting cwd (CLAUDE_PROJECT_DIR; same-repo worktree -> cwd)."""
    cwd = payload.get("cwd") or "."
    proj = os.environ.get("CLAUDE_PROJECT_DIR")
    anchor = proj or cwd
    if proj and os.path.isdir(cwd):
        a = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], cwd)
        b = git(["rev-parse", "--path-format=absolute", "--git-common-dir"], proj)
        if a and b and norm(a) == norm(b):
            anchor = cwd
    return Path(anchor) if os.path.isdir(anchor) else None


def in_roots(root: Path, roots) -> bool:
    here = norm(root) + os.sep
    return any(here.startswith(norm(r).rstrip("\\/") + os.sep) for r in roots if r)


def fingerprint(root: Path, cmd: str):
    """(git dir, digest) of HEAD + working-tree status + file stamps + command; None outside a git work tree."""
    gitdir = git(["rev-parse", "--path-format=absolute", "--git-dir"], root)
    status = git(["status", "--porcelain=v1", "--untracked-files=normal", "-z"], root)
    if gitdir is None or status is None:
        return None
    h = hashlib.sha256()
    h.update(cmd.encode())
    h.update((git(["rev-parse", "HEAD"], root) or "no-head").encode())
    h.update(status.encode("utf-8", "replace"))
    for entry in status.split("\0"):
        if len(entry) > 3:
            try:
                st = (root / entry[3:]).stat()
                h.update(f"{entry[3:]}:{st.st_size}:{st.st_mtime_ns}".encode())
            except OSError:
                pass
    return Path(gitdir), h.hexdigest()


def gate(payload: dict) -> str | None:
    """-> JSON string to print (block), or None (allow the stop)."""
    if payload.get("stop_hook_active") is True:  # loop guard: already blocked once without progress
        return None
    anchor = anchor_dir(payload)
    if anchor is None:
        return None
    root = Path(git(["rev-parse", "--show-toplevel"], anchor) or anchor)

    cfg = {**DEFAULT_CONFIG, **(load_json(claude_dir() / "ds-quality.config.json") or {})}
    cmd, timeout, cache = "", DEFAULT_TIMEOUT, True
    marker = root / ".claude" / "ds-quality.json"
    if marker.is_file():
        m = load_json(marker) or {}
        if m.get("enabled") is False:  # explicit opt-out wins
            return None
        cmd = m.get("command") or ""
        timeout = float(m.get("timeout") or timeout)
        cache = m.get("cache") is not False
    elif cfg.get("mode") == "auto" and in_roots(root, cfg.get("roots") or DEFAULT_CONFIG["roots"]):
        cmd = detect(root)
    if not cmd:  # nothing to check -> inert
        return None

    fp = fingerprint(root, cmd) if cache else None
    stamp = (fp[0] / "ds-quality.green") if fp else None
    if stamp and stamp.is_file() and stamp.read_text(encoding="utf-8", errors="ignore").strip() == fp[1]:
        return None  # unchanged since the last green run

    code, out = run_shell(cmd, root, timeout)
    if code == 0:
        if stamp:
            try:
                stamp.write_text(fp[1], encoding="utf-8")
            except OSError:
                pass
        return None
    if stamp and stamp.exists():
        try:
            stamp.unlink()
        except OSError:
            pass
    tail = out[-TAIL_CHARS:]
    if code is None:
        head = f"Quality gate TIMED OUT after {int(timeout)}s for: {cmd}"
        tail += f"\n\n(Raise `timeout` in {marker.name} or run the command by hand; an unfinished check is not a pass.)"
    else:
        head = f"Quality gate FAILED (exit {code}) for: {cmd}"
    reason = f"{head}\n\n{tail}\n\nFix the cause — do NOT weaken or skip checks/tests — then finish."
    return json.dumps({"decision": "block", "reason": reason}, ensure_ascii=False)


# --- install ----------------------------------------------------------------------------------------------

def install(argv) -> int:
    register = "--register" in argv
    dry = "--dry-run" in argv
    project = None
    if "--project" in argv:
        project = Path(argv[argv.index("--project") + 1]).expanduser()
    base = (project / ".claude") if project else claude_dir()
    hooks = base / "hooks"
    src = Path(__file__).resolve().parent
    say = print
    for name in HOOK_FILES:
        dst = hooks / name
        if dst.exists() and dst.read_bytes() == (src / name).read_bytes():
            continue
        say(f"{'would copy' if dry else 'copy'}  {name} -> {hooks}")
        if not dry:
            hooks.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src / name, dst)
            dst.chmod(0o755)
    cfg = base / "ds-quality.config.json"
    if not project and not cfg.exists():
        say(f"{'would write' if dry else 'write'}  default config {cfg}")
        if not dry:
            cfg.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
    if register:
        if project:
            cmd = ".claude/hooks/ds-quality-gate.sh"
        elif base == Path.home() / ".claude":
            cmd = "~/.claude/hooks/ds-quality-gate.sh"
        else:
            cmd = (hooks / "ds-quality-gate.sh").as_posix()
        settings = base / "settings.json"
        data = load_json(settings) if settings.exists() else {}
        if data is None:
            say(f"settings.json is not valid JSON: {settings} — not touched")
            return 1
        stop = data.setdefault("hooks", {}).setdefault("Stop", [])
        if any(h.get("command") == cmd for g in stop for h in (g.get("hooks") or [])):
            say("Stop hook already registered")
        else:
            say(f"{'would register' if dry else 'register'}  Stop hook {cmd}")
            if not dry:
                if settings.exists():
                    shutil.copyfile(settings, settings.with_name(f"settings.json.bak.{time.strftime('%Y%m%d%H%M%S')}"))
                stop.append({"hooks": [{"type": "command", "command": cmd, "timeout": 300}]})
                settings.parent.mkdir(parents=True, exist_ok=True)
                settings.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


# --- self-test --------------------------------------------------------------------------------------------

def self_test() -> int:
    failures: list[str] = []

    def check(name, cond):
        print(f"  {'ok  ' if cond else 'FAIL'} {name}")
        if not cond:
            failures.append(name)

    def sh(cmd, cwd):
        subprocess.run(cmd, cwd=cwd, check=True, capture_output=True)

    keep = {k: os.environ.get(k) for k in ("CLAUDE_CONFIG_DIR", "CLAUDE_PROJECT_DIR")}
    tmp = Path(tempfile.mkdtemp(prefix="ds-quality-test-"))
    try:
        os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "cfg")
        (tmp / "cfg").mkdir()
        repo = tmp / "trusted" / "repo"
        repo.mkdir(parents=True)
        for c in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "t"]):
            sh(c, repo)
        os.environ["CLAUDE_PROJECT_DIR"] = str(repo)
        payload = {"cwd": str(repo)}
        (tmp / "cfg" / "ds-quality.config.json").write_text(json.dumps({"mode": "auto", "roots": [str(tmp / "trusted")]}))

        # detect
        check("detect: empty repo -> nothing", detect(repo) == "")
        (repo / "go.mod").write_text("module x\n")
        d = detect(repo)
        check("detect: go.mod -> gofmt/vet/build/test", all(s in d for s in ("gofmt", "go vet", "go build", "go test")))
        (repo / "go.mod").unlink()
        (repo / "package.json").write_text('{"scripts":{"test":"jest"}}')
        check("detect: package.json test script -> npm test", detect(repo) == "npm test")
        (repo / "package.json").write_text('{"scripts":{"quality":"x","test":"jest"}}')
        check("detect: package.json quality script wins", detect(repo) == "npm run quality")
        (repo / "package.json").unlink()
        (repo / "pubspec.yaml").write_text("flutter:\n")
        check("detect: flutter without tests adds no test run", "flutter test" not in detect(repo))
        (repo / "test").mkdir()
        check("detect: flutter test dir adds test run", "flutter test --exclude-tags integration" in detect(repo))
        (repo / "pubspec.yaml").unlink()
        (repo / "test").rmdir()

        # gate
        check("gate: nothing detectable -> inert", gate(payload) is None)
        marker = repo / ".claude" / "ds-quality.json"
        marker.parent.mkdir()
        marker.write_text(json.dumps({"command": "exit 3"}))
        out = gate(payload)
        blocked = json.loads(out) if out else {}
        check("gate: failing command -> block JSON", blocked.get("decision") == "block" and "exit 3" in blocked.get("reason", ""))
        check("gate: loop guard -> allow", gate({**payload, "stop_hook_active": True}) is None)
        marker.write_text(json.dumps({"command": "exit 3", "enabled": False}))
        check("gate: enabled:false is a real kill switch", gate(payload) is None)
        marker.write_text(json.dumps({"command": "echo ok"}))
        check("gate: passing command -> allow", gate(payload) is None)
        green = list((repo / ".git").glob("ds-quality.green"))
        check("gate: green fingerprint stored", len(green) == 1)
        marker.write_text(json.dumps({"command": "echo ok", "timeout": 1}))
        check("gate: changed command invalidates the cache", gate(payload) is None)
        marker.write_text(json.dumps({"command": "sleep 5", "timeout": 1}))
        out = gate(payload)
        check("gate: timeout -> block (unfinished is not a pass)", bool(out) and "TIMED OUT" in json.loads(out)["reason"])
        marker.unlink()
        outside = tmp / "elsewhere"
        outside.mkdir()
        sh(["git", "init", "-q"], outside)
        (outside / "go.mod").write_text("module y\n")
        os.environ["CLAUDE_PROJECT_DIR"] = str(outside)
        check("gate: repo outside trusted roots -> inert", gate({"cwd": str(outside)}) is None)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("ds-quality self-test:", "FAILED " + ", ".join(failures) if failures else "all checks passed")
    return 1 if failures else 0


def main(argv) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    cmd = argv[0] if argv else ""
    if cmd == "gate":
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except ValueError:
            payload = {}
        out = gate(payload if isinstance(payload, dict) else {})
        if out:
            print(out)
        return 0
    if cmd == "detect":
        print(detect(argv[1] if len(argv) > 1 else "."), end="")
        return 0
    if cmd == "install":
        return install(argv[1:])
    if cmd == "--self-test":
        return self_test()
    print(__doc__)
    return 0 if cmd in ("", "-h", "--help") else 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
