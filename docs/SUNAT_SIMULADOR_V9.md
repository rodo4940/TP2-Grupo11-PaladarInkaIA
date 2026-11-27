# Simulador de comprobantes de pago electrónicos — v9 (SIN VALIDEZ TRIBUTARIA)

## Objetivo y límites
Implementación de laboratorio alineada parcialmente a conceptos de XML **UBL 2.1** y de los catálogos de SUNAT. Permite aprender y probar reglas del sistema sin usar el RUC, las credenciales, el certificado o el servicio de emisión de la pizzería.

**NO es un CPE legal, NO equivale a integración SUNAT real, NO genera CDR aceptado ni firma digital.** No declarar que cumple el 100 % de XSD, reglas vigentes, excepciones tributarias o interoperabilidad de proveedores OSE/PSE.

## API disponible (JWT y permisos de caja)
- `POST /api/v1/fiscal-demo/documents`: un documento de laboratorio 01 (factura demo) o 03 (boleta demo) por `Payment`, idempotencia obligatoria, cálculo total/céntimos/IGV ilustrativo.
- `GET /api/v1/fiscal-demo/documents`: historial no tributario con series FDEM/BDEM, jamás homologables.
- `GET /api/v1/fiscal-demo/documents/{id}`: estructura XML de laboratorio y SHA-256.
- `GET /api/v1/fiscal-demo/documents/{id}/verify`: integridad y parseo XML **locales**, con `official_sunat_validation=false`.
- `POST /api/v1/fiscal-demo/credit-notes`: nota 07 de laboratorio vinculada a boleta/factura demo con devolución **manual confirmada**; solo admin.

## Parámetros implementados
| Control | Implementación | Límite |
|---|---|---|
| Tipo | 01, 03 y 07 (referenciales) | No incluye nota débito ni todas las variantes |
| Serie | FDEM/BDEM/FNC1/BNC1 y correlativo único | Nunca serie oficial |
| Emisor | `00000000000`, ficticio | RUC inválido deliberado |
| Receptor | Tipo 0, DNI (8 dígitos), RUC (11 dígitos y dígito verificador) | No consulta padrón ni validez del receptor |
| Moneda | PEN, importes en céntimos | Solo soles |
| IGV | Códigos 10, 20, 30; 18 % ilustrativo en código 10 | No motor tributario oficial |
| Fecha | America/Lima, XML | No procesa vigencia/rechazos reales |
| Documento | XML demostrativo UBL 2.1 parcial y SHA-256 | Sin XSD oficial ni XMLDSig |
| Aceptación | SIMULADO_VALIDADO_LOCALMENTE | No CDR, sin autenticidad SUNAT |
| Idempotencia | Clave única y referencia de pago | No reintentos de PSE/OSE real |
| Anulación | Nota 07 demo y vinculación al pago | No constituye nota de crédito legal |

## Fuentes normativas de contraste
- <https://cpe.sunat.gob.pe/guias-y-manuales> — guías UBL 2.1 y catálogos oficiales.
- <https://cpe.sunat.gob.pe/noticias/servicio-beta-para-realizar-pruebas-ubl-21> — servicio beta estructural oficial, que **no ha sido llamado** aquí.
- <https://cpe.sunat.gob.pe/tipos_de_comprobantes/nota_de_credito> — notas de crédito vinculadas a comprobantes válidos.
- <https://cpe.sunat.gob.pe/sistema_emision/see_contribuyente> — envío, firma y constancia de recepción.

## Para alcanzar emisión real
1. Información tributaria real aprobada por el contador/representante, catálogos actuales y afectación IGV correcta.
2. Certificado digital/SEE o proveedor PSE/OSE; mTLS/credenciales y firma XMLDSig sobre estructura XSD vigente.
3. Validación oficial en beta, correlativos y reglas de emisión, reintentos y recepción del verdadero CDR.
4. E2E aceptado por negocio, controles de datos, conservación legal de XML, CDR y notas, y autorización escrita.
5. Revisión por asesor tributario; nunca copiar tal cual el XML de laboratorio como emisión auténtica.

**Estado:** simulador implementado; interoperabilidad tributaria y aprobación real pendientes.
