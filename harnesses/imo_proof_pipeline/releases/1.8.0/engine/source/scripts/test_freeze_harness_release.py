import json

import pytest

from scripts.freeze_harness_release import digest, sources, verify
from scripts import freeze_harness_release as freezer


def put(root, name, body):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


def test_static_closure_includes_workers_relative_imports_and_literal_imports(tmp_path):
    put(tmp_path, "candidate/__init__.py", "from . import main\n")
    put(tmp_path, "candidate/main.py", "from helpers import math\nimport importlib\nimportlib.import_module('dynamic.worker')\n")
    put(tmp_path, "candidate/spawned_worker.py", "import fractions\nPROMPT = 'prompts/generic.md'\n")
    put(tmp_path, "prompts/generic.md", "Generic prompt.\n")
    put(tmp_path, "helpers/__init__.py", "")
    put(tmp_path, "helpers/math.py", "import sympy\n")
    put(tmp_path, "dynamic/__init__.py", "")
    put(tmp_path, "dynamic/worker.py", "")
    put(tmp_path, "unrelated.py", "raise RuntimeError('must not be imported')")
    put(tmp_path, "candidate/__pycache__/bad.py", "bad syntax %")
    found, external = sources(tmp_path, "candidate")
    assert {str(p.relative_to(tmp_path)) for p in found} == {
        "candidate/__init__.py", "candidate/main.py", "candidate/spawned_worker.py",
        "helpers/__init__.py", "helpers/math.py", "dynamic/__init__.py", "dynamic/worker.py",
        "prompts/generic.md"}
    assert external == ["sympy"]


def release(tmp_path):
    source = put(tmp_path, "source/example.py", "frozen = True\n")
    lock = put(tmp_path, "freeze.json", json.dumps({"release_id": "test", "files": {"source/example.py": digest(source)}}))
    put(tmp_path, "SHA256SUMS", f"{digest(source)}  source/example.py\n{digest(lock)}  freeze.json\n")


def test_verify_detects_mutated_missing_and_extra_files(tmp_path):
    release(tmp_path)
    assert verify(tmp_path)["verified"]
    put(tmp_path, "source/example.py", "frozen = False\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        verify(tmp_path)
    release(tmp_path)
    put(tmp_path, "source/unlisted.py", "")
    with pytest.raises(ValueError, match="Unlisted/missing"):
        verify(tmp_path)


def test_verify_rejects_symlink_even_when_content_matches(tmp_path):
    release(tmp_path)
    original = tmp_path / "source/example.py"
    original.rename(tmp_path / "outside.py")
    original.symlink_to(tmp_path / "outside.py")
    with pytest.raises(ValueError):
        verify(tmp_path)


def test_source_only_release_has_no_fabricated_run_or_score(tmp_path, monkeypatch):
    put(tmp_path, "candidate/__init__.py", "")
    profile = put(tmp_path, "profile.json", '{"terminal_checkpoint": "cycle3"}')
    monkeypatch.setattr(freezer, "environment", lambda: {"model_weights_bundled": False})
    output = tmp_path / "release"
    result = freezer.build(tmp_path, "candidate", None, None, output, "source-test", [], profile=profile)
    assert result["verified"] and verify(output)["verified"]
    lock = json.loads((output / "freeze.json").read_text())
    assert lock["release_kind"] == "source_only"
    assert lock["reference_run"] is None and lock["reference_scores"] is None
    assert not (output / "reference").exists()
    assert (output / "runtime_profile.json").read_bytes() == profile.read_bytes()
    with pytest.raises(FileExistsError):
        freezer.build(tmp_path, "candidate", None, None, output, "source-test", [])


def test_incomplete_reference_is_not_allowed(tmp_path):
    put(tmp_path, "candidate/__init__.py", "")
    run = tmp_path / "unfinished"
    put(run, "result.json", '{"state": "running"}')
    with pytest.raises(ValueError, match="must have completed"):
        freezer.build(tmp_path, "candidate", run, None, tmp_path / "release", "bad", [])
    assert not (tmp_path / "release").exists()
