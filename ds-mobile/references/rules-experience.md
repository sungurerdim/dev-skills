# Rules: UX, Visual Design & Accessibility

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **User Experience** | UX-01–27 (1 CRITICAL, 3 CRITICAL, 20 HIGH, 3 LOW) | ~15 |
| **Visual Design** | VIS-01–25 (3 CRITICAL, 17 HIGH, 5 LOW) | ~185 |
| **Accessibility** | A11Y-01–12 (5 CRITICAL, 7 HIGH) | ~370 |

---

## User Experience

### UX-01 [CRITICAL] Bottom Navigation 3-5 Items
- **Detect:** Bottom navigation/tab bar with >5 or <3 items. Icon-only without labels. No active state differentiation
- **Fix:** 3-5 destinations with icon+label. Active state visually distinct (filled icon + tint). Use drawer/more for 5+ destinations
- **Source:** Nielsen Norman Group, Material 3

### UX-02 [HIGH] Skeleton Screens Over Spinners
Use skeleton/shimmer for content loading areas. Spinners only for discrete actions.
- **Detect:** `CircularProgressIndicator`, `ActivityIndicator`, `ProgressView` used for content loading (not submit/save actions)
- **Fix:** Replace with skeleton/shimmer widget matching content layout. 1.5-2s pulse cycles, 300-700ms animation
- **Impact:** 20% faster perceived, 9-20% lower bounce
- **Source:** UX research

### UX-03 [HIGH] Descriptive Loading Text
Loading indicators must include descriptive text.
- **Detect:** Bare progress indicator without context text. Spinner alone without label
- **Fix:** Add descriptive label alongside indicator: "Purchasing...", "Syncing...", "Loading records..."
- **Source:** Material 3, WCAG (screen reader context)

### UX-04 [HIGH] Empty States with CTA
Every empty screen: context + guidance + visual + CTA.
- **Detect:** Blank screens when no data. "No data" text without action. Missing first-use/no-results/error/offline variants
- **Fix:** Empty state widget: icon/illustration + title + subtitle + action button. Four variants: first-use, no-results, error, offline
- **Source:** Nielsen Norman Group

### UX-05 [HIGH] Error Recovery with Retry
Every error state offers concrete next action.
- **Detect:** Error messages without retry/action. Toast for critical errors. Dialog for trivial warnings. "Something went wrong" without guidance
- **Fix:** Inline retry for network errors. Toast (3-8s) for informational. Dialog only for blocking decisions. Clear, actionable error text
- **Source:** Nielsen Norman Group

### UX-06 [HIGH] Form Validation on Blur
Validate on blur/submit, not per-keystroke. Immediate only for critical format blockers.
- **Detect:** Validation firing on every character. Error shown on empty field before user types. No validation at all
- **Fix:** Validate on blur with 500-1000ms delay. Error below field. Format-critical (IBAN, email) validated immediately on invalid input
- **Impact:** 25% higher completion rate
- **Source:** Smashing Magazine

### UX-07 [HIGH] Correct Keyboard Types
Input fields trigger appropriate keyboard.
- **Detect:** Generic text keyboard for email/phone/number/URL fields. No Done button on numeric keyboard
- **Fix:** Set keyboardType per field: email, phone, number, url, decimal. Add input accessory for numeric Done button
- **Source:** Baymard Institute

### UX-08 [HIGH] Gesture Discoverability
Custom gestures have visual affordances. Alternative tap-based action always available.
- **Detect:** Swipe actions without visual hint. Long-press without tooltip. Custom gesture with no affordance
- **Fix:** Drag handles, swipe hint animations, contextual tooltips on first encounter. Always provide alternative tap action
- **Source:** Material Design

### UX-09 [HIGH] Animation Duration 200-500ms
State transition animations between 200-500ms. Must respect reduced motion.
- **Detect:** Animations >500ms or <150ms. No reduced motion check. Decorative animations without purpose
- **Fix:** 200-500ms for transitions. Check reduced motion setting. Replace scale/pan with opacity for reduced motion users
- **Source:** Interaction Design Foundation

### UX-10 [HIGH] Search Bar at Top
Prominent search with suggestions, recents, voice icon, no-results state.
- **Detect:** Search hidden in menu/drawer. No recent searches. No suggestions. Missing no-results state
- **Fix:** Search bar at top of screen. Real-time suggestions. Recent searches. Voice icon. Helpful no-results with alternatives
- **Source:** Mobile search UX

### UX-11 [HIGH] Progressive Onboarding
Value-first. Defer advanced features. Skip always visible.
- **Detect:** Full walkthrough before any interaction. Permission requests on first screen. Information overload at startup
- **Fix:** Value-first screen. Contextual tooltips on user actions. Skip button visible. Permission priming before system prompt
- **Source:** Interaction Design Foundation

### UX-12 [CRITICAL] Permission Priming
Pre-permission screen explaining WHY before system prompt.
- **Detect:** System permission dialog without preceding context screen. Permission request unrelated to current action
- **Fix:** Custom priming UI: explain benefit → user taps Continue → system prompt. If denied: degrade gracefully + settings redirect
- **Impact:** 28% higher grant rate
- **Source:** Nielsen Norman Group, Android permission guidelines

### UX-13 [HIGH] Infinite Scroll + Lazy Load
Infinite scroll for mobile lists. Lazy load images.
- **Detect:** Pagination with page numbers. Loading entire list at once. No image lazy loading
- **Fix:** Infinite scroll with lazy loading. Progressive image loading (placeholder → thumbnail → full). Pull-to-refresh
- **Source:** Smashing Magazine

### UX-14 [HIGH] Keyboard Avoidance
Content scrolls when keyboard appears. Fields not covered.
- **Detect:** Input fields hidden behind keyboard. No scroll adjustment. Fixed elements overlapping keyboard
- **Fix:** Scroll viewport to active field. Platform keyboard avoidance: iOS KeyboardAvoidingView, Android adjustResize, Flutter Scaffold resizeToAvoidBottomInset
- **Source:** Platform guidelines

### UX-15 [HIGH] Optimistic UI Updates
Show expected result immediately. Reconcile asynchronously.
- **Detect:** UI blocked during every server call. Spinner for every tap. List unchanged until API responds
- **Fix:** Update UI on user action. Reconcile with server response. Revert on failure with feedback
- **Source:** Modern UX

### UX-16 [LOW] Grouped Settings
Categories for 15+ settings. Toggles for immediate-effect only. Destructive actions at bottom.
- **Detect:** Flat settings list 15+ items. Toggles for irreversible actions. Delete/logout at top
- **Fix:** Category headers. Toggles only for immediate, reversible changes. Destructive actions at bottom with confirmation
- **Source:** Android Settings Guidelines

### UX-17 [LOW] Haptic Feedback
Tactile feedback for critical actions.
- **Detect:** No haptics on save/delete/purchase/toggle. Haptics on every tap (overuse)
- **Fix:** Light for selections. Medium for confirmations. Heavy for destructive. Co-design with visual+audio. Optimal keyclick 10-20ms
- **Source:** Apple HIG, Android Haptics Design

### UX-18 [HIGH] In-App Review Timing
After positive experience. Frequency capped.
- **Detect:** Review prompt on first launch. No frequency cap. Prompt after error
- **Fix:** Trigger after successful task. Cap 3x/year. Use platform API (SKStoreReviewController / ReviewManager)
- **Source:** Apple/Google review guidelines

### UX-19 [HIGH] Navigation Depth <= 3 Taps
Any core feature reachable within 3 taps from home.
- **Detect:** Navigation chain deeper than 3 levels for primary user flows. Key features buried in nested menus
- **Fix:** Flatten hierarchy. Use bottom nav, tabs, or shortcuts for frequent destinations. Max 3 taps to any core action
- **Impact:** Each extra tap loses ~20% of users (UX research)
- **Source:** Nielsen Norman Group, Mobile Navigation Patterns

### UX-20 [HIGH] Pull-to-Refresh
Scrollable content screens support pull-to-refresh gesture.
- **Detect:** Scrollable lists without `RefreshIndicator` (Flutter), `UIRefreshControl` (iOS), `SwipeRefresh` (Android), `RefreshControl` (RN). No manual refresh mechanism
- **Fix:** Add platform-native pull-to-refresh. Show last-updated timestamp. Disable during active refresh
- **Impact:** Expected mobile convention — absence feels broken to users
- **Source:** Material Design, Apple HIG

### UX-21 [HIGH] Consistent Back Navigation
Back button and swipe-back behave predictably across all screens.
- **Detect:** Inconsistent back behavior: some screens pop, others reset stack. Swipe-back disabled without reason. Data loss on back without confirmation
- **Fix:** Consistent back stack behavior. Enable swipe-back (iOS) and predictive back (Android 14+). Confirm before discarding unsaved data
- **Impact:** Unpredictable back navigation causes data loss and user frustration
- **Source:** Android Predictive Back, Apple HIG Navigation

### UX-22 [HIGH] Immediate Action Feedback
Every tap produces visual feedback within 100ms.
- **Detect:** Tappable elements without ripple/highlight state. Buttons with no pressed state. Actions with no visual response for >100ms
- **Fix:** Add ripple (Material) or highlight (Cupertino) to all interactive elements. Show loading indicator if action takes >300ms. Disable button during processing
- **Impact:** No feedback within 100ms makes users tap again, causing duplicate actions
- **Source:** Jakob Nielsen Response Time Limits

### UX-23 [LOW] Scroll Position Preservation
Scroll position restored after navigation, tab switch, or orientation change.
- **Detect:** Scroll resets to top on tab switch or back navigation. No scroll state persistence. List position lost on orientation change
- **Fix:** Save scroll offset in ViewModel/state. Restore on return. Use `PageStorageKey` (Flutter), `SavedStateHandle` (Android), state restoration (iOS)
- **Impact:** Losing scroll position forces users to re-find their place in long lists
- **Source:** Platform state restoration guidelines

### UX-24 [HIGH] Progressive Disclosure
No screen shows more than 7 primary options or controls at once.
- **Detect:** Screens with >7 buttons/options visible simultaneously. Settings without grouping. Forms showing all fields at once instead of steps
- **Fix:** Group related options. Use expandable sections, tabs, or stepper for complex forms. Show advanced options behind "More" or expand. Primary actions prominent, secondary collapsed
- **Impact:** Hick's Law: decision time increases logarithmically with number of choices
- **Source:** Hick's Law, Nielsen Norman Group

### UX-25 [CRITICAL] Destructive Action Safeguards
Irreversible actions require confirmation or offer undo.
- **Detect:** Delete/remove actions without confirmation dialog. No undo mechanism for destructive operations. Single-tap account deletion or data wipe
- **Fix:** Confirmation dialog for destructive actions with clear consequence description. Prefer undo (snackbar with "Undo" for 5-8s) over confirmation where possible. Require text input confirmation for high-impact actions (e.g., type "DELETE" to confirm)
- **Impact:** Irreversible data loss with no recovery path. Legal risk under GDPR Article 17
- **Source:** Nielsen Norman Group, Material Design Confirmation Patterns

### UX-26 [CRITICAL] Dark Pattern Prevention
No deceptive UI patterns that trick users into unintended actions.
- **Detect:** Pre-checked consent checkboxes. Confirmshaming ("No, I don't want to save money"). Asymmetric button styling (accept prominent, reject hidden). Hidden unsubscribe. Forced continuity without clear cancellation. Misdirection in privacy settings
- **Fix:** Equal visual weight for accept/reject. Unchecked opt-ins by default. Clear, neutral language for all choices. Easy-to-find cancellation. Transparent pricing and renewal terms
- **Impact:** EAA/GDPR fines up to EUR 100K+. App store rejection. User trust destruction
- **Source:** EU Consumer Rights Directive, FTC Dark Patterns Report, EAA 2019/882

### UX-27 [HIGH] Privacy Trust Indicators
Apps handling sensitive data must show visible trust indicators on relevant screens.
- **Detect:** App handles sensitive data (auth, health, finance, encrypted storage, PII) but shows no visual trust indicators on relevant screens. No encryption/security status near sensitive operations. No data handling disclosure before permission prompts
- **Fix:** Add contextual trust indicators: encryption badge on auth/data-entry screens. Data handling micro-text near sensitive operations (e.g., "Processed in memory only", "End-to-end encrypted"). Privacy transparency panel in settings showing what data is collected. Just-in-time disclosure before permission prompts (increases opt-in 12-19%)
- **Conditional:** Only for apps with privacy/security/health/finance focus — detect via manifest permissions, API patterns, or compliance docs
- **Source:** Signal, Ente, Bitwarden UX patterns; NNG Trust Design research

---

## Visual Design

### VIS-01 [CRITICAL] Dynamic Type / Font Scaling
Support system font scaling. iOS: Dynamic Type. Android: sp (never dp for text).
- **Detect:**
  - Android: text sized in `dp` instead of `sp`
  - iOS: fixed font sizes ignoring Dynamic Type
  - Flutter: not using `MediaQuery.textScaleFactor` or TextTheme
  - Text truncated at 200% scale
- **Fix:**
  - iOS: UIFontMetrics, Dynamic Type categories
  - Android: sp units for all text
  - Flutter: Theme.of(context).textTheme, test at 200% scale
  - **Interim safety (all platforms):** While building full WCAG 1.4.4 200% support, clamp text scaling to 0.8–1.3× range via platform text scale API to prevent layout breakage. Document the cap and plan its removal:
    - Flutter: `MediaQuery.textScaler.clamp(minScaleFactor: 0.8, maxScaleFactor: 1.3)` in `MaterialApp.builder`
    - iOS: `adjustsFontForContentSizeCategory` with maximum category limit
    - Android: `Configuration.fontScale` bounded in Application subclass
    - RN: `Text.defaultProps.maxFontSizeMultiplier = 1.3`
    - Web: `clamp(0.8rem, 1em, 1.3rem)` in CSS font-size
  - **Target:** Remove cap once all screens pass layout test at 200% scale
- **Source:** WCAG 1.4.4, Apple HIG, Material 3

### VIS-02 [CRITICAL] Minimum Text Size
Body >= 16sp/17pt. Never below 11sp/12pt for any text.
- **Detect:** Body text < 16sp. Any text < 11sp. Captions unreadable
- **Fix:** Material 3 scale: Display 57-36, Headline 32-24, Title 22-16, Body 16-14, Label 14-11
- **Source:** Typography best practices

### VIS-03 [HIGH] Semantic Color Tokens
Named colors (surface, primary, error), not hardcoded hex.
- **Detect:** Hardcoded `Color(0xFF...)`, `#hex`, `UIColor(red:green:blue:)` outside theme. Colors not adapting to dark mode
- **Fix:** Define via ColorScheme/ThemeData. Tokens: background, surface, onSurface, primary, onPrimary, error, outline, outlineVariant
- **Source:** Material 3, Apple Color

### VIS-04 [HIGH] Dark Mode
Respect system preference. Manual toggle. Test all screens.
- **Detect:** No dark mode. Hardcoded colors not adapting. Images not adapted. No theme toggle
- **Fix:** System-aware theme. Adapt images. Dark gray (#121212) for surfaces. Manual toggle in settings
- **Source:** Material 3, Apple HIG

### VIS-05 [LOW] Dark Gray Over Pure Black
#121212 for surfaces. Pure black (#000000) causes OLED smearing.
- **Detect:** `#000000` or `Color(0xFF000000)` as dark mode background
- **Fix:** #121212 or equivalent dark gray. Pure black only for decorative or user-requested high-contrast
- **Source:** OLED best practices

### VIS-06 [HIGH] 8dp Grid Spacing
All spacing in multiples of 8. Internal <= external.
- **Detect:** Arbitrary spacing (7, 13, 22). Inconsistent padding. Internal spacing > external
- **Fix:** 8dp multiples: 8, 16, 24, 32, 40, 48. Allow 4dp for compact. Internal <= external
- **Source:** Material 3, 8-point grid

### VIS-07 [HIGH] Platform Icons
SF Symbols (iOS), Material Icons (Android). Accessibility labels on all icons.
- **Detect:** Custom icons where platform icons exist. Inconsistent sizes. Icons without a11y labels
- **Fix:** SF Symbols (6900+, 9 weights, 3 scales). Material Icons (dp-based). Always label for screen readers
- **Source:** Apple SF Symbols, Material Icons

### VIS-08 [CRITICAL] Safe Area Handling
Respect notch, Dynamic Island (44-58px), punch-hole, system bars.
- **Detect:** Content behind system bars. Interactive elements under notch/Dynamic Island. No safe area padding
- **Fix:**
  - iOS: SafeAreaLayoutGuide, safeAreaPadding (iOS 17+)
  - Android: WindowInsetsCompat, edge-to-edge with inset handling
  - Flutter: SafeArea widget
  - Min 16-24pt edge distance
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
- **Source:** Material 3 Adaptive Design

### VIS-10 [HIGH] Typography Scale
Follow platform type scale. No ad-hoc sizes.
- **Detect:** Random font sizes outside scale. Mixed families. Inconsistent weights
- **Fix:** Define app type scale once using platform tokens. Material 3: 15 tokens. Apple: Dynamic Type categories
- **Source:** Material 3 Typography

### VIS-11 [HIGH] RTL Layout Support
Mirror layout for RTL languages. start/end not left/right.
- **Detect:** `android:supportsRtl` missing. left/right instead of start/end. Directional icons not mirrored. Layout broken in RTL
- **Fix:** `android:supportsRtl="true"`. Use start/end. Mirror directional icons. Test Arabic/Hebrew
- **Source:** Android i18n, WCAG

### VIS-12 [LOW] Bottom Sheet Drag Handle
Handle visible, >= 48dp wide. Snap points defined.
- **Detect:** Bottom sheet without handle. Handle < 48dp. No snap points
- **Fix:** Visible handle >= 48dp. Snap points: peek, half, full. Handle keyboard interaction
- **Source:** Material 3

### VIS-13 [LOW] Launch Screen Transition
Smooth splash-to-content transition. No blank flash.
- **Detect:** Blank/white flash between splash and content. Splash > 2s. No transition
- **Fix:** Platform splash API (Android 12+ SplashScreen, iOS launch storyboard). Fast transition to first content
- **Source:** Platform guidelines

### VIS-14 [HIGH] Adaptive Icons (Android)
Foreground + background layers. 66dp safe zone.
- **Detect:** Non-adaptive icon. Content outside safe zone. Single-layer icon
- **Fix:** 108x108dp with 66dp safe zone. Vector preferred. Separate foreground/background
- **Source:** Android Adaptive Icons

### VIS-15 [HIGH] Color Palette Limit & Harmony
Maximum 6 distinct hues in the app. All colors from theme tokens.
- **Detect:** >6 distinct hue values across the app. Random hex values outside theme definition. Colors not from `ColorScheme` / theme tokens
- **Fix:** Define a palette of max 6 hues (primary, secondary, tertiary, neutral, error, + 1 accent). All UI colors reference theme tokens. No arbitrary hex in widget code
- **Impact:** Uncontrolled color use creates visual noise and undermines brand identity
- **Source:** Material 3 Color System, Color Theory

### VIS-16 [HIGH] Color Blindness Safety
Color is never the sole differentiator. Shapes, icons, or text always accompany color.
- **Detect:** Red-green as only distinction (e.g., success/error). Status indicators using color alone without icon or label. Charts relying solely on color
- **Fix:** Pair every color indicator with icon, shape, or text label. Use colorblind-safe palettes. Test with deuteranopia/protanopia simulators
- **Impact:** 8% of males have color vision deficiency — color-only UI excludes them
- **Source:** WCAG 1.4.1, Material Design Accessibility

### VIS-17 [HIGH] Semantic Color Correctness
Colors match their semantic meaning. No misleading color usage.
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
- **Impact:** Inconsistent shadows create visual clutter and break spatial metaphor
- **Source:** Material 3 Elevation System

### VIS-20 [HIGH] Card Design Consistency
All cards on a screen share the same radius, padding, and elevation.
- **Detect:** Cards with different border radius on same screen. Inconsistent internal padding across cards. Mixed card styles (outlined vs elevated) without clear purpose
- **Fix:** Define card variants (elevated, filled, outlined) with fixed radius, padding, and elevation. Use one variant per context. Internal padding consistent across all cards
- **Impact:** Inconsistent cards make the UI feel unpolished and reduce scannability
- **Source:** Material 3 Card Component

### VIS-21 [HIGH] Button Style Hierarchy
Distinct button styles for primary, secondary, and tertiary actions.
- **Detect:** All buttons using same style (all filled or all outlined). No visual distinction between primary and secondary actions. Destructive actions styled like normal actions
- **Fix:** Primary: filled. Secondary: outlined or tonal. Tertiary: text button. Destructive: red/outlined-red. Disabled: reduced opacity. Consistent across all screens
- **Impact:** Uniform button styling removes action priority — users can't distinguish important from trivial
- **Source:** Material 3 Button Styles, Apple HIG Buttons

### VIS-22 [LOW] Image Aspect Ratio Consistency
Images maintain correct aspect ratio. No distortion.
- **Detect:** Images with `fit: BoxFit.fill` (Flutter), `resizeMode: 'stretch'` (RN), `contentMode: .scaleToFill` (iOS) causing distortion. Mixed aspect ratios in grid/list layouts
- **Fix:** Use `BoxFit.cover` or `BoxFit.contain`. Consistent aspect ratios in lists (e.g., all 16:9 or all 1:1). Placeholder for loading. Error image for failures
- **Impact:** Distorted images look unprofessional and damage trust in the app
- **Source:** Material Design Imagery, Apple HIG Images

### VIS-23 [HIGH] Icon Style Consistency
Single icon family throughout the app. Consistent sizing.
- **Detect:** Mixed icon families (Material + Cupertino + custom). Inconsistent icon sizes (20dp, 24dp, 28dp in same context). Outlined and filled icons mixed without purpose
- **Fix:** Choose one icon family per platform. Standard sizes: 16dp (inline), 24dp (actions), 40dp+ (features). Filled for selected states, outlined for unselected. Custom icons match family weight/style
- **Impact:** Mixed icon styles create visual inconsistency and feel like multiple apps stitched together
- **Source:** Material Icons Guide, SF Symbols Guidelines

### VIS-24 [HIGH] Interactive State Visibility
All interactive elements show pressed, disabled, focused, and loading states.
- **Detect:** Buttons without pressed/disabled visual state. No loading indicator on async buttons. Form fields without focus ring. Switches/checkboxes without state transition
- **Fix:** Define states for every interactive component: default, pressed, focused, disabled, loading, error. Disabled = reduced opacity (38%). Loading = spinner replacing label. Focus = visible ring/outline
- **Impact:** Missing interactive states make the UI feel unresponsive and confuse users about what's actionable
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
- **Source:** Platform layout overflow prevention guides

---

## Accessibility

### A11Y-01 [CRITICAL] WCAG 2.2 AA + EAA
EU apps must comply. EAA active since June 28, 2025. Fines up to EUR 100K or 4% revenue.
- **Detect:** No accessibility audit. WCAG violations in core flows
- **Fix:** Audit against WCAG 2.2 AA. Remediate by severity. Document conformance
- **Source:** WCAG 2.2, EAA 2019/882, EN 301 549

### A11Y-02 [CRITICAL] Touch Target >= 44dp
Every interactive element >= 44x44dp. Spacing >= 8dp between targets.
- **Detect:**
  - Check for: `height: [0-3][0-9]`, `width: [0-3][0-9]` on interactive widgets
  - Tappable elements with no minimum size constraint
- **Fix:** Set minWidth/minHeight 44dp. Add padding for hit area. 8dp+ spacing between targets
- **Note:** WCAG minimum 24x24. Apple recommends 44pt. Material 3 recommends 48dp. Use 44dp as practical minimum
- **Source:** WCAG 2.5.8, Apple HIG, Material 3

### A11Y-03 [CRITICAL] Semantic Labels
Every interactive widget has a11y label. Decorative elements hidden from tree.
- **Detect:**
  - Interactive widgets without: `accessibilityLabel` (iOS), `contentDescription` (Android), `Semantics(label:)` (Flutter), `accessibilityLabel` (RN)
  - Images without `isAccessibilityElement=false` or `Semantics(excludeSemantics:true)` for decorative
- **Fix:** Add descriptive labels. Mark decorative as excluded. Set traits/roles. Define custom actions
- **Source:** WCAG, Apple VoiceOver, Android a11y

### A11Y-04 [CRITICAL] Text Contrast 4.5:1
Normal text 4.5:1. Large text (18pt+ or 14pt+ bold) 3:1.
- **Detect:** Low-contrast text. Light gray on white. Placeholder text too faint
- **Fix:** Adjust colors. Never rely on color alone. 83.6% of websites fail contrast (WebAIM)
- **Source:** WCAG 1.4.3

### A11Y-05 [CRITICAL] Non-Text Contrast 3:1
UI components, focus indicators, meaningful graphics.
- **Detect:** Faint borders, outlines, or focus rings. Icons below 3:1
- **Fix:** Adjust component colors. Ensure focus indicators visible. Exception: inactive controls
- **Source:** WCAG 1.4.11

### A11Y-06 [HIGH] Respect Reduced Motion
All animations conditional on reduced motion setting.
- **Detect:** Animations ignoring accessibility settings. Parallax effects. Auto-play media
- **Fix:**
  - Check: `prefers-reduced-motion` (web/RN), `UIAccessibility.isReduceMotionEnabled` (iOS), `Settings.Global.ANIMATOR_DURATION_SCALE` (Android)
  - Replace scale/pan with opacity crossfade
  - Max 5s duration, max 3 flashes/sec
- **Source:** WCAG 2.3.3

### A11Y-07 [HIGH] Focus Management
Logical order. Focus moves to new content. Focus trapped in modals.
- **Detect:** Random focus after screen change. Lost focus on dismiss. No trap in dialogs
- **Fix:** iOS: @AccessibilityFocusState. Android: focusable + nextFocus. Move focus to new content. Restore on dismiss
- **Source:** WCAG

### A11Y-08 [HIGH] Color Not Sole Indicator
Pair color with text, icon, or pattern.
- **Detect:** Error only by red. Status only by color dot. Required marked only by color
- **Fix:** Icon + text alongside color. Shapes + labels in charts
- **Source:** WCAG 1.4.1

### A11Y-09 [HIGH] Both Orientations
Portrait + landscape unless functionally essential.
- **Detect:** Orientation locked without functional reason. Layout broken in landscape
- **Fix:** Support both. Test all screens. Adaptive layout
- **Source:** WCAG 1.3.4

### A11Y-10 [HIGH] Accessible Error Messages
Screen reader announced. Clear, actionable language. Associated with input.
- **Detect:** Errors not announced. Vague text. Error not linked to field
- **Fix:** iOS: UIAccessibility.post(.announcement). Android: accessibilityLiveRegion. Associate errors with inputs
- **Source:** WCAG 4.1.3

### A11Y-11 [HIGH] Dragging Alternatives
Every drag operation has a single-pointer alternative.
- **Detect:** Drag-to-reorder without alternative (move up/down buttons). Drag-to-dismiss without close button. Slider without text input alternative. Map pin drag without address input
- **Fix:** Provide single-pointer alternative for every drag: up/down buttons for reorder, tap-to-select for drag-to-position, text input for sliders. Drag is enhancement, not requirement
- **Impact:** Motor impairments and assistive devices cannot perform drag gestures
- **Source:** WCAG 2.5.7 (Dragging Movements) — new in WCAG 2.2

### A11Y-12 [HIGH] Accessible Authentication
No cognitive function test (memorization, transcription, puzzle) required for login.
- **Detect:** CAPTCHA without accessible alternative. Password-only login without paste support. Security questions requiring memorization. Custom auth challenges (math, pattern)
- **Fix:** Support paste in password fields. Offer biometric/passkey authentication. CAPTCHA with audio or object recognition alternative. Allow password managers. Provide "remember me" option
- **Impact:** Cognitive function tests exclude users with cognitive disabilities and dementia
- **Source:** WCAG 3.3.8 (Accessible Authentication — Minimum) — new in WCAG 2.2
