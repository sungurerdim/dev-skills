# Rules: Documentation Quality

| Section | Rules |
|---------|-------|
| **Structure & Content** | DOC-01 to DOC-04 (2 HIGH, 2 MEDIUM) |
| **Maintenance & Tools** | DOC-05 to DOC-09 (3 MEDIUM, 2 LOW) |
| **Harness Context Files** | DOC-10 to DOC-17 (1 CRITICAL, 3 HIGH, 3 MEDIUM, 2 LOW) |

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

**Source:** Launch research (rivereditor.com, GitHub analysis) — [references/launch-research.md](https://github.com/sungurerdim/dev-skills/blob/main/references/launch-research.md) Pattern 6

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

**Source:** Launch research (README best practices) — [references/launch-research.md](https://github.com/sungurerdim/dev-skills/blob/main/references/launch-research.md) Pattern 6

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
