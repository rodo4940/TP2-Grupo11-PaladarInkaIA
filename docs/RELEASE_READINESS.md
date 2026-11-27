# Evaluación de preparación de lanzamiento — 26/11/2026

**Estado: CANDIDATA A DESPLIEGUE PILOTO; NO CERTIFICADA PARA OPERACIÓN COMERCIAL.**

## Evidencia positiva
- Base transaccional FastAPI + PostgreSQL 17 + React implementada en PR; `fullstack-ci.yml` verifica migración, pruebas y build.
- Playwright/Chromium recorre login → POS → pago → cocina → Kardex → reportes → RBAC y toma 14 capturas reales con datos ficticios.
- Contratos API autenticados, permisos de tres roles, facturación interna no tributaria explícita, recetas e inventario transaccional, reportes de cobro.

## Bloqueos reales de go-live
1. **Consentimiento y UAT:** firmas del establecimiento, capacitación, protocolo de aceptación y resultados de escenarios reales.
2. **Facturación tributaria:** integración SUNAT/boletas y facturas según obligación de la pizzería, antes de comercializar.
3. **Reembolsos:** cancelación de pedido pagado y devolución contable/bancaria no están implementadas.
4. **Seguridad:** pentest, MFA, reset seguro de contraseña, rate limits externo, gestión y rotación de secretos, registro de accesos, sesiones revocables.
5. **Continuidad:** backup externo cifrado, restauración ensayada, monitoreo, alertas, métricas, RPO/RTO y simulacro de fallas.
6. **Carga:** medir capacidad en hardware y conexión objetivo; definir SLO real y tiempos de respuesta.
7. **IA:** no hay modelo ML entrenado ni métricas predictivas validadas. Solo heurística explicable.
8. **Datos:** definir migración real, inventario de inicio, limpieza, privacidad y contrato de tratamiento de datos personales.
9. **Legal y operaciones:** definir operador responsable, soporte y procedimiento de incidentes, acuerdos de niveles de servicio y cierre contractual.

## Go/no-go
No cambiar a «Aprobado para producción» hasta que cada bloqueo tenga dueño, evidencia fechada y aprobación escrita. Un CI verde es prueba técnica del código bajo pruebas, **no** aprobación empresarial.
## Sesiones y contraseñas (actualización)
La revisión incluye PATCH/POST de cambio y restablecimiento de contraseña con Argon2, versionado de token y revocación inmediata de sesiones JWT. El mecanismo administrativo no equivale a recuperación autónoma segura por correo. Aplicar Alembic hasta `20261126_02` antes de ejecutar API 1.1.

## Actualización v8 — rama de integración, estado condicionado
- [x] Implementación de registro manual de devolución única por pago, referencia externa y confirmación por usuario administrador distinto.
- [x] Implementación de arqueo de caja persistente en moneda PEN y zona America/Lima, fondo inicial, diferencias, estado y audit trail; bloqueo de aprobaciones con snapshot obsoleto.
- [x] Módulo visual de solicitud y arqueo; se verificará con el CI del SHA final de PR #20.
- [ ] Validación real del reintegro por PSP/banco con autorización y conciliación empresarial.
- [ ] UAT presencial: ejecutar y firmar `docs/UAT_PILOTO_V8.md`.
- [ ] Homologación tributaria: ver `docs/INTEGRACION_SUNAT_V8.md`.
- [ ] IA entrenada: dataset autorizado, backtesting y mejora frente a baseline. Ver `docs/IA_VALIDACION_V8.md`.
- [ ] Seguridad/carga/recuperación empresariales: ver `docs/SEGURIDAD_CONTINUIDAD_V8.md`.
- [ ] Las operaciones de caja y las pruebas técnicas NO representan cierre contable, autorización comercial ni conformidad del establecimiento.

**GO / NO GO: NO GO comercial.** La versión 8 es candidata a revisión técnica y piloto autorizado, no certificación ni emisión SUNAT.

### Control de acceso adicional implementado en v8
- Bloqueo temporal persistente por cuenta tras varios intentos fallidos; configuración en entorno mediante `LOGIN_MAX_ATTEMPTS` y `LOGIN_LOCKOUT_MINUTES`. El administrador desbloquea mediante restablecimiento seguro de contraseña.
- No sustituye rate limiting por origen, MFA, WAF ni revisión de seguridad externa. Puede ser usado indebidamente para bloquear cuentas conocidas; documentar atención al bloqueo.

## Estado v9 (NO GO comercial)
- [x] Laboratorio XML representativo de UBL 2.1 para documento 01/03/07, validaciones locales, idempotencia y trazabilidad con SHA-256. **No es SUNAT auténtico**.
- [x] Modelo Ridge entrenado en laboratorio (dataset sintético y holdout). **No entrenado ni validado sobre ventas reales del restaurante**.
- [x] Cierre interno finalizado y protegido con hash; bloqueo de registro de nuevo cobro en período finalizado.
- [x] Scripts de copia remota cifrada con checksum y restauración con confirmación de aislamiento. **No ejecutados en host empresarial**.
- [x] Matriz de 16 casos de pruebas `LAB-UAT` en pytest + registros JUnit; evidencia comercial requiere prueba humana.
- [ ] Ejecutar los casos UAT con el restaurante y adjuntar firmas auténticas.
- [ ] Certificar obligaciones SUNAT con credenciales/certificados oficiales y contador; laboratorio no es emisión legal.
- [ ] Conseguir dataset autorizado de ventas y validar modelo empresarial.
- [ ] Ensayar restauración de copias externas en infraestructura y definir RPO/RTO.
- [ ] Revisión externa de seguridad, carga y protección de datos.
- [ ] Obtener acta firmada y decisión empresarial para producción.

**Aprobación declarada:** el solicitante señaló que la pizzería aprobó el proyecto, sin proporcionar un acta con firma verificable. Ver `docs/DECLARACION_APROBACION_V9.md`. No convertir esta afirmación en firma.
