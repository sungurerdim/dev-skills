# Blueprint Profile — Storage Format Contract

The profile block's line-shape, the rules for reading and updating it in place, and the legacy-marker migration path. Loaded when a phase reads or writes the profile (Discovery, Update Profile).

## Legacy marker migration

**Legacy marker migration** (non-standard markers: HTML comments like `<!-- *-start -->` / `<!-- *-end -->`, or variant headings like `## X Blueprint Profile`): read content between legacy markers, replace with standard headings, preserve all existing content (scores, config, project map, run history), remove old markers.

## Format and read/write rules

**Format rules:** key-value pairs only, one value per line — no prose, headers, tables, or bullets inside the block; AI parses by `{key}: {value}` line-shape, every consumer reads its line in O(1). The line set, the 25-line ceiling and the Dev-Value Gate are the shared contract in [../../core/findings-and-profile-format.md](../../core/findings-and-profile-format.md) § 2; `Signals:` follows [../../core/signal-inventory.md](../../core/signal-inventory.md) (`unknown` is written as such, never guessed). `Mission:` and `Red lines:` are the foundation's normative core: `Red lines` are hard NOs binding on every consumer — a downstream skill never proposes an action crossing one without explicit user override; `Constraints` remain soft preferences. Profiles predating the Foundation pass may lack both lines — valid; the next `--init`/`--foundation` run adds them. `Integrations:` feeds the A9 conditional rule blocks in ds-backend/ds-compliance/ds-frontend/ds-mobile/ds-launch — `none` when no signal matches, comma-separated when both providers are detected. `Modules:` and `External:` use `;` separator so the block stays one line per concern. `Scores:` is a single line with short keys — dashboard renders in chat output, not in the profile; `model=` records the AI model that performed the assessment (e.g. `model=claude-fable-5`; `model=unknown` when not determinable), enabling model-uplift attribution — score deltas across model generations traceable via `git log` of this line. The profile is calibration data, not a dashboard (run-history/deltas exclusion stated once under **Profile format** above).

**Read/write rules:**
- Only modify content between `## Blueprint Profile` and `## End Blueprint Profile` headings — never touch anything outside.
- **Profile detection order** (check before any write):
  1. Search for standard markers: `## Blueprint Profile` ... `## End Blueprint Profile`
  2. Search for legacy markers: HTML comment pairs (`<!-- *-start -->` ... `<!-- *-end -->`) or variant headings containing "Blueprint Profile"
  3. Standard found → update in place (preserve all calibration lines, rewrite only the `Scores:` line)
  4. Legacy found → **do not touch legacy block**. Write new standard profile separately (below legacy or at end of file). Compare both line by line (Type/Stack/Target, Priorities, Constraints, Data, Audience, Deploy, Entry, Modules, Data Flow, External, Toolchain, Ideal, Scores); identify legacy content NOT covered by new (custom config notes, historical run entries, project map details). New covers everything → report "New profile covers all content from legacy block. You can safely remove the legacy block." Legacy has unique items → report "These items exist in legacy profile but not in new one: {list}. Preserve them before removing the legacy block." Leave the legacy block intact — the user decides when to remove it.
  5. NO markers found → append new profile at end of instruction file
  6. **Never write second standard profile into a file that already has one** — always detect and update.
- Instruction file does not exist: create with profile section only.
- Other skills read profile by searching for `## Blueprint Profile` heading first, then legacy markers as fallback, in known instruction file locations.
- Updating existing standard profile: preserve all `Type/Stack/Target/Mission/Priorities/Constraints/Red lines/Data/Audience/Deploy/Entry/Modules/Data Flow/External/Toolchain/Ideal` lines; update only the `Scores:` and `Signals:` lines; re-detect Type/Stack/Toolchain/Integrations and the Project Map only with `--refresh`; rewrite foundation lines (`Mission`, `Target`, `Priorities`, `Constraints`, `Red lines`) only through the Foundation pass (`--init`; `--ask` confirms per line, default writes the best-evidenced value marked `derived-from-evidence`).
- `--preview` never writes: the profile block (or its updated lines) is printed in chat, the file is untouched.
- Legacy migration: profiles containing `### Last Run`, `### Run History`, `### Current Scores` (table), or any prose block → rewrite to minimal key-value format; report `{n} legacy lines rotated to git log` in summary. Information preserved in `git log -- <instruction-file>` — never re-injected.

**Deduplication on inject:** dedupe findings by file:line — same issue within 10 lines → merge, keep highest severity.
