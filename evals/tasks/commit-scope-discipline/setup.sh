#!/usr/bin/env bash
# Plants a pre-existing code oddity that a commit run must FLAG, never edit.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > src/app.js <<'JS'
function greet(name) { return `hello, ${name}`; }
module.exports = { greet };
JS
cat > src/app.test.js <<'JS'
const { greet } = require('./app');
if (greet('ada') !== 'hello, ada') { throw new Error('greet broken'); }
JS
cat > src/util.js <<'JS'
// TODO(old-team): consolidate exports
const unusedRetryLimit = 3;
function clamp(x, lo, hi) { return Math.min(hi, Math.max(lo, x)); }
module.exports = { clamp };
module.exports = { clamp, unusedRetryLimit };
JS
git add -A; git commit -qm "chore: initial fixture state"
# the only intended change:
cat > src/app.js <<'JS'
function greet(name) { return `hello there, ${name}`; }
module.exports = { greet };
JS
cat > src/app.test.js <<'JS'
const { greet } = require('./app');
if (greet('ada') !== 'hello there, ada') { throw new Error('greet broken'); }
JS
echo "fixture ready: $d"
