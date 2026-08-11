#!/usr/bin/env bash
# Committed tree with one dead function + one dead file; live code has tests.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > src/calc.js <<'JS'
function add(a, b) { return a + b; }
function mul(a, b) { return a * b; }
// dead since the 2025 pricing rewrite — no callers anywhere:
function legacyRound(x) { return Math.floor(x * 100 + 0.5) / 100; }
module.exports = { add, mul };
JS
cat > src/calc.test.js <<'JS'
const { add, mul } = require('./calc');
if (add(2, 3) !== 5) { throw new Error('add broken'); }
if (mul(4, 5) !== 20) { throw new Error('mul broken'); }
JS
cat > src/unused-helper.js <<'JS'
// no file in this repo requires this module
function shout(s) { return s.toUpperCase(); }
module.exports = { shout };
JS
printf '# Calc\n\nTiny arithmetic helpers.\n' > README.md
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
