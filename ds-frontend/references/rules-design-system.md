# Rules: Design System & Theming

Rules for audit/fix/design modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Design Tokens** | TOK-01 to TOK-08 (3 HIGH, 3 MEDIUM, 2 LOW) | ~12 |
| **Theming** | THM-01 to THM-05 (2 HIGH, 2 MEDIUM, 1 LOW) | ~105 |

---

## Design Tokens

### TOK-01 [HIGH] Semantic Color Tokens
All colors referenced via semantic tokens, not hardcoded hex/rgb/hsl values.
- **Detect:** Search style files for color patterns (#hex, rgb(), hsl(), named colors) not wrapped in token references. Exclude: comments, test files, generated files, vendor directories.
  - CSS/SCSS: color values not using `var(--*)` or theme function
  - Flutter: Color(0x...) or Colors.* not from ThemeData/ColorScheme
  - SwiftUI: Color(red:green:blue:) not from asset catalog or extension
  - Compose: Color(0x...) not from MaterialTheme.colorScheme
  - React/Vue: inline style colors not from theme context/tokens
- **Fix:** Map each hardcoded color to nearest semantic token. Create token if no semantic match exists. Prefer semantic names (color.surface, color.error) over palette names (color.red-500).
- **Impact:** Hardcoded colors break theming (dark mode, brand changes), create visual inconsistency, and multiply maintenance cost.
- **Source:** W3C Design Tokens Community Group 2025.10, Material Design 3 Color System

### TOK-02 [HIGH] Spacing Scale
Consistent spacing scale (4/8/12/16/24/32/48/64), no arbitrary pixel values for padding/margin/gap.
- **Detect:** Search for padding/margin/gap values not in project's spacing scale. Common scales: 4px-based (4/8/12/16/20/24/32/48/64) or 8px-based (8/16/24/32/48/64).
  - CSS: padding/margin/gap with px values not in scale
  - Flutter: EdgeInsets/SizedBox with non-scale values
  - SwiftUI: .padding() with non-scale values
  - Compose: Modifier.padding() with non-scale dp values
- **Fix:** Round to nearest scale value. No defined scale → recommend 4px-based scale as starting point.
- **Impact:** Inconsistent spacing → visual noise, slows design iteration, and makes responsive behavior unpredictable.
- **Source:** Material Design Spacing, Apple HIG Layout Margins

### TOK-03 [HIGH] Typography Scale
Defined type scale with consistent ratio (1.2-1.5), no ad-hoc font sizes outside scale.
- **Detect:** Search for font-size values not matching project's type scale. Check for random sizes like 13px, 15px, 17px that break scale consistency.
  - CSS: font-size values not from CSS variables or type scale
  - Flutter: TextStyle fontSize not from Theme.textTheme
  - SwiftUI: .font() not using standard TextStyle enum or custom scale
  - Compose: fontSize not from MaterialTheme.typography
- **Fix:** Map to nearest type scale level. Minimum body text: 16px (web), 14sp (mobile). Recommended scale ratio: 1.25 (Major Third) for content-heavy, 1.2 (Minor Third) for compact UI.
- **Impact:** Random font sizes break visual hierarchy and readability. Users scan before reading -- broken hierarchy increases bounce rate.
- **Source:** Material Design Typography, Modular Scale theory

### TOK-04 [MEDIUM] Shadow Elevation System
Layered shadow tokens (sm/md/lg/xl) instead of arbitrary box-shadow values.
- **Detect:** Search for box-shadow/elevation values not using tokens. Multiple different shadow values across components.
- **Fix:** Define 4-5 elevation levels. Map existing shadows to nearest level. Each level = progressively larger offset + blur + lighter color.
- **Impact:** Arbitrary shadows → inconsistent depth perception and make theming difficult.
- **Source:** Material Design Elevation, Apple HIG Depth

### TOK-05 [MEDIUM] Border Radius Consistency
Radius tokens (sm/md/lg/full) instead of random values across components.
- **Detect:** Search for border-radius values. Count unique values -- more than 4-5 distinct radii indicates inconsistency.
- **Fix:** Define radius scale (e.g., 4/8/12/16/9999 for full). Map existing values to nearest token.
- **Impact:** Inconsistent radii create visual discord and suggest multiple design languages in one product.
- **Source:** Design system best practices

### TOK-06 [MEDIUM] Token Naming Convention
Semantic names (color.surface.primary) over descriptive (color.blue-500). Three-tier naming: option, decision, component.
- **Detect:** Token names using color names (blue, red, green) instead of semantic purpose (primary, error, surface). Missing tier structure.
- **Fix:** Rename tokens following 3-tier pattern:
  - **Option tier:** Raw palette values (blue-500, gray-100) -- internal only, not used in components
  - **Decision tier:** Semantic assignments (color.primary maps to blue-500, color.error maps to red-600) -- used in components
  - **Component tier:** Component-specific overrides (button.primary.bg maps to color.primary) -- optional, for complex systems
- **Impact:** Semantic naming → theming (dark mode swaps decision tier, not component code), improves discoverability for both humans and AI agents.
- **Source:** Martin Fowler -- Design Token-Based UI Architecture, Nathan Curtis -- Naming Tokens

### TOK-07 [LOW] W3C DTCG Format
Design tokens in $value/$type/$description JSON format per W3C 2025.10 specification.
- **Detect:** Search for token definition files. Check if they follow DTCG format with `$value`, `$type`, `$description` properties.
- **Fix:** Convert existing token files to DTCG format. Use Style Dictionary v4+ for transformation pipeline.
  Example:
  ```json
  {
    "color": {
      "primary": {
        "$value": "#0066CC",
        "$type": "color",
        "$description": "Primary brand color -- buttons, links, active states"
      }
    }
  }
  ```
- **Impact:** Standard format → tooling interoperability, automated token pipelines, and cross-platform synchronization.
- **Source:** W3C Design Tokens Community Group Format Module 2025.10

### TOK-08 [LOW] Token Coverage
Unused tokens flagged, untokenized value areas identified.
- **Detect:** Cross-reference defined tokens against usage in component/style files. Tokens defined but never referenced = unused. Hardcoded values in style files = untokenized areas.
- **Fix:** Remove unused tokens. Create tokens for frequently repeated hardcoded values (3+ occurrences).
- **Impact:** Unused tokens bloat token set and confuse consumers. Untokenized values resist theming and centralized updates.
- **Source:** Design system maintenance best practices

---

## Theming

### THM-01 [HIGH] Dark Mode Support
All screens render correctly in both light and dark themes. No hardcoded light-only values.
- **Detect:** Search for color values using light-only tokens without dark equivalents. Check for white/light backgrounds without dark theme alternative.
  - CSS: colors not using `light-dark()` or `prefers-color-scheme` media query
  - Flutter: hardcoded Colors.white without Theme.of(context).colorScheme equivalent
  - SwiftUI: Color.white without .background modifier using semantic color
  - Compose: Color.White without MaterialTheme.colorScheme equivalent
- **Fix:** Replace all hardcoded light values with semantic tokens that have both light and dark values defined.
- **Impact:** 82% of smartphone users use dark mode (Android Authority 2024). Missing dark mode = poor UX for majority.
- **Source:** Material Design Dark Theme, Apple HIG Dark Mode

### THM-02 [HIGH] Color Scheme Declaration
Platform-appropriate color scheme declaration at app root.
- **Detect:**
  - CSS: missing `color-scheme: light dark` on `:root` or `html`
  - Flutter: missing `ThemeData` with both `brightness` values or `themeMode`
  - SwiftUI: missing `preferredColorScheme` or Color asset variants
  - Compose: missing `isSystemInDarkTheme()` check in theme composition
- **Fix:** Add color scheme declaration at app root level. CSS: use `light-dark()` function (baseline May 2024) for automatic color adaptation without JavaScript.
- **Impact:** Without root-level declaration, browsers and OS cannot apply native dark mode behaviors (scrollbar theming, form control styling).
- **Source:** MDN light-dark() CSS function, platform theme guides

### THM-03 [MEDIUM] System Preference Respect
Honor user's OS-level theme preference by default.
- **Detect:** App forces a specific theme without checking system preference. Missing `prefers-color-scheme` (web), missing system theme detection (mobile).
- **Fix:** Default to system preference. Provide manual override toggle. Persist user's manual choice.
- **Impact:** Overriding system preference frustrates users who have chosen preferred mode for comfort or accessibility reasons.
- **Source:** WCAG 2.1 1.4.1, platform accessibility guidelines

### THM-04 [MEDIUM] Dark Mode Contrast
Dark theme maintains same WCAG contrast ratios as light theme.
- **Detect:** Calculate contrast ratios for all text/background pairs in dark mode. Flag any pair below 4.5:1 (normal text) or 3:1 (large text).
- **Fix:** Adjust dark theme color values to meet contrast requirements. Dark mode surfaces: use gray-900 (#1a1a1a) not pure black (#000000) for reduced eye strain.
- **Impact:** Dark themes frequently introduce contrast violations because designers test light mode first. Users with low vision disproportionately affected.
- **Source:** WCAG 2.2 1.4.3, Material Design Dark Theme contrast guidelines

### THM-05 [LOW] Image Dark Mode Adaptation
Images adjusted for dark backgrounds to prevent harsh contrast.
- **Detect:** Images with white/light backgrounds displayed on dark theme surfaces without adaptation.
- **Fix:** Apply filter (brightness 0.8-0.9, or invert for icons) in dark mode. Provide alternate dark-mode image assets for key visuals. SVG icons: use currentColor for automatic theme adaptation.
- **Impact:** Bright images on dark backgrounds → visual shock and discomfort, especially in low-light environments.
- **Source:** Apple HIG Images in Dark Mode
