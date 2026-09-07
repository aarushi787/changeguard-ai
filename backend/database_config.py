"""Shared database configuration for the API, workers and migrations."""
import os
from pathlib import Path
from sqlalchemy.engine import make_url
from sqlalchemy import create_engine, event


def database_settings(environ=None):
    env = os.environ if environ is None else environ
    raw = env.get('DATABASE_URL')
    if not raw and env.get('DATABASE_URL_FILE'):
        raw = Path(env['DATABASE_URL_FILE']).read_text(encoding='utf-8').strip()
    try:
        url = make_url(raw or 'sqlite:///./data/changeguard.db')
    except Exception:
        raise ValueError('Invalid database URL; check local database configuration.') from None
    if url.drivername in {'postgres', 'postgresql'}:
        url = url.set(drivername='postgresql+psycopg')
    host = (url.host or '').lower()
    supabase = host.endswith('.supabase.co') or host.endswith('.supabase.com')
    args = {'check_same_thread': False} if url.get_backend_name() == 'sqlite' else {}
    if supabase:
        if url.port == 6543:
            raise ValueError('Use the Supabase direct or session pooler connection on port 5432.')
        if url.query.get('sslmode', 'require') not in {'require', 'verify-ca', 'verify-full'}:
            raise ValueError('Supabase connections require TLS.')
        url = url.update_query_dict({'sslmode': url.query.get('sslmode', 'require')})
        args = {'connect_timeout': 15}
        if 'options' in url.query:
            raise ValueError('Remove options from the Supabase URL; the application sets its private schema.')
    return url, args, supabase


def set_private_schema(connection, record):
    # Supavisor may ignore startup options; set this on the actual session.
    with connection.cursor() as cursor:
        cursor.execute('SET SESSION search_path TO changeguard')
    connection.commit()


def configured_engine(url, connect_args, supabase, **kwargs):
    engine = create_engine(url, connect_args=connect_args, hide_parameters=True, **kwargs)
    if supabase:
        event.listen(engine, 'connect', set_private_schema)
    return engine
