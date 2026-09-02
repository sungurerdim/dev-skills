# Generate Detail — ds-test Phase 2a

Client-side scenario coverage and the approximate unit/integration/E2E distribution by project type. Loaded when Phase 2a runs.

**Client-side test scenarios (platform = mobile / web SPA / desktop):**

| Category | Required scenarios |
|----------|-------------------|
| Responsive layout | Viewport profiles 320dp / 375dp / 412dp / 744dp / 1024dp (minimum); portrait + landscape; no layout overflow |
| Font scaling | 0.8× / 1.0× / 1.3× system font scale; text readable, layouts intact |
| Theme | Light + dark mode render correctly; no hardcoded colors bypassing theme system |
| Accessibility | Screen reader (TalkBack / VoiceOver / Narrator / NVDA) traversal; all interactive elements have a11y labels; error states announced |

**Test ratio guideline (approximate distribution by project type — not simultaneous minimums):**

| Type | Unit | Component/Integration | E2E |
|------|------|-----------------------|-----|
| Mobile | ~70% | ~20% | ~10% |
| Web SPA | ~60% | ~25% | ~15% |
| API | ~60% | ~30% | ~10% |
| Library | ~80% | ~15% | ~5% |
