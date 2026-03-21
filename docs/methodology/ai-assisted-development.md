# AI-Assisted Development Guide

Research-backed best practices for AI-assisted software development (2025-2026 sources). Covers vibe coding evolution, agent orchestration, security risks, and productive workflows.

---

## 1. Vibe Coding: Definition & Evolution

**Origin:** Andrej Karpathy coined the term (Feb 2025) — "fully give in to the vibes, embrace exponentials, and forget that the code even exists."

**2026 Status:** Karpathy now considers vibe coding "passe" and has moved to "agentic engineering" — orchestrating agents with oversight and scrutiny. The term has been diluted to mean "any AI-assisted development."

**Key Distinction (Simon Willison):** "Not all AI-assisted programming is vibe coding." Vibe coding = no review. AI-assisted engineering = AI generates, human reviews.

Sources:
- [Karpathy original tweet](https://x.com/karpathy/status/1886192184808149383)
- [The New Stack: Vibe coding is passe](https://thenewstack.io/vibe-coding-is-passe/)
- [Simon Willison: Not all AI-assisted programming is vibe coding](https://simonwillison.net/2025/Mar/19/vibe-coding/)

---

## 2. Best Practices for AI-Assisted Development

### Specification Engineering (Critical)
- Front-load effort into detailed specs BEFORE invoking AI
- Addy Osmani calls this "waterfall in 15 minutes"
- If something fails after 2-3 AI attempts, manually code it

### Context Management
- Use config files: `.cursorrules`, `CLAUDE.md`, `.github/copilot-instructions.md`
- Break projects into small, chunked tasks (one function/feature at a time)
- Provide existing code examples so AI learns your patterns

### The 70/30 Rule
- 70% AI: boilerplate, CRUD, test generation, documentation, refactoring
- 30% Human: architecture, algorithms, security-sensitive code (auth, payment, encryption)

### Mandatory Review Workflow
- Never blindly accept AI output — review as if from junior developer
- Veracode 2025: 45% of AI-generated code contains security vulnerabilities
- Use secondary AI model for code review (don't let generator review itself)

### Tool Selection (2026 Consensus)
- **IDE-integrated AI (e.g. Cursor, Copilot):** Daily coding velocity, context-indexed, autocomplete
- **CLI AI (e.g. Claude Code, aider):** Complex refactoring, architecture decisions, large context windows
- Practical split: ~80% IDE-integrated / ~15% CLI / ~5% other

### Version Control Discipline
- Frequent, granular commits as safety checkpoints
- Each AI feature on its own branch with diff reviewed before merge

Sources:
- [Addy Osmani: My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [Graham Mann: How I'm Vibe Coding in 2026](https://grahammann.net/blog/how-im-vibe-coding-2026)
- [DEV Community: Complete Guide to AI-Pair Programming](https://dev.to/pockit_tools/vibe-coding-in-2026-the-complete-guide-to-ai-pair-programming-that-actually-works-42de)

---

## 3. Common Pitfalls & Anti-Patterns

### The "Vibe Coding Hangover" (3-6 Month Crisis)
- Nobody can explain how the code works
- Original prompts lost, architecture is a mystery
- Changing one thing breaks four others ("whack-a-mole")
- Root cause: lack of upfront specification

### Security (2.74x Higher Vulnerability Rate)
- CodeRabbit Dec 2025: AI co-authored code had ~1.7x more "major" issues
- AI optimizes for "making code run" not "making code safe"
- Common: hallucinated bypasses (AI removes auth checks to fix errors)
- Hallucinated packages: attackers register fake packages matching AI hallucinations

### Productivity Paradox
- July 2025 RCT: experienced OSS devs were **19% slower** with AI tools
- Despite predicting 24% speed gains
- Reason: more careful review (correct behavior, slower pace)

### Scaling Limits
- Falls apart with large codebases (>10K LOC)
- AI doesn't track overall design; incompatibilities accumulate

Sources:
- [The New Stack: Vibe coding could cause catastrophic explosions in 2026](https://thenewstack.io/vibe-coding-could-cause-catastrophic-explosions-in-2026/)
- [Towards Data Science: AI Agents and the Security Debt Crisis](https://towardsdatascience.com/the-reality-of-vibe-coding-ai-agents-and-the-security-debt-crisis/)
- [Kaspersky: Security risks of vibe coding](https://www.kaspersky.com/blog/vibe-coding-2025-risks/54584/)

---

## 4. Solo Developer Workflow (2026)

### Core Loop
```
Intent → Spec → Prompt → Generate → Review → Iterate → Ship
```

### Strategic Delegation
- **AI handles:** boilerplate, CRUD, test gen, validation, refactoring, docs
- **You handle:** architecture, security code, novel algorithms, business logic validation, code review

### Practical Workflow
- Use CLI AI for complex refactoring, IDE AI for daily velocity
- Multiple conversation threads for async work
- Minimal prompts (sometimes just error message + "fix this thoroughly")
- Documentation-as-context: AI continuously updates to-do lists
- Use multiple models: stronger model for building, others for review

Sources:
- [Graham Mann: How I'm Vibe Coding in 2026](https://grahammann.net/blog/how-im-vibe-coding-2026)
- [SitePoint: Vibe Coding Workflow Guide](https://www.sitepoint.com/vibe-coding-2026-complete-guide/)

---

## 5. When AI-Assisted Development Works vs Doesn't

### Works Well
- Rapid prototyping & MVPs
- Boilerplate & patterns (CRUD, forms, validation)
- Legacy refactoring
- Learning & throwaway projects
- Strongly-typed UI frameworks (type system catches mistakes)

### Doesn't Work
- Production systems >6 months old without specs
- Security-sensitive paths (auth, payment, encryption)
- Long-term maintenance without architectural oversight
- Complex state management
- Performance-critical optimization

Sources:
- [Sayed Ali Alkamel (Google Dev Expert): Vibe Coding — Senior Dev's Take](https://dev.to/sayed_ali_alkamel/vibe-coding-flutter-the-senior-devs-honest-take-1k0f)
- [Addy Osmani: Vibe coding is not AI-Assisted engineering](https://medium.com/@addyosmani/vibe-coding-is-not-the-same-as-ai-assisted-engineering-3f81088d5b98)

---

## 6. Security: AI-Generated Code Risks

### Statistics
- Veracode 2025: 45% of AI code has security vulnerabilities
- CodeRabbit Dec 2025: 2.74x higher vulnerability rate vs human code

### Common Vulnerability Types
1. Missing input validation
2. Exposed secrets (API keys hardcoded)
3. Broken authentication flows
4. Broken Object-Level Authorization (BOLA)
5. SQL/OS command injection
6. Insecure dependencies
7. Configuration errors (HTTPS, headers)

### Real-World Exploits (2025)
- Lovable Platform (May 2025): Missing RLS exposed 170+ production apps
- CurXecute (CVE-2025-54135): Malicious prompts executed OS commands via Cursor

### Mitigation
- SAST alone insufficient — dynamic testing (DAST) essential
- Every prompt requires re-testing
- Secrets scanning in pre-commit + CI
- Dependency scanning

Sources:
- [Towards Data Science: Security Debt Crisis](https://towardsdatascience.com/the-reality-of-vibe-coding-ai-agents-and-the-security-debt-crisis/)
- [Invicti: Vibe Coding Security Checklist](https://www.invicti.com/blog/web-security/vibe-coding-security-checklist-how-to-secure-ai-generated-apps)

---

## 7. Testing with AI Assistants

### Foundation
- Strong test suite BEFORE using AI (>= 80% coverage)
- Tests are your safety net when AI changes code

### AI Excels At
- Edge case identification
- Boundary condition testing
- Failure mode validation
- Test data generation

### Critical
- Human-reviewed acceptance criteria for AI-generated tests
- Avoid tests that validate incorrect behavior
- Regression suite after every AI change

Sources:
- [testrigor: Top Vibe Testing Tools 2026](https://testrigor.com/blog/vibe-testing-tools/)
- [Google Cloud: Vibe Coding Explained](https://cloud.google.com/discover/what-is-vibe-coding)

---

## 8. Experienced vs Beginner AI Usage

### Experienced Dev Pattern (Addy Osmani)
1. Waterfall planning in 15 minutes
2. Chunked, incremental work
3. Context packing (supply existing code, docs, constraints)
4. Human accountability (review all code, run tests, explain logic)
5. Version control discipline
6. Strategic model selection

### Beginner Anti-Patterns
- Treating AI as autonomous code generator
- Skipping planning
- Accepting all suggestions without review
- Using AI for security code without domain knowledge

Sources:
- [Addy Osmani: My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/)
- [Stack Overflow: Developers with AI assistants need pair programming model](https://stackoverflow.blog/2024/04/03/developers-with-ai-assistants-need-to-follow-the-pair-programming-model/)

---

## 9. Agent Orchestration Patterns (2026)

### Multi-Agent Workflows
- Separate agents for analysis, implementation, review, testing
- Use findings files or structured artifacts for inter-agent communication
- Human-in-the-loop for architectural decisions

### Context Window Management
- Progressive disclosure: load only relevant context per task
- Reference files loaded on demand, not upfront
- Skill-based decomposition: each skill handles one concern

### Quality Gates Between Agents
- Every agent output verified before next agent consumes it
- Automated quality checks (lint, type-check, test) between steps
- Human approval gates for irreversible actions (deploy, publish, delete)

### Effective Prompt Patterns
- Specification > conversation: write specs, not chat
- Include examples of desired output format
- Constrain output: positive framing ("only modify X") over negative ("don't touch Y")
- Provide existing code context so AI matches project patterns
