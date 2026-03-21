# /ds-docs

**Documentation Gap Analysis** — Identify missing docs, generate what's needed.

## Triggers

- User runs `/ds-docs`
- User asks to check, generate, or improve documentation
- User asks "what docs are missing" or "is the README up to date"
- User asks to verify documentation accuracy against source code

## Contract

- Fully functional standalone. When `.findings.md` exists with fresh data, uses it to skip redundant analysis.
- Every generated sentence must earn its place — no filler, marketing language, or obvious statements
- Only generates/modifies documentation files — never touches source code
- Verifies claims against actual source code before writing

## Arguments

| Flag | Effect |
|------|--------|
| `--auto` | Detect, analyze, generate all missing docs |
| `--preview` | Analyze gaps only, no generation |
| `--scope=X` | Single scope: readme, api, dev, user, ops, changelog, refine, verify |
| `--update` | Regenerate even if docs exist |
| `--force-approve` | Auto-apply needs_approval items (structural changes) |

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
| refine | Existing docs | UX/DX quality improvement |
| verify | Existing docs | Verify claims against source code |

## Execution Flow

Setup → Analysis → Gap Analysis → [Plan] → Generate → Summary

### Phase 1: Setup [SKIP if --auto]

**Findings file check:** If `.findings.md` exists with fresh `git_hash`, read findings with `docs` scope. Use them to target specific documentation gaps (skip own gap analysis for covered areas). If no findings file or stale, run own full analysis.

Recovery check: if progress artifact exists from prior run, ask: Resume / Start fresh.

1. **Mode selection.** If no flags provided, ask the user:
   - **Auto** — detect project type, analyze gaps, generate all missing docs
   - **Preview** — analyze gaps only, no generation
   - **Scoped** — pick specific scope(s): readme, api, dev, user, ops, changelog, refine, verify

2. **Scope selection.** If mode is not Auto/Preview, ask:
   - Which documentation areas to cover (Core: readme+changelog, Technical: api+dev, User-facing: user+ops)
   - How to handle existing docs (Fill gaps, Refine existing, Verify claims, Update all)

### Phase 2: Analysis

Scan existing docs, detect project type, assess completeness:
1. Search for doc files (README.md, CONTRIBUTING.md, docs/*, CHANGELOG.md, API.md, DEPLOY.md)
2. For each found doc: read and assess completeness (0-100%)
3. Detect project type from config files
4. Check for doc-sync issues: README drift, API signature mismatch, deprecated refs, broken links

### Phase 3: Gap Analysis (ideal vs current)

Ideal docs by project type:

| Type | README | API | Dev | User | Ops | Changelog |
|------|--------|-----|-----|------|-----|-----------|
| cli | Full | - | Basic | Full (man/help) | - | Yes |
| library | Full | Full | Full | Guides | Publish | Yes |
| api | Full | Full | Full | Full | Full | Yes |
| web | Full | Components | Full | Basic | Full | Yes |
| mobile | Full | - | Full | Store listing | Full | Yes |
| desktop | Full | - | Full | Full | Full | Yes |
| monorepo | Full | Per-package | Full | Per-package | Full | Yes |
| iac | Full | - | Full | Runbook | Full | Yes |
| devtool | Full | Full | Full | Full | - | Yes |
| data | Full | Schema | Full | Pipeline guide | Full | Yes |
| ml | Full | Model card | Full | Inference guide | Full | Yes |
| embedded | Full | HW interface | Full | Setup guide | Flash guide | Yes |
| game | Full | - | Full | Player guide | - | Yes |
| extension | Full | API/hooks | Full | Marketplace | Publish | Yes |

Missing docs = HIGH, incomplete (<70%) = MEDIUM.

**Refine scope:** Analyze for scannability, clarity, redundancy, conciseness.

**Verify scope (doc ↔ code sync):**

The verify scope is the most critical — it finds lies in documentation. For every testable claim in docs, search the source code to confirm or deny.

**What to verify (exhaustive checklist):**

| Claim type | How to verify | Example mismatch |
|-----------|--------------|------------------|
| CLI flags / arguments | Search source for flag definitions (argparse, cobra, clap, commander) | Doc says `--verbose`, code only has `--debug` |
| Function signatures | Search for function/method definition, compare params and return type | Doc shows `createUser(name, email)`, code has `createUser(name, email, role)` |
| API endpoints | Search route definitions (express routes, FastAPI paths, controller annotations) | Doc says `POST /api/users`, code has `POST /api/v2/users` |
| Config keys / env vars | Search for config reads (`process.env`, `os.environ`, config file parsers) | Doc says `DATABASE_URL`, code reads `DB_CONNECTION_STRING` |
| File paths / directory structure | Verify directories and files actually exist | Doc says "see `src/utils/`", directory doesn't exist |
| Import paths / package names | Verify package exists in manifest and export exists | Doc says `import { foo } from 'bar'`, package not in deps |
| Code examples | Verify function names, params, return values match actual source | Doc example uses old API that was refactored |
| Default values | Search for default assignments in code | Doc says "defaults to 3000", code defaults to 8080 |
| Version numbers | Compare doc versions with manifest/lockfile versions | Doc says "requires Node 16+", package.json says `>=18` |
| Step counts / numbered lists | Verify each step is still accurate and in correct order | "Step 3: Run migrate" — migrate command was renamed |
| Links (internal) | Verify target file/heading exists | `[See API docs](docs/api.md)` — file was deleted |
| Links (external) | Check URL accessibility (HEAD request, check for 404) | Link to deprecated library docs returns 404 |
| Feature descriptions | Search for feature implementation in code | Doc describes "real-time sync" but feature was removed |
| Error messages | Search for error strings in code | Doc says "Error: Invalid token", code says "Error: Token expired" |
| Dependency versions | Compare versions in docs vs manifest/lockfile | Doc says "requires React 18", package.json has `"react": "^19.0"` |
| Architecture claims | Verify patterns described match actual code structure | Doc says "Clean Architecture with 3 layers", code has no layer separation |
| Technology choices | Verify stated tech stack matches actual dependencies | Doc says "Built with Express", code uses Fastify |
| Setup/install steps | Verify each command works (check referenced scripts/commands exist) | Doc says `npm run setup`, script doesn't exist in package.json |
| Performance claims | Verify benchmarks or metrics against actual implementation | Doc claims "sub-100ms response", no caching or optimization in code |
| Security claims | Verify stated security features exist in code | Doc says "end-to-end encryption", no encryption implementation found |

**Verification process:**

1. Parse each doc file into testable claims (every code block, table row, flag, path, number, link)
2. For each claim, search the codebase for the referenced entity
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
| 1 | Drift | README.md:42  | `--port 3000` | Code defaults to 8080 | HIGH |
| 2 | Stale | API.md:15     | `GET /users/:id` | Endpoint removed in v2 | CRITICAL |
| 3 | Gap   | (missing)     | — | `POST /webhooks` undocumented | MEDIUM |
| 4 | Broken| README.md:88  | Link to wiki page | Returns 404 | HIGH |
```

**Minimum verification coverage:** ALL code blocks, ALL flag/option tables, ALL numbered step lists, ALL internal links. These are the highest-drift-risk elements.

### Phase 4: Plan Review (skip if --auto)

Display plan (target files, sections, sources). Ask: Generate All / High Priority Only / Abort.

### Phase 5: Generate Documentation (skip if --preview)

Generate missing docs following these principles:
1. Extract from code, don't invent — read source files for actual signatures/endpoints/configs
2. Brevity over verbosity — every sentence earns its place
3. Scannable format — headers, bullets, tables, copy-pasteable commands
4. Action-oriented — focus on what reader needs to do

Source mandate: every documented flag, endpoint, or config value MUST be verified by searching the source before inclusion.

### Phase 6: Summary

```
docs complete
=============
| Scope     | Status   | File            | Lines |
|-----------|----------|-----------------|-------|
| readme    | Updated  | README.md       |   +12 |
| api       | Created  | docs/api.md     |    85 |

Applied: 2 | Failed: 0 | Total: 2
```

`docs: {OK|WARN|FAIL} | Applied: N | Failed: N | Total: N`

## Quality Gates

- Every generated doc verified against source code — no claims without file:line evidence
- Only modify documentation files — never touch source code
- Generated docs match project's existing documentation style

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No existing docs | Generate from scratch using source code analysis |
| Docs contradict code | Flag discrepancy, update doc to match code |
| Multilingual docs | Maintain only detected languages, warn about sync |

