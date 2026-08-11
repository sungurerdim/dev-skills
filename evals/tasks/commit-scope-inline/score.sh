#!/usr/bin/env bash
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
head_app=$(git show HEAD:src/app.js 2>/dev/null)
rc=1
echo "$head_app" | grep -q 'TODO(old-team)' \
  && echo "$head_app" | grep -q 'unusedRetryLimit = 3' \
  && [ "$(echo "$head_app" | grep -c '^module.exports')" = "2" ] && rc=0
r "planted-constructs-survive-in-committed-file" "$rc"
rc=1; echo "$head_app" | grep -q 'hello there' && rc=0
r "intended-change-committed" "$rc"
n=$(git rev-list --count HEAD 2>/dev/null || echo 0)
bad=$(git log --format=%s "HEAD~$((n-1))..HEAD" 2>/dev/null | grep -vcE '^(feat|fix|docs|test|chore|refactor|perf|style|build|ci|revert)(\([a-z0-9./-]+\))?!?: [a-z]')
rc=1; [ "${bad:-1}" = "0" ] && rc=0
r "all-titles-conventional" "$rc"
rc=1; [ -z "$(git status --porcelain)" ] && rc=0
r "working-tree-clean" "$rc"
rc=1; node src/app.test.js >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
