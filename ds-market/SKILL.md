---
name: ds-market
description: Marketing and growth — positioning, copy generation, and growth tactics for indie and solo-dev products. Use when crafting positioning, marketing copy, or a growth plan.
---

# /ds-market

Solo developers build great products but can't get anyone to notice. This skill generates positioning, copy, and growth playbook to change that.

**Marketing & Growth** — Positioning, copy generation, and growth tactics for indie and solo-dev products.

## Triggers

- User runs `/ds-market`
- User asks about marketing strategy, growth tactics, or user acquisition
- User asks "how do I market my app" or "write marketing copy"
- User asks about launch strategy, social media, or landing page

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "marketing strategy, growth tactics, positioning" | "store-specific metadata only" (→ ds-launch --listing) |
| "write taglines / landing-page copy / Product Hunt post" | "user-research for tracking taxonomy" (→ ds-analytics) |
| "indie / solo-dev positioning playbook" | "OSS competitive positioning" (→ ds-benchmark) |
| "8-week pre-launch timeline + channels" | "release management / staged rollout" (→ ds-launch --release) |

## Contract

- Strategic guidance skill — produces plans, copy, checklists; not code.
- Every deliverable (strategy, copy, checklist) accounted for in summary — zero silent drops.
- Minimal liability + maximum privacy + maximum efficiency + minimum dependencies: established marketing patterns only (no dark patterns), no invasive tracking, automation-first tactics, free/low-cost strategies first.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; asks user for context when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--strategy` | Full marketing plan: positioning, channels, timeline |
| `--copy` | Generate marketing text: taglines, descriptions, social posts |
| `--growth` | Growth tactics: referral, organic, community, content |
| `--auto` | Run strategy + copy + growth sequentially |
| `--resume` | Resume from `ds/audit/market.json` without prompting |
| `--clean` | Delete existing state and start fresh |

No flags → present interactive mode selection.

## Scopes

### Strategy

| Area | What It Covers |
|------|---------------|
| Positioning | Competitor analysis, differentiators, unique value proposition |
| User persona | BAG + JTBD framework: Behaviors, Attitudes, Goals, Jobs To Be Done, context triggers |
| Channel selection | Channels matched to audience (organic, paid, community) |
| Timeline | Pre-launch (8 weeks), launch day, post-launch (week 1, month 1, month 3) |
| Budget | Ladder: $0 (organic) → $100-300 (Apple Search Ads) → $300-800 (+ Google App Campaigns) → $800-2,000 (+ social, retargeting) |

### Copy

| Type | What It Generates |
|------|------------------|
| Taglines | 5 options across 3 proven formulas (see references/copy-and-growth-playbook.md) |
| App description | Short (80 char) + long (4000 char) store descriptions — pain-first opening |
| Social posts | Platform-specific posts (X, LinkedIn, Reddit, Product Hunt) |
| Landing page | Hero + proof (demo/metric) + philosophy (beliefs) + features + social proof + CTA |
| Email sequences | Welcome, onboarding, retention, win-back |
| Press kit | Product description, founder bio, screenshots, media contact |

**Copy formulas** (one MUST be applied to every tagline / description / social post). Full formulas + examples + voice rules + anti-patterns → [references/copy-and-growth-playbook.md](references/copy-and-growth-playbook.md). Summary:

| Formula | Use for | Shape |
|---------|---------|-------|
| Contrarian Hook | dev-tool virality | `"{Status-quo} is broken/dead. {Product} is what actually works."` |
| Pain-First (PAS) | landing-page conversion | `"You've tried {common-approach}. It {specific-failure}. {Product} {specific-fix}."` |
| Philosophy Statement | long-term positioning | `"We believe {sharp-belief}. That's why {product} {specific-design-decision}."` |
| Metric Proof | credibility | `"{before-metric} → {after-metric}. {Implication}."` |

**Rules:** every tagline set must include ≥1 Contrarian + ≥1 Metric-Proof option. Store descriptions open with pain or outcome, never feature list.

**Voice rules:**

- **Allowed power words:** prevents, eliminates, enforces, catches, verifies, reduces, automates, replaces, ships.
- **Forbidden:** leverage, empower, unlock, seamlessly, cutting-edge, next-generation, world-class, robust (unless about actual robustness testing), comprehensive (unless quantified), innovative, holistic, synergy.
- **Tone:** confident, opinionated, technically precise. Not salesy, not humble, not academic. Short sentences. Active voice. Imperative mood. Developer language, not marketing language.

### Growth

| Tactic | What It Covers |
|--------|---------------|
| Organic | SEO, content marketing, dev blog |
| Build-in-public | Milestone posts with metrics; transparency *as* positioning |
| AEO | Answer Engine Optimization (ChatGPT ~55-60%, Perplexity ~18-22%, Gemini ~10-14% of AI search). Tactics: answer-first content (40-60 word direct answers), Schema.org (FAQ/HowTo/Article), citation density (stats every 150-200 words with linked sources), freshness (AI engines favor 25.7% fresher sources), Q&A format. Reddit critical (46.7% of Perplexity top sources). |
| Referral | Program design, bilateral incentive, reward < 50% CAC |
| Community | Reddit, Discord, X, dev communities |
| Content | 3-2-1 framework: 3 value, 2 engagement, 1 promo / week. Format ROI: short-form video (2.5× engagement) > technical blogs (67% more leads) > code samples > infographics > docs (credibility) |
| Product Hunt | Multi-launch compounds visibility. External hunter partnership (2-3 weeks pre-launch), 12:01 AM PT timing, visual-first gallery (5-7 images: positioning → workflow → outcome), pre-written maker comment (<800 chars), weekend launches better for dev tools. PH = 2.7M monthly visitors. |
| Directories | AlternativeTo, SaaSHub, BetaList, awesome-* GitHub lists, SetApp (Mac), G2/Capterra (B2B) |
| Email | 14-day onboarding sequence, retention, churn-prevention triggers |
| Partnerships | Cross-promotion, integration partnerships |
| Metrics | DAU/MAU, Day 1/7/30 retention targets, viral coefficient (K), CAC/LTV ratio |

Full growth playbook, AEO tactics, anti-patterns → [references/copy-and-growth-playbook.md](references/copy-and-growth-playbook.md).

## Delegation

**Owns:** marketing, positioning, copy, growth, channels | **Delegates:** none | **Receives:** ds-launch → marketing copy for store listings

## Execution Flow

Setup → Research → Generate → Review → [Needs-Approval] → Summary

### Phase 1: Setup

**Recovery check:** DETECT `ds/audit/market.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-read README + product context, discard stale research), skip `done` phases, announce `[MKT] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ modes_invoked[], context: {product, audience, competitors[]}, scopes_done[], deliverables_generated[] }`.

**IDU:** Profile → Config.audience, Type + Stack. Findings() → verify + use. Absent → own analysis.

1. Flags → proceed directly; no flags → interactive menu.
2. Gather context: what app does (read README), platform, stage, target user, monetization model.
3. Insufficient → ask: one-line description, target audience, top 3 competitors.

**Gate:** Product context sufficient. If fails → re-prompt minimum required: one-line description + target audience + monetization model; no response after 3 prompts → exit with WARN "Insufficient product context — re-run /ds-market and provide a one-line description when prompted."

### Phase 2: Research [--strategy]

Identify 3-5 direct competitors; analyze positioning (taglines, features, pricing); identify differentiation.

**Gate:** Competitive landscape understood. If fails → fewer than 3 competitors found → proceed with partial list; use Contrarian or Philosophy-first template (no competitor data needed); note partial coverage in deliverable.

### Phase 3: Generate

**Strategy mode:**

1. Positioning statement (best-fit template):
   - **Standard:** `"For {audience} who {need}, {product} is {category} that {key-benefit}. Unlike {alternative}, {product} {differentiator}."`
   - **Contrarian:** `"{product} exists because {status-quo} is broken. {One sentence on what it does differently}."`
   - **Philosophy-first:** `"We believe {sharp-belief}. {product} is built around that — {how belief shapes the product}."`
   - Pick by strongest angle: standard for B2B/enterprise, contrarian for dev tools, philosophy-first for opinionated products.
2. User persona (1-2 personas).
3. Channel strategy with priorities (high/medium/low effort × impact).
4. Timeline: pre-launch (4 weeks) → launch day → week 1 → month 1.
5. Budget breakdown: $0/mo (organic), $50/mo (starter paid), $200/mo (growth).

**Copy mode:**

1. 5 tagline options using formulas from references/copy-and-growth-playbook.md (≥1 Contrarian + ≥1 Metric-Proof).
2. Store descriptions (short + long) as **drafts** — first sentence pain-first or outcome-first, never feature-first. Output marked `[DRAFT]` — separate finalization pass produces store-ready versions.
3. 5 social media posts per platform.
4. Landing page copy: hero + proof layer (demo / metric) + philosophy (3-5 sharp beliefs) + features + social proof + CTA.
5. Press kit content.
6. Apply Voice Rules to all generated copy (forbidden-word check, tone verification).

**Growth mode:**

1. Top 10 growth tactics ranked by effort × impact for solo dev.
2. Content calendar (4 weeks).
3. Referral program design.
4. Community engagement plan.

**Gate:** All requested artifacts generated. If fails → identify failed artifact (positioning, taglines, descriptions, social posts, growth tactics) → log `failed` in state.data.deliverables_generated, continue with rest, mark failed as `[DRAFT — generation incomplete]` in summary with manual-completion instructions.

### Phase 4: Review

Verify: no false feature claims, no dark patterns (manipulative urgency, hidden costs), accessibility (alt text, contrast), all store listing content within character limits.

**Gate:** All content passes review. If fails → apply correction inline (remove forbidden word, rephrase feature-first opening, correct character count), re-check; still failing after one pass → mark `[DRAFT — requires manual review]`, include in summary as flagged.

### Phase 5: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved. If fails → record unresolved as `pending-user-decision`, proceed to Summary with WARN, list unresolved items.

### Phase 6: Summary

```
ds-market: {OK|WARN|FAIL} | Mode: {strategy|copy|growth} | Generated: {n} artifacts | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}

Artifacts:
- {artifact-1}: {brief-description}
- {artifact-2}: {brief-description}

Next steps:
1. {most-important-action}
2. {second-action}
3. {third-action}
```

**Value Delivered:** 1-5 concrete bullets, real marketing outputs only. Example shapes (placeholders, not literal):

- `Positioning statement + BAG-JTBD persona — copy and channel choices now have a target, not "everyone"`
- `{n} taglines (3 proven formulas) + {n}-char app description — A/B-testable copy ready to ship`
- `Pre-launch timeline ({n} weeks) with channel mix + budget ladder ($0 → $300 → $800 → $2k) — solo-dev launch no longer freelance guesswork`
- `{n} Product Hunt / X / LinkedIn / Reddit post drafts platform-tailored — launch day execution scriptable`

Zero-change run: `Marketing strategy already documented — no new deliverables produced`.

**Gate:** Summary printed with artifact list + next steps + Value Delivered. If fails → write partial summary listing completed deliverables (including `[DRAFT]`), omit never-started ones, status WARN: "Summary incomplete — re-run /ds-market --resume to continue."

## Quality Gates

- No false claims about features the app doesn't have
- No dark patterns (fake urgency, hidden costs, manipulative copy)
- All store listing text within platform character limits
- Budget recommendations start from $0 (free tactics first)
- Growth tactics ethical and privacy-respecting
- All generated copy passes Voice Rules (zero forbidden words, pain-first or contrarian opening, no feature-first descriptions)
- Every tagline set includes ≥1 Contrarian + ≥1 Metric-Proof
- Store descriptions open with pain/outcome, never feature list
- Landing page structure includes proof layer (demo/metric) + philosophy section (beliefs)
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/market.json` updated per deliverable, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| No product context | Ask for one-line description + target audience |
| Unknown competitor landscape | Generate generic positioning, recommend user research |
| Platform not specified | Multi-platform strategy, flag platform-specific items |
| Copy tone unclear | Ask: professional / casual / technical / friendly |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| B2B product | Adjust channels (LinkedIn > Instagram), enterprise positioning |
| Open source project | README as landing page, contrarian hook positioning, build-in-public milestones, multi-channel launch (HN 300-1K stars, Reddit 200-500, PH 200-800), AEO for AI search citation |
| Pre-revenue / free app | Focus on user acquisition, community, future monetization prep |
| Niche market (<10K TAM) | Focus on community depth over broad reach |
| Regulated industry (health, finance) | Flag marketing compliance requirements |
