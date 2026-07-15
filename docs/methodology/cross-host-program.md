# Cross-Host Program (v5) — Research-Backed Assessment & Roadmap

**Date:** 2026-07-15 · **Method:** three parallel verified research passes (comparable projects · harness system prompts · model failure modes), each datum ≥2-source-confirmed or explicitly flagged, cross-checked against a local audit of all 28 skills, SKILL-SPEC, install.sh, and measured token footprints.

**Purpose of this document:** record what the research verified, what it changes about the project's design assumptions, and the concrete v5 work program. SKILL-SPEC amendments listed here are **staged, not yet applied** — each lands together with the skill batch that implements it, so spec and skills never drift.

---

## 1. Verified findings

| # | Finding | Evidence | Confidence |
|---|---------|----------|------------|
| F1 | **False completion is a benchmarked, cross-model failure class** — verification failure (not execution failure) accounts for 47–60% of agent failures across Claude Opus 4.6, GPT-5.3-Codex, GLM-5, DeepSeek-V4-Pro; "false finish" attributed by name to Kimi K2.7, GLM 5.2, MiniMax M3 | Terminal-Bench 2.0 taxonomy ([arXiv:2601.11868](https://arxiv.org/abs/2601.11868)) · CLI-Universe ([arXiv:2606.22883](https://arxiv.org/abs/2606.22883)) · Long-Horizon-Terminal-Bench ([arXiv:2607.08964](https://arxiv.org/abs/2607.08964)) | HIGH |
| F2 | **Prose context files alone have low marginal value** — developer-written AGENTS.md-style files: ~+4% success at +19% inference cost, consistent across Claude, GPT, and Qwen | ETH Zurich / LogicStar ([arXiv:2602.11988](https://arxiv.org/abs/2602.11988)) | HIGH |
| F3 | **Curated skills (progressive disclosure) do work** — +16.6pp average pass rate; focused skills (≤3 modules) outperform large bundles | SkillsBench ([arXiv:2602.12670](https://arxiv.org/abs/2602.12670)) | HIGH |
| F4 | **Rule-position bias is model-family-dependent and opposite in direction** — DeepSeek/Qwen/Llama: primacy; Claude/Gemini/Mixtral: recency. No single position is safe for all models | MOSAIC ([arXiv:2601.18554](https://arxiv.org/abs/2601.18554)) · Lost-in-the-Middle | HIGH |
| F5 | **Instruction density degrades compliance** — best frontier models fall to 68% at 500 stacked instructions; smaller/non-reasoning models decay exponentially | IFScale ([arXiv:2507.11538](https://arxiv.org/abs/2507.11538)) | HIGH |
| F6 | **Self-verification is measurably weaker than external checks** — Reflexion ablations show self-review can even hurt (MBPP 80.1%→77.1%); external machine-checkable signals are the proven mitigation | Reflexion (NeurIPS 2023) · Anthropic best-practices docs | HIGH |
| F7 | **Harness asymmetry:** frontier harnesses (Claude Code, Cursor, Codex CLI, Gemini CLI, Copilot) bake read-before-edit / plan / verify into prompts or tool gates AND all gained blocking hook systems in 2025→2026. Thin harnesses (Aider, Cline, Roo, Kilo, OpenCode) leave quality behavior to user rules files — Kilo docs: without build/test commands it "cannot verify its own work"; OpenCode serves a weaker fallback prompt (`qwen.txt`) to open-weight models | Official docs (T1) per harness + leaked-prompt corpus | HIGH (thin-harness thinness: MEDIUM) |
| F8 | **Standards convergence:** AGENTS.md is the cross-tool rules standard (60k+ repos, Linux Foundation/AAIF governance); the Agent Skills spec (`SKILL.md`, agentskills.io) is open and read by ~40 products incl. Codex, Copilot, VS Code, Cursor, Gemini CLI, OpenCode. OpenCode reads `.claude/skills/` directly | agentskills.io spec · agents.md · official changelogs | HIGH (reader-list breadth: MEDIUM) |
| F9 | **Some model failures are structural, not promptable** — DeepSeek V4 rejects `tool_choice="required"` (HTTP 400) and requires `reasoning_content` passback; MiniMax emits malformed tool-call IDs / pseudo tool calls as text | DeepSeek official docs + issue #1376 · AgentEscapeBench, ISO-Bench | HIGH (DeepSeek) / MEDIUM (MiniMax) |
| F10 | **No comparable project combines this repo's triad** — pure-Markdown zero-dependency skills + explicit multi-model independence + a systematic weakness taxonomy (W1–W17). Closest: obra/superpowers (TDD "Iron Law" — one mechanism, one discipline) | Competitive scan (11+ awesome-lists, 9 major projects) | HIGH |
| F11 | **Promote recurring corrections into code, not repeated prompt-time fixes** — "Your agent could fix an issue every time it sees that issue happen, but that uses tokens and might miss cases. If Claude instead writes a lint rule, CI step, or routine, that class of issue can be fully automated forever." Domain knowledge belongs in infrastructure (skills, CLAUDE.md, docs, memories) so agents work "with zero additional context from the prompter" | Boris Cherny (Claude Code creator), [thread, 2026-07-15](https://x.com/bcherny/status/2077460395279692197) | Practitioner authority, single source — strong design signal, converges with F2/F6 |

**Resolved 2026-07-15 (both verified against primary sources):** Claude Code does **not** read AGENTS.md natively — official docs: "Claude Code reads `CLAUDE.md`, not `AGENTS.md`" (workaround: `@AGENTS.md` import or symlink) · Windsurf **was** rebranded to Devin Desktop on 2026-06-02 (Cognition, official Devin FAQ; Cascade EOL 2026-07-01; `.windsurf/rules/` still read, newer builds prefer `.devin/rules/`). **Still unresolved:** OpenCode fallback-prompt exact contents.

## 2. What the findings validate in the current design

- **Modular skills over monolithic rules** (F3, F5) — 28 separate on-demand skills is the right shape; measured always-on cost in Claude Code is only the frontmatter descriptions (~2K tokens for all 28), while full SKILL.md bodies total ~129K.
- **Mechanism over prose** (F2, F6, F7) — ds-quality's deterministic arms (Stop hook / Aider auto-test / pre-commit) are the industry-converged pattern; "done is an external signal" is now documented best practice, not an idiosyncrasy.
- **W-taxonomy relevance** (F1) — W6 Skip Tendency / false completion is the dominant frontier failure mode; the taxonomy is the project's clearest differentiator (F10).

## 3. Gaps

| ID | Gap | Evidence | Cost of leaving it |
|----|-----|----------|--------------------|
| G1 | **Distribution is automated for one host only.** install.sh targets `~/.claude` alone; README tells Cursor/Copilot/Windsurf users to paste SKILL.md into always-on rules files — stale paths (`.cursorrules` is ignored in Cursor Agent mode; `.windsurfrules` superseded by `.windsurf/rules/`) and a token anti-pattern (~4–9K permanent tokens per skill; all 28 ≈ 129K, impossible) | F2, F5, F8 + local measurement | The stated goal (same quality on every host) fails exactly where it matters most |
| G2 | **Only 1 of 28 skills enforces by mechanism.** The other 27 rely on prose gates a weak model can skip — the exact DeepSeek-style false-completion incident the project exists to prevent | F1, F6, F7 | Quality on thin harnesses/open-weight models stays instruction-dependent |
| G3 | **Critical gates sit in one position** (Quality Gates near the end of SKILL.md) — unsafe for primacy-biased families (DeepSeek, Qwen, Llama) | F4 | Silent gate-skipping on the models the project targets |
| G4 | **No compliance eval.** "Works with any model/host" is asserted, never measured | F1 (benchmarks exist as templates) | Claims can't be defended; regressions invisible |
| G5 | **Structural model quirks undocumented** — no adaptation notes for failures no ruleset can fix (F9) | F9 | Users burn time on unfixable prompt debugging |
| G6 | **Host claims stale/overstated** — "5 AI tools, same skill every host" vs reality: 1 host automated, 4 manual with outdated paths; meanwhile the Agent Skills standard made multi-host support *easier* than when the claim was written | F7, F8 | Credibility + missed adoption |

**Explicitly rejected as gaps:** duplicating frontier-harness built-ins (read-before-edit etc.) inside skills is near-zero cost because skills load on demand — pruning them is P2 polish, not a problem; the 28-skill breadth (launch/productize/brief) costs no tokens when uninvoked and stays.

## 4. Program

### P0 — highest leverage — **shipped 2026-07-15** (P0.1 `243351f`, P0.2 `aed603a`, P0.3 ds-quality arms D/E/F)

| # | Item | What it does | Acceptance |
|---|------|--------------|------------|
| P0.1 | **Completion-Evidence band** (spec amendment + all-skill batch) | Standard 3-line rule at BOTH top and bottom of every SKILL.md: a skill may not report done/OK without pasting the machine-checkable evidence (command + output) its gates name; self-assessment is never evidence | Duplicated placement per F4; wording per F1/F6; check-consistency.sh rule added |
| P0.2 | **Multi-host install + corrected docs** | install.sh: OpenCode covered via existing `~/.claude/skills` (zero new code — document it); add Codex/Copilot/Gemini skill-dir targets where the Agent Skills spec is read natively; README install table rewritten with current paths (`.cursor/rules/`, `.windsurf/rules/`, `.github/instructions/`, AGENTS.md pointer) and an explicit warning against pasting full SKILL.md into always-on rules files | `--check` passes per host target; no stale path remains in README |
| P0.3 | **ds-quality arm expansion** | New arms: Copilot hooks (`.github/hooks/*.json`), Gemini CLI hooks, Codex CLI hooks (`PreToolUse`/`Stop`) — all gained blocking hooks in 2025–26 (F7); OpenCode plugin-hook arm marked investigate-first (block semantics unconfirmed) | Each new arm has the Phase-5 green→red→green proof |

### P1

| # | Item | What it does |
|---|------|--------------|
| P1.1 | **Adversarial verify handoff** | Spec pattern (advisory-handoff, standalone-safe): before a skill reports OK on non-trivial changes, a fresh-context reviewer (subagent where the host supports it; self-re-read from files where not) checks the diff against the skill's gates — the worker never grades itself (F6) |
| P1.2 | **Cross-model placement rule** (spec §13 addition) | Codifies F4: safety-critical rules appear first AND last, never middle-only |
| P1.3 | **Mini compliance eval** | 3–5 machine-verifiable tasks per representative skill, bash-scored, runnable under any host/model; measures gate compliance (did phases produce output? was evidence shown?) — turns "works anywhere" into a number |
| P1.4 | **Mechanism-promotion affordance** | When a skill detects the same issue class recurring (≥3 instances — same threshold as W5's systemic-pattern rule), the fix menu offers a "promote to mechanism" option: generate the matching lint rule / CI step / pre-commit check instead of re-fixing one-off, and hand the wiring to ds-quality's gate. Converts token-cost prose corrections into permanent zero-token enforcement (F11) |

### P2

| # | Item | What it does |
|---|------|--------------|
| P2.1 | **Model adaptation notes** (`docs/infrastructure/`) | F9 quirks: DeepSeek `tool_choice`/`reasoning_content`, MiniMax tool-ID/pseudo-calls, Qwen parser flags — harness-level fixes, explicitly out of prompt scope |
| P2.2 | **Skill cards for rules-only hosts** | ~30-line compiled summary (triggers + contract + gates + evidence band) per skill for hosts that only have always-on rules files — bounded token cost instead of full SKILL.md paste |
| P2.3 | **Built-in-behavior pruning** | Trim skill lines that duplicate frontier-harness built-ins where they add no value on thin harnesses either |

## 5. Host matrix (v5 targets)

| Host | Skill ingestion | Enforcement hook (ds-quality arm) | Status |
|------|-----------------|-----------------------------------|--------|
| Claude Code | `~/.claude/skills/` (install.sh) | Stop hook — stop-time | Shipped |
| OpenCode | reads `.claude/skills/` directly — existing install works | plugin hooks (semantics unconfirmed) → investigate; fallback: pre-commit | **New target (v5)** |
| Cursor | Agent Skills reader (verify current build) · `.cursor/rules/` for cards | none confirmed → pre-commit | Docs fix P0.2 |
| GitHub Copilot | Agent Skills reader · `.github/instructions/` for cards · AGENTS.md | `.github/hooks/*.json` — P0.3 | Docs fix P0.2 |
| Windsurf (now Devin Desktop, 2026-06-02) | `.windsurf/rules/` still read; newer builds prefer `.devin/rules/` (cards) | none confirmed → pre-commit | Docs fix P0.2 (rebrand verified — official Devin FAQ) |
| Aider | `--read SKILL.md` / CONVENTIONS.md | auto-lint/auto-test — edit-time | Shipped |
| Codex CLI / Gemini CLI | Agent Skills readers · AGENTS.md · `install.sh --target` | native hooks — ds-quality arms E/F (stop-time), shipped | Candidate targets |

## 6. Per-skill optimization program (v5.1) — ledger

Every skill is individually evaluated against the rubric below, compared with researched same-purpose artifacts (skills/prompts/tools), optimized, CI-verified, and committed per family batch. This table is the resumable progress ledger — update the Status column as batches land.

**Rubric (per skill):** R1 spec-compliance (§9 checklist incl. evidence band) · R2 token-value (every line earns its tokens; prune frontier-builtin duplicates that add nothing on thin harnesses either) · R3 standalone invariant (fully functional installed alone; advisory-handoff only) · R4 gate quality (two-arm gates, machine-checkable pass conditions) · R5 domain currency (2026 best practice + deterministic tools preferred over prose, per family research) · R6 trigger precision (INVOKE/DON'T INVOKE accuracy).

| Batch | Skills | Research artifact | Status |
|-------|--------|-------------------|--------|
| A Ship | ds-commit · ds-pr · ds-devops · ds-deploy · ds-launch · ds-repo | `/tmp/ds-skills-research/family-ship.md` | research running |
| B Improve | ds-review · ds-fix · ds-test · ds-simplify · ds-deps · ds-tune · ds-solve (ds-quality done in P0.3) | `/tmp/ds-skills-research/family-improve.md` | research running |
| C Discover | ds-research · ds-benchmark · ds-blueprint · ds-pipeline | pending | pending |
| D Build | ds-init · ds-backend · ds-frontend · ds-mobile | pending | pending |
| E Document+Comply+Monetize+Track | ds-docs · ds-brief · ds-compliance · ds-productize · ds-issue | pending | pending |
| F Orchestrate | ds-ship · (ds-pipeline in C) | pending | pending |

Raw research artifacts (session-local, not committed): `/tmp/ds-skills-research/{competitors,harnesses,models,toolset-skill,family-*}.md`. Durable summary: knowledge repo, `repos/dev-skills/`.
