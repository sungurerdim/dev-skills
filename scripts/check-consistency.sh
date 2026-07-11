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
  grep -qP '^\*\*Dimensions:\*\*' "$f" || err "$f missing Dimensions: declaration"
  # Check carrier exclusion (layer E must not appear)
  if grep -qP '^\*\*Dimensions:\*\*.*E[0-9]' "$f"; then
    err "$f declares layer-E dimension (carriers cannot be dimensions)"
  fi
done

# 10. v4 — Advisory handoff pattern (SKILL-SPEC §12)
for f in ds-*/SKILL.md; do
  skill="${f%%/*}"
  # Skip orchestrators (they delegate by design)
  case "$skill" in ds-ship|ds-pipeline) continue;; esac
  # Detect hard-fail patterns
  if grep -qiP '"skill not found"|"install.*first"|hard.?fail' "$f" 2>/dev/null; then
    err "$f contains hard-fail pattern (violates standalone invariant)"
  fi
done

if [ "$fail" = "0" ]; then
  echo "OK: $dirs skills — sizes, delegation, ownership, state policy, W-registry, triggers, v4 dimensions, advisory-handoff all consistent"
else
  exit 1
fi
