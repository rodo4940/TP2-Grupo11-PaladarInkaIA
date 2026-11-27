"""Pruebas de integración para caja y devoluciones manuales.

Usa Base.metadata.create_all sobre SQLite solo como fixture de test;
la migración real se valida aparte en CI con PostgreSQL.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

from tests.test_business import post_order, env


def _payment(client, auth, method='cash'):
    order = post_order(client, auth['cashier'])
    assert order.status_code == 201, order.text
    paid = client.post(
        f"/api/v1/orders/{order.json()['id']}/payment",
        headers=auth['cashier'], json={'method': method, 'amount_cents': 3200})
    assert paid.status_code == 201, paid.text
    return paid.json()


def test_manual_refund_requires_two_people_and_keeps_payment_history(env):
    client, auth, session = env
    payment = _payment(client, auth, 'yape')
    request = client.post('/api/v1/billing/refunds', headers=auth['cashier'],
                          json={'payment_id': payment['id'], 'reason': 'Cliente reporta doble cobro externo'})
    assert request.status_code == 201, request.text
    refund = request.json()
    assert refund['amount_cents'] == 3200 and refund['status'] == 'pending'
    assert 'No ejecuta' in refund['disclaimer']
    assert client.post('/api/v1/billing/refunds', headers=auth['cashier'],
                       json={'payment_id': payment['id'], 'reason': 'Repetición no válida'}).status_code == 409
    assert client.post(f"/api/v1/billing/refunds/{refund['id']}/confirm",
                       headers=auth['cashier'], json={'external_reference': 'YAPE-123456'}).status_code == 403
    assert client.post(f"/api/v1/billing/refunds/{refund['id']}/confirm",
                       headers=auth['kitchen'], json={'external_reference': 'YAPE-123456'}).status_code == 403
    confirm = client.post(f"/api/v1/billing/refunds/{refund['id']}/confirm",
                          headers=auth['admin'], json={'external_reference': 'YAPE-123456'})
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()['status'] == 'confirmed'
    assert client.post(f"/api/v1/billing/refunds/{refund['id']}/confirm",
                       headers=auth['admin'], json={'external_reference': 'YAPE-789000'}).status_code == 409
    ledger = client.get('/api/v1/billing/ledger', headers=auth['cashier']).json()
    assert ledger['total_cents'] == 3200  # Pago original inmutable.
    assert ledger['confirmed_refunds_cents'] == 3200
    assert ledger['net_registered_cents'] == 0
    assert ledger['entries'][0]['refund_status'] == 'confirmed'
    assert ledger['entries'][0]['net_cents'] == 0
    report = client.get('/api/v1/reports/sales', headers=auth['cashier']).json()
    assert report['gross_payments_cents'] == 3200
    assert report['confirmed_refunds_cents'] == 3200
    assert report['sales_cents'] == 0
    assert report['paid_orders'] == 0
    dashboard = client.get('/api/v1/dashboard', headers=auth['cashier']).json()
    assert dashboard['sales_cents'] == 0
    forecast = client.get('/api/v1/ai/demand-forecast', headers=auth['cashier']).json()
    assert forecast['sample_paid_orders_7d'] == 0
    assert client.get('/api/v1/orders', headers=auth['admin']).json()[0]['paid'] is True
    with session() as db:
        from sqlalchemy import select
        from app.domain.models import Ingredient, StockMovement
        assert db.scalar(select(Ingredient).where(Ingredient.sku=='HAR')).stock == 800
        assert not list(db.scalars(select(StockMovement).where(StockMovement.reference.like('DEVOLUCION%'))))


def test_refunds_validate_missing_payment_and_roles(env):
    client, auth, _ = env
    payload={'payment_id': 999999, 'reason': 'Motivo suficientemente explícito'}
    assert client.post('/api/v1/billing/refunds', json=payload).status_code == 401
    assert client.post('/api/v1/billing/refunds', headers=auth['kitchen'], json=payload).status_code == 403
    assert client.post('/api/v1/billing/refunds', headers=auth['cashier'], json=payload).status_code == 404
    assert client.get('/api/v1/billing/refunds', headers=auth['kitchen']).status_code == 403
    assert client.get('/api/v1/billing/refunds', headers=auth['admin']).json() == []


def test_refund_requester_cannot_approve_own_request(env):
    client, auth, _ = env
    payment = _payment(client, auth)
    request = client.post('/api/v1/billing/refunds', headers=auth['admin'],
                          json={'payment_id':payment['id'],'reason':'Reverso con doble control'}).json()
    res = client.post(f"/api/v1/billing/refunds/{request['id']}/confirm",
                      headers=auth['admin'], json={'external_reference':'CASH-RECEIPT-01'})
    assert res.status_code == 409


def test_cash_closeout_persisted_and_approved_by_distinct_users(env):
    client, auth, _ = env
    payment = _payment(client, auth, 'cash')
    day = datetime.now(ZoneInfo('America/Lima')).date().isoformat()
    summary = client.get('/api/v1/billing/daily-summary', params={'day':day},
                         headers=auth['cashier']).json()
    assert summary['gross_payments_cents'] == 3200
    submit = client.post('/api/v1/billing/closeouts', headers=auth['cashier'],
                         json={'day':day, 'opening_cash_cents':1000,
                               'counted_cash_cents':4250, 'note':'Arqueo de prueba con fondo inicial'})
    assert submit.status_code == 201, submit.text
    data = submit.json()
    assert data['expected_cash_cents'] == 4200
    assert data['variance_cents'] == 50
    assert data['state'] == 'submitted' and data['stale'] is False
    assert client.post('/api/v1/billing/closeouts', headers=auth['cashier'],
                       json={'day':day,'opening_cash_cents':0,'counted_cash_cents':0}).status_code == 409
    assert client.post(f"/api/v1/billing/closeouts/{data['id']}/approve",
                       headers=auth['cashier'],
                       json={'approval_note':'Contado y revisado'}).status_code == 403
    approved=client.post(f"/api/v1/billing/closeouts/{data['id']}/approve",
                         headers=auth['admin'],
                         json={'approval_note':'Vouchers y diferencia verificados fuera del sistema'})
    assert approved.status_code == 200, approved.text
    assert approved.json()['state'] == 'approved'
    assert approved.json()['approved_by'] is not None
    check=client.get(f"/api/v1/billing/closeouts/{day}", headers=auth['cashier'])
    assert check.status_code == 200 and check.json()['state'] == 'approved'
    assert client.get('/api/v1/billing/daily-summary', headers=auth['cashier'],
                      params={'day':day}).json()['internal_closeout_state']=='approved'
    assert client.post(f"/api/v1/billing/closeouts/{data['id']}/approve",
                       headers=auth['admin'],
                       json={'approval_note':'Aprobación repetida'}).status_code == 409


def test_cash_closeout_rejects_stale_snapshot_and_self_approval(env):
    client, auth, _ = env
    day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
    submit=client.post('/api/v1/billing/closeouts', headers=auth['admin'],
                       json={'day':day,'opening_cash_cents':0,'counted_cash_cents':0})
    assert submit.status_code == 201
    record=submit.json()
    assert client.post(f"/api/v1/billing/closeouts/{record['id']}/approve",
                       headers=auth['admin'],
                       json={'approval_note':'No puede aprobar su propia caja'}).status_code==409
    _payment(client, auth)
    stale=client.get(f"/api/v1/billing/closeouts/{day}", headers=auth['cashier'])
    assert stale.json()['stale'] is True
    bad=client.post(f"/api/v1/billing/closeouts/{record['id']}/approve",
                    headers=auth['admin'],
                    json={'approval_note':'Diferencia pendiente de revisión'})
    assert bad.status_code==409


def test_cash_closeout_role_and_invalid_future_date(env):
    from datetime import timedelta
    client, auth, _=env
    today=datetime.now(ZoneInfo('America/Lima')).date()
    future=(today+timedelta(days=1)).isoformat()
    payload={'day':future,'opening_cash_cents':0,'counted_cash_cents':0}
    assert client.post('/api/v1/billing/closeouts', json=payload).status_code == 401
    assert client.post('/api/v1/billing/closeouts', headers=auth['kitchen'], json=payload).status_code==403
    assert client.post('/api/v1/billing/closeouts', headers=auth['cashier'], json=payload).status_code==422
    assert client.get(f"/api/v1/billing/closeouts/{today.isoformat()}", headers=auth['cashier']).status_code==404


def test_persistent_login_lockout_and_admin_password_reset(env):
    client, auth, _ = env
    url='/api/v1/auth/token'
    for _ in range(4):
        assert client.post(url, json={'username':'cajero','password':'wrong'}).status_code==401
    blocked=client.post(url,json={'username':'cajero','password':'wrong'})
    assert blocked.status_code==429 and int(blocked.headers['Retry-After'])>0
    assert client.post(url,json={'username':'cajero','password':'PasswordSecure123'}).status_code==429
    # No hay recuperación sin una segunda identidad administrativa autorizada.
    reset=client.post('/api/v1/users/2/reset-password', headers=auth['admin'],
                      json={'new_password':'ResetNewSecure456'})
    assert reset.status_code==200, reset.text
    assert client.post(url,json={'username':'cajero','password':'ResetNewSecure456'}).status_code==200
    # Restablecimiento revoca JWT anteriores emitidos a ese usuario.
    assert client.get('/api/v1/auth/me',headers=auth['cashier']).status_code==401
