# Contract: Findings File Format

**Purpose**: Define the shared format for `ds/audit/findings.md` — the inter-skill communication artifact.

**Location**: `ds/audit/findings.md` at repo root.

**Format**:

```markdown
<!-- findings-meta
git_hash: {HEAD}
timestamp: {ISO 8601}
source: {skill-name}
scopes: {comma-separated list of analyzed scopes}
-->

## Findings

| ID | Severity | Category | File | Line | Scope | Title |
|----|----------|----------|------|------|-------|-------|
| {id} | {severity} | {A|B} | {file} | {line} | {scope} | {title} |
```

**Field rules**:

| Field | Rule |
|-------|------|
| `git_hash` | MUST match current HEAD. If different, findings are stale — consumer must re-analyze. |
| `source` | Which skill produced these findings. Informational — any consumer treats findings equally. |
| `scopes` | MUST list every scope that was analyzed, even scopes with zero findings. Absence means "not analyzed". |
| `Severity` | CRITICAL, HIGH, MEDIUM, LOW (standard severity levels) |
| `Category` | A (autonomous fix allowed) or B (approval gated) |
| `File` | Precise path relative to repo root. `Line: 0` means file-level finding. |
| `Line` | Exact line number where the issue occurs. |
| `Scope` | Standard scope name from the Scope Coverage table in SKILL-SPEC. |

**Write semantics**:

| Scenario | Behavior |
|----------|----------|
| File doesn't exist | Create new file with your scopes in meta header |
| File exists, same git_hash | Scoped overwrite: rewrite own scopes' rows; preserve other scopes' rows |
| File exists, different git_hash | Stale. Full-codebase analyzer → overwrite entirely. Partial analyzer → overwrite own scopes only. |
| After consuming/fixing | Remove fixed entries. Delete file when zero entries remain. |

**Consumers**: ds-review, ds-test, ds-docs, ds-compliance, ds-mobile, ds-backend, ds-frontend, ds-simplify, ds-ship (orchestrator).
