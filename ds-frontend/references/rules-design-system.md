# Rules: Design System & Theming

Rules for audit/fix/design modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Design Tokens** | TOK-01 to TOK-11 (3 HIGH, 6 MEDIUM, 2 LOW) | ~14 |
| **Theming** | THM-01 to THM-05 (2 HIGH, 2 MEDIUM, 1 LOW) | ~124 |

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
- **Detect:** Search for font-size values not matching project's type scale. Check for random sizes like 13px, 15px, 17px that break scale consistency. Also check readability pairing: body line-height below 1.4 or above 1.8; long-form prose containers with no line-length constraint (lines running past ~75 characters).
  - CSS: font-size values not from CSS variables or type scale
  - Flutter: TextStyle fontSize not from Theme.textTheme
  - SwiftUI: .font() not using standard TextStyle enum or custom scale
  - Compose: fontSize not from MaterialTheme.typography
- **Fix:** Map to nearest type scale level. Minimum body text: 16px (web), 14sp (mobile). Recommended scale ratio: 1.25 (Major Third) for content-heavy, 1.2 (Minor Third) for compact UI. Body line-height 1.4–1.6; constrain prose to 45–75 characters per line (`max-width: 65ch` typical).
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
- **Note:** 2025.10 is the first stable version, but the spec remains a W3C Community Group Report, not a W3C Standard — treat it as the interoperability convention, not a normative requirement.
- **Source:** W3C Design Tokens Community Group Format Module 2025.10

### TOK-08 [LOW] Token Coverage
Unused tokens flagged, untokenized value areas identified.
- **Detect:** Cross-reference defined tokens against usage in component/style files. Tokens defined but never referenced = unused. Hardcoded values in style files = untokenized areas.
- **Fix:** Remove unused tokens. Create tokens for frequently repeated hardcoded values (3+ occurrences).
- **Impact:** Unused tokens bloat token set and confuse consumers. Untokenized values resist theming and centralized updates.
- **Source:** Design system maintenance best practices

### TOK-09 [MEDIUM] Role-Based Spacing Tokens
Every instance of the same structural role (e.g. card header padding, sidebar-panel padding, toolbar-in-a-panel padding) resolves to the *same* named token — not independently to different values that each happen to be on the spacing scale.
- **Detect:** A scale-membership check (TOK-02) can be fully green while this still fails — every value legally on the scale, but conceptually-identical elements (card header vs. sidebar-panel vs. toolbar-in-a-panel) each picked a different scale value with no shared name. Group declarations by selector role (header/body/footer of card-like containers, sidebar/rail panels, toolbar strips) and diff the padding values within each group; 2+ distinct values inside one role group is the signal, even when scale-only checks report zero findings.
- **Fix:** Name one token per role (e.g. `--panel-pad` for spacious chrome, `--panel-pad-compact` for dense sidebar/rail contexts) and repoint every same-role declaration at it. Pure token-naming refactor when existing values already coincide (zero visual diff); only becomes a visual change if the audit also unifies differing values — call that out and get it approved separately from the token-naming step.
- **Impact:** Scale-membership audits create false confidence — "every number is a legal spacing value" reads as "spacing is consistent," but same-role drift is exactly what a reviewer perceives as "no systematic padding," even though no individual rule is broken.
- **Source:** Design system token architecture (role/decision/component tier — see TOK-06); live audit pattern

### TOK-10 [MEDIUM] Palette Hue Distinguishability (non-chart UI)
The primary/secondary/accent and semantic status tokens (success/warning/error/info) are perceptually distinguishable from one another and from neutral/surface tokens — not near-duplicate hues that only differ by a few degrees of hue or a small lightness delta.
- **Detect:** Convert each brand/status token to OKLCH (perceptually uniform — preferred; HSL acceptable when tooling requires) and compute pairwise hue-delta + lightness-delta between tokens meant to signal *different* things (primary vs. secondary vs. accent, and each status color against the others and against primary/secondary). Flag pairs with low separation (e.g. hue delta <15° and lightness delta <10%). Exclude same-role shade pairs (e.g. `primary` vs `primary-hover`) — only compare tokens meant to read as distinct. Chart/series/categorical palette selection is out of scope here — see the `dataviz` skill.
- **Fix:** Adjust hue and/or lightness of the closer token so the pair clears the separation threshold.
- **Impact:** Two semantically distinct tokens (e.g. "info" blue and "primary" blue) that render nearly identically make status indicators, badges, and brand accents visually ambiguous — a user glancing at a colored dot or badge can't reliably tell them apart, and the ambiguity compounds for colorblind users on top of any hue-based distinction that was already marginal.
- **Source:** OKLCH perceptual-distance heuristic (color-theory practice); WCAG 1.4.1 Use of Color (a color-based distinction first requires the colors to be distinguishable)

### TOK-11 [MEDIUM] Z-Index Layer Scale
Stacking order comes from a small set of named layer tokens (e.g. `dropdown < sticky-chrome < modal < popover-above-modal < toast`) — never from ad-hoc literal z-index values.
- **Detect:** Literal `z-index` values not resolving to a token/theme constant; escalation-war values (`999`, `9999`, `2147483647`); more than ~6 distinct literal values across the codebase; two different overlay surfaces at the same literal value relying on DOM order to win.
- **Fix:** Define 5–6 named layer tokens covering the app's real stacking tiers; map every `z-index` declaration to one; the shared overlay primitive (CMP-09) consumes the top layers so a popover opened from inside a modal always renders above it.
- **Impact:** Ad-hoc z-index is the classic symptom of a missing layering architecture — each "just make it 9999" fix silently breaks a different surface, and the true stacking order becomes unknowable from reading any single file. A token scale makes stacking deterministic and reviewable.
- **Source:** CSS stacking-context practice; see CMP-09 (overlay layer contract)

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
- **Source:** MDN prefers-color-scheme, platform accessibility guidelines

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
