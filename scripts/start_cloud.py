"""Single-instance persistent cloud service. Migrations must succeed before serving."""
import os
import subprocess
import sys
from pathlib import Path


def main():
    if not os.getenv('DATABASE_URL') and not os.getenv('DATABASE_URL_FILE'):
        raise SystemExit('A server-side database secret is required.')
    storage = Path(os.environ['STORAGE_PATH'])
    storage.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'], check=True)
    if os.getenv('RESTORE_BUNDLED_DEMO') == '1':
        subprocess.run([sys.executable, '-m', 'scripts.restore_demo_sources'], check=True)
    os.execv(sys.executable, [sys.executable, '-m', 'uvicorn', 'backend.main:app',
        '--host', '0.0.0.0', '--port', os.getenv('PORT', '8000'), '--no-access-log'])


if __name__ == '__main__':
    main()
