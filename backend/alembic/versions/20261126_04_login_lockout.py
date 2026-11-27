"""Persist failed-login counters and temporary lockout across workers.

Revision ID: 20261126_04
Revises: 20261126_03
"""
from alembic import op
import sqlalchemy as sa

revision = '20261126_04'
down_revision = '20261126_03'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('login_locked_until', sa.DateTime(timezone=True), nullable=True))


def downgrade():
    op.drop_column('users', 'login_locked_until')
    op.drop_column('users', 'failed_login_attempts')
