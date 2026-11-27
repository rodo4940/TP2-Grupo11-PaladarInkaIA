# Ejecución de 16 escenarios UAT-LAB (NO aceptación empresarial)

**Sistema:** Paladar del Inka IA, rama `feature/paladar-v9-fiscal-ml-qa-launch`.  
**Naturaleza:** protocolo reproducible de pruebas de laboratorio, con base temporal, datos ficticios y acceso programático. **NO se ha entrevistado ni probado con el representante de la pizzería por estas pruebas.**

## Evidencia ejecutable
- `backend/tests/test_uat_lab_v9.py`: exactamente 16 escenarios parametrizados `LAB-UAT-01..16` más prueba de cierre final (se registran también como pruebas de pytest).
- `backend/tests/test_fiscal_ml_lab.py`: boleta/factura simulada, RUC y DNI por formato, XML, hash, idempotencia, nota de crédito de laboratorio, IA ML reproducible/holdout.
- Workflow `.github/workflows/lab-v9.yml`: produce `LAB_TESTS.xml`, JSON del modelo entrenado, dataset agregado ficticio, predicciones demo y manifiesto SHA-256. Registrar enlace de la ejecución **del SHA final**.
- Responsive: evidencia Playwright/Chromium del workflow ya existente sobre la interfaz y backend reales, con datos de pruebas. Es distinta de aceptación humana.

## Diferencia obligatoria: UAT del establecimiento
| Tipo | Ejecutado por | Evidencia | Valor como aceptación comercial |
|---|---|---|---|
| API/CI lab | GitHub Actions | JUnit + reportes SHA-256 | No acredita satisfacción del negocio |
| Chromium lab | Navegador CI | Capturas y reportes | No acredita firma comercial |
| UAT presencial | Empleados/representante autorizado | Acta de 16 casos, observaciones, firmas auténticas | Requerida |
| SUNAT real | Emisor autorizado/proveedor/SUNAT | XML firmado/CDR y aceptación | No habilitado |

Los **16 casos de `docs/UAT_PILOTO_V8.md` permanecen sin resultados reales de empleados**. No marcar conforme/no conforme, fecha, nombre, firma ni resultado de la pizzería sin sustento.

## Declaración de aprobación recibida
El solicitante del proyecto manifestó: «el proyecto ha sido aprobado». Se registra exclusivamente como **declaración no verificada del solicitante**. No hay acta, identidad de firmante, fecha oficial ni conformidad escrita accesible en el repositorio. El formato de firma permanece sin completar (ver `docs/DECLARACION_APROBACION_V9.md`).

## Estado
**QA LABORATORIO:** consultar resultado de workflow; ningún estado final se da por aprobado sin CI verde.  
**UAT PIZZERÍA:** pendiente de acta y evidencia.  
**GO-LIVE:** sujeto a UAT, seguridad, respaldo recuperado, obligaciones tributarias y aceptación real.
