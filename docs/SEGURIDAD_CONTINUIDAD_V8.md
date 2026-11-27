# Seguridad, recuperación y continuidad — procedimiento de piloto

**Estado:** plantilla operativa; ninguna prueba en infraestructura del restaurante se presupone ejecutada.

## Propietarios por designar
Dueño de infraestructura: ______ · Administrador de sistema: ______ · DPO/encargado privacidad: ______ · Responsable negocio: ______ · Proveedor internet/hosting: ______

## Seguridad antes de producción
- [ ] HTTPS real y dominio autorizado, verificación de cabeceras, configuración segura del host, firewall y acceso SSH restrictivo.
- [ ] Gestor de secretos fuera de repositorio, rotación documentada, credenciales únicas, mínimo privilegio, deshabilitación de cuentas y revocación de sesiones.
- [ ] Bloqueo de fuerza bruta distribuido (WAF/rate limit perimetral probado). No considerar protección suficiente un contador en memoria si hay múltiples réplicas.
- [ ] Recuperación de contraseña fuera de banda, procedimiento de identidad verificado, MFA o control equivalente acordado con empresa.
- [ ] Revisión OWASP ASVS/DAST, pentest autorizado y remediación de hallazgos.
- [ ] Política de retención, acceso y tratamiento de datos; contrato con negocio/proveedores.
- [ ] Alertas, logs centralizados sin PII/secretos, health y ready, dashboard de errores y dueños de incidentes.
- [ ] Prueba de carga real (picos de pedidos/pagos simultáneos) sobre hardware objetivo y SLO medidos.

## Respaldo comprobable, sin exponer clientes
1. Emitir en ventana controlada `bash deploy/backup.sh .env.production`. Guardar manifiesto SHA-256 y salida de comando.
2. Transferir dump **cifrado** a almacenamiento fuera del host, mínimo privilegio y política de retención acordada.
3. Crear infraestructura efímera, aislada y sin acceso público; restaurar **solo allí**:
   `CONFIRM_RESTORE=PERDER_DATOS_ACTUALES bash deploy/restore.sh backups/ARCHIVO.dump .env.production`.
4. Anotar hora de inicio/fin, tamaño de dump, SHA-256 validado, versión de esquema Alembic, conteos de órdenes, pagos y auditoría, consistencia de saldos y logs.
5. Validar login, caja/stock, migraciones y operación realista de pruebas; destruir el entorno con aprobación.
6. Definir RPO (pérdida de datos máxima) ____ y RTO (tiempo máximo de recuperación) ____ con el establecimiento. No escribir cifras inventadas.

## Simulacros e incidentes
| Evento | Comprobación requerida | Evidencia |
|---|---|---|
| Caída DB | API `/ready` falla, alerta y recuperación sin transacción parcial | ____ |
| Pérdida de host | Restauración desde copia externa en entorno aislado | ____ |
| Corte de energía/caja | Protocolo de venta offline manual aprobado; conciliación posterior | ____ |
| Robo de token | Desactivar usuario/cambiar clave y verificar revocación | ____ |
| Cobro repetido/devolución | Idempotencia, auditoría y referencia real de proveedor | ____ |
| Fuga de datos | Aislar, preservar evidencias y aplicar protocolo legal vigente | ____ |

**GO comercial:** solo si cada control tiene responsable, evidencia fechada y aprobación escrita. Un pipeline verde no constituye auditoría de seguridad externa.
