# Impact-surface map (ds-issue `--do`)

Before any code changes, enumerate the **touched · linked · affected** set. The output is a code-map contract: an explicit affected-set that every later phase is checked against. A change that breaks a node in this set is not done. Skipping this map is how a one-file "fix" silently breaks five callers.

## The six axes (DSC — evaluate every axis every run)

| Axis | What to enumerate | How to find it |
|------|-------------------|----------------|
| 1. callers | every reference to functions/exports you'll change | language server `findReferences`; grep the symbol on untyped code |
| 2. consumers | code depending on changed interfaces, types, constants, return shapes | language server `goToImplementation` + type references; grep imports |
| 3. serialization | sync / persistence / wire paths the change crosses — **both write and read sides** | trace the data from mutation to storage to re-load |
| 4. schema | schema or migration impact; is the change backward-compatible? | read the schema/migration definitions; check expand-contract |
| 5. i18n / a11y / compliance | user-facing strings (key parity), keyboard/contrast, regulated-data surfaces | grep string keys; check the change against accessibility + data-handling rules |
| 6. hazards | the adapter's project-specific data-loss / invariant checklist | read `hazardChecklist`; mark each item affected (with path) or N/A (with reason) |

Each axis produces either touched-set entries or an explicit **N/A with reason** — never a blank. On untyped code with no language server, fall back to grep and flag the axis confidence as lower (W5).

## Touched vs linked vs affected

- **Touched** — files you will edit directly.
- **Linked** — files that reference a touched symbol (callers, importers) — must be re-checked after the edit (W2).
- **Affected** — behavior that could change even without a code edit there: a serialized field's read side, a cached value, a downstream UI that renders the changed data.

The affected-set is the union; dedup by `file:line` (W7).

## Hazard checklist (axis 6)

The adapter's `hazardChecklist` points to a project doc enumerating data-loss / invariant traps (e.g. a sync-invariants doc: "a new field must be written in N places or pull silently wipes it"). For each item:

1. Does this change touch the trap's pattern? → **affected** (cite the path) or **N/A** (state why).
2. Affected → the plan must include the trap's required steps (e.g. add the field on both write and read sides + the schema) as bounded units with their own verify signal.

A silently-skipped hazard item is the failure mode this axis exists to prevent — every item gets a disposition.

## Output (Report Format)

```
| Axis            | Affected set                          | How found                |
|-----------------|---------------------------------------|--------------------------|
| callers         | foo.js:88, bar.js:#mutate (3 refs)    | findReferences           |
| consumers       | schema.ts Contact.roles               | type references          |
| serialization   | sync write index.js:64 + read :127    | data-path trace          |
| schema          | migration v33 needed (additive)       | read db-migrations       |
| i18n/a11y       | 2 new keys tr+en; N/A a11y            | key grep                 |
| hazards         | see hazard table ↓                    | hazardChecklist          |

| Hazard                       | Affected? | Path / reason            |
|------------------------------|-----------|--------------------------|
| one-sided field (write+read) | yes       | add to read side :127    |
| empty-container 400          | N/A       | no People-API container  |
```

This map drives the plan: every affected-set node becomes either a unit to change or a caller to re-verify post-change.
