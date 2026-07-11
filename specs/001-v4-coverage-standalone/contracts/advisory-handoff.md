# Contract: Advisory Handoff Pattern

**Purpose**: Define the cross-skill reference pattern that preserves standalone operation.

**Location**: SKILL-SPEC.md "Standalone Invariant" normative section. Patterns appear in individual SKILL.md files where cross-skill references are needed.

**Pattern**:

When a skill needs to reference a capability owned by another skill, it uses a three-way decision:

```text
If {target skill} is present → delegate
Else if skill can do a basic inline check → perform {basic check}, note "deeper analysis available via {target skill}"
Else → emit gap note: "[scope] not analyzed — requires {target skill}"
```

**Rules**:

1. A skill MUST NOT hard-fail (crash, return `FAIL`, or refuse to continue) when a target skill is absent
2. A skill MUST NOT silently omit a scope that a missing skill would normally cover — either perform an inline check or emit a gap note
3. The inline check is a simplified, best-effort analysis that catches the most common issues but is not as thorough as the dedicated skill's analysis
4. The gap note states exactly which scope was not analyzed and why, allowing the user to decide whether to install the missing skill
5. Orchestrator skills (ds-ship, ds-pipeline) MUST surface all missing skills in a `## Missing skills` section of their report

**Example — valid advisory handoff in ds-review**:

```markdown
If ds-frontend is present → delegate UI/UX analysis
Else → perform basic heuristic scan (check for hardcoded colors, missing alt text, missing ARIA labels)
         Note: "Basic UI/UX scan completed. For full design token enforcement and WCAG audit, install ds-frontend and re-run."
```

**Example — invalid hard-fail (must not exist)**:

```markdown
# INVALID — do not use:
Delegate to ds-frontend. Hard-fail if ds-frontend is not installed.
```

**Consumers**: Every non-orchestrator SKILL.md that references another skill, `check-consistency.sh` (v4 pattern detector), `/full-review` standalone category.

**Verification**: grep for `→ delegate` pattern in cross-skill context + verify no hard-fail patterns exist (`"skill not found"`, `"install X first"` as error-stop, not advisory).
