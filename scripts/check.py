#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""dev-skills quality gate — Python 3.8+ stdlib only; the only gate (no CI).

  python3 scripts/check.py                 run every check; exit 0 = green
  python3 scripts/check.py --self-test     prove each check goes red on the defect it exists to catch
  python3 scripts/check.py --install-hook  run this gate from .git/hooks/pre-commit
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

ROOT = Path(__file__).resolve().parent.parent
SKILL_MAX = 8192                       # bytes per SKILL.md: the always-loaded part stays small
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
RULE = re.compile(r"^### (\S+) \[([A-Z]+)\] (.+)$")
LINK = re.compile(r"\]\(([^)#\s]+\.(?:md|py|html))(?:#[^)]*)?\)")
RETIRED = ("ds-backend ds-benchmark ds-blueprint ds-build ds-commit ds-compliance ds-debug ds-deploy ds-deps ds-devops "
           "ds-docs ds-fix ds-freeze ds-frontend ds-init ds-issue ds-launch ds-mobile ds-pipeline ds-pr ds-productize "
           "ds-release ds-repo ds-review ds-simplify ds-solve ds-test ds-tune "
           "ds-ship ds-quality ds-rig ds-brief").split()  # the last four were renamed in 3.0.0
STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "no", "not", "is", "are", "by"}


def shipped(root: Path):
    """Every file an install ships, as (path, text)."""
    for p in sorted([*root.glob("ds-*/**/*"), *root.glob("core/**/*"), *root.glob("agents/*.md")]):
        if p.is_file() and p.suffix in (".md", ".py", ".html") and "__pycache__" not in p.parts:
            yield p, p.read_text(encoding="utf-8")


def check_skills(root: Path, err):
    skills = sorted(p.parent for p in root.glob("ds-*/SKILL.md"))
    if not skills:
        err("no ds-*/SKILL.md found")
    for d in skills:
        text = (d / "SKILL.md").read_text(encoding="utf-8")
        m = re.match(r"---\nname: (.+)\ndescription: (.+)\n(?:argument-hint: '[^'\n]+'\n)?---\n", text)
        if not m:
            err(f"{d.name}/SKILL.md: frontmatter must be name + description (+ optional single-quoted argument-hint)")
            continue
        if m.group(1).strip() != d.name:
            err(f"{d.name}/SKILL.md: name '{m.group(1).strip()}' != directory")
        if not 20 <= len(m.group(2)) <= 1024:
            err(f"{d.name}/SKILL.md: description length {len(m.group(2))} outside 20-1024")
        size = len(re.sub(r"(?m)^argument-hint: .*\n", "", text, count=1).encode("utf-8"))  # autocomplete hint, not skill text
        if size > SKILL_MAX:
            err(f"{d.name}/SKILL.md: {size} bytes > {SKILL_MAX}")
        if "kernel.md" not in text:
            err(f"{d.name}/SKILL.md: does not load ../core/kernel.md")


def check_links(root: Path, err):
    """Relative links resolve and stay inside what one install ships: the skill's own dir or core/."""
    for p, text in shipped(root):
        if p.suffix != ".md":
            continue
        top = p.relative_to(root).parts[0]
        allowed = [root / "core"] + ([root / top] if top.startswith("ds-") else [])
        prose = re.sub(r"```.*?```|`[^`\n]*`", "", text, flags=re.S)  # examples in code are not links
        for target in LINK.findall(prose):
            if "://" in target:
                continue
            t = (p.parent / target).resolve()
            rel = p.relative_to(root)
            if not t.exists():
                err(f"{rel}: dead link {target}")
            elif not any(t == a or a in t.parents for a in allowed):
                err(f"{rel}: link {target} leaves the shipped scope")


def rules(root: Path):
    for f in sorted((root / "core" / "rules").glob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("### "):
                yield f, n, line, RULE.match(line)


def check_rules(root: Path, err):
    seen, titles = {}, []
    for f, n, line, m in rules(root):
        where = f"core/rules/{f.name}:{n}"
        if not m:
            if re.match(r"^### [A-Z][A-Z0-9]*-\d+\b", line):  # looks like a rule, so it must parse as one
                err(f"{where}: rule heading must be `### ID [SEVERITY] Title`, got: {line[:70]}")
            continue
        rid, sev, title = m.groups()
        if sev not in SEVERITIES:
            err(f"{where}: severity [{sev}] not in {sorted(SEVERITIES)}")
        if rid in seen:
            err(f"{where}: rule id {rid} already defined at {seen[rid]}")
        seen[rid] = where
        words = set(re.findall(r"[a-z0-9]+", re.sub(r"\[.*?\]|\(.*?\)", "", title.lower()))) - STOP
        titles.append((where, f.name, title, words))
    for i, (w1, f1, t1, a) in enumerate(titles):
        for w2, f2, t2, b in titles[i + 1:]:
            if f1 != f2 and a and b and len(a & b) / len(a | b) >= 0.75:
                err(f"near-duplicate rule titles: {w1} '{t1}' ~ {w2} '{t2}'")


NETWORK = re.compile(r"^\s*(curl|wget|dig|nslookup|host|openssl\s+s_client|gh|npm\s+view|pip\s+download|ssh|nc)\b")
MECH = re.compile(r"^- \*\*Mech:\*\* (?:M\b.*|[ST] .*`[^`]+`.*)$")


def check_mech(root: Path, err):
    """A Mech line names its class; S and T name at least one command in backticks (audit.py scan runs them)."""
    for f in sorted((root / "core" / "rules").glob("*.md")):
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("- **Mech:**") and not MECH.match(line):
                err(f"core/rules/{f.name}:{n}: Mech line must be `- **Mech:** S|T `command`…` or `- **Mech:** M …`")
            elif line.startswith("- **Mech:** ") and line[12:13] in "ST":
                for cmd in re.findall(r"`([^`]+)`", line):
                    if NETWORK.match(cmd):
                        err(f"core/rules/{f.name}:{n}: Mech command `{cmd[:40]}` needs the network or credentials — "
                            "a scan is offline; name it in Detect and make the rule M")


def check_duplicate_lines(root: Path, err):
    """A long line repeated in two shipped files is a second home for one fact."""
    homes = {}
    for p, text in shipped(root):
        if p.suffix != ".md":
            continue
        for line in text.splitlines():
            s = line.strip()
            if len(s) >= 80 and not s.startswith(("|", "- **Source:**", "**Source:**", "Source:")):
                homes.setdefault(s, set()).add(p.relative_to(root).as_posix())
    for s, files in homes.items():
        if len(files) > 1:
            err(f"line repeated in {sorted(files)}: {s[:90]}")


def check_consumers(root: Path, err):
    """Every core file is referenced from somewhere that ships; an unreferenced file is dead weight."""
    corpus = "\n".join(t for _, t in shipped(root))
    for f in sorted((root / "core").rglob("*.md")):
        if f.name == "README.md":
            continue
        if f.name not in corpus.replace(f.read_text(encoding="utf-8"), ""):
            err(f"core/{f.relative_to(root / 'core').as_posix()}: no consumer references it")


def check_retired(root: Path, err):
    # a file or path name (ds-quality.json, .config/ds-rig) is a compatibility reference, not a skill mention
    pat = re.compile(r"(?<![\w/-])(" + "|".join(map(re.escape, RETIRED)) + r")(?![\w/-]|\.\w)")
    for p, text in shipped(root):
        for n, line in enumerate(text.splitlines(), 1):
            m = pat.search(line)
            if m:
                err(f"{p.relative_to(root)}:{n}: names retired skill {m.group(1)}")


def check_versions(root: Path, err):
    market = json.loads((root / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    versions = {market.get("version"), *(pl.get("version") for pl in market.get("plugins", []))}
    head = re.search(r"^## \[(\d+\.\d+\.\d+)\]", (root / "CHANGELOG.md").read_text(encoding="utf-8"), re.M)
    if len(versions) != 1 or not head or head.group(1) not in versions:
        err(f"version mismatch: marketplace {sorted(map(str, versions))}, CHANGELOG {head.group(1) if head else 'none'}")


def check_self_tests(root: Path, err):
    """Every asset self-test passes, and runs safely inside a git hook: git points GIT_INDEX_FILE at the outer commit's
    index (`commit --only`), and a self-test's temp repo must never write into it."""
    outer = Path(tempfile.mkdtemp(prefix="ds-hook-")).resolve()
    clean = {k: v for k, v in os.environ.items()  # this gate itself runs inside the pre-commit hook
             if k not in ("GIT_DIR", "GIT_INDEX_FILE", "GIT_WORK_TREE", "GIT_OBJECT_DIRECTORY", "GIT_COMMON_DIR",
                          "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX")}
    try:
        for a in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", "-C", str(outer), *a], check=True, capture_output=True, env=clean)
        (outer / "outer.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(outer), "add", "outer.txt"], check=True, capture_output=True, env=clean)
        index = outer / ".git" / "index"
        before = index.read_bytes()
        env = dict(clean, GIT_INDEX_FILE=str(index))
        for args in (["core/ds_detect.py", "--self-test"], ["ds-audit/assets/audit.py", "--self-test"],
                     ["ds-gate/assets/ds-gate.py", "--self-test"], ["ds-setup/assets/test_rc_deny.py"],
                     ["ds-setup/assets/probe.py", "--self-test"], ["ds-setup/assets/perms.py", "--self-test"],
                     ["ds-research/assets/verify-brief.py", "--self-test"]):
            if not (root / args[0]).exists():
                err(f"{args[0]}: missing")
                continue
            r = subprocess.run([sys.executable, "-B", *args], cwd=str(root), capture_output=True, text=True, env=env)
            if r.returncode != 0:
                err(f"{args[0]} self-test failed (exit {r.returncode}): {(r.stdout + r.stderr).strip()[-300:]}")
            if index.read_bytes() != before:
                err(f"{args[0]} self-test wrote into the outer git index (GIT_INDEX_FILE leak) — unsafe in a hook")
                index.write_bytes(before)
    finally:
        shutil.rmtree(outer, ignore_errors=True)


def check_spelling(root: Path, err):
    """typos with the repo's _typos.toml; absent tool -> a visible skip, never a silent pass."""
    exe = shutil.which("typos")
    if not exe:
        return "typos not installed (cargo install typos-cli / brew install typos-cli)"
    r = subprocess.run([exe, "--format", "brief"], cwd=str(root), capture_output=True, text=True)
    if r.returncode != 0:
        err("typos: " + (r.stdout + r.stderr).strip()[-400:])


CHECKS = [check_skills, check_links, check_rules, check_mech, check_duplicate_lines, check_consumers, check_retired,
          check_versions, check_self_tests, check_spelling]


SKIPPED = []


def run(root: Path, checks=CHECKS, quiet=False) -> list:
    errors = []
    for c in checks:
        before = len(errors)
        skip = c(root, errors.append)
        if skip:
            SKIPPED.append(c.__name__)
        if not quiet:
            print(f"SKIP {c.__name__}: {skip}" if skip else f"{'ok  ' if len(errors) == before else 'FAIL'} {c.__name__}")
    return errors


def self_test() -> int:
    """Each case injects the defect one check exists to catch into a copy; that check must go red."""
    cases = [
        (check_skills, "ds-audit/SKILL.md", lambda s: s.replace("name: ds-audit", "name: other")),
        (check_skills, "ds-audit/SKILL.md", lambda s: s + "x" * SKILL_MAX),
        (check_links, "ds-audit/SKILL.md", lambda s: s + "\n[x](../core/missing.md)\n"),
        (check_links, "ds-audit/SKILL.md", lambda s: s + "\n[x](../ds-setup/SKILL.md)\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-01 [HIGH] Again\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-99 [BLOCKER] Severity\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-98 [HIGH] Retry With Backoff\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-97 | HIGH | Pipe heading\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** S no command in backticks\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** S `curl -sI https://example.com`\n"),
        (check_duplicate_lines, "core/rules/web.md", lambda s: s + "\nAnimations must not trigger expensive layout recalculations; this line now has two homes.\n" * 1),
        (check_consumers, "core/orphan.md", lambda s: "# orphan\n"),
        (check_retired, "ds-audit/SKILL.md", lambda s: s + "\nDelegate to ds-review.\n"),
        (check_versions, ".claude-plugin/marketplace.json", lambda s: s.replace('"version": "', '"version": "9', 1)),
    ]
    failures = 0
    for check, rel, mutate in cases:
        tmp = Path(tempfile.mkdtemp(prefix="ds-check-")).resolve()  # macOS: /var is a symlink to /private/var
        try:
            for part in ("ds-audit", "ds-gate", "ds-research", "ds-setup", "core", "agents", ".claude-plugin"):
                if (ROOT / part).exists():
                    shutil.copytree(ROOT / part, tmp / part)
            shutil.copy(ROOT / "CHANGELOG.md", tmp / "CHANGELOG.md")
            target = tmp / rel
            if check is check_duplicate_lines:  # a line is only a duplicate once it exists in two files
                (tmp / "core/rules/ux.md").write_text((tmp / "core/rules/ux.md").read_text(encoding="utf-8")
                                                      + "\nAnimations must not trigger expensive layout recalculations; this line now has two homes.\n",
                                                      encoding="utf-8")
            original = target.read_text(encoding="utf-8") if target.exists() else ""
            if run(tmp, [check], quiet=True):
                print(f"  setup  {check.__name__}: already red before the mutation — fix the gate first")
                failures += 1
                continue
            target.write_text(mutate(original), encoding="utf-8")
            red = bool(run(tmp, [check], quiet=True))
            print(f"  {'ok  ' if red else 'BLIND'} {check.__name__} catches: {rel}")
            failures += not red
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("self-test:", "all checks proven" if not failures else f"{failures} case(s) failed")
    return 1 if failures else 0


def install_hook() -> int:
    hook = ROOT / ".git" / "hooks" / "pre-commit"
    hook.parent.mkdir(parents=True, exist_ok=True)
    py = Path(sys.executable).as_posix()
    hook.write_text(f'#!/bin/sh\n"{py}" scripts/check.py && exec "{py}" scripts/check.py --self-test\n', encoding="utf-8")
    hook.chmod(0o755)
    print(f"pre-commit hook -> {hook}")
    return 0


def main(argv) -> int:
    if "--self-test" in argv:
        return self_test()
    if "--install-hook" in argv:
        return install_hook()
    if argv and argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    errors = run(ROOT)
    for e in errors:
        print("  ", e)
    skipped = f", {len(SKIPPED)} check(s) not run: {', '.join(SKIPPED)}" if SKIPPED else ""
    print(f"check: {'OK' if not errors else 'FAIL'} — {len(errors)} problem(s){skipped}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
