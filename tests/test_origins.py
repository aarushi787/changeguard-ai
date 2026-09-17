import pytest
import backend.main as main
from backend.origins import configured_origins


def test_production_aliases_are_exact_and_keep_existing_origin():
    origins = configured_origins(True, {
        'APP_ORIGIN': 'https://existing.example',
        'APP_ADDITIONAL_ORIGINS': ' https://review.example/, https://existing.example, ',
    })
    assert origins == {'https://existing.example', 'https://review.example'}
    assert 'http://localhost:5173' not in origins


@pytest.mark.parametrize('value', [
    '*', 'https://*.vercel.app', 'https://user:secret@example.com',
    'https://example.com/path', 'https://example.com?query=x',
    'https://example.com#fragment', 'http://example.com', 'null',
    'https://example.com:bad', 'https://exa mple.com',
])
def test_invalid_production_origins_fail_closed(value):
    with pytest.raises(ValueError, match='exact HTTPS'):
        configured_origins(True, {'APP_ORIGIN': 'https://app.example',
                                  'APP_ADDITIONAL_ORIGINS': value})


def test_new_domain_login_session_and_old_domain_remain_working(company, monkeypatch):
    client, account = company
    monkeypatch.setattr(main, 'ALLOWED_ORIGINS', configured_origins(True, {
        'APP_ORIGIN': 'https://changeguard-ai.vercel.app',
        'APP_ADDITIONAL_ORIGINS': 'https://mccia-reviewdesk.vercel.app',
    }))
    for origin in ['https://mccia-reviewdesk.vercel.app', 'https://changeguard-ai.vercel.app']:
        response = client.post('/api/v1/auth/login', headers={'Origin': origin},
                               json={'email': account['email'], 'password': account['password']})
        assert response.status_code == 200
        assert client.get('/api/v1/auth/me').status_code == 200
        assert client.post('/api/v1/auth/logout', headers={'Origin': origin}).status_code == 200


@pytest.mark.parametrize('origin', [
    'https://mccia-reviewdesk.vercel.app.evil.example',
    'https://other-team.vercel.app', 'http://mccia-reviewdesk.vercel.app',
    'null', 'http://localhost:5173',
])
def test_untrusted_origins_cannot_submit(client, monkeypatch, origin):
    monkeypatch.setattr(main, 'ALLOWED_ORIGINS', configured_origins(True, {
        'APP_ORIGIN': 'https://mccia-reviewdesk.vercel.app',
    }))
    response = client.post('/api/v1/auth/login', headers={'Origin': origin},
                           json={'email': 'nobody@example.test', 'password': 'unused'})
    assert response.status_code == 403
    assert response.text == 'Origin not allowed'


def test_trusted_origin_still_requires_safety_header(client, monkeypatch):
    origin = 'https://mccia-reviewdesk.vercel.app'
    monkeypatch.setattr(main, 'ALLOWED_ORIGINS', frozenset({origin}))
    response = client.post('/api/v1/auth/login', headers={'Origin': origin, 'X-ChangeGuard': ''},
                           json={'email': 'nobody@example.test', 'password': 'unused'})
    assert response.status_code == 403
    assert response.text == 'Missing request safety header'
