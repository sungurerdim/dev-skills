# Arm Config Templates — Aider & git pre-commit

Consumer: SKILL.md Phase 4 (Enforcement), Arms B and C. Both wire the Phase-3 entry point verbatim — copy these templates, substituting the actual entry-point command.

## Arm B — Aider `.aider.conf.yml`

Verified against Aider's official config docs. Merge into existing values — never clobber unrelated keys.

```yaml
auto-lint: true          # Aider's default — runs lint-cmd after every edit
lint-cmd: "bash scripts/quality.sh"   # or `make quality` / `npm run quality` — the Phase-3 command
auto-test: true          # Aider's default is false — set true to enforce on every edit
test-cmd: "bash scripts/quality.sh"
```

`lint-cmd` accepts a per-language form (`lint-cmd: "python: ruff check ."`) for per-language granularity instead of the single fail-fast entry point; default to the single entry point for parity with the other arms. Aider re-runs the command after edits and surfaces failures to the agent inline (no separate loop-guard needed — Aider owns that flow).

## Arm C — universal `.git/hooks/pre-commit`

For any host without a native arm (Cursor, Windsurf, plain terminal use). Non-zero exit aborts the commit.

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
exec bash scripts/quality.sh   # or: make quality / npm run quality — the Phase-3 command
```

`chmod +x .git/hooks/pre-commit`. Hook-manager already present (husky, `pre-commit` framework) → add the same command as a step in its config instead of writing `.git/hooks/pre-commit` directly, so it isn't clobbered by the manager's own install step.
