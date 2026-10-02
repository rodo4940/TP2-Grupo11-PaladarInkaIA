# Plan Scrum - Paladar Inka IA

Este documento resume la organizacion agil del proyecto para el Anexo 05 y se mantiene alineado con el alcance del proyecto original.

## Alcance funcional de la primera version

- productos y categorias;
- clientes y consulta de DNI;
- pedidos y ventas;
- inventario y disponibilidad;
- pagos manuales;
- portal publico por QR;
- usuarios y roles;
- asistente IA mediante API de LLM y Tools / Function Calling.

Quedan fuera de esta primera version el pronostico de demanda, RAG, fine-tuning y el entrenamiento de modelos propios.

## Roles Scrum

- Product Owner: Jamil Shandee Hinojosa Ttito.
- Scrum Master: Jose Paolo Champi Palacios.
- Developers: Rodolfo Munoz Cruz, Erik Alexander Callanaupa Quispe y colaboracion tecnica del equipo.

Los roles se usan para organizar el trabajo academico. La responsabilidad sobre el incremento es compartida por el equipo de desarrollo.

## Definition of Ready

Una historia puede entrar a un Sprint cuando:

1. tiene objetivo y valor entendible;
2. posee criterios de aceptacion verificables;
3. identifica dependencias principales;
4. puede estimarse y completarse dentro del Sprint;
5. no depende de una funcionalidad futura fuera del alcance.

## Definition of Done

Una tarea se considera terminada cuando:

1. el codigo esta versionado;
2. las validaciones principales estan implementadas;
3. existen pruebas automatizadas cuando corresponde;
4. las pruebas pasan en el entorno del equipo;
5. no contiene secretos ni datos personales reales;
6. la documentacion afectada esta actualizada;
7. el incremento puede demostrarse.

## Product Backlog priorizado

| ID | Historia / necesidad | Prioridad |
| --- | --- | --- |
| HU-01 | Autenticacion y acceso por roles | Alta |
| HU-02 | Gestion de productos y categorias | Alta |
| HU-03 | Gestion de clientes y consulta DNI | Media |
| HU-04 | Registro y seguimiento de pedidos | Alta |
| HU-05 | Registro de ventas y calculo de totales | Alta |
| HU-06 | Control de inventario y disponibilidad | Alta |
| HU-07 | Pagos manuales y validacion administrativa | Alta |
| HU-08 | Portal publico por QR y carta digital | Alta |
| HU-09 | Consulta de estado de pedido | Media |
| HU-10 | Asistente IA con Tools / Function Calling | Media |
| HU-11 | Usuarios y ajustes | Media |
| HU-12 | Pruebas, documentacion y cierre | Alta |

## Plan por Sprints

### Sprint 1 - Base tecnica y acceso

Objetivo: disponer de una base ejecutable con backend, frontend, persistencia, autenticacion inicial y pruebas basicas.

### Sprint 2 - Flujo operativo

Objetivo: implementar productos, clientes, inventario, pedidos, ventas y pagos manuales con reglas de negocio en backend.

### Sprint 3 - Portal, asistente IA y calidad

Objetivo: completar portal QR, consultas de estado, asistente mediante Function Calling, pruebas finales, manuales y demostracion.

## Flujo del tablero

Backlog -> To Do -> In Progress -> Review / Test -> Done.

Cada tarjeta debe conservar el ID de historia, responsable, criterios de aceptacion y evidencia. Si aparece un defecto, el item vuelve a In Progress hasta corregirse y volver a probarse.

## Trazabilidad

Historia -> tarea -> rama/commit -> prueba -> evidencia.

Ejemplo: HU-06 -> validacion de stock -> commit correspondiente -> prueba automatizada -> captura o salida de ejecucion.
