# Operación y despliegue (plantilla verificable; sin entorno de producción asignado)

## Requisitos previos
- Servidor Linux administrado por la organización, Docker Compose v2, 2+ vCPU, 4+ GB RAM (dimensionar con carga real), SSD y backups externos.
- Dominio real apuntando al servidor; firewall solo 80/443 público y SSH restringido; NTP; autorización del establecimiento.
- Completar `docs/RELEASE_READINESS.md`; nunca ejecutar `app.seed` con información real.

## Instalación manual controlada
1. `cp .env.production.example .env.production`; sustituir **TODOS** los valores temporales.
2. `chmod 600 .env.production`, `git status --short` y revisión de secretos.
3. `docker compose --env-file .env.production -f docker-compose.prod.yml build`
4. `docker compose --env-file .env.production -f docker-compose.prod.yml up -d db`
5. `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm backend alembic upgrade head`
6. Crear el primer usuario administrador (solo una vez, por consola interactiva): `docker compose --env-file .env.production -f docker-compose.prod.yml run --rm backend python -m app.manage create-admin --username admin --name "Responsable autorizado"`. La contraseña se solicita sin eco y no queda en Git.
7. `docker compose --env-file .env.production -f docker-compose.prod.yml up -d`
8. Verificar HTTPS, `GET /api/v1/health` (proceso disponible) y `GET /api/v1/ready` (base de datos disponible), autenticación y compra de prueba; no utilizar datos personales reales hasta tener aprobación. El `healthcheck` del contenedor backend usa `/ready` para detectar fallos de conectividad y evitar confundir proceso vivo con servicio preparado.

## Backups y restauración
- `bash deploy/backup.sh .env.production` genera archivo pg_dump en `backups/` + SHA256. No es backup remoto ni cifrado en reposo: exportarlo cifrado a almacenamiento distinto, con control de acceso y retención.
- Para probar recuperación: provisionar ENTORNO DE PRUEBA aislado. `CONFIRM_RESTORE=PERDER_DATOS_ACTUALES bash deploy/restore.sh backups/archivo.dump .env.production`. Nunca hacerlo directamente sin ventana autorizada y validación de riesgo.
- Definir RPO/RTO con la empresa, programar copia cifrada y restauración ensayada. No prometer recuperación validada hasta ejecutarla.

## Seguridad
- TLS gestionado por Caddy para dominio real; Swagger deshabilitado; base de datos no tiene puerto público.
- JWT_SECRET y clave DB provienen de `.env.production`, fuera del repositorio.
- Falta configurar firewall, rotación de claves, rate limiting perimetral, monitoreo, SAST/DAST y gestión de vulnerabilidades antes de producción.

## Limitaciones normativas
- Los tickets internos NO son comprobantes de pago SUNAT. La activación de facturación electrónica requiere integración formal autorizada o proveedor OSE/PSE y validación tributaria aplicable.
- Los números de fidelización son referenciales; no hay contrato ni programa activo de canjes.
- La analítica usa estadísticas, no un modelo de IA entrenado, y no debe publicitarse como tal.
## Asistente empresarial
Por defecto `AI_API_KEY` y `AI_MODEL` están vacíos: la experiencia sigue operativa mediante reglas locales verificables. Para usar un proveedor externo, el responsable configura ambos valores en el entorno privado de despliegue (no en React, GitHub ni el navegador). Solo se envían indicadores agregados y preguntas operativas estandarizadas; deben revisarse condiciones de tratamiento, costo y disponibilidad del proveedor. El contenedor de producción recibe esos valores a través de Compose; para un entorno real se recomienda un almacén de secretos gestionado en lugar de ficheros sin cifrar.
