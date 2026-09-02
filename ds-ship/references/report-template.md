# Ship Report Template (Phase 6)

The exact shape of `ds/audit/report.md`. Loaded when Phase 6 writes the consolidated report. Every section below is emitted; a section with no content states so explicitly rather than being dropped.

```markdown
# Ship Report — {repo-name}

<!-- meta
generated: {ISO 8601} | git_hash: {HEAD} | stage: {classified-stage} | type: {project-type}
-->

## Summary

- Mode: {harden | release | launch | maintain} — {derivation: --mode flag | stage=… + intent …}
- Stage: {stage} — {cited signals}
- Signals: {the resolved Signals line}
- Instruction tokens loaded: {n} (measured — wc -c of every SKILL.md read this run ÷ 4)
- Value proposition: {paragraph}
- Autonomous fixes applied (Category A): {N}
- Awaiting user decision (Category B): {M}
- Ship-ready: yes | no ({K} mandated blockers remain — cited sources in Awaiting User Decision; advisory items never counted) — release/launch only; harden/maintain print `Health: {before}→{after}/100` instead
- Sequence gaps: {n} ({0 if none — a pre-launch/launched run with n > 0 cannot report Ship-ready: yes})
- Doc token reduction: {before} → {after} ({%})
- Security baseline ([../../core/principles.md](../../core/principles.md) §5): {n} secret-scan runs across delegated skills (ds-fix, ds-compliance, ds-pr); 0 unresolved leaks | gap: {skill X did not run secret scan}
- PR: {url} | declined-this-run | not applicable ({reason}) | muted
- Tracking: {n} filed ({refs}) | declined-this-run | not applicable (0 unresolved) | muted

## Sequence
| Skill | Status | Reason / signal | Findings (A / B) |
|-------|--------|-----------------|------------------|
| ds-blueprint | ran | findings absent | 12 / 3 |
| ds-launch | skipped — not part of this mode | mode=harden | — |
| ds-productize | skipped — no billing signal (billing=none) | | — |
Status vocabulary: `ran` · `skipped — not part of this mode` · `skipped — no signal ({key}={value})` · `skipped — another skill owns it for this project type` · `skipped — removed by you` · `failed` · `skipped — not installed`. Every candidate skill appears exactly once.

## Missing skills
| Skill | Would have covered | Signal that justified it |
Delegates the plan needed but the host does not have installed; omit the section when every planned skill was present.

## Architectural Changes (approved + applied)
| Change | Rationale | Concrete benefit |

## Autonomous Fixes (Category A)
| Fix | File:line | Problem solved |

## Awaiting User Decision (Category B)
| Proposal | Why needed | Risk / effort | Priority |

## Sequence Gaps
| Missing skill | Mandated by | Status |
Empty table = every matrix-mandated skill for this stage+type either ran or carries a recorded exclusion reason (Phase 0 step 10); omit this section entirely when empty.

## Recommended Human Actions (advisory — not blocking)
| Action | Why | Where |

Every human-required finding that fails the mandated-blocker test (mandated-blocker test: a citable external authority makes it a documented prerequisite whose omission causes rejection, legal exposure, or a broken production path) lands here instead of Category B/blockers — cite the mandating source for any item kept as a blocker in Category B or Summary; omit this section when empty.

## Intentional Deviations (kept as-is)
| Item | Why it stays |

## Promise vs Reality
| Promise | Source | Status |
| ... | README#L23 | implemented at src/foo.ts:42 |

## Orchestration log
- [P0] Stage classified: {stage}. Type: {type}. Sequence approved: ...
- [P{N}.{K}] invoke {skill} — completed — findings: {n} (A: {x}, B: {y})

## Next Trigger
{When should ds-ship next run — e.g. "after feature X lands", "quarterly hygiene", "next frontier-model upgrade"}

## Dimension Coverage
| Dimension | Status | Owning Skill | Notes |
|-----------|--------|-------------|-------|
| A1 | {audited | owner-skipped | unowned} | ds-benchmark + ds-productize |
| A2 | {audited | owner-skipped | unowned} | ds-productize |
| A3 | {audited | owner-skipped | unowned} | ds-productize + ds-deploy |
| A4 | {audited | owner-skipped | unowned} | ds-launch |
| A5 | {audited | owner-skipped | unowned} | ds-frontend (ux) |
| A6 | {audited | owner-skipped | unowned} | ds-frontend |
| A7 | {audited | owner-skipped | unowned} | ds-frontend (impl) + ds-compliance (regulatory) + ds-mobile (impl, mobile) |
| A8 | {audited | owner-skipped | unowned} | ds-fix (mechanical) + ds-compliance (rules) |
| A9 | {N/A — integrations none | conditional — integrations active | unowned} | ds-blueprint (signal) + ds-backend/ds-compliance/ds-frontend/ds-launch/ds-mobile (conditional) |
| A10 | {audited | owner-skipped | unowned} | ds-docs + ds-backend |
| A11 | {audited | owner-skipped | unowned} | ds-backend + ds-compliance + ds-productize |
| B1 | {audited | owner-skipped | unowned} | ds-review, ds-fix, ds-simplify, ds-quality |
| B2 | {audited | owner-skipped | unowned} | ds-blueprint + ds-review --strategic |
| B3 | {audited | owner-skipped | unowned} | ds-test |
| B4 | {audited | owner-skipped | unowned} | ds-blueprint + ds-repo |
| B5 | {audited | owner-skipped | unowned} | ds-backend + ds-docs |
| B6 | {audited | owner-skipped | unowned} | ds-docs |
| C1 | {audited | owner-skipped | unowned} | ds-compliance + 4 execution skills |
| C2 | {audited | owner-skipped | unowned} | ds-compliance |
| C3 | {audited | owner-skipped | unowned} | ds-compliance + ds-docs + ds-repo |
| C4 | {audited | owner-skipped | unowned} | ds-deps |
| C5 | {audited | owner-skipped | unowned} | ds-docs |
| D1 | {audited | owner-skipped | unowned} | ds-review --perf + ds-launch --perf-budget + ds-tune |
| D2 | {audited | owner-skipped | unowned} | ds-review --perf + ds-deploy --cost |
| D3 | {audited | owner-skipped | unowned} | ds-backend + ds-deploy |
| D4 | {audited | owner-skipped | unowned} | ds-deploy + ds-backend |
| D5 | {audited | owner-skipped | unowned} | ds-backend |
| D6 | {audited | owner-skipped | unowned} | ds-devops + ds-launch |
| D7 | {audited | owner-skipped | unowned} | ds-deploy |
| D8 | {audited | owner-skipped | unowned} | ds-repo |
| D9 | {audited | owner-skipped | unowned} | ds-deps + ds-review |
| D10 | {audited | owner-skipped | unowned} | ds-backend + ds-frontend + ds-deploy + ds-docs |
| E | N/A (carrier) | ds-ship, ds-pipeline, etc. | Process carriers — not quality dimensions |

Status values: `audited` (skill ran and produced findings), `skipped — not part of this mode` (its leg is outside this run's mode), `owner-skipped: {reason}` (skill exists but was not invoked — the reason MUST cite the concrete Phase 0 signal or rule that justified it, e.g. `owner-skipped: monetization=internal, no billing surface detected (Phase 0 step 8)` — a bare `owner-skipped` with no cited reason is not a valid status; resolve it to `audited` (run the skill) or `unowned` (flag) before reporting), `unowned` (no skill claims this dimension). ⚠️ Unowned dimensions MUST be flagged with an explicit warning prefix in the report summary. A general impression ("looks fine", "not needed here") is never a substitute for a cited signal — every non-`audited` status traces to something read this run (a file, a Phase 0 answer, a rule name), never to overall judgment alone.
```
