#!/usr/bin/env bash
# Scores the fixture repo at $1. TSV: criterion<TAB>PASS|FAIL. Exit 0 = all pass.
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
ok=0; fail=0
r() { if [ "$2" = "0" ]; then echo "$1	PASS"; ok=$((ok+1)); else echo "$1	FAIL"; fail=$((fail+1)); fi; }
rc=1; grep -qE '"version": *"1\.3\.0"' package.json && rc=0
r "version-bumped-minor(feat->1.3.0)" "$rc"
rc=1; grep -qE '^## \[1\.3\.0\] - 20[0-9]{2}-[0-9]{2}-[0-9]{2}' CHANGELOG.md && rc=0
r "changelog-has-dated-1.3.0-section" "$rc"
rc=1; awk '/^## \[1\.3\.0\]/{f=1;next} /^## \[/{f=0} f' CHANGELOG.md | grep -q 'addDays' && rc=0
r "unreleased-items-moved-into-1.3.0" "$rc"
rc=1; grep -q '^## \[Unreleased\]' CHANGELOG.md && [ -z "$(awk '/^## \[Unreleased\]/{f=1;next} /^## \[/{f=0} f' CHANGELOG.md | grep -E '^- ')" ] && rc=0
r "unreleased-section-kept-empty" "$rc"
rc=1; git tag --points-at HEAD | grep -qx 'v1.3.0' && rc=0
r "tag-v1.3.0-on-HEAD" "$rc"
rc=1; git log -1 --format=%s | grep -qiE '(release|version|bump).*1\.3\.0|1\.3\.0' && rc=0
r "release-commit-names-version" "$rc"
rc=1; node --test >/dev/null 2>&1 && rc=0
r "tests-still-green" "$rc"
rc=1; [ -z "$(git status --porcelain | grep -vE '^\?\? ds/$')" ] && rc=0
r "working-tree-clean" "$rc"
if [ "$fail" = "0" ]; then echo "OVERALL	PASS	$ok/$((ok+fail))"; exit 0; else echo "OVERALL	FAIL	$ok/$((ok+fail))"; exit 1; fi
