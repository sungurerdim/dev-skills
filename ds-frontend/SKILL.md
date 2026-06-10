# /ds-frontend

Hardcoded colors, inconsistent spacing, missing focus states, broken dark mode — design systems exist to prevent these. This skill enforces them in code.

**Frontend Design Quality** — design system audit, token enforcement, component states, accessibility, responsive layout, theming.

## Triggers

- User runs `/ds-frontend`
- User asks to audit UI quality, check design system, review components, review frontend
- User asks about accessibility, WCAG, contrast, dark mode, responsive, design tokens
- User asks to create or generate a design system, design tokens
- Project contains frontend framework indicators (React, Vue, Svelte, Angular, Flutter, RN, SwiftUI, Compose)

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit design system / tokens / hardcoded colors" | "audit business logic" (→ ds-review) |
| "WCAG / a11y technical audit (contrast, focus, ARIA)" | "regulatory a11y framing (EAA, ADA)" (→ ds-compliance --a11y) |
| "generate design tokens / set up theming" | "mobile gestures, permissions, store" (→ ds-mobile) |
| "review component states (empty/loading/error)" | "fix type errors in components" (→ ds-fix) |

## Contract

- Audits UI/UX design quality across web ({web-frameworks}), mobile ({mobile-frameworks}), desktop ({desktop-frameworks}) — only touches UI-layer code (styles, components, tokens, ARIA); business + backend untouched.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `design` |
| `--style-mode={x}` | `controlled` (default, ship-grade strict tokens + WCAG AA), `innovative` (prototype, relaxed). [references/controlled-vs-innovative.md](references/controlled-vs-innovative.md) |
| `--aesthetic={preset}` | Named preset (11 IDs below). [references/aesthetics-presets.md](references/aesthetics-presets.md) |
| `--scope={list}` | Comma-separated scopes (table below) or `all` |
| `--framework={f}` | Override detection: `react`, `vue`, `svelte`, `angular`, `flutter`, `swiftui`, `compose`, `rn` |
| `--check` | Report only, zero modifications |
| `--resume` | Resume from `ds/audit/frontend.json` without prompting |
| `--clean` | Delete existing state, start fresh |

Without flags: present mode selection.

## Scopes

| Scope | Covers | Reference |
|-------|--------|-----------|
| tokens | Color/spacing/typography/shadow/border token consistency, hardcoded value detection | rules-design-system.md |
| components | Component API quality, naming, composition, reuse, AI-friendly docs | rules-components.md |
| solid | SOLID/GRASP in components: SRP, OCP, ISP, DIP, Low Coupling, High Cohesion ([references/principles.md §2](references/principles.md)) | rules-components.md |
| states | empty/loading/error/success/disabled/hover/focus/active coverage | rules-components.md |
| a11y | WCAG 2.2 AA, ARIA patterns (APG), keyboard nav, contrast, screen reader | rules-accessibility.md |
| responsive | Layout overflow, breakpoints, container queries, fluid typography | rules-responsive.md |
| theming | Dark mode, `light-dark()`, color-scheme, semantic tokens, theme switching | rules-design-system.md |
| config | Env-consumed values externalized; `.env.example` updated; no secrets in source ([references/principles.md §8](references/principles.md)) | rules-design-system.md |

Default: all scopes.

## Modes

| Mode | Behavior |
|------|----------|
| `audit` | Scan and report only |
| `audit+fix` | Scan + report + fix CAT-1 (hardcoded→token, missing ARIA, contrast, focus) |
| `design` | Generate `tokens.json` (W3C DTCG 2025.10), component catalog, a11y checklist |

## Style Mode (orthogonal to Mode)

| Style Mode | Token rules | A11y | States required | Output use |
|-----------|------------|------|----------------|-----------|
| `controlled` (default) | strict — hardcoded literal = CRITICAL | WCAG 2.2 AA (contrast <4.5:1 = CRITICAL) | empty/loading/error/success/disabled/focus-visible all required | production |
| `innovative` | relaxed in `proto/`, `explore/`, `sandbox/` or files marked `<!-- innovative -->` | warnings only (MEDIUM) | only default + loading | design exploration |

**Heuristic selection (when not flagged):** "audit/review/ship/production/release" → controlled; "explore/experiment/concept/moodboard" → innovative; path under `proto/`, `explore/`, `sandbox/` → innovative; else controlled.

**Translating innovative → controlled:** `/ds-frontend --mode=audit+fix --style-mode=controlled --target={path}`. Replaces hardcoded → tokens (asks for token names if needed), adds missing a11y, completes state coverage, strips `// PROTOTYPE` header.

## Aesthetic Presets

When `--aesthetic={preset}` is set, the skill loads the preset from [references/aesthetics-presets.md](references/aesthetics-presets.md) and:

1. `design` mode → populates `tokens.json` with preset palette + typography + spacing + shadow + radius
2. `audit` / `audit+fix` → adds preset-specific lint rules from `forbidden` list (e.g. `{preset-id}` flags `{forbidden-pattern-1}`, `{forbidden-pattern-2}`)
3. Records `state.data.aesthetic` for resume

| ID | Best For | Anchor Color |
|----|----------|--------------|
| `dark-oled-luxury` | premium SaaS, fintech, AI tools | gold on black |
| `warm-trust` | health, legal, family, advisory | deep teal |
| `clean-minimal` | productivity, dev tools, docs | monochrome |
| `arctic-data` | dashboards, analytics, monitoring | cold blue-grey |
| `terracotta-craft` | artisan, indie commerce, wellness | terracotta |
| `neo-brutalist` | manifestos, indie creative, music | primary red |
| `clinical-calm` | medical, mental health, telehealth | muted sea-green |
| `consumer-glow` | mobile apps, social, lifestyle | vibrant gradient |
| `editorial` | content publishing, long-form, magazine | serif accent |
| `enterprise-sober` | B2B tools, admin panels, internal | workhorse blue |
| `studio-mono` | designer/dev portfolios | single-color |

## Delegation

**Owns:** tokens, components, states, a11y (implementation), responsive, theming, design-system | **Delegates:** none | **Receives:** ds-compliance → a11y implementation/fixes; ds-blueprint → frontend scope findings

## Execution Flow

```
Detect → [Configure] → Scan → Report → [Fix] → [Needs-Approval] → [Design] → Summary
```

### Phase 1: Detect

**Recovery check:** DETECT `ds/audit/frontend.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read files for pending findings, discard stale), skip `done` phases, announce `[FE] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ framework, mode, style_mode, aesthetic, scopes_selected, scopes_done[], design_system:{tokens_path, component_catalog}, findings[{id, severity, file, line, scope, disposition}], fix_progress, design_artifacts_generated[] }`.

1. **Framework detection.**

   | Framework | Detection |
   |-----------|-----------|
   | React | `package.json` dep `react` |
   | Vue | `package.json` dep `vue` |
   | Svelte | `package.json` dep `svelte` |
   | Angular | `package.json` dep `@angular/core` |
   | Flutter | `pubspec.yaml` with `flutter:` |
   | React Native | `package.json` dep `react-native` |
   | SwiftUI | `*.swift` files importing `SwiftUI` |
   | Compose | `build.gradle` with `compose` |
   | Electron/Tauri | `package.json` dep `electron` or `@tauri-apps/api` |
   | Plain HTML/CSS | `*.html` + `*.css` without framework |

2. **Findings file check:** `ds/audit/findings.md` fresh `git_hash` → read findings matching frontend scopes, skip redundant analysis. Stale/absent → own full analysis.
3. **IDU:** Profile → Type+Stack, Config.priorities, Current Scores. Findings(tokens, components, states, a11y, responsive, theming) → verify + use. Absent → own analysis.
4. **Design system detection.** Search for: CSS custom properties (`:root { --color-* }`), Tailwind config, CSS modules theme; styled-components / Emotion / MUI / Chakra theme; Flutter `ThemeData`/`ColorScheme`; SwiftUI Color assets; Compose `MaterialTheme`; `tokens.json`/`tokens.yaml`/`design-tokens.*`.
5. **Mode selection.** Ask or use flags: Audit / Audit & Fix / Design / Custom.
6. **Scope parsing.** Map selection to reference files. Default: all.

**Gate:** Framework identified; design system state cataloged (exists/partial/absent); mode + scope confirmed. If fails → framework undetectable → prompt "Which frontend framework?" (offer list); no response → fall back to plain HTML/CSS, announce; design system inconclusive → record `design_system: "unknown"`, proceed (missing tokens surface as findings).

### Phase 2: Configure [SKIP if single scope]

1. **Design system inventory:** color token count + naming, spacing scale, typography count, shadow levels, border radii.
2. **Component patterns:** component directories, naming, barrel exports, shared lib.
3. **A11y tooling:** axe-core, eslint-plugin-jsx-a11y, @angular-eslint/eslint-plugin-template, flutter_lints a11y rules.

**Gate:** Design system landscape mapped; component patterns identified. If fails → component dirs not locatable → prompt "Where are your component files? (e.g. `src/components/`, `app/ui/`)"; no response → scan all `.tsx`/`.jsx`/`.vue`/`.svelte`/`.dart` from root; record `component_catalog: "heuristic"`.

### Phase 3: Scan

Load matching reference file per in-scope domain:

| Scope | Reference File |
|-------|---------------|
| tokens, theming | [rules-design-system.md](references/rules-design-system.md) |
| components, states | [rules-components.md](references/rules-components.md) |
| a11y | [rules-accessibility.md](references/rules-accessibility.md) |
| responsive | [rules-responsive.md](references/rules-responsive.md) |
| (style-mode) | [controlled-vs-innovative.md](references/controlled-vs-innovative.md) |
| (aesthetic) | [aesthetics-presets.md](references/aesthetics-presets.md) |

**Large scope (3+ scopes):** progress checklist + persistent findings artifact. Max 2 parallel scans.

**Per scope:** search relevant files → search violation patterns → read context → classify CAT-1 (auto-fixable) or CAT-2 (needs approval).

**Confidence:** HIGH = match + context verified. MEDIUM = pattern match, ambiguous. LOW = heuristic.

**False-positive prevention:** skip tokens inside comments, generated files (`*.g.dart`, `*.gen.*`), test fixtures, vendor/`node_modules`. Skip patterns: `/* noqa */`, `// intentional`, `// safe:`.

**Recovery (context lost):** check progress checklist → read findings artifact → resume from first incomplete scope.

**Gate:** Every in-scope check evaluated; findings recorded with severity + confidence + category. If fails → scope unscan-able (reference missing, files unreadable) → mark scope `partial` in `state.scopes_done`, add MEDIUM "scan incomplete for scope {scope} — {reason}", continue; reference missing → WARN, proceed with embedded rules.

### Phase 4: Report

```
## Frontend Design Quality Report — {project-name}
Framework: {framework} | Scanned: {scopes} | Date: {today}
Design System: {exists|partial|absent}

### Findings
| # | Rule | Sev | File:Line | Issue | Fix | Conf |

### Summary
| Scope | CRITICAL | HIGH | MEDIUM | LOW | Total |
```

**Gate:** Report with findings + severities + summary. If fails → missing scope row → re-read `state.findings`, add row with recorded counts (or `0`), re-emit; do not proceed until every selected scope appears.

### Phase 5: Fix [SKIP if audit-only or --check]

1. **Plan.** Group by file, order CRITICAL → HIGH → MEDIUM → LOW.
2. **Execute.** CAT-1: hardcoded color → token; missing `alt` → add; contrast → adjust to 4.5:1; missing `:focus-visible` → add outline; missing `aria-label` → add from context.
3. **Verify.** Re-read each modified file.
4. **Record.** applied/failed/skipped.

**Gate:** `fixed + failed + skipped = total`; every modified file re-read. If fails → file un-re-readable → mark fix `failed (verify error)`, revert; undisposed finding → `skipped (accounting gap)`; counts imbalanced → status `WARN`.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → mark `skipped (no decision)`, proceed; do not retry.

### Phase 7: Design [SKIP if mode ≠ design]

1. **`tokens.json`** — W3C DTCG 2025.10: color (primary/secondary/error/warning/success/info/surface/background + 3 shades), spacing (4/8/12/16/24/32/48/64), typography (display/heading/title/body/label/caption), shadow (sm/md/lg/xl), border (radius sm/md/lg/full, width thin/medium/thick).
2. **Component catalog** — state coverage matrix, missing state recs, a11y compliance per component.
3. **A11y checklist** — WCAG 2.2 AA list specific to detected framework + components.

**Gate:** Artifacts generated and written; user informed of paths. If fails → artifact unwritable (permission, path conflict) → surface error, ask user to confirm/alternative path; no response → skip, record `failed (write error)` in `state.design_artifacts_generated`, continue.

### Phase 8: Summary

```
ds-frontend: {OK|WARN|FAIL} | Mode: {audit|audit+fix|design} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

FRC+DSC accounting. `fixed + failed + skipped + needs_approval + not_applicable = total`.

**Gate:** Summary rendered; equation balances. If fails → unaccounted finding → `skipped (accounting gap)`; still imbalanced → `WARN`, retain `ds/audit/frontend.json` for `--resume`.

**Value Delivered:** 1-5 concrete UI outcomes, real changes only. Example shapes (placeholders, not literal):

- `{n} hardcoded colors / spacings replaced with design tokens — theme + dark mode now consistent across the codebase`
- `{n} WCAG 2.2 AA contrast violations fixed — keyboard + screen-reader users no longer locked out of key flows`
- `Component state coverage filled: empty / loading / error / disabled / focus added for {n} components — broken UX edge cases eliminated`
- `Responsive layout: {n} overflow / breakpoint issues resolved — UI no longer breaks on common viewport widths`

Audit-only run: `{n} findings (severity: {breakdown}) — actionable list returned, no source modified`.

## Quality Gates

1. Every finding cites file:line — verified by reading actual code
2. Only modify UI-layer code (styles, components, tokens, ARIA) — business logic untouched
3. Every finding gets a disposition — zero silent drops (FRC)
4. Every scope check evaluated and accounted for — zero silent omissions (DSC)
5. After fix, re-read modified file to verify
6. W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/frontend.json` updated per scope + artifact, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for uncovered scopes. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No framework detected | Ask user to specify; fall back to CSS/HTML-only analysis |
| No design system found | Recommend design mode; audit raw hardcoded values |
| Token file format unrecognized | Catalog CSS custom properties as tokens; warn non-standard format |
| ARIA pattern unclear for complex widget | Reference W3C APG by component type; flag as needs-input |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Missing keyboard access on interactive element; text contrast <3:1; no focus indicator; interactive element without accessible name |
| HIGH | Hardcoded colors bypassing token system; missing empty/error states on data-driven component; no dark mode handling for themed app |
| MEDIUM | Spacing values off scale; missing loading state in async component; non-semantic token names |
| LOW | Minor spacing inconsistency; missing hover transition; suboptimal token naming |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Tailwind (utility-first) | Audit Tailwind config + custom values; skip "hardcoded color" for utility classes |
| CSS-in-JS (styled-components, Emotion) | Scan theme objects as token source; ThemeProvider as design system |
| No CSS at all (API-only) | Report "No UI layer detected", exit |
| Design mode on existing system | Audit existing + suggest improvements; preserve structure |
| Monorepo, multiple frameworks | Detect per-package; audit each with framework-specific rules |
| Flutter / SwiftUI / Compose | `ThemeData`/Color assets/`MaterialTheme` as token source; platform widget patterns for components |
| Server-rendered (Next.js SSR, Nuxt SSR) | Audit rendered HTML output alongside component source |
| Component library (no app) | Audit library components, skip app-level layout checks |
