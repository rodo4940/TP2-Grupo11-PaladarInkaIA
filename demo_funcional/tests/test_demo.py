"""Pruebas reales de integración HTTP de un MVP con DB temporal aislada."""
import pytest
from fastapi.testclient import TestClient
from demo_funcional import app as mod

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv('PALADAR_DEMO_DB', str(tmp_path / 'test.sqlite3'))
    mod.SESSIONS.clear()
    mod.init_db()
    with TestClient(mod.app) as client:
        yield client


def login(client, user='admin', password='demo123'):
    r=client.post('/api/login',json={'username':user,'password':password})
    assert r.status_code==200
    return {'Authorization':'Bearer '+r.json()['token']}


def order(client, headers, qty=1, product_id=1):
    return client.post('/api/orders',json={'customer':'Cliente de prueba','items':[{'product_id':product_id,'qty':qty}]},headers=headers)


def test_01_root_serves_real_interface(client):
    r=client.get('/'); assert r.status_code==200; assert 'Ventas / POS' in r.text


def test_02_health_sqlite_ready(client):
    r=client.get('/api/health'); assert r.status_code==200; assert r.json()['status']=='ok'


def test_03_login_ok_and_role(client):
    r=client.post('/api/login',json={'username':'admin','password':'demo123'}); assert r.status_code==200; assert r.json()['role']=='administrador'


def test_04_invalid_password_rejected(client):
    assert client.post('/api/login',json={'username':'admin','password':'bad'}).status_code==401


def test_05_reject_unauthenticated_products(client):
    assert client.get('/api/products').status_code==401


def test_06_list_products_and_recipes(client):
    products=client.get('/api/products',headers=login(client)).json();assert len(products)==3;assert products[0]['price_cents']==3400


def test_07_initial_inventory_valid(client):
    inv=client.get('/api/inventory',headers=login(client)).json();assert len(inv)==4;assert inv[0]['grams']==8000


def test_08_create_order_has_price_and_id(client):
    r=order(client,login(client));assert r.status_code==201; assert r.json()['total_cents']==3400; assert r.json()['order_id']==1


def test_09_order_deducts_recipe_atomically(client):
    h=login(client);r=order(client,h);assert r.status_code==201
    inv=client.get('/api/inventory',headers=h).json(); assert inv[0]['grams']==7740; assert inv[1]['grams']==4820


def test_10_inventory_kardex_trace(client):
    h=login(client);order(client,h)
    m=client.get('/api/movements',headers=h).json(); assert len(m)==3;assert all(x['order_id']==1 and x['delta_grams']<0 for x in m)


def test_11_insufficient_stock_is_rejected_without_write(client):
    h=login(client);assert order(client,h,qty=20,product_id=2).status_code==201
    before=client.get('/api/inventory',headers=h).json()
    r=order(client,h,qty=20,product_id=2);assert r.status_code==409
    assert client.get('/api/inventory',headers=h).json()==before
    assert client.get('/api/dashboard',headers=h).json()['orders']==1


def test_12_unknown_product_404_and_rollback(client):
    h=login(client);r=order(client,h,product_id=999);assert r.status_code==404
    assert client.get('/api/dashboard',headers=h).json()['orders']==0


def test_13_forbid_kitchen_to_create_orders(client):
    assert order(client,login(client,'cocina')).status_code==403


def test_14_forbid_cashier_kitchen_status(client):
    h=login(client);oid=order(client,h).json()['order_id'];r=client.patch(f'/api/orders/{oid}/status',headers=login(client,'cajero'),json={'status':'preparacion'});assert r.status_code==403


def test_15_kitchen_lifecycle_valid(client):
    h=login(client);oid=order(client,h).json()['order_id'];k=login(client,'cocina')
    for status in ['preparacion','listo','entregado']:
        r=client.patch(f'/api/orders/{oid}/status',headers=k,json={'status':status});assert r.status_code==200
    assert client.get('/api/orders',headers=h).json()[0]['status']=='entregado'


def test_16_kitchen_cannot_skip_status(client):
    h=login(client);oid=order(client,h).json()['order_id'];r=client.patch(f'/api/orders/{oid}/status',headers=login(client,'cocina'),json={'status':'entregado'});assert r.status_code==409


def test_17_pay_once_only(client):
    h=login(client);oid=order(client,h).json()['order_id'];assert client.post(f'/api/orders/{oid}/pay',headers=h).status_code==200
    assert client.post(f'/api/orders/{oid}/pay',headers=h).status_code==409


def test_18_report_only_counts_paid(client):
    h=login(client);first=order(client,h).json()['order_id'];order(client,h)
    client.post(f'/api/orders/{first}/pay',headers=h)
    assert client.get('/api/dashboard',headers=h).json()['sales_cents']==3400
    r=client.get('/api/reports/sales',headers=h); assert r.status_code==200;assert r.json()[0]['total_cents']==3400


def test_19_reports_restricted_for_cashier(client):
    assert client.get('/api/reports/sales',headers=login(client,'cajero')).status_code==403


def test_20_restock_requires_admin(client):
    c=login(client,'cajero');assert client.post('/api/inventory/receipts',headers=c,json={'ingredient_id':1,'grams':100}).status_code==403


def test_21_restock_adds_movement(client):
    h=login(client);r=client.post('/api/inventory/receipts',headers=h,json={'ingredient_id':1,'grams':1000});assert r.status_code==201
    assert client.get('/api/inventory',headers=h).json()[0]['grams']==9000
    assert client.get('/api/movements',headers=h).json()[0]['delta_grams']==1000


def test_22_heuristic_transparent_no_fake_ml(client):
    h=login(client);order(client,h,product_id=3)
    r=client.get('/api/recommendations',headers=h).json();assert r['products'][0]['name']=='Pizza Andina';assert 'NO modelo ML' in r['method']


def test_23_audit_responsibility(client):
    h=login(client);order(client,h)
    events=client.get('/api/audit',headers=h).json();assert events[0]['kind']=='pedido';assert events[0]['actor']=='admin'


def test_24_audit_forbidden_nonadmin(client):
    assert client.get('/api/audit',headers=login(client,'cocina')).status_code==403


def test_25_bad_quantity_rejected(client):
    h=login(client)
    r=client.post('/api/orders',headers=h,json={'customer':'Demo','items':[{'product_id':1,'qty':0}]});assert r.status_code==422


def test_26_nonexistent_order_not_paid(client):
    assert client.post('/api/orders/999/pay',headers=login(client)).status_code==404


def test_27_dashboard_counts_active_vs_delivered(client):
    h=login(client);id=order(client,h).json()['order_id'];k=login(client,'cocina')
    assert client.get('/api/dashboard',headers=h).json()['active_orders']==1
    for status in ['preparacion','listo','entregado']:
        client.patch(f'/api/orders/{id}/status',headers=k,json={'status':status})
    assert client.get('/api/dashboard',headers=h).json()['active_orders']==0