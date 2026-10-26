#!/usr/bin/env bash
# Muestra el código de una etapa en una carpeta aparte, sin cambiar la rama de esta
# carpeta (main), donde están las slides.
#
# Uso: scripts/etapa.sh e05 [carpeta]
#   e05      → número de etapa (o el nombre completo de la rama)
#   carpeta  → dónde dejar el código (por defecto: ../<repo>-codigo)
#
# Después: cd <carpeta> && docker compose up --build
set -euo pipefail

if [ $# -lt 1 ]; then
  echo "Uso: scripts/etapa.sh eNN [carpeta]" >&2
  exit 2
fi

raiz="$(git rev-parse --show-toplevel)"
carpeta="${2:-$(dirname "$raiz")/$(basename "$raiz")-codigo}"

rama=$(git -C "$raiz" for-each-ref --format='%(refname:short)' refs/heads \
  | grep -E "^$1(-|$)" || true)
if [ "$(wc -l <<<"$rama" | tr -d ' ')" != 1 ] || [ -z "$rama" ]; then
  echo "No encuentro una única rama para '$1'. Ramas disponibles:" >&2
  git -C "$raiz" for-each-ref --format='  %(refname:short)' refs/heads >&2
  exit 1
fi

if [ ! -e "$carpeta/.git" ]; then
  git -C "$raiz" worktree add --quiet --detach "$carpeta" "$rama"
  [ -f "$carpeta/.env" ] || cp "$carpeta/.env.example" "$carpeta/.env"
else
  if [ -n "$(git -C "$carpeta" status --porcelain --untracked-files=no)" ]; then
    echo "Hay cambios sin guardar en $carpeta. Descartalos o guardalos antes de cambiar de etapa." >&2
    exit 1
  fi
  git -C "$carpeta" checkout --quiet --detach "$rama"
fi

echo "Código de $rama en $carpeta"
echo "  cd $carpeta && docker compose up --build"
