# /ds-docs

Documentation drifts from code the moment it's written. This skill detects the gaps, verifies claims against source code, and generates what's missing.

**Documentation Gap Analysis** — Identify missing docs, generate what's needed.

## Triggers

- User runs `/ds-docs`
- User asks to check, generate, or improve documentation
- User asks "what docs are missing" or "is the README up to date"
- User asks to verify documentation accuracy against source code

## Contract

- Standalone. Uses blueprint profile or ds/audit/findings.md when available; own analysis when absent.
- FRC+DSC enforced.
- Every generated sentence must earn its place — no filler, marketing language, or obvious statements
- Only generates/modifies documentation files — never touches source code
- Verifies claims against actual source code before writing

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | Detect, analyze, generate all missing docs |
| `--preview` | Analyze gaps only, no generation |
| `--scope=X` | Single scope: readme, api, dev, user, ops, changelog, compliance, adr, refine, verify |
| `--adr` | ADR mode: scan architecture decisions, propose/maintain numbered ADR files under `docs/adr/` |
| `--update` | Regenerate even if docs exist |
| `--force-approve` | Auto-apply needs_approval items (structural changes) |
| `--resume` | Resume from `ds/audit/docs.json` without prompting |
| `--clean` | Delete existing state and start fresh |

Without flags: present mode selection to the user.

## Scopes

| Scope | Target | Purpose |
|-------|--------|---------|
| readme | README.md | Project overview, quick start |
| api | docs/api/, API.md | Endpoint/function reference |
| dev | CONTRIBUTING.md, docs/dev/ | Developer onboarding |
| user | docs/user/, USAGE.md | End-user guides |
| ops | docs/ops/, DEPLOY.md | Deployment, operations |
| changelog | CHANGELOG.md | Version history |
| compliance | docs/compliance/ | Privacy policy, DPIA, breach plan, processor registry |
| adr | docs/adr/ | Architecture Decision Records — numbered, with Context / Decision / Consequences |
| refine | Existing docs | UX/DX quality improvement |
| verify | Existing docs | Verify claims against source code |

### ADR scope (activated by `--adr` flag or when `adr` scope is explicitly selected)

**Structure:** `docs/adr/NNNN-{kebab-slug}.md` with sequential zero-padded numbering starting at `0001`.

**Template:**
```markdown
# ADR NNNN: {Title}

**Status:** proposed | accepted | deprecated | superseded-by NNNN
**Date:** YYYY-MM-DD

## Context
{One paragraph: the forces at play — technical, political, social, project-level — that pressured this decision.}

## Decision
{One paragraph: the choice taken. Active voice. Specific.}

## Consequences
{Bullet list: positive + negative consequences, both known and anticipated.}
```

**Operations (`--adr` mode):**

1. **Inventory:** list existing ADRs, verify numbering is contiguous, flag any with missing status / date / sections.
2. **Proposal candidates:** for every Category B decision surfaced in recent `ds/audit/findings.md` runs (scope `ideal-gap`, `architecture`, `stack-fitness`) without a matching ADR, propose a draft ADR. User approves each before writing.
3. **Supersedence:** when a new ADR contradicts an earlier one, the new ADR's status cites the superseded ADR and the earlier ADR is updated to `status: superseded-by NNNN`.
4. **No autonomous ADR writes.** Every new ADR is Category B — user approves title + draft content before the file is created.

## Delegation

**Owns:** docs, doc-drift, feature-documentation, adr (--adr mode) | **Delegates:** none | **Receives:** ds-blueprint → docs scope findings; ds-ship → Phase 4b; ds-repo → CONTRIBUTING / LICENSE content generation

## Execution Flow

Setup → Analysis → Gap Analysis → [Plan] → Generate → [Needs-Approval] → Summary

### Phase 0: Pre-flight [ALWAYS — never skip]

**Findings file check:** `ds/audit/findings.md` with fresh `git_hash` → read findings with `docs` scope. Use to target specific documentation gaps (skip own gap analysis for covered areas). No findings file or stale → run own full analysis.

**IDU:** Profile → {Config.audience, Project Map, Type, Config.priorities}. Findings({docs}) → verify + use. Absent → own analysis.

**Gate:** IDU complete, findings loaded or own analysis planned.

### Phase 1: Setup [SKIP if --auto]

**Recovery check:** DETECT `ds/audit/docs.json`. Absent + no `--resume` → fresh. Absent + `--resume` → warn, fresh. Present + `--clean` → delete, fresh. Present → READ, verify `git_hash` vs HEAD. Mismatch → prompt `Resume anyway? [Y/n]` (honor `--resume`). Resume → RE-VERIFY `in_progress` phase (re-check docs files that were being generated, discard stale inventory), skip `done` phases, announce `[DOC] Resuming from Phase {N}: {name}.` On successful Summary, delete state. Verify `ds/audit/*.json` in `.gitignore` on fresh start, append if missing.

**State `data` shape:** `{ mode, scopes_selected, project_type, docs_inventory[{file, completeness}], gaps[], docs_generated[], verifications_done[] }`.

1. **Mode selection.** No flags provided → ask user:
   - **Auto** — detect project type, analyze gaps, generate all missing docs
   - **Preview** — analyze gaps only, no generation
   - **Scoped** — pick specific scope(s): readme, api, dev, user, ops, changelog, refine, verify

3. **Scope selection.** Mode is not Auto/Preview → ask:
   - Which documentation areas to cover (Core: readme+changelog, Technical: api+dev, User-facing: user+ops)
   - How to handle existing docs (Fill gaps, Refine existing, Verify claims, Update all)

**Gate:** Mode and scope selected or flags parsed.

### Phase 2: Analysis

Scan existing docs, detect project type, assess completeness. Apply quality rules from [references/rules-writing.md](references/rules-writing.md):
1. Search for doc files (README.md, CONTRIBUTING.md, docs/*, CHANGELOG.md, API.md, DEPLOY.md)
2. Per found doc: read and assess completeness (0-100%)
3. Detect project type from config files
4. Check for doc-sync issues: README drift, API signature mismatch, deprecated refs, broken links

**Gate:** Project type detected and existing docs inventoried with completeness scores.

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

Missing docs = HIGH, incomplete (<70%) = MEDIUM.

**Refine scope:** Analyze for scannability, clarity, redundancy, conciseness.

**Verify scope (doc vs code sync):**

The verify scope is the most critical — it finds lies in documentation. For every testable claim in docs, search source code to confirm or deny.

**What to verify (exhaustive checklist):**

| Claim type | How to verify |
|-----------|--------------|
| CLI flags / arguments | Search source for flag definitions (argparse, cobra, clap, commander) |
| Function signatures | Search for function/method definition, compare params and return type |
| API endpoints | Search route definitions (express routes, FastAPI paths, controller annotations) |
| Config keys / env vars | Search for config reads (`process.env`, `os.environ`, config file parsers) |
| Code examples | Verify function names, params, return values match actual source |
| Default values | Search for default assignments in code |
| Version numbers | Compare doc versions with manifest/lockfile versions |
| Setup/install steps | Verify each command works (check referenced scripts/commands exist) |
| Feature descriptions | Search for feature implementation in code |
| Architecture claims | Verify patterns described match actual code structure |
| Performance claims | Verify benchmarks or metrics against actual implementation |
| Security claims | Verify stated security features exist in code |

**Verification process:**

1. Parse each doc file into testable claims (every code block, table row, flag, path, number, link)
2. Per claim, search codebase for referenced entity
3. Classify each finding:

| Result | Classification | Action |
|--------|---------------|--------|
| Claim matches source | Verified | Skip |
| Claim doesn't match source | **Drift** — doc is outdated | Flag as HIGH, show diff between doc claim and actual code |
| Claim references something that doesn't exist | **Stale** — feature/file was removed | Flag as CRITICAL, suggest removal |
| Source has something doc doesn't mention | **Gap** — undocumented feature | Flag as MEDIUM, suggest adding |
| Link returns 404 or target heading missing | **Broken link** | Flag as HIGH |

4. Report as table:

```
| # | Type  | Doc File:Line | Claim | Actual | Severity |
|---|-------|---------------|-------|--------|----------|
| {n} | {Drift/Stale/Gap/Broken} | {file}:{line} | {claim} | {actual} | {severity} |
```

**Minimum verification coverage:** ALL code blocks, ALL flag/option tables, ALL numbered step lists, ALL internal links. These are highest-drift-risk elements.

**Gate:** Gap analysis complete with severity-classified findings table.

### Phase 4: Plan Review (skip if --auto)

Display plan (target files, sections, sources). Ask: Generate All / High Priority Only / Abort.

**Gate:** User approved generation plan or --auto mode active.

### Phase 5: Generate Documentation (skip if --preview)

Generate missing docs following these principles:
1. Extract from code, don't invent — read source files for actual signatures/endpoints/configs
2. Brevity over verbosity — every sentence earns its place
3. Scannable format — headers, bullets, tables, copy-pasteable commands
4. Action-oriented — focus on what reader needs to do

Source mandate: every documented flag, endpoint, or config value MUST be verified by searching source before inclusion.

**Compliance scope templates (when scope = compliance):**

**Overwrite prevention:** Before generating any compliance document, check if target file already exists. Exists → do NOT overwrite — show diff between existing content and proposed content, ask: "Update existing / Keep existing / Show diff".

**Infrastructure-detail safety:** Compliance documents MUST NOT embed hardcoded server addresses, internal endpoints, secret-management tool names, or proprietary internal tool names. Use placeholders (`[your-domain]`, `[DPA-contact-email]`, `[your-cloud-region]`). Disclosure of internal infra in a public privacy policy is itself a security finding.

Generate compliance documents by scanning codebase for data flows, third-party SDKs, privacy configurations, and API patterns. Use these template structures:

1. **Privacy Policy** — Sections: Who we are, Data collected (table: data type / source / purpose), Data NOT collected, How data is used, Local storage, Server-side processing, Authentication, Third-party services (table: service / entity / data shared / purpose), Data retention (table: data type / retention period / deletion trigger), User rights (access, delete, export, revoke, portability), Children's privacy, International transfers, Security measures, Changes to policy, Contact
2. **DPIA** — Sections: Processing description + data category table, Necessity & proportionality + legal basis table per framework, Risk assessment matrix (ID / description / likelihood / severity / inherent risk) + mitigation table (risk ID / control / status / residual risk), Consultation record, Decision (approved/rejected + residual risk summary + review date max 12 months)
3. **Breach Notification Plan** — Sections: Scope, Regulatory timelines table (GDPR / KVKK / CCPA / LGPD / UK GDPR / PIPL / PIPA / PDPA with authority + user deadlines), Severity classification (P1 Critical / P2 High / P3 Medium / P4 Low with criteria + containment + notification timelines), 5-phase response procedure (Detection & Triage → Containment → Authority Notification → User Notification → Remediation), Contact information, Review log
4. **Processor Registry** — Per-processor entry: service name, legal entity, location, data processed, data NOT processed, legal basis per framework, user control mechanism, DPA/SCC status + expiry, transfer mechanism, retention policy. Annual review checklist (processors active, DPA current, transfers valid, minimization verified, opt-out functional, retention aligned)

**Gate:** Every generated claim verified against source code with file:line evidence.

### Phase 6: Needs-Approval Review [needs_approval > 0]

`--auto`: list and skip. `--force-approve`: apply all. **Interactive:** present with risk context, ask Apply All / Review Each / Skip All.

**Gate:** All needs_approval items resolved (applied → fixed/failed, declined → skipped).

### Phase 7: Summary

```
docs complete
=============
| Scope     | Status   | File            | Lines |
|-----------|----------|-----------------|-------|
| {scope}   | {status} | {file}          |   {n} |
| {scope}   | {status} | {file}          |   {n} |

Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}
```

`docs: {OK|WARN|FAIL} | Fixed: {n} | Skipped: {n} | Failed: {n} | Total: {n}`

Total findings = 0 → include "All {N} scopes evaluated: 0 findings" confirmation line in summary. Distinguishes clean result from skipped analysis.

**Profile update:** ds-docs does NOT modify the blueprint profile. The Documentation dimension score is recalculated by ds-blueprint on its next run. Run history is preserved in `git log` and the terminal summary above — never re-injected into context-loaded files.

**Gate:** Summary table rendered with fixed/skipped/failed/total counts. Every finding/action has a disposition. Accounting verified.

## Quality Gates

- Every generated doc verified against source code — no claims without file:line evidence
- Only modify documentation files — never touch source code
- Generated docs match project's existing documentation style
- W1: cite file:line, never assume. W2: check consumers after modify. W3: only task-required lines. W4: re-read after gap. W5: uncertain → lower severity. W6: verify all phases output. W7: dedup file:line. W8: no raw shell interpolation. W9: `ds/audit/docs.json` updated per doc generated, gitignored, deleted on successful Summary.

## Error Recovery

| Situation | Action |
|-----------|--------|
| Source code contradicts existing documentation | Flag as drift, update doc to match code |
| Referenced file or function no longer exists | Flag as stale, suggest removal |
| Doc generation exceeds reasonable size | Split into multiple files, ask user for structure preference |
| Verify scope finds broken internal links | List all broken links with suggested fixes |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No existing docs | Generate from scratch using source code analysis |
| Docs contradict code | Flag discrepancy, update doc to match code |
| Multilingual docs | Maintain only detected languages, warn about sync |
