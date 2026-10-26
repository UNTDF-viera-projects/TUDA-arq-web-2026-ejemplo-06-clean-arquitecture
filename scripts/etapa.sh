#!/usr/bin/env bash
# Muestra el código de una etapa en una carpeta aparte, sin cambiar la rama de esta
# carpeta (main), donde están las slides.
#
# Uso: scripts/etapa.sh            → menú para elegir la etapa
#      scripts/etapa.sh e05        → número de etapa (o el nombre completo de la rama)
#      scripts/etapa.sh e05 <dir>  → otra carpeta de destino
#
# Carpeta por defecto: ../<repo>-codigo (o la variable ETAPA_CARPETA).
# Después: cd <carpeta> && docker compose up --build
set -euo pipefail

raiz="$(git rev-parse --show-toplevel)"
carpeta="${2:-${ETAPA_CARPETA:-$(dirname "$raiz")/$(basename "$raiz")-codigo}}"

ramas_de_la_clase() {
  git -C "$raiz" for-each-ref --format='%(refname:short)' refs/heads \
    | grep -E '^(e[0-9]{2}-|ejercicio-|solucion-|opcional-)' | sort
}

# Rama que muestra hoy la carpeta de código (vacío si todavía no existe).
rama_actual() {
  [ -e "$carpeta/.git" ] || return 0
  local commit
  commit=$(git -C "$carpeta" rev-parse HEAD)
  git -C "$raiz" for-each-ref --points-at "$commit" --format='%(refname:short)' refs/heads \
    | grep -E '^(e[0-9]{2}-|ejercicio-|solucion-|opcional-)' | head -1 || true
}

elegir_con_menu() {
  local actual opciones=() rama asunto marca
  actual=$(rama_actual)
  for rama in $(ramas_de_la_clase); do
    asunto=$(git -C "$raiz" log -1 --format=%s "$rama")
    marca=""
    [ "$rama" = "$actual" ] && marca="  ← actual"
    opciones+=("$rama · $asunto$marca")
  done

  echo "¿A qué etapa vamos? (código en $carpeta)" >&2
  PS3="Número de etapa (Ctrl+C para salir): "
  select opcion in "${opciones[@]}"; do
    if [ -n "${opcion:-}" ]; then
      echo "${opcion%% ·*}"
      return 0
    fi
    echo "Elegí un número de la lista." >&2
  done
  exit 1  # fin de la entrada sin elegir
}

if [ $# -ge 1 ] && [ -n "$1" ]; then
  rama=$(ramas_de_la_clase | grep -E "^$1(-|$)" || true)
  if [ -z "$rama" ] || [ "$(wc -l <<<"$rama" | tr -d ' ')" != 1 ]; then
    echo "No encuentro una única rama para '$1'. Ramas disponibles:" >&2
    ramas_de_la_clase | sed 's/^/  /' >&2
    exit 1
  fi
else
  rama=$(elegir_con_menu)
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
