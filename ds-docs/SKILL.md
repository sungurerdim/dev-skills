---
name: ds-docs
description: Documentation integrity — gap analysis, doc-drift verification, ADR tracking, and AI-harness context-file curation. Use when docs are incomplete or stale, the user asks to write/improve README or API docs, wants a decision recorded, or wants CLAUDE.md/AGENTS.md trimmed.
---

# /ds-docs

Documentation drifts from code the moment it's written, decisions evaporate with no paper trail, and AI-harness context files silently bloat past the point they help. This skill detects the gaps, verifies claims against source code, tracks architecture decisions, and keeps harness context files signal-dense.

**Documentation & Decision Integrity** — doc-drift verification, gap generation, ADR tracking, harness-context-file curation.

> **Completion Evidence — applies to every phase:** Report `done`/`OK` only with the machine-checkable evidence the gates name — the exact command run and its observed output (or `file:line` diff). Missing evidence → report `INCOMPLETE` plus what is missing. Self-assessment is never evidence. *(This band repeats at file end by design — both copies are normative.)*

## Triggers

- User runs `/ds-docs`, asks to check, generate, or improve documentation, asks "what docs are missing" / "is the README up to date", or asks to verify documentation accuracy against source code

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit documentation gaps", "is README up to date" | "audit code quality" (→ ds-review) |
| "generate API docs from source" | "write marketing copy / landing page" (→ external / manual) |
| "verify docs against code (no drift)" | "test the documented examples" (→ ds-test) |
| "write ADR for this decision" | "research industry best practices" (→ ds-research) |
| "audit/trim my CLAUDE.md or AGENTS.md", "optimize my agent instructions file" | "configure harness permissions or install tools" (→ ds-rig) |

## Contract

**Dimensions:** B5 (getting-started), B6, C3 (templates), C5 (deprecation), A10 (API doc completeness), D10 (support docs)

- Every generated sentence must earn its place — no filler, marketing language, or obvious statements.
- Only generates/modifies documentation files — never touches source code.
- Verifies claims against actual source code before writing.
- Standalone. Uses blueprint profile when available; `ds/audit/findings.md` only when fresh (`git_hash == HEAD` AND current run-cycle); own analysis otherwise.
- Full accounting enforced: every finding and planned check ends in an explicit disposition (fixed / skipped + reason / only you can do); summary totals balance.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker. <!-- portable-only -->
- State-exempt: generated docs on disk are the progress record; re-running naturally resumes.

## Arguments

| Flag | Effect |
|------|--------|
| `--preview` | Analyze gaps only, no generation |
| `--scope={x}` | Single scope: readme, api, dev, user, ops, support, changelog, compliance, adr, harness, refine, verify |
| `--adr` | ADR mode: scan architecture decisions, propose/maintain numbered ADR files under `docs/adr/` |
| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |

Default: no disambiguating flag resolves to Auto mode (detect + analyze + generate all applicable scopes), recorded in the summary. `--ask` with no disambiguating flag: present mode selection to the user.

## Scopes

12 scopes — every row below runs when its signal applies (Relevance-First table follows).

| Scope | Target | Purpose |
|-------|--------|---------|
| readme | `README.md` | Project overview, quick start |
| api | `docs/api/`, `API.md` | Endpoint/function reference |
| dev | `CONTRIBUTING.md`, `docs/dev/` | Developer onboarding |
| user | `docs/user/`, `USAGE.md` | End-user guides |
| ops | `docs/ops/`, `DEPLOY.md` | Deployment, operations |
| support | `docs/support/`, `RUNBOOK.md` | D10 (advisory) — error-remediation runbooks, known-error KB, support escalation guide |
| changelog | `CHANGELOG.md` | Version history |
| compliance | `docs/compliance/` | Privacy policy, DPIA, breach plan, processor registry |
| adr | `docs/adr/` | Architecture Decision Records — numbered, with Context / Decision / Consequences |
| harness | `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, `.windsurfrules`/`.devin/rules/`, `.github/copilot-instructions.md`, `GEMINI.md`, `CONVENTIONS.md` | AI-harness context files — cut signal-diluting content, enforce per-vendor length budget |
| refine | Existing docs | UX/DX quality improvement |
| verify | Existing docs | Verify claims against source code |

| Scope | Runs when (signal) | Otherwise |
|-------|---------------------|-----------|
| readme | any source — every project needs one | — |
| api | `api` ≠ none, or a library/CLI with public exports | N/A — no API or exported surface |
| dev | any source — contributor onboarding applies broadly | — |
| user | `audience=public`, or `platforms` includes a UI/store target | N/A — developer-only surface |
| ops | `deploy` ≠ none | N/A — no deployment surface |
| support | `audience=public` and (`ui` ≠ none or `platforms` includes a store target) | N/A — not a user-facing product |
| changelog | any source — version history applies to any released artifact | — |
| compliance | `pii=yes`, `jurisdiction` resolved, or `audience=public` | N/A — no regulated-data or public-market signal |
| adr | any source — Category B decisions can exist in any codebase | — |
| harness | a harness-context file already exists, or `--scope=harness` explicitly requested | N/A — no harness file and scope not requested |
| refine | any source — applies whenever existing docs are found | N/A — no existing docs to refine |
| verify | any source — applies whenever existing docs are found | N/A — no existing docs to verify |

### Scope references

| Scope | Reference | Loaded when |
|-------|-----------|-------------|
| adr | [references/scope-adr.md](references/scope-adr.md) — ADR template, numbering, inventory/proposal/supersedence operations | `--adr` flag or `adr` scope explicitly selected |
| harness | [references/scope-harness.md](references/scope-harness.md) — target files, content classification (DOC-10–17), length budgets, Category B approval | `--scope=harness` or `harness` scope explicitly selected |

## Delegation

**Owns:** doc-drift, feature-documentation, adr (`--adr` mode), harness-context-audit (`--scope=harness`) | **Delegates:** none | **Receives:** ds-benchmark → ADR recording of accepted gap decisions; ds-ship → Phase 4b; ds-repo → CONTRIBUTING / LICENSE content generation. Verified consumer of ds-blueprint findings (docs scope): fills gaps from them, does not re-produce scan findings.; ds-freeze → post-freeze doc sync (deferred items never claimed live)

## Execution Flow

Setup → Analysis → Gap Analysis → [Plan] → Generate → [Needs-Approval] → Summary

### Phase 0: Pre-flight [ALWAYS — never skip]

**Upstream artifacts:** Profile → {`Audience:`, `Entry:`/`Modules:`/`Data Flow:`, Type, `Priorities:`}. Findings({docs}) → verify + use. Absent → own analysis. Freshness: see ../core/findings-and-profile-format.md — fresh → target specific gaps, skip covered scopes; drifted → incremental re-analysis of touched scopes, full only if structural/large; absent → own full analysis.

**Gate:** upstream artifacts read, findings loaded or own analysis planned. If fails → findings unreadable → discard, proceed with own full analysis; profile absent → continue + note "no blueprint profile — using own analysis" in run header.

### Phase 1: Setup

1. **Mode selection.** Default: Auto mode (detect + analyze + generate all applicable scopes), recorded in the summary. `--ask`, no disambiguating flag: present a menu of every mode: Auto (recommended — detect + analyze + generate all), Preview, Scoped, ADR, (Cancel). A disambiguating flag (e.g. `--adr`) skips the menu either way.
2. **Scope selection.** Default (Scoped mode only — Auto/Preview already cover every scope): all applicable areas, gaps filled on existing docs. `--ask`, Scoped mode: ask which areas (Core: readme+changelog / Technical: api+dev / User-facing: user+ops / Agent-facing: harness); how to handle existing (Fill gaps / Refine / Verify claims / Update all).

**Gate:** Mode and scope selected, or flags parsed. If fails → `--ask` got no response after two attempts → default Auto + all scopes; announce `[DOC] No selection received — defaulting to Auto mode, all scopes.`

### Phase 2: Analysis

Scan existing docs, detect project type, assess completeness. Apply quality rules from [references/rules-writing.md](references/rules-writing.md):

1. Search for doc files (`README.md`, `CONTRIBUTING.md`, `docs/*`, `CHANGELOG.md`, `API.md`, `DEPLOY.md`); per found doc, read + assess completeness (0-100%).
2. Project type: profile `Type` if present; else detect from config files.
3. Check doc-sync: README drift, API signature mismatch, deprecated refs, broken links; a structural change (file move/add/delete, rename, dependency bump) with no matching doc update — Phase 3 Verify scope's Drift/Stale detection is the safety net when same-commit coupling was missed (DOC-18); multiple `docs/compliance/*` copies within one checkout (monorepo packages) with diverged content and no canonical-plus-pointer structure (DOC-19); sibling files in a project's own machine-parsed corpus (a rules/fixtures/data directory another tool extracts from) using inconsistent heading levels or entry shapes for equivalent entries (DOC-26).
4. Deterministic doc linters configured in the repo (`.vale.ini` / `.markdownlint*` / `lychee.toml` / `.lycheeignore`) → run them and fold their output into findings ([references/rules-writing.md](references/rules-writing.md) DOC-09 severity mapping); absent → perform the same checks manually and record a gap-note — never install tools unasked.
5. **Doc-type discipline (Diátaxis, advisory):** classify each `user`/`dev`/`api` doc against the four Diátaxis types — tutorial / how-to guide / reference / explanation (framework with multi-org production adoption: Django, Canonical/Ubuntu, Cloudflare). One doc mixing types (reference tables interleaved with tutorial narrative, explanation buried in a how-to) → MEDIUM finding proposing a split along type boundaries; a needed type missing entirely for the project's audience (e.g. reference exists but no how-to for the top user tasks) → advisory row in the Phase 3 gap table.

**Gate:** Project type detected + existing docs inventoried with completeness scores. If fails → undetermined type → prompt user "What type? (cli / library / api / web / mobile / desktop / monorepo / other)"; unreadable doc → record `{ file, completeness: 0, status: "unreadable" }`, continue inventory.

### Phase 3: Gap Analysis (ideal vs current)

Full detail (ideal-docs-by-type table, Verify-scope claim/verification tables, the generated-numbers stack-independent rule, Product-DX check, End-user docs & support check group): [references/gap-analysis.md](references/gap-analysis.md). Missing docs = HIGH; incomplete (<70%) = MEDIUM.

**Harness scope:** orthogonal to project type — audits whatever AI-harness context files exist (`CLAUDE.md`/`AGENTS.md`-class; [references/scope-harness.md](references/scope-harness.md)). None present → advisory, not a gap, unless the scope was explicitly requested.

Report table: `| # | Type (Drift/Stale/Gap/Broken/SSOT-copy/Unwired-number/Unverified-date) | Doc File:Line | Claim | Actual | Severity |`
Label map for orchestrated runs: ds-ship's promise census uses `promised-not-implemented` (= `Drift`/`Stale` here) and `implemented-not-documented` (= `Gap` here) — same classes, census-side names.

**Gate:** Gap analysis complete with severity-classified findings. If fails → unreadable source file referenced by a claim → record `{ type: "inconclusive", severity: "MEDIUM", reason: "source file unreadable" }`, re-read once before marking inconclusive; still fails → flag scope `inconclusive` in summary.

### Phase 4: Plan Review [--ask]

Default: skip this phase — proceed directly to Phase 5 with every detected gap addressed (Generate All), recorded in the summary. `--ask`: display the plan (target files, sections, sources); ask Generate All / High Priority Only / Abort.

**Gate:** Plan resolved (by default, or by `--ask` response). If fails → `--ask` Abort → exit cleanly `docs: ABORTED | Generated: 0`; `--ask` High Priority Only → update scopes_selected to HIGH/CRITICAL only, proceed.

### Phase 5: Generate Documentation (skip if --preview)

**Checkpoint pre-step (before the first doc file is written,** [core checkpoint protocol](../core/checkpoint-protocol.md)**):** `git status --porcelain` → empty → proceed. Non-empty and disjoint from this run's planned targets → proceed, list the dirty paths as untouched. Non-empty and a planned target is already dirty → default: mark that target `skipped (only you can do)`, continue with the rest. `--ask`: show the dirty files, ask Commit first (recommended) / Stash / Proceed anyway (generation may overwrite uncommitted doc edits). Never overwrite uncommitted doc changes silently.

Principles: extract from code, don't invent — read source for actual signatures/endpoints/configs; brevity over verbosity — every sentence earns its place; scannable format — headers, bullets, tables, copy-pasteable commands; action-oriented — focus on what the reader needs to do. Source mandate: every documented flag, endpoint, or config value MUST be verified by searching source before inclusion. Every number written must trace to its generator or to a drift-checked canonical owner (see [references/gap-analysis.md](references/gap-analysis.md) § Generated and cross-surface numbers) — a figure with neither is not written; every date must belong to a source opened in this run.

**Compliance scope (when scope = compliance):**

- **Overwrite prevention:** target file exists → do NOT overwrite blind. Default: resolves by best judgment (Update when the proposed version is more accurate/complete than the existing one, else Keep), decision recorded in the summary. `--ask`: show diff between existing + proposed, ask "Update / Keep / Show diff".
- **Infrastructure-detail safety:** compliance docs MUST NOT embed hardcoded server addresses, internal endpoints, secret-management tool names, or proprietary internal tool names. Use placeholders (`{your-domain}`, `{DPA-contact-email}`, `{your-cloud-region}`). Disclosing internal infra in a public privacy policy is itself a security finding.

Generate from template (scan codebase for data flows, third-party SDKs, privacy configs, API patterns; fill every `{placeholder}` from verified source, never invent):

| Document | Template | Target |
|----------|----------|--------|
| Privacy Policy | [references/template-privacy-policy.md](references/template-privacy-policy.md) | `docs/compliance/privacy-policy.md` |
| DPIA | [references/template-dpia.md](references/template-dpia.md) | `docs/compliance/dpia.md` |
| Breach Notification Plan | [references/template-breach-notification.md](references/template-breach-notification.md) | `docs/compliance/breach-notification.md` |
| Processor Registry | [references/template-processor-registry.md](references/template-processor-registry.md) | `docs/compliance/processor-registry.md` |
| Store Privacy Labels | [references/template-store-privacy-labels.md](references/template-store-privacy-labels.md) | `docs/compliance/store-privacy-labels.md` |
| ToS / EULA | Service description; eligibility & account terms; license grants (free vs paid); payment terms (subscription/one-time/auto-renewal); cancellation & refund policy; acceptable use; disclaimer of warranties; limitation of liability; termination rights; governing law & dispute resolution; Privacy Policy cross-reference; Contact/DPO; version tracking. API/SaaS adds rate limits + SLA; mobile adds App Store SKU reference. | `docs/compliance/tos.md` |
| User FAQ | Grouped by topic (Getting Started, Account, Billing, Troubleshooting); each entry: question as a real user would phrase it + direct answer + link to the relevant walkthrough or support path if unresolved | `docs/user/FAQ.md` |
| Walkthrough outline | Goal (one sentence); numbered steps with screenshot/GIF placeholder per step, ≤60s-equivalent; expected result; "Still stuck?" link to the support contact path | `docs/user/{flow}.md`, one per top user flow |

DPIA, Breach Notification, and Processor Registry templates each carry their own dated Review Log section (DOC-20) — corrections tracked there, not restated here.

**Gate:** Every generated claim verified against source with file:line evidence. If fails → unverifiable claim → remove from generated doc, add `<!-- TODO: verify {claim} — source not found -->` at removed location, record scope `partial`, surface MEDIUM "unverified claim removed from {file}".

### Phase 6: Needs-Approval Review [needs_approval > 0]

Default: items resolve by best judgment (`fixed` or `failed`), recorded in the summary, except items matching the publish/irreversible exception list, which become `skipped (only you can do)`. `--ask`: present each item compactly (one line `[severity] title — file:line`) grouped by severity with counts, and state the question (`Approve these N items?`); ask Apply all / per-severity bulk (`Apply all HIGH` … alongside the total, CRITICAL bulk still confirms per item) / Review Each / Skip All. `approve-all` excludes CRITICAL; "all" = exactly the displayed set.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue to Summary; do not retry.

### Phase 7: Summary

Per-scope table `| Scope | Status | File | Lines |`, then:

`docs: {OK|WARN|FAIL} | Scopes: ran {a,b} · N/A — {c}={reason} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Total findings = 0 → include "All {n} scopes evaluated: 0 findings" confirmation. Distinguishes clean result from skipped analysis.

**Profile update:** ds-docs does NOT modify the blueprint profile — documentation dimension score is recalculated by ds-blueprint on next run. Run history is in `git log` + terminal summary — never re-injected into context-loaded files.

**Effect:** 1-5 concrete bullets, real changes only — each states what got better and why it matters, in plain language a non-technical reader understands (quantified when measurable), never the mechanical activity; they are the closing block's Effect line. Example shapes (placeholders, not literal output):

- `{n} doc-code drift findings closed — README claims now match actual source behavior`
- `API docs generated for {n} endpoints with examples — downstream consumers no longer reverse-engineer the contract`
- `{n} ADRs written for architectural decisions — future maintainers can read why, not just what`
- `CLAUDE.md trimmed {n}→{m} lines — cut code-derivable/generic content, kept only non-obvious conventions and gotchas`
- `Missing docs filled: {list-of-doc-types} — onboarding time for new contributors expected to drop noticeably`

Zero-finding run: `Documentation in sync with source — no drift detected`.

**Gate:** Summary + Effect emitted; every finding has a disposition; accounting verified. If fails → missing disposition → assign `skipped (accounting gap)`; re-emit summary as `WARN`; generated docs already on disk stand as the partial run's progress record — a re-run picks up from what exists.

## Quality Gates

- Every generated doc verified against source — no claims without file:line evidence
- Generated / cross-surface numbers come from the generator or a drift check — a hand-copied figure is a finding while it is still correct; access dates are written only for sources opened this run
- Only modify documentation files — never touch source code
- Generated docs match project's existing documentation style
- **Mechanical Done Gate:** resolve `{check-cmd}` once at setup — the ds-quality enforcement arm when installed, else the repo's doc checks (link checker, `markdownlint`, `typos`, a docs build such as `mkdocs build --strict` / `npm run docs:build`) from [../core/toolchains.md](../core/toolchains.md) when present; capture the baseline; re-run after each written doc batch and once in aggregate before reporting done. New red → fix (≤3 attempts, same command), then revert the offending file and record `reverted`; baseline red is reported red-at-baseline, never inherited; no doc tooling detectable → report the Verification-Infrastructure Gap and fall back to the source-verification gate above, never skip silently.
- W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered.
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. <!-- portable-only -->

## Error Recovery

| Situation | Action |
|-----------|--------|
| Source code contradicts existing documentation | Flag as drift, update doc to match code |
| Referenced file or function no longer exists | Flag as stale, suggest removal |
| Generated doc exceeds 500 lines (`wc -l`) or 5,000 words (`wc -w`) | Default: split at the next H2 boundary, recorded in the summary. `--ask`: ask user for structure preference. |
| Verify scope finds broken internal links | List all broken links with suggested fixes |
| Harness context file exceeds its vendor length budget (DOC-14) | Trim DOC-10–13 findings first; still over → propose split (nested per-directory files or path-scoped rules) |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No existing docs | Generate from scratch using source code analysis |
| Docs contradict code | Flag discrepancy, update doc to match code |
| Multilingual docs | Maintain only detected languages, warn about sync |
| No AI-harness context file present | Auto/Preview: skip silently (advisory, not a gap); `--scope=harness` explicitly requested → offer to generate a minimal starter from verified project commands/conventions only |

> **Completion Evidence — final gate (duplicate of the opening band by design):** Before the summary line, show the evidence for every gate that ran — command plus observed output; a phase with no visible output was not executed — execute it now. Report `done`/`OK` only with this evidence present; otherwise report `INCOMPLETE` plus what is missing. <!-- portable-only -->
