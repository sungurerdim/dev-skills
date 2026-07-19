#!/usr/bin/env bash
# Consistency gate for dev-skills — zero dependencies (bash + grep + awk).
# Run locally: ./scripts/check-consistency.sh    CI runs the same file.
set -u
cd "$(dirname "$0")/.."
fail=0
err() { echo "FAIL: $*"; fail=1; }

# 1. Skill count == README badge count
dirs=$(ls -d ds-*/ | wc -l | tr -d ' ')
badge=$(grep -o 'skills-[0-9]*-blue' README.md | grep -o '[0-9]*')
[ "$dirs" = "$badge" ] || err "skill dirs ($dirs) != README badge ($badge)"

# 2. Size ceilings (SKILL-SPEC section 8)
for f in ds-*/SKILL.md; do
  n=$(wc -l < "$f")
  [ "$n" -le 500 ] || err "$f is $n lines (ceiling 500)"
done
for f in ds-*/README.md; do
  n=$(wc -l < "$f")
  [ "$n" -le 80 ] || err "$f is $n lines (ceiling 80)"
done

# 3. Delegation line: exactly one spec-parseable line per skill (SKILL-SPEC section 10.2)
for f in ds-*/SKILL.md; do
  c=$(grep -cE '^\*\*Owns:\*\* [^|]+ \| \*\*Delegates:\*\* [^|]+ \| \*\*Receives:\*\* .+$' "$f")
  [ "$c" = "1" ] || err "$f has $c delegation lines (expected exactly 1)"
done

# 4. Single authoritative producer per scope: no token in two Owns lists
dups=$(for d in ds-*/; do
  awk -v s="${d%/}" '/^\*\*Owns:/{line=$0; sub(/^\*\*Owns:\*\* /,"",line); sub(/ \| \*\*Delegates.*/,"",line);
    n=split(line,a,","); for(i=1;i<=n;i++){t=a[i]; gsub(/^ +| +$/,"",t); sub(/ \(.*/,"",t); print t"\t"s}}' "$d/SKILL.md"
done | sort | awk -F'\t' '{if($1==p) print $1" -> "s" + "$2; p=$1; s=$2}')
[ -z "$dups" ] || err "duplicate Owns tokens:
$dups"

# 5. Resumable-state protocol only in the 4 qualifying skills (SKILL-SPEC section 5)
allowed="ds-blueprint ds-ship ds-solve ds-tune"
for f in $(grep -ln 'DETECT `ds/audit/' ds-*/SKILL.md); do
  skill=${f%%/*}
  case " $allowed " in *" $skill "*) ;; *) err "$skill carries state recovery protocol (only $allowed qualify)";; esac
done
for s in $allowed; do
  grep -q 'DETECT `ds/audit/' "$s/SKILL.md" || err "$s lost its state recovery protocol"
done

# 6. W-registry: no weakness numbers beyond W17 in runtime files
bogus=$(grep -rno 'W1[89]\|W2[0-9]' ds-*/SKILL.md ds-*/references ds-*/README.md agents/*.md 2>/dev/null || true)
[ -z "$bogus" ] || err "bogus W-numbers (registry is W1-W17):
$bogus"

# 7. Trigger Discipline: INVOKE / DON'T INVOKE table (real table shape, not just the bare string)
for f in ds-*/SKILL.md; do
  header=$(grep -cE '^\| *INVOKE *\| *.*DON.T INVOKE.* *\|$' "$f")
  [ "$header" -ge "1" ] || err "$f missing an INVOKE / DON'T INVOKE table header row"
done

# 8. Canonical gitignore: repo's own .gitignore has the ds/audit/ directory form,
#    and no SKILL.md documents a non-canonical variant (ds/audit/*.json, .ds-audit/, ds-audit/)
grep -qxF 'ds/audit/' .gitignore || err ".gitignore missing canonical 'ds/audit/' line"
wrong=$(grep -rnE 'ds/audit/\*\.json|\.ds-audit/|(^|[^/-])ds-audit/' ds-*/SKILL.md || true)
[ -z "$wrong" ] || err "non-canonical .gitignore pattern documented:
$wrong"

# 9. v4 — Dimension Declaration presence (SKILL-SPEC §11)
for f in ds-*/SKILL.md; do
  grep -qE '^\*\*Dimensions:\*\*' "$f" || err "$f missing Dimensions: declaration"
  # Check carrier exclusion (layer E must not appear)
  if grep -qE '^\*\*Dimensions:\*\*.*E[0-9]' "$f"; then
    err "$f declares layer-E dimension (carriers cannot be dimensions)"
  fi
done

# 10. v4 — Advisory handoff pattern (SKILL-SPEC §12)
for f in ds-*/SKILL.md; do
  skill="${f%%/*}"
  # Skip orchestrators (they delegate by design)
  case "$skill" in ds-ship|ds-pipeline) continue;; esac
  # Detect hard-fail patterns
  if grep -qiE '"skill not found"|"install.*first"|hard.?fail' "$f" 2>/dev/null; then
    err "$f contains hard-fail pattern (violates standalone invariant)"
  fi
done

# 11. v4 — Taxonomy membership: every declared dimension ID exists as a row in
#     SKILL-SPEC.md's Dimension Table appendix (SKILL-SPEC §11, §14)
valid_dims=$(awk -F'|' '/^\| [A-D][0-9]+ \|/{gsub(/^ +| +$/,"",$2); print $2}' SKILL-SPEC.md)
for f in ds-*/SKILL.md; do
  line=$(awk '/^\*\*Dimensions:\*\*/{print; exit}' "$f")
  ids=$(echo "$line" | sed -E 's/^\*\*Dimensions:\*\* *//; s/\([^)]*\)//g' | tr ',' '\n' | sed -E 's/^ +| +$//g')
  for id in $ids; do
    [ -z "$id" ] || [ "$id" = "none" ] && continue
    echo "$valid_dims" | grep -qxF "$id" || err "$f declares unknown dimension '$id' (not in SKILL-SPEC.md Dimension Table)"
  done
done

# 12. v4 — Overlap detection: a dimension declared by 2+ skills must have all of
#     them named in the appendix's Owning Skill(s) column for that row (SKILL-SPEC §11)
pairs=$(for f in ds-*/SKILL.md; do
  skill="${f%%/*}"
  line=$(awk '/^\*\*Dimensions:\*\*/{print; exit}' "$f")
  echo "$line" | sed -E 's/^\*\*Dimensions:\*\* *//; s/\([^)]*\)//g' | tr ',' '\n' | sed -E 's/^ +| +$//g' | while read -r id; do
    [ -z "$id" ] || [ "$id" = "none" ] && continue
    echo "$id	$skill"
  done
done)
for id in $(echo "$pairs" | cut -f1 | sort -u); do
  skills=$(echo "$pairs" | awk -F'\t' -v d="$id" '$1==d{print $2}')
  count=$(echo "$skills" | wc -l)
  [ "$count" -le 1 ] && continue
  owner_text=$(awk -F'|' -v d="$id" '/^\| [A-D][0-9]+ \|/{gsub(/^ +| +$/,"",$2); if($2==d){gsub(/^ +| +$/,"",$4); print $4}}' SKILL-SPEC.md)
  unauthorized=""
  for s in $skills; do
    echo "$owner_text" | grep -qF -- "$s" || unauthorized="$unauthorized $s"
  done
  [ -n "$unauthorized" ] && err "dimension $id declared by multiple skills ($(echo $skills | tr '\n' ' ')) not all listed in appendix owner column '$owner_text' — unauthorized:$unauthorized"
done

# 13. v5 — Completion Evidence band: exactly 2 verbatim copies per SKILL.md,
#     opening copy before the first '## ' section, closing copy in the last 3 lines
#     (SKILL-SPEC section 1, Completion Evidence Band)
for f in ds-*/SKILL.md; do
  n=$(grep -c '^> \*\*Completion Evidence — ' "$f")
  [ "$n" = "2" ] || { err "$f has $n Completion Evidence bands (expected exactly 2)"; continue; }
  first_band=$(grep -n '^> \*\*Completion Evidence — applies to every phase:' "$f" | head -1 | cut -d: -f1)
  first_sec=$(grep -n '^## ' "$f" | head -1 | cut -d: -f1)
  [ -n "$first_band" ] && [ -n "$first_sec" ] && [ "$first_band" -lt "$first_sec" ] \
    || err "$f opening Completion Evidence band missing or not before first '## ' section"
  tail -3 "$f" | grep -q '^> \*\*Completion Evidence — final gate' \
    || err "$f closing Completion Evidence band not in last 3 lines"
done

# 14. v5 — Flag integrity: a mode flag this skill uses in its own body must be
#     defined in its Arguments table (ghost-flag class — found 9x in the 2026-07 audit).
#     Lines referencing other skills (/ds-*) are excluded from the usage scan.
#     force-approve/dry-run/no-interactive/confirm are retired (folded into --auto
#     or renamed — see SKILL-SPEC.md Unattended Mode) and MUST NOT reappear.
for f in ds-*/SKILL.md; do
  for flag in auto preview resume clean status static run; do
    grep -v '/ds-' "$f" | grep -q "\`--$flag\`" || continue
    grep -qE "^\| *.?\`--$flag" "$f" || err "$f uses \`--$flag\` but its Arguments table does not define it"
  done
  for retired in force-approve dry-run no-interactive confirm; do
    grep -q -- "--$retired\b" "$f" && err "$f references retired flag --$retired (see SKILL-SPEC.md Unattended Mode / Flag Vocabulary)"
  done
done

# 14b. v5 — Every skill's Arguments table MUST define --auto with the canonical
#      contract (SKILL-SPEC.md §2 Unattended Mode) — no skill-local variant/omission.
for f in ds-*/SKILL.md; do
  grep -qE "^\| *.?\`--auto\`" "$f" || err "$f Arguments table missing mandatory --auto row (SKILL-SPEC.md Unattended Mode)"
done

# 15. v5 — Severity vocabulary: rule files use only the canonical set
#     (BLOCKER/CRITICAL/HIGH/MEDIUM/LOW/ADVISORY/INFO); MAJOR/MINOR are banned.
bad_sev=$(grep -rno '\[MAJOR\]\|\[MINOR\]' ds-*/references/*.md 2>/dev/null; grep -rnoE '[0-9]+ (MAJOR|MINOR)\b' ds-*/references/*.md 2>/dev/null; true)
[ -z "$bad_sev" ] || err "non-canonical severity vocabulary (MAJOR/MINOR banned — map to HIGH/MEDIUM):
$bad_sev"

# 16. v5 — List→table spacing: a table row starting directly on the line after a
#     list item breaks GFM rendering (blank line required).
bad_spacing=$(awk 'FNR==1{prev=""} prev ~ /^[-*] / && /^\|/ {print FILENAME":"FNR} {prev=$0}' ds-*/SKILL.md ds-*/references/*.md agents/*.md 2>/dev/null || true)
[ -z "$bad_spacing" ] || err "table starts directly after a list item (insert a blank line):
$bad_spacing"

# 17. v5 — Rule-count claims: 'N rules across' claims in SKILL.md/README.md must
#     match the actual ### header count in that skill's references/rules-*.md files.
for d in ds-*/; do
  s=${d%/}
  actual=$(cat "$d"references/rules-*.md 2>/dev/null | grep -c '^### ')
  [ "$actual" -gt 0 ] 2>/dev/null || continue
  for f in "$d"SKILL.md "$d"README.md; do
    [ -f "$f" ] || continue
    claim=$(grep -hoE '[0-9]+ rules across' "$f" 2>/dev/null | grep -oE '[0-9]+' | head -1)
    [ -n "$claim" ] || continue
    [ "$claim" = "$actual" ] || err "$f claims '$claim rules across' but $s/references/rules-*.md contain $actual"
  done
done

# 18. v5 — Mechanical Done Gate: every code-modifying skill carries the gate
#     (SKILL-SPEC section 4, Mechanical Done Gate). List = skills that create or
#     modify project files; read-only/planning skills are exempt by design.
for s in ds-compliance ds-freeze ds-init ds-backend ds-frontend ds-mobile ds-review ds-simplify ds-fix ds-test ds-deps ds-tune ds-solve ds-issue ds-commit; do
  grep -q "Mechanical Done Gate" "$s/SKILL.md" 2>/dev/null \
    || err "$s/SKILL.md missing Mechanical Done Gate (SKILL-SPEC section 4 — code-modifying skill)"
done

if [ "$fail" = "0" ]; then
  echo "OK: $dirs skills — sizes, delegation, ownership, state policy, W-registry, triggers, v4 dimensions, advisory-handoff, taxonomy-membership, overlap, evidence-band, flag-integrity, severity-vocab, list-table-spacing, rule-count-claims, mechanical-done-gate all consistent"
else
  exit 1
fi
