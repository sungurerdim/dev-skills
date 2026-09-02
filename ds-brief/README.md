# ds-brief

Turn a topic (or a set of URLs) into a **single-file, offline, print/PDF-ready HTML brief** where every claim is sourced and every datum is confirmed by ≥2 independent sources — or visibly flagged.

## What it does

- Researches deeply via a dedicated worker agent (`ds-research-agent`), or inline if the agent isn't available.
- Confirms every datum twice (≥2 independent sources), flags single-source data, and lists what stayed unknown.
- Shows its own reasoning: any conclusion the brief *derives* rather than quotes carries a `derived` badge with the premise quotes and the reasoning step.
- Targets **HIGH confidence**, computed from a multi-line gate (primary sourcing, record integrity, register sweep, red team, …) — below it, the skill re-researches the blocking items and, if they survive, names each one in plain language. No bare `MEDIUM` labels.
- Law/regulation topics: current consolidated text only (amendments, repeals and annulments explicitly checked), provisions read with their definitions and exceptions, obligations ranked by instrument, plus deadlines, sanctions (with the index year of amounts) and escalation triggers.
- Finite corpora (statute articles, standard clauses, endpoints): an article-by-article ledger accounts for every unit as covered / out-of-scope / gap.
- Assembles a personalized **"exactly what you must do"** checklist from the reader's situation — what · who · by when · how · on what authority — and flags unanswered questions instead of implying completeness.
- Builds one HTML file: all CSS+JS+data inline, system fonts, **no network calls** — opens offline, prints to clean PDF.
- SSOT: every number/date lives once in a `CONFIG` object; edit one place, the whole document updates.

## Usage

```
/ds-brief                         # asks depth + scope
/ds-brief {topic}                 # research a topic → sourced HTML brief
/ds-brief --deep {topic}          # parallel workers, all source tiers
/ds-brief --quick {topic}         # fast, T1-T2 only
/ds-brief --summarize <urls…>     # summarize given URLs/text (no discovery)
/ds-brief --static {topic}        # static, print-pure output
/ds-brief --ask {topic}           # interactive — menus and approval batches at every decision point
/ds-brief --no-archive {topic}    # skip the evidence bundle (HTML + findings only)
/ds-brief --from-artifact <findings.json>   # re-render from an existing artifact — zero research, works offline
```

## Output

- A directory by default: `report.html` (single-file, offline) + `findings.json` (research SSOT) + `sources/` (every cited source as fetched, SHA-256'd in `MANIFEST.json`) — `--no-archive` emits the HTML + findings only, and the HTML works with or without the bundle. Open in any browser; click **Print / PDF** for a clean PDF. Labels render in the language of the request. The bundle is what makes a later re-render (`--from-artifact`) and incremental refreshes possible without repeating the research.
- Sections: Summary → your situation → **what you must do** → findings → deadlines / sanctions / when to get help → Unknowns → Sources & method (with the coverage ledger). Apparatus is collapsed with counts in the summary line, so the first screen belongs to the answer.
- Compact chrome: one-band header, single-row nav at every width, container `min(1560px,96vw)` with prose at a 72ch measure — wide screens are used, text lines stay readable.
- Source chips: green = official (T1-T2), amber = secondary (T3-T6). Badges: `single source`, `[unverified]`, `disputed`, `derived`.

## Verification discipline

Every fact is source-backed · every datum 2×-confirmed or flagged · every reference a live link · no guessing · unclear → researched deeper, then declared unknown · known vs unknown explicit · contradictions shown, not smoothed · every inference shows its premises · normative text read in context and in its current consolidated version · HIGH confidence is the target, never an assertion. See [references/verification.md](references/verification.md).

The checks a parser can settle run as code (`python3 assets/verify-brief.py --artifact findings.json --report report.html --bundle sources/`), not as recall. Exit 0 is the run's completion evidence. It catches what reads as fine — a dropped action item, a citation id pointing nowhere, a coverage figure asserted rather than recomputed, an archived file whose hash no longer matches. `--self-test` proves the checks still fire, by running them against fixtures broken in named ways (the run prints its own defect count). Judgment-shaped checks (does the quote support the claim, does the PDF look right) stay manual by design. No `python3` on the host → the run declares a Verification-Infrastructure Gap, names every check left unrun, and works them by hand instead of reporting the phase clean on checks nobody executed.

## Tool-optionality

context-mode and rtk are **optional** — they cut context footprint only, never quality, source count, double-confirmation, or output. No gate depends on a tool being present.

## Files

```
SKILL.md                       orchestrator: phases, gates, scopes
../core/craap.md                source tiers, scoring, normative ladder (shared method)
references/
  verification.md              sourcing + 2x-confirm + known/unknown discipline (this skill's stricter HIGH gate + independence test)
  report-template.md           HTML conventions (SSOT, chips, print/PDF, a11y)
  research-pipeline.md         collect→store→read; context-mode + completeness
assets/
  brief-template.html          canonical offline print/PDF-safe skeleton (clone + fill)
  verify-brief.py              mechanical verifier (stdlib python3): artifact, report, cross, bundle
~/.claude/agents/
  ds-research-agent.md   deep sourced web-research worker
```

## Scopes

| scope | status |
|-------|--------|
| `research` (default) | full |
| `summarize` | light (no discovery) |

## Security

Single file, zero external dependencies. Text injected via `textContent`/DOM only (no `innerHTML` with data), no inline event handlers, no network access. Auditable with view-source alone.

Self-contained: depends on no other skill.
