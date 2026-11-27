# Sistema de gestión — El Paladar del Inka
## Arquitectura, experiencia, caja documental y analítica — v5

**Universidad Continental · Taller de Proyectos 2 · Revisión técnica: 27/11/2026**  
**Naturaleza:** piloto académico funcional conectado a PostgreSQL, pendiente de validación empresarial y autorización tributaria para uso comercial.

### 1. Principios del proyecto

El sistema conserva la secuencia transaccional: **registro del pedido → reserva/consumo de receta → comandas de cocina → pago único → ticket interno → reportes y análisis**. El frontend no inventa cifras ni ejecuta reglas de stock. La aplicación cliente consulta una API FastAPI autenticada con JWT; PostgreSQL persiste operaciones, relaciones y movimientos. Los permisos de usuario se verifican en el servidor incluso si se manipula manualmente la interfaz.

La identidad visual propone una interpretación gráfica original del sol y de geometrías andinas, integrada con la gastronomía artesanal. No pretende representar una figura histórica oficial ni un símbolo patrimonial registrado. El isotipo SVG mantiene nitidez en pantallas 320–1440 px, impresión y dispositivos de alta densidad. La fotografía de comida se usa solo como **imagen referencial** del piloto; el restaurante debe aprobar imágenes propias de su carta antes de abrir al público.

### 2. Capas técnicas

| Componente | Responsabilidad | Implementación |
|---|---|---|
| React/TypeScript | Interfaz, navegación por rol, validación visual, estados de carga/error, impresiones | `frontend/src/App.tsx` y `frontend/src/components/` |
| Tema gráfico | Identidad, accesibilidad, formularios, tarjetas y respuesta a resolución | `frontend/src/inka-v5.css` |
| Identidad original | Sol geométrico y gastronomía como SVG vectorial | `frontend/src/components/InkaBrand.tsx`; `frontend/public/branding/inka-mark.svg` |
| Cliente HTTP | API tipada, errores y sesión bearer | `frontend/src/services/api.ts` |
| FastAPI | Contratos HTTP, roles, validación y transacciones | `backend/app/domain/routes.py`, `billing_ai.py` |
| PostgreSQL/SQLAlchemy | Pedido, recetas, ventas, pagos, clientes y Kardex | `backend/app/domain/models.py` |
| Alembic | Versionado y actualización de tablas | `backend/alembic/versions/` |
| pytest | Integración HTTP y lógica de negocio con DB aislada | `backend/tests/test_business.py` |
| Playwright/Chromium | Navegación real y capturas reproducibles | `scripts/e2e_browser.py`, `e2e_responsive_matrix.py`, `e2e_studio_v4.py`, `e2e_inka_v5.py` |
| GitHub Actions | Compilación, pruebas, auditoría y distribución de evidencias | `.github/workflows/` |

### 3. Componentes y roles

| Vista | Administrador | Caja | Cocina | Observación |
|---|---:|---:|---:|---|
| Panel general | Sí | Sí | Sí | KPI obtenidos del servidor |
| Ventas y POS | Sí | Sí | No | El servidor recalcula importes y valida stock |
| Caja y comprobantes | Sí | Sí | No | Consulta y reimpresión de tickets internos |
| Pedidos | Sí | Sí | Sí | Detalle y estado trazables; cambios según rol |
| Cocina | Sí | No | Sí | Transiciones permitidas por FastAPI |
| Inventario y Kardex | Sí | Lectura | Lectura | Ajustes solo administración |
| Productos y recetas | Sí | Lectura | No | Edición solo administración |
| Clientes | Sí | Sí | No | Acceso restringido por backend |
| Reportes y analítica | Sí | Sí | No | Basados en pagos y registros agregados |
| Usuarios y auditoría | Sí | No | No | No es una restricción solo de CSS |
| Configuración | Sí | Sí | Sí | Contraseña propia, entorno y sesión |

### 4. Cobro, caja y comprobantes

**Fuente de verdad:** tabla `payments` vinculada unívocamente con `orders`. Se mantiene una regla de un pago confirmado por pedido, con bloqueo de fila y restricción de unicidad. El total del cobro se valida contra el total del pedido, nunca contra el cálculo del navegador.

**Nuevas rutas:**
- `GET /api/v1/billing/ledger?limit=100`: resumen y últimos cobros.
- `GET /api/v1/billing/ledger/{payment_id}`: detalle de una constancia individual.
- `GET /api/v1/orders/{order_id}/receipt`: ticket interno previo compatible.

Cada constancia se identifica con `INT-######` a partir del ID persistido de pago y tiene estado `NO_EMITIDO_SUNAT`. Incluye fecha localizada en `America/Lima`, pedido, cliente registrado o consumidor final, líneas, unidades, precios históricos, medio de pago y total. No se recalcula el impuesto ni se asigna número fiscal. Reimprimir no crea una venta, no modifica el stock y no duplica el pago.

**La función NO emite facturas o boletas SUNAT.** Para habilitar emisión tributaria real son necesarios, como mínimo, el RUC válido y régimen aplicable del establecimiento, identificación de receptor según comprobante, configuración de emisor SEE/OSE/PSE, certificados y formatos electrónicos establecidos, firma/validación, CDR, anulación y contingencias. No se debe inventar una serie `F001`/`B001` ni mostrar `Aceptado SUNAT` sin integración efectiva. Referencias oficiales: https://cpe.sunat.gob.pe/ y https://www.gob.pe/25681-sistema-de-emision-electronica-see-del-contribuyente .

### 5. Funcionamiento de la analítica y del asistente

El módulo no se limita a mostrar gráficos: permite preguntar en lenguaje natural por cuatro categorías concretas:

1. **Caja:** ventas de hoy y día anterior con zona horaria de Lima, a partir de `Payment`.
2. **Inventario:** insumos en `stock <= minimum_stock`; recomendación informativa de revisión y reposición.
3. **Pedidos/cocina:** pedidos activos y su distribución entre pendientes, en preparación y listos.
4. **Menú:** popularidad por cantidades de productos en pedidos cobrados; no inferencia estadística de demanda.

La ruta `GET /api/v1/ai/business-context` devuelve métricas agregadas, y `POST /api/v1/ai/ask` acepta una pregunta entre 5 y 500 caracteres, con JWT de caja/administración. **Nunca ejecuta acciones** sobre clientes, órdenes, usuarios o inventario.

#### Dos modos de respuesta

**Por defecto: `reglas_explicables_locales`.** No exige Internet ni claves, devuelve datos medidos y criterios identificables en el campo `basis`. Es una capa de analítica asistida, no un LLM entrenado.

**Opcional: `modelo_externo_configurado`.** Solo si un administrador define `AI_API_KEY` y `AI_MODEL` en el entorno del backend. Se usa la API Responses del proveedor con `store: false`, un límite de salida y timeout. El servidor construye contexto con cifras agregadas; no transmite nombres de clientes, teléfonos, contraseñas ni JWT. Las preguntas no pueden modificar instrucciones de sistema ni activar herramientas. Si el proveedor externo falla, la respuesta vuelve al mecanismo local.

**Limitación:** las respuestas son recomendaciones para una persona responsable, no pronósticos validados ni acciones automáticas. El resumen de demanda previo usa media móvil ponderada y no debe confundirse con un modelo de aprendizaje automático supervisado.

#### Ejemplo de trazabilidad

Consulta: «¿Qué ingredientes debo reponer?»  
Origen: filas `ingredients.stock`, `ingredients.minimum_stock` y `unit`.  
Lógica: seleccionar insumos con existencias por debajo o iguales al mínimo.  
Resultado: enumeración de los insumos observados y sugerencia de revisión de Kardex.  
Restricción: no se generan solicitudes de compra automáticamente.  
Prueba: `test_business_assistant_stock_risks_use_real_thresholds`.

### 6. Imágenes y rendimiento visual

- Identidad: SVG local vectorial para no depender de resolución de imagen.
- Hero de cocina: fotografía editorial referencial de Unsplash cargada mediante CDN con 1800 px; si la red falla, cambia a `/illustrations/pizza-artisan.svg` local.
- Fichas de pizza: URL referencial por SKU; evita presentar la imagen de una pizza como la de una bebida.
- Tarjetas e interfaces: imágenes `object-fit: cover`, contenedores con proporciones y controles de carga.
- Referencia de licencia de Unsplash: https://unsplash.com/license . No implica autorización para utilizar identidades o marcas visibles de terceros.

### 7. Pruebas y criterios de aceptación

**Backend:** autenticación, roles, stock atómico, cancelaciones, pago único, ticket y restricciones; ahora incluye ledger, validación de número `INT`, prohibición de acceder desde cocina, contexto agregado, respuestas sobre insumos y ausencia de transacciones en consultas. Las pruebas con SQLite en memoria verifican lógica HTTP, y la E2E comprueba PostgreSQL 17 como servidor real.

**Frontend:** `npm run build` con TypeScript, Vite, escáner de dependencia `npm audit` y evaluación inicial de WCAG 2.1 AA mediante axe-core. La ausencia de violaciones severas automatizadas **no** certifica accesibilidad universal.

**Evidencia visual:** el workflow ejecuta la suite anterior de 200 PNG y añade 40 capturas en cinco resoluciones (320, 390, 768, 1280 y 1440 px). Cada estado comprueba encabezados, contenedores, imagen cargada y ancho del PNG idéntico a la anchura real de viewport. Incluye login, panel, POS, caja y filtros, ticket y dos estados del asistente. El ZIP se acompaña de galería HTML, informe, manifiesto SHA-256 y logs originales. La expectativa de 240 capturas debe corroborarse mediante workflow **verde** y artefacto publicado.

**Repetibilidad local:** ejecutar `scripts/start.sh` o `scripts/start.ps1` según plataforma, usar .env propio, migrar con Alembic, levantar frontend y backend; nunca subir secretos o base de datos real al repositorio.

### 8. Pendientes externos reales

- Aprobación formal de branding, fotografías y carta por el establecimiento.
- Configuración de un emisor de comprobantes electrónicos admitido por SUNAT, pruebas de certificación y credenciales del contribuyente.
- Pruebas de aceptación firmadas por usuarios del restaurante (UAT).
- Política de datos personales, backups verificados con restauración, monitoreo y endurecimiento de infraestructura final.
- Clave de API externa y presupuesto de consumo si se quiere un modelo generativo. No hay modelo externo activo por defecto.

**Dictamen responsable:** cuando CI esté verde, se puede afirmar que la compilación, la interfaz y los flujos ensayados funcionan en laboratorio. La autorización para ventas comerciales y comprobantes tributarios requiere validación independiente.
