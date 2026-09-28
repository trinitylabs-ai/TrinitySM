"""External reference preparation preserves inputs without distributing bodies."""
import hashlib
import importlib
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def fetcher(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / 'scripts'))
    return importlib.import_module('prepare_imo_references')


def sample(fetcher):
    pdf, raw = b'example PDF bytes', b'non-distributed example text\n\f'
    normalized = raw.decode().strip().encode()
    row = dict(problem_id='imo2026_p1', pdf_sha256=fetcher.digest(pdf),
               extracted_sha256=fetcher.digest(raw), reference_sha256=fetcher.digest(normalized),
               download_url='https://example.invalid/source.pdf', local_grading_inputs=[
                   dict(path='grading/original.txt', format='pdftotext_layout', sha256=fetcher.digest(raw)),
                   dict(path='grading/normalized.txt', format='strip', sha256=fetcher.digest(normalized))])
    return pdf, raw, {'references': [row]}


def test_prepare_reconstructs_exact_input_bytes_without_network(fetcher, tmp_path, monkeypatch):
    pdf, raw, manifest = sample(fetcher)
    cache = tmp_path/'cache'; cache.mkdir(); (cache/'imo2026_p1.pdf').write_bytes(pdf)
    monkeypatch.setattr(fetcher.urllib.request, 'urlopen', lambda *a, **k: pytest.fail('unexpected download'))
    monkeypatch.setattr(fetcher.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout=raw))
    root = tmp_path/'repo'; root.mkdir()
    assert fetcher.prepare(manifest, root, cache) == 2
    assert (root/'grading/original.txt').read_bytes() == raw
    assert (root/'grading/normalized.txt').read_bytes() == raw.decode().strip().encode()
    assert fetcher.verify(manifest, root) == 2


def test_changed_extraction_cannot_change_grading_inputs(fetcher, tmp_path, monkeypatch):
    pdf, raw, manifest = sample(fetcher)
    cache = tmp_path/'cache'; cache.mkdir(); (cache/'imo2026_p1.pdf').write_bytes(pdf)
    monkeypatch.setattr(fetcher.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout=raw+b'changed'))
    with pytest.raises(ValueError, match='PDF text extraction'):
        fetcher.prepare(manifest, tmp_path, cache)
    assert not (tmp_path/'grading').exists()


def test_conflicting_existing_input_is_not_overwritten(fetcher, tmp_path, monkeypatch):
    pdf, raw, manifest = sample(fetcher)
    (tmp_path/'imo2026_p1.pdf').write_bytes(pdf)
    original = tmp_path/'grading/normalized.txt'; original.parent.mkdir(); original.write_text('keep')
    monkeypatch.setattr(fetcher.subprocess, 'run', lambda *a, **k: SimpleNamespace(stdout=raw))
    with pytest.raises(ValueError, match='Hash mismatch'):
        fetcher.prepare(manifest, tmp_path, tmp_path)
    assert original.read_text() == 'keep'
    assert not (tmp_path/'grading/original.txt').exists()


def test_incorrect_download_is_not_cached(fetcher, tmp_path, monkeypatch):
    _, _, manifest = sample(fetcher)
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self): return b'wrong upstream content'
    monkeypatch.setattr(fetcher.urllib.request, 'urlopen', lambda *a, **k: Response())
    target = tmp_path/'reference.pdf'
    with pytest.raises(ValueError, match='Hash mismatch'):
        fetcher.fetch_pdf(manifest['references'][0], target)
    assert not target.exists()


def test_destinations_cannot_escape_checkout(fetcher, tmp_path):
    with pytest.raises(ValueError): fetcher.checked_path(tmp_path, '../outside.txt')
    with pytest.raises(ValueError): fetcher.checked_path(tmp_path, '/absolute.txt')
    (tmp_path/'redirect').symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError): fetcher.checked_path(tmp_path, 'redirect/reference.txt')


def test_audit_detects_renamed_or_whitespace_wrapped_reference(fetcher):
    audit = importlib.import_module('audit_release')
    hashes = {hashlib.sha256(b'reference body').hexdigest()}
    assert audit.inspect_external_reference('innocent.md', b'\nreference body\n', hashes, set())
    assert not audit.inspect_external_reference('metadata.json', b'{"source": "url"}', hashes, set())
