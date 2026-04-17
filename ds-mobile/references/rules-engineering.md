# Rules: Architecture, Testing, Performance, Network & Internationalization

Rules for audit/fix/create modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Architecture & Code Quality** | ARC-01–10 (3 CRITICAL, 6 HIGH, 1 LOW) | ~12 |
| **Testing** | TST-01–06 (1 CRITICAL, 5 HIGH) | ~100 |
| **Performance** | PRF-01–09 (1 CRITICAL, 8 HIGH) | ~160 |
| **Network & Data** | NET-01–07 (2 CRITICAL, 5 HIGH) | ~214 |
| **Internationalization & Logging** | DEV-04–06, DEV-09 (4 HIGH) | ~262 |

---

## Architecture & Code Quality

### ARC-01 [CRITICAL] Clean Architecture Layers
Presentation (UI + ViewModel) / Domain (use cases) / Data (repositories). Dependencies inward only.
- **Detect:**
  - Business logic (if/else decisions, calculations, validation) in UI widgets/views/composables
  - Data access (API calls, DB queries) in UI layer
  - Circular dependencies between layers
  - Search for: `http.get`, `dio.`, `fetch(`, `Retrofit`, `Room` in UI/presentation files
- **Fix:** Extract logic to use cases (domain layer). Create repository interfaces in domain, implement in data. UI observes ViewModel state only
- **Production examples:** AppFlowy (73k+ stars) uses plugin architecture with event-based RPC + Protobuf across Flutter/Rust FFI boundary. Immich (60k+ stars) uses MVVM + Riverpod providers with hexagonal backend (repositories -> services -> controllers). Signal uses layered architecture: UI -> Service (singleton managers) -> Storage -> DB -> Network.
- **Source:** Android Architecture Guide, Flutter Architecture

### ARC-02 [CRITICAL] Unidirectional Data Flow
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
- **Source:** Kotlin Data Classes, Swift Value Types (WWDC), Dart Immutable Data Patterns

### ARC-04 [HIGH] Dependency Injection
Constructor injection preferred. DI container for lifecycle scope.
- **Detect:** Direct `new Service()` in UI. Service locator hiding dependencies. Global singletons without injection
- **Fix:**
  - Flutter: riverpod / get_it
  - Android: Hilt
  - iOS: constructor injection / Environment
  - RN: React Context / providers
- **Source:** Android DI Guide

### ARC-05 [CRITICAL] No Business Logic in UI
Zero business rules in widgets/views/composables. UI = display + event forwarding.
- **Detect:** if/else business decisions in build()/render()/body. API calls from UI. Data transformation in UI
- **Fix:** Move to ViewModel or use case. UI maps state to widgets. Events dispatched to ViewModel
- **Source:** Clean Architecture, SOLID SRP

### ARC-06 [CRITICAL] State Restoration
Handle process death (Android) and background termination (iOS).
- **Detect:** State lost on process death. Form data lost on background kill. Navigation stack not restored
- **Fix:**
  - Android: SavedStateHandle + rememberSaveable (Compose)
  - iOS: scene state restoration APIs
  - Flutter: RestorationMixin
  - Persist in-progress work to local storage
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
- **Source:** Kotlin Result API, Swift Error Handling (Swift Programming Language Guide), Dart Either Pattern

### ARC-09 [HIGH] Defensive API Parsing
Null-safe JSON. Fallback for unexpected shapes. No force-cast.
- **Detect:** Force-unwrap on JSON fields (`!`, `as!`, `.value!`). No fallback for missing fields. FormatException unhandled
- **Fix:** Conditional parsing with defaults. Handle String where Map expected. Validate shape before parsing
- **Source:** Postel's Law

### ARC-10 [LOW] Complexity Limits
Cyclomatic complexity <= 15. Method <= 50 lines. Nesting <= 3. Parameters <= 4.
- **Detect:** Functions exceeding limits. Deep nesting. Long parameter lists
- **Fix:** Extract methods. Early returns. Parameter objects. Composed functions
- **Source:** DCM, SonarQube

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
- **Source:** Android Screenshot Testing

### TST-05 [CRITICAL] No Weakened Assertions
Never skip, mock away, or relax assertions to pass tests.
- **Detect:** `skip: true` on failing tests. Assertions changed to match bugs. Mock replacing tested unit
- **Fix:** Fix code or fix test to validate correct behavior. Every bug fix = regression test
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
- **Source:** Flutter Analysis Options, Android ktlint/detekt, SwiftLint, ESLint TypeScript

---

## Performance

### PRF-01 [HIGH] Frame Rate Targets
60fps (16ms). 120fps on high-refresh (8ms). Jank < 5%.
- **Detect:** Dropped frames during scroll/animation. Build > 8ms. Raster > 8ms
- **Fix:** Profile with platform tools. Reduce rebuilds. Const constructors. Offload heavy work to isolate/worker
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
- **Source:** Android Reduce App Size Guide, Flutter App Size Optimization, Apple App Thinning

### PRF-04 [HIGH] Image Lazy Loading
Images on-demand as scrolled into view. Placeholder during load.
- **Detect:** All images loaded at screen init. No placeholder. High memory from images
- **Fix:** Lazy load with placeholder (shimmer/blurhash). Cache images. Server-side resize for device
- **Source:** Android Image Loading (Coil/Glide), Flutter Image Best Practices, Apple UIKit Image Optimization

### PRF-05 [HIGH] Efficient List Rendering
Virtualized/recycled list rendering for long lists.
- **Detect:** `ListView` without `.builder` (Flutter), `ScrollView` instead of `FlatList`/`FlashList` (RN), no `RecyclerView` (Android), `List` without lazy loading (SwiftUI). All items built at once
- **Fix:** Flutter: `ListView.builder` / `SliverList`. RN: `FlashList` (Shopify). Android: `LazyColumn` (Compose) / `RecyclerView`. iOS: `LazyVStack` (SwiftUI). Only build visible items + buffer
- **Impact:** 10K+ items without virtualization → jank, OOM, and 60fps failure
- **Source:** Flutter ListView.builder, Android RecyclerView/LazyColumn, Shopify FlashList, Apple LazyVStack

### PRF-06 [CRITICAL] Memory Leak Prevention
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
- **Source:** Flutter Animations Overview, iOS Core Animation Programming Guide, Jetpack Compose Animation, React Native Reanimated

---

## Network & Data

### NET-01 [CRITICAL] Offline-First Source of Truth
Local DB is canonical. Remote is sync target.
- **Detect:** UI reads from network directly. No local persistence. App unusable offline
- **Fix:** Local DB primary read. Background sync. UI reads local. Define conflict strategy
- **Impact:** 35% downtime reduction
- **Source:** Android Offline-First Guide

### NET-02 [HIGH] Exponential Backoff + Jitter
Retry transient failures. Cap retries.
- **Detect:** Fixed-interval retries. No retry on transient. Immediate retry flooding. No max limit
- **Fix:** delay * 2^attempt + jitter. Max 3-5 retries. Cap 30-60s. Distinguish transient vs permanent
- **Source:** MASVS-NETWORK

### NET-03 [HIGH] Circuit Breaker
Stop calling failing service after threshold.
- **Detect:** Repeated calls to failing endpoint. No failure tracking. Frozen on timeout
- **Fix:** Track failures. Open after N. Half-open on cooldown. Close on success. Show offline UI during open
- **Source:** Michael Nygard — Release It!, Microsoft Azure Circuit Breaker Pattern

### NET-04 [HIGH] Cache: TTL + ETag + SWR
Memory -> disk -> network. Stale-while-revalidate.
- **Detect:** No caching. Full fetch every screen. No stale display during revalidation
- **Fix:** LRU memory + disk + network. SWR: serve cached, update background. Respect Cache-Control
- **Source:** HTTP Caching MDN

### NET-05 [HIGH] Deep Linking
Universal Links (iOS) + App Links (Android) with domain verification.
- **Detect:** No deep links. Custom schemes only (unverified). No install fallback
- **Fix:** Verified deep links. Deferred deep linking for first-install. Web fallback
- **Note:** Firebase Dynamic Links being deprecated
- **Source:** Android App Links Guide, Apple Universal Links Documentation, Flutter Deep Linking

### NET-06 [CRITICAL] Sensitive Data Cache Exclusion
No credentials/PII in HTTP cache, screenshot cache, keyboard cache.
- **Detect:** Sensitive API responses cached. Sensitive fields in autocomplete. Screenshot of sensitive screen in app switcher
- **Fix:** `Cache-Control: no-store` for sensitive endpoints. Disable autocomplete on sensitive fields. FLAG_SECURE / windowScene for app switcher
- **Source:** MASVS-STORAGE, MASVS-PRIVACY

### NET-07 [HIGH] Sync Status Indicators
Show sync state, last sync time, offline indicator.
- **Detect:** No sync indication. User unaware of data currency. No offline mode indication
- **Fix:** Sync icon/text. "Last synced: X min ago". Offline banner. Pending changes count
- **Source:** Google Health Stack Sync

---

## Internationalization & Logging

### DEV-04 [HIGH] String Externalization (i18n)
All UI strings in resource files. Zero hardcoded.
- **Detect:**
  - Search for: quoted strings in UI code that are user-visible (not keys, not log messages)
  - Missing localization setup
- **Fix:**
  - Flutter: ARB + flutter_localizations + intl
  - Android: strings.xml
  - iOS: .xcstrings / Localizable.strings
  - RN: react-intl / i18n-js
- **Source:** Flutter Internationalization Guide, Android String Resources, Apple Localization Guide, react-intl

### DEV-05 [HIGH] Locale-Aware Formatting
Dates, numbers, currency formatted per locale.
- **Detect:** Hardcoded date format (MM/DD/YYYY). Hardcoded currency symbol. Manual number formatting
- **Fix:** Use Intl/DateFormat APIs with user locale
- **Source:** ICU Formatting Guide, Android DateFormat, Apple NSDateFormatter, Flutter intl Package

### DEV-06 [HIGH] Pluralization Rules
ICU message format. Languages have different rules (EN: 2, AR: 6, Slavic: 4).
- **Detect:** Manual if/else for singular/plural. Hardcoded "1 item"/"X items"
- **Fix:** ICU plural syntax in resource files. Test with complex-plural languages
- **Source:** ICU, Unicode CLDR

### DEV-09 [HIGH] Structured Logging
JSON logs. No secrets/PII. Correlation IDs.
- **Detect:** Unstructured log messages. Sensitive data in logs (tokens, passwords, PII). No request correlation
- **Fix:** Structured JSON format. Sanitize sensitive fields. Add correlation IDs. Define log levels (debug/info/warn/error)
- **Source:** OpenTelemetry Specification, Google SRE Book (Monitoring Distributed Systems)
