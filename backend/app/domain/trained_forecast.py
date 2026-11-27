"""Modelo predictivo entrenado con datos de laboratorio 100 % ficticios.

Regresión ridge (mínimos cuadrados regularizados) por SKU con tendencia y
efecto día de semana. Holdout cronológico separado y comparación con
promedio móvil de siete días. SIN datos reales de El Paladar del Inka.
No usar este modelo para comprar stock ni comunicar previsiones comerciales.
"""
from functools import lru_cache
from hashlib import sha256
from datetime import date, timedelta
import json
import math
import random

PRODUCTS={
    'PIZ-CLASICA': {'name':'Pizza clásica (ficticia)','base':21,'trend':0.052,'weekend':13},
    'PIZ-HAWAIANA': {'name':'Pizza hawaiana (ficticia)','base':15,'trend':0.035,'weekend':8},
    'PIZ-VEGETAL': {'name':'Pizza vegetal (ficticia)','base':11,'trend':0.028,'weekend':6},
}
BEGIN=date(2026,3,1)
DAYS=140
TRAIN_DAYS=112


def features(day_index:int)->list[float]:
    day=BEGIN+timedelta(days=day_index)
    return [1.0,day_index/100.0]+[float(day.weekday()==i) for i in range(7)]


def synthetic_history()->dict[str,list[int]]:
    """Muestra determinista únicamente didáctica; no simula pedidos personales."""
    result={}
    for index,(sku,settings) in enumerate(PRODUCTS.items()):
        rng=random.Random(20261126+index*133)
        values=[]
        for t in range(DAYS):
            day=BEGIN+timedelta(days=t)
            day_factor=settings['weekend'] if day.weekday() in (4,5,6) else 0
            values.append(max(0,round(settings['base']+settings['trend']*t+
                    day_factor+rng.gauss(0,2.2))))
        result[sku]=values
    return result


def solve(matrix:list[list[float]],vector:list[float])->list[float]:
    """Eliminación Gauss-Jordan con pivote; falla ante matriz degenerada."""
    n=len(vector)
    aug=[matrix[i][:]+[vector[i]] for i in range(n)]
    for k in range(n):
        pivot=max(range(k,n),key=lambda i:abs(aug[i][k]))
        if abs(aug[pivot][k])<1e-10:raise ArithmeticError('Matriz no invertible')
        aug[k],aug[pivot]=aug[pivot],aug[k]
        scale=aug[k][k]
        aug[k]=[v/scale for v in aug[k]]
        for i in range(n):
            if i==k:continue
            factor=aug[i][k]
            aug[i]=[aug[i][j]-factor*aug[k][j] for j in range(n+1)]
    return [aug[i][-1] for i in range(n)]


def train(y:list[int],end:int=TRAIN_DAYS,regularization:float=.1)->list[float]:
    if len(y)<end or end<28:raise ValueError('Historial insuficiente')
    dim=len(features(0))
    gram=[[0.0]*dim for _ in range(dim)]
    target=[0.0]*dim
    for day in range(end):
        x=features(day)
        for i in range(dim):
            target[i]+=x[i]*y[day]
            for j in range(dim):gram[i][j]+=x[i]*x[j]
    for i in range(dim):gram[i][i]+=regularization
    return solve(gram,target)


def predict(weights:list[float],t:int)->float:
    return max(0.0,sum(x*w for x,w in zip(features(t),weights)))


def score(actual:list[int],predicted:list[float])->dict:
    if len(actual)!=len(predicted) or not actual:raise ValueError('Muestra inválida')
    absolute=sum(abs(y-yhat) for y,yhat in zip(actual,predicted))
    return {'mae':round(absolute/len(actual),4),
            'wape_pct':round(100*absolute/max(1,sum(actual)),3),
            'bias_units':round(sum(yhat-y for y,yhat in zip(actual,predicted))/len(actual),3)}


@lru_cache(maxsize=1)
def trained_demo()->dict:
    data=synthetic_history()
    sha=sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    trained={}
    for sku,values in data.items():
        weights=train(values)
        heldout=values[TRAIN_DAYS:]
        predictions=[predict(weights,t) for t in range(TRAIN_DAYS,DAYS)]
        baselines=[sum(values[t-7:t])/7 for t in range(TRAIN_DAYS,DAYS)]
        trained[sku]={
            'name':PRODUCTS[sku]['name'],
            'coefficients':[round(w,9) for w in weights],
            'holdout':score(heldout,predictions),
            'baseline':score(heldout,baselines),
            'samples_train':TRAIN_DAYS,
            'samples_test':DAYS-TRAIN_DAYS,
            'quality_gate_passed':score(heldout,predictions)['mae']<=score(heldout,baselines)['mae'],
        }
    return {
        'model_type':'ridge_regression_9_features',
        'model_version':'ridge-demo-synthetic-v1',
        'dataset_origin':'GENERADO_FICTICIO_DE_LABORATORIO',
        'dataset_sha256':sha,
        'source_business_data':False,
        'train_period':f'{BEGIN.isoformat()}..{(BEGIN+timedelta(days=TRAIN_DAYS-1)).isoformat()}',
        'holdout_period':f'{(BEGIN+timedelta(days=TRAIN_DAYS)).isoformat()}..{(BEGIN+timedelta(days=DAYS-1)).isoformat()}',
        'products':trained,
        'warning':'Modelo entrenado y evaluado SOLO con series sintéticas. No validado con ventas de la pizzería.'
    }


def demo_predictions(horizon:int=7)->dict:
    if horizon<1 or horizon>14:raise ValueError('Horizonte fuera de rango')
    result=trained_demo()
    last_index=DAYS
    rows=[]
    for sku,item in result['products'].items():
        weights=item['coefficients']
        predictions=[{'day':(BEGIN+timedelta(days=t)).isoformat(),
                      'units':max(0,round(predict(weights,t)))}
                     for t in range(last_index,last_index+horizon)]
        rows.append({'sku':sku,'name':item['name'],'predictions':predictions,
                     'mae_holdout':item['holdout']['mae'],
                     'baseline_mae':item['baseline']['mae'],
                     'quality_gate_passed':item['quality_gate_passed']})
    return {'mode':'DEMO_MODELO_ENTRENADO_DATOS_SINTETICOS','model_version':result['model_version'],
            'dataset_origin':result['dataset_origin'],'dataset_sha256':result['dataset_sha256'],
            'train_period':result['train_period'],'holdout_period':result['holdout_period'],
            'horizon_days':horizon,'items':rows,'warning':result['warning']}


def train_on_authorized_daily_series(series:list[int],train_days:int)->dict:
    """Ruta de entrenamiento sin efectos secundarios para dataset agregado autorizado.

    Exige entrenamiento cronológico y holdout; NO persiste ni activa el modelo
    empresarial automáticamente. Entradas deben ser series diarias consecutivas
    y sin identidad de clientes.
    """
    if len(series)<70 or train_days<42 or len(series)-train_days<14:
        raise ValueError('Exige >=70 días y holdout temporal >=14 días')
    if any(type(x) is not int or x<0 for x in series):
        raise ValueError('Solo unidades vendidas enteras y no negativas')
    # La referencia temporal del índice se conserva en ambas particiones.
    weights=train(series,train_days)
    pred=[predict(weights,t) for t in range(train_days,len(series))]
    baseline=[sum(series[t-7:t])/7 for t in range(train_days,len(series))]
    return {'coefficients':weights,'holdout':score(series[train_days:],pred),
            'baseline':score(series[train_days:],baseline),'promoted':False,
            'requires_business_authorization':True}
