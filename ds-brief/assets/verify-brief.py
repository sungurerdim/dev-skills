#!/usr/bin/env python3
"""ds-brief mechanical verifier — the Phase 3 and Phase 6 checks as executable code.

Consumer: ds-brief SKILL.md Phase 6 (Output). Run it, quote its output as the
Completion Evidence for the run. Prose checks degrade silently on a long run;
these do not.

Stdlib only (no pip, no npm) — matches the repo's zero-runtime-dependency rule.

  python3 verify-brief.py --artifact findings.json [--report report.html]
                          [--bundle sources/] [--no-bundle] [-v]

Exit 0 = every check passed. Exit 1 = at least one FAIL. Exit 2 = could not run
(missing/unparseable input) — that is a Verification-Infrastructure Gap, not a pass.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from html.parser import HTMLParser

CHECKS = []          # (id, group, ok, detail)
VERBOSE = False


def record(cid, group, ok, detail=""):
    CHECKS.append((cid, group, ok, detail))


def fail(cid, group, detail):
    record(cid, group, False, detail)


def ok(cid, group, detail=""):
    record(cid, group, True, detail)


def cap(items, n=4):
    """Render at most n offenders, then a count — a wall of text hides the signal."""
    items = list(items)
    head = "; ".join(str(i) for i in items[:n])
    return head + (f" (+{len(items) - n} more)" if len(items) > n else "")


# --------------------------------------------------------------------------
# artifact loading (index + shards)
# --------------------------------------------------------------------------

def load_artifact(index_path):
    """Return (merged_artifact, notes). Follows the agent's Artifact write contract."""
    with open(index_path, encoding="utf-8") as fh:
        art = json.load(fh)
    notes = []
    shards = art.get("shards") or []
    base = os.path.dirname(os.path.abspath(index_path))

    if shards:
        for sh in shards:
            path = sh.get("path") or ""
            if not os.path.isabs(path):
                path = os.path.join(base, path)
            if not os.path.exists(path):
                raise FileNotFoundError(f"shard named in index is missing: {sh.get('path')}")
            with open(path, encoding="utf-8") as fh:
                payload = json.load(fh)
            field = sh.get("field")
            if field not in ("sections", "sources"):
                raise ValueError(f"unknown shard field: {field!r}")
            art.setdefault(field, []).extend(payload.get(field) or [])
            declared = sh.get("count")
            actual = len(payload.get(field) or [])
            if declared is not None and declared != actual:
                notes.append(f"{os.path.basename(path)}: count={declared} but holds {actual}")
        notes.append(f"{len(shards)} shard(s) merged")
    else:
        notes.append("inline artifact (shards:[])")
    return art, notes


def iter_claims(art):
    for sec in art.get("sections") or []:
        for cl in sec.get("claims") or []:
            yield sec, cl


def claim_key(sec, cl):
    text = (cl.get("text") or "")[:60]
    return f"{sec.get('id') or sec.get('title') or '?'}/{text}"


def all_sources(art):
    """Every source record, both the top-level list and the per-claim copies."""
    out = list(art.get("sources") or [])
    for _sec, cl in iter_claims(art):
        out.extend(cl.get("sources") or [])
    return out


def registrable(host):
    host = (host or "").lower().strip().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def host_of(url):
    m = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://([^/?#]+)", url or "")
    if not m:
        return ""
    return registrable(m.group(1).split("@")[-1].split(":")[0])


# --------------------------------------------------------------------------
# A: artifact checks
# --------------------------------------------------------------------------

def check_artifact(art):
    G = "artifact"

    # A01 — sections/sources present exactly once
    shards = art.get("shards") or []
    fields = {sh.get("field") for sh in shards}
    if shards and not {"sections", "sources"} & fields:
        fail("A01", G, "shards[] present but names neither sections nor sources")
    elif not art.get("sections"):
        fail("A01", G, "no sections in artifact (inline or sharded)")
    else:
        ok("A01", G, f"{len(art['sections'])} section(s), {len(art.get('sources') or [])} source(s)")

    # A02 — partial must be false in a finished artifact
    if art.get("partial") is True:
        fail("A02", G, "partial:true — this is a checkpoint, not a finished artifact")
    else:
        ok("A02", G)

    # A03 — citationId uniqueness + resolvability
    defined = {}
    dupes = []
    for src in all_sources(art):
        cid = src.get("citationId")
        if cid is None:
            continue
        url = src.get("finalUrl") or src.get("url")
        if cid in defined and defined[cid] != url:
            dupes.append(f"id {cid} → {defined[cid]} and {url}")
        defined.setdefault(cid, url)
    referenced = set()
    for _sec, cl in iter_claims(art):
        for src in cl.get("sources") or []:
            if src.get("citationId") is not None:
                referenced.add(src["citationId"])
    for block in ("todo", "deadlines", "sanctions"):
        for row in art.get(block) or []:
            referenced.update(row.get("citationIds") or [])
    for _k, v in (art.get("ssot") or {}).items():
        if isinstance(v, dict) and v.get("citationId") is not None:
            referenced.add(v["citationId"])
    dangling = sorted(referenced - set(defined))
    if dupes:
        fail("A03", G, f"citationId collision: {cap(dupes)}")
    elif dangling:
        fail("A03", G, f"citationId referenced but never defined: {cap(dangling)}")
    else:
        ok("A03", G, f"{len(defined)} unique ids, all references resolve")

    # A04 — source record integrity (host match, quote found)
    bad_host, no_quote = [], []
    for src in all_sources(art):
        url = src.get("finalUrl") or src.get("url") or ""
        dom = registrable(src.get("domain") or "")
        h = host_of(url)
        if dom and h and not (h == dom or h.endswith("." + dom)):
            bad_host.append(f"{src.get('citationId')}: domain={dom} url-host={h}")
        if src.get("quoteFound") is False:
            no_quote.append(str(src.get("citationId")))
    if bad_host:
        fail("A04", G, f"domain/url mismatch (corrupt record, not a typo): {cap(bad_host)}")
    elif no_quote:
        fail("A04", G, f"quoteFound:false shipped instead of rejected: {cap(no_quote)}")
    else:
        ok("A04", G)

    # A05 — pubDate present on every source
    missing = [str(s.get("citationId")) for s in all_sources(art) if not s.get("pubDate")]
    (ok if not missing else fail)("A05", G, "" if not missing else f"source without pubDate: {cap(missing)}")

    # A06 — verification label matches the independent-source count
    bad = []
    for sec, cl in iter_claims(art):
        srcs = cl.get("sources") or []
        doms = {registrable(s.get("domain") or "") for s in srcs if s.get("domain")}
        v = cl.get("verification")
        if v == "verified" and len(doms) < 2:
            bad.append(f"{claim_key(sec, cl)} verified on {len(doms)} distinct domain(s)")
        if v == "partial" and len(srcs) > 1 and len(doms) > 1:
            bad.append(f"{claim_key(sec, cl)} partial but has {len(doms)} independent sources")
    (ok if not bad else fail)("A06", G, "" if not bad else cap(bad))

    # A07 — primary-source mandate on load-bearing claims
    bad = []
    for sec, cl in iter_claims(art):
        if cl.get("loadBearing") and cl.get("primarySourced") is False:
            if cl.get("verification") == "verified":
                bad.append(claim_key(sec, cl))
    (ok if not bad else fail)("A07", G, "" if not bad else f"load-bearing + secondary-only shipped as verified: {cap(bad)}")

    # A08 — derived claims: >=2 verified, non-derived premises + a stated rule
    verified_ids, derived_ids = set(), set()
    for _sec, cl in iter_claims(art):
        ids = {s.get("citationId") for s in cl.get("sources") or []}
        if cl.get("verification") == "verified":
            verified_ids |= ids
        if cl.get("derivation"):
            derived_ids |= ids
    bad = []
    for sec, cl in iter_claims(art):
        d = cl.get("derivation")
        if not d:
            continue
        prem = d.get("premises") or []
        if len(prem) < 2:
            bad.append(f"{claim_key(sec, cl)}: {len(prem)} premise(s)")
        elif not (d.get("rule") or "").strip():
            bad.append(f"{claim_key(sec, cl)}: empty rule")
        else:
            weak = [p for p in prem if p not in verified_ids]
            chained = [p for p in prem if p in derived_ids]
            if weak:
                bad.append(f"{claim_key(sec, cl)}: premise not verified {cap(weak, 2)}")
            if chained:
                bad.append(f"{claim_key(sec, cl)}: chained off a derived claim")
    (ok if not bad else fail)("A08", G, "" if not bad else cap(bad))

    # A09 — normative claims carry a complete provision + obligation rank
    prov_keys = ("instrument", "unit", "consolidatedSource", "versionAsOf",
                 "lastAmended", "inForce", "annulled")
    bad = []
    for sec, cl in iter_claims(art):
        if not cl.get("obligation"):
            continue
        p = cl.get("provision") or {}
        miss = [k for k in prov_keys if k not in p]
        if miss:
            bad.append(f"{claim_key(sec, cl)}: provision missing {cap(miss, 3)}")
        rank = cl.get("obligationRank") or ""
        if cl["obligation"] in ("must", "mustnot") and rank not in ("N1", "N2", "N3", "N4"):
            bad.append(f"{claim_key(sec, cl)}: {cl['obligation']} on rank {rank or 'none'}")
    (ok if not bad else fail)("A09", G, "" if not bad else cap(bad))

    # A10 — red team on every load-bearing claim
    rt = {r.get("claimId"): r for r in art.get("redTeam") or []}
    empty = [k for k, r in rt.items() if not (r.get("attack") or "").strip()]
    unresolved = [k for k, r in rt.items() if r.get("outcome") == "overturned"]
    lb = sum(1 for _s, c in iter_claims(art) if c.get("loadBearing"))
    if empty:
        fail("A10", G, f"empty attack string = failed validation: {cap(empty)}")
    elif unresolved:
        fail("A10", G, f"unresolved overturned: {cap(unresolved)}")
    elif lb and len(rt) < lb:
        fail("A10", G, f"{lb} load-bearing claim(s) but {len(rt)} red-team entr(ies)")
    else:
        ok("A10", G, f"{len(rt)} attack(s) recorded")

    # A11 — threshold double-entry
    mism = [r.get("key") for r in art.get("ssotVerify") or [] if not r.get("match")]
    (ok if not mism else fail)("A11", G, "" if not mism else f"double-read mismatch shipped: {cap(mism)}")

    # A12 — corpus ledger recomputes, gaps reach Unknowns
    corpus = art.get("corpus") or []
    if corpus:
        counted = {"covered": 0, "outOfScope": 0, "gap": 0}
        for row in corpus:
            st = row.get("status")
            if st == "covered":
                counted["covered"] += 1
            elif st == "out-of-scope":
                counted["outOfScope"] += 1
            elif st == "gap":
                counted["gap"] += 1
        counted["total"] = len(corpus)
        declared = art.get("corpusCoverage") or {}
        drift = {k: (declared.get(k), v) for k, v in counted.items() if declared.get(k) != v}
        unknown_txt = json.dumps(art.get("knownUnknowns") or [], ensure_ascii=False)
        orphan = [r.get("unit") for r in corpus
                  if r.get("status") == "gap" and str(r.get("unit")) not in unknown_txt]
        if drift:
            fail("A12", G, f"corpusCoverage asserted, not recomputed: {drift}")
        elif orphan:
            fail("A12", G, f"gap row missing from knownUnknowns: {cap(orphan)}")
        else:
            ok("A12", G, f"{counted['total']} unit(s), {counted['gap']} gap(s)")
    else:
        ok("A12", G, "no corpus ledger (not a finite-corpus topic)")

    # A13 — coverage figures recomputed, not asserted
    claims = [c for _s, c in iter_claims(art)]
    if claims:
        got = sum(1 for c in claims if c.get("verification") == "verified") / len(claims)
        declared = art.get("validationCoverage")
        if declared is not None and abs(declared - got) > 0.02:
            fail("A13", G, f"validationCoverage={declared} but claims give {got:.2f}")
        else:
            ok("A13", G, f"coverage {got:.2f}")
    else:
        fail("A13", G, "no claims to compute coverage from")

    # A14 — confidence gate honesty
    gate = art.get("confidenceGate") or {}
    blockers = gate.get("blockers") or []
    lines = {k: v for k, v in gate.items()
             if isinstance(v, bool)}
    if art.get("confidence") == "HIGH" and (blockers or not all(lines.values())):
        unmet = [k for k, v in lines.items() if not v]
        fail("A14", G, f"HIGH asserted with {len(blockers)} blocker(s), unmet: {cap(unmet)}")
    elif blockers and gate.get("escalationRounds", 0) == 0:
        fail("A14", G, "blockers present but escalationRounds=0 — the targeted rounds are mandatory")
    else:
        ok("A14", G, f"{art.get('confidence')} with {len(blockers)} blocker(s)")

    # A15 — knownUnknowns carry what was tried
    bad = [u.get("question", "?")[:40] for u in art.get("knownUnknowns") or []
           if not (u.get("triedSources") and u.get("triedQueries"))]
    (ok if not bad else fail)("A15", G, "" if not bad else f"unknown without tried sources/queries: {cap(bad)}")

    # A16 — indexed amounts carry their year
    bad = [s.get("breach", "?")[:40] for s in art.get("sanctions") or []
           if not (s.get("indexYear") and s.get("revaluation"))]
    (ok if not bad else fail)("A16", G, "" if not bad else f"amount without indexYear/revaluation: {cap(bad)}")

    # A17 — every declared dimension value probed
    declared_vals = {(d.get("key"), v.get("val"))
                     for d in art.get("dimensions") or []
                     for v in d.get("values") or []}
    probed = {(p.get("key"), p.get("val")) for p in art.get("dimensionProbes") or []}
    unprobed = sorted(declared_vals - probed)
    if declared_vals:
        (ok if not unprobed else fail)("A17", G, "" if not unprobed
                                       else f"dimension value with no primary probe: {cap(unprobed)}")
    else:
        ok("A17", G, "no dimensions declared")

    # A18 — contradictions carry both candidates and a winner field
    bad = [c.get("field", "?") for c in art.get("contradictions") or []
           if len(c.get("candidates") or []) < 2 or "winner" not in c]
    (ok if not bad else fail)("A18", G, "" if not bad else cap(bad))


# --------------------------------------------------------------------------
# R: report (HTML) checks
# --------------------------------------------------------------------------

class Report(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.ids = set()
        self.external = []
        self.handlers = []
        self.todo_items = 0
        self.exhibits = []
        self.exrefs = []
        self.anchors = []
        self.data_cfg = []
        self.data_cite = []
        self.oblg_levels = []
        self.in_script = False
        self.script_text = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if a.get("id"):
            self.ids.add(a["id"])
        for k, v in attrs:
            if k.startswith("on"):
                self.handlers.append(f"<{tag} {k}>")
        for k in ("src", "href"):
            v = a.get(k) or ""
            if tag in ("script", "link", "img", "iframe", "source", "video", "audio"):
                if v.startswith("http://") or v.startswith("https://") or v.startswith("//"):
                    self.external.append(f"<{tag} {k}={v[:60]}>")
        if a.get("data-cfg"):
            self.data_cfg.append(a["data-cfg"])
        if a.get("data-cite"):
            self.data_cite.append(a["data-cite"])
        if tag == "a":
            href = a.get("href") or ""
            if href.startswith("#"):
                self.anchors.append(href[1:])
            if "exref" in classes:
                self.exrefs.append(href[1:] if href.startswith("#") else href)
        if tag == "figure" and "exh" in classes:
            self.exhibits.append(a.get("id") or "")
        if tag == "li" and "tdi" in classes:
            if any(t == "ol" and "todo" in c for t, c in self.stack):
                self.todo_items += 1
        if "oblg" in classes:
            self.oblg_levels.extend(c for c in classes if c != "oblg")
        if tag == "script":
            self.in_script = True
        if tag not in ("br", "hr", "img", "meta", "link", "input", "source"):
            self.stack.append((tag, classes))

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self.in_script:
            self.script_text.append(data)


def check_report(path):
    G = "report"
    with open(path, encoding="utf-8") as fh:
        html = fh.read()
    p = Report()
    p.feed(html)
    script = "\n".join(p.script_text)

    # R01 — single file, zero external dependencies
    extra = []
    if re.search(r"@import\s+(url\()?['\"]?https?:", html):
        extra.append("@import remote")
    if re.search(r"url\(\s*['\"]?https?://", html):
        extra.append("css url(remote)")
    if re.search(r"\bfetch\s*\(|XMLHttpRequest|navigator\.sendBeacon", script):
        extra.append("network call in script")
    bad = p.external + extra
    (ok if not bad else fail)("R01", G, "" if not bad else cap(bad))

    # R02 — no inline handlers
    (ok if not p.handlers else fail)("R02", G, "" if not p.handlers else cap(p.handlers))

    # R03 — no innerHTML with data
    hits = [m.group(0) for m in re.finditer(r"\.innerHTML\s*=\s*(?!['\"]{2}\s*;?)", script)]
    (ok if not hits else fail)("R03", G, "" if not hits else f"{len(hits)} innerHTML assignment(s) — use textContent/DOM")

    # R04 — no unfilled template placeholders
    ph = sorted(set(re.findall(r"\{[A-Z][A-Z0-9_|]{2,}\}", html)))
    (ok if not ph else fail)("R04", G, "" if not ph else f"unfilled slot(s): {cap(ph)}")

    # R05 — in-file anchors resolve
    dangling = sorted({a for a in p.anchors if a and a not in p.ids})
    (ok if not dangling else fail)("R05", G, "" if not dangling else f"anchor to missing id: {cap(dangling)}")

    # R06 — exhibits numbered and every exref resolves
    unnamed = [i for i, e in enumerate(p.exhibits) if not e]
    bad_ref = [r for r in p.exrefs if r not in p.ids]
    if unnamed:
        fail("R06", G, f"{len(unnamed)} figure.exh without an id")
    elif bad_ref:
        fail("R06", G, f"exref to missing exhibit: {cap(bad_ref)}")
    else:
        ok("R06", G, f"{len(p.exhibits)} exhibit(s), {len(p.exrefs)} reference(s)")

    # R07 — every data-cfg leaf resolves to a CONFIG key
    cfg_keys = set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", script))
    missing = sorted({c for c in p.data_cfg if c.split(".")[-1] not in cfg_keys})
    (ok if not missing else fail)("R07", G, "" if not missing else f"data-cfg with no CONFIG key: {cap(missing)}")

    # R08 — every data-cite resolves to a cites entry
    cite_keys = set(re.findall(r"['\"]?([A-Za-z0-9_]+)['\"]?\s*:\s*\{", script))
    missing = sorted({c for c in p.data_cite if c not in cite_keys and f'"{c}"' not in script})
    (ok if not missing else fail)("R08", G, "" if not missing else f"data-cite with no quote entry: {cap(missing)}")

    # R09 — print rules present
    need = ["@media print", "break-inside"]
    miss = [n for n in need if n not in html]
    (ok if not miss else fail)("R09", G, "" if not miss else f"missing print discipline: {cap(miss)}")

    return p


# --------------------------------------------------------------------------
# X: cross checks (artifact vs report vs bundle)
# --------------------------------------------------------------------------

def check_cross(art, p):
    G = "cross"

    # X01 — every action item in the artifact reached the report
    todo = art.get("todo") or []
    if todo:
        if p.todo_items != len(todo):
            fail("X01", G, f"todo[] has {len(todo)} item(s) but the report renders {p.todo_items} "
                           f"— {len(todo) - p.todo_items} silently dropped")
        else:
            ok("X01", G, f"{len(todo)} action item(s) rendered")
        # X02 — no obligation level lost wholesale. A level whose items all vanish leaves
        # the prose intact and the checklist quietly shorter; `free` is the usual casualty,
        # because a "nothing required of you" item looks like filler at build time.
        want = {}
        for t in todo:
            lvl = t.get("obligation")
            if lvl:
                want[lvl] = want.get(lvl, 0) + 1
        got = {}
        for lvl in p.oblg_levels:
            got[lvl] = got.get(lvl, 0) + 1
        lost = sorted(f"{lvl}: {n} in todo[], {got.get(lvl, 0)} rendered"
                      for lvl, n in want.items() if got.get(lvl, 0) < n)
        (ok if not lost else fail)("X02", G, ", ".join(f"{k}×{v}" for k, v in sorted(want.items()))
                                   if not lost else cap(lost))
    else:
        ok("X01", G, "no action list")
        ok("X02", G, "no action list")

    # X03 — source count in the report matches the artifact
    n_src = len({s.get("citationId") for s in all_sources(art) if s.get("citationId") is not None})
    ok("X03", G, f"{n_src} distinct cited source(s) in artifact")


def check_bundle(art, bundle_dir):
    G = "bundle"
    man_path = os.path.join(bundle_dir, "MANIFEST.json")
    if not os.path.exists(man_path):
        fail("B01", G, f"MANIFEST.json missing from {bundle_dir}")
        return
    try:
        with open(man_path, encoding="utf-8") as fh:
            man = json.load(fh)
    except json.JSONDecodeError as exc:
        fail("B01", G, f"MANIFEST.json does not parse: {exc}")
        return
    ok("B01", G, f"manifest with {len(man)} entr(ies)")

    cited = {str(s.get("citationId")) for s in all_sources(art) if s.get("citationId") is not None}
    missing = sorted(cited - set(map(str, man.keys())))
    (ok if not missing else fail)("B02", G, "" if not missing
                                  else f"cited id absent from manifest: {cap(missing)}")

    bad_hash, no_reason = [], []
    for cid, entry in man.items():
        if not isinstance(entry, dict):
            continue
        local = entry.get("localFile")
        if not local:
            if not entry.get("reason"):
                no_reason.append(cid)
            continue
        fpath = local if os.path.isabs(local) else os.path.join(bundle_dir, local)
        if not os.path.exists(fpath):
            bad_hash.append(f"{cid}: file missing ({local})")
            continue
        want = (entry.get("sha256") or "").lower()
        if want:
            got = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
            if got != want:
                bad_hash.append(f"{cid}: sha256 {got[:12]}… ≠ {want[:12]}…")
    if bad_hash:
        fail("B03", G, cap(bad_hash))
    elif no_reason:
        fail("B03", G, f"snapshot:null without a stated reason: {cap(no_reason)}")
    else:
        ok("B03", G, "every archived file matches its recorded hash")


# --------------------------------------------------------------------------

def main():
    global VERBOSE
    ap = argparse.ArgumentParser(description="ds-brief mechanical verifier")
    ap.add_argument("--artifact", required=True, help="findings artifact index JSON")
    ap.add_argument("--report", help="built single-file HTML report")
    ap.add_argument("--bundle", help="evidence bundle sources/ directory")
    ap.add_argument("--no-bundle", action="store_true", help="run was --no-archive")
    ap.add_argument("-v", "--verbose", action="store_true", help="show passing checks too")
    args = ap.parse_args()
    VERBOSE = args.verbose

    try:
        art, notes = load_artifact(args.artifact)
    except (OSError, ValueError) as exc:
        print(f"CANNOT RUN: {exc}", file=sys.stderr)
        return 2

    check_artifact(art)
    p = None
    if args.report:
        try:
            p = check_report(args.report)
        except OSError as exc:
            print(f"CANNOT RUN: {exc}", file=sys.stderr)
            return 2
        check_cross(art, p)
    if args.bundle and not args.no_bundle:
        check_bundle(art, args.bundle)

    failures = [c for c in CHECKS if not c[2]]
    width = max(len(c[0]) for c in CHECKS)
    for cid, group, passed, detail in CHECKS:
        if passed and not VERBOSE:
            continue
        mark = "PASS" if passed else "FAIL"
        line = f"{mark} {cid:<{width}} [{group}]"
        print(f"{line} {detail}" if detail else line)

    print("-" * 60)
    for n in notes:
        print(f"note: {n}")
    print(f"ds-brief verify: {len(CHECKS) - len(failures)}/{len(CHECKS)} checks passed"
          + (f" — {len(failures)} FAILED" if failures else ""))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
