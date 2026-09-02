#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
rc=1; node -e "const {slugify}=require('./src/text'); if (slugify('Hello, World!')!=='hello-world' || slugify('  A--B  ')!=='a-b') process.exit(1)" >/dev/null 2>&1 && rc=0
r "T1-verify(slugify)" "$rc"
rc=1; node -e "const {truncate}=require('./src/text'); if (truncate('abc',5)!=='abc' || truncate('abcdefgh',5)!=='abcd…') process.exit(1)" >/dev/null 2>&1 && rc=0
r "T2-verify(truncate)" "$rc"
rc=1; grep -q '^## Usage' README.md && grep -q 'slugify' README.md && grep -q 'truncate' README.md && rc=0
r "T3-verify(readme-usage)" "$rc"
tf=specs/001-text-helpers/tasks.md
rc=1; { [ ! -e "$tf" ] || ! grep -q '^- \[ \]' "$tf"; } && rc=0
r "tasks-ticked-or-file-retired" "$rc"
rc=1; [ "$(git rev-list --count HEAD)" -ge 2 ] && rc=0
r "work-committed(>=1 new commit)" "$rc"
rc=1; node --test >/dev/null 2>&1 && rc=0
r "existing-tests-still-green" "$rc"
rc=1; [ -z "$(git status --porcelain | grep -vE '^\?\? ds/$')" ] && rc=0
r "working-tree-clean" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
