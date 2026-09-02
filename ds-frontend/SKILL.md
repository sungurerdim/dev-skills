---
name: ds-frontend
description: Frontend design quality — design-system audit, token enforcement, component states, accessibility, responsive layout, theming. Use when building or reviewing UI for design consistency, a11y, or responsiveness.
---

# /ds-frontend

Hardcoded colors, inconsistent spacing, missing focus states, broken dark mode — design systems exist to prevent these. This skill enforces them in code.

**Frontend Design Quality** — design system audit, token enforcement, component states, accessibility, responsive layout, theming.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

User runs `/ds-frontend`, or asks to audit UI/design-system/components/a11y/WCAG/contrast/dark-mode/responsive/tokens, or create a design system; or the project contains frontend framework indicators (React, Vue, Svelte, Astro, SolidJS, htmx, Angular, Flutter, RN, SwiftUI, Compose).

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit design system / tokens / hardcoded colors" | "audit business logic" (→ ds-review) |
| "WCAG / a11y technical audit (contrast, focus, ARIA)" | "regulatory a11y framing (EAA, ADA)" (→ ds-compliance --a11y) |
| "generate design tokens / set up theming" | "mobile gestures, permissions, store" (→ ds-mobile) |
| "review component states (empty/loading/error)" | "fix type errors in components" (→ ds-fix) |
| "audit stale/stub routes, dead or mismatched buttons" | "chart/dataviz color palette selection" (→ dataviz) |

## Contract

**Dimensions:** A5 (ux scope), A6 (UI), A7 (implementation), A9 (conditional ecosystem rules), D10 (admin UI)

- Audits UI/UX quality across web, mobile, desktop UI — only touches UI-layer code (styles, components, tokens, ARIA); business + backend untouched.
- Privacy/PII data-handling audit is out of scope: `/ds-compliance` present → advisory-handoff; absent → gap-note `[privacy] not analyzed — requires /ds-compliance`. Never runs its own privacy detector.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- **State-qualifying:** scope-by-scope progress exists nowhere else — an interrupted run would re-scan from zero without it. Persists to `ds/audit/frontend.json` with the run's `git_hash`; applied fixes land in the working tree, git is the durable record. Deleted when the Summary completes.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->

## Arguments

| Flag | Effect |
|------|--------|
| `--mode={x}` | `audit`, `audit+fix`, `design` |
| `--style-mode={x}` | `controlled` (default, ship-grade strict tokens + WCAG AA), `innovative` (prototype, relaxed). [references/controlled-vs-innovative.md](references/controlled-vs-innovative.md) |
| `--aesthetic={preset}` | Named preset (3 IDs). [references/aesthetics-presets.md](references/aesthetics-presets.md) |
| `--scope={list}` | Comma-separated scopes (table below) or `all` |
| `--framework={f}` | Override detection: `react`, `vue`, `svelte`, `svelte5`, `astro`, `solid`, `htmx`, `angular`, `flutter`, `swiftui`, `compose`, `rn` |
| `--check` | Report only, zero modifications |
| `--resume` | Resume from `ds/audit/frontend.json` without the confirmation prompt |
| `--clean` | Delete `ds/audit/frontend.json` and start fresh |
| `--target={path}` | Restrict Fix/Design output to files under `{path}` — used to promote one prototype directory to production (see Translating Innovative → Controlled) |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default: resolves to Audit & Fix across all scopes (scan and fix autonomously), recorded in the summary. `--ask`: up-front menu covering every mode, one-line what-it-does each — Audit (recommended) — scan + report, no changes / Audit & Fix — scan + report + fix CAT-1 / Design — generate/populate design system / (Cancel). A disambiguating flag (e.g. `--mode`, `--scope`) skips the menu.

## Scopes

Every scope runs unless its signal excludes it (table below); an `unknown` signal never excludes a scope. `--scope=` overrides for the named scopes; `--ask` shows the resolved table before running.

| Scope | Runs when (signal) | Otherwise | Covers | Reference |
|-------|---------------------|-----------|--------|-----------|
| tokens | ui ≠ none | N/A | Color/spacing/typography/shadow/border token consistency, hardcoded value detection | rules-design-system.md |
| components | ui ≠ none | N/A | Component API quality, naming, composition, reuse, overlays, route liveness, control-action binding, icon system, AI-friendly docs | rules-components.md |
| solid | ui ≠ none | N/A | SOLID/GRASP in components: SRP, OCP, ISP, DIP, Low Coupling, High Cohesion ([../core/principles.md §2](../core/principles.md)) | rules-components.md |
| states | ui ≠ none | N/A | empty/loading/error/success/disabled/hover/focus/active coverage | rules-components.md |
| ux | ui ≠ none | N/A | Nielsen 10 heuristics, interaction laws, perceived performance, validation-timing, deceptive-pattern screening, UX writing, nav-depth/IA, onboarding; integrates with states | rules-ux.md |
| a11y | ui ≠ none | N/A | WCAG 2.2 AA, ARIA patterns (APG), keyboard nav, contrast, screen reader | rules-accessibility.md |
| responsive | ui = web | N/A (ds-mobile owns adaptive mobile layout) | Layout overflow, breakpoints, container queries, fluid typography, multi-column symmetry, alignment/geometry, print styles, RTL, Core Web Vitals | rules-responsive.md |
| theming | ui ≠ none | N/A | Dark mode, `light-dark()`, color-scheme, semantic tokens, theme switching | rules-design-system.md |
| config | ui ≠ none | N/A | Env-consumed values externalized; `.env.example` updated; no secrets in source ([../core/principles.md §8](../core/principles.md)) | rules-design-system.md |
| admin-ui | ui ≠ none and an admin/back-office surface is detected | N/A | D10 (advisory) — admin surfaces follow the same tokens/states/a11y rules as user-facing UI; no unstyled/raw-HTML admin screens | rules-components.md |
| scheduling | a scheduling/calendar/booking surface is detected (calendar dep, `/booking` or `/schedule` route) | N/A | Conditional (D3) — hover preview, create=edit, drag thresholds, capacity conflicts, off-hours, entity color SSOT | rules-scheduling.md |

### A9 — Google / Apple Ecosystem Rules (conditional)

**Activate when:** blueprint `Integrations` is `google-workspace` or `apple-ecosystem`; zero checks when absent. Button/flow rules: [references/rules-components.md § Ecosystem Rules](references/rules-components.md).

## Style Mode (orthogonal to Mode)

| Style Mode | Token rules | A11y | States required | Output use |
|-----------|------------|------|----------------|-----------|
| `controlled` (default) | strict — hardcoded literal = CRITICAL | WCAG 2.2 AA (contrast <4.5:1 = CRITICAL) | empty/loading/error/success/disabled/focus-visible all required | production |
| `innovative` | relaxed in `proto/`/`explore/`/`sandbox/` or `<!-- innovative -->`-marked files | warnings only (MEDIUM) | default + loading only | design exploration |

Selection heuristic (when not flagged), translating innovative → controlled, and the full enforced/relaxed contract detail: [references/controlled-vs-innovative.md](references/controlled-vs-innovative.md).

## Aesthetic Presets

`--aesthetic={preset}` → load preset from [references/aesthetics-presets.md](references/aesthetics-presets.md) (3 IDs, full catalog + mood/token detail there): `design` mode → populate `tokens.json` with preset palette/typography/spacing/shadow/radius; `audit`/`audit+fix` → add preset-specific lint rules from its `forbidden` list.

## Delegation

**Owns:** tokens, components, states, a11y (implementation), responsive, theming, design-system | **Delegates:** chart/dataviz color palettes → `dataviz` — target present, advisory-handoff; absent → TOK-10 covers only the fixed brand/status tokens | **Receives:** ds-compliance → a11y fixes; ds-blueprint → frontend findings; ds-ship → Phase 2 delegation; ds-backend → AI-feature UX (UX-10b); ds-freeze → flag-gate defer-hidden

## Execution Flow

Detect → [Configure] → Scan → Report → [Fix] → [Needs-Approval] → [Design] → Summary

### Phase 1: Detect

**Recovery check (first step, unconditional every invocation):** DETECT `ds/audit/frontend.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, compare state `git_hash` against `git rev-parse HEAD`. Mismatch → default: resume silently (the re-verify step below catches real drift), recorded in the summary; `--ask`: prompt `Resume anyway? [Y/n]`. Resume → RE-VERIFY the `in_progress` scope by re-reading the files its findings cite, keep `done` scopes, announce `[FE] Resuming from Phase {N}: {name}.` Successful Summary → delete state; empty `ds/audit/` → remove it. Fresh start: `grep -qxF 'ds/audit/' .gitignore` → exit 0; non-zero → append.

**State `data`:** `{ mode, style_mode, framework, scopes_selected, scopes_done[], findings_per_scope: {scope: [{id, severity, file, line, category, disposition}]}, design_system_state }`

1. **Framework detection** — full signal table (13 frameworks incl. Svelte 5 runes, Astro, SolidJS, htmx) + each new framework's specific pattern: [references/rules-components.md § Framework Detection](references/rules-components.md).

2. **Findings file check:** `ds/audit/findings.md` fresh (`git_hash == HEAD` AND produced in the current run-cycle; prior-cycle is stale, diff context only) → read findings matching frontend scopes, skip redundant analysis. Stale/absent → orchestrated run: request `/ds-blueprint --refresh` and wait; standalone: own scoped analysis, appended with own `source` + current `git_hash`.
3. **Upstream artifacts:** Profile → Type+Stack, Config.priorities, Current Scores. Findings(tokens, components, states, a11y, responsive, theming) → verify + use. Absent → own analysis.
4. **Design system detection.** Search for: CSS custom properties (`:root { --color-* }`), Tailwind config; styled-components/Emotion/MUI/Chakra theme; Flutter `ThemeData`; SwiftUI Color assets; Compose `MaterialTheme`; `tokens.json`/`.yaml`/`design-tokens.*`.
5. **Mode + scope.** Default: mode resolves to Audit & Fix, scope resolves to all, recorded in the summary. `--ask`: menu for Audit / Audit & Fix / Design / Custom; map scope selection to reference files.

**Gate:** Framework identified; design system state cataloged (exists/partial/absent); mode + scope confirmed. If fails → framework undetectable: prompt "Which frontend framework?" (offer list); no response → fall back to plain HTML/CSS, announce; design system inconclusive → record `design_system: "unknown"`, proceed (missing tokens surface as findings).

### Phase 2: Configure [SKIP if single scope]

1. **Design system inventory:** color token count + naming, spacing scale, typography count, shadow levels, border radii.
2. **Component patterns:** component directories, naming, barrel exports, shared lib.
3. **A11y tooling (layered):** component — `@storybook/addon-a11y` (axe-core); lint — eslint-plugin-jsx-a11y, @angular-eslint/eslint-plugin-template, flutter_lints; PR-level CI — axe-core; full-page — Lighthouse CI + pa11y.

**Gate:** Design system inventory recorded; component directories identified. If fails → component dirs not locatable → prompt "Where are your component files? (e.g. `src/components/`, `app/ui/`)"; no response → scan all `.tsx`/`.jsx`/`.vue`/`.svelte`/`.dart` from root; record `component_catalog: "heuristic"`.

### Phase 3: Scan

Load each in-scope domain's reference file per the Scopes table's Reference column above, plus, when active: style-mode → [controlled-vs-innovative.md](references/controlled-vs-innovative.md); aesthetic → [aesthetics-presets.md](references/aesthetics-presets.md).

**Large scope (3+ scopes):** progress checklist + persistent findings artifact; max 2 parallel scans. **Per scope:** search relevant files → search violation patterns → read context → classify CAT-1 (auto-fixable) or CAT-2 (needs approval). **Confidence:** HIGH = match + context verified; MEDIUM = pattern match, ambiguous; LOW = heuristic.

**Rendered-geometry rules** (RSP-08/12/15/17, AXE-16): browser automation available → verify by measured bounding boxes at the relevant viewport (row-sibling centers/baselines within 1–2px; group edges/gutters exact); unavailable → static analysis only, cap confidence MEDIUM, note `geometry unverified`.

**False-positive prevention:** skip tokens inside comments, generated files (`*.g.dart`, `*.gen.*`), test fixtures, vendor/`node_modules`, and `/* noqa */`/`// intentional`/`// safe:` lines. **Recovery (context lost):** read `ds/audit/frontend.json` → resume from the first scope not `done`, re-verifying the `in_progress` one — the state file is the progress record, an in-chat checklist is not. Write state after every completed scope, not only at phase boundaries.

**Gate:** Every in-scope check evaluated; findings recorded with severity + confidence + category. If fails → scope unscan-able (reference missing, files unreadable): mark scope `partial`, add MEDIUM "scan incomplete for scope {scope} — {reason}", continue; reference missing → WARN, proceed with embedded rules.

### Phase 4: Report

Header: `## Frontend Design Quality Report — {project-name}` + `Framework: {framework} | Scanned: {scopes} | Date: {today}` + `Design System: {exists|partial|absent}`. Findings table `| # | Rule | Sev | File:Line | Issue | Fix | Conf |`; summary table `| Scope | CRITICAL | HIGH | MEDIUM | LOW | Total |`.

**Gate:** Report with findings + severities + summary. If fails → missing scope row: re-read the collected findings, add row with recorded counts (or `0`), re-emit; do not proceed until every selected scope appears.

### Phase 5: Fix [SKIP if audit-only or --check]

0. **Checkpoint** (`../core/checkpoint-protocol.md`). `git status --porcelain` → empty: clean tree, proceed. Non-empty: default — proceed only when the pre-existing dirty state stays untouched by this skill's writes, otherwise stop that unit and record `only you can do`; `--ask` — show the dirty files, ask **Commit first (recommended) / Stash / Proceed anyway** (risk: fix edits interleave with uncommitted work, single-command rollback is lost). Never run a bulk fix over uncommitted unrelated changes silently.
1. **Plan.** Group by file, order CRITICAL → HIGH → MEDIUM → LOW.
2. **Execute.** CAT-1: hardcoded color → token; missing `alt` → add; contrast → adjust to 4.5:1; missing `:focus-visible` → add outline; missing `aria-label` → add from context.
3. **Verify + record.** Re-read each modified file; record applied/failed/skipped.

**Gate:** `fixed + failed + skipped = total`; every modified file re-read. If fails → file un-re-readable: mark fix `failed (verify error)`, revert; undisposed finding → `skipped (accounting gap)`; counts imbalanced → `WARN`.

### Phase 6: Needs-Approval Review [needs_approval > 0]

Default: items resolve by best judgment (`fixed`/`failed`) with the reasoning recorded in the summary; only items matching the publish/irreversible exception list become `skipped (only you can do)`. `--ask`: state the question (`Approve these N items?`), present each item compactly (`[severity] title — file:line`) grouped by severity with counts, and ask Apply all / per-severity bulk (alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved (applied → fixed/failed, declined → skipped). If fails → unresolved → mark `skipped (no decision)`, proceed; do not retry.

### Phase 7: Design [SKIP if mode ≠ design]

**Design input — prefer the highest-fidelity form available.** A runnable HTML/CSS mockup carries the intended design more precisely than a prose description or a screenshot, because it is expressed in the same language as the output — ask for or produce one before working from a description. Only a description available → generate a mockup artifact first, confirm it with the user, then build against the confirmed artifact rather than re-interpreting the prose at each step.

1. **`tokens.json`** — W3C DTCG 2025.10: color (primary/secondary/error/warning/success/info/surface/background + 3 shades), spacing (4/8/12/16/24/32/48/64), typography (display/heading/title/body/label/caption), shadow (sm/md/lg/xl), border (radius sm/md/lg/full, width thin/medium/thick).
2. **Component catalog** — state coverage matrix, missing state recs, a11y compliance per component.
3. **A11y checklist** — WCAG 2.2 AA list specific to detected framework + components.

**Gate:** Artifacts generated and written — each declared path exists on disk (`ls {path}` → listed); user informed of paths. If fails → artifact unwritable (permission, path conflict): default retries once with a sanitized fallback path, still unwritable → `failed (write error)` recorded in the generated-artifacts list, run continues; `--ask` surfaces the error, asks user to confirm/alternative path; no response → skip, record `failed (write error)`, continue.

### Mechanical Done Gate [any fix applied]

Resolve `{check-cmd}` in Phase 1: ds-quality enforcement arm installed → use its gate command; else stack-native format/lint/type/test (include the a11y lint layer from Phase 2 when wired); none detectable → Verification-Infrastructure Gap, offer `/ds-quality`, record the decision. Capture the baseline before Phase 5; baseline red → done means "no *new* red", never inherited as green. After each Phase 5/6 fix batch: run `{check-cmd}` on the touched scope — new red → repair and re-run (≤3 attempts); still red → revert via `git checkout -- {file}`, disposition `failed (mechanical gate)` with the captured error. Before Phase 8: run the full `{check-cmd}` once — its command + output is the Completion Evidence. Re-reading the file (Phase 5 step 3) is necessary but not this gate — only the check command's green is. Never report `OK` with a new red. Audit-only/`--check`/design-only runs → N/A, state it.

### Phase 8: Summary

```
ds-frontend: {OK|WARN|FAIL} | Mode: {audit|audit+fix|design} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
Scopes: ran {a, b, …} · N/A — {key}={value} {…}
```

Disposition accounting — totals balance. `fixed + failed + skipped + needs_approval + not_applicable = total` (shape: [../core/report-and-outcome-templates.md](../core/report-and-outcome-templates.md)).

**State cleanup:** run completed → delete `ds/audit/frontend.json`; `ds/audit/` now empty → remove it. Run ended WARN/FAIL → leave state in place so the next invocation can resume it.

**Gate:** Summary rendered; equation balances; state file deleted on a completed run (`test ! -f ds/audit/frontend.json`). If fails → unaccounted finding: `skipped (accounting gap)`; still imbalanced → `WARN`, report items needing reconciliation; state deletion fails → report the leftover path so the next run isn't silently resumed from it.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} hardcoded colors / spacings replaced with design tokens — theme + dark mode now consistent across the codebase`
- `{n} WCAG 2.2 AA contrast violations fixed — keyboard + screen-reader users no longer locked out of key flows`

Audit-only run: `{n} findings (severity: {breakdown}) — actionable list returned, no source modified`.

## Quality Gates

UI-layer-only scope, per-finding disposition, and post-fix re-read are enforced in the Contract and Phase 5's Gate above — not restated here.

- W9: state-qualifying — progress persists to `ds/audit/frontend.json` (written after each completed scope, deleted on a completed Summary); applied fixes land in the working tree, git is the durable record. W10: defer to fresh `ds/audit/findings.md` — own scan only for uncovered scopes.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| No framework detected | Ask user to specify; fall back to CSS/HTML-only analysis |
| No design system found | Recommend design mode; audit hardcoded values |
| Token file format unrecognized | Catalog CSS custom properties as tokens; warn non-standard |
| ARIA pattern unclear for complex widget | Reference W3C APG by component type; flag only you can do |

## Severity

Contrast policy (binding for every rule touching contrast — full definitions in `references/rules-accessibility.md` AXE-03/AXE-09): text below the WCAG threshold (4.5:1 normal, 3:1 large ≥18pt/24px or ≥14pt/18.7px bold — SC 1.4.3) is CRITICAL, a complete reading lockout; non-text/UI contrast below 3:1 (borders, icons, focus rings — SC 1.4.11) is HIGH, a narrower loss.

| Level | Meaning |
|-------|---------|
| CRITICAL | Missing keyboard access; text contrast below 4.5:1 normal/3:1 large; no focus indicator; interactive element without accessible name |
| HIGH | Hardcoded colors bypassing tokens; missing empty/error states on a data-driven component; no dark mode for a themed app; non-text/UI contrast below 3:1 |
| MEDIUM | Spacing off scale; missing loading state in an async component; non-semantic token names |
| LOW | Minor spacing inconsistency; missing hover transition; suboptimal token naming |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Tailwind (utility-first) | Audit config + custom values; skip "hardcoded color" for utility classes |
| CSS-in-JS (styled-components, Emotion) | Scan theme objects as token source; ThemeProvider as design system |
| No CSS (API-only) | Report "No UI layer detected", exit |
| Design mode on existing system | Audit existing + suggest improvements; preserve structure |
| Monorepo, multiple frameworks | Detect per-package; audit each with its own rules |
| Flutter / SwiftUI / Compose | `ThemeData`/Color assets/`MaterialTheme` as token source |
| Server-rendered (Next.js SSR, Nuxt SSR) | Audit rendered HTML alongside source |
| Component library (no app) | Audit library components, skip app-level layout checks |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
