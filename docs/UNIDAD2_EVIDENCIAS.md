# Unidad 2 - Evidencias y verificacion

Repositorio: https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA

Este archivo sirve como guia de evidencia real para los Anexos 04, 05 y 06. No sustituye las capturas del equipo cuando la guia solicita evidencia visual.

## Anexo 04 - Entorno, Git y GitHub

Evidencia verificable en el repositorio:

- rama principal `main`;
- estructura `backend/`, `frontend/`, `docs/` y `scripts/`;
- `.gitignore`, `.gitattributes`, `.python-version` y `.nvmrc`;
- README con instrucciones de ejecucion;
- workflow `.github/workflows/backend-tests.yml`;
- script `scripts/verificar_entorno.ps1`.

Capturas que debe incorporar el equipo:

- IDE con el proyecto abierto;
- salida de `scripts/verificar_entorno.ps1`;
- `git remote -v`;
- `git log --oneline --graph --decorate --all`;
- ramas reales;
- Pull Request revisado/fusionado;
- colaboradores, si corresponde.

## Anexo 05 - Scrum

La linea base Scrum esta en `docs/SCRUM.md`.

Para la sustentacion se debe mostrar:

- Product Backlog;
- Sprint Goal;
- tablero actualizado;
- una tarea vinculada a una historia;
- evidencia de incremento real;
- retrospectiva breve basada en hechos.

## Anexo 06 - Pruebas

Framework actualmente configurado: Pytest.

Ubicacion:

- `backend/tests/`;
- configuracion en `backend/pyproject.toml`;
- ejecucion automatizada en `.github/workflows/backend-tests.yml`.

Comando recomendado desde `backend/`:

```bash
python -m pip install -e ".[test]"
pytest -v
```

Para cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

Evidencias a capturar:

- terminal o GitHub Actions con pruebas aprobadas;
- caso de prueba y codigo asociado;
- tablero Scrum con tarea de testing en Done;
- resultado de cobertura si se presenta como metrica.

## Regla de integridad

Solo se marca como ejecutada una actividad cuando exista evidencia real. Los espacios de captura del informe deben completarse con resultados obtenidos por el equipo.
