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
| Datum badges | Three visible states beyond normal (=2×-confirmed): `single` (amber — exactly 1 source), `unverified` (red — context only, no datum depends on it), `disputed` (red dashed — credible sources conflict; the badge is a link to the contradiction note showing BOTH readings). Badge state is mechanical (source count + contradiction record), never judgment. |
| Access date + disclaimer | Every report shows source access dates (and publication dates in the Sources table; `unknown` when undated) plus an "informational only — not advice or a binding opinion" notice. |
| Unknowns section | Mandatory closing section listing open questions (what was sought, not found, why). Multi-aspect topic → optionally render as a small gap matrix (aspect × answered/partial/open) instead of a flat list. |
| Trust strip + method details | Verification status is **signals, not prose**: a single quiet `.trust` line (first block of `main`) shows Confidence (colored dot + text label — never color alone), 2×-confirmed % (mini severity meter), source count (official split), access date, and a `{Method}` link. The method **explanation** (what the labels mean + `searchCompleteness` — how completely the space was *searched*, distinct from claim confidence) lives once in the collapsed `#method` details beside Sources. Never open the report with method prose or large self-referential stat tiles — the first screen belongs to the topic (BLUF). |

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

## Compact / density (akis firm-site)

- **Fluid spacing scale:** one `clamp()` scale (`--space-2xs … --space-xl`), not per-breakpoint padding overrides. Section padding/gap pull from it → tight on small screens, airy on large, no media-query sprawl.
- **Intrinsic grids:** `repeat(auto-fit, minmax(min(280px,100%), 1fr))` + every grid child `min-width:0` — responsive with **zero breakpoints**.
- **1px section rhythm:** `.sec + .sec { border-top:1px solid var(--line) }` instead of large vertical gaps.
- **Accent-bar headings:** `h2::after` 36×3px gradient bar anchors each heading without bulk.
- **Two-column strip (`.strip`):** pack related blocks (e.g. contact + about, or two short cards) side by side to shorten the page; collapses to one column intrinsically.
- **Pill-chip dense listing (`.pills`/`.pill`):** short items as tight rounded chips with a gradient-dot bullet — never half-empty cards.
- Readable measure: long body text capped at `--measure: 68ch`.

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

## Obligation levels (`ds-opt:oblg` — legal/official/rules content)

**Activate when** the brief contains normative content — law, regulation, official procedure, standards, contractual rules. The reader must never have to guess whether a statement binds them.

| Rule | Detail |
|------|--------|
| One badge per normative statement | Every actionable/normative claim opens with exactly one `.oblg` badge: `must` (Mandatory — sanctioned if skipped) · `mustnot` (Prohibited — sanctioned if done) · `should` (Recommended — advisable, no sanction) · `may` (Optional — reader's choice) · `free` (No effect — changes nothing). Labels localized at build. |
| Level traces to the source | The badge mirrors the source's own wording ("shall"/"must"/"may"/"is prohibited") — never inferred stricter or looser than the source states. The obligation level is itself a datum: it follows the same ≥2-source / "single source" badge discipline as any other claim. Ambiguous wording → the weaker level + a note naming the ambiguity. |
| Legend once | A compact `.oblg-legend` strip appears above the first badged content, explaining all five levels in one line each. |
| Shape ≠ source chips | `.oblg` is square-ish and leading; source chips are pills and trailing — the two signal classes never blur. Never color alone: the label text always carries the meaning (must and mustnot share the hard-rule red deliberately). |
| Descriptive content exempt | Purely descriptive claims (history, statistics, definitions) carry no badge — badging everything would bury the normative signal. |

## Motion & visual polish (all guarded)

- **Scroll-reveal:** JS adds `.reveal` then `.in` on intersection (cards, KPIs, notes, accordions, chart figures). Progressive enhancement — JS-off, `prefers-reduced-motion`, and print all render fully visible; never author `.reveal` into the HTML by hand.
- **Hover elevation:** cards + KPI tiles lift (`translateY(-2px)` + `--shh` shadow step) under `@media(hover:hover)` only; coverage-meter fill animates width once on load.
- **Header glow orbs:** two pure-CSS radial-gradient decorations on `header.top` (`::before`/`::after`) — no images, hidden in print.
- **Icon sprite (`ds-opt:icons`):** inline `<symbol>` sprite (info, alert, check, doc, scale, calc, user, home, q, link), `currentColor` strokes, used via `<svg class="ico"><use href="#i-…"/></svg>`; decorative uses carry `aria-hidden="true"`. Prune when no `<use>` remains. Never emoji in structural UI.
- All motion dies under `prefers-reduced-motion` (global transition kill + explicit `.reveal` opt-out) and in print (`.reveal{opacity:1}`).

## Interaction (adaptive)

**Always on:** sticky nav with **condensed report title** (appears when the header scrolls out; hidden ≤900px), **scrollspy** (`aria-current` on the active section's nav button), **reading-progress bar** (2px gradient under the nav), **back-to-top** button (appears after 600px), theme switcher, live search with `<mark>` highlight (auto-opens any `<details>` containing a match), source chips, verbatim-text toggles.
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
