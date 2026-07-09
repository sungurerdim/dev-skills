# ds-productize

Projects reach technical ship-readiness with zero revenue readiness: no monetization model, paid features unenforced client-side, pricing invented in release week, no funnel to learn from.

Audits monetization, pricing/packaging, and go-to-market baseline with file:line evidence, and produces a decision-ready productization plan.

## Install

```bash
git clone https://github.com/sungurerdim/dev-skills.git /tmp/dev-skills
```

| Tool | Install |
|------|---------|
| **Claude Code** | `cp -r /tmp/dev-skills/ds-productize ~/.claude/skills/ds-productize` |
| **Cursor** | Copy `SKILL.md` + `references/` to `.cursor/rules/` |
| **GitHub Copilot** | Append `SKILL.md` content to `.github/copilot-instructions.md` |
| **Windsurf** | Append `SKILL.md` content to `.windsurfrules` |
| **Aider** | Reference `SKILL.md` via `--read` flag |

```bash
rm -rf /tmp/dev-skills
```

## Use

```bash
/ds-productize                       # up-front menu: Audit / Plan / All
/ds-productize --audit               # gap audit of existing monetization/pricing/gtm
/ds-productize --plan                # productization plan -> ds/productize/plan.md
/ds-productize --scope=monetization  # one scope only
```

## Scopes

| Scope | What it audits |
|-------|---------------|
| monetization | Model fit, server-side entitlement enforcement, webhook signature verification, subscription lifecycle (trial/dunning/grace), cancellation parity, free-tier gate design |
| pricing | Tier/decoy structure, annual framing, price externalization, commission/MoR fit, packaging copy |
| gtm | Value proposition (cross-checked against code), persona/JTBD, conversion surface, privacy-first funnel events, revenue-metric computability, launch plan |

## Features

- Benchmarks cited per rule (RevenueCat SOSA, subscription-law summaries) — no from-memory statistics
- CRITICAL gate on entitlement bypass, unverified payment webhooks, and selling promised-not-implemented features
- Business decisions are approval-gated (Category B) — the skill never picks your price for you
- Delegates canonical legal/privacy to ds-compliance, billing-code security to ds-backend, store execution to ds-launch
- State-exempt — audit + plan regenerate from source; `ds/productize/plan.md` is the durable deliverable
