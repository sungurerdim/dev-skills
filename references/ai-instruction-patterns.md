# AI Instruction Patterns Reference

Best practices for writing effective AI agent/model instructions, compiled from 2025-2026 research.

## Sources

**Anthropic official (2026):** [Prompting Best Practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices) · [Context Engineering for Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) · [Managed Agents](https://www.anthropic.com/engineering/managed-agents) · [Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) · [Prompt Caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)

**Academic (2025-2026):** [Wharton CoT Report 2025](https://gail.wharton.upenn.edu/research-and-insights/tech-report-chain-of-thought/) · [RDS+/CRDS arXiv 2602.13773](https://arxiv.org/abs/2602.13773) · [Process Reward Models ACL 2025](https://arxiv.org/abs/2501.07301) · [ThinkPRM arXiv 2504.16828](https://arxiv.org/pdf/2504.16828) · [SHIELDA arXiv 2508.07935](https://arxiv.org/html/2508.07935v1) · [Focused CoT ICLR 2025](https://arxiv.org/pdf/2511.22176) · [Context Length Hurts arXiv 2510.05381](https://arxiv.org/html/2510.05381v1) · [Multi-Agent Orchestration arXiv 2511.15755](https://arxiv.org/abs/2511.15755) · [MAS Survey arXiv 2601.13671](https://arxiv.org/html/2601.13671v1) · [Utility-Guided Orchestration arXiv 2603.19896](https://arxiv.org/html/2603.19896) · [Many-Tier Hierarchy arXiv 2604.09443](https://arxiv.org/html/2604.09443v3) · [Instruction Hierarchy arXiv 2404.13208](https://arxiv.org/html/2404.13208v1) · [Reasoning Theater arXiv 2603.05488](https://arxiv.org/html/2603.05488v2) · [SpecBench arXiv 2605.21384](https://arxiv.org/abs/2605.21384) · [SWE-ABS arXiv 2603.00520](https://arxiv.org/abs/2603.00520) · [BrokenMath arXiv 2510.04721](https://arxiv.org/abs/2510.04721) · [AI Review Authorship Bias arXiv 2603.18740](https://arxiv.org/abs/2603.18740) · [MASFT arXiv 2503.13657](https://arxiv.org/abs/2503.13657)

**Industry/security (2025-2026):** [Lakera Prompt Engineering Guide 2026](https://www.lakera.ai/blog/prompt-engineering-guide) · [Lakera Agent Attacks Q4 2025](https://www.lakera.ai/blog/the-year-of-the-agent-what-recent-attacks-revealed-in-q4-2025-and-what-it-means-for-2026) · [OWASP LLM01:2025](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) · [OWASP Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html) · [OpenAI: Agents vs Injection](https://openai.com/index/designing-agents-to-resist-prompt-injection/) · [Chroma Context Rot 2025](https://www.trychroma.com/context-rot) · [Databricks Structured Outputs 2025](https://www.databricks.com/blog/introducing-structured-outputs-for-batch-and-agent-workflows) · [Preventing AI Agent Drift](https://www.getmaxim.ai/articles/a-comprehensive-guide-to-preventing-ai-agent-drift-over-time/)

---

## 1. Constraint Enforcement

Negative constraints ("Don't...") are less reliable than positive framing. The original claim (Lakera 2026) that hard negatives fail ~5%, soft negatives ~10-15%, positive framing ~2-3% is **[unverified — no quantified failure-rate data found in Lakera 2026 guide; guide confirms qualitative pattern without citing those percentages]**. The qualitative finding holds: Anthropic's official 2026 docs confirm positive framing consistently outperforms prohibitions for Claude 4.x.

Overloading >3 constraints that conflict with positive goals causes accuracy drops (qualitative; no updated percentage found in 2026 sources).

| Fails | Works |
|-------|-------|
| "Do not hallucinate APIs" | "Verify each API exists before using. If uncertain, state 'not verified' and ask." |
| "Don't modify untouched code" | "Only modify lines directly required by the task." |
| "Never skip steps" | "Every phase must produce output before proceeding." |

**Rules:**
- Frame 70%+ of instructions positively (what to do)
- Reserve hard negatives for safety-critical rules only (max 5)
- Soft negatives for preferences: "prefer X over Y" or "avoid Y when X is available"
- Avoid aggressive capitalization ("CRITICAL!", "YOU MUST NEVER") — overtriggers model, produces worse outputs (Anthropic Official Docs 2026)

**Placement:** Front-load critical constraints in lines 1-5. Repeat at phase boundaries for long sessions.

**Source:** Lakera Prompt Engineering Guide 2026, Anthropic Official Docs 2026 — Last verified: 2026-04

## 2. Structured Phases with Gates

```
### Phase N: Name
**Goal:** [1-line success metric]

1. Step
2. Step

**Gate:** [Condition to proceed]. If fails → [recovery action].
```

Gates prevent forward drift with incomplete state. 60%+ higher success rate vs ungated workflows — **[unverified — original claim from SHIELDA arXiv 2025; no 2026 replication found; treat as directional]**. Process-level supervision (step-by-step verification) outperforms outcome-only supervision (Process Reward Models, ACL 2025; ThinkPRM arXiv 2025).

**2026 update — ThinkPRM findings:** Generative step-verifiers outperform discriminative PRMs even with 99% fewer process labels. ThinkPRM beats outcome-only baselines by 8% on GPQA-Diamond using chain-of-thought verification at each step. Implication for skill design: verification phases that ask the model to reason through each step's validity outperform binary pass/fail checks.

**Enhancement:** Add outcome scoring at each gate — not just pass/fail, but quality indicators (findings count, confidence level). Separate the agent that does the work from the agent that judges it (Anthropic three-agent harness, 2026): agents overrate their own outputs on subjective tasks.

**Source:** SHIELDA (arXiv), Process Reward Models (ACL 2025), ThinkPRM (arXiv 2025), Anthropic Harness Design 2026 — Last verified: 2026-04

## 3. Adaptive Thinking (replaces forced CoT)

**Confirmed 2025 finding (Wharton GenAI Labs, verified 2026):** Forced chain-of-thought adds only 2.9% accuracy for o3-mini and 3.1% for o4-mini — reasoning-capable models. Cost: 20-80% more tokens, 10-20 seconds latency. Non-reasoning models still benefit: Gemini Flash 2.0 +13.5%, Sonnet 3.5 +11.7%.

**2026 update — Effort parameter (Claude 4.x):** Use the `effort` API parameter instead of prompting for reasoning depth. Levels: `low`, `medium`, `high`, `xhigh` (best for coding/agentic), `max`. Claude Opus 4.7 respects effort strictly; shallow reasoning on complex problems → raise effort level, not prompt complexity. Explicit reasoning prompt only needed at `low` effort: `"This task involves multi-step reasoning. Think carefully before responding."`

**2026 update — Reasoning theater (arXiv 2603.05488):** Visible CoT may not reflect actual model reasoning. Models produce plausible-looking chains diverging from internal computation. Do not use visible CoT as a trust signal; use output quality metrics.

| Instead of | Write |
|-----------|-------|
| "Think through this step-by-step before answering" | Set `effort: xhigh` in API params |
| "Reason carefully about each option" | "Compare options against these criteria: [list]" |
| "Let me think about this..." | Let model decide; override only with effort param |

**When to prompt reasoning explicitly (low-effort configs only):**
- Non-reasoning models (Haiku) on complex tasks: still beneficial (+11-13%)
- Multi-criteria decisions with >3 trade-offs
- Novel problems outside training distribution

**Source:** Wharton GenAI Labs 2025, Anthropic Official Docs 2026, arXiv 2603.05488 — Last verified: 2026-04

## 4. Example Density

**Confirmed (Anthropic Official Docs 2026, RDS+/CRDS arXiv 2602.13773 Feb 2026):** 3-5 examples optimal. Well-selected small subsets outperform large datasets in instruction tuning (CRDS framework confirms RDS+ finding: semantic redundancy in embeddings means more examples ≠ better). Most recent example LAST (recency bias leveraged).

**2026 note — Many-shot regime:** As context windows expand, many-shot (hundreds of examples) shows meaningful gains for complex reasoning tasks. For standard agent skills, 3-5 remains the sweet spot. For specialized reasoning harnesses with >100k token budgets, consider many-shot.

**Pattern:**
1. Happy path case
2. Edge case showing constraint
3. Error recovery case

**Anti-pattern:** Examples clustering in same domain/error type — semantic redundancy wastes tokens. Watch majority-label bias: if 3 of 4 examples share same output class, model defaults to that class for ambiguous inputs.

**Source:** Anthropic Official Docs 2026, RDS+/CRDS (arXiv 2602.13773), Many-Shot ICL (Google/OpenReview 2404.11018) — Last verified: 2026-04

## 5. Token Efficiency and Context Engineering

**2025-2026 finding — Context rot (Chroma 2025, verified 2026):** Performance degrades non-linearly as context grows. Chroma tested 18 frontier models; every one degrades. Degradation is not always gradual — performance can drop sharply and unpredictably before the context limit. Advertised context windows are ceilings, not performance guarantees: models claiming 200K context degrade noticeably around 130K tokens in practice.

**2025 finding (arXiv 2510.05381, confirmed 2026):** Even with perfect retrieval, accuracy drops 13.9-85% as input grows within stated context limits. Llama-3.1-8B loses 24.2% accuracy despite finding all relevant tokens. Implication: shrinking context is more valuable than maximizing it.

**"Lost in the middle" (confirmed 2026):** Accuracy drops >30% when relevant content is in the middle vs start/end. Primacy and recency biases are consistent across all tested models. Place critical constraints at the start and queries at the end.

| Format | Token Efficiency |
|--------|-----------------|
| Tables | Best for structured data |
| Numbered lists | Best for sequences |
| XML/markdown tags | Good for conditional sections |
| Prose paragraphs | Worst — avoid for rules |

**Performance guidelines (2025-2026):**
- Instruction degradation onset: model-dependent, not a fixed 3,000-token threshold — **[original 3k claim unverified in 2026; Anthropic context engineering docs deliberately avoid prescribing a number]**
- Sweet spot for narrative instructions: 150-300 words
- Data/reference sections: place at TOP (before query)
- Query/instructions at END improve response quality by up to 30% (confirmed, Anthropic Official Docs 2026)
- 1M-token practical ceiling: performance degrades meaningfully past ~1M tokens regardless of model's stated maximum

**Optimization priorities:**
1. Remove redundant preamble: ~10% savings
2. Use shorthand for repeated concepts: ~15% savings
3. Compress examples (outcome, not full trace): ~20% savings
4. Prompt caching for repeated instructions: 90% cost reduction on cache hits (0.1× base price; break-even at 1-2 reads for 5-min TTL, Anthropic 2026)

**2026 caching note:** Default TTL changed from 1 hour to 5 minutes in April 2026. Extended 1-hour caching available at 2× write cost. For long-running agents with stable system prompts, explicitly set extended TTL.

**Source:** CodeSignal 2025, Anthropic Official Docs 2026, Chroma Context Rot 2025, arXiv 2510.05381, Anthropic Prompt Caching Docs 2026 — Last verified: 2026-04

## 6. Behavioral Anchoring & State Persistence

**Instruction decay claim ("~50 turns"):** **[unverified — no 2026 source confirms this specific number; qualitative pattern holds but exact threshold is model- and context-dependent]**.

Confirmed prevention strategies (Anthropic Context Engineering 2026, Harness Design 2026):

- Write progress to structured external artifact (JSON, markdown) after each phase — not just in-memory
- Repeat core constraints at phase boundaries
- Use structured progress notes: completed / current / next / blocked
- Persistent state files survive context compaction; conversation memory does not
- For multi-session agents: commit to git after each feature — provides rollback and clean session handoff

**2026 update — Context compaction vs reset (Anthropic Managed Agents 2026):**
- **Compaction:** Summarizes earlier context in place; preserves continuity; 1,000-2,000 tokens of distilled output typical; context anxiety can still persist
- **Context reset:** Clean slate for next agent; requires handoff artifact with enough state to resume; eliminates context anxiety; adds orchestration overhead
- Claude Sonnet 4.5 showed "context anxiety" (premature task wrap-up) requiring resets; Claude Opus 4.5+ eliminated this behavior; harness assumptions go stale as models improve — audit regularly

**State file pattern:**
```json
{
  "skill": "ds-review",
  "phase": 3,
  "completed": ["setup", "analyze"],
  "current": "reporting",
  "blocked": [],
  "findings": [],
  "git_hash": "abc123"
}
```

**Source:** Anthropic Context Engineering 2026, SHIELDA (arXiv), Anthropic Managed Agents 2026 — Last verified: 2026-04

## 7. Claude 4.x Literal Interpretation

**Confirmed (Anthropic Official Docs 2026, Claude Opus 4.7 release):** Claude 4.x takes instructions literally. Claude Opus 4.7 is more literal than 4.6, especially at lower effort levels. It will not silently generalize an instruction from one item to another, and will not infer requests not made.

**Practical implications for 2026:**
- Scope must be stated explicitly: "Apply this formatting to every section, not just the first one"
- Omitted details = omitted from output
- At `low`/`medium` effort, model scopes work to exactly what was asked — moderately complex tasks risk under-thinking
- Code review harnesses tuned for earlier models may show reduced recall on Claude Opus 4.7: the model follows filtering instructions more faithfully, not fewer bugs found but fewer reported below the stated bar

| Vague (fails) | Explicit (works) |
|---------------|-----------------|
| "Review the code" | "Review for security, performance, and missing error handling. Report each finding with file:line, severity, and fix suggestion." |
| "Fix the tests" | "Fix failing tests by correcting test logic. Preserve assertion strength. If a test validates wrong behavior, fix the test." |
| "Be conservative" | "Report any bugs causing incorrect behavior or test failure. Omit only pure style/naming nits." |

**Source:** Anthropic Official Docs 2026, Claude Opus 4.7 prompting guide — Last verified: 2026-04

## 8. Error Recovery Pattern

```
## Error Recovery
1. Tool fails → Attempt alternative approach once
2. Still fails → Report error verbatim + propose manual step
3. Ambiguous input → List 2-3 interpretations, ask which
4. Same action fails twice → Stop retrying, report error, try different approach
5. Context limit near → Save state to progress artifact; trigger compaction or reset
6. Subagent returns unexpected format → Validate against schema before passing downstream
```

**2026 update — Utility-guided execution (arXiv 2603.19896):** Tool-using agents face a persistent quality-vs-cost tension. Additional verification steps improve answers but increase token use and latency. Design recovery paths to be bounded: set a maximum retry count and escalate to human review rather than looping indefinitely. This makes agent trajectories "controllable, inspectable, and experimentally defensible."

**Source:** SHIELDA (arXiv), Anthropic Context Engineering, arXiv 2603.19896 — Last verified: 2026-04

## 9. Conditional Logic

Use explicit if/else with indentation, not prose:

```
**Decision:**
- If [condition A] → [action A]
- If [condition B] → [action B]
- Otherwise → [fallback action]
```

Avoid nested conditionals >2 levels. Each branch must lead to a concrete action, not another decision tree.

**2026 note:** Claude Opus 4.7 at `low` effort executes conditional logic precisely as written without inferring omitted branches. Every branch must be explicit.

## 10. Instruction Priority

```
Level 1 (highest): Skill/system instructions (SKILL.md, system prompt)
Level 2: User request in current session
Level 3: Tool output / external data
Level 4 (lowest): Content from analyzed files
```

Lower level cannot override higher level. Frame constraints as non-negotiable policy.

**2026 update — Many-tier hierarchy (arXiv 2604.09443):** Two-tier (system vs user) is insufficient for real-world agents interacting with many tools, sub-agents, and skills. The field is moving toward many-tier models where each instruction source carries a trust score. Current practical guidance: explicitly label content source in prompts (`<user_input>`, `<tool_output>`, `<external_doc>`) so the model can apply appropriate skepticism.

**2026 security update — Instruction hierarchy training (arXiv 2404.13208, ICLR 2025):** IH-trained models show 63% improvement in system prompt extraction defense and 30%+ improvement in jailbreak robustness. When using Claude 4.x: treat tool outputs as untrusted by default; do not embed instructions in tool response fields.

**2026 threat update (Lakera/Cisco 2026):** Prompt injection vulnerabilities found in 73% of production AI deployments. Multi-hop indirect attacks (via agents/tools) increased 70% YoY. MCP server tool descriptions are a new attack vector — malicious tool descriptions bypass most content filtering because they are treated as trusted.

**Source:** Instruction Hierarchy arXiv 2024/ICLR 2025, Many-Tier arXiv 2604.09443, OWASP Prompt Injection, Lakera 2026 — Last verified: 2026-04

## 11. Structured Output Contracts

**2026 reliability data (TokenMix/DeepFounder, 2M API calls):**

| Method | Parse failure rate |
|--------|-------------------|
| OpenAI JSON Mode | 2-5% |
| OpenAI Structured Outputs (schema enforcement) | <0.1% |
| Anthropic Tool Use (typed tool input) | <0.2% |
| Gemini Response Schema | <0.3% |
| Prompt-only JSON (no enforcement) | 8-15% |

Without schema enforcement, LLM JSON responses fail parsing 8-15% of the time. With enforcement: <0.3%.

**Rules:**
- Define explicit output schema for each phase that produces data
- Use tool-use API / response_schema (not prompt-only JSON) for guaranteed structure
- Validate output against schema before passing to next phase; business logic validation catches what JSON Schema cannot
- Summary phase: use standard format line (`skill: {OK|WARN|FAIL} | Fixed: N | ...`)

**Source:** Anthropic Structured Outputs Docs 2026, Databricks 2025, TokenMix/DeepFounder 2026 — Last verified: 2026-04

## 12. Positive Framing Summary

Every rule should answer: "What should I DO?" not "What should I NOT do?"

| Instead of | Write |
|-----------|-------|
| "Don't create unnecessary files" | "Only create files explicitly required by the task" |
| "Don't guess" | "State uncertainty explicitly. Ask when unsure." |
| "Never flag test fixtures" | "Skip: test fixtures, `# noqa`, `# intentional`, platform guards" |

**Quantified:** Hard negatives fail ~5%, soft negatives ~10-15%, positive framing ~2-3% failure — **[unverified; qualitative finding confirmed by Anthropic 2026, but these specific percentages have no traceable 2026 primary source]**. Anthropic's official docs confirm positive framing is more reliable, but do not publish failure rate benchmarks.

**Source:** Lakera 2026 (qualitative), Anthropic Official Docs 2026 — Last verified: 2026-04

---

## 13. Context Engineering for Long-Running Agents [NEW — 2026]

Context engineering supersedes prompt engineering as the primary lever for agent reliability. The question shifts from "what words" to "what configuration of tokens maximizes desired behavior across this full context window."

**Core principle (Anthropic Engineering 2026):** Find the smallest set of high-signal tokens that maximize the likelihood of desired outcomes. More tokens ≠ better performance. Every token competes for model attention.

**Just-in-time loading:** Load data at runtime when needed rather than front-loading everything. Maintain lightweight references; resolve them dynamically. Claude Code example: retain only the five most recently accessed files during context resets.

**Context ordering (Anthropic recommendation):**
1. System instructions
2. Relevant memory / persistent state
3. Tool definitions
4. Conversation/task history
5. Query (END of prompt)

**Tool design for efficiency:** Tools should return token-efficient information and encourage efficient agent behaviors. Verbose tool outputs (e.g., full file contents when only a line range is needed) are a primary source of context bloat.

**Multi-session pattern (Anthropic Harness Design 2026):**
- Initializer agent (first session): creates feature list (JSON), progress file, init script
- Coding agent (subsequent sessions): reads progress file, runs init script, makes incremental progress, commits after each feature
- Evaluator agent (separate): judges output quality; reduces self-overrating bias in subjective tasks

**Source:** Anthropic Context Engineering 2026, Anthropic Harness Design 2026, Anthropic Managed Agents 2026 — Last verified: 2026-04

## 14. Multi-Agent Coordination Patterns [NEW — 2026]

Single-agent LLMs produce vague or unusable recommendations in complex decision support. Multi-agent orchestration achieves deterministic quality through specialization and separation of concerns.

**Key findings (arXiv 2511.15755, 348 trials):**
- Multi-agent orchestration: 100% actionable recommendation rate
- Single-agent: 1.7% actionable recommendation rate
- Quality variance: zero across all multi-agent trials (enables SLA commitments)
- Latency similar (~40s) — architectural value is deterministic quality, not speed

**Emerging patterns (arXiv 2601.13671, 2601.03328 — Jan 2026):**
- **A2A + MCP hybrid:** Agent-to-Agent protocol combined with Model Context Protocol for multimodal, adaptive enterprise coordination
- **Dynamic orchestration** outperforms rigid rule-based workflows; agents can align to domain-specific constraints at runtime
- **Planner/Generator/Evaluator triad** (Anthropic three-agent harness 2026): proven pattern for long-horizon coding; evaluator is calibrated with few-shot scoring criteria; separating judgment from execution is the primary lever against self-overrating

**Persistent challenges (arXiv 2601.07136 — 42K commits, 4.7K issues across 8 MAS systems):** bugs 22%, infrastructure 14%, agent coordination 10%. Hallucination and interpretability remain critical barriers in regulated domains.

**Utility-guided orchestration (arXiv 2603.19896):** Each tool invocation should be governed by an explicit utility estimate (expected quality gain vs. token/latency cost). Free-form ReAct agents over-execute; fixed workflows under-adapt. Utility guidance makes agent paths controllable and auditable.

**Source:** arXiv 2511.15755, 2601.13671, 2601.03328, 2601.07136, 2603.19896, Anthropic Managed Agents 2026 — Last verified: 2026-04

## 15. Prompt Injection Defense (2026) [UPDATED SECTION — formerly embedded in §10]

Prompt injection is OWASP #1 LLM vulnerability in 2026. Present in 73% of audited production deployments (Cisco State of AI Security 2026). No complete solution exists — all defenses are mitigations.

**2026-specific attack vectors:**
- **MCP server exploitation:** Malicious tool descriptions bypass content filters because they are processed as trusted content
- **RAG poisoning:** Documents injected into knowledge base embed instructions executed at query time
- **Multi-hop indirect injection:** Via agent chains; increased 70% YoY in 2025-2026
- **Multimodal injection:** Malicious prompts in image metadata, audio, or video files
- **Tool manipulation:** Forged tool outputs injecting false reasoning steps into agent memory

**Defense layers (OWASP 2026, ranked by impact):**
1. Least privilege — restrict agent tool access to minimum required
2. Segregate external content — clearly label and isolate untrusted inputs (`<external_content>`, `<user_input>`)
3. Human-in-the-loop for privileged actions (sending email, executing code, payment)
4. Input validation before LLM sees it
5. Output filtering post-LLM
6. Instruction hierarchy enforcement (see §10)
7. Adversarial testing / red-teaming — regularly, not just at launch

**Architectural note:** True injection prevention requires hardware-style separation between instruction and data token streams — not achievable with current transformer architectures. Current defenses reduce blast radius; they do not eliminate the attack class.

**Source:** OWASP LLM01:2025, OWASP Prompt Injection Prevention Cheat Sheet, Lakera Agent Attacks 2026, Cisco AI Security 2026 — Last verified: 2026-04

## 16. AI Code-Quality Failure Modes & Mitigating Patterns [NEW — 2026]

Recent research isolates failure modes the patterns above must actively counter. Each pairs the failure with its mitigating pattern.

- **Reward hacking / specification gaming** — the model satisfies the literal test or metric while violating intent (SWE-ABS: 19.78% of "solved" tasks semantically wrong; SpecBench: gap widens +28pp with 10× more code). *Pattern:* verify against described intent + a held-out case the model hasn't seen; never special-case test inputs (§1).
- **Sycophancy / authority deference** — the model drops a correct position under pushback or defers to authority cues (BrokenMath: GPT-5 29% sycophantic; redacting AI-authorship cues recovered 68.75% of missed review findings). *Pattern:* on pushback, re-verify from source; judge artifacts by behavior, not claims.
- **Slopsquatting / dependency hallucination** — ~19.7% of LLM-suggested packages don't exist; attackers pre-register the names (USENIX 2025; CSA 2026). *Pattern:* before importing, confirm the package exists in the registry with real age + downloads and is pinned in the lockfile.
- **Context rot** — accuracy degrades as input grows even within the window (Chroma 18-model study; see §5, §13). *Pattern:* front-load constraints, re-ground from files every ~20 steps, summarize don't accumulate.
- **Subagent / handoff failure** — specs and results distort across delegation; trusting a subagent's return as ground truth compounds errors (MASFT, 1,600+ traces; see §14). *Pattern:* explicit handoff contract + verify returned data against source before acting.

**Source:** SWE-ABS arXiv 2603.00520, SpecBench arXiv 2605.21384, BrokenMath arXiv 2510.04721, arXiv 2603.18740, USENIX Security '25, CSA 2026, Chroma 2025, MASFT arXiv 2503.13657 — Last verified: 2026-06

---

## Changelog — Changes Since Previous Version (2025-2026)

**Kept:** §1 (failure-% unverified), §2 (60% claim marked directional), §3 (Wharton 2.9/3.1% confirmed), §4 (3-5 examples confirmed), §7 (extended for Opus 4.7), §9 (unchanged), §11 (new failure-rate table added), §12 (unverified disclaimer added).

**Updated:** §3 added effort param guidance + reasoning-theater finding. §5 removed fixed 3k-token threshold (no 2026 source); added context rot framing, 1M-token ceiling, caching TTL change. §6 marked 50-turn claim unverified; added compaction-vs-reset and context-anxiety findings. §8 added utility-guided execution bound. §10 added many-tier hierarchy, MCP injection vector, updated statistics. §11 replaced qualitative claim with failure-rate table.

**Added:** §13 Context Engineering for Long-Running Agents. §14 Multi-Agent Coordination Patterns. §15 Prompt Injection Defense (expanded from §10 note to full section). §16 AI Code-Quality Failure Modes & Mitigating Patterns (reward hacking, sycophancy, slopsquatting, context rot, subagent handoff).

**Removed claims (no 2026 source found):** "3,000-token degradation threshold" — replaced with context rot framing. "Instruction decay after ~50 turns" — marked unverified. Virtualization Review 2025 source — removed; pattern confirmed by Anthropic 2026 docs instead.

**Deprecated:** None.
