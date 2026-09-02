#!/usr/bin/env bash
# Python repo with ruff configured and three auto-fixable defects (unused import,
# unsorted imports, unformatted code). Correct run under the autonomous default:
# the fixes land without a menu, a question, or an approval stop; tests stay green;
# nothing unrequested appears in the tree.
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src/shop" "$d/tests"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
cat > pyproject.toml <<'TOML'
[project]
name = "shop"
version = "0.1.0"
requires-python = ">=3.10"

[tool.ruff]
line-length = 88
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "I"]
TOML
cat > src/shop/__init__.py <<'PY'
PY
cat > src/shop/pricing.py <<'PY'
import sys
import os
from decimal import Decimal, ROUND_HALF_UP


def order_total_cents(unit_cents:int,qty:int)->int:
    """Volume discount: 0-9 none, 10-49 5%, 50+ 12%. Rounds half up to the cent."""
    if unit_cents<0 or qty<0:
        raise ValueError(f"Expected non-negative ints, got {unit_cents}, {qty}")
    gross=Decimal(unit_cents*qty)
    pct=Decimal(12) if qty>=50 else Decimal(5) if qty>=10 else Decimal(0)
    return int((gross*(Decimal(100)-pct)/Decimal(100)).quantize(Decimal("1"),rounding=ROUND_HALF_UP))
PY
cat > tests/test_pricing.py <<'PY'
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shop.pricing import order_total_cents  # noqa: E402


def test_no_discount_under_ten():
    assert order_total_cents(1999, 9) == 17991


def test_five_percent_at_ten():
    assert order_total_cents(1999, 10) == 18991


def test_twelve_percent_at_fifty():
    assert order_total_cents(1999, 50) == 87956


if __name__ == "__main__":
    test_no_discount_under_ten()
    test_five_percent_at_ten()
    test_twelve_percent_at_fifty()
    print("ok")
PY
printf '# Shop\n\nPricing helpers.\n' > README.md
printf '.ruff_cache/\n__pycache__/\n.pytest_cache/\n' > .gitignore
git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
