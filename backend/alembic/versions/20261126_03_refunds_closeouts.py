"""Internal refund registration and dual-control cash closeout.

Revision ID: 20261126_03
Revises: 20261126_02
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa

revision = '20261126_03'
down_revision = '20261126_02'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'refunds',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('payment_id', sa.Integer(), sa.ForeignKey('payments.id', ondelete='RESTRICT'), nullable=False, unique=True),
        sa.Column('requested_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('confirmation_reference', sa.String(length=120), unique=True, nullable=True),
        sa.Column('confirmed_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("status IN ('pending','confirmed')", name='ck_refund_status'),
    )
    op.create_table(
        'cash_closeouts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('day', sa.String(length=10), nullable=False, unique=True),
        sa.Column('opening_cash_cents', sa.Integer(), nullable=False),
        sa.Column('expected_cash_cents', sa.Integer(), nullable=False),
        sa.Column('counted_cash_cents', sa.Integer(), nullable=False),
        sa.Column('variance_cents', sa.Integer(), nullable=False),
        sa.Column('gross_payments_cents', sa.Integer(), nullable=False),
        sa.Column('confirmed_refunds_cents', sa.Integer(), nullable=False),
        sa.Column('payments_count', sa.Integer(), nullable=False),
        sa.Column('refunds_count', sa.Integer(), nullable=False),
        sa.Column('submitted_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('approved_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='RESTRICT'), nullable=True),
        sa.Column('state', sa.String(length=20), nullable=False),
        sa.Column('note', sa.String(length=500), nullable=False),
        sa.Column('approval_note', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("opening_cash_cents >= 0", name='ck_closeout_opening'),
        sa.CheckConstraint("counted_cash_cents >= 0", name='ck_closeout_counted'),
        sa.CheckConstraint("state IN ('submitted','approved')", name='ck_closeout_state'),
    )


def downgrade() -> None:
    op.drop_table('cash_closeouts')
    op.drop_table('refunds')
