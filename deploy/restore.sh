#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
FILE="${1:-}"; ENV_FILE="${2:-.env.production}"
[[ -f "$FILE" && -f "$ENV_FILE" ]] || { echo 'Uso: deploy/restore.sh backup.dump .env.production'; exit 1; }
[[ "${CONFIRM_RESTORE:-}" == 'PERDER_DATOS_ACTUALES' ]] || { echo 'Requiere CONFIRM_RESTORE=PERDER_DATOS_ACTUALES'; exit 1; }
# Ejecutar solo en ventana de mantenimiento, con respaldo previo y acceso aislado.
cat "$FILE" | docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T db sh -ec 'PGPASSWORD="$POSTGRES_PASSWORD" pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
echo 'Restauración aplicada; validar integridad, saldos y pedidos antes de reabrir el servicio.'