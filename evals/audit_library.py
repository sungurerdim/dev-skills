#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Eval: ds-audit on a small Node library with no UI, store, billing or mobile signals.

  python3 evals/audit_library.py setup DIR     build the fixture repo
  python3 evals/audit_library.py score DIR     one `criterion<TAB>PASS|FAIL` line each, then OVERALL; exit 0 = all pass
  python3 evals/audit_library.py validate      prove the scorer: red on the untouched fixture, green on a run audit.py
                                               itself completed (init, checks, every phase closed, report)

Request given to the agent: "Audit and improve this project." Score the repo afterwards, never the agent's claim.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FILES = {
    "package.json": '{\n  "name": "slug-kit",\n  "version": "0.3.0",\n  "main": "src/index.js",\n'
                    '  "scripts": { "test": "node --test" },\n  "license": "MIT"\n}\n',
    "src/index.js": "function slugify(s) {\n  return String(s).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-')"
                    ".replace(/^-+|-+$/g, '');\n}\nfunction truncate(s, n) {\n  s = String(s);\n"
                    "  return s.length <= n ? s : s.slice(0, n);\n}\nmodule.exports = { slugify, truncate };\n",
    "test/index.test.js": "const test = require('node:test');\nconst assert = require('node:assert/strict');\n"
                          "const { slugify, truncate } = require('../src/index');\n"
                          "test('slugify', () => { assert.equal(slugify('Hello, World!'), 'hello-world'); });\n"
                          "test('truncate', () => { assert.equal(truncate('abc', 5), 'abc'); });\n",
    "README.md": "# slug-kit\n\nTiny slug helpers.\n\n## Install\n\n`npm install slug-kit`\n",
    ".gitignore": "node_modules/\n",
}
NOT_APPLICABLE = ("store", "money", "mobile", "a11y")  # area words, core/rules/README.md
AUDIT = Path(__file__).resolve().parent.parent / "ds-audit" / "assets" / "audit.py"


def audit(d: Path, *args):
    return subprocess.run([sys.executable, "-B", str(AUDIT), "--root", str(d), *args], capture_output=True, text=True)


def git(d, *a):
    return subprocess.run(["git", *a], cwd=d, capture_output=True, text=True)


def setup(d: Path):
    shutil.rmtree(d, ignore_errors=True)
    for rel, text in FILES.items():
        (d / rel).parent.mkdir(parents=True, exist_ok=True)
        (d / rel).write_text(text, encoding="utf-8", newline="\n")
    for a in (["init", "-q", "-b", "main"], ["config", "user.email", "eval@example.com"],
              ["config", "user.name", "Eval"], ["add", "-A"], ["commit", "-qm", "chore: initial fixture"]):
        git(d, *a)


def score(d: Path) -> int:
    rep = d / "ds" / "audit" / "report.md"
    text = rep.read_text(encoding="utf-8") if rep.is_file() else ""
    phases = re.search(r"^## Phases\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    phases = phases.group(1) if phases else ""
    results = [
        ("report-written", bool(text)),
        ("status-line", bool(re.search(r"^ds-audit: (OK|WARN|FAIL) ·", text, re.M))),  # INCOMPLETE = a phase left open
        ("signals-line", bool(re.search(r"^Signals: .*ui=none", text, re.M))),
        ("irrelevant-areas-N/A", all(re.search(rf"\b{a} N/A", phases) for a in NOT_APPLICABLE)),
        ("ledger-valid", bool(text) and audit(d, "validate").returncode == 0),
        ("closing-message", "Asked:" in text and ("| Change |" in text or "No findings" in text)),
        ("tests-green", subprocess.run(["node", "--test"], cwd=d, capture_output=True).returncode == 0),
        ("clean-tree", git(d, "status", "--porcelain").stdout.strip() == ""),
    ]
    for name, ok in results:
        print(f"{name}\t{'PASS' if ok else 'FAIL'}")
    passed = sum(ok for _, ok in results)
    print(f"OVERALL\t{'PASS' if passed == len(results) else 'FAIL'}\t{passed}/{len(results)}")
    return 0 if passed == len(results) else 1


def validate() -> int:
    d = Path(tempfile.mkdtemp(prefix="ship-eval-")) / "repo"
    setup(d)
    red = score(d) != 0
    init = audit(d, "init", "all")
    audit(d, "checks", "baseline")
    audit(d, "checks", "now")
    for name in re.findall(r'"(lean|build|safe|surface|ship)": \{\s*"status": "pending"', init.stdout):
        unread = json.loads(audit(d, "coverage", name).stdout).get(name, {}).get("unread", [])
        if unread:  # stands in for the reviewers: every file on the phase's reading list is read
            audit(d, "read", name, *unread)
        audit(d, "phase", name, "done")
    audit(d, "report")
    green = score(d) == 0
    print(f"validate: {'OK' if red and green else 'BROKEN'} (red before: {red}, green after: {green})")
    shutil.rmtree(d.parent, ignore_errors=True)
    return 0 if red and green else 1


if __name__ == "__main__":
    cmd, *rest = sys.argv[1:] or ["-h"]
    if cmd == "setup":
        setup(Path(rest[0]))
    elif cmd == "score":
        sys.exit(score(Path(rest[0])))
    elif cmd == "validate":
        sys.exit(validate())
    else:
        print(__doc__)
