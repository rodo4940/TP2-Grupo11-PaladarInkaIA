# Integración SUNAT — contrato de activación, no habilitada

## Estado de la versión v8
El sistema genera `INT-xxxxxx` de carácter administrativo y contiene el texto inequívoco `NO_EMITIDO_SUNAT`. **No emite boletas, facturas, notas de crédito ni CDR auténticos.** Las devoluciones manuales no generan documentos tributarios.

## Dependencias externas antes de desarrollar e integrar
1. Determinar con la pizzería su RUC, condición de emisor, régimen, tipo de venta, afectación IGV, moneda, series y tratamiento de consumidor final. Datos y decisiones bajo responsabilidad del representante/contador.
2. Elegir medio autorizado para emisión: solución SUNAT aplicable u operador/proveedor OSE/PSE según corresponda, con contratos y credenciales válidas.
3. Obtener credenciales/certificados y entorno de pruebas autorizados. Secretos solo en el entorno seguro, nunca Git/React/HTML/colección Postman publicada.
4. Acordar qué pasa ante anulación, nota de crédito, devolución bancaria, rechazos, timeout, reintentos, cambio de numeración y contingencias.
5. Definir esquema de documento, catálogo SUNAT vigente, identificación del cliente, XML/UBL aplicable, firma digital y preservación de XML+CDR conforme a obligaciones específicas.
6. Ejecutar homologación/casos con el proveedor, conciliación tributaria con contabilidad y firma de conformidad.

## Diseño técnico al integrar proveedor
- Mantener las entidades `Payment`, `Refund` y `CashCloseout` separadas del futuro `FiscalDocument`: pagos y comprobantes no son equivalentes.
- Asignar UUID idempotente por intento y tipo de documento; nunca presentar ticket INT como CPE.
- Estado de máquina sugerido: `draft` → `submitted` → `accepted` / `rejected` / `unknown`. Una respuesta HTTP 200 no demuestra CDR aceptado.
- Guardar hash del XML firmado, serie/correlativo autorizado, respuesta íntegra del proveedor, CDR, timestamp, usuario y reintentos; proteger PII.
- No permitir duplicados ante reintento; consultar estado tras timeout antes de emitir de nuevo.
- Validar importe con céntimos y reglas fiscales con contador. Una devolución puede requerir nota de crédito pero **no debe generarse automáticamente sin la regla tributaria validada**.
- Habilitar por `FISCAL_ISSUANCE_ENABLED=false` hasta homologación. No agregar una simulación que anuncie documentos auténticos.

## Condición de salida
**PENDIENTE EXTERNO.** Requiere proveedor/credenciales/homologación, pruebas de emisión y rechazo, y conformidad formal. Las pruebas de backend del proyecto no cierran este requisito.
