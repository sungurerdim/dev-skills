# Flutter Architecture Patterns

Research-backed architecture patterns from 10+ production open-source Flutter apps (73k+ stars combined). Universal patterns applicable to any Flutter project.

---

## Executive Summary

Modern production Flutter apps converge on: **Riverpod state management, Clean Architecture layered separation, offline-first strategies, and Material Design 3 theming**.

---

## Section 1: Production App Architecture Analysis

### AppFlowy — Notion Alternative

**GitHub**: AppFlowy-IO/AppFlowy | **Stars**: 73k+ | **Stack**: Flutter + Rust (FFI)

| Aspect | Detail |
|--------|--------|
| Architecture | Hybrid Flutter + Rust, Event-based RPC + Protobuf |
| State Management | Command/event pattern (Flutter → Rust, Notifications Rust → Flutter) |
| Database | SQLite metadata + CollabKVDB (CRDT-based collaboration) |
| Key Innovation | Plugin architecture, CRDT-based real-time collaboration, self-hostable |

**Takeaway**: "Data Privacy First" philosophy with local-first architecture and native FFI performance.

---

### Immich — Google Photos Alternative

**GitHub**: immich-app/immich | **Stack**: Flutter + Node.js/NestJS

| Aspect | Detail |
|--------|--------|
| Mobile Architecture | MVVM-inspired + Riverpod providers |
| State Management | Riverpod + async providers |
| Local DB | Isar Database (high-performance NoSQL) |
| Backend | Hexagonal Architecture (repositories → services → controllers) |
| Sync | Checksum-based duplicate detection, album synchronization |

**Takeaway**: Riverpod + Isar combination with hexagonal backend architecture. Checksum-based deduplication applicable to any media-heavy app.

---

### Spotube — Spotify Client

**GitHub**: KRTirtho/spotube | **Stack**: Flutter + Riverpod + Hooks

| Aspect | Detail |
|--------|--------|
| State Management | flutter_riverpod + flutter_hooks |
| HTTP Client | Dio |
| Local DB | Drift (SQLite) or flutter_cache_manager |
| Audio | just_audio + audio_service + audio_session |
| Innovation | Plugin architecture, community extensions |

**Takeaway**: Riverpod + Hooks combination provides clean reactive patterns for media apps.

---

### Wonderous — Google Flutter Showcase

**GitHub**: gskinnerTeam/flutter-wonderous-app | **By**: gskinner (Google partner)

| Aspect | Detail |
|--------|--------|
| Focus | Visual fidelity, effects, transitions |
| Animation | Custom scroll patterns, rich animations, custom graphics |
| Accessibility | Foregrounded throughout development |
| Platforms | iOS (Impeller), Android, Web (WASM), macOS, Windows |

**Takeaway**: Reference-quality animation and transition patterns. Custom scroll patterns for rich UX.

---

### Ente — Encrypted Cloud Storage

**GitHub**: ente-io/ente | **Stack**: Flutter + Go + Rust + TypeScript (Monorepo)

| Aspect | Detail |
|--------|--------|
| Security | Audited by Cure53, Symbolic Software, Fallible |
| Encryption | End-to-end encryption (E2EE) |
| Secure Storage | flutter_secure_storage (Keychain iOS, EncryptedSharedPreferences Android) |
| License | AGPL-3.0 |

**Takeaway**: Encryption patterns and security audit approach. flutter_secure_storage usage patterns directly applicable.

---

### Finamp — Jellyfin Music Player

**GitHub**: UnicornsOnLSD/finamp | **Stack**: Flutter + Hive

| Aspect | Detail |
|--------|--------|
| Database | Hive (local data persistence) |
| API Layer | Low-level (jellyfin_api) + user-facing (jellyfin_api_helper) |
| Offline | Download management, transcoded downloads |
| Code Generation | Hive, json_serializable; generated files committed |

**Takeaway**: Two-layer API abstraction pattern (raw API + helper). Download management patterns reusable for any content-heavy app.

---

### Signal — Encrypted Messaging (Kotlin/Swift)

**GitHub**: signalapp/Signal-Android | **Stack**: Kotlin + Java (Android), Swift (iOS)

| Aspect | Detail |
|--------|--------|
| Android | Kotlin 63.3%, Java 36.4% |
| iOS Architecture | UI → Service (Singleton managers) → Storage (GRDB) → DB (SQLCipher) → Network |
| Crypto | Rust libsignal, Signal Protocol, Double Ratchet, Perfect Forward Secrecy |
| Backend | Java + Dropwizard, Redis clusters |

**Takeaway**: Layered architecture (UI → Service → Storage → DB → Network) and minimal data collection philosophy. Privacy by design = minimal data retention, not just encryption.

---

## Section 2: Universal Improvement Patterns

### Feature-First Directory Structure

```
lib/features/
  {feature_name}/
    data/         # Repository implementations
    domain/       # Use cases, entities
    presentation/ # Screens, widgets
    widgets/      # Feature-specific widgets
```

80%+ of modern projects adopt feature-first. Simplifies adding/removing features.

### State Management: Riverpod Optimization

```dart
// Avoid — rebuilds on any state change
final job = ref.watch(someProvider);

// Prefer — rebuilds only when specific field changes
final phase = ref.watch(
  someProvider.select((state) => state.phase),
);
```

### AsyncValue Pattern Matching

```dart
data.when(
  loading: () => LoadingWidget(),
  data: (result) => ContentWidget(result),
  error: (err, stack) => ErrorWidget(err),
);
```

### Cold Start Optimization

Target: TTID <2s, TTFD <4s

```dart
void main() {
  runApp(const MyApp());
  WidgetsBinding.instance.addPostFrameCallback((_) {
    _initializeNonCriticalServices();
  });
}
```

49% of users expect app to open within 2 seconds. 53% abandon apps exceeding 3 seconds.

### Performance Quick Wins

| Pattern | Impact | Complexity |
|---------|--------|------------|
| `const` constructors on static widgets | Rebuild prevention | Low |
| `Container(color: X.withOpacity(0.5))` over `Opacity` widget | Avoids `saveLayer()` | Low |
| `AnimatedBuilder` with `child` parameter | Single build, reuse in animation frames | Low |
| Riverpod `select()` | Targeted rebuilds only | Low |

### Offline-First: Repository Pattern with Streams

```dart
class ContentRepository {
  Stream<List<Item>> getItems() async* {
    // Serve cached data first
    final cached = await _localDb.fetchItems();
    yield cached;

    // Then fetch fresh data from server
    try {
      final fresh = await _api.getItems();
      await _localDb.updateItems(fresh);
      yield fresh;
    } catch (e) {
      // Network error — user already sees cached data
    }
  }
}
```

### Privacy-First UX: Trust Indicators

| Location | Indicator |
|----------|-----------|
| Auth screen | "End-to-end encrypted" badge |
| Data processing screen | "Your data is not stored on servers" micro-text |
| Results screen | Encryption lock icon + explanation |
| Settings | Data transparency panel (what data is collected) |

### Just-In-Time Privacy Disclosure

Show privacy context at permission request time:

```
Before requesting microphone permission:
"Your voice is only used temporarily during processing and
permanently deleted after completion."
```

### Micro-interactions

| Interaction | Recommendation |
|-------------|---------------|
| Primary action start/stop | Haptic feedback (medium impact) |
| Purchase confirmation | Haptic feedback + success animation |
| Task completion | Check animation or confetti |
| File upload | Progress ring + percentage |

Micro-interactions increase user engagement by ~23% (Google Play Store data).

### Animation Duration Standards

| Animation Type | Duration |
|----------------|----------|
| Button feedback | 100-200ms |
| Page transitions | 300-400ms |
| Attention-drawing | 200-300ms |
| Loading/pulsing | 1000-1500ms |

### Dark Mode Rules

- Use dark gray (#121212) instead of pure black (#000000) — reduces eye strain
- OLED screens consume 63% less power on dark pixels
- Reduce saturation of primary colors, use lighter tones
- 82% of users use dark mode

---

## Section 3: Reference App Summary

| App | Stack | GitHub Stars | Key Lesson |
|-----|-------|-------------|------------|
| AppFlowy | Flutter + Rust | 73k+ | Plugin architecture, CRDT collaboration, FFI performance |
| Immich | Flutter + NestJS | 60k+ | Riverpod + Isar, hexagonal backend, checksum sync |
| Spotube | Flutter + Riverpod | 35k+ | Riverpod + Hooks, audio_service, plugin system |
| Ente | Flutter + Go + Rust | 25k+ | E2EE, security audits, flutter_secure_storage |
| Wonderous | Flutter | 4k+ | Animation quality, custom scroll, a11y focus |
| Finamp | Flutter + Hive | 4k+ | Two-layer API, offline download management |
| BlackHole | Flutter | 12k+ | 15+ language support, 320kbps audio, open source |
| Signal | Kotlin/Swift | 26k+ | Minimal data collection, layered architecture, E2EE |
| Joplin | Electron + RN | 43k+ | Delta-based sync, AES-256, plugin API |
| Bitwarden | C# Xamarin | 35k+ | Client-side encryption, PBKDF2, open audit |

---

## Section 4: Common Principles Across Successful Apps

1. **State Management**: Riverpod (modern) or BLoC (mature) — both provide testability and scalability
2. **Architecture**: Clean Architecture or Hexagonal Architecture — clear layer separation
3. **Database**: Isar (simple) or Drift (complex) with offline-first strategy
4. **Navigation**: GoRouter — flexibility and deep linking
5. **Testing**: Unit + Widget tests (80%+ coverage)
6. **UI**: Material Design 3 + responsive design
7. **Security**: flutter_secure_storage + E2EE where applicable
8. **DI**: GetIt service locator or Riverpod DI
9. **Accessibility**: Semantic widgets + screen reader testing
10. **CI/CD**: GitHub Actions for automated test and build

### Anti-Patterns to Avoid

- Single-layer architecture (everything in main.dart)
- No test strategy
- Hard-coded dimensions/values
- Global mutable state
- Ignoring accessibility
- Weak error handling
- Missing offline support in data-centric apps
- Insufficient encryption for sensitive data

---

## Sources

### Official Documentation
- [Flutter App Architecture Guide](https://docs.flutter.dev/app-architecture)
- [Material Design 3 for Flutter](https://m3.material.io/develop/flutter)
- [Flutter Performance Best Practices](https://docs.flutter.dev/perf/best-practices)
- [Flutter Accessibility](https://docs.flutter.dev/accessibility-and-localization/accessibility)
- [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/)

### Architecture & State Management
- [Riverpod Official](https://riverpod.dev/)
- [riverpod_generator](https://pub.dev/packages/riverpod_generator)
- [Flutter Project Structure - CodeWithAndrea](https://codewithandrea.com/articles/flutter-project-structure/)

### Performance & UX
- [Offline-First Support](https://docs.flutter.dev/app-architecture/design-patterns/offline-first)
- [Micro-interaction Examples](https://userpilot.com/blog/micro-interaction-examples/)
- [Privacy-First UX Design](https://medium.com/@harsh.mudgal_27075/privacy-first-ux-design-systems-for-trust-9f727f69a050)
