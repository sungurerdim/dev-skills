#!/usr/bin/env bash
# Untested pure function. The generated test must be green on correct code AND
# red on a mutated copy — assertion strength measured mechanically.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > src/pricing.js <<'JS'
// Volume discount: 0-9 units none, 10-49 units 5%, 50+ units 12%. Rounds to cents.
function orderTotalCents(unitCents, qty) {
  if (!Number.isInteger(unitCents) || !Number.isInteger(qty) || unitCents < 0 || qty < 0) {
    throw new Error(`Expected non-negative integers, got unitCents=${unitCents} qty=${qty}`);
  }
  const gross = unitCents * qty;
  const pct = qty >= 50 ? 12 : qty >= 10 ? 5 : 0;
  return Math.round(gross * (100 - pct) / 100);
}
module.exports = { orderTotalCents };
JS
printf '# Pricing\n\nVolume-discount helper. No tests yet.\n' > README.md
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
