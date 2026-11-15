#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Eval: ds-audit on a small Node library with no UI, store, billing or mobile signals.

  python3 evals/audit_library.py setup DIR     build the fixture repo
  python3 evals/audit_library.py score DIR     one `criterion<TAB>PASS|FAIL` line each, then OVERALL; exit 0 = all pass
  python3 evals/audit_library.py validate      prove the scorer: red on the untouched fixture, green on a hand-made report

Request given to the agent: "Audit and improve this project." Score the repo afterwards, never the agent's claim.
"""
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
NOT_APPLICABLE = ("store", "monetization", "mobile", "a11y")


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
    areas = next((l for l in text.splitlines() if l.startswith("Areas:")), "")
    results = [
        ("report-written", bool(text)),
        ("status-line", bool(re.search(r"^ds-audit: (OK|WARN|FAIL|INCOMPLETE) \|", text, re.M))),
        ("signals-line", bool(re.search(r"^Signals: .*ui=none", text, re.M))),
        ("irrelevant-areas-N/A", all(re.search(rf"\b{a}\b[^·]*N/A", areas) for a in NOT_APPLICABLE)),
        ("closing-block", all(k in text for k in ("Asked:", "Done:"))),
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
    (d / ".git" / "info" / "exclude").write_text("ds/audit/\n", encoding="utf-8")
    (d / "ds" / "audit").mkdir(parents=True)
    (d / "ds" / "audit" / "report.md").write_text(
        "ds-audit: OK | findings 0 · fixed 0 · open 0 · only-you 0\n"
        "Signals: ui=none api=none db=none tests=node platforms=library\n"
        "Areas: security ran · testing ran · store N/A — deploy=none · monetization N/A — billing=none · "
        "mobile N/A — mobile=none · a11y N/A — ui=none\n\nAsked: audit\nDone: nothing to change\n", encoding="utf-8")
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
