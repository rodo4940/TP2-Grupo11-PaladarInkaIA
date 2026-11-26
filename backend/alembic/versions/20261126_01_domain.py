"""Initial business domain schema: users, menu, recipes, orders, inventory, payments, audit.

Revision ID: 20261126_01
Revises:
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa

revision = '20261126_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('customers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=160), nullable=False),
    sa.Column('phone', sa.String(length=32), nullable=True),
    sa.Column('notes', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ingredients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sku', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('unit', sa.String(length=12), nullable=False),
    sa.Column('stock', sa.Integer(), nullable=False),
    sa.Column('minimum_stock', sa.Integer(), nullable=False),
    sa.CheckConstraint('minimum_stock >= 0', name='ck_ingredient_minimum'),
    sa.CheckConstraint('stock >= 0', name='ck_ingredient_stock'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('sku')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('sku', sa.String(length=40), nullable=False),
    sa.Column('name', sa.String(length=140), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=False),
    sa.Column('price_cents', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('image_url', sa.String(length=512), nullable=True),
    sa.CheckConstraint('price_cents >= 0', name='ck_product_price'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_sku'), 'products', ['sku'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('full_name', sa.String(length=160), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("role IN ('admin','cashier','kitchen')", name='ck_user_role'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('audit_events',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('actor_id', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=60), nullable=False),
    sa.Column('entity', sa.String(length=80), nullable=False),
    sa.Column('entity_id', sa.Integer(), nullable=False),
    sa.Column('detail', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('table_label', sa.String(length=32), nullable=False),
    sa.Column('status', sa.String(length=24), nullable=False),
    sa.Column('total_cents', sa.Integer(), nullable=False),
    sa.Column('notes', sa.String(length=500), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("status IN ('pending','preparing','ready','delivered','cancelled')", name='ck_order_status'),
    sa.CheckConstraint('total_cents >= 0', name='ck_order_total'),
    sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recipe_lines',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.CheckConstraint('amount > 0', name='ck_recipe_amount'),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('product_id', 'ingredient_id', name='uq_recipe_product_ingredient')
    )
    op.create_index(op.f('ix_recipe_lines_ingredient_id'), 'recipe_lines', ['ingredient_id'], unique=False)
    op.create_index(op.f('ix_recipe_lines_product_id'), 'recipe_lines', ['product_id'], unique=False)
    op.create_table('stock_movements',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('delta', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=False),
    sa.Column('reference', sa.String(length=120), nullable=False),
    sa.Column('actor_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['actor_id'], ['users.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_consumptions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('ingredient_id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.CheckConstraint('amount > 0', name='ck_consumption_amount'),
    sa.ForeignKeyConstraint(['ingredient_id'], ['ingredients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id', 'ingredient_id', name='uq_order_consumption')
    )
    op.create_table('order_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=140), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('unit_price_cents', sa.Integer(), nullable=False),
    sa.CheckConstraint('quantity > 0', name='ck_order_item_quantity'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.Integer(), nullable=False),
    sa.Column('method', sa.String(length=20), nullable=False),
    sa.Column('amount_cents', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.CheckConstraint("method IN ('cash','card','yape','plin')", name='ck_payment_method'),
    sa.CheckConstraint('amount_cents >= 0', name='ck_payment_amount'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    # ### end Alembic commands ###

def downgrade() -> None:
    op.drop_table('payments')
    op.drop_table('order_items')
    op.drop_table('order_consumptions')
    op.drop_table('stock_movements')
    op.drop_index(op.f('ix_recipe_lines_product_id'), table_name='recipe_lines')
    op.drop_index(op.f('ix_recipe_lines_ingredient_id'), table_name='recipe_lines')
    op.drop_table('recipe_lines')
    op.drop_table('orders')
    op.drop_table('audit_events')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_products_sku'), table_name='products')
    op.drop_table('products')
    op.drop_table('ingredients')
    op.drop_table('customers')
    # ### end Alembic commands ###