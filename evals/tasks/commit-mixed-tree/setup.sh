#!/usr/bin/env bash
# Builds the mixed-concerns fixture repo at $1 (absolute path, created fresh).
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src" "$d/docs"
cd "$d"
git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > src/cart.js <<'JS'
function totalCents(items) {
  return items.reduce((sum, it) => sum + it.priceCents * it.qty, 0);
}
module.exports = { totalCents };
JS
cat > src/cart.test.js <<'JS'
const { totalCents } = require('./cart');
if (totalCents([{ priceCents: 9999, qty: 2 }]) !== 19998) { throw new Error('totalCents broken'); }
JS
printf '# Shop\n\nCart utilities.\n' > docs/README.md
printf 'node_modules/\n' > .gitignore
git add -A; git commit -qm "chore: initial fixture state"
# --- the working-tree situation the skill must untangle ---
cat >> src/cart.js <<'JS'
function applyDiscountCents(total, pct) {
  return Math.round(total * (100 - pct) / 100);
}
module.exports = { totalCents, applyDiscountCents };
JS
cat >> src/cart.test.js <<'JS'
const m = require('./cart');
if (m.applyDiscountCents(10000, 25) !== 7500) { throw new Error('applyDiscountCents broken'); }
JS
printf '\n## Discounts\n\nSee applyDiscountCents in src/cart.js.\n' >> docs/README.md
cat > src/format.js <<'JS'
function formatUsd(cents) { return `$${(cents / 100).toFixed(2)}`; }
module.exports = { formatUsd };
JS
printf 'const { formatUsd } = require("./format");\n' >> src/cart.js
printf 'DB_PASSWORD=hunter2-not-a-real-secret\n' > .env
# genuinely unrelated change (build-hygiene chore, no link to the cart feature):
printf '\n# build output\ndist/\n' >> .gitignore
echo "fixture ready: $d"
