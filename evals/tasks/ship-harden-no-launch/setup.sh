#!/usr/bin/env bash
# Small node library with tests and no UI / store / billing signals. A harden-mode
# ship run must produce ds/audit/report.md with Mode: harden and must not run the
# launch legs (ds-benchmark, ds-launch, ds-productize) — they are mode-excluded and
# signal-absent here.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src" "$d/test"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > package.json <<'JSON'
{
  "name": "slug-kit",
  "version": "0.3.0",
  "description": "Tiny slug helpers",
  "main": "src/index.js",
  "scripts": { "test": "node --test" },
  "license": "MIT"
}
JSON
cat > src/index.js <<'JS'
function slugify(s) {
  return String(s).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '');
}
function truncate(s, n) {
  s = String(s);
  return s.length <= n ? s : s.slice(0, n);
}
module.exports = { slugify, truncate };
JS
cat > test/index.test.js <<'JS'
const test = require('node:test');
const assert = require('node:assert/strict');
const { slugify, truncate } = require('../src/index');
test('slugify collapses punctuation', () => { assert.equal(slugify('Hello, World!'), 'hello-world'); });
test('truncate keeps short strings', () => { assert.equal(truncate('abc', 5), 'abc'); });
JS
printf '# slug-kit\n\nTiny slug helpers.\n\n## Install\n\n`npm install slug-kit`\n' > README.md
printf 'node_modules/\nds/audit/\n' > .gitignore
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
