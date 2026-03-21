# Web Frontend UX Patterns

Production-ready patterns for web frontend development. Framework-agnostic with framework-specific examples where relevant. Performance-first, accessibility-included.

Last updated: March 2026

---

## Core Web Vitals

Three metrics that directly affect SEO ranking and user experience. Only 48% of mobile pages pass all three (2025 Web Almanac). INP replaced FID in March 2024.

| Metric | Good | Needs Improvement | Poor | What It Measures |
|--------|------|-------------------|------|------------------|
| LCP | < 2.5s | 2.5s - 4.0s | > 4.0s | Largest visible element render time |
| INP | < 200ms | 200ms - 500ms | > 500ms | Worst interaction latency (75th percentile) |
| CLS | < 0.1 | 0.1 - 0.25 | > 0.25 | Visual stability during load and session |

### LCP -- Highest-Impact Fixes

1. **Preload the LCP resource** -- the single most effective fix.
2. Set explicit `width`/`height` on images and use `fetchpriority="high"`.
3. Inline critical CSS, defer the rest.

```html
<!-- Preload hero image with high fetch priority -->
<link rel="preload" as="image" href="/hero.webp" fetchpriority="high">
<img src="/hero.webp" alt="Hero" width="1200" height="600" fetchpriority="high">

<!-- Defer non-critical CSS -->
<link rel="preload" href="/styles.css" as="style" onload="this.rel='stylesheet'">
```

### INP -- Highest-Impact Fixes

43% of sites fail the 200ms threshold -- the most commonly failed metric in 2026.

1. **Break long tasks** with `scheduler.yield()` or `setTimeout`.
2. Avoid layout thrashing (batch DOM reads, then writes).
3. Use `content-visibility: auto` for off-screen content.

```js
// Break long task to keep INP low
async function processItems(items) {
  for (const item of items) {
    processItem(item);
    // Yield to main thread every iteration
    await scheduler.yield();
  }
}

// Fallback for browsers without scheduler.yield
function yieldToMain() {
  return new Promise(resolve => setTimeout(resolve, 0));
}
```

### CLS -- Highest-Impact Fixes

1. **Always set dimensions** on images, videos, iframes, and ads.
2. Use `min-height` on dynamic content slots.
3. Prefer CSS `transform` animations over properties that trigger layout.

```css
/* Reserve space for dynamic content */
.ad-slot { min-height: 250px; }
.avatar { width: 48px; height: 48px; aspect-ratio: 1; }

/* Animate with transform (no layout shift) */
.slide-in {
  transform: translateX(-100%);
  transition: transform 300ms ease-out;
}
```

---

## Responsive Design

### Mobile-First Approach

Start with the smallest viewport, layer up with `min-width` queries. This produces smaller default CSS bundles for mobile devices.

```css
/* Base: mobile */
.grid { display: flex; flex-direction: column; gap: 1rem; }

/* Tablet and up */
@media (min-width: 48rem) {
  .grid { flex-direction: row; flex-wrap: wrap; }
  .grid > * { flex: 1 1 calc(50% - 0.5rem); }
}

/* Desktop */
@media (min-width: 64rem) {
  .grid > * { flex: 1 1 calc(33.33% - 0.67rem); }
}
```

### Fluid Typography with `clamp()`

Eliminates breakpoint-based font size jumps entirely.

```css
:root {
  /* Min 1rem (16px), preferred 2.5vw, max 1.5rem (24px) */
  --fs-body: clamp(1rem, 0.85rem + 0.5vw, 1.25rem);
  --fs-h1:   clamp(2rem, 1.5rem + 2.5vw, 3.5rem);
  --fs-h2:   clamp(1.5rem, 1.2rem + 1.5vw, 2.5rem);
}

body { font-size: var(--fs-body); }
h1   { font-size: var(--fs-h1); }
```

### Container Queries (93%+ Global Support)

Use media queries for page-level (macro) layout. Use container queries for component-level (micro) layout. They complement each other -- container queries are not a replacement for media queries.

```css
/* Define container */
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

/* Component adapts to its container, not the viewport */
@container card (min-width: 400px) {
  .card { display: grid; grid-template-columns: 200px 1fr; }
  .card__image { aspect-ratio: 1; }
}

@container card (min-width: 700px) {
  .card { grid-template-columns: 300px 1fr; gap: 2rem; }
}
```

### Intrinsic Layouts

Let content determine sizing. Prefer `auto-fit`/`auto-fill` with `minmax()`.

```css
/* Cards that auto-wrap without media queries */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(280px, 100%), 1fr));
  gap: 1.5rem;
}
```

---

## Component Architecture

### Atomic Design Hierarchy

| Level | Examples | Scope |
|-------|----------|-------|
| Atoms | Button, Input, Label, Icon | Single HTML element + styles |
| Molecules | SearchField, FormGroup | 2-3 atoms combined |
| Organisms | Header, ProductCard, Form | Complex, self-contained section |
| Templates | PageLayout, DashboardShell | Page structure without data |
| Pages | HomePage, SettingsPage | Templates filled with real data |

### Compound Components Pattern

Components that share implicit state without prop drilling. Works in React, Vue, and Svelte.

```tsx
// React compound component with context
const TabsContext = createContext<{
  activeTab: string;
  setActiveTab: (id: string) => void;
} | null>(null);

function Tabs({ defaultTab, children }: TabsProps) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div role="tablist">{children}</div>
    </TabsContext.Provider>
  );
}

function Tab({ id, children }: TabProps) {
  const { activeTab, setActiveTab } = useContext(TabsContext)!;
  return (
    <button
      role="tab"
      aria-selected={activeTab === id}
      onClick={() => setActiveTab(id)}
    >
      {children}
    </button>
  );
}

function Panel({ id, children }: PanelProps) {
  const { activeTab } = useContext(TabsContext)!;
  if (activeTab !== id) return null;
  return <div role="tabpanel">{children}</div>;
}

// Usage -- clean, declarative API
<Tabs defaultTab="profile">
  <Tab id="profile">Profile</Tab>
  <Tab id="settings">Settings</Tab>
  <Panel id="profile"><ProfileForm /></Panel>
  <Panel id="settings"><SettingsForm /></Panel>
</Tabs>
```

### Render Slots / Composition

Prefer composition (slots/children) over configuration props for flexible components.

```tsx
// Instead of: <Card title="..." subtitle="..." icon={...} />
// Use slots for maximum flexibility:
<Card>
  <Card.Header>
    <Icon name="star" />
    <h3>Title</h3>
  </Card.Header>
  <Card.Body>{content}</Card.Body>
  <Card.Footer><Button>Action</Button></Card.Footer>
</Card>
```

---

## State Management

### Decision Tree

Pick the simplest solution that fits. Move state "up" only when needed.

```
Is the data from the server?
  YES --> Server state (TanStack Query, SWR, Apollo)
  NO  --> Does it need to survive page navigation?
    YES --> URL state (search params, route params)
    NO  --> Is it used by a single component?
      YES --> Local state (useState, ref, $state)
      NO  --> Is it used by 2-3 nearby components?
        YES --> Lift state to nearest common ancestor
        NO  --> Global state (Zustand, Pinia, Svelte stores)
```

### Server State with TanStack Query

```tsx
// Stale-while-revalidate with automatic caching
const { data, isLoading, error } = useQuery({
  queryKey: ['users', filters],
  queryFn: () => fetchUsers(filters),
  staleTime: 5 * 60 * 1000,        // fresh for 5 minutes
  gcTime: 30 * 60 * 1000,           // garbage collect after 30 min
  placeholderData: keepPreviousData, // show old data while fetching
});

// Optimistic mutation
const mutation = useMutation({
  mutationFn: updateUser,
  onMutate: async (newData) => {
    await queryClient.cancelQueries({ queryKey: ['users'] });
    const previous = queryClient.getQueryData(['users']);
    queryClient.setQueryData(['users'], (old) => applyUpdate(old, newData));
    return { previous };
  },
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(['users'], context?.previous); // rollback
  },
  onSettled: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
});
```

### Minimal Global State with Zustand

```ts
// Only put truly global, client-only state here
const useStore = create<AppStore>((set) => ({
  theme: 'system',
  sidebarOpen: false,
  setTheme: (theme) => set({ theme }),
  toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
}));

// Use selectors to avoid unnecessary re-renders
const theme = useStore((s) => s.theme);
```

---

## Form UX

### Validation Timing

| Event | Validate? | Why |
|-------|-----------|-----|
| Focus | No | User hasn't typed yet |
| Input (typing) | Only if field was already invalid | Instant feedback on fixing errors |
| Blur (leave field) | Yes | User finished their attempt |
| Submit | Yes, all fields | Final gate before sending |

### Error Message Rules

- Place error text directly below the field, not in a toast or banner.
- Use `aria-describedby` to connect error to input.
- Start with what went wrong, not a field label. "Must be at least 8 characters" not "Password: invalid."
- Use `aria-invalid="true"` on the input.

```html
<label for="email">Email</label>
<input id="email" type="email"
  aria-describedby="email-error"
  aria-invalid="true" />
<p id="email-error" role="alert" class="error">
  Enter a valid email address (e.g. name@example.com)
</p>
```

### Multi-Step Forms with Persistence

- Save progress to `sessionStorage` on every step change.
- Show a progress indicator (step 2 of 4).
- Allow back navigation without data loss.
- Validate per step, not all at once.

### Layout

Single-column forms outperform multi-column forms in completion rate. Top-aligned labels outperform left-aligned labels on mobile.

---

## Navigation Patterns

### SPA Routing Best Practices

- Announce route changes to screen readers with a live region.
- Restore scroll position on back navigation.
- Update `document.title` on every route change.

```tsx
// Route change announcement (framework-agnostic)
function announceRouteChange(title: string) {
  const el = document.getElementById('route-announcer');
  if (el) el.textContent = `Navigated to ${title}`;
}

// <div id="route-announcer" aria-live="assertive" class="sr-only"></div>
```

### Breadcrumbs with ARIA

```html
<nav aria-label="Breadcrumb">
  <ol>
    <li><a href="/">Home</a></li>
    <li><a href="/products">Products</a></li>
    <li><a href="/products/widgets" aria-current="page">Widgets</a></li>
  </ol>
</nav>
```

### Skip Links

First focusable element on the page. Essential for keyboard users.

```html
<a href="#main-content" class="skip-link">Skip to main content</a>
<!-- ... header/nav ... -->
<main id="main-content" tabindex="-1">
```

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 9999;
  padding: 1rem;
  background: var(--color-bg);
}
.skip-link:focus { top: 0; }
```

---

## Loading Patterns

### Priority Order

| Priority | Pattern | Use Case |
|----------|---------|----------|
| 1 | Skeleton screens | Known layout, data loading |
| 2 | Optimistic updates | User-initiated mutations |
| 3 | Suspense boundaries | Code splitting, lazy loading |
| 4 | Progressive loading | Large lists, images below fold |
| 5 | Spinners | Unknown layout, full page loads only |

### Skeleton Screens Over Spinners

Skeletons reduce perceived load time by ~30%. They communicate structure before data arrives.

```css
.skeleton {
  background: linear-gradient(
    90deg,
    var(--skeleton-base) 25%,
    var(--skeleton-shine) 50%,
    var(--skeleton-base) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}
```

### Optimistic Updates with Rollback

Show the result immediately. Roll back on server error.

```ts
// Pattern: update UI --> send request --> rollback on failure
async function toggleLike(postId: string) {
  const previous = getPostState(postId);
  updatePostState(postId, { liked: !previous.liked }); // instant UI

  try {
    await api.toggleLike(postId);
  } catch {
    updatePostState(postId, previous); // rollback
    showToast('Could not update. Please try again.');
  }
}
```

### Suspense Boundaries

Place boundaries at layout boundaries, not around every component.

```tsx
<Suspense fallback={<DashboardSkeleton />}>
  <Dashboard />
</Suspense>
```

---

## Error Handling UX

### Error Boundary Strategy

Granularity matters. One boundary per independent UI section, not one for the whole app.

```
App
 +-- ErrorBoundary (full page fallback -- last resort)
      +-- Header
      +-- ErrorBoundary (sidebar -- isolate navigation)
      |    +-- Sidebar
      +-- ErrorBoundary (main content -- most likely to fail)
           +-- Content
```

```tsx
// React error boundary with retry
class ErrorBoundary extends Component<Props, State> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    reportError(error, info);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div role="alert">
          <p>Something went wrong.</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Retry Policies

| Error Type | Retry? | Strategy |
|------------|--------|----------|
| Network (timeout, 5xx) | Yes | Exponential backoff, max 3 attempts |
| Auth (401, 403) | No | Redirect to login |
| Validation (400, 422) | No | Show field errors |
| Not found (404) | No | Show not-found page |
| Rate limit (429) | Yes | Respect `Retry-After` header |

### Offline Handling

```ts
// Detect online/offline status
window.addEventListener('online', () => syncPendingActions());
window.addEventListener('offline', () =>
  showBanner('You are offline. Changes will sync when reconnected.')
);
```

---

## Accessibility (WCAG 2.2)

### New in WCAG 2.2 (Key Criteria)

| Criterion | Level | Requirement |
|-----------|-------|-------------|
| 2.4.11 Focus Not Obscured (Minimum) | AA | Focused element not fully hidden by sticky headers/footers |
| 2.4.13 Focus Appearance | AAA | Focus indicator >= 2px, sufficient contrast |
| 2.5.7 Dragging Movements | AA | Drag actions must have non-dragging alternative |
| 2.5.8 Target Size (Minimum) | AA | Interactive targets >= 24x24 CSS px |
| 3.3.7 Redundant Entry | A | Don't ask for same info twice in a flow |
| 3.3.8 Accessible Authentication | AA | No cognitive function test (e.g. CAPTCHA) required |

### Keyboard Navigation Checklist

- All interactive elements reachable via Tab.
- Logical tab order (follows DOM order, avoid positive `tabindex`).
- Custom widgets use arrow keys for internal navigation (roving tabindex).
- Escape closes modals/popups and returns focus to trigger.
- Enter/Space activates buttons and links.

### ARIA Rules

1. **Don't use ARIA if a native element exists.** `<button>` over `<div role="button">`.
2. **All interactive ARIA roles need keyboard support.** `role="tab"` requires arrow key navigation.
3. **Never use `aria-label` on non-interactive elements** unless they are landmarks.
4. **`aria-live="polite"`** for status updates. **`aria-live="assertive"`** for errors only.

### Focus Management

```ts
// After opening a modal
function openModal(modalElement: HTMLElement) {
  modalElement.showModal(); // native <dialog> handles focus trap
}

// After closing, return focus to trigger
function closeModal(modalElement: HTMLElement, triggerElement: HTMLElement) {
  modalElement.close();
  triggerElement.focus();
}

// After dynamic content insertion
function insertContent(container: HTMLElement) {
  container.innerHTML = newContent;
  const heading = container.querySelector('h2');
  heading?.setAttribute('tabindex', '-1');
  heading?.focus();
}
```

---

## Animation

### Meaningful Motion Principles

- Animation should communicate, not decorate.
- Entrance/exit: 150-250ms. Transitions: 200-350ms. Complex sequences: 300-500ms.
- Use ease-out for entrances, ease-in for exits.

### No-Motion-First Approach

Default to no animation. Layer motion on for users who accept it.

```css
/* Animations OFF by default */
.element {
  transition: none;
}

/* Enable only when user hasn't requested reduced motion */
@media (prefers-reduced-motion: no-preference) {
  .element {
    transition: transform 200ms ease-out, opacity 200ms ease-out;
  }
}
```

### CSS Performance Properties

| Property | Triggers | Performance |
|----------|----------|-------------|
| `transform` | Composite only | Best |
| `opacity` | Composite only | Best |
| `filter` | Composite only | Good |
| `background-color` | Paint | Moderate |
| `width`, `height` | Layout + Paint | Avoid animating |
| `top`, `left` | Layout + Paint | Use `transform` instead |

### Timing Reference

```css
:root {
  --duration-instant: 100ms;
  --duration-fast:    150ms;
  --duration-normal:  250ms;
  --duration-slow:    350ms;
  --ease-out:         cubic-bezier(0.16, 1, 0.3, 1);
  --ease-in:          cubic-bezier(0.7, 0, 0.84, 0);
  --ease-in-out:      cubic-bezier(0.45, 0, 0.55, 1);
}
```

---

## Dark Mode

### CSS Custom Properties Architecture

```css
:root {
  color-scheme: light dark;

  /* Using light-dark() -- baseline support since 2024 */
  --color-bg:      light-dark(#ffffff, #121212);
  --color-surface:  light-dark(#f5f5f5, #1e1e1e);
  --color-text:     light-dark(#1a1a1a, #e0e0e0);
  --color-border:   light-dark(#e0e0e0, #333333);
  --color-primary:  light-dark(#0066cc, #4da6ff);
}

body {
  background: var(--color-bg);
  color: var(--color-text);
}
```

### `light-dark()` Function

Switches values based on the computed `color-scheme` property. Cleaner than duplicating rules in `prefers-color-scheme` blocks.

```css
/* Traditional approach -- verbose */
:root { --btn-bg: #0066cc; }
@media (prefers-color-scheme: dark) {
  :root { --btn-bg: #4da6ff; }
}

/* Modern approach with light-dark() -- single declaration */
:root {
  color-scheme: light dark;
  --btn-bg: light-dark(#0066cc, #4da6ff);
}
```

### FOUC Prevention

Inline this script in `<head>` to set the theme before first paint.

```html
<script>
  (function() {
    const saved = localStorage.getItem('theme');
    const system = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    const theme = saved || system;
    document.documentElement.setAttribute('data-theme', theme);
    document.documentElement.style.colorScheme = theme;
  })();
</script>
```

### User Toggle with System Default

```ts
type Theme = 'light' | 'dark' | 'system';

function setTheme(theme: Theme) {
  const resolved = theme === 'system'
    ? (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
    : theme;

  document.documentElement.setAttribute('data-theme', resolved);
  document.documentElement.style.colorScheme = resolved;
  localStorage.setItem('theme', theme);
}

// Listen for system theme changes when set to 'system'
matchMedia('(prefers-color-scheme: dark)')
  .addEventListener('change', () => {
    if (localStorage.getItem('theme') === 'system') setTheme('system');
  });
```

### Image Handling in Dark Mode

```css
/* Reduce brightness of light images in dark mode */
@media (prefers-color-scheme: dark) {
  img:not([src*=".svg"]) {
    filter: brightness(0.9) contrast(1.05);
  }
}

/* Or use <picture> for art-directed dark mode images */
```

```html
<picture>
  <source srcset="/hero-dark.webp" media="(prefers-color-scheme: dark)">
  <img src="/hero-light.webp" alt="Hero image">
</picture>
```

---

## Framework Comparison

Decision matrix for React/Next.js, Vue/Nuxt, and Svelte/SvelteKit as of early 2026.

| Criterion | React + Next.js | Vue + Nuxt | Svelte + SvelteKit |
|-----------|-----------------|------------|---------------------|
| **Bundle size (min+gz)** | ~44 KB runtime | ~33 KB runtime | ~2-5 KB (compiled) |
| **Learning curve** | Steep (hooks, RSC, server actions) | Moderate (Options + Composition API) | Gentle (closest to vanilla JS/HTML) |
| **Ecosystem size** | Largest (npm packages, tooling) | Large (growing, mature) | Smaller but growing fast |
| **SSR/SSG** | Excellent (App Router, RSC) | Excellent (Nuxt 3, Nitro) | Excellent (SvelteKit) |
| **TypeScript** | First-class | First-class | First-class |
| **Performance** | Good (requires optimization) | Good (reactive by default) | Excellent (no virtual DOM) |
| **Hiring pool** | Largest | Moderate | Smallest |
| **Best for** | Large teams, complex apps, enterprise | Mid-size apps, developer experience | Performance-critical, smaller teams |
| **Reactivity model** | Manual (useState/hooks) | Proxy-based (automatic) | Compiler-based ($state runes) |
| **Mobile companion** | React Native | Capacitor / Ionic | Capacitor / Ionic |

### When to Choose What

- **React/Next.js**: Large team, existing React expertise, need maximum ecosystem breadth, enterprise requirements.
- **Vue/Nuxt**: Team values clear conventions, progressive adoption needed, strong preference for SFC developer experience.
- **Svelte/SvelteKit**: Bundle size is critical, smaller team, greenfield project, targeting performance-constrained environments.

---

## Sources

- [Core Web Vitals Explained (2026)](https://www.corewebvitals.io/core-web-vitals)
- [Core Web Vitals 2026: INP, LCP & CLS Optimization](https://www.digitalapplied.com/blog/core-web-vitals-2026-inp-lcp-cls-optimization-guide)
- [2025 In Review: What's New In Web Performance -- DebugBear](https://www.debugbear.com/blog/2025-in-web-performance)
- [INP as Core Web Vital -- web.dev](https://web.dev/blog/inp-cwv-launch)
- [CSS Container Queries -- MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Containment/Container_queries)
- [Container Queries in 2026 -- LogRocket](https://blog.logrocket.com/container-queries-2026/)
- [The State of CSS in 2026](https://www.codercops.com/blog/state-of-css-2026)
- [light-dark() -- MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/color_value/light-dark)
- [light-dark() -- CSS-Tricks](https://css-tricks.com/almanac/functions/l/light-dark/)
- [Dark Mode Guide -- CSS-Tricks](https://css-tricks.com/a-complete-guide-to-dark-mode-on-the-web/)
- [WCAG 2.2 -- W3C](https://www.w3.org/TR/WCAG22/)
- [Container Queries Unleashed -- Josh Comeau](https://www.joshwcomeau.com/css/container-queries-unleashed/)
