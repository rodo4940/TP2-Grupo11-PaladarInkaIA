# Protocolo UAT y acta de aceptación — versión piloto v8

**Proyecto:** Sistema de ventas, inventario y atención asistida para El Paladar del Inka  
**Versión evaluada:** commit Git SHA: ______________ · URL del despliegue: ______________  
**Fecha y sede:** ______________ · **Responsable de pizzería:** ______________  
**Equipo ejecutor:** ______________ · **Ambiente:** [ ] pruebas [ ] piloto autorizado  
**Estado del documento:** PLANTILLA, **SIN PRUEBAS COMERCIALES EJECUTADAS NI FIRMAS**.

> Las pruebas CI con datos ficticios no sustituyen estas comprobaciones de negocio. Nunca marcar "Aprobado" sin testigo, resultado y evidencia auténticos.

## Requisitos y prerrequisitos
- Permiso escrito del establecimiento para la sesión, tratamiento de datos y documentación.
- Datos ficticios o dataset autorizado; precios, recetas, existencias iniciales e impuestos aprobados por el responsable.
- Roles separados `admin`, `cashier`, `kitchen`; acceso a impresora y red del piloto.
- Identificar quién verifica dinero, vouchers y devoluciones; disponer de registro externo de operación para reintegros.
- No emitir documentos tributarios con la versión demostrativa: los tickets `INT-*` son internos.
- Guardar SHA del commit, hora America/Lima, navegador/dispositivo, ID de pedido y evidencia con acceso restringido.

## Matriz de pruebas para ejecución PRESENCIAL

| ID | Escenario | Criterio de aceptación verificable | Resultado real |
|---|---|---|---|
| UAT-01 | Ingreso con cajero | Accede solo al POS y funciones del rol | Sin ejecutar |
| UAT-02 | Ingreso con cocina | No ve clientes, pagos ni usuarios | Sin ejecutar |
| UAT-03 | Crear pedido | Total es precio × cantidad; ID persiste al refrescar | Sin ejecutar |
| UAT-04 | Stock insuficiente | Error controlado; pedido y kardex sin movimiento parcial | Sin ejecutar |
| UAT-05 | Descuento de insumos | Cantidades coinciden con receta y kardex | Sin ejecutar |
| UAT-06 | Flujo cocina | Pedido pasa por preparando/listo/entregado | Sin ejecutar |
| UAT-07 | Pago con medio real o simulado | Una operación, importe exacto; duplicado rechazado | Sin ejecutar |
| UAT-08 | Constancia interna | Documento INT indica claramente que no es SUNAT | Sin ejecutar |
| UAT-09 | Caja por fecha Perú | Venta junto a medianoche se contabiliza en día correcto | Sin ejecutar |
| UAT-10 | Solicitud de devolución | Mantiene pago histórico y registra motivo/auditoría | Sin ejecutar |
| UAT-11 | Devolución de doble control | Otro administrador documenta referencia del reintegro EXTERNO | Sin ejecutar |
| UAT-12 | Arqueo y cierre interno | Fondo inicial, conteo, diferencia y aprobación registrada por otra persona administradora | Sin ejecutar |
| UAT-13 | Cambios posteriores al arqueo | Registro se marca desactualizado y bloquea aprobación pendiente | Sin ejecutar |
| UAT-14 | Responsive accesible | 320/390/768/1440 sin corte; teclado y lector de pantalla básico | Sin ejecutar |
| UAT-15 | Analítica/IA | Aclara heurística, fuentes y límites, no inventa movimientos | Sin ejecutar |
| UAT-16 | Respaldo y caída de red | Operador identifica recuperación, responsables y tiempos medidos | Sin ejecutar |

Por caso: **fecha/hora** ______ · **ejecutor** ______ · **dato de prueba/ID** ______ · **observado** ______ · **esperado** ______ · **evidencia** ______ · **resultado** [ ] Conforme [ ] Observado [ ] No conforme · **incidencia** ______.

## Evidencias y trazabilidad
- Resultados automáticos: enlazar run del SHA exacto, JUnit/Playwright y manifiesto SHA-256 de capturas.
- Evidencia UAT distinta: minutas, fotos autorizadas de pantalla, registros de pedidos de prueba anonimizados, comprobantes de prueba claramente rotulados, responsables y resultado por caso.
- No usar firmas reconstruidas, capturas simuladas presentadas como reales ni nombres inventados.
- Defectos: código, severidad, pasos reproducibles, responsable, fecha objetivo, PR correctivo y nueva verificación.
- Una observación crítica de cobro, stock, acceso indebido, SUNAT o recuperación determina **NO GO comercial**.

## Dictamen y firmas (completar PRESENCIALMENTE)
**Resumen:** casos conformes ____ / 16; observados ____; no conformes ____; no ejecutados ____.  
**Observaciones obligatorias:** ________________________________________________________________  
**Decisión:** [ ] CONFORME PARA PILOTO CONTROLADO [ ] CON OBSERVACIONES [ ] NO CONFORME  
**La conformidad de piloto NO autoriza automáticamente operación tributaria/comercial.**

Representante autorizado de El Paladar del Inka: nombre ______________ cargo ______________ firma ______________ fecha ______________  
Responsable técnico del proyecto: nombre ______________ firma ______________ fecha ______________  
Especialista/validador externo (si corresponde): nombre ______________ firma ______________ fecha ______________

## Cierre académico
Incorporar esta acta únicamente con resultados auténticos en anexos; diferenciar claramente pruebas CI (técnicas), UAT (aceptación empresarial) y homologación operativa/tributaria (externa).
