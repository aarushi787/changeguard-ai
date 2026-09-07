from alembic import context
from sqlalchemy import pool
from backend.db import Base, DATABASE_URL, DATABASE_CONNECT_ARGS, SUPABASE
from sqlalchemy import create_engine, text
from backend.database_config import configured_engine
import backend.universal_models
config=context.config
if context.is_offline_mode():
    context.configure(url=DATABASE_URL,target_metadata=Base.metadata,literal_binds=True)
    with context.begin_transaction(): context.run_migrations()
else:
    connectable=configured_engine(DATABASE_URL,DATABASE_CONNECT_ARGS,SUPABASE,poolclass=pool.NullPool)
    with connectable.connect() as connection:
        if SUPABASE:
            connection.execute(text('CREATE SCHEMA IF NOT EXISTS changeguard'))
            connection.execute(text('REVOKE ALL ON SCHEMA changeguard FROM PUBLIC, anon, authenticated'))
            connection.commit()
        context.configure(connection=connection,target_metadata=Base.metadata)
        with context.begin_transaction(): context.run_migrations()
