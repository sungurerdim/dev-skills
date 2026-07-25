# Rubric: Architecture & Interface Quality

**Consumer:** the `--strategic` verifier pass (`architecture`, `patterns`, `contract-consistency`, `maintainability`). Hand this file to the verifier as its whole contract — it judges the codebase against these dimensions and returns a level plus the observable signal that placed it there.

**Why a rubric and not a rule list.** The scopes above turn on taste: "is this the right abstraction" has no pattern to grep. A rule list forces arbitrary thresholds; a rubric states what each level looks like concretely, so the judgment is reproducible and auditable. Rule-shaped findings still belong in `rules-quality.md` — this file covers only what a rule cannot express.

**How to use.** Score each dimension independently. A level is claimed only with a `file:line` example that demonstrates the named signal; no example → drop to the level you can evidence. Report the lowest-scoring dimension first — it is the one constraining the codebase.

## Dimensions

### 1. Module boundaries

| Level | What it looks like |
|-------|--------------------|
| Strong | A reader can predict which file holds a given behavior from the module name alone. Changing one product decision touches one module. |
| Adequate | Boundaries hold for the core domain; utility and glue code drift into catch-all modules (`utils`, `helpers`, `common`). |
| Weak | A single product change requires edits in 5+ unrelated files (shotgun surgery), or one module changes for more than one reason (SRP break, `principles.md §2`). |

### 2. Dependency direction

| Level | What it looks like |
|-------|--------------------|
| Strong | High-level policy depends on abstractions only; concrete adapters sit at the edges and are substitutable without touching policy. |
| Adequate | Direction is mostly correct; a few concrete imports leak upward at well-understood seams. |
| Weak | Policy imports concrete infrastructure directly (DIP break), or the import graph contains a cycle. |

### 3. Interface consistency

| Level | What it looks like |
|-------|--------------------|
| Strong | One verb per operation class across the whole codebase; one return and error shape per layer; analogous functions share parameter order and options shape; units and formats agree at every boundary. |
| Adequate | Consistent within each layer, divergent across layers — a caller must remember which convention applies where. |
| Weak | The same concept carries 3+ names, or `throw` / `Result` / `null` are mixed inside one layer. Flag as systemic only with 3+ concrete examples of the same drift. |

### 4. Abstraction fit

| Level | What it looks like |
|-------|--------------------|
| Strong | Every abstraction has ≥2 real callers and removing it would force duplication. Complexity tracks the problem, not the anticipated problem. |
| Adequate | One or two abstractions are speculative but harmless — cheap to inline later. |
| Weak | Layers exist with a single caller, or configuration flags exist that nothing reads (YAGNI). Three similar lines would have been better than the indirection. |

### 5. Failure surface

| Level | What it looks like |
|-------|--------------------|
| Strong | Every external call carries an explicit timeout and a defined failure path; errors name what was expected, what arrived, and what to do. |
| Adequate | Failure paths exist on the critical flows; peripheral calls rely on framework defaults. |
| Weak | Unbounded waits, blanket catches that swallow the cause, or error text that tells the reader nothing actionable. |

## Verdict format

Per dimension: `{dimension}: {Strong|Adequate|Weak} — {observable signal} ({file:line})`. Then one line naming the single change that would raise the lowest dimension, and what it would cost. No score number — a rubric level with evidence is more actionable than a percentage.
