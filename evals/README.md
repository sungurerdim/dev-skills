# Evals

Behavioral evals score what a skill run leaves in a fixture repo, never what the agent says it did.

| Eval | Skill | Request | Proves |
|------|-------|---------|--------|
| `audit_library.py` | ds-audit | `/ds-audit all` | report with status, `Signals:` line and the kernel §6 closing message; store, money, mobile and a11y areas reported N/A for a UI-less library; tests still green; clean tree |

Run: `python3 evals/audit_library.py setup /tmp/fx` → give the agent the request in `/tmp/fx` → `python3 evals/audit_library.py score /tmp/fx`. `validate` proves the scorer is red on the untouched fixture and green on a correct outcome. Compare two skill versions with the same model, fixture and request; record task success, false "done" claims, tokens and tool calls.
