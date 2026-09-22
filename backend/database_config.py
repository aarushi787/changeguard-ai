"""Shared database configuration for the API, workers and migrations."""
import os
from pathlib import Path
from sqlalchemy.engine import make_url
from sqlalchemy import create_engine, event, text


def is_supabase(url):
    host = (url.host or '').lower()
    return host.endswith('.supabase.co') or host.endswith('.supabase.com')


def is_neon(url):
    return (url.host or '').lower().endswith('.neon.tech')


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
    supabase = is_supabase(url)
    neon = is_neon(url)
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
    if neon:
        if '-pooler.' in (url.host or '').lower():
            raise ValueError('Use the Neon direct connection with pooling disabled; session schema settings require it.')
        if url.query.get('sslmode', 'require') not in {'require', 'verify-ca', 'verify-full'}:
            raise ValueError('Neon connections require TLS.')
        if 'options' in url.query:
            raise ValueError('Remove options from the Neon URL; the application sets its private schema.')
        url = url.update_query_dict({'sslmode': url.query.get('sslmode', 'require')})
        args = {'connect_timeout': 15}
    return url, args, supabase or neon


def set_private_schema(connection, record):
    # Supavisor may ignore startup options; set this on the actual session.
    with connection.cursor() as cursor:
        cursor.execute('SET SESSION search_path TO changeguard')
    connection.commit()


def configured_engine(url, connect_args, private_schema, **kwargs):
    engine = create_engine(url, connect_args=connect_args, hide_parameters=True, **kwargs)
    if private_schema:
        event.listen(engine, 'connect', set_private_schema)
    return engine


def initialize_private_schema(connection, url):
    """Bootstrap only our schema; provider-specific roles may not exist on Neon."""
    connection.execute(text('CREATE SCHEMA IF NOT EXISTS changeguard'))
    connection.execute(text('REVOKE ALL ON SCHEMA changeguard FROM PUBLIC'))
    if is_supabase(url):
        connection.execute(text('REVOKE ALL ON SCHEMA changeguard FROM anon, authenticated'))
    connection.commit()
