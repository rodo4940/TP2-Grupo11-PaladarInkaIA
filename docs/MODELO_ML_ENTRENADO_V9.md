# Entrenamiento real, datos sintéticos — IA predictiva v9

**Qué sí está implementado:** un modelo Ridge de regresión multivariable estimado mediante mínimos cuadrados regularizados, con tendencia temporal y efectos del día de la semana. Entrena tres series diarias de SKUs de laboratorio reproducibles con semilla fija. Evalúa errores fuera de muestra (holdout cronológico) frente a promedio móvil de siete días y registra SHA-256 del dataset.

**Qué NO se ha demostrado:** predicción de ventas reales de la pizzería, causalidad, validación en ventas observadas o autorización para reponer productos.

## Datos y separación
- Generador determinista: `backend/app/domain/trained_forecast.py`, sin datos personales.
- 140 días sintéticos por SKU, 112 días de entrenamiento, 28 días finales de evaluación con separación por tiempo.
- Características: intercepto, tendencia en días, siete indicadores de día semanal, regularización L2.
- Métricas: MAE, WAPE, sesgo; referencia de ventana móvil de 7 días.
- SHA-256 del dataset almacenado en `METRICAS_MODELO_DEMO.json` generado por `scripts/qa_model_v9.py`.

## Integración
- `GET /ai/trained-demo/metrics`: retorna versión, procedencia, periodos, coeficientes ajustados y métricas.
- `GET /ai/trained-demo/forecast?days=7`: pronósticos sintéticos de 1 a 14 días.
- Dashboard: panel educativo etiquetado **MODELO ENTRENADO CON DATOS FICTICIOS**.
- `/ai/demand-forecast` existente: sigue usando **media ponderada descriptiva sobre los pagos reales del entorno conectado**; no mezcla predicciones de laboratorio con operaciones comerciales.
- No promueve automáticamente modelos, no mueve inventario ni dinero.

## Entrenamiento empresarial futuro (requiere datos externos)
1. Autorizar uso de registros históricos agregados por día, SKU y cantidades, sin DNI/teléfono/nombres.
2. Establecer inicio real, días sin operación, roturas de stock, feriados, precios y cambios de menú.
3. Entrenar con holdout temporal del negocio y comparar con baselines reales.
4. Registrar MAE/WAPE por categoría, sesgo, deriva, versión de dataset y reglas de promoción; contar con aprobación por responsable.
5. Solo después activar un modelo empresarial con monitoreo y rollback.

**Estado del componente de IA:** modelo de laboratorio efectivamente entrenable y evaluable, pero **no un modelo comercial entrenado con datos autorizados de El Paladar del Inka**.
