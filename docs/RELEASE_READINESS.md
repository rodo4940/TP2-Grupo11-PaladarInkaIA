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