# Backtrack Logic

Decision logic, state machine, and budget mathematics for [/ds-solve](../SKILL.md). Research scoring follows [CRAAP+ methodology](craap-scoring.md). Revert mechanism uses a git ratchet pattern.

## State Machine

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
SETUP ──► PLAN ──► RESEARCH ──► EXECUTE ──┬──► next step ─────┤
            ▲         ▲                   │                    │
            │         │                   ▼                    │
            │         │            step fails alt              │
            │         │                   │                    │
            │         │                   ▼                    │
            │         │        ┌─── BACKTRACK ───┐             │
            │         │        │  new research   │             │
            │         │        │  round found    │             │
            │         │        └────────┘        │             │
            │         │                          │             │
            │         │              rounds exhausted          │
            │         │                          │             │
            │    RE-PLAN ◄───────────────────────┘             │
            │         │                                        │
            │    plan budget exhausted                         │
            │         │                                        │
            │    ESCALATE ──► user input ──► new direction ────┘
            │         │
            │    abort ──► SUMMARY
            │                ▲
            └────────────────┘ (all steps complete)
```

## Decision Tree

At each decision point, the logic is deterministic:

### Step-Level Decision (after each attempt)

```
attempt finished
  ├─ verification PASS + red lines HOLD → step SUCCESS → next step
  ├─ verification PASS + red line VIOLATED → REVERT → try next alternative
  ├─ verification FAIL + red lines HOLD → record failure → try next alternative
  └─ verification FAIL + red line VIOLATED → REVERT → record both → try next alternative

no more alternatives (alt > budget.A)
  └─ trigger BACKTRACK
```

### Backtrack Decision (step alternatives exhausted)

```
research_round for this step
  ├─ round <= budget.R → web research new alternatives → EXECUTE with new set
  └─ round > budget.R → trigger RE-PLAN
```

### Re-plan Decision (step research exhausted)

```
plan_counter
  ├─ plan <= budget.P → create new plan → RESEARCH
  └─ plan > budget.P → trigger ESCALATE
```

### Escalate Decision (user input)

```
user choice
  ├─ update red lines → reset plan counter → PLAN (with updated constraints)
  ├─ reduce scope → reset plan counter → PLAN (with reduced objective)
  ├─ new direction → reset plan counter → PLAN (with new context)
  └─ abort → SUMMARY
```

## Budget Mathematics

### Default Budget: 3x3x5

| Level | Default | Meaning |
|-------|---------|---------|
| P (plans) | 3 | Maximum full plan redesigns |
| R (rounds) | 3 | Maximum research rounds per step |
| A (alternatives) | 5 | Maximum alternatives per research round |

### Theoretical Maximum Attempts

```
max_attempts_per_step = P × R × A = 3 × 3 × 5 = 45
max_attempts_total = max_attempts_per_step × max_steps = 45 × 10 = 450
```

In practice, most problems resolve in plan 1, round 1, alternatives 1-3.

### Override Format

`--budget=PxRxA` where P, R, A are positive integers.

| Example | Meaning |
|---------|---------|
| `3x3x5` | Default: thorough exploration |
| `1x1x3` | Quick: 1 plan, 1 round, 3 alternatives |
| `5x5x10` | Exhaustive: for critical problems |
| `1x1x1` | Rejected: minimum is `1x1x2` |

### Budget Validation

- Minimum: P=1, R=1, A=2 (at least 2 alternatives to have a fallback)
- Maximum: P=10, R=10, A=20 (prevent runaway resource usage)
- Invalid format → use default `3x3x5` with warning

## Learned Constraint Propagation

When an alternative fails, the failure reason is analyzed for reusable constraints:

### Extraction Rules

| Failure Pattern | Learned Constraint |
|-----------------|-------------------|
| Dependency version conflict | "library X requires version >= Y" |
| Missing system tool | "tool X not available in environment" |
| Permission denied | "operation requires elevated privileges" |
| API not available | "service X not reachable from this environment" |
| Incompatible platform | "approach requires OS/arch X" |
| Test regression | "changing X breaks test Y" |

### Propagation Scope

Learned constraints are applied to:
1. **Same step, next alternative:** Exclude approaches that would hit the same constraint
2. **Same step, next research round:** Include constraint in search queries (e.g., "solve X without dependency Y")
3. **New plan:** Available in episodic memory for plan design — avoid steps that depend on blocked resources

### Constraint Format in State File

```json
{
  "constraint": "react@17 incompatible with library@3.x",
  "source": "plan-1/step-2/alt-3",
  "scope": "global",
  "type": "dependency_conflict"
}
```

Scope values:
- `step` — applies only to this step
- `plan` — applies to all steps in current plan
- `global` — applies to all future plans

## Revert Mechanism

### When to Revert

Revert is triggered when:
1. Red line post-check fails after an execution attempt
2. An alternative needs to be abandoned (verification failed)

### Revert Strategy

Ordered by preference:

1. **Git revert:** If changes were committed, `git revert` or `git reset` to pre-attempt state
2. **File restore:** If changes are uncommitted, restore files from pre-attempt backup
3. **Manual undo:** If neither is possible, apply inverse operations

### Pre-Attempt Snapshot

Before each attempt:
1. Record list of files that will be modified
2. Store git HEAD ref (if in git repo)
3. Record relevant state (running processes, config values)

After failed attempt:
1. Restore to snapshot state
2. Verify red lines hold after restore
3. If restore itself fails → flag as CRITICAL, enter Escalate

## State File Schema

`.ds-solve-state.json`:

```json
{
  "version": 1,
  "objective": "description of what to achieve",
  "verification": "command or check that proves success",
  "red_lines": [
    { "id": 1, "description": "...", "source": "auto|user", "check": "command or condition" }
  ],
  "budget": { "P": 3, "R": 3, "A": 5 },
  "current_plan": 1,
  "status": "in_progress|completed|failed|escalated",
  "plans": [
    {
      "id": "plan-1",
      "status": "in_progress|completed|failed",
      "steps": [
        {
          "id": "step-1",
          "description": "...",
          "verification": "...",
          "red_line_risk": [1, 3],
          "status": "pending|in_progress|completed|failed|skipped",
          "current_round": 1,
          "rounds": [
            {
              "id": "round-1",
              "alternatives": [
                {
                  "id": "alt-1",
                  "description": "...",
                  "source": "local|web",
                  "craap_score": 85,
                  "status": "pending|success|failed",
                  "failure_reason": null,
                  "learned_constraint": null
                }
              ]
            }
          ]
        }
      ]
    }
  ],
  "episodic_memory": [
    {
      "plan": 1, "step": 1, "round": 1, "alt": 1,
      "action": "what was attempted",
      "result": "success|fail",
      "evidence": "command output or observation",
      "learned_constraint": { "constraint": "...", "scope": "step|plan|global", "type": "..." },
      "timestamp": "ISO 8601"
    }
  ],
  "red_line_checks": [
    { "timestamp": "...", "context": "pre|post step-1 alt-2", "all_passed": true, "violations": [] }
  ]
}
```

## Episodic Memory Compression

When context or state file grows large:

1. **Keep:** failure reasons, learned constraints, step outcomes
2. **Compress:** verbose command outputs → one-line summaries
3. **Drop:** successful intermediate outputs (the success is recorded in step status)

Trigger: episodic_memory exceeds 50 entries. Compress oldest entries first, keeping the 20 most recent in full detail.
