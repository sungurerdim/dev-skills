#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# dev-skills installer/syncer — copies ONLY runtime files (ds-*/ skills, core/, agents/).
# Spec, docs, and methodology stay in the repo; they are never loaded at runtime.
# core/ (the shared references every skill links to as ../core/<file>.md) ships on
# every install — full, --skills subset, and --target alike — so a lone skill's
# links resolve exactly as they do in the repo.
#
# Needs only bash, coreutils (cp, find, cmp, comm, mktemp) and git — no rsync, so it
# runs unchanged in Git Bash on Windows, macOS, and Linux.
#
#   ./install.sh                 install/sync all skills into ~/.claude (global;
#                                also covers OpenCode, which reads ~/.claude/skills)
#   ./install.sh --project DIR   install into DIR/.claude instead
#   ./install.sh --target DIR    install skills into DIR directly — any Agent Skills
#                                host dir (e.g. .agents/skills, .opencode/skill).
#                                Skills only; shared agents/ are Claude-Code-specific
#   ./install.sh --skills a,b    only the named skills (e.g. ds-review,ds-commit);
#                                core/ is still shipped
#   ./install.sh --profile P     portable (default) ships files verbatim — full
#                                self-contained density for any host. lean strips
#                                the blocks marked `<!-- portable-only -->` at
#                                install time — for Claude-5-generation hosts with
#                                an always-on rules layer (e.g. dev-rules) that
#                                already supplies those universal gates. claude =
#                                lean + a Claude-Code-only line injected into
#                                ds-ship's delegation step: delegates run as forked
#                                subagents (isolated context, waited on in-turn,
#                                summary returned). Repo files always keep the full
#                                portable, host-neutral text.
#   ./install.sh --check         report drift between repo and installed copy
#                                (profile-aware; reads profile from version stamp)
#   ./install.sh --status        one screen: what is installed, what the repo has,
#                                whether upstream has newer commits, whether the
#                                installed copy drifted — read-only, no changes
#   ./install.sh --update        fast-forward this clone (git pull --ff-only), show
#                                what changed, then re-install with the stamped
#                                profile. Equivalent to `git pull && ./install.sh`;
#                                never merges or rebases on your behalf
#   ./install.sh --uninstall     remove installed dev-skills content
#
# Idempotent: safe to run twice. Sync replaces each skill dir wholesale, so files
# removed from a skill in the repo are also removed from the installed copy.
set -euo pipefail
cd "$(dirname "$0")"

for tool in cp find cmp comm mktemp git; do
  command -v "$tool" >/dev/null 2>&1 || { echo "$tool is required but not found on PATH (on Windows, run this from Git Bash)."; exit 1; }
done

target="$HOME/.claude"
mode="install"
only=""
skills_dir=""
with_agents=1
profile=""
while [ $# -gt 0 ]; do
  case "$1" in
    --project) target="$2/.claude"; shift 2 ;;
    --target)  skills_dir="$2"; with_agents=0; shift 2 ;;
    --skills)  only="$2"; shift 2 ;;
    --profile) profile="$2"; shift 2 ;;
    --check)   mode="check"; shift ;;
    --status)  mode="status"; shift ;;
    --update)  mode="update"; shift ;;
    --uninstall) mode="uninstall"; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown flag: $1 (see --help)"; exit 2 ;;
  esac
done
case "$profile" in ""|lean|portable|claude) ;; *) echo "Unknown profile: $profile (use portable, lean or claude)"; exit 2 ;; esac

[ -n "$skills_dir" ] || skills_dir="$target/skills"
agents_dir="$target/agents"
version_file="$skills_dir/.dev-skills-version"

skill_list() {
  if [ -n "$only" ]; then
    echo "$only" | tr ',' '\n' | while IFS= read -r s; do
      [[ "$s" =~ ^ds-[a-zA-Z0-9_-]+$ ]] && echo "$s" || echo "Skip: '$s' is not a valid ds-* skill name" >&2
    done
  else
    ls -d ds-*/ | sed 's:/$::'
  fi
}

stamp() {
  git rev-parse --short HEAD 2>/dev/null || echo "unknown"
}

# sync_tree SRC DST — DST becomes an exact copy of SRC (delete semantics: files gone
# from SRC disappear from DST). DST is always a path this script owns (a ds-*/ or
# core/ dir under skills_dir), so the wholesale replace is safe.
sync_tree() {
  local src="$1" dst="$2"
  rm -rf "${dst:?}"
  mkdir -p "$dst"
  cp -R "$src/." "$dst/"
}

# tree_diff EXPECTED INSTALLED — one line per path that differs, relative to the
# tree root: `(modified)`, `(missing)` (in repo, not installed), `(extra)` (installed,
# not in repo). Paths are handled one per line, so spaces in $HOME are fine.
tree_diff() {
  local exp="$1" got="$2" f
  local lst; lst=$(mktemp -d)
  ( cd "$exp" && find . -type f | sed 's#^\./##' | sort ) > "$lst/exp"
  ( cd "$got" && find . -type f | sed 's#^\./##' | sort ) > "$lst/got"
  comm -23 "$lst/exp" "$lst/got" | sed 's/$/ (missing)/'
  comm -13 "$lst/exp" "$lst/got" | sed 's/$/ (extra)/'
  comm -12 "$lst/exp" "$lst/got" | while IFS= read -r f; do
    cmp -s "$exp/$f" "$got/$f" || echo "$f (modified)"
  done
  rm -rf "$lst"
}

# Lean-profile transform, applied to an installed SKILL.md (never a repo file):
# drops lines suffixed `<!-- portable-only -->`, drops
# `<!-- portable-only:start -->`..`<!-- portable-only:end -->` blocks, and removes
# the opening band's "repeats at file end" note (true only on portable installs).
lean_strip() {
  awk '
    /<!-- portable-only:start -->/ { blk=1; next }
    /<!-- portable-only:end -->/   { blk=0; next }
    blk { next }
    /<!-- portable-only -->[[:space:]]*$/ { next }
    { gsub(/ \*\(This band repeats at file end by design — both copies are normative\.\)\*/, ""); print }
  ' "$1" > "$1.lean.tmp" && mv "$1.lean.tmp" "$1"
}

# Claude-profile transform, applied to an installed ds-ship/SKILL.md after lean_strip
# (never a repo file): the delegation step gains the Claude-Code-specific fork
# instruction. The anchor sentence is the host-neutral one the repo carries; a
# missing anchor fails loudly so the profile never silently degrades to lean.
CLAUDE_ANCHOR='in an isolated sub-context when the host offers one.'
CLAUDE_INJECT='in an isolated sub-context when the host offers one. Claude Code: run the delegate as a forked subagent — a fresh context whose prompt is the delegate'"'"'s installed `SKILL.md` plus the arguments, waited on in this turn (`background: false` semantics, full tool set) — and treat its final summary as the delegate'"'"'s return; under `--ask` invoke the delegate inline instead, so its prompts reach the user.'
claude_inject() {
  grep -qF "$CLAUDE_ANCHOR" "$1" || { echo "claude profile: anchor sentence not found in $1 — refusing to install a profile that would silently equal lean." >&2; exit 1; }
  awk -v a="$CLAUDE_ANCHOR" -v b="$CLAUDE_INJECT" '{ i = index($0, a); if (i) { $0 = substr($0, 1, i-1) b substr($0, i+length(a)) } print }' "$1" > "$1.claude.tmp" && mv "$1.claude.tmp" "$1"
}

# apply_profile SKILL_MD PROFILE SKILL — the install-time transform for one skill file
apply_profile() {
  local f="$1" eff="$2" s="$3"
  [ -f "$f" ] || return 0
  case "$eff" in
    lean)   lean_strip "$f" ;;
    claude) lean_strip "$f"; [ "$s" = "ds-ship" ] && claude_inject "$f" ;;
  esac
  return 0
}

# apply_core_profile DIR PROFILE — the same strip over the shared references: core/
# carries the closing block and doctrine an always-on rules layer (dev-rules) already
# supplies on lean/claude hosts, marked `<!-- portable-only:start/end -->` there.
apply_core_profile() {
  local d="$1" eff="$2" f
  case "$eff" in
    lean|claude) for f in "$d"/*.md; do [ -f "$f" ] && lean_strip "$f"; done ;;
  esac
  return 0
}

# Resolve effective profile: explicit flag wins; else the installed stamp; else portable.
effective_profile() {
  if [ -n "$profile" ]; then echo "$profile"
  elif [ -f "$version_file" ] && grep -q 'profile=claude' "$version_file"; then echo "claude"
  elif [ -f "$version_file" ] && grep -q 'profile=lean' "$version_file"; then echo "lean"
  else echo "portable"
  fi
}

# expected_tree DIR PROFILE — materialize what an install of the current repo would
# contain (skills with the profile transform applied, plus core/) under DIR.
expected_tree() {
  local dst="$1" eff="$2" s
  for s in $(skill_list); do
    [ -d "$s" ] || continue
    sync_tree "$s" "$dst/$s"
    apply_profile "$dst/$s/SKILL.md" "$eff" "$s"
  done
  sync_tree core "$dst/core"
  apply_core_profile "$dst/core" "$eff"
}

# drift_report — prints DRIFT/MISSING lines; returns 1 on any drift. Shared by
# --check and --status.
drift_report() {
  local eff="$1" drift=0 expected s d
  expected=$(mktemp -d)
  expected_tree "$expected" "$eff"
  for s in $(skill_list); do
    [ -d "$s" ] || continue
    if [ ! -d "$skills_dir/$s" ]; then
      echo "MISSING: $s not installed"; drift=1; continue
    fi
    d=$(tree_diff "$expected/$s" "$skills_dir/$s")
    [ -z "$d" ] || { echo "DRIFT in $s:"; echo "$d" | sed 's/^/  /'; drift=1; }
  done
  if [ ! -d "$skills_dir/core" ]; then
    echo "MISSING: core/ not installed (every ../core/ link in the skills is dead)"; drift=1
  else
    d=$(tree_diff "$expected/core" "$skills_dir/core")
    [ -z "$d" ] || { echo "DRIFT in core:"; echo "$d" | sed 's/^/  /'; drift=1; }
  fi
  if [ "$with_agents" = "1" ]; then
    for a in agents/*.md; do
      [ -e "$a" ] || continue
      cmp -s "$a" "$agents_dir/$(basename "$a")" || { echo "DRIFT in agents/$(basename "$a")"; drift=1; }
    done
  fi
  rm -rf "$expected"
  return "$drift"
}

if [ "$mode" = "update" ]; then
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || { echo "--update needs a git clone of dev-skills (no .git here). Re-clone, or re-run plain ./install.sh after refreshing the files yourself."; exit 2; }
  [ -z "$(git status --porcelain)" ] \
    || echo "Note: this clone has local modifications — they are kept; a fast-forward only touches tracked files upstream changed."
  before=$(git rev-parse HEAD)
  git pull --ff-only \
    || { echo "git pull --ff-only failed (diverged history or offline). Resolve manually, then re-run ./install.sh."; exit 1; }
  after=$(git rev-parse HEAD)
  if [ "$before" = "$after" ]; then
    echo "Already up to date ($(stamp)) — re-syncing the installed copy."
  else
    echo "Updated $(git rev-parse --short "$before") -> $(stamp):"
    git log --oneline "$before..$after" | sed 's/^/  /'
  fi
  mode="install"
fi

case "$mode" in
  install)
    eff=$(effective_profile)
    mkdir -p "$skills_dir"
    n=0
    for s in $(skill_list); do
      [ -d "$s" ] || { echo "Skip: $s not found in repo"; continue; }
      sync_tree "$s" "$skills_dir/$s"
      apply_profile "$skills_dir/$s/SKILL.md" "$eff" "$s"
      n=$((n+1))
    done
    sync_tree core "$skills_dir/core"
    apply_core_profile "$skills_dir/core" "$eff"
    if [ "$with_agents" = "1" ]; then
      mkdir -p "$agents_dir"
      for a in agents/*.md; do
        [ -e "$a" ] || continue
        cp "$a" "$agents_dir/$(basename "$a")"
      done
    fi
    echo "dev-skills@$(stamp) profile=$eff" > "$version_file"
    if [ "$with_agents" = "1" ]; then
      echo "Installed/synced $n skill(s) + core/ [$eff profile] -> $skills_dir (agents -> $agents_dir)"
    else
      echo "Installed/synced $n skill(s) + core/ [$eff profile] -> $skills_dir (skills only — shared agents are Claude-Code-specific)"
    fi
    echo "Version: $(cat "$version_file")"
    ;;
  check)
    eff=$(effective_profile)
    drift=0
    [ -f "$version_file" ] && echo "Installed: $(cat "$version_file") | Repo: dev-skills@$(stamp) profile=$eff" \
      || { echo "No version stamp found — install not done via install.sh yet."; drift=1; }
    drift_report "$eff" || drift=1
    [ "$drift" = "0" ] && echo "In sync." || exit 1
    ;;
  status)
    eff=$(effective_profile)
    if [ -f "$version_file" ]; then
      echo "Installed: $(cat "$version_file") at $skills_dir"
    else
      echo "Installed: nothing (no version stamp at $skills_dir) — run ./install.sh"
    fi
    echo "Repo:      dev-skills@$(stamp) on $(git branch --show-current 2>/dev/null || echo '?')"
    if git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1; then
      if git fetch -q 2>/dev/null; then
        behind=$(git rev-list --count 'HEAD..@{u}' 2>/dev/null || echo '?')
        ahead=$(git rev-list --count '@{u}..HEAD' 2>/dev/null || echo '?')
        case "$behind" in
          0) echo "Upstream:  up to date with $(git rev-parse --abbrev-ref '@{u}')" ;;
          *) echo "Upstream:  $behind commit(s) behind $(git rev-parse --abbrev-ref '@{u}') — run ./install.sh --update" ;;
        esac
        [ "$ahead" = "0" ] || echo "           ($ahead local commit(s) not upstream)"
      else
        echo "Upstream:  unreachable (offline?) — could not fetch"
      fi
    else
      echo "Upstream:  no tracking branch configured"
    fi
    if [ -f "$version_file" ]; then
      if out=$(drift_report "$eff"); then
        echo "Drift:     none — installed copy matches the repo ($eff profile)"
      else
        echo "Drift:     $(echo "$out" | grep -c '^  \|^MISSING') path(s) differ — run ./install.sh --check for the list, ./install.sh to re-sync"
      fi
    fi
    ;;
  uninstall)
    for s in $(skill_list); do
      rm -rf "${skills_dir:?}/$s"
    done
    [ -z "$only" ] && rm -rf "${skills_dir:?}/core"
    rm -f "$version_file"
    if [ "$with_agents" = "1" ]; then
      echo "Removed dev-skills skills from $skills_dir (agents left in place — remove manually if desired)"
    else
      echo "Removed dev-skills skills from $skills_dir"
    fi
    ;;
esac
