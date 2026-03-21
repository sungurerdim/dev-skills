# Solo Developer Workflow Guide

A practical, opinionated system for shipping software alone — optimized for AI-assisted development in 2025-2026.

---

## Philosophy: Systems Over Heroics

Solo development is not about working harder. It is about building systems that make consistent output inevitable.

Three principles govern everything:

1. **Simplicity wins.** Every tool, process, or abstraction you add must earn its place. If it does not reduce friction or increase output, remove it.
2. **Shipping is the unit of progress.** Code that is not deployed is inventory, not value. Optimize for small, frequent releases over large, perfect ones.
3. **Sustainable pace is non-negotiable.** Heroic sprints create debt — technical, physical, and mental. A solo developer who burns out has zero bus factor recovery.

The goal is not to simulate a team. It is to exploit the advantages of working alone: zero coordination overhead, instant decision-making, and full-stack context in one brain.

---

## Project Management for One

### GitHub Issues as Single Source of Truth

Do not scatter tasks across Notion, Todoist, sticky notes, and your head. Use GitHub Issues for everything:

- **Bug reports** — label: `bug`, include reproduction steps
- **Feature requests** — label: `feature`, include acceptance criteria
- **Technical debt** — label: `debt`, include impact description
- **Research spikes** — label: `spike`, timebox in the title (e.g., "Spike: evaluate auth libraries [2h]")

### Milestone-Based Delivery

Organize issues into milestones that represent shippable increments:

| Milestone | Scope | Duration |
|-----------|-------|----------|
| v0.1 — Walking skeleton | Core flow works end-to-end | 1-2 weeks |
| v0.2 — MVP | Minimum feature set for first users | 2-4 weeks |
| v0.3 — Hardening | Error handling, edge cases, docs | 1-2 weeks |
| v1.0 — Launch | Polish, performance, public release | 1-2 weeks |

Close milestones on time. Unfinished issues move forward — they do not block the milestone.

---

## Task Prioritization

Use three frameworks for three different decisions.

### ICE Scoring — What to Build Next

Score each feature/task on Impact, Confidence, and Ease (1-10 each). Multiply for a composite score.

| Task | Impact | Confidence | Ease | ICE Score |
|------|--------|------------|------|-----------|
| Add OAuth login | 9 | 8 | 4 | 288 |
| Dark mode support | 5 | 7 | 6 | 210 |
| Refactor DB layer | 7 | 9 | 3 | 189 |
| Add export to CSV | 6 | 6 | 8 | 288 |
| Custom email templates | 4 | 5 | 5 | 100 |

Work top-down. Re-score weekly as context changes.

### MoSCoW — Scope Control for a Release

Before each milestone, classify every issue:

- **Must have** — The release is broken without it.
- **Should have** — Expected by users but can ship without.
- **Could have** — Nice to have, only if time permits.
- **Won't have** — Explicitly out of scope for this release.

Write the Won't Have list. It is more important than the Must Have list because it prevents scope creep.

### Eisenhower Matrix — Handling Interruptions

When something unexpected lands in your lap:

| | Urgent | Not Urgent |
|---|--------|------------|
| **Important** | Do now (production bug) | Schedule (architecture improvement) |
| **Not Important** | Delegate to automation or decline | Drop it |

As a solo developer, "delegate" means automate or defer to a GitHub Issue for later.

---

## Shipping Cadence

### The 80% Rule

Ship when a feature is 80% polished. The last 20% of polish takes 80% of the time and is often invisible to users. Ship, get feedback, then decide if that 20% matters.

### Weekly Release Rhythm

- **Monday-Thursday:** Build
- **Friday morning:** Cut release, deploy to staging
- **Friday afternoon:** Smoke test, deploy to production

If Friday's release is not ready, it ships next Friday. Do not crunch over the weekend.

### MVP Mindset

For every feature, ask: "What is the smallest version of this that delivers value?" Build that. Then stop. Wait for user feedback before expanding scope.

---

## Time Management

### Deep Work Blocks — Daily Structure

| Block | Time | Activity |
|-------|------|----------|
| Morning focus | 09:00-12:00 | Deep work: core feature development |
| Midday break | 12:00-13:00 | Lunch, walk, no screens |
| Afternoon build | 13:00-15:30 | Implementation, testing, reviews |
| Admin block | 15:30-16:30 | Issues triage, communication, planning |
| Learning/debt | 16:30-17:30 | Tech debt, learning, experimentation |

Protect the morning block ruthlessly. No email, no Slack, no meetings before noon.

### Timeboxing — Recommended Durations

| Activity | Timebox |
|----------|---------|
| Bug investigation | 30 min before asking for help or escalating |
| Research spike | 2 hours max, then decide |
| Code review (self) | 15 min per PR |
| Architecture decision | 1 hour of analysis, then commit |
| Dependency evaluation | 30 min per candidate |

If the timebox expires without resolution, the answer is "not now" — file an issue and move on.

### Batching Communication

Check and respond to email/messages twice daily: once at midday, once at end of day. Disable all push notifications during focus blocks. Async communication is your superpower — use it.

---

## Decision-Making

### Build vs Buy vs Skip

Apply this hierarchy for every technical decision:

1. **Skip** — Do you actually need this? If the answer is not an obvious yes, skip it entirely.
2. **Buy/Use** — Is there a maintained library, SaaS, or managed service? Use it.
3. **Build** — Only if nothing exists, or existing solutions have deal-breaking limitations.

### The 3-Year TCO Test

Before building anything custom, estimate the total cost of ownership over 3 years:

- **Build:** Development time + maintenance time + opportunity cost of features not built
- **Buy:** License cost + integration time + migration risk if vendor dies

If build TCO exceeds 3x buy TCO, buy. Solo developers underestimate maintenance burden consistently.

### Reversible vs Irreversible Decisions

- **Reversible** (most decisions): Decide in under 10 minutes. Database column name, UI layout, library choice for a non-core feature. Move fast, change later if wrong.
- **Irreversible** (few decisions): Take a full day. Public API contracts, database schema for core entities, pricing model. These deserve an ADR (see Documentation section).

---

## Technical Debt Management

### The 20% Budget Rule

Allocate 20% of your engineering time to debt reduction — roughly one day per week. This is not optional. Research shows developers spend 23-33% of their time on debt whether they plan for it or not. Planning makes that time productive instead of reactive.

### Debt Classification

| Type | Example | Priority | Action |
|------|---------|----------|--------|
| **Reckless deliberate** | "We don't have time for tests" | CRITICAL | Schedule immediately |
| **Prudent deliberate** | "Ship now, refactor before v2" | HIGH | Track with deadline |
| **Reckless inadvertent** | "What's a connection pool?" | HIGH | Learn, then fix |
| **Prudent inadvertent** | "Now we know what the design should have been" | MEDIUM | Refactor when touching that area |

Classification based on Martin Fowler's Technical Debt Quadrant.

### Flag It to Fix It

Never silently work around bad code. When you encounter debt:

1. Add a `// DEBT:` comment with a one-line explanation
2. Create a GitHub Issue with label `debt`
3. Link the comment to the issue number
4. Fix it during your 20% budget or when you next touch that file

```
// DEBT(#142): This function handles both validation and persistence.
// Split into separate concerns when adding the next validation rule.
```

---

## AI-Assisted Workflow

AI tools (Claude Code, GitHub Copilot, Cursor) are the solo developer's force multiplier. Use them deliberately, not casually.

### Spec First

Never start a coding session by typing code. Start with a specification:

1. Write the acceptance criteria in plain English
2. Define input/output contracts
3. List edge cases and error conditions
4. Feed this spec to your AI tool as context

The spec is the prompt. A vague spec produces vague code.

### Context Packing

AI tools perform better with rich context. Before prompting:

- Include relevant type definitions and interfaces
- Reference existing patterns in your codebase
- Provide example inputs and expected outputs
- Specify constraints (performance, compatibility, style)

### CRISP Prompts

Structure prompts for maximum AI output quality:

- **C**ontext — What exists, what is the current state
- **R**equirements — What must be true when done
- **I**nput/Output — Concrete examples of data flow
- **S**tyle — Patterns, conventions, and constraints to follow
- **P**lan — Ask the AI to outline its approach before coding

### Chunked Implementation

Break work into AI-manageable chunks:

1. One function or component per prompt
2. Review and test each chunk before proceeding
3. Feed reviewed code back as context for the next chunk
4. Never let AI generate more than 200 lines without a review checkpoint

### Review Loops

AI-generated code requires the same scrutiny as a junior developer's PR:

- Read every line — do not skim
- Run the tests — do not trust "this should work"
- Check for hallucinated imports and APIs
- Verify edge case handling matches your spec

### Agent Orchestration

In 2026, agentic workflows allow parallel task execution:

- Use background agents for mechanical tasks (test writing, refactoring, documentation)
- Keep the main thread for architectural decisions and complex logic
- Define clear boundaries: agents work within a file or module, not across architectural seams
- Always review agent output before merging — you are the architect, agents are the builders

---

## Documentation as You Go

### ADR Template (Architecture Decision Records)

For every irreversible or high-impact decision, create a short record:

```markdown
# ADR-NNN: [Title]

**Status:** Accepted | Superseded by ADR-XXX
**Date:** YYYY-MM-DD

## Context
What is the situation that requires a decision?

## Decision
What did we decide and why?

## Consequences
What are the trade-offs? What becomes easier or harder?
```

Store ADRs in `docs/decisions/` and number them sequentially.

### README as Living Document

Your README is your project's front door. Update it when you:

- Add a new feature
- Change setup instructions
- Modify environment variables
- Alter the deployment process

A stale README is worse than no README — it actively misleads.

### Inline Documentation Rules

| Write docs for | Skip docs for |
|----------------|---------------|
| Public APIs and interfaces | Private helper functions with clear names |
| Non-obvious business logic | Getters/setters and CRUD operations |
| Workarounds and hacks (with context) | Code that reads like prose |
| Configuration and environment variables | Standard library usage |

Comment the "why," not the "what." If you need to explain what the code does, the code needs refactoring, not comments.

---

## Burnout Prevention

### Hard Constraints

These are non-negotiable boundaries:

- **Maximum 8 hours of focused work per day.** Context-switching and admin do not count.
- **One full day off per week minimum.** No "just checking one thing."
- **Two weeks vacation per year minimum.** Schedule it in advance and protect it.
- **No coding after 20:00.** Evening problem-solving happens on paper, not in the IDE.

### Scope as Energy Budget

You have a finite amount of decision-making energy each day. Spend it deliberately:

- Reduce decisions: use templates, conventions, and defaults
- Front-load hard decisions to the morning
- Batch low-energy tasks to the afternoon admin block
- Say no to feature requests that do not align with current milestone

### Identity Diversification

If your entire identity is "the person building this project," burnout is inevitable. Maintain at least one serious interest outside of software. Exercise, creative hobbies, community involvement — these are not distractions, they are load-bearing walls.

### Early Warning Signals

Watch for these and take action immediately:

- Dreading opening the IDE three days in a row
- Skipping tests because "it's fine"
- Working weekends to "catch up" more than once a month
- Losing interest in the problem you are solving
- Irritability when receiving user feedback

The fix is always the same: reduce scope, take a break, then reassess priorities.

---

## Quality vs Speed Trade-offs

### Non-Negotiables (Never Cut These)

- Input validation and sanitization
- Authentication and authorization checks
- Data backup and recovery paths
- Error handling for external service calls
- Secrets management (no hardcoded credentials)

### Where Cutting Corners Is Acceptable

| Area | Acceptable Shortcut | Recovery Path |
|------|---------------------|---------------|
| UI polish | Ship with basic styling | Iterate based on user feedback |
| Test coverage | Cover happy path + critical edge cases | Add regression tests as bugs appear |
| Performance | Ship unoptimized if response < 2s | Profile and optimize when users notice |
| Documentation | Inline comments + README basics | Expand docs before onboarding contributors |
| Monitoring | Basic health check + error logging | Add metrics when traffic justifies it |

The rule: cut corners on things that affect perception (polish, docs). Never cut corners on things that affect correctness (security, data integrity).

---

## Solo CI/CD Workflow

### Trunk-Based Development

- `main` is always deployable
- Create short-lived feature branches (< 2 days)
- Self-review every PR before merging — the diff view catches what the editor view misses
- Squash merge to keep history clean

### Feature Flags Lifecycle

| Stage | Flag State | Duration |
|-------|------------|----------|
| Development | Off in production, on in dev | During development |
| Rollout | On for subset of users | 1-2 weeks |
| General availability | On for everyone | 1 week observation |
| Cleanup | Remove flag entirely | Next sprint |

Never let a feature flag live longer than 30 days after GA. Dead flags are technical debt.

### Minimal CI Pipeline

Every push should trigger, at minimum:

1. **Lint** — Catch style issues and common errors
2. **Type check** — If using a typed language
3. **Test** — Unit + integration tests
4. **Build** — Verify the artifact builds cleanly
5. **Deploy to staging** — On merge to main

Keep CI under 5 minutes. A slow pipeline kills shipping cadence.

---

## Community Building

### Open Source as Distribution

Open-sourcing components of your project serves two purposes:

- **Distribution:** Every GitHub star is a potential user or contributor
- **Quality pressure:** Public code forces better practices

Open-source the generic parts (utilities, libraries, tools). Keep the business logic proprietary if applicable.

### Building in Public

Share your progress regularly:

- **Weekly updates** on Twitter/X or a dev blog — what shipped, what is next
- **Technical write-ups** for interesting problems you solved
- **Milestone announcements** with screenshots or demos
- **Honest retrospectives** including what went wrong

Building in public creates accountability, attracts early users, and builds a network that compounds over years.

---

## Learning Strategy

### T-Shaped Model

Go deep in your primary stack (the vertical bar of the T). Go broad enough in adjacent areas to be dangerous (the horizontal bar).

- **Deep:** Your primary language, framework, database, and deployment platform
- **Broad:** Enough to evaluate and integrate — security basics, UX principles, infrastructure concepts, data modeling

### Efficient Sources

| Source Type | Time Investment | Knowledge Return |
|-------------|-----------------|------------------|
| Official documentation | 30 min/week | Highest — authoritative, current |
| Conference talks (2x speed) | 1 hour/week | High — curated expert knowledge |
| Peer code review (OSS) | 30 min/week | High — real patterns and anti-patterns |
| Technical newsletters | 15 min/week | Medium — awareness of trends |
| Books (technical) | 1 per quarter | Medium — deep understanding |
| Social media/forums | 15 min/day max | Low — high noise-to-signal ratio |

### Scheduled Learning

Block 30-60 minutes daily (the 16:30-17:30 slot in the daily schedule). Alternate between:

- **Monday:** Read documentation for a tool you use daily
- **Wednesday:** Watch a conference talk or read a technical post
- **Friday:** Experiment with a new library or technique in a throwaway project

Learning without application decays in days. Always tie learning to a current or upcoming project need.

---

## Weekly Workflow Template

### Monday — Plan and Prioritize

| Time | Activity |
|------|----------|
| 09:00-09:30 | Review last week's metrics: what shipped, what slipped |
| 09:30-10:00 | Triage new issues, update ICE scores, set weekly goals (3 max) |
| 10:00-12:00 | Deep work: hardest task of the week |
| 13:00-15:30 | Implementation |
| 15:30-16:30 | Community: respond to issues, review PRs, post update |
| 16:30-17:30 | Learning: read docs for current tools |

### Tuesday — Build

| Time | Activity |
|------|----------|
| 09:00-12:00 | Deep work: primary feature development |
| 13:00-15:30 | Continue implementation, write tests |
| 15:30-16:30 | Admin: email, messages, dependency updates |
| 16:30-17:30 | Tech debt: 20% budget work |

### Wednesday — Build and Learn

| Time | Activity |
|------|----------|
| 09:00-12:00 | Deep work: primary feature development |
| 13:00-15:30 | Implementation and integration testing |
| 15:30-16:30 | Admin and issue management |
| 16:30-17:30 | Learning: conference talk or technical reading |

### Thursday — Polish and Debt

| Time | Activity |
|------|----------|
| 09:00-12:00 | Deep work: finish weekly goal features |
| 13:00-15:30 | Tech debt work, refactoring, documentation |
| 15:30-16:30 | Self-review all PRs from the week |
| 16:30-17:30 | Prepare release notes |

### Friday — Ship and Reflect

| Time | Activity |
|------|----------|
| 09:00-10:00 | Final testing and QA |
| 10:00-11:00 | Cut release, deploy to staging |
| 11:00-12:00 | Smoke test staging, deploy to production |
| 13:00-14:00 | Write weekly retrospective (what worked, what did not, what to change) |
| 14:00-15:00 | Plan next week's milestone targets |
| 15:00-16:00 | Community: write blog post or share update |
| 16:00-17:00 | Learning: experiment with new tool or technique |

### Monthly Rhythm

- **First Monday:** Review monthly metrics (features shipped, bugs reported, debt reduced)
- **First Monday:** Update project roadmap and milestones
- **Last Friday:** Dependency audit and security updates

### Quarterly Rhythm

- **Week 1:** Strategic review — is the project heading in the right direction?
- **Week 1:** Update tech stack decisions — any tools to add, remove, or replace?
- **Week 1:** Set 3 quarterly goals (OKRs or similar)
- **Ongoing:** One quarterly "big refactor" if debt has accumulated beyond the 20% budget

---

## Sources

- [Solo Developer Project Management Systems 2025](https://apatero.com/blog/solo-developer-project-management-systems-2025)
- [Solo Developer Systems: 7 Smart Workflows to Scale Alone](https://codecondo.com/solo-developer-systems-smart-workflows/)
- [The Effective Solo Developer — Better Programming](https://betterprogramming.pub/the-effective-solo-dev-8407d86c8a9e)
- [2025 Year in Review: Lessons from Solo SaaS Development](https://dev.to/pipipi-dev/2025-year-in-review-lessons-from-solo-saas-development-3i08)
- [Solo DevOps — Jonathan Hall](https://jhall.io/posts/solo-devops/)
- [What Is Agentic Engineering? — Glide Blog](https://www.glideapps.com/blog/what-is-agentic-engineering)
- [How Agentic AI Will Reshape Engineering Workflows in 2026 — CIO](https://www.cio.com/article/4134741/how-agentic-ai-will-reshape-engineering-workflows-in-2026.html)
- [AI-Assisted Development in 2026 — DEV Community](https://dev.to/austinwdigital/ai-assisted-development-in-2026-best-practices-real-risks-and-the-new-bar-for-engineers-3fom)
- [5 Key Trends Shaping Agentic Development in 2026 — The New Stack](https://thenewstack.io/5-key-trends-shaping-agentic-development-in-2026/)
- [Optimizing Your 20% Time for Technical Debt](https://www.practicalengineering.management/p/optimizing-your-20-time-for-tech-debt)
- ["20% for Tech Debt" Doesn't Work — Manager.dev](https://newsletter.manager.dev/p/how-to-implement-20-for-tech-debt-)
- [How to Manage Technical Debt — Netguru](https://www.netguru.com/blog/managing-technical-debt)
- [Technical Debt Ratio: How to Measure — DX](https://getdx.com/blog/technical-debt-ratio/)
- [Git Workflows for Solo Developers — DasRoot](https://dasroot.net/posts/2026/03/git-workflows-solo-developers-content-creators/)
- [Agentic Coding in 2026 — Times of AI](https://www.timesofai.com/industry-insights/agentic-coding-in-software-development/)
- [2026 Agentic Coding Trends Report — Anthropic](https://resources.anthropic.com/hubfs/2026%20Agentic%20Coding%20Trends%20Report.pdf)
