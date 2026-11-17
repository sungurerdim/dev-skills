# Web — browser-only surface checks

Loaded for web UIs (`ui∋web`). Behaviour every graphical UI shares is in [ux.md](ux.md); accessibility in [a11y.md](a11y.md); web security headers, CSP, XSS and cookies in [security.md](security.md) and [auth.md](auth.md); bundle size, INP and layout thrashing in [perf.md](perf.md) (PRF-03, PRF-09, PRF-16).

### WEB-09 [HIGH] Core Web Vitals unmeasured or over threshold
- **Detect:** no field measurement (the `web-vitals` library or a RUM tool) on a public site; LCP element (hero image, heading) lazy-loaded, without `fetchpriority="high"` or preload, or behind render-blocking CSS/JS; images, video, iframes and ad or embed slots without reserved `width`/`height` or `aspect-ratio`; content injected above existing content after load; web fonts swapping without metric overrides. INP causes and fixes are PRF-16.
- **Mech:** T `git grep -nIE '<(img|iframe|video)[[:space:]]' -- '*.html' '*.jsx' '*.tsx' '*.vue' '*.svelte' '*.astro' | grep -v -e 'height=' -e 'aspect-ratio'`
- **Fixture:** hit `a.html: <img src="hero.jpg" alt="Hero">` · miss `b.html: <img src="hero.jpg" alt="Hero" width="800" height="400">`
- **Fix:** preload or `fetchpriority="high"` the LCP resource and never lazy-load it; reserve space for every media and embed slot; insert late content below the viewport or in reserved space; `size-adjust`/`font-display` tuned fonts; report field p75 of LCP, INP and CLS.
- **Impact:** slow first paint and jumping layouts lose users before the first interaction and misplace taps; search ranking uses the same field data.
- **Source:** Make it work, right, fast; web.dev, Core Web Vitals thresholds LCP ≤ 2.5 s, INP ≤ 200 ms, CLS ≤ 0.1 at p75 (https://web.dev/articles/vitals).

### WEB-05 [HIGH] Layout breaks on narrow viewports
- **Detect:** an HTML entry point with no `<meta name="viewport" content="width=device-width…">`; fixed pixel widths on containers wider than a phone without `max-width`; tables, code blocks or wide media with no scroll container; horizontal scroll at 320 CSS px width.
- **Mech:** T `git grep -nIE '(^|[^-])width:[[:space:]]*[0-9]{4,}px' -- '*.html' '*.css' '*.scss' '*.less'` · `git grep -LI 'name="viewport"' -- '*.html'`
- **Fixture:** hit `a.css: .wrap { width: 1200px; }` · hit `a.html: <title>A</title>` · miss `b.html: <meta name="viewport" content="width=device-width">` · miss `b.css: .wrap { max-width: 1200px; }`
- **Fix:** the viewport meta tag; fluid containers (`max-width`, `%`, `min()`), grid and flex wrapping; a scroll wrapper for content that cannot reflow; check at 320, 768 and 1280 px.
- **Impact:** phone users get sideways scrolling or cut-off controls on every page.
- **Source:** WCAG 2.2 SC 1.4.10 Reflow; MDN, Viewport meta tag.

### WEB-10 [MEDIUM] Images heavier than the viewport needs
- **Detect:** committed raster images over ~200 KB; `<img>` without `srcset`/`sizes` where several display widths exist; below-the-fold images without `loading="lazy"`; JPEG/PNG photos where AVIF or WebP is supported by the browser target (WEB-15).
- **Mech:** T `git ls-tree -r -l HEAD | awk '$4 > 204800 && $5 ~ /\.(png|jpe?g|gif|bmp|tiff?)$/ {print $5, $4}'`
- **Fixture:** history
- **Fix:** compress and convert at build time; `srcset`/`sizes` or the framework's image component; `loading="lazy"` below the fold only.
- **Impact:** every visit downloads bytes the screen cannot show, slowing LCP on mobile networks.
- **Source:** web.dev, Optimize images (https://web.dev/learn/images).

### WEB-15 [MEDIUM] No declared browser support target
- **Detect:** no Browserslist query (`browserslist` in `package.json` or `.browserslistrc`) and no Baseline target stated; platform features used (CSS nesting, `:has()`, `popover`, View Transitions) with no fallback for browsers the product claims to support; transpile and polyfill settings that do not follow the target.
- **Mech:** T `git ls-files | grep -qE '(^|/)\.browserslistrc$' || git grep -qIE '"browserslist"|Baseline' -- package.json README.md || echo 'no Browserslist query or Baseline target'`
- **Fixture:** says `no Browserslist query or Baseline target` · miss `src/app.js: const browsers = []` · quiet `.browserslistrc: defaults`
- **Fix:** declare one target (a Browserslist query or a Baseline year) and feed it to the transpiler, CSS tooling and linter; test the oldest browser in it.
- **Impact:** features silently fail for part of the audience, or polyfills ship to browsers that never needed them.
- **Source:** web.dev, Baseline (https://web.dev/baseline); Browserslist (https://browsersl.ist/).

### WEB-07 [MEDIUM] Framework default error pages
- **Detect:** no custom 404 and 5xx page or route; no top-level error boundary in a client-rendered app, so one render error blanks the page; error pages without a way back (home, search, retry). Stack traces in responses are SAR-06.
- **Mech:** T `git ls-files | grep -qiE '(^|/)(404|500|not-found|error)\.(html|tsx?|jsx?|vue|svelte|astro)$' || echo 'no custom 404 or error page tracked'`
- **Fixture:** says `no custom 404 or error page tracked` · miss `src/home.html: <h1>Home</h1>` · quiet `public/404.html: <h1>Not found</h1>`
- **Fix:** a branded 404 with navigation and search, a 5xx with retry and a support path, and an app-level error boundary that logs and renders the same.
- **Impact:** a dead end with no route back turns one broken link or exception into an abandoned session.
- **Source:** Nielsen heuristic 9, help users recover from errors; MDN, HTTP 404.

### WEB-08 [MEDIUM] Public pages not indexable or not shareable
applies_when: audience=public
- **Detect:** pages without a unique `<title>` and `<meta name="description">`; no `rel="canonical"` on duplicate URLs; no Open Graph tags; no `robots.txt` or sitemap; content pages rendered only on the client.
- **Mech:** T `git grep -LIE '<title' -- '*.html'` · `git ls-files | grep -E '(^|/)(robots\.txt|sitemap[^/]*\.xml)$'`
- **Fixture:** hit `a.html: <h1>No title</h1>` · hit `public/robots.txt: User-agent: *` · miss `b.html: <title>B</title>`
- **Fix:** per-page title, description, canonical and Open Graph tags; generate robots.txt and a sitemap; server-render or pre-render content pages.
- **Impact:** pages rank poorly and shared links show blank previews.
- **Source:** Google Search Central, SEO starter guide; Open Graph protocol (https://ogp.me/).

### CMP-09 [HIGH] Overlay clipped or stacked by accident
- **Detect:** dropdowns, menus, popovers and typeahead lists positioned `absolute` inside an `overflow: hidden|auto` ancestor instead of a portal, top layer (`popover`, `<dialog>`) or anchor positioning; literal `z-index` values (`999`, `9999`) instead of a layer scale; overlays without a `max-height` and inner scroll.
- **Mech:** T `git grep -nIE 'z-index:[[:space:]]*[0-9]{3,}' -- '*.html' '*.css' '*.scss' '*.less' '*.vue' '*.svelte'`
- **Fixture:** hit `a.css: .modal { z-index: 9999; }` · miss `b.css: .modal { z-index: 10; }`
- **Fix:** render overlays in the top layer or a portal; one named z-index scale (base, sticky, overlay, modal, toast); a max-height tied to the viewport with scroll.
- **Impact:** menus cut off inside cards or hidden behind sticky headers make actions unreachable.
- **Source:** MDN, Stacking context; HTML popover attribute; CSS Anchor Positioning.

### RSP-21 [MEDIUM] Scrollbars or hover shift layout
- **Detect:** content jumps sideways when a scrollbar appears (scroll containers without `scrollbar-gutter: stable`); hover or focus styles that change width, border width or font weight and reflow neighbours.
- **Mech:** T `git grep -nIE 'overflow(-y)?:[[:space:]]*auto' -- '*.html' '*.css' '*.scss' '*.less'`
- **Fixture:** hit `a.css: .list { overflow-y: auto; }` · miss `b.css: .list { overflow: hidden; }`
- **Fix:** `scrollbar-gutter: stable` on scroll containers whose content length varies; hover states through colour, outline, shadow or transform only.
- **Impact:** moving targets cause mis-clicks and read as a broken page.
- **Source:** MDN, scrollbar-gutter; complements WEB-09 (CLS).

### RSP-19 [MEDIUM] Media query overridden by a later rule
- **Detect:** an `@media` override followed later in the same cascade (file or bundle order) by a rule of equal specificity setting the same property, so the override never applies.
- **Mech:** M (compare source order of each `@media` block with later same-selector rules; the browser devtools show the struck-through declaration)
- **Fix:** put media overrides after the base rule, or write mobile-first with `min-width` queries after the base styles.
- **Impact:** the responsive layout silently never activates at the breakpoint it was written for.
- **Source:** MDN, Cascade, specificity and order of appearance.

### RSP-13 [LOW] Printable page without print styles
- **Detect:** pages users print or save as PDF (invoices, receipts, reports, tickets) with no `@media print` block: navigation, dark backgrounds and interactive chrome print, content splits across page breaks.
- **Mech:** T `git grep -qI '@media print' -- '*.css' '*.scss' '*.less' '*.html' '*.vue' '*.svelte' || git grep -lIiE 'invoice|receipt|ticket' -- '*.html' '*.jsx' '*.tsx' '*.vue' '*.svelte' '*.astro'`
- **Fixture:** hit `invoice.html: <h1>Invoice</h1>` · miss `about.html: <h1>About</h1>` · quiet `print.css: @media print { nav { display: none; } }`
- **Fix:** an `@media print` block that hides chrome, uses dark text on white, and sets `break-inside: avoid` on rows and cards.
- **Impact:** printed documents waste ink and lose content at page breaks.
- **Source:** W3C CSS Fragmentation Module Level 3; CSS Paged Media Module Level 3.
