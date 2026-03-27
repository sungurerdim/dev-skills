# ds-frontend

Hardcoded colors, inconsistent spacing, missing focus states, broken dark mode — design systems exist to prevent these, but nobody enforces them in code.

Audits UI/UX design quality across 45 rules, enforces design tokens, generates design systems, and catches WCAG 2.2 violations — for any frontend framework.

## Install

```bash
cp -r ds-frontend ~/.claude/skills/ds-frontend
```

## Use

```
/ds-frontend                         # Audit all scopes
/ds-frontend --mode=audit+fix        # Audit and auto-fix CAT-1
/ds-frontend --mode=design           # Generate design system (tokens.json, catalog, a11y checklist)
/ds-frontend --scope=a11y            # Accessibility audit only
/ds-frontend --scope=tokens,theming  # Design token + dark mode audit
/ds-frontend --check                 # Report only, no modifications
```

## Scopes

| Scope | What It Covers |
|-------|---------------|
| tokens | Color/spacing/typography/shadow/border token consistency |
| components | Component API, naming, composition, AI-friendly documentation |
| states | Empty/loading/error/success/disabled/hover/focus/active coverage |
| a11y | WCAG 2.2 AA, ARIA patterns, keyboard nav, contrast, screen reader |
| responsive | Layout overflow, breakpoints, container queries, fluid typography |
| theming | Dark mode, light-dark(), color-scheme, semantic tokens |

## Features

- 45 rules across 4 reference files (design system, components, accessibility, responsive)
- Supports all UI frameworks: React, Vue, Svelte, Angular, Flutter, RN, SwiftUI, Compose, Electron, Tauri
- Design mode generates W3C DTCG 2025.10 tokens.json, component catalog, and WCAG checklist
- Auto-fixes hardcoded colors, missing ARIA, contrast violations, focus indicators
- AI-discoverable component documentation standard (progressive disclosure architecture)
