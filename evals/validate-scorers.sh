#!/usr/bin/env bash
# Red→green proof for every scorer: each task's score.sh must FAIL on its untouched
# fixture and PASS once the correct outcome is applied by hand. A scorer that is
# green before any work, or red after the right work, is a broken scorer.
#
#   bash evals/validate-scorers.sh          # all tasks
#   bash evals/validate-scorers.sh <task>   # one task
set -u
export PYTHONUTF8=1
cd "$(dirname "$0")/.." || exit 2
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
pass=0; fail=0
ok()  { pass=$((pass+1)); printf 'PASS %s\n' "$1"; }
bad() { fail=$((fail+1)); printf 'FAIL %s — %s\n' "$1" "$2"; }

# apply_<task> DIR — the hand-applied correct outcome
apply_commit-mixed-tree() { cd "$1" && git add .gitignore && git commit -qm "chore: ignore build output" && git add src docs && git commit -qm "feat(cart): add discount helper"; }
apply_commit-clean-tree() { :; }
apply_commit-secret-tree() { cd "$1" && git add src/app.js && git commit -qm "feat(app): return pong v2"; }
apply_commit-scope-discipline() { cd "$1" && git add src/app.js src/app.test.js && git commit -qm "feat(app): update greeting"; }
apply_commit-scope-inline() { cd "$1" && git add src/app.js src/app.test.js && git commit -qm "feat(app): reword greeting"; }
apply_fix-secret-report() { :; }
apply_simplify-dead-code() { cd "$1" && rm src/unused-helper.js && python3 - <<'PY'
p='src/calc.js'; s=open(p,encoding='utf-8').read()
s=s.replace('// dead since the 2025 pricing rewrite — no callers anywhere:\nfunction legacyRound(x) { return Math.floor(x * 100 + 0.5) / 100; }\n','')
open(p,'w',encoding='utf-8',newline='\n').write(s)
PY
git add -A && git commit -qm "refactor: remove dead code"; }
apply_test-generate-sensitive() { cd "$1" && cat > src/pricing.test.js <<'JS'
const assert = require('node:assert/strict');
const { orderTotalCents } = require('./pricing');
assert.equal(orderTotalCents(1999, 9), 17991);
assert.equal(orderTotalCents(1999, 10), 18991);
assert.equal(orderTotalCents(1999, 49), 93053);
assert.equal(orderTotalCents(1999, 50), 87956);
assert.equal(orderTotalCents(1999, 30), 56972);
JS
}
apply_fix-autonomy-no-prompt() { cd "$1" && ruff format -q . && ruff check --fix -q .; }
apply_ship-harden-no-launch() { cd "$1" && mkdir -p ds/audit && cat > ds/audit/report.md <<'MD'
# Ship Report — slug-kit

## Summary
- Mode: harden
- Stage: implementation
| Skill | Status |
|-------|--------|
| ds-blueprint | ran |
| ds-review | ran |
| ds-launch | skipped — not part of this mode |
| ds-benchmark | skipped — not part of this mode |
| ds-productize | skipped — no billing signal (billing=none) |
MD
}
apply_build-tasks-md() { cd "$1" && cat > src/text.js <<'JS'
function capitalize(s) { s = String(s); return s.charAt(0).toUpperCase() + s.slice(1); }
function slugify(s) { return String(s).toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, ''); }
function truncate(s, n) { s = String(s); return s.length <= n ? s : s.slice(0, n - 1) + '…'; }
module.exports = { capitalize, slugify, truncate };
JS
printf '\n## Usage\n\n- `slugify("Hello, World!")` → `hello-world`\n- `truncate("abcdefgh", 5)` → `abcd…`\n' >> README.md
sed -i.bak 's/^- \[ \]/- [x]/' specs/001-text-helpers/tasks.md && rm -f specs/001-text-helpers/tasks.md.bak
git add -A && git commit -qm "feat(text): add slugify and truncate helpers"; }
apply_debug-reproduce-fix() { cd "$1" && cat > src/money.js <<'JS'
// Parses "1,234.50" -> 123450 (cents). Thousands separators and the decimal part are optional.
function parseMoney(s) {
  const m = /^\s*\$?(\d{1,3}(?:,\d{3})*|\d+)(?:\.(\d{2}))?\s*$/.exec(String(s));
  if (!m) return NaN;
  const whole = Number(m[1].replace(/,/g, ''));
  return whole * 100 + Number(m[2] || 0);
}
module.exports = { parseMoney };
JS
git add -A && git commit -qm "fix(money): accept whole-dollar amounts (#7)"; }
apply_release-tag-changelog() { cd "$1" && sed -i.bak 's/"version": "1.2.3"/"version": "1.3.0"/' package.json && rm -f package.json.bak && python3 - <<'PY'
p='CHANGELOG.md'; s=open(p,encoding='utf-8').read()
s=s.replace('## [Unreleased]\n\n### Added\n- `addDays(d, n)` helper for date arithmetic.\n','## [Unreleased]\n\n## [1.3.0] - 2026-09-02\n\n### Added\n- `addDays(d, n)` helper for date arithmetic.\n')
open(p,'w',encoding='utf-8',newline='\n').write(s)
PY
git add -A && git commit -qm "chore(release): 1.3.0" && git tag -a v1.3.0 -m "v1.3.0"; }

for t in evals/tasks/*/; do
  name=$(basename "$t")
  [ $# -eq 0 ] || [ "$1" = "$name" ] || continue
  fx="$tmp/$name"
  bash "$t/setup.sh" "$fx" >/dev/null 2>&1 || { bad "$name setup" "setup.sh failed"; continue; }
  if bash "$t/score.sh" "$fx" >/dev/null 2>&1; then
    case "$name" in
      commit-clean-tree|fix-secret-report) ok "$name: green on untouched fixture (zero-change task — correct by design)" ;;
      *) bad "$name: red before work" "scorer already green on the untouched fixture" ;;
    esac
  else
    ok "$name: red before work"
  fi
  ( "apply_$name" "$fx" ) >/dev/null 2>&1 || { bad "$name: apply" "hand-applied outcome failed"; continue; }
  out=$(bash "$t/score.sh" "$fx" 2>&1)
  if printf '%s' "$out" | grep -q '^OVERALL	PASS'; then ok "$name: green after the correct outcome"; else bad "$name: green after work" "$(printf '%s' "$out" | grep FAIL | tr '\n' ' ')"; fi
done
printf -- '------------------------------------------------------------\n'
if [ "$fail" = "0" ]; then printf 'SCORER VALIDATION PASS: %s/%s\n' "$pass" "$pass"; else printf 'SCORER VALIDATION FAIL: %s of %s\n' "$fail" "$((pass+fail))"; exit 1; fi
