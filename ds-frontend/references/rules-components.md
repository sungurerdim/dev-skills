# Rules: Components, States & Interactions

Rules for audit/fix/design modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Component Quality** | CMP-01 to CMP-08 (5 HIGH, 2 MEDIUM, 1 LOW) | ~12 |
| **Interactions** | INT-01 to INT-04 (2 MEDIUM, 2 LOW) | ~120 |

---

## Component Quality

### CMP-01 [HIGH] Component API Consistency
Props/parameters follow consistent naming convention, are typed, and have sensible defaults.
- **Detect:** Search for component definitions. Compare prop/parameter names across components:
  - Inconsistent boolean naming: `isVisible` vs `visible` vs `show` vs `hidden`
  - Inconsistent callback naming: `onClick` vs `handleClick` vs `onPress` vs `onTap`
  - Missing type annotations on props
  - Missing default values for optional props
- **Fix:** Establish naming convention (e.g., `is*` for booleans, `on*` for callbacks). Apply consistently. Add types and defaults to all props.
- **Impact:** Inconsistent APIs increase learning curve, cause bugs from wrong prop names, and confuse AI code generators.
- **Source:** React Component API Design, Platform component conventions

### CMP-02 [HIGH] Interactive State Coverage
Every interactive component has all required visual states: default, hover, active, focus-visible, disabled.
- **Detect:** Search for interactive components (buttons, links, inputs, toggles, cards with click handlers). Verify each has styles for:
  - Hover (web) / highlight state (mobile)
  - Active / pressed state
  - Focus-visible / focus state (web) / focused state (mobile)
  - Disabled state with reduced opacity and no pointer events
  - Missing any state = finding
- **Fix:** Add missing state styles. Follow platform conventions for state feedback (web: CSS pseudo-classes; Flutter: MaterialStateProperty; SwiftUI: .disabled(); Compose: InteractionSource).
- **Impact:** Missing states make UI feel unresponsive. Users rely on state changes to confirm their actions registered.
- **Source:** Material Design State Layers, Apple HIG Interactive Elements

### CMP-03 [HIGH] Empty State Pattern
Data-driven components show meaningful empty state instead of blank space when data is absent.
- **Detect:** Search for conditional rendering patterns. Flag components that render nothing (blank, null, empty container) when data array is empty or null.
  - React: `{items.length > 0 && <List />}` without else branch
  - Flutter: `items.isEmpty ? Container() : ListView()` (empty Container)
  - Vue: `v-if="items.length"` without `v-else`
- **Fix:** Add empty state with: headline (what's empty), explanation (why), CTA button (what to do next). Use encouraging tone, not error tone.
  Example: "No projects yet" + "Create your first project to get started" + [Create Project] button.
- **Impact:** Blank states confuse users ("is it loading? broken? empty?"). Empty states with CTAs drive engagement.
- **Source:** Material Design Empty States, Luke Wroblewski Empty State Design

### CMP-04 [HIGH] Loading State Pattern
Async components show loading indicator with delay (200ms) to prevent flash for fast operations.
- **Detect:** Search for async data fetching in components. Verify loading state exists and uses delay before showing.
  - Missing loading state entirely (jumps from empty to loaded)
  - Loading indicator shows immediately (flashes for fast operations)
  - Generic spinner instead of content-shaped skeleton
- **Fix:** Add loading state with 200ms delay before showing indicator. Prefer skeleton screens (content-shaped placeholders) over spinners for content areas. Use spinners only for actions (button loading, form submit).
- **Impact:** Missing loading = users think app is frozen. Immediate spinner flash = jittery UX. Skeleton screens feel 30% faster (perception study).
- **Source:** Nielsen Norman Group Loading Indicators, Material Design Progress Indicators

### CMP-05 [HIGH] Error State Pattern
Errors displayed with recovery action, plain language, and multi-signal feedback (icon + color + text).
- **Detect:** Search for error handling in UI. Flag:
  - Generic messages: "Error", "Something went wrong", "An error occurred"
  - Color-only error indication (red text without icon or label)
  - Missing retry/recovery action
  - Error messages using technical jargon (HTTP status codes, stack traces)
- **Fix:** Replace with: descriptive message (what happened) + guidance (how to fix) + action button (retry/dismiss/contact). Combine icon + color + text for accessibility (color alone fails for colorblind users).
  Example: "Could not save your changes -- check your internet connection and try again" + [Retry] button.
- **Impact:** Generic errors frustrate users. Actionable errors reduce support tickets. Color-only fails 8% of male users (color blindness).
- **Source:** Nielsen Norman Group Error Messages, WCAG 1.4.1 Use of Color

### CMP-06 [MEDIUM] Component Composition
Complex components use composition pattern (children/slots/compound) instead of deep prop drilling.
- **Detect:** Components with >7 props, especially when many props passed through to child components unchanged. Deeply nested prop passing (3+ levels).
- **Fix:** Refactor to composition pattern:
  - React: compound components with React.Children or context
  - Vue: slots (default + named)
  - Svelte: slots
  - Flutter: builder pattern or widget composition
  - SwiftUI: ViewBuilder
  - Compose: content lambda
- **Impact:** Deep prop drilling makes components rigid, hard to test, and resistant to change. Composition enables flexible reuse.
- **Source:** React Composition vs Inheritance, Kent C. Dodds Compound Components

### CMP-07 [MEDIUM] AI-Discoverable Documentation
Each component documented for both human and AI agent consumption.
- **Detect:** Components without documentation file or JSDoc/docstring. Missing: props table, usage examples, accessibility notes, variant list.
- **Fix:** Add component documentation following progressive disclosure:
  1. **One-liner:** What this component does (1 sentence)
  2. **Props table:** Name, type, default, description (machine-readable)
  3. **Usage examples:** 2-3 common use cases with code
  4. **A11y notes:** Required ARIA attributes, keyboard behavior
  5. **Variants:** All supported visual variants listed
  Organize complex docs: essential info first, details in expandable sections.
- **Impact:** Well-documented components reduce AI hallucination by 60-80% (AI generates valid code instead of guessing). Agents using MCP can query component metadata directly.
- **Source:** Storybook Documentation, Brad Frost AI & Design Systems

### CMP-08 [LOW] Naming Convention
Components follow platform-standard naming convention.
- **Detect:** Component names not following convention:
  - Web (React/Vue/Svelte/Angular): PascalCase (Button, UserProfile)
  - Flutter: PascalCase with Widget suffix convention
  - SwiftUI: PascalCase with View suffix
  - Compose: PascalCase composable functions
- **Fix:** Rename to follow platform convention. Descriptive names preferred over generic (UserAvatar over Avatar when domain-specific).
- **Impact:** Non-standard naming confuses contributors and breaks conventions that tooling depends on (auto-imports, component discovery).
- **Source:** Platform component naming conventions

---

## Interactions

### INT-01 [MEDIUM] Animation Timing
Transitions use 200-500ms duration with consistent easing per interaction type.
- **Detect:** Search for animation/transition declarations. Flag:
  - Duration outside 200-500ms range (too fast or too slow)
  - Linear easing on UI transitions (feels mechanical)
  - Inconsistent duration for same interaction type (e.g., all modals should use same timing)
- **Fix:** Apply consistent timing: micro-interactions 200ms, standard transitions 300ms, complex animations 500ms. Use ease-out for entrances, ease-in for exits, ease-in-out for state changes.
- **Impact:** Wrong timing breaks illusion of responsiveness. Too fast = jarring. Too slow = sluggish. Inconsistent = unprofessional.
- **Source:** Material Design Motion, Apple HIG Animation

### INT-02 [MEDIUM] Immediate Action Feedback
Every user action receives visual feedback within 100ms.
- **Detect:** Interactive elements without visual response on interaction:
  - Buttons without active/pressed state
  - Links without hover underline or color change
  - Form inputs without focus ring
  - Toggle switches without transition
- **Fix:** Add immediate visual feedback: scale change, color shift, opacity change, or elevation change on interaction. Response must be <100ms (below human perception threshold for "instant").
- **Impact:** Without immediate feedback, users double-click, retry, or abandon. 100ms threshold is well-established UX constant.
- **Source:** Jakob Nielsen Response Time Limits, Material Design State Feedback

### INT-03 [LOW] Micro-interaction Consistency
Same interaction type produces same animation parameters across entire application.
- **Detect:** Compare animation parameters for same interaction types:
  - All page transitions use same duration/easing?
  - All dropdown menus use same open/close animation?
  - All toast notifications use same enter/exit?
- **Fix:** Define interaction pattern library: page transition, reveal, dismiss, feedback. Each pattern = one set of duration + easing + properties.
- **Impact:** Inconsistent micro-interactions make product feel like a collection of parts rather than a cohesive experience.
- **Source:** Material Design Motion Patterns

### INT-04 [LOW] Compositor-Only Animation
Animations target transform and opacity (GPU-composited) instead of layout-triggering properties.
- **Detect:** Animations targeting: width, height, top, left, margin, padding, font-size (trigger layout recalculation). CSS: `transition: width` or animation keyframes changing layout props.
- **Fix:** Replace with transform equivalents: `translateX/Y` instead of left/top, `scale` instead of width/height, `opacity` instead of visibility. Add `will-change: transform` for known animation targets.
  - Flutter: Use Transform widget, not AnimatedContainer for size changes during animation
  - Web: animate transform/opacity only; use will-change hint
  - Mobile: use platform GPU animation APIs (React Native: useNativeDriver: true)
- **Impact:** Layout-triggering animations → jank (dropped frames). Compositor-only animations run on GPU at 60fps+.
- **Source:** Google Web Fundamentals Rendering Performance, CSS Triggers
