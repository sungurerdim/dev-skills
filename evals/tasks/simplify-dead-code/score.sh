#!/usr/bin/env bash
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
rc=0; grep -q 'legacyRound' src/calc.js 2>/dev/null && rc=1
r "dead-function-removed" "$rc"
rc=0; [ -e src/unused-helper.js ] && rc=1
r "dead-file-removed" "$rc"
rc=1; grep -q 'function add' src/calc.js && grep -q 'function mul' src/calc.js && rc=0
r "live-code-intact" "$rc"
rc=1; node src/calc.test.js >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
root=$(git rev-list --max-parents=0 HEAD)
rc=1; git diff --quiet "$root" HEAD -- README.md src/calc.test.js && [ -z "$(git status --porcelain -- README.md src/calc.test.js)" ] && rc=0
r "no-collateral-edits" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
