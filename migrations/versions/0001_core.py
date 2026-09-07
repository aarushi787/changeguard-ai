"""Tenant-scoped controlled aggregates and database-enforced append-only audit."""
from alembic import op
import sqlalchemy as sa
revision='0001'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('organizations',sa.Column('id',sa.String(32),primary_key=True),sa.Column('name',sa.String(160),nullable=False),sa.Column('pack',sa.String(60),nullable=False))
    op.create_table('users',sa.Column('id',sa.String(32),primary_key=True),sa.Column('tenant',sa.String(32),nullable=False),sa.Column('email',sa.String(200),unique=True,nullable=False),sa.Column('name',sa.String(100),nullable=False),sa.Column('password',sa.Text(),nullable=False),sa.Column('role',sa.String(40),nullable=False))
    op.create_index('ix_users_tenant','users',['tenant'])
    op.create_table('sessions',sa.Column('id',sa.String(64),primary_key=True),sa.Column('user_id',sa.String(32),nullable=False),sa.Column('expires',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_sessions_user_id','sessions',['user_id'])
    op.create_table('records',sa.Column('id',sa.String(32),primary_key=True),sa.Column('tenant',sa.String(32),nullable=False),sa.Column('kind',sa.String(40),nullable=False),sa.Column('data',sa.JSON(),nullable=False),sa.Column('created',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_records_tenant','records',['tenant']); op.create_index('ix_records_kind','records',['kind'])
    op.create_table('audit_events',sa.Column('id',sa.String(32),primary_key=True),sa.Column('tenant',sa.String(32),nullable=False),sa.Column('actor',sa.String(200),nullable=False),sa.Column('entity',sa.String(32),nullable=False),sa.Column('operation',sa.String(80),nullable=False),sa.Column('details',sa.JSON(),nullable=False),sa.Column('created',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_audit_events_tenant','audit_events',['tenant']); op.create_index('ix_audit_events_entity','audit_events',['entity'])
    if op.get_bind().dialect.name=='postgresql':
        op.execute("CREATE FUNCTION deny_audit_mutation() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN RAISE EXCEPTION 'audit_events are append-only'; END $$")
        op.execute('CREATE TRIGGER immutable_audit BEFORE UPDATE OR DELETE ON audit_events FOR EACH ROW EXECUTE FUNCTION deny_audit_mutation()')
    else:
        op.execute("CREATE TRIGGER audit_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END")
        op.execute("CREATE TRIGGER audit_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END")

def downgrade():
    raise RuntimeError('Destructive downgrade disabled: archive the controlled data and use a reviewed recovery migration.')
