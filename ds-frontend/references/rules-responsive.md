# Rules: Responsive Design & Layout

Rules for audit/fix modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Layout** | RSP-01 to RSP-04 (4 HIGH) | ~12 |
| **Advanced** | RSP-05 to RSP-08 (2 MEDIUM, 1 MEDIUM, 1 LOW) | ~72 |
| **Core Web Vitals** | RSP-09 to RSP-11 (2 HIGH, 1 MEDIUM) | ~148 |

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
- **Fix:** Add responsive image markup:
  ```html
  <img srcset="img-400.webp 400w, img-800.webp 800w, img-1200.webp 1200w"
       sizes="(max-width: 600px) 100vw, 50vw"
       src="img-800.webp" alt="..." width="800" height="600" loading="lazy">
  ```
  Always include width/height to prevent CLS. Use `loading="lazy"` for below-fold images.
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

  Also test: landscape orientation, font scale 1.3x, dark mode, RTL layout (if i18n supported).
- **Fix:** Fix layout issues at each viewport. Priority: 320px (most constrained) first, then progressively wider.
- **Impact:** Untested viewports are where layout bugs hide. Test matrix ensures coverage of most common real-world device classes.
- **Source:** Material 3 Window Size Classes, StatCounter GlobalStats viewport distribution

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
