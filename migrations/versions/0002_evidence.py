"""Versioned controlled records, typed dependencies, immutable evidence snapshots."""
from alembic import op
import sqlalchemy as sa
revision='0002'
down_revision='0001'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('records',sa.Column('version',sa.Integer(),nullable=False,server_default='1'))
    op.create_table('knowledge_edges',sa.Column('id',sa.String(32),primary_key=True),sa.Column('tenant',sa.String(32),nullable=False),sa.Column('project_id',sa.String(32),nullable=False),sa.Column('source',sa.String(100),nullable=False),sa.Column('target',sa.String(100),nullable=False),sa.Column('relation',sa.String(80),nullable=False),sa.Column('evidence',sa.JSON(),nullable=False),sa.UniqueConstraint('tenant','project_id','source','target','relation',name='uq_knowledge_edge'))
    op.create_index('ix_knowledge_edges_tenant','knowledge_edges',['tenant']);op.create_index('ix_knowledge_edges_project_id','knowledge_edges',['project_id'])
    op.create_table('evidence_snapshots',sa.Column('id',sa.String(32),primary_key=True),sa.Column('tenant',sa.String(32),nullable=False),sa.Column('entity',sa.String(32),nullable=False),sa.Column('stage',sa.String(40),nullable=False),sa.Column('digest',sa.String(64),nullable=False),sa.Column('data',sa.JSON(),nullable=False),sa.Column('created',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_evidence_snapshots_tenant','evidence_snapshots',['tenant']);op.create_index('ix_evidence_snapshots_entity','evidence_snapshots',['entity'])
    if op.get_bind().dialect.name=='postgresql':
        op.execute('CREATE TRIGGER immutable_snapshot BEFORE UPDATE OR DELETE ON evidence_snapshots FOR EACH ROW EXECUTE FUNCTION deny_audit_mutation()')
    else:
        for verb in ['UPDATE','DELETE']:
            op.execute(f"CREATE TRIGGER snapshot_no_{verb.lower()} BEFORE {verb} ON evidence_snapshots BEGIN SELECT RAISE(ABORT, 'evidence snapshots are append-only'); END")

def downgrade():raise RuntimeError('Evidence-preserving migration; destructive downgrade is disabled.')
