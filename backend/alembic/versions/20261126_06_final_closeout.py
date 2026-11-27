"""Final immutable internal day close snapshot.

Revision ID: 20261126_06
Revises: 20261126_05
"""
from alembic import op
import sqlalchemy as sa
revision='20261126_06'
down_revision='20261126_05'
branch_labels=None
depends_on=None

def upgrade():
    op.drop_constraint('ck_closeout_state','cash_closeouts',type_='check')
    op.create_check_constraint('ck_closeout_state','cash_closeouts',
      "state IN ('submitted','approved','finalized')")
    op.add_column('cash_closeouts',sa.Column('finalized_at',sa.DateTime(timezone=True),nullable=True))
    op.add_column('cash_closeouts',sa.Column('finalized_by',sa.Integer(),nullable=True))
    op.add_column('cash_closeouts',sa.Column('snapshot_sha256',sa.String(length=64),nullable=True))
    op.create_foreign_key('fk_cash_closeout_finalized_by','cash_closeouts','users',['finalized_by'],['id'],ondelete='RESTRICT')


def downgrade():
    op.drop_constraint('fk_cash_closeout_finalized_by','cash_closeouts',type_='foreignkey')
    op.drop_column('cash_closeouts','snapshot_sha256')
    op.drop_column('cash_closeouts','finalized_by')
    op.drop_column('cash_closeouts','finalized_at')
    op.drop_constraint('ck_closeout_state','cash_closeouts',type_='check')
    op.create_check_constraint('ck_closeout_state','cash_closeouts',
      "state IN ('submitted','approved')")
