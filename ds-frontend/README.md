# ds-frontend

Hardcoded colors, inconsistent spacing, missing focus states, broken dark mode — design systems exist to prevent these, but nobody enforces them in code.

Audits UI/UX design quality across 155 rules, enforces design tokens, generates design systems, and catches WCAG 2.2 AA violations (including all four new-in-2.2 criteria) — for any frontend framework.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-frontend ~/.claude/skills/ds-frontend` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
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
| tokens | Color/spacing/typography/shadow/border/z-index token consistency, palette distinguishability |
| components | Component API, naming, composition, overlays, route liveness, control-action binding, icon system, AI-friendly documentation |
| states | Empty/loading/error/success/disabled/hover/focus/active coverage (error never collapses into empty) |
| ux | Nielsen 10 heuristics, onboarding/first-use flow, activation/time-to-value |
| a11y | WCAG 2.2 AA (incl. all new-in-2.2 criteria), ARIA patterns, keyboard nav, contrast, screen reader |
| responsive | Layout overflow, breakpoints, container queries, fluid typography, multi-column symmetry, print styles, RTL-readiness, Core Web Vitals |
| theming | Dark mode, light-dark(), color-scheme, semantic tokens |

Plus `solid`, `config`, `admin-ui`, and `scheduling` scopes — see SKILL.md for the full table.

## Features

- 155 rules across 6 reference files (design system, components, accessibility, responsive, ux, scheduling — incl. Laws of UX, perceived performance, validation strategy, deceptive-pattern screening, UX writing, IA)
- Supports all UI frameworks: React, Vue, Svelte, Angular, Flutter, RN, SwiftUI, Compose, Electron, Tauri
- Design mode generates W3C DTCG 2025.10 tokens.json, component catalog, and WCAG checklist
- Auto-fixes hardcoded colors, missing ARIA, contrast violations, focus indicators
- AI-discoverable component documentation standard (progressive disclosure architecture)
- Rendered-geometry verification (column symmetry, focus-not-obscured) via in-session browser automation when available
