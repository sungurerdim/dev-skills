# /ds-frontend

Hardcoded colors, inconsistent spacing, missing focus states, broken dark mode — design systems exist to prevent these. This skill enforces them in code.

**Frontend Design Quality** — Design system audit, token enforcement, component states, accessibility, responsive layout, theming.

## Triggers

- User runs `/ds-frontend`
- User asks to audit UI quality, check design system, review components, review frontend
- User asks about accessibility, WCAG, contrast, dark mode, responsive, design tokens
- User asks to create or generate a design system, design tokens
- Project contains frontend framework indicators (React, Vue, Svelte, Angular, Flutter, RN, SwiftUI, Compose)

## Contract

- Audits UI/UX design quality in code — stays clear of business logic and backend
- Applies to all UI platforms: web (React/Vue/Svelte/Angular), mobile (Flutter/RN/SwiftUI/Compose), desktop (Electron/Tauri)
- Standalone. Uses blueprint/.ds-findings.md when available; own analysis when absent.
- FRC+DSC enforced.
- Only modifies UI-layer code (styles, components, tokens, ARIA) — business logic stays untouched

## Arguments

| Flag | Effect |
|------|--------|
| `--mode=<mode>` | `audit`, `audit+fix`, `design` |
| `--scope=<scopes>` | Comma-separated: tokens, components, states, a11y, responsive, theming, or `all` |
| `--framework=<f>` | Override: `react`, `vue`, `svelte`, `angular`, `flutter`, `swiftui`, `compose`, `rn` |
| `--check` | Report only, zero modifications |

Without flags: present mode selection to the user.

## Scopes

| Scope | Covers | Reference |
|-------|--------|-----------|
| tokens | Color/spacing/typography/shadow/border token consistency, hardcoded value detection | rules-design-system.md |
| components | Component API quality, naming, composition, reuse, AI-friendly docs | rules-components.md |
| states | Empty/loading/error/success/disabled/hover/focus/active state coverage | rules-components.md |
| a11y | WCAG 2.2 AA, ARIA patterns (APG), keyboard nav, contrast, screen reader | rules-accessibility.md |
| responsive | Layout overflow, breakpoints, container queries, fluid typography | rules-responsive.md |
| theming | Dark mode, light-dark(), color-scheme, semantic tokens, theme switching | rules-design-system.md |

Default: all scopes.

## Modes

| Mode | Behavior |
|------|----------|
| `audit` | Scan and report only — no changes |
| `audit+fix` | Scan, report, fix CAT-1 findings (hardcoded->token, missing ARIA, contrast fix, focus style) |
| `design` | Generate design system artifacts: tokens.json (W3C DTCG 2025.10), component catalog, a11y checklist |

## Execution Flow

```
Detect -> [Configure] -> Scan -> Report -> [Fix] -> [Needs-Approval] -> [Design] -> Summary
```

### Phase 1: Detect

1. **Framework detection.**

   | Framework | Detection |
   |-----------|-----------|
   | React | `package.json` with `react` dependency |
   | Vue | `package.json` with `vue` dependency |
   | Svelte | `package.json` with `svelte` dependency |
   | Angular | `package.json` with `@angular/core` dependency |
   | Flutter | `pubspec.yaml` with `flutter:` section |
   | React Native | `package.json` with `react-native` dependency |
   | SwiftUI | `*.swift` files importing `SwiftUI` |
   | Compose | `build.gradle` with `compose` dependencies |
   | Electron/Tauri | `package.json` with `electron` or `@tauri-apps/api` |
   | Plain HTML/CSS | `*.html` + `*.css` files without framework |

2. **Findings file check:** `.ds-findings.md` with fresh `git_hash` → read findings matching frontend scopes. Use verified findings to skip redundant analysis. Stale or absent → run own full analysis.

3. **IDU:** Profile → Type+Stack, Config.priorities, Current Scores. Findings(tokens, components, states, a11y, responsive, theming) → verify + use. Absent → own analysis.

4. **Design system detection.** Search for existing token/theme sources:
   - CSS: custom properties (`:root { --color-*`), Tailwind config, CSS modules theme
   - JS/TS: styled-components ThemeProvider, Emotion theme, MUI theme, Chakra theme
   - Flutter: ThemeData, ColorScheme
   - SwiftUI: Color assets, custom theme extensions
   - Compose: MaterialTheme, custom theme objects
   - Files: `tokens.json`, `tokens.yaml`, `design-tokens.*`

5. **Mode selection.** Ask user or use flags: Audit Only / Audit & Fix / Design / Custom.

6. **Scope parsing.** Map selection to reference files. Default: all scopes.

**Gate:** Framework identified, design system state cataloged (exists/partial/absent), mode and scope confirmed.

### Phase 2: Configure [SKIP if single scope audit]

1. **Design system inventory:** Catalog color token count/naming, spacing scale, typography count, shadow levels, border radii.
2. **Component pattern detection:** Search component directories, naming conventions, barrel exports, shared library.
3. **A11y tooling detection:** Search for axe-core, eslint-plugin-jsx-a11y, @angular-eslint/eslint-plugin-template, flutter_lints accessibility rules.

**Gate:** Design system landscape mapped, component patterns identified.

### Phase 3: Scan

Load matching reference file for each in-scope domain:

| Scope | Reference File |
|-------|---------------|
| tokens, theming | [rules-design-system.md](references/rules-design-system.md) |
| components, states | [rules-components.md](references/rules-components.md) |
| a11y | [rules-accessibility.md](references/rules-accessibility.md) |
| responsive | [rules-responsive.md](references/rules-responsive.md) |

**Large scope (3+ scopes):** Progress checklist + persistent findings artifact. Max 2 parallel scans.

**Per scope:** Search relevant files → search for violation patterns → read context to verify → classify CAT-1 (auto-fixable) or CAT-2 (needs approval).

**Confidence:** HIGH = pattern match + context verified. MEDIUM = pattern match, ambiguous context. LOW = heuristic only.

**False positive prevention:** Skip tokens inside comments, generated files (*.g.dart, *.gen.*), test fixtures, vendor/node_modules directories. Respect skip patterns: `/* noqa */`, `// intentional`, `// safe:`.

**Recovery (context lost):** Check progress checklist → read findings artifact → resume from first incomplete scope.

**Gate:** Every in-scope check evaluated, all findings recorded with severity, confidence, and category.

### Phase 4: Report

```
## Frontend Design Quality Report — [project_name]
Framework: [framework] | Scanned: [scopes] | Date: [today]
Design System: [exists/partial/absent]

### Findings
| # | Rule | Sev | File:Line | Issue | Fix | Conf |

### Summary
| Scope | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Gate:** Report presented to user with all findings, severities, and scope summary.

### Phase 5: Fix [SKIP if audit-only or --check]

1. **Plan.** Group by file, order CRITICAL→HIGH→MEDIUM→LOW.
2. **Execute.** CAT-1 fixes: hardcoded color→token, missing `alt`→add, contrast→adjust to 4.5:1, missing `:focus-visible`→add outline, missing `aria-label`→add from context.
3. **Verify.** Re-read each modified file.
4. **Record.** Track applied/failed/skipped.

**Gate:** Fixed + failed + skipped = total. Every modified file re-read and verified.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied -> fixed/failed, declined -> skipped).

### Phase 7: Design [SKIP if mode is not design]

1. **tokens.json** — W3C DTCG 2025.10 format: color (primary/secondary/error/warning/success/info/surface/background + 3 shades), spacing (4/8/12/16/24/32/48/64), typography (display/heading/title/body/label/caption), shadow (sm/md/lg/xl), border (radius sm/md/lg/full, width thin/medium/thick).
2. **Component catalog** — state coverage matrix, missing state recommendations, a11y compliance per component.
3. **A11y checklist** — WCAG 2.2 AA checklist specific to detected framework and components.

**Gate:** Design artifacts generated and written to project. User informed of file locations.

### Phase 8: Summary

```
ds-frontend: {OK|WARN|FAIL} | Mode: {audit|audit+fix|design} | Fixed: N | Skipped: N | Failed: N | Total: N
```

FRC+DSC accounting.

**Gate:** Summary rendered. `fixed + failed + skipped + needs_approval + not_applicable = total`.

## Quality Gates

- Every finding cites file:line — verified by reading actual code
- Only modify UI-layer code (styles, components, tokens, ARIA attributes) — business logic untouched
- Every finding gets a disposition in summary — zero silent drops (FRC)
- Every scope check evaluated and accounted for — zero silent omissions (DSC)
- After fix, re-read modified file to verify fix worked
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No framework detected | Ask user to specify, fall back to CSS/HTML-only analysis |
| No design system found | Recommend design mode, audit raw hardcoded values |
| Token file format unrecognized | Catalog CSS custom properties as tokens, warn about non-standard format |
| ARIA pattern unclear for complex widget | Reference W3C APG by component type, flag as needs-input |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Missing keyboard access on interactive element, text contrast <3:1, no focus indicator, interactive element without accessible name |
| HIGH | Hardcoded colors bypassing token system, missing empty/error states on data-driven component, no dark mode handling for themed app |
| MEDIUM | Spacing values following incorrect scale, missing loading state in async component, non-semantic token names |
| LOW | Minor spacing inconsistency, missing hover transition, suboptimal token naming convention |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Tailwind project (utility-first) | Audit Tailwind config consistency and custom values; skip "hardcoded color" detection for Tailwind utility classes |
| CSS-in-JS (styled-components, Emotion) | Scan theme objects as token source, ThemeProvider as design system |
| No CSS at all (API-only project) | Report "No UI layer detected", exit |
| Design mode on existing design system | Audit existing system and suggest improvements — preserve existing structure |
| Monorepo with multiple frameworks | Detect per-package, audit each with correct framework-specific rules |
| Flutter/SwiftUI/Compose | Scan ThemeData/Color assets/MaterialTheme as token source; platform widget patterns for component rules |
| Server-rendered (Next.js SSR, Nuxt SSR) | Audit rendered HTML output patterns alongside component source |
| Component library (no app) | Audit library components, skip app-level layout checks |
