# Paladar Inka AI — rediseño visual, cobertura funcional y calidad

**Referencia:** consolidado del Taller de Proyectos 2 y prototipos de la pizzería El Paladar del Inka. **Aplicación verificada:** React + TypeScript, FastAPI, SQLAlchemy/Alembic y PostgreSQL 17. **Alcance:** piloto técnico reproducible con datos de prueba. No equivale al lanzamiento empresarial.

## Principios y sistema de diseño
- Referencia visual de prototipo: navegación lateral **azul marino**, superficies blancas, acciones de venta **rojas**, tarjetas de pizzas y cocina diferenciada por estado.
- Ajustes realizados directamente en `frontend/src/App.tsx` y `frontend/src/styles.css`: acceso, dashboard, buscadores, módulos, filtros, POS, reportes, tablas, tarjetas, panel de ventas, exportación CSV, diseño móvil y lectura táctil.
- Estados siempre se consultan al backend. No se crean cifras de facturación como decoración.
- Se mantiene un único backend y una única aplicación web; el prototipo desconectado anterior permanece solo en el historial.
- Accesibilidad: labels para controles, textos contrastados, responsive. Auditoría automatizada con axe-core, que no sustituye validación manual WCAG.
- En móvil, la experiencia es **web responsive** en navegador; no se afirma que sea una aplicación Android/iOS nativa ni que soporte trabajo offline.

## Funcionalidades y evidencia
| Flujo | Función | Prueba verificada |
|---|---|---|
| Acceso | JWT, Argon2, roles admin/caja/cocina, revocación de sesiones | Backend pytest, HTTP 401/403, Chromium |
| Panel | Indicadores consultados a API, alertas y navegación rápida | Chromium React + PostgreSQL |
| Ventas | Búsqueda, filtros, cantidades, pedido salón/recojo/delivery (etiqueta), transacción de insumos | Playwright + HTTP POS/stock |
| Cocina | Estados pendiente, preparando, listo, entregado y control de transición | Backend + recorrido completo Chromium |
| Inventario | Insumos, reposiciones, ajustes, Kardex, reversión al cancelar | Pytest + E2E + exportación CSV |
| Catálogo | Altas, edición, desactivación, receta por producto y stock de ingredientes | Pytest + Chromium |
| Clientes | Registro, búsqueda, historial vinculado al pedido | API + Chromium |
| Reportes | Ventas registradas, distribución por pagos y CSV | API + exportación navegador |
| Inteligencia operativa | Ranking descriptivo y medias móviles explicables | API + pantalla de analítica |
| Administración | Usuarios, roles, desactivación, cambio de contraseña, bitácora | Pytest + HTTP 403 + Chromium |
| Diseño responsive | Menú lateral móvil, POS móvil y tablet | Capturas en viewports 390 y 820 píxeles |

**Nota:** un pedido etiquetado «Delivery» no constituye seguimiento GPS ni integración con repartidores; un pago marcado como Yape/Tarjeta es registro administrativo, no autorización de una pasarela. El ticket interno no es un comprobante tributario SUNAT. Las recomendaciones son heurísticas, no un modelo ML entrenado.

## Evidencia verificable de GitHub Actions
- `backend/tests/test_business.py` + `backend/tests/api/test_health.py`: **51 pruebas** ejecutadas en CI con condiciones especificadas; la suite de dominio usa SQLite aislado y la migración/health se valida con PostgreSQL.
- `.github/workflows/fullstack-ci.yml`: tests FastAPI, migraciones Alembic sobre PostgreSQL, `npm ci` y `npm run build`.
- `.github/workflows/first-run-smoke.yml`: instalación desde clon limpio, boot Docker, login y proceso de venta.
- `.github/workflows/e2e-full-coverage.yml`: 90 capturas originales desde Chromium con semillas ficticias y 27 controles HTTP de autorización/validación.
- `.github/workflows/security-accessibility.yml`: Bandit SAST, `npm audit` con umbral high, métricas de assets y axe-core en 10 vistas. Los informes JSON íntegros se conservan incluso cuando aparece un fallo. **No declarar OWASP/WCAG aprobado hasta ver la ejecución verde**.
- En cada captura se conserva la imagen PNG de Playwright y su manifiesto JSON. El ZIP del artefacto de GitHub Actions corresponde a un SHA exacto; no se alteran las capturas.

## Reproducción
```bash
git clone --branch release/paladar-inka-v1-piloto --single-branch https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA.git
cd TP2-Grupo11-PaladarInkaIA
bash scripts/start.sh
```

En Windows con Docker Desktop: ejecutar `INICIAR_WINDOWS.bat`. El primer arranque genera secretos locales en `.env` y datos ficticios de QA. Abrir `http://localhost:5173`. Los resultados son del **entorno local de desarrollo**, no de la instalación del cliente.

## Criterios reales pendientes de go-live
UAT empresarial firmado, dominio e infraestructura propia autorizada, evaluación y protección de datos personales, backups externos y restauración verificada, monitoreo real, revisión OWASP/DAST y pruebas de carga con límites acordados. Si el restaurante requiere documentos tributarios y pagos en línea, integrar SUNAT/proveedor autorizado y pasarela formal. No promocionar como software de IA predictiva sin un modelo y evaluación válidos. Detalle en `docs/RELEASE_READINESS.md` e issue #12.

## Guía académica
El capítulo de calidad del informe debe incluir los procedimientos y resultados reales disponibles (W3C/estructura, ISO/IEC 25010 como criterios de calidad, OWASP como referencia de riesgos, WCAG/axe como comprobación parcial) y la demostración funcional. Presentar anexos solo con información observada y sin fabricar aceptación de usuarios o dictámenes externos.
