"""Restore only exact-hash bundled fictional sources onto a new persistent volume."""
import hashlib
import os
import re
from pathlib import Path
from sqlalchemy import select
from backend.db import Session
from backend.universal_models import ControlledChange


def restore(source, storage, fixtures):
    key = source.get('storage_key', '')
    if not re.fullmatch(r'[a-f0-9]{32}\.csv', key):
        return False
    expected = source.get('sha256')
    content = fixtures.get(expected)
    if content is None or hashlib.sha256(content).hexdigest() != expected:
        return False
    target = storage / key
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise RuntimeError('Existing source differs; restore refused.')
        return False
    with target.open('xb') as stream:
        stream.write(content)
    return True


def main():
    storage = Path(os.environ['STORAGE_PATH'])
    storage.mkdir(parents=True, exist_ok=True)
    fixtures = {}
    for path in Path('samples/multidomain').glob('*.csv'):
        content = path.read_bytes()
        fixtures[hashlib.sha256(content).hexdigest()] = content
    count = 0
    with Session() as session:
        for change in session.scalars(select(ControlledChange)):
            if change.data.get('demo') is not True:
                continue
            for source in change.data.get('sources', {}).values():
                count += restore(source, storage, fixtures)
    print(f'Restored {count} exact-hash fictional source files. Database evidence was not changed.')


if __name__ == '__main__':
    main()
