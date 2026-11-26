# Lista de preparación para producción y sustentación

## Estado comprobable

- [x] API REST de módulos de negocio (autenticación, pedidos, pagos, cocina, inventario, clientes, catálogo, usuarios, reportes y auditoría).
- [x] Separación de roles aplicada en backend.
- [x] Inventario transaccional, rollback por falta de stock, historial de movimientos.
- [x] Migración Alembic y base PostgreSQL en el pipeline de integración.
- [x] Suite automatizada con fixtures aislados y pruebas de negocio.
- [x] Build de React/TypeScript automatizado en GitHub Actions (revisar run para resultado).
- [x] Documentación de arquitectura, criterios QA y guía operativa.

## Pendiente antes de un despliegue empresarial REAL

- [ ] Autorización escrita del establecimiento y contrato de tratamiento de datos.
- [ ] HTTPS/TLS y reverse proxy seguro, HSTS, CSP y controles OWASP ASVS revisados.
- [ ] Gestión de secretos con vault, rotación de JWT, reinicio de sesiones, rate-limit y reset de contraseñas.
- [ ] Verificación de migración de datos reales y plan de respaldo/restauración probado periódicamente.
- [ ] Monitoreo, métricas operativas, log centralizado y alertas de fallos.
- [ ] Pruebas de carga con concurrencia y criterios de SLA acordados.
- [ ] Revisión de seguridad profesional (SAST, DAST, pentest autorizado).
- [ ] Validación de facturación/documentos tributarios con SUNAT, si aplica al alcance empresarial.
- [ ] Protocolo de devoluciones de dinero y reversión contable de ventas.
- [ ] Auditoría de cambios en recetas y control de versiones de ingredientes históricos.
- [ ] Pruebas UAT con representante de la pizzería y firma de conformidad auténtica.
- [ ] Modelo predictivo de IA entrenado/evaluado con dataset autorizado y línea base medible.

## Criterio de honestidad técnica

El proyecto es una **versión integrada evaluable técnicamente**; el check de CI confirma pasos automatizados, no certifica la satisfacción de clientes, seguridad integral o uso empresarial. Los registros de demostración son ficticios.