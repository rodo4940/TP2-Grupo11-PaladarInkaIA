# Procedimiento de copia remota cifrada — v9

Este proyecto dispone de `deploy/backup_encrypted.sh` y `deploy/restore_encrypted.sh`. **No afirma haber efectuado una copia real del restaurante**: no hay host, identidad age, cuenta remota ni autorización de datos suministrados en este proyecto.

## Requisitos operativos
Servidor autorizado con Docker Compose 2, cliente `age` y `rclone`, acceso a un remoto compatible (S3/WebDAV/otro backend rclone aprobado). Las claves se administran fuera de Git; prueba de recuperación en un entorno aislado. El programa local anterior `deploy/backup.sh` conserva un dump NO cifrado y no debe exportarse a destinos externos.

## Copia cifrada y verificación remota
1. Provisionar `AGE_RECIPIENT` (clave pública del custodio), `BACKUP_REMOTE` (destino rclone, accesos con privilegios mínimos), y `.env.production` externo.
2. Programar en el servidor mediante scheduler de la organización:
   `AGE_RECIPIENT='age1...' BACKUP_REMOTE='remote:paladar/backups' bash deploy/backup_encrypted.sh .env.production`
3. El script ejecuta `pg_dump -Fc` por canal de proceso directamente a `age` sin dump local claro, calcula SHA-256, sube ZIP cifrado y manifiesto, y vuelve a leer copia remota para comparar hashes.
4. Retención y versiones inmutables se configuran en el proveedor; **NO** eliminar respaldos automáticamente desde un script sin regla autorizada.
5. Registrar fecha, duración, volumen, nombre remoto, SHA-256, error y responsable en bitácora sin PII.

## Restauración controlada
1. Crear instancia temporal sin acceso público a producción y con datos mínimos. Descargar `archivo.dump.age` y `archivo.dump.age.sha256`.
2. Proteger `AGE_IDENTITY_FILE` (clave privada) y ejecutar:
   `RESTORE_ISOLATED=YES_I_CONFIRMED_ISOLATION CONFIRM_RESTORE=PERDER_DATOS_ACTUALES AGE_IDENTITY_FILE=/run/secrets/age.key bash deploy/restore_encrypted.sh archivo.dump.age .env.production`.
3. Medir tiempo, ejecutar `alembic current`, comprobar tabla de pagos, devoluciones, cierres, documentos demo y login de operador QA.
4. Definir con negocio RPO/RTO y programar simulacro mensual. No marcar recuperabilidad como validada sin bitácora, firma y evidencia de ejecución.

## Riesgos y limitaciones
- SHA-256 comprueba integridad, no autenticidad del origen; use controles de identidad de bucket y acceso a versiones.
- Una pérdida total de clave privada age hace imposible descifrar el respaldo: custodia y rotación fuera del repositorio.
- El parámetro `RESTORE_ISOLATED` es declaración manual, **no** comprobación criptográfica de aislamiento del servidor.
- No hay backups productivos ejecutados ni SLA de recuperación verificado.
