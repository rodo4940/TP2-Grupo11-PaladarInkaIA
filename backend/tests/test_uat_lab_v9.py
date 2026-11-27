"""16 escenarios funcionales de laboratorio mapeados a la matriz UAT.

AQUÍ NO PARTICIPA EL RESTAURANTE: es una SIMULACIÓN HTTP con SQLite aislada.
La UAT comercial presencial y firma permanecen pendientes de evidencia externa.
"""
from datetime import datetime
from zoneinfo import ZoneInfo
import pytest
from tests.test_business import env,post_order


def pay(client,actor,order_id:int,method='cash'):
    result=client.post(f'/api/v1/orders/{order_id}/payment',headers=actor,
        json={'method':method,'amount_cents':3200})
    assert result.status_code==201,result.text
    return result.json()


@pytest.mark.parametrize('scenario',range(1,17),ids=[f'LAB-UAT-{i:02}' for i in range(1,17)])
def test_16_functional_lab_scenarios(env,scenario):
    client,roles,_=env
    cashier=roles['cashier'];admin=roles['admin'];kitchen=roles['kitchen']
    if scenario==1:
        assert client.get('/api/v1/auth/me',headers=cashier).status_code==200
    elif scenario==2:
        assert client.get('/api/v1/customers',headers=kitchen).status_code==403
        assert client.get('/api/v1/billing/ledger',headers=kitchen).status_code==403
    elif scenario==3:
        assert post_order(client,cashier).status_code==201
    elif scenario==4:
        assert post_order(client,cashier,quantity=100).status_code==409
        assert client.get('/api/v1/orders',headers=admin).json()==[]
    elif scenario==5:
        order=post_order(client,cashier)
        assert order.status_code==201
        movements=client.get('/api/v1/inventory/movements',headers=cashier).json()
        assert len(movements)==2
    elif scenario==6:
        oid=post_order(client,cashier).json()['id']
        for status in ('preparing','ready','delivered'):
            r=client.patch(f'/api/v1/orders/{oid}/status',
                    headers=kitchen,json={'status':status})
            assert r.status_code==200,r.text
    elif scenario==7:
        oid=post_order(client,cashier).json()['id']
        pay(client,cashier,oid)
        assert client.post(f'/api/v1/orders/{oid}/payment',headers=cashier,
               json={'method':'cash','amount_cents':3200}).status_code==409
    elif scenario==8:
        oid=post_order(client,cashier).json()['id']
        pay(client,cashier,oid)
        receipt=client.get(f'/api/v1/orders/{oid}/receipt',headers=cashier).json()
        assert 'NO_TRIBUTARIO' in receipt['type']
    elif scenario==9:
        oid=post_order(client,cashier).json()['id'];pay(client,cashier,oid)
        day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
        s=client.get('/api/v1/billing/daily-summary',headers=cashier,params={'day':day})
        assert s.status_code==200 and s.json()['payments_count']==1
    elif scenario==10:
        oid=post_order(client,cashier).json()['id']
        payment=pay(client,cashier,oid)
        req=client.post('/api/v1/billing/refunds',headers=cashier,json={
            'payment_id':payment['id'],'reason':'Anulación en laboratorio, no transferencia bancaria'})
        assert req.status_code==201 and req.json()['status']=='pending'
    elif scenario==11:
        oid=post_order(client,cashier).json()['id']
        payment=pay(client,cashier,oid)
        req=client.post('/api/v1/billing/refunds',headers=cashier,json={
            'payment_id':payment['id'],'reason':'Reintegro registrado por laboratorio QA'}).json()
        assert client.post(f"/api/v1/billing/refunds/{req['id']}/confirm",
               headers=admin,json={'external_reference':'LAB-REF-011'}).status_code==200
        assert client.post(f"/api/v1/billing/refunds/{req['id']}/confirm",
               headers=cashier,json={'external_reference':'LAB-REF-012'}).status_code==403
    elif scenario==12:
        day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
        s=client.post('/api/v1/billing/closeouts',headers=cashier,json={
            'day':day,'opening_cash_cents':1000,'counted_cash_cents':1000})
        assert s.status_code==201 and s.json()['variance_cents']==0
    elif scenario==13:
        day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
        s=client.post('/api/v1/billing/closeouts',headers=cashier,json={
            'day':day,'opening_cash_cents':0,'counted_cash_cents':0}).json()
        oid=post_order(client,cashier).json()['id']
        pay(client,cashier,oid)
        assert client.get(f"/api/v1/billing/closeouts/{day}",headers=cashier).json()['stale']
        assert client.post(f"/api/v1/billing/closeouts/{s['id']}/approve",
            headers=admin,json={'approval_note':'Datos están desactualizados'}).status_code==409
    elif scenario==14:
        assert client.get('/api/v1/billing/daily-summary',headers=kitchen).status_code==403
        assert client.get('/api/v1/ai/trained-demo/metrics',headers=kitchen).status_code==403
        # E2E real de interfaz responsive se ejecuta en workflow Chromium independiente.
    elif scenario==15:
        model=client.get('/api/v1/ai/trained-demo/metrics',headers=cashier)
        assert model.status_code==200
        assert model.json()['source_business_data'] is False
    else:
        # Seguridad de superficie API, no restauración productiva ni UAT presencial.
        r=client.get('/api/v1/system/info',headers=admin)
        assert r.status_code==200
        assert r.headers.get('x-content-type-options')=='nosniff'


def test_final_closeout_hash_freeze_and_role_security(env):
    client,roles,TestSession=env
    cashier=roles['cashier'];admin=roles['admin']
    day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
    order=post_order(client,cashier)
    pay(client,cashier,order.json()['id'])
    submitted=client.post('/api/v1/billing/closeouts',headers=cashier,json={
        'day':day,'opening_cash_cents':500,'counted_cash_cents':3700})
    assert submitted.status_code==201,submitted.text
    closeout_id=submitted.json()['id']
    assert client.post(f'/api/v1/billing/closeouts/{closeout_id}/finalize',
          headers=admin,json={'final_note':'No se debe finalizar antes de aprobar'}).status_code==409
    approved=client.post(f'/api/v1/billing/closeouts/{closeout_id}/approve',headers=admin,json={
        'approval_note':'Contado y conciliado íntegramente en laboratorio'})
    assert approved.status_code==200,approved.text
    final=client.post(f'/api/v1/billing/closeouts/{closeout_id}/finalize',headers=admin,json={
        'final_note':'Cierre final de prueba, sin fondos reales'})
    assert final.status_code==200,final.text
    assert final.json()['state']=='finalized'
    assert len(final.json()['snapshot_sha256'])==64
    integrity=client.get(f'/api/v1/billing/closeouts/{day}/integrity',headers=cashier)
    assert integrity.json()['hash_valid'] is True
    assert integrity.json()['movements_unchanged'] is True
    assert client.post(f'/api/v1/billing/closeouts/{closeout_id}/finalize',headers=admin,json={
        'final_note':'No permitir cierre definitivo repetido'}).status_code==409
    new_order=post_order(client,cashier)
    assert new_order.status_code==201
    assert client.post(f"/api/v1/orders/{new_order.json()['id']}/payment",
        headers=cashier,json={'method':'cash','amount_cents':3200}).status_code==409
    # Una intervención directa sobre DB posterior al cierre detecta el cambio de hash.
    with TestSession() as db:
        from app.domain.models import CashCloseout
        row=db.get(CashCloseout,closeout_id)
        row.counted_cash_cents+=100
        db.commit()
    assert client.get(f'/api/v1/billing/closeouts/{day}/integrity',
                      headers=admin).json()['hash_valid'] is False
