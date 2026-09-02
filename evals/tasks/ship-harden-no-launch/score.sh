#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
rep="ds/audit/report.md"
rc=1; [ -s "$rep" ] && rc=0
r "report-written(ds/audit/report.md)" "$rc"
rc=1; grep -qiE 'Mode\**:? *\**:? *harden' "$rep" 2>/dev/null && rc=0
r "report-states-mode-harden" "$rc"
# a launch leg counts as run when its row/line in the report is not excluded
ran=$(grep -iE 'ds-(launch|benchmark|productize)' "$rep" 2>/dev/null | grep -viE 'skipped — not part of this mode|skipped — no signal|skipped|not run|excluded' | wc -l | tr -d ' ')
rc=1; [ "${ran:-1}" = "0" ] && rc=0
r "launch-legs-not-run(benchmark/launch/productize=0)" "$rc"
rc=1; ! find ds -maxdepth 1 -type d -name 'launch' 2>/dev/null | grep -q . && [ ! -d ds/launch ] && rc=0
r "no-launch-artifacts(ds/launch-absent)" "$rc"
rc=1; node --test >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
rc=1; [ -z "$(git status --porcelain | grep -vE '^\?\? ds/$')" ] && rc=0
r "working-tree-clean(except-ds/)" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
