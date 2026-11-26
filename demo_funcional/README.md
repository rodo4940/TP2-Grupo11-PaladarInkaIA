# MVP funcional verificable — El Paladar del Inka

Esta carpeta añade **una prueba de concepto ejecutable** al repositorio del Taller de Proyectos 2. **No es el despliegue productivo** ni equivale a que la solución principal del proyecto esté implementada. Permite documentar evidencia REAL de ejecución con datos artificiales.

## Ejecución

Desde la raíz del repositorio, con Python 3.12+ y FastAPI/Uvicorn instalados:

```bash
pip install fastapi uvicorn httpx pytest
uvicorn demo_funcional.app:app --host 127.0.0.1 --port 8765
```

Visitar `http://127.0.0.1:8765`. Cuentas **solo de demostración**: `admin`, `cajero`, `cocina`; contraseña compartida `demo123`. Estas credenciales y el almacenamiento de tokens en memoria **no son seguros para producción**. No publicar el servidor en Internet.

## Pruebas

```bash
pytest -q demo_funcional/tests
```

Para reiniciar datos, detener el servidor y borrar `demo_funcional/demo_data.sqlite3`; se regenerará con tres productos, cuatro ingredientes y recetas predefinidas. Se puede elegir otra base mediante `PALADAR_DEMO_DB=/ruta/demo.sqlite3`.

## Funcionalidades que realmente implementa

- Login demo con sesiones temporales y tres roles.
- Catálogo de pizzas y recetas/consumo de ingredientes.
- Pedidos con deducción transaccional de inventario y rechazo por falta de stock.
- Ciclo de cocina con transiciones estrictas: `nuevo → preparacion → listo → entregado`.
- Pago único por pedido y sumatoria de ingresos cobrados.
- Recepción de insumos y Kardex trazable.
- Reportes diarios de ventas y dashboard.
- Ranking **heurístico**, sin entrenar modelos de IA.
- Bitácora de eventos con responsable y control de acceso por rol.

## Límites

Este MVP usa **SQLite local**, no la base PostgreSQL del backend principal. No dispone de autenticación endurecida, integración SUNAT, pagos externos, recomendaciones predictivas basadas en ML, despliegue ni aceptación de usuarios reales. Los datos son ficticios y todas las capturas deben identificar el entorno como `MVP local de demostración`.