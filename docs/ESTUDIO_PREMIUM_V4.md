# Diseño y validación visual — Studio v4

**Proyecto:** El Paladar del Inka | Taller de Proyectos 2 · Universidad Continental  
**Rama de desarrollo:** `feature/premium-v4-design-system-200-evidencias`  
**Base:** `release/paladar-inka-v1-piloto`  
**Naturaleza:** versión candidata de presentación/piloto, no autorización de venta comercial.

## 1. Objetivos concretos

Consolidar la calidad visual de todo el ERP sin alterar los contratos HTTP ya probados:

1. Diseñar una **identidad propia** coherente con una pizzería artesanal, no una colección de estilos inconexos.
2. Aplicar la misma jerarquía a módulos, formularios, tablas, estados, acciones, datos y mensajes.
3. Reducir los desplazamientos móviles con navegación inferior por rol y acceso directo al carrito.
4. No inventar estados de salud ni métricas: mostrar lo que efectivamente informa FastAPI.
5. Mantener imágenes visibles aunque falle el CDN fotográfico.
6. Sustentar cada afirmación de QA en archivos generados por navegador con nombres, dimensiones y SHA-256.

## 2. Componentes de diseño implementados

| Componente o capa | Propósito | Archivo |
|---|---|---|
| `styles.css` | Estilos funcionales y layouts base existentes | `frontend/src/styles.css` |
| `premium.css` | Tema editorial previo, fotografía y tarjetas de productos | `frontend/src/premium.css` |
| `experience.css` | Cockpit, modal de ayuda, microinteracciones y adaptación | `frontend/src/experience.css` |
| `studio.css` | Consolida encabezados, diseño responsive y tratamientos de todas las vistas | `frontend/src/studio.css` |
| `SectionArtwork` | Arte vectorial local por módulo con licencia propia | `frontend/src/components/SectionArtwork.tsx` |
| `MobileDock` | Navegación táctil y consciente del rol | `frontend/src/components/MobileDock.tsx` |
| `OperationsOverview` | Resumen agregado de pedidos reales de la API | `frontend/src/components/OperationsOverview.tsx` |
| `SupportCenter` | Ayuda contextual con navegación accesible | `frontend/src/components/SupportCenter.tsx` |
| `pizza-artisan.svg` | Respaldo de imágenes independiente de Unsplash | `frontend/public/illustrations/pizza-artisan.svg` |

Los recursos SVG de `SectionArtwork` son ilustraciones propias; su función es decorativa y se ocultan a tecnologías asistivas por `aria-hidden`. Las imágenes del catálogo provenientes de Unsplash **son referencias genéricas**, no fotos reales aprobadas del establecimiento. Licencia general del proveedor: https://unsplash.com/license.

## 3. Consistencia por módulo

| Área | Elementos reforzados |
|---|---|
| Acceso | Diseño editorial, credenciales claras, enfoque y arte local de respaldo |
| Panel general | Banner, indicadores, historial, alertas, cockpit y acciones por rol |
| Punto de venta | Tarjetas fotográficas, categorías, precios PEN y carrito persistente en la vista |
| Pedidos | Encabezado propio, filtros, estados, tabla, detalles y seguimiento |
| Cocina | Identidad cálida, comandas por columna y botones de transición destacados |
| Inventario | Encabezado de almacén, alertas, controles de stock y Kardex legible |
| Productos y recetas | Catálogo con miniaturas, formularios y disponibilidad |
| Clientes | Registro, búsqueda, historial y fichas |
| Reportes | Indicadores financieros, distribución, exportación CSV y gráficos |
| Analítica | Recomendaciones explicables y pronóstico etiquetado como orientativo |
| Usuarios | Roles, estado de cuentas y auditoría |
| Configuración | Salud real de API, sesión y cambio de contraseña, en orden de lectura |

El **backend valida los permisos**; ocultar acciones no reemplaza la autorización. Los estados de conexión, KPI, operaciones y precios corresponden al servicio conectado. Si falla la consulta, se señala el fallo y se ofrece un botón de reintento sin falsear el estado de la API.

## 4. Responsive y accesibilidad

Puntos de quiebre de diseño: 350, 420, 700, 880, 1020, 1280 y 1500 píxeles. En móvil se incorpora un `MobileDock` para las operaciones más frecuentes, respetando restricciones de `admin`, `cashier` y `kitchen`; el menú lateral conserva acceso a los módulos secundarios. Se mantienen accesibilidad de teclado, anillo de foco, salto a contenido, etiquetas semánticas, `Escape` en ayuda, movimiento reducido y tablas desplazables internamente.

**Criterio de QA:** el documento raíz no debe tener overflow horizontal. Las tablas anchas pueden desplazarse en su contenedor específico para conservar información sin comprimir columnas. La suite no reemplaza la evaluación manual de accesibilidad y usabilidad.

## 5. Evidencia incremental

| Ciclo | Rango | Criterio |
|---|---|---|
| Base funcional y escenarios de operación | 001–090 | Interacciones reales sobre sistema de QA |
| UI premium v2 | 091–100 | Fotografías e interacciones visuales |
| Responsive v3 | 101–152 | 360, 390, 768 y 1440 px; módulos y ayuda |
| Studio v4 | 153–200 | 320, 414, 820 y 1366 px; login y 11 módulos |

Los **48 nuevos PNG** provienen de `scripts/e2e_studio_v4.py`. Además de capturar, verifican: acceso real, indicadores de API, navegación móvil por rol, once módulos, ilustración específica en encabezados, ausencia de overflow horizontal y errores JavaScript, carga correcta de imágenes en el POS, ayuda accesible, atajos de escritorio, bloqueo del POS para el rol cocina y representación con SVG local al bloquear el servidor remoto de fotografías.

La secuencia y sumatoria es: `scripts/e2e_browser.py` (100), `scripts/e2e_responsive_matrix.py` (+52) y `scripts/e2e_studio_v4.py` (+48) = **200 evidencias previstas**. La aprobación se verifica **solo** en un job verde del commit final, nunca a partir de una captura modificada o un conteo sin ejecución.

### Entregables del workflow

El flujo `Extended Full-System UI Evidence` debe producir el artefacto `paladar-studio-v4-200-real-screens` con los siguientes archivos:

- `e2e/evidencias/` con 200 PNG originales.
- `GALERIA_200.html` para buscar y revisar capturas.
- `MANIFIESTO_SHA256_200.csv` con hash y tamaño por archivo.
- `REPORTE_EVIDENCIAS_200.json`, `studio-v4-results.json`, `responsive-matrix-results.json` y `security-smoke-results.json`.
- Logs del frontend/backend del entorno QA.

**Validaciones adicionales:** 51 pruebas de backend, build de React 19/TypeScript, migración y arranque Docker, Bandit, npm audit y escaneo automatizado preliminar axe-core/WCAG. Se debe documentar cualquier fallo y no fusionar cambios hasta obtener aprobaciones.

## 6. Límites comerciales

Un resultado verde **prueba la operación en laboratorio**, no una autorización para cobrar o gestionar datos personales reales. Siguen requiriéndose: UAT con personal del restaurante y actas firmadas, fotografías propias aprobadas por SKU, cumplimiento SUNAT para comprobantes, política de datos personales, pruebas de rendimiento sobre el servidor final, backups restaurados con éxito y monitoreo de operación real.

La inteligencia de la aplicación sigue siendo heurística y descriptiva; no debe presentarse como aprendizaje automático entrenado con históricos reales.

## 7. Matriz de trazabilidad del curso

- **Capítulo V / Anexo 13:** diseño visual, arquitectura funcional, log de cambios, capturas de módulos, pruebas E2E y adaptabilidad.
- **Capítulo V / Anexo 12:** requerimientos y restricciones, incluyendo integridad, economía, infraestructura y seguridad.
- **Anexo 07:** manual de uso, reglas operativas de cada rol y decisiones UI.
- **Capítulo IV / Anexo 10:** decisiones ligeras de UX y reducción de dependencias por SVG locales; no reclamar mediciones energéticas si no hay datos.
- **Anexos 02, 08 y 09:** solo actas colaborativas, exposición y coevaluación realmente realizadas.

El informe de cierre debe enlazar la ejecución de CI del commit exacto utilizado en la demostración.
