# Experiencia premium v3 — calidad del diseño, operación y evidencia responsive

**Producto:** El Paladar del Inka | Universidad Continental · Taller de Proyectos 2  
**Rama del trabajo:** `feature/paladar-premium-v3-responsive-release`  
**Base:** `release/paladar-inka-v1-piloto`  
**Objetivo de revisión:** candidato técnico de interfaz, no autorización de apertura comercial.

## 1. Diagnóstico previo y decisiones

Se conservó React 19, TypeScript, Vite, FastAPI, SQLAlchemy/PostgreSQL 17 y el sistema de diseño editorial preexistente. No se reescribieron los módulos de venta e inventario que ya contaban con pruebas. Se corrigieron tres puntos concretos:

1. **Estado API engañoso:** la cabecera mostraba “conectada” sin atender a fallos de sincronización. Ahora diferencia comprobación, resultado satisfactorio y error; muestra la última hora de consulta confirmada.
2. **Accesos no filtrados:** los botones del dashboard podían mostrar vistas de otras funciones. El nuevo cockpit y los botones del banner respetan los roles; la API sigue siendo el control real de autorización.
3. **Uso en móviles:** el cajero necesitaba desplazarse mucho para alcanzar el carrito. Se añadió acceso directo contextual y se revisaron tamaños táctiles, anchos y navegación colapsada.

El objetivo es ofrecer una experiencia **coherente, legible y eficiente**, no añadir efectos decorativos ajenos al proceso del negocio.

## 2. Sistema visual

| Eje | Criterio de diseño | Implementación |
|---|---|---|
| Identidad | Pizzería artesanal contemporánea | Verde horno, crema, acentos dorados y carmín |
| Estructura | Jerarquía y consistencia | Sidebar por roles, cabecera, KPI, secciones y tarjetas |
| Lectura | Contraste y escalas tipográficas | Titulares concisos, tabla con jerarquía, unidades y formato PEN |
| Fotografía | Apetito visual sin atribuciones falsas | Fotografías de referencia Unsplash; placeholders visuales si falla el recurso |
| Datos | No mostrar indicadores inventados | React consume los endpoints de FastAPI; agregados del cockpit derivados de pedidos |
| Acciones | Cada botón tiene un propósito | Accesos rápidos, carrito, tareas de cocina y enlaces de detalle |
| Inclusión | Interacción con teclado, lectura asistida | Skip link, foco visible, modal con foco contenido, `aria-current`, `aria-live` y `Escape` |
| Movilidad | Sin desbordamiento de página | Estilos específicos de teléfono, tableta y escritorio; tablas con desplazamiento interno |

Se respetan las licencias de las fotografías externas: https://unsplash.com/license. Las imágenes **no son fotografías certificadas de los platos**. Para la publicación definitiva deben obtenerse fotografías autorizadas del establecimiento y alojarse en un medio controlado.

## 3. Comportamiento funcional actualizado

**Panel general:** incluye estado de sincronización, KPI del servidor, distribución real de estados de pedidos, ratio de entregas sobre pedidos no cancelados, tareas pendientes visibles según rol, inventario, ranking de ventas y acceso a módulos.

**Ventas:** catálogo fotográfico, búsqueda, filtros, tarjetas táctiles, suma y resta, elección de atención (salón, recojo o referencia delivery), carrito con acceso móvil, confirmación de pedido y registro de cobro. El servidor recalcula el total y descuenta inventario conforme a las reglas de negocio existentes.

**Cocina:** tablero de columnas y estados; no se alteró la lógica de transición. **Almacén:** inventario, mínimos, Kardex y exportaciones. **Clientes:** alta, edición e historial. **Administración:** usuarios, roles, recetas, reportes, bitácora y configuración.

**Ayuda:** el botón `Ayuda` explica la vista actual. Los atajos `Alt+1..4` respetan privilegios; `Escape` cierra ayuda y menú. El foco regresa al elemento que abrió la ayuda. Los datos se actualizan cada 60 segundos mientras la pestaña está visible; el botón `Actualizar` conserva la actualización manual. Esto **no equivale a WebSocket ni a sincronización instantánea**.

## 4. Matriz de evidencias 101–152

Se añaden **52 capturas reales** a las 100 previas: 13 estados (login, los 11 módulos y centro de ayuda) multiplicados por cuatro tamaños:

| Perfil | Viewport | Propósito |
|---|---|---|
| Teléfono compacto | 360 × 780 | Comprobar navegación y legibilidad al mínimo práctico |
| Teléfono estándar | 390 × 844 | Validar operación móvil frecuente |
| Tableta vertical | 768 × 1024 | Confirmar transición de paneles y navegación |
| Escritorio | 1440 × 900 | Evaluar densidad, legibilidad de tablas y uso simultáneo |

**Verificaciones de la suite:** inicio real de sesión, 11 módulos navegables por rol administrador, contenido operativo, panel nuevo, botón de carrito adaptable, apertura/cierre de ayuda, `aria-current`, ausencia de desbordamiento horizontal del documento, atajos en escritorio, 152 PNG únicos, generación SHA-256 y reporte JSON de métricas. El movimiento reducido está habilitado durante las capturas para estabilizar la evidencia.

El artefacto se denomina `paladar-v3-responsive-152-evidence`. Incluye `GALERIA_152.html`, `MANIFIESTO_SHA256_152.csv`, `REPORTE_EVIDENCIAS_152.json`, `responsive-matrix-results.json`, los originales PNG y logs. El workflow que lo produce es `Extended Full-System UI Evidence` y **solo se acepta el paquete generado por una ejecución verde del último commit**.

## 5. Verificación de calidad antes de aprobar el PR

- Backend: conservar las 51 pruebas existentes.
- Seguridad HTTP: comprobar **27 controles con cero fallos** en servidor de test.
- Frontend: `npm ci`, `tsc -b` y `vite build`.
- Instalación limpia: validación `Fresh Clone Local Start` mediante Docker Compose.
- Funcionalidad real: ejecutar el escenario completo de Playwright previo y las 52 nuevas capturas responsive.
- Revisión humana: inspección de pantallas, lectura en teléfono, flujos de cajero/cocina, contraste y tipografías.

Los resultados deben leerse desde las ejecuciones del commit correspondiente; los resultados de una rama o ejecución anterior **no sustituyen** a la aprobación de los cambios nuevos.

## 6. Trazabilidad con el informe del curso

Los cambios de interfaz, roles, indicadores, pruebas y commits sustentan principalmente **Capítulo V, sección 5.2, Anexo 13** (diseño, desarrollo y verificación), así como el **Anexo 07** (manuales y documentación técnica). Las evidencias de coordinación se deben reflejar en el Anexo 02 cuando existan actas auténticas. El material fotográfico tiene atribución de procedencia/licencia en esta ficha, pero no implica aprobación institucional o comercial.

## 7. Restricciones de salida comercial

La aplicación es **candidato de piloto técnico**, no sistema autorizado para operar ventas reales. Antes del lanzamiento con clientes reales hace falta: UAT y firmas del establecimiento, comprobantes y pasarela/fiscalidad según corresponda, pruebas de carga y seguridad sobre la infraestructura de destino, backups con restauración ensayada, revisión de privacidad y políticas de conservación, imágenes propias aprobadas y monitoreo operacional. No se atribuye aprendizaje automático entrenado a las reglas heurísticas actuales.

**Criterio de aceptación:** UI y QA de laboratorio completos + evidencias verificables = listo para presentación/demostración técnica. **No** implica lanzamiento comercial automático.