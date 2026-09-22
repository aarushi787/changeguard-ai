from alembic import context
from sqlalchemy import pool
from backend.db import Base, DATABASE_URL, DATABASE_CONNECT_ARGS, PRIVATE_SCHEMA
from sqlalchemy import create_engine, text
from backend.database_config import configured_engine, initialize_private_schema
import backend.universal_models
config=context.config
if context.is_offline_mode():
    context.configure(url=DATABASE_URL,target_metadata=Base.metadata,literal_binds=True)
    with context.begin_transaction(): context.run_migrations()
else:
    connectable=configured_engine(DATABASE_URL,DATABASE_CONNECT_ARGS,PRIVATE_SCHEMA,poolclass=pool.NullPool)
    with connectable.connect() as connection:
        if PRIVATE_SCHEMA:
            initialize_private_schema(connection, DATABASE_URL)
        context.configure(connection=connection,target_metadata=Base.metadata)
        with context.begin_transaction(): context.run_migrations()
