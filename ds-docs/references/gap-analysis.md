# Reference: Phase 3 Gap Analysis Detail

Consumer: ds-docs Phase 3 (Gap Analysis). Loaded whenever Phase 3 runs — every default and `--ask` run reaches this phase.

## Ideal docs by project type

| Type | README | API | Dev | User | Ops | Changelog | Compliance |
|------|--------|-----|-----|------|-----|-----------|------------|
| cli | Full | - | Basic | Full (man/help) | - | Yes | - |
| library | Full | Full | Full | Guides | Publish | Yes | - |
| api | Full | Full | Full | Full | Full | Yes | Privacy, DPIA, Breach plan |
| web | Full | Components | Full | Basic | Full | Yes | Privacy, Cookie policy, DPIA |
| mobile | Full | - | Full | Store listing | Full | Yes | Privacy, DPIA, Breach plan, Processor registry |
| desktop | Full | - | Full | Full | Full | Yes | Privacy, DPIA |
| monorepo | Full | Per-package | Full | Per-package | Full | Yes | Per-package if user-facing |
| iac | Full | - | Full | Runbook | Full | Yes | - |
| devtool | Full | Full | Full | Full | - | Yes | - |
| data | Full | Schema | Full | Pipeline guide | Full | Yes | Privacy, DPIA, Model card privacy |
| ml | Full | Model card | Full | Inference guide | Full | Yes | Privacy, DPIA, Model card privacy |
| embedded | Full | HW interface | Full | Setup guide | Flash guide | Yes | - |
| game | Full | - | Full | Player guide | - | Yes | Privacy (if online/IAP) |
| extension | Full | API/hooks | Full | Marketplace | Publish | Yes | Privacy (if data collected) |

Missing docs = HIGH; incomplete (<70%) = MEDIUM.

**Refine scope:** analyze for scannability, clarity, redundancy, conciseness.

## Verify scope (doc vs code sync) — the most critical scope

Finds lies in documentation. For every testable claim, search source to confirm or deny.

| Claim type | How to verify |
|-----------|--------------|
| CLI flags / arguments | Search source for flag definitions (argparse, cobra, clap, commander) |
| Function signatures | Search for function/method definition, compare params + return type |
| API endpoints | Search route definitions (express routes, FastAPI paths, controller annotations) |
| Config keys / env vars | Search for config reads (`process.env`, `os.environ`, config file parsers) |
| Code examples | Verify function names, params, return values match source |
| Default values | Search for default assignments |
| Version numbers | Compare doc versions with manifest/lockfile |
| Setup/install steps | Verify each command works (referenced scripts/commands exist) |
| Feature descriptions | Search for feature implementation |
| Architecture claims | Verify patterns match actual code structure |
| Performance claims | Verify benchmarks / metrics against implementation |
| Security claims | Verify stated security features exist in code |
| Vendor/third-party name in customer-facing copy | Confirm the named vendor/model is still the one wired in the current pipeline; prefer function-neutral phrasing ("speech-to-text engine") unless the name is contractually required (DOC-24) |

**Verification process:** parse each doc into testable claims (every code block, table row, flag, path, number, link); per claim, search codebase for the referenced entity; classify:

| Result | Classification | Action |
|--------|---------------|--------|
| Claim matches source | Verified | Skip |
| Claim doesn't match source | **Drift** — doc outdated | HIGH, show diff |
| Claim references something that doesn't exist | **Stale** — feature/file removed. Before asserting: run a control query proven to return hits on the same corpus/tool/flags (DOC-25) — a control that returns nothing means the search is broken, not the subject | CRITICAL, suggest removal |
| Source has something doc doesn't mention | **Gap** — undocumented feature | MEDIUM, suggest adding |
| Doc duplicates a code-owned fact (version literal, config default, port, dependency version) | **SSOT-copy** — value copied instead of referenced; drifts on next change | MEDIUM, replace with a reference to the owning source (file path, command, or manifest) |
| Number a tool computes (counts, coverage %, sizes, benchmark figures) or that also lives on another surface, hand-written with no generator and no drift check | **Unwired-number** — correct today, silently wrong after the next change | MEDIUM, emit it from the generator or wire it to a drift check |
| Access / verification / "last reviewed" date on a source not opened during this run | **Unverified-date** — freshness asserted instead of observed | HIGH, re-open the source now or drop the date |
| Link returns 404 or target heading missing | **Broken link** | HIGH |

**Generated and cross-surface numbers — stack-independent rule.** A number a doc states has exactly two legal forms: **emitted by its generator** at build time, or **hand-written and covered by a drift check** that goes red when the owning source moves. This covers every number some tool produces (rule/test counts, coverage, bundle size, benchmark results) and every number repeated on a second surface (config, UI copy, site, store listing, another doc). A hand-copied figure that is correct today is still a finding — the finding is the missing wire, not the value. This is the doc-side, stack-independent form of the ds-devops build-hygiene pair DOP-38 (generated artifacts are regenerated at the gate, never hand-edited) and DOP-39 (a cross-surface fact gets one canonical owner plus a drift gate); it applies with no CI, no pipeline, and no particular stack. Dates obey the same discipline: an access/verification date is written only for a source actually opened in this run, and is never bumped to today because the line around it was edited.

Report table: `| # | Type (Drift/Stale/Gap/Broken/SSOT-copy/Unwired-number/Unverified-date) | Doc File:Line | Claim | Actual | Severity |`
Label map for orchestrated runs: ds-ship's promise census uses `promised-not-implemented` (= `Drift`/`Stale` here) and `implemented-not-documented` (= `Gap` here) — same classes, census-side names.

## Product-DX onboarding-curve check (when scope includes getting-started or API docs)

1. Does a "Quickstart" / "Getting Started" guide exist with copy-pasteable first command?
2. Can a new user complete the core flow (install → configure → first success) in under 5 steps?
3. Is the first example minimal (no auth, no config, no external dependencies if possible)?
4. Do examples use `{placeholder}` values (not real secrets, not hardcoded test data)?
5. Is there one canonical entry point everyone is directed to (README or docs landing page)?

## End-user docs & support check group

B6, advisory — never a blocker; user-facing project types only: web, mobile, desktop, extension, game.

| Check | Missing = | Where |
|-------|-----------|-------|
| User-facing FAQ exists | MEDIUM advisory | `docs/user/FAQ.md`, `FAQ.md`, or an in-app/site FAQ section |
| Task-based walkthroughs for the top user flows (short step guides or ≤60s screen-recording equivalents) | MEDIUM advisory | `docs/user/` per-flow guide, or linked from the FAQ/help surface |
| Help surface reachable from the product itself | MEDIUM advisory | In-app help link/menu item, or a site help section linked from the product UI — not doc-repo-only |
| Support contact path published | MEDIUM advisory | Email, contact form, or ticketing link in README/site footer/in-app |

**Minimum verification coverage:** ALL code blocks, ALL flag/option tables, ALL numbered step lists, ALL internal links. These are highest-drift-risk.
