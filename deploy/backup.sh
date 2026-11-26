#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${1:-.env.production}"
if [[ ! -f "$ENV_FILE" ]]; then echo "Falta $ENV_FILE" >&2; exit 1; fi
umask 077
mkdir -p backups
OUT="backups/paladar_$(date -u +%Y%m%d_%H%M%S).dump"
# El cliente pg_dump se ejecuta dentro del contenedor con las credenciales de su entorno.
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T db sh -ec 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$OUT"
[[ -s "$OUT" ]] || { rm -f "$OUT"; echo 'Respaldo vacío' >&2; exit 1; }
sha256sum "$OUT" > "$OUT.sha256"
echo "Respaldo local generado: $OUT (no está cifrado; cifrar antes de exportar a backup externo)"