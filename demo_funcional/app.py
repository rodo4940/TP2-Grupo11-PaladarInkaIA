"""MVP de demostración de El Paladar del Inka: API real con SQLite y datos ficticios.
NO es producción ni demuestra que los módulos empresariales estén desplegados.
Ejecutar desde la raíz: uvicorn demo_funcional.app:app --port 8765
"""
from __future__ import annotations

import os
import secrets
import sqlite3
import time
from collections import defaultdict
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

HERE = Path(__file__).resolve().parent
DEMO_CREDENTIALS = {'admin': ('demo123', 'administrador'), 'cajero': ('demo123', 'cajero'), 'cocina': ('demo123', 'cocina')}
SESSIONS: dict[str, tuple[str, str, float]] = {}
app = FastAPI(title='Paladar Inka AI | MVP verificable (datos ficticios)', version='0.1.0-demo')


def database_path() -> Path:
    return Path(os.getenv('PALADAR_DEMO_DB', str(HERE / 'demo_data.sqlite3')))


def db() -> sqlite3.Connection:
    cn = sqlite3.connect(str(database_path()), timeout=15, isolation_level=None)
    cn.row_factory = sqlite3.Row
    cn.execute('PRAGMA foreign_keys=ON')
    cn.execute('PRAGMA busy_timeout=15000')
    return cn


def init_db() -> None:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with db() as cn:
        cn.executescript('''
          CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, price_cents INTEGER NOT NULL CHECK(price_cents>0), active INTEGER NOT NULL DEFAULT 1);
          CREATE TABLE IF NOT EXISTS ingredients(id INTEGER PRIMARY KEY, name TEXT UNIQUE NOT NULL, grams INTEGER NOT NULL CHECK(grams>=0), minimum_grams INTEGER NOT NULL CHECK(minimum_grams>=0));
          CREATE TABLE IF NOT EXISTS recipes(product_id INTEGER NOT NULL REFERENCES products(id), ingredient_id INTEGER NOT NULL REFERENCES ingredients(id), grams INTEGER NOT NULL CHECK(grams>0), PRIMARY KEY(product_id,ingredient_id));
          CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY, customer TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'nuevo', payment_status TEXT NOT NULL DEFAULT 'pendiente', total_cents INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS order_items(order_id INTEGER NOT NULL REFERENCES orders(id), product_id INTEGER NOT NULL REFERENCES products(id), qty INTEGER NOT NULL CHECK(qty>0), price_cents INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS movements(id INTEGER PRIMARY KEY, ingredient_id INTEGER NOT NULL REFERENCES ingredients(id), delta_grams INTEGER NOT NULL, reason TEXT NOT NULL, order_id INTEGER REFERENCES orders(id), created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
          CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, kind TEXT NOT NULL, detail TEXT NOT NULL, actor TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        ''')
        if cn.execute('SELECT COUNT(*) FROM products').fetchone()[0] == 0:
            cn.executemany('INSERT INTO products(id,name,price_cents) VALUES (?,?,?)', [(1,'Pizza Inka',3400),(2,'Pizza Suprema',3950),(3,'Pizza Andina',3200)])
            cn.executemany('INSERT INTO ingredients(id,name,grams,minimum_grams) VALUES (?,?,?,?)', [(1,'Masa',8000,2000),(2,'Mozzarella',5000,1500),(3,'Salsa de tomate',4000,1000),(4,'Pepperoni',2500,600)])
            cn.executemany('INSERT INTO recipes(product_id,ingredient_id,grams) VALUES (?,?,?)', [(1,1,260),(1,2,180),(1,3,120),(2,1,280),(2,2,200),(2,3,130),(2,4,90),(3,1,260),(3,2,150),(3,3,120)])


init_db()


def user(authorization: Annotated[str | None, Header()] = None) -> tuple[str, str]:
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(401, 'Token de sesión requerido')
    entry = SESSIONS.get(authorization[7:])
    if not entry or entry[2] < time.time():
        raise HTTPException(401, 'Sesión inexistente o vencida')
    return (entry[0], entry[1])


def require(*roles: str):
    def check(u: tuple[str, str] = Depends(user)) -> tuple[str, str]:
        if u[1] not in roles:
            raise HTTPException(403, 'Acceso restringido según rol')
        return u
    return check


class Login(BaseModel):
    username: str
    password: str


class Item(BaseModel):
    product_id: int
    qty: int = Field(gt=0, le=20)


class NewOrder(BaseModel):
    customer: str = Field(min_length=2, max_length=80)
    items: list[Item] = Field(min_length=1, max_length=20)


class StatusChange(BaseModel):
    status: str


class Restock(BaseModel):
    ingredient_id: int
    grams: int = Field(gt=0, le=50000)


@app.get('/')
def home():
    return FileResponse(HERE / 'static' / 'index.html')


@app.get('/api/health')
def health():
    with db() as cn:
        cn.execute('SELECT 1').fetchone()
    return {'status': 'ok', 'storage': 'sqlite', 'scope': 'mvp local'}


@app.post('/api/login')
def login(payload: Login):
    entry = DEMO_CREDENTIALS.get(payload.username)
    if not entry or not secrets.compare_digest(payload.password, entry[0]):
        raise HTTPException(401, 'Credenciales inválidas')
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = (payload.username, entry[1], time.time() + 3600)
    return {'token': token, 'username': payload.username, 'role': entry[1], 'expires_in': 3600}


@app.get('/api/products')
def products(_: tuple[str, str] = Depends(user)):
    with db() as cn:
        return [dict(x) for x in cn.execute('SELECT * FROM products WHERE active=1 ORDER BY id')]


@app.get('/api/inventory')
def inventory(_: tuple[str, str] = Depends(user)):
    with db() as cn:
        return [dict(x) | {'alert': x['grams'] <= x['minimum_grams']} for x in cn.execute('SELECT * FROM ingredients ORDER BY id')]


@app.get('/api/movements')
def movements(_: tuple[str, str] = Depends(require('administrador', 'cajero'))):
    with db() as cn:
        return [dict(x) for x in cn.execute('SELECT m.id,i.name AS ingredient,m.delta_grams,m.reason,m.order_id,m.created_at FROM movements m JOIN ingredients i ON i.id=m.ingredient_id ORDER BY m.id DESC LIMIT 100')]


@app.post('/api/inventory/receipts', status_code=201)
def restock(payload: Restock, u: tuple[str, str] = Depends(require('administrador'))):
    with db() as cn:
        try:
            cn.execute('BEGIN IMMEDIATE')
            cur = cn.execute('UPDATE ingredients SET grams=grams+? WHERE id=?', (payload.grams, payload.ingredient_id))
            if not cur.rowcount:
                raise HTTPException(404, 'Ingrediente inexistente')
            cn.execute('INSERT INTO movements(ingredient_id,delta_grams,reason) VALUES (?, ?, ?)', (payload.ingredient_id,payload.grams,'compra/recepción'))
            cn.execute('INSERT INTO events(kind,detail,actor) VALUES (?,?,?)', ('reposicion',f'Ingrediente {payload.ingredient_id}: +{payload.grams} g',u[0]))
            cn.commit()
        except Exception:
            cn.rollback()
            raise
    return {'status': 'registrado'}


@app.post('/api/orders', status_code=201)
def create_order(payload: NewOrder, u: tuple[str, str] = Depends(require('administrador','cajero'))):
    quantities = defaultdict(int)
    for item in payload.items:
        quantities[item.product_id] += item.qty
    with db() as cn:
        try:
            cn.execute('BEGIN IMMEDIATE')
            items = []
            needed = defaultdict(int)
            for product_id, qty in quantities.items():
                product = cn.execute('SELECT * FROM products WHERE id=? AND active=1', (product_id,)).fetchone()
                if not product:
                    raise HTTPException(404, f'Producto {product_id} inexistente')
                recipe = cn.execute('SELECT ingredient_id,grams FROM recipes WHERE product_id=?', (product_id,)).fetchall()
                if not recipe:
                    raise HTTPException(409, 'Producto sin receta válida')
                for rec in recipe:
                    needed[rec['ingredient_id']] += rec['grams'] * qty
                items.append((product_id,qty,product['price_cents']))
            for ingredient_id, grams in needed.items():
                row = cn.execute('SELECT name,grams FROM ingredients WHERE id=?', (ingredient_id,)).fetchone()
                if row is None or row['grams'] < grams:
                    raise HTTPException(409, f'Stock insuficiente: {row["name"] if row else ingredient_id}')
            total = sum(qty * unit for _,qty,unit in items)
            cur = cn.execute('INSERT INTO orders(customer,total_cents) VALUES (?,?)', (payload.customer.strip(),total))
            order_id = cur.lastrowid
            for product_id,qty,unit in items:
                cn.execute('INSERT INTO order_items(order_id,product_id,qty,price_cents) VALUES (?,?,?,?)',(order_id,product_id,qty,unit))
            for ingredient_id, grams in needed.items():
                cn.execute('UPDATE ingredients SET grams=grams-? WHERE id=?',(grams,ingredient_id))
                cn.execute('INSERT INTO movements(ingredient_id,delta_grams,reason,order_id) VALUES (?,?,?,?)',(ingredient_id,-grams,'consumo por receta',order_id))
            cn.execute('INSERT INTO events(kind,detail,actor) VALUES (?,?,?)', ('pedido',f'Pedido #{order_id}: S/{total/100:.2f}',u[0]))
            cn.commit()
        except Exception:
            cn.rollback()
            raise
    return {'order_id': order_id, 'total_cents':total, 'status':'nuevo', 'payment_status':'pendiente'}


@app.get('/api/orders')
def orders(_: tuple[str, str] = Depends(user)):
    with db() as cn:
        return [dict(x) for x in cn.execute('SELECT * FROM orders ORDER BY id DESC LIMIT 200')]


@app.patch('/api/orders/{order_id}/status')
def change_status(order_id: int, payload: StatusChange, u: tuple[str, str] = Depends(require('administrador','cocina'))):
    allowed = {'nuevo':'preparacion','preparacion':'listo','listo':'entregado'}
    with db() as cn:
        try:
            cn.execute('BEGIN IMMEDIATE')
            row=cn.execute('SELECT status FROM orders WHERE id=?',(order_id,)).fetchone()
            if not row:
                raise HTTPException(404, 'Pedido inexistente')
            if allowed.get(row['status']) != payload.status:
                raise HTTPException(409,'Transición de estado no permitida')
            cn.execute('UPDATE orders SET status=? WHERE id=?',(payload.status,order_id))
            cn.execute('INSERT INTO events(kind,detail,actor) VALUES (?,?,?)',('cocina',f'Pedido #{order_id}: {row["status"]} → {payload.status}',u[0]))
            cn.commit()
        except Exception:
            cn.rollback()
            raise
    return {'order_id':order_id,'status':payload.status}


@app.post('/api/orders/{order_id}/pay')
def pay(order_id: int, u: tuple[str, str] = Depends(require('administrador','cajero'))):
    with db() as cn:
        try:
            cn.execute('BEGIN IMMEDIATE')
            row = cn.execute('SELECT payment_status,total_cents FROM orders WHERE id=?',(order_id,)).fetchone()
            if not row:
                raise HTTPException(404, 'Pedido inexistente')
            if row['payment_status']=='pagado':
                raise HTTPException(409,'Pedido ya pagado')
            cn.execute("UPDATE orders SET payment_status='pagado' WHERE id=?",(order_id,))
            cn.execute('INSERT INTO events(kind,detail,actor) VALUES (?,?,?)',('pago',f'Pedido #{order_id}: S/{row["total_cents"]/100:.2f}',u[0]))
            cn.commit()
        except Exception:
            cn.rollback()
            raise
    return {'order_id':order_id,'payment_status':'pagado', 'total_cents':row['total_cents']}


@app.get('/api/dashboard')
def dashboard(_: tuple[str, str] = Depends(user)):
    with db() as cn:
        row = cn.execute("SELECT COUNT(*) n,COALESCE(SUM(CASE WHEN payment_status='pagado' THEN total_cents ELSE 0 END),0) sales FROM orders").fetchone()
        alert = cn.execute('SELECT COUNT(*) FROM ingredients WHERE grams<=minimum_grams').fetchone()[0]
        active = cn.execute("SELECT COUNT(*) FROM orders WHERE status IN ('nuevo','preparacion','listo')").fetchone()[0]
        return {'orders':row['n'], 'sales_cents':row['sales'], 'active_orders':active, 'low_stock':alert}


@app.get('/api/reports/sales')
def sales_report(_: tuple[str, str] = Depends(require('administrador'))):
    with db() as cn:
        rows = cn.execute('SELECT date(created_at) day,COUNT(*) n,SUM(total_cents) total_cents FROM orders WHERE payment_status=? GROUP BY date(created_at) ORDER BY day',('pagado',)).fetchall()
        return [dict(row) for row in rows]


@app.get('/api/recommendations')
def recommendation(_: tuple[str, str] = Depends(user)):
    """Heurística transparente de popularidad (no aprendizaje automático)."""
    with db() as cn:
        rows=cn.execute('''SELECT p.name,COALESCE(SUM(oi.qty),0) units,p.price_cents FROM products p
            LEFT JOIN order_items oi ON oi.product_id=p.id WHERE p.active=1
            GROUP BY p.id ORDER BY units DESC,p.price_cents ASC''').fetchall()
    return {'method':'ranking heurístico por unidades vendidas (NO modelo ML entrenado)', 'products':[dict(x) for x in rows]}


@app.get('/api/audit')
def audit(_: tuple[str, str] = Depends(require('administrador'))):
    with db() as cn:
        return [dict(x) for x in cn.execute('SELECT * FROM events ORDER BY id DESC LIMIT 100')]