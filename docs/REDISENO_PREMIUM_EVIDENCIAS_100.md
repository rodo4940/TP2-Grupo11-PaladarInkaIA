# Rediseño premium y ampliación de QA a 100 evidencias

**Proyecto:** Sistema inteligente de gestión para El Paladar del Inka · Taller de Proyectos 2 · 2026-II
**Rama:** `feature/premium-ui-100-evidencias`
**Base:** `release/paladar-inka-v1-piloto`

## 1. Objetivo y alcance comprobable

Mejorar la presentación comercial del software **sin reemplazar las reglas ni los endpoints existentes**. Se preservan React 19 + TypeScript, FastAPI, PostgreSQL, cálculo transaccional en servidor, JWT/RBAC, trazabilidad Kardex y operaciones de venta/cocina. Las pruebas históricas de 51 casos + 27 controles HTTP fueron ejecutadas en el commit de referencia anterior; **deben volver a aprobar sobre esta rama**.

El rediseño incluye un sistema de diseño coherente, fotografía ilustrativa, dashboard de venta, tarjetas de catálogo, vista administrativa con miniaturas, estados de hover/foco, adaptación a tabletas y móviles, y capturas verificadas mediante navegador.

## 2. Diseño visual entregado

- Paleta: verde oscuro de horno artesanal, crema cálido, vino/carmín, acentos miel y estados semánticos.
- Sidebar y cabecera: jerarquía de navegación por roles, énfasis de selección, indicadores de sesión/API.
- Login: composición editorial, fotografía de referencia y formulario real autenticado con la API.
- Dashboard: banner con imagen, KPI del backend, pedidos, alertas, indicadores y accesos rápidos.
- POS: fotografías por SKU de las cuatro pizzas de demostración, precios en soles, carrito, filtros y tipos de atención.
- Catálogo administrativo: fotografías diminutas por SKU y mantenimiento existente.
- Cocina, inventario, clientes, reportes, seguridad: consistencia visual sin alterar operaciones.
- Responsive: puntos de quiebre de 1250, 880, 650 y 380 px, menú móvil y lectura legible en teléfono.
- Accesibilidad: `alt` para fotografías semánticas, foco visible y modo de movimiento reducido.

## 3. Fotografía y propiedad intelectual

Se utilizan **fotografías de referencia**, no fotos verificadas de productos vendidos por la pizzería. Fueron seleccionadas de **Unsplash** bajo su licencia pública: https://unsplash.com/license

Una referencia comprobable: https://unsplash.com/photos/a-pepperoni-pizza-sitting-on-top-of-a-wooden-cutting-board-xIqVfW8XUt4

Los cuatro recursos de ejemplo se identifican en `frontend/src/assets/menuPhotos.ts` por SKU (`PIZ-INK`, `PIZ-AND`, `PIZ-SUP`, `PIZ-VEG`) y se sirven desde `images.unsplash.com`. Para productos nuevos de la categoría Pizzas se utiliza una fotografía genérica **siempre etiquetada como referencial**, sin afirmar que corresponde a su receta; otras categorías sin recurso verificado mantienen un estado visual neutro.

**Decisión pendiente para producción:** sustituir estas fotos por fotografías propias aprobadas, comprimirlas a WebP/AVIF y servirlas desde el almacenamiento del proyecto/CDN controlado. El CDN remoto puede no cargar sin Internet; el componente presenta un estado de respaldo y las pruebas de fotografía declaran fallo si la imagen esperada no se carga.

## 4. Pruebas y evidencias 91-100

`scripts/e2e_premium_visual.py` es ejecutado por el orquestador de la suite ya existente. El workflow `e2e-full-coverage.yml` valida exactamente 100 PNG únicos y que los controles HTTP mantengan cero errores.

| N.º | Evidencia esperada | Comprobación |
|---|---|---|
| 91 | Login con fotografía | Imagen cargada en Chromium antes de capturar |
| 92 | Dashboard 1536 px | Datos de API y fotografía cargada |
| 93 | POS con fotos | Todas las tarjetas de pizzas con imagen completa y decodificada (`naturalWidth > 0` y `decode()`) |
| 94 | Carrito una pizza | Añadir desde tarjeta funcional |
| 95 | Carrito dos pizzas | Suma interactiva y detalle de unidades |
| 96 | Catálogo administrativo | Miniatura fotografiada por SKU |
| 97 | Comandas premium | Columnas y pedidos reales de QA |
| 98 | POS tablet 1024 px | Adaptación de vista en navegador |
| 99 | Dashboard móvil 390 px | Layout de indicadores y sesión |
| 100 | POS móvil con fotografías | Catálogo y carrito responsive |

Las imágenes 01-90 corresponden a los escenarios de la rama previa. Las nuevas **solo se pueden declarar aprobadas cuando el job de GitHub Actions haya finalizado en verde**. Cada captura conserva nombre, descripción, fecha UTC y origen en `e2e/evidencias/e2e-results.json`.

## 5. Reproducibilidad

```bash
bash scripts/start.sh              # Inicia con Docker y secretos generados
bash scripts/verify.sh             # Controles del repositorio
# En CI, el workflow Extended Full-System UI Evidence genera el artefacto
# paladar-full-ui-evidence con 100 PNG cuando todo supera las validaciones.
```

Para replicar el navegador contra una instancia QA con datos ficticios, ejecutar `python scripts/e2e_browser.py` con `SEED_ADMIN_PASSWORD` y `E2E_FRONTEND_URL` correctamente configurados.

## 6. Limitaciones no resueltas por un rediseño

**No equivalen a salida comercial lista** las 100 capturas, el resultado CI ni la mejora estética. Faltan UAT firmada con personal del negocio, validación de procesos reales, verificación tributaria y medios de pago, endurecimiento de infraestructura, seguridad DAST y backup/restauración verificada. La analítica se mantiene heurística y la predicción estadística descriptiva, no ML entrenado.

Las evidencias no deben atribuirse a producción ni alterarse digitalmente para simular resultados.