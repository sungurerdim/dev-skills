# New-Skill Authoring Checklist

The guided on-ramp for adding a `ds-*` skill (issue #26). `SKILL-SPEC.md` stays
the authority; this checklist sequences it and names the mechanical gate that
proves each step. When the two disagree, the spec wins — then fix this file.

**The finish line is mechanical:** `bash scripts/quality.sh` green (35
consistency checks + self-tests). Everything below exists to get you there in
one pass instead of twenty failed gate runs.

## 1. Before writing anything

- [ ] **One verb, one owner.** State the skill's job in one sentence. If an
      existing skill's INVOKE table already claims it, extend that skill instead
      (Trigger Discipline, spec §2). Check the Dimension Coverage Map (spec
      appendix): a new dimension needs the amendment process (spec §14).
- [ ] **Standalone by design.** The directory must work installed alone: no
      other skill's files by path, no in-repo doc citations, links stay inside
      the directory (checks 21-23).

## 2. Scaffold — copy the template

- [ ] Copy the SKILL.md template from spec §Phase Template + Section Order:
      frontmatter (`name`, `description` ONLY — check 33) → pain-first opening
      (2 lines, no marketing words — check 31) → opening Completion Evidence
      band (verbatim from spec §1 — checks 13+32) → Triggers + INVOKE/DON'T
      INVOKE table (checks 7) → Contract → Arguments (canonical `--auto` row
      verbatim — checks 14b+23) → Scopes → Delegation line (checks 3, 20, 34)
      → Execution Flow phases → Quality Gates → Edge Cases → closing band with
      ` <!-- portable-only -->` (checks 13, 27, 32).
- [ ] Contract carries the two canonical bullets verbatim (spec §1/§8; check
      32): full-accounting, and pre-existing-errors with its portable-only
      marker.

## 3. Phases and gates

- [ ] Every phase ends `**Gate:** {pass condition}. If {failure} → {concrete
      recovery}.` — the pass condition names an observable (command output,
      exit code, file existence), never a self-assessment (check 29).
- [ ] Deterministic verifications state command + expected signal
      ("`git status --porcelain` → empty output"), and counts are computed by
      command, never tallied by the model.
- [ ] Writes/deletes/resets project files in bulk? Add the Checkpoint
      pre-step before the first write (spec §4 Checkpoint Gate) AND add the
      skill to check 35's list in `scripts/check-consistency.sh`.
- [ ] Code-modifying skill? Carry the Mechanical Done Gate (spec §4) and add
      the skill to check 18's list.
- [ ] No ambiguous conditions ("as needed", "if appropriate" — check 30); no
      unscoped trigger verbs; hard negatives ≤5, safety-critical only.

## 4. References (only if the skill needs them)

- [ ] Rules files: `references/rules-*.md`, every rule a `### ID [SEVERITY]`
      level-3 heading (check 25), canonical severity vocabulary only (check
      15), IDs are skill-scoped — citing another skill's ID names the owner on
      the same line (check 26).
- [ ] Any "N rules across" claim in SKILL.md/README must match the actual
      heading count (check 17).
- [ ] Copying the shared `principles.md`? Byte-match the majority copy, or
      declare the difference with `<!-- variant: ... -->` in the first 5 lines
      (check 28).
- [ ] Dated external facts (store policies, fines, API requirements) open with
      the currency rule: "verified seed map, never the authority — re-verify
      against live official sources at run time".

## 5. Wire the catalog

- [ ] README badge count, CLAUDE.md heading + count line + flat list all
      increment (checks 1, 19).
- [ ] Delegation reciprocity: every skill you Delegate to must name yours back
      in its Receives (check 20) — that is an edit in the OTHER skill's file.
- [ ] Both trigger tables disambiguate against the nearest-neighbor skill
      (yours lists their phrase under DON'T INVOKE, and vice versa).

## 6. Prove it

- [ ] `bash scripts/quality.sh` → `all checks passed`.
- [ ] `./install.sh --target /tmp/lone-test --skills ds-{name}` → invoke the
      skill from that lone copy; every reference resolves, nothing dangles.
- [ ] Behaviour eval (recommended): add a fixture + scorer pair under
      `evals/tasks/` proving one core behaviour, self-tested in both
      directions (a scripted correct solution passes, a scripted broken one
      fails) — see `evals/README.md`.
- [ ] New consistency check added? It needs a fixture in `--self-test` or a
      mutation entry — a check without a proof is a no-op risk (AGENTS.md).

Size ceilings the gate enforces: SKILL.md ≤500 lines / ≤48,000 bytes;
README.md ≤80 lines (check 2).
