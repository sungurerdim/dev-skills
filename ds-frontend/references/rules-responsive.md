# Rules: Responsive Design & Layout

Rules applied during audit and fix runs. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Layout** | RSP-01 to RSP-04 (4 HIGH) | ~12 |
| **Advanced** | RSP-05 to RSP-08 (2 MEDIUM, 1 MEDIUM, 1 LOW) | ~72 |
| **Core Web Vitals** | RSP-09 to RSP-11 (2 HIGH, 1 MEDIUM) | ~148 |
| **Symmetry & Print** | RSP-12 to RSP-14 (1 HIGH, 2 MEDIUM) | ~193 |
| **Alignment & Visual Geometry** | RSP-15 to RSP-18 (2 HIGH, 1 MEDIUM, 1 LOW) | ~230 |
| **Cascade & Delivery** | RSP-19 to RSP-20 (2 MEDIUM) | ~275 |
| **Layout Stability** | RSP-21 (1 HIGH) | ~266 |

---

## Layout

### RSP-01 [HIGH] Mobile-First Approach
Base styles target smallest viewport; enhancements added via min-width queries.
- **Detect:** Search for media queries. Flag `max-width` as primary responsive strategy:
  - CSS with predominantly `@media (max-width: ...)` queries
  - Component responsive logic starting from desktop and stripping down
  - Desktop-first indicators: large default font sizes, multi-column default layouts
- **Fix:** Restructure: base styles = mobile (single column, comfortable spacing), add complexity via `@media (min-width: ...)`. Benefits: faster mobile paint (no override chain), forces content prioritization.
  - Web: `@media (min-width: 768px) { ... }`
  - Flutter: LayoutBuilder with width-based breakpoints
  - SwiftUI: GeometryReader or horizontalSizeClass
  - Compose: BoxWithConstraints
- **Impact:** 64.35% of web traffic is mobile (July 2025). Mobile-first forces essential-content-first design.
- **Source:** Google Mobile-First Indexing, Responsive Web Design Best Practices

### RSP-02 [HIGH] Viewport Overflow Prevention
No horizontal scroll at any viewport width (320px minimum production target).
- **Detect:** Search for elements that may cause horizontal overflow:
  - Fixed width values >320px on layout containers
  - Images without `max-width: 100%`
  - Tables without responsive wrapping
  - Pre-formatted text without overflow handling
  - Hardcoded pixel widths on flex/grid children
- **Fix:** Add `max-width: 100%` to images and media. Use `overflow-x: auto` on tables. Use `overflow-wrap: break-word` on text containers. Replace fixed widths with responsive units (%, vw, fr). Test at 320px width in browser DevTools.
- **Impact:** Horizontal scroll breaks mobile UX fundamentally. Users expect vertical-only scrolling. WCAG 2.2 SC 1.4.10 requires content reflow at 320px width.
- **Source:** WCAG 2.2 SC 1.4.10 Reflow

### RSP-03 [HIGH] Flexible Layout System
Layout uses CSS Grid/Flexbox (web) or platform layout system with responsive units. No fixed pixel widths on containers.
- **Detect:** Search for layout patterns:
  - `width: Npx` on container elements (not icons/images)
  - Float-based layouts
  - Absolute positioning for page layout
  - Missing responsive layout system (no Grid, no Flexbox, no platform equivalent)
  - Web: fixed-width wrapper divs
  - Flutter: Container with hardcoded width (not in Row)
  - All platforms: layout containers with absolute dimensions
- **Fix:** Use intrinsic layout (Grid/Flex auto-fit, minmax):
  ```css
  /* Responsive grid without media queries */
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  ```
  Replace fixed widths with fluid alternatives: percentage, fr units, min/max constraints.
- **Impact:** Fixed layouts break at unexpected viewport sizes and create maintenance burden when adding breakpoints.
- **Source:** CSS Grid Layout, Flexbox Layout, Every Layout (Heydon Pickering)

### RSP-04 [HIGH] Text Overflow Protection
Text in constrained containers has overflow handling to prevent layout breakage.
- **Detect:** Text elements in constrained parents (flex row, grid cell, fixed-width container) without overflow protection:
  - CSS: missing text-overflow/overflow/white-space combination
  - Long words without word-break/overflow-wrap
  - Text in flex row without min-width: 0 (flex item will not shrink below content)
  - Flutter: Text in Row without Flexible/Expanded and maxLines/overflow
  - SwiftUI: Text in HStack without lineLimit
  - Compose: Text in Row without Modifier.weight() and maxLines
- **Fix:** Add overflow protection:
  - Single-line truncation: `overflow: hidden; text-overflow: ellipsis; white-space: nowrap`
  - Multi-line clamp: `-webkit-line-clamp: N` or `line-clamp: N`
  - Word break: `overflow-wrap: break-word`
  - Flex child: add `min-width: 0` to allow shrinking below content size
- **Impact:** Text overflow → layout shifts (CLS), horizontal scroll, and broken visual hierarchy.
- **Source:** MDN text-overflow, CSS Overflow Module Level 4

---

## Advanced

### RSP-05 [MEDIUM] Container Queries
Components respond to their container's size, not viewport (where browser support allows).
- **Detect:** Component-level responsive logic using viewport media queries when container queries would be more appropriate:
  - Card component switching layout based on `@media (min-width)` instead of `@container`
  - Components behaving differently in sidebar vs main content (should use container width)
  - Media queries inside component-scoped CSS
- **Fix:** Replace component-level media queries with container queries:
  ```css
  .card-container { container-type: inline-size; }
  @container (min-width: 400px) { .card { display: grid; grid-template-columns: 1fr 1fr; } }
  ```
  41% of developers used container queries in 2025 (State of CSS). All major browsers supported since Feb 2023.
- **Impact:** Viewport-based component layout breaks when same component appears in different-width containers (sidebar vs main content vs modal).
- **Source:** MDN Container Queries, CSS Containment Module Level 3

### RSP-06 [MEDIUM] Fluid Typography
Font sizes scale smoothly between breakpoints using clamp() or equivalent.
- **Detect:** Hard font-size changes at breakpoints without interpolation:
  - `@media (...) { h1 { font-size: 24px } }` jumping to `@media (...) { h1 { font-size: 36px } }`
  - No fluid sizing between mobile and desktop text sizes
- **Fix:** Use `clamp()` for fluid scaling:
  ```css
  /* Scales from 16px to 24px between 320px and 1200px viewport */
  font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem);
  ```
  Flutter: use responsive scale utility or MediaQuery-based interpolation.
- **Impact:** Hard font-size jumps at breakpoints → visual discontinuity. Fluid typography → smooth reading experience across all viewport widths.
- **Source:** Modern Fluid Typography Using CSS Clamp, Utopia Fluid Type Calculator

### RSP-07 [MEDIUM] Responsive Images
Images serve appropriate size for viewport and pixel density.
- **Detect:**
  - `<img>` without `srcset` and `sizes` attributes (single fixed-size image)
  - Missing `width` and `height` attributes (causes CLS)
  - Large images served to mobile viewports
  - Missing modern format (WebP/AVIF) with fallback
  - Flutter: Image.network without cacheWidth/cacheHeight
  - Images stretched or distorted by their frame (missing `object-fit`), or frames whose aspect ratio fights the source media
- **Fix:** Add responsive image markup:
  ```html
  <img srcset="img-400.webp 400w, img-800.webp 800w, img-1200.webp 1200w"
       sizes="(max-width: 600px) 100vw, 50vw"
       src="img-800.webp" alt="..." width="800" height="600" loading="lazy">
  ```
  Always include width/height to prevent CLS. Use `loading="lazy"` for below-fold images. Present images undistorted in deliberately sized frames: `object-fit: cover|contain` per context, frame dimensions chosen for the content, and wide-viewport layouts that use available space without stretching the source. (XR-191)
- **Impact:** Oversized images are largest contributor to page weight. Serving 1200px images to 375px viewports wastes bandwidth and slows load.
- **Source:** MDN Responsive Images, Web.dev Image Optimization

### RSP-08 [LOW] Viewport Test Matrix
Test UI at representative viewport widths to verify no breakage.
- **Detect:** Verify layouts render correctly at these widths:

  | Width | Profile | Class |
  |-------|---------|-------|
  | 320px | Small phone (iPhone SE) | Compact |
  | 375px | Standard phone | Compact |
  | 768px | Tablet | Medium |
  | 1024px | Small desktop / iPad Pro | Expanded |
  | 1440px | Desktop | Expanded |

  Also test: landscape orientation — both orientations must stay usable, never lock one (WCAG 2.2 SC 1.3.4 Orientation, AA) — font scale 1.3x, dark mode, RTL layout (if i18n supported).
- **Fix:** Fix layout issues at each viewport. Priority: 320px (most constrained) first, then progressively wider.
- **Impact:** Untested viewports are where layout bugs hide. Test matrix ensures coverage of most common real-world device classes.
- **Source:** Material 3 Window Size Classes, StatCounter GlobalStats viewport distribution, WCAG 2.2 SC 1.3.4 Orientation

---

## Core Web Vitals

### RSP-09 [HIGH] Largest Contentful Paint (LCP)
Target: < 2.5s. Largest visible element render time. Directly affects SEO ranking.
- **Detect:** Hero image without `srcset`/`fetchpriority="high"`. No `<link rel="preload">` for LCP element. Render-blocking CSS/JS in `<head>` without deferral. LCP element loaded from third-party origin without preconnect.
- **Fix:** Preload LCP resource (single most effective fix). Set `fetchpriority="high"` on LCP image. Inline critical CSS, defer rest via `<link rel="preload" as="style" onload="this.rel='stylesheet'">`. Add `<link rel="preconnect">` for third-party LCP origins. Optimize hero image format (WebP/AVIF).
  ```html
  <link rel="preload" as="image" href="/hero.webp" fetchpriority="high">
  <img src="/hero.webp" alt="Hero" width="1200" height="600" fetchpriority="high">
  ```
- **Impact:** Only 48% of mobile pages pass all three CWV (2025 Web Almanac). LCP is most impactful single metric for perceived load speed.
- **Source:** web.dev Core Web Vitals, Chrome User Experience Report, DebugBear 2025 Web Performance Review

### RSP-10 [HIGH] Cumulative Layout Shift (CLS)
Target: < 0.1. Visual stability during load and session lifetime.
- **Detect:** Images/videos/iframes without explicit `width` and `height` attributes. Dynamically injected content above fold without reserved space. Font swap causing reflow (FOUT). Ad slots without `min-height`. CSS animations using layout-triggering properties (width, height, top, left).
- **Fix:** Set explicit dimensions on all media elements. Use `min-height` on dynamic content slots (ads, embeds). Use `font-display: optional` to eliminate font-swap layout shift. Reserve placeholder space for dynamically loaded content. Animate with `transform` only (compositor-only, no layout shift).
  ```css
  .ad-slot { min-height: 250px; }
  img, video { width: 100%; height: auto; aspect-ratio: attr(width) / attr(height); }
  @font-face { font-display: optional; }
  ```
- **Impact:** CLS measures visual stability across entire session, not just initial load. Layout shifts erode user trust and cause mis-clicks.
- **Source:** web.dev Core Web Vitals, Chrome User Experience Report

### RSP-11 [MEDIUM] Interaction to Next Paint (INP)
Target: < 200ms. Worst interaction latency at 75th percentile. Replaced FID in March 2024.
- **Detect:** Long tasks (>50ms) on main thread during user interaction. Heavy re-renders on click/input events. No task yielding in event handlers processing large datasets. `content-visibility: auto` not used for off-screen content. Layout thrashing (interleaved DOM reads and writes).
- **Fix:** Break long tasks with `scheduler.yield()` (or `setTimeout(0)` fallback). Debounce input handlers. Use `content-visibility: auto` for off-screen content. Batch DOM reads then writes to avoid layout thrashing. Offload heavy computation to web workers.
  ```js
  async function processItems(items) {
    for (const item of items) {
      processItem(item);
      await scheduler.yield(); // yield to main thread
    }
  }
  ```
- **Impact:** 43% of sites fail 200ms INP threshold -- most commonly failed CWV metric in 2026.
- **Source:** web.dev INP as Core Web Vital, Chrome User Experience Report, DebugBear 2025 Web Performance Review

---

## Symmetry & Print

### RSP-12 [HIGH] Multi-Column Layout Symmetry (shared chrome, not per-column chrome)
When a layout places sibling columns/panes side by side (e.g. a filter rail, a main content area, a summary rail), any header/toolbar/control-row that logically belongs to the *page*, not to one specific column, is rendered once above/outside the column grid — never duplicated as the first child inside just one of the columns.
- **Detect:** A grid/flex row of 2+ sibling "column" containers where only *one* column's markup includes an extra header/toolbar element before its main content (mode-switch chips, a date-nav strip, an actions row) while sibling columns start directly with their real content. Even when the outer grid/flex container aligns all columns' top edges (`align-items: start` with equal padding), the columns' *real, meaningful* content (the first filter item, the actual data grid, the first summary stat) will start at visibly different vertical offsets, because one column spent extra height on a header row the others don't have. This reads as "the columns aren't aligned" even when the outer container-level alignment is technically correct.
- **Fix:** Hoist any such control row out of the single column it was nested in and render it as one shared, full-width element positioned above (or as a header for) the entire multi-column grid. After the move, verify with actual measured layout — not visual inspection alone — that every column's first *real content* element starts at the same coordinate: measure each column's first meaningful child's bounding box and assert the top offsets match within a few pixels.
- **Impact:** A common source of "the page looks subtly unbalanced" feedback that's hard to pin down from CSS inspection alone, because the outer grid *is* aligned — the drift is inside the columns, at the first-real-content level, which most spacing/alignment audits don't measure (they check declared CSS, not rendered geometry).
- **Source:** Live audit + fix pattern (rendered-geometry alignment check, not just declared CSS)

### RSP-13 [MEDIUM] Print Stylesheet
Pages containing printable content (invoices, receipts, reports, appointment/order summaries, tickets) define `@media print` rules that hide interactive chrome, force readable contrast, and control page breaks — a page is not printed as if it were a live screen.
- **Detect:** Pages/routes rendering content with clear print intent — search for the absence of any `@media print` block in the stylesheet chain, or a print block that only hides nav with no color/page-break handling. Flag: dark/colored backgrounds with light text and no print override (prints illegible or wastes ink); fixed/sticky nav or header with no print override (repeats or obscures content across pages); no `page-break-inside: avoid` on card/table-row/line-item groups (content splits mid-row across a page boundary).
- **Fix:** Add an `@media print { }` block: hide non-content chrome (nav, sidebar, buttons, modals) via `display: none`; force light background + dark text regardless of the active theme; add `page-break-inside: avoid` on atomic content blocks (table rows, cards, line items); set an explicit `@page { margin: ... }` if the layout needs non-default margins.
- **Impact:** A page with no print stylesheet prints exactly as it renders on screen — dark-mode backgrounds waste ink or render illegible, sticky nav repeats on every page eating margin, and unbounded content splits an invoice line or table row across a page break. Invisible in normal QA because nobody previews print output unless explicitly testing it.
- **Source:** W3C CSS Fragmentation Module Level 3 (page-break control), CSS Paged Media Module Level 3 (`@page`)

### RSP-14 [MEDIUM] Direction-Agnostic Layout (CSS Logical Properties)
Layout direction comes from logical properties (`margin-inline-start`, `padding-inline`, `inset-inline`, `text-align: start`) rather than physical ones (`margin-left`, `left`, `text-align: left`), so the layout mirrors correctly under RTL.
- **Detect:** Physical direction properties (`margin-left/right`, `padding-left/right`, `left`/`right` offsets, `text-align: left/right`, `border-left/right`) in a codebase that declares 2+ locales or any RTL locale (ar, he, fa, ur); missing `dir` attribute handling on `<html>` per locale. Codebase with no i18n intent → downgrade to LOW advisory, don't churn working styles.
- **Fix:** Replace with logical equivalents (baseline in all modern browsers): `margin-inline-start/end`, `padding-inline`, `inset-inline-start`, `text-align: start/end`, `border-inline-start`; set `dir` on `<html>` from the active locale; verify one RTL locale via the RSP-08 matrix.
- **Impact:** Physical properties mirror nothing under RTL — the layout renders left-anchored for right-to-left readers, and retrofitting is a full-codebase sweep with visual-regression risk. Writing logical properties from day one costs nothing.
- **Source:** MDN CSS Logical Properties and Values; W3C i18n layout best practices

## Alignment & Visual Geometry

### RSP-15 [HIGH] In-Item Alignment (icon/text/control rows)
Every horizontal composite (icon + label, avatar + text, input + button, badge in a row) is vertically aligned by an explicit rule — centered or baseline-aligned — never by accidental line-box math.
- **Detect:** Flex/grid rows containing an icon/image next to text without `align-items: center` (or `baseline` when aligning text of one size to text of another); mixed inline elements with differing `line-height`/`font-size` producing visibly offset baselines (icon riding high/low next to its label); buttons or chips whose label sits off-center because vertical padding is asymmetric or line-height exceeds the control height; fixed-height controls in one row with differing heights (input 40px next to button 36px).
- **Fix:** State the alignment intent in code: `align-items: center` for icon+text and control rows; `align-items: baseline` for text-to-text of different sizes; equalize control heights in a shared row via a shared size token; give icons a fixed box (`flex: none; width/height`) so they can't stretch. When browser automation is available, verify by measured bounding boxes: centers (or baselines) of siblings in one row must match within 1–2px.
- **Impact:** Off-by-2px icon/label misalignment is the single most common "feels unpolished" signal — invisible in code review, obvious to every user.
- **Source:** Every Layout (Heydon Pickering) cluster/center patterns; flexbox alignment spec (MDN)

### RSP-16 [HIGH] Row/Column Content Alignment (tables, lists, forms)
Columnar content aligns by data type, and headers align with their column's data.
- **Detect:** Data tables/lists where numeric columns (amounts, counts, dates) are left- or center-aligned, or rendered with proportional figures so digits don't line up vertically; column headers whose alignment differs from their column's data alignment; text columns center-aligned (ragged both sides); form layouts mixing label positions (some above, some inline) or labels not aligned to a common edge within one form; multi-line list items where wrapped text falls back under the leading icon/marker instead of hanging-indented to the text start.
- **Fix:** Numbers: end-aligned + `font-variant-numeric: tabular-nums` (monospaced digits) so magnitudes compare vertically; text: start-aligned; headers inherit their column's alignment; one label-placement convention per form, labels on a shared edge; wrapped list-item text hang-indents to the text column (grid `auto 1fr` or padding + negative text-indent).
- **Impact:** Misaligned numeric columns make scanning/comparison measurably slower and error-prone; mixed form alignment breaks the vertical scan line users navigate by.
- **Source:** Practical Typography (butterick) tabular figures; NN/g form-label alignment research

### RSP-17 [MEDIUM] Shared-Edge & Gutter Consistency (page-level grid)
Sibling blocks on the same page align to shared edges and use uniform gutters from the spacing scale.
- **Detect:** Cards/panels in one visual row with unequal heights where the design implies equality (`align-items` left at default `stretch` defeated by fixed heights, or misc margins pushing one card's edge off); different `gap`/margin values between siblings of the same group (16px here, 20px there); content blocks whose left edges almost-but-not-quite align (nested containers adding stray padding so text starts at 24px in one section and 28px in the next); section max-widths that differ without intent, breaking the page's shared content column.
- **Fix:** One grid definition per page region — siblings inherit edges from the grid rather than carrying their own offsets; gutters come from a single spacing token per group (TOK-02/TOK-09); container padding defined once at the region level, not re-added per child. Verify rendered geometry where automation is available: left edges and gutters of a group must match exactly (same rendered-geometry protocol as RSP-12).
- **Impact:** Every stray edge breaks the invisible grid that makes a page read as designed rather than assembled; users can't name the problem but reliably rate such pages lower.
- **Source:** Gestalt alignment/continuity principles; 8pt-grid practice; live-audit pattern (extends RSP-12 from column chrome to all sibling groups)

### RSP-18 [LOW] Vertical Rhythm & Optical Alignment (advisory)
Type sits on a consistent rhythm, and visually-heavy shapes are aligned optically, not just geometrically.
- **Detect (advisory):** Heading/body `line-height` and inter-block spacing values unrelated to the base spacing unit, producing irregular vertical intervals down the page; icons/glyphs that are geometrically centered but look off-center because their visual mass is asymmetric (play triangles, chevrons, back arrows); large punctuation or quote marks pushing the first text line out of the shared left edge.
- **Fix:** Derive line-heights and block margins from the same base unit as the spacing scale (multiples, not arbitrary values); nudge asymmetric glyphs by 1–2px toward visual balance (optical centering) and encode the nudge in the icon component, not per-call-site; where supported, hang leading punctuation (`hanging-punctuation` / negative indent) so text edges stay flush. Advisory: propose, never churn a working layout for rhythm alone.
- **Impact:** Rhythm and optical corrections are the difference between "clean" and "template-y" — low individual cost, compounding aesthetic effect.
- **Source:** Baseline-rhythm typography practice; optical-adjustment guidance (icon design conventions)

## Cascade & Delivery

### RSP-19 [MEDIUM] CSS Cascade Source-Order for Media Overrides
A same-specificity `@media` rule overriding a base selector must be declared AFTER that base rule in source order — media queries don't add specificity, so a later same-specificity base rule wins regardless of viewport width.
- **Detect:** For each `@media` block, check whether an identical-specificity non-media selector targeting the same property is declared later in the same file/bundle (including later imports/bundling order) — if so, the base rule always wins and the media override never applies at any viewport.
- **Fix:** Move the base declaration before the media override in source order, or intentionally increase the override's specificity so source order no longer matters.
- **Impact:** A silently dead responsive override is invisible in code review (both rules "look correct" in isolation) and only surfaces as "this breakpoint doesn't work" during manual device testing.
- **Source:** MDN CSS Cascade — specificity and source order

### RSP-20 [MEDIUM] Lazy Route-Based Code-Splitting for Zero-Build/Vanilla Stacks
A build-free/vanilla-module frontend can still achieve route-based code-splitting: replace an eager static-import module registry with a lazy loader map exposed through a Proxy that preserves existing synchronous-access call sites.
- **Detect:** A vanilla/no-bundler frontend with a static import registry (`import ViewA from './a.js'` for every route/view) all loaded eagerly at boot; a lazy-loaded view that synchronously renders/embeds another view with no declared dependency, so the embed silently renders blank on first navigation to that route.
- **Fix:** Replace the eager registry with a `name → () => import(path)` loader map behind a Proxy (returns `undefined` before load, preserving synchronous property-access call sites once loaded); when a view synchronously embeds another view in its render, declare that dependency explicitly (an `embeds` list) so the loader pre-loads it before rendering.
- **Impact:** Route-based code-splitting is achievable without adopting a bundler, cutting initial payload; the explicit `embeds` declaration prevents a silent blank-render regression when a transitive view dependency hasn't loaded yet.
- **Source:** MDN dynamic `import()`; JavaScript Proxy (MDN)

## Layout Stability

### RSP-21 [HIGH] Scrollbars and Hover Never Shift Layout
Scrollbar appearance/disappearance and hover effects never change layout metrics.
- **Detect:** Content jumps sideways when a scrollbar appears; hover changes width/height/wrap (text un-wrapping, borders growing into layout); scroll/wrap behavior styled ad hoc per surface.
- **Fix:** Reserve the scrollbar gutter permanently (`scrollbar-gutter: stable` or equivalent) or use overlay scrollbars that never affect layout width. Restrict hover to non-layout-affecting changes (color, shadow, cursor, transform); forbid hover effects that alter width, height, or line count. Define this scroll/wrap policy once in the central style layer and derive all scroll areas from it.
- **Impact:** Layout jitter from scrollbars and hover reads as instability and causes misclicks precisely at the moment of interaction.
- **Source:** XR-132 — cross-project experience registry (2026); complements RSP-10 (CLS).
