#!/bin/sh
# ds-quality-gate — Claude Code Stop hook. Thin launcher over ds-quality.py (stdlib python3, identical on macOS, Linux and
# Windows/Git Bash); every decision lives there. See references/hook-contract.md.
d=$(dirname "$0")
py=
for c in python3 python; do
  command -v "$c" >/dev/null 2>&1 || continue
  # skip the Microsoft Store python3 stub and anything older than 3.8
  "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' >/dev/null 2>&1 && { py=$c; break; }
done
[ -n "$py" ] || { echo "ds-quality: python3 (>= 3.8) not found - quality gate inactive" >&2; exit 0; }
exec "$py" "$d/ds-quality.py" gate "$@"
