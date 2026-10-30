# Barrier functions (loaded by pre-commit, commit-msg and pre-push).
# The list of forbidden expressions is NOT versioned: .git/info/forbidden-terms.txt (one ERE per line, case-insensitive).
LIST="$(git rev-parse --git-path info/forbidden-terms.txt)"
[ -s "$LIST" ] || { echo "BARRIER: missing $LIST (without a list nothing is committed or pushed)" >&2; exit 1; }
PATTERN=$(grep -v -e '^#' -e '^[[:space:]]*$' "$LIST" | paste -sd'|')
[ -n "$PATTERN" ] || { echo "BARRIER: $LIST has no expressions" >&2; exit 1; }
failures=()
fail() { failures+=("$1"); }
with_data() { printf '%s\n' "$1" | grep -iE "$PATTERN" | head -3 | tr '\n' ' ' | cut -c1-200; }
finish() {
  if [ ${#failures[@]} -gt 0 ]; then
    echo "BARRIER ($1): REJECTED." >&2
    for f in "${failures[@]}"; do echo "  - $f" >&2; done
    exit 1
  fi
  exit 0
}
