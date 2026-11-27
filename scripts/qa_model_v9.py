"""Exporta métricas reproducibles de IA sintética + 16 escenarios de prueba.

Solo se ejecuta tras pytest satisfactorio. No crea firmas/UAT comerciales.
"""
from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
import csv

from app.domain.trained_forecast import trained_demo, demo_predictions, synthetic_history

folder=Path('e2e/lab-v9')
folder.mkdir(parents=True,exist_ok=True)
model=trained_demo()
forecast=demo_predictions(7)
assert model['dataset_origin']=='GENERADO_FICTICIO_DE_LABORATORIO'
assert all(v['samples_test']==28 for v in model['products'].values())
with (folder/'METRICAS_MODELO_DEMO.json').open('w',encoding='utf-8') as f:
    json.dump(model,f,ensure_ascii=False,indent=2)
with (folder/'PREDICCIONES_DEMO_7_DIAS.json').open('w',encoding='utf-8') as f:
    json.dump(forecast,f,ensure_ascii=False,indent=2)
with (folder/'DATASET_SINTETICO_AGREGADO.csv').open('w',encoding='utf-8',newline='') as f:
    rows=synthetic_history()
    writer=csv.writer(f);writer.writerow(['dia_relativo','producto_demo','unidades_ficticias'])
    for sku,values in rows.items():
        for t,val in enumerate(values):writer.writerow([t,sku,val])
manifest=[]
for path in sorted(folder.glob('*')):
    if path.is_file():
        manifest.append({'file':path.name,'sha256':sha256(path.read_bytes()).hexdigest(),
                         'bytes':path.stat().st_size})
with (folder/'MANIFIESTO_SHA256.json').open('w',encoding='utf-8') as f:
    json.dump({'git_sha':os.getenv('GITHUB_SHA','no definido'),
               'source':'Generación ficticia por código de laboratorio',
               'commercial_uat_executed':False,
               'real_sunat_emission':False,
               'business_model_trained':False,
               'generated_utc':datetime.now(timezone.utc).isoformat(),
               'files':manifest},f,ensure_ascii=False,indent=2)
print('ML LAB',model['dataset_sha256'],
      {sku:row['holdout'] for sku,row in model['products'].items()})
print('NO UAT EMPRESARIAL, NO EMISIÓN SUNAT',flush=True)
