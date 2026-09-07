import pytest
from backend.database_config import database_settings


def test_sqlite_unchanged():
    url, args, private = database_settings({})
    assert url.drivername == 'sqlite' and args['check_same_thread'] is False and not private


@pytest.mark.parametrize('prefix', ['postgres', 'postgresql', 'postgresql+psycopg'])
def test_supabase_url_tls_private_schema(prefix):
    url, args, private = database_settings({'DATABASE_URL': f'{prefix}://postgres:pass%25word@db.example.supabase.co:5432/postgres'})
    assert url.drivername == 'postgresql+psycopg'
    assert url.password == 'pass%word'
    assert url.query['sslmode'] == 'require'
    assert args['connect_timeout'] == 15 and private


def test_private_schema_set_on_real_session():
    from unittest.mock import MagicMock
    from backend.database_config import set_private_schema
    connection = MagicMock()
    set_private_schema(connection, None)
    connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with('SET SESSION search_path TO changeguard')
    connection.commit.assert_called_once()


@pytest.mark.parametrize('suffix', [':6543/postgres', ':5432/postgres?sslmode=disable', ':5432/postgres?options=unsafe'])
def test_reject_unsafe_supabase_config(suffix):
    with pytest.raises(ValueError):
        database_settings({'DATABASE_URL': 'postgresql://postgres:secret@aws-0.example.pooler.supabase.com' + suffix})


def test_secret_file_and_env_precedence(tmp_path):
    path = tmp_path / 'database.txt'
    path.write_text('postgresql://postgres:secret@db.example.supabase.co/postgres')
    assert database_settings({'DATABASE_URL_FILE': str(path)})[2]
    assert not database_settings({'DATABASE_URL': 'sqlite://', 'DATABASE_URL_FILE': str(path)})[2]


def test_malformed_url_does_not_echo_secret():
    with pytest.raises(ValueError) as failure:
        database_settings({'DATABASE_URL': 'secret-password'})
    assert 'secret-password' not in str(failure.value)
