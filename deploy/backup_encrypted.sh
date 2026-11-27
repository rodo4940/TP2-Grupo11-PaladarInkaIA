#!/usr/bin/env bash
# Respaldo PostgreSQL en flujo CIFRADO: dump sin escribir en disco en texto claro.
# Requiere age y rclone instalados y almacenamiento remoto configurado.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${1:-.env.production}"
: "${AGE_RECIPIENT:?Se necesita AGE_RECIPIENT fuera de Git}"
: "${BACKUP_REMOTE:?Se necesita BACKUP_REMOTE (ruta remota rclone) fuera de Git}"
[[ -f "$ENV_FILE" ]] || { echo "No existe archivo de entorno" >&2; exit 1; }
command -v age >/dev/null
command -v rclone >/dev/null
command -v sha256sum >/dev/null
[[ "$AGE_RECIPIENT" == age1* ]] || { echo "Destinatario age inválido" >&2; exit 1; }
umask 077
mkdir -p backups/encrypted
NOW="$(date -u +%Y%m%dT%H%M%SZ)"
NAME="paladar_${NOW}_$$.dump.age"
TARGET="backups/encrypted/$NAME"
TEMP="${TARGET}.tmp"
trap 'rm -f "$TEMP"' EXIT
docker compose --env-file "$ENV_FILE" -f docker-compose.prod.yml exec -T db sh -ec \
 'PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
 | age -r "$AGE_RECIPIENT" -o "$TEMP"
[[ -s "$TEMP" ]] || { echo 'Copia cifrada vacía' >&2; exit 1; }
mv "$TEMP" "$TARGET"
sha256sum "$TARGET" > "$TARGET.sha256"
echo "Verificando transferencia de copia cifrada a destino remoto..."
rclone copyto "$TARGET" "${BACKUP_REMOTE%/}/$NAME"
rclone copyto "$TARGET.sha256" "${BACKUP_REMOTE%/}/$NAME.sha256"
EXPECTED="$(sha256sum "$TARGET" | awk '{print $1}')"
REMOTE_HASH="$(rclone cat "${BACKUP_REMOTE%/}/$NAME" | sha256sum | awk '{print $1}')"
[[ "$EXPECTED" == "$REMOTE_HASH" ]] || { echo "Checksum remoto diferente" >&2; exit 1; }
echo "VERIFICADO: copia cifrada remota SHA-256 $EXPECTED"
echo "Restauración aún no probada; ejecutar procedimiento separado en entorno aislado."
