# Manual operativo — El Paladar del Inka

## Acceso

Configura las credenciales usando `SEED_ADMIN_PASSWORD` en `.env` y ejecuta la semilla **solo en un entorno demostrativo**. Abre `http://localhost:5173`. Ingresa con los usuarios demo `admin`, `cajero` o `cocina`. La interfaz muestra únicamente las secciones autorizadas para tu rol; el backend también lo verifica.

## 1. Caja / POS

Selecciona productos y cantidades, vincula opcionalmente a un cliente y confirma el pedido. La API comprueba la receta y descuenta ingredientes dentro de la misma transacción. Si falta un ingrediente, devuelve `409 Stock insuficiente` y no crea un pedido incompleto. Al cobrar usa el importe confirmado por servidor; repetir el cobro devuelve `409 Pedido ya pagado`.

## 2. Cocina

Revisa las comandas en `Cocina`. Un pedido pasa por `pendiente → preparando → listo → entregado`. No se permite saltar estados. Una cancelación anterior al cobro repone los insumos registrados en el consumo original; una venta ya cobrada requiere un proceso formal de devolución aún no incluido.

## 3. Inventario

Consulta existencias, mínimos y Kardex. Solo administración puede registrar ajustes positivos o negativos; cada movimiento registra referencia, saldo y usuario. Stock negativo se bloquea.

## 4. Productos, recetas y clientes

Administración crea productos e insumos y registra recetas. **No vender productos sin receta**, salvo que se decida expresamente otro proceso aprobado. Caja registra clientes opcionales. No utilizar datos personales reales sin autorización.

## 5. Reportes e IA

Ventas: muestra únicamente transacciones cobradas. Recomendaciones: ranking por popularidad y disponibilidad. Proyección: media móvil ponderada de siete días, no modelo ML entrenado. Con pocas ventas el resultado es orientativo y no un pronóstico auditado.

## 6. Usuarios

Administración crea cuentas, cambia roles o desactiva otras cuentas. No puede desactivar su propia sesión ni quitarse a sí misma el rol administrador desde la API. La bitácora permite comprobar cambios relevantes.

## Resolución de incidencias

- API no disponible: `docker compose ps` y `docker compose logs backend`.
- Error 401: ingresar nuevamente o revisar estado de cuenta y token.
- Error 403: usuario sin rol adecuado.
- Error 409: operación incompatible con el estado actual (stock, cobro, transición o duplicado).
- Error 422: payload/validación incorrecta.
- Error PostgreSQL: `docker compose logs db`; revisar `alembic current`.

## Respaldo y restauración

Realizar copias de seguridad usando `pg_dump` con credenciales seguras y prueba de restauración en entorno aislado. Este repositorio no ejecuta por sí mismo respaldos automáticos certificados. No hacer `docker compose down -v` salvo que se quieran eliminar deliberadamente los datos locales.