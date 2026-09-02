# Entry-Point Coverage — the two mechanical properties

Consumer: SKILL.md Phase 3 (Single quality entry point), run before wiring the arm. Report both lists — wired / excluded-with-reason — in the run report; they are the entire coverage claim this skill is allowed to make.

## 1. Every check in the repo is called by the entry point

Enumerate what already exists — `scripts/`+`tools/` executables, `package.json` scripts, `Makefile` targets, `.pre-commit-config.yaml` hooks, audit/verify scripts, test directories the runner's discovery pattern does not reach — and grep the entry point for each by name.

Uncalled → wire it in, or record it as a deliberate exclusion **at the entry point** with the condition under which it does run (platform-pinned goldens, a slow suite moved to pre-push). A check nothing calls counts as absent, however green it looks when run by hand (ds-review TST-14). Callers must propagate the exit code — a step whose result is discarded is uncalled in effect.

## 2. Every check declares the file set it scans

Each wired step passes an explicit path/glob (or prints the file count it processed) instead of relying on the invocation directory; a step that matches zero files fails rather than passes, and a repo-wide rule's scope is compared against `git ls-files` once, so a directory added later joins the scan or breaks the gate (ds-review TST-13).
