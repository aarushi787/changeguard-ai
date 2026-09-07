"""Shared controlled changes and indexed dependency edges; preserve drawing aggregates."""
from alembic import op
import sqlalchemy as sa
revision = '0003'
down_revision = '0002'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('controlled_changes',
        sa.Column('id', sa.String(32), primary_key=True), sa.Column('tenant', sa.String(32), nullable=False),
        sa.Column('domain', sa.String(40), nullable=False), sa.Column('status', sa.String(40), nullable=False),
        sa.Column('classification', sa.String(30), nullable=False), sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False), sa.Column('created', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated', sa.DateTime(timezone=True), nullable=False))
    op.create_index('ix_controlled_tenant_domain_status', 'controlled_changes', ['tenant','domain','status'])
    op.create_table('change_dependencies',
        sa.Column('id', sa.String(32), primary_key=True), sa.Column('tenant', sa.String(32), nullable=False),
        sa.Column('change_id', sa.String(32), nullable=False), sa.Column('source', sa.String(100), nullable=False),
        sa.Column('target', sa.String(100), nullable=False), sa.Column('relation', sa.String(80), nullable=False),
        sa.Column('evidence', sa.JSON(), nullable=False),
        sa.UniqueConstraint('tenant','change_id','source','target','relation',name='uq_change_dependency'))
    op.create_index('ix_dependency_traversal','change_dependencies',['tenant','change_id','source'])

def downgrade():
    raise RuntimeError('Controlled evidence must be retained. Destructive downgrade disabled.')
