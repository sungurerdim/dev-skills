#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""dev-skills installer — Python 3.8+ stdlib only; same on macOS, Linux and Windows.

  python3 install.py                     install or update into ~/.claude/skills (Claude Code; OpenCode reads it too)
  python3 install.py --dir DIR           any Agent Skills directory (e.g. ~/.codex/skills, .agents/skills)
  python3 install.py --skills a,b        only these skills; core/ always ships with them
  python3 install.py --check             report drift between this checkout and the installed copy; changes nothing
  python3 install.py --uninstall         remove everything dev-skills installed into DIR
  python3 install.py --dry-run           print what would change
  python3 install.py --self-test         install, refresh, check and uninstall in a temporary directory

Every install is a clean replace: everything the previous version installed (from its stamp), every skill
that earlier versions shipped, and the old ds-quality hook files are removed first, so no old file can
shadow a new one. Only paths dev-skills owns are touched; any other skill in DIR is left alone.
"""
from __future__ import annotations

import filecmp
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
STAMP = ".dev-skills.json"
OLD_STAMP = ".dev-skills-version"
# every skill name any earlier dev-skills release installed
LEGACY_SKILLS = (
    "ds-backend ds-benchmark ds-blueprint ds-brief ds-build ds-commit ds-compliance ds-debug ds-deploy ds-deps "
    "ds-devops ds-docs ds-fix ds-freeze ds-frontend ds-init ds-issue ds-launch ds-mobile ds-pipeline ds-pr "
    "ds-productize ds-quality ds-release ds-repo ds-review ds-rig ds-ship ds-simplify ds-solve ds-test ds-tune"
).split()
AGENTS = ("ds-research-agent.md",)
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")


def version() -> str:
    data = json.loads((REPO / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    return data["version"]


def repo_skills() -> list:
    return sorted(p.name for p in REPO.glob("ds-*") if (p / "SKILL.md").is_file())


def agents_dir(skills_dir: Path):
    """Shared agents ship only for Claude Code, beside its skills directory."""
    return skills_dir.parent / "agents" if skills_dir.parent.name == ".claude" else None


def owned(skills_dir: Path) -> set:
    """Every path a previous dev-skills install may have left in skills_dir (and its agents dir)."""
    paths = {skills_dir / "core", skills_dir / STAMP, skills_dir / OLD_STAMP}
    paths |= {skills_dir / s for s in LEGACY_SKILLS + repo_skills()}  # current names too: 2.x shipped a ds-research
    stamp = skills_dir / STAMP
    if stamp.is_file():
        try:
            paths |= {skills_dir / p for p in json.loads(stamp.read_text(encoding="utf-8")).get("paths", [])}
        except ValueError:
            pass
    ad = agents_dir(skills_dir)
    if ad:
        paths |= {ad / a for a in AGENTS}
    return {p for p in paths if p.exists() or p.is_symlink()}


def remove(p: Path, dry: bool):
    print(f"{'would remove' if dry else 'remove'}  {p}")
    if not dry:
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p)
        else:
            p.unlink()


HOOK_FILES = (("ds-gate.py", "ds-gate/assets/ds-gate.py"), ("ds_detect.py", "core/ds_detect.py"))


def migrate_hooks(skills_dir: Path, dry: bool):
    """Keep an installed ds-gate Stop hook in step with the skill: re-register a pre-3.0 ds-quality hook as ds-gate, and
    refresh the hook's files (ds-gate.py and the ds_detect.py it imports) whenever a ds-gate hook is installed."""
    hooks = skills_dir.parent / "hooks"
    old = [n for n in ("ds-quality-gate.sh", "ds-quality.py") if (hooks / n).exists()]
    current = (hooks / "ds-gate.py").exists()
    if skills_dir.parent.name == ".claude" and (old or current) and (skills_dir / "ds-gate").is_dir():
        args = [sys.executable, str(skills_dir / "ds-gate" / "assets" / "ds-gate.py"), "install"] + (["--register"] * bool(old))
        why = "replaces the old ds-quality hook" if old else "refreshes the installed hook"
        print(f"{'would run' if dry else 'run'}  {' '.join(args)}  ({why})")
        if not dry:
            env = dict(os.environ, CLAUDE_CONFIG_DIR=str(skills_dir.parent))
            subprocess.run(args, check=False, env=env)


def install(skills_dir: Path, skills: list, dry: bool) -> int:
    for p in sorted(owned(skills_dir)):
        remove(p, dry)
    paths = []
    for name in skills + ["core"]:
        print(f"{'would copy' if dry else 'copy'}  {name} -> {skills_dir / name}")
        if not dry:
            shutil.copytree(REPO / name, skills_dir / name, ignore=IGNORE)
        paths.append(name)
    ad = agents_dir(skills_dir)
    if ad and "ds-research" in skills:
        for a in AGENTS:
            print(f"{'would copy' if dry else 'copy'}  agents/{a} -> {ad}")
            if not dry:
                ad.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / "agents" / a, ad / a)
    if not dry:
        (skills_dir / STAMP).write_text(json.dumps({"version": version(), "skills": skills, "paths": paths}, indent=2) + "\n",
                                        encoding="utf-8")
    migrate_hooks(skills_dir, dry)
    print(f"dev-skills {version()}: {len(skills)} skills {'would be ' if dry else ''}installed in {skills_dir}")
    return 0


def check(skills_dir: Path) -> int:
    stamp = skills_dir / STAMP
    if not stamp.is_file():
        print(f"not installed in {skills_dir} (no {STAMP})")
        return 1
    data = json.loads(stamp.read_text(encoding="utf-8"))
    drift = [] if data.get("version") == version() else [f"version {data.get('version')} installed, {version()} here"]
    for name in data.get("skills", []) + ["core"]:
        cmp = filecmp.dircmp(REPO / name, skills_dir / name, ignore=["__pycache__"])
        stack = [(cmp, name)]
        while stack:
            c, rel = stack.pop()
            drift += [f"{rel}/{f}: differs" for f in c.diff_files]
            drift += [f"{rel}/{f}: missing in install" for f in c.left_only]
            drift += [f"{rel}/{f}: not in this checkout" for f in c.right_only]
            stack += [(sub, f"{rel}/{n}") for n, sub in c.subdirs.items()]
    hooks = skills_dir.parent / "hooks"
    if (hooks / "ds-gate.py").exists():
        for name, src in HOOK_FILES:
            if not (hooks / name).exists():
                drift.append(f"hooks/{name}: missing (the ds-gate hook imports it)")
            elif not filecmp.cmp(REPO / src, hooks / name, shallow=False):
                drift.append(f"hooks/{name}: differs from {src}")
    for line in drift:
        print("DRIFT", line)
    print(f"{len(drift)} drift item(s) in {skills_dir}")
    return 1 if drift else 0


def self_test() -> int:
    """Dry run, install, hook refresh, drift check and uninstall in a temporary `.claude`; another skill is never touched."""
    import contextlib
    import io
    import tempfile
    fails = []
    tmp = Path(tempfile.mkdtemp(prefix="dev-skills-install-"))
    try:
        skills_dir, hooks = tmp / ".claude" / "skills", tmp / ".claude" / "hooks"
        other = skills_dir / "other-skill" / "SKILL.md"
        other.parent.mkdir(parents=True)
        other.write_text("not ours\n", encoding="utf-8")
        hooks.mkdir()
        (hooks / "ds-gate.py").write_text("# stale ds-gate hook\n", encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            install(skills_dir, repo_skills(), dry=True)
            if sorted(p.name for p in skills_dir.iterdir()) != ["other-skill"]:
                fails.append("--dry-run changed the skills directory")
            install(skills_dir, repo_skills(), dry=False)
            drift = check(skills_dir)
            if drift:
                fails.append("a fresh install reports drift")
            for name, src in HOOK_FILES:
                if not (hooks / name).is_file() or (hooks / name).read_bytes() != (REPO / src).read_bytes():
                    fails.append(f"installed hook {name} not refreshed from {src}")
            for p in sorted(owned(skills_dir)):
                remove(p, False)
        left = sorted(p.name for p in skills_dir.iterdir())
        if left != ["other-skill"] or other.read_text(encoding="utf-8") != "not ours\n":
            fails.append(f"uninstall left {left} or touched another skill")
        fresh = tmp / "typo"
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = main(["--no-such-flag", "--dir", str(fresh)])
        if code != 2 or fresh.exists():
            fails.append(f"an unknown flag installed anyway (exit {code}); it must print usage and exit 2")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for f in fails:
        print("  FAIL", f)
    print("install self-test:", "all checks passed" if not fails else f"{len(fails)} failed")
    return 1 if fails else 0


def main(argv) -> int:
    if "--self-test" in argv:
        return self_test()

    def opt(flag):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None

    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    values = {i + 1 for i, a in enumerate(argv) if a in ("--dir", "--skills")}
    unknown = [a for i, a in enumerate(argv) if i not in values and a not in
               ("--dir", "--skills", "--check", "--uninstall", "--dry-run")]
    if unknown:
        print(f"install.py: unknown argument(s) {' '.join(unknown)}; see python3 install.py --help", file=sys.stderr)
        return 2
    if sys.version_info < (3, 8):
        print("Python 3.8+ required")
        return 1
    skills_dir = Path(opt("--dir") or Path.home() / ".claude" / "skills").expanduser().resolve()
    dry = "--dry-run" in argv
    if "--check" in argv:
        return check(skills_dir)
    if "--uninstall" in argv:
        for p in sorted(owned(skills_dir)):
            remove(p, dry)
        return 0
    available = repo_skills()
    skills = available if not opt("--skills") else [s.strip() for s in opt("--skills").split(",")]
    unknown = [s for s in skills if s not in available]
    if unknown:
        print(f"unknown skill(s): {', '.join(unknown)} — available: {', '.join(available)}")
        return 2
    if not dry:
        skills_dir.mkdir(parents=True, exist_ok=True)
    return install(skills_dir, skills, dry)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
