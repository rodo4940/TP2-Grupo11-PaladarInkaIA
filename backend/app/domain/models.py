"""Modelos de persistencia transaccional de Paladar Inka AI.

Se utilizan importes enteros en centimos y cantidades enteras de unidad base
(gramos, unidades o mililitros), para evitar errores de punto flotante.
"""
from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    __table_args__ = (CheckConstraint("role IN ('admin','cashier','kitchen')", name='ck_user_role'),)


class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    category: Mapped[str] = mapped_column(String(80), default='Pizzas', nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    recipe_lines: Mapped[list['RecipeLine']] = relationship(back_populates='product', cascade='all, delete-orphan', lazy='selectin')
    __table_args__ = (CheckConstraint('price_cents >= 0', name='ck_product_price'),)


class Ingredient(Base):
    __tablename__ = 'ingredients'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str] = mapped_column(String(12), nullable=False, default='g')
    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    minimum_stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    __table_args__ = (CheckConstraint('stock >= 0', name='ck_ingredient_stock'), CheckConstraint('minimum_stock >= 0', name='ck_ingredient_minimum'))


class RecipeLine(Base):
    __tablename__ = 'recipe_lines'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    product: Mapped[Product] = relationship(back_populates='recipe_lines')
    ingredient: Mapped[Ingredient] = relationship(lazy='joined')
    __table_args__ = (UniqueConstraint('product_id', 'ingredient_id', name='uq_recipe_product_ingredient'), CheckConstraint('amount > 0', name='ck_recipe_amount'))


class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey('customers.id', ondelete='SET NULL'), nullable=True)
    table_label: Mapped[str] = mapped_column(String(32), default='Mostrador', nullable=False)
    status: Mapped[str] = mapped_column(String(24), default='pending', nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    notes: Mapped[str] = mapped_column(String(500), default='', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    items: Mapped[list['OrderItem']] = relationship(back_populates='order', cascade='all, delete-orphan', lazy='selectin')
    payment: Mapped['Payment | None'] = relationship(back_populates='order', uselist=False, lazy='selectin')
    consumptions: Mapped[list['OrderConsumption']] = relationship(back_populates='order', lazy='selectin')
    customer: Mapped[Customer | None] = relationship(lazy='selectin')
    __table_args__ = (CheckConstraint('total_cents >= 0', name='ck_order_total'), CheckConstraint("status IN ('pending','preparing','ready','delivered','cancelled')", name='ck_order_status'))


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    product_name: Mapped[str] = mapped_column(String(140), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[Order] = relationship(back_populates='items')
    __table_args__ = (CheckConstraint('quantity > 0', name='ck_order_item_quantity'),)


class Payment(Base):
    __tablename__ = 'payments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, unique=True)
    method: Mapped[str] = mapped_column(String(20), nullable=False)
    amount_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    order: Mapped[Order] = relationship(back_populates='payment')
    __table_args__ = (CheckConstraint("method IN ('cash','card','yape','plin')", name='ck_payment_method'), CheckConstraint('amount_cents >= 0', name='ck_payment_amount'))


class StockMovement(Base):
    __tablename__ = 'stock_movements'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False)
    delta: Mapped[int] = mapped_column(Integer, nullable=False)
    balance: Mapped[int] = mapped_column(Integer, nullable=False)
    reference: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    ingredient: Mapped[Ingredient] = relationship(lazy='joined')


class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    action: Mapped[str] = mapped_column(String(60), nullable=False)
    entity: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[int] = mapped_column(Integer, nullable=False)
    detail: Mapped[str] = mapped_column(String(500), default='', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)


class OrderConsumption(Base):
    """Snapshot de ingredientes para restauraciones correctas al cancelar."""
    __tablename__ = 'order_consumptions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey('ingredients.id', ondelete='RESTRICT'), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    order: Mapped[Order] = relationship(back_populates='consumptions')
    __table_args__ = (UniqueConstraint('order_id','ingredient_id',name='uq_order_consumption'), CheckConstraint('amount > 0', name='ck_consumption_amount'))