#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Consistency gate for dev-skills — zero dependencies (bash + grep + awk).
# Run locally: ./scripts/check-consistency.sh    CI runs the same file.
# Self-test (proves the checks below actually fail on broken input):
#   ./scripts/check-consistency.sh --self-test
set -u
fail=0
err() { echo "FAIL: $*"; fail=1; }

# --- Checks 1, 8, 19, 20, 21, 22, 23, 24 and the canonical --auto row are wrapped in
#     functions so --self-test can fixture them; the inline checks are proven by --mutation-test
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
#     decides gaps, ds-solve decides steps, ds-brief decides claims — none of them
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

# 23. v5 — Canonical --auto row (SKILL-SPEC Unattended Mode: "every skill pastes
#     this verbatim"). Compares the EFFECT cell (last cell) of each skill's
#     `--auto` Arguments row against the canonical text in SKILL-SPEC.md, so a
#     table with an extra Default column still passes while reworded, narrowed
#     or locally re-derived text fails. Per-skill carve-outs belong in the
#     skill's Contract citing rule 4, never in this row.
check_auto_row_canonical() {
  local canon skill row effect
  canon=$(grep -m1 '^| `--auto` | Zero-interaction run' SKILL-SPEC.md \
          | sed 's/.*| \(Zero-interaction run.*\) |$/\1/')
  [ -n "$canon" ] || { err "SKILL-SPEC.md: canonical --auto row not found"; return; }
  for skill in ds-*/; do
    [ -f "$skill/SKILL.md" ] || continue
    row=$(awk '/^\| `--auto` \|/{print; exit}' "$skill/SKILL.md")
    [ -n "$row" ] || { err "$skill/SKILL.md missing the mandatory --auto Arguments row"; continue; }
    effect=$(printf '%s' "$row" | sed 's/.*| \(Zero-interaction run.*\) |$/\1/')
    [ "$effect" = "$canon" ] \
      || err "$skill/SKILL.md --auto row deviates from the SKILL-SPEC canonical text (carve-outs go in Contract, citing Unattended Mode rule 4)"
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

# 28. v6.1 — Shared principles.md sync: many skills carry a same-named copy on
#     purpose (Standalone Invariant), synced only by hand. A copy that diverges
#     from the majority hash must declare it with `<!-- variant: ... -->` in its
#     first 5 lines — three copies had silently diverged before this check existed.
check_principles_sync() {
  local hashes major h f
  hashes=$(for f in ds-*/references/principles.md; do
    [ -f "$f" ] || continue
    printf '%s %s\n' "$(cksum < "$f" | awk '{print $1"-"$2}')" "$f"
  done)
  [ -n "$hashes" ] || return 0
  major=$(printf '%s\n' "$hashes" | awk '{print $1}' | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
  while read -r h f; do
    [ "$h" = "$major" ] && continue
    head -5 "$f" | grep -q '<!-- variant:' \
      || err "$f diverges from the majority principles.md without a '<!-- variant: ... -->' declaration in its first 5 lines (silent drift)"
  done <<PRINEOF
$hashes
PRINEOF
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
  vd_c=$(grep -m1 '^\*\*Value Delivered:\*\* 1-5' SKILL-SPEC.md)
  { [ -n "$open_c" ] && [ -n "$close_c" ] && [ -n "$acct_c" ] && [ -n "$pre_c" ] && [ -n "$vd_c" ]; } \
    || { err "SKILL-SPEC.md canonical strings not extractable (bands / accounting / pre-existing / value-delivered)"; return; }
  for f in ds-*/SKILL.md; do
    line=$(grep -m1 '^> \*\*Completion Evidence — applies to every phase:' "$f")
    [ -z "$line" ] || [ "$line" = "$open_c" ] || err "$f opening Completion Evidence band deviates from SKILL-SPEC verbatim text"
    line=$(grep -m1 '^> \*\*Completion Evidence — final gate' "$f")
    [ -z "$line" ] || [ "$line" = "$close_c" ] || err "$f closing Completion Evidence band deviates from SKILL-SPEC verbatim text"
    line=$(grep -m1 '^- Full accounting enforced:' "$f")
    [ -z "$line" ] || [ "$line" = "$acct_c" ] || err "$f full-accounting bullet deviates from SKILL-SPEC canonical text"
    line=$(grep -m1 '^- Pre-existing / out-of-scope' "$f")
    [ -z "$line" ] || [ "$line" = "$pre_c" ] || err "$f pre-existing-errors bullet deviates from SKILL-SPEC canonical text"
    line=$(grep -m1 '^\*\*Value Delivered:\*\* 1-5' "$f")
    case "$line" in ""|"$vd_c"*) ;; *) err "$f Value-Delivered preamble deviates from the SKILL-SPEC canonical prefix";; esac
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
  for s in ds-backend ds-compliance ds-deploy ds-deps ds-devops ds-docs ds-fix ds-frontend ds-init ds-issue ds-mobile ds-review ds-simplify ds-solve ds-test ds-tune; do
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

  # Fixture: check_auto_row_canonical — skill reworded the canonical --auto row
  mkdir -p "$tmp/autorow/ds-x"
  printf '| `--auto` | Zero-interaction run — every decision resolved by best judgment; only the fixed irreversible-exception list is skipped and recorded `needs-human`. Ends in the standard summary only. |\n' > "$tmp/autorow/SKILL-SPEC.md"
  printf '| `--auto` | Zero-interaction run but it also opens a PR. |\n' > "$tmp/autorow/ds-x/SKILL.md"
  assert_catches "check_auto_row_canonical" "$tmp/autorow" check_auto_row_canonical

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

  # Fixture: check_principles_sync — two majority copies, one silent divergence
  mkdir -p "$tmp/f10/ds-alpha/references" "$tmp/f10/ds-beta/references" "$tmp/f10/ds-gamma/references"
  printf '# Principles\nshared text\n' > "$tmp/f10/ds-alpha/references/principles.md"
  printf '# Principles\nshared text\n' > "$tmp/f10/ds-beta/references/principles.md"
  printf '# Principles\nshared text\nplus a silent local addition\n' > "$tmp/f10/ds-gamma/references/principles.md"
  assert_catches "check_principles_sync" "$tmp/f10" check_principles_sync

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
**Value Delivered:** 1-5 canonical preamble:
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

  if [ "$st_fail" = "0" ]; then
    echo "SELF-TEST PASS: all 19 fixtured checks correctly caught their deliberately-broken input"
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
  _mut "23 canonical --auto row" "sed 's/^| \`--auto\` |.*/| \`--auto\` | Reworded locally. |/' ds-repo/SKILL.md > t && mv t ds-repo/SKILL.md"
  _mut "10 advisory handoff"     "printf 'If the target skill is absent, hard-fail with \"skill not found\".\n' >> ds-fix/SKILL.md"
  _mut "12 overlap authorization" "id=\$(sed -n 's/^\*\*Dimensions:\*\* *//p' ds-fix/SKILL.md | head -1 | cut -d, -f1 | sed 's/ *(.*//'); sed \"s/^\*\*Dimensions:\*\* none (carrier)/**Dimensions:** \$id/\" ds-commit/SKILL.md > t && mv t ds-commit/SKILL.md"
  _mut "14b auto-row presence"   "grep -v '^| \`--auto\`' ds-repo/SKILL.md > t && mv t ds-repo/SKILL.md"
  _mut "16 list-table spacing"   "printf -- '- item\n| a | b |\n' >> ds-fix/SKILL.md"

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
allowed="ds-blueprint ds-frontend ds-mobile ds-ship ds-solve ds-tune"
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
#     force-approve/dry-run/no-interactive/confirm are retired (folded into --auto
#     or renamed — see SKILL-SPEC.md Unattended Mode) and MUST NOT reappear.
for f in ds-*/SKILL.md; do
  for flag in auto preview resume clean status static run; do
    grep -v '/ds-' "$f" | grep -q "\`--$flag\`" || continue
    grep -qE "^\| *.?\`--$flag" "$f" || err "$f uses \`--$flag\` but its Arguments table does not define it"
  done
  # Retired names are SKILL-flag vocabulary (SKILL-SPEC.md §Flag Vocabulary), so match
  # the shape a skill flag always has here: backtick-delimited on its own (`--preview`)
  # or an Arguments-table row — the same shape the ghost-flag arm above matches. A
  # third-party CLI flag inside a command string (`npx wrangler deploy --dry-run
  # --outdir dist`) is not this skill's vocabulary; ds-fix's toolchain reference has
  # carried exactly that usage from the start.
  for retired in force-approve dry-run no-interactive confirm; do
    grep -q -- "\`--$retired\`" "$f" && err "$f uses retired flag \`--$retired\` (see SKILL-SPEC.md Unattended Mode / Flag Vocabulary)"
    grep -qE "^\| *.?\`--$retired" "$f" && err "$f Arguments table defines retired flag --$retired (see SKILL-SPEC.md Unattended Mode / Flag Vocabulary)"
  done
done

# 14b. v5 — Every skill's Arguments table MUST define --auto with the canonical
#      contract (SKILL-SPEC.md §2 Unattended Mode) — no skill-local variant/omission.
for f in ds-*/SKILL.md; do
  grep -qE "^\| *.?\`--auto\`" "$f" || err "$f Arguments table missing mandatory --auto row (SKILL-SPEC.md Unattended Mode)"
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
for s in ds-compliance ds-freeze ds-init ds-backend ds-frontend ds-mobile ds-review ds-simplify ds-fix ds-test ds-deps ds-tune ds-solve ds-issue ds-commit; do
  grep -q "Mechanical Done Gate" "$s/SKILL.md" 2>/dev/null \
    || err "$s/SKILL.md missing Mechanical Done Gate (SKILL-SPEC section 4 — code-modifying skill)"
done

check_claude_md_counts
check_delegates_receives_graph
check_standalone_paths
check_intra_skill_links
check_bare_repo_paths
check_auto_row_canonical
check_rule_heading_level
check_rule_id_namespace
check_portable_only_markers
check_principles_sync
check_gate_two_arm
check_ambiguous_phrases
check_marketing_words
check_canonical_strings
check_frontmatter_fields
check_delegation_targets
check_checkpoint_gate
check_secret_pattern_set

if [ "$fail" = "0" ]; then
  echo "OK: $dirs skills — sizes, delegation, ownership, state policy, W-registry, triggers, v4 dimensions, advisory-handoff, taxonomy-membership, overlap, evidence-band, flag-integrity, severity-vocab, list-table-spacing, rule-count-claims, mechanical-done-gate, claude-md-count-reciprocity, delegates-receives-graph-reciprocity, standalone-paths, intra-skill-links, bare-repo-paths, approval-critical-carveout, auto-row-canonical, rule-heading-level, rule-id-namespace, portable-only-markers, principles-sync, gate-two-arm, ambiguous-phrases, marketing-words, canonical-strings, frontmatter-fields, delegation-targets, checkpoint-gate, secret-pattern-set all consistent"
else
  exit 1
fi
