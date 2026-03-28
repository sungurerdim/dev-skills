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
- No annotation — **mandatory phase, always executes**

### Mandatory vs Conditional Phases

Phases without a `[CONDITION]` annotation are **mandatory** — they execute on every run, regardless of mode or flags. Skipping a mandatory phase is a skill execution bug.

In the execution flow overview, the convention is:
- `Phase` (no brackets) = mandatory, always runs
- `[Phase]` (square brackets) = conditional, runs only when condition is met

**Example:** `Assess → Consolidate → Dashboard → [Suggest] → Update Profile → Summary`
- Assess, Consolidate, Dashboard, Update Profile, Summary = mandatory
- Suggest = conditional (skip if --preview)

**Mandatory phase outputs:** Every mandatory phase MUST produce visible output. If a mandatory phase completes but produces no user-visible output (no table, no summary line, no status), the skill has a bug. Mandatory phases exist because their output is essential for the user to understand the skill's results.

**Enforcement:** When a phase has no `[SKIP if ...]` or `[CONDITION]` annotation, the execution engine treats it as a hard requirement. The summary phase MUST verify that all mandatory phases produced output.

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

{Pain point or problem this skill addresses.}

One-sentence description framed as outcome.

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
- **WHAT** to do — the action and its inputs (explicit, not vague — Claude 4.x takes instructions literally)
- **WHAT** to verify — the expected outcome or gate condition
- **WHAT** to output — format, structure, and scope of the result

Avoid specifying:
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
- **Positive framing** — "Only modify required lines" instead of "Don't touch unrelated code". Hard negatives fail ~5%, soft negatives ~10-15%. Positive framing is 2-5× more reliable. Reserve hard negatives for safety-critical rules only (max 5 per skill).
- **Gates over prose** — every phase ends with an explicit pass/fail condition + recovery action. Process-level verification outperforms outcome-only checks.
- **3-5 examples per rule** — more is diminishing returns. Well-selected 3.5% of examples outperforms 100% random (RDS+ arXiv 2025). Place the most relevant example last (recency bias). Prioritize diversity over quantity.
- **Hyper-explicit intent** — Claude 4.x takes instructions literally — omitted details are omitted from output. Specify desired output format, scope, and criteria precisely. Vague intent produces vague results.
- **Placeholder examples** — All examples in SKILL.md use `{placeholder}` tokens, never hardcoded project names, file paths, library names, or version numbers. Examples must be reusable across any project context.

| Write This | Not This |
|------------|----------|
| `{type}({scope}): {description}` | `feat(auth): add OAuth2 login` |
| `{tool_a} conflict with {tool_b} → {resolution}` | `ESLint conflict with Prettier → Prettier wins` |
| `{n} commits ({type_a}+{type_b}) → net: {dominant_type}` | `3 commits (feat+fix+refactor) → net: feat` |
| `If {metric} < {threshold} → {action}` | `If coverage < 80% → generate tests` |

### Skill Voice

**Pain-first opening:** Every SKILL.md opens with the problem it solves, not the feature it provides. First line = pain or status-quo challenge. Second line = how the skill addresses it.

| Pattern | Example |
|---------|---------|
| Good | "AI commits are vague and bundle unrelated changes. This skill reads the diff, groups logically, writes precisely." |
| Bad | "Smart Commits — Quality gates + atomic grouping + conventional commit format." |

Every claim in the opening must be verifiable against the skill's actual scope. If the skill generates plans but doesn't execute them, say "generates the playbook" not "fixes the problem."

**Allowed words:** prevents, eliminates, enforces, catches, verifies, reduces, automates, replaces, ships, generates, detects, flags.

**Forbidden words:** leverage, empower, unlock, seamlessly, cutting-edge, next-generation, world-class, innovative, holistic, synergy. These signal marketing-speak and reduce trust with developer audiences.

**Tone:** Confident, opinionated, technically precise. Not salesy, not humble, not academic. Short sentences. Active voice. Imperative mood.

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

### Adaptive Thinking (replaces forced CoT)

Reasoning-capable models (Claude 4.x, o3-mini) reason adaptively by default. Forced chain-of-thought ("think step-by-step") adds only 2.9–3.1% accuracy while costing 20-80% more tokens (Wharton GenAI Labs 2025).

| Instead of | Write |
|-----------|-------|
| "Think through this step-by-step" | "Identify the 3 key factors, then decide" |
| "Reason carefully about each option" | "Compare options against these criteria: [list]" |
| "Let me analyze this..." | (Omit — model calibrates reasoning depth) |

**Prompt reasoning explicitly only when:**
- Using non-reasoning models (Haiku) on complex tasks (+11-13% accuracy gain)
- Multi-criteria decisions with >3 trade-offs
- Novel problems outside common patterns

**Skip reasoning prompts for:**
- Procedural tasks with clear numbered steps
- Pattern-matching tasks (code review, linting)
- Simple lookups or transformations

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

**Pattern:** Write findings and progress to a structured file (findings file, checklist, or progress log) that can be re-read if context is lost. Conversation memory is volatile — structured files survive context compression.

**Requirements:**
- Each phase writes its output to the progress artifact on completion
- Recovery reads the artifact to determine which phases completed
- Use structured formats (JSON, markdown tables) over prose for state files — easier to parse on recovery
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

### Finding Resolution Completeness (FRC)

Every finding produced by an audit phase MUST appear in the summary with exactly one disposition. No finding may be silently dropped.

**Standard dispositions:**

| Disposition | Meaning | When to use |
|-------------|---------|-------------|
| `fixed` | Applied successfully, verified | Fix confirmed via re-read or API check |
| `failed` | Fix attempted, did not succeed | Tool error, API rejection, or verification failed |
| `skipped` | Intentionally not fixed, reason stated | Platform limitation, plan scope, user declined |
| `needs-input` | Requires information from user | URL, credential, preference, or decision the skill cannot infer |
| `needs-approval` | Risky or cross-module, awaiting confirmation | Destructive action, multi-contributor impact, architectural change |
| `not-applicable` | Re-verified and dismissed | Context changed, false positive on re-check, already resolved |

**Rules:**

1. Every finding gets exactly one disposition — `fixed + failed + skipped + needs_input + needs_approval + not_applicable = total`
2. `needs-input` findings MUST trigger a question to the user before the summary phase. Present the finding context and ask for the required input. If the user provides input → attempt fix → `fixed` or `failed`. If the user declines → `skipped`.
3. `needs-approval` findings MUST trigger a review step before the summary phase. Present all needs-approval items with context (why they are risky: cross-module, destructive, architectural). Ask: Apply All / Review Each / Skip All. `--auto` without `--force-approve` → list and skip. `--force-approve` → apply all without asking. If the user approves → attempt fix → `fixed` or `failed`. If the user skips → `skipped (user declined)`.
4. `skipped` findings MUST include a parenthetical reason: `Skipped: 2 (1 platform limit, 1 user declined)`
5. The summary table lists every finding with its disposition — no finding appears only in the audit phase and disappears from the summary.

**Example — correct:**
```
| # | Finding              | Disposition                        |
|---|----------------------|------------------------------------|
| 1 | {finding_1}          | fixed ✅                           |
| 2 | {finding_2}          | skipped ({limitation_reason})      |
| 3 | {finding_3}          | needs-input → user provided → fixed ✅ |
| 4 | {finding_4}          | skipped ({limitation_reason})      |
| 5 | {finding_5}          | needs-approval → user approved → fixed ✅ |
```

**Example — incorrect ({finding_3} silently dropped):**
```
| # | Finding              | Disposition                   |
|---|----------------------|-------------------------------|
| 1 | {finding_1}          | fixed ✅                      |
| 2 | {finding_2}          | skipped ({limitation_reason})  |
```

### Deterministic Scope Checklist (DSC)

Every scope that performs auditing MUST define an explicit, enumerated checklist of checks. Each check produces exactly one outcome per run.

**Check outcomes:**

| Outcome | Symbol | Meaning |
|---------|--------|---------|
| Finding | severity tag | Issue detected, added to findings list |
| Pass | ✅ | Check executed, no issue found |
| Not applicable | N/A | Check cannot apply to this project (with reason) |

**Rules:**

1. Each scope section in SKILL.md lists its checks as a numbered or bulleted list with a short name for each check
2. Every listed check MUST be evaluated on every run — no check is silently omitted based on context
3. If a check cannot apply (e.g., "social preview" on private repo), report as N/A with reason — never silently skip
4. The "clean scopes" or "healthy" section in the summary explicitly lists which checks passed, confirming they were evaluated
5. Two runs of the same skill on the same repo at the same commit MUST evaluate the same checklist — the checks are deterministic, only the outcomes may differ

**Example scope definition:**
```markdown
**{scope} scope checks:**
1. {check_1} — {expected_value}
2. {check_2} — {expected_value}
3. {check_3} — {expected_value}
4. {check_4} — {expected_value}
5. {check_5} — {expected_value}
```

**Example scope result (all checks accounted):**
```
{scope}: 3 findings, 2 pass
  1. {check_1}     → ✅ {expected_value}
  2. {check_2}     → MEDIUM: {actual_value} (expected {expected_value})
  3. {check_3}     → MEDIUM: {actual_value} (expected {expected_value})
  4. {check_4}     → MEDIUM: {actual_value} (expected {expected_value})
  5. {check_5}     → N/A ({reason_not_applicable})
```

### Summary Format

All skills produce a summary line:

```
{skill-name}: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

Status codes:
- **OK** — no failures, no unresolved CRITICAL findings
- **WARN** — some failures but no CRITICAL findings unresolved
- **FAIL** — CRITICAL finding unresolved, or execution error

**Accounting gate:** The summary MUST satisfy `fixed + failed + skipped + needs_input + needs_approval + not_applicable = total`. If the equation does not balance, the skill has a bug.

---

## 6. Inter-Skill Boundaries

### Ownership & Independence

Each skill is **fully functional standalone**. Skills are self-contained: no skill references SKILL-SPEC, other skills, or files outside its own directory at runtime. The only shared artifacts are `.ds-findings.md` (project root) and the blueprint profile section in the AI instruction file — both are optional optimizations.

The boundaries below define **primary ownership** — which skill provides the deepest, most authoritative analysis for each concern. When `.ds-findings.md` exists, skills consume pre-analyzed data to avoid duplicate work. When it doesn't, every skill runs its own complete analysis.

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
| ds-frontend | Frontend design quality: design system, tokens, components, states, a11y, responsive, theming | Full UI audit + design system generation for any framework |
| ds-tune | Autonomous optimization: measurable metric loop, 100+ experiments, keep only improvements | Full optimization workflow for any measurable metric |
| ds-solve | Adaptive problem-solving: multi-plan backtracking, web research, constraint preservation | Full iterative solve with 3-layer budget ({P} plans x {R} rounds x {A} alternatives) |

### Overlap Resolution

Where scopes overlap between skills, each skill handles the full scope independently when standalone. When multiple skills run together, `.ds-findings.md` prevents duplicate analysis.

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
| UI/UX quality | ds-frontend (design system), ds-mobile (mobile UX), ds-review (code quality), ds-compliance (a11y law) | ds-frontend owns design tokens, component states, responsive, theming. ds-mobile owns mobile-specific UX (gestures, permissions, store). ds-review owns code-level quality. ds-compliance owns regulatory a11y (EAA, ADA). |

### Inter-Skill Communication

Skills do not import from each other. No shared reference files. Each skill is fully self-contained.

Communication happens through two well-known file locations:

**1. Blueprint profile** — between `## Blueprint Profile` and `## End Blueprint Profile` heading markers in the AI instruction file. Markdown headings are universally preserved by every tool. Read-only for all skills except ds-blueprint.

**Marker detection:** Consumer skills search for `## Blueprint Profile` heading first, then legacy markers (HTML comment pairs or variant headings containing "Blueprint Profile") as fallback. ds-blueprint writes a new standard profile alongside legacy blocks without touching them, then reports coverage comparison so the user can decide when to remove the legacy block.

**2. Findings file** — `.ds-findings.md` in project root. Universal format for passing analysis results between skills (or between any analyzer and any fixer).

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

**Single file, always.** There is exactly ONE `.ds-findings.md` per project. All producers write to the same file. All consumers read from the same file. No skill creates its own separate findings file.

| Rule | Detail |
|------|--------|
| **Location** | `.ds-findings.md` in project root. Add to `.gitignore` — this is a transient artifact, not committed. |
| **Freshness** | Compare `git_hash` with current HEAD. If different, findings are stale — skill must re-analyze. |
| **Scopes** | Lists which scopes were analyzed. A fix skill checks: is my scope listed? If yes → use findings. If no → run own analysis for that scope. |
| **Consumption** | After a fix skill processes findings, it removes the fixed entries. When all entries are resolved, delete the file. |
| **Source agnostic** | The `source` field is informational. Any tool, skill, or manual analysis can produce this file. A fix skill treats all findings equally regardless of source. |
| **Line 0** | `Line: 0` means file-level finding (not a specific line). |
| **Detail level** | Findings are signals, not detailed analyses. The title is a short description (e.g., "Hardcoded API secret"). The consuming skill reads the actual file:line to understand context, verify the finding, and determine the fix. |

#### Write Semantics

Multiple skills produce findings. They all write to the same `.ds-findings.md` with these rules:

| Scenario | Behavior |
|----------|----------|
| File doesn't exist | Create new file with your scopes in the meta header |
| File exists, same `git_hash` | **Append**: add your findings rows, add your scopes to the `scopes` list in meta header. Dedup: if a finding at the same file:line already exists, keep the one with higher severity. |
| File exists, different `git_hash` | File is stale. If you are a full-codebase analyzer (ds-blueprint): overwrite entirely. If you are a partial analyzer (ds-compliance, ds-mobile, ds-test): overwrite only YOUR scopes — preserve findings from other scopes that are still valid. |
| After consuming/fixing | Remove fixed entries from the file. Update scopes list if a scope is now fully resolved. Delete file when zero entries remain. |

**Producer priority:** When ds-blueprint and another skill both write the same scope, ds-blueprint's findings take precedence (it scans the entire codebase). The other skill's findings are merged only for scopes ds-blueprint didn't cover.

**Meta header after multi-producer append:**
```
<!-- findings-meta
git_hash: {HEAD}
timestamp: {latest write timestamp}
source: ds-blueprint, ds-compliance, ds-test
scopes: security, privacy, hygiene, types, ..., regulatory, web, testing
-->
```

#### Scope Coverage

All scopes from all skills can appear in findings. The analyzer does not need to know which skill will consume the finding — it just classifies by scope.

| Scope | Typical producer | Typical consumer |
|-------|-----------------|-----------------|
| security, privacy | ds-blueprint, ds-compliance | ds-review (tactical) |
| hygiene, types, simplify | ds-blueprint, ds-compliance | ds-review (tactical) |
| ai-hygiene, doc-sync | ds-blueprint | ds-review (tactical) |
| performance | ds-blueprint, ds-compliance | ds-review (tactical) |
| robustness, production-readiness | ds-blueprint | ds-review (tactical) |
| architecture, patterns, cross-cutting | ds-blueprint | ds-review (strategic) |
| maintainability, ai-architecture | ds-blueprint | ds-review (strategic) |
| testing, functional-completeness | ds-blueprint, ds-review | ds-test (generates/updates tests based on findings) |
| testing (run+fix) | ds-test (own execution) | ds-test (fixes test-side issues) |
| stack | ds-blueprint | ds-review, ds-fix, ds-devops |
| dx | ds-blueprint | ds-review |
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
| tokens, components, states, a11y (design), responsive, theming | ds-blueprint, ds-frontend | ds-frontend (audit + fix + design) |

Note: ds-fix and ds-devops primarily run external tools (formatters, linters, CI commands) and typically do their own analysis. They may read findings for context but their primary input is tool output, not the findings file.

#### Findings Flow

```
Analyzer (any)              Fixer (any)
──────────────              ───────────
Scan codebase        →      Check: .ds-findings.md exists?
Classify by scope    →        Yes + fresh → read findings for my scopes
Write .ds-findings.md              → verify each finding (re-read file:line)
                                → fix verified findings
                                → remove fixed entries from .ds-findings.md
                              Yes + stale → re-analyze, overwrite
                              No → run own full analysis
```

### Inter-Skill Data Utilization (IDU)

Skills are standalone, but when upstream artifacts exist they MUST be fully utilized — not partially read or ignored.

**Three shared artifacts:**

| Artifact | Location | Producer | Consumers |
|----------|----------|----------|-----------|
| Blueprint profile | AI instruction file (`## Blueprint Profile`) | ds-blueprint | All skills that analyze or fix code |
| Findings file | `.ds-findings.md` in project root | ds-blueprint, ds-compliance, ds-mobile, ds-review | All skills that fix code or generate assets |
| Repo metadata | GitHub API (live query) | ds-repo (also cached in findings when relevant) | Skills that need repo context (visibility, plan, settings) |

#### Producer Requirements

Producer skills MUST ensure their output is maximally useful for downstream consumers:

1. **Blueprint profile completeness:** When ds-blueprint writes the profile, ALL sections must be populated — every field exists because specific consumers depend on it:
   - **Header** (Type, Stack, Target): used by all consumers for detection skip and severity calibration
   - **Config.priorities**: ds-review (scope ordering), ds-docs (generation priority)
   - **Config.constraints**: ds-deploy (infra limits), ds-repo (settings), ds-compliance (scope)
   - **Config.data + regulations**: ds-compliance (regulation framework + PII types), ds-analytics (privacy), ds-backend (auth), ds-mobile (store compliance)
   - **Config.audience + deploy**: ds-docs (tone), ds-launch (store requirements), ds-deploy (target), ds-devops (pipeline)
   - **Project Map.Toolchain**: ds-fix (formatter/linter), ds-test (test framework), ds-devops (CI platform)
   - **Project Map.Modules + External**: ds-backend (API structure), ds-docs (what to document), ds-deploy (dependencies)
   - **Ideal Metrics.Coverage**: ds-test (threshold target)
   - **Current Scores**: ds-review (focus low dimensions), ds-mobile (focus low dimensions)
   An incomplete profile forces consumers to re-detect what blueprint already discovered.

2. **Findings file scope coverage:** When writing `.ds-findings.md`, the `scopes` field in the meta header MUST list every scope that was analyzed — even if zero findings were found for that scope. This tells consumers "this scope was checked and is clean" vs "this scope was never analyzed." Example:
   ```
   scopes: security, code-quality, architecture, performance, resilience, testing, stack, dx, docs
   ```
   A consumer checking for `testing` findings and seeing `testing` in the scopes list with zero matching rows knows testing is clean. If `testing` is absent from scopes, the consumer must run its own testing analysis.

3. **Finding actionability:** Every finding in `.ds-findings.md` must include enough context for a consumer to act:
   - `File` and `Line` must be precise (not approximate or file-level when line-level is possible)
   - `Title` must describe the issue, not just name the check (e.g., "Hardcoded API key in config" not "SEC-01 violation")
   - `Scope` must use standard scope names from the Scope Coverage table

#### Consumer Requirements

Every skill is **fully standalone** — zero dependency on any other skill. Upstream artifacts are **performance optimizations**, not functional requirements. A skill with no blueprint profile and no findings file MUST produce identical quality output by running its own complete analysis. The only difference: with upstream data, it skips redundant work.

Consumer skills MUST check for and fully utilize upstream artifacts before running their own analysis:

1. **Blueprint profile utilization:** Before starting, search for `## Blueprint Profile` in known instruction files. If found, read and use:
   - **Project type + stack** → skip own detection, use profile values
   - **Quality target** → calibrate severity thresholds (prototype: lenient, enterprise: strict)
   - **Priorities** → order scope execution by user priorities
   - **Constraints** → respect stated constraints (e.g., "keep framework" = flag framework changes as needs_approval)
   - **Current scores** → focus effort on lowest-scoring dimensions

2. **Findings file utilization:** Before scanning a scope, check if `.ds-findings.md` covers that scope:
   - Scope listed + findings present → verify each finding (re-read file:line), use verified ones, skip own scan
   - Scope listed + zero findings → trust the clean result, skip own scan for that scope
   - Scope NOT listed → run own full analysis for that scope
   - Stale git_hash → ignore findings file entirely, run own analysis

3. **Cross-skill context:** When a skill needs information another skill produces:
   - Repo visibility/plan (needed by ds-review, ds-compliance for severity calibration) → query GitHub API directly if ds-repo hasn't run, or read from blueprint profile constraints if available
   - Project type (needed by almost all skills) → prefer blueprint profile, fall back to own detection

#### Utilization Matrix

Each cell specifies WHAT to read and HOW it changes behavior — not just field names.

| Consumer | Profile Field → Behavioral Change | Findings Scopes |
|----------|----------------------------------|-----------------|
| ds-review | **Config.priorities** → order scope execution by priority. **Config.quality** → prototype: skip LOW findings, enterprise: flag all. **Current Scores** → start with lowest-scoring dimensions. **Project Map.Toolchain** → know existing patterns, avoid suggesting incompatible tools. | security, hygiene, types, performance, architecture, patterns |
| ds-fix | **Project Map.Toolchain** → skip tool detection, use stated formatter/linter/typechecker directly. **Type + Stack** → select correct toolchain from references. | — (runs external tools) |
| ds-test | **Ideal Metrics.Coverage** → set coverage threshold. **Project Map.Toolchain** → skip test framework detection. **Current Scores.Testing** → if low, prioritize coverage gaps. | testing |
| ds-docs | **Config.audience** → tailor doc tone (public: user-friendly, developers: technical). **Project Map** → know modules/entry points to document. **Type** → select ideal doc set per project type. | docs |
| ds-compliance | **Config.regulations** → skip regulation detection, use stated frameworks (GDPR, KVKK, etc.) directly. **Config.data** → know data types to scan for (PII, credentials). **Config.audience** → public: stricter compliance. | security, privacy, regulatory |
| ds-deploy | **Config.deploy** → skip target detection, use stated method (Docker, VPS, PaaS). **Project Map.External** → know dependencies to configure (Redis, DB, etc.). **Config.constraints** → respect infra constraints. | deployment, infra, monitoring |
| ds-devops | **Project Map.Toolchain** → skip CI detection, use stated CI platform. **Type + Stack** → select correct pipeline templates. | ci, signing, deps |
| ds-mobile | **Config.data** → know privacy requirements for store compliance. **Config.deploy** → know build pipeline (CI, signing). **Current Scores** → focus on lowest dimensions. | mobile-specific scopes |
| ds-backend | **Project Map.Modules** → know API structure, skip architecture discovery. **Config.data** → know auth/data requirements. **Project Map.External** → know existing DB/cache/queue. | api, db, auth |
| ds-analytics | **Config.data** → know privacy constraints for tracking design. **Config.audience** → context for event taxonomy. **Config.regulations** → compliance requirements for analytics. | analytics, privacy |
| ds-launch | **Config.audience** → know store requirements. **Config.deploy** → know release pipeline. **Type** → select store-specific checklists (mobile vs desktop). | store, release, privacy-labels |
| ds-frontend | **Config.priorities** → order scope execution. **Type + Stack** → select framework-specific patterns. **Current Scores** → focus on lowest-scoring UX dimensions. | tokens, components, states, a11y, responsive, theming |
| ds-solve | **Type + Stack** → research query context. **Config.constraints** → automatic red lines. **Current Scores** → weak dimensions near objective. | — (context consumer, not scope producer) |
| ds-repo | — (producer only) | — |
| ds-blueprint | — (producer only, reads own profile for incremental updates) | — (producer only) |

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
| Installable tool unavailable | Offer to install: show install command, ask "Install and continue?" If accepted → install, re-run. If declined → skip scope, warn in summary. For system-level tools requiring manual install → show instructions, skip scope. |
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

### Concise Expression

Same meaning, fewer tokens. Apply these compression patterns without losing precision or AI model comprehension:

| Pattern | Before | After | Saving |
|---------|--------|-------|--------|
| Phase header + Goal merge | `### Phase N: {Name}\n\n**Goal:** {desc}` | `### Phase N: {Name} — {desc}` | ~40% |
| IDU check inline | 6-8 lines of findings + blueprint check | 2-3 line `**IDU check.** {artifact} → {behavior}; ...` | ~60% |
| Needs-Approval boilerplate | 6-8 lines per skill | 3 lines: modes on one line, gate on next | ~55% |
| Redundant prose removal | "The goal of this phase is to..." | Direct imperative: "Decompose into steps." | ~30% |
| Single-row tables | `\| Col \|\n\|---\|\n\| Val \|` | Inline: `**Col:** Val` | ~60% |

**Rule:** If a phrase can be shortened without changing what the AI model executes, shorten it. Measure by: does the compressed version produce identical behavior?

**Ceiling:** Never compress below readability for a human reviewer. The skill author must still understand the instruction on first read.

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
| **FRC+DSC** | Every finding gets disposition, every scope check enumerated | Most findings tracked, most checks listed | Some findings dropped or checks unlisted | No finding tracking |
| **IDU** | Fully standalone + reads all upstream artifacts when available | Standalone + partial upstream usage | Depends on upstream or ignores it entirely | No inter-skill awareness |

**Score:** 0-24. Target: ≥18 for production skills, ≥14 for MVP skills.

---

## Appendix B: SKILL.md Template

```markdown
# /skill-name

{Pain point or problem statement in one sentence — what currently goes wrong.}

**Skill Name** — One-line description framed as outcome.

## Triggers

- User runs `/skill-name`
- User asks to [action] (e.g., "audit my project", "fix the code")
- [Contextual trigger] (e.g., "after committing changes, suggest PR creation")

## Contract

- [Positive guarantee]: "Always [behavior]"
- [Boundary]: "Only [scope] — [other skill] handles [excluded scope]"
- [Independence]: "Fully functional standalone — zero dependency on other skills. When blueprint profile or .ds-findings.md exist, uses them to skip redundant analysis. When absent, runs own complete analysis with identical quality."
- [FRC]: "Every finding receives a disposition in the summary — zero silent drops"

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

1. **Findings file check:** If `.ds-findings.md` exists with fresh `git_hash`, use relevant findings. Otherwise, run own analysis.
2. Step description [SKIP if condition]
3. Step description [PARALLEL]

**Gate:** [Specific condition]. If fails → [specific recovery].

### Phase 2: Name

**Goal:** [1-line success metric]

1. Step description
2. Step description

**Gate:** [Condition to proceed].

### Phase N-1: Needs-Approval Review [needs_approval > 0]

Items flagged `needs_approval` (cross-module changes, destructive actions, architectural decisions):
- **--auto without --force-approve:** List items, skip them, note in summary
- **--force-approve:** Apply all needs_approval items without asking
- **Interactive:** Present needs_approval items with risk context. Ask: Apply All / Review Each / Skip All

**Gate:** All needs_approval items resolved (applied → `fixed`/`failed`, declined → `skipped`).

### Phase N: Summary

**Mandatory.** Always execute, always produce output — never skip regardless of mode or flags.

**FRC accounting:** Every finding from audit phase appears with a disposition (see Finding Resolution Completeness).

**DSC verification:** Every scope lists which checks passed, failed, or were N/A (see Deterministic Scope Checklist).

Output format:
```
{skill}: {OK|WARN|FAIL} | Fixed: N | Skipped: N | Failed: N | Total: N
```

## Quality Gates

- Every finding cites file:line (not "Don't report without evidence")
- Only modify lines required by the task (not "Don't touch unrelated code")
- Every finding gets a disposition in the summary — zero silent drops (FRC)
- Every scope check is evaluated and accounted for — zero silent omissions (DSC)

## Error Recovery

| Situation | Action |
|-----------|--------|
| Required tool unavailable | Stop with clear error message |
| Installable tool unavailable | Offer to install (show command), ask user. Accepted → install + re-run. Declined → skip scope. |
| Optional tool unavailable | Skip with warning, continue with next phase |
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
