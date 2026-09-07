import hashlib
import pytest
from scripts.restore_demo_sources import restore


def test_restore_preserves_evidence(tmp_path):
    content = b'id,value\nC27,20\n'
    digest = hashlib.sha256(content).hexdigest()
    source = {'storage_key': 'a' * 32 + '.csv', 'sha256': digest}
    assert restore(source, tmp_path, {digest: content})
    assert not restore(source, tmp_path, {digest: content})
    (tmp_path / source['storage_key']).write_bytes(b'changed')
    with pytest.raises(RuntimeError):
        restore(source, tmp_path, {digest: content})


def test_unknown_sources_and_traversal_are_not_restored(tmp_path):
    assert not restore({'storage_key': '../outside.csv', 'sha256': 'x'}, tmp_path, {'x': b'x'})
    assert not restore({'storage_key': 'a' * 32 + '.csv', 'sha256': 'unknown'}, tmp_path, {})
    assert not list(tmp_path.iterdir())
