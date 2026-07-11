# Quickstart: v4 Transformation Validation Guide

**Phase**: Phase 1 — Design & Contracts
**Feature**: v4 Dimension Coverage Taxonomy + Standalone + AI-Legibility
**Date**: 2026-07-11

---

## Prerequisites

- Repository cloned at `D:\GitHub\dev-skills`
- Claude Code CLI installed (for `/full-review` command)
- Bash shell available (for `check-consistency.sh`)
- Git available for staging/commit verification
- Phase 0.5 baseline measurement completed (`ds/audit/v4-baseline.json`)

---

## Validation Scenarios

Each scenario validates a specific FR/Success Criterion from the specification. Run in order.

---

### V1: Baseline Measurement (FR8.1)

**Setup**: No prior transformation work done.

**Steps**:
1. Run the baseline measurement commands against the current state:
   ```bash
   # Line count per SKILL.md
   for f in ds-*/SKILL.md SKILL-SPEC.md; do wc -l "$f"; done | sort -r -t' ' -k1,1n
   ```
2. Compare total against the spec's stated baseline (8,545 lines across 28 SKILL.md, 1,883 for SKILL-SPEC.md)
3. Record results to `ds/audit/v4-baseline.json`

**Expected outcome**: Total matches 8,545 ± 1% for skills, 1,883 ± 1% for SKILL-SPEC. Any variance >1% indicates the baseline needs updating before Phase 5 token reports are meaningful.

---

### V2: Taxonomy Appendix Created (FR1.3)

**Setup**: After Phase 2 completion.

**Steps**:
1. Open `SKILL-SPEC.md` and locate the "Appendix: Dimension Coverage Map" section
2. Verify the table contains all rows from the taxonomy (A1 through D9, plus E carriers)
3. Verify each row has non-empty `#`, `Boyut`, `Sahip skill (scope)` columns

**Expected outcome**: A normative appendix exists in SKILL-SPEC.md with all 28 dimensions (A1–D9 inclusive) plus the E carrier row. No dimension is missing and no column is empty for any dimension row.

---

### V3: Dimension Declaration Check (FR4.1, SC5)

**Setup**: After Phase 4 scope expansions complete.

**Steps**:
1. Run the dimension declaration check:
   ```bash
   bash scripts/check-consistency.sh
   ```
2. Exit code must be 0
3. To test rejection, create a test branch with a SKILL.md that has no `Dimensions:` line:
   ```bash
   cp ds-review/SKILL.md /tmp/review-no-dim.md
   # Remove the Dimensions: line from /tmp/review-no-dim.md
   cp /tmp/review-no-dim.md ds-review/SKILL.md
   bash scripts/check-consistency.sh
   ```
4. Exit code must be non-zero (1+)
5. `git checkout -- ds-review/SKILL.md` to restore

**Expected outcome**: `check-consistency.sh` exits 0 with all valid declarations. Exits non-zero when a declaration is missing, proving the automated gate works (SC5).

---

### V4: Overlap Detection (FR4.3, SC5)

**Setup**: After Phase 2 (check-consistency.sh v4 extensions).

**Steps**:
1. Verify the overlap check is in the script:
   ```bash
   grep -n "overlap\|aynı boyut" scripts/check-consistency.sh
   ```
2. Run the script — it should exit 0 (no overlaps in current state)
3. Verify the script reports no overlap findings

**Expected outcome**: The overlap-detection check exists in the script and reports zero violations against the current state. This proves the automated overlap gate works.

---

### V5: Standalone Operation — Single Skill Run (FR2.1, SC2)

**Setup**: After Phase 5 (all 28 skills rewritten).

**Steps**:
1. Select 3 sample non-orchestrator skills (e.g., ds-review, ds-docs, ds-test)
2. For each skill, read the SKILL.md and verify:
   - Every cross-skill reference uses the advisory-handoff pattern
   - No hard-fail patterns exist (`"skill not found"`, `"install X first"` as error-stop)
   - The `Receives:` line in the Delegation section includes an advisory-handoff note
3. Grep for advisory-handoff:
   ```bash
   grep -c "advisory-handoff\|inline\|gap note\|delegate if present" ds-review/SKILL.md
   ```
4. Count should be ≥1 (at least one handoff pattern)

**Expected outcome**: All 3 sampled skills use the advisory-handoff pattern and contain no hard-fail patterns.

---

### V6: Ambiguity-Free AI-Legible Text (FR3.1, SC4)

**Setup**: After Phase 5 (all 28 skills rewritten).

**Steps**:
1. Run the ambiguity detection across all 28 SKILL.md files:
   ```bash
   grep -in "if appropriate\|consider\|may want to\|as needed" ds-*/SKILL.md
   ```
2. Count should be 0 (excluding literal matches in example/placeholder text)
3. Repeat for gate-arm completeness:
   ```bash
   grep -c "If fails →" ds-*/SKILL.md
   ```
4. The count should be high — every gate should have a failure arm

**Expected outcome**: Zero ambiguous phrase matches in instruction text. Every gate line has an `If fails →` arm.

---

### V7: Token Reduction Verified (FR3.2, SC3)

**Setup**: After Phase 5 completion.

**Steps**:
1. Re-run the Phase 0.5 token measurement against all 28 SKILL.md:
   ```bash
   for f in ds-*/SKILL.md; do
     chars=$(sed '1,/^---$/d' "$f" | sed '/^---/,$d' | wc -c)
     tokens=$(( chars / 4 ))
     echo "$f: $tokens tokens"
   done
   ```
   (Note: the frontmatter strip assumes `---` at start — adjust if some skills use different frontmatter markers)
2. Compare total against the baseline from `ds/audit/v4-baseline.json`
3. The aggregate total should be lower (token reduction)

**Expected outcome**: Total token estimate after Phase 5 is strictly less than the Phase 0.5 baseline. The aggregate delta is reported as a percentage.

---

### V8: Rule Preservation (FR3.3)

**Setup**: After Phase 5 completion.

**Steps**:
1. Run the rule counter against each skill:
   ```bash
   grep -cE "verify|check|ensure|enforce|MUST|kural|doğrula|denetle" ds-*/SKILL.md
   ```
2. Compare per-skill counts against the Phase 0.5 baseline
3. For any skill with a decrease, verify that a written justification exists

**Expected outcome**: No skill has a decreased rule count without a written justification in the Phase 5 batch report.

---

### V9: ds-ship Dimension Coverage Report (FR5.1, SC6)

**Setup**: After Phase 3 completion.

**Steps**:
1. Read ds-ship Phase 6 report format in `ds-ship/SKILL.md`
2. Verify the report template includes a "Dimension Coverage" section:
   ```bash
   grep -A 10 "Dimension Coverage\|Boyut kapsamı" ds-ship/SKILL.md
   ```
3. Verify the table has columns: Dimension, Status, Owning Skill, Notes
4. Verify the three status values are documented: `audited`, `owner-skipped`, `unowned`
5. Verify `unowned` status triggers an explicit warning

**Expected outcome**: The ds-ship Phase 6 report template includes the Dimension Coverage section with the required columns and status values. Unowned dimensions trigger warnings.

---

### V10: End-to-End Program Self-Consistency (SC7)

**Setup**: After Phase 6 reconciliation.

**Steps**:
1. Run the consistency check:
   ```bash
   bash scripts/check-consistency.sh
   if ($?) { echo "PASS: exit 0" } else { echo "FAIL" }
   ```
2. Run the full review:
   ```bash
   /full-review
   ```
3. Verify tasks.md — every item should be `[x]`:
   ```bash
   grep -c "\[ \]" tasks.md ; if ($?) { echo "HAS OPEN ITEMS" } else { echo "ALL COMPLETE" }
   ```

**Expected outcome**: `check-consistency.sh` exits 0, `/full-review` reports 8+ green categories with zero CRITICAL/HIGH findings, and tasks.md has zero open `[ ]` items.

---

### V11: Taxonomy Amendment Process Exists (FR1.6)

**Setup**: After Phase 6 reconciliation.

**Steps**:
1. Search SKILL-SPEC.md for the amendment process section:
   ```bash
   grep -A 20 "Taxonomy Amendment\|Boyut ekleme" SKILL-SPEC.md
   ```
2. Verify all 4 steps exist: (1) propose via issue/PR with dimension name, layer, skill, framework reference; (2) gate: no existing skill covers this surface; (3) gate: owning skill has capacity; (4) after merge: three files updated (SKILL.md, SKILL-SPEC appendix, ds-ship report)

**Expected outcome**: The amendment process section exists in SKILL-SPEC with all 4 required steps.

---

### V12: Pre-Expansion Size Audit (FR7.7)

**Setup**: Before Phase 4 scope expansions.

**Steps**:
1. Create the pre-expansion size audit table as a script:
   ```bash
   echo "Skill | Current lines | Class ceiling | Est. expansion | Post-exp. est. | Safe?"
   echo "------|-------------|---------------|----------------|---------------|------"
   # Check each skill being expanded
   for skill in ds-frontend ds-launch ds-review ds-backend ds-docs ds-mobile ds-compliance; do
     lines=$(wc -l < "$skill/SKILL.md")
     # Determine ceiling based on class...
   done
   ```
2. Verify each skill's post-expansion estimate does not exceed its ceiling
3. For any skill at risk, verify reference externalization was done before expansion

**Expected outcome**: All expanded skills' estimated post-expansion line counts are below their class ceiling. Skills at risk have had content externalized to `references/` before expansion.
