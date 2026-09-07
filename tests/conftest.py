import os
import tempfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

Path('tmp').mkdir(exist_ok=True)
TEST_ROOT=tempfile.mkdtemp(prefix='cg-tests-',dir='tmp')
os.environ['DATABASE_URL']=os.getenv('TEST_DATABASE_URL') or 'sqlite:///'+str(Path(TEST_ROOT,'test.db').resolve()).replace('\\','/')
os.environ['STORAGE_PATH']=str(Path(TEST_ROOT,'documents').resolve())
os.environ['RUN_WORKER']='0'
os.environ['ENVIRONMENT']='test'
from backend.main import app

@pytest.fixture
def client():
    with TestClient(app,headers={'X-ChangeGuard':'1'}) as c: yield c

@pytest.fixture
def company(client):
    from uuid import uuid4
    email=f'{uuid4().hex}@example.test'
    payload={'email':email,'password':'TestPassword!2026','name':'Test Engineer','organization':'Fictional Test Company','pack':'precision_engineering'}
    assert client.post('/api/v1/auth/register',json=payload).status_code==201
    assert client.post('/api/v1/auth/login',json={'email':email,'password':payload['password']}).status_code==200
    # Rate limiting is a separate test; clear between independently provisioned test companies.
    from backend.main import LOGIN_ATTEMPTS
    LOGIN_ATTEMPTS.clear()
    return client,payload
