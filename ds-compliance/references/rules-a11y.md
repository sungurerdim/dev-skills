# Rules: Accessibility (WCAG 2.2 AA)

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

Target: WCAG 2.2 AA (ISO/IEC 40500:2025) — the enforceable baseline that EAA/ADA/Section 508 reference. WCAG 3.0 is a Working Draft (March 2026; not expected final before 2028) — never test against 3.0 draft criteria or its Bronze/Silver/Gold tiers.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Accessibility** | A11Y-01–12 (4 CRITICAL, 5 HIGH, 3 MEDIUM) | ~10 |

---

## Accessibility

**Regulatory framing (2026):** EAA is in active enforcement since 28 Jun 2025 (first court ruling: France/Carrefour — 71% RGAA conformance rejected as a defense, daily penalties imposed; NL/SE/DK market-surveillance audits running). The harmonized EU standard is still EN 301 549 → WCAG **2.1** AA (the WCAG-2.2-based EN 301 549 v4.1.1 was expected in 2026 but not yet OJ-harmonized as of Jul 2026). US ADA Title II likewise mandates WCAG **2.1** AA; DOJ interim final rule (20 Apr 2026) extended compliance to 26 Apr 2027 (population ≥50k) / 26 Apr 2028 (others). Auditing against WCAG 2.2 AA (as these rules do) satisfies both regimes with margin.

### A11Y-01 [CRITICAL] Semantic Labels on Interactive Elements
All interactive elements (buttons, links, inputs, toggles) must have accessible labels.
- **Detect:**
  - HTML/JSX: `<button>`, `<a>`, `<input>` without `aria-label`, `aria-labelledby`, visible text content, or `<label>` association
  - Flutter: `ElevatedButton`, `IconButton`, `GestureDetector` without `semanticsLabel` or `Semantics` wrapper
  - SwiftUI: `Button`, `Toggle` without `.accessibilityLabel`
  - Compose: `IconButton`, `Button` without `contentDescription` or `semantics { contentDescription = ... }`
  - React Native: `TouchableOpacity`, `Pressable` without `accessibilityLabel`
- **Fix:** Add appropriate label attribute for the framework
- **Impact:** Unlabeled controls are invisible to screen readers — blind and low-vision users cannot identify or operate the element at all.
- **Source:** WCAG 2.2 SC 4.1.2 Name, Role, Value

### A11Y-02 [CRITICAL] Keyboard Navigation
All interactive elements must be reachable and operable via keyboard.
- **Detect:**
  - `onClick` without `onKeyDown`/`onKeyUp` on non-button elements (`<div onClick>`, `<span onClick>`)
  - Missing `tabIndex` on custom interactive elements
  - `tabIndex` > 0 (disrupts natural tab order)
  - CSS `outline: none` or `outline: 0` without alternative focus indicator
- **Fix:** Use semantic HTML (`<button>`, `<a>`), add keyboard handlers, preserve focus indicators
- **Impact:** Keyboard-only and switch-device users (motor impairments, no mouse) cannot reach or activate the element — the feature is unusable for them.
- **Source:** WCAG 2.2 SC 2.1.1 Keyboard

### A11Y-03 [CRITICAL] Color Contrast
Text must meet minimum contrast ratios against background.
- **Detect:**
  - Hardcoded color values with insufficient contrast (text <4.5:1, large text <3:1)
  - Grey text on white: `color: #999` or lighter on `#fff` background
  - Placeholder text with insufficient contrast
- **Fix:** Adjust colors to meet WCAG AA ratios (4.5:1 normal text, 3:1 large text/UI components)
- **Impact:** Low-vision and color-blind users cannot read text below the contrast floor — content becomes illegible rather than just harder to read.
- **Source:** WCAG 2.2 SC 1.4.3 Contrast (Minimum)

### A11Y-04 [HIGH] Image Alt Text
All meaningful images must have alt text. Decorative images must be marked as such.
- **Detect:**
  - `<img>` without `alt` attribute
  - `<img alt="">` on non-decorative images (images with information content)
  - Flutter `Image` without `semanticLabel`
  - React Native `Image` without `accessibilityLabel`
- **Fix:** Add descriptive `alt` text or mark as decorative (`alt=""`, `role="presentation"`)
- **Impact:** Screen reader users hear nothing (or a useless filename) where a sighted user sees meaning — the image's information is lost entirely.
- **Source:** WCAG 2.2 SC 1.1.1 Non-text Content

### A11Y-05 [HIGH] Form Error Identification
Error messages must be programmatically associated with their form fields.
- **Detect:**
  - Form validation errors displayed without `aria-describedby` or `aria-errormessage` association
  - Error text rendered without `role="alert"` or `aria-live="polite"`
  - Required fields without `aria-required="true"` or `required` attribute
- **Fix:** Associate errors with fields via `aria-describedby`, announce errors with live regions
- **Impact:** Screen reader users aren't told which field failed or why — they must guess across the whole form to find and fix the error.
- **Source:** WCAG 2.2 SC 3.3.1 Error Identification

### A11Y-06 [HIGH] Heading Hierarchy
Page headings must follow logical hierarchy (no skipped levels).
- **Detect:**
  - `<h1>` followed by `<h3>` (skipping `<h2>`)
  - Multiple `<h1>` elements per page
  - No `<h1>` on page
- **Fix:** Restructure headings to follow sequential hierarchy
- **Impact:** Screen reader users navigate by heading level to skim a page — a skipped or duplicated level breaks that navigation model and hides structure.
- **Source:** WCAG 2.2 SC 1.3.1 Info and Relationships

### A11Y-07 [MEDIUM] Focus Management
Focus must be managed during dynamic content changes (modals, route changes).
- **Detect:**
  - Modal/dialog without focus trap
  - Route change without focus reset to main content
  - Dynamic content insertion without `aria-live` announcement
- **Fix:** Implement focus trap for modals, reset focus on navigation, use `aria-live` for updates
- **Impact:** Focus left behind after a modal or route change strands keyboard/screen-reader users off-screen or back at the top, forcing them to re-navigate from scratch.
- **Source:** WCAG 2.2 SC 2.4.3 Focus Order

### A11Y-08 [MEDIUM] Touch Target Size
Interactive elements must meet minimum touch target size.
- **Detect:**
  - Buttons/links with `width` or `height` < 44px (iOS) or < 48dp (Android)
  - Flutter: `SizedBox` wrapping tappable with dimensions < 48
  - Inline links without adequate spacing
- **Fix:** Ensure minimum 44x44px (iOS) / 48x48dp (Android) / 24x24px (WCAG 2.2 AA) target size
- **Impact:** Targets below the minimum size are hard or impossible to tap accurately for users with motor impairments or tremor, and on mobile touchscreens generally.
- **Source:** WCAG 2.2 SC 2.5.8 Target Size (Minimum)

### A11Y-09 [HIGH] Page Language Declared
All text content must declare its language so assistive technology selects the correct voice/pronunciation and hyphenation rules.
- **Detect:**
  - `<html>` with no `lang` attribute, or `lang=""`
  - A page/section with substantial content in a different language than the document `lang` and no `lang` override on that sub-tree (`<span lang="fr">`, `<blockquote lang="tr">`)
  - Framework app-shell templates (`index.html`, root layout) shipping `<html lang="en">` hardcoded regardless of the served locale in an i18n project
- **Fix:** Set `<html lang="{bcp47-code}">` matching the actual served content; in an i18n app, derive it from the active locale rather than hardcoding; wrap any inline foreign-language passage in its own `lang` attribute.
- **Impact:** A missing or wrong `lang` attribute makes a screen reader use the wrong pronunciation engine for the entire page — every word is mispronounced, not just misformatted, and browser translation tools mis-trigger or fail to trigger.
- **Source:** WCAG 2.2 SC 3.1.1 Language of Page

### A11Y-10 [CRITICAL] Zoom and Text Resize Not Blocked
Users must be able to zoom and resize text up to 200% without losing content or functionality.
- **Detect:**
  - `<meta name="viewport">` containing `user-scalable=no` or `maximum-scale` below 5
  - Fixed-pixel font sizes with no relative-unit path to 200% resize (root font size and layout that clip or overlap at 200% browser zoom)
  - Native (iOS/Android) text that ignores the OS-level Dynamic Type / font-scale setting
- **Fix:** Remove `user-scalable=no` and restrictive `maximum-scale` from the viewport meta tag; use relative units (`rem`/`em`/`%`) for text sizing so browser zoom and OS text-scale both work; on iOS/Android, opt UI text into Dynamic Type / scalable font APIs rather than fixed point sizes.
- **Impact:** Blocking zoom or ignoring OS text-scale doesn't just inconvenience low-vision users, it removes the one mechanism they rely on to read the page at all — content that can't reach a readable size for that user is functionally invisible, the same severity as failing contrast (A11Y-03).
- **Source:** WCAG 2.2 SC 1.4.4 Resize Text

### A11Y-11 [HIGH] Media Captions and Transcripts
Prerecorded audio and video content must have captions or an equivalent transcript.
- **Detect:**
  - `<video>`/`<audio>` elements with spoken/meaningful audio content and no `<track kind="captions">`, no adjacent transcript link, and no third-party captioning (e.g. YouTube auto-captions) confirmed present
  - Onboarding/marketing video content embedded with no caption track
- **Fix:** Add a captions track (`<track kind="captions" src="…" srclang="{locale}">`) for every prerecorded video with spoken content, or provide a full-text transcript adjacent to the player; for third-party embeds, verify the embed's own captions are enabled by default, not opt-in.
- **Impact:** Deaf and hard-of-hearing users get zero access to audio-only information in uncaptioned media — not degraded access, none — and auto-play video with no caption track is the single most common way this gap ships unnoticed.
- **Source:** WCAG 2.2 SC 1.2.2 Captions (Prerecorded)

### A11Y-12 [MEDIUM] Skip Navigation Link
A mechanism exists to bypass repeated navigation blocks and jump directly to main content.
- **Detect:**
  - No "Skip to main content" link as the first focusable element in the DOM (or a screen-reader-only link that appears on focus)
  - `<main>`/`role="main"` landmark present but nothing lets a keyboard user reach it without tabbing through the full nav on every single page
- **Fix:** Add a visually-hidden-until-focused skip link as the first tabbable element, targeting the main-content landmark (`<a href="#main-content" class="skip-link">Skip to main content</a>`); ensure the target has a matching `id`/`tabindex="-1"` so focus actually lands there.
- **Impact:** Without a skip link, every keyboard and screen-reader user re-tabs through the entire navigation on every page load before reaching content — a tax paid on every single page visit, not a one-time inconvenience.
- **Source:** WCAG 2.2 SC 2.4.1 Bypass Blocks
