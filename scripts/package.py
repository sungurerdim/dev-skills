#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build one self-contained ZIP per skill for upload to claude.ai (Customize > Skills > Upload a skill).

  python3 scripts/package.py              build dist/<skill>.zip for every skill
  python3 scripts/package.py --out DIR    write the zips to DIR instead of dist/
  python3 scripts/package.py --skills a,b only these skills

The repo keeps one shared core/ beside the skills; an uploaded skill sees only its own folder. So each zip
holds `<skill>/` with `core/` copied inside it, and every Markdown link into core/ is rewritten to its new
relative path; Claude Code-only frontmatter keys (argument-hint) are dropped, since claude.ai rejects them. The repo itself is not changed. Each build is checked before it is zipped: frontmatter per the
Agent Skills rules, and every relative Markdown link must resolve inside the package. Python 3.8+ stdlib only.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHARED = "core"
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc")
LINK = re.compile(r"(\]\()([^)\s#]+)(#[^)\s]*)?(\))")
NAME = re.compile(r"^[a-z0-9-]{1,64}$")
FIXED_TIME = (2020, 1, 1, 0, 0, 0)
# keys a claude.ai upload accepts (code.claude.com/docs/en/skills, "Using skill frontmatter outside Claude Code")
UPLOAD_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)  # links shown as examples inside code are not links


def repo_skills() -> list:
    return sorted(p.name for p in REPO.glob("ds-*") if (p / "SKILL.md").is_file())


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        raise SystemExit(f"{skill_md}: no YAML frontmatter")
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.*)$", m.group(1), re.M))


def strip_upload_keys(skill_md: Path) -> None:
    """claude.ai rejects any frontmatter key outside UPLOAD_KEYS (e.g. Claude Code's argument-hint), so drop them."""
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^(---\r?\n)(.*?)(\r?\n---\r?\n)", text, re.S)
    keep = [ln for ln in m.group(2).splitlines() if re.match(r"([A-Za-z_-]+):", ln).group(1) in UPLOAD_KEYS]
    skill_md.write_text(m.group(1) + "\n".join(keep) + m.group(3) + text[m.end():], encoding="utf-8", newline="")


def check_frontmatter(skill: str, fm: dict) -> list:
    errs = []
    extra = set(fm) - UPLOAD_KEYS
    if extra:
        errs.append(f"frontmatter keys claude.ai rejects: {', '.join(sorted(extra))}")
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != skill:
        errs.append(f"name '{name}' must equal the folder name '{skill}'")
    if not NAME.match(name) or "anthropic" in name or "claude" in name:
        errs.append(f"name '{name}': lowercase letters, digits, hyphens, max 64, no 'anthropic'/'claude'")
    if not desc or len(desc) > 1024 or re.search(r"<[^>]+>", desc):
        errs.append(f"description: non-empty, max 1024 characters, no XML tags (has {len(desc)})")
    return errs


def rewrite_links(md: Path, src_dir: Path, pkg_root: Path, skill_src: Path) -> None:
    """Point links that went from the skill into the repo's core/ at the copy inside the package."""
    core_src = REPO / SHARED

    def fix(m):
        target = m.group(2)
        if "://" in target or target.startswith(("mailto:", "/")):
            return m.group(0)
        resolved = Path(os.path.normpath(src_dir / target))
        try:
            rel_core = resolved.relative_to(core_src)
        except ValueError:
            return m.group(0)
        new_abs = pkg_root / SHARED / rel_core
        new = Path(os.path.relpath(new_abs, md.parent)).as_posix()
        return f"{m.group(1)}{new}{m.group(3) or ''}{m.group(4)}"

    text = md.read_text(encoding="utf-8")
    new = LINK.sub(fix, text)
    if new != text:
        md.write_text(new, encoding="utf-8", newline="")


def broken_links(pkg_root: Path) -> list:
    bad = []
    for md in pkg_root.rglob("*.md"):
        for m in LINK.finditer(CODE.sub("", md.read_text(encoding="utf-8"))):
            target = m.group(2)
            if "://" in target or target.startswith(("mailto:", "/")):
                continue
            dest = Path(os.path.normpath(md.parent / target))
            if not dest.exists():
                bad.append(f"{md.relative_to(pkg_root.parent).as_posix()}: {target} (missing)")
            elif pkg_root not in dest.parents and dest != pkg_root:
                bad.append(f"{md.relative_to(pkg_root.parent).as_posix()}: {target} (outside the package)")
    return bad


def build(skill: str, out: Path, stage: Path) -> Path:
    src = REPO / skill
    pkg = stage / skill
    shutil.copytree(src, pkg, ignore=IGNORE)
    shutil.copytree(REPO / SHARED, pkg / SHARED, ignore=IGNORE)
    strip_upload_keys(pkg / "SKILL.md")
    for md in pkg.rglob("*.md"):
        rel = md.relative_to(pkg)
        if rel.parts[0] == SHARED:
            continue  # core's own links are relative to core and stay valid
        rewrite_links(md, (src / rel).parent, pkg, src)
    errs = check_frontmatter(skill, frontmatter(pkg / "SKILL.md")) + broken_links(pkg)
    if errs:
        raise SystemExit(f"{skill}:\n  " + "\n  ".join(errs))
    out.mkdir(parents=True, exist_ok=True)
    zpath = out / f"{skill}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for f in sorted(p for p in pkg.rglob("*") if p.is_file()):
            info = zipfile.ZipInfo(f.relative_to(stage).as_posix(), FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if f.suffix == ".py" else 0o644) << 16
            z.writestr(info, f.read_bytes())
    return zpath


def main(argv) -> int:
    def opt(flag):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None

    if "-h" in argv or "--help" in argv:
        print(__doc__)
        return 0
    out = Path(opt("--out") or REPO / "dist").expanduser().resolve()
    skills = opt("--skills").split(",") if opt("--skills") else repo_skills()
    unknown = [s for s in skills if s not in repo_skills()]
    if unknown:
        print(f"unknown skill(s): {', '.join(unknown)}")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        for skill in skills:
            z = build(skill, out, Path(tmp))
            with zipfile.ZipFile(z) as zf:
                n = len(zf.namelist())
            print(f"{z}  {z.stat().st_size // 1024} KB  {n} files")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
