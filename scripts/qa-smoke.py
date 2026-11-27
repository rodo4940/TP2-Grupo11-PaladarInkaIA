"""Smoke HTTP de primer arranque en entorno de desarrollo con datos FICTICIOS.

Se usa desde CI sobre un PostgreSQL temporal. Crea un único pedido ficticio.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.request import Request, urlopen

root=Path(__file__).resolve().parents[1]
values={}
for line in (root/'.env').read_text(encoding='utf-8').splitlines():
    if line and not line.startswith('#') and '=' in line:
        k,v=line.split('=',1);values[k]=v
assert values.get('APP_ENV') != 'production', 'No ejecutar pruebas ficticias en producción'
base=f"http://127.0.0.1:{values.get('BACKEND_PORT','8000')}/api/v1"

def request(method,path,data=None,token=None):
    headers={'Content-Type':'application/json'}
    if token:headers['Authorization']='Bearer '+token
    payload=json.dumps(data).encode() if data is not None else None
    with urlopen(Request(base+path,data=payload,headers=headers,method=method),timeout=12) as response:
        assert 200<=response.status<300,(path,response.status)
        return json.loads(response.read())

print('1. Estado de API y PostgreSQL')
request('GET','/health')
request('GET','/ready')
print('2. Sesión de administrador (contraseña generada localmente)')
login=request('POST','/auth/token',{'username':'admin','password':values['SEED_ADMIN_PASSWORD']})
token=login['access_token']
assert login['user']['role']=='admin'
print('3. Catálogo y creación transaccional de pedido demo')
products=request('GET','/products',token=token)
assert products,'La semilla no cargó productos'
order=request('POST','/orders',{'items':[{'product_id':products[0]['id'],'quantity':1}],'table_label':'QA-SMOKE-CI'},token)
assert order['total_cents']==products[0]['price_cents']
print('4. Kardex y cobro único')
movements=request('GET','/inventory/movements',token=token)
assert any(m['reference']==f"PEDIDO-{order['id']}" for m in movements)
payment=request('POST',f"/orders/{order['id']}/payment",{'method':'cash','amount_cents':order['total_cents']},token)
assert payment['order_id']==order['id']
report=request('GET','/reports/sales',token=token)
assert report['paid_orders']>=1 and report['sales_cents']>=order['total_cents']
print('OK: health, ready, auth, catálogo, pedido, Kardex, pago y reportes. Datos ficticios.')