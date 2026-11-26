#!/usr/bin/env bash
# Instalación local reproducible: datos ficticios, credenciales generadas en el equipo.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  echo 'ERROR: instala Docker Desktop/Engine con Compose v2 y arráncalo.' >&2; exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo 'ERROR: Docker no está iniciado o tu usuario no tiene permisos.' >&2; exit 1
fi

random_hex() { od -An -v -N "$1" -tx1 /dev/urandom | tr -d ' \n'; }
if [[ ! -f .env ]]; then
  umask 077
  db_pass="$(random_hex 24)"
  jwt_secret="$(random_hex 48)"
  demo_pass="$(random_hex 18)"
  while IFS= read -r line || [[ -n "$line" ]]; do
    case "$line" in
      DATABASE_PASSWORD=*) printf 'DATABASE_PASSWORD=%s\n' "$db_pass" ;;
      JWT_SECRET=*) printf 'JWT_SECRET=%s\n' "$jwt_secret" ;;
      SEED_ADMIN_PASSWORD=*) printf 'SEED_ADMIN_PASSWORD=%s\n' "$demo_pass" ;;
      *) printf '%s\n' "$line" ;;
    esac
  done < .env.example > .env
  chmod 600 .env
  echo 'Se creó .env con claves aleatorias. No compartas ni subas este archivo.'
else
  echo 'Se conservará el archivo .env existente; no se sobrescriben credenciales.'
fi
if grep -Eq '^APP_ENV=production([[:space:]]*)$' .env; then
  echo 'ERROR: scripts/start.sh es solo para desarrollo/demostración. No usar con APP_ENV=production.' >&2; exit 1
fi

printf '\n[1/4] Compilando e iniciando PostgreSQL, API y React...\n'
docker compose up --build -d
printf '[2/4] Comprobando que la API y PostgreSQL están listos...\n'
ready=0
for i in $(seq 1 45); do
  if docker compose exec -T backend python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/v1/ready',timeout=3)" >/dev/null 2>&1; then
    ready=1; break
  fi
  sleep 2
done
if [[ "$ready" != '1' ]]; then
  echo 'ERROR: API no se inicializó. Revisa: docker compose logs --tail=100 backend db' >&2
  exit 1
fi
printf '[3/4] Creando usuarios, catálogo y existencias FICTICIAS (idempotente)...\n'
docker compose exec -T backend python -m app.seed
printf '[4/4] Verificando frontend...\n'
ui_ready=0
for i in $(seq 1 30); do
  if docker compose exec -T frontend node -e "fetch('http://127.0.0.1:5173').then(r=>{if(!r.ok)process.exit(1)}).catch(()=>process.exit(1))" >/dev/null 2>&1; then
    ui_ready=1; break
  fi
  sleep 2
done
if [[ "$ui_ready" != '1' ]]; then
  echo 'ERROR: React no responde. Revisa: docker compose logs --tail=100 frontend' >&2
  exit 1
fi
cat <<'MESSAGE'

LISTO: entorno local de demostración levantado.
  Interfaz:      http://localhost:5173
  API/Swagger:   http://localhost:8000/docs
  Usuarios:      admin | cajero | cocina
  Contraseña:    valor SEED_ADMIN_PASSWORD dentro de tu .env local

  Ejecutar pruebas de conectividad: bash scripts/verify.sh
  Detener sin perder datos:         docker compose down
  Limpiar datos demo (DESTRUCTIVO): bash scripts/reset-demo.sh

AVISO: operaciones de ejemplo; NO enviar boletas SUNAT ni cobrar dinero real.
MESSAGE