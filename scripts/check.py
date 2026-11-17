#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""dev-skills quality gate — Python 3.8+ stdlib only; the only gate (no CI).

  python3 scripts/check.py                 run every check; exit 0 = green
  python3 scripts/check.py --self-test     prove each check goes red on the defect it exists to catch
  python3 scripts/check.py --install-hook  run this gate from .git/hooks/pre-commit
"""
from __future__ import annotations

import importlib.util
import json
import os
import py_compile
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
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
PERL_ONLY = re.compile(r"\\[bBsSwWdD]")
MECH = re.compile(r"^- \*\*Mech:\*\* (?:M\b.*|[ST] .*`[^`]+`.*)$")


def prose_greps(cmd: str) -> list:
    """`git grep` calls in a shell command that also search Markdown: no pathspec, or only exclusions none of which
    is ':!*.md'. Such a pattern matches the rule's own prose and every doc that names it (a hit that is no finding)."""
    lex = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        toks = list(lex)
    except ValueError:  # unbalanced quotes: the shell would fail too
        return [cmd]
    found = []
    for i in range(len(toks) - 1):
        if toks[i] == "git" and toks[i + 1] == "grep":
            seg = []
            for t in toks[i + 2:]:
                if set(t) <= set("|;&()"):
                    break
                seg.append(t)
            spec = seg[seg.index("--") + 1:] if "--" in seg else []
            if not any(s == ":!*.md" or not s.startswith(":") for s in spec):
                found.append(" ".join(["git", "grep", *seg]))
    return found


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
                    if re.search(r"\bgrep\b", cmd) and (PERL_ONLY.search(cmd) or re.search(r"\s-[a-zA-Z]*P", cmd)):
                        err(f"core/rules/{f.name}:{n}: Mech grep `{cmd[:40]}` uses a Perl-only escape or -P — "
                            "grep -E and git grep -E on macOS match nothing for \\b \\s \\w \\d (a silent false clean); "
                            "use [[:space:]], [[:alnum:]_], [0-9], (^|[^[:alnum:]_])word([^[:alnum:]_]|$)")
                    for g in prose_greps(cmd):
                        err(f"core/rules/{f.name}:{n}: Mech `{g[:50]}` also searches Markdown, so it hits its own "
                            "rule text — add -- ':!*.md', or name the paths (`.` to scan prose on purpose)")


FIXTURE = re.compile(r"(?m)^- \*\*Mech:\*\* ([ST]) (.*)\n(?:- \*\*Fixture:\*\* (.*))?")
ENTRY = re.compile(r"(hit|miss|quiet|says) `([^`]+)`")
# Commands reading git history run on one scripted repo (history_repo); each names what it must and must not print.
HISTORY = {
    "DOP-04": (["Update stuff"], ["fix: crash on empty input"]),
    "DOP-48": (["v1.2.0", "## [1.2.0]", '"version": "1.2.0"'], ["v0.9.0"]),
    "RPO-06": (["origin/stale", "assets/big.png"], ["src/app.py"]),
    "WEB-10": (["assets/big.png"], ["assets/icon.png"]),
    "TST-11": (["crash on empty input"], ["covered parser bug"]),
    "DOC-02": (["src/gone.py", "src/old_name.py", "$ make build"], ["src/app.py", "Plain prose line."]),
    "PRF-12": (["perf: faster startup"], ["Update stuff"]),
}


def git_env(home: Path) -> dict:
    """No GIT_* variable of the caller (a hook points GIT_INDEX_FILE at the outer commit), no user or system config."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return dict(env, HOME=str(home), XDG_CONFIG_HOME=str(home / ".config"), GIT_CONFIG_NOSYSTEM="1",
                GIT_AUTHOR_NAME="fixture-author", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")


def git_in(d: Path, env: dict, *args) -> str:
    return subprocess.run(["git", "-C", str(d), *args], check=True, capture_output=True, text=True, env=env).stdout.strip()


def commit(d: Path, env: dict, msg: str, files=(), drop=()):
    for path, text in files:
        (d / path).parent.mkdir(parents=True, exist_ok=True)
        (d / path).write_bytes(text) if isinstance(text, bytes) else (d / path).write_text(text, encoding="utf-8")
    for path in drop:
        (d / path).unlink()
    git_in(d, env, "add", "-A")
    git_in(d, env, "commit", "-q", "--allow-empty", "-m", msg)


def history_repo(d: Path, env: dict) -> str:
    """Base commit (tags, a merged remote branch), then fix/perf/odd commits, a rename, a delete and a 10 MB blob."""
    git_in(d.parent, env, "init", "-q", d.name)
    commit(d, env, "chore: base", [
        ("src/app.py", "def run():\n    return 1\n"), ("src/old_name.py", "X = 1\n"), ("src/gone.py", "Y = 2\n"),
        ("README.md", "Run it:\n\n    $ make build\n\nPlain prose line.\n"), ("CHANGELOG.md", "# Changelog\n\n## [1.2.0]\n"),
        ("package.json", '{\n  "version": "1.2.0"\n}\n')])
    base = git_in(d, env, "rev-parse", "HEAD")
    for tag in ("v0.9.0", "v1.0.0", "v1.1.0", "v1.2.0"):
        git_in(d, env, "tag", tag)
    git_in(d, env, "update-ref", "refs/remotes/origin/stale", base)
    commit(d, env, "fix: crash on empty input", [("src/app.py", "def run():\n    return 2\n")])
    commit(d, env, "fix: covered parser bug", [("tests/test_app.py", "def test_run():\n    assert run() == 2\n")])
    commit(d, env, "Update stuff", [("notes.txt", "x\n")])
    commit(d, env, "perf: faster startup", [("src/app.py", "def run():\n    return 3\n")])
    git_in(d, env, "mv", "src/old_name.py", "src/new_name.py")
    commit(d, env, "refactor: move module", drop=["src/gone.py"])
    commit(d, env, "build: add assets", [("assets/big.png", b"\0" * 10485761), ("assets/icon.png", b"\x89PNG")])
    return base


def parts(text: str) -> set:
    return {t.strip() for t in text.split("\\n") if t.strip()}


def shown(entry, lines, common=frozenset()) -> bool:
    """An entry shows when an output line holds one of its content lines (except boilerplate `common` to a hit and a
    miss) or names its path (file-listing commands)."""
    path, text = entry
    own = parts(text) - common
    named = re.compile(r"(^|[\s/:])" + re.escape(path) + r"($|[\s:])") if path else None
    return any(any(p in ln for p in own) or (named and named.search(ln)) for ln in lines)


def outputs(audit, d: Path, rid: str, cls: str, cmds, base: str, problems: list, skip: list) -> list:
    """(command, printed lines) of each command that ran; a missing tool goes to skip, an error to problems."""
    out = []
    for cmd in cmds:
        row = audit.run_mech(d, rid, cls, cmd, {"base": base})
        if row["status"] == "tool absent":
            skip.append(f"{rid} `{cmd.split()[0]}`")
        elif row["status"] in ("error", "timeout"):
            problems.append(f"`{cmd[:60]}` {row['status']}: {row.get('detail', '')[-150:]}")
        else:
            out.append((cmd, row["hits"] if row["status"] == "hit" else []))
    return out


def judge(out, ran_all: bool, hits, misses, skip: list, rid: str, later=None) -> list:
    """Every command that ran shows a hit (or goes to `later`, for the quiet stage); every hit shows (else, with a tool
    absent, it is listed); no miss shows."""
    problems, hit_paths = [], {h[0] for h in hits}
    common = set().union(*(parts(t) for _, t in hits)) & set().union(*(parts(t) for _, t in misses))
    for cmd, lines in out:
        if any(shown(h, lines, common) for h in hits):
            continue
        if later is None:
            problems.append(f"`{cmd[:60]}` shows none of its hit fixtures (output: {lines[:3]})")
        else:
            later.append(cmd)
    for h in hits:
        if not any(shown(h, lines, common) for _, lines in out):
            if ran_all:
                problems.append(f"hit `{h[0]}: {h[1][:40]}` shown by no command")
            else:
                skip.append(f"{rid} hit `{h[1][:30]}` (left to the absent tool)")
    for path, text in misses:
        if any(shown((path if path not in hit_paths else "", text), lines, common) for _, lines in out):
            problems.append(f"miss `{path}: {text[:40]}` is reported")
    return problems


def fixture_files(entries):
    files = {}
    for path, text in entries:
        files[path] = files.get(path, "") + text.replace("\\n", "\n") + "\n"
    return files.items()


def fixture_rule(audit, tmp: Path, env: dict, hist: tuple, rid: str, cls: str, cmds: list, fx) -> tuple:
    """(problems, skips) of one S/T rule's Fixture line."""
    problems, skip = [], []
    if fx is None:
        return ["an S/T rule needs `- **Fixture:** hit `path: line` · miss `path: line`` right after its Mech line "
                "(or `history`, or `none · reason`)"], skip
    if fx.startswith("none · "):
        return problems, [f"{rid} (none: {fx[7:]})"]
    if fx == "history":
        if rid not in HISTORY:
            return ["Fixture history, but scripts/check.py HISTORY has no entry for it"], skip
        hits, misses = ([("", t) for t in side] for side in HISTORY[rid])
        out = outputs(audit, hist[0], rid, cls, cmds, hist[1], problems, skip)
        return problems + judge(out, not skip, hits, misses, skip, rid), skip
    e = {k: [] for k in ("hit", "miss", "quiet", "says")}
    for kind, body in ENTRY.findall(fx):
        path, sep, text = body.partition(": ")
        e[kind].append(("", body) if kind == "says" else (path, text) if sep else ("", "\0"))
    if ("", "\0") in e["hit"] + e["miss"] + e["quiet"] or not e["hit"] + e["says"] or not e["miss"] + e["quiet"]:
        return ["Fixture needs entries `hit|miss|quiet `path: line`` or `says `text``: at least one hit or says, and "
                "one miss or quiet"], skip
    d = tmp / rid
    git_in(tmp, env, "init", "-q", d.name)
    commit(d, env, "chore: base")
    base = git_in(d, env, "rev-parse", "HEAD")
    commit(d, env, "chore: fixture", fixture_files(e["hit"] + e["miss"]))
    out = outputs(audit, d, rid, cls, cmds, base, problems, skip)
    later = [] if e["quiet"] else None  # a command for the present thing may show it after the quiet files
    problems += judge(out, not skip, e["hit"] + e["says"], e["miss"], skip, rid, later)
    if e["quiet"] and not skip:
        commit(d, env, "chore: quiet", fixture_files(e["quiet"]))
        said = {c for c, lines in out if any(shown(s, lines) for s in e["says"])}
        for cmd, lines in outputs(audit, d, rid, cls, cmds, base, problems, skip):
            if cmd in said and lines:  # an absence check falls silent once the thing exists
                problems.append(f"`{cmd[:60]}` still prints after the quiet files: {lines[:2]}")
            problems += [f"`{t[1][:40]}` still shown after the quiet files"
                         for t in ([] if e["says"] else e["hit"]) if shown(t, lines)]
            if cmd in later and not any(shown(q, lines) for q in e["quiet"]):
                problems.append(f"`{cmd[:60]}` shows none of its hit or quiet fixtures")
    elif later:
        problems += [f"`{c[:60]}` shows none of its hit fixtures" for c in later]
    return problems, skip


def check_mech_fixtures(root: Path, err):
    """Each S/T Mech command runs, as audit.py scan runs it, on a temp repo holding its rule's Fixture files: it shows
    every hit and `says` text and no miss; after the `quiet` files are committed a command that printed a `says` text
    prints nothing (with no says, the hits are gone). `history` rules run on one scripted history; `none` and absent
    tools are listed as skipped, never passed. Rules run in parallel: each is a few git and grep processes."""
    spec = importlib.util.spec_from_file_location("ds_audit_fixture", root / "ds-audit" / "assets" / "audit.py")
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    tmp = Path(tempfile.mkdtemp(prefix="ds-fix-")).resolve()
    env = audit.ENV = dict(git_env(tmp), CI="1", GIT_PAGER="cat", GIT_EDITOR="true", PAGER="cat", GIT_TERMINAL_PROMPT="0")
    jobs, skip = [], []
    try:
        hist = (tmp / "history", history_repo(tmp / "history", env))
        for f in sorted((root / "core" / "rules").glob("*.md")):
            for block in re.split(r"(?m)^(?=### )", f.read_text(encoding="utf-8")):
                head, m = RULE.match(block.split("\n", 1)[0]), FIXTURE.search(block)
                if head and m:
                    jobs.append((f.name, head.group(1), m.group(1), re.findall(r"`([^`]+)`", m.group(2)), m.group(3)))
        with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as pool:
            results = pool.map(lambda j: fixture_rule(audit, tmp, env, hist, *j[1:]), jobs)
            for (name, rid, *_), (problems, skipped) in zip(jobs, results):
                skip += skipped
                for p in problems:
                    err(f"core/rules/{name} {rid}: {p}")
        declared = {rid for _, rid, _, _, fx in jobs if fx == "history"}
        for rid in sorted(set(HISTORY) - declared):
            err(f"scripts/check.py HISTORY: {rid} is no S/T rule with `- **Fixture:** history`")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if skip:
        return f"{len(skip)} fixture command(s) not run: " + ", ".join(skip)


def check_principles(root: Path, err):
    """Every kernel §7 principle is enforced somewhere: a rule with a Detect line cites its exact name in Source."""
    kernel = (root / "core" / "kernel.md").read_text(encoding="utf-8")
    sec7 = kernel[kernel.find("## 7."):]
    names = [n for n in re.findall(r"^\| ([^|]+?) \|", sec7, re.M) if n != "Principle" and set(n) - set("-")]
    if not names:
        err("core/kernel.md: no §7 principle table found")
    sources = []
    for f in sorted((root / "core" / "rules").glob("*.md")):
        for block in re.split(r"(?m)^(?=### )", f.read_text(encoding="utf-8")):
            src = re.search(r"(?m)^- \*\*Source:\*\* (.*)$", block)
            if RULE.match(block.split("\n", 1)[0]) and "- **Detect:**" in block and src:
                sources.append(src.group(1).lower())
    for n in names:
        if not any(n.lower() in s for s in sources):
            err(f"kernel §7 principle '{n}': no rule with a Detect line cites it in its Source line")


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
                     ["ds-research/assets/verify-brief.py", "--self-test"], ["install.py", "--self-test"]):
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


def check_python_compiles(root: Path, err):
    """Every Python file parses; the bytecode goes to a temp dir, so no __pycache__ lands in the repo."""
    out = Path(tempfile.mkdtemp(prefix="ds-pyc-"))
    try:
        for p in sorted(root.rglob("*.py")):
            if ".git" in p.parts or "__pycache__" in p.parts:
                continue
            try:
                py_compile.compile(str(p), cfile=str(out / "x.pyc"), doraise=True)
            except py_compile.PyCompileError as e:
                x = e.exc_value
                err(f"{p.relative_to(root).as_posix()}:{getattr(x, 'lineno', '?')}: does not compile: "
                    f"{e.exc_type_name}: {getattr(x, 'msg', x)}")
    finally:
        shutil.rmtree(out, ignore_errors=True)


CHECKS = [check_skills, check_links, check_rules, check_mech, check_mech_fixtures, check_principles, check_duplicate_lines,
          check_consumers, check_retired, check_versions, check_python_compiles, check_self_tests, check_spelling]


SKIPPED = []


def run(root: Path, checks=CHECKS, quiet=False) -> list:
    errors = []
    for c in checks:
        before = len(errors)
        skip = c(root, errors.append)
        if skip:
            SKIPPED.append(c.__name__)
        if not quiet:
            state = "FAIL" if len(errors) > before else "SKIP" if skip else "ok  "
            print(f"{state} {c.__name__}" + (f" — skipped: {skip}" if skip else ""))
    return errors


DUP = "Gate fixture line long enough to count as a fact: it now has two homes in two shipped files."


def self_test() -> int:
    """Each case injects the defect one check exists to catch into a copy; that check must go red."""
    cases = [
        (check_skills, "ds-audit/SKILL.md", lambda s: s.replace("name: ds-audit", "name: other")),
        (check_skills, "ds-audit/SKILL.md", lambda s: s + "x" * SKILL_MAX),
        (check_links, "ds-audit/SKILL.md", lambda s: s + "\n[x](../core/missing.md)\n"),
        (check_links, "ds-audit/SKILL.md", lambda s: s + "\n[x](../ds-setup/SKILL.md)\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-09 [HIGH] Again\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-99 [BLOCKER] Severity\n"),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-98 [HIGH] Gate fixture near duplicate title alpha beta\n",
         {"core/rules/ux.md": "\n### UX-998 [LOW] Gate fixture near duplicate title alpha\n"}),
        (check_rules, "core/rules/web.md", lambda s: s + "\n### WEB-97 | HIGH | Pipe heading\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** S no command in backticks\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** S `curl -sI https://example.com`\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** T `git grep -nE '\\bfoo\\b'`\n"),
        (check_mech, "core/rules/web.md", lambda s: s + "\n- **Mech:** T `git grep -nE 'foo' -- ':!*.lock' | sort`\n"),
        (check_principles, "core/kernel.md", lambda s: s.replace("| YAGNI |", "| Gate fixture principle | Never |\n| YAGNI |")),
        (check_duplicate_lines, "core/rules/web.md", lambda s: s + "\n" + DUP + "\n", {"core/rules/ux.md": "\n" + DUP + "\n"}),
        (check_consumers, "core/orphan.md", lambda s: "# orphan\n"),
        (check_retired, "ds-audit/SKILL.md", lambda s: s + "\nDelegate to ds-review.\n"),
        (check_versions, ".claude-plugin/marketplace.json", lambda s: s.replace('"version": "', '"version": "9', 1)),
        (check_python_compiles, "core/broken.py", lambda s: "def broken(:\n"),
        (check_mech_fixtures, "core/rules/web.md", lambda s: s + "\n### WEB-96 [LOW] Gate fixture blind command\n"
         "- **Mech:** S `git grep -nE 'never_written' -- '*.py'`\n- **Fixture:** hit `a.py: written` · miss `b.py: other`\n"),
    ]
    failures = 0
    for check, rel, mutate, *prep in cases:
        tmp = Path(tempfile.mkdtemp(prefix="ds-check-")).resolve()  # macOS: /var is a symlink to /private/var
        try:
            for part in ("ds-audit", "ds-gate", "ds-research", "ds-setup", "core", "agents", ".claude-plugin"):
                if (ROOT / part).exists():
                    shutil.copytree(ROOT / part, tmp / part)
            shutil.copy(ROOT / "CHANGELOG.md", tmp / "CHANGELOG.md")
            target = tmp / rel
            for path, extra in (prep[0] if prep else {}).items():  # the counterpart a duplicate needs, own text
                (tmp / path).write_text((tmp / path).read_text(encoding="utf-8") + extra, encoding="utf-8")
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
    skipped = f", {len(SKIPPED)} check(s) with skips: {', '.join(SKIPPED)}" if SKIPPED else ""
    print(f"check: {'OK' if not errors else 'FAIL'} — {len(errors)} problem(s){skipped}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
