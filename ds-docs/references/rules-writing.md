# Rules: Documentation Quality

| Section | Rules |
|---------|-------|
| **Structure & Content** | DOC-01 to DOC-04 (2 HIGH, 2 MEDIUM) |
| **Maintenance & Tools** | DOC-05 to DOC-09 (3 MEDIUM, 2 LOW) |
| **Harness Context Files** | DOC-10 to DOC-24 (1 CRITICAL, 4 HIGH, 7 MEDIUM, 3 LOW) |
| **Claim & Structure Discipline** | DOC-25 to DOC-26 (1 HIGH, 1 MEDIUM) |

## Structure & Content

### DOC-01 | HIGH | README Hook

**Detect:** README starts with project name, badge wall, feature list, or generic description ("A library for..."). First line describes what project is rather than why it matters.

**Fix:** Lead with pain-point statement or contrarian hook in 10 words or fewer. Follow with solution framing.

```markdown
<!-- Before -->
# MyTool
A CLI tool for managing Docker deployments with zero-config setup.

<!-- After -->
# MyTool
AI commits are vague and bundle unrelated changes.

MyTool analyzes your staged changes and generates atomic,
context-aware commit messages.
```

**Why:** Repos with compelling READMEs receive 4x more stars and 6x more contributors. First line determines whether a visitor reads further or bounces. Pain-point hook → immediate recognition and relevance.

**Source:** Launch research (rivereditor.com, GitHub analysis) — [launch research](https://github.com/sungurerdim/dev-skills/blob/main/docs/methodology/launch-research.md) Pattern 6

---

### DOC-02 | HIGH | Verified Code Examples

**Detect:** Code blocks in documentation contain snippets that have drifted from actual source code. Example output, function signatures, or API calls reference outdated implementations.

**Fix:** Verify every code block against current source. Prefer auto-generated documentation (OpenAPI for REST, TypeDoc for TypeScript, rustdoc for Rust, Sphinx for Python) to keep examples in sync with implementation. For manually written examples, include source file path as a comment.

```markdown
<!-- Include source reference for manual examples -->
```javascript
// From: src/config.ts#L42-L55
const config = loadConfig({ strict: true });
```
```

**Why:** Incorrect code examples waste developer time and erode trust. Auto-generated docs eliminate drift by construction.

---

### DOC-03 | MEDIUM | Quick Start in 5 Commands or Fewer

**Detect:** Getting started section requires more than 5 commands or more than 10 minutes for a new user to reach working state.

**Fix:** Reduce setup to minimum path: clone, install, run (3 commands ideal). Provide copy-paste blocks with expected output.

```markdown
## Quick Start

```bash
git clone https://github.com/user/project && cd project
npm install
npm start
# Server running at http://localhost:3000
```
```

Projects requiring configuration → provide sensible defaults or a setup script:

```bash
cp .env.example .env   # defaults work out of the box
npm install && npm start
```

**Why:** Every additional setup step loses a percentage of potential contributors. 10-minute threshold aligns with average attention span for evaluating a new tool.

**Source:** GitHub README best practices, launch research (Quick Start pattern)

---

### DOC-04 | MEDIUM | Scannable Format

**Detect:** Documentation sections contain more than 5 consecutive prose paragraphs without structural breaks (headings, tables, bullet lists, or code blocks).

**Fix:** Break dense prose into scannable elements:

- **Comparisons:** Use tables
- **Steps/procedures:** Use numbered lists
- **Options/features:** Use bullet lists
- **Concepts:** Use heading + 1-3 sentence summary + example

| Format | Use When |
|--------|----------|
| Table | Comparing 3+ items across 2+ dimensions |
| Bullet list | Enumerating items without priority |
| Numbered list | Sequential steps or ranked items |
| Code block | Any executable or configuration example |
| Heading | Every new concept or topic shift |

**Why:** Developers scan documentation; they rarely read linearly. Structured content reduces time-to-answer by 40-60% compared to prose walls.

**Source:** Nielsen Norman Group readability research, technical writing best practices

---

## Maintenance & Tools

### DOC-05 | MEDIUM | Link Freshness

**Detect:** Documentation contains links returning 404, pointing to moved pages, or referencing outdated URLs (e.g., old API versions, deprecated docs sites).

**Fix:** Verify all links resolve correctly. Use relative links for internal references (resilient to domain changes). For external links, prefer canonical URLs over blog posts or tutorials that may be removed.

```markdown
<!-- Prefer relative for internal -->
See [Configuration](./docs/config.md)

<!-- Prefer canonical for external -->
See [Express docs](https://expressjs.com/en/guide/routing.html)
```

Repo has a link checker configured (e.g., lychee) → run it and consume the report; suppress known false positives via `.lycheeignore` instead of loosening the check.

**Why:** Broken links signal unmaintained documentation and send users to dead ends. Single 404 in a getting-started guide can block adoption.

**Source:** Web maintenance best practices; lychee (lycheeverse)

---

### DOC-06 | MEDIUM | Auto-Generated API Documentation

**Detect:** API documentation manually written in a separate file, disconnected from source code. Changes to implementation require updating docs in a second location.

**Fix:** Use framework's canonical documentation generator:

| Stack | Tool | Source |
|-------|------|--------|
| REST API | OpenAPI/Swagger (auto-generate from routes) | openapis.org |
| GraphQL | Schema introspection + GraphiQL | graphql.org |
| TypeScript library | TypeDoc | typedoc.org |
| Rust library | rustdoc (built-in) | doc.rust-lang.org |
| Python library | Sphinx + autodoc | sphinx-doc.org |
| Go library | godoc (built-in) | pkg.go.dev |

**Why:** Manually maintained API docs inevitably drift from implementation. Auto-generation makes source code single source of truth.

**Source:** OpenAPI 3.1 specification, framework-specific documentation standards

---

### DOC-07 | LOW | Badge Discipline

**Detect:** README displays more than 7 badges, creating visual clutter that pushes actual content below the fold.

**Fix:** Keep 4-7 badges maximum. Prioritize actionable information:

| Keep | Remove |
|------|--------|
| Build/CI status | "PRs welcome" |
| Test coverage | "Made with love" |
| Latest version/release | Duplicate status badges |
| License | Platform badges that add no info |

**Why:** Badge walls create visual noise and delay reader from reaching content that determines whether they will use or contribute to project. Screenshots increase stars approximately 42%; excessive badges do opposite.

**Source:** Launch research (README best practices) — [launch research](https://github.com/sungurerdim/dev-skills/blob/main/docs/methodology/launch-research.md) Pattern 6

---

### DOC-08 | LOW | Changelog in Standard Format

**Detect:** No `CHANGELOG.md` file, or changelog exists in non-standard format (e.g., raw git log dumps, unstructured notes).

**Fix:** Follow Keep a Changelog format with sections for Added, Changed, Deprecated, Removed, Fixed, and Security. Auto-generate from conventional commits where project uses them.

```markdown
# Changelog

## [1.2.0] - 2026-03-15

### Added
- Health check endpoint with dependency verification

### Fixed
- SSL certificate renewal failing silently on Caddy restart

## [1.1.0] - 2026-02-28

### Changed
- Switched from Nginx to Caddy for automatic HTTPS
```

**Why:** Well-maintained changelog helps users decide whether to upgrade and understand breaking changes without reading commit history. Often first file checked before a version bump.

**Source:** Keep a Changelog (keepachangelog.com), Semantic Versioning

---

### DOC-09 | MEDIUM | Deterministic Doc-Lint Stack

**Detect:** Docs checked only by manual/LLM review — no prose linter (Vale), Markdown-structure linter (markdownlint), or link checker (lychee) configured in a repo that has a docs directory or CI.

**Fix:** Run the configured stack and consume its output; where absent, propose it as a needs-approval item — never install unasked:

| Tool | Checks | Severity mapping |
|------|--------|------------------|
| lychee | broken URLs, dead anchors | error — fails the check; `.lycheeignore` for known false positives |
| markdownlint | structure: bare code fences, heading order, missing image alt text | error |
| Vale | prose style: passive voice, sentence length, word choice | warning — advisory, never blocks |

**Why:** Deterministic linters catch drift that review misses and produce repeatable signals; the severity split keeps style suggestions from blocking at broken-link level.

**Source:** GitLab documentation testing guide (Vale + markdownlint); lychee (lycheeverse); documentation-linting severity practice 2026

---

## Harness Context Files

`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/`, `.windsurfrules`/`.devin/rules/`, `.github/copilot-instructions.md`, `GEMINI.md`, `CONVENTIONS.md` (Aider). These are re-injected as low-trust background context on every session, not read once like a README — signal density matters more than completeness. A file that only contains what the agent cannot derive on its own outperforms a comprehensive one.

### DOC-10 | CRITICAL | Secrets in Harness Context File

**Detect:** Hardcoded credentials, API keys, tokens, or connection strings with embedded passwords appear in the file body.

**Fix:** Remove immediately. Reference the variable by name only (`{ENV_VAR_NAME}`), never its value.

**Why:** These files are typically git-committed and re-sent to the model provider on every session — a secret placed here leaks on every future run, not just once.

**Source:** General secret-handling policy (no vendor documentation explicitly warns against this despite recommending the file be committed to git — treated as an inferred-but-undocumented risk, not a sourced vendor claim).

---

### DOC-11 | HIGH | Code-Derivable Content

**Detect:** Directory layout, dependency lists, file-by-file descriptions, or architecture overviews that duplicate what the agent discovers in seconds by reading the code.

**Fix:** Remove, or replace with a one-line pointer (`see src/` / `see package.json`). Verify the claim is genuinely derivable — read the actual file/directory before flagging — before cutting it.

```markdown
<!-- Before -->
## Project Structure
- src/api/ — REST route handlers
- src/db/ — database models
- src/utils/ — shared helpers

<!-- After -->
(section removed — agent reads the tree directly)
```

**Why:** This is exactly the boilerplate that dominates auto-generated context files. An 18-repo AgentBench study found LLM-generated context files cut task success 2–3% while raising inference cost 20%+; removing the project's existing docs made those same generated files useful again (+2.7%), pointing to derivable-content redundancy as the core failure mode.

**Source:** [Anthropic Claude Code best practices](https://code.claude.com/docs/en/best-practices) (✅/❌ table); [Cursor Rules docs](https://cursor.com/docs/rules); [Evaluating AGENTS.md, arXiv:2602.11988](https://arxiv.org/abs/2602.11988)

---

### DOC-12 | HIGH | Generic Self-Evident Advice

**Detect:** Instructions the model already follows from training or the harness's own defaults — "write clean code," "handle errors properly," "use meaningful variable names" with no project-specific specifics.

**Fix:** Delete. Do not replace with a project-specific version unless the project genuinely diverges from the default.

**Why:** This does not just waste tokens — it measurably degrades output. An independent 1,188-test benchmark across 3 models and 10 instruction profiles found an empty file was the best-performing configuration, with a −0.95 correlation between instruction token count and output quality; even a 4-bullet minimal profile scored below no instructions at all.

**Source:** [Anthropic best practices](https://code.claude.com/docs/en/best-practices); [Windsurf/Devin Cascade Memories docs](https://docs.devin.ai/desktop/cascade/memories) ("already baked into Cascade's training data"); independent 1,188-test community benchmark (single-sourced, directionally consistent with the peer-reviewed-adjacent AgentBench finding above)

---

### DOC-13 | MEDIUM | Pasted Reference Material

**Detect:** API documentation, tutorials, or frequently-changing detail (endpoint lists, config schemas) copied inline instead of linked.

**Fix:** Replace with a link to the canonical source (docs site, OpenAPI spec, source file).

**Why:** Pasted content goes stale the moment the source changes and bloats every session regardless of relevance to the current task.

**Source:** [Anthropic best practices](https://code.claude.com/docs/en/best-practices) ("Detailed API documentation (link to docs instead)"); [Cursor Rules docs](https://cursor.com/docs/rules) ("Reference files rather than copying their contents")

---

### DOC-14 | MEDIUM | Length Over Harness Budget

**Detect:** File exceeds the target harness's own adherence threshold.

| Harness | File | Budget |
|---------|------|--------|
| Claude Code | `CLAUDE.md` | <200 lines (warn; still loaded in full past this) |
| Claude Code | `MEMORY.md` (auto-memory) | first 200 lines / 25KB only auto-load |
| Cursor | `.cursor/rules/*.mdc` | <500 lines/file |
| Windsurf/Devin | `global_rules.md` | 6,000 chars (hard cap) |
| Windsurf/Devin | `.devin/rules/*.md` | 12,000 chars/file (risk of silent truncation past this) |
| Cross-harness | any | <300 lines — general consensus |

**Fix:** Cut DOC-10–DOC-13 findings first. Still over budget → split via nested per-directory files (monorepo pattern, DOC-17) or path-scoped/glob-conditional rules where the harness supports them (Cursor `globs`, Copilot `applyTo`, Windsurf glob-activation mode). Do **not** rely on `@path`/`@file.md` imports to reduce size — imported content is expanded and loaded in full at launch alongside the referencing file; imports organize, they do not shrink context.

**Why:** Claude Code's own docs state files over 200 lines "consume more context and may reduce adherence"; independent teams converge on shorter-is-better (HumanLayer's own production file is under 60 lines).

**Source:** [How Claude remembers your project](https://code.claude.com/docs/en/memory); [Cursor Rules docs](https://cursor.com/docs/rules); [Windsurf/Devin Cascade Memories docs](https://docs.devin.ai/desktop/cascade/memories); [Writing a good CLAUDE.md — HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)

---

### DOC-15 | MEDIUM | Missing Recommended Content

**Detect:** File lacks non-guessable build/test/lint commands, code-style rules that diverge from language/tool defaults, non-obvious gotchas or architecture rationale, or repo etiquette — despite the project clearly having them (custom scripts, non-default lint config, documented past incidents).

**Fix:** Add tersely, one line per item, each earning its place. Prefer a concrete before/after code example over an abstract rule statement.

**Why:** These are the categories every major harness's own docs recommend, and agents will actually execute listed test/build commands automatically.

**Source:** [Anthropic best practices](https://code.claude.com/docs/en/best-practices); [agents.md](https://agents.md/) ("the agent will attempt to execute relevant programmatic checks"); [Gemini CLI GEMINI.md docs](https://geminicli.com/docs/cli/gemini-md/); [Aider conventions docs](https://aider.chat/docs/usage/conventions.html)

---

### DOC-16 | LOW | Negative-Framed Instructions

**Detect:** A rule stated as a prohibition ("don't write unclear code") where a positive equivalent exists ("write clear code").

**Fix:** Rewrite as the positive action.

**Why:** Weak, single-sourced evidence of a measurable gap in favor of positive framing — kept at LOW severity pending independent replication.

**Source:** Independent community benchmark (single-sourced; not independently replicated)

---

### DOC-17 | LOW | Single Monolithic Root File in a Monorepo

**Detect:** One root context file covers multiple unrelated packages instead of nested per-package files.

**Fix:** Add a context file inside each package; the file closest to the working directory takes precedence, so package-specific content doesn't dilute the root file for unrelated work.

**Why:** Independently implemented by three harnesses as the standard monorepo pattern — OpenAI's own repo carries 88 nested `AGENTS.md` files.

**Source:** [agents.md](https://agents.md/); [How Claude remembers your project](https://code.claude.com/docs/en/memory) (nested `CLAUDE.md` discovery); [Gemini CLI GEMINI.md docs](https://geminicli.com/docs/cli/gemini-md/) (just-in-time directory scan)

---

### DOC-18 | HIGH | Structural Changes and Their Docs Land in the Same Commit

File moves/adds/deletes, renames, and dependency version bumps update the affected docs (README, architecture, main guide, design system) in the same change — doc truth is part of "done".

**Detect:** Docs claiming file counts, versions, paths, or module lists that no longer match the code; structural commits with no doc diff; doc updates tracked as separate "later" tasks.

**Fix:** Treat the doc update as part of the structural change's definition of done: the commit that moves/renames/bumps also fixes every doc claim it invalidates. ds-docs' drift detection is the safety net, not the mechanism.

**Why:** Same-commit coupling is the only doc-sync strategy that doesn't decay — every "update docs later" queue converges to permanently wrong docs.

**Source:** XR-014 — cross-project experience registry (2026).

---

### DOC-19 | HIGH | Cross-Repo Documents Keep One Canonical Copy; Others Become Pointers

In multi-repo products, every cross-cutting document (breach plan, DPIA, retention table) is canonical in exactly one repo; other repos hold a short pointer plus only their scope-specific notes.

**Detect:** The same policy/compliance document independently editable in two repos; copies that have already diverged; a "shared" doc with no designated canonical home.

**Fix:** Pick the canonical repo per document; convert every other copy into a pointer stub (link + repo-specific addenda only). Two independently-editable copies of regulatory content are never left standing.

**Why:** Diverged compliance copies mean the org provably follows at most one of them — and in an audit, the divergence itself is the finding.

**Source:** XR-015 — cross-project experience registry (2026).

---

### DOC-20 | MEDIUM | Living Compliance Docs Correct Through a Dated Review Log

Regularly reviewed compliance documents (DPIA, security policy, breach plan) record corrections in a dated review-log section — what changed, when, and what triggered it — instead of silently overwriting past errors.

**Detect:** Compliance docs whose history exists only in git (invisible to auditors reading the doc); errors fixed in place with no trace; no review-log section.

**Fix:** Maintain a dated Review Log section per living compliance doc: date, what was corrected, trigger (code audit, doc-drift check, new decision). The document's accuracy history stays auditable and defensible on its face.

**Why:** A silently-corrected compliance doc can't demonstrate it was ever reviewed — the review log is what turns "we fixed it" into evidence of a working review process.

**Source:** XR-016 — cross-project experience registry (2026); complements the Breach Plan template's Review log section.

---

### DOC-21 | MEDIUM | Evidence-Based Decisions Are Locked; Reopening Requires New Evidence

Engineering decisions grounded in measurement or experiment (model parameter, dependency version, a deliberately removed security/resilience layer) live in a decision ledger tagged "not to be revisited without new evidence", citing the triggering measurement.

**Detect:** Measured decisions re-litigated on preference; a deliberately removed control re-added by a later audit that didn't know the removal was deliberate; decision records with no reference to the evidence that drove them.

**Fix:** Record each evidence-based decision with its measurement/incident reference and an explicit reopening condition (new measured evidence, real threat-model change). Automated and human reviews route around locked decisions instead of re-flagging the same deliberate trade-off.

**Why:** Without decision locks, every audit cycle re-fights settled questions — and eventually someone "fixes" a deliberate removal back in, un-measuring a measured system.

**Source:** XR-017 — cross-project experience registry (2026); pairs with ADR supersedence.

---

### DOC-22 | MEDIUM | Accepted Debt Is Tracked With ID, Reason, and Fix Path

Deliberately deferred architectural gaps are recorded openly: short ID, what's missing, why not fixed now, and the fix path.

**Detect:** Known gaps living in team memory or code comments; the next review re-discovering and re-debating an already-accepted trade-off as a "new finding"; debt entries without a fix path.

**Fix:** Register each accepted gap with an ID, the missing piece, the deferral rationale, and the concrete fix path; reviews cite the existing acceptance record instead of reopening it. Silent accumulation is the failure mode this kills.

**Why:** Untracked debt is re-discovered at the worst time (incident, audit, onboarding) and re-debated from scratch; tracked debt is a managed queue with prices attached.

**Source:** XR-018 — cross-project experience registry (2026).

---

### DOC-23 | MEDIUM | Numeric Claims Trace to a Reproducible Measurement Artifact

Every quality/performance claim (accuracy, latency, size) is backed by a re-runnable measurement script and the raw log/record it produced, both kept in the repo.

**Detect:** Docs stating numbers with no script that reproduces them; measurement logs lost to chat threads; claims that survive pipeline changes unre-measured.

**Fix:** Pair every reported number with (1) the measurement script and (2) its raw output artifact, stored as repo sources; every documented figure must trace to that artifact. Re-run on relevant changes — this is Measure-Before-Optimize applied to documentation.

**Why:** Untraceable numbers rot into marketing fiction; traceable ones let anyone — including future-you — re-verify the claim in one command.

**Source:** XR-093 — cross-project experience registry (2026).

---

### DOC-24 | LOW | Third-Party Names Vendor-Neutral in Customer Copy; Re-Verified Against the Live Pipeline

Customer-facing text describes third-party models/libraries in vendor-neutral, function-accurate terms, and the copy is periodically re-verified against the current pipeline.

**Detect:** Customer copy naming specific vendors/models that the pipeline may swap; descriptions accurate at writing time but stale against the current implementation; no re-verification trigger on pipeline changes.

**Fix:** Describe components by function ("speech-to-text engine", not the vendor's product name) unless the vendor name is contractual; re-verify the description against the actual current pipeline on a schedule and on every pipeline swap.

**Why:** Vendor-named copy goes false the day the pipeline swaps suppliers — turning an implementation detail into a public misstatement.

**Source:** XR-184 — cross-project experience registry (2026).

### DOC-25 | HIGH | Absence Claims Require a Proven-Positive Control Query

A claim that something does not exist is only valid when the search that found nothing is itself proven to work.

**Detect:** An assertion of absence ("no such function", "unused anywhere", "not implemented", "no rule covers this") resting on a search that returned zero results, with no evidence the query, flags, or path scope were correct. Zero-result searches reported as findings without a companion query that returned hits.

**Fix:** Before asserting absence, run a control query against the same corpus with the same tool and flags that is guaranteed to return hits. Control returns nothing → the search is broken, not the subject; fix the query and re-run. Record both queries alongside the claim so a reader can re-verify.

**Why:** An empty result is ambiguous — the thing is absent, or the query is malformed (a wrong escape, a bad path filter, a case-sensitivity default). Acting on the wrong branch deletes live code or invents missing features that already ship.

**Source:** XR-203 — cross-project experience registry (2026).

### DOC-26 | MEDIUM | Machine-Read Corpora Keep One Structural Convention Across Sibling Files

Every file in a corpus that tooling parses uses the same heading level and entry shape for the same kind of entry.

**Detect:** Sibling files under one corpus using different heading depths (`##` vs `###`) or different entry formats for equivalent entries; a parser that needs per-file special-casing to read the set; extraction counts that disagree with a manual count for one file only.

**Fix:** Pin one structural convention per corpus and state it in the corpus README; add a structural lint that fails when a sibling deviates. Parsers key on the pinned convention and never guess per file.

**Why:** A single deviating file silently drops all of its entries from every extraction, and nothing errors — the corpus looks complete while every downstream count, audit, and report reads a subset.

**Source:** XR-204 — cross-project experience registry (2026).
