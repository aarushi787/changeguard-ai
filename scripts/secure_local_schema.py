"""Install audit triggers on a pre-existing local evaluation schema without deleting data."""
from sqlalchemy import inspect,text
from backend.db import Base,engine

if engine.dialect.name!='sqlite':raise RuntimeError('Use Alembic migrations for PostgreSQL.')
inspector=inspect(engine)
for table in Base.metadata.sorted_tables:
    actual={c['name'] for c in inspector.get_columns(table.name)}
    expected={c.name for c in table.columns}
    if actual!=expected:raise RuntimeError(f'Schema differs for {table.name}; review migration before stamping.')
with engine.begin() as c:
    c.execute(text("CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END"))
    c.execute(text("CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit_events BEGIN SELECT RAISE(ABORT, 'audit_events are append-only'); END"))
print('Existing local schema columns verified; immutable audit triggers installed.')
