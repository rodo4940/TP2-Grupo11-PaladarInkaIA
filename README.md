# Paladar Inka AI

Sistema inteligente basado en IA para la gestion de ventas, inventario y atencion al cliente en la pizzeria El Paladar del Inka.

## Stack

- Backend: Python 3.12 + FastAPI
- Frontend: React + TypeScript + Vite
- Base de datos: PostgreSQL 17
- Pruebas: Pytest
- Control de versiones: Git + GitHub

## Estructura

- `backend/`: API, configuracion, persistencia y pruebas.
- `frontend/`: interfaz web.
- `scripts/`: utilidades de apoyo.
- `.github/workflows/`: pruebas automaticas.

## Backend

Desde `backend/`:

```bash
python -m pip install -e ".[test]"
uvicorn app.main:app --reload
```

## Frontend

Desde `frontend/`:

```bash
npm install
npm run dev
```

## Pruebas

Desde `backend/`:

```bash
pytest -v
```

Tambien se ejecutan automaticamente mediante GitHub Actions.

## Verificacion del entorno

En Windows PowerShell:

```powershell
.\scripts\verificar_entorno.ps1
```

## Seguridad

No subir `.env`, tokens, contrasenas ni datos personales reales.
