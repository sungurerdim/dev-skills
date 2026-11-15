# Rules: Mobile — UX & Visual Design

## User Experience

### MUX-01 [HIGH] Bottom Navigation 3-5 Items
- **Detect:** Bottom navigation/tab bar with >5 or <3 items. Icon-only without labels. No active state differentiation
- **Fix:** 3-5 destinations with icon+label. Active state visually distinct (filled icon + tint). Use drawer/more for 5+ destinations
- **Impact:** More than 5 destinations forces icon-only or cramped labels that users can't parse at a glance, and fewer than 3 wastes the pattern entirely — both push users to the wrong tab repeatedly.
- **Source:** Nielsen Norman Group, Material 3

### MUX-07 [HIGH] Correct Keyboard Types
Input fields trigger appropriate keyboard.
- **Detect:** Generic text keyboard for email/phone/number/URL fields. No Done button on numeric keyboard
- **Fix:** Set keyboardType per field: email, phone, number, url, decimal. Add input accessory for numeric Done button
- **Impact:** A generic keyboard on a numeric or email field adds friction to every single entry — small per-field, compounding across a form.
- **Source:** Baymard Institute

### MUX-08 [HIGH] Gesture Discoverability
Custom gestures have visual affordances. Alternative tap-based action always available.
- **Detect:** Swipe actions without visual hint. Long-press without tooltip. Custom gesture with no affordance
- **Fix:** Drag handles, swipe hint animations, contextual tooltips on first encounter. Always provide alternative tap action
- **Impact:** A custom gesture with no visual hint and no tap alternative is invisible to users who don't already know it exists — the feature functions as if it isn't there.
- **Source:** Material Design

### MUX-09 [HIGH] Animation Duration 200-500ms
State transition animations between 200-500ms. Must respect reduced motion.
- **Detect:** Animations >500ms or <150ms. No reduced motion check. Decorative animations without purpose
- **Fix:** 200-500ms for transitions. Check reduced motion setting. Replace scale/pan with opacity for reduced motion users
- **Impact:** Animations outside 200-500ms read as either sluggish (too slow) or jarring (too fast), and ignoring reduced-motion settings can trigger real discomfort for vestibular-disorder users.
- **Source:** Interaction Design Foundation

### MUX-10 [HIGH] Search Bar at Top
Prominent search with suggestions, recents, voice icon, no-results state.
- **Detect:** Search hidden in menu/drawer. No recent searches. No suggestions. Missing no-results state
- **Fix:** Search bar at top of screen. Real-time suggestions. Recent searches. Voice icon. Helpful no-results with alternatives
- **Impact:** Search buried in a menu goes unused even when it's the fastest path to content, because users don't look for what they can't see.
- **Source:** Nielsen Norman Group — Mobile Search Patterns, Material 3 Search Component

### MUX-12 [HIGH] Permission Priming
Pre-permission screen explaining WHY before system prompt.
- **Detect:** System permission dialog without preceding context screen. Permission request unrelated to current action
- **Fix:** Custom priming UI: explain benefit → user taps Continue → system prompt. Denied → degrade gracefully + settings redirect
- **Impact:** 28% higher grant rate
- **Source:** Nielsen Norman Group — Permission Priming, Android Runtime Permissions Guide, Apple Pre-Alert Patterns

### MUX-13 [HIGH] Infinite Scroll + Lazy Load
Infinite scroll for mobile lists. Lazy load images.
- **Detect:** Pagination with page numbers. Loading entire list at once. No image lazy loading
- **Fix:** Infinite scroll with lazy loading. Progressive image loading (placeholder → thumbnail → full). Pull-to-refresh
- **Impact:** Numbered pagination on mobile adds a tap-and-wait cycle to browsing that infinite scroll eliminates, and loading full images up front spikes initial load time.
- **Source:** Smashing Magazine

### MUX-14 [HIGH] Keyboard Avoidance
Content scrolls when keyboard appears. Fields not covered.
- **Detect:** Input fields hidden behind keyboard. No scroll adjustment. Fixed elements overlapping keyboard
- **Fix:** Scroll viewport to active field. Platform keyboard avoidance: iOS KeyboardAvoidingView, Android adjustResize, Flutter Scaffold resizeToAvoidBottomInset
- **Impact:** A field hidden behind the keyboard is a field the user cannot fill in without first discovering they need to scroll manually.
- **Source:** Apple HIG — Keyboard Management, Android Input Method Guide, Flutter Scaffold.resizeToAvoidBottomInset

### MUX-16 [LOW] Grouped Settings
Categories for 15+ settings. Toggles for immediate-effect only. Destructive actions at bottom.
- **Detect:** Flat settings list 15+ items. Toggles for irreversible actions. Delete/logout at top
- **Fix:** Category headers. Toggles only for immediate, reversible changes. Destructive actions at bottom with confirmation
- **Impact:** An unsorted flat list of 15+ settings makes a specific option something users must scan for every time instead of finding by category.
- **Source:** Android Settings Guidelines

### MUX-17 [LOW] Haptic Feedback
Tactile feedback for critical actions.
- **Detect:** No haptics on save/delete/purchase/toggle. Haptics on every tap (overuse)
- **Fix:** Light for selections. Medium for confirmations. Heavy for destructive. Co-design with visual+audio. Optimal keyclick 10-20ms
- **Impact:** No haptic feedback on save/delete/purchase leaves the user uncertain the tap registered; haptics on every tap desensitize the signal for when it matters.
- **Source:** Apple HIG, Android Haptics Design

### MUX-18 [HIGH] In-App Review Timing
After positive experience. Frequency capped.
- **Detect:** Review prompt on first launch. No frequency cap. Prompt after error
- **Fix:** Trigger after successful task. Cap 3x/year. Use platform API (SKStoreReviewController / ReviewManager)
- **Impact:** Prompting for a review right after a bad experience (or an uncapped number of times) collects negative reviews and trains users to dismiss the prompt on sight.
- **Source:** Apple App Store Review Guidelines (Section 1.1.7), Google Play In-App Review API

### MUX-20 [HIGH] Pull-to-Refresh
Scrollable content screens support pull-to-refresh gesture.
- **Detect:** Scrollable lists without `RefreshIndicator` (Flutter), `UIRefreshControl` (iOS), `SwipeRefresh` (Android), `RefreshControl` (RN). No manual refresh mechanism
- **Fix:** Add platform-native pull-to-refresh. Show last-updated timestamp. Disable during active refresh
- **Impact:** Expected mobile convention — absence feels broken to users
- **Source:** Material Design, Apple HIG

### MUX-21 [HIGH] Consistent Back Navigation
Back button and swipe-back behave predictably across all screens.
- **Detect:** Inconsistent back behavior: some screens pop, others reset stack. Swipe-back disabled without reason. Data loss on back without confirmation
- **Fix:** Consistent back stack behavior. Enable swipe-back (iOS) and predictive back (Android 14+). Confirm before discarding unsaved data
- **Impact:** Unpredictable back navigation → data loss and user frustration
- **Source:** Android Predictive Back, Apple HIG Navigation

### MUX-23 [LOW] Scroll Position Preservation
Scroll position restored after navigation, tab switch, or orientation change.
- **Detect:** Scroll resets to top on tab switch or back navigation. No scroll state persistence. List position lost on orientation change
- **Fix:** Save scroll offset in ViewModel/state. Restore on return. Use `PageStorageKey` (Flutter), `SavedStateHandle` (Android), state restoration (iOS)
- **Impact:** Losing scroll position forces users to re-find their place in long lists
- **Source:** Android SavedStateHandle, iOS State Restoration Guide, Flutter PageStorageKey

### MUX-25 [CRITICAL] Destructive Action Safeguards
Irreversible actions require confirmation or offer undo.
- **Detect:** Delete/remove actions without confirmation dialog. No undo mechanism for destructive operations. Single-tap account deletion or data wipe
- **Fix:** Confirmation dialog for destructive actions with clear consequence description. Prefer undo (snackbar with "Undo" for 5-8s) over confirmation where possible. Require text input confirmation for high-impact actions (e.g., type "DELETE" to confirm)
- **Impact:** Irreversible data loss with no recovery path. Legal risk under GDPR Article 17
- **Source:** Nielsen Norman Group, Material Design Confirmation Patterns

### MUX-27 [HIGH] Privacy Trust Indicators
Apps handling sensitive data must show visible trust indicators on relevant screens.
- **Detect:** App handles sensitive data (auth, health, finance, encrypted storage, PII) but shows no visual trust indicators on relevant screens. No encryption/security status near sensitive operations. No data handling disclosure before permission prompts
- **Fix:** Add contextual trust indicators: encryption badge on auth/data-entry screens. Data handling micro-text near sensitive operations (e.g., "Processed in memory only", "End-to-end encrypted"). Privacy transparency panel in settings showing what data is collected. Just-in-time disclosure before permission prompts (increases opt-in 12-19%)
- **Conditional:** Only for apps with privacy/security/health/finance focus — detect via manifest permissions, API patterns, or compliance docs
- **Impact:** Users handling sensitive data with no visible trust signal have no way to distinguish a careful implementation from a careless one, and will assume the worse of the two by default.
- **Source:** Nielsen Norman Group — Trust in UX Design, Signal/Ente/Bitwarden Privacy UX Patterns

## Visual Design

### VIS-01 [HIGH] Dynamic Type / Font Scaling
Support system font scaling. iOS: Dynamic Type. Android: sp (never dp for text).
- **Detect:**
  - Android: text sized in `dp` instead of `sp`
  - iOS: fixed font sizes ignoring Dynamic Type
  - Flutter: not using `MediaQuery.textScalerOf(context)` (current API — `textScaleFactor` is deprecated) or TextTheme
  - Text truncated at 200% scale
- **Fix:**
  - iOS: UIFontMetrics, Dynamic Type categories
  - Android: sp units for all text
  - Flutter: Theme.of(context).textTheme, test at 200% scale
  - **Interim safety (all platforms):** While building full WCAG 1.4.4 200% support, clamp text scaling to 0.8–1.3× range via platform text scale API to prevent layout breakage. Document cap and plan its removal:
    - Flutter: `MediaQuery.textScaler.clamp(minScaleFactor: 0.8, maxScaleFactor: 1.3)` in `MaterialApp.builder`
    - iOS: `adjustsFontForContentSizeCategory` with maximum category limit
    - Android: `Configuration.fontScale` bounded in Application subclass
    - RN: `Text.defaultProps.maxFontSizeMultiplier = 1.3`
    - Web: `clamp(0.8rem, 1em, 1.3rem)` in CSS font-size
  - **Target:** Remove cap once all screens pass layout test at 200% scale
- **Impact:** Text that doesn't scale with the system font setting is unreadable for the users who rely on that setting most — low-vision users who set 150-200% scaling.
- **Source:** WCAG 1.4.4, Apple HIG, Material 3

### VIS-02 [HIGH] Minimum Text Size
Body >= 16sp/17pt. Never below 11sp/12pt for any text.
- **Detect:** Body text < 16sp. Any text < 11sp. Captions unreadable
- **Fix:** Material 3 scale: Display 57-36, Headline 32-24, Title 22-16, Body 16-14, Label 14-11
- **Impact:** Text below 11sp/12pt is unreadable at arm's length for a large share of users regardless of accessibility settings, not just an edge-case population.
- **Source:** Material 3 Typography Scale, Apple Dynamic Type Sizes, WCAG 1.4.4

### VIS-05 [LOW] Dark Gray Over Pure Black
#121212 for surfaces. Pure black (#000000) → OLED smearing.
- **Detect:** `#000000` or `Color(0xFF000000)` as dark mode background
- **Fix:** #121212 or equivalent dark gray. Pure black only for decorative or user-requested high-contrast
- **Impact:** Pure black on OLED panels causes visible smearing during scroll and motion, a display artifact users notice even without knowing the cause.
- **Source:** Material Design Dark Theme Guide, OLED Display Smearing Research

### VIS-06 [HIGH] 8dp Grid Spacing
All spacing in multiples of 8. Internal <= external.
- **Detect:** Arbitrary spacing (7, 13, 22). Inconsistent padding. Internal spacing > external
- **Fix:** 8dp multiples: 8, 16, 24, 32, 40, 48. Allow 4dp for compact. Internal <= external
- **Impact:** Arbitrary spacing values compound into a visibly inconsistent layout as the app grows past a handful of screens, each one built to a slightly different rhythm.
- **Source:** Material 3, 8-point grid

### VIS-07 [HIGH] Platform Icons
SF Symbols (iOS), Material Icons (Android). Accessibility labels on all icons.
- **Detect:** Custom icons where platform icons exist. Inconsistent sizes. Icons without a11y labels
- **Fix:** SF Symbols (6900+, 9 weights, 3 scales). Material Icons (dp-based). Always label for screen readers
- **Impact:** Custom icons where a platform icon exists break the visual vocabulary users already know from every other app on their device, adding a recognition tax to every screen.
- **Source:** Apple SF Symbols, Material Icons

### VIS-08 [HIGH] Safe Area Handling
Respect notch, Dynamic Island (44-58px), punch-hole, system bars.
- **Detect:** Content behind system bars. Interactive elements under notch/Dynamic Island. No safe area padding
- **Fix:**
  - iOS: SafeAreaLayoutGuide, safeAreaPadding (iOS 17+)
  - Android: WindowInsetsCompat, edge-to-edge with inset handling
  - Flutter: SafeArea widget
  - Min 16-24pt edge distance
- **Impact:** Interactive elements placed under the notch, Dynamic Island, or system bars are literally untappable on the affected device class.
- **Source:** Apple HIG, Android 15 edge-to-edge

### VIS-09 [HIGH] Adaptive Layout
Phone, tablet, foldable support via window size classes.
- **Detect:** Fixed layouts breaking on tablet/foldable. Single column on large screens
- **Fix:** Compact (<600dp), Medium (600-840dp), Expanded (840dp+). Canonical layouts: list-detail, feed, supporting panel
- **Test matrix (covers 99%+ of devices):**

  | Profile | Width | Class | Notes |
  |---------|-------|-------|-------|
  | Ultra-narrow | 240dp | Narrow | Extreme edge case (small wearable) |
  | Small phone | 320dp | Compact | iPhone SE, low-end Android |
  | Standard phone | 375dp | Compact | Most common phone baseline |
  | Large phone | 412dp | Compact | Most common Android (Pixel) |
  | Phablet | 428dp | Compact | Upper phone bound |
  | Small tablet | 744dp | Medium | iPad Mini, Android tablet |
  | Large tablet | 1024dp | Expanded | iPad Pro, desktop window |

  Also test: landscape orientation, font scale 1.3×, dark mode, RTL layout (if i18n supported)
- **Impact:** A fixed phone layout on tablet or foldable either wastes most of the screen or clips content — both read as an unfinished, unmaintained app on that device class.
- **Source:** Material 3 Adaptive Design

### VIS-12 [LOW] Bottom Sheet Drag Handle
Handle visible, >= 48dp wide. Snap points defined.
- **Detect:** Bottom sheet without handle. Handle < 48dp. No snap points
- **Fix:** Visible handle >= 48dp. Snap points: peek, half, full. Handle keyboard interaction
- **Impact:** A bottom sheet with no visible or undersized drag handle leaves users unsure the sheet is draggable at all.
- **Source:** Material 3

### VIS-13 [LOW] Launch Screen Transition
Smooth splash-to-content transition. No blank flash.
- **Detect:** Blank/white flash between splash and content. Splash > 2s. No transition
- **Fix:** Platform splash API (Android 12+ SplashScreen, iOS launch storyboard). Fast transition to first content
- **Impact:** A blank flash between splash and content reads as a stutter or crash-and-recover, even though nothing actually failed.
- **Source:** Android 12 SplashScreen API, Apple Launch Storyboard Guide, Flutter Native Splash

### VIS-14 [HIGH] Adaptive Icons (Android)
Foreground + background layers. 66dp safe zone.
- **Detect:** Non-adaptive icon. Content outside safe zone. Single-layer icon
- **Fix:** 108x108dp with 66dp safe zone. Vector preferred. Separate foreground/background
- **Impact:** A non-adaptive icon renders with the wrong shape or clipped content across the different mask shapes Android launchers apply, looking broken on a portion of the Android install base.
- **Source:** Android Adaptive Icons

### VIS-15 [HIGH] Color Palette Limit & Harmony
Maximum 6 distinct hues in app. All colors from theme tokens.
- **Detect:** >6 distinct hue values across app. Random hex values outside theme definition. Colors not from `ColorScheme` / theme tokens
- **Fix:** Define palette of max 6 hues (primary, secondary, tertiary, neutral, error, + 1 accent). All UI colors reference theme tokens. No arbitrary hex in widget code
- **Impact:** Uncontrolled color use → visual noise and undermines brand identity
- **Source:** Material 3 Color System, Color Theory

### VIS-17 [HIGH] Semantic Color Correctness
Colors match semantic meaning. No misleading color usage.
- **Detect:** Green used for errors or warnings. Red used for success states. Blue used for destructive actions. Inconsistent semantic color assignment across screens
- **Fix:** Error = red/orange. Success = green. Warning = amber/yellow. Info = blue. Destructive = red. Define semantic tokens and enforce globally
- **Impact:** Wrong semantic colors confuse users and increase error rates
- **Source:** Color Psychology in UI, Material 3 Color Roles

### VIS-18 [HIGH] Visual Hierarchy
Clear primary/secondary/tertiary action distinction per screen.
- **Detect:** Multiple filled/elevated buttons on same screen competing for attention. No clear primary CTA. All text same size/weight. No visual grouping of related elements
- **Fix:** One primary (filled) button per screen. Secondary actions as outlined/tonal. Tertiary as text buttons. Size and weight establish information hierarchy
- **Impact:** Without visual hierarchy, users don't know where to look or what to do first
- **Source:** Gestalt Principles, Material 3 Button Hierarchy

### VIS-19 [LOW] Consistent Elevation & Shadow
Shadow values follow design system tokens. No arbitrary elevation.
- **Detect:** Arbitrary `elevation` / `boxShadow` values not from theme. Mixed shadow styles on same screen. Inconsistent elevation levels across similar components
- **Fix:** Define elevation scale (e.g., 0, 1, 2, 3, 4, 5). Map to component types: 0=flat, 1=card, 2=appbar, 3=FAB, 4=dialog, 5=drawer. Use theme elevation tokens only
- **Impact:** Inconsistent shadows → visual clutter and break spatial metaphor
- **Source:** Material 3 Elevation System

### VIS-20 [HIGH] Card Design Consistency
All cards on a screen share same radius, padding, and elevation.
- **Detect:** Cards with different border radius on same screen. Inconsistent internal padding across cards. Mixed card styles (outlined vs elevated) without clear purpose
- **Fix:** Define card variants (elevated, filled, outlined) with fixed radius, padding, and elevation. Use one variant per context. Internal padding consistent across all cards
- **Impact:** Inconsistent cards → unpolished UI and reduced scannability
- **Source:** Material 3 Card Component

### VIS-21 [HIGH] Button Style Hierarchy
Distinct button styles for primary, secondary, and tertiary actions.
- **Detect:** All buttons using same style (all filled or all outlined). No visual distinction between primary and secondary actions. Destructive actions styled like normal actions
- **Fix:** Primary: filled. Secondary: outlined or tonal. Tertiary: text button. Destructive: red/outlined-red. Disabled: reduced opacity. Consistent across all screens
- **Impact:** Uniform button styling removes action priority — users can't distinguish important from trivial
- **Source:** Material 3 Button Styles, Apple HIG Buttons

### VIS-22 [LOW] Image Aspect Ratio Consistency
Images maintain correct aspect ratio. No distortion.
- **Detect:** Images with `fit: BoxFit.fill` (Flutter), `resizeMode: 'stretch'` (RN), `contentMode: .scaleToFill` (iOS) → distortion. Mixed aspect ratios in grid/list layouts
- **Fix:** Use `BoxFit.cover` or `BoxFit.contain`. Consistent aspect ratios in lists (e.g., all 16:9 or all 1:1). Placeholder for loading. Error image for failures
- **Impact:** Distorted images look unprofessional and damage trust
- **Source:** Material Design Imagery, Apple HIG Images

### VIS-23 [HIGH] Icon Style Consistency
Single icon family throughout app. Consistent sizing.
- **Detect:** Mixed icon families (Material + Cupertino + custom). Inconsistent icon sizes (20dp, 24dp, 28dp in same context). Outlined and filled icons mixed without purpose
- **Fix:** Choose one icon family per platform. Standard sizes: 16dp (inline), 24dp (actions), 40dp+ (features). Filled for selected states, outlined for unselected. Custom icons match family weight/style
- **Impact:** Mixed icon styles → visual inconsistency, feels like multiple apps stitched together
- **Source:** Material Icons Guide, SF Symbols Guidelines

### VIS-24 [HIGH] Interactive State Visibility
All interactive elements show pressed, disabled, focused, and loading states.
- **Detect:** Buttons without pressed/disabled visual state. No loading indicator on async buttons. Form fields without focus ring. Switches/checkboxes without state transition
- **Fix:** Define states for every interactive component: default, pressed, focused, disabled, loading, error. Disabled = reduced opacity (38%). Loading = spinner replacing label. Focus = visible ring/outline
- **Impact:** Missing interactive states → UI feels unresponsive and confuses users about what's actionable
- **Source:** Material 3 State Layers, Apple HIG Interactive Elements

### VIS-25 [HIGH] Overflow Prevention Patterns
Constrained layouts must protect against text/content overflow across all viewport sizes.
- **Detect:**
  - Text in constrained horizontal parent (Row/HStack/LinearLayout/flexbox) without overflow protection (maxLines, ellipsis, line clamp)
  - Multiple text elements in horizontal layout without flexible sizing (Flexible/Expanded, flexShrink, layout weight, flex-shrink)
  - Vertical content with spacers/padding but no scroll wrapper — will overflow on small screens or large font
  - Hardcoded pixel widths > 200dp on elements that should be responsive
  - Screen size query triggering unnecessary full-tree rebuilds instead of targeted size reads
- **Fix:**
  - Every horizontal layout with text needs at least one flexible child:
    - Flutter: `Flexible`/`Expanded` + `Text(maxLines, overflow: TextOverflow.ellipsis)`
    - iOS: `compressionResistance` priority + `numberOfLines` + `lineBreakMode`
    - Android: `0dp` with `layout_weight` + `ellipsize`; Compose: `Modifier.weight()` + `maxLines`
    - RN: `flexShrink: 1` + `numberOfLines`
    - Web: `flex-shrink: 1` + `text-overflow: ellipsis` + `overflow: hidden`
  - Content that might exceed viewport height: wrap in scrollable container with min-height constraint
  - Replace hardcoded widths with responsive values (percentage, flex, weight)
  - Use targeted size queries (Flutter: `MediaQuery.sizeOf` not `.of`; Web: container queries not window resize; iOS: trait collections)
- **Impact:** Unprotected text/content overflow clips or overlaps UI unpredictably across device sizes and font-scale settings, the exact combination real users run in and not just the design's reference viewport.
- **Source:** Flutter Layout Overflow Debugging, CSS Overflow Module Level 3, Android ConstraintLayout Guide, Auto Layout Guide (Apple)
