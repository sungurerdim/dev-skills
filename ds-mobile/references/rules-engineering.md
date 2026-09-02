# Rules: Architecture, Testing, Performance, Network & Internationalization

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Architecture & Code Quality** | ARC-01–12 (10 HIGH, 1 MEDIUM, 1 LOW) | ~12 |
| **Testing** | TST-01–06 (6 HIGH) | ~100 |
| **Performance** | PRF-01–10 (9 HIGH, 1 MEDIUM) | ~160 |
| **Network & Data** | NET-01–07 (1 CRITICAL, 6 HIGH) | ~250 |
| **Internationalization & Logging** | DEV-01–05 (5 HIGH) | ~300 |
| **Hybrid & WebView Bridge** (conditional) | HYB-01–04 (1 CRITICAL, 2 HIGH, 1 MEDIUM) | ~345 |
| **Scan-Time Cross-Cutting Checks** | reference (SKILL.md Phase 4) | ~17 |

---

## Scan-Time Cross-Cutting Checks

Applied during Phase 4 Scan alongside the ARC/HYB/NET rules below — these are cross-rule principle applications, not individually numbered.

**arch scope mandatory checks** ([../../core/principles.md §2](../../core/principles.md)): widget/screen/view-model/repository layers vs SOLID — SRP (widget changes for >1 reason: UI + state + I/O), OCP, LSP (subtype violates parent navigation contract), ISP (unused lifecycle hooks), DIP (UI imports concrete platform-channel instead of abstraction) — and GRASP: Information Expert, Low Coupling (>7 unrelated peer imports), High Cohesion. Cite principle by name.

**arch scope hybrid checks** [hybrid shell detected]: run HYB-01–04 (§ Hybrid & WebView Bridge below) — WebView origin/bridge exposure in the committed `capacitor.config.*`, plugin dead-load audit (every plugin needs a consumer, searched repo-wide — a scoped search misses root entry files), the web-build → `cap sync` → native-build chain, and native behaviors the WebView doesn't supply. Not hybrid → skip silently.

**network + perf scope reliability checks** ([../../core/principles.md §4](../../core/principles.md)): flag missing — timeout on every API call, retry-with-backoff on transient failures, offline/slow-network degradation, app-lifecycle handlers (background→foreground), idempotency keys on payment/order/write endpoints, logging surviving restart, fail-fast validation at every boundary (deep links, push, intent extras).

---

## Architecture & Code Quality

### ARC-01 [HIGH] Clean Architecture Layers
Presentation (UI + ViewModel) / Domain (use cases) / Data (repositories). Dependencies inward only.
- **Detect:**
  - Business logic (if/else decisions, calculations, validation) in UI widgets/views/composables
  - Data access (API calls, DB queries) in UI layer
  - Circular dependencies between layers
  - Search for: `http.get`, `dio.`, `fetch(`, `Retrofit`, `Room` in UI/presentation files
- **Fix:** Extract logic to use cases (domain layer). Create repository interfaces in domain, implement in data. UI observes ViewModel state only
- **Production examples:** AppFlowy (73k+ stars) uses plugin architecture with event-based RPC + Protobuf across Flutter/Rust FFI boundary. Immich (60k+ stars) uses MVVM + Riverpod providers with hexagonal backend (repositories -> services -> controllers). Signal uses layered architecture: UI -> Service (singleton managers) -> Storage -> DB -> Network.
- **Impact:** Business logic embedded in the UI layer cannot be unit tested or reused, so every behavior change requires a UI-level test (or no test at all) and regressions surface only at runtime.
- **Source:** Android Architecture Guide, Flutter Architecture

### ARC-02 [HIGH] Unidirectional Data Flow
State down, events up. Single source of truth per data type.
- **Detect:** Two-way binding. State modified from multiple locations. UI mutating shared state directly
- **Fix:** ViewModel exposes immutable state. UI sends events. ViewModel processes and emits new state
- **Platform:**
  - Flutter: Riverpod 3.0 / BLoC
  - Android: StateFlow + ViewModel
  - iOS: @Observable (Swift 6.2+)
  - RN: Zustand (2KB, minimal)
- **Production patterns:** Riverpod `select()` for targeted rebuilds (Immich, Spotube): `ref.watch(provider.select((s) => s.phase))` rebuilds only when specific field changes. AsyncValue pattern matching: `data.when(loading: () => ..., data: (r) => ..., error: (e, s) => ...)` for exhaustive async state handling.
- **Impact:** 40% faster feature delivery vs bidirectional
- **Source:** Android UI Layer Guide

### ARC-03 [HIGH] Immutable Data Models
Data classes immutable. copyWith for derivation.
- **Detect:** Mutable data classes with public setters. In-place mutation. Missing equals/hashCode
- **Fix:**
  - Flutter: freezed / built_value
  - Kotlin: data class (val only)
  - Swift: struct
  - RN: TypeScript readonly + Immer
- **Impact:** Mutable models with shared references let one part of the app change state another part is mid-read on, producing bugs that only reproduce under specific timing.
- **Source:** Kotlin Data Classes, Swift Value Types (WWDC), Dart Immutable Data Patterns

### ARC-04 [HIGH] Dependency Injection
Constructor injection preferred. DI container for lifecycle scope.
- **Detect:** Direct `new Service()` in UI. Service locator hiding dependencies. Global singletons without injection
- **Fix:**
  - Flutter: riverpod / get_it
  - Android: Hilt
  - iOS: constructor injection / Environment
  - RN: React Context / providers
- **Impact:** Hardcoded concrete dependencies make a class untestable in isolation — every test drags in the real network/database/platform dependency behind it.
- **Source:** Android DI Guide

### ARC-05 [HIGH] No Business Logic in UI
Zero business rules in widgets/views/composables. UI = display + event forwarding.
- **Detect:** if/else business decisions in build()/render()/body. API calls from UI. Data transformation in UI
- **Fix:** Move to ViewModel or use case. UI maps state to widgets. Events dispatched to ViewModel
- **Impact:** Business rules inside widget/view code duplicate silently across screens that need the same rule, so a fix applied to one screen leaves the others still wrong.
- **Source:** Clean Architecture, SOLID SRP

### ARC-06 [HIGH] State Restoration
Handle process death (Android) and background termination (iOS).
- **Detect:** State lost on process death. Form data lost on background kill. Navigation stack not restored
- **Fix:**
  - Android: SavedStateHandle + rememberSaveable (Compose)
  - iOS: scene state restoration APIs
  - Flutter: RestorationMixin
  - Persist in-progress work to local storage
- **Impact:** Unrecovered process death or background termination discards in-progress form data and navigation state — the user's work disappears with no error to explain why.
- **Source:** Android Architecture, iOS App Lifecycle

### ARC-07 [HIGH] Feature Modularization
Feature modules with clear API boundaries.
- **Detect:** Single app module with everything. Feature coupling. Build times >5 min incremental
- **Fix:** Feature modules with public API. Shared module for common code. Clear dependency graph
- **Impact:** 3x faster builds, 20-30% smaller APK with dynamic delivery
- **Source:** Android Modularization Guide

### ARC-08 [HIGH] Result/Either Error Types
Typed results for recoverable errors. Exceptions for exceptional cases only.
- **Detect:** try-catch for expected errors. Null as error signal. Untyped error propagation
- **Fix:**
  - Kotlin: Result / sealed class
  - Swift: Result<T, E>
  - Dart: Either (dartz/fpdart) / sealed class
  - TS: discriminated unions
- **Impact:** Untyped error propagation forces every caller to guess what can go wrong, so failure paths get skipped and errors surface as unhandled exceptions in production.
- **Source:** Kotlin Result API, Swift Error Handling (Swift Programming Language Guide), Dart Either Pattern

### ARC-09 [HIGH] Defensive API Parsing
Null-safe JSON. Fallback for unexpected shapes. No force-cast.
- **Detect:** Force-unwrap on JSON fields (`!`, `as!`, `.value!`). No fallback for missing fields. FormatException unhandled
- **Fix:** Conditional parsing with defaults. Handle String where Map expected. Validate shape before parsing
- **Impact:** A force-unwrap or unguarded cast on API response data crashes the app the first time the backend sends a null, a missing field, or a shape the client didn't expect.
- **Source:** Postel's Law

### ARC-10 [LOW] Complexity Limits
Cyclomatic complexity <= 15. Method <= 50 lines. Nesting <= 3. Parameters <= 4.
- **Detect:** Functions exceeding limits. Deep nesting. Long parameter lists
- **Fix:** Extract methods. Early returns. Parameter objects. Composed functions
- **Impact:** High-complexity functions are the ones bugs hide in and the ones new contributors are afraid to touch — complexity growth compounds review and onboarding cost over time.
- **Source:** DCM, SonarQube

### ARC-11 [HIGH] Feature-First Directory Structure
Organize by feature, not by technical layer, at the top level.
- **Detect:** Top-level directories split by technical layer only (a global `models/`, `services/`, `screens/`) rather than by feature. A new feature's files scattered across 4+ top-level directories instead of one feature folder.
- **Fix:** Adopt `lib/features/{feature_name}/{data,domain,presentation,widgets}/` — each feature owns its own data/domain/presentation/widgets subtree; shared code lives in a `core/`/`shared/` module. 80%+ of surveyed production Flutter apps use this shape.
- **Impact:** Layer-first structure means adding or removing one feature touches files scattered across the whole tree; feature-first isolates that change to one directory, and deleting a feature means deleting one folder instead of a cross-cutting search.
- **Source:** [Flutter App Architecture Guide](https://docs.flutter.dev/app-architecture)

### ARC-12 [MEDIUM] Two-Layer API Client: Raw Transport Separated From Consumer-Facing Helper
A low-level API client (endpoints, serialization, transport) is wrapped by a separate, higher-level helper that the rest of the app actually calls.
- **Detect:** Screens/view-models calling a raw HTTP/generated-client method directly, with response-shaping, pagination, or retry logic duplicated at each call site. A single class doing both wire-level request construction and app-facing convenience methods.
- **Fix:** Split into a raw client (thin wrapper over the endpoints, one method per endpoint, minimal logic) and a helper/facade layer (composes raw-client calls, shapes responses for the UI, owns pagination/retry) — only the helper is imported outside the data layer.
- **Impact:** Without the split, a transport-level change (new auth header, retry policy, pagination cursor format) requires editing every call site instead of one helper; the split keeps that change to the helper layer alone.
- **Source:** [Flutter App Architecture Guide](https://docs.flutter.dev/app-architecture) — data-layer service/repository separation

---

## Testing

### TST-01 [HIGH] Test Pyramid 70/20/10
70% unit (domain/service/ViewModel), 20% integration (layer interactions), 10% E2E (critical flows).
- **Detect:** Inverted pyramid. No integration tests. Untested ViewModels. Only E2E tests
- **Fix:** Unit test every public domain/service/ViewModel method. Integration with fakes. E2E for critical journeys
- **Impact:** 4x faster releases with pyramid
- **Source:** Android Testing Strategies

### TST-02 [HIGH] >= 80% Meaningful Coverage
CI gate at 80%+. Quality over quantity.
- **Detect:** Coverage < 80%. Tests without assertions. Happy-path-only tests
- **Fix:** CI coverage gate. Branch coverage for critical paths. Test edge cases and errors
- **Note:** 80% meaningful > 95% superficial. Mobile average only 30%
- **Impact:** Below 80% meaningful coverage, regressions in the untested paths ship undetected until a user hits them — the CI gate exists specifically to catch what manual testing misses.
- **Source:** ICSE 2025 Research

### TST-03 [HIGH] Fakes Over Mocks
Deterministic fake implementations. Mocks only for interaction verification.
- **Detect:** Mocks verifying implementation details. Tests breaking on refactor. External deps in tests
- **Fix:** In-memory fake repositories/services. Fakes simulate real behavior. Mocks only for verifying calls were made
- **Impact:** 80% faster tests, refactor-resistant
- **Source:** Flutter Testing, Google Testing Blog

### TST-04 [HIGH] Screenshot/Golden Tests
Visual regression testing for UI.
- **Detect:** No visual regression tests. UI changes undetected
- **Fix:**
  - Android: Compose Preview Screenshot Testing
  - iOS: XCTest snapshot
  - Flutter: matchesGoldenFile
  - Update goldens intentionally
- **Impact:** Without golden/screenshot tests, a layout regression (broken padding, clipped text, wrong color) ships silently because nothing in CI looks at rendered output.
- **Source:** Android Screenshot Testing

### TST-05 [HIGH] No Weakened Assertions
Never skip, mock away, or relax assertions to pass tests.
- **Detect:** `skip: true` on failing tests. Assertions changed to match bugs. Mock replacing tested unit
- **Fix:** Fix code or fix test to validate correct behavior. Every bug fix = regression test
- **Impact:** A weakened assertion or skipped test turns a red build green without fixing anything — the bug it was guarding against ships, and the test suite now lies about coverage.
- **Source:** Kent Beck — Test-Driven Development: By Example, Google Testing Blog

### TST-06 [HIGH] Static Analysis CI Gate
Lint + analyzer must pass in CI.
- **Detect:** No lint/analyze in CI. Suppressed warnings without justification
- **Fix:** CI: format → analyze → test → coverage. Fail on errors
- **Platform:**
  - Flutter: `flutter analyze` + analysis_options.yaml
  - Android: ktlint + detekt
  - iOS: SwiftLint
  - RN: ESLint + TS strict
- **Impact:** With no lint/analyze gate in CI, style and correctness regressions accumulate until a manual cleanup pass becomes unavoidable — the exact cost automation was supposed to prevent.
- **Source:** Flutter Analysis Options, Android ktlint/detekt, SwiftLint, ESLint TypeScript

---

## Performance

### PRF-01 [HIGH] Frame Rate Targets
60fps (16ms). 120fps on high-refresh (8ms). Jank < 5%.
- **Detect:** Dropped frames during scroll/animation. Build > 8ms. Raster > 8ms
- **Fix:** Profile with platform tools. Reduce rebuilds. Const constructors. Offload heavy work to isolate/worker
- **Impact:** Dropped frames during scroll or animation are the most visible, most-complained-about defect class in app-store reviews — users describe it as 'laggy' or 'janky' even when everything else works.
- **Source:** Flutter Perf Metrics, Android Rendering

### PRF-02 [HIGH] Cold Start < 2s
Cold < 2s. Warm < 1s. > 5s is excessive.
- **Detect:** Measure with platform tools. Heavy init on main thread. Blocking network on startup
- **Fix:** Defer non-critical init. Lazy-load features. Minimize main thread work. Platform splash API.
  Cold start optimization pattern (Flutter): `addPostFrameCallback` to defer non-critical services after first frame:
  ```dart
  void main() {
    runApp(const MyApp());
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeNonCriticalServices(); // analytics, remote config, etc.
    });
  }
  ```
- **Impact:** 100ms delay = 1% user loss. 49% of users expect app to open within 2s. 53% abandon apps exceeding 3s.
- **Source:** Android Startup, Flutter TTID/TTFD

### PRF-03 [HIGH] App Size Budget
Track APK/IPA size. Tree-shaking. Remove unused assets.
- **Detect:** APK > 50MB unjustified. Unused assets. No size analysis
- **Fix:** `flutter build --analyze-size`. R8 shrinking. Remove unused packages. WebP/AVIF images
- **Impact:** An oversized binary raises the abandon rate on slow connections and metered data plans, and on some markets pushes the app past a download-size warning threshold users treat as a stop sign.
- **Source:** Android Reduce App Size Guide, Flutter App Size Optimization, Apple App Thinning

### PRF-04 [HIGH] Image Lazy Loading
Images on-demand as scrolled into view. Placeholder during load.
- **Detect:** All images loaded at screen init. No placeholder. High memory from images
- **Fix:** Lazy load with placeholder (shimmer/blurhash). Cache images. Server-side resize for device
- **Impact:** Loading every image at once on a list screen spikes memory and network usage immediately, often triggering an OS memory-pressure kill on lower-end devices before the screen even finishes rendering.
- **Source:** Android Image Loading (Coil/Glide), Flutter Image Best Practices, Apple UIKit Image Optimization

### PRF-05 [HIGH] Efficient List Rendering
Virtualized/recycled list rendering for long lists.
- **Detect:** `ListView` without `.builder` (Flutter), `ScrollView` instead of `FlatList`/`FlashList` (RN), no `RecyclerView` (Android), `List` without lazy loading (SwiftUI). All items built at once
- **Fix:** Flutter: `ListView.builder` / `SliverList`. RN: `FlashList` (Shopify). Android: `LazyColumn` (Compose) / `RecyclerView`. iOS: `LazyVStack` (SwiftUI). Only build visible items + buffer
- **Impact:** 10K+ items without virtualization → jank, OOM, and 60fps failure
- **Source:** Flutter ListView.builder, Android RecyclerView/LazyColumn, Shopify FlashList, Apple LazyVStack

### PRF-06 [HIGH] Memory Leak Prevention
All subscriptions, controllers, and observers properly disposed.
- **Detect:**
  - Flutter: `StreamController` / `AnimationController` / `TextEditingController` without `.dispose()` in `dispose()` method
  - iOS: Closures capturing `self` without `[weak self]`. `NotificationCenter` observers not removed
  - Android: `ViewModel` holding Activity/Fragment reference. `Flow.collect` in wrong lifecycle scope
  - RN: `useEffect` without cleanup function for subscriptions
- **Fix:** Dispose all controllers in `dispose()`. Use `[weak self]` in closures. Collect flows in `repeatOnLifecycle`. Return cleanup from `useEffect`. Profile with platform memory tools
- **Impact:** Memory leaks → OS kills app → data loss and state corruption
- **Source:** Flutter Memory Best Practices, Android Memory Management Guide, Apple Instruments Leaks, MASVS-RESILIENCE

### PRF-07 [HIGH] Battery Optimization
No unnecessary background activity that drains battery.
- **Detect:** Polling intervals < 15 minutes. GPS with `kCLLocationAccuracyBest` / `PRIORITY_HIGH_ACCURACY` always-on. Indefinite wake locks. Continuous sensor reads without user action. Background network requests without `BackgroundTasks` (iOS) / `WorkManager` (Android)
- **Fix:** Use push notifications instead of polling. Significant location change monitoring instead of continuous GPS. Release wake locks promptly. Use platform background task APIs with constraints (charging, wifi). Batch network requests
- **Impact:** Excessive battery drain is #1 reason users uninstall apps
- **Source:** Android Battery Optimization, iOS Energy Efficiency Guide

### PRF-08 [HIGH] Immutable / Static UI Component Optimization
UI components with unchanging inputs must be marked immutable to skip unnecessary rebuilds.
- **Detect:** UI component with all-final/immutable fields not marked as compile-time constant or memoized. Leaf components (spacers, padding, icons, static text) recreated every render cycle without immutability hint
- **Fix:**
  - Flutter: `const` constructor on all eligible widgets (leaf widgets first: SizedBox, Padding, EdgeInsets, Icon, Text with literal)
  - SwiftUI: struct-based views are immutable by default; use `EquatableView` for expensive body computations
  - Compose: `@Stable` / `@Immutable` annotations on data classes passed to composables
  - RN: `React.memo()` wrapper on functional components with stable props
  - Web React: `React.memo()` / `useMemo()` for expensive render subtrees; Vue: `v-once` for static content
- **Impact:** Lowest-cost, highest-impact rebuild optimization across all platforms. Non-immutable leaf widgets rebuild even when inputs are unchanged
- **Source:** Flutter Performance Best Practices (const widgets), React.memo API Reference, Jetpack Compose Stability, SwiftUI EquatableView

### PRF-09 [HIGH] Animation Performance Anti-Patterns
Animations must not trigger expensive layout recalculations or rebuild entire subtrees.
- **Detect:** Opacity/transparency change wrapping complex subtree (triggers full-layer composite / `saveLayer()`). Animation builder/callback rebuilding expensive child every frame. Animation controller without lifecycle sync (vsync / CADisplayLink / Choreographer / requestAnimationFrame). Animating layout-triggering properties (width, height, margin, padding) instead of compositor-only properties (transform, opacity)
- **Fix:**
  - Flutter: `FadeTransition` instead of `Opacity` on complex children. `AnimatedBuilder(child: const ExpensiveWidget(), builder: (_, child) => ...)` to build child once. `TickerProviderStateMixin` for vsync
  - iOS: Animate `CALayer` properties (opacity, transform) instead of view layout. Use `UIView.animate` with `.allowUserInteraction`
  - Android/Compose: `Modifier.graphicsLayer { alpha = ... }` instead of `Modifier.alpha()` on complex subtrees. `RenderEffect` for GPU-side effects
  - RN: `useNativeDriver: true` in Animated API. `Reanimated` worklets for complex gesture-driven animations
  - Web: Animate `transform`/`opacity` only (compositor-only properties). `will-change` hint for known animation targets. `requestAnimationFrame` for frame sync
- **Impact:** Animating layout-triggering properties instead of compositor-only ones forces a full layout+paint pass every frame, turning a decorative animation into the actual cause of the jank users report.
- **Source:** Flutter Animations Overview, iOS Core Animation Programming Guide, Jetpack Compose Animation, React Native Reanimated

### PRF-10 [MEDIUM] Embedded Large Assets Are Subset to Actual Coverage — Offline, Not In-Build
Large bundled static assets (fonts, dictionaries, model files) are reduced to the range the supported languages/character sets actually require, via a manual offline maintenance task with the coverage boundary documented.
- **Detect:** Full multi-megabyte assets bundled where a subset serves the shipped locales; subsetting wired into build/CI (needing network access, slowing every build); no documented statement of what the subset covers.
- **Fix:** Subset assets to the supported coverage; run subsetting as a manual offline task executed only when the source asset changes (it needs network and is slow — keep it out of build/CI); document the resulting coverage boundary explicitly so a locale addition knows to re-run it.
- **Impact:** Full assets inflate download size for every user forever; undocumented subsets are worse — a new locale ships with missing glyphs/entries and nobody knows why.
- **Source:** XR-071 — cross-project experience registry (2026).

---

## Network & Data

### NET-01 [HIGH] Offline-First Source of Truth
Local DB is canonical. Remote is sync target.
- **Detect:** UI reads from network directly. No local persistence. App unusable offline
- **Fix:** Local DB primary read. Background sync. UI reads local. Define conflict strategy
- **Impact:** 35% downtime reduction
- **Source:** Android Offline-First Guide

### NET-02 [HIGH] Exponential Backoff + Jitter
Retry transient failures. Cap retries.
- **Detect:** Fixed-interval retries. No retry on transient. Immediate retry flooding. No max limit
- **Fix:** delay * 2^attempt + jitter. Max 3-5 retries. Cap 30-60s. Distinguish transient vs permanent
- **Impact:** Retrying without backoff during an outage adds client-generated load on top of a struggling backend, turning a partial outage into a full one.
- **Source:** MASVS-NETWORK

### NET-03 [HIGH] Circuit Breaker
Stop calling failing service after threshold.
- **Detect:** Repeated calls to failing endpoint. No failure tracking. Frozen on timeout
- **Fix:** Track failures. Open after N. Half-open on cooldown. Close on success. Show offline UI during open
- **Impact:** With no circuit breaker, every screen that calls a failing endpoint hangs for the full timeout on every attempt, compounding one backend outage into an app-wide stall.
- **Source:** Michael Nygard — Release It!, Microsoft Azure Circuit Breaker Pattern

### NET-04 [HIGH] Cache: TTL + ETag + SWR
Memory -> disk -> network. Stale-while-revalidate.
- **Detect:** No caching. Full fetch every screen. No stale display during revalidation
- **Fix:** LRU memory + disk + network. SWR: serve cached, update background. Respect Cache-Control
- **Impact:** No caching means every screen revisit re-fetches from network, so a slow or flaky connection makes even previously-loaded content reload from scratch every time.
- **Source:** HTTP Caching MDN

### NET-05 [HIGH] Deep Link Fallback & Deferred Linking
Universal Links (iOS) + App Links (Android) with domain verification, plus first-install handling. Store-side domain/AASA verification config is STO-17; this rule covers the runtime linking behavior — unverified schemes, missing fallback, deferred (first-install) linking.
- **Detect:** No deep links. Custom schemes only (unverified). No install fallback
- **Fix:** Verified deep links. Deferred deep linking for first-install. Web fallback
- **Note:** Firebase Dynamic Links being deprecated
- **Impact:** Custom-scheme-only links with no verified domain association and no web fallback break every marketing, email, and cross-app link into the app, and first-install deep links silently lose their destination.
- **Source:** Android App Links Guide, Apple Universal Links Documentation, Flutter Deep Linking

### NET-06 [CRITICAL] Sensitive Data Cache Exclusion
No credentials/PII in HTTP cache, screenshot cache, keyboard cache.
- **Detect:** Sensitive API responses cached. Sensitive fields in autocomplete. Screenshot of sensitive screen in app switcher
- **Fix:** `Cache-Control: no-store` for sensitive endpoints. Disable autocomplete on sensitive fields. FLAG_SECURE / windowScene for app switcher
- **Impact:** Sensitive fields cached in HTTP cache, autocomplete, or the app-switcher screenshot are readable by anything with access to that cache — a shared device, screen-recording malware, or a forensic device image.
- **Source:** MASVS-STORAGE, MASVS-PRIVACY

### NET-07 [HIGH] Sync Status Indicators
Show sync state, last sync time, offline indicator.
- **Detect:** No sync indication. User unaware of data currency. No offline mode indication
- **Fix:** Sync icon/text. "Last synced: X min ago". Offline banner. Pending changes count
- **Impact:** With no sync-status indicator, users can't tell whether what they're looking at is current, and act on stale data believing it's live.
- **Source:** Google Health Stack Sync

---

## Internationalization & Logging

### DEV-01 [HIGH] String Externalization (i18n)
All UI strings in resource files. Zero hardcoded.
- **Detect:**
  - Search for: quoted strings in UI code that are user-visible (not keys, not log messages)
  - Missing localization setup
- **Fix:**
  - Flutter: ARB + flutter_localizations + intl
  - Android: strings.xml
  - iOS: .xcstrings / Localizable.strings
  - RN: react-intl / i18n-js
- **Impact:** Hardcoded strings can't be localized without a code change and a new release, blocking every future market the app wants to expand into.
- **Source:** Flutter Internationalization Guide, Android String Resources, Apple Localization Guide, react-intl

### DEV-02 [HIGH] Locale-Aware Formatting
Dates, numbers, currency formatted per locale.
- **Detect:** Hardcoded date format (MM/DD/YYYY). Hardcoded currency symbol. Manual number formatting
- **Fix:** Use Intl/DateFormat APIs with user locale
- **Impact:** A hardcoded date/number/currency format displays wrong values to every locale that doesn't match the hardcoded convention — e.g. US date format misread as day-first by non-US users.
- **Source:** ICU Formatting Guide, Android DateFormat, Apple NSDateFormatter, Flutter intl Package

### DEV-03 [HIGH] Pluralization Rules
ICU message format. Languages have different rules (EN: 2, AR: 6, Slavic: 4).
- **Detect:** Manual if/else for singular/plural. Hardcoded "1 item"/"X items"
- **Fix:** ICU plural syntax in resource files. Test with complex-plural languages
- **Impact:** Manual singular/plural if-else breaks for any language with more than two plural forms (Arabic has 6, Slavic languages have 4), producing grammatically wrong UI text.
- **Source:** ICU, Unicode CLDR

### DEV-04 [HIGH] Structured Logging
JSON logs. No secrets/PII. Correlation IDs.
- **Detect:** Unstructured log messages. Sensitive data in logs (tokens, passwords, PII). No request correlation
- **Fix:** Structured JSON format. Sanitize sensitive fields. Add correlation IDs. Define log levels (debug/info/warn/error)
- **Impact:** Unstructured logs with embedded PII or secrets turn every log aggregator and crash-reporting dashboard into an unintended data-exposure surface.
- **Source:** OpenTelemetry Specification, Google SRE Book (Monitoring Distributed Systems)

### DEV-05 [HIGH] Three Global Error Hooks Bound Together at Startup
Uncaught async/framework errors are captured by three mechanisms bound together at app start — zone-based catch-all, framework error hook, platform-dispatcher hook — all feeding one central (consent-based) crash reporter.
- **Detect:** Only one or two of the three hooks bound; hooks removed during a refactor; hooks wired to different sinks; business-logic errors routed into the uncaught-error hooks.
- **Fix:** Bind all three at startup (e.g. Flutter: runZonedGuarded + FlutterError.onError + PlatformDispatcher.onError — or the platform's equivalents) and keep them permanently; route all three to the same central consent-based reporter. Scope them strictly to uncaught errors: business-logic failures are handled at their site, never here.
- **Impact:** Each unbound hook is a class of crashes that vanishes without a trace — the app dies, no report is filed, and the team learns about it from store reviews.
- **Source:** XR-175 — cross-project experience registry (2026).

---

## Hybrid & WebView Bridge (conditional — hybrid platform only)

**Activate when** Phase 1 detects a hybrid shell: `capacitor.config.ts` / `capacitor.config.json` / `@capacitor/core` in `package.json` (or a Cordova `config.xml`). Zero checks on native and Flutter/RN projects. Commands below are Capacitor; a Cordova project maps `cap sync` → `cordova prepare`.

The shell is the whole attack surface: web code that would be sandboxed in a browser tab runs here with native plugin access, and the native projects are generated artifacts that go stale silently.

### HYB-01 [CRITICAL] The WebView Loads Local Assets, Not a Remote Origin
Production ships bundled assets over the app scheme; live-reload settings never reach a release build.
- **Detect:** `server.url` set in the committed `capacitor.config.*` (Capacitor's own declaration marks it "not intended for use in production" — it points the shell at a remote origin); `server.cleartext: true`; `server.allowNavigation` carrying a wildcard or a broad domain; `android.webContentsDebuggingEnabled` / `ios.webContentsDebuggingEnabled` true in the release configuration; a single config file with no dev/release split
- **Fix:** remove `server.url` and `cleartext` from the committed config (keep them in a dev-only override applied by the dev script); `allowNavigation` empty, or the exact hosts needed and nothing wider; debugging flags false for release; verify the shipped build with `npx cap doctor` plus a read of the generated native config
- **Impact:** with a remote origin loaded, one XSS on that origin owns every native plugin the app has registered — camera, filesystem, contacts, secure storage. This is the single highest-value finding in a hybrid audit
- **Source:** Capacitor `CapacitorConfig` declarations (`server.url`, `server.cleartext`, `server.allowNavigation`)

### HYB-02 [HIGH] Every Installed Plugin Has At Least One Consumer
A plugin in the manifest is native code, permissions, and store-declared capability compiled into the binary — whether or not any line of web code calls it.
- **Detect:** for each `@capacitor/*` / `capacitor-*` / `cordova-plugin-*` dependency, search the **entire repo** for an import or bridge call (`git grep`, repo-wide — a `src/`-scoped search misses a root entry file and produces a false "unused"); a dependency with zero consumers is the finding. Second half of the same check: a plugin *used* in code but missing from the manifest — the runtime failure only appears on device
- **Fix:** unused → remove the dependency, run `npx cap sync`, then re-check the native permission manifests for the entries it left behind (removing the package does not always remove its merged permissions); used-but-unlisted → add it and sync
- **Impact:** dead plugins add permissions the store listing must justify and the privacy declaration must cover — a permission with no feature behind it is a rejection reason and a privacy claim you cannot defend
- **Source:** same manifest-plus-consumer test as ds-review YAGNI-USAGE; Capacitor plugin registration is generated during `cap sync`

### HYB-03 [HIGH] The Build Chain Runs Web Build → `cap sync` → Native Build
`cap sync` is copy + update in one: it copies the built web assets **and** regenerates native plugin registration. Skipping either half ships a stale shell.
- **Detect:** a release script that runs `cap copy` (assets only) after a dependency change instead of `cap sync`; `cap sync` invoked without a preceding web build, so it copies the previous build's output; native platform directories committed but no sync step in the release path; no `cap doctor` in the pre-release checklist
- **Fix:** fixed chain — web build → `npx cap sync` → native build; `cap copy` only when web assets alone changed and no dependency moved; make the chain one command so the ordering cannot be performed from memory
- **Impact:** the classic failure is invisible in the simulator and fatal on device: the plugin call resolves during development and throws "not implemented" in the shipped build, because registration was never regenerated
- **Source:** Capacitor CLI — `sync` is defined as copy plus update (`cli/src/tasks/sync.ts`)

### HYB-04 [MEDIUM] Native Behaviors Are Handled, Not Inherited From The Browser
A page that behaves correctly in a browser tab still misses the platform contracts the shell is expected to honor.
- **Detect:** no Android hardware back-button handler (back exits the app instead of navigating); safe-area insets unhandled (content under notch / home indicator); no keyboard-resize behavior, so inputs sit behind the keyboard; deep links and app-lifecycle events (background → foreground) not bound in the web layer; browser-only APIs used for storage of anything that must survive an OS cache purge
- **Fix:** bind back-button, lifecycle, and deep-link handlers at shell start; consume safe-area insets in the layout; select an explicit keyboard resize mode; move must-survive data out of WebView-managed storage into a native-backed store
- **Impact:** these are the findings users report as "it feels like a website" — and the back-button one alone is a documented store-review complaint class
- **Source:** platform behaviors the WebView does not supply by default; verified against Capacitor's `CapacitorConfig` platform sections
