# Research Pipeline (collect → store → read)

How the agent gathers deep, double-confirmed evidence while keeping bulk content out of the main context window. Optimization is aggressive but **never trades away quality, depth, source count, or double-confirmation** — tools are a context-efficiency layer only.

## Tool-optionality (HARD)

context-mode, rtk and similar are **"nice to have"**, never required. They improve **context/token footprint only** — they do **not** change research quality, source count, double-verification, or output. Without them the skill+agent run at **identical quality**, only with a larger context footprint. Every tool call is wrapped `use-if-present / else-equivalent-fallback`:

| Tool (optional) | If present | If absent (same quality) |
|-----------------|-----------|--------------------------|
| context-mode (`ctx_fetch_and_index` / `ctx_search`) | index page, pull only BM25 slice (context saving) | `WebFetch` + per-page summary (LangChain ODR method) |
| rtk | command output token-optimized | raw command output |
| MCP access in subagent | worker indexes | worker WebFetch; or fetch on the skill side, agent does WebSearch + synthesis |

No gate is ever conditioned on "tool available". Gates bind to source / confirmation / output signals only.

## The three layers

| Layer | Mechanism | Where the bulk lives |
|-------|-----------|----------------------|
| **Collect** | WebSearch (discovery, start-wide) → `ctx_fetch_and_index([{url,source}], concurrency)` in parallel | raw content in the FTS5/BM25 index |
| **Store** | index (`raw`) + findings artifact JSON (`compressed`: verbatim snippet + distilled summary + provenance) | artifact on disk; not in main context |
| **Read / Analyze** | skill reads `ctx_search` snippets + the artifact; raw page never enters the main window | only distilled, source-traced data |

Fallback (no context-mode): WebFetch the page → produce `{summary, key_excerpts}` per page (key_excerpts keep verbatim quotes for provenance; summary is retrieval-efficient) → write to artifact. The raw page body is summarized at the fetch boundary and discarded — same discipline, larger footprint.

## The loop

```
discover (start-wide) → index/fetch → think-step → query/extract → cross-verify
  → register sweep → record integrity → red team → synthesize
```

**Three passes that web search cannot substitute for** (they exist because their absence produced wrong reports):

| Pass | What it does |
|------|--------------|
| **Register sweep** | For each authority whose rules the brief states, walk *its own* decision/announcement index and disposition every item. Search ranks by popularity; a decisive decision that no one blogged about is invisible to it. Also: one primary probe per reader-situation value, asking whether an instrument creates a carve-out for that case. |
| **Record integrity** | Before labelling anything: URL host equals the recorded domain, the verbatim quote occurs in the fetched text, ids are unique, redirects are resolved. Failures are rejected, not flagged. Then collapse copy chains — near-identical sentences across "independent" sites are one origin. |
| **Red team** | Attack every load-bearing claim (supersession · carve-out · contrary reading · provenance · transcription) and record what was tried. "Can I support this?" has confirmation bias built in; "can I break this?" does not. |

**Primary-source mandate:** a rule-driving datum needs a source from the authority that *issued* the rule. Secondary sources corroborate and explain; they never establish. Track `primaryCoverage` separately from `validationCoverage` — the pair is what distinguishes a grounded brief from a well-cross-referenced echo of the same blog post ([verification.md](verification.md) Rules 13-17).

- **Start-wide-then-narrow:** short broad query first → see the gaps → narrow. Agents default to over-narrow queries; resist it.
- **think-step (pure reflection):** before each fetch round, reflect "what do I know / what's missing" — exposes the known/unknown gap, cuts useless search loops. No tool call; just reasoning.
- **Two-tier notes:** raw stays in the index; only verbatim snippet + distilled summary + provenance reach the artifact. Bulk never enters main context.
- **Verbatim grounding:** each claim's `verbatimQuote` is *extracted* from the source (ctx_search snippet or WebFetch excerpt), never generated.
- **Double-verification (reviewer/reviser):** draft claims are mapped back to sources in a reviewer pass; each "confirmed" claim needs ≥2 independent verbatim-backed sources; unsupported/contradicted claims go to a reviser pass (new query). Low-confidence claims are labeled `verified | partial | unknown` — never silently dropped.
- **Dual termination:** primary = explicit "research-complete" (completeness) signal; backup = hard budget (max iterations). Budget is never the primary stop.
- **Perspective diversity:** complex topic → 3-5 viewpoints (expert / skeptic / practitioner / regulator) ask different questions; disagreement surfaces in the finding set and the report reconciles it openly.
- **Source-quality heuristics (in prompt):** prefer primary/authoritative (official docs, academic PDF, law text) over SEO content farms; CRAAP+ scoring; security/legal T1 override.
- **Batch fetch in parallel** (3+ tools at once where independent). **Saturation gate:** 3+ T1/T2 agree → skip lower tiers. **In-cycle source promotion:** a newly found credible source is used immediately, not deferred.

## Model routing & re-grounding

- Worker = `sonnet` (synthesis quality beats doubling token budget). Fast single-look scope = `haiku`.
- Re-ground every ~20 tool calls on long runs: refresh plan + artifact (W14).
- **Checkpoint every phase, not just the plan** (W4): each phase ends by overwriting the artifact with everything gathered so far, `partial:true`, before the next begins. Persisting only the plan means a truncation at the final write loses every finding the run paid for — and the final write is exactly where a deep artifact is most likely to fail.
- **Write it as index + shards, never one call** (agent § Artifact write contract): no single write payload near the host's output ceiling, the small index written last as the commit, and both read back. A deep normative artifact does not fit one write, and a truncated write looks like a completed one.

## Two verification layers, and neither substitutes for the other

**Mechanical (`assets/verify-brief.py`).** Everything a parser can settle: record integrity, id resolution, recomputed coverage and ledger counts, gate honesty, artifact-vs-report agreement, bundle hashes. It runs identically every time and it does not get tired at hour three — which is precisely when the prose checks start being remembered instead of performed. Its exit code is the phase's evidence.

**By hand.** Everything judgment-shaped, because automated checks miss hallucinations on unusual queries (Anthropic finding): offline open, sourcing spot-check, does the quote actually support the claim, print/PDF appearance, prose register, security review.

A check that a parser could settle belongs in the script, not in a list someone re-reads. A check that needs judgment belongs to the reader, not to a regex that will approve it.

## Patterns adopted (source-traced)

| Pattern | Source |
|---------|--------|
| Orchestrator-workers + parallelization | Anthropic — Building Effective Agents |
| Worker task contract; scale effort to query complexity | Anthropic — Multi-agent research system |
| Artifact-store + lightweight reference (bulk outside) | Anthropic — Multi-agent research system |
| CitationAgent / separate verification pass | Anthropic — Multi-agent research system |
| `cited_text` extracted-not-generated | Anthropic — Citations API |
| raw_notes vs notes; per-page summary | LangChain Open Deep Research |
| `Information{citation_uuid,url,snippets}` provenance unit | Stanford STORM |
| learnings/citations/followups structure | GPT-Researcher |
| think-step pure reflection; soft-done + hard-budget | LangChain ODR + STORM |
| reviewer/reviser verification-centric design | Marco DeepResearch |
