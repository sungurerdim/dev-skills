# Reference: Harness Scope

Consumer: ds-docs `harness` scope, activated by `--scope=harness` or when `harness` scope is explicitly selected.

**Target files:** `CLAUDE.md`, `AGENTS.md`, `.cursor/rules/*.mdc`, `.windsurfrules`/`.devin/rules/*.md`, `.github/copilot-instructions.md` + `.github/instructions/*.instructions.md`, `GEMINI.md`, `CONVENTIONS.md` (Aider) — root file plus every nested per-package file in a monorepo.

These files are re-injected into every session as low-trust background context, not read once like a README — signal density matters more than completeness. Apply rules from [rules-writing.md](rules-writing.md) DOC-10 to DOC-17.

## Operations

1. **Inventory:** find every target file present (root + nested). None present → record as advisory gap, do not fabricate one unless the user explicitly requested `harness` scope with no existing file (then generate a minimal starter from verified project commands/conventions only, per Phase 5).
2. **Classify content, line by line:**

   | Category | Verdict | Rule |
   |----------|---------|------|
   | Non-guessable commands, style rules diverging from tool defaults, non-obvious gotchas/rationale, repo etiquette | Keep — flag as gap if missing and the project clearly has one | DOC-15 |
   | Directory layout, dependency lists, file-by-file descriptions, architecture overviews | Cut — agent derives this by reading code | DOC-11 |
   | Generic/self-evident advice ("write clean code") | Cut — measurably degrades output, not just wasted tokens | DOC-12 |
   | Pasted API docs, long tutorials, frequently-changing detail | Replace with a link | DOC-13 |
   | Secrets, credentials, API keys, tokens | Cut immediately | DOC-10 (CRITICAL) |
   | Negative-framed rule with a positive equivalent | Rewrite positive | DOC-16 |
3. **Verify before flagging DOC-11:** read the actual file/directory the content claims to describe — confirm it is genuinely derivable before reporting. Unconfirmed → do not flag.
4. **Length check (DOC-14):** measure with `wc -l` (line budgets) / `wc -c` (char budgets), compare against the target harness's own budget (Claude Code `CLAUDE.md` <200 lines; Cursor rule file <500 lines; Windsurf/Devin `global_rules.md` 6,000 chars / workspace rule file 12,000 chars; cross-harness community consensus <300 lines). Still over budget after cutting DOC-10–13 → propose a split: nested per-directory files (monorepo pattern) or path-scoped/glob-conditional rules where the harness supports them — never `@path`/`@file.md` imports alone, which load in full at launch and do not reduce context.
5. **Monorepo check (DOC-17):** one root file covering unrelated packages → propose nested per-package files.

**Gate:** Every present file inventoried and classified; every DOC-11 flag verified against source. If fails → source unreadable → mark item `inconclusive`, do not cut it.

Category B: a harness context file shapes every future session's behavior across the whole project, a higher blast radius than most doc edits. Default: the diff (cuts + additions + one-line rationale each) applies using the same cut/keep judgment named above — nothing about editing a harness file matches the publish/irreversible exception list — recorded in the summary. `--ask`: show the proposed diff and get approval before writing.
