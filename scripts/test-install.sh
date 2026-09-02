#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# install.sh round-trip test — the only proof that the installer's `rsync --delete`
# and `rm -rf` stay scoped to dev-skills content.
#
# install.sh is the one script here that writes into and deletes from a user's home
# directory. Its guards (`${skills_dir:?}`, per-skill --delete, ds-* names only from
# skill_list) all look right by reading; this asserts they behave right. Everything
# runs against a temp dir via --target, so $HOME is never touched.
#
#   bash scripts/test-install.sh
#
# Each assertion names the concrete failure it guards against.
set -uo pipefail
cd "$(dirname "$0")/.." || { echo "FAIL: cannot reach the repo root from $0"; exit 2; }

pass=0
fail=0
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

skills="$tmp/skills"
ok()   { pass=$((pass+1)); printf 'PASS %s\n' "$1"; }
bad()  { fail=$((fail+1)); printf 'FAIL %s — %s\n' "$1" "$2"; }
check() { # check "<what it guards>" "<expected>" "<actual>"
  if [ "$2" = "$3" ]; then ok "$1"; else bad "$1" "expected '$2', got '$3'"; fi
}

repo_count=$(find . -maxdepth 1 -type d -name 'ds-*' | wc -l | tr -d ' ')

# --- decoys: content the installer must never touch ---------------------------
mkdir -p "$skills/ds-not-from-this-repo" "$skills/unrelated-tool"
printf 'keep me\n' > "$skills/ds-not-from-this-repo/keep.txt"
printf 'keep me too\n' > "$skills/unrelated-tool/notes.md"
printf 'someone elses file\n' > "$skills/loose-file.md"

# --- 1. install ---------------------------------------------------------------
./install.sh --target "$skills" >/dev/null 2>&1
installed=$(find "$skills" -maxdepth 1 -type d -name 'ds-*' -not -name 'ds-not-from-this-repo' | wc -l | tr -d ' ')
check "install copies every ds-* skill (guards: a silently skipped skill)" "$repo_count" "$installed"

if [ -f "$skills/.dev-skills-version" ]; then
  ok "install writes the version stamp (guards: --check having nothing to compare)"
else
  bad "install writes the version stamp" "no .dev-skills-version at $skills"
fi

if [ -f "$skills/ds-commit/SKILL.md" ]; then
  ok "installed skill carries its SKILL.md (guards: an empty skill dir passing as installed)"
else
  bad "installed skill carries its SKILL.md" "ds-commit/SKILL.md missing"
fi

if [ -e "$skills/ds-commit/README.md" ] && [ ! -e "$skills/SKILL-SPEC.md" ]; then
  ok "runtime files only — spec/docs stay out of the install (guards: context-path bloat)"
else
  bad "runtime files only" "SKILL-SPEC.md leaked into $skills, or README.md missing"
fi

if [ -f "$skills/core/principles.md" ] && [ ! -e "$skills/core/SKILL.md" ]; then
  ok "install ships core/ beside the skills, without a SKILL.md (guards: every ../core/ link dead; core listed as a command)"
else
  bad "install ships core/ beside the skills" "no $skills/core/principles.md, or a SKILL.md inside core/"
fi

# --- 1b. a single-skill install still gets core/ -------------------------------
one="$tmp/one-skill"
./install.sh --target "$one" --skills ds-review >/dev/null 2>&1
one_n=$(find "$one" -maxdepth 1 -type d -name 'ds-*' | wc -l | tr -d ' ')
check "--skills installs only the named skill (guards: subset flag ignored)" "1" "$one_n"
if [ -f "$one/core/principles.md" ]; then
  ok "--skills subset still ships core/ (guards: a lone skill whose ../core/ links are dead)"
else
  bad "--skills subset still ships core/" "no core/principles.md under $one"
fi

# --- 2. --check on a clean install --------------------------------------------
./install.sh --target "$skills" --check >/dev/null 2>&1
check "--check reports clean right after install (guards: false drift on every run)" "0" "$?"

# --- 2b. lean profile: install-time strip + profile-aware check ----------------
lean="$tmp/lean-skills"
./install.sh --target "$lean" --profile lean >/dev/null 2>&1
if grep -q 'portable-only' "$lean/ds-commit/SKILL.md" 2>/dev/null; then
  bad "lean install strips portable-only blocks" "marker text survived in ds-commit/SKILL.md"
else
  ok "lean install strips portable-only blocks (guards: lean shipping the duplicate layer anyway)"
fi
bands=$(grep -c '^> \*\*Completion Evidence — ' "$lean/ds-commit/SKILL.md" 2>/dev/null)
check "lean install keeps exactly the opening Completion Evidence band (guards: over-stripping)" "1" "$bands"
if grep -q 'profile=lean' "$lean/.dev-skills-version" 2>/dev/null; then
  ok "lean install stamps its profile (guards: --check comparing against the wrong profile)"
else
  bad "lean install stamps its profile" "no profile=lean in $lean/.dev-skills-version"
fi
./install.sh --target "$lean" --check >/dev/null 2>&1
check "--check is clean on a lean install without re-passing --profile (guards: false drift)" "0" "$?"
if grep -q 'portable-only' "$lean/core/report-and-outcome-templates.md" 2>/dev/null; then
  bad "lean install strips the portable-only block in core/" "marker text survived in core/report-and-outcome-templates.md"
else
  ok "lean install strips the portable-only block in core/ (guards: lean shipping dev-rules' closing block twice)"
fi
if grep -q '^Owner: the always-on rules layer' "$lean/core/report-and-outcome-templates.md" 2>/dev/null; then
  ok "lean install keeps the core/ owner pointer above the stripped block (guards: a dangling § 5 reference)"
else
  bad "lean install keeps the core/ owner pointer" "no owner line in lean core/report-and-outcome-templates.md"
fi
if grep -q 'portable-only:start' "$skills/core/report-and-outcome-templates.md"; then
  ok "portable install keeps the core/ closing block (guards: a host without a rules layer losing its Outcome Report)"
else
  bad "portable install keeps the core/ closing block" "no portable-only:start marker in portable core/"
fi
if grep -q 'portable-only' "$skills/ds-commit/SKILL.md"; then
  ok "portable install ships the markers verbatim (guards: default install silently stripping)"
else
  bad "portable install ships the markers verbatim" "no portable-only marker in portable ds-commit/SKILL.md"
fi

# --- 2c. claude profile: lean + the Claude-only fork line in ds-ship only -------
cl="$tmp/claude-skills"
./install.sh --target "$cl" --profile claude >/dev/null 2>&1
check "claude install exits 0 (guards: a missing anchor sentence aborting every install)" "0" "$?"
if grep -q 'portable-only' "$cl/ds-ship/SKILL.md" 2>/dev/null; then
  bad "claude install strips portable-only blocks" "marker text survived in ds-ship/SKILL.md"
else
  ok "claude install strips portable-only blocks (guards: claude shipping the duplicate layer)"
fi
if grep -q 'run the delegate as a forked subagent' "$cl/ds-ship/SKILL.md" 2>/dev/null; then
  ok "claude install injects the fork instruction into ds-ship (guards: profile silently equal to lean)"
else
  bad "claude install injects the fork instruction into ds-ship" "no fork sentence in $cl/ds-ship/SKILL.md"
fi
if grep -rq 'forked subagent' "$cl/ds-review/SKILL.md" "$cl/ds-commit/SKILL.md" 2>/dev/null; then
  bad "claude injection stays inside ds-ship" "fork sentence leaked into a delegate's SKILL.md"
else
  ok "claude injection stays inside ds-ship (guards: host-specific text spreading to every skill)"
fi
if grep -q 'forked subagent' ds-ship/SKILL.md; then
  bad "repo ds-ship/SKILL.md stays host-neutral" "fork sentence present in the repo file"
else
  ok "repo ds-ship/SKILL.md stays host-neutral (guards: install-time text landing in the repo)"
fi
if grep -q 'profile=claude' "$cl/.dev-skills-version" 2>/dev/null; then
  ok "claude install stamps its profile (guards: --check comparing against lean)"
else
  bad "claude install stamps its profile" "no profile=claude in $cl/.dev-skills-version"
fi
./install.sh --target "$cl" --check >/dev/null 2>&1
check "--check is clean on a claude install without re-passing --profile (guards: false drift)" "0" "$?"

# --- 3. --check detects a mutated file ----------------------------------------
printf '\nlocal edit that is not in the repo\n' >> "$skills/ds-commit/SKILL.md"
out=$(./install.sh --target "$skills" --check 2>&1)
code=$?
check "--check exits non-zero on drift (guards: drift reported but not failed)" "1" "$code"
case "$out" in
  *DRIFT*ds-commit*) ok "--check names the drifted skill (guards: an unactionable failure)" ;;
  *) bad "--check names the drifted skill" "no DRIFT line for ds-commit in output" ;;
esac

# --- 4. --check detects a deleted file ----------------------------------------
rm -f "$skills/ds-pr/SKILL.md"
./install.sh --target "$skills" --check >/dev/null 2>&1
check "--check catches a deleted installed file (guards: silent partial install)" "1" "$?"

# --- 4b. --check detects drift inside core/ -----------------------------------
./install.sh --target "$skills" >/dev/null 2>&1
printf '
local edit
' >> "$skills/core/principles.md"
out=$(./install.sh --target "$skills" --check 2>&1)
case "$out" in
  *"DRIFT in core"*) ok "--check names drift inside core/ (guards: a stale shared reference passing as in sync)" ;;
  *) bad "--check names drift inside core/" "no 'DRIFT in core' line in output" ;;
esac

# --- 5. re-install repairs both -----------------------------------------------
./install.sh --target "$skills" >/dev/null 2>&1
./install.sh --target "$skills" --check >/dev/null 2>&1
check "re-install restores drifted + deleted files (guards: --delete not resyncing)" "0" "$?"

# --- 6. uninstall is scoped ---------------------------------------------------
./install.sh --target "$skills" --uninstall >/dev/null 2>&1
left=$(find "$skills" -maxdepth 1 -type d -name 'ds-*' -not -name 'ds-not-from-this-repo' | wc -l | tr -d ' ')
check "uninstall removes every installed skill (guards: orphaned skill dirs)" "0" "$left"

if [ -f "$skills/.dev-skills-version" ]; then
  bad "uninstall removes the version stamp" "stamp survived at $skills/.dev-skills-version"
else
  ok "uninstall removes the version stamp (guards: --check claiming an install that is gone)"
fi

if [ -d "$skills/core" ]; then
  bad "uninstall removes core/" "core/ survived at $skills/core"
else
  ok "uninstall removes core/ (guards: orphaned shared references after uninstall)"
fi

if [ -f "$skills/ds-not-from-this-repo/keep.txt" ] &&
   [ -f "$skills/unrelated-tool/notes.md" ] &&
   [ -f "$skills/loose-file.md" ]; then
  ok "uninstall touches nothing it did not install (guards: rm -rf eating a user's other skills)"
else
  bad "uninstall touches nothing it did not install" "a decoy file was deleted from $skills"
fi

printf -- '------------------------------------------------------------\n'
if [ "$fail" = "0" ]; then
  printf 'INSTALL ROUND-TRIP PASS: %s/%s assertions\n' "$pass" "$pass"
else
  printf 'INSTALL ROUND-TRIP FAIL: %s of %s assertions failed\n' "$fail" "$((pass+fail))"
  exit 1
fi
