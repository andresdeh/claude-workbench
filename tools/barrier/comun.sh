# Funciones de la barrera (las cargan pre-commit, commit-msg y pre-push). Ver docs/01-diseno.md §8.
# La lista de expresiones prohibidas NO se versiona: .git/info/palabras-prohibidas.txt (una ERE por línea, sin distinguir mayúsculas).
LISTA="$(git rev-parse --git-path info/palabras-prohibidas.txt)"
[ -s "$LISTA" ] || { echo "BARRERA: falta $LISTA (sin lista no se commitea ni se sube nada)" >&2; exit 1; }
PATRON=$(grep -v -e '^#' -e '^[[:space:]]*$' "$LISTA" | paste -sd'|')
[ -n "$PATRON" ] || { echo "BARRERA: $LISTA no tiene expresiones" >&2; exit 1; }
fallas=()
falla() { fallas+=("$1"); }
con_dato() { printf '%s\n' "$1" | grep -iE "$PATRON" | head -3 | tr '\n' ' ' | cut -c1-200; }
terminar() {
  if [ ${#fallas[@]} -gt 0 ]; then
    echo "BARRERA ($1): RECHAZADO." >&2
    for f in "${fallas[@]}"; do echo "  - $f" >&2; done
    exit 1
  fi
  exit 0
}
