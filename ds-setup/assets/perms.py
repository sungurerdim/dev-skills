#!/usr/bin/env python3
"""ds-setup step 6 for Claude Code, mechanically: merge the permission profile into the global settings.

  perms.py [--dry-run] [--hook]   merge allow / ask / deny into ~/.claude/settings.json (honors CLAUDE_CONFIG_DIR):
                                  additions only, timestamped backup first, every user entry kept; an entry the user
                                  already placed in another list is skipped and reported. --hook also installs
                                  rc_deny.py as a PreToolUse(Bash) hook. Prints JSON: added, skipped, backup.
  perms.py --self-test            exit 0 = merge is additive, idempotent, conflict-safe and backed up

The lists below are the Claude Code instantiation of the RC classes in references/permissions.md (that file holds
the intent and the reasons; this file holds the exact entries). Each Bash entry is mirrored for wrappers Claude Code
does not strip: `rtk` for every list, and `rtk proxy`, `direnv exec`, `mise exec`, `devbox run` for ask and deny.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ALLOW_TOOLS = ["Read", "Glob", "Grep", "WebSearch", "Edit(./**)"]
ALLOW_BASH = [
    # inspect
    "ls", "cat", "head", "tail", "wc", "file", "stat", "du", "df", "which", "type", "tree", "rg", "fd", "jq", "diff",
    "sort", "uniq", "cut", "pwd", "echo", "printf", "date", "basename", "dirname", "realpath",
    # git, local and reversible
    "git status", "git log", "git diff", "git show", "git blame", "git branch", "git rev-parse", "git ls-files",
    "git grep", "git fetch", "git add", "git commit", "git stash list", "git stash show", "git stash push",
    "git stash create", "git switch", "git checkout -b", "git tag", "git worktree list", "git worktree add", "git merge --ff-only", "git merge-base", "git merge-tree", "git remote -v", "git config --get",
    # build, test, check (workspace autonomy)
    "npm test", "npm run", "npm ls", "pnpm test", "pnpm run", "yarn test", "yarn run", "bun test", "bun run",
    "npx prettier", "npx eslint", "npx tsc", "npx biome", "npx vitest", "npx jest",
    "pytest", "python -m pytest", "python3 -m pytest", "ruff", "black", "mypy", "pyright", "uv run", "pip list",
    "cargo build", "cargo test", "cargo check", "cargo clippy", "cargo fmt", "cargo tree",
    "go build", "go test", "go vet", "go list", "gofmt", "make", "dart format", "dart analyze", "flutter analyze",
    "flutter test", "dotnet build", "dotnet test", "dotnet format", "./gradlew", "mvn test", "swift build", "swift test",
    "shellcheck", "shfmt", "typos", "gitleaks", "osv-scanner", "actionlint", "hadolint", "zizmor",
    # rig tools, read and status forms
    "rtk gain", "gh pr view", "gh pr list", "gh pr diff", "gh pr checks", "gh issue view", "gh issue list",
    "gh run view", "gh run list", "gh repo view",
]
ASK_TOOLS = ["WebFetch"]
ASK_BASH = [
    "git push", "git reset --hard", "git stash drop", "git stash clear", "git worktree remove", "dd", "git checkout --", "git restore", "git clean", "git rebase", "git pull",
    "npm publish", "cargo publish", "twine upload", "gem push", "docker push", "gh release create", "gh pr create",
    "gh pr merge", "gh issue create", "gh api", "npm install", "npm i", "pnpm add", "yarn add", "pip install",
    "uv add", "uv pip install", "cargo add", "cargo install", "go install", "brew install", "apt install",
    "winget install", "scoop install", "claude mcp add", "chmod +x",
]
DENY_TOOLS = [
    "Read(~/.ssh/**)", "Read(~/.gnupg/**)", "Read(~/.aws/**)", "Read(~/.config/gcloud/**)", "Read(~/.kube/**)",
    "Read(~/.docker/config.json)", "Read(~/.netrc)", "Edit(~/.claude/settings.json)", "Edit(~/.claude/hooks/**)",
]
DENY_BASH = [
    "rm -rf /", "rm -rf ~", "rm -rf $HOME", "sudo", "su", "doas", "mkfs", "fdisk", "parted", "diskutil eraseDisk",
    "shred", "git push --force", "git push -f", "git push --force-with-lease", "git filter-branch", "git filter-repo",
    "git remote remove", "git branch -D main", "git branch -D master", "terraform destroy", "kubectl delete", "docker system prune", "aws s3 rb", "redis-cli FLUSHALL",
    "crontab -e", "crontab -r", "launchctl load", "systemctl enable", "security dump-keychain", "gpg --export-secret-keys",
    "npx -y", "Remove-Item -Recurse -Force", "format", "diskpart", "bcdedit", "reg add", "schtasks /create",
    "Add-MpPreference",
]
WRAP_ALL = ["rtk"]
WRAP_GUARD = ["rtk proxy", "direnv exec *", "mise exec * --", "devbox run"]


def bash(cmd: str) -> str:
    """`Bash(cmd *)` matches `cmd` alone and `cmd` with arguments, not `cmdx` (code.claude.com/docs/en/permissions)."""
    return f"Bash({cmd} *)"


def entries(cmds, wrappers) -> list:
    out = []
    for c in cmds:
        out.append(bash(c))
        out.extend(bash(f"{w} {c}") for w in wrappers)
    return out


def profile() -> dict:
    return {"allow": ALLOW_TOOLS + entries(ALLOW_BASH, WRAP_ALL),
            "ask": ASK_TOOLS + entries(ASK_BASH, WRAP_ALL + WRAP_GUARD),
            "deny": DENY_TOOLS + entries(DENY_BASH, WRAP_ALL + WRAP_GUARD)}


def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def merge(data: dict, prof: dict) -> tuple:
    perms = data.setdefault("permissions", {})
    have = {k: list(perms.get(k) or []) for k in ("allow", "ask", "deny")}
    owner = {e: k for k, v in have.items() for e in v}
    added, skipped = {k: [] for k in have}, []
    for k in ("deny", "ask", "allow"):
        for e in prof[k]:
            if e in owner:
                if owner[e] != k:
                    skipped.append({"entry": e, "wanted": k, "user_has": owner[e]})
                continue
            have[k].append(e)
            owner[e] = k
            added[k].append(e)
    for k, v in have.items():
        if v:
            perms[k] = v
    return added, skipped


def add_hook(data: dict, cfg: Path, dry: bool) -> bool:
    src = Path(__file__).resolve().parent / "rc_deny.py"
    dst = cfg / "hooks" / "rc_deny.py"
    cmd = f'"{Path(sys.executable).as_posix()}" "{dst.as_posix()}" --claude-hook'
    pre = data.setdefault("hooks", {}).setdefault("PreToolUse", [])
    if any("rc_deny.py" in (h.get("command") or "") for g in pre for h in (g.get("hooks") or [])):
        return False
    if not dry:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    pre.append({"matcher": "Bash", "hooks": [{"type": "command", "command": cmd}]})
    return True


def apply(argv) -> dict:
    dry, hook = "--dry-run" in argv, "--hook" in argv
    cfg = claude_dir()
    settings = cfg / "settings.json"
    raw = settings.read_text(encoding="utf-8") if settings.exists() else "{}"
    data = json.loads(raw)  # invalid JSON raises: never overwrite a file we cannot read
    added, skipped = merge(data, profile())
    hooked = add_hook(data, cfg, dry) if hook else False
    changed = any(added.values()) or hooked
    backup = None
    if changed and not dry:
        cfg.mkdir(parents=True, exist_ok=True)
        if settings.exists():
            backup = settings.with_name(f"settings.json.bak.{time.strftime('%Y%m%d%H%M%S')}")
            shutil.copyfile(settings, backup)
        tmp = settings.with_name("settings.json.tmp")
        tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        json.loads(tmp.read_text(encoding="utf-8"))
        os.replace(tmp, settings)
    return {"settings": str(settings), "dryRun": dry, "added": {k: len(v) for k, v in added.items()},
            "hook": hooked, "skipped": skipped, "backup": str(backup) if backup else None}


def self_test() -> int:
    fails = []
    tmp = Path(tempfile.mkdtemp(prefix="ds-setup-perms-"))
    keep = os.environ.get("CLAUDE_CONFIG_DIR")
    os.environ["CLAUDE_CONFIG_DIR"] = str(tmp)
    try:
        user = {"permissions": {"allow": ["Bash(git push *)", "Bash(custom *)"], "deny": ["Bash(ls *)"]},
                "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "keep-me"}]}]}, "model": "x"}
        (tmp / "settings.json").write_text(json.dumps(user))
        r1 = apply(["--hook"])
        after = json.loads((tmp / "settings.json").read_text())
        p = after["permissions"]
        check = lambda name, ok: None if ok else fails.append(name)
        check("user entries kept", {"Bash(git push *)", "Bash(custom *)"} <= set(p["allow"]) and "Bash(ls *)" in p["deny"])
        check("conflict skipped, not moved", "Bash(git push *)" not in p["ask"] and "Bash(ls *)" not in p["allow"]
              and {s["entry"] for s in r1["skipped"]} >= {"Bash(git push *)", "Bash(ls *)"})
        check("profile added", "Bash(sudo *)" in p["deny"] and "Bash(rtk git push *)" in p["ask"]
              and "Bash(direnv exec * git push --force *)" in p["deny"] and "Edit(./**)" in p["allow"])
        check("other settings kept", after["model"] == "x" and after["hooks"]["Stop"][0]["hooks"][0]["command"] == "keep-me")
        check("hook installed", r1["hook"] and (tmp / "hooks" / "rc_deny.py").is_file())
        check("backup written", r1["backup"] and json.loads(Path(r1["backup"]).read_text()) == user)
        r2 = apply(["--hook"])
        check("idempotent", not any(r2["added"].values()) and not r2["hook"] and r2["backup"] is None)
        check("no duplicates", all(len(v) == len(set(v)) for v in p.values()))
        (tmp / "settings.json").write_text("{broken")
        try:
            apply([])
            fails.append("invalid JSON must not be overwritten")
        except ValueError:
            check("invalid JSON left untouched", (tmp / "settings.json").read_text() == "{broken")
    finally:
        if keep is None:
            os.environ.pop("CLAUDE_CONFIG_DIR", None)
        else:
            os.environ["CLAUDE_CONFIG_DIR"] = keep
        shutil.rmtree(tmp, ignore_errors=True)
    print("perms self-test:", "FAILED " + ", ".join(fails) if fails else "all checks passed")
    return 1 if fails else 0


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        sys.exit(self_test())
    print(json.dumps(apply(sys.argv[1:]), indent=2))
