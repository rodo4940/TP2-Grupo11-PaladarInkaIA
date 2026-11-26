"""Operaciones centrales: ventas, inventario, cocina, caja, clientes y reportes.

Todas las reglas de stock y pago se verifican en servidor y bajo transacción.
La capa REST no utiliza datos de una interfaz ficticia o un prototipo.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.domain.auth import current_user, issue_token, require_roles, verify_password
from app.domain.models import (AuditEvent, Customer, Ingredient, Order, OrderConsumption, OrderItem, Payment, Product, RecipeLine, StockMovement, User)
from app.domain.schemas import (AdjustStockIn, CustomerIn, CustomerOut, IngredientIn, IngredientOut, LoginIn, MovementOut, OrderIn, OrderOut, PaymentIn, PaymentOut, ProductIn, ProductOut, RecipeIn, StatusIn, TokenOut, UserOut, UserCreate, RoleChange, ActiveChange)

router = APIRouter()
admin = require_roles('admin')
cashier = require_roles('admin', 'cashier')
kitchen = require_roles('admin', 'kitchen')

def log_action(db: Session, actor: User, action: str, entity: str, entity_id: int, detail: str='') -> None:
    db.add(AuditEvent(actor_id=actor.id, action=action, entity=entity, entity_id=entity_id, detail=detail[:500]))


def order_response(order: Order) -> OrderOut:
    out = OrderOut.model_validate(order)
    return out.model_copy(update={'paid':order.payment is not None})


def not_found(what: str) -> HTTPException:
    return HTTPException(404, f'{what} no encontrado')

@router.post('/auth/token', response_model=TokenOut)
def login(payload: LoginIn, db: Session=Depends(get_db)) -> dict[str, Any]:
    user = db.scalar(select(User).where(User.username==payload.username.strip().lower()))
    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, 'Usuario o contraseña incorrectos')
    return {'access_token':issue_token(user), 'token_type':'bearer', 'user':UserOut.model_validate(user)}

@router.get('/auth/me', response_model=UserOut)
def me(user: User=Depends(current_user)) -> User:
    return user

@router.get('/products', response_model=list[ProductOut])
def products(db: Session=Depends(get_db), user: User=Depends(current_user)) -> list[Product]:
    return list(db.scalars(select(Product).where(Product.active.is_(True)).order_by(Product.id)))

@router.post('/products', response_model=ProductOut, status_code=201)
def create_product(payload: ProductIn, db: Session=Depends(get_db), user: User=Depends(admin)) -> Product:
    item=Product(**payload.model_dump())
    db.add(item)
    try:
        db.flush()
        log_action(db,user,'product.create','product',item.id, item.sku)
        db.commit(); db.refresh(item)
    except IntegrityError:
        db.rollback(); raise HTTPException(409, 'SKU ya registrado')
    return item

@router.put('/products/{product_id}/recipe', response_model=list[dict])
def replace_recipe(product_id:int, data:list[RecipeIn], db:Session=Depends(get_db), user:User=Depends(admin)) -> list[dict]:
    product=db.get(Product,product_id)
    if product is None: raise not_found('Producto')
    if not data: raise HTTPException(422,'La receta requiere al menos un insumo')
    ids=[x.ingredient_id for x in data]
    if len(ids)!=len(set(ids)): raise HTTPException(422, 'Insumos duplicados en receta')
    valid=set(db.scalars(select(Ingredient.id).where(Ingredient.id.in_(ids))).all())
    if valid != set(ids): raise HTTPException(422, 'Uno o más insumos no existen')
    for line in list(product.recipe_lines): db.delete(line)
    db.flush()
    for line in data:
        db.add(RecipeLine(product_id=product_id, ingredient_id=line.ingredient_id, amount=line.amount))
    log_action(db,user,'recipe.update','product',product_id,str(len(data))+' ingredientes')
    db.commit()
    return [x.model_dump() for x in data]

@router.get('/ingredients', response_model=list[IngredientOut])
def ingredients(db:Session=Depends(get_db), user:User=Depends(current_user)) -> list[Ingredient]:
    return list(db.scalars(select(Ingredient).order_by(Ingredient.name)))

@router.post('/ingredients', response_model=IngredientOut, status_code=201)
def create_ingredient(payload:IngredientIn,db:Session=Depends(get_db),user:User=Depends(admin)) -> Ingredient:
    item=Ingredient(**payload.model_dump())
    db.add(item)
    try:
        db.flush();log_action(db,user,'ingredient.create','ingredient',item.id,item.sku)
        db.commit();db.refresh(item)
    except IntegrityError:
        db.rollback();raise HTTPException(409,'SKU de insumo duplicado')
    return item

@router.post('/ingredients/{ingredient_id}/adjust',response_model=IngredientOut)
def adjust_stock(ingredient_id:int,payload:AdjustStockIn,db:Session=Depends(get_db),user:User=Depends(admin)) -> Ingredient:
    item=db.scalar(select(Ingredient).where(Ingredient.id==ingredient_id).with_for_update())
    if item is None: raise not_found('Insumo')
    if payload.delta==0: raise HTTPException(422,'El movimiento no puede ser cero')
    if item.stock+payload.delta<0: raise HTTPException(409,'El ajuste dejaría stock negativo')
    # UPDATE condicional: evita stock negativo también ante actualizaciones concurrentes.
    changed=db.execute(update(Ingredient).where(Ingredient.id==ingredient_id,Ingredient.stock+payload.delta>=0).values(stock=Ingredient.stock+payload.delta))
    if changed.rowcount!=1: db.rollback();raise HTTPException(409,'Stock insuficiente')
    db.flush();db.refresh(item)
    db.add(StockMovement(ingredient_id=ingredient_id,delta=payload.delta,balance=item.stock,reference='AJUSTE: '+payload.reason,actor_id=user.id))
    log_action(db,user,'stock.adjust','ingredient',ingredient_id,payload.reason)
    db.commit();db.refresh(item)
    return item

@router.get('/inventory/movements',response_model=list[MovementOut])
def movements(db:Session=Depends(get_db),user:User=Depends(current_user),limit:int=Query(100,ge=1,le=500)) -> list[StockMovement]:
    return list(db.scalars(select(StockMovement).order_by(StockMovement.id.desc()).limit(limit)))

@router.get('/customers',response_model=list[CustomerOut])
def customers(db:Session=Depends(get_db),user:User=Depends(cashier)) -> list[Customer]:
    return list(db.scalars(select(Customer).order_by(Customer.id.desc()).limit(200)))

@router.post('/customers',response_model=CustomerOut,status_code=201)
def create_customer(payload:CustomerIn,db:Session=Depends(get_db),user:User=Depends(cashier)) -> Customer:
    c=Customer(**payload.model_dump());db.add(c);db.flush()
    log_action(db,user,'customer.create','customer',c.id,c.name)
    db.commit();db.refresh(c)
    return c

@router.get('/orders',response_model=list[OrderOut])
def list_orders(db:Session=Depends(get_db),user:User=Depends(current_user),limit:int=Query(100,ge=1,le=300)) -> list[OrderOut]:
    return [order_response(x) for x in db.scalars(select(Order).order_by(Order.id.desc()).limit(limit))]

@router.get('/orders/{order_id}',response_model=OrderOut)
def get_order(order_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)) -> OrderOut:
    obj=db.get(Order,order_id)
    if obj is None: raise not_found('Pedido')
    return order_response(obj)

@router.post('/orders',response_model=OrderOut,status_code=201)
def create_order(data:OrderIn,db:Session=Depends(get_db),user:User=Depends(cashier)) -> OrderOut:
    if data.customer_id and db.get(Customer,data.customer_id) is None:raise not_found('Cliente')
    counts:dict[int,int]=defaultdict(int)
    for line in data.items:
        counts[line.product_id]+=line.quantity
        if counts[line.product_id]>100:raise HTTPException(422,'Máximo 100 unidades por producto')
    catalog={p.id:p for p in db.scalars(select(Product).where(Product.id.in_(counts)).with_for_update())}
    if len(catalog)!=len(counts) or any(not p.active for p in catalog.values()):
        raise HTTPException(404,'Producto inexistente o inactivo')
    demand:dict[int,int]=defaultdict(int)
    lines=[]
    for product_id,qty in counts.items():
        product=catalog[product_id]
        if not product.recipe_lines: raise HTTPException(409,f'Producto sin receta: {product.name}')
        lines.append(OrderItem(product_id=product.id,product_name=product.name,quantity=qty,unit_price_cents=product.price_cents))
        for recipe in product.recipe_lines: demand[recipe.ingredient_id]+=recipe.amount*qty
    order=Order(customer_id=data.customer_id,table_label=data.table_label,status='pending',
                total_cents=sum(x.unit_price_cents*x.quantity for x in lines),notes=data.notes)
    db.add(order);db.flush()
    for item in lines: item.order_id=order.id;db.add(item)
    # El UPDATE con condición es atómico en PostgreSQL y evita sobreventa de stock.
    for ingredient_id,required in sorted(demand.items()):
        result=db.execute(update(Ingredient).where(Ingredient.id==ingredient_id,Ingredient.stock>=required).values(stock=Ingredient.stock-required))
        if result.rowcount!=1:
            db.rollback();raise HTTPException(409,f'Stock insuficiente para el insumo {ingredient_id}')
        stock=db.get(Ingredient,ingredient_id);db.refresh(stock)
        db.add(StockMovement(ingredient_id=ingredient_id,delta=-required,balance=stock.stock,reference=f'PEDIDO-{order.id}',actor_id=user.id))
        db.add(OrderConsumption(order_id=order.id,ingredient_id=ingredient_id,amount=required))
    log_action(db,user,'order.create','order',order.id,f'Total {order.total_cents} céntimos')
    db.commit()
    return order_response(db.get(Order,order.id))

ALLOWED={
    'pending':{'preparing','cancelled'},
    'preparing':{'ready','cancelled'},
    'ready':{'delivered'},
    'delivered':set(),
    'cancelled':set(),
}

@router.patch('/orders/{order_id}/status',response_model=OrderOut)
def change_status(order_id:int,payload:StatusIn,db:Session=Depends(get_db),user:User=Depends(kitchen)) -> OrderOut:
    order=db.scalar(select(Order).where(Order.id==order_id).with_for_update())
    if order is None:raise not_found('Pedido')
    if payload.status not in ALLOWED[order.status]:raise HTTPException(409,f'Transición no permitida: {order.status} → {payload.status}')
    if payload.status=='cancelled':
        if order.payment is not None:raise HTTPException(409,'Pedido pagado: realizar devolución mediante proceso autorizado')
        for consumption in order.consumptions:
            db.execute(update(Ingredient).where(Ingredient.id==consumption.ingredient_id).values(stock=Ingredient.stock+consumption.amount))
            ingredient=db.get(Ingredient,consumption.ingredient_id);db.refresh(ingredient)
            db.add(StockMovement(ingredient_id=consumption.ingredient_id,delta=consumption.amount,balance=ingredient.stock,reference=f'CANCELACION-{order.id}',actor_id=user.id))
    order.status=payload.status
    log_action(db,user,'order.status','order',order.id,payload.status)
    db.commit();return order_response(db.get(Order,order.id))

@router.post('/orders/{order_id}/payment',response_model=PaymentOut,status_code=201)
def pay(order_id:int,payload:PaymentIn,db:Session=Depends(get_db),user:User=Depends(cashier)) -> Payment:
    order=db.scalar(select(Order).where(Order.id==order_id).with_for_update())
    if order is None:raise not_found('Pedido')
    if order.status=='cancelled':raise HTTPException(409,'No se puede pagar un pedido cancelado')
    if order.payment is not None:raise HTTPException(409,'Pedido ya pagado')
    if payload.amount_cents != order.total_cents:raise HTTPException(422,'Importe no coincide con el total del pedido')
    payment=Payment(order_id=order.id,method=payload.method,amount_cents=payload.amount_cents)
    db.add(payment)
    try:
        db.flush()
        log_action(db,user,'payment.create','order',order.id,payload.method)
        db.commit();db.refresh(payment)
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Pago ya registrado')
    return payment

@router.get('/dashboard')
def dashboard(db:Session=Depends(get_db),user:User=Depends(current_user)) -> dict[str,Any]:
    orders=list(db.scalars(select(Order)))
    sales=int(db.scalar(select(func.coalesce(func.sum(Payment.amount_cents),0))) or 0)
    critical=list(db.scalars(select(Ingredient).where(Ingredient.stock<=Ingredient.minimum_stock).order_by(Ingredient.name)))
    return {'sales_cents':sales,'orders_total':len(orders),'orders_active':sum(o.status in {'pending','preparing','ready'} for o in orders),
            'orders_delivered':sum(o.status=='delivered' for o in orders),'customers_total':db.scalar(select(func.count(Customer.id))) or 0,
            'low_stock':[{'id':x.id,'name':x.name,'stock':x.stock,'minimum_stock':x.minimum_stock,'unit':x.unit} for x in critical]}

@router.get('/reports/sales')
def sales_report(db:Session=Depends(get_db),user:User=Depends(cashier)) -> dict[str,Any]:
    paid=list(db.scalars(select(Payment).order_by(Payment.created_at.desc())))
    top=Counter()
    for payment in paid:
        for item in payment.order.items:top[item.product_name]+=item.quantity
    return {'paid_orders':len(paid),'sales_cents':sum(p.amount_cents for p in paid),
            'by_method':dict(Counter({method:sum(p.amount_cents for p in paid if p.method==method) for method in {'cash','card','yape','plin'}})),
            'top_products':[{'name':name,'quantity':qty} for name,qty in top.most_common(10)]}

@router.get('/recommendations')
def recommendations(db:Session=Depends(get_db),user:User=Depends(current_user),limit:int=Query(5,ge=1,le=20)) -> dict[str,Any]:
    """Clasificador explicable de popularidad y disponibilidad. NO es un modelo ML."""
    sold=Counter()
    for payment in db.scalars(select(Payment)):
        for item in payment.order.items:sold[item.product_id]+=item.quantity
    rows=[]
    for p in db.scalars(select(Product).where(Product.active.is_(True))):
        available=bool(p.recipe_lines) and all(r.ingredient.stock>=r.amount for r in p.recipe_lines)
        if not available:continue
        rows.append({'product_id':p.id,'name':p.name,'price_cents':p.price_cents,'orders_count':sold[p.id],
                     'reason':'Prioridad por compras confirmadas y disponibilidad de ingredientes'})
    rows.sort(key=lambda x:(-x['orders_count'],x['name']))
    return {'method':'ranking_heuristico_explicable_sin_modelo_entrenado','items':rows[:limit]}

@router.get('/audit')
def audit(db:Session=Depends(get_db),user:User=Depends(admin),limit:int=Query(100,ge=1,le=500)) -> list[dict[str,Any]]:
    rows=db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(limit))
    return [{'id':x.id,'actor_id':x.actor_id,'action':x.action,'entity':x.entity,'entity_id':x.entity_id,
             'detail':x.detail,'created_at':x.created_at.isoformat()} for x in rows]

@router.get('/users',response_model=list[UserOut])
def list_users(db:Session=Depends(get_db),user:User=Depends(admin)) -> list[User]:
    return list(db.scalars(select(User).order_by(User.id)))

@router.post('/users',response_model=UserOut,status_code=201)
def create_user(payload:UserCreate,db:Session=Depends(get_db),user:User=Depends(admin)) -> User:
    from app.domain.auth import hash_password
    u=User(username=payload.username.strip().lower(),full_name=payload.full_name,role=payload.role,password_hash=hash_password(payload.password))
    db.add(u)
    try:
        db.flush();log_action(db,user,'user.create','user',u.id,u.username);db.commit();db.refresh(u)
    except IntegrityError:
        db.rollback();raise HTTPException(409,'Nombre de usuario ocupado')
    return u

@router.patch('/users/{user_id}/role',response_model=UserOut)
def change_role(user_id:int,payload:RoleChange,db:Session=Depends(get_db),actor:User=Depends(admin)) -> User:
    u=db.scalar(select(User).where(User.id==user_id).with_for_update())
    if not u:raise not_found('Usuario')
    if u.id==actor.id and u.role=='admin' and payload.role!='admin':
        raise HTTPException(409,'No puedes retirar tu propio acceso administrador')
    u.role=payload.role;log_action(db,actor,'user.role','user',u.id,payload.role)
    db.commit();db.refresh(u)
    return u

@router.patch('/users/{user_id}/active',response_model=UserOut)
def change_active(user_id:int,payload:ActiveChange,db:Session=Depends(get_db),actor:User=Depends(admin)) -> User:
    u=db.scalar(select(User).where(User.id==user_id).with_for_update())
    if not u:raise not_found('Usuario')
    if u.id==actor.id and not payload.active:raise HTTPException(409,'No puedes desactivar tu propia cuenta')
    u.active=payload.active;log_action(db,actor,'user.active','user',u.id,str(payload.active))
    db.commit();db.refresh(u)
    return u

@router.get('/ai/demand-forecast')
def demand_forecast(db:Session=Depends(get_db),user:User=Depends(cashier)) -> dict[str,Any]:
    """Estimación de demanda de siete días por media ponderada de ventas pagadas.

    NO es un modelo de aprendizaje automático ni una inferencia garantizada.
    """
    from datetime import date, timedelta
    from math import sqrt, ceil
    start=date.today()-timedelta(days=6)
    days={start+timedelta(days=n):n for n in range(7)}
    paid=list(db.scalars(select(Payment)))
    result=[]
    for p in db.scalars(select(Product).where(Product.active.is_(True))):
        sales=[0]*7
        for payment in paid:
            day=payment.created_at.date()
            if day not in days:continue
            for item in payment.order.items:
                if item.product_id==p.id:sales[days[day]]+=item.quantity
        weights=[1,2,3,4,5,6,7]
        mu=sum(s*w for s,w in zip(sales,weights))/sum(weights)
        expected=ceil(mu)
        lower=max(0,int(mu-1.96*sqrt(max(mu,0))))
        upper=ceil(mu+1.96*sqrt(max(mu,0)))
        result.append({'product_id':p.id,'name':p.name,'units_by_day':sales,
                       'suggested_units_next_day':expected,'indicative_range':[lower,upper]})
    return {'method':'media_movil_ponderada_7_dias','type':'estimacion_descriptiva_no_ml',
            'sample_paid_orders_7d':sum(p.created_at.date()>=start for p in paid),
            'limitations':'Datos insuficientes pueden invalidar el pronóstico. Intervalo indicativo, no estadísticamente calibrado.',
            'items':result}

@router.get('/system/info')
def system_info(user:User=Depends(admin)) -> dict[str,Any]:
    from app.core.config import get_settings
    s=get_settings()
    return {'app':s.app_name,'version':'1.0.0','environment':s.app_env,
            'database':'PostgreSQL (modo operativo) / SQLite en tests',
            'modules':['auth','orders','kitchen','inventory','products','customers','payments','reports','ai-heuristics','audit']}
