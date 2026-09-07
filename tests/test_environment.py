from backend.environment import load_environment


def test_dotenv_preserves_secrets_and_explicit_settings(tmp_path):
    path = tmp_path / '.env'
    path.write_text('DATABASE_URL=postgresql://user:literal${PASSWORD}@db.example/postgres\nAPP_ORIGIN=https://file.example\nRUN_WORKER=1\n')
    env = {'APP_ORIGIN': 'https://deployment.example'}
    load_environment(path, env)
    assert env['APP_ORIGIN'] == 'https://deployment.example'
    assert '${PASSWORD}' in env['DATABASE_URL']
    assert env['RUN_WORKER'] == '1'


def test_explicit_secret_file_and_test_mode_are_preserved(tmp_path):
    path = tmp_path / '.env'
    path.write_text('DATABASE_URL=postgresql://local\nRUN_WORKER=1\n')
    env = {'DATABASE_URL_FILE': '/deployment/secret'}
    load_environment(path, env)
    assert 'DATABASE_URL' not in env
    isolated = {'ENVIRONMENT': 'test'}
    load_environment(path, isolated)
    assert isolated == {'ENVIRONMENT': 'test'}
