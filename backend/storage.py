"""Private immutable byte storage. API tenant checks govern access to blob references."""
import hashlib
import os
import re
from pathlib import Path
from sqlalchemy import select, func, text
from backend.db import DocumentBlob, Session

class StorageCapacityError(ValueError):
    pass


class DatabaseObject:
    def __init__(self, key):
        if not re.fullmatch(r'[a-f0-9]{32}\.[a-z0-9]{1,8}', key):
            raise ValueError('Invalid storage key')
        self.key = key

    def read_bytes(self):
        with Session() as session:
            row = session.get(DocumentBlob, self.key)
            if row is None:
                raise FileNotFoundError('Controlled source is not available in shared storage.')
            content = bytes(row.content)
            if hashlib.sha256(content).hexdigest() != row.sha256:
                raise ValueError('Stored source integrity check failed.')
            return content

    def exists(self):
        with Session() as session:
            return session.scalar(select(DocumentBlob.key).where(DocumentBlob.key == self.key)) is not None

    def write_bytes(self, content):
        if len(content) > 25 * 1024 * 1024:
            raise StorageCapacityError('Shared storage object exceeds the 25 MB pilot limit.')
        with Session.begin() as session:
            if session.bind.dialect.name == 'postgresql':
                session.execute(text('SELECT pg_advisory_xact_lock(726184902)'))
            if session.get(DocumentBlob, self.key) is not None:
                raise FileExistsError('Controlled source keys are immutable.')
            total = session.scalar(select(func.coalesce(func.sum(DocumentBlob.size), 0)))
            limit = int(os.getenv('DOCUMENT_STORAGE_LIMIT_MB', '200')) * 1024 * 1024
            if total + len(content) > limit:
                raise StorageCapacityError('Pilot document storage capacity reached.')
            session.add(DocumentBlob(key=self.key, content=content, size=len(content), sha256=hashlib.sha256(content).hexdigest()))
        return len(content)


class DatabaseStorage:
    def __truediv__(self, key):
        return DatabaseObject(str(key))


def document_storage():
    mode = os.getenv('STORAGE_BACKEND', 'filesystem')
    if mode == 'database':
        return DatabaseStorage()
    if mode != 'filesystem':
        raise ValueError('Unknown document storage backend')
    path = Path(os.getenv('STORAGE_PATH', 'data/documents')).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path
