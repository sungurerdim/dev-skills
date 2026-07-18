# Report Template Conventions

Distilled from four hand-built guides (gvk-20b, vergi-kilavuzu ×2, is-hukuku) and the akis design system (`akis/assets/tokens.css`, `akis/dist/firm-site.html`, `akis/src/constants/palettes.js`). `assets/brief-template.html` is the concrete, working skeleton of these rules — clone and fill it; never generate the HTML from scratch (lowers hallucination risk). These conventions are the *why*; the skeleton is the *what*. All visible label strings here are canonical English — localized to the request language at build (SKILL.md Contract).

## Hard requirements (every brief)

| Convention | Rule |
|------------|------|
| Single-file / offline | All CSS + JS + data embedded. **No external fonts** (`system-ui` / `-apple-system` stack), no CDN, no network call. View-source must be self-sufficient → offline + reliable PDF. |
| SSOT data block | Every number/rate/date/quantity lives once, in a single `CONFIG` JS object. HTML reads them via `[data-cfg="key"]` spans, filled by one render pass. Edit one place → all prose/tables/calc update. |
| Source chip | Two visible chip types: `official` / `secondary` (secondary = T3-T6, amber). Every claim carries one. |
| Semantic colors | green = positive / in-scope / confirmed; red = negative / penalty / out-of-scope; amber = conditional / threshold / single-source. **Constant across every theme** — they encode meaning, not brand, so only the brand set changes when the theme switches. |
| Verbatim quote | Official text (law, spec, standard) shown byte-for-byte in a monospace `.lawtext` block + a source line. Quote is *extracted*, never paraphrased or generated. |
| Access date + disclaimer | Every report shows source access dates (and publication dates in the Sources table; `unknown` when undated) plus an "informational only — not advice or a binding opinion" notice. |
| Unknowns section | Mandatory closing section listing open questions (what was sought, not found, why). |
| Confidence + coverage | A **KPI stat-tile row** (first block of `main`) shows Confidence (colored dot + text label — never color alone), 2×-confirmed % (with a severity meter), source count (official/secondary split), and access date. Tile contract: uppercase label · large value (proportional figures, fluid `clamp()` size) · muted sub-line. |

## Print / PDF discipline (the new emphasis)

`@media print` block must:
- Hide sticky nav, search box, toggle buttons, the "Print/PDF" button, and any interactive control.
- Force-open collapsed content — accordions/`details`/tabbed views get `display:block!important` so nothing prints hidden.
- `break-inside:avoid` on cards, calculators, tables, quote blocks.
- Drop shadows and dark backgrounds (`body{background:#fff}`; invert `.lawtext` to light).
- Expose link targets: `a[href]:after{content:" (" attr(href) ")"}` so URLs survive on paper.

A visible **"🖨 Print / PDF"** button calls `window.print()` → the browser's "Save as PDF" yields a clean document. JS must force-open all collapsible sections on `beforeprint` (in case CSS alone misses a JS-driven toggle).

## Theming (selectable, akis palettes)

- **6 embedded palettes** in a `THEMES` JS object (from `akis/src/constants/palettes.js`): `slate, teal, emerald, indigo, rose, amber`. Each sets only the brand 5 — `primary, accent, bg, surface, text`. **Default = `slate`** (neutral, corporate — best for report/legal content).
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

- **KPI tiles + meter:** headline numbers are stat tiles, never chips or a one-bar chart. The coverage meter's fill carries severity (`ok ≥80 / warn ≥50 / bad <50`), its unfilled track is a **lighter step of the same hue** (`color-mix` 15%), and it carries an `aria-label` with the plain-language reading.
- **Comparison bars (`ds-opt:chart`):** only for 2–7 comparable magnitudes (rates, costs, limits); >7 items → table only. Single hue: fill = **theme `--primary`** (all 6 themes ≥3:1 on surface — validator PASS). **Emphasis form:** `hl:true` keeps the primary hue and every other row is auto-dimmed to gray — never primary-vs-accent (validator: indigo ΔE 7.9, rose 13.6 = normal-vision FAIL; 4 accents < 3:1 contrast). The dim gray's contrast WARN is relieved as the validator requires: every bar carries a direct value label and a `<details>` data table is built from the same items.
- **Mark specs:** bar 18px (≤24 cap), 4px rounded data-end + square baseline, 2px surface gaps between rows, 1px hairline baseline, labels/values in text tokens (never the series color).
- **Value placement (deliberate deviation):** values sit in a fixed right-aligned column (an implicit value axis), not at each bar tip — guarantees zero label/mark overlap at every viewport width; the data table carries exact values. Tooltips are omitted: every mark is already direct-labeled + tabled.
- Re-run `dataviz` skill's `scripts/validate_palette.js` before changing any theme, semantic, or chart color.

## Interaction (adaptive)

**Always on:** sticky nav with **condensed report title** (appears when the header scrolls out; hidden ≤900px), **scrollspy** (`aria-current` on the active section's nav button), **reading-progress bar** (2px gradient under the nav), **back-to-top** button (appears after 600px), theme switcher, live search with `<mark>` highlight (auto-opens any `<details>` containing a match), source chips, verbatim-text toggles.
**Collapsibles = native `<details>/<summary>`** (work with zero JS; `id` + hash deep-link opens the target on load/`hashchange`).
**Topic-dependent (only if it genuinely helps, e.g. tax / labor / pricing):** interactive calculator, scenario wizard. Don't add a calculator to a topic that has nothing to compute.
**`--no-interactive`:** minimal JS, document-pure output (everything expanded, no toggles) — safest for archival/printing.

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
