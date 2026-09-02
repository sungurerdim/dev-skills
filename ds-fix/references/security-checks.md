# Security — Debug Residue & Temp-File Discipline

Consumer: SKILL.md Phase 6 (Security) 6c, advisory sub-checks for all stacks.

## Debug endpoints

Grep route registrations whose path literal matches `/(debug|__test|_internal)` outside test directories → flag each for manual review, never auto-remove. Honesty note: this class is explicitly not amenable to complete static analysis (CMU SEI) — the grep narrows candidates, a human confirms intent.

## Temp files in shell scripts

Hardcoded `/tmp/<name>` paths or `$$`-based temp names → propose `TMPFILE=$(mktemp)` (mode 600, unpredictable name — closes the symlink-attack window) with `trap 'rm -f "$TMPFILE"' EXIT` set immediately after creation so cleanup fires on every exit path, not just normal completion.
