"""Contratos HTTP públicos de la API: validaciones explícitas de entrada."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class ORMOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    password: str = Field(min_length=1, max_length=256)

class UserOut(ORMOut):
    id: int
    username: str
    full_name: str
    role: str
    active: bool

class TokenOut(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user: UserOut

class ProductIn(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=140)
    category: str = Field(default='Pizzas', max_length=80)
    price_cents: int = Field(ge=0, le=99999999)

class ProductPatch(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=140)
    category: str | None = Field(default=None, min_length=2, max_length=80)
    price_cents: int | None = Field(default=None, ge=0, le=99999999)
    active: bool | None = None

class RecipeIn(BaseModel):
    ingredient_id: int = Field(gt=0)
    amount: int = Field(gt=0, le=1000000)

class ProductOut(ORMOut):
    id: int
    sku: str
    name: str
    category: str
    price_cents: int
    active: bool

class IngredientIn(BaseModel):
    sku: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    unit: str = Field(pattern='^(g|ml|unit)$')
    stock: int = Field(ge=0, le=100000000)
    minimum_stock: int = Field(ge=0, le=100000000)

class IngredientOut(ORMOut):
    id: int
    sku: str
    name: str
    unit: str
    stock: int
    minimum_stock: int

class AdjustStockIn(BaseModel):
    delta: int = Field(ge=-100000000, le=100000000)
    reason: str = Field(min_length=4, max_length=120)

class CustomerIn(BaseModel):
    name: str = Field(min_length=3, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    notes: str | None = Field(default=None, max_length=500)

class CustomerPatch(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=160)
    phone: str | None = Field(default=None, max_length=32)
    notes: str | None = Field(default=None, max_length=500)

class CustomerOut(ORMOut):
    id: int
    name: str
    phone: str | None
    notes: str | None

class OrderItemIn(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100)

class OrderIn(BaseModel):
    items: list[OrderItemIn] = Field(min_length=1, max_length=30)
    customer_id: int | None = Field(default=None, gt=0)
    table_label: str = Field(default='Mostrador', min_length=1, max_length=32)
    notes: str = Field(default='', max_length=500)

class OrderItemOut(ORMOut):
    id: int
    product_id: int
    product_name: str
    quantity: int
    unit_price_cents: int

class OrderOut(ORMOut):
    id: int
    status: str
    customer_id: int | None
    table_label: str
    total_cents: int
    notes: str
    created_at: datetime
    items: list[OrderItemOut]
    paid: bool = False

class StatusIn(BaseModel):
    status: str = Field(pattern='^(preparing|ready|delivered|cancelled)$')

class PaymentIn(BaseModel):
    method: str = Field(pattern='^(cash|card|yape|plin)$')
    amount_cents: int = Field(ge=0)

class PaymentOut(ORMOut):
    id: int
    order_id: int
    method: str
    amount_cents: int
    created_at: datetime

class MovementOut(ORMOut):
    id: int
    ingredient_id: int
    delta: int
    balance: int
    reference: str
    actor_id: int
    created_at: datetime

class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=256)
    new_password: str = Field(min_length=12, max_length=128)

class PasswordReset(BaseModel):
    new_password: str = Field(min_length=12, max_length=128)

class UserCreate(BaseModel):
    username: str = Field(min_length=3,max_length=80,pattern=r'^[a-z][a-z0-9_.-]+$')
    full_name: str = Field(min_length=3,max_length=160)
    password: str = Field(min_length=12,max_length=128)
    role: str = Field(pattern='^(admin|cashier|kitchen)$')

class RoleChange(BaseModel):
    role: str = Field(pattern='^(admin|cashier|kitchen)$')

class ActiveChange(BaseModel):
    active: bool