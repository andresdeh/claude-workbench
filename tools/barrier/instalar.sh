#!/usr/bin/env bash
# Activates the barrier in this copy of the repo. Run once per clone, from the root.
set -eu
git config core.hooksPath tools/barrier
list="$(git rev-parse --git-path info/forbidden-terms.txt)"
if [ ! -s "$list" ]; then
  mkdir -p "$(dirname "$list")"
  printf '%s\n' '# One extended regular expression per line; case-insensitive. NOT versioned.' \
    '# Add: your company or private domain, servers, accounts, network ranges, internal names.' > "$list"
  echo "Created empty $list: fill it in. While it has no expressions, the barrier rejects everything."
fi
echo "Barrier active (core.hooksPath=$(git config core.hooksPath))."
