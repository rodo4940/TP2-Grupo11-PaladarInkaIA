#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
docker compose exec -T backend python -c "import urllib.request; u='http://127.0.0.1:8000/api/v1/ready'; r=urllib.request.urlopen(u,timeout=5); print('API /ready',r.status,r.read().decode())"
docker compose exec -T frontend node -e "fetch('http://127.0.0.1:5173').then(async r=>{console.log('React:',r.status);if(!r.ok)process.exit(1)}).catch(e=>{console.error(e);process.exit(1)})"
docker compose exec -T backend alembic current
echo 'Verificación rápida completada; para tests unitarios revisa el workflow de GitHub o ejecuta pytest en backend.'