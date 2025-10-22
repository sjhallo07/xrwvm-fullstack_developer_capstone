#!/usr/bin/env bash
# Encuentra archivos duplicados por hash (md5) y lista sus rutas.
# Uso:
#  ./find_duplicates.sh --check    # solo informa
#  ./find_duplicates.sh --delete   # elimina duplicados dejando uno por hash (SÓLO USAR CON CAUTELA)
#
# Excluye node_modules, .git y venv por defecto.

set -euo pipefail

MODE="${1:---check}"
ROOT_DIR="${2:-.}"

TMPFILE=$(mktemp)
trap 'rm -f "$TMPFILE"' EXIT

echo "Generando hashes en $ROOT_DIR ..."
find "$ROOT_DIR" -type f \
  ! -path "*/node_modules/*" \
  ! -path "*/.git/*" \
  ! -path "*/venv/*" \
  ! -path "*/.venv/*" \
  -print0 |
  xargs -0 md5sum > "$TMPFILE"

echo "Buscando duplicados..."
awk '{ print $1 " " $2 }' "$TMPFILE" | sort | awk '
{
  hash=$1; $1=""; path=substr($0,2);
  a[hash]=a[hash] "||" path;
  cnt[hash]++;
}
END {
  for (h in cnt) {
    if (cnt[h] > 1) {
      n = split(a[h], arr, "||");
      printf("DUP_HASH %s COUNT %d\n", h, cnt[h]);
      for (i=1;i<=n;i++) if (length(arr[i])>0) print "  " arr[i];
      print "";
    }
  }
}
'

if [ "$MODE" = "--delete" ]; then
  echo "MODO --delete: eliminando duplicados y conservando el primer archivo listado por hash."
  awk '{ print $1 " " $2 }' "$TMPFILE" | sort | awk '
{
  hash=$1; $1=""; path=substr($0,2);
  if (!(hash in seen)) {
    seen[hash]=path;
  } else {
    print path;
  }
}' | while read -r dup; do
    echo "Eliminando: $dup"
    rm -v "$dup"
  done
  echo "Eliminación completada. Recomendado: revisar git status y confirmar."
else
  echo "Modo de solo verificación (--check). Para eliminar duplicados ejecutar con --delete."
fi
