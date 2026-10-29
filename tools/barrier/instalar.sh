#!/usr/bin/env bash
# Activa la barrera en esta copia del repo. Correr una vez por clon, desde la raíz.
set -eu
git config core.hooksPath tools/barrier
lista="$(git rev-parse --git-path info/palabras-prohibidas.txt)"
if [ ! -s "$lista" ]; then
  mkdir -p "$(dirname "$lista")"
  printf '%s\n' '# Una expresión regular extendida por línea; no distingue mayúsculas. NO se versiona.' \
    '# Agregar: dominio y servidores de la empresa, cuentas, rangos de red, nombres internos.' > "$lista"
  echo "Creada $lista vacía: completarla. Mientras no tenga expresiones, la barrera rechaza todo."
fi
echo "Barrera activa (core.hooksPath=$(git config core.hooksPath))."
