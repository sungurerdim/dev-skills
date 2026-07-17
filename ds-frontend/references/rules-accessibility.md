# Rules: Accessibility (WCAG 2.2)

Rules for audit/fix modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

Applies to all UI platforms: web, mobile, desktop.

Conformance target: WCAG 2.2 AA — the standard operative in current US/EU law. WCAG 3.0 remains a W3C Working Draft referenced by no active law; keep targeting 2.2 until a law references a WCAG 3.0 Recommendation.

Coverage: AXE-01 to AXE-23 cover the WCAG 2.2 A/AA success criteria that manifest in code, plus ARIA implementation correctness (APG keyboard models, name computation, live regions) — including all four new-in-2.2 criteria (2.4.11 Focus Not Obscured, 2.5.7 Dragging Movements, 3.3.7 Redundant Entry, 3.3.8 Accessible Authentication). Rules sourced from AAA criteria are marked as such and never block AA conformance claims.

**Automated-tool limits:** automated scanners (axe-core etc.) detect only a share of accessibility issues — the exact percentage is vendor-contested (vendor ~57% vs lower independent estimates; never hard-code a number). Manual keyboard + screen-reader passes remain mandatory; weight manual testing toward the screen readers users actually run (JAWS/NVDA/VoiceOver per current WebAIM survey).

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Critical (Keyboard & Contrast)** | AXE-01 to AXE-04 (4 CRITICAL) | ~22 |
| **High (ARIA & Structure)** | AXE-05 to AXE-09 (5 HIGH) | ~85 |
| **Medium (Targets & Announcements)** | AXE-10 to AXE-12 (3 MEDIUM) | ~148 |
| **AA Completeness (Structure, Input & new-in-2.2)** | AXE-13 to AXE-20 (2 HIGH, 6 MEDIUM) | ~191 |
| **ARIA Implementation Correctness** | AXE-21 to AXE-23 (3 MEDIUM) | ~263 |

---

## Critical (Keyboard & Contrast)

### AXE-01 [CRITICAL] Keyboard Navigation
All interactive elements reachable via Tab key, operable via Enter/Space/Escape. No keyboard traps.
- **Detect:**
  - `<div>` or `<span>` with click handler but no `role="button"` and no `tabindex="0"`
  - Custom interactive elements without keyboard event handlers
  - Modal/dialog without focus trap (Tab escapes to background content)
  - Focus trapped with no Escape key handler
  - Positive `tabindex` values (`tabindex="1"` or higher) overriding natural DOM focus order (SC 2.4.3 Focus Order)
  - Web: search for click handlers on non-interactive elements
  - Flutter: GestureDetector without Focus widget wrapper
  - SwiftUI: .onTapGesture without .focusable()
  - Compose: Modifier.clickable without Modifier.focusable
- **Fix:** Use native interactive elements (`<button>`, `<a>`, `<input>`) where possible. For custom elements: add `role`, `tabindex="0"`, keyboard handlers (Enter to activate, Escape to dismiss). For modals: implement focus trap with Tab cycling and Escape to close.
- **Impact:** 2.5B people worldwide have disabilities. Keyboard navigation is foundation of all assistive technology access. Missing keyboard access = legal liability under EAA (in force June 2025; enforcement is active — first EAA lawsuits filed November 2025), ADA, AODA.
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
- **Impact:** Without focus indicator, keyboard users cannot see where they are on page. WCAG 2.2 SC 2.4.7 (AA) requires a visible indicator; the size/contrast bar used here follows SC 2.4.13 Focus Appearance (AAA) as best practice.
- **Source:** WCAG 2.2 SC 2.4.7 Focus Visible, SC 2.4.13 Focus Appearance (AAA)

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
  - Links whose accessible name is generic ("click here", "read more", "learn more") with no programmatic context (SC 2.4.4 Link Purpose)
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
  - Text baked into images (banners, buttons shipped as PNGs) where real text + CSS would serve — unscalable and invisible to screen readers/translation (SC 1.4.5 Images of Text, AA)
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
  - Auto-advancing carousels / auto-updating content without a visible pause/stop control — required for **all** users, independent of the reduced-motion preference (SC 2.2.2 Pause, Stop, Hide — A)
  - Essential animations (progress indicators, state changes) should still work
  - Web: CSS animations/transitions without `@media (prefers-reduced-motion: reduce)` guard
  - Flutter: no MediaQuery.disableAnimations check
  - SwiftUI: no ReduceMotion environment check
  - Compose: no reduceMotion accessibility check
- **Fix:** Wrap non-essential animations: `@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; } }`. Keep essential animations (loading spinners, progress bars) but simplify them.
- **Impact:** Motion can trigger vestibular disorders (dizziness, nausea) in affected users. Respecting preference is both accessibility and comfort requirement.
- **Source:** WCAG 2.2 SC 2.3.3 Animation from Interactions (AAA; the `prefers-reduced-motion` practice is the accepted baseline), SC 2.2.2 Pause, Stop, Hide (A)

---

## AA Completeness (Structure, Input & new-in-2.2)

### AXE-13 [HIGH] Page Scaffold: Skip Link, Landmarks, Language, Title
Every page provides the structural scaffold assistive technology depends on: a skip-to-content link, semantic landmarks, a correct language declaration, and a route-specific title.
- **Detect:**
  - No skip link as the first focusable element on pages with repeated navigation (SC 2.4.1 Bypass Blocks)
  - No `<main>` landmark (or `role="main"`); content regions not wrapped in `header`/`nav`/`main`/`footer`
  - Missing or wrong `lang` on `<html>`; foreign-language passages without their own `lang` (SC 3.1.1/3.1.2)
  - SPA route changes that never update `document.title` — every route announces the same generic title (SC 2.4.2)
  - Mobile: screens without semantic grouping (Flutter `Semantics`, SwiftUI `accessibilityElement(children:)`, Compose `semantics {}`)
- **Fix:** Add a visually-hidden-until-focused skip link targeting `<main>`; wrap regions in landmarks; set `lang` per locale; hook the router to update `document.title` per route.
- **Impact:** Screen-reader users navigate by landmarks and titles first (WebAIM surveys rank them alongside headings); without a skip link, keyboard users re-tab through the entire nav on every single page; a wrong `lang` makes the screen reader mispronounce all content in the wrong phonology.
- **Source:** WCAG 2.2 SC 2.4.1 Bypass Blocks, SC 2.4.2 Page Titled, SC 3.1.1 Language of Page, SC 3.1.2 Language of Parts; W3C ARIA landmarks practice

### AXE-14 [MEDIUM] Input Purpose & Keyboard Optimization
Inputs collecting user data declare their purpose (`autocomplete`) and trigger the right input surface (`type`/`inputmode`, platform keyboard type).
- **Detect:**
  - Name/email/tel/address/credit-card inputs without the matching `autocomplete` token, or with `autocomplete="off"` on identity fields (SC 1.3.5)
  - Numeric/tel/email/url inputs left as bare `type="text"` with no `inputmode`
  - Flutter: `TextField` without `keyboardType`; SwiftUI: no `textContentType`/`keyboardType`; Compose: no `KeyboardOptions`
- **Fix:** Add the correct `autocomplete` token from the HTML spec list; set semantic `type` (falling back to `inputmode` where the type's UI is undesirable); set the platform keyboard type on mobile.
- **Impact:** SC 1.3.5 is a plain AA requirement; autofill removes the highest-friction, highest-error step for motor- and cognitively-impaired users, and the wrong mobile keyboard slows every user on every field.
- **Source:** WCAG 2.2 SC 1.3.5 Identify Input Purpose; WHATWG HTML autocomplete attribute; MDN inputmode

### AXE-15 [HIGH] Text Resize & Spacing Tolerance
Layout survives 200% text zoom and user text-spacing overrides without clipping or losing content.
- **Detect:**
  - Fixed pixel `height` on containers holding text (clips at 200% zoom / large OS font settings) — `min-height` is the tolerant form
  - Font sizes in `px` where `rem`/`em` would let user settings scale them
  - `overflow: hidden` on text blocks with no intentional line-clamp
  - Flutter: fixed-height widgets containing `Text` with no `MediaQuery.textScaler` handling; SwiftUI: fixed `.font(.system(size:))` ignoring Dynamic Type; Compose: text sizes in `dp` instead of `sp`
- **Fix:** Use relative units for font sizes (`rem`/`em`, `sp`, Dynamic Type styles); prefer `min-height` over `height` on text containers; verify at 200% browser zoom and 1.3–2.0 font scale; tolerate the WCAG text-spacing override set (line-height 1.5, paragraph 2em, letter 0.12em, word 0.16em) without clipping or overlap.
- **Impact:** SC 1.4.4 failure is a functional lockout — low-vision users who zoom lose content entirely, with no workaround. It reproduces only under zoom/large-font settings, so default-setting QA never sees it.
- **Source:** WCAG 2.2 SC 1.4.4 Resize Text, SC 1.4.12 Text Spacing

### AXE-16 [MEDIUM] Focus Not Obscured by Sticky Chrome
An element receiving keyboard focus is never fully hidden behind sticky/fixed headers, footers, or toolbars.
- **Detect:** `position: sticky`/`fixed` chrome with no corresponding `scroll-padding-top/bottom` on the scroll container (or `scroll-margin` on focus/anchor targets); tabbing into an element scrolls it behind the sticky bar; in-page anchor links landing under a fixed header.
- **Fix:** Set `scroll-padding` on the scroll container equal to the sticky chrome's height (use the same size token the chrome uses); or `scroll-margin` on focusable/anchor targets. Verify by tabbing through a scrolled page — every focused element must be visible.
- **Impact:** New-in-2.2 AA. The keyboard user's focus lands behind the sticky header, invisible — functionally identical to a missing focus ring, but it only reproduces on scrolled pages, so it escapes casual QA even on teams that test focus indicators.
- **Source:** WCAG 2.2 SC 2.4.11 Focus Not Obscured (Minimum); MDN scroll-padding

### AXE-17 [MEDIUM] Pointer Alternatives for Drag & Multi-Point Gestures
Every drag or multi-point/path-based gesture has a single-pointer and keyboard alternative.
- **Detect:** Drag-and-drop as the only way to reorder/move/assign (dnd handlers with no button/menu path); sliders operable only by dragging (no arrow-key handling, no adjacent numeric input); pinch/two-finger/path gestures without a single-tap equivalent; mobile swipe-to-delete with no visible alternative affordance.
- **Fix:** Pair every drag with a click/keyboard path — move up/down buttons, a "move to…" menu, a numeric field next to the slider; expose swipe-only actions in an overflow menu too.
- **Impact:** SC 2.5.7 is new-in-2.2 AA. Motor-impaired users, switch-access users, and many assistive-tech setups cannot perform a drag at all — a drag-only interaction is a hard lockout, not a degraded experience.
- **Source:** WCAG 2.2 SC 2.5.7 Dragging Movements, SC 2.5.1 Pointer Gestures

### AXE-18 [MEDIUM] Redundant Entry & Accessible Authentication
Flows never re-ask for information already provided in the same session, and authentication never blocks the tools users rely on.
- **Detect:** Multi-step flows re-asking data entered earlier (billing address re-typed with no "same as shipping"); password fields blocking paste (`onpaste` + `preventDefault`) or carrying `autocomplete="off"` instead of `current-password`/`new-password`; login codes that can't be copy-pasted; a cognitive test (CAPTCHA, memorized puzzle) as the only authentication gate.
- **Fix:** Auto-populate or offer one-tap reuse of previously entered data; never block paste in auth fields; use the correct `autocomplete` tokens so password managers work; offer a non-cognitive alternative (magic link, OAuth, passkey) alongside any CAPTCHA.
- **Impact:** Both criteria are new-in-2.2. Paste-blocking specifically defeats password managers — punishing exactly the users with the strongest passwords — and redundant entry multiplies the error surface for everyone, worst for cognitive and motor impairments.
- **Source:** WCAG 2.2 SC 3.3.7 Redundant Entry (A), SC 3.3.8 Accessible Authentication (Minimum) (AA)

### AXE-19 [MEDIUM] Predictable Interaction; Hover/Focus Content Control
Focusing or filling a control never triggers a surprise context change, and hover/focus-revealed content is dismissable, hoverable, and persistent.
- **Detect:** `onchange` on a `<select>` triggering navigation or form submit; receiving focus opening a modal or moving focus elsewhere; inputs auto-submitting on the last character with no prior notice; tooltips/popovers that can't be dismissed with Escape, that vanish when the pointer moves onto them, or that disappear on a timer.
- **Fix:** Context changes only on explicit activation (button press, Enter); hover/focus-triggered content must be dismissable without moving the pointer (Escape), hoverable (pointer can travel onto it), and persistent until dismissed or invalid.
- **Impact:** Surprise navigation disorients screen-reader and keyboard users who can't see the change coming; a tooltip that dies when the pointer moves toward it is unreadable for screen-magnifier users, who must move the pointer to read.
- **Source:** WCAG 2.2 SC 3.2.1 On Focus (A), SC 3.2.2 On Input (A), SC 1.4.13 Content on Hover or Focus (AA)

### AXE-20 [MEDIUM] Media Alternatives
Video has captions, audio-only content has a transcript, and nothing plays sound automatically.
- **Detect:** `<video>` with speech and no `<track kind="captions">` (or open captions); audio-only content (podcast player, voice notes) with no transcript link; media that autoplays with sound and no immediate pause/mute control; video conveying visual-only information with no audio description or text alternative.
- **Fix:** Add caption tracks (SC 1.2.2) and transcripts (SC 1.2.1); never autoplay with sound — and when any audio plays >3s, provide an independent pause/volume control (SC 1.4.2); provide audio description or an equivalent text alternative for visual-only information (SC 1.2.5).
- **Impact:** Uncaptioned video excludes deaf and hard-of-hearing users entirely, and captions also serve the far larger sound-off-in-public audience; autoplaying sound hijacks the screen reader's audio channel, making the whole page unusable until the user finds the stop control.
- **Source:** WCAG 2.2 SC 1.2.1–1.2.5 Time-based Media, SC 1.4.2 Audio Control

### AXE-21 [MEDIUM] APG Keyboard Interaction Models for Composite Widgets
Custom ARIA widgets implement the W3C APG keyboard model for their pattern — keyboard support is author work, ARIA alone adds none.
- **Detect:** Composite widgets (tabs, menu, listbox, combobox, grid, tree) built with ARIA roles but missing the pattern's keyboard model — arrow-key navigation *within* the widget, Tab moving *past* it as one stop (roving tabindex or `aria-activedescendant`); every option/item left individually tabbable; Home/End/Escape handlers absent where the APG pattern names them.
- **Fix:** Implement the matching APG pattern's keyboard table; one Tab stop per composite widget, arrows navigate inside. Prefer native elements where they exist. (APG conformance is not itself a WCAG requirement — it is the accepted implementation standard for 2.1.1 Keyboard.)
- **Impact:** An ARIA widget without its keyboard model is worse than plain HTML — it announces capabilities keyboard users cannot use.
- **Source:** [W3C APG — Keyboard Interface](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/) (2×-confirmed 2026-07-17)

### AXE-22 [MEDIUM] Accessible-Name Computation Correctness
Names resolve by strict precedence: `aria-labelledby` > `aria-label` > native HTML labeling > `title` — conflicts resolve silently.
- **Detect:** Both `aria-labelledby` and `aria-label` on one element (`aria-label` silently discarded); `aria-label` overriding visible text with different content (breaks voice-control "click X"; SC 2.5.3 Label in Name); icon-only controls with no name source at all; `title` as the only naming mechanism.
- **Fix:** One deliberate naming mechanism per element; visible text included in the accessible name; verify with the browser accessibility tree, not source reading.
- **Impact:** Wrong or discarded names mislabel controls for screen readers and break voice-control targeting — invisible in visual QA.
- **Source:** [W3C APG — Names and Descriptions](https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/); MDN aria-labelledby (2×-confirmed 2026-07-17)

### AXE-23 [MEDIUM] Live-Region Discipline
Dynamic updates announce via at most two stable live regions — polite by default, assertive only for time-critical alerts.
- **Detect:** `aria-live="assertive"` (or `role="alert"`) on routine updates (search-result counts, autosave, chat); live regions injected into the DOM at announce time (unreliable — region must exist before content changes); many scattered live regions; loading/progress updates announcing every increment.
- **Fix:** Two persistent regions max (one polite, one assertive), present from page load; route messages into them; assertive reserved for session-expiry/error-class interruptions; throttle repetitive updates.
- **Impact:** Assertive misuse interrupts screen-reader users mid-task; late-injected regions announce nothing — silent feature loss.
- **Source:** a11y-collective + practitioner consensus on aria-live (2×-confirmed 2026-07-17)
