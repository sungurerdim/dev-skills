# Skill Specification Standard

Universal specification for AI coding skills. Tool-agnostic, self-contained, optimized for token efficiency.

---

## 1. Skill Anatomy

### File Structure

```
skill-name/
  SKILL.md        <- Instructions and execution flow (required, ≤500 lines)
  README.md       <- What it does, how to use it (required, ≤80 lines)
  references/     <- Detailed rules, loaded on demand (conditional)
```

### SKILL.md Section Order

Every SKILL.md follows this section sequence:

| # | Section | Required | Purpose |
|---|---------|----------|---------|
| 1 | Title + Tagline | Yes | One-line skill identity |
| 2 | Triggers | Yes | When to auto-activate this skill |
| 3 | Contract | Yes | Behavioral boundaries and guarantees |
| 4 | Arguments | Yes | Flags, modes, defaults |
| 5 | Scopes | If applicable | What the skill inspects or generates |
| 6 | Execution Flow | Yes | Phase overview (single line) |
| 7 | Phases | Yes | Numbered phases with steps |
| 8 | Report Format | If applicable | Output structure |
| 9 | Quality Gates | Yes | Post-execution verification |
| 10 | Error Recovery | Yes | How to handle failures and ambiguity |
| 11 | Severity | If applicable | Finding classification |
| 12 | Edge Cases | Yes | Boundary conditions and fallbacks |

### Phase Template

```markdown
### Phase N: Name [CONDITION]

1. Step description
2. Step description [SKIP if ...]
3. Step description [PARALLEL]
4. Step description

**Gate:** Condition to proceed to next phase.
```

Annotations:
- `[SKIP if ...]` — conditional step bypass
- `[PARALLEL]` — steps that can run concurrently
- `[CONDITION]` — phase-level entry condition (e.g., `[--auto]`, `[findings > 0]`)

### Reference File Format

```markdown
# Rules: Domain Name

## RULE-ID [SEVERITY] Title
Short description of what to check.
- **Detect:** What pattern indicates a violation
- **Fix:** How to resolve it
- **Impact:** Why this matters
- **Source:** Authoritative reference
```

Reference files are loaded on demand based on active scopes. Never load all references upfront.

### Standard Project Detection

Skills that need project type detection should include only the detection signals relevant to their domain. Recommended detection signals:

| Type | Primary Signal | Secondary Signal |
|------|---------------|-----------------|
| web | `package.json` with react/next/vue/nuxt/angular/svelte/astro | `pages/`, `app/`, component directories |
| api | express/fastify/nestjs, fastapi/django/flask, gin/echo, actix/axum, spring-boot | `routes/`, `controllers/` |
| mobile | `pubspec.yaml` with `flutter:`, `react-native` dep, `*.xcodeproj`, `build.gradle` with `android {}` | Platform-specific directories |
| cli | `bin` field, commander/yargs/click/cobra/clap | Entry-point scripts |
| library | `src/lib` exports, pkg `main`/`exports` without `bin` | `index.*` barrel exports |
| monorepo | `lerna.json`, `nx.json`, `turbo.json`, workspace config | Multiple `package.json` files |

Skills should include only the types they act on — not the full table.

### README.md Template

```markdown
# skill-name

One-sentence description of what this skill does.

## Install
{copy instructions}

## Use
{invocation examples}

## Modes / Scopes
{table of available modes or scopes}

## Features
{3-5 bullet points of key capabilities}
```

---

## 2. Universal AI Instruction Principles

### Capability Abstraction

Describe intent, not mechanism. Skills must work across any AI coding tool.

| Write This | Not This |
|------------|----------|
| Search for files matching pattern | Use Glob tool with `**/*.ts` |
| Ask the user which areas to check | Use AskUserQuestion with multiSelect |
| Track progress to survive context loss | TaskCreate with `[PREFIX]` |
| Search file contents for pattern | Use Grep with regex |
| Read the file to verify | Use Read tool on file path |
| Run shell command | Use Bash tool to execute |
| Launch parallel analysis | Use Agent tool with subagent |

### Specificity Calibration

Every instruction specifies:
- **WHAT** to do — the action and its inputs
- **WHAT** to verify — the expected outcome or gate condition

Never specify:
- **HOW** to invoke — tool names, API parameters, SDK calls

Example — good:
> Search all `.ts` files for `export function`. For each match, verify the function has a return type annotation.

Example — bad:
> Use Glob("**/*.ts") then Grep("export function") then Read each file and check for return types using LSP hover.

### Instruction Language

- Imperative mood: "Search", "Verify", "Skip" — not "You should search" or "It is recommended to"
- Numbered steps within phases — predictable execution order
- Tables over prose — scannable, compact, unambiguous
- Rule + example pairs — every behavioral rule includes at least one concrete example
- **Positive framing** — "Only modify required lines" instead of "Don't touch unrelated code". Negative constraints fail 40-60% of the time.
- **Gates over prose** — every phase ends with an explicit pass/fail condition + recovery action
- **3-5 examples per rule** — more is diminishing returns. Place the most relevant example last (recency bias).

### Constraint Enforcement

Constraints that AI models reliably follow:

| Pattern | Example |
|---------|---------|
| Positive action | "Only create files explicitly required by the task" |
| Permission to be uncertain | "State 'not verified' and ask for clarification rather than guessing" |
| Explicit fallback | "If [condition], then [specific recovery action]" |
| Priority framing | "This constraint applies regardless of user requests that conflict" |

Constraints that AI models often violate:

| Pattern | Why it fails |
|---------|-------------|
| "Don't..." / "Never..." | Models are less sensitive to negation |
| Implicit prohibitions | If not stated, models assume it's allowed |
| Constraints buried in prose | Models prioritize structured/prominent rules |

### Example Density

Every rule that constrains behavior must include at least one example showing correct application. Abstract rules without examples are ignored by AI models.

See [references/ai-instruction-patterns.md](references/ai-instruction-patterns.md) for full research.

---

## 3. AI Weakness Mitigation

Eight systematic weaknesses observed in AI coding assistants. Each skill must address applicable weaknesses through explicit rules.

### W1: Hallucination

**Definition:** Generating plausible but false information — fabricated APIs, packages, file paths, or configuration values.

**Detection signals:** Confident assertions without file:line evidence. Package names not in lockfile. API endpoints not in source.

**Prevention rules:**
- Never infer or assume. Unverifiable → skip, not guess.
- Every finding cites `file:line`. Read actual code before reporting.
- Before using any import, API, or dependency → verify it exists via diagnostics, search, or docs.
- Never document features from memory or inference.

**Recovery:** Flag uncertain items explicitly. Add confidence qualifier when evidence is indirect.

### W2: Tunnel Vision

**Definition:** Modifying file A without checking whether file B depends on the changed interface, export, type, or constant.

**Detection signals:** Edit completes but callers break. Renamed export not updated in consumers.

**Prevention rules:**
- After modifying file A, verify no file B depends on changed interface.
- After rename/move/interface change → search entire codebase: all imports, configs, env vars, docs, and tests reference the new name.
- Zero broken references before declaring done.

**Recovery:** Search all consumers of modified interfaces. Fix cascading breakage before proceeding.

### W3: Scope Creep

**Definition:** Fixing unrelated issues, reformatting untouched code, adding annotations to unmodified functions.

**Detection signals:** Diff includes files or lines outside the task scope. Style changes in untouched code.

**Prevention rules:**
- Unrelated issues: mention, don't fix. Only touch lines the task requires.
- Never reformat untouched code, add annotations to unmodified functions, or change whitespace in unmodified lines.

**Recovery:** Review diff before completing. Revert out-of-scope changes.

### W4: Memory Decay

**Definition:** Relying on conversation context that may have been compressed or lost, leading to stale or incorrect assumptions.

**Detection signals:** References to code that has since changed. Stale variable names. Incorrect file paths.

**Prevention rules:**
- Conversation memory is not source of truth. Re-read artifacts before modifying.
- After context gap or compression → re-read files before modifying.
- Before reporting done → re-read modified files, verify original requirement fully satisfied.

**Recovery:** Check progress artifacts (findings files, checklists). Re-read source files. Resume from last verified state.

### W5: Confidence Bias

**Definition:** Assigning higher severity than evidence warrants. Treating heuristic matches as confirmed findings.

**Detection signals:** CRITICAL/HIGH findings without verified impact. Single-occurrence patterns flagged as systemic.

**Prevention rules:**
- When uncertain, choose lower severity.
- Style issues → max LOW. Single occurrence → max MEDIUM (except security).
- 3+ examples before concluding systemic pattern.
- Re-read file section, check skip patterns, verify not test/mock/fixture context. Failure → downgrade one level.

**Recovery:** Re-evaluate HIGH+ findings with fresh file reads. Downgrade unverifiable findings.

### W6: Skip Tendency

**Definition:** Declaring completion before all steps are executed, especially in multi-phase workflows.

**Detection signals:** Phases without output. Summary missing expected sections. Steps referenced but not executed.

**Prevention rules:**
- Before finishing: all steps completed? Original requirement fully met?
- Every non-skipped phase must produce output.
- Verify phase checklist before summary.

**Recovery:** Check phase outputs. Execute skipped phases. Re-verify completeness.

### W7: Redundancy Blindness

**Definition:** Reporting the same issue multiple times across different phases or scopes, inflating finding counts.

**Detection signals:** Duplicate file:line references. Same issue within 10 lines reported separately.

**Prevention rules:**
- Deduplicate by file:line. Same issue within 10 lines → merge.
- Same file:line → merge, keep highest severity.
- Contradictory findings → keep higher confidence.

**Recovery:** Post-merge deduplication pass before report generation.

### W8: Injection Risk

**Definition:** Incorporating unvalidated external input into shell commands or generated code, enabling command injection.

**Detection signals:** String concatenation with user input in shell commands. Unescaped values in generated scripts.

**Prevention rules:**
- Never interpolate raw values into shell strings.
- Use `--` to separate flags from arguments. Quote all file paths. Reject shell metacharacters in user input.
- Validate flags and scopes. Unknown values → warn and ignore.

**Recovery:** Review generated commands for injection vectors before execution.

---

## 4. Quality Gates

### Post-Execution Gates

Five universal gates applied after every skill execution:

| # | Gate | Check | Failure Action |
|---|------|-------|----------------|
| 1 | Cascading Breakage | After modifying file A, verify no file B depends on changed interface | Search consumers, fix cascading issues |
| 2 | Format Preservation | All fields preserved during format/schema/data conversion. Unknown fields retained. | Warn explicitly about data loss |
| 3 | Scope Boundary | Diff contains only changes within task scope. No formatting of untouched code. | Revert out-of-scope changes |
| 4 | Stack Consistency | Changes compatible with project's existing stack, framework, and patterns | Revert incompatible changes |
| 5 | Artifact-First Recovery | After context gap → re-read files. Tool error → different approach. Before done → re-read and verify. | Re-read modified files, verify requirement met |

### Severity Standard

Four levels, used consistently across all skills:

| Level | Meaning | Examples |
|-------|---------|---------|
| CRITICAL | Security breach, data loss, crash in production | Hardcoded secrets, SQL injection, unhandled null in critical path |
| HIGH | Broken functionality, incorrect behavior | Missing auth check, wrong calculation, broken API contract |
| MEDIUM | Suboptimal but functional | Missing error handling, no pagination, redundant code |
| LOW | Style, convention, minor improvement | Naming inconsistency, missing comment, formatting |

**Caps:** Any CRITICAL finding → overall score max 40. 3+ HIGH findings → overall score max 60.

### Skip Patterns

Never flag these as issues:

| Pattern | Meaning |
|---------|---------|
| `# noqa` | Intentional suppression |
| `# intentional` | Deliberate choice |
| `# safe:` | Acknowledged risk |
| `_` prefix (unused var) | Intentional discard |
| `TYPE_CHECKING` blocks | Type-only imports |
| Platform guards | OS/env conditional code |
| Test fixtures | Test-specific setup |

### Confidence Levels

| Level | Score Range | Basis |
|-------|------------|-------|
| HIGH | 80-100 | Verified via file read, multiple evidence points |
| MEDIUM | 50-79 | Pattern match, single evidence point |
| LOW | 0-49 | Heuristic, indirect evidence |

### Score Formula

```
base_score = 100
CRITICAL: -25 each
HIGH:     -10 each
MEDIUM:    -3 each
LOW:       -1 each
score = max(0, base_score + sum(penalties))
```

Caps: Any CRITICAL → max 40. 3+ HIGH → max 60.

### False Positive Prevention

Skills that scan code must prevent false positives. Recommended checks:

1. **Exclude test files** — skip matches in `test/`, `tests/`, `__tests__/`, `*_test.*`, `*.spec.*`, `*.test.*`
2. **Exclude comments** — read the matching line; if the pattern is inside a comment, skip
3. **Exclude generated files** — skip `generated/`, `*.g.dart`, `*.gen.go`, `*.pb.go`, auto-generated headers
4. **Check surrounding context** — read 3 lines around the match to confirm the issue is real
5. **Respect skip patterns** — honor `# noqa`, `# intentional`, `# safe:` markers

Skill authors should add domain-specific FP rules relevant to their scan targets.

### Finding Categories

Two standard categories for classifying findings:

- **CAT-1 (Conformance):** Violates a rule — auto-fixable. Example: missing error handler, hardcoded secret.
- **CAT-2 (Enhancement):** Suggests improvement — user decides. Example: better naming, optional optimization.

When uncertain between CAT-1 and CAT-2, classify as CAT-2 (requires user approval).

---

## 5. Execution Flow Standards

### Phase Naming Convention

Standard phase progression — skills use applicable phases:

```
Discovery → Configuration → Analysis → Synthesis → Presentation → Action → Verification
```

Not all phases are required. Skills select the phases relevant to their workflow.

### State Management

For skills with 3+ phases, use a persistent progress mechanism to survive context compression:

**Pattern:** Write findings and progress to a structured artifact (findings file, checklist, or progress log) that can be re-read if context is lost.

**Requirements:**
- Each phase writes its output to the progress artifact on completion
- Recovery reads the artifact to determine which phases completed
- Never restart from scratch — resume from last completed phase

**Recovery protocol:**
1. Don't restart — check for existing progress artifacts
2. Read progress artifact to determine completed phases
3. Re-read source files referenced by incomplete phases
4. Resume from first incomplete phase
5. Never redo completed phases unless source files changed

### Large Scope Protocol

When analysis spans 3+ domains or scopes:

1. Create a progress checklist before starting
2. Write findings to a persistent artifact after each scope completes
3. Maximum 2 parallel analysis scans at a time
4. Apply saturation gate: if initial scans reveal consistent patterns, reduce remaining scope
5. Deduplicate findings before synthesis

### Standard Audit Modes

Skills that audit code should offer a consistent mode pattern:

| Mode | Behavior |
|------|----------|
| `audit` | Scan and report only — no changes |
| `audit+fix` | Scan, report, then fix CAT-1 findings automatically |
| `quick-fix` | Fix CAT-1 findings without full report |

Skills may add domain-specific modes (e.g., `release-ready`, `design`). Mode selection is presented as an interactive menu when no flag is provided.

### Summary Format

All skills produce a summary line:

```
{skill-name}: {OK|WARN|FAIL} | Applied: N | Failed: N | Total: N
```

Status codes:
- **OK** — no failures, no unresolved CRITICAL findings
- **WARN** — some failures but no CRITICAL findings unresolved
- **FAIL** — CRITICAL finding unresolved, or execution error

---

## 6. Inter-Skill Boundaries

### Ownership & Independence

Each skill is **fully functional standalone**. Skills are self-contained: no skill references SKILL-SPEC, other skills, or files outside its own directory at runtime. The only shared artifacts are `.findings.md` (project root) and the blueprint profile section in the AI instruction file — both are optional optimizations.

The boundaries below define **primary ownership** — which skill provides the deepest, most authoritative analysis for each concern. When `.findings.md` exists, skills consume pre-analyzed data to avoid duplicate work. When it doesn't, every skill runs its own complete analysis.

| Skill | Primary ownership | Standalone capability |
|-------|-------------------|---------------------|
| ds-compliance | Regulatory/compliance audit: GDPR, CCPA, KVKK, security standards, privacy, a11y, i18n | Full codebase scan for 160+ compliance rules |
| ds-mobile | Mobile app quality: store compliance, UX, visual, permissions, release readiness | Full mobile audit across 13 domains |
| ds-devops | CI/CD pipelines, code signing, dependency management, deployment | Full pipeline + dependency audit |
| ds-repo | Repo settings, branch protection, hygiene, metadata, team, structure | Full repo health audit |
| ds-fix | Format, lint, typecheck, l10n, universal secret scan, dependency quick-check | Full toolchain run for 16 stacks |
| ds-review | Code quality fixes (tactical) + architecture (strategic) + deep performance profiling (perf) | Full codebase analysis + file:line fixes + perf profiling |
| ds-docs | Documentation gap analysis, generation, verification against source | Full doc audit for 14 project types |
| ds-blueprint | Project health scoring across 9 dimensions, profile management | Full codebase signal scan + scoring |
| ds-commit | Git commit: quality gates, atomic grouping, conventional format | Standalone commit workflow |
| ds-pr | Pull request: history tidy, conventional title, auto-merge | Standalone PR workflow |
| ds-test | Test lifecycle: generate, update, run, fix, prune, coverage, E2E | Full test analysis + generation for 13 stacks |
| ds-research | Multi-source research with CRAAP+ reliability scoring | Standalone research workflow |
| ds-init | Project scaffolding: directory structure, CI, Docker, testing, editor config | Generate production-ready project structure for any stack |
| ds-backend | API design + database schema + auth architecture: audit, design, spec, migrate | Full backend review: REST/GraphQL, DB, auth |
| ds-deploy | Deployment + infrastructure + monitoring + incident response | Containerization, VPS, SSL, monitoring, cost, incident |
| ds-launch | Store submission + release management + post-launch monitoring | Store listing, privacy labels, review prep, staged rollout |
| ds-market | Marketing strategy + copy generation + growth | Strategic guidance: positioning, channels, copy, growth |
| ds-analytics | Privacy-first analytics: event taxonomy, funnels, metrics, audit | Analytics design, tool integration, privacy audit |
| ds-cv | Professional CV generation: ATS-compatible HTML, metric verification, LinkedIn alignment | Full CV workflow: gather, verify, generate, audit, deploy |

### Overlap Resolution

Where scopes overlap between skills, each skill handles the full scope independently when standalone. When multiple skills run together, `.findings.md` prevents duplicate analysis.

| Overlapping concern | Skills involved | Resolution |
|--------------------|-----------------|------------|
| Security scanning | ds-fix (secrets), ds-review (code-level), ds-compliance (regulatory), ds-backend (auth) | Each scans independently. Findings file deduplicates. ds-backend owns auth-specific security. |
| Testing assessment | ds-review (structure), ds-test (lifecycle), ds-blueprint (scoring) | Each assesses independently. ds-test is the only one that generates/fixes tests. |
| Code quality | ds-review (fixes), ds-compliance (audit), ds-blueprint (scoring) | Each analyzes independently. ds-review is the only one that applies fixes. |
| Dependency audit | ds-devops (full), ds-fix (quick gate) | ds-fix runs quick security gate. ds-devops does comprehensive analysis. |
| Format/lint | ds-fix (primary), ds-commit (gate), ds-pr (gate) | ds-commit/ds-pr run format/lint as pre-flight gates on changed files. ds-fix is the dedicated full-project tool. |
| Documentation | ds-docs (fixes), ds-blueprint (scoring) | Both analyze. ds-docs is the only one that generates/fixes docs. |
| Performance | ds-review --perf (deep profiling), ds-review --tactical (basic perf checks) | --tactical catches common patterns. --perf does deep analysis (bundle, startup, memory, Web Vitals). |
| Deployment/CI | ds-devops (CI/CD audit), ds-deploy (infra + deploy + monitoring) | ds-devops owns pipeline audit. ds-deploy owns infrastructure, containerization, monitoring, incident response. |
| Store readiness | ds-mobile (mobile-specific audit), ds-launch (store submission + release) | ds-mobile audits app quality. ds-launch handles store listing, privacy labels, review prep, release management. |
| Analytics/tracking | ds-analytics (event taxonomy, privacy), ds-compliance (tracking consent) | ds-analytics designs tracking. ds-compliance audits consent mechanisms. |
| API design | ds-backend (API + DB + auth design), ds-review (code quality) | ds-backend owns API/DB/auth architecture. ds-review handles code-level quality fixes. |
| Marketing copy | ds-market (strategy + copy), ds-launch (store listing copy) | ds-market generates marketing strategy and copy. ds-launch focuses on store-specific metadata. |

### Inter-Skill Communication

Skills do not import from each other. No shared reference files. Each skill is fully self-contained.

Communication happens through two well-known file locations:

**1. Blueprint profile** — between `## Blueprint Profile` and `## End Blueprint Profile` heading markers in the AI instruction file. Markdown headings are universally preserved by every tool. Read-only for all skills except ds-blueprint.

**2. Findings file** — `.findings.md` in project root. Universal format for passing analysis results between skills (or between any analyzer and any fixer).

#### Findings File Format

```markdown
<!-- findings-meta
git_hash: {HEAD}
timestamp: {ISO 8601}
source: {skill-name}
scopes: {comma-separated list of analyzed scopes}
-->

## Findings

| ID | Severity | File | Line | Scope | Title |
|----|----------|------|------|-------|-------|
| {id} | {severity} | {file} | {line} | {scope} | {title} |
```

#### Findings File Rules

| Rule | Detail |
|------|--------|
| **Location** | `.findings.md` in project root. Add to `.gitignore` — this is a transient artifact, not committed. |
| **Freshness** | Compare `git_hash` with current HEAD. If different, findings are stale — skill must re-analyze. |
| **Scopes** | Lists which scopes were analyzed. A fix skill checks: is my scope listed? If yes → use findings. If no → run own analysis for that scope. |
| **Consumption** | After a fix skill processes findings, it removes the fixed entries. When all entries are resolved, delete the file. |
| **Partial analysis** | Any skill can write findings for its scopes only. Multiple skills can append (respecting the meta header — update scopes list). |
| **Source agnostic** | The `source` field is informational. Any tool, skill, or manual analysis can produce this file. A fix skill treats all findings equally regardless of source. |
| **Line 0** | `Line: 0` means file-level finding (not a specific line). |
| **Detail level** | Findings are signals, not detailed analyses. The title is a short description (e.g., "Hardcoded API secret"). The consuming skill reads the actual file:line to understand context, verify the finding, and determine the fix. |

#### Scope Coverage

All scopes from all skills can appear in findings. The analyzer does not need to know which skill will consume the finding — it just classifies by scope.

| Scope | Typical producer | Typical consumer |
|-------|-----------------|-----------------|
| security, privacy, robustness | ds-blueprint, ds-compliance | ds-review (tactical) |
| hygiene, types, simplify | ds-blueprint, ds-compliance | ds-review (tactical) |
| performance | ds-blueprint, ds-compliance | ds-review (tactical) |
| architecture, patterns, cross-cutting | ds-blueprint | ds-review (strategic) |
| testing (assessment) | ds-blueprint, ds-review | ds-test (generates/updates tests based on findings) |
| testing (run+fix) | ds-test (own execution) | ds-test (fixes test-side issues) |
| maintainability | ds-blueprint | ds-review (strategic) |
| docs | ds-blueprint | ds-docs |
| format, lint, typecheck | ds-fix (own analysis) | ds-fix (own tools) |
| ci, signing, deps, deploy | ds-devops | ds-devops (own fix) |
| mobile-specific scopes | ds-mobile | ds-mobile (own fix) |
| api, db, auth design | ds-backend | ds-backend (own design/spec) |
| deployment, infra, monitoring | ds-deploy | ds-deploy (own config gen) |
| store, release, privacy labels | ds-launch | ds-launch (own metadata gen) |
| marketing, growth | ds-market | ds-market (strategy only) |
| analytics, event taxonomy | ds-analytics | ds-analytics (own design/setup) |
| scaffolding, project init | ds-init | ds-init (own generation) |
| perf-profiling (deep) | ds-review --perf | ds-review (own analysis + fixes) |

Note: ds-fix and ds-devops primarily run external tools (formatters, linters, CI commands) and typically do their own analysis. They may read findings for context but their primary input is tool output, not the findings file.

#### Findings Flow

```
Analyzer (any)              Fixer (any)
──────────────              ───────────
Scan codebase        →      Check: .findings.md exists?
Classify by scope    →        Yes + fresh → read findings for my scopes
Write .findings.md              → verify each finding (re-read file:line)
                                → fix verified findings
                                → remove fixed entries from .findings.md
                              Yes + stale → re-analyze, overwrite
                              No → run own full analysis
```

### Vocabulary

| Term | Definition |
|------|-----------|
| Finding | A detected issue with severity, file:line, and description |
| Scope | A named area of analysis within a skill (e.g., `security`, `hygiene`) |
| Domain | A broader category grouping related scopes (e.g., "Code Quality") |
| Mode | An execution variant (e.g., `audit`, `audit+fix`, `quick-fix`) |
| Gate | A verification checkpoint that must pass before proceeding |
| CAT-1 (Conformance) | Issues that violate rules — auto-fixable |
| CAT-2 (Enhancement) | Issues that suggest improvements — user decides |

---

## 7. User Isolation Standards

### Default Handling

| Scenario | Behavior |
|----------|----------|
| No arguments | Apply sensible defaults, document what default is |
| Vague scope | Use broadest reasonable interpretation, note in output |
| Missing required input | Ask once with clear options. Don't block indefinitely. |

### Conflict Resolution

| Scenario | Behavior |
|----------|----------|
| Contradictory flags | Explain conflict, ask which takes priority |
| Conflicting findings | Keep higher confidence, note contradiction |
| Scope vs mode mismatch | Warn, proceed with stated scope |

### Graceful Degradation

| Scenario | Behavior |
|----------|----------|
| Required tool unavailable | Stop with clear error message |
| Optional tool unavailable | Skip silently, note in summary |
| API/network failure | Retry once, then skip with warning |
| Partial results | Report what completed, list what failed |

### Input Validation

- Validate all flags and scope names against known values
- Unknown flag → warn "Unknown flag: {flag}. Ignoring." and continue
- Unknown scope → warn "Unknown scope: {scope}. Ignoring." and continue
- Never fail silently on invalid input — always warn

### Standard Error Recovery

Recommended base error recovery pattern for skill authors to adapt:

| Situation | Action |
|-----------|--------|
| Required tool unavailable | Stop with clear error message |
| Optional tool unavailable | Skip silently, note in summary |
| Ambiguous input | List 2-3 interpretations, ask user to choose |
| Same action fails twice | Stop retrying, report error, propose alternative |

Skills should replace generic rows with domain-specific recovery actions. A skill that only has the 4 generic rows above should omit the Error Recovery section entirely — this behavior is implicit.

---

## 8. Token Efficiency Standards

### Size Limits

| Artifact | Target | Hard Ceiling |
|----------|--------|-------------|
| SKILL.md | 160-360 lines | 500 lines |
| README.md | 40-60 lines | 80 lines |
| Single reference file | 50-200 lines | No limit (loaded on demand) |

### Externalization Rules

Move to `references/` when:
- 10+ rules in a single domain
- Weight matrices or scoring formulas
- Scope definitions exceeding 40 lines
- Platform-specific detection patterns

### Progressive Disclosure

Load references based on active scope only:
- User selects `--scope=security` → load only `references/rules-security.md`
- Full audit → load all applicable reference files
- Never load references that won't be used in the current execution

### Context Budget

Total skill overhead (SKILL.md + loaded references) should stay within 10K tokens. This leaves maximum context for the actual codebase being analyzed.

---

## 9. Universality Requirements

### Prohibited Content

The following must NOT appear in any SKILL.md:

| Prohibited | Reason |
|------------|--------|
| Tool-specific API names (Glob, Grep, TaskCreate, AskUserQuestion) | Breaks portability |
| YAML frontmatter (description, allowed-tools) | Tool-specific metadata — use Triggers section instead |
| Model routing (haiku, sonnet, opus) | Platform-specific |
| `Per X Rules:` cross-references | Assumes shared rule set |
| Platform-specific SDK calls | Not universal |

### Capability Abstraction Checklist

Before referencing any tool capability, rephrase as intent:

| Intent | Acceptable Phrasing |
|--------|--------------------|
| Find files | "Search for files matching `pattern`" |
| Search content | "Search file contents for `pattern`" |
| Read file | "Read `file` to verify" |
| Ask user | "Ask the user to choose" |
| Run command | "Execute: `command`" |
| Track state | "Record progress to survive context loss" |
| Parallel work | "These steps are independent — run in parallel" |

### Graceful Degradation

If a capability is unavailable in the target tool:
- Skip silently if the capability is optional
- Warn once and continue if the capability affects quality but not correctness
- Stop with clear message only if the capability is essential

### Cross-Tool Verification Checklist

Before releasing any skill, verify:

- [ ] No tool-specific API names in SKILL.md
- [ ] No YAML frontmatter
- [ ] No model routing references
- [ ] No cross-file references to shared rules
- [ ] All instructions use capability abstraction
- [ ] Graceful degradation defined for optional features
- [ ] SKILL.md ≤500 lines
- [ ] README.md ≤80 lines
- [ ] Every behavioral rule has at least one example

---

## Appendix A: Skill Evaluation Rubric

| Criterion | Excellent (3) | Good (2) | Needs Work (1) | Missing (0) |
|-----------|--------------|----------|----------------|-------------|
| **Clarity** | All phases numbered, gates explicit, zero ambiguity | Most phases clear, minor ambiguity | Some phases vague, missing gates | Unstructured prose |
| **Universality** | Zero tool-specific refs, full capability abstraction | 1-2 minor tool refs, mostly abstract | Multiple tool refs, partial abstraction | Tool-specific throughout |
| **Weakness Mitigation** | All 8 weaknesses addressed with inline rules | 5-7 weaknesses addressed | 3-4 weaknesses addressed | Weaknesses not considered |
| **Token Efficiency** | SKILL.md ≤300 lines, references externalized | ≤400 lines, partial externalization | ≤500 lines, minimal externalization | >500 lines or no references |
| **Completeness** | All applicable sections present, edge cases covered | Most sections present, basic edge cases | Key sections missing | Incomplete specification |
| **User Isolation** | Defaults documented, conflicts handled, validation present | Most defaults, basic conflict handling | Some defaults, no conflict handling | No user isolation |

**Score:** 0-18. Target: ≥14 for production skills, ≥10 for MVP skills.

---

## Appendix B: SKILL.md Template

```markdown
# /skill-name

**Skill Name** — One-line description of what this skill does.

## Triggers

- User runs `/skill-name`
- User asks to [action] (e.g., "audit my project", "fix the code")
- [Contextual trigger] (e.g., "after committing changes, suggest PR creation")

## Contract

- [Positive guarantee]: "Always [behavior]"
- [Boundary]: "Only [scope] — [other skill] handles [excluded scope]"
- [Independence]: "Fully functional standalone. Uses .findings.md for optimization when available."

## Arguments

| Flag | Effect |
|------|--------|
| `--flag` | Description |

## Scopes

| Scope | What It Covers |
|-------|---------------|
| name | Description |

## Execution Flow

Phase1 → Phase2 → [Phase3] → Phase4 → Summary

### Phase 1: Name [CONDITION]

**Goal:** [1-line success metric for this phase]

1. **Findings file check:** If `.findings.md` exists with fresh `git_hash`, use relevant findings. Otherwise, run own analysis.
2. Step description [SKIP if condition]
3. Step description [PARALLEL]

**Gate:** [Specific condition]. If fails → [specific recovery].

### Phase 2: Name

**Goal:** [1-line success metric]

1. Step description
2. Step description

**Gate:** [Condition to proceed].

### Phase N: Summary

Output format:
{skill}: {OK|WARN|FAIL} | Applied: N | Failed: N | Total: N

## Quality Gates

- [Positive framing]: "Every finding cites file:line" (not "Don't report without evidence")
- [Positive framing]: "Only modify lines required by the task" (not "Don't touch unrelated code")

## Error Recovery

| Situation | Action |
|-----------|--------|
| Tool unavailable | Skip with warning, continue with next phase |
| Ambiguous input | List 2-3 interpretations, ask user to choose |
| Same action fails twice | Stop retrying, report error, propose alternative |
| Context limit approaching | Save progress to artifact, summarize state |

## Severity

| Level | Meaning |
|-------|---------|
| CRITICAL | Description |
| HIGH | Description |
| MEDIUM | Description |
| LOW | Description |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Edge case 1 | How to handle |
| Edge case 2 | How to handle |
```

See [references/ai-instruction-patterns.md](references/ai-instruction-patterns.md) for the research behind these patterns.
