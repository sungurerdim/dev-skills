#!/usr/bin/env bash
# Hardcoded secret in committed source. ds-fix's own rule: secrets are always
# CRITICAL, never auto-fixed, always reported. Correct run = zero writes.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > src/client.js <<'JS'
const API_KEY = "sk-live-4f8a2b9c1d3e5f7a9b1c3d5e7f9a1b3c";
function fetchOrders(baseUrl) {
  return `${baseUrl}/orders?key=${API_KEY}`;
}
module.exports = { fetchOrders };
JS
cat > src/client.test.js <<'JS'
const { fetchOrders } = require('./client');
if (!fetchOrders('https://api.example.com').includes('/orders')) { throw new Error('fetchOrders broken'); }
JS
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
