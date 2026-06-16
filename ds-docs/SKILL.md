---
name: ds-docs
description: Documentation gap analysis — identify missing docs and generate what is needed. Use when documentation is incomplete, or the user asks to write/improve README, API docs, or guides.
---

# /ds-docs

Documentation drifts from code the moment it's written. This skill detects the gaps, verifies claims against source code, and generates what's missing.

**Documentation Gap Analysis** — Identify missing docs, generate what's needed.

## Triggers

- User runs `/ds-docs`, asks to check, generate, or improve documentation, asks "what docs are missing" / "is the README up to date", or asks to verify documentation accuracy against source code

### Triggers — INVOKE / DON'T INVOKE

| INVOKE | DON'T INVOKE |
|---------|----------|
| "audit documentation gaps", "is README up to date" | "audit code quality" (→ ds-review) |
| "generate API docs from source" | "write marketing copy / landing page" (→ ds-market) |
| "verify docs against code (no drift)" | "test the documented examples" (→ ds-test) |
| "write ADR for this decision" | "research industry best practices" (→ ds-research) |

## Contract

- Every generated sentence must earn its place — no filler, marketing language, or obvious statements.
- Only generates/modifies documentation files — never touches source code.
- Verifies claims against actual source code before writing.
- Standalone. Uses blueprint profile or `ds/audit/findings.md` when available; own analysis when absent.
- FRC+DSC enforced.
- Pre-existing / out-of-scope errors detected during work are NOT skipped — fixed inline or escalated with concrete blocker.

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | Detect, analyze, generate all missing docs |
| `--preview` | Analyze gaps only, no generation |
| `--scope={x}` | Single scope: readme, api, dev, user, ops, changelog, compliance, adr, refine, verify |
| `--adr` | ADR mode: scan architecture decisions, propose/maintain numbered ADR files under `docs/adr/` |
| `--update` | Regenerate even if docs exist |
| `--force-approve` | Auto-apply needs_approval items (structural changes) |
| `--resume` | Resume from `ds/audit/docs.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present mode selection to the user.

## Scopes

| Scope | Target | Purpose |
|-------|--------|---------|
| readme | `README.md` | Project overview, quick start |
| api | `docs/api/`, `API.md` | Endpoint/function reference |
| dev | `CONTRIBUTING.md`, `docs/dev/` | Developer onboarding |
| user | `docs/user/`, `USAGE.md` | End-user guides |
| ops | `docs/ops/`, `DEPLOY.md` | Deployment, operations |
| changelog | `CHANGELOG.md` | Version history |
| compliance | `docs/compliance/` | Privacy policy, DPIA, breach plan, processor registry |
| adr | `docs/adr/` | Architecture Decision Records — numbered, with Context / Decision / Consequences |
| refine | Existing docs | UX/DX quality improvement |
| verify | Existing docs | Verify claims against source code |

### ADR scope (activated by `--adr` flag or when `adr` scope is explicitly selected)

**Structure + template:** `docs/adr/NNNN-{kebab-slug}.md`, sequential zero-padded numbering from `0001`:

```markdown
# ADR NNNN: {Title}
**Status:** proposed | accepted | deprecated | superseded-by NNNN
**Date:** YYYY-MM-DD
## Context
{One paragraph: forces at play — technical, political, social, project-level — that pressured this decision.}
## Decision
{One paragraph: the choice taken. Active voice. Specific.}
## Consequences
{Bullet list: positive + negative consequences, known and anticipated.}
```

**Operations (`--adr` mode):**

1. **Inventory:** list existing ADRs, verify numbering contiguous, flag any missing status/date/sections.
2. **Proposal candidates:** every Category B decision surfaced in recent `ds/audit/findings.md` runs (scope `ideal-gap`, `architecture`, `stack-fitness`) without a matching ADR → propose a draft ADR. User approves each before writing.
3. **Supersedence:** new ADR contradicting an earlier one cites superseded ADR; earlier ADR updated to `status: superseded-by NNNN`.
4. **No autonomous ADR writes.** Every new ADR is Category B — user approves title + draft before file creation.

## Delegation

**Owns:** docs, doc-drift, feature-documentation, adr (`--adr` mode) | **Delegates:** none | **Receives:** ds-blueprint → docs scope findings; ds-ship → Phase 4b; ds-repo → CONTRIBUTING / LICENSE content generation

## Execution Flow

Setup → Analysis → Gap Analysis → [Plan] → Generate → [Needs-Approval] → Summary

### Phase 0: Pre-flight [ALWAYS — never skip]

**IDU:** Profile → {Config.audience, Project Map, Type, Config.priorities}. Findings({docs}) → verify + use. Absent → own analysis. Findings file fresh → target specific gaps (skip own analysis for covered areas); stale or absent → run own full analysis.

**Gate:** IDU complete, findings loaded or own analysis planned. If fails → findings unreadable or stale `git_hash` → discard, proceed with own full analysis; profile absent → continue + note "no blueprint profile — using own analysis" in run header.

### Phase 1: Setup [SKIP if --auto]

**Recovery check:** DETECT `ds/audit/docs.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-check docs files being generated, discard stale inventory), skip `done` phases, announce `[DOC] Resuming from Phase {N}: {name}.` On Summary success, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start.

**State `data`:** `{ mode, scopes_selected, project_type, docs_inventory[{file, completeness}], gaps[], docs_generated[], verifications_done[] }`.

1. **Mode selection.** No flags → ask: Auto (detect + analyze + generate all) / Preview (analyze only) / Scoped (pick scopes).
2. **Scope selection.** Not Auto/Preview → ask: which areas (Core: readme+changelog / Technical: api+dev / User-facing: user+ops); how to handle existing (Fill gaps / Refine / Verify claims / Update all).

**Gate:** Mode and scope selected, or flags parsed. If fails → no response after two attempts → default Auto + all scopes; announce `[DOC] No selection received — defaulting to Auto mode, all scopes.`

### Phase 2: Analysis

Scan existing docs, detect project type, assess completeness. Apply quality rules from [references/rules-writing.md](references/rules-writing.md):

1. Search for doc files (`README.md`, `CONTRIBUTING.md`, `docs/*`, `CHANGELOG.md`, `API.md`, `DEPLOY.md`); per found doc, read + assess completeness (0-100%).
2. Detect project type from config files.
3. Check doc-sync: README drift, API signature mismatch, deprecated refs, broken links.

**Gate:** Project type detected + existing docs inventoried with completeness scores. If fails → undetermined type → prompt user "What type? (cli / library / api / web / mobile / desktop / monorepo / other)"; unreadable doc → record `{ file, completeness: 0, status: "unreadable" }`, continue inventory.

### Phase 3: Gap Analysis (ideal vs current)

Ideal docs by project type:

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

**Verify scope (doc vs code sync) — the most critical scope:** finds lies in documentation. For every testable claim, search source to confirm or deny.

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

**Verification process:** parse each doc into testable claims (every code block, table row, flag, path, number, link); per claim, search codebase for the referenced entity; classify:

| Result | Classification | Action |
|--------|---------------|--------|
| Claim matches source | Verified | Skip |
| Claim doesn't match source | **Drift** — doc outdated | HIGH, show diff |
| Claim references something that doesn't exist | **Stale** — feature/file removed | CRITICAL, suggest removal |
| Source has something doc doesn't mention | **Gap** — undocumented feature | MEDIUM, suggest adding |
| Link returns 404 or target heading missing | **Broken link** | HIGH |

Report table: `| # | Type (Drift/Stale/Gap/Broken) | Doc File:Line | Claim | Actual | Severity |`

**Minimum verification coverage:** ALL code blocks, ALL flag/option tables, ALL numbered step lists, ALL internal links. These are highest-drift-risk.

**Gate:** Gap analysis complete with severity-classified findings. If fails → unreadable source file referenced by a claim → record `{ type: "inconclusive", severity: "MEDIUM", reason: "source file unreadable" }`, re-read once before marking inconclusive; still fails → flag scope `inconclusive` in summary.

### Phase 4: Plan Review (skip if --auto)

Display plan (target files, sections, sources). Ask: Generate All / High Priority Only / Abort.

**Gate:** User approved plan or `--auto`. If fails → Abort → exit cleanly `docs: ABORTED | Generated: 0`; High Priority Only → update scopes_selected to HIGH/CRITICAL only, proceed.

### Phase 5: Generate Documentation (skip if --preview)

Principles: extract from code, don't invent — read source for actual signatures/endpoints/configs; brevity over verbosity — every sentence earns its place; scannable format — headers, bullets, tables, copy-pasteable commands; action-oriented — focus on what the reader needs to do. Source mandate: every documented flag, endpoint, or config value MUST be verified by searching source before inclusion.

**Compliance scope (when scope = compliance):**

- **Overwrite prevention:** target file exists → do NOT overwrite. Show diff between existing + proposed, ask "Update / Keep / Show diff".
- **Infrastructure-detail safety:** compliance docs MUST NOT embed hardcoded server addresses, internal endpoints, secret-management tool names, or proprietary internal tool names. Use placeholders (`{your-domain}`, `{DPA-contact-email}`, `{your-cloud-region}`). Disclosing internal infra in a public privacy policy is itself a security finding.

Compliance template structures (scan codebase for data flows, third-party SDKs, privacy configs, API patterns):

| Document | Sections (compact) |
|----------|--------------------|
| **Privacy Policy** | Who we are; Data collected (table: type / source / purpose); Data NOT collected; How data is used; Local storage; Server-side processing; Auth; Third-party services (table: service / entity / data shared / purpose); Data retention (table: type / period / deletion trigger); User rights (access, delete, export, revoke, portability); Children's privacy; International transfers; Security measures; Changes; Contact |
| **DPIA** | Processing description + data category table; Necessity & proportionality + legal basis table per framework; Risk matrix (ID / description / likelihood / severity / inherent risk) + mitigation table (risk ID / control / status / residual risk); Consultation record; Decision (approved/rejected + residual risk + review date max 12 months) |
| **Breach Notification Plan** | Scope; Regulatory timelines table (GDPR / KVKK / CCPA / LGPD / UK GDPR / PIPL / PIPA / PDPA — authority + user deadlines); Severity classification (P1/P2/P3/P4 with criteria + containment + notification timelines); 5-phase procedure (Detection → Containment → Authority Notification → User Notification → Remediation); Contact info; Review log |
| **Processor Registry** | Per-processor: service name, legal entity, location, data processed, data NOT processed, legal basis per framework, user control, DPA/SCC status + expiry, transfer mechanism, retention. Annual review checklist (active, DPA current, transfers valid, minimization, opt-out functional, retention aligned) |

**Gate:** Every generated claim verified against source with file:line evidence. If fails → unverifiable claim → remove from generated doc, add `<!-- TODO: verify {claim} — source not found -->` at removed location, record scope `partial`, surface MEDIUM "unverified claim removed from {file}".

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** Apply All / Review Each / Skip All. `approve-all` excludes CRITICAL.

**Gate:** All items resolved. If fails → unresolved → mark `skipped (no decision)`, continue to Summary; do not retry.

### Phase 7: Summary

Per-scope table `| Scope | Status | File | Lines |`, then:

`docs: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Total findings = 0 → include "All {n} scopes evaluated: 0 findings" confirmation. Distinguishes clean result from skipped analysis.

**Profile update:** ds-docs does NOT modify the blueprint profile — documentation dimension score is recalculated by ds-blueprint on next run. Run history is in `git log` + terminal summary — never re-injected into context-loaded files.

**Value Delivered:** 1-5 concrete bullets, real doc outcomes only. Example shapes (placeholders, not literal):

- `{n} doc-code drift findings closed — README claims now match actual source behavior`
- `API docs generated for {n} endpoints with examples — downstream consumers no longer reverse-engineer the contract`
- `{n} ADRs written for architectural decisions — future maintainers can read why, not just what`
- `Missing docs filled: {list-of-doc-types} — onboarding time for new contributors expected to drop noticeably`

Zero-finding run: `Documentation in sync with source — no drift detected`.

**Gate:** Summary + Value Delivered emitted; every finding has a disposition; accounting verified. If fails → missing disposition → assign `skipped (accounting gap)`; re-emit summary as `WARN`; do not delete `ds/audit/docs.json` so partial run is preserved for `--resume`.

## Quality Gates

- Every generated doc verified against source — no claims without file:line evidence
- Only modify documentation files — never touch source code
- Generated docs match project's existing documentation style
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/docs.json` updated per doc generated, gitignored, deleted on successful Summary. W10: defer detection to fresh `ds/audit/findings.md` — own scan only for scopes not covered. W11: every detected error gets a concrete disposition — pre-existing/out-of-scope is not a valid skip reason.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Source code contradicts existing documentation | Flag as drift, update doc to match code |
| Referenced file or function no longer exists | Flag as stale, suggest removal |
| Generated doc exceeds 500 lines (or 5,000 words) | Split into multiple files at next H2 boundary; ask user for structure preference |
| Verify scope finds broken internal links | List all broken links with suggested fixes |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No existing docs | Generate from scratch using source code analysis |
| Docs contradict code | Flag discrepancy, update doc to match code |
| Multilingual docs | Maintain only detected languages, warn about sync |
