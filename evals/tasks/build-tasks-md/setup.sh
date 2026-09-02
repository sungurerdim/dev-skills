#!/usr/bin/env bash
# Node library plus a specs/*/tasks.md with three tasks, each carrying a `— verify:`
# command. Correct run: every task implemented, every verify command green, tasks
# ticked (or the file removed once all are ticked), work committed, tree clean.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src" "$d/test" "$d/specs/001-text-helpers"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > package.json <<'JSON'
{ "name": "text-kit", "version": "0.1.0", "main": "src/text.js", "scripts": { "test": "node --test" }, "license": "MIT" }
JSON
cat > src/text.js <<'JS'
function capitalize(s) { s = String(s); return s.charAt(0).toUpperCase() + s.slice(1); }
module.exports = { capitalize };
JS
cat > test/text.test.js <<'JS'
const test = require('node:test');
const assert = require('node:assert/strict');
const { capitalize } = require('../src/text');
test('capitalize', () => { assert.equal(capitalize('hello'), 'Hello'); });
JS
printf '# text-kit\n\nSmall string helpers.\n' > README.md
cat > specs/001-text-helpers/tasks.md <<'MD'
# Tasks — text helpers

- [ ] T1 Add `slugify(s)` to `src/text.js` and export it: lowercase, non-alphanumerics collapse to single `-`, no leading/trailing `-` — verify: `node -e "const {slugify}=require('./src/text'); if (slugify('Hello, World!')!=='hello-world' || slugify('  A--B  ')!=='a-b') process.exit(1)"` → exit 0
- [ ] T2 Add `truncate(s, n)` to `src/text.js` and export it: returns `s` unchanged when `s.length <= n`, else the first `n-1` characters plus `…` — verify: `node -e "const {truncate}=require('./src/text'); if (truncate('abc',5)!=='abc' || truncate('abcdefgh',5)!=='abcd…') process.exit(1)"` → exit 0
- [ ] T3 Document both helpers in README.md under a `## Usage` heading with one example each — verify: `grep -q '^## Usage' README.md && grep -q 'slugify' README.md && grep -q 'truncate' README.md` → exit 0

Gate: `node --test` green after every task.
MD
printf 'node_modules/\nds/audit/\n' > .gitignore
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
