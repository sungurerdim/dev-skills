# Lean — is the project the right size for its purpose?

Project-level proportion: does what exists, and the way it is built, match the stated purpose? Code-level removal (dead code, single callers, premature abstraction, orphans) is in [simplify.md](simplify.md). Measurements come from `ds-audit/assets/lean.py`; the field each rule reads is named in its Detect. The model judges only need and fit; counts are never estimated.

### LEAN-01 [HIGH] No measurable purpose
- **Detect:** no `SCOPE.md` with `Purpose:` and `Done when:`, and no README/spec sentence naming who it serves and what observable result means done.
- **Fix:** propose a one-sentence purpose, its users and a done condition from README, spec and issues; the owner confirms (`only you can do` without them). Every other LEAN rule is judged against it.
- **Impact:** without a purpose, need cannot be judged, so every unit, rule and dependency survives by default.
- **Source:** YAGNI; Gall's law.

### LEAN-02 [HIGH] Core path not working while scope grows
- **Detect:** the T0 path (the purpose's main user flow) does not run end to end — README or status lists it as planned, no entry point reaches it (`entry_points`) — while recent commits (`commits_30d`, per-unit `commits`) go to non-T0 units.
- **Fix:** freeze non-T0 units (tier T1/T2); next work only closes the T0 path. Record the freeze in `SCOPE.md`.
- **Impact:** months pass without a usable result; work on later tiers is built on guesses the T0 path would have corrected.
- **Source:** Gall's law; make it work, right, fast (Beck).

### LEAN-03 [HIGH] Unit serving no need
- **Detect:** a unit in the inventory whose `Serves` cell names no T0/T1 need after the purpose is set; confirm `fan_in` by reading its importers before calling it unused.
- **Fix:** cut it with everything that exists only for it: its tests, docs, gate and CI steps, config, dependencies. Record the last commit that had it in the cut commit message so it is one `git checkout {sha} -- {path}` away.
- **Impact:** every unit is maintained, tested, documented and reviewed forever; one that serves nothing taxes all work.
- **Source:** YAGNI; Chesterton's fence (read `git log` of the unit before cutting).

### LEAN-04 [MEDIUM] More units than the need
- **Detect:** write the fewest units that would meet T0 and T1 from scratch, reusing what the platform, stdlib and existing dependencies give (kernel §1 step 2). Current `units` ≥ 2 × that number, or two units with the same reason to change.
- **Fix:** `merge→{unit}` rows in `SCOPE.md`, applied one merge per commit; the minimal sketch goes in the report.
- **Impact:** each boundary adds an interface, wiring and tests; extra boundaries multiply change cost without adding capability.
- **Source:** KISS; separation of concerns (one reason to change per unit, not one unit per idea).

### LEAN-05 [MEDIUM] Process tooling outweighs the product
- **Detect:** units whose job is the project's own process (custom gates, checkers, status/record generators, internal release or tracker tools) — their `src_lines` + `test_lines` and `commits` against the product units; `commits_without_source` / `commits` above 0.25.
- **Fix:** replace each with an existing tool (the stack's linter or formatter, a ds-gate entry point, `gh`, the build tool's own tasks) or delete it; keep custom tooling only for a check no tool provides and the purpose needs.
- **Impact:** effort spent on the workshop is effort not spent on the product, and the tooling itself needs gates, tests and fixes.
- **Source:** kernel §1 (reuse before build; automate last).

### LEAN-06 [MEDIUM] Dependency that removes no burden
- **Detect:** each entry in `deps` (runtime first): which concrete burden does it remove? The stdlib, the platform or another listed dependency already does it, or it is used in one call site for a few lines of logic.
- **Fix:** replace with stdlib/platform or the existing dependency and remove it; keep with a one-line reason in `SCOPE.md` when it removes real work. Supply-chain risk of what stays is judged in SAR-11.
- **Impact:** every dependency adds updates, advisories, build time and lock-in.
- **Source:** kernel §1 step 2; NIST SSDF PW.4 (reuse well-secured software).

### LEAN-07 [MEDIUM] Slow path where a proven faster one exists
- **Detect:** a hand-built mechanism, stack or workflow for a job a mature tool, framework feature or managed platform does (queue, scheduler, ORM, auth, build, release, docs site, test runner), or a process step that a single command replaces. Evidence: the named alternative and what it removes.
- **Fix:** adopt the alternative when it meets the purpose with less code or time; record a rejected alternative with its reason so it is not re-proposed.
- **Impact:** weeks spent rebuilding what exists; the custom version keeps costing after it works.
- **Source:** kernel §1 step 2; Twelve-Factor (backing services as attached resources).

### LEAN-08 [MEDIUM] Plans and docs outweigh the product
- **Detect:** `doc_kb` above the budget or above ~1 KB per 100 `src_lines`; spec sections, issues or milestones for T2 or unbuilt features; open issues several times the closed ones in the last 30 days.
- **Fix:** keep docs for what exists and the next tier; move the rest to a short backlog list; close or label issues of cut units (`only you can do`, with the command list).
- **Impact:** large plans are read, kept consistent and obeyed by every agent and person; detail for work that may never happen steers today's work wrongly.
- **Source:** YAGNI; DOC rules in [docs.md](docs.md) for the docs that stay.

### LEAN-09 [HIGH] Missing essential
- **Detect:** a T0 need no unit serves, or the T0 path lacks one of: a way to install or run it, a check that proves it works (a test or command), handling of its expected failure inputs.
- **Fix:** add the smallest piece that closes it; this is the only kind of addition the lean phase makes.
- **Impact:** a lean project that cannot be run or trusted has cut the wrong things.
- **Source:** Gall's law; fail fast.

### LEAN-10 [MEDIUM] Trajectory drift
- **Detect:** `days` and `commits` against T0 progress; parallel work lost or parked (stale branches in `branches`, recovery branches, status notes about lost batches); repeated rework of the same unit (high `commits` on a unit with no user-visible change).
- **Fix:** one T0 item in progress at a time; sequential small commits on one branch; record the work-in-progress limit in `SCOPE.md`.
- **Impact:** a week of work becomes months, and nobody can say what is done.
- **Source:** Little's law (less work in progress, shorter lead time); Gall's law.

### LEAN-11 [MEDIUM] Scope drift since the last lean pass
- **Detect:** `lean.py --check SCOPE.md` is red: a unit without a row, a row for a gone unit, an unapplied cut, or the budget exceeded.
- **Fix:** give the new unit a tier and the need it serves, or remove it; raise a budget only with the reason in `SCOPE.md`.
- **Impact:** without a check, the project regrows to its old size within weeks.
- **Source:** fitness functions (Ford, Parsons, Kua — *Building Evolutionary Architectures*).

### LEAN-12 [MEDIUM] Standing rule without scope or reason
- **Detect:** `lean.py --rules` items with `absolute` and no `reason`, or added by a commit whose subject is about one task (the rule came from a single moment); rules that contradict each other or the purpose.
- **Fix:** the owner decides each (the rules step of the lean procedure): keep, reword, scope it (`until {date or condition}`), move it to a dated decision log, or delete it. A kept rule states its reason in the same line.
- **Impact:** a sentence said for one day becomes how all work is done, and every agent obeys it without knowing why.
- **Source:** Chesterton's fence (know why before keeping or removing); ADR practice (decision + context + consequences).
