# Rules: UX (Nielsen 10 + Interaction Laws + Perceived Performance + Forms + Error Presentation + Deceptive Patterns + Notifications + Writing + IA + Navigation Safety)

Rules applied during audit and fix runs. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

Applies to all UI platforms: web, mobile, desktop.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Heuristics (Nielsen 10 + dev-skills UX-10a/10b)** | UX-01 to UX-10, UX-10a, UX-10b (12 rules) | ~28 |
| **Onboarding / First-Use Flow** | UX-ON-01 to UX-ON-05 (5 rules) | ~116 |
| **Activation / Time-to-Value** | UX-AC-01 to UX-AC-02 (2 rules) | ~155 |
| **Interaction Laws (Laws of UX)** | UX-LX-01 to UX-LX-07 (7 rules) | ~175 |
| **Perceived Performance & Optimism** | UX-PP-01 to UX-PP-03 (3 rules) | ~230 |
| **Forms: Validation Strategy** | UX-FM-01 to UX-FM-02 (2 rules) | ~255 |
| **Error Presentation** | UX-EP-01 (1 rule) | ~273 |
| **Deceptive Patterns** | UX-DP-01 to UX-DP-03 (3 rules) | ~284 |
| **Notifications & Interruption Budget** | UX-NT-01 (1 rule) | ~311 |
| **UX Writing** | UX-WR-01 to UX-WR-04 (4 rules) | ~322 |
| **Information Architecture** | UX-IA-01, UX-IA-02, UX-16 (3 rules) | ~354 |
| **Navigation Safety** | UX-NS-01 (1 rule) | ~379 |
| **Filtering & Bulk Selection** | UX-11 (1 rule) | ~390 |
| **Status & Health Communication** | UX-12 (1 rule) | ~399 |
| **Tooltip Discipline** | UX-13 (1 rule) | ~410 |
| **Validation Severity** | UX-14 (1 rule) | ~421 |
| **Audit & History Surfaces** | UX-15 (1 rule) | ~432 |

---

## Heuristics (Nielsen 10 + dev-skills UX-10a/10b)

### UX-01 [HIGH] Visibility of System Status
applies_when: ui≠none
The system keeps users informed about what is happening through appropriate feedback within reasonable time.
- **Detect:** Async action (submit, save, delete, upload) with no loading indicator, spinner, progress bar, or disabled-state feedback during the pending window; state change (toggle, filter, sort) with no visual confirmation.
- **Fix:** Add a loading/pending state for every async action >100ms; confirm state changes with a toast, inline message, or visual diff (checkmark, highlight).
- **Impact:** Users without status feedback assume the app is broken and repeat the action (duplicate submits) or abandon the task.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 1)

### UX-02 [HIGH] Match Between System and the Real World
applies_when: ui≠none
The system speaks the users' language, with familiar words, phrases, and concepts, following real-world conventions.
- **Detect:** Internal jargon, error codes, or database field names surfaced verbatim in user-facing copy (`ERR_4001`, `null`, `undefined`, `NPE`); icons with no accompanying label for non-standard actions.
- **Fix:** Replace internal identifiers with plain-language copy; pair novel icons with text labels or tooltips.
- **Impact:** Users cannot act on errors or labels they don't understand — support-ticket volume rises.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 2)

### UX-03 [HIGH] User Control and Freedom
applies_when: ui≠none
Users need a clearly marked "emergency exit" to leave an unwanted state without going through an extended process.
- **Detect:** Multi-step flow (wizard, checkout, onboarding) with no back/cancel affordance; destructive action (delete, send, publish) with no confirm step or undo window; modal with no close button or Escape-key handler.
- **Fix:** Add cancel/back at every step; add a confirm dialog or a timed undo (5-10s) for destructive actions; every modal closable via explicit control + Escape.
- **Impact:** Users trapped in a flow abandon the task entirely rather than search for an exit.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 3)

### UX-04 [MEDIUM] Consistency and Standards
applies_when: ui≠none
Users should not have to wonder whether different words, situations, or actions mean the same thing — follow platform and internal conventions.
- **Detect:** Same action labeled differently across screens ("Delete" vs "Remove" vs "Trash" for the same operation); same icon used for different actions in different views; primary-button placement inconsistent across comparable screens.
- **Fix:** One verb per action class, enforced repo-wide (cross-reference `contract-consistency` scope in ds-blueprint); one icon-to-action mapping; consistent primary-action placement per platform convention.
- **Impact:** Inconsistent terminology forces users to relearn the interface on every screen, raising cognitive load and error rate.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 4)

### UX-05 [HIGH] Error Prevention
applies_when: ui≠none
Eliminate error-prone conditions, or check for them and present a confirmation before users commit to the action.
- **Detect:** Free-text input where a constrained control (select, date-picker, toggle) would prevent invalid values; irreversible action with no confirmation step; form that allows submission of a state known to be invalid (e.g., end-date before start-date) without inline validation.
- **Fix:** Replace free-text with constrained controls where the value space is enumerable; add confirmation for irreversible actions; validate inline before submission, not only after.
- **Impact:** Every prevented error is a support ticket and a recovery flow the user never has to endure.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 5)

### UX-06 [MEDIUM] Recognition Rather Than Recall
applies_when: ui≠none
Minimize the user's memory load by making elements, actions, and options visible or easily retrievable.
- **Detect:** Multi-step flow requiring the user to remember a value entered in an earlier step with no on-screen recap; command/action available only via a shortcut with no visible menu entry; search/filter with no recent-values or autocomplete.
- **Fix:** Surface prior-step values in a summary panel; expose every shortcut-only action in a visible menu; add autocomplete/recents to search and filter inputs.
- **Impact:** Recall-dependent interfaces disproportionately fail novice and infrequent users.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 6)

### UX-07 [LOW] Flexibility and Efficiency of Use
applies_when: ui≠none
Accelerators — unseen by the novice user — may speed up the interaction for the expert user, so the design caters to both.
- **Detect:** High-frequency action (per product analytics or repo-declared primary flow) with no keyboard shortcut, bulk-action, or saved-preset path; power-user flow requires the same number of steps as the first-time flow.
- **Fix:** Add keyboard shortcuts for the top 3-5 most frequent actions; add bulk operations (select-all, batch-apply) where single-item flows repeat; add saved presets/filters for repeat configurations.
- **Impact:** Without accelerators, expert users pay the novice-user tax on every use, increasing task time at scale.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 7)

### UX-08 [MEDIUM] Aesthetic and Minimalist Design
applies_when: ui≠none
Interfaces should not contain irrelevant or rarely needed information that competes with the relevant units of information.
- **Detect:** Screen presenting more than the primary + 1-2 secondary actions above the fold; dense forms exposing rarely-used optional fields by default instead of behind "Advanced"/"More options"; decorative elements with no functional or wayfinding purpose competing for attention with primary content.
- **Fix:** Collapse rarely-used fields behind progressive disclosure; limit primary actions per screen to 1 (with secondary actions visually subordinate); remove decoration that doesn't aid comprehension or wayfinding.
- **Impact:** Visual clutter raises the time and error rate for finding the primary action, especially for first-time and low-vision users.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 8)

### UX-09 [HIGH] Help Users Recognize, Diagnose, and Recover from Errors
applies_when: ui≠none
Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.
- **Detect:** Error message stating only that something failed ("Something went wrong", "Error") with no cause or next step; error message exposing a raw stack trace or internal exception to the end user; error with no visible recovery action (retry, edit, contact support).
- **Fix:** Every error states what was expected, what happened, and how to fix it (mirrors this project's own Error Message quality bar); never surface raw stack traces to end users; pair every error with a recovery action.
- **Impact:** Vague errors convert a recoverable failure into task abandonment.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 9)

### UX-10 [LOW] Help and Documentation
applies_when: ui≠none
Even though it's better if the system can be used without documentation, providing help and documentation may be necessary.
- **Detect:** Non-trivial feature (multi-step config, integration setup, advanced filter syntax) with no in-context help (tooltip, inline hint, linked doc) and no entry in the product's documentation surface (cross-reference `B6` documentation dimension).
- **Fix:** Add in-context help for non-trivial features; ensure the doc surface (ds-docs B6) covers each one; keep help task-focused and searchable, not a monolithic manual.
- **Impact:** Undocumented complexity forces users to trial-and-error or abandon the feature.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 10)

### UX-10a [HIGH] AI Output Transparency
applies_when: integrations contain an LLM/AI provider (`OPENAI_`, `ANTHROPIC_`, or an SDK import)
AI-generated or AI-assisted content is labeled, and claims presented as fact are traceable to a source.
- **Detect:** AI-generated summary, suggestion, or content block rendered indistinguishably from human-authored or ground-truth content; AI-generated factual claim (price, statistic, citation) with no visible source or "AI-generated — verify" affordance; AI chat/assistant response with no indication that a human is not on the other end.
- **Fix:** Label AI-generated content at the point of display (badge, "Generated by AI" caption, or distinct visual treatment); attach source links or a "why am I seeing this" affordance to AI-derived claims; disclose AI vs human agent identity in conversational UIs.
- **Impact:** Unlabeled AI content erodes trust once discovered, and unsourced AI claims propagate hallucinations as fact.
- **Source:** dev-skills extension, not an official NN/g heuristic — verified 2026-07-11 against [nngroup.com/articles/ten-usability-heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), which states the 10 heuristics "have remained relevant and unchanged since 1994." Added here to cover an AI-transparency gap the original 10 don't address.

### UX-10b [HIGH] AI Interaction Affordances
applies_when: integrations contain an LLM/AI provider (`OPENAI_`, `ANTHROPIC_`, or an SDK import)
LLM-backed features stream output, stay interruptible, and scope uncertainty display to stakes.
- **Detect:** AI response rendered as spinner-then-full-dump instead of incremental token streaming; generation in progress with no "Stop Generation" control; confidence/uncertainty indicators attached to every response regardless of stakes (indicator fatigue), or absent on high-stakes outputs (medical, financial, legal, destructive actions); multi-step agent flows with no visible deliberation/progress state.
- **Fix:** Stream tokens incrementally (reduced-opacity or cursor treatment while in flight); always provide a Stop Generation control so users don't wait out an irrelevant answer; show step-level progress for multi-step/agentic flows; use confidence indicators only where being wrong has meaningful stakes — not on every response.
- **Impact:** A non-interruptible spinner-dump turns every bad generation into forced waiting; unscoped confidence chrome trains users to ignore the one warning that matters.
- **Source:** AI-feature UX research (streaming + stop-control + stakes-scoped uncertainty conventions); receives delegation from ds-backend `llm` scope.

---

## Onboarding / First-Use Flow

### UX-ON-01 [HIGH] First-Run Path Exists and Is Bounded
applies_when: ui≠none
A first-time user reaches a working state without reading external documentation.
- **Detect:** No distinguishable first-run experience (empty state, welcome screen, guided setup) for a new account/workspace/project; first-run path requires more than 5 user actions (clicks/taps/keystrokes) before the user reaches a usable state.
- **Fix:** Add a first-run experience distinct from the steady-state UI; bound it to ≤5 actions to first usable state, or break it into resumable steps with visible progress.
- **Impact:** Products without a bounded first-run path lose new users to abandonment before they experience any value.
- **Source:** Nielsen Norman Group — Onboarding UX; RT2 ([dev-skills research trace](https://github.com/sungurerdim/dev-skills/blob/main/specs/001-v4-coverage-standalone/research.md))

### UX-ON-02 [MEDIUM] Empty States Teach, Not Just Announce
applies_when: ui≠none
Every empty state (no data yet) explains what belongs there and how to add it, not just "No items."
- **Detect:** Empty list/table/dashboard rendering only a "No X found" message with no call-to-action to create the first item, and no example of what populated state looks like.
- **Fix:** Pair every empty state with a primary CTA ("Create your first X") and, where feasible, a preview/illustration of populated state.
- **Impact:** A bare empty state is a dead end for new users who don't yet know what the feature does.
- **Source:** Nielsen Norman Group — Empty State Design

### UX-ON-03 [MEDIUM] Progressive Disclosure During Setup
applies_when: ui≠none
Setup/onboarding requests only the information required to reach first value; optional configuration is deferred.
- **Detect:** Sign-up or setup flow collecting fields not required until a later feature is used (e.g., billing details before any paid action, notification preferences before any notification-triggering event).
- **Fix:** Move non-blocking fields to post-onboarding settings, defaults, or just-in-time prompts triggered when the field becomes relevant.
- **Impact:** Every non-essential field in the setup path raises drop-off before the user has experienced any value.
- **Source:** Nielsen Norman Group — Progressive Disclosure

### UX-ON-04 [MEDIUM] Auto-Navigate + Auto-Resume for Unavoidable Manual External Steps
applies_when: a setup/connection flow includes a manual external step (e.g. OAuth consent, API key generation, store approval)
When an otherwise-automated setup/connection flow hits one step with no programmatic API — a manual console toggle, a one-time consent screen, an app-store approval — the app deep-links the user to the exact right external page and auto-resumes the flow on return, instead of leaving a written instruction to go do it themselves.
- **Detect:** A setup/onboarding flow describing an external step only as prose ("go to Settings → API → enable X, then come back") with no deep link to the exact page; no detection of the user's return (focus/visibility-change, redirect callback, or polling) to auto-continue; the user must manually find their way back and re-trigger the next step themselves.
- **Fix:** Deep-link directly to the specific external page/screen the manual step requires (not its parent settings area). On return, auto-detect completion (poll the resource, listen for a redirect callback, or check on focus-regain) and resume the flow at the next step without requiring manual re-navigation.
- **Impact:** A "go do this yourself" instruction is a common abandonment point — users lose the thread in an unfamiliar external UI and don't return; auto-navigate + auto-resume preserves the flow's momentum through a step the app genuinely can't automate away.
- **Source:** Extends UX-ON-01 (bounded first-run path) to the specific case of an unavoidable external dependency with no automatable API

### UX-ON-05 [MEDIUM] Onboarding Is Skippable for Returning and Existing Users
applies_when: ui≠none
A first-run or re-introduction flow never re-traps a user who has already reached productive use — returning users can skip straight past it.
- **Detect:** An onboarding/tour/tutorial flow triggered again after a feature update, re-login, or new-device sign-in with no visible skip/dismiss control, forcing an already-oriented user through the full sequence; onboarding state keyed only to account creation with no per-flow "seen it" tracking for incremental feature tours.
- **Fix:** Track completion/dismissal per onboarding flow (not just account-level), and always render a visible skip/close control; re-triggered tours for existing users default to a compact "what's new" entry point, not the full first-run sequence.
- **Impact:** Forcing a returning user through a first-timer flow they've already completed reads as the product not recognizing them, and burns the same abandonment risk the flow exists to prevent.
- **Source:** [Nielsen Norman Group — Onboarding Tutorials](https://www.nngroup.com/articles/onboarding-tutorials/)

---

## Activation / Time-to-Value

### UX-AC-01 [HIGH] First-Success Step Count Is Measured and Bounded
applies_when: ui≠none
The number of steps from first-run to the user's first successful outcome (the product's core value moment) is known and ≤ the product's stated target.
- **Detect:** No instrumented or documented step count from account/session start to first core-value event (first message sent, first file processed, first report generated — product-specific); step count exceeds 7 discrete user actions with no justification tied to the domain (e.g., regulated onboarding).
- **Fix:** Instrument or manually trace the first-run → first-success path; if it exceeds 7 actions, cut, merge, or defer steps until it doesn't, or record an explicit justification in the blueprint profile Priorities/Constraints.
- **Impact:** Time-to-value is the strongest predictor of activation-to-retention conversion; unmeasured time-to-value means regressions ship undetected.
- **Source:** RT2 ([dev-skills research trace](https://github.com/sungurerdim/dev-skills/blob/main/specs/001-v4-coverage-standalone/research.md)); product-led-growth activation literature

### UX-AC-02 [MEDIUM] Core Value Moment Is Explicit and Celebrated
applies_when: ui≠none
The product marks the moment the user reaches first value (visually, not just functionally).
- **Detect:** First-success event (first save, first successful integration, first completed task) produces no distinguishable feedback beyond the generic loading/success pattern used elsewhere in the app.
- **Fix:** Add a distinguishable first-success moment (confirmation, next-step suggestion, or lightweight celebration) tied specifically to the first occurrence of the core-value event.
- **Impact:** An unmarked value moment leaves the user unsure whether they succeeded, undermining the activation the product just achieved.
- **Source:** RT2 ([dev-skills research trace](https://github.com/sungurerdim/dev-skills/blob/main/specs/001-v4-coverage-standalone/research.md))

---

---

## Interaction Laws (Laws of UX)

Catalog: [lawsofux.com](https://lawsofux.com/) (Yablonski) `[single-source aggregator]` — each law traces to original research named per rule. **Auditor-bias note (Aesthetic-Usability Effect):** a visually polished UI is *perceived* as more usable and masks real usability flaws — never soften a finding's severity because the screen looks good.

### UX-LX-01 [MEDIUM] Choice Overload at Decision Points (Hick + Miller)
applies_when: ui≠none
Decision time grows with the number and complexity of choices; working memory holds ~7±2 chunks.
- **Detect:** Menu, nav bar, settings screen, or picker presenting >7 ungrouped options at one level; onboarding/checkout step asking multiple unrelated decisions at once; long flat lists where grouping or search exists nowhere.
- **Fix:** Chunk options into labeled groups; split compound decision steps; add search/filter to long option lists; move rare options behind progressive disclosure (UX-08).
- **Impact:** Every extra simultaneous choice raises decision latency and abandonment at exactly the points (nav, checkout) where hesitation costs most.
- **Source:** Laws of UX — Hick's Law, Miller's Law `[single-source]` (originals: Hick 1952; Miller 1956)

### UX-LX-02 [MEDIUM] Action Distance (Fitts)
applies_when: ui≠none
Target acquisition time is a function of distance to and size of the target — actions live next to the objects they act on.
- **Detect:** Per-item action (edit/delete/reply) rendered far from the item it affects (e.g. a global toolbar acting on a list selection below the fold); form submit separated from the form by unrelated content; on mobile, the primary action outside the natural thumb zone while rare actions occupy it.
- **Fix:** Co-locate actions with their objects (row-level actions on the row, submit directly under the form); reserve the easiest-to-reach positions for the highest-frequency actions. Target *size* is audited by the accessibility target-size rule — this rule owns *distance*.
- **Impact:** Distant targets add pointing time to every interaction and break the visual object-action link, causing wrong-object operations.
- **Source:** Laws of UX — Fitts's Law `[single-source]` (original: Fitts 1954)

### UX-LX-03 [MEDIUM] Convention Adherence (Jakob)
applies_when: ui≠none
Users expect a new UI to work like the products they already use — deviation from platform/domain convention needs a reason.
- **Detect:** Novel interaction pattern where a dominant convention exists (cart icon not in the header, settings not behind a gear/avatar, non-standard gesture replacing a visible control, scroll hijacking); platform-convention mismatch (web app overriding browser back, desktop app without native menu/shortcut conventions).
- **Fix:** Default to the dominant convention; keep innovation for the product's differentiating interaction only, and pair it with an on-ramp (hint, fallback control). Cross-ref [controlled-vs-innovative.md](controlled-vs-innovative.md).
- **Impact:** Every convention break spends user trust and adds relearning cost — users blame themselves, then leave.
- **Source:** Laws of UX — Jakob's Law `[single-source]` (Nielsen)

### UX-LX-04 [MEDIUM] Ordering & Salience (Serial Position + Von Restorff)
applies_when: ui≠none
First and last positions are best remembered; one visually distinct item among uniform peers draws recall and attention.
- **Detect:** Critical nav/menu items buried mid-list while low-value items hold the first/last slots; primary CTA visually identical to its neighbor actions (no salience); MORE than one "distinct" element per view competing for the Von Restorff slot (everything highlighted = nothing highlighted).
- **Fix:** Place the highest-value items at list start/end; give exactly one primary action per view distinct weight; demote decorative highlights that compete with it.
- **Impact:** Mid-list burial and salience inflation both push users toward wrong or slower choices on every visit.
- **Source:** Laws of UX — Serial Position Effect, Von Restorff Effect `[single-source]` (originals: Ebbinghaus; von Restorff 1933)

### UX-LX-05 [MEDIUM] Progress Visibility in Multi-Step Flows (Goal-Gradient + Zeigarnik)
applies_when: ui≠none
Motivation rises with visible proximity to completion; interrupted tasks stay mentally open — show progress and make resumption easy.
- **Detect:** Multi-step flow (wizard, onboarding, checkout) with no step indicator or completion signal; interruptible long task (profile setup, import) with no resumable state or "continue where you left off" entry point; progress indicator that starts at 0% when prior steps are already done (artificial-start omission).
- **Fix:** Add a step/progress indicator that credits completed work (start >0% when justified); persist partial progress and surface a resume affordance on return.
- **Impact:** Invisible progress and lost partial work are the two dominant causes of multi-step abandonment.
- **Source:** Laws of UX — Goal-Gradient Effect, Zeigarnik Effect `[single-source]` (originals: Hull 1932; Zeigarnik 1927)

### UX-LX-06 [MEDIUM] Input Tolerance (Postel)
applies_when: a form or free-text input surface is present
Be liberal in what you accept from users, conservative in what you emit — normalize instead of rejecting.
- **Detect:** Input rejected for recoverable formatting the code could normalize: spaces/dashes in card, IBAN, or phone numbers; case-sensitive email/username match; trailing whitespace failing validation; date accepted in only one rigid format when the locale implies others.
- **Fix:** Trim, strip separators, and case-normalize before validating; accept the formats users actually paste; keep the *stored/emitted* value strictly canonical.
- **Impact:** Every rejection of normalizable input converts a completed user intention into an error state the code caused.
- **Source:** Laws of UX — Postel's Law `[single-source]` (original: RFC 761 robustness principle)

### UX-LX-07 [MEDIUM] Complexity Placement (Tesler)
applies_when: ui≠none
Inherent complexity cannot be eliminated — it can only be moved; move it into the system, not onto the user.
- **Detect:** User asked for a value the system can derive (country from locale/GeoIP suggestion, card type from number, timezone from device); configuration required before first use where a working default exists; every option exposed because "the user should decide".
- **Fix:** Derive what is derivable (editable, not locked); ship working defaults with override; absorb decision complexity into smart defaults and keep the choice available for the minority that needs it.
- **Impact:** Complexity pushed onto users taxes every user on every use; complexity absorbed into the system costs the developer once.
- **Source:** Laws of UX — Tesler's Law `[single-source]` (Tesler, Xerox PARC)

---

## Perceived Performance & Optimism

### UX-PP-01 [HIGH] Optimistic UI Has a Rollback Path
applies_when: ui≠none and api≠none
Optimistic updates (UI reflects success before the server confirms) are used only for fast, reliable, reversible actions — and always with rollback.
- **Detect:** UI state updated before request resolution with no failure handler that reverts the state and informs the user; optimistic pattern on non-reversible or high-stakes actions (payment, send, delete, publish); rollback that silently reverts with no explanation of what failed.
- **Fix:** Pair every optimistic update with an error path that restores prior state + surfaces a plain-language notice with retry; use pessimistic (wait-for-server) flow for payments, sends, and destructive actions.
- **Impact:** An optimistic update without rollback shows the user a success that never happened — data-loss-grade trust damage when discovered.
- **Source:** [Smashing Magazine — Optimistic UIs](https://www.smashingmagazine.com/2016/11/true-lies-of-optimistic-user-interfaces/); [Hearne — Optimistic UI Patterns](https://simonhearne.com/2021/optimistic-ui-patterns/)

### UX-PP-02 [HIGH] Interaction Responsiveness Budget (INP)
applies_when: ui≠none (INP field/lab measurement specifically requires platforms∋web)
Interactions respond within the Core Web Vitals INP budget: Good ≤200ms at the 75th percentile (Needs Improvement 200-500ms, Poor >500ms).
- **Detect:** Web: no INP measurement (field data or lab proxy) for the primary flows; long tasks >50ms blocking the main thread on interaction handlers; synchronous heavy work (large render, JSON parse, layout thrash) inside click/input handlers. All platforms: any interaction regularly exceeding ~400ms with no immediate feedback (Doherty threshold `[single-source]`).
- **Fix:** Yield long tasks (`scheduler.postTask`/`setTimeout` chunking), move heavy work off the interaction path (worker, defer), show immediate feedback (UX-01) when real work must exceed the budget.
- **Impact:** Interactions over budget read as "broken" — users re-click (duplicate actions) or leave; INP is also a ranking-relevant field metric.
- **Source:** [web.dev — INP](https://web.dev/articles/inp) (thresholds verified 2×, 2026-07-17); Laws of UX — Doherty Threshold `[single-source]`

### UX-PP-03 [MEDIUM] Loading Pattern Matches What Is Known Before Render
applies_when: ui≠none
The loading pattern communicates what the system already knows about the incoming content — skeleton screens when the layout is known, spinners only when it is not.
- **Detect:** A generic spinner used for content whose layout/shape is already known (a list, a card grid, a known-shape detail page) instead of a skeleton matching that shape; a full-page spinner used for a partial, below-the-fold, or code-split region instead of scoping the loading state to that region.
- **Fix:** Use a skeleton screen shaped like the incoming content whenever the layout is known ahead of the fetch; reserve bare spinners for genuinely unknown-layout or full-page loads; scope loading boundaries to the region that's actually pending, not the whole page.
- **Impact:** A skeleton communicates structure and progress the instant it renders — response within the "feels instant" perceptual window keeps users in flow — while an undifferentiated spinner reads as dead time regardless of actual latency.
- **Source:** [Nielsen Norman Group — Response Times: The 3 Important Limits](https://www.nngroup.com/articles/response-times-3-important-limits/)

---

## Forms: Validation Strategy

### UX-FM-01 [HIGH] One Deliberate Validation-Timing Strategy + Error Summary
applies_when: a form or input-validation surface is present
The product picks ONE validation-timing strategy deliberately and applies it consistently; long forms pair errors with a summary that links to fields.
- **Detect:** Mixed timing across forms (some validate on blur, some on submit, some on keystroke) with no documented choice; premature validation that flags a field as wrong *while the user is still typing* their first entry; submit-time errors shown only inline on a long form with no top error summary; error summary entries not linked/focused to their fields.
- **Fix:** Choose and document one strategy — (a) GOV.UK: validate on submit only + error summary component at top, each entry a link that moves focus to its field; or (b) reward-early/punish-late: validate a field immediately once it *becomes* valid, but flag errors only after the user leaves it. Never punish mid-typing. Cross-ref rules-accessibility.md AXE-14 (autocomplete/input purpose) and error-association rules.
- **Impact:** Inconsistent or premature validation trains users to distrust the form; unlinked errors on long forms strand users hunting for the failing field.
- **Source (both positions kept — documented contradiction):** [GOV.UK — validation pattern](https://design-system.service.gov.uk/patterns/validation/) + [error summary](https://design-system.service.gov.uk/components/error-summary/) vs [Smart Interface Design Patterns — inline validation](https://smart-interface-design-patterns.com/articles/inline-validation-ux/), [NN/g — hostile error messages](https://www.nngroup.com/articles/hostile-error-messages/)

### UX-FM-02 [MEDIUM] Form Layout: Single-Column, Top-Aligned Labels
applies_when: a form is present
Long forms complete at a higher rate as a single column with labels above their fields, especially on mobile.
- **Detect:** A form with more than one visual column of unrelated fields (side-by-side fields that aren't a genuine pair like City/State); labels placed to the left of their input on a narrow (mobile) viewport instead of above it.
- **Fix:** Lay out forms as a single column top-to-bottom; place labels directly above their field, not beside it, on narrow viewports. Reserve side-by-side placement for fields that are a genuine logical pair (e.g. City/State/ZIP) at wide viewports only.
- **Impact:** Multi-column and left-aligned-label forms measurably raise completion time and abandonment versus single-column, top-aligned layouts.
- **Source:** [Nielsen Norman Group — Web Form Design](https://www.nngroup.com/articles/web-form-design/)

---

## Error Presentation

### UX-EP-01 [MEDIUM] Error Presentation Channel Matches Error Scope
applies_when: ui≠none
The channel an error is shown in matches its scope and severity — a field-level problem stays inline, a transient/recoverable issue uses a toast, and a decision-blocking error uses a dialog.
- **Detect:** A single field's validation error shown as a page-level toast/banner instead of inline at the field; a transient, auto-recoverable issue (network retry, a background sync) interrupting the user with a blocking dialog; a decision-blocking error (data loss risk, an action that cannot proceed) shown only as a toast that can be missed or auto-dismisses before it's read.
- **Fix:** Field-level problems render inline next to the field; transient/recoverable issues use a toast/snackbar that doesn't block interaction; errors requiring a decision before the user can proceed use a dialog that blocks until acknowledged.
- **Impact:** A mismatched channel either interrupts the user for something that didn't need it or lets a blocking problem slip past as an ignorable toast.
- **Source:** [Nielsen Norman Group — Error Message Guidelines](https://www.nngroup.com/articles/error-message-guidelines/)

---

## Deceptive Patterns (Never Ship These)

Canonical catalog: [deceptive.design/types](https://www.deceptive.design/types). These carry legal exposure (FTC negative-option enforcement, EU consumer law) on top of trust damage.

### UX-DP-01 [HIGH] Preselection Steering
applies_when: a consent, upsell, add-on, or subscription-tier selection surface is present
No pre-checked choice commits the user to something not required for the requested service.
- **Detect:** Pre-checked checkboxes for marketing consent, data sharing, add-on purchases, subscriptions, or "donation/tip" amounts; default-selected paid tier where a free path exists but is visually demoted.
- **Fix:** Ship consent and upsell choices unchecked; make the no-extra path equally visible; preselect only what the user's explicit request implies.
- **Impact:** Preselection converts inattention into unwanted commitments — refund/complaint load plus consent invalid under GDPR-class rules (cross-ref ds-compliance consent rules).
- **Source:** [deceptive.design — Preselection](https://www.deceptive.design/types) `[single-source]` (catalog); consent-validity: GDPR Art. 4(11) active-consent standard

### UX-DP-02 [HIGH] Cancellation Parity
applies_when: billing≠none or an account-deletion/unsubscribe flow is present
Cancelling, unsubscribing, or downgrading is as easy as signing up — same channel, comparable step count.
- **Detect:** Online signup but cancellation only via phone/chat/email; cancellation flow with retention interstitials exceeding one clearly skippable offer; "delete account" absent or buried while "upgrade" is one click; unsubscribe link missing or requiring login.
- **Fix:** Provide cancellation in the same channel as signup with comparable effort; one optional retention offer max, skippable; account deletion reachable and completable online.
- **Impact:** Obstructed exits are the most-enforced deceptive pattern (FTC negative-option actions, EU consumer law) and the fastest trust-to-chargeback converter.
- **Source:** [deceptive.design — Hard to cancel](https://www.deceptive.design/types); FTC negative-option enforcement coverage (2026) — rule's litigation status recorded as contradiction in research notes; parity is the safe bar regardless

### UX-DP-03 [HIGH] Honest Pricing & Presentation
applies_when: billing≠none
All mandatory costs are visible before effort is invested; information is never hidden, disguised, or nagged past.
- **Detect:** Mandatory fees (service, booking, shipping minimums) first revealed at the final checkout step; visually demoted decline options ("confirmshaming" microcopy, low-contrast reject button vs high-contrast accept); countdown/scarcity claims not backed by real data; repeated interrupting prompts for the same permission/upsell after the user declined.
- **Fix:** Show full mandatory price as early as a price is shown; give accept/decline equal visual weight; remove or data-back urgency claims; respect a decline for the session at minimum.
- **Impact:** Late fees and interference patterns trade one-time conversion for churn, chargebacks, and regulator attention.
- **Source:** [deceptive.design — Hidden costs, Visual interference, Nagging](https://www.deceptive.design/types) `[single-source]` (catalog); EU Omnibus/CPC price-transparency enforcement practice

---

## Notifications & Interruption Budget

### UX-NT-01 [HIGH] Notification Frequency Stays Under the Abandonment Threshold
applies_when: a notification-sending feature is present (push, email, or in-app)
Per-user notification volume (push, email, in-app) is capped low enough that it doesn't drive unsubscribes or app abandonment.
- **Detect:** No enforced per-user daily/weekly notification cap across all notification-triggering features combined (each feature owns its own trigger with no shared budget); notification volume for an active user regularly exceeding roughly 5/day with no user-configurable frequency control.
- **Fix:** Enforce one shared per-user notification budget across every feature that sends them (not per-feature limits that sum uncontrolled); default to ≤5/day-equivalent; give users a visible frequency/category control rather than all-or-nothing opt-out.
- **Impact:** Unsubscribe rate rises sharply past roughly 10-15 notifications/day and app abandonment follows — over-notification is a top-cited reason for both muting and uninstalling.
- **Source:** [Business of Apps — Push Notification Statistics](https://www.businessofapps.com/marketplace/push-notifications/research/push-notifications-statistics/)

---

## UX Writing

### UX-WR-01 [MEDIUM] Buttons Name Their Outcome
applies_when: ui≠none
Every action label states the specific outcome — one consistent verb per action class, no bare "OK"/"Submit"/"Yes".
- **Detect:** Generic labels (`OK`, `Submit`, `Yes`, `No`, `Continue` on a consequential step) where the outcome is nameable (`Save changes`, `Delete 3 items`, `Send message`); confirm dialogs whose buttons don't answer the question asked; the same operation labeled with different verbs across screens (defer to UX-04 for the consistency half).
- **Fix:** Rewrite labels as verb + object of the actual outcome; confirm-dialog buttons restate the choice (`Delete` / `Keep`), never `Yes`/`No`.
- **Impact:** Outcome-named buttons cut wrong-click rates on consequential actions — the label is the last defense before an unintended operation.
- **Source:** [Material Design — Writing guidance](https://m2.material.io/design/communication/writing.html); Google Material communication codelab (2×-confirmed)

### UX-WR-02 [LOW] Sentence Case for UI Text
applies_when: ui≠none
Titles, headings, labels, and buttons use sentence case — not Title Case, not ALL CAPS.
- **Detect:** Mixed casing conventions across views; ALL-CAPS body/label text (also a localization hazard — casing rules differ across locales, e.g. Turkish dotted/dotless i); Title Case in products that localize.
- **Fix:** Standardize on sentence case in the design system tokens/lint (one exception: proper nouns); remove CSS `text-transform: uppercase` from translatable strings.
- **Impact:** Sentence case reads faster, localizes safely, and removes per-screen casing debates.
- **Source:** [Material Design — Writing guidance](https://m2.material.io/design/communication/writing.html) (2×-confirmed)

### UX-WR-03 [LOW] Single-Heading Principle (Prune Redundant Subtitles)
applies_when: ui≠none
A subtitle/description directly under a heading renders only if it adds information the heading doesn't already state — a subtitle that merely paraphrases the heading in different words is pruned.
- **Detect:** A subtitle/description under a page or section heading that restates the heading (e.g. "History" heading, "Past records" subtitle) rather than adding a constraint, legal notice, count, or concrete detail the heading omits.
- **Fix:** Remove subtitles that only paraphrase; keep or add ones with genuine added information (a caveat, a behavior note, a count); remove the now-unused i18n string. Exempt: structural group/section labels within a multi-part form — those organize, they don't repeat.
- **Impact:** A paraphrasing subtitle adds visual clutter and scan cost with zero new information — pruning it is a pure, risk-free legibility win.
- **Source:** Nielsen Norman Group — content redundancy / scannability practice

### UX-WR-04 [LOW] Separator Convention and Platform-Safe Copy
applies_when: ui≠none
User-visible text uses one consistent separator convention, and copyable/shareable text is platform-safe by default.
- **Detect:** Mixed separators across surfaces (em-dash here, colon there); em-dashes in UI copy; copy-to-clipboard or share output that embeds emoji/styled characters by default.
- **Fix:** Pick one separator set (middle dot `·`, slash `/`, or colon) and apply it everywhere; avoid em-dashes in UI copy. Default copyable/shareable text to plain text; make emoji and decoration opt-in.
- **Impact:** Inconsistent separators read as sloppiness at scale; emoji-laden clipboard text breaks when pasted into CRMs, terminals, and legacy systems.
- **Source:** XR-167 + XR-062 — cross-project experience registry (2026).

---

## Information Architecture

### UX-IA-01 [MEDIUM] Navigation Depth Budget & Breadcrumbs
applies_when: ui≠none
Visible navigation supports 2-3 tiers; deeper hierarchies switch to breadcrumbs + landing pages instead of deeper menus.
- **Detect:** Nav menus nesting beyond 3 levels (flyout-in-flyout-in-flyout); content ≥3 levels deep with no breadcrumb trail; breadcrumb showing only the current page (no ancestor links) or breaking on direct/deep-linked entry; multi-user workspace product mixes personal-context surfaces (my settings, my day) and shared-workspace surfaces (team schedule, shared records) in one undifferentiated navigation tier
- **Fix:** Cap visible nav at 2-3 tiers; add breadcrumbs on every page below tier 2 (ancestors linked, current page unlinked); deep sections get section landing pages instead of deeper flyouts. In multi-user workspace products, separate the IA into two consistent tiers — personal context (e.g. `#/me/…`) and shared workspace (e.g. `#/workspace/…`) — and keep every surface clearly in one tier. (XR-137)
- **Impact:** Over-deep menus hide content from discovery; missing breadcrumbs strand deep-linked visitors (search/social arrivals) with no sense of place.
- **Source:** [NN/g — Local navigation](https://www.nngroup.com/articles/local-navigation/); [NN/g — Breadcrumbs](https://www.nngroup.com/articles/breadcrumb-navigation-useful/) (2×-confirmed)

### UX-IA-02 [MEDIUM] Primary Information Occupies the F-Pattern Scan Path
applies_when: ui≠none
Content placement matches how users actually scan a page — the highest-priority information sits where the first, heaviest scan passes land (top and left of the content area), not wherever layout convenience puts it.
- **Detect:** The primary identifying fact of a row/card/page (title, status, the thing the user came to find) placed to the right of or below secondary/metadata content (timestamps, IDs, tags) instead of leading it; dense list/table views with no consistent left-anchored primary column.
- **Fix:** Lead each row/card with its primary fact, top-left of the content block; keep metadata secondary in position and typographic weight; keep this ordering consistent across every comparable view.
- **Impact:** Content placed against the natural scan path is read late or missed entirely, especially on unfamiliar or dense screens.
- **Source:** [Nielsen Norman Group — F-Shaped Pattern of Reading on the Web](https://www.nngroup.com/articles/f-shaped-pattern-reading-web-content-discovered/)

### UX-16 [MEDIUM] Rarely-Used Aggregate Stats Leave the Primary Work Screen
applies_when: ui≠none and a dashboard/stats surface is present
Aggregate statistics consulted occasionally (KPI tiles, heatmaps, trend widgets) move to a dedicated report/stats screen instead of occupying the daily working view.
- **Detect:** The primary work screen dedicates permanent space to summary widgets users consult weekly or less; the working canvas is compressed to make room for them.
- **Fix:** Relocate occasional aggregates to a dedicated stats/report surface; keep them drillable (click → filtered detail view, per CMP-12) and make filtered work surfaces route-addressable so drill targets are linkable.
- **Impact:** Every pixel spent on rarely-read stats is taken from the screen users work in for hours — the core task gets the leftover space.
- **Source:** XR-050 — cross-project experience registry (2026).

---

## Navigation Safety

### UX-NS-01 [HIGH] Unsaved-Work Confirmation on Exit or Navigate-Away
applies_when: ui≠none
Leaving a screen that holds unsaved user input — via back navigation, closing a tab, or an in-app route change — never silently discards that input.
- **Detect:** A form, editor, or multi-step flow with dirty (unsaved, unsubmitted) input where browser back, an in-app nav link, or tab/window close discards the input with no warning; autosave present but not confirmed to the user (no "saved"/"unsaved changes" indicator to know whether it's safe to leave).
- **Fix:** Intercept navigation away from dirty state and confirm before discarding (native `beforeunload` for tab/window close, an in-app confirm dialog for router navigation); where autosave exists, surface its status so the user can tell without guessing.
- **Impact:** Silent loss of typed input on accidental navigation is one of the most trust-damaging failures in a product — users don't file a bug, they stop trusting the form.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 3, User Control and Freedom — extends UX-03 to the navigate-away case)

---

## Filtering & Bulk Selection

### UX-11 [MEDIUM] Mute-Not-Hide Filtering + Distinct Select-All/Clear-All
applies_when: a filterable list/grid/calendar view with spatially-contextual items is present
When a filter is applied to a list/grid/calendar view where surrounding context matters (adjacency, occupancy, availability), non-matching items are de-emphasized (muted/desaturated), never hidden outright — and bulk-selection panels expose "select all" and "clear all" as two distinct, unambiguous controls.
- **Detect:** A filter/highlight interaction on a spatially-contextual list/grid/calendar view that sets non-matching items to `display: none` (destroying adjacency/occupancy information) instead of a muted/faded style; a mute pass applied only at mount and not reapplied after re-render; a bulk-selection panel with a single toggle button whose action (select-all vs clear-all) silently depends on hidden prior state.
- **Fix:** Replace hide-on-filter with an idempotent mute pass (lower opacity/desaturate, stays interactive) that reapplies on every re-render; split any ambiguous toggle into two explicitly labeled "Select all" / "Clear all" (or "Select none") controls.
- **Impact:** Hiding non-matching items destroys the spatial context users rely on to judge adjacency/availability; an ambiguous select/clear toggle causes real data loss when it silently clears instead of selecting.
- **Source:** Gestalt continuity/context principles; NN/g bulk-action affordance clarity

## Status & Health Communication

### UX-12 [MEDIUM] Cascading Health/Status-Check Severity Demotion
applies_when: a multi-check status or health dashboard is present
When multiple health/status checks have a dependency relationship (a root check gating several downstream checks), a downstream check's displayed severity demotes when a known upstream root-cause check has already failed — never presented as N independent criticals for one root cause.
- **Detect:** A status/health dashboard with dependency-ordered checks (e.g. connectivity → auth → sync → feature-specific) where a single outage condition (e.g. offline) causes multiple simultaneous, unrelated-looking CRITICAL badges instead of one root-cause indicator plus demoted symptoms.
- **Fix:** Order checks by dependency; when an upstream check fails, demote dependent checks' displayed severity (e.g. to informational/"blocked by X") rather than each reporting independently.
- **Impact:** An inflated list of unrelated-looking criticals for one root cause obscures the actual starting point for diagnosis and erodes trust in the status panel.
- **Source:** Cascading-failure / root-cause-first alerting practice (SRE incident-communication conventions)

---

## Tooltip Discipline

### UX-13 [HIGH] Tooltip Discipline: None on Self-Explanatory Elements; Standard Behavior Everywhere Else
applies_when: ui≠none
Tooltips exist only where they add real information, and every tooltip derives from one SSOT component with industry-standard behavior.
- **Detect:** Tooltips on elements whose visible label is already complete (noise tooltips); essential information available only inside a tooltip; multiple tooltip implementations; a tooltip that covers its own trigger, appears on hover but not keyboard focus, cannot be dismissed with Esc, disappears when the pointer moves onto it, flashes open with zero delay, or contains interactive content.
- **Fix:** Remove tooltips from self-explanatory elements; never put must-know information only in a tooltip. Route every remaining tooltip through one shared component that: positions adjacent to the trigger (smart top/bottom/side placement, never covering it), opens on hover AND keyboard focus, is dismissable (Esc), hoverable, and persistent per WCAG 1.4.13, opens after a ~300–500ms delay, contains no interactive content (use popover/toggletip for that), and has a touch-accessible equivalent.
- **Impact:** Noise tooltips degrade every interaction; non-standard ones violate WCAG 1.4.13 and randomly hide the very content they exist to show.
- **Source:** XR-131 — cross-project experience registry (2026); WCAG 1.4.13.

---

## Validation Severity

### UX-14 [MEDIUM] Soft-Warn Is the Default for Reversible, Non-Destructive Limit Violations
applies_when: ui≠none
Limit violations that cause no data loss warn but do not block; hard blocks are reserved for irreversible or physically impossible states.
- **Detect:** A soft limit (roster size, recommended maximum, quota advisory) hard-blocks the action; or the block/warn choice is hardcoded with no owner-level escalation option.
- **Fix:** Default every no-data-loss limit violation to a soft warning that lets the action proceed; hard-block only genuine impossibilities (e.g. physical capacity conflicts) — and let the workspace owner deliberately escalate a soft warning to a hard block as a reversible, recorded setting.
- **Impact:** Overzealous hard blocks force users into workarounds (fake data, split records) that corrupt the dataset more than the exceeded limit ever would.
- **Source:** XR-185 — cross-project experience registry (2026).

---

## Audit & History Surfaces

### UX-15 [HIGH] Audit Screens Show Resolved, Human-Readable Facts — Filterable on Every Axis
applies_when: an audit or history view is present
Audit/history views resolve raw identifiers into human-readable facts and support filtering, search, and grouping on every recorded dimension.
- **Detect:** Audit rows show raw IDs (user id, entity id), machine timestamps, or field-diff JSON; filtering is limited to free-text; no facet/dropdown filters or collapsible grouping.
- **Fix:** Render WHO (display name), WHEN (readable local date-time), ON WHAT (the record's human-readable name), and EXACTLY WHAT changed (field-by-field old→new in plain words); add facet filters (date, actor, location, action type, affected entity) and grouped views. An admin must understand any row without a second query or cross-referencing.
- **Impact:** An audit trail nobody can read is compliance theater — investigations stall and accountability silently disappears.
- **Source:** XR-101 — cross-project experience registry (2026).

---

## Integration with `states` Scope

The `ux` scope audits *whether* a flow reaches success/error correctly from the user's perspective (heuristics, onboarding, activation); the `states` scope (rules-components.md) audits *whether* each UI component correctly implements the empty/loading/error/success/disabled/hover/focus/active states that `ux` findings depend on. Run `states` findings first when both scopes are in play — a `ux` finding that traces to a missing `states` implementation (e.g., UX-01 flagging missing loading feedback) should cite the corresponding `states` rule rather than duplicate it.
