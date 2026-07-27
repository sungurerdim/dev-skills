# Report Template Conventions

Distilled from four hand-built guides (gvk-20b, vergi-kilavuzu ×2, is-hukuku) and the akis design system (`akis/assets/tokens.css`, `akis/dist/firm-site.html`, `akis/src/constants/palettes.js`). `assets/brief-template.html` is the concrete, working skeleton of these rules — clone and fill it; never generate the HTML from scratch (lowers hallucination risk). These conventions are the *why*; the skeleton is the *what*. All visible label strings here are canonical English — localized to the request language at build (SKILL.md Contract).

## Hard requirements (every brief)

| Convention | Rule |
|------------|------|
| Single-file / offline | All CSS + JS + data embedded. **No external fonts** (`system-ui` / `-apple-system` stack), no CDN, no network call. View-source must be self-sufficient → offline + reliable PDF. |
| SSOT data block | Every number/rate/date/quantity lives once, in a single `CONFIG` JS object. HTML reads them via `[data-cfg="key"]` spans, filled by one render pass. Edit one place → all prose/tables/calc update. |
| Source chip | Two visible chip types: `official` / `secondary` (secondary = T3-T6, amber). Every claim carries one. |
| Claim→quote popover (`ds-opt:cites`) | The strongest trust signal in the field (Elicit / NotebookLM / Scite pattern): clicking a chip shows the source's **extracted verbatim sentence** (`CONFIG.cites`, byte-for-byte — the artifact's `verbatimQuote`) + pubDate + tier *inside the page*, with the outbound link inside the popover. Ship quotes for every key datum's chip; prune the block only when no quotes ship. JS-off → chips are plain links. |
| Depth cross-reference (`ds-opt:xref`) | **Every topic summarized in one place but covered more fully elsewhere in the file (detail `<details>`, matrix, appendix section) carries a `.xref` button at the summary** — rounded-rect + arrow, visually distinct from source chips (pill = external evidence; xref = internal "read more"). Hash deep-link auto-opens a target `<details>`. This pairs with BLUF: the answer up front, depth one press away. A topic with no deeper coverage gets no xref (a button to nowhere is clutter). |
| Semantic colors | green = positive / in-scope / confirmed; red = negative / penalty / out-of-scope; amber = conditional / threshold / single-source. **Constant across every theme** — they encode meaning, not brand, so only the brand set changes when the theme switches. |
| Verbatim quote | Official text (law, spec, standard) shown byte-for-byte in a monospace `.lawtext` block + a source line. Quote is *extracted*, never paraphrased or generated. |
| Datum badges | Four visible states beyond normal (=2×-confirmed): `single` (amber — exactly 1 source), `unverified` (red — context only, no datum depends on it), `disputed` (red dashed — credible sources conflict; the badge links to the contradiction note showing BOTH readings), `derived` (primary outline — the brief's own inference; the badge's popover shows the premise quotes + the reasoning sentence, per verification.md Rule 9). Badge state is mechanical (source count + contradiction record + presence of a `derivation` object), never judgment. |
| Access date + disclaimer | Every report shows source access dates (and publication dates in the Sources table; `unknown` when undated) plus an "informational only — not advice or a binding opinion" notice. The notice is **one compact line in the header meta row**, not a full-width banner — it must be visible and printable without costing a third of the first screen. |
| Unknowns section | Mandatory closing section listing open questions (what was sought, not found, why). Rendered as a `<details>` whose summary carries the count ("Unknowns (3)") — present and countable at a glance, expanded on demand, force-open in print and on search hit. Multi-aspect topic → optionally a small gap matrix (aspect × answered/partial/open) instead of a flat list. |
| Trust strip + method details | Verification status is **signals, not prose**: a single quiet `.trust` line (first block of `main`) shows Confidence (colored dot + text label — never color alone) **with its plain-language sentence**, 2×-confirmed % (mini severity meter), source count (official split), access date, and a `{Method}` link. No band name ever ships bare: `MEDIUM` alone is a defect — it reads "Medium — most facts are double-confirmed, {n} rest on a single source". Full label sentences: verification.md § Confidence. The method **explanation** lives once in the collapsed `#method` details beside Sources. Never open the report with method prose or large self-referential stat tiles — the first screen belongs to the topic (BLUF). |
| Confidence target | HIGH is the delivery target (verification.md Rule 12). Below HIGH → the report carries a **"What would make this HIGH"** block: one plain-language line per remaining blocker. A brief that ships MEDIUM without that block is incomplete. |
| Calm first screen | Everything that is not the answer starts collapsed: Sources, `#method`, corpus ledger, contradiction notes, appendix detail. Open by default: the topic's own content, the trust strip, the action list. A reader who scrolls once must see findings, not apparatus. |

## Authoring language (how the text itself is written)

Sourced from Minto Pyramid Principle / BLUF and UK Government Analysis Function guidance (2025). These bind the prose, not the layout:

| Rule | Detail |
|------|--------|
| Answer first (BLUF) | The executive summary opens with the conclusion/recommendation, then support — never background-first. Each section lead does the same at section scale. |
| Descriptive headings | Section titles state the finding, not the category: "Deposit is capped at 3 months' rent", not "Findings". (Nav labels may stay short; `h2` carries the message.) |
| Sentence budget | Target ~25 words per sentence; split anything that needs two breaths. Assume a smart reader with zero domain background (audience setting may raise this). |
| No spatial references | Never "as shown above/below" — collapsed/branched/reflowed content breaks spatial order. Use an `.xref` or a named link ("see *Penalties*"). |
| Descriptive links | Link text names the destination ("TBK art. 344 full text"), never "click here" / bare URL. |
| Front-load key content | Most important content top-left / first in every list and section (F-pattern scanning); ordering is by importance, not chronology of discovery. |
| Audience register | Phase 1 may set an audience (general reader default / expert). General: every term explained at first use, examples concrete. Expert: terms unexplained, denser sentences allowed — the verification discipline never changes. |

## Print / PDF discipline (the new emphasis)

`@media print` block must:
- Hide sticky nav, search box, toggle buttons, the "Print/PDF" button, and any interactive control.
- Force-open collapsed content — accordions/`details`/tabbed views get `display:block!important` so nothing prints hidden.
- `break-inside:avoid` on cards, calculators, tables, quote blocks.
- Drop shadows and dark backgrounds (`body{background:#fff}`; invert `.lawtext` to light).
- Expose link targets: `a[href]:after{content:" (" attr(href) ")"}` so URLs survive on paper — but suppress it for in-file anchors (`a[href^="#"]:after{content:""}`): nav/xref/disputed targets are noise on paper.
- Typography at the break: `p,li{orphans:3;widows:3}` (browser default 2 leaves lone lines); `@page` margins in absolute units (mm — viewport units don't map to paper); long tables keep semantic `<thead>` so the browser repeats the header on every page.

A visible **"🖨 Print / PDF"** button calls `window.print()` → the browser's "Save as PDF" yields a clean document. JS must force-open all collapsible sections on `beforeprint` (in case CSS alone misses a JS-driven toggle).

## Theming (selectable, akis palettes + validated dark)

- **6 embedded light palettes** in a `THEMES` JS object (from `akis/src/constants/palettes.js`): `slate, teal, emerald, indigo, rose, amber`. Each sets only the brand 5 — `primary, accent, bg, surface, text`. **Default = `slate`** (neutral, corporate — best for report/legal content).
- **`dark` palette** (7th): near-black bg (never `#000` — halation), desaturated accents. Dark may additionally re-tune **semantic lightness only** (same hue family: `ok/bad/warn` brightened for dark surfaces) plus the on-color trio `onprim/onbad/onwarn` (text on primary/bad/warn fills — CSS falls back to `#fff` when unset). Keys a theme omits reset to `:root` defaults on switch. A dark toggle does **not** satisfy WCAG by itself — every changed pair re-passes 4.5:1 text / 3:1 UI before shipping (see validation note below).
- **OS preference:** no stored choice → `prefers-color-scheme: dark` selects `dark`; an explicit user selection always wins. `color-scheme` is declared (`light` at `:root`, `dark` under `[data-theme="dark"]`) so form controls/scrollbars follow.
- A theme `<select>` in the nav switches live; choice persists via `localStorage` (try/catch — `file://` may block it). `data-theme` on `<html>` + `CONFIG.palette` give a JS-off default.
- **Derived tokens via `color-mix()`** (theme-reactive, no hardcoded greys): `--mut`, `--line`, all `*bg` tints, shadows are mixed from brand+semantic colors, so they stay coherent on every theme.
- **Color-injection guard (`safeColor()`)** — every color value applied at runtime (theme set, any `CONFIG` color) must pass a `#hex | rgb()/rgba() | hsl()/hsla()` regex before `setProperty`; rejected values are ignored (akis BP-030). Never inject an unvalidated color.

## Chrome, width & the first-screen budget

Chrome is everything that is not the report: header, nav, tools, trust strip, disclaimer. It is overhead, and it competes with the answer for the reader's first screen.

| Rule | Detail |
|------|--------|
| Header is one compact band | Title + one-line subtitle + a single inline meta row (as-of date · source count · the one-line "informational only" notice). No full-width disclaimer banner, no stacked meta bars, no stat tiles. Budget: the header occupies **≤ 150px at desktop widths**; at 1280×800 the reader's first screen already shows the first finding, not just branding. |
| Nav is exactly one row, at every width | Section links live in a horizontally scrollable strip (`overflow-x:auto`, hidden scrollbar, momentum scroll); the tool cluster is pinned right and never wraps. A nav that wraps to two or three rows on a long report is a bug, not a responsive behavior. `--navH` stays measured live (ResizeObserver) for scroll-padding. |
| Tools are icon-first, right-pinned, ordered by frequency | Search → theme → print, right-aligned in that order. Search is an icon that expands to an input on `:focus-within` (CSS only — no JS dependency, keyboard-reachable); theme is an icon-labelled `<select>`; print shows its label ≥900px and goes icon-only below. Every icon-only control carries an `aria-label` and a `title`. Coarse pointers still get ≥44px targets. |
| Width adapts to the screen, text to the eye | `.wrap` is `min(1560px, 96vw)` — never a fixed 1080px cap: a 27" screen must not read like a phone with margins. **Prose** is constrained separately by `--measure: 72ch` so lines stay readable; tables, matrices, grids, charts, and the action list take the full wrap width. Two different constraints, two different jobs. |
| Collapsed by default | Sources table, `#method`, corpus ledger, contradiction notes, long verbatim text, appendix detail. Each `<details>` summary carries a count or a one-line gist, so collapsed never means hidden ("Sources (202)", "Unknowns (3)"). Search and print force them open (existing behavior). |
| Back to top is always present | Fixed bottom-right, appears after 400px of scroll, ≥44px on coarse pointers, above the iOS safe area, hidden in print. It is core chrome — never pruned with an optional block. |
| Size budget | Target ≤ 1.5 MB for the single file. Over budget → prune unused `ds-opt` blocks, move bulk verbatim text into collapsed `<details>`, dedupe repeated quotes. Never split the file (single-file is a hard requirement), and never buy space by dropping sources, Unknowns, or the coverage ledger. |

## Compact / density (akis firm-site)

- **Fluid spacing scale:** one `clamp()` scale (`--space-2xs … --space-xl`), not per-breakpoint padding overrides. Section padding/gap pull from it → tight on small screens, airy on large, no media-query sprawl.
- **Intrinsic grids:** `repeat(auto-fit, minmax(min(280px,100%), 1fr))` + every grid child `min-width:0` — responsive with **zero breakpoints**.
- **1px section rhythm:** `.sec + .sec { border-top:1px solid var(--line) }` instead of large vertical gaps.
- **Accent-bar headings:** `h2::after` 36×3px gradient bar anchors each heading without bulk.
- **Two-column strip (`.strip`):** pack related blocks (e.g. contact + about, or two short cards) side by side to shorten the page; collapses to one column intrinsically.
- **Pill-chip dense listing (`.pills`/`.pill`):** short items as tight rounded chips with a gradient-dot bullet — never half-empty cards.
- Readable measure: long body text capped at `--measure: 72ch` — the container is wide, the *text line* is not (see § Chrome, width & the first-screen budget).

## Dataviz layer (validated 2026-07-18, dataviz-skill six-checks)

- **Trust strip + meter:** report-meta numbers live in the one-line `.trust` strip (see Hard requirements), never in large stat tiles — self-referential metrics must not outrank content. **Topic** headline numbers (the subject's own KPIs) may still use stat-tile treatment inside sections. The coverage meter's fill carries severity (`ok ≥80 / warn ≥50 / bad <50`), its unfilled track is a **lighter step of the same hue** (`color-mix` 15%), and it carries an `aria-label` with the plain-language reading.
- **Comparison bars (`ds-opt:chart`):** only for 2–7 comparable magnitudes (rates, costs, limits); >7 items → table only. Single hue: fill = **theme `--primary`** (all 6 themes ≥3:1 on surface — validator PASS). **Emphasis form:** `hl:true` keeps the primary hue and every other row is auto-dimmed to gray — never primary-vs-accent (validator: indigo ΔE 7.9, rose 13.6 = normal-vision FAIL; 4 accents < 3:1 contrast). The dim gray's contrast WARN is relieved as the validator requires: every bar carries a direct value label and a `<details>` data table is built from the same items.
- **Mark specs:** bar 18px (≤24 cap), 4px rounded data-end + square baseline, 2px surface gaps between rows, 1px hairline baseline, labels/values in text tokens (never the series color).
- **Value placement (deliberate deviation):** values sit in a fixed right-aligned column (an implicit value axis), not at each bar tip — guarantees zero label/mark overlap at every viewport width; the data table carries exact values. Tooltips are omitted: every mark is already direct-labeled + tabled.
- Before changing any theme, semantic, or chart color: run the `dataviz` skill's `scripts/validate_palette.js` when installed; absent → run an equivalent WCAG pair check (script the contrast ratios of every changed text/bg and UI/bg pair; `color-mix` = linear sRGB interpolation) and record the observed PASS list. Never ship an unvalidated color change.

## Matrix layer (`ds-opt:matrix` — entity×attribute comparison)

**Activate when** the topic compares 2+ entities on shared attributes (products, plans, jurisdictions, options). The matrix IS the data — no chart substitutes it (Elicit/SciSpace pattern: audit needs exact values).

| Rule | Detail |
|------|--------|
| Cell-level provenance | Every **filled** cell carries a `.cellcite` superscript (`data-cite` → the same quote popover as chips). A number without a per-cell citation is not a matrix cell — it's an unsourced claim. |
| Explicit gaps | A value not found in sources is an explicit `.miss` "—" cell (with a "{not found in sources}" title) — a visible gap, never silently blank and never guessed. |
| Completeness score | Each row ends with `N/M` attributes-found (`.cmp`; amber `.part` when incomplete) — the per-entity thin-evidence signal (Consensus Study Snapshot pattern). Silently omitting a column for one entity is forbidden. |
| Verification carries over | Cell values follow the same 2×/single/disputed discipline as prose datums; a single-source cell's `.cellcite` popover shows exactly one quote — that is its badge. |
| Same-or-different verdict (2-entity comparisons) | Comparing exactly two regimes/products/jurisdictions → every row ends with a verdict tag: `same` · `differs` · `only-A` · `only-B`, each derived mechanically from the cells (identical values → `same`; one side `—` → `only-X`). A "show differences only" toggle filters to non-`same` rows; print keeps every row with its verdict. This is what answers "where are these two actually the same, and where not" in one table instead of two. |
| Verdict is a datum | A `same` verdict on two differently-worded provisions is a **derived** claim (verification.md Rule 9): it carries the `derived` badge and names the equivalence reasoning. Superficially similar rules with different scope are `differs`, not `same`. |

## Branching layer (`ds-opt:branch` — scenario/persona adaptive content)

**Activate when** the topic splits by reader role or situation — tenant/landlord, employee/employer, buyer/seller, fixed/indefinite contract, company-size bands. One clear signal: the same question has different answers depending on who is asking. No such split → prune the block entirely (a selector with one meaningful option is clutter).

| Rule | Detail |
|------|--------|
| One decision = one `.choices[data-key]` group | `.choice` buttons carry `data-val`; the last option is always the localized "Show all" reset (`data-val=""`). Level-1 (persona) uses `.choices.big` cards with icon + one-line description; nested levels use compact pills. |
| Tree depth is free | Nest a `.choices` group inside a `data-when` block — the child decision appears only when its parent branch is selected. Grammar: `data-when="key:val"`, OR via `\|` (`persona:tenant\|landlord`), AND via space (`persona:tenant contract:fixed`). |
| Presentation-only filtering | ALL branches ship in the file; selection toggles `hidden` only. No selection (or JS off) = everything visible. Print force-shows every branch. Accuracy discipline is branch-independent: every branch block keeps its own source chips/badges; Unknowns and Sources are never branch-filtered. |
| `.whochip` on every branch block | Names the block's branch at all times — the reader (and the printout) always knows whose rule a block states. |
| A11y | Buttons carry `aria-pressed`; each group `role="group"` + `aria-label`; a visually-hidden `aria-live` region (`#branchLive`) announces the choice. |
| Persistence | Selection persists per key via `localStorage` (try/catch); "Show all" clears it. |
| `--static` | Drop the `.choices` controls, keep every branch expanded with its `.whochip` label. |

### Many-dimension topics (3+ decisions)

Per-combination blocks explode: 6 dimensions × 4 values is 4096 possible readings, and authoring them as `data-when` cards guarantees gaps. Above **2 dimensions**, switch representation:

| Rule | Detail |
|------|--------|
| Rule-tagged items, not combination blocks | Author the *rules* once, each carrying the condition under which it applies (`when="entity:ltd\|as data:special transfer:abroad"`). The filter evaluates conditions against the reader's selections; content scales linearly with the rule count, not with the product of the dimensions. Branch **cards** stay for genuinely narrative per-persona content; everything obligation-shaped becomes a rule-tagged item feeding the action list below. |
| Order dimensions by discriminating power | The first question asked is the one that changes the most answers (usually role/entity type), then data sensitivity, then activity, then geography. Never ask a question whose answer changes nothing in this brief — if no item's `when` references a key, that decision does not exist. |
| Every dimension declares its full value set | The value list is exhaustive over the topic's real-world cases, with a documented catch-all ("other / not listed"). A missing value silently gives the reader an empty, falsely reassuring result. |
| Unanswered decisions are visible | Any key with no selection → the action list shows a "{n} questions unanswered — this list may be incomplete" note naming them. Partial input must never look like a complete answer. |
| Combinations that cannot occur | An impossible pairing (e.g. "natural person" + "board resolution required") is stated as such in one line, not silently empty. |

**Standard dimension: legal-entity type.** For any brief where obligations differ by who the reader legally is, this dimension is mandatory and its value set starts from — extended, never trimmed, per topic:

`natural person (private, non-commercial)` · `natural person acting commercially (sole trader / self-employed professional)` · `ordinary partnership` · `limited liability company` · `joint-stock company` · `cooperative / association / foundation` · `public body` · `foreign-established entity with a local branch or liaison office`

Each value's row in the report states the two things that actually differ: **who is the responsible person** (the individual vs the legal entity vs its representative) and **who is personally exposed** when the obligation is missed. A brief that merges "sole trader" into "company" hides exactly the difference the reader came for.

## Action list layer (`ds-opt:todo` — "exactly what you must do")

**Activate when** the brief tells the reader to *do* things — legal, regulatory, procedural, or process topics. This is the payload block: the reader's selections in the branch layer assemble into a concrete, ordered, personalized checklist.

| Rule | Detail |
|------|--------|
| Authored once, filtered by the same evaluator | Each item is authored as a rule-tagged `<li data-when="…">` — the same grammar and the same pass that filters branch content. One rule, one place; the checklist and the prose can never disagree (SSOT). Authored markup, not JS-rendered: with scripting off the reader still gets the whole list, each item carrying its condition chip. JS only counts, labels the profile, and flags unanswered decisions. |
| Ordered at authoring time | Mandatory → prohibited → recommended → optional, each group a separate `<ol class="todo">` under its heading; within a group, earliest deadline first. The order is part of the content, not a runtime sort. |
| Every item is complete on its own | An item carries: obligation badge (`must`/`mustnot`/`should`/`may`), the action in plain imperative language, **who** it falls on, **by when** (deadline chip, linked to the deadline table), **where/how** it is done (portal, form, filing), and ≥1 source chip. An item missing the "by when" or the "how" is half an instruction. |
| Applicability is a datum | The `when` condition is itself sourced. Where applicability is the brief's own inference rather than a source's statement, the item carries the `derived` badge with its premises (verification.md Rule 9). |
| Grouped by force, ordered by deadline | Mandatory first, then prohibited, then recommended, then optional; within a group, earliest deadline first. Never alphabetical — the reader's risk is chronological. |
| Profile line + count | The list opens with the reader's resolved profile in words ("Limited company · processes special-category data · transfers abroad") and the count ("14 obligations apply to you"), plus the unanswered-questions note when any decision is unset. |
| No selection = everything, labeled | JS-off, print, or no selection → every item is present with its condition label. Nothing is ever *only* reachable through the selector, and `--static` needs no special case: the list is already static markup, only the controls drop. |
| Personal print is opt-in and labeled | An explicit "print only my items" toggle narrows **the action list section only**; the printout carries the profile line so the page is never ambiguous. Default print = every item with its conditions, per the branch-layer accuracy rule. |
| Copy-out | A "copy list" control writes the resolved list as plain text via the async clipboard API inside try/catch; on failure it reveals a pre-selected `<textarea>` instead. No network, no dependency. |

## Corpus coverage ledger (`ds-opt:coverage`)

**Activate when** the topic has a finite authoritative corpus the brief claims to cover — a statute's articles, a regulation's sections, a standard's clauses, an API's endpoints. Search-completeness metrics answer "how hard did we look"; only an enumerated ledger answers "did we miss an article".

| Rule | Detail |
|------|--------|
| Enumerate from the source, not from memory | The unit list is extracted from the official text's own table of contents at research time. A ledger built from recollection is worse than none. |
| Three statuses, no fourth | `covered` (with the in-file anchor where it is treated) · `out-of-scope` (with a one-line reason the reader can disagree with) · `gap` (searched, not resolved — also appears in Unknowns). |
| Counts are recomputed | The ledger's header line ("31 covered · 2 out of scope · 0 gaps of 33") is computed from the rows at build, never asserted. |
| Collapsed by default | It lives in a `<details>` near Sources — it is an audit instrument, not reading material. Its one-line summary carries the counts. |
| Zero gaps is a HIGH-gate condition | A `gap` row blocks the HIGH confidence label (verification.md § Confidence, line `corpusNoGaps`). |
| Multi-instrument topics | One ledger per instrument, in one table with an instrument column — a comparison brief must show coverage on both sides, or the comparison is asymmetric by construction. |

## Normative brief — required blocks

Any brief whose content is law, regulation, or official procedure ships these, in addition to obligation badges:

| Block | Rule |
|-------|------|
| **Currency line** | Every normative section states the version it reflects: "current consolidated text as of {date}; last amended {instrument, date}". A provision changed *in part* by a later decision is quoted in its current wording, with the change named — never the superseded text (verification.md Rule 11). |
| **Deadlines table** | Every period in the brief in one table: trigger event → period → counted from (calendar/business days, from notification/from awareness) → consequence of missing it → source. Scattered deadlines are missed deadlines; the action list's deadline chips link here. |
| **Sanctions table** | Consequence → who imposes it → range → appeal path → **index year of the amounts** and the revaluation rule. An amount without its year is stale-in-waiting (verification.md Skill-side gate). |
| **Escalation triggers** | The honest counterpart to the "informational only" notice: a short list of situations where the reader must stop and get professional or regulator input, each with the concrete signal that triggers it. A brief cannot make a lawyer unnecessary; it can tell the reader exactly when one becomes necessary — and cover everything else completely. |
| **Obligation rank** | Every `must`/`mustnot` badge traces to an N1-N4 instrument (craap.md § Normative source ladder). Guidance and recitals justify `should` at most. |

## Obligation levels (`ds-opt:oblg` — legal/official/rules content)

**Activate when** the brief contains normative content — law, regulation, official procedure, standards, contractual rules. The reader must never have to guess whether a statement binds them.

| Rule | Detail |
|------|--------|
| One badge per normative statement | Every actionable/normative claim opens with exactly one `.oblg` badge: `must` (Mandatory — sanctioned if skipped) · `mustnot` (Prohibited — sanctioned if done) · `should` (Recommended — advisable, no sanction) · `may` (Optional — reader's choice) · `free` (No effect — changes nothing). Labels localized at build. |
| Level traces to the source | The badge mirrors the source's own wording ("shall"/"must"/"may"/"is prohibited") — never inferred stricter or looser than the source states. The obligation level is itself a datum: it follows the same ≥2-source / "single source" badge discipline as any other claim. Ambiguous wording → the weaker level + a note naming the ambiguity. |
| Legend once | A compact `.oblg-legend` strip appears above the first badged content, explaining all five levels in one line each. |
| Shape ≠ source chips | `.oblg` is square-ish and leading; source chips are pills and trailing — the two signal classes never blur. Never color alone: the label text always carries the meaning (must and mustnot share the hard-rule red deliberately). |
| Descriptive content exempt | Purely descriptive claims (history, statistics, definitions) carry no badge — badging everything would bury the normative signal. |

## Ornament budget (what is NOT in the report)

A research report earns trust by looking like it has nothing to hide. Every visual element either encodes information or competes with it — there is no neutral decoration. Removed deliberately, and not to be reintroduced:

| Removed | Why |
|---------|-----|
| Scroll-reveal animation | Hid content until scrolled, cost an observer, encoded nothing. A report is read, not experienced. |
| Header glow orbs / gradient blobs | Pure ornament; the first screen belongs to the answer. |
| Card hover-lift and meter fill animation | Micro-interactions that carry no data. |
| Six-palette theme menu | Palette is the *report's* choice (`CONFIG.palette`, set at build); the reader's legitimate need is reading comfort → one **light/dark toggle**, one control fewer in the nav. |
| Unused icon symbols | The sprite ships only symbols the report actually `<use>`s. |
| Repeated scalars | A number appears in exactly one place (the source count lives in the trust strip, not also in the header). Dead `CONFIG` keys are deleted, not left "for later". |

Kept, because each is a signal: reading-progress bar (position), scrollspy (position), semantic colour (meaning), obligation badge shape (force), accent bar under `h2` (hierarchy), tabular figures (comparability). Motion that remains is limited to state transitions and dies under `prefers-reduced-motion`.

- **Icon sprite (`ds-opt:icons`):** inline `<symbol>` sprite, `currentColor` strokes, used via `<svg class="ico"><use href="#i-…"/></svg>`; decorative uses carry `aria-hidden="true"`. Add a symbol when a `<use>` needs it; prune when none remains. Never emoji in structural UI.

## Narrative spine (what the reader gets in the first screen)

| Element | Rule |
|---------|------|
| Governing thought | The summary's `h2` is the single assertion the whole brief establishes — not "Summary". |
| 3-5 key messages | `ol.keymsg`: each an assertion carrying its number, one line of support, and a link to the evidence (`a.exref` / `.xref` / source chip). A reader who reads only this list must be able to act. Fewer than 3 means the brief has no argument; more than 5 means it has no priorities. |
| Scope box | One line: what this answers · for whom · what it excludes. A brief that never states its boundary invites the reader to assume it covers their case. |
| "So what" per section | Each section closes with `p.sowhat`: the consequence, not a restatement of the finding. |
| Worked example (`ds-opt:vignette`) | One concrete actor walked through the rules end to end, **every step sourced** — a walkthrough is an argument, not an illustration. |
| Glossary (`ds-opt:glossary`) | Defined terms, collapsed, linked from first use. Explaining a term in place still fails the reader who lands in section 6 from a search. |
| What changed (`ds-opt:changed`) | On a re-run only: what moved since the previous version and the instrument that moved it. A flip with no named source change is an extraction error, not an update. |
| Exposure chip | Action items carry what is at stake if missed (`.expchip low/med/high` + the amount), so a long list can be triaged. The value is a datum and carries its source. |
| Deadline timeline (`ds-opt:timeline`) | Periods get a timeline exhibit as well as the table: the table gives values, only the sequence shows order and gaps — which is what the reader plans against. Hard deadlines carry the red marker. |

## Evidence bundle (what ships beside the HTML)

Default output is a directory, not a lone file: `report.html` · `findings.json` · `sources/` (every **cited** source as fetched — page text or the original PDF) · `sources/MANIFEST.json` (`citationId → localFile, url, finalUrl, sha256, bytes, retrievedAt, primary, tier`). The Sources table gains a **local copy** column (path + short hash); drop that column under `--no-archive`.

Why it earns its place: a citation to a page that later changes is unverifiable, and on a re-run the stored hash decides *mechanically* whether the source changed or the reading did (verification.md Rules 8, 18). Not archivable (paywall, login, size cap) → recorded as such, and an un-archivable load-bearing primary source goes to Unknowns. **The HTML stays fully self-sufficient with or without the bundle.**

## Exhibit discipline (every table, chart and diagram)

The most visible line between a professional report and a long web page. Non-negotiable for any figure carrying data:

| Rule | Detail |
|------|--------|
| Numbered, in document order | Each is a `<figure class="exh">` numbered at load by JS (`Exhibit 1, 2, …`). Never hand-numbered — a reordered or pruned exhibit would leave stale references behind. |
| Caption states the finding | `.extitle` is an **assertion**: "Penalty ceilings differ by a factor of 20", never "Penalties by regime". A reader who skims only captions must come away with the argument. A caption that names a category instead of a finding is a defect, not a style choice. |
| Source line on the exhibit | `.exsrc` carries unit/period/as-of + the source chips. An exhibit whose provenance lives only in body text is unciteable once it is screenshotted. |
| Referenced from the text | The prose points at it with `<a class="exref" href="#ex-…">`; JS writes the label from the target, so it always says the right number. An exhibit nothing references is either unnecessary or the text is missing a sentence. |
| Indexed | The print-only exhibit index lists every one with its caption — built from the document, so it cannot drift. |

## Print artifact (the PDF is what gets forwarded)

| Element | Rule |
|---------|------|
| Cover page | Print-only `section.cover`, `break-after:page`: title, subtitle, as-of date, confidence + its plain-language sentence, source/coverage counts, version, scope statement, disclaimer. Every value comes from `CONFIG` — no facts that exist only on the cover. |
| Contents + exhibit index | Print-only `nav.toc`, `break-after:page`, built by JS from the document's own `h2`s and exhibits. |
| No fake page numbers | Chrome does not support `@page` margin-box counters, and a pagination library would break the single-file rule. The contents lists sections and exhibits **without** page numbers rather than inventing them. State this limitation rather than papering over it. |
| Everything else | Per § Print / PDF discipline below: chrome hidden, collapsibles force-open, `break-inside:avoid` on cards/exhibits/tables, absolute `@page` margins, orphans/widows 3. |

## Interaction (adaptive)

**Always on:** sticky one-row nav with **condensed report title** (appears when the header scrolls out; hidden ≤900px), **scrollspy** (`aria-current` on the active section's nav button), **reading-progress bar** (2px gradient under the nav), **back-to-top** button (appears after 400px), theme switcher, live search with `<mark>` highlight (auto-opens any `<details>` containing a match), source chips, verbatim-text toggles.
**Collapsibles = native `<details>/<summary>`** (work with zero JS; `id` + hash deep-link opens the target on load/`hashchange`). **Disclosure depth ≤ 2 levels** (NN/g: beyond two, readers get lost) — deeper structure becomes sections + xrefs, not nested accordions.
**Topic-dependent (only if it genuinely helps, e.g. tax / labor / pricing):** interactive calculator, scenario wizard. Don't add a calculator to a topic that has nothing to compute.
**`--static`:** minimal JS, document-pure output (everything expanded, no toggles) — safest for archival/printing.

## Layout & a11y

- Responsive via intrinsic grids + fluid spacing; canonical breakpoints only when truly needed (`900` condensed nav title, `640` nav wrap, `380` chart label stacking).
- **Wrap/overlap discipline:** `overflow-wrap:break-word` inherited from `body` (long words/URLs never force horizontal overflow — test 320px); `text-wrap:balance` on headings, `pretty` on paragraphs; every grid/flex child that can shrink carries `min-width:0`; chart bars grow inside a dedicated `.plot` box so the value column can never be overlapped.
- **Sticky-chrome offset is measured, not hardcoded:** JS keeps `--navH` = live nav height (ResizeObserver); `html{scroll-padding-top:calc(var(--navH) + 10px)}` so anchors and tabbed-to elements never land under the bar, even when the nav wraps to two rows.
- **Contrast rules:** links + focus ring + law-button text use `--primary`, never `--accent` (accents fail 4.5:1 text / 3:1 focus contrast on several themes — slate `#0ea5e9` = 2.7:1). Interactive-control borders use `--ctl` (30% text mix), stronger than the decorative `--line` (13%).
- **Touch targets:** `@media(pointer:coarse)` bumps nav buttons / tools / print / law buttons to ≥44px and back-to-top to 48px.
- Semantic HTML5 (`header`, `nav`, `main`, `section`, `footer`, `h1-h3`, `ul/li`, `details/summary`).
- **Skip link** (`.skip`) first in `<body>`; `prefers-reduced-motion` guard disables transitions; `[hidden]{display:none!important}` wins specificity battles.
- **Inline SVG icons** (`svg.ico`, `currentColor`) for search/print/theme — no emoji in structural controls (cleaner print), no icon font.
- `env(safe-area-inset-bottom)` padding on footer for iOS notch.
- Keyboard navigable; color contrast targets Lighthouse a11y ≥ 90.

## Security (hard)

- Fill text via `textContent` / DOM node creation — **never `innerHTML`** with data values (XSS defense).
- No inline event handlers (`onclick=`); wire everything with `addEventListener`.
- Search highlight wraps matches by splitting text nodes and inserting `createElement('mark')` — not by `innerHTML`.
- Every runtime color value passes `safeColor()` before being applied (CSS-injection defense).
- Zero external dependencies; nothing loads over the network.

## Two authoring patterns (pick per topic)

| Pattern | When | Example |
|---------|------|---------|
| **Static HTML + `[data-cfg]` spans** | Prose-heavy brief, few computed numbers | gvk-20b: sections authored in HTML, scalars injected from CONFIG |
| **Data-driven render** | Many repeated cards/rows from structured findings | is-hukuku: a `DATA` object, JS builds topic cards / tables / source chips |

The skeleton supports the static+CONFIG pattern by default (simplest, least error-prone). For a findings-heavy brief, the skill may render sections from the artifact's `sections[]` using safe DOM construction.
