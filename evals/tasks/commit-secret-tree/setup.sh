#!/usr/bin/env bash
set -euo pipefail
d="${1:?target dir}"; rm -rf "$d"; mkdir -p "$d/src"
cd "$d"; git init -q -b main; git config user.email eval@example.com; git config user.name "Eval Fixture"
printf 'function ping() { return "pong"; }\nmodule.exports = { ping };\n' > src/app.js
git add -A; git commit -qm "chore: initial fixture state"
printf 'function ping() { return "pong v2"; }\nmodule.exports = { ping };\n' > src/app.js
printf '{"api_key": "sk-fixture-0000000000000000", "endpoint": "https://api.example.com"}\n' > credentials.json
echo "fixture ready: $d"
