#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# dev-skills installer/syncer — copies ONLY runtime files (ds-*/ skills, agents/).
# Spec, docs, and references stay in the repo; they are never loaded at runtime.
#
#   ./install.sh                 install/sync all skills into ~/.claude (global;
#                                also covers OpenCode, which reads ~/.claude/skills)
#   ./install.sh --project DIR   install into DIR/.claude instead
#   ./install.sh --target DIR    install skills into DIR directly — any Agent Skills
#                                host dir (e.g. .agents/skills, .opencode/skill).
#                                Skills only; shared agents/ are Claude-Code-specific
#   ./install.sh --skills a,b    only the named skills (e.g. ds-review,ds-commit)
#   ./install.sh --profile P     portable (default) ships files verbatim — full
#                                self-contained density for any host. lean strips
#                                the blocks marked `<!-- portable-only -->` at
#                                install time — for Claude-5-generation hosts with
#                                an always-on rules layer (e.g. dev-rules) that
#                                already supplies those universal gates. Repo files
#                                always keep the full portable text.
#   ./install.sh --check         report drift between repo and installed copy
#                                (profile-aware; reads profile from version stamp)
#   ./install.sh --update        fast-forward this clone (git pull --ff-only),
#                                then re-install with the already-stamped profile.
#                                Equivalent to `git pull && ./install.sh`; never
#                                merges or rebases on your behalf
#   ./install.sh --uninstall     remove installed dev-skills content
#
# Idempotent: safe to run twice. Sync uses --delete per skill dir, so files
# removed from a skill in the repo are also removed from the installed copy.
set -euo pipefail
cd "$(dirname "$0")"

command -v rsync >/dev/null 2>&1 || { echo "rsync is required but not installed. Install it (e.g. 'brew install rsync' or 'apt install rsync') and re-run."; exit 1; }

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
    --update)  mode="update"; shift ;;
    --uninstall) mode="uninstall"; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown flag: $1 (see --help)"; exit 2 ;;
  esac
done
case "$profile" in ""|lean|portable) ;; *) echo "Unknown profile: $profile (use lean or portable)"; exit 2 ;; esac

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

# Resolve effective profile: explicit flag wins; else the installed stamp; else portable.
effective_profile() {
  if [ -n "$profile" ]; then echo "$profile"
  elif [ -f "$version_file" ] && grep -q 'profile=lean' "$version_file"; then echo "lean"
  else echo "portable"
  fi
}

if [ "$mode" = "update" ]; then
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 \
    || { echo "--update needs a git clone of dev-skills (no .git here). Re-clone, or re-run plain ./install.sh after refreshing the files yourself."; exit 2; }
  git pull --ff-only \
    || { echo "git pull --ff-only failed (diverged history or offline). Resolve manually, then re-run ./install.sh."; exit 1; }
  mode="install"
fi

case "$mode" in
  install)
    eff=$(effective_profile)
    mkdir -p "$skills_dir"
    n=0
    for s in $(skill_list); do
      [ -d "$s" ] || { echo "Skip: $s not found in repo"; continue; }
      rsync -a --delete "$s/" "$skills_dir/$s/"
      [ "$eff" = "lean" ] && [ -f "$skills_dir/$s/SKILL.md" ] && lean_strip "$skills_dir/$s/SKILL.md"
      n=$((n+1))
    done
    if [ "$with_agents" = "1" ]; then
      mkdir -p "$agents_dir"
      for a in agents/*.md; do
        [ -e "$a" ] || continue
        rsync -a "$a" "$agents_dir/$(basename "$a")"
      done
    fi
    echo "dev-skills@$(stamp) profile=$eff" > "$version_file"
    if [ "$with_agents" = "1" ]; then
      echo "Installed/synced $n skill(s) [$eff profile] -> $skills_dir (agents -> $agents_dir)"
    else
      echo "Installed/synced $n skill(s) [$eff profile] -> $skills_dir (skills only — shared agents are Claude-Code-specific)"
    fi
    echo "Version: $(cat "$version_file")"
    ;;
  check)
    eff=$(effective_profile)
    drift=0
    [ -f "$version_file" ] && echo "Installed: $(cat "$version_file") | Repo: dev-skills@$(stamp) profile=$eff" \
      || { echo "No version stamp found — install not done via install.sh yet."; drift=1; }
    expected=""
    if [ "$eff" = "lean" ]; then
      expected=$(mktemp -d)
      trap 'rm -rf "$expected"' EXIT
    fi
    for s in $(skill_list); do
      [ -d "$s" ] || continue
      if [ ! -d "$skills_dir/$s" ]; then
        echo "MISSING: $s not installed"; drift=1; continue
      fi
      src="$s"
      if [ "$eff" = "lean" ]; then
        rsync -a "$s/" "$expected/$s/"
        [ -f "$expected/$s/SKILL.md" ] && lean_strip "$expected/$s/SKILL.md"
        src="$expected/$s"
      fi
      d=$(rsync -rcn --delete --out-format='%n' "$src/" "$skills_dir/$s/" | grep -v '/$' || true)
      [ -z "$d" ] || { echo "DRIFT in $s:"; echo "$d" | sed 's/^/  /'; drift=1; }
    done
    if [ "$with_agents" = "1" ]; then
      for a in agents/*.md; do
        [ -e "$a" ] || continue
        cmp -s "$a" "$agents_dir/$(basename "$a")" || { echo "DRIFT in agents/$(basename "$a")"; drift=1; }
      done
    fi
    [ "$drift" = "0" ] && echo "In sync." || exit 1
    ;;
  uninstall)
    for s in $(skill_list); do
      rm -rf "${skills_dir:?}/$s"
    done
    rm -f "$version_file"
    if [ "$with_agents" = "1" ]; then
      echo "Removed dev-skills skills from $skills_dir (agents left in place — remove manually if desired)"
    else
      echo "Removed dev-skills skills from $skills_dir"
    fi
    ;;
esac
