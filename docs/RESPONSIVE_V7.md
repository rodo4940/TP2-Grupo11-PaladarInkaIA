# Diseño adaptable v7 — El Paladar del Inka

**Alcance:** las doce interfaces operativas y el inicio de sesión de React, conectadas con FastAPI/PostgreSQL.  
**Validación:** Chromium/Playwright en GitHub Actions sobre registros ficticios y la misma compilación React/TypeScript.

## Decisiones de diseño

- **Móvil (320–430 px):** tarjetas con etiquetas para tablas de pedidos, último historial del dashboard, stock, Kardex, productos, clientes, historial individual, usuarios y bitácora. Se priorizan nombre, estado, total y acciones. Navegación inferior con área segura y objetivos táctiles mayores o iguales a 42×44 px.
- **Tableta (768–880 px):** navegación lateral temporal, contenido de ancho fluido, dos columnas cuando son legibles y tablas accesibles con scroll dentro de su panel.
- **Portátil (1024 px):** navegación fija y paneles en columnas sin depender de anchuras rígidas.
- **Escritorio (1440 px y superior):** composición fluida, márgenes proporcionales, paneles y controles alineados.
- **Accesibilidad:** drawer móvil con foco inicial en Cerrar, retención de Tab en el menú, restauración del foco y scroll de fondo bloqueado; acciones con `focus-visible`, semántica de tablas conservada en HTML, encabezados de celda reproducidos con `data-label`.
- **Fotografías:** se conservan imágenes gastronómicas referenciales y logotipo SVG original; su uso final queda sujeto a autorización del establecimiento.

## Matriz de evidencia real en navegador

| Resolución (px) | Ejecución | Pantallas |
|---|---|---|
| 320 × 720 | Teléfono compacto | 13 |
| 360 × 780 | Teléfono | 13 |
| 390 × 844 | Teléfono | 13 |
| 430 × 932 | Teléfono amplio | 13 |
| 768 × 1024 | Tableta | 13 |
| 1024 × 768 | Portátil | 13 |
| 1440 × 900 | Escritorio | 13 |
| **Total** | **7 resoluciones** | **91 capturas** |

Las 13 pantallas por resolución son: Acceso, Panel general, Ventas/POS, Pedidos, Cocina, Inventario/Kardex, Productos y recetas, Clientes, Reportes de ventas, Analítica, Usuarios y roles, Configuración y Caja y comprobantes.

El flujo `responsive-v7.yml` prueba que cada PNG tenga exactamente la resolución elegida; no haya desplazamiento horizontal a nivel de documento, el dock se muestre únicamente cuando corresponde, los botones del dock en móvil respeten su tamaño táctil, existan las tarjetas con etiquetas y se pueda abrir/cerrar el menú lateral con bloqueo de scroll. Los errores JavaScript detienen el trabajo. Conserva:

- `e2e/adaptive-v7/RESULTADOS_RESPONSIVE_V7.json`
- `e2e/adaptive-v7/GALERIA_RESPONSIVE_V7.html`
- 91 PNG con SHA-256 individual
- bitácoras FastAPI y Vite en el archivo de GitHub Actions.

**Ejecución validada en la rama antes de fusionar:** [Responsive v7, 91 capturas y 7 resoluciones](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/actions/runs/45923342653).

**Revisión de integración:** [PR #19](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/pull/19).

## Alcance de la garantía

La auditoría es una prueba automática de laboratorio sobre el navegador Chromium. No sustituye controles manuales con dispositivos físicos, revisión de lector de pantalla, contrastes con otros motores de navegador, aceptación del restaurante o autorización para facturar por SUNAT. El sistema sigue siendo un **piloto técnico listo para demostración**, no una certificación de operación comercial.
