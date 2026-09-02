# Reference: Phase 4 Build Report — Slot Manifest & Fill Rules

Consumer: ds-brief Phase 4 (Build Report). Build only by cloning `assets/brief-template.html` (never from scratch).

## Slot manifest

Full rule per slot in "Fill these slots" below.

| Slot | Source of truth | Verifier check |
|------|------------------|-----------------|
| Brand / theme tokens | Baked CSS `:root` | R01 |
| `CONFIG` SSOT | Artifact trust scalars | R07, R15 |
| Nav links / sections / source chips | Artifact `sections[]`/`sources[]` | R05, X03 |
| `.lawtext` verbatim blocks | Artifact `verbatimQuote` | X05 |
| Badges (single/unverified/disputed/derived) | Artifact `verification`, `contradictions[]`, `derivation`, `claimType` | A19, X02 |
| Unknowns section | Artifact `knownUnknowns[]` | A15 |
| Sources table + `#method` | Artifact `sources[]` + `runMetadata` | X03, B01-B03 |
| `CONFIG.cites` (claim→quote popover) | Artifact `verbatimQuote` per `citationId` | R08, X05 |
| `.xref` depth cross-reference | In-file section coverage | R05 |
| Narrative spine | Artifact `sections[]` | R10, R12 |
| Exhibits (`figure.exh`) | Artifact tabular/chart data | R06, R14 |
| Print artifact (cover, contents) | `CONFIG` scalars | R09, R12 |
| Ornament budget | Pruning rule | R13 |
| Entity×attribute matrix | Artifact `.cellcite` per cell | X05 |
| Prose / field content rules | Artifact `sections[]` | R10 |
| `CONFIG.charts` | Artifact magnitudes | dataviz validator (advisory) |
| Branch layer (`ds-opt:branch`) | Phase 1 `dimensions` | R04 |
| Obligation badges (`ds-opt:oblg`) | Artifact `provision` fields | X02 |
| Rule-card spine (`ds-opt:todo`) | Artifact `todo[]` | X01, X02 |
| Deadlines / sanctions / escalation | Artifact `deadlines[]`/`sanctions[]` | R04 |
| Corpus ledger (`ds-opt:coverage`) | Artifact `corpus[]` | A12 |
| Confidence blockers (`ds-opt:gate`) | Artifact `confidenceGate.blockers[]` | A14, X04 |
| Plain-language signals | `confidenceNote` + label sentences (verification.md § Confidence) | R04 |

## Fill these slots

- Brand — baked into the CSS at build: default = `slate` preset; **a host project supplies its brand input instead** (token values + category color + `CONFIG.themeStorageKey`) and ds-brief bakes it as-is — no post-hoc canonicalization. Dark ships as a CSS block (JS-off safe). Rules: report-template.md § Theming
- `CONFIG` SSOT — trust scalars (`confidence`, `coveragePct`, `sourceCount`, `officialCount`, `searchCompleteness`, dates) feed the trust strip + `#method` details
- Nav links matching section ids · sections · source chips (official/secondary by tier) · semantic colors (hue-constant across themes; dark re-tunes lightness only)
- Verbatim `.lawtext` blocks (extracted, not paraphrased) · badges (`single`/`unverified`/`disputed`) · Unknowns section · Sources table (+ collapsed `#method` details beside it) · trust strip as the first block of `main` — signals only, method prose never opens the report
- `CONFIG.cites` (ds-opt:cites) — every key datum's chip carries `data-cite` → the artifact's `verbatimQuote` + `pubDate` + tier, shown in-page before the reader leaves (claim→quote click-through); prune only when no quotes ship
- Depth cross-references (ds-opt:xref) — **every topic summarized here but covered more fully elsewhere in the file gets a `.xref` button at the summary** (report-template.md § Depth cross-reference); no deeper coverage → no button
- Narrative spine — governing-thought `h2`, 3-5 key messages with evidence links, scope box, per-section "so what" line; plus vignette / glossary / what-changed / what-could-change-it (ds-opt:watch — entry names the pending instrument + its source; R11) / exposure chips / deadline timeline where the topic has them (rules: report-template.md § Narrative spine)
- Exhibits — every table, chart and diagram is a `figure.exh` with an auto-assigned number, an **assertion** caption ("Penalty ceilings differ by a factor of 20", never "Penalties by regime"), a source line, and a text reference via `a.exref` whose label JS writes from the target (rules: report-template.md § Exhibit discipline)
- Print artifact — the print-only cover (`section.cover`) and contents/exhibit index (`nav.toc`) ship on every brief; all their values come from `CONFIG`, and the contents carries no page numbers (browsers cannot count pages without breaking the single-file rule — state the limit, never fake it)
- Ornament budget — no scroll-reveal, no glow orbs, no hover-lift, no palette menu (light/dark toggle only), no unused icon symbols, no scalar shown twice (report-template.md § Ornament budget)
- Entity×attribute matrix (ds-opt:matrix) **only when the topic compares 2+ entities on shared attributes** — per-cell `.cellcite` provenance, explicit "—" gaps, per-row `N/M` completeness score (rules: report-template.md § Matrix layer)
- Prose follows report-template.md § Authoring language — answer-first (BLUF), descriptive headings, ~25-word sentences, no spatial references, descriptive link text, register per the Phase 1 audience
- **Field content rules** — every summary slot carries a finding, not a topic label ("Deposits max 3 months' rent"); every `h2`/`h3.tdgroup` is an assertion (generic headings banned — verify-brief R10); each section leads with its `p.sowhat`; budgets: summary ≤2 sentences, section leads ≤2, one ~140-char imperative per card — longer material collapses into `<details>` depth (report-template.md § Authoring language)
- `CONFIG.charts` (ds-opt:chart) **only when the topic has 2-7 comparable magnitudes** (rates, costs, limits) — single hue, `hl` for the story's item, auto-built data table; >7 items → table, never more bars (rules: [report-template.md](report-template.md) § Dataviz layer)
- Branch layer (ds-opt:branch) — the **default entry** on a topic that splits by reader role/situation: the selector is the first interactive block after the summary and a selection filters cards, prose, whole sections and the nav (`syncBranchChrome`); hiding is honest (`#hiddenNote` count + "Show all"). Invariants: all branches ship, no-selection/JS-off = all visible labeled, print shows every branch, sources/badges/Unknowns never filtered (rules: report-template.md § Branching layer)
- Obligation badges (ds-opt:oblg) **whenever the content is normative** (law, regulation, procedure, standard) — every normative statement opens with exactly one level badge (Mandatory / Prohibited / Recommended / Optional / No effect), level mirrors the source's wording (never inferred stricter/looser) and traces to an N1-N4 instrument, legend once above first use (rules: report-template.md § Obligation levels)
- Rule-card spine (ds-opt:todo) — on a normative/action topic this is the report's **body, not an appendix**: topic groups (each `h3.tdgroup` an assertion) hold rule cards authored once as `<li data-when>` (JS-off safe), filtered by the branch evaluator; a rule lives in exactly one card, its evidence depth (prose, verbatim provision) collapsing into the card's `<details>`; profile line + count + unanswered note; copy-list and opt-in personal print. Above 2 dimensions this **replaces** per-combination branch cards; analytical topics keep prose sections (rules: report-template.md § Action list layer)
- Normative required blocks (ds-opt:deadlines · ds-opt:sanctions · ds-opt:escalate) **on law/regulation/procedure topics** — one consolidated deadlines table (trigger → period → counted from → consequence), one sanctions table (amounts carry their index year + revaluation rule), and the escalation-trigger list naming exactly when the reader must stop and get professional or regulator input; plus the currency line ("current consolidated text as of {date}")
- Corpus ledger (ds-opt:coverage) **when the topic has a finite authoritative corpus** — every unit from the official contents listing, `covered` / `out-of-scope` (reason) / `gap`, counts recomputed, collapsed near Sources
- Confidence blockers (ds-opt:gate) **whenever the HIGH gate did not fully pass** — "What would make this HIGH", one plain line per blocker; pruned entirely on a HIGH run
- Plain-language signals — `confidenceNote` is mandatory and non-empty; no band name (`MEDIUM`, `T2`, `68%`) ships without its one-sentence reading

## Localize, chrome budget, prune

Localize all visible UI labels to the request language; use the compact primitives (fluid spacing, intrinsic `.grid.auto`, `.strip`, `.pills`, 1px section rhythm, accent-bar headings) and native `<details>` collapsibles. **Chrome budget** (report-template.md § Chrome, width & the first-screen budget): one compact header band ≤150px at desktop with the disclaimer as an inline meta chip (never a full-width banner), nav exactly one row at every width (links scroll horizontally, tools pinned right: search → theme → print), `.wrap` at `min(1560px,96vw)` with prose capped at `--measure` — the container follows the screen, the text line follows the eye — apparatus (Sources, method, corpus ledger, Unknowns) collapsed with counts in the summary, back-to-top always shipped. Add an interactive calculator/scenario **only when the topic genuinely computes something**; `--static` → minimal JS, everything expanded. **Prune:** delete every unused `ds-opt:NAME` block (CSS + HTML) so each report ships only the CSS it needs. Apply [report-template.md](report-template.md).
