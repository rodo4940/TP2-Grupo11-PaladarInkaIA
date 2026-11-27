# Plan de validación de IA predictiva

## Afirmación verificable actual
La API `/ai/demand-forecast` usa una media móvil ponderada de siete días y un rango orientativo **no calibrado**. El asistente puede consultar indicadores agregados y responder con reglas explicables. Esto **no es entrenamiento ni validación estadística de un modelo ML**.

## Insumos para pasar a un modelo entrenado
- Recabar al menos 8–12 semanas (preferiblemente más, incluyendo días de baja demanda, festivos y cambios de menú) de cantidades vendidas **autorizadas** por producto, agregadas por fecha local.
- Excluir pedidos anulados y descontar devoluciones confirmadas según regla comercial documentada. Evaluar mermas y cambios de stock por separado.
- No exportar nombres, teléfonos, DNI, datos de tarjetas, vouchers ni texto libre de clientes.
- Registrar porcentaje de fechas sin datos y distinguir entre "cero ventas" y "sistema sin operación".
- Preservar SHA-256 de dataset, consentimiento, diccionario de datos, versión y periodos de entrenamiento.

## Experimento mínimo reproducible
1. Ordenar por fecha, reservar el tramo final (por ejemplo últimas 2 semanas) como holdout SIN usarlo para elegir hiperparámetros.
2. Entrenar solo con fechas anteriores. Comparar media móvil actual, naive estacional (mismo día de semana) y un regresor con variables de calendario y rezagos.
3. Evaluar MAE, WAPE y sesgo por SKU, sin fuga temporal. Reportar horizontes 1 y 7 días, tamaño y volatilidad de cada grupo.
4. Aprobar un modelo solo cuando supere baselines con margen útil, estabilidad y revisión humana; registrar errores en días con stock agotado.
5. Incorporar inferencia tras aprobación con control de versión, fallback a heurística, monitoreo de drift y rollback de modelo.

## Criterios de aceptación propuestos (sujetos a acuerdo)
- Evaluación temporal real, sin datos sintéticos etiquetados como comerciales.
- MAE/WAPE no peor que baseline por un margen acordado y error documentado por producto.
- El backend expone `model_version`, fecha de datos y `method`; aviso de baja confianza visible.
- Ensayar fallos, latencia y ausencia de dataset; ninguna IA modifica dinero, pedidos o stock por sí sola.

**Estado:** PENDIENTE DATASET AUTORIZADO Y EVALUACIÓN REAL. El proyecto puede ser piloto con heurística claramente etiquetada; no afirmar "IA predictiva entrenada".
