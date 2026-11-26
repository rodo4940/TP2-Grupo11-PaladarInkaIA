#!/usr/bin/env bash
# Elimina la base de datos de la DEMO local; nunca usar contra producción.
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
if grep -Eq '^APP_ENV=production([[:space:]]*)$' .env 2>/dev/null; then
 echo 'ERROR: No se permite borrar datos con APP_ENV=production.' >&2; exit 1
fi
echo 'ATENCIÓN: Se eliminarán todos los datos persistentes del entorno demo de esta carpeta.'
read -r -p 'Escribe ELIMINAR-DEMO para confirmar: ' answer
if [[ "$answer" != 'ELIMINAR-DEMO' ]]; then echo 'Cancelado: no se modificó nada.'; exit 0; fi
docker compose down --volumes
echo 'Datos demo borrados. Puedes arrancar de nuevo con bash scripts/start.sh.'