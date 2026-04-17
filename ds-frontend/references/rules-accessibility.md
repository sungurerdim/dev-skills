# Rules: Accessibility (WCAG 2.2)

Rules for audit/fix modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

Applies to all UI platforms: web, mobile, desktop.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Critical (Keyboard & Contrast)** | AXE-01 to AXE-04 (4 CRITICAL) | ~14 |
| **High (ARIA & Structure)** | AXE-05 to AXE-09 (5 HIGH) | ~72 |
| **Medium (Targets & Announcements)** | AXE-10 to AXE-12 (3 MEDIUM) | ~132 |

---

## Critical (Keyboard & Contrast)

### AXE-01 [CRITICAL] Keyboard Navigation
All interactive elements reachable via Tab key, operable via Enter/Space/Escape. No keyboard traps.
- **Detect:**
  - `<div>` or `<span>` with click handler but no `role="button"` and no `tabindex="0"`
  - Custom interactive elements without keyboard event handlers
  - Modal/dialog without focus trap (Tab escapes to background content)
  - Focus trapped with no Escape key handler
  - Web: search for click handlers on non-interactive elements
  - Flutter: GestureDetector without Focus widget wrapper
  - SwiftUI: .onTapGesture without .focusable()
  - Compose: Modifier.clickable without Modifier.focusable
- **Fix:** Use native interactive elements (`<button>`, `<a>`, `<input>`) where possible. For custom elements: add `role`, `tabindex="0"`, keyboard handlers (Enter to activate, Escape to dismiss). For modals: implement focus trap with Tab cycling and Escape to close.
- **Impact:** 2.5B people worldwide have disabilities. Keyboard navigation is foundation of all assistive technology access. Missing keyboard access = legal liability under EAA (June 2025), ADA, AODA.
- **Source:** WCAG 2.2 SC 2.1.1 Keyboard, W3C ARIA APG Dialog Pattern

### AXE-02 [CRITICAL] Focus Indicator
Visible focus ring on all interactive elements. Minimum 3:1 contrast against surrounding area.
- **Detect:**
  - `outline: none` or `outline: 0` without `:focus-visible` replacement style
  - Focus indicator with contrast <3:1 against adjacent colors
  - Focus indicator smaller than 2px (not visible enough)
  - Web: search for `outline: none/0` in CSS, verify `:focus-visible` exists
  - Flutter: missing `focusColor` in ThemeData
  - SwiftUI: no visible focus ring in tvOS/macOS mode
  - Compose: missing `indication` in Modifier.clickable
- **Fix:** Add `:focus-visible` style with 3px or larger outline or 2px solid with offset. Recommended: `outline: 3px solid currentColor; outline-offset: 2px`. Use `:focus-visible` (not `:focus`) to show ring only for keyboard users.
- **Impact:** Without focus indicator, keyboard users cannot see where they are on page. WCAG 2.2 SC 2.4.11 requires minimum focus appearance.
- **Source:** WCAG 2.2 SC 2.4.7 Focus Visible, SC 2.4.11 Focus Appearance

### AXE-03 [CRITICAL] Text Contrast
Text contrast ratio at least 4.5:1 for normal text, at least 3:1 for large text (18pt+ or 14pt+ bold).
- **Detect:** Calculate contrast ratio between text color and background color pairs. Flag pairs below threshold.
  - Check both light and dark theme values
  - Large text threshold: 18pt (24px) regular weight, or 14pt (18.7px) bold
  - Incidental text (disabled, decorative) exempt
  - Web: parse CSS color and background-color pairs
  - Flutter: check TextStyle color against parent container color
  - All platforms: verify against both theme variants
- **Fix:** Adjust either text or background color to meet ratio. Use WCAG contrast formula. Prefer adjusting lighter color (more perceptually stable). Tools: WebAIM Contrast Checker, Chrome DevTools contrast inspector.
- **Impact:** 83.6% of websites fail color contrast (WebAIM 2024). Number one accessibility violation. Error rate increases significantly with low contrast, especially for low-vision users (14% of adults).
- **Source:** WCAG 2.2 SC 1.4.3 Contrast (Minimum), WebAIM Million 2024

### AXE-04 [CRITICAL] Interactive Element Labels
All buttons, links, and inputs have an accessible name (visible text, aria-label, or aria-labelledby).
- **Detect:**
  - `<button>` without text content or `aria-label`
  - `<a>` without text content (icon-only links without aria-label)
  - `<input>` without associated `<label>` or `aria-labelledby`
  - Icon buttons (trash, edit, close) without `aria-label`
  - `<img>` without `alt` attribute (meaningful images)
  - Flutter: IconButton without tooltip
  - SwiftUI: Button with Image-only label without .accessibilityLabel
  - Compose: IconButton without contentDescription
- **Fix:** Add accessible name. Prefer visible text over aria-label. Icon-only buttons: `aria-label="Delete item"` (web), `tooltip: 'Delete item'` (Flutter), `.accessibilityLabel("Delete item")` (SwiftUI), `contentDescription = "Delete item"` (Compose). Decorative images: `alt=""` (web), excludeFromSemantics (Flutter).
- **Impact:** Without accessible names, screen readers announce "button" (unhelpful). Users cannot understand or operate unlabeled controls.
- **Source:** WCAG 2.2 SC 1.1.1 Non-text Content, SC 4.1.2 Name Role Value

---

## High (ARIA & Structure)

### AXE-05 [HIGH] ARIA Widget Patterns
Custom widgets follow W3C ARIA Authoring Practices Guide (APG) patterns for correct role, state, and property usage.
- **Detect:** Custom implementations of common widgets without correct ARIA pattern:
  - Tabs: missing `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`, arrow key navigation
  - Dialog: missing `role="dialog"`, `aria-modal="true"`, focus trap
  - Accordion: missing `aria-expanded`, `aria-controls`, button trigger
  - Combobox: missing `role="combobox"`, `aria-expanded`, `aria-activedescendant`
  - Menu: missing `role="menu"`, `role="menuitem"`, arrow key navigation
  - Search for custom widget containers without ARIA roles
- **Fix:** Implement per W3C APG specification. Each pattern defines required roles, states, properties, and keyboard interactions.
- **Impact:** Incorrect ARIA is worse than no ARIA -- it actively misleads assistive technology users about what a widget does and how to operate it.
- **Source:** W3C ARIA Authoring Practices Guide (APG)

### AXE-06 [HIGH] Image Alt Text
Meaningful images have descriptive alt text. Decorative images have empty alt or presentation role.
- **Detect:**
  - `<img>` without `alt` attribute (missing entirely)
  - Meaningful images with generic alt: "image", "photo", "icon", "banner"
  - Decorative images (backgrounds, separators) with non-empty alt
- **Fix:** Meaningful images: describe content and function ("Company logo linking to homepage"). Decorative: `alt=""` (web) or `excludeFromSemantics: true` (Flutter). Complex images (charts, diagrams): provide `aria-describedby` with full description.
- **Impact:** Screen reader users encounter images frequently. Missing or generic alt text provides no information, while verbose decorative alt text creates noise.
- **Source:** WCAG 2.2 SC 1.1.1, W3C Alt Text Decision Tree

### AXE-07 [HIGH] Form Label Association
Every form input has a programmatically associated label.
- **Detect:**
  - `<input>` without `<label for="id">` or `aria-labelledby`
  - Placeholder text used as sole label (disappears on input)
  - `<select>`, `<textarea>` without associated label
  - Flutter: TextField without InputDecoration.labelText
  - SwiftUI: TextField without .accessibilityLabel or visible label
  - Compose: TextField without label parameter
- **Fix:** Add `<label for="input-id">` (web) or platform equivalent. Label must be visible and persistent (not placeholder-only). Mark required fields with * or explicit "required" text.
- **Impact:** 32% higher form error rate when only optional fields are marked vs required fields (Baymard Institute). Unlabeled inputs are unusable with screen readers.
- **Source:** WCAG 2.2 SC 1.3.1 Info and Relationships, SC 3.3.2 Labels or Instructions

### AXE-08 [HIGH] Heading Hierarchy
Sequential heading levels (h1 then h2 then h3), no skipped levels, single h1 per page.
- **Detect:**
  - `<h3>` appearing after `<h1>` without `<h2>` in between (skipped level)
  - Multiple `<h1>` on same page
  - Heading used for visual styling only (should be CSS, not heading element)
  - Flutter: no explicit heading semantics (Semantics with header: true)
- **Fix:** Restructure headings to follow logical hierarchy. Use CSS for visual sizing, HTML for structure. Each page: single h1 (page title), then h2 (sections), h3 (subsections).
- **Impact:** Screen reader users navigate by headings (67% use headings as primary navigation method, WebAIM survey). Skipped levels break this navigation model.
- **Source:** WCAG 2.2 SC 1.3.1, MDN Heading Elements

### AXE-09 [HIGH] Non-Text Contrast
UI components (borders, icons, focus indicators) and meaningful graphics maintain at least 3:1 contrast ratio.
- **Detect:** Check contrast of:
  - Form field borders against background
  - Icon fills against background
  - Chart/graph elements against adjacent elements
  - Custom checkbox/radio visual indicators
- **Fix:** Adjust component colors to meet 3:1 ratio. Especially important: light gray borders on white backgrounds (common failure).
- **Impact:** Low-contrast UI components become invisible to low-vision users. Form boundaries, icons, and data visualizations all depend on sufficient non-text contrast.
- **Source:** WCAG 2.2 SC 1.4.11 Non-text Contrast

---

## Medium (Targets & Announcements)

### AXE-10 [MEDIUM] Target Size
Interactive targets minimum 24x24 CSS px (AA), 44x44 recommended (AAA).
- **Detect:** Measure interactive element dimensions:
  - Buttons, links, checkboxes, radio buttons, toggles
  - Flag elements <24x24 CSS px
  - Warn for elements 24-43 CSS px (meets AA but not AAA)
  - Exception: inline text links (size determined by text)
- **Fix:** Increase padding/size to meet minimum. Icon buttons: add padding around icon to reach target. Mobile: 48x48dp minimum (Material), 44x44pt (Apple HIG).
- **Impact:** Error rate 3x higher below 44px target size (University of Maryland 2023). Affects motor impairments, mobile users, and elderly.
- **Source:** WCAG 2.2 SC 2.5.8 Target Size, SC 2.5.5 Target Size Enhanced

### AXE-11 [MEDIUM] Error Announcement
Form errors announced to screen readers via aria-live region or role="alert".
- **Detect:**
  - Error messages that appear visually but are not announced (no aria-live, no role="alert")
  - Form validation errors only shown on submit without per-field announcement
  - Dynamic content changes without live region notification
- **Fix:** Add `aria-live="polite"` to error message container, or `role="alert"` for critical errors. Inline validation: announce error on blur, remove announcement on correction.
  - Flutter: Semantics with liveRegion: true
  - SwiftUI: AccessibilityNotification.Announcement
  - Compose: LiveRegionMode.Polite
- **Impact:** Sighted users see error messages appear. Screen reader users hear nothing unless errors announced via live regions. Silent failures = abandoned forms.
- **Source:** WCAG 2.2 SC 4.1.3 Status Messages, W3C ARIA Live Regions

### AXE-12 [MEDIUM] Reduced Motion
Non-essential animations disabled when user prefers reduced motion.
- **Detect:**
  - Animations without `prefers-reduced-motion` media query check
  - Auto-playing animations (carousels, parallax, decorative motion)
  - Essential animations (progress indicators, state changes) should still work
  - Web: CSS animations/transitions without `@media (prefers-reduced-motion: reduce)` guard
  - Flutter: no MediaQuery.disableAnimations check
  - SwiftUI: no ReduceMotion environment check
  - Compose: no reduceMotion accessibility check
- **Fix:** Wrap non-essential animations: `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }`. Keep essential animations (loading spinners, progress bars) but simplify them.
- **Impact:** Motion can trigger vestibular disorders (dizziness, nausea) in affected users. Respecting preference is both accessibility and comfort requirement.
- **Source:** WCAG 2.2 SC 2.3.3 Animation from Interactions
