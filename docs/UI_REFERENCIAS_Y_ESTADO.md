# Correspondencia entre los 20 diseños y la implementación evaluada

Las 20 imágenes del portafolio recibido son **referencias de diseño** generadas digitalmente. No corresponden a la versión operativa ni son evidencia de QA. GitHub Actions `Real UI Screenshots` contiene capturas auténticas de React/FastAPI/PostgreSQL con datos ficticios y manifiesto.

| Pantalla de referencia | Implementación demostrable | Brecha relevante |
|---|---|---|
| 01 Login | Sí, React con JWT/Argon2 | MFA, bloqueo/rate limit y recuperación |
| 02 Dashboard | Sí, métricas de pagos/pedidos/stock | Comparativos históricos y filtros |
| 03 POS | Sí, pedido y cálculo servidor | Devoluciones, integración de cobro y comprobante fiscal |
| 04 Pedidos | Sí, listado, filtros y detalle | Delivery, notificaciones en tiempo real |
| 05 Cocina KDS | Sí, estados y tablero por columnas | Tiempos SLA, impresión de comandas |
| 06 Inventario | Sí, stock, ajustes, Kardex | Compras, lote/fecha vencimiento, inventario físico |
| 07 Productos/clientes | Sí, alta/edición de producto, recetas y clientes | Imágenes reales, variantes/combo |
| 08 Reportes | Sí, ventas pagadas/top productos/medios | Exportaciones, cierres de caja y tributos |
| 09 Panel IA | Parcial, ranking explicable | ML entrenado/evaluado y asistente conversacional |
| 10 Usuarios/configuración | Sí, permisos/estados y bitácora | MFA, auditoría de sesiones, políticas password |
| 11 Venta completada | Sí, pago y ticket interno | Boleta/factura electrónica oficial |
| 12 Detalle pedido | Sí, productos/etapas/importe | Courier y firma entrega |
| 13 Kardex | Sí, movimientos por pedido | Lotes/FEFO y conciliación física |
| 14 Registro producto | Sí, precios/activación y receta | Imagen, variantes, combos, impuestos |
| 15 Fidelización | Parcial, historial/puntos referenciales | Programa aprobado y canjes seguros |
| 16 Pronóstico/IA | Parcial, estimación estadística sin ML | Dataset, entrenamiento, métricas out-of-sample |
| 17 Seguridad | Parcial, RBAC/auditoría/headers | Pentest, seguridad perimetral y alertas |
| 18 API/QA | Sí, Swagger de desarrollo y CI | Rendimiento bajo carga real, DAST |
| 19 Responsive | Sí, CSS adaptable y captura móvil | WCAG y prueba de accesibilidad de usuario |
| 20 GitHub/entorno | Sí, repo con CI y migración | Despliegue productivo y UAT firmada |

**Regla:** nunca afirmar “implementado” cuando solo exista el prototipo gráfico; no afirmar “en producción” cuando las pruebas sean de laboratorio.