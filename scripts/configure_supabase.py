"""Run interactively: python -m scripts.configure_supabase. Never echoes credentials."""
from getpass import getpass
import argparse
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from backend.database_config import database_settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host')
    parser.add_argument('--username')
    parser.add_argument('--password-dialog', action='store_true')
    args_in = parser.parse_args()
    if args_in.password_dialog:
        if not args_in.host or not args_in.username:
            parser.error('--host and --username are required with --password-dialog')
        import tkinter as tk
        from tkinter.simpledialog import askstring
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        password = askstring('Connect ChangeGuard to Supabase',
            'Enter the database password you set for ChangeGuard AI.\nIt will be saved locally, excluded from Git, and never printed.',
            show='*', parent=root)
        root.destroy()
        if not password:
            print('Cancelled. No connection settings changed.')
            return 1
        raw = URL.create('postgresql+psycopg', username=args_in.username, password=password,
            host=args_in.host, port=5432, database='postgres').render_as_string(hide_password=False)
    else:
        raw = getpass('Supabase direct/session PostgreSQL URL (hidden): ').strip()
    try:
        url, args, is_supabase = database_settings({'DATABASE_URL': raw})
        if not is_supabase:
            raise ValueError('Use a Supabase PostgreSQL connection URL.')
        with create_engine(url, connect_args=args, hide_parameters=True).connect() as connection:
            connection.execute(text('SELECT 1'))
    except Exception as error:
        detail = str(error).lower()
        if 'password authentication failed' in detail or 'wrong password' in detail:
            reason = 'The database rejected the password.'
        elif 'tenant or user not found' in detail:
            reason = 'The pooler did not recognize this project/user.'
        elif 'options' in detail or 'search_path' in detail:
            reason = 'The pooler rejected the private-schema connection setting.'
        elif 'certificate' in detail or 'ssl' in detail:
            reason = 'TLS verification or negotiation failed.'
        elif 'timeout' in detail or 'timed out' in detail:
            reason = 'The database connection timed out.'
        else:
            reason = 'Database driver failure (' + type(error).__name__ + ').'
        print('Connection failed. ' + reason + ' No credentials were saved.')
        return 1
    target = Path('data/supabase-database-url.txt')
    target.parent.mkdir(exist_ok=True)
    target.write_text(raw, encoding='utf-8')
    target.chmod(0o600)
    print('Connection verified. Saved to the Git-ignored local data directory. Run scripts/start-supabase.ps1 next.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
