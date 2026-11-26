# Paladar Inka AI · Software de gestión para pizzería

Proyecto académico de Ingeniería de Sistemas e Informática, Universidad Continental (Cusco, 2026). **El Paladar del Inka**.

## Estado real

Esta rama integra el **frontend React** con una **API FastAPI** que persiste en **PostgreSQL 17**, con 36+ pruebas de integración de negocio, CI, control de roles y migraciones Alembic. La aplicación no representa un despliegue empresarial autorizado ni una aprobación firmada por la pizzería. Se debe completar UAT con usuarios reales, revisión de seguridad y un plan de operaciones antes de un uso productivo.

El módulo de recomendaciones utiliza reglas explicables y proyecciones descriptivas; **no se afirma que exista un modelo de machine learning entrenado** sin conjunto de datos de ventas suficiente.

## Módulos

| Módulo | Función | Backend |
|---|---|---|
| Autenticación y RBAC | Usuarios con JWT; roles admin, caja y cocina | `/auth/*`, `/users/*` |
| Ventas/POS | Crear pedidos y registrar pagos sin duplicados | `/orders`, `/orders/{id}/payment` |
| Cocina | Estados válidos: pendiente → preparando → listo → entregado | `/orders/{id}/status` |
| Inventario | Reserva de recetas, stock atómico y Kardex | `/ingredients`, `/inventory/movements` |
| Productos | Catálogo, precios y receta por producto | `/products` |
| Clientes | Registro y asociación a pedidos | `/customers` |
| Reportes | Ventas cobradas, métodos de pago, popularidad | `/reports/sales` |
| Inteligencia operativa | Ranking de popularidad y media móvil ponderada | `/recommendations`, `/ai/demand-forecast` |
| Auditoría | Historial de operaciones de negocio | `/audit` |
| Monitoreo | Salud de API y base de datos | `/health`, `/ready` |

## Preparación local (requiere Docker Compose v2)

1. Copia variables: `cp .env.example .env` (PowerShell: `Copy-Item .env.example .env`).
2. Cambia **DATABASE_PASSWORD**, **JWT_SECRET** (mínimo 32 caracteres aleatorios) y **SEED_ADMIN_PASSWORD** (mínimo 12 caracteres). Nunca publiques `.env`.
3. Levanta el stack: `docker compose up --build -d`.
4. Inicializa **solo datos ficticios de demostración**: `docker compose exec backend python -m app.seed`. Esta semilla está prohibida en `APP_ENV=production` y es idempotente.
5. Abre `http://localhost:5173` e ingresa con cuentas demo `admin`, `cajero` o `cocina`, todas con la contraseña **que tú configuraste en .env**.
6. Swagger: `http://localhost:8000/docs`. Health: `http://localhost:8000/api/v1/health`.

> Nunca usar contraseñas demo para cuentas reales. La semilla solo funciona en entornos no productivos.

## Verificación

```bash
# Mismas pruebas que se ejecutan en GitHub Actions
# Si usas Docker, no requiere Python local

docker compose exec backend pytest -q

docker compose exec backend alembic current

# Compilar la interfaz
docker compose exec frontend npm run build
```

En el PR revisa los jobs `Fullstack Quality` (pruebas y migración Postgres / build de React) y `MVP Demonstration Tests`. El XML de pruebas se publica como artefacto de CI. La etiqueta verde de CI verifica ese conjunto concreto de pasos, no una auditoría externa de seguridad o una instalación real.

## Arquitectura

`React + TypeScript → FastAPI → SQLAlchemy → PostgreSQL`, Docker Compose en local. Migraciones versionadas en `backend/alembic/versions`. Servicios principales transaccionales (sin microservicios ni colas para primera versión).

- Dinero en **céntimos enteros**, no flotantes.
- Insumos en unidades base enteras (`g`, `ml`, `unit`); recetas vinculadas al producto.
- Reserva de inventario mediante `UPDATE ... WHERE stock >= cantidad`, atómica en BD.
- Cancelaciones restauran consumos originales registrados en `order_consumptions`.
- Pago único por pedido mediante `UNIQUE(order_id)` y comprobación del total.
- Acceso a endpoints por JWT y validación del rol en servidor.
- Bitácora registra acciones sobre entidades relevantes.

## Limitaciones antes de producción

No incluye integración con SUNAT, pasarelas de pago reales, protección avanzada contra fuerza bruta, restablecimiento de contraseña seguro, versionado de recetas frente a cambios históricos de catálogo ni una política completa de backups y retención. El frontend utiliza sessionStorage para tokens y debe cambiarse a sesiones HttpOnly seguras en un despliegue público. Revisar OWASP ASVS y requerimientos legales de datos personales antes de producción.

## Documentación

- [Arquitectura y decisiones](docs/ARQUITECTURA.md)
- [Plan de QA y criterios de evidencia](docs/PLAN_QA.md)
- [Manual operativo](docs/MANUAL_USUARIO.md)
- [Lista de controles pendientes para producción](docs/CHECKLIST_PRODUCCION.md)
- [MVP previo de demostración (separado)](demo_funcional/README.md)

**Autores:** Jamil Shandee Hinojosa Ttito; Jose Paolo Champi Palacios; Rodolfo Muñoz Cruz; Erik Alexander Callañaupa Quispe. **Docente:** Ing. Néstor Gutiérrez Huamán.