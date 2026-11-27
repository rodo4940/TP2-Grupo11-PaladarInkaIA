#!/usr/bin/env bash
# Restauración solo en entorno de RECUPERACIÓN AISLADO y autorizado.
set -Eeuo pipefail
cd "$(dirname "$0")/.."
FILE="${1:-}"
ENV_FILE="${2:-.env.production}"
[[ -f "$FILE" && -f "$FILE.sha256" && -f "$ENV_FILE" ]] || {
  echo "Uso: restore_encrypted.sh archivo.dump.age .env.production" >&2; exit 1; }
[[ "${CONFIRM_RESTORE:-}" == 'PERDER_DATOS_ACTUALES' ]] || {
  echo "Falta CONFIRM_RESTORE=PERDER_DATOS_ACTUALES" >&2; exit 1; }
[[ "${RESTORE_ISOLATED:-}" == 'YES_I_CONFIRMED_ISOLATION' ]] || {
  echo "Se debe certificar el entorno aislado antes de restaurar" >&2; exit 1; }
: "${AGE_IDENTITY_FILE:?Proporciona AGE_IDENTITY_FILE externo al repositorio}"
[[ -r "$AGE_IDENTITY_FILE" ]] || { echo 'Identidad age inaccesible' >&2; exit 1; }
command -v age >/dev/null
sha256sum --check "$FILE.sha256"
umask 077
TEMP="$(mktemp --tmpdir paladar_restore_XXXXXXXX.dump)"
trap 'rm -f "$TEMP"' EXIT
age -d -i "$AGE_IDENTITY_FILE" -o "$TEMP" "$FILE"
[[ -s "$TEMP" ]] || { echo 'El dump descifrado está vacío' >&2; exit 1; }
sha256sum "$TEMP" > "$TEMP.sha256"
trap 'rm -f "$TEMP" "$TEMP.sha256"' EXIT
CONFIRM_RESTORE=PERDER_DATOS_ACTUALES bash deploy/restore.sh "$TEMP" "$ENV_FILE"
echo "AVISO: validar saldos, roles, inventario, migración y tiempos RTO antes de acreditar recuperación."
