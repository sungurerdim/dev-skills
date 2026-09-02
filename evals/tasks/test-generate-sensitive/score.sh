#!/usr/bin/env bash
# Finds the generated test file, runs it green against correct code, then runs it
# against two mutants (discount threshold off-by-one, rounding dropped) — a test
# that stays green on a mutant has no real assertions for the spec.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
tf=$(ls src/*.test.js src/*_test.js test/*.js tests/*.js 2>/dev/null | head -1)
rc=1; [ -n "$tf" ] && rc=0
r "test-file-created" "$rc"
if [ -z "$tf" ]; then echo "OVERALL	FAIL	1/5"; exit 1; fi
rc=1; grep -q 'orderTotalCents' "$tf" && rc=0
r "targets-the-function" "$rc"
# Run the generated file with whatever runner the agent wired up: a plain
# `node` script, or jest/vitest/mocha declared in a package.json it created.
# A jest suite run with bare `node` fails on `describe` and would score red on
# every criterion at once — a scorer artifact, not a skill failure.
runner="node"
if [ -f package.json ]; then
  grep -q '"vitest"' package.json && runner="npx --no-install vitest run --silent"
  grep -q '"jest"'   package.json && runner="npx --no-install jest --silent"
  grep -q '"mocha"'  package.json && runner="npx --no-install mocha"
fi
run_tests() { $runner "$tf" >/dev/null 2>&1; }
rc=1; run_tests && rc=0
r "green-on-correct-code($runner)" "$rc"
cp src/pricing.js /tmp/pricing.eval.bak 2>/dev/null || cp src/pricing.js pricing.eval.bak
mutate() { python3 - "$1" <<'PY'
import sys
p = 'src/pricing.js'; s = open(p).read()
if sys.argv[1] == 'threshold':
    s = s.replace('qty >= 50 ? 12', 'qty >= 51 ? 12').replace('qty >= 10 ? 5', 'qty >= 11 ? 5')
else:
    s = s.replace('Math.round(gross * (100 - pct) / 100)', 'Math.floor(gross * (100 - pct) / 100)')
open(p, 'w').write(s)
PY
}
restore() { cp pricing.eval.bak src/pricing.js 2>/dev/null || cp /tmp/pricing.eval.bak src/pricing.js; }
cp src/pricing.js pricing.eval.bak
mutate threshold; run_tests; m1=$?; restore
mutate rounding;  run_tests; m2=$?; restore
rm -f pricing.eval.bak /tmp/pricing.eval.bak
rc=1; [ "$m1" != "0" ] && rc=0
r "red-on-threshold-mutant(assertions-cover-discount-boundaries)" "$rc"
rc=1; [ "$m2" != "0" ] && rc=0
r "red-on-rounding-mutant(assertions-cover-rounding)" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
