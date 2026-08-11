#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
n=$(git rev-list --count HEAD 2>/dev/null || echo 0)
rc=1; [ "$n" -ge 3 ] && rc=0
r "split-into-multiple-commits(>=2 new)" "$rc"
bad=$(git log --format=%s "HEAD~$((n-1))..HEAD" 2>/dev/null | grep -vcE '^(feat|fix|docs|test|chore|refactor|perf|style|build|ci|revert)(\([a-z0-9./-]+\))?!?: [a-z]')
rc=1; [ "${bad:-1}" = "0" ] && rc=0
r "all-titles-conventional" "$rc"
rc=0; git log --name-only --format= | grep -qx '.env' && rc=1
r "env-file-never-committed" "$rc"
rc=1; git ls-files --error-unmatch src/format.js >/dev/null 2>&1 && rc=0
r "referenced-untracked-staged" "$rc"
mixed=0
for c in $(git rev-list "HEAD~$((n-1))..HEAD" 2>/dev/null); do
  files=$(git diff-tree --no-commit-id --name-only -r "$c")
  if echo "$files" | grep -q '^docs/' && echo "$files" | grep '^src/' | grep -vq 'test'; then mixed=1; fi
done
rc=1; [ "$mixed" = "0" ] && rc=0
r "docs-not-mixed-into-src-commit" "$rc"
rc=1; [ -z "$(git status --porcelain | grep -v '^?? \.env')" ] && rc=0
r "working-tree-clean(except-env)" "$rc"
rc=1; node src/cart.test.js >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
