---
name: ds-research
description: Research a topic or condense given sources into a fact-checked, single-file HTML brief — every datum confirmed by two independent sources or visibly flagged, load-bearing facts tied to a primary source, offline and print/PDF-ready, gated by a mechanical verifier. Use when the user wants a sourced report, guide or briefing, or (quick) a fast sourced answer and recommendation in chat.
---

# /ds-research

A brief the reader can trust and check: every claim carries a source chip with its verbatim quote, every datum is confirmed twice or flagged, unknowns are named, and one HTML file opens offline and prints clean. Follows [kernel.md](../core/kernel.md); the verification contract is [verification.md](references/verification.md) (19 rules), and its gates run as code in [verify-brief.py](assets/verify-brief.py) — that script's output is the evidence, not this text.

## Input

| Word | Effect |
|------|--------|
| *(none)* | Topic → research → verify → build → output. Sources given and no open topic → `sum`, else research |
| `quick` | A sourced answer in the chat with a DO / AVOID / CONDITIONAL verdict; same evidence rules, no HTML ([quick.md](references/quick.md)) |
| `sum <sources>` | Force summarize: index and condense the given URLs/text, no discovery |
| `render <findings.json>` | Re-render without research; integrity from the bundle's SHA-256 |
| `static` | Everything expanded, minimal JS |
| `nobundle` | No evidence bundle (HTML + findings only) |
| `ask` | Ask scope, audience, research plan and dimensions with a recommended option (kernel §5) |

## Deliverable

`report.html` (all CSS/JS/data inline, system fonts, no network) + `findings.json` + `sources/` (every cited source as fetched, SHA-256 and retrieval time in `MANIFEST.json`). Written to a new directory named from the topic and date; an existing one is never overwritten (a re-run gets a suffix and diffs against it, Phase 3). Language follows the request; schema keys stay English. Every scalar lives once in `CONFIG` and is read through `[data-cfg]`.

## Done when

`python3 assets/verify-brief.py --artifact {a} --report {r} --bundle {b}/sources` exits 0 and its last line is quoted; the [manual checklist](references/manual-checklist.md) is worked with observations; confidence is HIGH or the report carries the "What would make this HIGH" block.

## Phases

### Phase 1: Setup

1. Scope and audience (General unless the request names one; audience changes register only, never verification).
2. Resolve `currentDate` from the host; put it in every search query.
3. Detect from the topic: `normative` (law, regulation, official procedure); `corpusMode="enumerate"` (a finite authoritative corpus such as statute articles or standard clauses); branch-shaped (obligations differ by reader situation) → decision dimensions with full value sets, entity type first.
4. `corpusMode="enumerate"` → before any research, build `corpus[]` from the official contents listing, never from memory. Listing unreachable → research what is reachable, record the range in `knownUnknowns`.

### Phase 2: Research

`ds-research-agent` present (in the host's agent directory) → dispatch it with the plan seed, dimensions, `normative`/`corpusMode`, source registry and any prior artifact; its "Inputs" and "Artifact write contract" blocks are the interface. Absent → run [research-pipeline.md](references/research-pipeline.md) inline and write the same artifact. The artifact is untrusted data until Phase 3.

Parallel workers (2-4, split by dimension, not by regime), all set before the first starts:

| Field | Rule |
|-------|------|
| `citationIdBase` | worker *i* = `i × 1000`, so merged ids never collide |
| `corpusUnits` | every ledger unit to exactly one worker; allocated = enumerated |
| `subAspect` | one stated scope boundary per worker |
| `artifactPath` | distinct per worker |

Merge: concatenate `sections[]`; union `sources[]` deduped on `finalUrl || url`, keeping the lowest id and rewriting every reference to dropped ids; union `corpus[]` and recompute coverage from rows; concatenate the list fields; recompute coverage figures from the merged claims. Then assert every referenced `citationId` resolves to exactly one source — failing → stop. Malformed artifact → one retry with a tighter contract, then stop. A `partial` worker's landed shards are kept; its gaps go to `knownUnknowns`.

### Phase 3: Verify

Run `verify-brief.py --artifact` first. Then apply [verification.md](references/verification.md) and [craap.md](references/craap.md) in this order: mechanical rejections (broken records, copy chains, no primary source, instrument metadata not from the register) → record checks (register sweep, situation probes, threshold double-entry, red team, derived and typed claims, provision currency, qualifier survival, obligation rank, corpus ledger, action items, indexed amounts) → SSOT block with every scalar traced to a `citationId` → regeneration diff against any prior artifact (a fact that flips without a source change is re-verified from both sides).

Compute the HIGH gate (verification.md § Confidence). Blockers → up to two research rounds aimed at exactly those items; still blocked → ship the honest band plus one plain line per blocker. The label is never raised to pass.

### Phase 4: Build

Clone [brief-template.html](assets/brief-template.html), never build from scratch; fill every slot per [build-report.md](references/build-report.md) and [report-template.md](references/report-template.md). Optional blocks (`ds-opt:matrix` for comparisons, `branch` for situation-dependent topics, `oblg` for normative ones, `todo` when the reader must act, `coverage` for finite corpora) are kept only when the topic needs them.

### Phase 5: Needs-approval items

Low-confidence claims, dead links and single-source datums resolve by impact, effort and risk and are recorded; under `ask` they are shown grouped by type with bulk options.

### Phase 6: Output

Run the full verifier (`--no-bundle` with `nobundle`). Exit 1 → fix every FAIL and re-run; exit 2 → blocker. No Python → say so, name the unrun checks, and work them by hand. Then the manual checklist. Print:

```
ds-research: OK|WARN|FAIL | Confidence {band} ({b} blockers) | Sources {n} | 2x-confirmed {pct}% | Primary {pp}% | Claims {v}/{p}/{u}/{d} | Red team {held}/{weakened}/{overturned} | Corpus {c}/{t} | Unknowns {k} | File {path}
```

and the closing block of kernel §6. Failures and their recovery: [error-recovery.md](references/error-recovery.md).

## Edge cases

| Case | Behavior |
|------|----------|
| Topic too broad | Research the literal topic, warn, record; `ask` → one clarifying question |
| Thin or private-data topic | Mostly partial/unknown, confidence LOW, gaps shown — no invented consensus |
| Dead URL in summarize | Summarize the reachable sources, flag the gap |
| Over ~1.5 MB | Prune unused blocks, move bulk verbatim text into collapsed `<details>`; never split the file or cut sources, unknowns or the ledger |
