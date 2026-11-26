# Instalación desde GitHub — Paladar Inka AI

Esta es la **ruta oficial para ejecutar la versión de demostración en tu propia computadora**, con usuarios y ventas ficticios. No equivale a activar el servicio en producción.

## Requisitos
- Windows 10/11 con Docker Desktop + WSL2, o Linux/macOS con Docker Engine y **Docker Compose v2**.
- Motor Docker iniciado, conectividad a Docker Hub para descargar las imágenes de Node, Python y PostgreSQL.
- Recomendación para la demo: 4 GB libres de memoria, 6 GB en disco y puertos locales 5173/8000 libres. No requiere instalar Node, Python ni PostgreSQL por separado.

## Descargar (importante: rama correcta)
La rama principal `main` puede no contener la versión integrada hasta que el PR #11 supere la política de revisión del repositorio.

**Desde GitHub:** abre la rama `feature/mvp-demostrable-qa-20261126` y selecciona **Code → Download ZIP**. Extrae la carpeta.

**Desde terminal:**
```bash
git clone --branch feature/mvp-demostrable-qa-20261126 --single-branch https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA.git
cd TP2-Grupo11-PaladarInkaIA
```
Cuando el PR #11 se fusione, podrás clonar `main` normalmente.

## Windows — recomendado
1. Abre Docker Desktop y espera a que indique que el motor esté listo.
2. Haz doble clic en **`INICIAR_WINDOWS.bat`** en la raíz del proyecto (alternativa: desde PowerShell `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start.ps1`).
3. Se generará automáticamente `.env` con secretos aleatorios **solo si no existía**, se crearán contenedores y migraciones, y se cargarán usuarios e inventario ficticios.
4. Abre **http://localhost:5173**.
5. Usuario `admin`, `cajero` o `cocina`. La contraseña aleatoria está en `SEED_ADMIN_PASSWORD` dentro del `.env` de tu propia computadora. No publiques ese archivo.

## Linux, macOS o WSL
```bash
bash scripts/start.sh
```
Después abre **http://localhost:5173**. API: http://localhost:8000/docs (Swagger habilitado solo en desarrollo).

## Uso posterior (con datos conservados)
Puedes volver a ejecutar el mismo script. No cambia contraseñas existentes ni duplica el catálogo de prueba. Para apagar sin borrar datos:
```bash
docker compose down
```
Para comprobar que funciona:
```bash
bash scripts/verify.sh
```
Para limpiar por completo la base de datos ficticia, ejecuta `bash scripts/reset-demo.sh`: el comando pide la palabra de confirmación `ELIMINAR-DEMO` y **destruye los datos locales** del proyecto.

## Problemas conocidos y solución
| Síntoma | Acción |
|---|---|
| Docker no está iniciado | Abrir Docker Desktop; ejecutar `docker info` |
| Puerto 5173 ocupado | Edita `.env`: `FRONTEND_PORT=5174` y `CORS_ORIGINS=http://localhost:5174`; abre `localhost:5174` |
| Puerto 8000 ocupado | Edita `.env`: `BACKEND_PORT=8001` y `VITE_API_URL=http://localhost:8001`; reconstruye el frontend `docker compose up -d --build` |
| PostgreSQL local usa puerto 5432 | No hay conflicto: el PostgreSQL de esta instalación no publica 5432 fuera de Docker |
| No puedes iniciar sesión | Revisa la contraseña de semilla en `.env`, busca errores con `docker compose logs backend`; no restablezcas datos sin respaldo |
| Pantalla o API vacía | `docker compose ps` y `docker compose logs --tail=100 frontend backend db` |
| Actualizaste código en GitHub | `git pull` y luego `bash scripts/start.sh` o el archivo Windows; Alembic aplica las nuevas migraciones |

## Seguridad y alcance
- El demo usa datos de prueba y claves generadas localmente; el script de instalación se bloquea si `APP_ENV=production`.
- La base PostgreSQL no está expuesta al host, la API y React solo están publicados en `127.0.0.1`.
- Nunca copies `.env` a GitHub ni reutilices estas contraseñas en entornos públicos.
- Ticket interno **no es comprobante electrónico SUNAT**. Las recomendaciones de demanda son estadísticas y no un modelo IA entrenado.
- Antes de producción: consulta `docs/RELEASE_READINESS.md`, `deploy/OPERACIONES.md` y el issue #12.