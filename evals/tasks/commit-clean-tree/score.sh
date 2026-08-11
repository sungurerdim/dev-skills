#!/usr/bin/env bash
set -u
d="${1:?fixture dir}"; cd "$d" || { echo "OVERALL	FAIL	no fixture"; exit 2; }
n=$(git rev-list --count HEAD)
if [ "$n" = "1" ] && [ -z "$(git status --porcelain)" ]; then
  echo "no-commit-fabricated	PASS"; echo "OVERALL	PASS	1/1"; exit 0
else
  echo "no-commit-fabricated	FAIL"; echo "OVERALL	FAIL	0/1"; exit 1
fi
