# Rules: Scheduling & Calendar (Conditional)

Conditional rules loaded only for projects with a scheduling/calendar/booking surface (appointment apps, resource planners, agenda views). Each rule: ID, severity, title, detect pattern, fix action. Generic UX/a11y/responsive rules still apply; these add the scheduling-specific layer.

## Table of Contents

| Section | Rules | Line |
|---------|-------|------|
| **Interaction** | SCH-01, SCH-02, SCH-03, SCH-04, SCH-11 (1 HIGH, 4 MEDIUM) | ~17 |
| **Time grid** | SCH-05, SCH-06, SCH-09 (3 MEDIUM) | ~56 |
| **Visual encoding** | SCH-07, SCH-12 (1 HIGH, 1 LOW) | ~81 |
| **Booking integrity** | SCH-08 (1 CRITICAL) | ~99 |
| **Navigation** | SCH-10 (1 HIGH) | ~110 |

---

## Interaction

### SCH-01 [MEDIUM] Hover Preview Before Full Detail
Schedule items reveal a lightweight summary on hover/long-press before the user commits to opening full detail.
- **Detect:** Opening an item is the only way to see its contents; hover (desktop) or long-press (touch) shows no summary card of the item's key fields.
- **Fix:** Add a read-only, non-intrusive preview (tooltip-style card) rendering the item's key fields from the same data source as the detail view; dismiss on pointer-out and Esc; keep it visually calm (no dense borders, no harsh contrast).
- **Impact:** Users open and close items repeatedly just to identify them — schedule triage becomes click-heavy and slow.
- **Source:** XR-051 — cross-project experience registry (2026).

### SCH-02 [HIGH] Create and Edit Share One Progressive Surface
Creating an item and editing an existing one open the identical surface (modal/panel); the creation flow is step-based and asks the highest-value fields first.
- **Detect:** Create and edit use different forms with divergent field sets; or the create flow front-loads rarely-changed fields, forcing users through every field on every creation.
- **Fix:** Use one shared create=edit surface where every field is visible and editable in both modes; order the flow by progressive disclosure — most-frequently-changed, decision-critical fields first, everything else deferred or defaulted — so a typical creation completes with the minimum number of inputs.
- **Impact:** Divergent create/edit forms drift apart (fields editable in one but not the other), and front-loaded low-value questions slow the most frequent workflow in the product.
- **Source:** XR-157 + XR-052 — cross-project experience registry (2026).

### SCH-03 [MEDIUM] Drag-and-Drop Engages on a Small Threshold With Directional Feedback
Dragging a schedule item starts after a small movement threshold and continuously shows what is being moved where.
- **Detect:** Drag starts on mouse-down with zero threshold (accidental drags on click), or engages only after a long delay; the dragged item gives no ghost/outline/target-slot highlight while moving.
- **Fix:** Engage drag after a small pointer-movement threshold (a few px), then render immediate, continuous visual feedback: moving ghost of the item, live highlight of the drop target slot, and snap preview of the resulting time. Cancel cleanly on Esc.
- **Impact:** Without a threshold, plain clicks mutate the schedule; without live feedback, users drop items into the wrong slot and lose trust in direct manipulation.
- **Source:** XR-158 — cross-project experience registry (2026).

### SCH-04 [MEDIUM] Active Filters Prefill New Records
Entity values already selected in active filters (person, resource, room, mode) prefill the corresponding fields when the user creates a new record from the filtered view.
- **Detect:** With filters active, clicking an empty slot opens a creation form with those same fields blank.
- **Fix:** Map each active filter dimension to its creation-form field and prefill it; keep every prefilled value editable.
- **Impact:** Users re-enter context the UI already knows, adding avoidable steps to the most frequent creation path.
- **Source:** XR-159 — cross-project experience registry (2026).

### SCH-11 [MEDIUM] Item Context Menu Replaces the Browser Default
Right-click (or equivalent) on a schedule item opens the app's own context menu with high-frequency shortcuts; empty areas keep the browser menu.
- **Detect:** Right-click on items shows the browser's default menu; or a custom menu exists but lacks keyboard support.
- **Fix:** On items, open an app context menu offering edit/delete plus high-value quick actions (duplicate to +1/+2 weeks, repeat monthly); implement with `role=menu`/`menuitem` and roving tabindex per the APG menu pattern; preserve the native browser menu on empty space.
- **Impact:** Power users lose the fastest path to repetitive operations; a non-ARIA custom menu locks out keyboard and screen-reader users.
- **Source:** XR-161 — cross-project experience registry (2026).

---

## Time grid

### SCH-05 [MEDIUM] Off-Hours Render Shaded and Inactive — Including at Scroll Boundaries
Areas outside configured working hours/days always render visually distinct (shaded/inactive), with a guard against boundary rendering bugs.
- **Detect:** Off-hours cells render identical to working cells; or at scroll extremes (overscroll, virtualized edges) off-hours areas flash active/white.
- **Fix:** Derive the shaded region from the configured working-hours setting (single source), apply it to every rendered cell including virtualized/overscrolled ones, and add a rendering test or guard for the scroll-boundary edge case.
- **Impact:** Users book into closed hours, and boundary glitches make the calendar look broken exactly where attention is lowest.
- **Source:** XR-054 — cross-project experience registry (2026).

### SCH-06 [MEDIUM] Visible Hour Range Is Configurable and Self-Correcting
The calendar's visible hour range is a setting (default near working hours, optionally 24h), and invalid ranges self-correct with an explicit error.
- **Detect:** The grid always renders a fixed range (e.g. 00:00–24:00) padding the view with dead space; or a start ≥ end configuration renders a broken grid silently.
- **Fix:** Expose visible-range start/end in settings; default to working hours ± small margin; on conflicting values, auto-correct to the nearest valid range and surface a validation error naming expected vs received.
- **Impact:** A fixed 24h grid shrinks the useful working area to a fraction of the viewport; silent invalid ranges break the core screen.
- **Source:** XR-162 — cross-project experience registry (2026).

### SCH-09 [MEDIUM] Atomic Stepped Date-Time Picker
Time selection uses one atomic date-time picker with a consistent step (e.g. 15 min) everywhere times are chosen.
- **Detect:** Different surfaces select time via different widgets (free-text here, dropdown there) or inconsistent step sizes; date and time are picked in disconnected controls that can produce impossible combinations.
- **Fix:** Provide one shared date-time picker primitive with a configured step; use it for every time selection on the scheduling surface; validate the combined value atomically.
- **Impact:** Inconsistent pickers produce off-grid times that break overlap checks and visual alignment on the calendar grid.
- **Source:** XR-187 — cross-project experience registry (2026).

---

## Visual encoding

### SCH-07 [HIGH] Entity Distinction: Curated Color SSOT Plus a Second Visual Axis
Concurrent schedule entities (people, rooms, modes) are distinguishable via a curated, CVD-safe palette AND one additional non-color axis.
- **Detect:** Entity colors are generated ad hoc (random hues, harsh/neon tones) instead of from one curated palette; or color is the only signal distinguishing room/mode when many sessions render side by side.
- **Fix:** Auto-assign entity colors from a single validated, CVD-safe categorical palette (≈8 hues, no glaring tones), allow manual override, and encode the second dimension (room, mode) on a separate visual axis — border style, corner badge, icon, or pattern — never color alone (WCAG 1.4.1).
- **Impact:** With ad-hoc colors and color-only coding, dense views become unreadable and ~8% of male users cannot distinguish entities at all.
- **Source:** XR-053 — cross-project experience registry (2026).

### SCH-12 [LOW] Reliability Risk Indicator on Frequent Reschedulers
Contacts who repeatedly cancel or late-reschedule carry a visible risk indicator derived from a configurable threshold.
- **Detect:** Reschedule/cancellation counts exist in data but no surface exposes them at booking time.
- **Fix:** Derive a risk flag from a configurable reschedule-count threshold and show it unobtrusively wherever the contact is selected for a new booking.
- **Impact:** Staff rebook chronically unreliable contacts into prime slots with no warning, losing revenue-bearing capacity.
- **Source:** XR-188 — cross-project experience registry (2026).

---

## Booking integrity

### SCH-08 [CRITICAL] Resource Capacity Enforced by Exact Interval-Overlap Check
Bookings against a finite resource (room, seat, device) are blocked by an exact, earliest-possible conflict check with a clear reason shown.
- **Detect:** Overlap is checked at coarse granularity (slot/hour) instead of the half-open interval test `a.start < b.end && b.start < a.end`; capacity/allowed-service constraints live only in UI hints; the conflict is reported only on final submit; or the rejection shows no reason.
- **Fix:** Model per-resource capacity and allowed-service constraints as admin-editable settings; run the half-open interval-overlap check at second precision at the earliest interaction point (while composing, not only on submit) and again server-side; on block, state exactly which resource is full and when.
- **Impact:** Double-booked rooms and over-capacity sessions are operational failures users discover in person — the single most trust-destroying bug a scheduling product can ship.
- **Source:** XR-096 — cross-project experience registry (2026).

---

## Navigation

### SCH-10 [HIGH] Detail and Edit Happen In-Place, Not on a Separate Page
Entity details reached from the working view (filters, rows, calendar items) open in an embedded panel on the same page whenever possible.
- **Detect:** Clicking a filter entity or list row navigates to a separate page, discarding the user's working context (scroll position, active filters, visible range).
- **Fix:** Open detail/edit in an embedded panel — replacing the secondary/summary area or overlaying the canvas edge — with progressive disclosure: core workflow stays on the main canvas, secondary detail lives in the panel; keep one design language and support in-place person/entity operations.
- **Impact:** Full-page navigation for every lookup destroys working context; users pay a re-orientation cost on every return.
- **Source:** XR-049 — cross-project experience registry (2026).
