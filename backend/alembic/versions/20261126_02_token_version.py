"""Invalidate JWT sessions after password changes.

Revision ID: 20261126_02
Revises: 20261126_01
Create Date: 2026-11-26
"""
from alembic import op
import sqlalchemy as sa
revision='20261126_02'
down_revision='20261126_01'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('users',sa.Column('token_version',sa.Integer(),nullable=False,server_default='0'))

def downgrade():
    op.drop_column('users','token_version')