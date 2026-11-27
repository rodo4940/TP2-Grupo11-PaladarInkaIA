# Operación diaria y preparación de lanzamiento
## El Paladar del Inka · v6

**Naturaleza del documento:** instrucciones de operación de la versión técnica; no equivale a un acta empresarial ni certificación tributaria.

### 1. Flujo probado de ventas

1. El personal de caja inicia sesión con rol `cashier` o `admin`.
2. Desde **Ventas / POS** selecciona un producto activo con receta; el servidor verifica existencias y descuenta ingredientes de forma transaccional. Si falta stock, el pedido no se crea.
3. Registra el medio de pago mediante la API. Un pedido solo admite un pago confirmado; una segunda solicitud de pago se rechaza.
4. En **Caja y comprobantes** aparece el ticket interno `INT-XXXXXX`, asociado a un `Payment.id` real, sin constituir comprobante electrónico SUNAT.
5. En **Resumen diario de caja** elige una fecha en zona `America/Lima`. El servidor convierte los límites del día a UTC para evitar contabilizar pagos en la fecha equivocada cerca de medianoche.
6. Compara los importes registrados por **Efectivo, Tarjeta, Yape y Plin** con vouchers y efectivo físico. Si corresponde, introduce el efectivo contado: la interfaz muestra la diferencia solo en memoria.
7. Exporta CSV si necesita una conciliación auxiliar. El CSV utiliza solamente identificadores internos, medios conocidos e importes, sin nombres arbitrarios que puedan activar fórmulas de hojas de cálculo.
8. La persona responsable debe **revisar y firmar fuera del sistema** el arqueo. Esta versión no registra ni aprueba un cierre contable definitivo, ni gestiona devoluciones financieras.

### 2. Fuente y semántica de los importes

| Campo | Origen | Significado |
|---|---|---|
| `gross_payments_cents` | Suma de `Payment.amount_cents` | Pagos brutos registrados durante el día local, en céntimos |
| `by_method` | Mismos registros `Payment` | Conteo e importe por método |
| `entries` | `Payment → Order → OrderItem` | Lista inmutable de constancias y detalles asociados |
| `cash-physical-input` | Solo frontend | Efectivo digitado para comparación; **no** se guarda |
| `reconciliation_state` | Valor fijo | `PENDIENTE_VERIFICACION_MANUAL`; nunca `APROBADO` |
| `fiscal_status` | Valor fijo | `NO_EMITIDO_SUNAT` |

El resumen no representa utilidad, ingresos netos después de devoluciones, comprobantes electrónicos, impuestos ni cierre fiscal. El cobro efectivo debe verificarse con el proveedor de pagos o con caja.

### 3. Roles y seguridad

- `admin` y `cashier`: pueden leer resúmenes y tickets.
- `kitchen`: no puede acceder a la caja ni al asistente por API, aunque conozca la URL.
- Anónimos: `401`; roles no autorizados: `403`; fechas inválidas: `422`.
- El asistente externo no recibe el texto libre de la pregunta. Un clasificador de intención lo sustituye por preguntas estándares de negocio antes de enviarlo, junto con métricas agregadas. No hay herramientas para modificar datos mediante IA.
- Las imágenes del menú son fotografías referenciales; deben sustituirse por imágenes autorizadas del negocio antes de publicarlo.

### 4. Evidencias QA regenerables

El flujo de GitHub Actions `Extended Full-System UI Evidence` debe ejecutar, sobre PostgreSQL de pruebas y React, las suites acumuladas y recoger **252 PNG** desde Chromium/Playwright. Los últimos 12 archivos corresponden a cuatro tamaños (320, 390, 768 y 1440 píxeles), tres estados por cada uno: resumen diario, fecha histórica sin pagos y comparación con efectivo. Los PNG deben conservar el ancho exacto de su viewport y carecer de overflow horizontal de documento.

Se publican además:

- `caja-v6-results.json`: dimensiones y validaciones de cada captura.
- `GALERIA_252.html`: galería revisable.
- `MANIFIESTO_SHA256_252.csv`: hash individual para auditar integridad.
- `e2e-results.json`: trazabilidad ordenada del lote.
- Resultados de compilación TypeScript, pruebas `pytest`, accesibilidad axe-core, análisis de dependencias y arranque Docker.

Los indicadores de calidad deben consultarse en el **workflow del commit exacto**. Una ejecución previa verde no acredita automáticamente cambios posteriores.

### 5. Control de lanzamiento (go/no-go)

| Verificación | Condición antes de operar con clientes reales |
|---|---|
| Pruebas técnicas | Workflows CI verdes para el commit a desplegar |
| Inventario inicial y precios | Aprobados por la pizzería; migración auditada |
| Protección de datos | Contrato, información y permisos adecuados para el tratamiento |
| Facturación electrónica | Integración autorizada y probada según obligaciones SUNAT; ticket INT insuficiente |
| Caja y devoluciones | Procedimiento real de reembolso, conciliación, turnos y arqueo aprobado |
| Seguridad | MFA o controles equivalentes, protección anti-fuerza bruta, gestión de secretos, prueba externa |
| Continuidad | Copia externa cifrada, restauración ensayada, RPO/RTO y responsables |
| Capacidad | Pruebas de carga en la infraestructura final y monitoreo |
| Fotografías y marca | Activos autorizados y contenidos aprobados |
| UAT | Casos reales ejecutados y conformidad del establecimiento firmada |

**Decisión de esta versión:** técnicamente candidata a piloto; **NO GO comercial** hasta que la pizzería valide y firme la lista de control, y se resuelvan los bloqueos de seguridad/tributación. Este dictamen no puede sustituirse por capturas ni por un informe académico.
