> **Descarga recomendada (piloto técnico verificado):** utiliza esta rama `release/paladar-inka-v1-piloto`. En Windows abre `INICIAR_WINDOWS.bat` con Docker Desktop iniciado; en Linux/macOS/WSL ejecuta `bash scripts/start.sh`. Los usuarios de demostración usan datos ficticios. La descarga de `main` todavía NO contiene esta versión mientras el PR #11 esté pendiente de aprobación.

## Experiencia premium v3 — validada para piloto técnico

La mejora [PR #14 (fusionado)](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/pull/14) está integrada en esta rama de entrega. Incluye centro de operaciones con datos del servidor, sincronización verificable, ayuda accesible y navegación por roles, carrito móvil, fotografías referenciales con ilustración local de respaldo y diseño responsive. La [ejecución E2E aprobada](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/actions/runs/45897585108) generó **152 PNG auténticos**: 100 escenarios previos más 52 capturas en pantallas de 360, 390, 768 y 1440 px (login, 11 módulos y centro de ayuda), con galería, manifiesto SHA-256, 27/27 controles HTTP, cero errores JavaScript y cero desbordamientos horizontales detectados. También aprobaron Fullstack Quality, Fresh Clone Docker y Security and Accessibility QA (axe-core automatizado preliminar).

- [Decisiones UI/UX y matriz de 152 evidencias](docs/EXPERIENCIA_PREMIUM_V3_RESPONSIVE.md)
- [Galería, SHA-256 y controles de pantalla del workflow](.github/workflows/e2e-full-coverage.yml)

## Antecedente: interfaz premium v2 y sus primeras 100 evidencias

La rama `release/paladar-inka-v1-piloto` incorpora el rediseño visual premium y responsive, fotografías **referenciales** de pizzas en POS y catálogo, login/dashboard con fotografía y la suite Playwright ampliada a **100 capturas reales de navegador**. La [ejecución E2E final aprobada](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/actions/runs/45892814169) aporta el artefacto `paladar-full-ui-evidence` con 100 PNG, galería HTML, SHA256 y los 27 controles HTTP con cero errores. Las fotografías son ilustrativas y deben sustituirse por recursos propios aprobados antes del uso comercial.

- [Decisiones de diseño, licencia de fotografías y matriz QA 91–100](docs/REDISENO_PREMIUM_EVIDENCIAS_100.md)
- [Workflow que produce el ZIP de evidencias reales](.github/workflows/e2e-full-coverage.yml)

# Paladar Inka AI — gestión integral de pizzería

Sistema académico de ingeniería de software desarrollado para **El Paladar del Inka**, Taller de Proyectos 2, Universidad Continental (2026-II).

**Tecnologías:** React 19 + TypeScript + Vite · FastAPI (Python 3.12) · PostgreSQL 17 · SQLAlchemy y Alembic · Docker Compose · GitHub Actions.

## Ejecutar después de descargar GitHub

No necesitas instalar Node, Python o PostgreSQL localmente. Solo **Docker Desktop/Engine + Docker Compose v2**.

**En Windows:** abre Docker Desktop y haz doble clic en **`INICIAR_WINDOWS.bat`**.

**En Linux, macOS o WSL:**
```bash
bash scripts/start.sh
```

El instalador crea **`.env` con secretos locales aleatorios**, inicia PostgreSQL + API + React, aplica migraciones y crea datos de prueba sin duplicados. Luego abre:

| Acceso | URL |
|---|---|
| Aplicación React | http://localhost:5173 |
| API Swagger (solo demo) | http://localhost:8000/docs |
| Comprobación API | http://localhost:8000/api/v1/ready |

Usuarios de demostración: `admin`, `cajero` y `cocina`. Lee el valor **`SEED_ADMIN_PASSWORD` de tu `.env` local** para la contraseña. Es una demo con insumos y pedidos ficticios, no un despliegue empresarial.

**[Manual de instalación paso a paso y solución de errores](docs/INSTALACION_LOCAL.md)** · [Operación comercial y despliegue seguro](deploy/OPERACIONES.md)

> **Rama GitHub:** mientras [el PR #11](https://github.com/rodo4940/TP2-Grupo11-PaladarInkaIA/pull/11) espera la revisión requerida para entrar en `main`, descarga la rama `feature/mvp-demostrable-qa-20261126` desde el selector de ramas. Descargar `main` antes de la fusión no garantiza encontrar este código.

## Módulos operativos

| Área | Funcionalidades implementadas |
|---|---|
| Autenticación | JWT, Argon2, roles administrador/caja/cocina, revocación de sesiones tras cambio de clave |
| Productos | Catálogo, precios, activación/desactivación, recetas por ingrediente |
| Ventas y POS | Crear pedidos, calcular total en servidor, controlar stock, cobro único por pedido |
| Cocina | Comandas y estados pendiente → preparando → listo → entregado |
| Inventario | Existencias, mínimos, ajustes, consumo por receta y Kardex trazable |
| Clientes | Registro, historial y totales de compras confirmadas |
| Reportes | Ingresos confirmados por medio de pago y ranking de productos |
| Inteligencia operativa | Recomendaciones heurísticas y previsión descriptiva de demanda con límites explícitos |
| Seguridad y auditoría | Roles RBAC y bitácora de cambios críticos |

**Importante:** el ticket generado es exclusivamente **interno**, no una boleta o factura electrónica de SUNAT. El módulo de inteligencia todavía no usa modelos ML entrenados con histórico real.

## Ejecutar controles y detener

```bash
bash scripts/verify.sh
# Detener y conservar los datos
docker compose down
# Borrado explícito de datos ficticios, con confirmación
bash scripts/reset-demo.sh
```

CI integra pruebas backend sobre PostgreSQL, compilación React, una prueba de instalación desde cero con Docker y recorridos de navegador con capturas.

## Despliegue real y seguridad

`docker-compose.prod.yml` y `deploy/Caddyfile` son una **plantilla de despliegue**, no autorización automática para operar con clientes ni cobrar pagos. Para producción deben verificarse seguridad, TLS, backups recuperables, auditoría, privacidad, UAT real y proceso tributario aplicable.

- [Checklist **go / no-go**](docs/RELEASE_READINESS.md)
- [Runbook de producción](deploy/OPERACIONES.md)
- [Arquitectura técnica](docs/ARQUITECTURA.md)
- [Pruebas y evidencias](docs/PLAN_QA.md)
- [Manual de usuario](docs/MANUAL_USUARIO.md)
- [Cobertura visual de pantallas](docs/UI_REFERENCIAS_Y_ESTADO.md)

**Autores:** Jamil Shandee Hinojosa Ttito · Jose Paolo Champi Palacios · Rodolfo Muñoz Cruz · Erik Alexander Callañaupa Quispe.

**Docente:** Ing. Néstor Gutiérrez Huamán.