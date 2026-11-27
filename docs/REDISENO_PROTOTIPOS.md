# Rediseño de interfaz: identidad de El Paladar del Inka

## Referencias de diseño aprobadas
El rediseño utiliza los prototipos aportados por el equipo académico como referencia: fondo casi negro, paneles carbón, acentos dorados, menú lateral con identidad de pizzería, indicadores compactos, acciones operativas visibles, tipografía clara y densidad de información adecuada a 1440–1536 px. El objetivo visual es mantener una identidad uniforme en escritorio, tableta y móvil.

## Módulos y estado comprobable

| Módulo | Interfaz | Integración real |
|---|---|---|
| Acceso | Panel dividido, fotografía referencial y formulario oscuro | JWT y controles server-side existentes |
| Dashboard | Métricas, evolución 7 días, lista de pedidos, estados de cocina, alertas | Datos de pedidos, ventas, productos e inventario recibidos de la API |
| Punto de venta | Catálogo con fotografías, filtros, carrito, tipo de atención, cliente, medios de pago y ticket | Crea pedido y registra pago único, permite comanda sin pago y recuperación de pedido pendiente |
| Pedidos | Listado, filtros, panel lateral con detalle y línea de tiempo | Estados y pagos autorizados por el backend |
| Cocina KDS | Columnas pendientes, preparando, listos y entregados; acciones visibles | Estados persistidos mediante API. El estado «hornear» de los prototipos no existe en la máquina de estados del backend y no se simula como dato real |
| Inventario | Indicadores, filtro, tabla, ficha lateral, Kardex y ajuste | Existencias y movimientos, ajuste exclusivo del administrador |
| Catálogo y recetas | Tema negro/oro sobre edición, alta de productos y recetas | CRUD, receta, activación y precios, preserva las operaciones previas |
| Clientes | Tema negro/oro con alta e historial | CRUD, historial y datos autorizados existentes |
| Reportes | Tema negro/oro, indicadores, tablas y exportaciones | Reportes de cobros registrados y CSV |
| IA | Tema negro/oro, asistencia explicable y modelo demostrativo | Heurística sobre registros conectados; entrenamiento separado con datos sintéticos |
| Usuarios, permisos y configuración | Tema negro/oro, controles de roles, auditoría y preferencias | RBAC existente de admin/cajero/cocina; no se finge MFA ni privilegios dinámicos inexistentes |
| Caja | Tema negro/oro, historial, comprobante interno, devoluciones y arqueo | Acciones auditables y controles de aprobación; simulación fiscal separada, sin SUNAT legal |

## Arquitectura del cambio
- Los componentes `ReferenceDashboard`, `ReferencePOS`, `ReferenceOrders`, `ReferenceKitchen` y `ReferenceInventory` mantienen las llamadas a servicios actuales, sin introducir una base de datos paralela.
- `prototype-dark-gold.css`, `prototype-detail.css`, `prototype-inventory.css` y `prototype-a11y.css` definen un sistema visual común.
- El buscador superior permite navegar módulos por permisos (atajo `Ctrl+K`) y no busca clientes/productos si la API no ofrece un endpoint unificado de búsqueda.
- Los importes son PEN con valores provenientes del servidor; ni ventas ni alertas ni fidelización se generan artificialmente para llenar pantallas.
- No se reemplazan comprobantes SUNAT ni confirmaciones bancarias con estados de interfaz. Los comprobantes `INT-*` son internos.
- Se mantienen controles visuales de carga, errores y validaciones, y las acciones sensibles siguen requiriendo JWT/RBAC del servidor.

## Evidencia automatizable
La validación utiliza `Fullstack Quality` (compilación React/TypeScript y pruebas de backend), `Security and Accessibility QA`, `Responsive Experience` (320, 360, 390, 430, 768, 1024 y 1440 px, más caja) y `Extended Full-System UI Evidence`, que operan sobre Chromium y PostgreSQL de laboratorio.

La aprobación visual final debe basarse en el artefacto realmente generado por la ejecución del commit aprobado; no en capturas de los prototipos ni en ejemplos sin conexión al código. Una prueba de laboratorio no acredita aceptación presencial ni salida comercial.

## Contrastes sin promesas ficticias
El prototipo incluye elementos de aspiración —dos factores «activo», SUNAT «conectado», etapa individual «hornear» y métricas de IA entrenada real con clientes— que no pueden exhibirse como capacidades verificadas sin implementación y evidencia de negocio. Por seguridad y rigor, la aplicación presenta las capacidades actuales y sus límites.
