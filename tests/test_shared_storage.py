import hashlib
from uuid import uuid4
import pytest
from backend.storage import DatabaseStorage


def test_shared_bytes_survive_new_storage_instances(client):
    key = uuid4().hex + '.csv'
    content = b'id,value\nC27,20\n'
    store = DatabaseStorage()
    assert not (store / key).exists()
    (store / key).write_bytes(content)
    assert (DatabaseStorage() / key).read_bytes() == content
    with pytest.raises(FileExistsError):
        (store / key).write_bytes(b'replacement')


def test_storage_rejects_traversal_and_missing_objects(client):
    store = DatabaseStorage()
    with pytest.raises(ValueError):
        store / '../private.env'
    with pytest.raises(FileNotFoundError):
        (store / (uuid4().hex + '.csv')).read_bytes()


def test_storage_quota(client, monkeypatch):
    monkeypatch.setenv('DOCUMENT_STORAGE_LIMIT_MB', '0')
    with pytest.raises(ValueError, match='capacity'):
        (DatabaseStorage() / (uuid4().hex + '.csv')).write_bytes(b'x')


def test_structured_sources_download_from_database(company, monkeypatch):
    from backend import universal
    c, _ = company
    monkeypatch.setattr(universal, 'STORAGE', DatabaseStorage())
    owner = c.get('/api/v1/auth/me').json()['id']
    response = c.post('/api/v1/changes', json={'domain':'engineering','title':'Shared storage test','owner':owner,'reason':'Verify durable source bytes','mode':'QUICK'})
    assert response.status_code == 201, response.text
    change = response.json()
    response = c.post('/api/v1/changes/'+change['id']+'/sources/old/upload',
        params={'label':'Rev A','expected_version':change['version'],'reason':'Test durable upload'},
        files={'file':('source.csv', b'id,nominal\nC27,20\n', 'text/csv')})
    assert response.status_code == 200, response.text
    downloaded = c.get('/api/v1/changes/'+change['id']+'/sources/old/download')
    assert downloaded.status_code == 200
    assert downloaded.content == b'id,nominal\nC27,20\n'
    c.post('/api/v1/auth/logout')
    assert c.get('/api/v1/changes/'+change['id']+'/sources/old/download').status_code == 401
