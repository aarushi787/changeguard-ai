"""Read-only live connection checks; prints no credentials or document contents."""
import json
from sqlalchemy import text
from backend.db import engine, SUPABASE


def main():
    if not SUPABASE:
        raise SystemExit('Configure a Supabase database before running this check.')
    with engine.connect() as connection:
        def scalar(sql):
            return connection.execute(text(sql)).scalar()
        result = {
            'schema': scalar('select current_schema()'),
            'migration': scalar('select version_num from alembic_version'),
            'client_connection_tls': bool(connection.connection.driver_connection.pgconn.ssl_in_use),
            'users': scalar('select count(*) from users'),
            'changes': scalar('select count(*) from controlled_changes'),
            'anon_schema_access': scalar("select has_schema_privilege('anon','changeguard','USAGE')"),
            'authenticated_schema_access': scalar("select has_schema_privilege('authenticated','changeguard','USAGE')"),
        }
        print(json.dumps(result))
        if result['schema'] != 'changeguard' or not result['client_connection_tls'] or result['anon_schema_access'] or result['authenticated_schema_access']:
            raise SystemExit('Private schema check failed.')


if __name__ == '__main__':
    main()
