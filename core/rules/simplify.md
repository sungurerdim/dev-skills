# Simplify — code that should not exist

Code-level removal for the lean phase; the project-level proportion rules are in [lean.md](lean.md). Tool output upgrades the detector, never the decision: every hit is confirmed by reading it (kernel §4 skip list: public API manifests, `__all__`, framework entry points, generated code, test fixtures) and every removal passes Category A/B. Chesterton's fence: read the `git log` of what is removed.

### SIM-01 [MEDIUM] Dead code
- **Detect:** exports, functions, files and parameters with zero code references. A `git grep -w {name}` hit inside a comment, a doc or a string literal is not a reference. Skip exports in public API manifests (`exports` in `package.json`, `__all__`, a library's public re-exports).
- **Mech:** T `knip --no-progress` · `vulture . --min-confidence 80` · `deadcode ./...`
- **Fix:** delete it with its tests and docs; a parameter nothing passes is removed from the signature and every call site.
- **Impact:** dead code is read, kept compiling, tested and migrated forever, and misleads readers about what is live.
- **Source:** YAGNI; Knip (knip.dev), Vulture, golang.org/x/tools/cmd/deadcode.

### SIM-02 [LOW] Single-caller indirection
- **Detect:** an internal helper, wrapper or export with exactly one caller and under ~10 lines, adding a name without hiding complexity. Skip recursive helpers, trait or interface implementations, and helpers that isolate a side effect for testing.
- **Mech:** M (reference counts from SIM-01's tools or `git grep -cw {name}`)
- **Fix:** inline at the caller and remove the export.
- **Impact:** every hop costs a reader a jump; one-caller layers hide nothing.
- **Source:** KISS; Fowler, *Refactoring* (Inline Function).

### SIM-03 [MEDIUM] Branch that never runs
- **Detect:** compatibility residue (`legacy`, `backward compat`, version checks below the minimum supported runtime, `catch` that returns a default with no re-throw) and feature-flag branches whose flag is the same literal in every config source with no runtime setter. A flag set remotely, per tenant or at runtime is skipped.
- **Mech:** T `git grep -nIiE 'backward.?compat|legacy|deprecated|for old (clients|versions)'`
- **Fix:** delete the dead branch and the flag; in an unreleased product with no external consumer delete compatibility shims outright (breaking-first); a shim genuinely needed during a transition gets a removal date in the same line.
- **Impact:** untested branches rot silently and double the paths a reader must consider.
- **Source:** YAGNI; Piranha (Uber) for stale-flag removal.

### SIM-04 [MEDIUM] Premature abstraction
- **Detect:** an interface or abstract base with one implementation, a factory for one type, a generic container, wrapper, hook or plugin point with ≤ 2 concrete uses, a config option nothing sets. Evidence: the abstraction's `file:line` and each use.
- **Mech:** M
- **Fix:** inline the uses and drop the abstraction; reintroduce it when a second real use exists.
- **Impact:** speculative indirection is paid for on every change and usually guesses the future wrong.
- **Source:** YAGNI; Metz, "duplication is far cheaper than the wrong abstraction".

### SIM-05 [LOW] Code kept "just in case"
- **Detect:** commented-out code, `// removed`, `// TODO: delete`, `// unused`, `_unused` renames, files named `old_*`/`*_backup`/`*.bak`.
- **Mech:** S `git grep -nIE '//[[:space:]]*(removed|unused|TODO:? delete|kill this)|_unused[A-Z_]' -- ':!*.md'` · `git ls-files '*_backup*' '*.bak' '*/old_*'`
- **Fix:** delete; git history keeps it.
- **Impact:** quarantined code is noise every reader and every search has to skip.
- **Source:** Boy Scout rule; git as the archive.

### SIM-06 [HIGH] One fact, several homes — any artifact
- **Detect:** the one home of the single-source principle; every other rule that finds a copy (TOK literal colours, I18N hard-coded strings, SIM-08, SIM-09) is a detector of it. Any artifact counts: logic (near-identical blocks; a new helper redoing an existing one), a value or rule (threshold, URL, limit, enum mapping, regex), markup and style, UI copy, configuration, a documentation passage, an asset (image, icon, font, document) committed under two paths. Two copies are a note; the third, or two that already disagree, is a finding. Test fixtures, protocol constants and framework-required literals are not findings.
- **Mech:** T `jscpd --min-lines 6 --reporters console .` · `git ls-files -s | awk '{c[$2]++; p[$2]=p[$2]" "$4} END{for(k in c) if(c[k]>1) print p[k]}'` · `git ls-files -z '*.md' '*.rst' '*.txt' | xargs -0 awk 'length>=80 && !/^[|]/' | sort | uniq -d`
- **Fix:** one owning definition; every other place imports, references or links it; a duplicate asset or passage is deleted and its users point at the one copy.
- **Impact:** a change lands in one home and the others silently disagree; a bug fixed in one copy stays in the rest.
- **Source:** DRY / single source of truth (Hunt & Thomas, *The Pragmatic Programmer*); rule of three (Fowler, *Refactoring*).

### SIM-07 [LOW] Orphan file
- **Detect:** a tracked source, asset, stylesheet or doc no other tracked file names (with or without extension). Skip entry points, convention-named config, `README`, `LICENSE`, `CHANGELOG`.
- **Mech:** T `knip --include files --no-progress`
- **Fix:** delete it, or link it from where it is meant to be found.
- **Impact:** orphans look live and get maintained for nothing.
- **Source:** YAGNI.

### SIM-08 [MEDIUM] UI element built twice
applies_when: ui≠none
- **Detect:** a UI primitive — button, separator, label/badge/chip, input, icon, card, toolbar, dialog — hand-built inside a screen where a shared component or style exists (raw `<button>`/`<hr>`, a platform widget used directly instead of the design-system one, copied markup or style blocks), or a one-off variant of it. Detector of SIM-06.
- **Mech:** T `git grep -nE '<(button|hr|dialog)(^|[^[:alnum:]_])' -- '*.html' '*.jsx' '*.tsx' '*.vue' '*.svelte'` · `git grep -nE '(^|[^[:alnum:]_])(ElevatedButton|TextButton|OutlinedButton|Divider|AlertDialog)\(' -- '*.dart'`
- **Fix:** route every use through the one primitive; a genuinely new look becomes a variant (prop) of it, not a copy.
- **Impact:** the same element drifts in size, colour, focus ring and behaviour from screen to screen, and every fix has to be repeated.
- **Source:** design systems (Frost, *Atomic Design*); Nielsen heuristic 4, consistency and standards.

### SIM-09 [MEDIUM] Action defined twice
applies_when: ui≠none
- **Detect:** one user action (delete, share, save, archive, export…) whose label, icon, shortcut, confirmation, permission check or handler is defined separately in each place that offers it — toolbar, menu, context menu, shortcut, command palette, CLI flag and help text — or whose copies already differ ("Delete" here, "Remove" there; a confirmation in one place only). Detector of SIM-06.
- **Mech:** M (compare every entry point of the same action; the duplicated label literals show up in SIM-06's scan)
- **Fix:** one command definition per action — label, icon, shortcut, confirmation, permission, handler — that every entry point renders; in a CLI, one command table that drives both parsing and help.
- **Impact:** users meet the same action with different names and safety nets, and a permission fix lands in one entry point while another stays open.
- **Source:** command pattern (Gamma et al., *Design Patterns*); WAI-ARIA APG menu and toolbar patterns; Nielsen heuristic 4.
