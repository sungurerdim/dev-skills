# Rules: UX (Nielsen 10 + AI Transparency)

Rules for audit/fix modes. Each rule: ID, severity, title, detect pattern, fix action, platform notes.

Applies to all UI platforms: web, mobile, desktop.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Heuristics (Nielsen 10 + dev-skills UX-10a)** | UX-01 to UX-10, UX-10a (11 rules) | ~15 |
| **Onboarding / First-Use Flow** | UX-ON-01 to UX-ON-03 (3 rules) | ~110 |
| **Activation / Time-to-Value** | UX-AC-01 to UX-AC-02 (2 rules) | ~140 |

---

## Heuristics (Nielsen 10 + dev-skills UX-10a)

### UX-01 [HIGH] Visibility of System Status
The system keeps users informed about what is happening through appropriate feedback within reasonable time.
- **Detect:** Async action (submit, save, delete, upload) with no loading indicator, spinner, progress bar, or disabled-state feedback during the pending window; state change (toggle, filter, sort) with no visual confirmation.
- **Fix:** Add a loading/pending state for every async action >100ms; confirm state changes with a toast, inline message, or visual diff (checkmark, highlight).
- **Impact:** Users without status feedback assume the app is broken and repeat the action (duplicate submits) or abandon the task.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 1)

### UX-02 [HIGH] Match Between System and the Real World
The system speaks the users' language, with familiar words, phrases, and concepts, following real-world conventions.
- **Detect:** Internal jargon, error codes, or database field names surfaced verbatim in user-facing copy (`ERR_4001`, `null`, `undefined`, `NPE`); icons with no accompanying label for non-standard actions.
- **Fix:** Replace internal identifiers with plain-language copy; pair novel icons with text labels or tooltips.
- **Impact:** Users cannot act on errors or labels they don't understand — support-ticket volume rises.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 2)

### UX-03 [HIGH] User Control and Freedom
Users need a clearly marked "emergency exit" to leave an unwanted state without going through an extended process.
- **Detect:** Multi-step flow (wizard, checkout, onboarding) with no back/cancel affordance; destructive action (delete, send, publish) with no confirm step or undo window; modal with no close button or Escape-key handler.
- **Fix:** Add cancel/back at every step; add a confirm dialog or a timed undo (5-10s) for destructive actions; every modal closable via explicit control + Escape.
- **Impact:** Users trapped in a flow abandon the task entirely rather than search for an exit.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 3)

### UX-04 [MEDIUM] Consistency and Standards
Users should not have to wonder whether different words, situations, or actions mean the same thing — follow platform and internal conventions.
- **Detect:** Same action labeled differently across screens ("Delete" vs "Remove" vs "Trash" for the same operation); same icon used for different actions in different views; primary-button placement inconsistent across comparable screens.
- **Fix:** One verb per action class, enforced repo-wide (cross-reference `contract-consistency` scope in ds-blueprint); one icon-to-action mapping; consistent primary-action placement per platform convention.
- **Impact:** Inconsistent terminology forces users to relearn the interface on every screen, raising cognitive load and error rate.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 4)

### UX-05 [HIGH] Error Prevention
Eliminate error-prone conditions, or check for them and present a confirmation before users commit to the action.
- **Detect:** Free-text input where a constrained control (select, date-picker, toggle) would prevent invalid values; irreversible action with no confirmation step; form that allows submission of a state known to be invalid (e.g., end-date before start-date) without inline validation.
- **Fix:** Replace free-text with constrained controls where the value space is enumerable; add confirmation for irreversible actions; validate inline before submission, not only after.
- **Impact:** Every prevented error is a support ticket and a recovery flow the user never has to endure.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 5)

### UX-06 [MEDIUM] Recognition Rather Than Recall
Minimize the user's memory load by making elements, actions, and options visible or easily retrievable.
- **Detect:** Multi-step flow requiring the user to remember a value entered in an earlier step with no on-screen recap; command/action available only via a shortcut with no visible menu entry; search/filter with no recent-values or autocomplete.
- **Fix:** Surface prior-step values in a summary panel; expose every shortcut-only action in a visible menu; add autocomplete/recents to search and filter inputs.
- **Impact:** Recall-dependent interfaces disproportionately fail novice and infrequent users.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 6)

### UX-07 [LOW] Flexibility and Efficiency of Use
Accelerators — unseen by the novice user — may speed up the interaction for the expert user, so the design caters to both.
- **Detect:** High-frequency action (per product analytics or repo-declared primary flow) with no keyboard shortcut, bulk-action, or saved-preset path; power-user flow requires the same number of steps as the first-time flow.
- **Fix:** Add keyboard shortcuts for the top 3-5 most frequent actions; add bulk operations (select-all, batch-apply) where single-item flows repeat; add saved presets/filters for repeat configurations.
- **Impact:** Without accelerators, expert users pay the novice-user tax on every use, increasing task time at scale.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 7)

### UX-08 [MEDIUM] Aesthetic and Minimalist Design
Interfaces should not contain irrelevant or rarely needed information that competes with the relevant units of information.
- **Detect:** Screen presenting more than the primary + 1-2 secondary actions above the fold; dense forms exposing rarely-used optional fields by default instead of behind "Advanced"/"More options"; decorative elements with no functional or wayfinding purpose competing for attention with primary content.
- **Fix:** Collapse rarely-used fields behind progressive disclosure; limit primary actions per screen to 1 (with secondary actions visually subordinate); remove decoration that doesn't aid comprehension or wayfinding.
- **Impact:** Visual clutter raises the time and error rate for finding the primary action, especially for first-time and low-vision users.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 8)

### UX-09 [HIGH] Help Users Recognize, Diagnose, and Recover from Errors
Error messages should be expressed in plain language, precisely indicate the problem, and constructively suggest a solution.
- **Detect:** Error message stating only that something failed ("Something went wrong", "Error") with no cause or next step; error message exposing a raw stack trace or internal exception to the end user; error with no visible recovery action (retry, edit, contact support).
- **Fix:** Every error states what was expected, what happened, and how to fix it (mirrors this project's own Error Message quality bar); never surface raw stack traces to end users; pair every error with a recovery action.
- **Impact:** Vague errors convert a recoverable failure into task abandonment.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 9)

### UX-10 [LOW] Help and Documentation
Even though it's better if the system can be used without documentation, providing help and documentation may be necessary.
- **Detect:** Non-trivial feature (multi-step config, integration setup, advanced filter syntax) with no in-context help (tooltip, inline hint, linked doc) and no entry in the product's documentation surface (cross-reference `B6` documentation dimension).
- **Fix:** Add in-context help for non-trivial features; ensure the doc surface (ds-docs B6) covers each one; keep help task-focused and searchable, not a monolithic manual.
- **Impact:** Undocumented complexity forces users to trial-and-error or abandon the feature.
- **Source:** Nielsen Norman Group — 10 Usability Heuristics (heuristic 10)

### UX-10a [HIGH] AI Output Transparency
AI-generated or AI-assisted content is labeled, and claims presented as fact are traceable to a source.
- **Detect:** AI-generated summary, suggestion, or content block rendered indistinguishably from human-authored or ground-truth content; AI-generated factual claim (price, statistic, citation) with no visible source or "AI-generated — verify" affordance; AI chat/assistant response with no indication that a human is not on the other end.
- **Fix:** Label AI-generated content at the point of display (badge, "Generated by AI" caption, or distinct visual treatment); attach source links or a "why am I seeing this" affordance to AI-derived claims; disclose AI vs human agent identity in conversational UIs.
- **Impact:** Unlabeled AI content erodes trust once discovered, and unsourced AI claims propagate hallucinations as fact.
- **Source:** dev-skills extension, not an official NN/g heuristic — verified 2026-07-11 against [nngroup.com/articles/ten-usability-heuristics](https://www.nngroup.com/articles/ten-usability-heuristics/), which states the 10 heuristics "have remained relevant and unchanged since 1994." Added here to cover an AI-transparency gap the original 10 don't address.

---

## Onboarding / First-Use Flow

### UX-ON-01 [HIGH] First-Run Path Exists and Is Bounded
A first-time user reaches a working state without reading external documentation.
- **Detect:** No distinguishable first-run experience (empty state, welcome screen, guided setup) for a new account/workspace/project; first-run path requires more than 5 user actions (clicks/taps/keystrokes) before the user reaches a usable state.
- **Fix:** Add a first-run experience distinct from the steady-state UI; bound it to ≤5 actions to first usable state, or break it into resumable steps with visible progress.
- **Impact:** Products without a bounded first-run path lose new users to abandonment before they experience any value.
- **Source:** Nielsen Norman Group — Onboarding UX; RT2 (specs/001-v4-coverage-standalone/research.md)

### UX-ON-02 [MEDIUM] Empty States Teach, Not Just Announce
Every empty state (no data yet) explains what belongs there and how to add it, not just "No items."
- **Detect:** Empty list/table/dashboard rendering only a "No X found" message with no call-to-action to create the first item, and no example of what populated state looks like.
- **Fix:** Pair every empty state with a primary CTA ("Create your first X") and, where feasible, a preview/illustration of populated state.
- **Impact:** A bare empty state is a dead end for new users who don't yet know what the feature does.
- **Source:** Nielsen Norman Group — Empty State Design

### UX-ON-03 [MEDIUM] Progressive Disclosure During Setup
Setup/onboarding requests only the information required to reach first value; optional configuration is deferred.
- **Detect:** Sign-up or setup flow collecting fields not required until a later feature is used (e.g., billing details before any paid action, notification preferences before any notification-triggering event).
- **Fix:** Move non-blocking fields to post-onboarding settings, defaults, or just-in-time prompts triggered when the field becomes relevant.
- **Impact:** Every non-essential field in the setup path raises drop-off before the user has experienced any value.
- **Source:** Nielsen Norman Group — Progressive Disclosure

---

## Activation / Time-to-Value

### UX-AC-01 [HIGH] First-Success Step Count Is Measured and Bounded
The number of steps from first-run to the user's first successful outcome (the product's core value moment) is known and ≤ the product's stated target.
- **Detect:** No instrumented or documented step count from account/session start to first core-value event (first message sent, first file processed, first report generated — product-specific); step count exceeds 7 discrete user actions with no justification tied to the domain (e.g., regulated onboarding).
- **Fix:** Instrument or manually trace the first-run → first-success path; if it exceeds 7 actions, cut, merge, or defer steps until it doesn't, or record an explicit justification in the blueprint profile Priorities/Constraints.
- **Impact:** Time-to-value is the strongest predictor of activation-to-retention conversion; unmeasured time-to-value means regressions ship undetected.
- **Source:** RT2 (specs/001-v4-coverage-standalone/research.md); product-led-growth activation literature

### UX-AC-02 [MEDIUM] Core Value Moment Is Explicit and Celebrated
The product marks the moment the user reaches first value (visually, not just functionally).
- **Detect:** First-success event (first save, first successful integration, first completed task) produces no distinguishable feedback beyond the generic loading/success pattern used elsewhere in the app.
- **Fix:** Add a distinguishable first-success moment (confirmation, next-step suggestion, or lightweight celebration) tied specifically to the first occurrence of the core-value event.
- **Impact:** An unmarked value moment leaves the user unsure whether they succeeded, undermining the activation the product just achieved.
- **Source:** RT2 (specs/001-v4-coverage-standalone/research.md)

---

## Integration with `states` Scope

The `ux` scope audits *whether* a flow reaches success/error correctly from the user's perspective (heuristics, onboarding, activation); the `states` scope (rules-components.md) audits *whether* each UI component correctly implements the empty/loading/error/success/disabled/hover/focus/active states that `ux` findings depend on. Run `states` findings first when both scopes are in play — a `ux` finding that traces to a missing `states` implementation (e.g., UX-01 flagging missing loading feedback) should cite the corresponding `states` rule rather than duplicate it.
