# UX Design Guidelines

Research-backed UX patterns for mobile and web applications. Platform-agnostic principles with specific implementation guidance.

---

## 1. Button Sizing & Touch Targets

- **Material 3 minimum**: 48dp touch target (visual can be smaller if padding compensates)
- **WCAG 2.5.5 (AAA)**: 44x44 CSS px minimum for interactive elements
- **Apple HIG**: 44pt minimum tap target
- **Recommendation**: All interactive elements (icon buttons, chips, list tiles) must meet 44dp/pt minimum

---

## 2. Color & Theming

- **Dynamic color**: Generate harmonious palette from a single seed color (Material 3 `ColorScheme.fromSeed()` or CSS custom properties)
- **Hardcoded colors break theming**: Use semantic color tokens (`surface`, `onSurface`, `primary`, `onPrimary`) instead of hex values
- **Contrast ratios**: WCAG AA requires 4.5:1 for normal text, 3:1 for large text
- **Color-blind safety**: Never use color alone to convey state. Pair with icons/text (e.g., error = red + error icon)

---

## 3. Information Hierarchy

- **F-pattern reading**: Primary info (title, status) top-left; metadata (duration, cost) secondary
- **Visual weight**: Title > subtitle > caption. Use typographic scale consistently
- **Spacing rhythm**: Consistent spacing (8/12/16/24dp multiples) improves scanability
- **Card density**: 16dp card spacing reduces visual clutter on content lists

---

## 4. Navigation

- **Bottom sheets**: Ideal for contextual actions. Keep < 3 actions per sheet
- **Drag handle**: 60dp width is more discoverable than 40dp
- **Modal vs push**: Use modal (bottom sheet) for preview/quick actions; push navigation for full-screen content
- **Back navigation**: Cancel/close actions should confirm if destructive work is in progress

---

## 5. Empty States

- **First-run**: Large icon (64dp) + title + subtitle + primary CTA. Never leave blank screens
- **After deletion**: Show empty state with re-engagement prompt
- **Illustration hierarchy**: Icon > Title > Subtitle > Action button (vertical stack, centered)
- **Tone**: Encouraging, not apologetic ("No items yet" > "Nothing here")

---

## 6. Error Presentation

| Type | When to Use | Examples |
|------|-------------|---------|
| Inline errors | Form-level or field-level issues | Validation errors, field requirements |
| Snackbar/toast | Transient, recoverable issues | Network retry, file not found |
| Dialog errors | Blocking errors requiring user decision | Insufficient balance, permission denied |

- **Error recovery**: Always provide a clear next action (retry button, go back, contact support)
- **Error padding**: Generous padding (24dp) around error messages improves readability under stress

---

## 7. Accessibility

- **Semantic labels**: Every interactive widget needs screen reader labels
- **Reduced motion**: Check user preference before running animations. Provide static fallback
- **Color contrast**: Use theme-provided color roles; avoid opacity-based text colors below 0.6 alpha
- **Focus order**: Ensure logical tab order matches visual layout
- **Touch targets**: Minimum 44dp/pt on all interactive elements

---

## 8. Microinteractions

| Interaction | Recommendation |
|-------------|---------------|
| Loading states | Progress indicator + descriptive text ("Saving..." not just spinner) |
| Pulse animation | 1500ms duration, ease-in-out curve |
| Scrollbar feedback | Visible scrollbar on long lists provides scroll position awareness |
| Haptic feedback | Consider for primary action start/stop, purchase confirmation |

Micro-interactions increase user engagement by ~23%.

---

## 9. Progressive Disclosure

- Show high-level progress by default; detailed technical info in expandable sections
- Show primary content prominently; metadata as secondary chips/labels
- Technical users get detail on demand; casual users get simple summaries
- Cost/pricing transparency: show estimates early, detailed breakdown on demand

---

## 10. Animation Duration Standards

| Animation Type | Duration |
|----------------|----------|
| Button feedback | 100-200ms |
| Page transitions | 300-400ms |
| Attention-drawing | 200-300ms |
| Loading/pulsing | 1000-1500ms |

---

## 11. Dark Mode

- Use dark gray (#121212) instead of pure black (#000000) — reduces eye strain
- OLED screens consume 63% less power on dark pixels
- Reduce saturation of primary colors, use lighter tones
- 82% of users prefer dark mode

---

## 12. Onboarding

- Keep onboarding steps short and focused (3-5 steps max)
- Show progress indicator (progress bar) to reduce abandonment
- Each step: one key concept only
- Allow skip for returning users

---

## 13. Notification Best Practices

| Daily Notifications | Impact |
|--------------------|--------|
| ≤5 | <1% unsubscribe rate |
| 6-10 | Stable engagement |
| 11-15 | High unsubscribe risk |
| >20 | Users abandon the app |

Push notifications increase engagement by ~88%. Users who enable notifications: 65% return within 30 days.

---

## 14. Web-Specific UX Patterns

### Responsive Design
- Mobile-first approach: design for smallest screen, enhance for larger
- Fluid typography: use `clamp()` for text sizing
- Container queries for component-level responsiveness

### Form UX
- Inline validation as user types (debounced)
- Progressive disclosure for complex forms (multi-step)
- Auto-save drafts to prevent data loss

### Loading Patterns
- Skeleton screens over spinners (perceived performance)
- Optimistic updates for user actions
- Lazy loading for below-the-fold content

### Core Web Vitals Targets
| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤2.5s | ≤4.0s | >4.0s |
| INP | ≤200ms | ≤500ms | >500ms |
| CLS | ≤0.1 | ≤0.25 | >0.25 |

---

## Sources

- [Material Design 3 — Components](https://m3.material.io/components)
- [Material Design 3 — Color System](https://m3.material.io/styles/color)
- [WCAG 2.2 — Target Size](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html)
- [WCAG 2.2 — Contrast Requirements](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [Apple HIG — Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
- [Nielsen Norman Group — Empty States](https://www.nngroup.com/articles/empty-state-interface-design/)
- [Nielsen Norman Group — Error Messages](https://www.nngroup.com/articles/error-message-guidelines/)
- [web.dev — Core Web Vitals](https://web.dev/vitals/)
