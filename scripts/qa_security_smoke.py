"""Seguridad: controles HTTP verificables y reproducibles, NO pentest ni OWASP certificado.

Todos los tests ejecutan la API real en un entorno temporal con datos ficticios.
No se envían contraseñas ni tokens al archivo de resultados.
"""
import json
import os
from pathlib import Path
from datetime import datetime,timezone
import httpx

ROOT=os.getenv('E2E_API_URL','http://127.0.0.1:8000/api/v1')
PWD=os.environ['SEED_ADMIN_PASSWORD']
OUT=Path('e2e/evidencias')
OUT.mkdir(parents=True,exist_ok=True)
checks=[]
with httpx.Client(base_url=ROOT,timeout=10.0) as c:
    def test(name, actual, expected, context):
        success=actual==expected
        checks.append({'id':f'SEC-{len(checks)+1:02d}','name':name,'expected':expected,'actual':actual,'success':success,'context':context})
        print(('PASS' if success else 'FAIL'),name,actual,flush=True)
    for path in ['/health','/ready']:
        response=c.get(path);test('Disponibilidad pública '+path,response.status_code,200,'GET '+path)
    for path in ['/auth/me','/users','/orders','/ingredients','/audit','/products/manage','/customers','/reports/sales']:
        response=c.get(path);test('Sin token '+path,response.status_code,401,'GET '+path)
    invalid=c.post('/auth/token',json={'username':'admin','password':'not-the-password'})
    test('Credenciales incorrectas',invalid.status_code,401,'POST /auth/token')
    own=c.post('/auth/token',json={'username':'admin','password':PWD})
    test('Administrador válido',own.status_code,200,'POST /auth/token')
    admin={'Authorization':'Bearer '+own.json()['access_token']}
    cooking=c.post('/auth/token',json={'username':'cocina','password':PWD})
    test('Cocina autenticada',cooking.status_code,200,'POST /auth/token')
    kitchen={'Authorization':'Bearer '+cooking.json()['access_token']}
    for path in ['/users','/audit','/reports/sales','/customers']:
        r=c.get(path,headers=kitchen);test('Rol cocina denegado '+path,r.status_code,403,'GET '+path)
    for path,data in [('/orders',{'items':[{'product_id':1,'quantity':0}]}),('/products',{'sku':'QA_INVALID','name':'X','price_cents':-1})]:
        r=c.post(path,json=data,headers=admin);test('Payload inválido '+path,r.status_code,422,'POST '+path)
    bad=c.post('/ingredients/1/adjust',json={'delta':-99999999,'reason':'Test negativo de stock'},headers=admin)
    test('Protección de stock no negativo',bad.status_code,409,'POST /ingredients/1/adjust')
    bad_role=c.post('/ingredients/1/adjust',json={'delta':100,'reason':'Usuario cocina sin permiso'},headers=kitchen)
    test('Solo admin cambia stock',bad_role.status_code,403,'POST /ingredients/1/adjust')
    r=c.options('/orders',headers={'Origin':'https://evil.invalid','Access-Control-Request-Method':'POST'})
    test('CORS no acepta origen externo',int(r.headers.get('access-control-allow-origin')=='https://evil.invalid'),0,'OPTIONS /orders')
    r=c.get('/health')
    for key,expected in [('x-content-type-options','nosniff'),('x-frame-options','DENY')]:
        test('Cabecera '+key,r.headers.get(key),expected,'GET /health')
    r=c.get('/auth/me',headers=admin)
    test('JWT administrador vigente',r.status_code,200,'GET /auth/me')
    fake={'Authorization':'Bearer invalid.signature.token'}
    r=c.get('/auth/me',headers=fake)
    test('JWT inválido denegado',r.status_code,401,'GET /auth/me')
    r=c.get('/users',headers=admin)
    test('RBAC admin lista colaboradores',r.status_code,200,'GET /users')

report={'name':'Security HTTP smoke - Paladar Inka AI', 'scope':'API CI temporal con datos ficticios; no equivalente a pentest, OWASP ZAP, WCAG, auditoría externa ni UAT', 'timestamp_utc':datetime.now(timezone.utc).isoformat(), 'count':len(checks), 'passed':sum(i['success'] for i in checks),'failed':sum(not i['success'] for i in checks),'cases':checks}
(OUT/'security-smoke-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert report['failed']==0,f"Fallaron {report['failed']} casos de seguridad: {[x['id'] for x in checks if not x['success']]}"
print('SECURITY SMOKE:',report['passed'],'/',report['count'],'VERIFIED',flush=True)