#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""ds-audit mechanics — Python 3.8+ stdlib only. Everything countable is done here; the model writes findings.

A run leaves ds/audit/report.md (machine state in its first line, then Closing, Phases, Findings, Notes; the model
appends Findings rows and Notes lines, this script writes the rest) and ds/audit/report.html (the same report for
people: self-contained, responsive, light/dark, printable), both git-excluded.

  audit.py init [WORD ...]           start or resume a run: fetch, fast-forward, scope, signals, check command,
                                     phase plan; prints JSON (what runs next and why)
  audit.py checks baseline|now       run each step of the check command; record pass/fail/timeout per step
  audit.py scan PHASE                run the Mech commands of the phase's loaded rules; prints JSON hits
  audit.py signal KEY VALUE          confirm or correct a judged signal (auth, pii, audience);
                                     re-plans the areas of phases not yet started
  audit.py validate                  Findings schema, rule IDs, file:line, commits, totals; exit 1 = red
  audit.py phase PHASE done|blocked [REASON]   close a phase (done refuses open rows or a red validate)
  audit.py report                    rewrite Closing + Phases, write report.html, print the closing message (kernel §6)
  audit.py lean [--depth N]          lean inventory: units, lines, fan-in, commits, deps, docs, entry points
  audit.py lean-check [SCOPE.md]     every unit tiered, no stale or unapplied rows, Budget holds; exit 1 = red
  audit.py rules [--since SHA] [--also PATH ...]   recorded rules with blame date, subject, absolute, reason, refs
  audit.py --self-test               prove every command on temp repos

Global option: --root DIR (default: the current directory). Words: all, dry, ask, auto, a phase name, area words.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = next((d for d in (HERE.parent / "core", HERE.parent.parent / "core") if (d / "ds_detect.py").is_file()), None)
if CORE is None:
    sys.exit("audit.py: core/ds_detect.py not found next to this skill — reinstall dev-skills (python3 install.py)")
sys.path.insert(0, str(CORE))
from ds_detect import SRC, check_cmd, deps, files, git, isolate_git, line, read, signals  # noqa: E402

PHASES = ("lean", "build", "safe", "surface", "ship")
SEVS = ("CRITICAL", "HIGH", "MEDIUM", "LOW")
REPORT = Path("ds") / "audit" / "report.md"
BRANCH = "ds/audit"  # every commit of an all / phase / area run lands here; the owner reviews and merges it once
STATE = re.compile(r"^<!-- ds-audit-state (.*) -->$", re.M)
COLS = ("#", "Phase", "Sev", "Area", "Rule", "Where", "Finding", "Prevents", "Plan", "Disposition", "Commit")
DISPOSITION = re.compile(r"^(open|fixed|reverted \(.+\)|skipped \(.+\)|not applicable \(.+\)|only you can do \(.+\))$")
CLOSED = ("fixed", "not applicable")
DOC = {".md", ".rst", ".adoc", ".txt"}
STEP_TIMEOUT = 900
SCAN_TIMEOUT = 120
ENV = dict(os.environ, CI="1", GIT_PAGER="cat", GIT_EDITOR="true", PAGER="cat", GIT_TERMINAL_PROMPT="0")


# --- rule index -------------------------------------------------------------------------------------------

def area_table(core: Path = None) -> list:
    """core/rules/README.md rows: word, phase, rule files, load-when expression."""
    rows, text = [], read((core or CORE) / "rules" / "README.md")
    for ln in text.splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) < 4 or not re.match(r"^`[\w-]+`$", cells[0]):
            continue
        plain = re.sub(r"\[[^\]]*\]\([^)]*\)", "", cells[2])  # templates load on fix, not on detect
        rows.append({"word": cells[0].strip("`"), "phase": cells[1].strip("`"),
                     "files": [f for f in re.findall(r"[\w./-]+\.md", plain)], "when": cells[3]})
    return rows


def loads(expr: str, sig: dict) -> tuple:
    """(True|False, reason) for a load-when expression: `always`, `k=v`, `k≠v`, `k∋v`, joined by `or`; unknown loads."""
    expr = re.sub(r"\(.*?\)", "", expr).strip()
    if expr in ("always", "") or "always" in expr.split(" or "):
        return True, ""
    misses = []
    for term in re.split(r"\s+or\s+|,\s*or\s+", expr):
        m = re.match(r"`?(\w+)\s*(=|≠|∋)\s*([\w-]+)`?", term.strip())
        if not m:
            return True, ""  # a condition this script cannot read loads the area (never silently skipped)
        key, op, val = m.groups()
        have = (sig.get(key) or {}).get("value", "unknown")
        values = set(have.split(","))
        if have == "unknown":
            return True, f"{key}=unknown"
        if (op == "=" and val in values) or (op == "∋" and val in values) or (op == "≠" and values != {val}):
            return True, ""
        misses.append(f"{key}={have}")
    return False, "N/A — " + ", ".join(misses)


def rule_ids(core: Path = None) -> set:
    core, ids = core or CORE, set()
    for f in (core / "rules").glob("*.md"):
        ids |= set(re.findall(r"^### (\S+) \[", read(f), re.M))
    kernel = read(core / "kernel.md")
    sec7 = kernel[kernel.find("## 7."):]
    ids |= {n.strip() for n in re.findall(r"^\| ([^|]+?) \|", sec7, re.M) if n.strip() not in ("Principle", "-")}
    return ids | {"judgment"}


# --- report file ------------------------------------------------------------------------------------------

def load(root: Path):
    text = read(root / REPORT)
    m = STATE.search(text)
    return (json.loads(m.group(1)) if m else None), text


def section(text: str, name: str) -> str:
    m = re.search(r"^## " + name + r"\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def write(root: Path, state: dict, closing: str = "", phases: str = "", findings: str = "", notes: str = ""):
    path = root / REPORT
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "| " + " | ".join(COLS) + " |\n|" + "|".join("---" for _ in COLS) + "|\n"
    body = (f"<!-- ds-audit-state {json.dumps(state, ensure_ascii=False)} -->\n# ds-audit report\n\n"
            f"## Closing\n{closing or '(written by audit.py report)'}\n\n## Phases\n{phases}\n\n"
            f"## Findings\n{findings or header}\n## Notes\n{notes or '(decided: … · only-you: … — one per line)'}\n")
    tmp = path.with_suffix(".tmp")
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(path)  # atomic: a run cut short never leaves half a report


def rows(text: str) -> list:
    out = []
    for ln in section(text, "Findings").splitlines():
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) == len(COLS) and cells[0].isdigit():
            out.append(dict(zip(COLS, cells)))
    return out


def save_state(root: Path, state: dict):
    _, text = load(root)
    write(root, state, section(text, "Closing").strip(), section(text, "Phases").strip(),
          section(text, "Findings"), section(text, "Notes").strip())


# --- init -------------------------------------------------------------------------------------------------

def parse_words(words) -> dict:
    flat = [w.lstrip("-") for arg in words for w in re.split(r"[,\s=]+", arg) if w.strip("-")]
    known = {r["word"] for r in area_table()}
    out = {"all": "all" in flat, "dry": "dry" in flat, "ask": "ask" in flat, "auto": "auto" in flat,
           "phases": [w for w in flat if w in PHASES], "areas": [w for w in flat if w in known and w not in PHASES],
           "path": next((w for w in flat if "/" in w or w == "."), None)}
    out["unknown"] = [w for w in flat if w not in ("all", "dry", "ask", "auto") and w not in PHASES and w not in known
                      and w != out["path"]]
    return out


def init(root: Path, words) -> dict:
    state, text = load(root)
    if state and any(p["status"] in ("pending", "running") for p in state["phases"].values()):
        nxt = next(n for n in PHASES if state["phases"].get(n, {}).get("status") in ("pending", "running"))
        return {"resume": True, "report": str(REPORT), "next": nxt, "plan": state["phases"],
                "signals": state["signals"], "check": state["check"]}
    w = parse_words(words)
    if w["unknown"]:
        raise SystemExit(f"audit.py init: unknown word(s) {w['unknown']} — expected all, dry, ask, a phase "
                         f"({', '.join(PHASES)}) or an area word from core/rules/README.md")
    if w["ask"] and w["auto"]:
        raise SystemExit("audit.py init: `ask` and `auto` exclude each other — `ask` asks every decision, "
                         "`auto` decides every one; pick one")
    is_git = bool(git(root, "rev-parse", "--git-dir"))
    notes = []
    if not is_git:
        w["dry"] = True
        notes.append("decided: no git repository — run is dry (no commits possible, no changed scope)")
    start = git(root, "rev-parse", "HEAD").strip()
    if is_git:
        if subprocess.run(["git", "-C", str(root), "fetch", "--prune", "--quiet"], capture_output=True, env=ENV,
                          timeout=90).returncode != 0:
            notes.append("decided: git fetch failed (offline or no remote) — audited against the local upstream ref")
        st = git(root, "status", "--porcelain=v2", "--branch", "-uall")
        ab = re.search(r"^# branch\.ab \+(\d+) -(\d+)", st, re.M)
        ahead, behind = (int(ab.group(1)), int(ab.group(2))) if ab else (0, 0)
        if behind and not ahead:
            ok = subprocess.run(["git", "-C", str(root), "merge", "--ff-only", "--quiet", "@{u}"], capture_output=True,
                                env=ENV, timeout=60).returncode == 0
            notes.append(f"decided: fast-forwarded {behind} commit(s) from upstream" if ok else
                         f"only-you: branch is {behind} behind and fast-forward was refused — `git pull --ff-only`")
            start = git(root, "rev-parse", "HEAD").strip()
        elif behind and ahead:
            mt = subprocess.run(["git", "-C", str(root), "merge-tree", "--write-tree", "--name-only", "HEAD", "@{u}"],
                                capture_output=True, text=True, env=ENV, timeout=60)  # git >= 2.38; changes nothing
            clash = [ln for ln in mt.stdout.splitlines()[1:] if ln and not ln.startswith(("Auto-merging", "CONFLICT"))]
            notes.append(f"only-you: branch diverged (behind {behind}, ahead {ahead}) — audited without rebasing; "
                         "integrate with `git pull --rebase` when ready"
                         + (f"; would conflict: {', '.join(clash[:10])}" if mt.returncode == 1 and clash else ""))
        exclude = root / ".git" / "info" / "exclude"
        if exclude.parent.is_dir() and "ds/audit/" not in read(exclude):
            with exclude.open("a", encoding="utf-8") as f:
                f.write("\nds/audit/\n")
    base = git(root, "rev-parse", "--abbrev-ref", "@{u}").strip() or git(root, "rev-parse", "--abbrev-ref",
                                                                          "origin/HEAD").strip()
    if w["all"] or w["phases"] or w["areas"]:
        scope = "all" if w["all"] or not (w["phases"] or w["areas"]) else "named"
        changed = []
    else:
        scope = "changed"
        diff = git(root, "diff", "--name-only", f"{base}...HEAD").split() if base else []
        changed = sorted(set(diff) | {ln[3:] for ln in git(root, "status", "--porcelain").splitlines()})
        if not base:
            notes.append("decided: no upstream — changed scope is uncommitted files only")
    home = git(root, "rev-parse", "--abbrev-ref", "HEAD").strip()
    branch = home
    if is_git and scope != "changed" and not w["dry"] and home != BRANCH:
        exists = bool(git(root, "rev-parse", "--verify", "--quiet", BRANCH))
        r = subprocess.run(["git", "-C", str(root), "switch", *([] if exists else ["-c"]), BRANCH],
                           capture_output=True, text=True, env=ENV, timeout=60)
        if r.returncode == 0:
            branch = BRANCH
            notes.append(f"decided: commits go to the local branch {BRANCH} ({'resumed' if exists else 'new'}); "
                         f"{home} is not touched")
            start = git(root, "rev-parse", "HEAD").strip() if not exists else start
        else:
            w["dry"] = True
            notes.append(f"only-you: could not switch to {BRANCH} ({r.stderr.strip()[-160:]}) — run is dry; "
                         f"commit or stash, then rerun")
    if branch == BRANCH:
        for wf in (n for n in files(root) if re.match(r"^\.github/workflows/.+\.ya?ml$", n)):
            body = read(root / wf)
            if re.search(r"^\s*(on:\s*\[?[^\n]*\bpush\b|push\s*:)", body, re.M) and "branches" not in body:
                notes.append(f"decided: pushing {BRANCH} triggers {wf} (runs on a push to any branch)")
    sig = signals(root)
    cmd = check_cmd(root)
    plan = make_plan(sig, w, scope, root)
    if not cmd:
        notes.append("decided: no runnable check found — Verification gap (HIGH); fixes limited to Category A")
    if scope == "changed" and not changed:
        notes.append("decided: nothing changed — /ds-audit all audits the whole project")
        for p in plan.values():
            p["status"] = "skipped"
    state = {"v": 1, "words": {k: w[k] for k in ("phases", "areas")}, "sig": sig, "start": start,
             "home": home, "branch": branch, "started": int(time.time()), "base": base, "scope": scope, "changed": changed,
             "dry": w["dry"], "ask": w["ask"], "auto": w["auto"], "carried": 0, "signals": line(sig), "check": cmd, "checks": {}, "phases": plan}
    carried = [r for r in rows(text) if not r["Disposition"].startswith(CLOSED)] if text else []
    findings = "| " + " | ".join(COLS) + " |\n|" + "|".join("---" for _ in COLS) + "|\n" + "".join(
        "| " + " | ".join([str(i)] + [r[c] for c in COLS[1:9]] + ["open", "—"]) + " |\n"
        for i, r in enumerate(carried, 1))
    state["carried"] = len(carried)
    write(root, state, findings=findings, notes="\n".join(notes))
    nxt = next((n for n, p in plan.items() if p["status"] == "pending"), None)
    return {"resume": False, "report": str(REPORT), "next": nxt, "scope": scope, "changed": len(changed),
            "carried_open": len(carried), "plan": plan, "signals": state["signals"], "check": cmd, "notes": notes}


def make_plan(sig: dict, w: dict, scope: str, root: Path) -> dict:
    plan = {}
    for p in PHASES:
        areas = {}
        for r in (r for r in area_table() if r["phase"] == p):
            named = r["word"] in w["areas"] or p in w["phases"]
            if (w["areas"] or w["phases"]) and not named:
                continue
            ok, why = loads(r["when"], sig)
            if p == "lean" and scope == "changed" and r["word"] == "rules":
                ok, why = False, "N/A — changed scope; /ds-audit rules reviews recorded rules"
            areas[r["word"]] = "ran" if ok or named else why
        if areas:
            plan[p] = {"status": "pending" if any(v == "ran" for v in areas.values()) else "skipped", "areas": areas}
    return plan


def set_signal(root: Path, key: str, value: str) -> dict:
    state, _ = load(root)
    if not state:
        raise SystemExit("audit.py signal: no run — start with `audit.py init`")
    if key not in state["sig"]:
        raise SystemExit(f"audit.py signal: unknown key '{key}' — one of {sorted(state['sig'])}")
    state["sig"][key] = {"value": value, "by": "confirmed"}
    state["signals"] = line(state["sig"])
    fresh = make_plan(state["sig"], dict(state["words"], all=False), state["scope"], root)
    for p, plan in fresh.items():
        if state["phases"].get(p, {}).get("status", "pending") in ("pending", "skipped"):
            state["phases"][p] = plan
    save_state(root, state)
    return {"signals": state["signals"], "plan": state["phases"]}


# --- checks -----------------------------------------------------------------------------------------------

def checks(root: Path, which: str) -> dict:
    state, _ = load(root)
    if not state:
        raise SystemExit("audit.py checks: no run — start with `audit.py init`")
    result = {}
    for step in [s.strip() for s in state["check"].split(" && ") if s.strip()]:
        try:
            r = subprocess.run(step, shell=True, cwd=str(root), capture_output=True, text=True, env=ENV,
                               timeout=STEP_TIMEOUT)
            result[step] = {"status": "pass" if r.returncode == 0 else "fail",
                            "tail": (r.stdout + r.stderr).strip()[-1500:]}
        except subprocess.TimeoutExpired:
            result[step] = {"status": "timeout", "tail": f"no result in {STEP_TIMEOUT}s"}
    state["checks"][which] = {k: v["status"] for k, v in result.items()}
    save_state(root, state)
    return result


# --- scan -------------------------------------------------------------------------------------------------

MECH = re.compile(r"^- \*\*Mech:\*\* ([STM])\b(.*)$", re.M)


def scan(root: Path, phase: str, core: Path = None) -> list:
    core = core or CORE
    state, _ = load(root)
    sig = state["sig"] if state else signals(root)
    out = []
    for r in area_table(core):
        if r["phase"] != phase:
            continue
        if state and state["phases"].get(phase, {}).get("areas", {}).get(r["word"]) != "ran":
            continue
        if not state and not loads(r["when"], sig)[0]:
            continue
        for fname in r["files"]:
            text = read(core / "rules" / fname)
            for block in re.split(r"^(?=### )", text, flags=re.M):
                head = re.match(r"^### (\S+) \[", block)
                m = MECH.search(block)
                if not head or not m or m.group(1) == "M":
                    continue
                when = re.search(r"^applies_when:\s*(.+)$", block, re.M)
                ok, why = loads(when.group(1), sig) if when else (True, "")
                if not ok:  # the rule's own narrowing: reported, not run, so a hit never comes from a rule that does not apply
                    out.append({"rule": head.group(1), "class": m.group(1), "status": "not applicable", "reason": why})
                    continue
                for cmd in re.findall(r"`([^`]+)`", m.group(2)):
                    out.append(run_mech(root, head.group(1), m.group(1), cmd, state))
    return out


def run_mech(root: Path, rid: str, cls: str, cmd: str, state) -> dict:
    q = shlex.quote  # a ref name may hold `;`, `$` or `(`: never pass it to the shell bare
    cmd = cmd.replace("{base}", q((state or {}).get("base") or "HEAD")).replace(
        "{audit}", f'{q(sys.executable)} -B {q(str(HERE / "audit.py"))} --root {q(str(root))}')
    tool = cmd.split()[0].strip('"')
    row = {"rule": rid, "class": cls, "cmd": cmd}
    if tool not in ("git", "grep", "test", "find") and not shutil.which(tool):
        return dict(row, status="tool absent")
    try:
        r = subprocess.run(cmd, shell=True, cwd=str(root), capture_output=True, text=True, env=ENV,
                           timeout=SCAN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return dict(row, status="timeout")
    lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if r.returncode not in (0, 1) and not lines:
        return dict(row, status="error", detail=r.stderr.strip()[-300:])
    return dict(row, status="hit" if lines else "clean", hits=lines[:50], more=max(0, len(lines) - 50))


# --- validate ---------------------------------------------------------------------------------------------

def validate(root: Path, core: Path = None) -> list:
    state, text = load(root)
    if not state:
        return ["no run — start with `audit.py init`"]
    ids, problems, seen = rule_ids(core), [], set()
    areas = {r["word"] for r in area_table(core)}
    for r in rows(text):
        n = r["#"]
        if n in seen:
            problems.append(f"row {n}: number used twice")
        seen.add(n)
        if r["Phase"] not in PHASES:
            problems.append(f"row {n}: phase '{r['Phase']}' not in {PHASES}")
        if r["Sev"] not in SEVS:
            problems.append(f"row {n}: severity '{r['Sev']}' not in {SEVS}")
        if r["Area"] not in areas:
            problems.append(f"row {n}: area '{r['Area']}' unknown")
        for rid in re.split(r"\s*[·,]\s*", r["Rule"]):
            if rid not in ids and not rid.startswith("tool:"):
                problems.append(f"row {n}: rule '{rid}' is not a rule ID, a kernel §7 principle, tool:<name> or judgment")
        m = re.match(r"^`?(.+?):(\d+)(?:-\d+)?`?$", r["Where"])
        if m:
            path, ln = m.group(1), int(m.group(2))
            now = root / path
            old = git(root, "show", f"{state['start']}:{path}") if state.get("start") else ""
            count = max(read(now).count("\n") + 1 if now.is_file() else 0, old.count("\n") + 1 if old else 0)
            if not count:
                problems.append(f"row {n}: {path} does not exist (now or at the run's start)")
            elif ln > count:
                problems.append(f"row {n}: {path} has {count} lines, row cites line {ln}")
        if not DISPOSITION.match(r["Disposition"]):
            problems.append(f"row {n}: disposition '{r['Disposition']}' not one of open · fixed · reverted (error) · "
                            "skipped (blocker) · not applicable (reason) · only you can do (action)")
        c = r["Commit"]
        if r["Disposition"] == "fixed" and c != "uncommitted":
            if not re.match(r"^[0-9a-f]{7,40}$", c) or not git(root, "rev-parse", "--verify", "--quiet", c + "^{commit}"):
                problems.append(f"row {n}: fixed needs a commit hash of this repo (or 'uncommitted'), got '{c}'")
            elif state.get("start") and subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor",
                                                        state["start"], c], capture_output=True).returncode != 0:
                problems.append(f"row {n}: commit {c} is not after the run's start")
        if r["Disposition"] == "fixed" and state.get("dry"):
            problems.append(f"row {n}: fixed in a dry run")
    return problems


# --- phases and report ------------------------------------------------------------------------------------

def phase(root: Path, name: str, status: str, reason: str = "") -> str:
    state, text = load(root)
    if not state or name not in state["phases"]:
        raise SystemExit(f"audit.py phase: '{name}' is not in this run's plan {list((state or {}).get('phases', {}))}")
    if status == "done":
        bad = validate(root)
        open_rows = [r["#"] for r in rows(text) if r["Phase"] == name and r["Disposition"] == "open"]
        if bad or open_rows:
            raise SystemExit("audit.py phase: not done — " + "; ".join(bad + [f"open rows {open_rows}"] * bool(open_rows)))
    elif status != "blocked" or not reason:
        raise SystemExit("audit.py phase: use `done`, or `blocked \"<concrete blocker>\"`")
    state["phases"][name]["status"] = status
    if reason:
        state["phases"][name]["reason"] = reason
    save_state(root, state)
    if status == "done":
        push(root, state)
    return next((n for n, p in state["phases"].items() if p["status"] == "pending"), "")


def push(root: Path, state: dict):
    """Back up the review branch after each closed phase: no force, no other ref; refused -> only-you."""
    if state.get("branch") != BRANCH or state.get("dry") or "origin" not in git(root, "remote").split():
        return
    try:
        r = subprocess.run(["git", "-C", str(root), "push", "--quiet", "-u", "origin", BRANCH], capture_output=True,
                           text=True, env=ENV, timeout=120)
        ok, why = r.returncode == 0, r.stderr.strip()[-160:]
    except subprocess.TimeoutExpired:
        ok, why = False, "timeout"
    if not ok:
        _, text = load(root)
        notes = section(text, "Notes").strip()
        line_ = f"only-you: push of {BRANCH} refused ({why}) — fix the remote side, then `git push -u origin {BRANCH}`"
        if line_ not in notes:
            state, _ = load(root)
            write(root, state, section(text, "Closing").strip(), section(text, "Phases").strip(),
                  section(text, "Findings"), (notes + "\n" + line_).strip())


def status_of(state: dict, findings: list) -> str:
    if any(p["status"] in ("pending", "running", "blocked") for p in state["phases"].values()):
        return "INCOMPLETE"
    open_ = [r for r in findings if not r["Disposition"].startswith(CLOSED)]
    base, now = state["checks"].get("baseline", {}), state["checks"].get("now", {})
    newly_red = [s for s, v in now.items() if v != "pass" and base.get(s) == "pass"]
    if any(r["Sev"] == "CRITICAL" for r in open_) or newly_red:
        return "FAIL"
    if any(r["Sev"] == "HIGH" for r in open_) or not state["check"] or (state["check"] and not now):
        return "WARN"
    return "OK"


def report(root: Path) -> str:
    state, text = load(root)
    if not state:
        raise SystemExit("audit.py report: no run — start with `audit.py init`")
    findings = rows(text)
    status = status_of(state, findings)
    minutes = max(1, round((time.time() - state["started"]) / 60))
    stat = git(root, "diff", "--shortstat", state["start"]).strip() if state["start"] else ""
    got = {k: int(v) for v, k in re.findall(r"(\d+) (file|insertion|deletion)", stat)}
    commits = git(root, "rev-list", "--count", f"{state['start']}..HEAD").strip() if state["start"] else "0"
    fixed = [r for r in findings if r["Disposition"] == "fixed"]
    only = [r for r in findings if r["Disposition"].startswith("only you")]
    open_ = [r for r in findings if not r["Disposition"].startswith(CLOSED) and r not in only]
    notes = section(text, "Notes")
    decided = [ln.split(":", 1)[1].strip() for ln in notes.splitlines() if ln.startswith("decided:")]
    only_lines = [ln.split(":", 1)[1].strip() for ln in notes.splitlines() if ln.startswith("only-you:")]
    only_lines += [f"{r['Where']}: {r['Disposition'][len('only you can do ('):-1]}" for r in only]
    if state.get("branch") == BRANCH and commits not in ("", "0"):
        only_lines.append(f"review and merge {BRANCH}: `git diff {state['start'][:12]}...{BRANCH}` · "
                          f"`git switch {state['home']}` · `git merge --ff-only {BRANCH}` · `git branch -d {BRANCH}` · "
                          f"`git push origin --delete {BRANCH}` (or drop it all: `git branch -D {BRANCH}`)")
    scope = f"changed: {len(state['changed'])} files" if state["scope"] == "changed" else state["scope"]
    out = [f"ds-audit: {status} · {minutes} min · scope {scope} · findings {len(findings)} · fixed {len(fixed)} · "
           f"open {len(open_)} · only-you {len(only)}",
           f"Asked: /ds-audit {state['scope']}" + "".join(f" {k}" for k in ("dry", "ask", "auto") if state.get(k)), "",
           "| Change | Files | Lines | Commits |", "|--------|------:|------:|--------:|",
           f"| code | {got.get('file', 0)} | +{got.get('insertion', 0)} −{got.get('deletion', 0)} | {commits} |", ""]
    if findings:
        order = sorted(findings, key=lambda r: (SEVS.index(r["Sev"]) if r["Sev"] in SEVS else 9,
                                                r["Disposition"] != "fixed", int(r["#"])))
        out += ["| # | Sev | Where | Finding | Outcome | Prevents / gains |", "|---|-----|-------|---------|---------|---|"]
        for r in order[:15]:
            outcome = r["Disposition"] + (f" {r['Commit']}" if r["Disposition"] == "fixed" else "")
            out.append(f"| {r['#']} | {r['Sev']} | {r['Where']} | {r['Finding']} | {outcome} | {r['Prevents']} |")
        if len(order) > 15:
            out.append(f"+{len(order) - 15} more in {REPORT}")
    else:
        out.append("No findings")
    base, now = state["checks"].get("baseline", {}), state["checks"].get("now", {})
    effect = [f"{s}: {base.get(s, '—')} → {now.get(s, '—')}" for s in (base or now)]
    out += ["", "Effect: " + ("; ".join(effect) if effect else "no check ran")]
    if state.get("carried"):
        prior = [r for r in findings if int(r["#"]) <= state["carried"]]
        out.append(f"Since the last run: {len(findings) - len(prior)} new · "
                   f"{sum(r['Disposition'] == 'fixed' for r in prior)} of {len(prior)} carried fixed · "
                   f"{sum(not r['Disposition'].startswith(CLOSED) for r in prior)} still open")
    if decided:
        out.append("Decided without asking — say if wrong: " + "; ".join(decided))
    if only_lines:
        out.append("Only you can do: " + "; ".join(only_lines))
    closing = "\n".join(out)
    phases_md = "| Phase | Status | Areas |\n|---|---|---|\n" + "".join(
        f"| {n} | {p['status']}{' — ' + p['reason'] if p.get('reason') else ''} | "
        + " · ".join(f"{a} {v}" for a, v in p["areas"].items()) + " |\n" for n, p in state["phases"].items())
    phases_md += f"\n{state['signals']}\n"
    write(root, state, closing, phases_md, section(text, "Findings"), notes.strip())
    page = root / REPORT.with_suffix(".html")
    page.write_text(render_html(root, state, findings, status, minutes, got, commits, decided, only_lines),
                    encoding="utf-8")
    return closing


# --- html report ------------------------------------------------------------------------------------------

CSS = """
:root{--plane:#f3f5f8;--surface:#fff;--ink:#16202c;--ink-2:#566274;--line:#d9dfe7;--accent:#1d5fd1;
--ok:#17794a;--ok-bg:#dff3e8;--warn:#8f5a00;--warn-bg:#fcefd0;--bad:#b3261e;--bad-bg:#fae3e0;--info:#1d5fd1;
--info-bg:#e2ebfa;--mute:#69727f;--mute-bg:#eceff3;color-scheme:light}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--plane:#0f1318;--surface:#181d24;--ink:#e6eaf0;
--ink-2:#9ba5b3;--line:#2b323c;--accent:#7aa5ff;--ok:#52c485;--ok-bg:#14301f;--warn:#e6b24d;--warn-bg:#362b12;
--bad:#f08077;--bad-bg:#3b1c19;--info:#7aa5ff;--info-bg:#1a2742;--mute:#8c96a4;--mute-bg:#242a33;color-scheme:dark}}
:root[data-theme=dark]{--plane:#0f1318;--surface:#181d24;--ink:#e6eaf0;--ink-2:#9ba5b3;--line:#2b323c;
--accent:#7aa5ff;--ok:#52c485;--ok-bg:#14301f;--warn:#e6b24d;--warn-bg:#362b12;--bad:#f08077;--bad-bg:#3b1c19;
--info:#7aa5ff;--info-bg:#1a2742;--mute:#8c96a4;--mute-bg:#242a33;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--plane);color:var(--ink);font:13.5px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,
"Helvetica Neue",Arial,sans-serif;-webkit-text-size-adjust:100%}
.page{max-width:1080px;margin:0 auto;padding-block:16px 32px;padding-left:max(16px,env(safe-area-inset-left,0px));
padding-right:max(16px,env(safe-area-inset-right,0px))}
.top{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:flex-end;justify-content:space-between;margin-bottom:10px}
h1{margin:0;font-size:22px;letter-spacing:-.02em}.sub{color:var(--ink-2);font-size:12.5px;margin-top:2px}
.badge{display:inline-flex;align-items:center;gap:4px;font-size:11.5px;font-weight:600;border-radius:999px;
padding:2px 9px;white-space:nowrap}
.b-ok{background:var(--ok-bg);color:var(--ok)}.b-warn{background:var(--warn-bg);color:var(--warn)}
.b-bad{background:var(--bad-bg);color:var(--bad)}.b-info{background:var(--info-bg);color:var(--info)}
.b-mute{background:var(--mute-bg);color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:10px;margin-top:10px}
.grid>*{min-width:0}
.card{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:10px 12px;min-width:0;
overflow-wrap:anywhere}
.card h2{margin:0 0 6px;font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--ink-2)}
.wide{margin-top:10px}
.kpi{display:grid;grid-template-columns:auto 1fr;gap:12px;align-items:center}
.ring{width:84px;height:84px}.ring circle{fill:none;stroke-width:10}.ring .base{stroke:var(--mute-bg)}
.ring text{fill:var(--ink);font-weight:800;font-size:22px}
.status{font-size:16px;font-weight:800}.row{display:flex;flex-wrap:wrap;gap:5px;margin-top:4px}
.note{font-size:11.5px;color:var(--ink-2);margin-top:4px}
ul.plain{margin:0;padding-left:18px;display:grid;gap:3px;font-size:12.5px}
.phase{display:flex;justify-content:space-between;gap:8px;align-items:center;font-weight:700}
.areas{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
.wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;font-weight:600;color:var(--ink-2);font-size:11px;padding:4px;border-bottom:1px solid var(--line)}
td{padding:6px 4px;border-bottom:1px solid var(--line);vertical-align:top}
td.id{font-variant-numeric:tabular-nums;color:var(--ink-2)}
code,pre{font:11.5px/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{margin:0;white-space:pre-wrap;word-break:break-word;background:var(--plane);border:1px solid var(--line);
border-radius:8px;padding:8px}
.toggle{font:inherit;font-size:12px;font-weight:600;color:var(--ink);background:var(--surface);
border:1px solid color-mix(in srgb,var(--ink) 28%,transparent);border-radius:999px;padding:3px 11px;cursor:pointer}
.toggle:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
@media (max-width:560px){thead{display:none}tr{display:grid;grid-template-columns:auto 1fr;gap:2px 8px;padding:6px 0;
border-bottom:1px solid var(--line)}td{border:0;padding:1px 0}td[data-k]:not(.id)::before{content:attr(data-k) ": ";
color:var(--ink-2)}td:not(.id){grid-column:1 / -1}}
@page{size:A4;margin:10mm}
@media print{body{background:#fff;font-size:10.5px}.page{padding:0}.card{break-inside:avoid}.toggle{display:none}}
"""

THEME_JS = """(function(){var K="ds-audit-theme",O=["auto","light","dark"],s="auto",b=document.getElementById("theme");
try{s=localStorage.getItem(K)||"auto"}catch(e){}if(O.indexOf(s)<0)s="auto";
function a(){if(s==="auto")document.documentElement.removeAttribute("data-theme");
else document.documentElement.setAttribute("data-theme",s);b.textContent="Theme: "+s}
b.addEventListener("click",function(){s=O[(O.indexOf(s)+1)%3];try{localStorage.setItem(K,s)}catch(e){}a()});a()})();"""

SEV_BADGE = {"CRITICAL": "b-bad", "HIGH": "b-warn", "MEDIUM": "b-info", "LOW": "b-mute"}
STATUS_BADGE = {"OK": "b-ok", "WARN": "b-warn", "FAIL": "b-bad", "INCOMPLETE": "b-mute"}
PHASE_BADGE = {"done": "b-ok", "pending": "b-mute", "running": "b-info", "blocked": "b-bad", "skipped": "b-mute"}


def render_html(root: Path, state: dict, findings: list, status: str, minutes: int, got: dict, commits: str,
                decided: list, only_lines: list) -> str:
    from html import escape as e
    fixed = sum(r["Disposition"] == "fixed" for r in findings)
    only = sum(r["Disposition"].startswith("only you") for r in findings)
    open_ = sum(not r["Disposition"].startswith(CLOSED) for r in findings) - only
    pct = round(100 * fixed / len(findings)) if findings else None
    color = {"OK": "var(--ok)", "WARN": "var(--warn)", "FAIL": "var(--bad)"}.get(status, "var(--mute)")
    when = time.strftime("%Y-%m-%d %H:%M", time.localtime(state["started"]))
    mode = "".join(f" {k}" for k in ("dry", "ask", "auto") if state.get(k))
    base, now = state["checks"].get("baseline", {}), state["checks"].get("now", {})

    def badge(cls, text):
        return f'<span class="badge {cls}">{e(text)}</span>'

    checks_html = "".join(
        f"<li><code>{e(s)}</code> {badge('b-ok' if base.get(s) == 'pass' else 'b-bad', base.get(s, '—'))} → "
        f"{badge('b-ok' if now.get(s) == 'pass' else 'b-bad' if s in now else 'b-mute', now.get(s, '—'))}</li>"
        for s in (base or now)) or "<li>No check ran</li>"
    phases_html = "".join(
        f'<section class="card"><div class="phase">{e(n)} {badge(PHASE_BADGE.get(p["status"], "b-mute"), p["status"])}'
        f'</div>{"<div class=note>" + e(p["reason"]) + "</div>" if p.get("reason") else ""}<div class="areas">'
        + "".join(badge("b-ok" if v == "ran" else "b-mute", f"{a} {v}") for a, v in p["areas"].items())
        + "</div></section>" for n, p in state["phases"].items())
    order = sorted(findings, key=lambda r: (SEVS.index(r["Sev"]) if r["Sev"] in SEVS else 9,
                                            r["Disposition"] != "fixed", int(r["#"])))
    rows_html = "".join(
        f'<tr><td class="id" data-k="#">{e(r["#"])}</td><td data-k="Severity">{badge(SEV_BADGE.get(r["Sev"], "b-mute"), r["Sev"])}'
        f' <span class="note">{e(r["Phase"])} · {e(r["Area"])} · {e(r["Rule"])}</span></td>'
        f'<td data-k="Where"><code>{e(r["Where"])}</code></td><td data-k="Finding">{e(r["Finding"])}</td>'
        f'<td data-k="Prevents">{e(r["Prevents"])}</td><td data-k="Outcome">'
        f'{badge("b-ok" if r["Disposition"] == "fixed" else "b-warn" if r["Disposition"].startswith("only you") else "b-mute", r["Disposition"])}'
        f'{" <code>" + e(r["Commit"]) + "</code>" if r["Disposition"] == "fixed" else ""}</td></tr>' for r in order)
    findings_html = (f'<div class="wrap"><table><thead><tr><th>#</th><th>Severity</th><th>Where</th><th>Finding</th>'
                     f'<th>Prevents / gains</th><th>Outcome</th></tr></thead><tbody>{rows_html}</tbody></table></div>'
                     if findings else '<p class="note">No findings</p>')
    lists = "".join(
        f'<section class="card"><h2>{title}</h2><ul class="plain">{"".join("<li>" + e(x) + "</li>" for x in items)}</ul></section>'
        for title, items in (("Decided without asking — say if wrong", decided), ("Only you can do", only_lines)) if items)
    ring = (f'<circle cx="50" cy="50" r="40" stroke="{color}" stroke-dasharray="{(pct or 0) * 2.513:.1f} 252" '
            f'transform="rotate(-90 50 50)" stroke-linecap="round"/>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>ds-audit · {e(root.name)}</title><style>{CSS}</style></head><body><div class="page">
<header class="top"><div><h1>ds-audit · {e(root.name)}</h1>
<div class="sub">{e(when)} · {minutes} min · scope {e(state["scope"])}{e(mode)} · start <code>{e(state["start"][:12])}</code></div></div>
<div class="row">{badge(STATUS_BADGE.get(status, "b-mute"), status)}<button class="toggle" id="theme" type="button">Theme: auto</button></div>
</header>
<div class="grid">
<section class="card"><h2>Result</h2><div class="kpi"><svg class="ring" viewBox="0 0 100 100" role="img"
aria-label="Findings fixed"><circle class="base" cx="50" cy="50" r="40"/>{ring}<text x="50" y="58"
text-anchor="middle">{"–" if pct is None else f"{pct}%"}</text></svg><div><div class="status" style="color:{color}">{e(status)}</div>
<div class="row">{badge("b-ok", f"{fixed} fixed")}{badge("b-warn", f"{open_} open")}{badge("b-info", f"{only} only you")}</div>
<div class="note">{len(findings)} findings · code {got.get("file", 0)} files +{got.get("insertion", 0)} −{got.get("deletion", 0)} · {e(commits)} commits</div></div></div></section>
<section class="card"><h2>Checks · baseline → now</h2><ul class="plain">{checks_html}</ul></section>
</div>
<div class="grid">{phases_html}</div>
<section class="card wide"><h2>Findings</h2>{findings_html}</section>
<div class="grid">{lists}</div>
<section class="card wide"><h2>Signals</h2><pre>{e(state["signals"])}</pre></section>
</div><script>{THEME_JS}</script></body></html>
"""


# --- lean -------------------------------------------------------------------------------------------------

TEST = re.compile(r"(^|/)(tests?|__tests__|spec)(/|$)|(_test|\.test|\.spec|_spec|Tests?)\.\w+$|(^|/)test_[^/]+\.py$")
ENTRY = re.compile(r"(^|/)(main|__main__|index|app|server|cli)\.\w+$")
TIERS = re.compile(r"^(T0|T1|T2|cut|merge\s*(?:→|->)\s*\S+)$")
BUDGET = re.compile(r"\b(units|deps|docs)\s*(?:≤|<=)\s*(\d+)")
RULE_FILES = re.compile(r"(^|/)(CLAUDE|AGENTS|GEMINI|CONVENTIONS|SCOPE|DECISIONS)\.md$|(^|/)\.cursorrules$|"
                        r"(^|/)\.windsurfrules$|(^|/)\.cursor/rules/[^/]+\.mdc?$|(^|/)\.devin/rules/[^/]+\.md$|"
                        r"(^|/)\.github/copilot-instructions\.md$|(^|/)\.github/instructions/[^/]+\.md$|"
                        r"(^|/)(adrs?|decisions)/[^/]+\.md$|decision[-_ ]?log[^/]*\.md$", re.I)
ABSOLUTE = re.compile(r"\b(always|never|every|must|all|only|forbidden|mandatory)\b|her zaman|daima|asla|hiçbir|"
                      r"hiç bir|\bhep\b|kesinlikle|yalnızca|sadece|zorunlu|yasak", re.I)
REASON = re.compile(r"\b(because|so that|since|reason|why\b|otherwise|to avoid|to keep)|→|çünkü|zira|gerekçe|"
                    r"aksi halde|yoksa|\*\*Why", re.I)
RULE_ID = re.compile(r"\b[A-Z][A-Z0-9]{0,5}-\d{1,4}\b")


def unit_of(path: str, depth: int) -> str:
    return "/".join(path.split("/")[:-1][:depth]) or "."


def inventory(root: Path, depth: int = 2) -> dict:
    names = files(root)
    units, texts = {}, {}
    for n in names:
        ext = Path(n).suffix.lower()
        if ext not in SRC:
            continue
        u = units.setdefault(unit_of(n, depth), {"files": 0, "src_lines": 0, "test_lines": 0, "entry": False})
        text = read(root / n)
        lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        u["files"] += 1
        if TEST.search(n):
            u["test_lines"] += lines
        else:
            u["src_lines"] += lines
            texts.setdefault(unit_of(n, depth), []).append(text)
            if ENTRY.search(n) or (ext == ".go" and re.search(r"^package main\b", text, re.M)):
                u["entry"] = True
    for name, u in units.items():
        pats = [re.compile(r"(?<![\w.\-])" + re.escape(t) + r"(?![\w\-])")
                for t in ({name, name.replace("/", ".")} if name != "." else set())]
        u["fan_in"] = sum(1 for other, ts in texts.items() if other != name and any(p.search(t) for t in ts for p in pats))
    commits, stamps = [], []
    for chunk in git(root, "log", "--format=%x00%ct", "--name-only").split("\0")[1:]:
        head, *paths = chunk.strip().split("\n")
        stamps.append(int(head))
        commits.append({unit_of(p, depth) for p in paths if p and Path(p).suffix.lower() in SRC})
    for name, u in units.items():
        u["commits"] = sum(1 for c in commits if name in c)
    now = max(stamps) if stamps else 0
    doc_names = [n for n in names if Path(n).suffix.lower() in DOC]
    dep_list = deps(root, names)
    src_lines = sum(u["src_lines"] for u in units.values())
    test_lines = sum(u["test_lines"] for u in units.values())
    return {
        "head": git(root, "rev-parse", "--short", "HEAD").strip(), "depth": depth,
        "totals": {
            "files": len(names), "units": len(units), "src_lines": src_lines, "test_lines": test_lines,
            "test_to_src": round(test_lines / src_lines, 2) if src_lines else None,
            "doc_files": len(doc_names), "doc_kb": round(sum((root / n).stat().st_size for n in doc_names) / 1024),
            "deps_runtime": sum(1 for d in dep_list if d["kind"] == "runtime"),
            "deps_dev": sum(1 for d in dep_list if d["kind"] == "dev"),
            "commits": len(stamps), "days": round((now - min(stamps)) / 86400) + 1 if stamps else 0,
            "commits_30d": sum(1 for s in stamps if s > now - 30 * 86400),
            "commits_without_source": sum(1 for c in commits if not c),
            "branches": len(git(root, "for-each-ref", "--format=x", "refs/heads").split()),
        },
        "units": [dict(unit=k, **v) for k, v in sorted(units.items(), key=lambda kv: -kv[1]["src_lines"])],
        "deps": dep_list,
        "entry_points": sorted(k for k, v in units.items() if v["entry"]),
    }


def lean_check(root: Path, scope: Path, depth: int = 2) -> list:
    inv = inventory(root, depth)
    present = {u["unit"] for u in inv["units"]}
    text = read(scope)
    if not text:
        return [f"{scope}: missing or empty — /ds-audit lean writes it"]
    seen, cols, problems = {}, None, []
    for ln in text.splitlines():
        if not ln.lstrip().startswith("|"):
            cols = None
            continue
        cells = [c.strip().strip("`") for c in ln.strip().strip("|").split("|")]
        if cols is None:
            low = [c.lower() for c in cells]
            cols = (low.index("unit"), low.index("tier")) if "unit" in low and "tier" in low else False
            continue
        if not cols or set(ln) <= set("|-: "):
            continue
        unit, tier = cells[cols[0]], cells[cols[1]]
        if unit in seen:
            problems.append(f"unit {unit}: listed twice")
        seen[unit] = tier
        if not TIERS.match(tier):
            problems.append(f"unit {unit}: tier '{tier}' is not T0, T1, T2, cut or merge→<unit>")
        elif unit in present and not tier.startswith("T"):
            problems.append(f"unit {unit}: marked {tier} but still present — apply it or change the tier")
    problems += [f"unit {u}: no row — every unit needs a tier and the need it serves" for u in sorted(present - seen.keys())]
    problems += [f"unit {u}: row for a unit that no longer exists — remove the row"
                 for u in sorted(k for k, t in seen.items() if k not in present and t.startswith("T"))]
    m = re.search(r"^Budget:(.*)$", text, re.M)
    if not m:
        problems.append("no 'Budget:' line (units ≤ n · deps ≤ n · docs ≤ n KB)")
    actual = {"units": inv["totals"]["units"], "deps": inv["totals"]["deps_runtime"], "docs": inv["totals"]["doc_kb"]}
    for key, limit in BUDGET.findall(m.group(1) if m else ""):
        if actual[key] > int(limit):
            problems.append(f"budget: {key} {actual[key]}{' KB' if key == 'docs' else ''} > {limit}")
    return problems


def rule_lines(text: str):
    fence = False
    for n, ln in enumerate(text.splitlines(), 1):
        t = ln.strip()
        if t.startswith("```"):
            fence = not fence
            continue
        if fence or len(t) < 15 or t.startswith(("#", "---", "<!--")) or set(t) <= set("|-: "):
            continue
        yield n, t


def recorded_rules(root: Path, since: str = "", also=()) -> list:
    floor = int(git(root, "show", "-s", "--format=%ct", since).strip() or 0) if since else 0
    sources = [(root / n, n) for n in files(root) if RULE_FILES.search(n)]
    for extra in also:
        p = Path(extra).expanduser().resolve()
        if not p.exists():
            raise SystemExit(f"audit.py rules: --also {extra} does not exist")
        for f in (sorted(p.glob("*.md")) if p.is_dir() else [p]):
            sources.append((f, f.relative_to(root).as_posix() if root in f.parents else str(f)))
    items = []
    for path, label in sources:
        blame, meta, cur, sha, num = {}, {}, {}, "", 0
        porcelain = "" if Path(label).is_absolute() else git(root, "blame", "--line-porcelain", "--", label)
        for ln in porcelain.splitlines():
            head = re.match(r"^([0-9a-f]{40}) \d+ (\d+)", ln)
            if head:
                sha, num = head.group(1), int(head.group(2))
                cur = meta.setdefault(sha, {})
            elif ln.startswith("author-time "):
                cur["time"] = int(ln.split()[1])
            elif ln.startswith("summary "):
                cur["subject"] = ln[8:]
            elif ln.startswith("\t"):
                blame[num] = sha
        mtime = int(path.stat().st_mtime) if path.exists() else 0
        for n, t in rule_lines(read(path)):
            s = blame.get(n, "")
            when = meta.get(s, {}).get("time", mtime)
            if when > floor:
                items.append({"file": label, "line": n, "text": t[:400], "date": when, "commit": s[:12],
                              "subject": meta.get(s, {}).get("subject", ""),
                              "absolute": bool(ABSOLUTE.search(t)), "reason": bool(REASON.search(t))})
    corpus = "\n".join(read(root / n) for n in files(root) if Path(n).suffix.lower() in DOC | SRC)
    counts = {}
    for i in items:
        i["refs"] = sum(counts.setdefault(x, len(re.findall(r"\b" + re.escape(x) + r"\b", corpus)))
                        for x in set(RULE_ID.findall(i["text"])))
    items.sort(key=lambda i: (not (i["absolute"] and not i["reason"]), -i["refs"], i["date"]))
    for i in items:
        i["date"] = time.strftime("%Y-%m-%d", time.gmtime(i["date"])) if i["date"] else ""
    return items


# --- self-test --------------------------------------------------------------------------------------------

def self_test() -> int:
    global CORE
    fails = []
    saved = isolate_git()
    isolate_git(ENV)
    gitenv = dict(ENV, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

    def expect(ok, msg):
        if not ok:
            fails.append(msg)

    real_core = CORE
    tmp = Path(tempfile.mkdtemp(prefix="ds-audit-"))
    try:
        def w(rel, body):
            (tmp / rel).parent.mkdir(parents=True, exist_ok=True)
            (tmp / rel).write_text(body, encoding="utf-8")

        def commit(msg):
            for args in (["add", "-A"], ["commit", "-qm", msg]):
                subprocess.run(["git", "-C", str(tmp), *args], check=True, env=gitenv, capture_output=True)
            return git(tmp, "rev-parse", "--short", "HEAD").strip()

        subprocess.run(["git", "-C", str(tmp), "init", "-q"], check=True, env=gitenv, capture_output=True)
        CORE = Path(tempfile.mkdtemp(prefix="ds-audit-core-"))
        (CORE / "rules").mkdir()
        (CORE / "rules" / "README.md").write_text(
            "| Area (word) | Phase | Files | Load when | IDs | Standards |\n|---|---|---|---|---|---|\n"
            "| `lean` | lean | lean.md | always | LEAN | x |\n| `code` | build | t.md | always | T | x |\n"
            "| `sec` | safe | t.md | always | T | x |\n| `a11y` | surface | t.md | ui≠none | T | x |\n"
            "| `docs` | ship | t.md | always | T | x |\n", encoding="utf-8")
        (CORE / "rules" / "lean.md").write_text("### LEAN-03 [HIGH] Unit serving no need\n", encoding="utf-8")
        (CORE / "rules" / "t.md").write_text("### T-01 [LOW] Todo\n- **Detect:** x\n- **Mech:** S `git grep -n TODO`\n\n"
                                             "### T-02 [LOW] Absent\n- **Mech:** T `no-such-tool-xyz .`\n\n"
                                             "### T-03 [LOW] Web only\napplies_when: ui≠none\n"
                                             "- **Mech:** S `git grep -n TODO`\n",
                                             encoding="utf-8")
        (CORE / "kernel.md").write_text("## 7. Named\n| Principle | Apply as |\n|---|---|\n| YAGNI | x |\n",
                                        encoding="utf-8")
        w("go.mod", "module m\n\nrequire (\n\tgolang.org/x/sys v0.1.0\n\tgithub.com/x/y v1.0.0 // indirect\n)\n")
        w("a/x.go", "package a\n\nfunc X() int { return 1 }\n")
        w("a/x_test.go", "package a\n\nimport \"testing\"\n\nfunc TestX(t *testing.T) {}\n")
        w("cmd/app/main.go", "package main\n\nimport \"m/a\"\n\nfunc main() { a.X() }\n")
        w("vendor/v/v.go", "package v\n")
        w("README.md", "# m\n")
        w("AGENTS.md", "# Rules\n\n- Always run the full gate before any commit (GT-1).\n"
                       "- Keep the CLI flags stable so that scripts keep working.\n")
        commit("init")

        # lean inventory, SCOPE check, recorded rules
        inv = inventory(tmp)
        units = {u["unit"]: u for u in inv["units"]}
        expect(set(units) == {"a", "cmd/app"}, f"lean units {sorted(units)} (vendor skipped)")
        expect(units.get("a", {}).get("test_lines") == 5 and units["a"]["fan_in"] == 1, "lean test lines / fan-in")
        expect(inv["entry_points"] == ["cmd/app"] and inv["totals"]["deps_runtime"] == 1, "lean entry points / deps")
        good = ("Budget: units ≤ 2 · deps ≤ 1 · docs ≤ 5 KB\n\n| Unit | Tier | Serves |\n|---|---|---|\n"
                "| a | T0 | core |\n| cmd/app | T0 | entry |\n")
        for name, body, red in (("complete", good, False),
                                ("missing unit", good.replace("| cmd/app | T0 | entry |\n", ""), True),
                                ("gone unit", good + "| old | T1 | x |\n", True),
                                ("pending cut", good.replace("| a | T0 |", "| a | cut |"), True),
                                ("bad tier", good.replace("| a | T0 |", "| a | maybe |"), True),
                                ("budget", good.replace("units ≤ 2", "units ≤ 1"), True),
                                ("no budget", good.split("\n", 1)[1], True)):
            (tmp / "SCOPE.md").write_text(body, encoding="utf-8")
            expect(bool(lean_check(tmp, tmp / "SCOPE.md")) == red, f"lean-check {name}: expected {'red' if red else 'green'}")
        (tmp / "SCOPE.md").unlink()
        items = recorded_rules(tmp)
        expect(len(items) == 2 and items[0]["absolute"] and not items[0]["reason"] and items[0]["subject"] == "init"
               and items[0]["refs"] == 1, f"rules order/flags/refs {items[:1]}")
        expect(recorded_rules(tmp, since="HEAD") == [], "rules --since HEAD lists nothing older")

        # a run: init, findings, validate, phase, report
        start = git(tmp, "rev-parse", "HEAD").strip()
        res = init(tmp, ["all"])
        expect(res["next"] == "lean" and not res["resume"], f"init next {res.get('next')}")
        expect(init(tmp, [])["resume"], "second init resumes the open run")
        try:
            init(Path(tempfile.mkdtemp(prefix="ds-audit-x-")), ["ask", "auto"])
            fails.append("init accepted ask together with auto")
        except SystemExit:
            pass
        state, text = load(tmp)
        expect(state["start"] == start and "ds/audit/" in read(tmp / ".git/info/exclude"), "init state + exclude")
        expect(state["branch"] == BRANCH and git(tmp, "rev-parse", "--abbrev-ref", "HEAD").strip() == BRANCH
               and state["home"] != BRANCH, "an all run commits on ds/audit, home branch recorded")
        w("a/x.go", "package a\n\n// X returns one.\nfunc X() int { return 1 }\n")
        fixc = commit("fix")
        good_row = f"| 1 | lean | HIGH | lean | LEAN-03 | a/x.go:3 | f | p | plan | fixed | {fixc} |\n"
        bad_rows = [("bad severity", good_row.replace("HIGH", "URGENT")),
                    ("bad rule", good_row.replace("LEAN-03", "NOPE-1")),
                    ("line past end", good_row.replace("a/x.go:3", "a/x.go:99")),
                    ("missing file", good_row.replace("a/x.go:3", "zz.go:1")),
                    ("fake commit", good_row.replace(fixc, "deadbee")),
                    ("bad disposition", good_row.replace("| fixed |", "| done |"))]
        findings = section(text, "Findings")
        for name, row in [("good", good_row)] + bad_rows:
            write(tmp, state, findings=findings + row)
            expect(bool(validate(tmp)) == (name != "good"), f"validate {name}")
        write(tmp, state, findings=findings + good_row.replace("| fixed |", "| open |").replace(fixc, "—"))
        try:
            phase(tmp, "lean", "done")
            fails.append("phase done accepted an open row")
        except SystemExit:
            pass
        crit = good_row.replace("HIGH", "CRITICAL").replace("| fixed |", "| skipped (needs a key) |").replace(fixc, "—")
        write(tmp, state, findings=findings + crit)
        for p in state["phases"]:
            phase(tmp, p, "blocked", "test") if p != "lean" else phase(tmp, p, "done")
        expect(report(tmp).startswith("ds-audit: INCOMPLETE"), "report INCOMPLETE while a phase is blocked")
        state, text = load(tmp)
        for p in state["phases"].values():
            p["status"] = "done"
        state["checks"] = {"baseline": {"go test": "pass"}, "now": {"go test": "pass"}}
        save_state(tmp, state)
        expect(report(tmp).startswith("ds-audit: FAIL"), "report FAIL on an open CRITICAL")
        write(tmp, state, findings=findings + good_row.replace("| f | p |", "| <script>x</script> | p |"))
        expect(report(tmp).startswith("ds-audit: OK"), "report OK when all fixed and checks hold")
        page = read(tmp / REPORT.with_suffix(".html"))
        expect("&lt;script&gt;x" in page and "<script>x" not in page and "@media (max-width:560px)" in page,
               "report.html escapes finding text and carries the narrow-screen layout")
        state["checks"]["now"]["go test"] = "fail"
        save_state(tmp, state)
        expect(report(tmp).startswith("ds-audit: FAIL"), "report FAIL on a check newly red")
        write(tmp, state, findings=findings + crit)
        init(tmp, ["all"])
        carried = rows(load(tmp)[1])
        expect(len(carried) == 1 and carried[0]["Disposition"] == "open" and load(tmp)[0]["carried"] == 1,
               "a new run carries the previous run's open rows as open")

        # scan: a rule with a Mech line runs; a missing tool is reported, not run
        w("b.txt", "TODO here\n")
        commit("todo")
        (tmp / REPORT).unlink()
        hits = {h["rule"]: h for h in scan(tmp, "build")}
        expect(hits.get("T-01", {}).get("status") == "hit" and hits.get("T-02", {}).get("status") == "tool absent",
               f"scan {hits}")
        expect(hits.get("T-03", {}).get("status") == "not applicable", f"scan runs a rule its applies_when excludes: {hits}")
        inj = run_mech(tmp, "T-04", "T", "echo {base}", {"base": "o/x;echo INJECTED"})  # `;` is legal in a ref name
        expect(inj.get("hits") == ["o/x;echo INJECTED"], f"scan passes {{base}} to the shell unquoted: {inj}")
        expect("YAGNI" in rule_ids() and loads("ui≠none or api≠none", {"ui": {"value": "none"},
                                                                     "api": {"value": "rest"}})[0], "rule ids / loads")
        expect(not loads("pii=yes", {"pii": {"value": "no"}})[0] and loads("pii=yes", {})[0], "loads unknown → runs")
        init(tmp, ["all"])
        expect(load(tmp)[0]["phases"]["surface"]["areas"]["a11y"].startswith("N/A"), "a11y N/A while ui=none")
        sres = set_signal(tmp, "ui", "web")
        expect(sres["plan"]["surface"]["areas"]["a11y"] == "ran" and "ui=web" in sres["signals"],
               "signal correction re-plans a pending phase")
        (tmp / REPORT).unlink()
        expect(init(tmp, ["a11y"])["plan"].get("surface", {}).get("areas", {}).get("a11y") == "ran",
               "a named area runs even when its signal says N/A")
    finally:
        if CORE != real_core:
            shutil.rmtree(CORE, ignore_errors=True)
        CORE = real_core
        shutil.rmtree(tmp, ignore_errors=True)
        os.environ.update(saved)
        ENV.update(saved)
    for f in fails:
        print("  FAIL", f)
    print("ds-audit self-test:", "all checks passed" if not fails else f"{len(fails)} failed")
    return 1 if fails else 0


# --- cli --------------------------------------------------------------------------------------------------

def take(argv, flag, many=False):
    vals = []
    while flag in argv:
        i = argv.index(flag)
        if i + 1 >= len(argv):
            raise SystemExit(f"audit.py: {flag} needs a value")
        vals.append(argv[i + 1])
        del argv[i:i + 2]
        if not many:
            break
    return vals if many else (vals[0] if vals else None)


def main(argv) -> int:
    argv = list(argv)
    root = Path(take(argv, "--root") or ".").resolve()
    depth = int(take(argv, "--depth") or 2)
    cmd, rest = (argv[0], argv[1:]) if argv else ("-h", [])
    dump = lambda o: print(json.dumps(o, indent=1, ensure_ascii=False))  # noqa: E731
    if cmd == "--self-test":
        return self_test()
    if cmd == "init":
        dump(init(root, rest))
    elif cmd == "checks" and rest[:1] in (["baseline"], ["now"]):
        res = checks(root, rest[0])
        dump(res)
        return 0 if all(v["status"] == "pass" for v in res.values()) else 1
    elif cmd == "scan" and rest[:1] and rest[0] in PHASES:
        dump(scan(root, rest[0]))
    elif cmd == "signal" and len(rest) == 2:
        dump(set_signal(root, rest[0], rest[1]))
    elif cmd == "validate":
        problems = validate(root)
        for p in problems:
            print("  ", p)
        print(f"validate: {'OK' if not problems else 'FAIL'} — {len(problems)} problem(s)")
        return 1 if problems else 0
    elif cmd == "phase" and len(rest) >= 2:
        print(phase(root, rest[0], rest[1], " ".join(rest[2:])) or "all phases closed — run `audit.py report`")
    elif cmd == "report":
        print(report(root))
    elif cmd == "lean":
        dump(inventory(root, depth))
    elif cmd == "lean-check":
        problems = lean_check(root, root / (rest[0] if rest else "SCOPE.md"), depth)
        for p in problems:
            print("  ", p)
        print(f"lean-check: {'OK' if not problems else 'FAIL'} — {len(problems)} problem(s)")
        return 1 if problems else 0
    elif cmd == "rules":
        dump(recorded_rules(root, take(rest, "--since") or "", take(rest, "--also", many=True)))
    else:
        print(__doc__)
        return 0 if cmd in ("-h", "--help") else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
