"""Load private local configuration without overriding deployment secrets."""
import os
from pathlib import Path
from dotenv import dotenv_values


def load_environment(path=None, environ=None):
    env = os.environ if environ is None else environ
    if env.get('ENVIRONMENT') == 'test':
        return
    path = Path(path) if path is not None else Path(__file__).resolve().parent.parent / '.env'
    if not path.is_file():
        return
    for key, value in dotenv_values(path, interpolate=False).items():
        if value is None or (key == 'DATABASE_URL' and env.get('DATABASE_URL_FILE')):
            continue
        env.setdefault(key, value)
