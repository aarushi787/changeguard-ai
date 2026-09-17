"""Exact browser origins allowed to submit authenticated mutations."""
import os
from urllib.parse import urlsplit


def configured_origins(production: bool, environ=None) -> frozenset[str]:
    env = os.environ if environ is None else environ
    primary = env.get('APP_ORIGIN', 'http://127.0.0.1:5173')
    extra = env.get('APP_ADDITIONAL_ORIGINS', '')
    origins = set()
    for value in [primary, *extra.split(',')]:
        value = value.strip()
        if not value:
            continue
        try:
            parsed = urlsplit(value)
            valid = (
                parsed.scheme in ({'https'} if production else {'https', 'http'})
                and parsed.hostname and parsed.netloc
                and not parsed.username and not parsed.password
                and parsed.path in {'', '/'}
                and not parsed.query and not parsed.fragment
                and not any(c.isspace() or c in '*\\%?#' for c in value)
            )
            parsed.port  # Validate any explicit port.
        except ValueError:
            valid = False
        if not valid:
            # Configuration may accidentally contain secrets; never echo its value.
            raise ValueError('App origins must be exact HTTPS origins in production, without credentials, paths or wildcards.')
        origins.add(value.rstrip('/'))
    if not origins:
        raise ValueError('At least one app origin must be configured.')
    if not production:
        origins.update({'http://127.0.0.1:8010', 'http://localhost:8010',
                        'http://127.0.0.1:5173', 'http://localhost:5173'})
    return frozenset(origins)
