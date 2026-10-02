# Paladar Inka AI

## Descripcion

Sistema inteligente basado en IA para la gestion de ventas, inventario y atencion al cliente en la pizzeria El Paladar del Inka.

El repositorio se encuentra actualmente en una etapa de base tecnica y evidencias academicas. Todavia no se consideran implementados todos los modulos funcionales de negocio.

## Arquitectura

El proyecto usa un monolito modular:

- `backend/`: API central con FastAPI y reglas de negocio.
- `frontend/`: cliente React con TypeScript y Vite.
- PostgreSQL: fuente de verdad operativa.
- Asistente IA: previsto mediante API de LLM y Tools / Function Calling sobre funciones autorizadas del backend.

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
- Git y GitHub

Docker y Docker Compose se conservan como una opcion de reproducibilidad local, pero no son requisito para trabajar con el repositorio ni para las evidencias de la Unidad 2.

## Requisitos minimos

- Git
- Python 3.12
- Node.js 22 LTS
- npm
- PostgreSQL 17

## Verificacion del entorno

En Windows PowerShell:

```powershell
.\scripts\verificar_entorno.ps1
```

La salida sirve como evidencia del Anexo 04 y debe capturarse con los datos reales de cada integrante.

## Configuracion del backend

Desde `backend/`:

```bash
python -m pip install -e ".[test]"
```

Configurar las variables de entorno necesarias a partir de `.env.example`.

## Ejecucion del backend

Desde `backend/`:

```bash
uvicorn app.main:app --reload
```

## Configuracion y ejecucion del frontend

Desde `frontend/`:

```bash
npm install
npm run dev
```

## URLs de desarrollo

- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- Ready: http://localhost:8000/api/v1/ready

## Pruebas backend

Desde `backend/`:

```bash
pytest -v
```

Para cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

Las pruebas tambien se ejecutan en GitHub Actions mediante `.github/workflows/backend-tests.yml`.

## Migraciones

Desde `backend/`:

```bash
alembic revision --autogenerate -m "descripcion"
alembic upgrade head
```

## Docker opcional

Si un integrante prefiere trabajar con contenedores:

```bash
docker compose up --build
```

Para detenerlos:

```bash
docker compose down
```

## Documentacion de la Unidad 2

- `docs/SCRUM.md`: linea base de Scrum alineada con el alcance real del proyecto.
- `docs/UNIDAD2_EVIDENCIAS.md`: checklist de evidencias de los Anexos 04, 05 y 06.
- `scripts/verificar_entorno.ps1`: verificacion del entorno para capturas reales.

## Estructura

- `backend/app/api`: rutas HTTP versionadas.
- `backend/app/core`: configuracion central.
- `backend/app/db`: conexion y utilidades de base de datos.
- `backend/alembic`: migraciones.
- `backend/tests`: pruebas automatizadas.
- `frontend/src`: aplicacion React.
- `docs`: documentacion tecnica y academica.
- `scripts`: utilidades de apoyo.

## Seguridad

No subir `.env`, claves, tokens, passwords reales ni datos personales. Los valores de `.env.example` son placeholders para desarrollo local.
