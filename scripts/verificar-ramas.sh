#!/usr/bin/env bash
# Corre los tests del backend en cada rama de la clase, sin tocar el árbol de trabajo.
# Uso: scripts/verificar-ramas.sh [python]   (por defecto: backend/.venv/bin/python)
set -euo pipefail

raiz="$(git rev-parse --show-toplevel)"
python="${1:-$raiz/backend/.venv/bin/python}"
temporal="$(mktemp -d)"
trap 'rm -rf "$temporal"' EXIT

ramas=$(git -C "$raiz" for-each-ref --format='%(refname:short)' refs/heads \
  | grep -E '^(e[0-9]{2}-|ejercicio-|solucion-|opcional-)' | sort)

fallas=0
for rama in $ramas; do
  destino="$temporal/$rama"
  mkdir -p "$destino"
  git -C "$raiz" archive "$rama" backend | tar -x -C "$destino"
  if salida=$(cd "$destino/backend" && "$python" manage.py test 2>&1); then
    printf '✔ %-34s %s\n' "$rama" "$(grep -E '^Ran ' <<<"$salida")"
  elif [[ "$rama" == ejercicio-* ]]; then
    # El ejercicio trae tests que fallan hasta que se resuelva.
    printf '○ %-34s %s (esperado)\n' "$rama" "$(grep -E '^(Ran |FAILED)' <<<"$salida" | tr '\n' ' ')"
  else
    printf '✘ %-34s %s\n' "$rama" "$(grep -E '^(Ran |FAILED)' <<<"$salida" | tr '\n' ' ')"
    fallas=$((fallas + 1))
  fi
done

if [ "$fallas" -gt 0 ]; then
  echo "$fallas rama(s) con tests en rojo"
  exit 1
fi
echo "Todas las ramas en verde"
