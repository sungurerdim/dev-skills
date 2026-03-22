# Rules: Web-Specific

Conditional rules loaded only for web frontend projects. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Web Security** | WEB-01–04 (1 BLOCKER, 3 CRITICAL) | ~12 |
| **Web Quality** | WEB-05–08 (4 MAJOR) | ~55 |
| **Web Performance** | WEB-09–13 (2 CRITICAL, 3 MAJOR) | ~105 |

---

## Web Security

### WEB-01 [BLOCKER] Content Security Policy
CSP header preventing inline scripts and unauthorized sources.
- **Detect:**
  - No `Content-Security-Policy` header in responses
  - CSP with `unsafe-inline` or `unsafe-eval` for scripts
  - No CSP meta tag or header configuration
  - Search: absence of `content-security-policy` in middleware/headers config
- **Fix:** Set CSP header: `default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' [api-domains]`. Use nonces for inline scripts. Report violations with `report-uri`
- **Impact:** CSP prevents XSS exploitation even when injection vulnerabilities exist
- **Source:** MDN CSP, OWASP CSP Cheat Sheet

### WEB-02 [CRITICAL] CORS Configuration
Restrictive CORS. No wildcard origins in production.
- **Detect:**
  - `Access-Control-Allow-Origin: *` in production config
  - CORS allowing any origin with credentials
  - Search: `origin: '*'`, `origin: true`, `cors({ origin: '*' })` in production code
- **Fix:** Whitelist specific origins. Never use `*` with credentials. Validate origin against whitelist. Set appropriate `Access-Control-Allow-Methods` and `Access-Control-Allow-Headers`
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
- **Source:** OWASP XSS Prevention Cheat Sheet

### WEB-04 [CRITICAL] CSRF Protection
State-changing operations protected against cross-site request forgery.
- **Detect:**
  - No CSRF token in forms/state-changing requests
  - `SameSite` cookie attribute missing
  - No CSRF middleware configured
  - Search: POST/PUT/DELETE handlers without CSRF validation
- **Fix:** Use `SameSite=Strict` or `SameSite=Lax` cookies. CSRF tokens for form submissions. Verify `Origin`/`Referer` headers. Use framework CSRF middleware (csurf, Django CSRF, Spring CSRF)
- **Source:** OWASP CSRF Prevention Cheat Sheet

---

## Web Quality

### WEB-05 [MAJOR] Responsive Design
Layout adapts to all screen sizes. No horizontal scroll on mobile.
- **Detect:**
  - Search: `width:` with pixel values >320px without `max-width` or media query context (e.g., `width: 960px`, `width: 1200px` on containers)
  - Search: missing `<meta name="viewport">` tag in HTML entry points (`index.html`, layout templates)
  - Search: `@media` query absence in CSS/SCSS files (zero responsive breakpoints)
  - Search: fixed-width containers without responsive alternatives (`width: [4-9]\d\dpx`, `width: \d{4,}px` without accompanying `max-width` or `%`/`vw` fallback)
  - Images without responsive sizing (`<img` without `srcset` or CSS `max-width: 100%`)
- **Fix:** Use relative units (%, rem, vw). Mobile-first media queries. Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`. Responsive images with `srcset`/`sizes`. CSS Grid/Flexbox for layouts
- **Source:** Responsive Web Design, MDN

### WEB-06 [MAJOR] Web Accessibility (WCAG 2.2 AA)
Core flows meet WCAG 2.2 AA. Keyboard navigable. Screen reader compatible.
- **Detect:**
  - Images without `alt` attribute
  - Form inputs without associated labels
  - Interactive elements not keyboard accessible
  - Missing ARIA roles/landmarks on dynamic content
  - Color contrast below 4.5:1 for normal text
  - Search: `<img` without `alt=`, `<input` without associated `<label`
- **Fix:** Add `alt` text to all images (empty `alt=""` for decorative). Associate labels with inputs. Ensure keyboard navigation (tab order, focus management). Use semantic HTML. Test with screen reader (NVDA, VoiceOver). Ensure 4.5:1 contrast ratio
- **Impact:** ~15% of users have some form of disability. EAA 2025 enforcement for EU
- **Source:** WCAG 2.2, EAA 2019/882

### WEB-07 [MAJOR] Error Pages
Custom error pages (404, 500) with helpful content and consistent branding.
- **Detect:**
  - Default framework error pages in production
  - Stack traces visible in error responses
  - No custom 404 page
  - No global error boundary (React) or error page (Next.js)
- **Fix:** Custom 404 with navigation/search. Custom 500 with "try again" and support contact. Error boundaries for React. Never expose stack traces. Log errors server-side
- **Source:** UX best practices

### WEB-08 [MAJOR] SEO Fundamentals
Proper meta tags, semantic HTML, structured data for public-facing pages.
- **Detect:**
  - Missing `<title>` or `<meta name="description">` on pages
  - No Open Graph / Twitter Card meta tags
  - Non-semantic HTML (div soup)
  - No sitemap.xml or robots.txt
  - Client-side only rendering without SSR/SSG for content pages
- **Fix:** Unique `<title>` and `<meta description>` per page. Open Graph tags for social sharing. Semantic HTML (header, main, nav, article, section). Generate sitemap.xml. SSR/SSG for content pages
- **Source:** Google Search Central, MDN Semantic HTML

---

## Web Performance

### WEB-09 [CRITICAL] Core Web Vitals
LCP < 2.5s, INP < 200ms, CLS < 0.1.
- **Detect:**
  - No performance monitoring (no web-vitals library, no RUM)
  - Large images above the fold without optimization
  - Layout shifts from dynamically loaded content
  - Long tasks blocking main thread
- **Fix:** Optimize LCP: preload critical resources, optimize images (WebP/AVIF, srcset), use CDN. Optimize INP: break long tasks, use `requestIdleCallback`, debounce handlers. Optimize CLS: set explicit dimensions on images/embeds, avoid injecting content above viewport
- **Impact:** Core Web Vitals are a Google ranking signal. Poor scores = lower search visibility
- **Source:** web.dev Core Web Vitals

### WEB-10 [MAJOR] Image Optimization
Modern formats, responsive sizes, lazy loading for below-fold images.
- **Detect:**
  - Large unoptimized images (PNG/JPEG > 200KB)
  - No lazy loading on below-fold images
  - No responsive image sizing (srcset/sizes)
  - Search: `<img` without `loading="lazy"` (excluding above-fold hero images)
- **Fix:** Convert to WebP/AVIF. Use `<img srcset>` for responsive sizes. `loading="lazy"` for below-fold. Use image CDN (Cloudinary, imgix, Vercel Image Optimization) for on-the-fly resizing
- **Source:** web.dev Image Optimization

### WEB-11 [MAJOR] Code Splitting & Dynamic Imports
Route-based code splitting. Lazy load non-critical JavaScript.
- **Detect:**
  - Single large JavaScript bundle (> 200KB gzipped)
  - No dynamic imports for routes/features
  - Heavy libraries imported in main bundle (moment.js, lodash full)
- **Fix:** Route-based splitting (Next.js/React.lazy automatic). Dynamic import for heavy features. Replace heavy libraries with lighter alternatives (date-fns, lodash-es). Tree-shake unused exports
- **Source:** webpack Code Splitting, Next.js Dynamic Imports

### WEB-12 [MAJOR] HTTPS & Cookie Security
All cookies secure. Proper cookie attributes.
- **Detect:**
  - Cookies without `Secure` flag
  - Session cookies without `HttpOnly`
  - Missing `SameSite` attribute
  - Cookies with excessive expiry (> 1 year for non-essential)
- **Fix:** Set all cookies: `Secure; HttpOnly; SameSite=Lax` (or Strict for sensitive). Session cookies: no explicit expiry (browser session). Persistent cookies: reasonable TTL. Use `__Host-` prefix for sensitive cookies
- **Source:** MDN HTTP Cookies, OWASP Cookie Security

### WEB-13 [CRITICAL] Sensitive Data Cache Exclusion
No credentials/PII in HTTP cache, CDN cache, or logs.
- **Detect:**
  - Sensitive API responses without `Cache-Control: no-store`
  - Auth tokens in URL query parameters (cached in logs, browser history)
  - PII in CDN-cached responses
  - Sensitive data in error messages/stack traces returned to client
- **Fix:** `Cache-Control: no-store, no-cache` for sensitive endpoints. Auth tokens in headers only (never URL). Sanitize error responses. Exclude sensitive paths from CDN
- **Source:** OWASP Secure Headers
