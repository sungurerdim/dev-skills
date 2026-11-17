# Docs — README, accuracy, changelog, agent context files

Applies to every project. Every claim a doc makes is checked against the code; the same passage kept in two places is SIM-06.

### DOC-01 [HIGH] README does not say what it is or how to start
- **Detect:** no README; a first screen opening with badges, a feature list or a generic line instead of the problem the project solves; no install-and-run path, or more than about 5 commands to a first success; no proof (screenshot, output, example) where one applies; stale badges (a CI that no longer runs, DOP-01) or so many that the content starts below the fold.
- **Mech:** T `git ls-files -z 'README*' | xargs -0 head -n 30`
- **Fixture:** hit `README.md: # Tool\nDoes one thing.` · miss `docs/guide.md: Not the readme.`
- **Fix:** one-line problem and what the project does → proof → quick start (copy-paste commands with expected output; defaults or an `.env.example` so it runs unconfigured) → links to deeper docs; keep only badges a reader acts on (version, licence, a CI that runs).
- **Impact:** visitors leave before they learn what it does; new users stall in setup.
- **Source:** GitHub Docs, About READMEs; Diátaxis (tutorials).

### DOC-02 [HIGH] Docs claim what the code no longer does
- **Detect:** every testable claim — command, flag, path, config key, env var, default, endpoint, signature, version, code example, feature, security or performance statement — checked against the code and classed `Drift` (differs; HIGH), `Stale` (names what no longer exists; CRITICAL, asserted only after a control query on the same corpus with the same tool and flags returns hits, so the empty search proves absence and not a broken query) or `Gap` (shipped behaviour no doc mentions; MEDIUM); moves, renames, deletions and version bumps since {base} whose docs did not change in the same commit. Code blocks, flag tables, numbered steps and internal links first: they drift most. ds-audit's promise census calls Drift and Stale `promised-not-implemented` and Gap `implemented-not-documented`.
- **Mech:** T `git diff --name-status {base} -- ':!*.md' | grep -E '^(R|D)'` · `git grep -nE '^[[:space:]]*(\$ |npm (run )?|npx |make |python3? |\./|cargo |go run )' -- '*.md'`
- **Fixture:** history
- **Fix:** fix the doc in the same commit as the change; replace a copied fact (version, default, port) with a reference to its owning file or command; generate reference docs where the stack has a generator (DOC-06).
- **Impact:** a wrong doc costs more than none: readers and agents act on it.
- **Source:** Write the Docs, Docs as Code; kernel §3 (evidence).

### DOC-23 [MEDIUM] Number or date in a doc with nothing keeping it true
- **Detect:** a number a tool produces (counts, coverage, sizes, benchmark results, accuracy) or that also lives on another surface (config, UI, site, store listing), written by hand with no generator and no drift check; a figure with no re-runnable measurement script and raw output in the repo; an access or "last verified" date on a source nobody opened in that change.
- **Mech:** T `git grep -nE '[0-9]+ (tests|rules|checks|files|steps)|[0-9]+(\.[0-9]+)?% (coverage|faster|smaller|fewer)' -- '*.md'`
- **Fixture:** hit `README.md: Runs 42 checks in 3 seconds.` · miss `docs/a.md: Runs every check.`
- **Fix:** emit the number from its generator at build time, or keep the hand copy under a check that fails when its source moves; keep the measurement script and its raw output beside the claim; write a verification date only for a source opened in that change.
- **Impact:** correct today, silently wrong after the next change, and nobody can re-check it.
- **Source:** DRY / single source of truth; SIM-06 (single source of truth); The Turing Way, Reproducible research.

### DOC-05 [MEDIUM] Broken links and unlinted docs
- **Detect:** internal links to missing files or anchors; external links that fail (`lychee .`, network); a repo with a docs directory and no link checker or Markdown linter in the gate.
- **Mech:** T `lychee --offline --no-progress '**/*.md'` · `markdownlint-cli2 '**/*.md' '#node_modules'`
- **Fixture:** none · needs lychee or markdownlint-cli2
- **Fix:** relative links for internal targets, canonical URLs for external ones; lychee and markdownlint in the gate with `.lycheeignore` for known false positives; Vale for prose style, advisory only.
- **Impact:** a dead link on the getting-started path blocks adoption; unlinted structure drifts.
- **Source:** lychee; markdownlint; Vale; GitLab Docs, Documentation testing.

### DOC-06 [MEDIUM] API reference written by hand beside the code
applies_when: api≠none or platforms∋library
- **Detect:** endpoint or public-API docs maintained in a separate file while the stack has a generator.
- **Mech:** T `git ls-files | grep -iE '(^|/)(openapi|swagger)[^/]*\.(ya?ml|json)$|(^|/)(typedoc\.json|mkdocs\.yml|docs/conf\.py)$'`
- **Fixture:** hit `api/openapi.yaml: openapi: 3.1.0` · miss `api/notes.yaml: x: 1`
- **Fix:** generate it: OpenAPI from routes, GraphQL introspection, TypeDoc, rustdoc, Sphinx autodoc, godoc, dartdoc.
- **Impact:** a hand-kept reference drifts from the implementation with every change.
- **Source:** DRY / single source of truth; OpenAPI Specification 3.1; each stack's documentation generator.

### DOC-08 [LOW] No changelog a user can read
- **Detect:** a released project with no changelog, or one that is a raw git log instead of versioned sections (Added, Changed, Deprecated, Removed, Fixed, Security) under `## [x.y.z] - YYYY-MM-DD`. Agreement with tags is DOP-48.
- **Mech:** T `git ls-files | grep -qiE '^(CHANGELOG|CHANGES|HISTORY|NEWS)(\.md)?$' || echo 'no changelog tracked'` · `git grep -nE '^## ' -- CHANGELOG.md`
- **Fixture:** says `no changelog tracked` · miss `docs/history-notes.txt: later` · quiet `CHANGELOG.md: ## [1.0.0]`
- **Fix:** Keep a Changelog sections with an Unreleased block on top, written per change or generated from Conventional Commits (DOP-04).
- **Impact:** users cannot tell whether an upgrade is safe without reading commits.
- **Source:** Keep a Changelog 1.1.0; Semantic Versioning 2.0.0.

### DOC-27 [HIGH] Docs the project type needs are missing
- **Detect:** by signal: `platforms∋cli` without `--help` text covering every command and flag; `platforms∋library` without a public-API reference and a versioning statement; `api≠none` without a reference (DOC-06) and an auth and error guide; `ui≠none` without help reachable from the product and a support contact; a deployed service without the runbook of DEP-33.
- **Mech:** T `git ls-files | grep -iE '(^|/)(docs?|man|help)/|(^|/)(FAQ|SUPPORT|USAGE|RUNBOOK)[^/]*$'`
- **Fixture:** hit `docs/usage.md: How to use.` · miss `src/main.py: print(1)`
- **Fix:** add the missing page at the size the project needs, linked from the README.
- **Impact:** users and operators cannot use or run what they cannot find out about.
- **Source:** Diátaxis (tutorials, how-to guides, reference, explanation); GitHub Docs, Adding support resources to your project.

## Agent context files

`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/*.mdc`, `.windsurfrules`, `.devin/rules/*.md`, `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `CONVENTIONS.md` (Aider), root and nested. They are re-sent with every session, so signal density beats completeness. An edit to one steers every later session: it is Category B, applied with a one-line reason per cut or addition. None present → note it; write one only when asked, from verified commands. Secrets in them are SEC-01.

### DOC-11 [HIGH] Context file repeats what the agent can derive or already does
- **Detect:** directory layouts, dependency lists, file-by-file descriptions or architecture overviews the agent reads from the code in seconds; generic advice the model follows anyway ("write clean code", "handle errors properly"); pasted API docs, schemas or tutorials instead of links. Read the file or directory a passage describes before flagging it as derivable; unconfirmed → not a finding.
- **Mech:** T `git grep -nE '^#+ .*(Structure|Layout|Director|Tech Stack|Dependencies|Overview)' -- '*CLAUDE.md' '*AGENTS.md' '*GEMINI.md' '.github/copilot-instructions.md' '.cursor/rules/*'`
- **Fixture:** hit `AGENTS.md: ## Project Structure` · miss `CLAUDE.md: ## Commands`
- **Fix:** delete it, or replace it with a one-line pointer (`see package.json`, a docs URL).
- **Impact:** measured: generated and overview-heavy context files lowered task success and raised inference cost by over 20%; generic instructions degrade output, not only waste tokens.
- **Source:** DRY / single source of truth; "Evaluating AGENTS.md" (arXiv:2602.11988); Anthropic, Claude Code best practices; Cursor Docs, Rules.

### DOC-14 [MEDIUM] Context file over its harness budget
- **Detect:** a file over its harness's budget — Claude Code `CLAUDE.md` 200 lines; a Cursor rule file 500 lines; Windsurf/Devin global rules 6,000 characters, a workspace rule file 12,000; about 300 lines elsewhere — or one root file covering several unrelated packages of a monorepo.
- **Mech:** T `git ls-files -z '*CLAUDE.md' '*AGENTS.md' '*GEMINI.md' '.cursor/rules/*' '.devin/rules/*' '.windsurfrules' '.github/copilot-instructions.md' | xargs -0 wc -lc`
- **Fixture:** hit `AGENTS.md: Run make test.` · miss `README.md: Not an agent file.`
- **Fix:** cut DOC-11 content first; then nested per-package files (the nearest one wins) or path-scoped rules (Cursor `globs`, Copilot `applyTo`); `@path` imports organize but still load in full.
- **Impact:** past the budget adherence drops, or the harness truncates silently.
- **Source:** Anthropic, How Claude remembers your project; Cursor Docs, Rules; Devin Docs, Cascade memories; agents.md (nested files).

### DOC-15 [MEDIUM] Context file lacks what only the project knows
- **Detect:** no non-guessable build, test or lint command; no style rule that differs from tool defaults; no non-obvious gotcha or rationale; no repo etiquette; no intent and hard limits (whom it serves, what a change must never do) — while the project clearly has them (custom scripts, non-default lint config, documented incidents).
- **Mech:** M (compare the file with package scripts, Makefile, lint config and incident notes)
- **Fix:** one terse line each, a before/after example over an abstract rule; intent and hard limits come from a person: propose them from evidence as `only you can do: confirm`, never write them as settled.
- **Impact:** agents run listed commands automatically; context files help mainly through such non-standard requirements.
- **Source:** agents.md; Anthropic, Claude Code best practices; "Evaluating AGENTS.md" (arXiv:2602.11988).
