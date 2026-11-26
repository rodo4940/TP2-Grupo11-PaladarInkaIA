# Alcance de pruebas y evidencias auténticas

Las pruebas de `demo_funcional/tests/test_demo.py` son pruebas de integración HTTP contra una aplicación **local de demostración**. Usan una base SQLite temporal, datos ficticios y no consultan datos reales de la pizzería.

## Reproducir
```bash
pip install fastapi uvicorn httpx pytest
PYTHONPATH=. python -m pytest -v demo_funcional/tests --junitxml=demo-mvp-results.xml
PYTHONPATH=. uvicorn demo_funcional.app:app --host 127.0.0.1 --port 8765
```

Abrir `http://127.0.0.1:8765`. Usar los usuarios de prueba `admin`, `cajero` y `cocina` (clave de demo `demo123`).

## Pruebas automatizadas (27 casos)
- Salud del servidor y UI servida
- Credenciales y acceso no autenticado
- Catálogo e inventario inicial
- Creación transaccional de pedido y consumo de receta
- Kardex con referencia de pedido
- Stock insuficiente y rollback sin efectos secundarios
- Errores 404 para productos inexistentes
- RBAC: cocina sin permiso de venta, cajero sin permiso de estados
- Ciclo estricto de estados y bloqueo de saltos
- Pago único (bloqueo de doble cobro)
- Reporte solo de pagos confirmados
- RBAC de reportes, reabastecimiento y bitácora
- Movimientos positivos por reabastecimiento
- Ranking heurístico explicado sin afirmar ML
- Rechazo de cantidades no válidas y pedidos inexistentes
- Métricas de pedidos abiertos/cerrados

## Limitaciones y buenas prácticas
- No son pruebas de la solución principal React/PostgreSQL del repositorio.
- No se ensayó uso empresarial con trabajadores ni facturación SUNAT.
- Autenticación/contraseñas demo NO son aptas para producción.
- No se emitieron actas ni conformidades empresariales.
- Se documenta visualmente un MVP demostrable y auditable, no un producto instalado en la pizzería.
