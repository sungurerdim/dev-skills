#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
# Needs ruff + python3 on PATH (the fixture's own toolchain).
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
rc=1; ruff check . >/dev/null 2>&1 && rc=0
r "lint-clean(ruff check)" "$rc"
rc=1; ruff format --check . >/dev/null 2>&1 && rc=0
r "format-clean(ruff format --check)" "$rc"
rc=1; python3 tests/test_pricing.py >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
rc=1; grep -q 'ROUND_HALF_UP' src/shop/pricing.py && grep -q 'qty >= 50' src/shop/pricing.py && rc=0
r "behavior-intact(discount-logic-present)" "$rc"
# only the fixture's own files may change; nothing new and untracked besides caches
rc=1; [ -z "$(git status --porcelain | grep -vE '^ M (src/shop/pricing.py|tests/test_pricing.py)$' | grep -vE '^(A |M |\?\? )?(\.ruff_cache/|__pycache__/)')" ] && rc=0
r "no-unrequested-files-or-edits" "$rc"
rc=1; ! git diff --quiet HEAD -- src/shop/pricing.py 2>/dev/null && rc=0
[ "$(git rev-list --count HEAD)" -gt 1 ] && rc=0
r "fix-actually-landed(pricing.py-changed-or-committed)" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
