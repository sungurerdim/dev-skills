# Rules: Components, States & Interactions

Rules for audit/fix/design modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Framework Detection** | reference table (SKILL.md Phase 1) | ~14 |
| **Ecosystem Rules** | reference table (SKILL.md Scopes A9) | ~35 |
| **Component Quality** | CMP-01 to CMP-27 (12 HIGH, 14 MEDIUM, 1 LOW) | ~46 |
| **Interactions** | INT-01 to INT-05 (3 MEDIUM, 2 LOW) | ~280 |

---

## Framework Detection

Detection signal per framework, evaluated in SKILL.md Phase 1 step 1. First hit wins; a genuinely polyglot project (e.g. a Svelte app with an Astro marketing site) may report more than one.

| Framework | Detection |
|-----------|-----------|
| React | `package.json` dep `react` |
| Vue | `package.json` dep `vue` |
| Svelte | `package.json` dep `svelte`, no `$state`/`$derived`/`$effect`/`$props` runes in `.svelte` files |
| Svelte 5 (runes) | `package.json` dep `svelte` ^5, `$state`/`$derived`/`$effect`/`$props` calls in `.svelte`/`.svelte.js`/`.svelte.ts` files |
| Astro | `astro.config.mjs`/`.ts`, `.astro` component files, `package.json` dep `astro` |
| SolidJS | `package.json` dep `solid-js`, `createSignal`/`createEffect`/`createMemo` imports |
| htmx | `package.json`/CDN script tag for `htmx.org`, `hx-get`/`hx-post`/`hx-target`/`hx-swap` attributes in HTML/templates |
| Angular | `package.json` dep `@angular/core` |
| Flutter | `pubspec.yaml` with `flutter:` |
| React Native | `package.json` dep `react-native` |
| SwiftUI | `*.swift` files importing `SwiftUI` |
| Compose | `build.gradle` with `compose` |
| Electron/Tauri | `package.json` dep `electron` or `@tauri-apps/api` |
| Plain HTML/CSS | `*.html` + `*.css` without framework |

## Ecosystem Rules

A9 — Google / Apple Ecosystem Rules (conditional, SKILL.md Scopes). Active only when the blueprint profile's `Integrations` field is `google-workspace` or `apple-ecosystem`; zero checks otherwise.

| Provider | Rule | Scope |
|----------|------|-------|
| Google | Official button/flow standards — Google Identity branding (G-button, One Tap, Credential Manager) | tokens, components |
| Apple | Apple HIG Sign-in — `ASAuthorizationAppleIDButton`, SF Symbols, HIG | tokens, components |

**Framework-specific pattern each new row checks:**
- **Svelte 5 (runes):** a `.svelte.js`/`.svelte.ts` module exporting a reassignable `$state` primitive directly (`export let count = $state(0)`) is broken — reassignment doesn't propagate across the module boundary. Flag a raw exported `$state` value; fix by exporting an object, class, or getter/setter pair instead. **Source:** [Svelte docs — states are not exportable](https://svelte.dev/docs/svelte/$state) (verified 2026-09-02, HTTP 200).
- **Astro:** client-side interactivity requires an explicit `client:*` directive (`client:load`/`client:idle`/`client:visible`/`client:media`/`client:only`) on any framework island — a component using event handlers or state with no `client:*` directive ships zero JS and silently does nothing. Flag an interactive island component with no directive. **Source:** [Astro docs — Islands](https://docs.astro.build/en/concepts/islands/) (verified 2026-09-02, HTTP 200).
- **SolidJS:** props are not reactive when destructured (`const { x } = props`) — Solid implements props as getters for fine-grained reactivity, and destructuring reads the value once at that point instead of tracking it. Flag destructured props used in JSX or inside `createEffect`; fix via `splitProps`/`mergeProps` or accessing `props.x` directly. **Source:** [SolidJS docs — Props](https://docs.solidjs.com/concepts/components/props) (verified 2026-09-02, HTTP 200).
- **htmx:** every `hx-get`/`hx-post`/`hx-put`/`hx-delete` target endpoint should return an HTML fragment, not JSON — htmx swaps response markup directly into the DOM. The default `hx-swap` is `innerHTML`; an unset `hx-swap` on a nested target can replace more than intended, and swapping into `<body>` always forces `innerHTML` regardless of the configured strategy. **Source:** [htmx docs — hx-swap](https://htmx.org/attributes/hx-swap/) (verified 2026-09-02, HTTP 200).

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
  Search/filter inputs specifically: seed an initial unfiltered result set (first N items) at mount rather than gating results behind a minimum query length — an empty result area at mount is ambiguous ("no data" vs. "type more") when data actually exists to show.
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

### CMP-09 [HIGH] Anchored Overlay Portal Isolation
Every anchored/floating overlay (search-result dropdown, "more actions" menu, status popover, typeahead list) renders through a shared top-level portal host with viewport-relative fixed positioning — never as a `position:absolute` descendant nested inside the trigger's own container.
- **Detect:** Search for `position:\s*absolute` (or the framework equivalent — React portal-less floating divs, Vue teleport-less dropdowns, Flutter `Positioned` inside a clipping `ClipRect`/`Container(overflow:Clip)`) on elements that behave as a dropdown/menu/typeahead result list. Cross-reference against every ancestor selector for `overflow:\s*(hidden|auto|scroll)` — a `position:absolute` overlay whose DOM ancestor chain includes such a rule is a live or latent clip, even if not clipped today: the next refactor that nests it one level deeper silently reintroduces the bug with zero code change to the overlay itself.
- **Fix:** Introduce (or reuse) one shared overlay primitive that (a) appends its content to a single body-level host element created once, (b) computes position from the trigger's `getBoundingClientRect()`, (c) uses `position: fixed` so no ancestor's overflow/clipping context can affect it, (d) clamps the computed position inside the viewport bounds, and (e) shares one z-index layer token above the app's modal/dialog layer. Migrate every ad-hoc overlay onto this primitive instead of patching each container's `overflow` property one at a time.
  **Focus-trap independence:** a body-appended overlay opened from inside a modal/dialog is outside that modal's own focus-trap DOM subtree. If the overlay doesn't establish its own independent trap (Tab/Shift+Tab wrapping inside just the overlay, initial focus moved in on open, focus returned to the trigger on close), a keyboard-only user tabbing through it will leak straight back into the host modal's fields. Verify by opening the overlay with a mouse, then tabbing from its first focusable element — focus must stay within the overlay until Escape/selection.
- **Impact:** This is the single most common cause of "the dropdown is half-cut-off / invisible" bug reports — architecturally silent until an unrelated later change adds `overflow:hidden` to some ancestor for a completely different reason. The focus-trap gap is worse specifically when opened from inside a modal (two traps interact unpredictably) than from the page directly, and mouse-driven QA never notices it.
- **Source:** CSS positioning/stacking-context practice; W3C ARIA APG focus management; live audit + fix

### CMP-10 [MEDIUM] Anchored Overlay Sizing Contract
Every anchored overlay (see CMP-09) shares one min-width / max-width / max-height(+internal scroll) / word-wrap contract instead of each instance hand-rolling its own bounds.
- **Detect:** Multiple overlay/dropdown/menu components each defining their own `min-width`/`max-width`/`max-height` values, or omitting one — e.g. no `max-height`, so a long result list grows unbounded past the viewport bottom with no scroll. Also check for missing `overflow-wrap`/`word-break` on long unbroken strings inside the panel — without it, the panel's own `max-width` gets silently violated by the content forcing it wider; a modal whose outer size shifts as content changes, nested/double scrollbars inside an overlay, or header/action bars that scroll away with content
- **Fix:** Define the four values once (as tokens/theme constants) and apply them uniformly at the shared overlay primitive level (see CMP-09): a floor width, a ceiling width paired with `overflow-wrap: anywhere`, and a ceiling height with `overflow-y: auto`. Size stability: the overlay's outer dimensions never change with content; overflow resolves in exactly ONE defined internal scroll region while header and action areas stay fixed; nested scrollbars are forbidden; post-open layout shift stays near zero. (XR-170)
- **Impact:** Without a shared contract, some overlays cap height and others don't, some wrap long content and others let it overflow the panel's own box — visibly inconsistent polish across the same interaction pattern.
- **Source:** Live audit pattern; CSS Overflow Module Level 4

### CMP-11 [MEDIUM] Structural Field-Type Registry
Every structural data type that needs input masking, validation, parsing, and display formatting (phone numbers, national ID/tax numbers, money + currency, percentages, integers with a "no limit" sentinel, dates, URLs, …) is defined **once** in a central registry (mask/validate/parse/format/inputAttrs per type) — never re-implemented ad hoc at each input field or display site.
- **Detect:** Search for inline regex patterns, inline `parseFloat`/`parseInt`/custom parsing, or inline formatting logic duplicated across multiple form fields or display components for what is recognizably the same underlying data type. Also check whether validation failures block saving (HARD) vs. only warn — inconsistency across fields of the *same type* is itself a signal of missing centralization.
- **Fix:** Introduce one registry keyed by type id, each entry exposing `{ mask, validate, format, parse, inputAttrs, placeholder }`; every input field and every display site consumes it instead of writing its own logic. Keep the *stored* canonical value format stable and separate from the *display* mask. Phone numbers specifically: format per-country and render every display with a country indicator (flag or dial code) from the registry's phone type. (XR-168)
- **Impact:** Duplicated per-field validation/formatting logic drifts silently — one call site's phone regex accepts a format another rejects, one money field loses precision on round-trip that another preserves.
- **Source:** Live audit pattern (production field-type registry)

### CMP-12 [MEDIUM] Summary/Stat Tiles Are Drillable, Not Dead Text
A stat tile, KPI number, or summary count that represents an underlying filtered set of records is a real link/button to that filtered view — not inert, unclickable text.
- **Detect:** A dashboard/summary tile rendering a number or short stat with no `href`/`onClick`/keyboard affordance, where the number is visibly a count or aggregate of records that exist elsewhere in the app as a listable/filterable collection.
- **Fix:** Wrap the tile in an actual link or button that navigates to the corresponding filtered list view, with an accessible name that states both the label and the value (e.g. `aria-label="Overdue: 3"`).
- **Impact:** Users routinely try to click stat tiles expecting drill-through; a dead tile is a broken expectation and a missed navigation shortcut, discovered by users clicking and getting nothing.
- **Source:** Live audit pattern (dashboard KPI tiles)

### CMP-13 [HIGH] Error State Must Not Collapse Into Empty State
A data-loading surface has four *distinct* states — empty, loading, error, and permission-denied — and a failure in any one must never silently render as a different one, especially error-as-empty.
- **Detect:** Search async data-fetching code for a `catch` block that sets the data array/state to an empty value (`catch (e) { setItems([]) }` or equivalent) without a separate error flag. Separately, check whether a permission/authorization failure (403-equivalent) renders as a generic "something went wrong" error rather than a distinct "you don't have access" state with no retry button (retrying a permission error never succeeds).
- **Fix:** Track loading/error/empty/forbidden as separate, mutually exclusive state values, not derived from "is the array empty"; a `catch` sets an explicit error flag distinct from "zero results," and the component branches on that flag before checking array length. A permission failure gets its own render branch.
- **Impact:** Error-as-empty is a silent failure class — the user sees "no data" with no signal anything broke, so they never report it, and passive error monitoring can miss it too since nothing *looks* broken. This is qualitatively worse than a visible error.
- **Source:** Live audit pattern (async fetch error handling)

### CMP-14 [MEDIUM] Action/Field Grouping via Spacing (Gestalt Proximity)
Related actions or fields are visually grouped by tighter spacing between them than the spacing separating them from the next unrelated group — never a single uniform gap applied indiscriminately across an entire toolbar, action row, or form.
- **Detect:** A row/toolbar/action-bar with 3+ controls where every gap between adjacent controls is identical, while the controls belong to visually or functionally distinct clusters (e.g. view/filter controls vs. a destructive "Delete" action; primary "Save" next to secondary "Cancel" next to unrelated "Export"). Also flag a destructive action (delete/remove/discard) positioned with the exact same spacing and visual weight as adjacent non-destructive actions, with no separator or grouping container distinguishing it.
- **Fix:** Increase the gap between distinct clusters (roughly 2x the intra-cluster gap) or insert a visual separator/divider so proximity itself communicates grouping; give destructive actions extra spacing and/or a divider from non-destructive ones.
- **Impact:** Uniform spacing flattens visual hierarchy — a user has to read every label to figure out which controls belong together instead of perceiving groups at a glance; unseparated destructive actions sitting flush against safe ones raise the chance of a mis-click destroying data.
- **Source:** Gestalt Law of Proximity (perceptual grouping via spacing)

### CMP-15 [HIGH] No Stale, Empty, or Stub Routes
Every route/page reachable in the router (and every entry linked from navigation) renders real, current content — not a leftover placeholder, an empty component, a "Coming soon" stub, or a route left over from a removed/renamed feature.
- **Detect:** Enumerate the router's route table (React Router / Vue Router / Next.js `app` or `pages` dir / Angular routing module / Flutter `go_router` / etc.) and cross-reference against: (a) component files that render only a placeholder (`return null`, `<div>TODO</div>`, `<div>Coming soon</div>`, a single heading with no functional content), (b) routes with zero inbound references from any nav/menu/link in the codebase — orphaned, reachable only by typing the URL directly, (c) routes whose target component file was deleted or renamed but the route registration wasn't (dead import, or silently falls through to a catch-all). Flag each independently — a route can be linked-but-stub, unlinked-but-complete (dead code, lower severity), or unlinked-and-stub (both).
- **Fix:** Stale/removed feature → delete the route registration and its nav entry together, never partially. In-progress feature → finish the page before it ships to production routing, or gate it behind a feature flag / an honest "not yet available" state, excluded from primary nav until ready.
- **Impact:** A stub or dead route reachable by a real user (via nav, a stale bookmark, or a shared link) reads as "this app is broken" — worse than a 404, which at least signals "this doesn't exist," while a blank/placeholder page signals "this is broken." Orphaned routes silently bloat the bundle and the router's mental model for every future contributor.
- **Source:** Live audit pattern (route/page hygiene); general SPA routing practice

### CMP-16 [HIGH] Every Control Has a Real, Correct, Bound Action
Every interactive control (button, menu item, icon action, link) is necessary, has a concrete bound handler, and that handler does what the control's label/icon says — not a no-op, a placeholder, or a handler wired to the wrong action.
- **Detect:** For each interactive element, check: **no-op** — empty handler body, a handler that only `console.log`s or has a `// TODO`, `href="#"` with no click handler, a control that looks enabled but isn't wired to anything; **necessity** — a control whose action duplicates another control on the same screen with no distinct value, or a control gated behind a permission/feature flag that's never true in the current build (dead affordance); **correctness** — handler behavior mismatched against the control's visible label or icon (e.g. a button labeled "Delete" bound to an update call, a universally-understood "save" icon wired to "cancel"). Cross-reference the handler's actual side effect (API call, state mutation, navigation target) against the label's stated intent.
- **Fix:** No-op → implement the real action or remove the control until it's ready. Duplicate/unnecessary → consolidate to one control or remove the redundant one. Mismatched → rename the label/icon to match the real behavior, or rewire the handler to match the stated intent — whichever reflects the actual intended behavior; never leave the mismatch in place.
- **Impact:** A control that looks actionable but does nothing (or does the wrong thing) is worse than no control — it costs the user a wasted click plus the effort of re-verifying what actually happened, and a mislabeled destructive/non-destructive mismatch specifically risks data loss or a startled user.
- **Source:** Live audit pattern (control-to-handler correctness); Nielsen heuristic 1 — Visibility of System Status (the user-facing failure mode when it's absent)

### CMP-17 [MEDIUM] Icon System Consistency
All icons come from one icon set, sized by tokens, colored via `currentColor`/semantic tokens, with one stable icon-to-action mapping across the app.
- **Detect:** Two or more icon libraries imported in one codebase (e.g. lucide + Font Awesome + heroicons mixed); raw pixel `width`/`height` on icons instead of a small size scale (16/20/24); icons with hardcoded `fill`/`stroke` colors instead of `currentColor` or a semantic token (breaks theming — see THM-05); mixed visual styles (outlined and filled variants of the same set side by side on one surface); the same action drawn with different icons in different views.
- **Fix:** Standardize on one icon set; expose 2–3 size tokens and route every icon through them; use `currentColor` so icons inherit text color and adapt to theme automatically; maintain one icon-to-action mapping (the comprehension side — does the icon need a text label — is UX-02's check; the mapping-consistency side is UX-04's; this rule owns the visual/technical system).
- **Impact:** Mixed icon languages are one of the fastest "this product is stitched together" signals a user perceives, without being able to name why; hardcoded icon colors silently break in dark mode; drifting metaphors force users to re-learn the same action per screen.
- **Source:** Design-system iconography practice (Material Symbols, SF Symbols usage guidelines)

### CMP-18 [MEDIUM] Select-or-Create Pattern for Entity-Linking Pickers
Any UI flow that lets a user add a new related record by typing a name (tag, category, contact, or other reusable entity) first searches existing matching records and offers to select one, before offering "create new".
- **Detect:** An "add new {entity}" flow that links a reusable/searchable entity (contact, tag, category, org) and jumps straight to a blank creation form with no prior existing-record search/autocomplete step.
- **Fix:** Add a search-existing step (autocomplete/picker) before the create-new fallback; only fall through to creation when no match is selected.
- **Impact:** Skipping the search-existing step is the direct cause of accidental duplicate entities, which then silently fragments data (the same person/tag existing twice under different records).
- **Source:** Autocomplete/typeahead entity-resolution UX practice

### CMP-19 [HIGH] Provenance Display for Override-vs-Default Fields
A field that overrides a shared/system/org-level default renders its input value as ONLY the explicit override (empty if none) — the live system default appears solely as placeholder text, never merged into the value.
- **Detect:** An editable field whose value is computed as `override || systemDefault` (or equivalent merge) rather than showing the override alone with the default as placeholder — saving that form untouched would permanently freeze the current system default as a per-record override.
- **Fix:** Render the input's value as the explicit override only (empty when none exists); show the live default as placeholder; pair with a visible "customized" indicator and a reset-to-default action when an override is active.
- **Impact:** Merging the resolved value into the input is a silent-freeze bug — an untouched "Save" permanently pins what should have stayed a live-following default, and the bug is invisible until the org-wide default is later changed and the frozen record doesn't follow.
- **Source:** Live incident pattern (org-default-merged-into-editable-value freeze bug)

### CMP-20 [MEDIUM] Unified Status-Center Rollup
Multiple independent status/notification indicators a user could see simultaneously (connectivity, sync, error/conflict count, update-available) consolidate into one rollup indicator backed by a single status-collection function.
- **Detect:** A topbar/header with 3+ separate, always-visible status badges whose meanings overlap or that could report inconsistent/duplicated information because each derives its state independently.
- **Fix:** Consolidate into one rollup indicator fed by a single status-collection function; a detail popover partitions facets from that same collection (never re-derives independently, so nothing is double-counted).
- **Impact:** Competing status badges with overlapping meaning confuse users about whether something is actually wrong; a single rollup plus itemized popover answers that question at a glance.
- **Source:** Status/notification consolidation practice (dashboard information-architecture convention)

### CMP-21 [MEDIUM] Event-Delegation Over Inline Handlers
A framework-free/vanilla-DOM UI wires interactivity via a single delegated document-level listener plus a declarative action attribute (e.g. `data-action="module.method"`), not inline `onclick="..."` handlers.
- **Detect:** Inline event-handler attributes (`onclick`, `onchange`, etc.) in templates, especially ones referencing module-scoped functions that had to be bridged onto the global namespace to be reachable from markup.
- **Fix:** Replace with one delegated listener at the document/root level dispatching on a `data-action`-style attribute to a registerable handler map; remove the global-namespace bridge objects this required.
- **Impact:** Inline handlers force a global-namespace bridge for every referenced module/function, hurt testability (handler wiring isn't a separate, inspectable map), and are incompatible with a strict CSP (`script-src 'self'`, no `unsafe-inline`) — flag as both a CSP blocker and a testability gap.
- **Source:** Content Security Policy Level 3 (`unsafe-inline` restriction); event-delegation pattern (DOM Events spec)

### CMP-22 [MEDIUM] Reload-Safe Form-State Snapshot/Restore
A forced-reload path that can interrupt an open form/modal (new-version-deploy prompt, cache-bust redirect) snapshots the form's field values before reload and restores them after, excluding any field explicitly marked sensitive/no-persist.
- **Detect:** A forced-reload flow (version-update prompt, cache invalidation redirect) with no form-state preservation for an open form/modal at the time reload fires.
- **Fix:** Snapshot the open form/modal's field values on the page's unload/hide event to short-lived storage; restore them once the app re-opens the same route/modal after reload; exclude fields explicitly marked sensitive, even transiently.
- **Impact:** Losing in-progress form input to a forced reload the user didn't initiate is a silent-data-loss UX risk that measurably makes users defer or avoid updates/edits.
- **Source:** Page Lifecycle API (`pagehide`/`visibilitychange`) — MDN

### CMP-23 [MEDIUM] Filter Panel Primitive: Shared Behavior Core, Per-Surface Labels
All filter panels derive from one shared primitive: common controls (select-all, clear) share text, behavior, and position; labels stay configurable per surface.
- **Detect:** Multiple filter panels implement their own select-all/clear with different wording, placement, or semantics; filter field layouts differ arbitrarily between surfaces.
- **Fix:** Extract one filter-panel primitive (checkbox list + chip toggles) owning the behavioral contract — idempotent select-all/clear, consistent placement, one base layout. Keep the functional core single-sourced, but let button/group labels be configured per usage site rather than hardcoded from one dictionary.
- **Impact:** Divergent filter behavior forces users to relearn the same control per screen; a shared primitive makes every future filter free.
- **Source:** XR-048 — cross-project experience registry (2026).

### CMP-24 [MEDIUM] Entity Row and Picker Primitives Are Shared and Context-Filterable
Recurring entity displays (person rows, record rows) render from one aligned-column primitive, and entity pickers accept contextual filters.
- **Detect:** The same entity type renders with different field order/alignment across surfaces; entity pickers show the full unfiltered population where the context implies a subset (e.g. only staff, only customers).
- **Fix:** Extract one entity-row primitive with aligned columns (name, phone, other fields column-aligned by data type); give picker primitives a context-filter parameter (e.g. by role/category) so each usage site scopes its candidate list declaratively.
- **Impact:** Unaligned ad-hoc rows slow scanning on every list; unfiltered pickers make users search through irrelevant records on every selection.
- **Source:** XR-063 + XR-064 — cross-project experience registry (2026).

### CMP-25 [HIGH] Search Behavior Derives From One SSOT
Every search field (global rail, board, pickers, settings search) shares the same debounce, minimum-character threshold, result limit, and combobox a11y behavior from one source.
- **Detect:** Search inputs hardcode their own debounce/threshold/limit values; keyboard behavior (arrow navigation, Enter, Esc) differs between search fields.
- **Fix:** Centralize search constants and a shared search helper (debounce ms, min chars, result cap, combobox keyboard model) and require every search field to consume it; forbid per-field hardcoded values.
- **Impact:** Each divergent search field is a separate bug surface and a separate muscle-memory reset for users.
- **Source:** XR-166 — cross-project experience registry (2026).

### CMP-26 [MEDIUM] Form Ergonomics: Dependency Order, Derived-but-Editable, Status Color
Form fields follow dependency order; derived values stay visible and overridable; validation state is color-coded; popovers portal correctly above modals.
- **Detect:** A field's options depend on another field placed below it; derived values are hidden or locked; override state is indistinguishable from default; validation state is text-only; popovers clip or render under modal overlays.
- **Fix:** Order fields so dependencies flow downward; show derived values as editable with a visible override-vs-default distinction (per CMP-19); color-code validation state (with a non-color companion per AXE rules); render popovers through a portal layered above the modal.
- **Impact:** Dependency-inverted forms force backtracking; hidden derivations produce "where did this value come from" support tickets.
- **Source:** XR-056 — cross-project experience registry (2026).

### CMP-27 [HIGH] Routes Derive From One Manifest; Every Surface Is Addressable
All routes derive from a single route-manifest SSOT, and every user surface — including modals and panels — has its own route, is bookmarkable, and reopens refresh-safe.
- **Detect:** Routes registered by scattered imperative calls with no single manifest; modals/detail panels that vanish on refresh; surfaces unreachable by direct URL; state reachable only through a click sequence.
- **Fix:** Define one route manifest (path, surface, params, tier) as the SSOT and derive registration, navigation, and liveness checks from it; give every surface a route that restores the same state on refresh or direct entry.
- **Impact:** Scattered route registration drifts (dead routes, orphan surfaces); non-addressable surfaces break refresh, sharing, bookmarks, and support ("send me the link" fails).
- **Source:** XR-003 + XR-136 — cross-project experience registry (2026).

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

### INT-05 [MEDIUM] Zero-Refresh In-Page Filter/Toggle
An in-page filter/toggle/tab-switch handler within an already-rendered view mutates DOM/state directly (class toggle, targeted patch) rather than calling the view's full render/navigate function.
- **Detect:** A filter chip, column-filter, or tab-switch handler within the same view that calls the top-level render/navigate function instead of patching the DOM/state directly.
- **Fix:** Flip CSS classes or patch the affected DOM/state directly for in-page interactions; reserve full-view re-render/navigation for actual route changes.
- **Impact:** An unnecessary full re-render discards scroll position and focus and is perceptibly slower than a targeted patch — reserved cost that a real route change would justify, spent on a same-view toggle.
- **Source:** Live audit pattern (in-page interaction vs. route-level render)
