# Paladar Inka AI 2

## Descripcion

Sistema inteligente basado en IA para la gestion de ventas, inventario y atencion al cliente en la pizzeria El Paladar del Inka.

TASK-001 contiene solo el bootstrap tecnico: backend, frontend, base de datos, Docker, pruebas y documentacion inicial. No incluye modulos funcionales de negocio.

## Arquitectura

El proyecto usa un monolito modular:

- `backend/`: API central con FastAPI y reglas de negocio futuras.
- `frontend/`: cliente React con TypeScript.
- `db`: PostgreSQL como fuente de verdad operativa.

## Tecnologias

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- Alembic
- Pydantic v2 y pydantic-settings
- PostgreSQL 17
- Pytest
- Node.js 22
- React
- TypeScript
- Vite
- Docker y Docker Compose

## Requisitos

- Git
- Docker Desktop
- Docker Compose v2

## Configuracion

1. Clonar el repositorio.
2. Copiar `.env.example` a `.env`.
3. Revisar los valores locales de `.env`.
4. Iniciar Docker.

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

## Ejecucion

```bash
docker compose up --build
```

## URLs

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- Ready: http://localhost:8000/api/v1/ready

## Pruebas backend

```bash
docker compose exec backend pytest -v
```

Tambien puede ejecutarse localmente desde `backend/` si las dependencias estan instaladas:

```bash
pytest -v
```

## Migraciones

Desde `backend/`:

```bash
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

Alembic toma la URL de base de datos desde las mismas variables usadas por la aplicacion.

## Detener proyecto

Detener contenedores conservando volumenes:

```bash
docker compose down
```

Detener contenedores y eliminar volumenes, incluyendo datos locales de PostgreSQL:

```bash
docker compose down -v
```

## Estructura

- `backend/app/api`: rutas HTTP versionadas.
- `backend/app/core`: configuracion central.
- `backend/app/db`: conexion y utilidades de base de datos.
- `backend/alembic`: migraciones.
- `backend/tests`: pruebas automatizadas.
- `frontend/src`: aplicacion React.
- `docs`: documentacion futura del proyecto.
- `scripts`: scripts futuros de apoyo.

## Seguridad

No subir `.env`, claves, tokens, passwords reales ni datos personales. Los valores de `.env.example` son placeholders para desarrollo local.
