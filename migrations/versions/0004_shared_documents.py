"""Private durable document bytes for a disk-free pilot backend."""
from alembic import op
import sqlalchemy as sa

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('document_blobs',
        sa.Column('key', sa.String(80), primary_key=True),
        sa.Column('content', sa.LargeBinary(), nullable=False),
        sa.Column('sha256', sa.String(64), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=False))
    if op.get_bind().dialect.name == 'postgresql':
        op.execute('REVOKE ALL ON TABLE document_blobs FROM PUBLIC')
        op.execute('CREATE TRIGGER immutable_document_blob BEFORE UPDATE OR DELETE ON document_blobs FOR EACH ROW EXECUTE FUNCTION deny_audit_mutation()')
    else:
        for verb in ['UPDATE', 'DELETE']:
            op.execute(f"CREATE TRIGGER blob_no_{verb.lower()} BEFORE {verb} ON document_blobs BEGIN SELECT RAISE(ABORT, 'Document bytes are immutable'); END")


def downgrade():
    raise RuntimeError('Document evidence must be retained; destructive downgrade disabled.')
