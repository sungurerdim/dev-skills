#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
# Red proof is measured mechanically: the suite must go red again when the original
# (buggy) source is restored, which proves the test exercises the bug.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
root=$(git rev-list --max-parents=0 HEAD)
rc=1; node --test >/dev/null 2>&1 && rc=0
r "tests-green-after-fix" "$rc"
rc=1; node -e "const {parseMoney}=require('./src/money'); if (parseMoney('1,234')!==123400 || parseMoney('12')!==1200 || parseMoney('1,234.50')!==123450) process.exit(1)" >/dev/null 2>&1 && rc=0
r "bug-actually-fixed(whole-dollar-and-decimal-inputs)" "$rc"
# the shipped test still asserts the original expected values — never weakened
rc=1; grep -q "123400" test/money.test.js && grep -q "1200" test/money.test.js && grep -q "123450" test/money.test.js && rc=0
r "test-not-weakened(original-assertions-present)" "$rc"
# red proof: restore the buggy source, the suite must fail
cp src/money.js money.eval.bak
git show "$root:src/money.js" > src/money.js
node --test >/dev/null 2>&1; red=$?
cp money.eval.bak src/money.js; rm -f money.eval.bak
rc=1; [ "$red" != "0" ] && rc=0
r "red-on-original-source(regression-test-exercises-the-bug)" "$rc"
rc=1; [ "$(git rev-list --count HEAD)" -ge 2 ] && git diff --quiet "$root" HEAD -- README.md && rc=0
r "fix-committed-readme-untouched" "$rc"
rc=1; [ -z "$(git status --porcelain | grep -vE '^\?\? ds/$')" ] && rc=0
r "working-tree-clean" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
