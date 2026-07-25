#!/usr/bin/env bash
# Consistency gate for dev-skills — zero dependencies (bash + grep + awk).
# Run locally: ./scripts/check-consistency.sh    CI runs the same file.
# Self-test (proves the checks below actually fail on broken input):
#   ./scripts/check-consistency.sh --self-test
set -u
fail=0
err() { echo "FAIL: $*"; fail=1; }

# --- Checks 1, 8, 19, 20, 21, 22 are wrapped in functions purely so --self-test can run
#     them in isolation against a fixture directory; execution order/logic/
#     messages are otherwise identical to a plain top-to-bottom script. Each
#     function operates on $PWD, same as every other check in this file. The
#     remaining checks stay inline (unwrapped) — see BP-007 self-test note at
#     the bottom of this file for why they're not all fixture-tested. ---

# 1. Skill count == README badge count
check_skill_badge() {
  dirs=$(ls -d ds-*/ | wc -l | tr -d ' ')
  badge=$(grep -o 'skills-[0-9]*-blue' README.md | grep -o '[0-9]*')
  [ "$dirs" = "$badge" ] || err "skill dirs ($dirs) != README badge ($badge)"
}

# 8. Canonical gitignore: repo's own .gitignore has the ds/audit/ directory form,
#    and no SKILL.md documents a non-canonical variant (ds/audit/*.json, .ds-audit/, ds-audit/)
check_gitignore_canonical() {
  grep -qxF 'ds/audit/' .gitignore || err ".gitignore missing canonical 'ds/audit/' line"
  wrong=$(grep -rnE 'ds/audit/\*\.json|\.ds-audit/|(^|[^/-])ds-audit/' ds-*/SKILL.md || true)
  [ -z "$wrong" ] || err "non-canonical .gitignore pattern documented:
$wrong"
}

# 19. v5 — CLAUDE.md skill-count reciprocity (BP-002/BP-006/G4: heading, Skill
#     count line, and flat list must all agree with the actual ds-*/ dir count)
check_claude_md_counts() {
  dirs=$(ls -d ds-*/ | wc -l | tr -d ' ')
  heading_n=$(grep -oE '^## Skills \([0-9]+\)' CLAUDE.md | grep -oE '[0-9]+')
  [ "$heading_n" = "$dirs" ] || err "CLAUDE.md '## Skills ($heading_n)' heading != actual skill dirs ($dirs)"
  count_line_n=$(grep -oE '\*\*Skill count:\*\* [0-9]+' CLAUDE.md | grep -oE '[0-9]+')
  [ "$count_line_n" = "$dirs" ] || err "CLAUDE.md '**Skill count:** $count_line_n' line != actual skill dirs ($dirs)"
  flat_n=$(grep '^Flat list:' CLAUDE.md | grep -oE '`ds-[a-z-]+`' | wc -l | tr -d ' ')
  [ "$flat_n" = "$dirs" ] || err "CLAUDE.md 'Flat list:' enumerates $flat_n skills != actual skill dirs ($dirs)"
}

# 20. v5 — Full Delegates/Receives graph reciprocity (BP-006/BP-007/BP-008: every
#     skill's Delegates target must name the delegator back in its own Receives
#     line — SKILL-SPEC §10.2 rule 4). Orchestrators (ds-ship, ds-pipeline) are
#     excluded as sources, matching check 10's "they delegate by design" carve-out.
check_delegates_receives_graph() {
  for f in ds-*/SKILL.md; do
    src="${f%%/*}"
    case "$src" in ds-ship|ds-pipeline) continue;; esac
    deleg_line=$(awk '/^\*\*Owns:\*\*/{print; exit}' "$f")
    deleg_text=$(echo "$deleg_line" | sed -E 's/^.*\*\*Delegates:\*\* //; s/ \| \*\*Receives:\*\*.*//')
    echo "$deleg_text" | grep -qE '^none([^a-z]|$)' && continue
    for tgt in $(echo "$deleg_text" | grep -oE 'ds-[a-z][a-z-]*' | sort -u); do
      [ "$tgt" = "$src" ] && continue
      [ -f "$tgt/SKILL.md" ] || continue
      recv_line=$(awk '/^\*\*Owns:\*\*/{print; exit}' "$tgt/SKILL.md")
      recv_text=$(echo "$recv_line" | sed -E 's/^.*\*\*Receives:\*\* //')
      echo "$recv_text" | grep -qE "(^|[^a-z-])$src([^a-z-]|\$)" \
        || err "$f Delegates -> $tgt, but $tgt/SKILL.md:$(grep -n '^\*\*Owns:\*\*' "$tgt/SKILL.md" | cut -d: -f1) Receives does not reciprocate $src (SKILL-SPEC §10.2 rule 4)"
    done
  done
}

# 21. v6 — Standalone paths: a skill may never reference another skill's files by
#     path. Prose handoffs are fine (check 10 guards hard-fail wording); a file
#     path is not, because a lone install has no sibling directory to resolve it
#     against. `../agents/` is exempt — install.sh ships agents separately.
check_standalone_paths() {
  hits=$(grep -rnoE '\]\((\.\./)?ds-[a-z-]+/[^)]*\)' ds-*/SKILL.md ds-*/references/*.md 2>/dev/null || true)
  [ -z "$hits" ] || err "cross-skill file path — a lone install cannot resolve it (SKILL-SPEC Standalone Invariant):
$hits"
}

# 22. v6 — Intra-skill link resolution: every relative .md link inside a skill
#     must resolve AND stay inside that skill's own directory — a lone install
#     ships one directory, so a link escaping it is dead even when the repo
#     layout makes it look fine. Fenced code blocks are skipped: they hold
#     illustrative links, not real ones. Escapes that land back inside the same
#     skill (references/../SKILL.md) are legitimate and pass.
norm_path() {
  local seg out=() IFS=/
  for seg in $1; do
    case "$seg" in
      ''|.) ;;
      ..) [ "${#out[@]}" -gt 0 ] && unset 'out[${#out[@]}-1]' ;;
      *) out+=("$seg") ;;
    esac
  done
  printf '%s' "${out[*]}"
}
check_intra_skill_links() {
  bad=""
  for f in ds-*/SKILL.md ds-*/references/*.md; do
    [ -f "$f" ] || continue
    skill="${f%%/*}"; dir=$(dirname "$f")
    for l in $(awk '/^```/{fence=!fence; next} !fence' "$f" \
                 | grep -oE '\]\([^)]+\.md[^)]*\)' \
                 | sed -E 's/^\]\(//; s/\)$//; s/#.*$//' || true); do
      case "$l" in http*|'') continue;; esac
      target=$(norm_path "$dir/$l")
      case "$target" in
        "$skill"/*) [ -e "$target" ] || bad="$bad
  $f -> $l (no such file)" ;;
        *) bad="$bad
  $f -> $l (escapes $skill/ — not present in a lone install)" ;;
      esac
    done
  done
  [ -z "$bad" ] || err "link a lone install cannot follow:$bad"
}

# --- Self-test (BP-007): fixture-proves the checks above actually fail on
#     broken input. Builds a temp dir per check, deliberately breaks one
#     input, runs the real check function against it, asserts a FAIL: line
#     appears. Covers check_skill_badge (1), check_gitignore_canonical (8),
#     check_claude_md_counts (19), check_delegates_receives_graph (20),
#     check_standalone_paths (21) and check_intra_skill_links (22) —
#     the 6 checks factored into standalone functions. The remaining checks
#     (2-7, 9-18) stay inline and entangled with full-repo state (SKILL-SPEC.md
#     dimension table, agents/*.md, references/*.md globs, hardcoded skill
#     lists) — fixturing them cheaply would mean re-deriving large slices of
#     those inputs, so per the task's own "don't force it" allowance they are
#     left uncovered by this fixture harness. Cleans up on exit regardless of
#     outcome. ---
assert_catches() {
  local name="$1" dir="$2" fn="$3" out
  out=$(cd "$dir" && fail=0 && "$fn" 2>&1)
  if echo "$out" | grep -q '^FAIL:'; then
    echo "SELF-TEST OK: $name caught the fixture:"
    echo "$out" | sed 's/^/  /'
  else
    echo "SELF-TEST BROKEN: $name did NOT catch the deliberately-broken fixture (no-op check)"
    st_fail=1
  fi
}

self_test() {
  local tmp
  st_fail=0
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' RETURN

  # Fixture: check_skill_badge — 2 skill dirs, README badge claims 99
  mkdir -p "$tmp/f1/ds-alpha" "$tmp/f1/ds-beta"
  printf '![skills](https://img.shields.io/badge/skills-99-blue)\n' > "$tmp/f1/README.md"
  assert_catches "check_skill_badge" "$tmp/f1" check_skill_badge

  # Fixture: check_gitignore_canonical — .gitignore missing the canonical line
  mkdir -p "$tmp/f2/ds-alpha"
  printf 'node_modules/\n' > "$tmp/f2/.gitignore"
  printf '**Owns:** x | **Delegates:** none | **Receives:** none\n' > "$tmp/f2/ds-alpha/SKILL.md"
  assert_catches "check_gitignore_canonical" "$tmp/f2" check_gitignore_canonical

  # Fixture: check_claude_md_counts — 2 skill dirs, CLAUDE.md still says 5
  mkdir -p "$tmp/f3/ds-alpha" "$tmp/f3/ds-beta"
  cat > "$tmp/f3/CLAUDE.md" <<'EOF'
## Skills (5)

- **Skill count:** 5

Flat list: `ds-alpha`, `ds-beta`
EOF
  assert_catches "check_claude_md_counts" "$tmp/f3" check_claude_md_counts

  # Fixture: check_delegates_receives_graph — ds-alpha delegates to ds-beta,
  # but ds-beta's Receives never names ds-alpha back (BP-008-shaped gap)
  mkdir -p "$tmp/f4/ds-alpha" "$tmp/f4/ds-beta"
  printf '**Owns:** a | **Delegates:** ds-beta -> some task | **Receives:** none\n' > "$tmp/f4/ds-alpha/SKILL.md"
  printf '**Owns:** b | **Delegates:** none | **Receives:** ds-gamma -> unrelated\n' > "$tmp/f4/ds-beta/SKILL.md"
  assert_catches "check_delegates_receives_graph" "$tmp/f4" check_delegates_receives_graph

  # Fixture: check_standalone_paths — ds-alpha reads ds-beta's reference file
  mkdir -p "$tmp/f5/ds-alpha/references" "$tmp/f5/ds-beta/references"
  printf 'See [beta rules](../ds-beta/references/rules.md) for detail.\n' > "$tmp/f5/ds-alpha/SKILL.md"
  printf '# rules\n' > "$tmp/f5/ds-beta/references/rules.md"
  assert_catches "check_standalone_paths" "$tmp/f5" check_standalone_paths

  # Fixture: check_intra_skill_links — a missing reference file and a link that
  # escapes the skill directory; the illustrative link inside a fence and the
  # legitimate references/../SKILL.md escape-and-return must NOT be flagged
  mkdir -p "$tmp/f6/ds-alpha/references" "$tmp/f6/agents"
  cat > "$tmp/f6/ds-alpha/SKILL.md" <<'EOF'
Real link: [gone](references/missing.md)
Escaping link: [agent](../agents/worker.md)

```markdown
Illustrative only: [Configuration](./docs/config.md)
```
EOF
  printf 'Back to [/ds-alpha](../SKILL.md).\n' > "$tmp/f6/ds-alpha/references/ok.md"
  printf '# worker\n' > "$tmp/f6/agents/worker.md"
  assert_catches "check_intra_skill_links" "$tmp/f6" check_intra_skill_links

  if [ "$st_fail" = "0" ]; then
    echo "SELF-TEST PASS: all 6 fixtured checks correctly caught their deliberately-broken input"
  else
    echo "SELF-TEST FAIL: at least one check is a no-op against broken input (see SELF-TEST BROKEN lines above)"
  fi
  return "$st_fail"
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
  exit $?
fi

cd "$(dirname "$0")/.."

check_skill_badge

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

check_gitignore_canonical

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

check_claude_md_counts
check_delegates_receives_graph
check_standalone_paths
check_intra_skill_links

if [ "$fail" = "0" ]; then
  echo "OK: $dirs skills — sizes, delegation, ownership, state policy, W-registry, triggers, v4 dimensions, advisory-handoff, taxonomy-membership, overlap, evidence-band, flag-integrity, severity-vocab, list-table-spacing, rule-count-claims, mechanical-done-gate, claude-md-count-reciprocity, delegates-receives-graph-reciprocity, standalone-paths, intra-skill-links all consistent"
else
  exit 1
fi
