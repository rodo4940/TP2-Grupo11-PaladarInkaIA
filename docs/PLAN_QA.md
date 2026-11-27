# Plan de calidad y trazabilidad — Paladar Inka AI

## Tipos de prueba

1. **Unitarias/integración de API:** pytest + TestClient + SQLAlchemy y SQLite temporal; se ejecutan en `backend/tests/test_business.py`.
2. **Integración PostgreSQL:** job CI `backend-tests` migra un servicio PostgreSQL 17 con Alembic y ejecuta el conjunto de tests (incluidos los tests existentes de salud).
3. **Frontend:** job CI `frontend-build` realiza `npm ci` y `npm run build` (TypeScript + Vite).
4. **Instalación desde cero:** workflow `first-run-smoke.yml` genera credenciales locales, construye contenedores, ejecuta migraciones y recorre API real con datos ficticios.
5. **Recorrido visual:** `e2e-ui-evidence.yml` automatiza Chromium contra React y PostgreSQL para producir capturas verificables.
6. **Pruebas de negocio en establecimiento:** requieren ejecución y aceptación de representante; NO están acreditadas aquí.

## Cobertura funcional

| Requisito | Endpoint / módulo | Evidencia automatizable |
|---|---|---|
| RF-01 Autenticación | `/auth/token`, `/auth/me` | Credenciales correctas e incorrectas; 401 sin token |
| RF-02 Roles | `/users`, `/orders`, `/customers` | 403 para actor sin permiso |
| RF-03 Catálogo | `/products` | Alta, SKU duplicado, producto sin receta |
| RF-04 Recetas | `/products/{id}/recipe` | Referencias válidas; sin duplicados |
| RF-05 Pedido | `/orders` | 201, importe de venta y validación de stock |
| RF-06 Inventario | `/ingredients`, Kardex | Descuento por receta, rollback por falta de stock |
| RF-07 Cocina | `/orders/{id}/status` | Transición válida/errónea y restricciones de rol |
| RF-08 Cancelación | `/orders/{id}/status` | Reposición de consumos previos; prohibido si ya se pagó |
| RF-09 Caja | `/orders/{id}/payment` | Importe exacto, 201 y rechazo de doble cobro |
| RF-10 Reportes | `/reports/sales` | Solo pagos confirmados en resultados |
| RF-11 Clientes | `/customers` | Creación y acceso por rol |
| RF-12 Inteligencia | `/recommendations`, `/ai/demand-forecast` | Método declarado heurístico y parámetros válidos |
| RF-13 Auditoría | `/audit` | Registro accesible solo a admin |

## Capturas con evidencia

Para cada captura incluir: pantalla, acción ejecutada, HTTP asociado, versión o SHA de commit, entorno, fecha y condición; nunca poner '100 % superado' si no existe reporte original de ejecución. Subir XML de pruebas con GitHub Actions y conservar enlace del run exitoso.

## Exclusiones explícitas

No se ejecutaron por este pipeline: pruebas OWASP ZAP reales, pruebas de carga JMeter con concurrencia empresarial, facturación SUNAT, entrenamiento de un modelo ML con datos del restaurante, autorización legal de producción ni UAT firmado por el dueño.

## Seguridad/ética

No usar DNI, teléfonos ni ventas reales de la pizzería sin autorización. Los registros de la semilla `app.seed` son ficticios. No insertar contraseñas reales ni tokens en Git.

## v8 — trazabilidad adicional, NO sustituye UAT
| Requisito | Implementación | Validación técnica |
|---|---|---|
| RF-14 Solicitar devolución | `POST /billing/refunds` | Pago existente, motivo, rol, unicidad |
| RF-15 Confirmar devolución | `POST /billing/refunds/{id}/confirm` | Admin distinto, referencia externa y segundo intento 409 |
| RF-16 Cuadrar arqueo | `POST /billing/closeouts` | Zona Perú, fondo inicial, conteo y diferencia persistente |
| RF-17 Aprobar arqueo | `POST /billing/closeouts/{id}/approve` | Admin independiente, registro auditado y bloqueo por datos obsoletos |
| RF-18 Analítica neta | Dashboard, reportes, asistente y heurística | Pagos originales y devoluciones separados; no incluir devoluciones confirmadas en unidades vendidas |

Suite: `backend/tests/test_reconciliation.py`. Ejecutar en el commit final del PR y verificar resultados reales del workflow. Todos los resultados empresariales de `docs/UAT_PILOTO_V8.md` permanecen SIN EJECUTAR hasta que el negocio participe.
