# UX — behaviour, states, layout and tokens of graphical UIs

Applies to graphical UIs (`ui` ∋ web, ios, android or desktop); a terminal-only product skips this file for [cli.md](cli.md). Browser-only checks are in [web.md](web.md), accessibility in [a11y.md](a11y.md), billing screens in [monetization.md](monetization.md). A UI element or action built twice is SIM-08 or SIM-09; a literal where a token or string resource exists is a detector of SIM-06.

### UX-01 [HIGH] Pending work shows no status
- **Detect:** async actions (save, submit, upload, sync) with no pending state, disabled re-submit or completion signal; a generic full-page spinner where the layout is known (a skeleton fits) or where only one region loads; multi-step flows with no step indicator or resume point; offline or unsynced data with no indicator; interactions over ~400 ms with no immediate visual response.
- **Mech:** M
- **Fix:** an immediate pressed or pending state, then a progress or skeleton scoped to the loading region after a short delay (~300 ms) to avoid flashes; a step indicator and resume for long flows; a visible sync or offline state.
- **Impact:** users repeat the action (double orders, duplicate posts) or abandon a flow they think is stuck.
- **Source:** Nielsen heuristic 1, visibility of system status; NN/g, Response Times: The 3 Important Limits.

### UX-09 [HIGH] Error message without cause or way forward
- **Detect:** "Something went wrong" with no cause and no next step; raw codes, exception text or `undefined`/`null`/`[object Object]` shown to users; no retry, edit or support path; a field error shown as a page toast, or a blocking error shown only as a toast that disappears.
- **Mech:** T `git grep -nIiE '["'"'"'](something went wrong|an error occurred|unknown error|error!?)["'"'"']' -- ':!*test*' ':!*.md'`
- **Fix:** say what happened, why if known, and what to do, in the user's words; field errors inline at the field, page errors in a persistent banner, transient recoverable issues as a non-blocking notice.
- **Impact:** users cannot recover on their own, so the error becomes a support ticket or a lost user.
- **Source:** Fail fast; Nielsen heuristic 9; NN/g, Error-Message Guidelines.

### CMP-13 [HIGH] Failure shown as an empty state
- **Detect:** a fetch `catch` that sets the list to empty without an error flag; permission or authentication failures (401/403) rendered as "nothing here"; one `isEmpty` branch for both no-data and failed-load.
- **Mech:** T `git grep -nIE 'catch.*(set[A-Z][A-Za-z]*\(\[\]\)|= \[\]|emptyList\(\)|const \[\])' -- ':!*test*' ':!*.md'`
- **Fix:** separate loading, empty, error and forbidden states in the data type; render each differently, with retry on error and an access path on forbidden.
- **Impact:** users conclude their data is gone and re-create or abandon it while the real failure stays hidden.
- **Source:** Fail fast; Nielsen heuristics 1 and 9; ARC-06 (errors signalled consistently).

### UX-ON-02 [MEDIUM] Empty state without a next step
- **Detect:** empty lists, tables and dashboards that render nothing, or only "No items", with no action to create or import the first item and no hint of what it will show.
- **Mech:** M
- **Fix:** explain what will appear, offer the primary create or import action, and link help where setup is non-trivial.
- **Impact:** a new user's first screen is a dead end.
- **Source:** NN/g, Designing Empty States in Complex Applications.

### UX-03 [HIGH] No way back from a step or a destructive action
- **Detect:** wizards and flows without back or cancel; dialogs without a close control or Escape; destructive actions (delete, send, publish, wipe) with neither a confirmation naming what is lost nor an undo window; a CLI command that deletes or overwrites with no `--dry-run`, confirmation or backup; confirmation on trivial, reversible actions (confirmation fatigue).
- **Mech:** M
- **Fix:** back and cancel on every step; prefer undo (soft delete, delayed send) for reversible actions; a confirmation that names the object and its consequence for irreversible ones.
- **Impact:** one mis-tap destroys data or traps the user in a flow.
- **Source:** Reversibility; Nielsen heuristic 3, user control and freedom; heuristic 5, error prevention.

### UX-NS-01 [HIGH] Unsaved input lost on leave or reload
- **Detect:** forms, editors or flows with unsaved input that browser back, a nav link, a tab close, an app-update reload or a system back gesture discards without warning; autosave with no saved/unsaved indicator.
- **Mech:** T `git grep -nIE 'beforeunload|useBlocker|beforeRouteLeave|canDeactivate|PopScope|WillPopScope|onBackPressed' -- ':!*.md'`
- **Fix:** autosave drafts or warn on leave when input is dirty; snapshot and restore form state across forced reloads; show the save status.
- **Impact:** users lose minutes of work to a single click and stop trusting the product.
- **Source:** Nielsen heuristic 3; MDN, beforeunload event and Page Lifecycle API.

### UX-05 [MEDIUM] Input invites errors or rejects fixable formats
- **Detect:** free text where a constrained control fits (dates, enumerations); impossible combinations accepted (end before start); spaces, dashes or case in phone, card, IBAN or email rejected instead of normalised; trailing whitespace failing validation; one rigid date format.
- **Mech:** M
- **Fix:** constrained controls and cross-field checks before submit; normalise input (trim, strip separators, case-fold emails) before validating.
- **Impact:** users fail forms for formatting the system could have fixed, and invalid data reaches the backend.
- **Source:** Nielsen heuristic 5; Postel's robustness principle (RFC 761); Laws of UX, Postel's Law.

### UX-FM-01 [MEDIUM] Form validation fires at the wrong time
- **Detect:** errors shown while the user is still typing a first entry; different timing (keystroke, blur, submit) across forms with no chosen rule; long forms that show submit errors only inline with no summary; a summary whose entries do not move focus to the field.
- **Mech:** M
- **Fix:** one strategy for the product: validate on blur or submit, re-validate live once a field has shown an error; on submit, a summary at the top linking to each field.
- **Impact:** premature errors distract and punish; a long form with hidden errors looks broken.
- **Source:** Least astonishment; GOV.UK Design System, Validation pattern and Error summary; Baymard Institute, inline validation research.

### UX-06 [MEDIUM] Actions only memory can find
- **Detect:** commands reachable only by keyboard shortcut, gesture, long-press or swipe with no visible control or menu entry; flows that make users remember a value from an earlier step; frequent actions with no shortcut or bulk path at all.
- **Mech:** M
- **Fix:** every action visible in a menu or control, with shortcuts and gestures as accelerators shown in that menu or a tooltip; recap earlier input; bulk actions for frequent list operations.
- **Impact:** features go undiscovered, and users repeat tedious steps.
- **Source:** Nielsen heuristics 6 and 7, recognition rather than recall, flexibility and efficiency.

### UX-08 [MEDIUM] Screen without one clear primary action
- **Detect:** several equally prominent filled buttons or highlighted elements in one view; no visual difference between primary, secondary and destructive buttons; more than ~7 ungrouped options at one level; rarely used options shown by default instead of behind "More"; a primary action far from what it acts on or outside thumb reach on phones.
- **Mech:** M
- **Fix:** one primary action per view; a button hierarchy (filled, outlined or tonal, text; destructive styled distinctly); group or progressively disclose options; place actions next to their object.
- **Impact:** users hesitate or pick the wrong action; decision time grows with every equal option.
- **Source:** Nielsen heuristic 8; Laws of UX, Hick's Law, Fitts's Law, Von Restorff effect.

### UX-LX-03 [MEDIUM] Platform conventions overridden
- **Detect:** scroll hijacking; browser or system back not undoing the last navigation; the native context menu, text selection or zoom suppressed with no replacement; custom controls replacing standard ones (date picker, select, share sheet) without need; desktop apps without the platform's menu, shortcut and window conventions.
- **Mech:** T `git grep -nIE 'contextmenu.*preventDefault|user-select:[[:space:]]*none|history\.pushState|wheel.*preventDefault' -- ':!*.md'`
- **Fix:** keep native behaviour unless the replacement is strictly better and complete; when replacing, support the same keys, gestures and accessibility.
- **Impact:** users' habits from every other app fail here, which reads as broken.
- **Source:** Least astonishment; Laws of UX, Jakob's Law; Apple Human Interface Guidelines; Material Design; Microsoft Windows app design guidelines.

### UX-LX-07 [MEDIUM] Asks for what it could derive or does not need yet
- **Detect:** sign-up or setup asking for data not needed until later (billing before any paid action, preferences before the feature exists); values the system can derive asked from the user (country from locale, card type from number, time zone from device); configuration required where a working default exists.
- **Mech:** M
- **Fix:** derive or default, let the user correct; ask for each field at the moment it is first needed.
- **Impact:** every extra field costs completions and collects data the product does not need (PRV-03).
- **Source:** Secure / private by default; Laws of UX, Tesler's Law; NN/g, Progressive Disclosure.

### UX-ON-01 [HIGH] First run does not reach value quickly
- **Detect:** no defined first-run path for a new account or workspace; more steps than needed between sign-up and the first useful result, with no measurement of that step count; tours that cannot be skipped or that replay for returning users; external setup steps described in prose with no deep link and no automatic resume when the user returns.
- **Mech:** M
- **Fix:** one short path to the first success, measured in steps or time; skippable, once-per-feature tours; deep links into external setup pages and resume on return (redirect callback or focus event).
- **Impact:** users leave before they see what the product does.
- **Source:** NN/g, Onboarding Tutorials vs. Contextual Help.

### UX-IA-01 [MEDIUM] Views not addressable or nested too deep
- **Detect:** navigation nested beyond three levels; deep content without breadcrumbs; views, dialogs, tabs, filters or detail panels that vanish on reload or cannot be linked; state reachable only by a click sequence; routes registered in several places with no single route table.
- **Mech:** M
- **Fix:** a single route table; every meaningful view and filter state in the URL or the platform's deep-link and restoration path; breadcrumbs below the top level.
- **Impact:** users cannot share, bookmark or return to what they were looking at, and support cannot reproduce it.
- **Source:** NN/g, Breadcrumbs: 11 Design Guidelines; W3C, Cool URIs don't change.

### UX-PP-01 [HIGH] Optimistic update with no rollback
- **Detect:** UI state changed before the request resolves with no failure path that restores it and tells the user; optimistic updates on irreversible or paid actions (payment, send, delete, publish); silent rollback.
- **Mech:** M
- **Fix:** optimistic only for reversible, high-success actions; on failure restore the previous state and show what failed with retry; pessimistic (pending) for irreversible ones.
- **Impact:** users believe an action succeeded that never happened.
- **Source:** Reversibility; Nielsen heuristic 1; React, `useOptimistic` documentation.

### UX-DP-01 [HIGH] Choices preselected against the user
- **Detect:** pre-checked boxes for marketing, data sharing, add-ons, donations or upgrades; the paid option preselected while the free path is visually demoted; decline options worded to shame ("No, I like paying more") or styled to disappear; repeated prompts after a "no".
- **Mech:** T `git grep -nIE '(checked|defaultChecked|value:[[:space:]]*true|initialValue:[[:space:]]*true)' -- ':!*test*' ':!*.md' | grep -iE 'consent|marketing|newsletter|share|addon|add_on|upsell|tip|donat'`
- **Fix:** opt-in defaults, accept and decline of equal visual weight in neutral words, one prompt per decision.
- **Impact:** users end up with purchases and sharing they did not choose, and consent obtained this way does not count (PRV-01).
- **Source:** Secure / private by default; deceptive.design, types catalogue (preselection, confirmshaming, nagging); GDPR Art. 4(11).

### UX-WR-01 [MEDIUM] Labels that do not name the outcome
- **Detect:** `OK`, `Submit`, `Yes`, `Continue` on consequential steps where the outcome is nameable; confirmation buttons that do not answer the dialog's question; internal jargon or field names in user copy.
- **Mech:** T `git grep -nIE '>[[:space:]]*(OK|Ok|Submit|Yes|No)[[:space:]]*<|["'"'"'](OK|Submit|Yes|No)["'"'"']' -- '*.html' '*.jsx' '*.tsx' '*.vue' '*.svelte' '*.dart' '*.swift' '*.kt'`
- **Fix:** verb plus object on every action ("Save changes", "Delete 3 files"); dialog buttons that repeat the verb from the title.
- **Impact:** users confirm the wrong thing, most dangerously in destructive dialogs.
- **Source:** Least astonishment; Nielsen heuristic 2, match between system and the real world; Apple HIG, Writing; Material Design, Writing.

### UX-13 [MEDIUM] Essential information only in a tooltip
- **Detect:** instructions, error details or values available only on hover; tooltips on controls whose visible label already says everything; tooltips unreachable by keyboard focus or touch.
- **Mech:** M
- **Fix:** put essential information in visible text; keep tooltips for supplementary hints on icon-only controls, triggered by hover and focus (behaviour rules: AXE-19).
- **Impact:** touch and keyboard users never see the information, and noise tooltips teach everyone to ignore them.
- **Source:** NN/g, Tooltip Guidelines; WCAG 2.2 SC 1.4.13.

### UX-NT-01 [MEDIUM] Notifications without a shared budget or user control
- **Detect:** each feature sends push, email or in-app notifications on its own trigger with no shared per-user cap; no per-category opt-out or frequency setting; marketing and transactional messages on one channel.
- **Mech:** M
- **Fix:** one notification service with per-user rate limits, quiet hours and per-category preferences; transactional separate from marketing.
- **Impact:** users disable notifications entirely or uninstall, and the important messages are lost with the rest.
- **Source:** Apple HIG, Managing notifications; Material Design, Notifications.

### UX-10a [HIGH] AI output presented as fact or uninterruptible
applies_when: integrations∋openai or integrations∋anthropic
- **Detect:** generated text, summaries or images not marked as AI-generated; generated factual claims (prices, citations, figures) without a source or a verify hint; long generations with no streaming and no stop control; no way to correct, retry or report a bad answer; personal data sent to a third-party model with no disclosure in the UI.
- **Mech:** M
- **Fix:** label generated content; show sources where claims are made; stream with a stop control; offer retry, edit and feedback; name the provider before personal data is sent.
- **Impact:** users act on fabricated facts, and the product carries the blame.
- **Source:** Google PAIR, People + AI Guidebook; Microsoft, Guidelines for Human-AI Interaction (Amershi et al., CHI 2019); Apple App Review Guideline 5.1.2(i).

### CMP-02 [HIGH] Interactive states missing
- **Detect:** controls without distinct hover, pressed, focus, disabled, selected and loading states; disabled controls that give no reason; buttons that accept a second press while the first is pending.
- **Mech:** M (the component library's state list, or the design-system preview)
- **Fix:** every state defined once in the shared component (SIM-08); disable during pending work; explain why something is disabled.
- **Impact:** users cannot tell whether a tap registered, and double submissions follow.
- **Source:** Material Design, States; Apple HIG, Buttons.

### CMP-16 [HIGH] Control or route that does nothing
- **Detect:** enabled controls with an empty handler, a `console.log`/`print` only, `href="#"` without a handler, `onPressed: () {}`; routes and screens rendering only a placeholder ("coming soon", `TODO`); menu items for unbuilt features.
- **Mech:** T `git grep -nIE 'href="#"|onPressed:[[:space:]]*\(\)[[:space:]]*\{[[:space:]]*\}|onClick=\{\(\)[[:space:]]*=>[[:space:]]*\{\}\}|@click="\(\)[[:space:]]*=>[[:space:]]*\{\}"|coming soon|NotImplementedError' -- ':!*test*' ':!*.md'`
- **Fix:** wire the action, or remove or hide the control and route until it works.
- **Impact:** users hit dead ends, and store reviewers reject incomplete apps (STO-12).
- **Source:** Least astonishment; Nielsen heuristic 1; Apple App Review Guideline 2.1, App Completeness.

### INT-01 [MEDIUM] Animation durations outside the usable range
- **Detect:** UI transitions under ~100 ms (unseen) or over ~500 ms (blocking) for routine feedback; durations and easings as literals scattered per component rather than motion tokens; linear easing on movement.
- **Mech:** T `git grep -nIE '(transition|animation)[^;]*[0-9]{4,}ms|milliseconds:[[:space:]]*[0-9]{4,}|duration:[[:space:]]*[0-9]{4,}' -- ':!*.md'`
- **Fix:** a small set of duration and easing tokens (short ~100–200 ms, medium ~250–400 ms); reduced-motion handling per AXE-12.
- **Impact:** slow motion makes every interaction wait; inconsistent motion looks unfinished.
- **Source:** DRY / single source of truth; Material Design 3, Easing and duration; Apple HIG, Motion.

### TOK-01 [HIGH] Colours outside the token set
- **Detect:** hex, `rgb()`, `hsl()` or platform colour literals in components instead of semantic tokens (surface, on-surface, primary, error); tokens named by hue (`blue-500`) used directly in components; status colours that are hard to tell apart or used against meaning (green for an error, red for success). Detector of SIM-06.
- **Mech:** T `git grep -nIE '(^|[^&])#[0-9a-fA-F]{3,8}([^0-9a-zA-Z_-]|$)|rgba?\(|hsla?\(' -- '*.html' '*.css' '*.scss' '*.less' '*.vue' '*.svelte' '*.jsx' '*.tsx' ':!*token*' ':!*theme*' ':!*variables*'` · `git grep -nIE 'Color\(0x[0-9A-Fa-f]{8}\)|Colors\.[a-z]+[^a-zA-Z]' -- '*.dart' ':!*theme*'`
- **Fix:** primitive palette → semantic tokens → components; components reference semantic tokens only; one meaning per status colour.
- **Impact:** a brand or theme change misses screens, and dark mode breaks wherever a literal hides.
- **Source:** DRY / single source of truth; W3C Design Tokens Community Group, Format Module; Material Design 3, Color roles; SIM-06.

### TOK-02 [MEDIUM] Spacing, radius and elevation off the scale
- **Detect:** padding, margin and gap values outside one base-unit scale (4 or 8, chosen once); more than ~5 distinct corner radii; shadow or elevation literals per component; the same role (card padding, panel header) using different steps in different places.
- **Mech:** T `git grep -nIE '(margin|padding|gap|border-radius)[a-z-]*:[^;]*[0-9]+px' -- '*.html' '*.css' '*.scss' '*.less' '*.vue' '*.svelte' ':!*token*' ':!*theme*'` · `git grep -nIE 'EdgeInsets\.[a-zA-Z]+\([^)]*[0-9]|BorderRadius\.circular\([0-9]|elevation:[[:space:]]*[0-9]' -- '*.dart' ':!*theme*'`
- **Fix:** spacing, radius and elevation tokens with role names on top (`space-card`, `radius-control`); enforce with a linter rule (stylelint `declaration-property-value-allowed-list`, a custom lint) where the stack has one.
- **Impact:** layouts drift by a few pixels everywhere, and every spacing change becomes a hunt.
- **Source:** DRY / single source of truth; Material Design, Layout spacing; W3C Design Tokens Community Group; SIM-06.

### TOK-03 [MEDIUM] Type off the scale or hard to read
- **Detect:** font sizes outside the type scale; body text smaller than the platform's default body style or any text under 11 pt/sp; body line height outside ~1.4–1.6; prose lines wider than ~80 characters.
- **Mech:** T `git grep -nIE 'font-size:[[:space:]]*[0-9.]+px' -- '*.html' '*.css' '*.scss' '*.less' '*.vue' '*.svelte' ':!*token*' ':!*theme*'` · `git grep -nIE 'fontSize:[[:space:]]*[0-9]' -- '*.dart' '*.jsx' '*.tsx' ':!*theme*'`
- **Fix:** a named type scale (display, title, body, label) in tokens or the platform text styles; `max-width` around 65ch on prose.
- **Impact:** text that is too small, cramped or too wide slows reading and drives zooming.
- **Source:** Material Design 3, Type scale; Apple HIG, Typography; WCAG 2.2 SC 1.4.8 (AAA, line length).

### THM-03 [MEDIUM] Theme ignores the system setting
- **Detect:** light or dark forced with no system option; web pages without `color-scheme` (native controls and scrollbars stay light in dark mode) and no `prefers-color-scheme`; native apps not following `ThemeMode.system`, `UITraitCollection` or `isSystemInDarkTheme()`; the user's explicit choice not persisted.
- **Mech:** T `git grep -qIE 'prefers-color-scheme|color-scheme|ThemeMode\.system|isSystemInDarkTheme|userInterfaceStyle|AppCompatDelegate\.setDefaultNightMode' -- ':!*.md' || echo 'no system theme handling in tracked code'` · `git grep -nIE 'ThemeMode\.(light|dark)|color-scheme:[[:space:]]*(light|dark)[[:space:]]*;|overrideUserInterfaceStyle' -- ':!*.md'`
- **Fix:** default to the system theme, offer light/dark/system, persist the choice; declare `color-scheme` on the root.
- **Impact:** a bright screen at night, or mismatched native controls, on every visit.
- **Source:** Least astonishment; MDN, prefers-color-scheme and color-scheme; Apple HIG, Dark Mode; Material Design, Dark theme.

### THM-01 [MEDIUM] Theme applied to only part of the UI
- **Detect:** a dark, high-contrast or density mode that some screens or components ignore (hard-coded light surfaces, images with white backgrounds, unthemed third-party widgets); pure black (`#000000`) dark surfaces where elevation needs grey steps; contrast checked only in the default theme (AXE-03).
- **Mech:** M (switch every theme and mode and walk the main screens)
- **Fix:** every component reads the same semantic tokens; dark surfaces from the theme's grey steps (Material uses #121212 as the base); transparent or theme-specific images; contrast checked per theme.
- **Impact:** a half-applied theme looks broken and hides text on mismatched surfaces.
- **Source:** Material Design, Dark theme; Apple HIG, Dark Mode.

### THM-06 [MEDIUM] Flash of wrong theme or empty content on start
- **Detect:** the page or app first paints in the default theme and then switches; a white flash between splash screen and first content; theme applied from several code paths; first render before required initial data, then reflow.
- **Mech:** M
- **Fix:** set the theme before first paint (inline script reading the stored choice, the platform splash API); render a skeleton until required data arrives; apply the theme in one place.
- **Impact:** every start flickers, which reads as slow and unfinished.
- **Source:** MDN, prefers-color-scheme; Android, SplashScreen API; web.dev, CLS.

### RSP-04 [HIGH] Text overflows its container
- **Detect:** long words, URLs, user names or translated strings that overflow fixed-width rows, buttons and table cells; flex children without `min-width: 0`; no wrapping or truncation policy; Flutter `Row` with unbounded `Text` (overflow stripes), fixed-width native labels.
- **Mech:** T `git grep -nIE 'white-space:[[:space:]]*nowrap' -- '*.html' '*.css' '*.scss' '*.less' '*.vue' '*.svelte'`
- **Fix:** wrap by default; truncate deliberately with the full text available (tooltip or detail view); `min-width: 0` and `overflow-wrap: anywhere` where needed; `Flexible`/`Expanded` around native text; test with long and translated strings (I18N-01 pseudo-locale).
- **Impact:** overflowing text hides content or controls, worst in longer languages.
- **Source:** MDN, overflow-wrap and text-overflow; Flutter, Common Flutter errors (RenderFlex overflowed).

### RSP-08 [MEDIUM] Layout fixed to one window size
- **Detect:** one phone-width layout stretched on tablets, foldables, desktop windows and landscape; no window-size breakpoints; desktop or web windows that break when resized narrow.
- **Mech:** M (check compact, medium and expanded widths)
- **Fix:** layouts for compact (< 600 dp), medium (600–840 dp) and expanded widths: multi-pane and navigation rail where space allows; test resizing.
- **Impact:** large-screen users get a stretched phone UI; small windows lose controls.
- **Source:** Material Design 3, Window size classes; Apple HIG, Layout.

### RSP-16 [LOW] Numbers misaligned in tables and lists
- **Detect:** numeric columns (amounts, counts, dates) left- or centre-aligned or in proportional figures; headers aligned differently from their column.
- **Mech:** T `git grep -qIE 'tabular-nums|tnum|FontFeature\.tabularFigures|monospacedDigit' -- ':!*.md' || git grep -lIE '<(table|td)[[:space:]>]|DataTable' -- '*.html' '*.jsx' '*.tsx' '*.vue' '*.svelte' '*.dart'`
- **Fix:** right-align numbers with tabular figures; align headers with their data.
- **Impact:** users misread magnitudes when digits do not line up.
- **Source:** Butterick, Practical Typography (tabular figures).

### VIS-22 [LOW] Images stretched out of aspect ratio
- **Detect:** images scaled with fill modes that distort (`BoxFit.fill`, `resizeMode="stretch"`, `.scaleToFill`, `object-fit: fill`); mixed aspect ratios in one grid.
- **Mech:** T `git grep -nIE 'BoxFit\.fill|resizeMode=.?.?stretch|scaleToFill|object-fit:[[:space:]]*fill' -- ':!*.md'`
- **Fix:** cover or contain with a fixed aspect-ratio box.
- **Impact:** distorted photos and logos look broken.
- **Source:** MDN, object-fit; Flutter, BoxFit.

### SCH-08 [CRITICAL] Overlapping bookings of a finite resource not rejected
- **Detect:** when the product reserves time on a finite resource (room, seat, person, device), overlap checked at coarse slots instead of the half-open interval test `a.start < b.end && b.start < a.end`; checked only in the UI or only at final submit; the check and the insert not in one transaction or guarded by a constraint; the rejection shows no reason.
- **Mech:** M
- **Fix:** the interval test server-side in the same transaction as the insert (or a database exclusion constraint, e.g. Postgres `EXCLUDE USING gist` on a range), mirrored early in the UI; name the conflicting booking in the message.
- **Impact:** double bookings surface in person, the most trust-destroying failure such a product can have.
- **Source:** Allen's interval algebra; PostgreSQL, Exclusion constraints; CWE-362 (race condition).
