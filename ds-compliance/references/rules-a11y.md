# Rules: Accessibility (WCAG 2.2 AA)

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Accessibility** | A11Y-01–08 (3 CRITICAL, 3 MAJOR, 2 MEDIUM) | ~10 |

---

## Accessibility

### A11Y-01 [CRITICAL] Semantic Labels on Interactive Elements
All interactive elements (buttons, links, inputs, toggles) must have accessible labels.
- **Detect:**
  - HTML/JSX: `<button>`, `<a>`, `<input>` without `aria-label`, `aria-labelledby`, visible text content, or `<label>` association
  - Flutter: `ElevatedButton`, `IconButton`, `GestureDetector` without `semanticsLabel` or `Semantics` wrapper
  - SwiftUI: `Button`, `Toggle` without `.accessibilityLabel`
  - Compose: `IconButton`, `Button` without `contentDescription` or `semantics { contentDescription = ... }`
  - React Native: `TouchableOpacity`, `Pressable` without `accessibilityLabel`
- **Fix:** Add appropriate label attribute for the framework
- **Source:** WCAG 2.2 SC 4.1.2 Name, Role, Value

### A11Y-02 [CRITICAL] Keyboard Navigation
All interactive elements must be reachable and operable via keyboard.
- **Detect:**
  - `onClick` without `onKeyDown`/`onKeyUp` on non-button elements (`<div onClick>`, `<span onClick>`)
  - Missing `tabIndex` on custom interactive elements
  - `tabIndex` > 0 (disrupts natural tab order)
  - CSS `outline: none` or `outline: 0` without alternative focus indicator
- **Fix:** Use semantic HTML (`<button>`, `<a>`), add keyboard handlers, preserve focus indicators
- **Source:** WCAG 2.2 SC 2.1.1 Keyboard

### A11Y-03 [CRITICAL] Color Contrast
Text must meet minimum contrast ratios against background.
- **Detect:**
  - Hardcoded color values with insufficient contrast (text <4.5:1, large text <3:1)
  - Grey text on white: `color: #999` or lighter on `#fff` background
  - Placeholder text with insufficient contrast
- **Fix:** Adjust colors to meet WCAG AA ratios (4.5:1 normal text, 3:1 large text/UI components)
- **Source:** WCAG 2.2 SC 1.4.3 Contrast (Minimum)

### A11Y-04 [MAJOR] Image Alt Text
All meaningful images must have alt text. Decorative images must be marked as such.
- **Detect:**
  - `<img>` without `alt` attribute
  - `<img alt="">` on non-decorative images (images with information content)
  - Flutter `Image` without `semanticLabel`
  - React Native `Image` without `accessibilityLabel`
- **Fix:** Add descriptive `alt` text or mark as decorative (`alt=""`, `role="presentation"`)
- **Source:** WCAG 2.2 SC 1.1.1 Non-text Content

### A11Y-05 [MAJOR] Form Error Identification
Error messages must be programmatically associated with their form fields.
- **Detect:**
  - Form validation errors displayed without `aria-describedby` or `aria-errormessage` association
  - Error text rendered without `role="alert"` or `aria-live="polite"`
  - Required fields without `aria-required="true"` or `required` attribute
- **Fix:** Associate errors with fields via `aria-describedby`, announce errors with live regions
- **Source:** WCAG 2.2 SC 3.3.1 Error Identification

### A11Y-06 [MAJOR] Heading Hierarchy
Page headings must follow a logical hierarchy (no skipped levels).
- **Detect:**
  - `<h1>` followed by `<h3>` (skipping `<h2>`)
  - Multiple `<h1>` elements per page
  - No `<h1>` on the page
- **Fix:** Restructure headings to follow sequential hierarchy
- **Source:** WCAG 2.2 SC 1.3.1 Info and Relationships

### A11Y-07 [MEDIUM] Focus Management
Focus must be managed during dynamic content changes (modals, route changes).
- **Detect:**
  - Modal/dialog without focus trap
  - Route change without focus reset to main content
  - Dynamic content insertion without `aria-live` announcement
- **Fix:** Implement focus trap for modals, reset focus on navigation, use `aria-live` for updates
- **Source:** WCAG 2.2 SC 2.4.3 Focus Order

### A11Y-08 [MEDIUM] Touch Target Size
Interactive elements must meet minimum touch target size.
- **Detect:**
  - Buttons/links with `width` or `height` < 44px (iOS) or < 48dp (Android)
  - Flutter: `SizedBox` wrapping tappable with dimensions < 48
  - Inline links without adequate spacing
- **Fix:** Ensure minimum 44x44px (iOS) / 48x48dp (Android) / 24x24px (WCAG 2.2 AA) target size
- **Source:** WCAG 2.2 SC 2.5.8 Target Size (Minimum)
