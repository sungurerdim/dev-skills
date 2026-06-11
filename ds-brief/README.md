# ds-brief

Turn a topic (or a set of URLs) into a **single-file, offline, print/PDF-ready HTML brief** where every claim is sourced and every datum is confirmed by ≥2 independent sources — or visibly flagged.

## What it does

- Researches deeply via a dedicated worker agent (`ds-research-agent`), or inline if the agent isn't available.
- Confirms every datum twice (≥2 independent sources), flags single-source data, and lists what stayed unknown.
- Builds one HTML file: all CSS+JS+data inline, system fonts, **no network calls** — opens offline, prints to clean PDF.
- SSOT: every number/date lives once in a `CONFIG` object; edit one place, the whole document updates.

## Usage

```
/ds-brief                         # asks depth + scope
/ds-brief {topic}                 # research a topic → sourced HTML brief
/ds-brief --deep {topic}          # parallel workers, all source tiers, resumable
/ds-brief --quick {topic}         # fast, T1-T2 only
/ds-brief --summarize <urls…>     # summarize given URLs/text (no discovery)
/ds-brief --no-interactive {topic} # static, print-pure output
/ds-brief --resume                # resume a deep run
```

## Output

- One `.html` file (single-file, offline). Open in any browser; click **🖨 Yazdır / PDF** for a clean PDF.
- Sections: Özet → Bulgular → (optional calculator) → **Bilinmeyenler / Belirsizler** → Kaynakça.
- Source chips: green = official (T1-T2), amber = secondary (T3-T6). Badges: "tek kaynak" (single source), `[doğrulanmadı]` (unsourced context).

## Verification discipline

Every fact is source-backed · every datum 2×-confirmed or flagged · every reference a live link · no guessing · unclear → researched deeper, then declared unknown · known vs unknown explicit · contradictions shown, not smoothed. See [references/verification.md](references/verification.md).

## Tool-optionality

context-mode and rtk are **optional** — they cut context footprint only, never quality, source count, double-confirmation, or output. No gate depends on a tool being present.

## Files

```
SKILL.md                       orchestrator: phases, gates, scopes
references/
  craap.md                     source reliability scoring (self-contained)
  verification.md              sourcing + 2x-confirm + known/unknown discipline
  report-template.md           HTML conventions (SSOT, chips, print/PDF, a11y)
  research-pipeline.md         collect→store→read; context-mode + completeness
assets/
  brief-template.html          canonical offline print/PDF-safe skeleton (clone + fill)
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
