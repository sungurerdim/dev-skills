# Rules: Web-Specific

Conditional rules loaded only for web frontend projects. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Web Security** | WEB-01–04, WEB-14 (1 BLOCKER, 3 CRITICAL, 1 HIGH) | ~12 |
| **Web Quality** | WEB-05–08 (4 HIGH) | ~70 |
| **Web Performance** | WEB-09–13 (2 CRITICAL, 3 HIGH) | ~120 |

---

## Web Security

### WEB-01 [BLOCKER] Content Security Policy
CSP header preventing inline scripts and unauthorized sources.
- **Detect:**
  - No `Content-Security-Policy` header in responses
  - CSP with `unsafe-inline` or `unsafe-eval` for scripts
  - Host-allowlist CSP (long domain lists, no nonces) — bypassable via JSONP endpoints/open redirects on allowed hosts
  - No CSP meta tag or header configuration
  - Search: absence of `content-security-policy` in middleware/headers config
  - **Allowlist-completeness (distinct from presence/strictness):** grep every `fetch()`/XHR/SDK-call target host in source (auth/token endpoints, identity/userinfo endpoints, every third-party API) and cross-reference against the `connect-src` directive — a fetched host absent from `connect-src` fails silently in the browser (request just blocked) with no error surfaced until a user reports a broken feature
- **Fix:** Strict CSP (2026 default): `script-src 'nonce-{RANDOM}' 'strict-dynamic'; object-src 'none'; base-uri 'none'` — nonce-based with `'strict-dynamic'` (CSP Level 3, widely supported in modern browsers) instead of host allowlists. Deploy as `Content-Security-Policy-Report-Only` first; promote to enforcement only after violation reports go quiet. Where supported (Chromium), add `require-trusted-types-for 'script'` (Trusted Types) to block DOM-XSS sinks. Report violations with `report-to`/`report-uri`. For `connect-src` completeness: generate the allowlist from the same host-constants file the fetch calls use, or add a lint/audit step that fails when a new external host is called but not yet allowlisted
- **Impact:** CSP prevents XSS exploitation even when injection vulnerabilities exist; allowlist CSPs are routinely bypassed, strict nonce CSPs are not. A CSP that's strict but incomplete on `connect-src` silently breaks real features (a real incident: an OIDC identity-verification endpoint omitted from `connect-src` silently broke post-login identity hydration, only caught via a live login-loop bug report)
- **Source:** OWASP CSP Cheat Sheet (strict CSP), MDN CSP

### WEB-02 [CRITICAL] CORS Configuration
Restrictive CORS. No wildcard origins in production.
- **Detect:**
  - `Access-Control-Allow-Origin: *` in production config
  - CORS allowing any origin with credentials
  - Search: `origin: '*'`, `origin: true`, `cors({ origin: '*' })` in production code
- **Fix:** Whitelist specific origins. Never use `*` with credentials. Validate origin against whitelist. Set appropriate `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`
- **Impact:** A wildcard CORS origin (especially with credentials) lets any website read authenticated API responses on behalf of a logged-in user — cross-origin data theft.
- **Source:** MDN CORS, OWASP

### WEB-03 [CRITICAL] XSS Prevention
No raw HTML rendering of user input. Output encoding enforced.
- **Detect:**
  - React: `dangerouslySetInnerHTML` with user input
  - Vue: `v-html` with user input
  - Angular: bypassing DomSanitizer
  - Server: template rendering without auto-escaping
  - Search: `innerHTML`, `dangerouslySetInnerHTML`, `v-html`, `|safe`, `mark_safe` near user input variables
- **Fix:** Use framework auto-escaping (React JSX, Vue templates, Angular templates). Sanitize with DOMPurify when raw HTML is required. Never use `eval()` or `innerHTML` with user data
- **Impact:** Unescaped user input rendered as HTML lets an attacker run arbitrary script in every victim's browser session — session theft, account takeover, defacement.
- **Source:** OWASP XSS Prevention Cheat Sheet

### WEB-04 [CRITICAL] CSRF Protection
State-changing operations protected against cross-site request forgery.
- **Detect:**
  - No CSRF token in forms/state-changing requests
  - `SameSite` cookie attribute missing
  - No CSRF middleware configured
  - Search: POST/PUT/DELETE handlers without CSRF validation
- **Fix:** Use `SameSite=Strict` or `SameSite=Lax` cookies. CSRF tokens for form submissions. Verify `Origin`/`Referer` headers. Use framework CSRF middleware (Node/Express: `csrf-csrf` or `csrf-sync` — `csurf` is deprecated; Django CSRF, Spring CSRF)
- **Impact:** Without CSRF protection, a malicious site can trigger state-changing requests (transfers, password changes, deletions) using the victim's own authenticated session.
- **Source:** OWASP CSRF Prevention Cheat Sheet

### WEB-14 [HIGH] Third-Party Content Integrity
External scripts/styles carry SRI hashes; embedded third-party content is sandboxed.
- **Detect:**
  - `<script src=` or `<link rel="stylesheet"` from external origins without `integrity=` attribute
  - `<iframe>` embedding third-party content without `sandbox` attribute
  - Search: `integrity="sha256-` (weaker than the SHA-384 default; only SHA-256/384/512 are supported by the spec)
- **Fix:** Add `integrity="sha384-…"` + `crossorigin="anonymous"` to third-party `<script>`/`<link>` tags (SHA-384 default). Sandbox third-party iframes with the minimum capability set (e.g. `<iframe sandbox="allow-scripts">`). Known coverage gap: dynamically-served assets (e.g. Google Fonts) do not support SRI — self-host those assets instead
- **Impact:** A compromised CDN or third-party host can inject arbitrary script into every page; SRI turns that into a failed load instead of an XSS
- **Source:** MDN Subresource Integrity, OWASP Third-Party JavaScript Cheat Sheet

---

## Web Quality

### WEB-05 [HIGH] Responsive Design
Layout adapts to all screen sizes. No horizontal scroll on mobile.
- **Detect:**
  - Search: `width:` with pixel values >320px without `max-width` or media query context (e.g., `width: 960px`, `width: 1200px` on containers)
  - Search: missing `<meta name="viewport">` tag in HTML entry points (`index.html`, layout templates)
  - Search: `@media` query absence in CSS/SCSS files (zero responsive breakpoints)
  - Search: fixed-width containers without responsive alternatives (`width: [4-9]\d\dpx`, `width: \d{4,}px` without accompanying `max-width` or `%`/`vw` fallback)
  - Images without responsive sizing (`<img` without `srcset` or CSS `max-width: 100%`)
- **Fix:** Use relative units (%, rem, vw). Mobile-first media queries. Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`. Responsive images with `srcset`/`sizes`. CSS Grid/Flexbox for layouts
- **Impact:** A layout that doesn't adapt forces mobile users into horizontal scrolling and unreadable text — a majority-share traffic segment gets a broken experience.
- **Source:** Responsive Web Design, MDN

### WEB-06 [HIGH] Web Accessibility (WCAG 2.2 AA)
Core flows meet WCAG 2.2 AA. Keyboard navigable. Screen reader compatible.
- **Detect:**
  - Images without `alt` attribute
  - Form inputs without associated labels
  - Interactive elements not keyboard accessible
  - Missing ARIA roles/landmarks on dynamic content
  - Color contrast below 4.5:1 for normal text
  - Search: `<img` without `alt=`, `<input` without associated `<label`
- **Fix:** Add `alt` text to all images (empty `alt=""` for decorative). Associate labels with inputs. Ensure keyboard navigation (tab order, focus management). Use semantic HTML. Test with screen reader (NVDA, VoiceOver). Ensure 4.5:1 contrast ratio
- **Impact:** ~15% of users have some form of disability. EAA enforcement live since 28 Jun 2025 — an active obligation for products/services marketed in the EU, not a future deadline
- **Source:** WCAG 2.2, EAA 2019/882

### WEB-07 [HIGH] Error Pages
Custom error pages (404, 500) with helpful content and consistent branding.
- **Detect:**
  - Default framework error pages in production
  - Stack traces visible in error responses
  - No custom 404 page
  - No global error boundary (React) or error page (Next.js)
- **Fix:** Custom 404 with navigation/search. Custom 500 with "try again" and support contact. Error boundaries for React. Never expose stack traces. Log errors server-side
- **Impact:** A default framework error page or an exposed stack trace leaks internal structure to attackers and shows every real user a dead end with no way back.
- **Source:** UX best practices

### WEB-08 [HIGH] SEO Fundamentals
Proper meta tags, semantic HTML, structured data for public-facing pages.
- **Detect:**
  - Missing `<title>` or `<meta name="description">` on pages
  - No Open Graph / Twitter Card meta tags
  - Non-semantic HTML (div soup)
  - No sitemap.xml or robots.txt
  - Client-side only rendering without SSR/SSG for content pages
- **Fix:** Unique `<title>` and `<meta description>` per page. Open Graph tags for social sharing. Semantic HTML (header, main, nav, article, section). Generate sitemap.xml. SSR/SSG for content pages
- **Cross-ref:** Launch-surface SEO execution (sitemap/robots generation, JSON-LD validation, CWV tie-breaker, llms.txt posture) is canonical in ds-launch `--seo`; this rule is the audit-time web-quality check — when both run, generation work routes to ds-launch
- **Impact:** Missing title/description/OG tags and non-semantic markup suppress search ranking and produce blank, unclickable link previews when shared.
- **Source:** Google Search Central, MDN Semantic HTML

---

## Web Performance

### WEB-09 [CRITICAL] Core Web Vitals
LCP < 2.5s, INP < 200ms, CLS < 0.1.
- **Detect:**
  - No performance monitoring (no web-vitals library, no RUM)
  - Large images above fold without optimization
  - Layout shifts from dynamically loaded content
  - Long tasks blocking main thread
- **Fix:** Optimize LCP: preload critical resources, optimize images (WebP/AVIF, srcset), use CDN. Optimize INP: break long tasks, use `requestIdleCallback`, debounce handlers. Optimize CLS: set explicit dimensions on images/embeds, avoid injecting content above viewport
- **Impact:** Core Web Vitals are Google ranking signal. Poor scores = lower search visibility
- **Source:** web.dev Core Web Vitals

### WEB-10 [HIGH] Image Optimization
Modern formats, responsive sizes, lazy loading for below-fold images.
- **Detect:**
  - Large unoptimized images (PNG/JPEG > 200KB)
  - No lazy loading on below-fold images
  - No responsive image sizing (srcset/sizes)
  - Search: `<img` without `loading="lazy"` (excluding above-fold hero images)
- **Fix:** Convert to WebP/AVIF. Use `<img srcset>` for responsive sizes. `loading="lazy"` for below-fold. Use image CDN (Cloudinary, imgix, Vercel Image Optimization) for on-the-fly resizing
- **Impact:** Unoptimized, non-lazy images inflate page weight and push back Largest Contentful Paint — slower loads measurably cost conversion and search ranking.
- **Source:** web.dev Image Optimization

### WEB-11 [HIGH] Code Splitting & Dynamic Imports
Route-based code splitting. Lazy load non-critical JavaScript.
- **Detect:**
  - Single large JavaScript bundle (> 200KB gzipped)
  - No dynamic imports for routes/features
  - Heavy libraries imported in main bundle (moment.js, lodash full)
- **Fix:** Route-based splitting (Next.js/React.lazy automatic). Dynamic import for heavy features. Replace heavy libraries with lighter alternatives (date-fns, lodash-es). Tree-shake unused exports
- **Impact:** A single unsplit bundle forces every visitor to download the whole application's code before any route renders, even for a one-page visit.
- **Source:** webpack Code Splitting, Next.js Dynamic Imports

### WEB-12 [HIGH] HTTPS & Cookie Security
All cookies secure. Proper cookie attributes.
- **Detect:**
  - Cookies without `Secure` flag
  - Session cookies without `HttpOnly`
  - Missing `SameSite` attribute
  - Cookies with excessive expiry (> 1 year for non-essential)
- **Fix:** Set all cookies: `Secure; HttpOnly; SameSite=Lax` (or Strict for sensitive). Session cookies: no explicit expiry (browser session). Persistent cookies: reasonable TTL. Use `__Host-` prefix for sensitive cookies (browser-enforced: requires `Secure`, forbids `Domain`, requires `Path=/` — blocks subdomain cookie-tossing); use `__Secure-` only when legitimate subdomain sharing is required. Reference form: `Set-Cookie: __Host-SID=<token>; path=/; Secure; HttpOnly; SameSite=Strict`
- **Impact:** A cookie missing Secure/HttpOnly/SameSite is readable over plaintext HTTP, stealable via XSS, or replayable cross-site — any one of the three defeats session security.
- **Source:** MDN HTTP Cookies, OWASP Cookie Security

### WEB-13 [CRITICAL] Sensitive Data Cache Exclusion
No credentials/PII in HTTP cache, CDN cache, or logs.
- **Detect:**
  - Sensitive API responses without `Cache-Control: no-store`
  - Auth tokens in URL query parameters (cached in logs, browser history)
  - PII in CDN-cached responses
  - Sensitive data in error messages/stack traces returned to client
- **Fix:** `Cache-Control: no-store, no-cache` for sensitive endpoints. Auth tokens in headers only (never URL). Sanitize error responses. Exclude sensitive paths from CDN
- **Impact:** Sensitive data cached by a browser, proxy, or CDN persists outside the application's control and can surface in shared caches, browser history, or logs long after the response is served.
- **Source:** OWASP Secure Headers
