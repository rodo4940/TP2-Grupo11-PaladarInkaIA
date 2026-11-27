"""Create isolated non-fiscal CPE simulation tables.

Revision ID: 20261126_05
Revises: 20261126_04
"""
from alembic import op
import sqlalchemy as sa

revision='20261126_05'
down_revision='20261126_04'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('fiscal_demo_documents',
      sa.Column('id',sa.Integer(),primary_key=True),
      sa.Column('payment_id',sa.Integer(),sa.ForeignKey('payments.id',ondelete='RESTRICT'),nullable=False),
      sa.Column('document_type',sa.String(length=2),nullable=False),
      sa.Column('series',sa.String(length=4),nullable=False),
      sa.Column('correlative',sa.Integer(),nullable=False),
      sa.Column('issue_date',sa.String(length=10),nullable=False),
      sa.Column('customer_name',sa.String(length=160),nullable=False),
      sa.Column('customer_document_type',sa.String(length=1),nullable=False),
      sa.Column('customer_document_number',sa.String(length=11),nullable=False),
      sa.Column('affectation_code',sa.String(length=2),nullable=False),
      sa.Column('total_cents',sa.Integer(),nullable=False),
      sa.Column('net_cents',sa.Integer(),nullable=False),
      sa.Column('tax_cents',sa.Integer(),nullable=False),
      sa.Column('xml_demo',sa.String(length=50000),nullable=False),
      sa.Column('xml_sha256',sa.String(length=64),nullable=False),
      sa.Column('idempotency_key',sa.String(length=96),nullable=False,unique=True),
      sa.Column('reference_document_id',sa.Integer(),sa.ForeignKey('fiscal_demo_documents.id',ondelete='RESTRICT'),nullable=True,unique=True),
      sa.Column('reason',sa.String(length=250),nullable=False),
      sa.Column('created_by',sa.Integer(),sa.ForeignKey('users.id',ondelete='RESTRICT'),nullable=False),
      sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
      sa.UniqueConstraint('series','correlative',name='uq_fiscal_demo_series_correlative'),
      sa.CheckConstraint("document_type IN ('01','03','07')",name='ck_fiscal_demo_type'),
      sa.CheckConstraint("total_cents >= 0 AND net_cents >= 0 AND tax_cents >= 0",name='ck_fiscal_demo_money')
    )

def downgrade():
    op.drop_table('fiscal_demo_documents')
