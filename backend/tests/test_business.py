"""Pruebas de integración HTTP con base de datos aislada para la API principal.

No sustituyen pruebas de carga, aceptación empresarial ni auditorías externas.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.domain.auth import hash_password
from app.domain.models import Ingredient, Product, RecipeLine, User, Order, Payment, StockMovement, AuditEvent

@pytest.fixture
def env():
    engine=create_engine('sqlite+pysqlite://',connect_args={'check_same_thread':False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    TestSession=sessionmaker(engine,expire_on_commit=False)
    def override():
        with TestSession() as s:yield s
    app.dependency_overrides[get_db]=override
    with TestSession() as s:
        s.add_all([User(username='admin',full_name='Administradora',role='admin',password_hash=hash_password('PasswordSecure123')),
                   User(username='cajero',full_name='Caja',role='cashier',password_hash=hash_password('PasswordSecure123')),
                   User(username='cocina',full_name='Cocina',role='kitchen',password_hash=hash_password('PasswordSecure123'))])
        s.add_all([Ingredient(sku='HAR',name='Harina',unit='g',stock=1000,minimum_stock=200),
                   Ingredient(sku='MOZ',name='Queso',unit='g',stock=450,minimum_stock=180)])
        s.add(Product(sku='PIZ',name='Pizza prueba',category='Pizzas',price_cents=3200))
        s.commit()
        p=s.scalar(select(Product).where(Product.sku=='PIZ'))
        ing={i.sku:i for i in s.scalars(select(Ingredient))}
        s.add_all([RecipeLine(product_id=p.id,ingredient_id=ing['HAR'].id,amount=200),RecipeLine(product_id=p.id,ingredient_id=ing['MOZ'].id,amount=150)])
        s.commit()
    with TestClient(app) as client:
        def auth(name):
            token=client.post('/api/v1/auth/token',json={'username':name,'password':'PasswordSecure123'}).json()['access_token']
            return {'Authorization':'Bearer '+token}
        yield client, {'admin':auth('admin'),'cashier':auth('cajero'),'kitchen':auth('cocina')}, TestSession
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def post_order(client,headers,quantity=1):
    return client.post('/api/v1/orders',headers=headers,json={'items':[{'product_id':1,'quantity':quantity}],'table_label':'Mesa 4'})

def test_login_invalid_credentials(env):
    c,a,s=env
    assert c.post('/api/v1/auth/token',json={'username':'admin','password':'bad'}).status_code==401

def test_anonymous_denied(env):
    c,a,s=env
    assert c.get('/api/v1/orders').status_code==401

def test_self_profile(env):
    c,a,s=env
    assert c.get('/api/v1/auth/me',headers=a['kitchen']).json()['role']=='kitchen'

def test_product_list_authenticated(env):
    c,a,s=env
    assert len(c.get('/api/v1/products',headers=a['cashier']).json())==1

def test_product_write_restricted(env):
    c,a,s=env
    r=c.post('/api/v1/products',headers=a['kitchen'],json={'sku':'ZZ','name':'Nueva pizza','price_cents':1000})
    assert r.status_code==403

def test_product_creation_and_duplicate(env):
    c,a,s=env
    payload={'sku':'NN','name':'Nuevo producto','price_cents':3500}
    assert c.post('/api/v1/products',headers=a['admin'],json=payload).status_code==201
    assert c.post('/api/v1/products',headers=a['admin'],json=payload).status_code==409

def test_customer_creation(env):
    c,a,s=env
    r=c.post('/api/v1/customers',headers=a['cashier'],json={'name':'Cliente pruebas','phone':'999888777'})
    assert r.status_code==201
    assert len(c.get('/api/v1/customers',headers=a['cashier']).json())==1

def test_order_reduces_stock_and_kardex(env):
    c,a,s=env
    r=post_order(c,a['cashier'])
    assert r.status_code==201,r.text
    assert r.json()['total_cents']==3200
    rows=c.get('/api/v1/ingredients',headers=a['cashier']).json()
    assert {i['sku']:i['stock'] for i in rows}=={'HAR':800,'MOZ':300}
    mov=c.get('/api/v1/inventory/movements',headers=a['cashier']).json()
    assert len(mov)==2 and set(x['delta'] for x in mov)=={-200,-150}

def test_insufficient_stock_rolls_back(env):
    c,a,s=env
    assert post_order(c,a['cashier'],quantity=4).status_code==409
    assert len(c.get('/api/v1/orders',headers=a['admin']).json())==0
    assert {i['sku']:i['stock'] for i in c.get('/api/v1/ingredients',headers=a['admin']).json()}=={'HAR':1000,'MOZ':450}

def test_unknown_product_rejected(env):
    c,a,s=env
    assert c.post('/api/v1/orders',headers=a['cashier'],json={'items':[{'product_id':999,'quantity':1}]}).status_code==404

def test_kitchen_cannot_create_order(env):
    c,a,s=env
    assert post_order(c,a['kitchen']).status_code==403

def test_cashier_cannot_change_kitchen_status(env):
    c,a,s=env; oid=post_order(c,a['cashier']).json()['id']
    assert c.patch(f'/api/v1/orders/{oid}/status',headers=a['cashier'],json={'status':'preparing'}).status_code==403

def test_kitchen_order_lifecycle(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    for state in ['preparing','ready','delivered']:
        r=c.patch(f'/api/v1/orders/{oid}/status',headers=a['kitchen'],json={'status':state})
        assert r.status_code==200,r.text
        assert r.json()['status']==state

def test_order_skipping_status_rejected(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    assert c.patch(f'/api/v1/orders/{oid}/status',headers=a['kitchen'],json={'status':'delivered'}).status_code==409

def test_cancel_restocks_consumption(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    assert c.patch(f'/api/v1/orders/{oid}/status',headers=a['kitchen'],json={'status':'cancelled'}).status_code==200
    rows=c.get('/api/v1/ingredients',headers=a['cashier']).json()
    assert {i['sku']:i['stock'] for i in rows}=={'HAR':1000,'MOZ':450}

def test_cannot_cancel_after_payment(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    assert c.post(f'/api/v1/orders/{oid}/payment',headers=a['cashier'],json={'method':'cash','amount_cents':3200}).status_code==201
    assert c.patch(f'/api/v1/orders/{oid}/status',headers=a['kitchen'],json={'status':'cancelled'}).status_code==409

def test_payment_single_charge(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    payload={'method':'yape','amount_cents':3200}
    assert c.post(f'/api/v1/orders/{oid}/payment',headers=a['cashier'],json=payload).status_code==201
    assert c.post(f'/api/v1/orders/{oid}/payment',headers=a['cashier'],json=payload).status_code==409

def test_payment_invalid_amount(env):
    c,a,s=env;oid=post_order(c,a['cashier']).json()['id']
    assert c.post(f'/api/v1/orders/{oid}/payment',headers=a['cashier'],json={'method':'cash','amount_cents':1}).status_code==422

def test_report_only_paid(env):
    c,a,s=env;oid1=post_order(c,a['cashier']).json()['id'];post_order(c,a['cashier'])
    r=c.get('/api/v1/reports/sales',headers=a['admin']).json()
    assert r['sales_cents']==0
    c.post(f'/api/v1/orders/{oid1}/payment',headers=a['cashier'],json={'method':'cash','amount_cents':3200})
    r=c.get('/api/v1/reports/sales',headers=a['admin']).json()
    assert r['sales_cents']==3200 and r['paid_orders']==1

def test_stock_adjust_restricted(env):
    c,a,s=env
    assert c.post('/api/v1/ingredients/1/adjust',headers=a['cashier'],json={'delta':100,'reason':'Compra validada'}).status_code==403

def test_stock_adjust_no_negative(env):
    c,a,s=env
    assert c.post('/api/v1/ingredients/1/adjust',headers=a['admin'],json={'delta':-2000,'reason':'Mermas inventario'}).status_code==409

def test_stock_adjust_positive(env):
    c,a,s=env
    r=c.post('/api/v1/ingredients/1/adjust',headers=a['admin'],json={'delta':100,'reason':'Compra validada'})
    assert r.status_code==200 and r.json()['stock']==1100

def test_low_stock_alert(env):
    c,a,s=env
    post_order(c,a['cashier'],quantity=2)
    data=c.get('/api/v1/dashboard',headers=a['admin']).json()
    assert any(x['name']=='Queso' for x in data['low_stock'])

def test_recommendations_are_labelled_heuristic(env):
    c,a,s=env
    r=c.get('/api/v1/recommendations',headers=a['admin']).json()
    assert 'heuristico' in r['method'] and r['items'][0]['product_id']==1

def test_audit_admin_only(env):
    c,a,s=env
    post_order(c,a['cashier'])
    assert c.get('/api/v1/audit',headers=a['cashier']).status_code==403
    assert any(x['action']=='order.create' for x in c.get('/api/v1/audit',headers=a['admin']).json())

def test_recipe_requires_valid_ingredient(env):
    c,a,s=env
    assert c.put('/api/v1/products/1/recipe',headers=a['admin'],json=[{'ingredient_id':999,'amount':10}]).status_code==422

def test_create_new_ingredient_and_recipe(env):
    c,a,s=env
    r=c.post('/api/v1/ingredients',headers=a['admin'],json={'sku':'ACE','name':'Aceitunas','unit':'g','stock':500,'minimum_stock':50})
    assert r.status_code==201
    rid=r.json()['id']
    r=c.put('/api/v1/products/1/recipe',headers=a['admin'],json=[{'ingredient_id':rid,'amount':20}])
    assert r.status_code==200
    r=post_order(c,a['cashier'])
    assert r.status_code==201
    assert next(x['stock'] for x in c.get('/api/v1/ingredients',headers=a['admin']).json() if x['sku']=='ACE')==480

def test_kitchen_cannot_view_customers(env):
    c,a,s=env
    assert c.get('/api/v1/customers',headers=a['kitchen']).status_code==403

def test_invalid_quantity_rejected_by_schema(env):
    c,a,s=env
    assert post_order(c,a['cashier'],quantity=0).status_code==422

def test_last_order_id_unknown(env):
    c,a,s=env
    assert c.get('/api/v1/orders/123456',headers=a['admin']).status_code==404

def test_admin_create_user_and_duplicate(env):
    c,a,s=env
    data={'username':'nuevo_cajero','full_name':'Cajero adicional','password':'long_test_password123','role':'cashier'}
    assert c.post('/api/v1/users',headers=a['admin'],json=data).status_code==201
    assert c.post('/api/v1/users',headers=a['admin'],json=data).status_code==409
    assert len(c.get('/api/v1/users',headers=a['admin']).json())==4

def test_non_admin_cannot_create_user(env):
    c,a,s=env
    assert c.post('/api/v1/users',headers=a['cashier'],json={'username':'otro','full_name':'Otro usuario','password':'password123456','role':'cashier'}).status_code==403

def test_prevent_self_demotion_and_disabling(env):
    c,a,s=env
    assert c.patch('/api/v1/users/1/role',headers=a['admin'],json={'role':'kitchen'}).status_code==409
    assert c.patch('/api/v1/users/1/active',headers=a['admin'],json={'active':False}).status_code==409

def test_reject_invalid_role(env):
    c,a,s=env
    assert c.patch('/api/v1/users/2/role',headers=a['admin'],json={'role':'root'}).status_code==422

def test_forecast_identifies_statistical_method(env):
    c,a,s=env
    r=c.get('/api/v1/ai/demand-forecast',headers=a['cashier'])
    assert r.status_code==200
    assert r.json()['type']=='estimacion_descriptiva_no_ml'
    assert r.json()['items'][0]['suggested_units_next_day']==0

def test_system_info_hides_secrets(env):
    c,a,s=env
    assert c.get('/api/v1/system/info',headers=a['cashier']).status_code==403
    r=c.get('/api/v1/system/info',headers=a['admin'])
    assert r.status_code==200 and 'jwt_secret' not in r.json()


def test_admin_can_list_disabled_products_and_cashier_cannot(env):
    c,a,_=env
    assert c.patch('/api/v1/products/1',headers=a['admin'],json={'active':False}).status_code==200
    assert c.get('/api/v1/products',headers=a['cashier']).json()==[]
    assert len(c.get('/api/v1/products/manage',headers=a['admin']).json())==1
    assert c.get('/api/v1/products/manage',headers=a['cashier']).status_code==403


def test_product_edit_updates_price_without_changing_historical_sale(env):
    c,a,_=env
    old=post_order(c,a['cashier']).json()
    updated=c.patch('/api/v1/products/1',headers=a['admin'],json={'name':'Pizza renovada','price_cents':4900})
    assert updated.status_code==200,updated.text
    assert updated.json()['price_cents']==4900
    assert c.get(f'/api/v1/orders/{old["id"]}',headers=a['cashier']).json()['total_cents']==3200


def test_cannot_update_product_with_invalid_fields_or_role(env):
    c,a,_=env
    assert c.patch('/api/v1/products/1',headers=a['cashier'],json={'price_cents':2500}).status_code==403
    assert c.patch('/api/v1/products/1',headers=a['admin'],json={'price_cents':-1}).status_code==422
    assert c.patch('/api/v1/products/500',headers=a['admin'],json={'price_cents':100}).status_code==404


def test_customer_edit_and_insights_payments_only(env):
    c,a,_=env
    cus=c.post('/api/v1/customers',headers=a['cashier'],json={'name':'Cliente universitario'}).json()
    cid=cus['id']
    patched=c.patch(f'/api/v1/customers/{cid}',headers=a['cashier'],json={'name':'Cliente actualizado','phone':'999123321'})
    assert patched.status_code==200 and patched.json()['phone']=='999123321'
    first=c.post('/api/v1/orders',headers=a['cashier'],json={'customer_id':cid,'items':[{'product_id':1,'quantity':1}]}).json()
    before=c.get(f'/api/v1/customers/{cid}/insights',headers=a['cashier']).json()
    assert before['orders_total']==1 and before['spent_cents']==0 and before['reference_points']==0
    assert c.post(f'/api/v1/orders/{first["id"]}/payment',headers=a['cashier'],json={'method':'cash','amount_cents':3200}).status_code==201
    after=c.get(f'/api/v1/customers/{cid}/insights',headers=a['cashier']).json()
    assert after['spent_cents']==3200 and after['orders_paid']==1 and after['reference_points']==3
    assert after['top_products'][0]['name']=='Pizza prueba'


def test_kitchen_cannot_read_customer_insights(env):
    c,a,_=env
    r=c.get('/api/v1/customers/1/insights',headers=a['kitchen'])
    assert r.status_code==403


def test_receipt_requires_payment_and_is_non_tax(env):
    c,a,_=env;order=post_order(c,a['cashier']).json()
    assert c.get(f'/api/v1/orders/{order["id"]}/receipt',headers=a['cashier']).status_code==409
    assert c.post(f'/api/v1/orders/{order["id"]}/payment',headers=a['cashier'],json={'method':'yape','amount_cents':3200}).status_code==201
    receipt=c.get(f'/api/v1/orders/{order["id"]}/receipt',headers=a['cashier'])
    assert receipt.status_code==200,receipt.text
    data=receipt.json()
    assert data['type']=='TICKET_INTERNO_NO_TRIBUTARIO'
    assert data['items'][0]['subtotal_cents']==3200 and data['total_cents']==3200
    assert 'SUNAT' in data['disclaimer']
    assert c.get(f'/api/v1/orders/{order["id"]}/receipt',headers=a['kitchen']).status_code==403


def test_new_endpoints_missing_entities(env):
    c,a,_=env
    assert c.get('/api/v1/customers/999/insights',headers=a['cashier']).status_code==404
    assert c.patch('/api/v1/customers/999',headers=a['cashier'],json={'name':'Nuevo nombre'}).status_code==404
    assert c.get('/api/v1/orders/999/receipt',headers=a['cashier']).status_code==404


def test_first_admin_bootstrap_is_one_time_and_hashed(env, monkeypatch):
    from app import manage
    from sqlalchemy import select
    from app.domain.models import User
    c,roles,TestSession=env
    # El entorno de la prueba ya tiene tres usuarios: no permite segundo bootstrap.
    monkeypatch.setattr(manage,'SessionLocal',TestSession)
    with pytest.raises(RuntimeError,match='Ya existen usuarios'):
        manage.create_admin('otra-admin','Otra Administradora','SecurePassword1234')


def test_first_admin_rejects_weak_credentials_before_database(env,monkeypatch):
    from app import manage
    with pytest.raises(ValueError,match='contraseña'):
        manage.create_admin('admin','Administrador Prueba','123')
    with pytest.raises(ValueError,match='inválido'):
        manage.create_admin('!unsafe','Administrador Prueba','SecurePassword1234')