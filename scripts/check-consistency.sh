#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Consistency gate for dev-skills — zero dependencies (bash + grep + awk).
# Run locally: ./scripts/check-consistency.sh    CI runs the same file.
# Self-test (proves the checks below actually fail on broken input):
#   ./scripts/check-consistency.sh --self-test
set -u
fail=0
err() { echo "FAIL: $*"; fail=1; }

# --- Most checks are wrapped in functions so --self-test can fixture them; the
#     inline checks are proven by --mutation-test. Each function operates on $PWD,
#     same as every other check in this file. ---

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

# 21. v7 — Core links: every relative .md link inside a skill must resolve AND land
#     either inside that skill's own directory or inside core/ — the two places a
#     lone install ships (install.sh copies core/ on every install). A link into a
#     sibling skill or anywhere else is dead in a lone install even when the repo
#     layout makes it look fine. Fenced code blocks are skipped: they hold
#     illustrative links, not real ones. Escapes that land back inside the same
#     skill (references/../SKILL.md) are legitimate and pass. Replaces the v6
#     standalone-paths + intra-skill-links pair.
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
check_core_links() {
  bad=""
  for f in ds-*/SKILL.md ds-*/README.md ds-*/references/*.md; do
    [ -f "$f" ] || continue
    skill="${f%%/*}"; dir=$(dirname "$f")
    for l in $(awk '/^```/{fence=!fence; next} !fence' "$f" \
                 | grep -oE '\]\([^)]+\.md[^)]*\)' \
                 | sed -E 's/^\]\(//; s/\)$//; s/#.*$//' || true); do
      case "$l" in http*|'') continue;; esac
      target=$(norm_path "$dir/$l")
      case "$target" in
        "$skill"/*|core/*) [ -e "$target" ] || bad="$bad
  $f -> $l (no such file)" ;;
        ds-*/*) bad="$bad
  $f -> $l (points into a sibling skill — absent from a lone $skill install)" ;;
        *) bad="$bad
  $f -> $l (escapes $skill/ and core/ — not present in a lone install)" ;;
      esac
    done
  done
  [ -z "$bad" ] || err "link a lone install cannot follow:$bad"
}
# 23. v6 — Bare in-repo path citations. Check 22 covers markdown links; a skill can
#     still tell the reader to open a repo file in plain prose ("sources in
#     `docs/methodology/cross-host-program.md`"), which a lone install cannot follow
#     either. Only paths that actually EXIST in this repo and sit outside the citing
#     skill are flagged — `docs/adr/`, `docs/user/FAQ.md` and friends are paths in the
#     *user's* project and must stay clean. A line carrying an http(s) URL is exempt:
#     that is the repo's convention for pointing at its own files resolvably.
#     Scoped to docs/ and specs/ deliberately: those hold provenance a skill cites and
#     expects the reader to open. scripts/ and agents/ paths in skill text are almost
#     always instruction targets in the *user's* project (ds-quality's "create
#     scripts/quality.sh"), and flagging them by name collision with this repo would
#     be a false positive. Known limitation: a provenance citation of scripts/ or
#     agents/ would slip past — check 21/22 still cover the link-shaped case.
check_bare_repo_paths() {
  bad=""
  for f in ds-*/SKILL.md ds-*/README.md ds-*/references/*.md; do
    [ -f "$f" ] || continue
    skill="${f%%/*}"
    # One awk pass per file — fence-strip, drop URL-carrying lines, and emit every
    # candidate path. Doing this with a grep per line made the gate ~40x slower.
    for p in $(awk '
      /^```/ { fence = !fence; next }
      fence { next }
      /https?:\/\// { next }
      {
        s = $0
        while (match(s, /(^|[^A-Za-z0-9_\/.-])(specs|docs)\/[A-Za-z0-9._\/-]+/)) {
          p = substr(s, RSTART, RLENGTH)
          sub(/^[^A-Za-z]/, "", p)
          print p
          s = substr(s, RSTART + RLENGTH)
        }
      }' "$f"); do
      p="${p%.}"; p="${p%,}"; p="${p%\`}"
      [ -f "$p" ] || continue                 # not a FILE of this repo — user-project path, or a
                                              #   directory layout the skill proposes (docs/adr/, docs/api/)
      case "$p" in "$skill"/*) continue;; esac # the skill's own directory is fine
      bad="$bad
  $f -> $p (exists in this repo, absent from a lone $skill install — link it by URL or drop the path)"
    done
  done
  [ -z "$bad" ] || err "bare in-repo path a lone install cannot follow:$bad"
}
# 24. v6 — CRITICAL carve-out in severity-graded approval menus. The All-Affordance
#     Rule lets a menu offer "approve all", but CRITICAL items must still be
#     confirmed one by one. A skill that abbreviates its approval block to a
#     reference ("apply the approval-menu convention") loses that rule entirely,
#     and a lone install has nowhere else to read it — which is how ds-devops
#     dropped it. Scoped to blocks that actually grade by severity: ds-benchmark
#     decides gaps, ds-build decides steps, ds-brief decides claims — none of them
#     has a CRITICAL severity to carve out, so none is required to mention it.
check_approval_critical_carveout() {
  bad=""
  for f in ds-*/SKILL.md; do
    [ -f "$f" ] || continue
    while IFS= read -r line; do
      case "$line" in
        *'**Interactive:**'*'per-severity bulk'*)
          case "$line" in
            *'excludes CRITICAL'*|*'CRITICAL bulk still confirms'*) ;;
            *) bad="$bad
  $f (severity-graded approval menu without the CRITICAL carve-out)" ;;
          esac ;;
      esac
    done < "$f"
  done
  [ -z "$bad" ] || err "approval menu drops the CRITICAL carve-out (All-Affordance Rule):$bad"
}

# 23. v7 — Canonical --ask row (SKILL-SPEC Autonomous Default: "every skill pastes
#     this verbatim"). Compares the EFFECT cell (last cell) of each skill's `--ask`
#     Arguments row against the canonical text in SKILL-SPEC.md, so a table with an
#     extra Default column still passes while reworded, narrowed or locally
#     re-derived text fails. Per-skill carve-outs belong in the skill's Contract,
#     citing the ask-exception list, never in this row.
check_ask_row_canonical() {
  local canon skill row effect
  canon=$(grep -m1 '^| `--ask` | Interactive run' SKILL-SPEC.md \
          | sed 's/.*| \(Interactive run.*\) |$/\1/')
  [ -n "$canon" ] || { err "SKILL-SPEC.md: canonical --ask row not found"; return; }
  for skill in ds-*/; do
    [ -f "$skill/SKILL.md" ] || continue
    row=$(awk '/^\| `--ask` \|/{print; exit}' "$skill/SKILL.md")
    [ -n "$row" ] || { err "$skill/SKILL.md missing the mandatory --ask Arguments row"; continue; }
    effect=$(printf '%s' "$row" | sed 's/.*| \(Interactive run.*\) |$/\1/')
    [ "$effect" = "$canon" ] \
      || err "$skill/SKILL.md --ask row deviates from the SKILL-SPEC canonical text (carve-outs go in Contract, citing the ask-exception list)"
  done
}

# 27. v6.1 — Portable-only marker hygiene (SKILL-SPEC §1 Portable-only markers):
#     `install.sh --profile lean` strips marked lines at install time, so the
#     spec-named blocks must carry the marker, block markers must balance, and no
#     table row may be marked (stripping a row corrupts `|$`-anchored checks).
check_portable_only_markers() {
  local f m s e bad
  m='<!-- portable-only -->'
  for f in ds-*/SKILL.md; do
    [ -f "$f" ] || continue
    grep -E '^> \*\*Completion Evidence — final gate' "$f" | grep -qF "$m" \
      || err "$f closing Completion Evidence band lacks the portable-only marker (lean install cannot strip it)"
    if grep -qE '^- Pre-existing' "$f"; then
      grep -E '^- Pre-existing' "$f" | grep -qF "$m" \
        || err "$f pre-existing-errors contract bullet lacks the portable-only marker"
    fi
    if grep -qE '^- W1: cite file:line' "$f"; then
      grep -E '^- W1: cite file:line' "$f" | grep -qF "$m" \
        || err "$f generic W-recap line lacks the portable-only marker"
    fi
    s=$(grep -c 'portable-only:start' "$f"); e=$(grep -c 'portable-only:end' "$f")
    [ "$s" = "$e" ] || err "$f has $s portable-only:start vs $e portable-only:end markers (unbalanced block)"
    bad=$(grep -nE '^\|.*portable-only' "$f" || true)
    [ -z "$bad" ] || err "$f marks a table row portable-only (lean strip would corrupt the table):
$bad"
  done
}

# 29. v6.2 — Gate two-arm form: every phase gate names a failure arm as `If … →`
#     (SKILL-SPEC Phase Template). A pass-only gate leaves the model to silently
#     proceed, invent recovery, or stall.
check_gate_two_arm() {
  local bad
  bad=$(grep -n '^\*\*Gate:\*\*' ds-*/SKILL.md | grep -vE 'If .*→' || true)
  [ -z "$bad" ] || err "gate line without an 'If … →' failure arm (SKILL-SPEC Phase Template):
$bad"
}

# 30. v6.2 — Ambiguous-condition phrasing ban (SKILL-SPEC §13 AI-Legibility rule f):
#     a condition the executor cannot evaluate mechanically is a condition that
#     silently becomes model mood.
check_ambiguous_phrases() {
  local bad
  bad=$(grep -rniE 'if appropriate|as needed|may want to|should consider|it is recommended' ds-*/SKILL.md || true)
  [ -z "$bad" ] || err "ambiguous condition phrasing (state the condition explicitly — SKILL-SPEC §13f):
$bad"
}

# 31. v6.2 — Marketing-word denylist (SKILL-SPEC Skill Voice forbidden list).
#     'innovative' is deliberately absent: it is ds-frontend's --style-mode value,
#     a flag vocabulary term, not voice.
check_marketing_words() {
  local bad
  bad=$(grep -rniwE 'leverage|empower|unlock|seamlessly|cutting-edge|next-generation|world-class|holistic|synergy' ds-*/SKILL.md ds-*/README.md 2>/dev/null || true)
  [ -z "$bad" ] || err "forbidden marketing word (SKILL-SPEC Skill Voice):
$bad"
}

# 32. v6.2 — Canonical-string equality: the five spec-canonical lines must match
#     SKILL-SPEC verbatim wherever present (presence itself is governed by other
#     checks/templates). Prevents the silent paraphrase drift that produced two
#     'a concrete blocker' variants before this check existed.
check_canonical_strings() {
  local open_c close_c acct_c pre_c vd_c f line
  open_c=$(grep -m1 '^> \*\*Completion Evidence — applies to every phase:' SKILL-SPEC.md)
  close_c=$(grep -m1 '^> \*\*Completion Evidence — final gate' SKILL-SPEC.md)
  acct_c=$(grep -m1 '^- Full accounting enforced:' SKILL-SPEC.md)
  pre_c=$(grep -m1 '^- Pre-existing / out-of-scope' SKILL-SPEC.md)
  vd_c=$(grep -m1 '^\*\*Effect:\*\* 1-5' SKILL-SPEC.md)
  { [ -n "$open_c" ] && [ -n "$close_c" ] && [ -n "$acct_c" ] && [ -n "$pre_c" ] && [ -n "$vd_c" ]; } \
    || { err "SKILL-SPEC.md canonical strings not extractable (bands / accounting / pre-existing / effect)"; return; }
  for f in ds-*/SKILL.md; do
    line=$(grep -m1 '^> \*\*Completion Evidence — applies to every phase:' "$f")
    [ -z "$line" ] || [ "$line" = "$open_c" ] || err "$f opening Completion Evidence band deviates from SKILL-SPEC verbatim text"
    line=$(grep -m1 '^> \*\*Completion Evidence — final gate' "$f")
    [ -z "$line" ] || [ "$line" = "$close_c" ] || err "$f closing Completion Evidence band deviates from SKILL-SPEC verbatim text"
    line=$(grep -m1 '^- Full accounting enforced:' "$f")
    [ -z "$line" ] || [ "$line" = "$acct_c" ] || err "$f full-accounting bullet deviates from SKILL-SPEC canonical text"
    line=$(grep -m1 '^- Pre-existing / out-of-scope' "$f")
    [ -z "$line" ] || [ "$line" = "$pre_c" ] || err "$f pre-existing-errors bullet deviates from SKILL-SPEC canonical text"
    line=$(grep -m1 '^\*\*Effect:\*\* 1-5' "$f")
    case "$line" in ""|"$vd_c"*) ;; *) err "$f Effect preamble deviates from the SKILL-SPEC canonical prefix";; esac
  done
}

# 33. v6.2 — Frontmatter fields: exactly name + description (Agent Skills
#     discovery loads these for every skill at startup; anything else is either
#     dead weight or an unreviewed host directive).
check_frontmatter_fields() {
  local f bad
  for f in ds-*/SKILL.md; do
    bad=$(awk '/^---$/{n++; next} n==1 && NF && !/^(name|description):/ {print FILENAME": "$0} n>=2{exit}' "$f")
    [ -z "$bad" ] || err "unexpected frontmatter field (only name + description allowed):
$bad"
  done
}

# 34. v6.2 — Delegation-target existence: a Delegates/Receives token naming a
#     skill that does not exist routes work into a void (check 20 verifies
#     reciprocity but silently skips missing targets).
check_delegation_targets() {
  local f src part tgt
  for f in ds-*/SKILL.md; do
    src="${f%%/*}"
    part=$(awk '/^\*\*Owns:\*\*/{print; exit}' "$f" | sed -E 's/^.*\*\*Delegates:\*\* //')
    for tgt in $(printf '%s' "$part" | grep -oE 'ds-[a-z][a-z-]*' | sort -u); do
      [ "$tgt" = "$src" ] && continue
      [ -d "$tgt" ] || [ -f "agents/$tgt.md" ] \
        || err "$f delegation line references non-existent skill $tgt"
    done
  done
}

# 35. v6.2 — Checkpoint gate: every bulk-modifying skill carries a mechanical
#     clean-tree pre-step before its first project-file write (SKILL-SPEC §4
#     Checkpoint Gate; ds-tune's reset loop made this a data-loss guard). List =
#     skills that write/delete/reset project files in bulk; read-only, planning,
#     and infra-only skills are exempt by design.
check_checkpoint_gate() {
  local s
  for s in ds-backend ds-build ds-compliance ds-debug ds-deploy ds-deps ds-devops ds-docs ds-fix ds-frontend ds-init ds-issue ds-mobile ds-pr ds-release ds-repo ds-review ds-simplify ds-test ds-tune; do
    [ -f "$s/SKILL.md" ] || continue
    { grep -qi 'checkpoint' "$s/SKILL.md" && grep -q 'git status --porcelain' "$s/SKILL.md"; } \
      || err "$s/SKILL.md missing the Checkpoint pre-step (clean-tree gate via git status --porcelain before first write — SKILL-SPEC §4)"
  done
}

# 36. v6.3 — Canonical secret filename patterns (SKILL-SPEC §4): a skill carrying
#     a filename-based secret exclusion must carry the FULL canonical set — a
#     partial copy is drift, and the missed pattern is the one that leaks.
check_secret_pattern_set() {
  local f t missing
  for f in ds-*/SKILL.md; do
    [ -f "$f" ] || continue
    grep -qE 'credentials\.\*|secrets\.\*|\*\.pem' "$f" || continue
    missing=""
    for t in '`.env`' '`.env.*`' '`*.pem`' '`*.key`' '`credentials.*`' '`secrets.*`'; do
      grep -qF "$t" "$f" || missing="$missing $t"
    done
    [ -z "$missing" ] || err "$f carries a filename secret-exclusion list but misses:$missing (SKILL-SPEC canonical set — partial copies drift)"
  done
}

# 37. v7 — Spec citations: a skill never cites the spec or its internal labels
#     (SKILL-SPEC, Unattended Mode rule N, rule-4 exception, IDU, DSC, OVERLAP-n,
#     `| VAR` status cells). A lone install has no spec to resolve them against,
#     so the executor is left with a pointer and no rule. The canonical inline
#     equivalents live in SKILL-SPEC §9 Prohibited Content. DSC-NN rule ids
#     (ds-productize discount rules) are a namespace, not a citation, and pass.
check_spec_citations() {
  local bad
  bad=$(grep -rnE 'SKILL-SPEC|Unattended Mode rule|rule-4 exception|(^|[^A-Za-z0-9_])IDU([^A-Za-z0-9_]|$)|(^|[^A-Za-z0-9_])DSC([^-A-Za-z0-9_]|$)|OVERLAP-[0-9]|\| VAR( |$)' ds-*/SKILL.md ds-*/README.md ds-*/references/*.md 2>/dev/null || true)
  [ -z "$bad" ] || err "spec citation inside a skill (say the rule inline — SKILL-SPEC §9 canonical equivalents):
$bad"
}

# 38. v7 — Dead Source pointers: a `Source:` line that names a file (bare token
#     such as dev-rules.md or canonical-xr.json) which exists neither in the citing
#     skill, nor in core/, nor at the repo root. URLs are not checked here (the
#     link checks and the release-time curl sweep cover those).
check_dead_sources() {
  local bad="" f tok skill base
  for f in ds-*/SKILL.md ds-*/references/*.md; do
    [ -f "$f" ] || continue
    skill="${f%%/*}"
    # markdown links are removed first: a linked file is resolvable by definition
    for tok in $(grep -E '^\*\*Source' "$f" 2>/dev/null | sed -E 's#\[[^]]*\]\([^)]*\)##g; s#https?://[^ )>]+##g' \
                   | grep -oE '(^|[^A-Za-z0-9_./-])[A-Za-z0-9_./-]+\.(md|json|ya?ml|toml)([^A-Za-z0-9_./-]|$)' \
                   | sed -E 's/^[^A-Za-z0-9_./-]//; s/[^A-Za-z0-9_./-]$//' | sort -u); do
      if [ -e "$skill/$tok" ] || [ -e "$skill/references/$tok" ] || [ -e "core/$tok" ]; then continue; fi
      # a name that exists elsewhere in this repo (docs/, another skill) is a pointer
      # a lone install cannot follow; a name that exists nowhere here is an external
      # citation (dev-rules.md) and passes, as do the generic project-file names a
      # rule legitimately talks about (CLAUDE.md, README.md, CODEOWNERS, …)
      base=$(basename "$tok")
      case "$base" in CLAUDE.md|AGENTS.md|GEMINI.md|README.md|CHANGELOG.md|CONTRIBUTING.md|SECURITY.md|CODE_OF_CONDUCT.md|LICENSE.md|CODEOWNERS|copilot-instructions.md|SKILL.md|package.json|pyproject.toml|tsconfig.json|pubspec.yaml|Cargo.toml|go.mod) continue;; esac
      [ -z "$(find . -path ./.git -prune -o -name "$base" -print 2>/dev/null | grep -v "^./$skill/" | head -1)" ] \
        || bad="$bad
  $f -> $tok"
    done
  done
  [ -z "$bad" ] || err "Source: line names a repo file a lone install cannot follow (link it by URL or move it into core/):$bad"
}

# 39. v7 — README count claims mirror SKILL.md: a README saying "N scopes" /
#     "N modes" / "N domains" / "N checks" / "N dimensions" must carry the same
#     "N word" string as its SKILL.md — the README is a mirror, never a second
#     source of counts (rule counts are check 17).
check_readme_counts() {
  local d s f claim bad=""
  for d in ds-*/; do
    s=${d%/}; f="$d/README.md"
    [ -f "$f" ] && [ -f "$d/SKILL.md" ] || continue
    for claim in $(grep -oE '[0-9]+ (scopes|modes|domains|checks|dimensions)' "$f" 2>/dev/null | tr ' ' '_' | sort -u); do
      grep -qF "$(echo "$claim" | tr '_' ' ')" "$d/SKILL.md" || bad="$bad
  $f claims '$(echo "$claim" | tr '_' ' ')' but $s/SKILL.md never states it"
    done
  done
  [ -z "$bad" ] || err "README count claim not mirrored in SKILL.md:$bad"
}

# 40. v7 — Scope-resolution table (SKILL-SPEC Relevance First): a skill whose
#     Scopes section lists two or more scopes carries a `| Scope | Runs when …`
#     table somewhere in SKILL.md, so what runs is decided by the project's signals,
#     never by "scan everything".
check_scope_resolution_table() {
  local f n
  for f in ds-*/SKILL.md; do
    [ -f "$f" ] || continue
    grep -q '^## Scopes' "$f" || continue
    n=$(awk '/^## Scopes/{f=1; next} /^## /{f=0} f && (/^\| *`?[a-z][a-z0-9-]*`? *\|/ || /^### [a-z]/ || /^- \*\*[a-z]/) {c++} END{print c+0}' "$f")
    [ "$n" -ge 2 ] || continue
    grep -qE '^\| *Scope(\(s\))? *\| *Runs when' "$f" \
      || err "$f has $n scopes but no scope-resolution table ('| Scope | Runs when (signal) | Otherwise |' — SKILL-SPEC Relevance First)"
  done
}

# 41. v7 — Rule impact: every `### ID [SEVERITY] Title` entry in a rules file carries
#     an Impact line (`- **Impact:**` or `**Impact:**`) before the next entry — the
#     "why this matters" the Reference File Format mandates. A rule without it reads
#     as a lint nit and gets skipped.
check_rule_impact() {
  local bad
  bad=$(awk '
    FNR==1 { if (open && !has) print cur; open=0 }
    /^### [A-Z]/ { if (open && !has) print cur; open=1; has=0; cur=FILENAME":"FNR" "$0; next }
    /^-? ?\*\*Impact/ { has=1 }
    END { if (open && !has) print cur }' ds-*/references/rules-*.md 2>/dev/null | cut -c1-120)
  [ -z "$bad" ] || err "rule entries without an Impact line (SKILL-SPEC Reference File Format):
$bad"
}

# 42. v7 — Duplicate rule titles: within one skill, two rules with the same title
#     text are one rule written twice (or one rule whose second copy drifted).
check_duplicate_rule_titles() {
  local d f dup bad=""
  for d in ds-*/; do
    f=$(ls "$d"references/rules-*.md 2>/dev/null) || true
    [ -n "$f" ] || continue
    # shellcheck disable=SC2086
    dup=$(grep -h '^### [A-Z]' $f | sed -E 's/^### [A-Z-]+[0-9]+ \[[A-Z]+\] //' | sort | uniq -d)
    [ -z "$dup" ] || bad="$bad
  ${d%/}: $(printf '%s' "$dup" | tr '\n' ';')"
  done
  [ -z "$bad" ] || err "duplicate rule titles inside one skill:$bad"
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

  # Fixture: check_ask_row_canonical — skill reworded the canonical --ask row
  mkdir -p "$tmp/askrow/ds-x"
  printf '| `--ask` | Interactive run — menus, approval batches and confirmations at every decision point. Without it every decision resolves by best judgment from the evidence gathered and is recorded in the summary; only the publish/irreversible exception list is skipped and recorded `only you can do`. |\n' > "$tmp/askrow/SKILL-SPEC.md"
  printf '| `--ask` | Interactive run but it also opens a PR. |\n' > "$tmp/askrow/ds-x/SKILL.md"
  assert_catches "check_ask_row_canonical" "$tmp/askrow" check_ask_row_canonical

  # Fixture: check_scope_resolution_table — three scopes, no resolution table
  mkdir -p "$tmp/f22/ds-alpha"
  printf '## Scopes\n\n| Scope | What |\n|---|---|\n| `a11y` | x |\n| `perf` | y |\n| `seo` | z |\n\n## Delegation\n' > "$tmp/f22/ds-alpha/SKILL.md"
  assert_catches "check_scope_resolution_table" "$tmp/f22" check_scope_resolution_table

  # Fixture: check_rule_impact — one rule with Impact, one without
  mkdir -p "$tmp/f23/ds-alpha/references"
  printf '### ZZ-01 [HIGH] Good rule\n- **Detect:** x\n- **Impact:** y\n\n### ZZ-02 [LOW] Bare rule\n- **Detect:** x\n' > "$tmp/f23/ds-alpha/references/rules-zz.md"
  assert_catches "check_rule_impact" "$tmp/f23" check_rule_impact

  # Fixture: check_duplicate_rule_titles — the same title under two ids
  mkdir -p "$tmp/f24/ds-alpha/references"
  printf '### ZZ-01 [HIGH] Rate limiting\n- **Impact:** a\n### ZZ-07 [LOW] Rate limiting\n- **Impact:** b\n' > "$tmp/f24/ds-alpha/references/rules-zz.md"
  assert_catches "check_duplicate_rule_titles" "$tmp/f24" check_duplicate_rule_titles

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

  # Fixture: check_core_links — a sibling-skill link, a missing core file and a
  # missing own reference; the fenced illustrative link, the references/../SKILL.md
  # escape-and-return and the existing ../core/ link must NOT be flagged
  mkdir -p "$tmp/f5/ds-alpha/references" "$tmp/f5/ds-beta/references" "$tmp/f5/core"
  cat > "$tmp/f5/ds-alpha/SKILL.md" <<'EOF'
Sibling: [beta rules](../ds-beta/references/rules.md)
Core ok: [principles](../core/principles.md)
Core gone: [missing](../core/nope.md)
Own gone: [gone](references/missing.md)

```markdown
Illustrative only: [Configuration](./docs/config.md)
```
EOF
  printf '# rules\n' > "$tmp/f5/ds-beta/references/rules.md"
  printf '# principles\n' > "$tmp/f5/core/principles.md"
  printf 'Back to [/ds-alpha](../SKILL.md).\n' > "$tmp/f5/ds-alpha/references/ok.md"
  assert_catches "check_core_links" "$tmp/f5" check_core_links
  out=$(cd "$tmp/f5" && fail=0 && check_core_links 2>&1)
  case "$out" in
    *"../core/principles.md"*|*"references/ok.md"*) echo "SELF-TEST BROKEN: check_core_links flagged a legitimate core/ or escape-and-return link"; st_fail=1 ;;
    *) echo "SELF-TEST OK: check_core_links left the legitimate links alone" ;;
  esac

  # Fixture: check_bare_repo_paths — a prose citation of a repo file that exists
  # outside the skill. The user-project path (docs/adr/), the URL-carrying line and
  # the fenced example must NOT be flagged, or the check is unusable in real docs.
  mkdir -p "$tmp/f7/ds-alpha/references" "$tmp/f7/docs/methodology"
  printf '# research\n' > "$tmp/f7/docs/methodology/program.md"
  cat > "$tmp/f7/ds-alpha/SKILL.md" <<'EOF'
Sources verified against `docs/methodology/program.md` on 2026-07-15.
Write the decision to docs/adr/NNNN-title.md in your project.
Full provenance: [program](https://example.com/docs/methodology/program.md).

```markdown
Illustrative: see docs/methodology/program.md
```
EOF
  assert_catches "check_bare_repo_paths" "$tmp/f7" check_bare_repo_paths

  # Fixture: check_approval_critical_carveout — ds-alpha grades by severity but
  # omits the carve-out; ds-beta decides gaps (no severity) and must NOT be flagged.
  mkdir -p "$tmp/f8/ds-alpha" "$tmp/f8/ds-beta"
  printf '**Interactive:** ask Apply all / per-severity bulk / Review Each / Skip All.\n' > "$tmp/f8/ds-alpha/SKILL.md"
  printf '**Interactive:** per row, plus per-dimension bulk (`Close all <dimension>`).\n' > "$tmp/f8/ds-beta/SKILL.md"
  assert_catches "check_approval_critical_carveout" "$tmp/f8" check_approval_critical_carveout

  # Fixture: check_portable_only_markers — closing band without the marker
  mkdir -p "$tmp/f9/ds-alpha"
  printf -- '- Pre-existing / out-of-scope errors are NOT skipped. <!-- portable-only -->\n> **Completion Evidence — final gate:** evidence required.\n' > "$tmp/f9/ds-alpha/SKILL.md"
  assert_catches "check_portable_only_markers" "$tmp/f9" check_portable_only_markers

  # Fixture: check_gate_two_arm — pass-only gate with no failure arm
  mkdir -p "$tmp/f11/ds-alpha"
  printf '**Gate:** Pass = all files processed.\n' > "$tmp/f11/ds-alpha/SKILL.md"
  assert_catches "check_gate_two_arm" "$tmp/f11" check_gate_two_arm

  # Fixture: check_ambiguous_phrases — condition the executor cannot evaluate
  mkdir -p "$tmp/f12/ds-alpha"
  printf 'Re-run the scan as needed.\n' > "$tmp/f12/ds-alpha/SKILL.md"
  assert_catches "check_ambiguous_phrases" "$tmp/f12" check_ambiguous_phrases

  # Fixture: check_marketing_words — forbidden voice
  mkdir -p "$tmp/f13/ds-alpha"
  printf 'Leverage the synergy of this world-class skill.\n' > "$tmp/f13/ds-alpha/SKILL.md"
  assert_catches "check_marketing_words" "$tmp/f13" check_marketing_words

  # Fixture: check_canonical_strings — paraphrased accounting bullet
  mkdir -p "$tmp/f14/ds-alpha"
  cat > "$tmp/f14/SKILL-SPEC.md" <<'EOF'
> **Completion Evidence — applies to every phase:** canonical opening.
> **Completion Evidence — final gate:** canonical closing. <!-- portable-only -->
- Full accounting enforced: canonical accounting sentence.
- Pre-existing / out-of-scope errors: canonical bullet. <!-- portable-only -->
**Effect:** 1-5 canonical preamble:
EOF
  cat > "$tmp/f14/ds-alpha/SKILL.md" <<'EOF'
> **Completion Evidence — applies to every phase:** canonical opening.
- Full accounting enforced: a locally reworded accounting sentence.
EOF
  assert_catches "check_canonical_strings" "$tmp/f14" check_canonical_strings

  # Fixture: check_frontmatter_fields — extra frontmatter key
  mkdir -p "$tmp/f15/ds-alpha"
  printf -- '---\nname: ds-alpha\ndescription: x\nmodel: opus\n---\n# body\n' > "$tmp/f15/ds-alpha/SKILL.md"
  assert_catches "check_frontmatter_fields" "$tmp/f15" check_frontmatter_fields

  # Fixture: check_delegation_targets — delegates into a void
  mkdir -p "$tmp/f16/ds-alpha"
  printf '**Owns:** a | **Delegates:** ds-ghost -> cleanup | **Receives:** none\n' > "$tmp/f16/ds-alpha/SKILL.md"
  assert_catches "check_delegation_targets" "$tmp/f16" check_delegation_targets

  # Fixture: check_checkpoint_gate — bulk-modifying skill with no clean-tree pre-step
  mkdir -p "$tmp/f17/ds-fix"
  printf '### Phase 2: Apply\n1. Write fixes to project files.\n' > "$tmp/f17/ds-fix/SKILL.md"
  assert_catches "check_checkpoint_gate" "$tmp/f17" check_checkpoint_gate

  # Fixture: check_secret_pattern_set — partial filename-exclusion copy (drops *.key, secrets.*)
  mkdir -p "$tmp/f18/ds-alpha"
  printf 'Auto-exclude files matching `.env`, `.env.*`, `*.pem`, `credentials.*` before staging.\n' > "$tmp/f18/ds-alpha/SKILL.md"
  assert_catches "check_secret_pattern_set" "$tmp/f18" check_secret_pattern_set

  # Fixture: check_spec_citations — a skill cites the spec; the DSC-01 rule id must pass
  mkdir -p "$tmp/f19/ds-alpha/references"
  printf 'Resolve per Unattended Mode rule 3.\n' > "$tmp/f19/ds-alpha/SKILL.md"
  printf '### DSC-01 [LOW] discount rule\n' > "$tmp/f19/ds-alpha/references/rules-x.md"
  assert_catches "check_spec_citations" "$tmp/f19" check_spec_citations
  mkdir -p "$tmp/f19b/ds-alpha/references"
  printf '### DSC-01 [LOW] discount rule\nSee DSC-02.\n' > "$tmp/f19b/ds-alpha/references/rules-x.md"
  printf 'clean body\n' > "$tmp/f19b/ds-alpha/SKILL.md"
  out=$(cd "$tmp/f19b" && fail=0 && check_spec_citations 2>&1)
  case "$out" in
    *FAIL*) echo "SELF-TEST BROKEN: check_spec_citations flagged a DSC-NN rule id"; st_fail=1 ;;
    *) echo "SELF-TEST OK: check_spec_citations ignores DSC-NN rule ids" ;;
  esac

  # Fixture: check_dead_sources — Source: line names a docs/ guide that exists in
  # the repo but not in the skill or core/; the external citation (dev-rules.md) and
  # the linked core file must NOT be flagged
  mkdir -p "$tmp/f20/ds-alpha/references" "$tmp/f20/core" "$tmp/f20/docs/backend"
  printf '**Source:** [OWASP](https://owasp.org/), api-guide.md Section 2\n**Source:** dev-rules.md — Error Ownership Gate\n' > "$tmp/f20/ds-alpha/references/rules-y.md"
  printf '**Source:** [principles](../core/principles.md)\n' > "$tmp/f20/ds-alpha/SKILL.md"
  printf '# p\n' > "$tmp/f20/core/principles.md"
  printf '# guide\n' > "$tmp/f20/docs/backend/api-guide.md"
  assert_catches "check_dead_sources" "$tmp/f20" check_dead_sources
  out=$(cd "$tmp/f20" && fail=0 && check_dead_sources 2>&1)
  case "$out" in
    *"dev-rules.md"*|*"principles.md"*) echo "SELF-TEST BROKEN: check_dead_sources flagged an external citation or a linked core file"; st_fail=1 ;;
    *) echo "SELF-TEST OK: check_dead_sources left the external citation and the core link alone" ;;
  esac

  # Fixture: check_readme_counts — README claims 9 scopes, SKILL.md says 7
  mkdir -p "$tmp/f21/ds-alpha"
  printf 'Covers 9 scopes.\n' > "$tmp/f21/ds-alpha/README.md"
  printf '## Scopes\n7 scopes in total.\n' > "$tmp/f21/ds-alpha/SKILL.md"
  assert_catches "check_readme_counts" "$tmp/f21" check_readme_counts

  if [ "$st_fail" = "0" ]; then
    echo "SELF-TEST PASS: all 24 fixtured checks correctly caught their deliberately-broken input"
  else
    echo "SELF-TEST FAIL: at least one check is a no-op against broken input (see SELF-TEST BROKEN lines above)"
  fi
  return "$st_fail"
}

# 25. v6 — Rule-entry heading convention (DOC-26): every rule in every
#     ds-*/references/rules-*.md is a level-3 heading. A file that drops to '##'
#     silently vanishes from every '###'-keyed extraction while looking complete.
check_rule_heading_level() {
  local bad
  bad=$(grep -rnE '^## [A-Z]{2,6}(-[A-Z]{2})?-[0-9]+' ds-*/references/rules-*.md 2>/dev/null || true)
  [ -z "$bad" ] || err "rule entries must be '### ID', not '## ID' (DOC-26 — breaks corpus extraction):
$bad"
}

# 26. v6 — Rule-ID namespace: IDs are scoped to their owning skill (ARC-01 means
#     three different rules in ds-compliance / ds-mobile / ds-review). Any
#     reference to a rule this skill does not own must name the owner on the same
#     line, either qualified (ds-review:ARC-13) or in prose (ds-deploy DEP-17).
check_rule_id_namespace() {
  local map hits f skill id owners owner_ok line
  map=$(mktemp); hits=$(mktemp)
  for f in ds-*/references/rules-*.md; do
    skill=${f%%/*}
    while read -r id; do printf '%s %s\n' "$id" "$skill"; done < <(
      grep -oE '^### [A-Z]{2,6}(-[A-Z]{2})?-[0-9]+' "$f" 2>/dev/null | sed 's/^### //'
    )
  done | sort -u > "$map"
  for f in ds-*/SKILL.md ds-*/references/*.md; do
    [ -f "$f" ] || continue
    skill=${f%%/*}
    while read -r id; do
      owners=$(awk -v i="$id" '$1==i{printf "%s ", $2}' "$map")
      [ -n "$owners" ] || continue
      case " $owners " in *" $skill "*) continue;; esac
      while IFS= read -r line; do
        owner_ok=0
        for o in $owners; do case "$line" in *"$o"*) owner_ok=1;; esac; done
        [ "$owner_ok" = "1" ] || printf '%s references foreign rule id %s (owned by: %s) without naming the owner on that line\n' "$f" "$id" "$owners" >> "$hits"
      done < <(grep -nE "(^|[^:[:alnum:]_-])$id([^[:alnum:]_-]|$)" "$f" 2>/dev/null)
    done < <(
      grep -oE '(^|[^:[:alnum:]_-])[A-Z]{2,6}(-[A-Z]{2})?-[0-9]+([^[:alnum:]_-]|$)' "$f" 2>/dev/null \
        | grep -oE '[A-Z]{2,6}(-[A-Z]{2})?-[0-9]+' | sort -u
    )
  done
  [ ! -s "$hits" ] || err "foreign rule-id references without an owner on the line (SKILL-SPEC Rule-ID Namespace):
$(sort -u "$hits")"
  rm -f "$map" "$hits"
}

# --- Mutation test (TST-11): the 9 checks above are wrapped in functions and
#     fixture-proven by --self-test. Checks 2-7 and 9-18 stay inline and
#     entangled with full-repo state, so they are proven a different way:
#     copy the tracked tree to a temp dir, apply ONE known-bad mutation, run
#     this whole script there, and assert it goes red. A check that stays green
#     against its own mutation is a no-op and is reported. ---
mutation_test() {
  local pristine tmp mt_fail=0 name snippet work out rc
  tmp=$(mktemp -d); pristine="$tmp/pristine"
  trap 'rm -rf "$tmp"' RETURN
  mkdir -p "$pristine"
  git ls-files -z | while IFS= read -r -d '' f; do
    mkdir -p "$pristine/$(dirname "$f")"; cp "$f" "$pristine/$f"
  done

  _mut() {
    name="$1"; snippet="$2"
    work="$tmp/w"; rm -rf "$work"; cp -R "$pristine" "$work"
    ( cd "$work" && eval "$snippet" ) >/dev/null 2>&1
    out=$(cd "$work" && bash scripts/check-consistency.sh 2>&1 </dev/null); rc=$?
    if [ "$rc" != "0" ] && printf '%s' "$out" | grep -q '^FAIL:'; then
      echo "MUTATION OK:     $name"
    elif printf '%s' "$out" | grep -q '^FAIL:'; then
      echo "MUTATION SURVIVED: $name — printed FAIL but exited 0 (fail flag lost in a subshell)"
      mt_fail=1
    else
      echo "MUTATION SURVIVED: $name — the check did not go red (possible no-op)"
      mt_fail=1
    fi
  }

  _mut "2 size ceiling"          "for i in \$(seq 1 20000); do echo 'padding line to blow the size ceiling'; done >> ds-fix/SKILL.md"
  _mut "3 delegation line"       "grep -v '^\*\*Owns:\*\*' ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "4 producer uniqueness"   "sed -n 's/^\*\*Owns:\*\* \(.*\)\$/\1/p' ds-fix/SKILL.md | head -1 | awk '{print \"**Owns:** \" \$0 \" | **Delegates:** none | **Receives:** none\"}' >> ds-test/SKILL.md"
  _mut "5 resumable state"       "echo 'DETECT \`ds/audit/docs.json\` on entry.' >> ds-docs/SKILL.md"
  _mut "6 W-registry ceiling"    "echo 'See W42 for the rationale.' >> ds-fix/SKILL.md"
  _mut "7 trigger discipline"    "grep -v \"DON'T INVOKE\" ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "9 dimension declaration" "grep -v '^\*\*Dimensions:\*\*' ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "11 taxonomy membership"  "sed 's/^\*\*Dimensions:\*\*.*/**Dimensions:** ZZ99/' ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "13 evidence band"        "grep -v '^> \*\*Completion Evidence — final gate' ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "14 flag integrity"       "echo 'Run with \`--status\` to skip.' >> ds-repo/SKILL.md"
  _mut "14r retired flag"        "echo 'Pass \`--dry-run\` to preview.' >> ds-repo/SKILL.md"
  _mut "14r retired flag row"    "echo '| \`--no-interactive={x}\` | Retired flag smuggled into the Arguments table. |' >> ds-repo/SKILL.md"
  _mut "15 severity vocabulary"  "echo '### ZZZ-01 [URGENT] bogus severity' >> ds-review/references/rules-quality.md"
  _mut "17 rule-count claim"     "sed 's/[0-9][0-9]* rules across/9999 rules across/' ds-frontend/README.md > t && mv t ds-frontend/README.md"
  _mut "18 mechanical done gate" "grep -v 'Mechanical Done Gate' ds-fix/SKILL.md > t && mv t ds-fix/SKILL.md"
  _mut "25 rule heading level"   "sed 's/^### DP-01/## DP-01/' ds-backend/references/rules-data-pipeline.md > t && mv t ds-backend/references/rules-data-pipeline.md"
  _mut "26 rule-id namespace"    "echo 'See ARC-13 for the rationale.' >> ds-backend/references/rules-api.md"
  _mut "23 canonical --ask row"  "sed 's/^| \`--ask\` |.*/| \`--ask\` | Reworded locally. |/' ds-repo/SKILL.md > t && mv t ds-repo/SKILL.md"
  _mut "10 advisory handoff"     "printf 'If the target skill is absent, hard-fail with \"skill not found\".\n' >> ds-fix/SKILL.md"
  _mut "12 overlap authorization" "id=\$(sed -n 's/^\*\*Dimensions:\*\* *//p' ds-fix/SKILL.md | head -1 | cut -d, -f1 | sed 's/ *(.*//'); sed \"s/^\*\*Dimensions:\*\* none (carrier)/**Dimensions:** \$id/\" ds-commit/SKILL.md > t && mv t ds-commit/SKILL.md"
  _mut "14b ask-row presence"    "grep -v '^| \`--ask\`' ds-repo/SKILL.md > t && mv t ds-repo/SKILL.md"
  _mut "14r retired --auto"      "echo 'Under \`--auto\` skip the menu.' >> ds-repo/SKILL.md"
  _mut "40 scope table"          "grep -v 'Runs when' ds-compliance/SKILL.md > t && mv t ds-compliance/SKILL.md"
  _mut "41 rule impact"          "printf '### ZZ-99 [LOW] Bare rule\\n- **Detect:** x\\n' >> ds-backend/references/rules-api.md"
  _mut "42 duplicate rule title" "printf '### API-98 [LOW] Twin\\n- **Impact:** a\\n### API-99 [LOW] Twin\\n- **Impact:** b\\n' >> ds-backend/references/rules-api.md"
  _mut "16 list-table spacing"   "printf -- '- item\n| a | b |\n' >> ds-fix/SKILL.md"
  _mut "14 discovered ghost flag" "echo 'Pass \`--turbo\` to go faster.' >> ds-repo/SKILL.md"
  _mut "37 spec citation"        "echo 'Resolve per Unattended Mode rule 3.' >> ds-fix/SKILL.md"
  _mut "21 core link missing"    "echo 'See [x](../core/does-not-exist.md).' >> ds-fix/SKILL.md"
  _mut "21 sibling link"         "echo 'See [x](../ds-test/SKILL.md).' >> ds-fix/SKILL.md"
  _mut "38 dead source"          "echo '**Source:** nowhere-to-be-found.md' >> ds-backend/references/rules-api.md"
  _mut "39 readme count"         "echo 'Runs 99 scopes.' >> ds-repo/README.md"
  _mut "18 done gate new member" "grep -v 'Mechanical Done Gate' ds-pr/SKILL.md > t && mv t ds-pr/SKILL.md"
  _mut "35 checkpoint new member" "grep -v 'git status --porcelain' ds-repo/SKILL.md > t && mv t ds-repo/SKILL.md"

  if [ "$mt_fail" = "0" ]; then
    echo "MUTATION PASS: every mutated check went red"
  else
    echo "MUTATION FAIL: at least one check survived its mutation (see SURVIVED lines)"
  fi
  return "$mt_fail"
}

if [ "${1:-}" = "--self-test" ]; then
  self_test
  exit $?
fi

if [ "${1:-}" = "--mutation-test" ]; then
  cd "$(dirname "$0")/.." || exit 2
  mutation_test
  exit $?
fi

cd "$(dirname "$0")/.." || { echo "FAIL: cannot reach the repo root from $0 — refusing to check the wrong tree." >&2; exit 2; }

check_skill_badge

# 2. Size ceilings (SKILL-SPEC section 8). Two units on purpose: lines bound the
#    structure, bytes bound the context cost the README promises. A line ceiling
#    alone cannot see a 45KB file that happens to sit on 285 long lines, which is
#    exactly the case that reached main (ds-brief). 48000 B ~= 12K tokens at the
#    ~4 B/token rule of thumb — the measured ceiling README.md states.
for f in ds-*/SKILL.md; do
  n=$(wc -l < "$f")
  [ "$n" -le 500 ] || err "$f is $n lines (ceiling 500)"
  b=$(wc -c < "$f")
  [ "$b" -le 48000 ] || err "$f is $b bytes (ceiling 48000 ~= 12K tokens)"
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

# 5. Resumable-state protocol only in the 6 qualifying skills (SKILL-SPEC section 5).
#    ds-mobile (13 domains) and ds-frontend (multi-scope) joined the set: their
#    scope-by-scope progress exists nowhere outside the run, so an interruption
#    used to restart the scan from zero.
allowed="ds-blueprint ds-frontend ds-mobile ds-ship ds-tune"
for f in $(grep -ln 'DETECT `ds/audit/' ds-*/SKILL.md); do
  skill=${f%%/*}
  case " $allowed " in *" $skill "*) ;; *) err "$skill carries state recovery protocol (only $allowed qualify)";; esac
done
for s in $allowed; do
  grep -q 'DETECT `ds/audit/' "$s/SKILL.md" || err "$s lost its state recovery protocol"
done

# 6. W-registry: no weakness numbers beyond W17 in runtime files
bogus=$(grep -rnoE 'W(1[89]|[2-9][0-9]|[0-9]{3,})\b' ds-*/SKILL.md ds-*/references ds-*/README.md agents/*.md 2>/dev/null || true)
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
  [ -n "$unauthorized" ] && err "dimension $id declared by multiple skills ($(echo "$skills" | tr '\n' ' ')) not all listed in appendix owner column '$owner_text' — unauthorized:$unauthorized"
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
#     force-approve/dry-run/no-interactive/confirm/auto are retired (the autonomous
#     default replaced --auto; the rest were folded or renamed — see SKILL-SPEC.md
#     Autonomous Default / Flag Vocabulary) and MUST NOT reappear.
for f in ds-*/SKILL.md; do
  # every backtick-delimited skill flag used in the body must appear in a table row
  # (the Arguments table) — discovered, not a fixed list. Excluded: fenced blocks,
  # /ds-* handoff lines, the delegation line (it names sibling skills' flags), and
  # lines that carry a third-party command or tool (gh, git, npm, cargo, Knip,
  # Vulture, the ds-brief verifier, CSS custom properties such as `--measure`)
  # whose own flags are not this skill's vocabulary.
  for flag in $(awk '/^```/{fence=!fence; next} !fence' "$f" | grep -v '/ds-' | grep -v '^\*\*Owns:' \
                  | grep -vE '[Kk]nip|Vulture|verify-brief|CSS|[0-9]px|`(gh|git|npm|npx|pnpm|yarn|bun|pip|pipx|uv|cargo|go|dart|flutter|dotnet|mvn|gradlew?|composer|bundle|mix|sbt|docker|kubectl|helm|terraform|wrangler|clasp|gitleaks|trufflehog|syft|knip|actionlint|shellcheck|eslint|prettier|ruff|pytest|stryker|python3?|reset|rebase|push|commit) |\.(py|sh) |install\.sh' \
                  | grep -oE '`--[a-z][a-z0-9-]*' | sed 's/^`--//' | sort -u); do
    case "$flag" in no-verify|json|limit|state|reason|parent|add-blocked-by|add-sub-issue|body-file|web|fix|write|force|hard|mixed) continue;; esac
    grep -qE "^\|.*\`--$flag" "$f" || err "$f uses \`--$flag\` but its Arguments table does not define it"
  done
  # Retired names are SKILL-flag vocabulary (SKILL-SPEC.md §Flag Vocabulary), so match
  # the shape a skill flag always has here: backtick-delimited on its own (`--preview`)
  # or an Arguments-table row — the same shape the ghost-flag arm above matches. A
  # third-party CLI flag inside a command string (`npx wrangler deploy --dry-run
  # --outdir dist`) is not this skill's vocabulary; ds-fix's toolchain reference has
  # carried exactly that usage from the start.
  for retired in force-approve dry-run no-interactive confirm auto; do
    grep -q -- "\`--$retired\`" "$f" && err "$f uses retired flag \`--$retired\` (see SKILL-SPEC.md Unattended Mode / Flag Vocabulary)"
    grep -qE "^\| *.?\`--$retired" "$f" && err "$f Arguments table defines retired flag --$retired (see SKILL-SPEC.md Unattended Mode / Flag Vocabulary)"
  done
done

# 14b. v7 — Every skill's Arguments table MUST define --ask with the canonical
#      contract (SKILL-SPEC.md §2 Autonomous Default) — no skill-local variant/omission.
for f in ds-*/SKILL.md; do
  grep -qE "^\| *.?\`--ask\`" "$f" || err "$f Arguments table missing mandatory --ask row (SKILL-SPEC.md Autonomous Default)"
done

# 15. v5 — Severity vocabulary: rule files use only the canonical set
#     (BLOCKER/CRITICAL/HIGH/MEDIUM/LOW/ADVISORY/INFO); MAJOR/MINOR are banned.
bad_sev=$(grep -rhoE '^#{2,3} [A-Z]{2,6}(-[A-Z]{2})? ?-?[0-9]+ *\[[A-Z]+\]' ds-*/references/rules-*.md 2>/dev/null \
          | grep -oE '\[[A-Z]+\]' | sort -u \
          | grep -vE '^\[(BLOCKER|CRITICAL|HIGH|MEDIUM|LOW|ADVISORY|INFO)\]$' || true
          grep -rno '\[MAJOR\]\|\[MINOR\]' ds-*/references/*.md 2>/dev/null; grep -rnoE '[0-9]+ (MAJOR|MINOR)\b' ds-*/references/*.md 2>/dev/null; true)
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
for s in ds-compliance ds-freeze ds-init ds-backend ds-frontend ds-mobile ds-review ds-simplify ds-fix ds-test ds-deps ds-tune ds-issue ds-commit ds-pr ds-repo ds-devops ds-docs ds-build ds-debug ds-release; do
  grep -q "Mechanical Done Gate" "$s/SKILL.md" 2>/dev/null \
    || err "$s/SKILL.md missing Mechanical Done Gate (SKILL-SPEC section 4 — code-modifying skill)"
done

check_claude_md_counts
check_delegates_receives_graph
check_core_links
check_bare_repo_paths
check_ask_row_canonical
check_rule_heading_level
check_rule_id_namespace
check_portable_only_markers
check_gate_two_arm
check_ambiguous_phrases
check_marketing_words
check_canonical_strings
check_frontmatter_fields
check_delegation_targets
check_checkpoint_gate
check_secret_pattern_set
check_spec_citations
check_dead_sources
check_readme_counts
check_scope_resolution_table
check_rule_impact
check_duplicate_rule_titles

if [ "$fail" = "0" ]; then
  echo "OK: $dirs skills — sizes, delegation, ownership, state policy, W-registry, triggers, v4 dimensions, advisory-handoff, taxonomy-membership, overlap, evidence-band, flag-integrity, severity-vocab, list-table-spacing, rule-count-claims, mechanical-done-gate, claude-md-count-reciprocity, delegates-receives-graph-reciprocity, core-links, bare-repo-paths, approval-critical-carveout, ask-row-canonical, rule-heading-level, rule-id-namespace, portable-only-markers, gate-two-arm, ambiguous-phrases, marketing-words, canonical-strings, frontmatter-fields, delegation-targets, checkpoint-gate, secret-pattern-set, spec-citations, dead-sources, readme-counts, scope-resolution-table, rule-impact, duplicate-rule-titles all consistent"
else
  exit 1
fi
