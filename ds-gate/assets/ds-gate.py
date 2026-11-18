#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""ds-gate — deterministic, local, no-CI quality gate for AI coding hosts.

Stdlib only (Python 3.8+), identical on macOS, Linux and Windows. No jq, no network.

  ds-gate.py gate [--exit2]        before-done hook: stdin JSON. Default (Claude Code / Codex Stop): block = stdout
                                      {"decision":"block","reason":...}. --exit2 (Gemini AfterAgent): block = reason on
                                      stderr + exit 2. Allow = no output, exit 0.
  ds-gate.py run [--staged] [DIR]  run DIR's quality command now (marker, else detected); exit code = the command's.
                                      Used by git pre-commit (--staged), Aider lint-cmd/test-cmd, or by hand.
  ds-gate.py detect [DIR]          print the quality command for DIR; nothing printed = nothing detectable
  ds-gate.py install [--register] [--dry-run]
                                      copy this file into ~/.claude/hooks, write the default config if absent, remove
                                      files of older versions; --register merges the Stop hook into settings.json
                                      (idempotent, backed up, replaces older ds-gate entries). Honors CLAUDE_CONFIG_DIR.
  ds-gate.py --self-test           fixture checks (temp repos); exit 0 = green

Resolution per Stop, in priority order:
  1. <root>/.claude/ds-gate.json marker -> its `command` (enabled:false = kill switch; optional `timeout` seconds,
     `cache:false`)
  2. else mode=auto and the repo is under a trusted root (config `roots`, default ~/projects) -> detect()
  3. else / nothing detectable -> inert (exit 0, no output)

Auto-fix: a marker `fix` command (safe fixers only, e.g. "ruff format {files} && ruff check --fix {files}") runs
before the check, on the changed files ({files} = their quoted paths; without {files} it runs as written). With
--staged only fully staged files are fixed and re-staged; a file that also has unstaged edits is never touched, so no
unstaged work can slip into the commit. Fixer exit codes are ignored — the check that follows decides.

A green result is remembered per repo fingerprint (HEAD + working-tree status + file stamps + command): an unchanged
tree is not re-checked on the next Stop. Beyond the marker's `fix`, it never edits code — it blocks so the fix gets made.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shlex
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# The quality-command detector is shared with ds-audit (core/ds_detect.py); the installed hook carries a copy beside it.
_HERE = Path(__file__).resolve().parent
_CORE = next((d for d in (_HERE, _HERE.parent / "core", _HERE.parent.parent / "core") if (d / "ds_detect.py").is_file()), _HERE)
sys.path.insert(0, str(_CORE))
from ds_detect import TEXT, check_cmd as detect, isolate_git, shell_argv  # noqa: E402

WINDOWS = os.name == "nt"
TAIL_CHARS = 4000
DEFAULT_TIMEOUT = 270  # seconds; under the 300 s hook timeout so a slow gate reports instead of being killed
DEFAULT_CONFIG = {"mode": "auto", "roots": ["~/projects"]}
HOOK_FILES = ("ds-gate.py", "ds_detect.py")
LEGACY_FILES = ("ds-quality-gate.sh", "ds-quality-detect.sh", "ds-quality.py")  # earlier names of this hook
OLD_MARKER, OLD_CONFIG = "ds-quality.json", "ds-quality.config.json"  # read when the new name is absent


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
        r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, **TEXT, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def norm(p) -> str:
    return os.path.normcase(os.path.realpath(os.path.expandvars(os.path.expanduser(str(p)))))


def run_shell(cmd: str, cwd: Path, timeout: float):
    """Run `cmd` through a POSIX shell (bash on Windows too). -> (exit_code | None on timeout, combined output)."""
    argv = shell_argv(cmd)
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


def marker_path(root: Path) -> Path:
    """The repo's marker: .claude/ds-gate.json, else the pre-rename .claude/ds-quality.json when only that exists."""
    new, old = root / ".claude" / "ds-gate.json", root / ".claude" / OLD_MARKER
    return old if old.is_file() and not new.is_file() else new


def config_path(base: Path) -> Path:
    new, old = base / "ds-gate.config.json", base / OLD_CONFIG
    return old if old.is_file() and not new.is_file() else new


def resolve(root: Path, auto: bool):
    """-> (command, timeout, cache) for root; command "" when disabled or nothing applies."""
    marker = marker_path(root)
    if marker.is_file():
        m = load_json(marker) or {}
        if m.get("enabled") is False:  # explicit opt-out wins
            return "", DEFAULT_TIMEOUT, True
        return m.get("command") or "", float(m.get("timeout") or DEFAULT_TIMEOUT), m.get("cache") is not False
    return (detect(root) if auto else ""), DEFAULT_TIMEOUT, True


def lines0(out) -> list:
    return [x for x in (out or "").split("\0") if x]


def changed_files(root: Path, staged: bool) -> tuple:
    """-> (files to fix, files skipped). staged: fully staged files only; else modified + untracked."""
    if staged:
        idx = set(lines0(git(["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMR"], root)))
        partial = idx & set(lines0(git(["diff", "--name-only", "-z"], root)))
        return sorted(idx - partial), sorted(partial)
    out = git(["status", "--porcelain", "-z", "-uall"], root) or ""
    files, entries = [], out.split("\0")
    i = 0
    while i < len(entries):
        e = entries[i]
        if len(e) > 3 and e[0] != "D" and e[1] != "D":
            files.append(e[3:])
        i += 2 if e[:1] in ("R", "C") else 1  # a rename/copy is followed by its source path
    return sorted(f for f in files if (root / f).is_file()), []


def auto_fix(root: Path, staged: bool, timeout: float) -> None:
    m = load_json(marker_path(root)) or {}
    fix = m.get("fix") if m.get("enabled") is not False else None
    if not fix:
        return
    files, skipped = changed_files(root, staged)
    for f in skipped:
        print(f"ds-gate: not auto-fixing {f} (it also has unstaged edits)", file=sys.stderr)
    if "{files}" in fix:
        if not files:
            return
        fix = fix.replace("{files}", " ".join(shlex.quote(f) for f in files))
    elif staged:
        print("ds-gate: fix has no {files}; skipped at commit time so unstaged files stay untouched", file=sys.stderr)
        return
    print(f"ds-gate: fix: {fix}", file=sys.stderr)
    run_shell(fix, root, timeout)
    if staged and files:
        git(["add", "--", *files], root)


def run(argv) -> int:
    staged = "--staged" in argv
    argv = [a for a in argv if a != "--staged"]
    start = Path(argv[0]) if argv else Path(".")
    root = Path(git(["rev-parse", "--show-toplevel"], start) or start)
    cmd, timeout, _ = resolve(root, auto=True)
    auto_fix(root, staged, timeout)
    if not cmd:
        print(f"ds-gate: no quality command for {root} (add .claude/ds-gate.json)", file=sys.stderr)
        return 0
    print(f"ds-gate: {cmd}", file=sys.stderr)
    code, out = run_shell(cmd, root, timeout)
    sys.stdout.write(out)
    if code is None:
        print(f"ds-gate: TIMED OUT after {int(timeout)}s — an unfinished check is not a pass", file=sys.stderr)
        return 1
    return code


def gate(payload: dict) -> str | None:
    """-> JSON string to print (block), or None (allow the stop)."""
    if payload.get("stop_hook_active") is True:  # loop guard: already blocked once without progress
        return None
    anchor = anchor_dir(payload)
    if anchor is None:
        return None
    root = Path(git(["rev-parse", "--show-toplevel"], anchor) or anchor)

    cfg = {**DEFAULT_CONFIG, **(load_json(config_path(claude_dir())) or {})}
    auto = cfg.get("mode") == "auto" and in_roots(root, cfg.get("roots") or DEFAULT_CONFIG["roots"])
    cmd, timeout, cache = resolve(root, auto)
    marker = marker_path(root)
    if not cmd:  # nothing to check -> inert
        return None

    fp = fingerprint(root, cmd) if cache else None
    stamp = (fp[0] / "ds-gate.green") if fp else None
    if stamp and stamp.is_file() and stamp.read_text(encoding="utf-8", errors="ignore").strip() == fp[1]:
        return None  # unchanged since the last green run
    if (load_json(marker) or {}).get("fix"):
        auto_fix(root, False, timeout)
        fp = fingerprint(root, cmd) if cache else None  # the fixers changed the tree

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

def hook_command(hooks: Path) -> str:
    """Absolute interpreter + script: no shell launcher, no PATH lookup, same on every OS."""
    return f'"{Path(sys.executable).as_posix()}" "{(hooks / "ds-gate.py").as_posix()}" gate'


def install(argv) -> int:
    register = "--register" in argv
    dry = "--dry-run" in argv
    base = claude_dir()
    hooks = base / "hooks"
    say = print
    for name in HOOK_FILES:
        src = (_HERE if name == "ds-gate.py" else _CORE) / name
        dst = hooks / name
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            continue
        say(f"{'would copy' if dry else 'copy'}  {name} -> {hooks}")
        if not dry:
            hooks.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            dst.chmod(0o755)
    for name in LEGACY_FILES:
        if (hooks / name).exists():
            say(f"{'would remove' if dry else 'remove'}  old {name}")
            if not dry:
                (hooks / name).unlink()
    cfg = base / "ds-gate.config.json"
    if (base / OLD_CONFIG).is_file() and not cfg.exists():
        say(f"{'would rename' if dry else 'rename'}  {OLD_CONFIG} -> {cfg.name}")
        if not dry:
            (base / OLD_CONFIG).rename(cfg)
    if not cfg.exists():
        say(f"{'would write' if dry else 'write'}  default config {cfg}")
        if not dry:
            cfg.write_text(json.dumps(DEFAULT_CONFIG, indent=2) + "\n", encoding="utf-8")
    if not register:
        return 0
    cmd = hook_command(hooks)
    settings = base / "settings.json"
    data = load_json(settings) if settings.exists() else {}
    if data is None:
        say(f"settings.json is not valid JSON: {settings} — not touched")
        return 1
    stop = data.setdefault("hooks", {}).setdefault("Stop", [])
    ours = lambda h: any(k in (h.get("command") or "") for k in ("ds-quality-gate.sh", "ds-quality.py", "ds-gate.py"))
    current = [h for g in stop for h in (g.get("hooks") or []) if ours(h)]
    if len(current) == 1 and current[0].get("command") == cmd:
        say("Stop hook already registered")
        return 0
    for g in stop:
        g["hooks"] = [h for h in (g.get("hooks") or []) if not ours(h)]
    stop[:] = [g for g in stop if g.get("hooks")]
    stop.append({"hooks": [{"type": "command", "command": cmd, "timeout": 300}]})
    say(f"{'would register' if dry else 'register'}  Stop hook {cmd}" + (f" (replacing {len(current)} older)" if current else ""))
    if not dry:
        if settings.exists():
            shutil.copyfile(settings, settings.with_name(f"settings.json.bak.{time.strftime('%Y%m%d%H%M%S')}"))
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
    keep.update(isolate_git())
    tmp = Path(tempfile.mkdtemp(prefix="ds-gate-test-"))
    try:
        os.environ["CLAUDE_CONFIG_DIR"] = str(tmp / "cfg")
        (tmp / "cfg").mkdir()
        repo = tmp / "trusted" / "repo"
        repo.mkdir(parents=True)
        for c in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "t"]):
            sh(c, repo)
        os.environ["CLAUDE_PROJECT_DIR"] = str(repo)
        payload = {"cwd": str(repo)}
        (tmp / "cfg" / "ds-gate.config.json").write_text(json.dumps({"mode": "auto", "roots": [str(tmp / "trusted")]}))

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
        marker = repo / ".claude" / "ds-gate.json"
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
        green = list((repo / ".git").glob("ds-gate.green"))
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

        # run
        marker.write_text(json.dumps({"command": "exit 4"}))
        check("run: exit code is the command's", run([str(repo)]) == 4)
        marker.write_text(json.dumps({"command": "exit 0"}))
        check("run: green -> 0", run([str(repo)]) == 0)
        old = marker.with_name(OLD_MARKER)
        marker.rename(old)
        check("pre-rename marker still read", resolve(repo, False)[0] == "exit 0")
        old.rename(marker)
        marker.write_text(json.dumps({"command": "exit 5", "cache": False}))
        r = subprocess.run([sys.executable, __file__, "gate", "--exit2"], input=json.dumps({"cwd": str(repo)}),
                           capture_output=True, **TEXT, env=dict(os.environ, CLAUDE_PROJECT_DIR=str(repo)))
        check("gate --exit2: block -> exit 2 + reason on stderr", r.returncode == 2 and "exit 5" in r.stderr and not r.stdout)

        # auto-fix at commit time: fully staged files fixed and re-staged; partly staged and unstaged files untouched
        fx = tmp / "trusted" / "fixrepo"
        fx.mkdir()
        for c in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"], ["git", "config", "user.name", "t"]):
            sh(c, fx)
        for n in ("a.txt", "b.txt", "c.txt"):
            (fx / n).write_text("v1\n")
        sh(["git", "add", "."], fx)
        sh(["git", "commit", "-qm", "init"], fx)
        (tmp / "fixer.py").write_text("import sys\nfor f in sys.argv[1:]:\n    open(f, 'a').write('FIXED\\n')\n")
        (fx / ".claude").mkdir()
        (fx / ".claude" / "ds-gate.json").write_text(json.dumps(
            {"command": "exit 0", "fix": f'"{Path(sys.executable).as_posix()}" "{(tmp / "fixer.py").as_posix()}" {{files}}'}))
        (fx / "a.txt").write_text("v2\n")                      # fully staged
        (fx / "b.txt").write_text("v2\n")
        sh(["git", "add", "a.txt", "b.txt"], fx)
        (fx / "b.txt").write_text("v2\nunstaged\n")           # partly staged
        (fx / "c.txt").write_text("v2\n")                      # unstaged only
        with contextlib.redirect_stderr(io.StringIO()):
            rc = run(["--staged", str(fx)])
        staged_a = subprocess.run(["git", "show", ":a.txt"], cwd=fx, capture_output=True, **TEXT).stdout
        staged_b = subprocess.run(["git", "show", ":b.txt"], cwd=fx, capture_output=True, **TEXT).stdout
        check("fix --staged: fully staged file fixed and re-staged", rc == 0 and staged_a == "v2\nFIXED\n")
        check("fix --staged: partly staged file untouched", staged_b == "v2\n" and (fx / "b.txt").read_text() == "v2\nunstaged\n")
        check("fix --staged: unstaged file untouched", (fx / "c.txt").read_text() == "v2\n")

        # install: legacy launcher + legacy Stop entry replaced, idempotent
        hooks = tmp / "cfg" / "hooks"
        hooks.mkdir()
        (hooks / "ds-quality-gate.sh").write_text("old")
        settings = tmp / "cfg" / "settings.json"
        settings.write_text(json.dumps({"hooks": {"Stop": [
            {"hooks": [{"type": "command", "command": "~/.claude/hooks/ds-quality-gate.sh"}]},
            {"hooks": [{"type": "command", "command": "python ~/.claude/hooks/ds-quality.py gate"}]},
            {"hooks": [{"type": "command", "command": "other-hook"}]}]}}))
        with contextlib.redirect_stdout(io.StringIO()):
            install(["--register"])
            install(["--register"])
        st = json.loads(settings.read_text())["hooks"]["Stop"]
        cmds = [h["command"] for g in st for h in g["hooks"]]
        check("install: legacy launcher removed", not (hooks / "ds-quality-gate.sh").exists())
        check("install: one ds-gate entry, others kept", cmds.count(hook_command(hooks)) == 1 and "other-hook" in cmds and len(cmds) == 2)
    finally:
        for k, v in keep.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(tmp, ignore_errors=True)
    print("ds-gate self-test:", "FAILED " + ", ".join(failures) if failures else "all checks passed")
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
        if out and "--exit2" in argv:
            print(json.loads(out)["reason"], file=sys.stderr)
            return 2
        if out:
            print(out)
        return 0
    if cmd == "run":
        return run(argv[1:])
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
