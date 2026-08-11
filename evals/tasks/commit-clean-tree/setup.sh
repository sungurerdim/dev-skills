#!/usr/bin/env bash
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
printf '# Clean\n' > README.md; git add -A; git commit -qm "chore: initial fixture state"
echo "fixture ready: $d"
