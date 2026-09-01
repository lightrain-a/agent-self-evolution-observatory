import json
from pathlib import Path

import pytest

from research_pipeline.run_c1_pacta_rb_qwen397_t05_images_20260901 import (
    SPECS,
    atomic_bytes,
    image_ref,
    sha_file,
    unique_amd64,
)

def test_fixed_eleven_unique():
    assert len(SPECS) == 11
    assert len({row[0] for row in SPECS}) == 11
    assert all(len(row[1]) == 64 and len(row[2]) == 64 for row in SPECS)

def test_image_reference_exact():
    assert image_ref("pydata__xarray-4966") == "swebench/sweb.eval.x86_64.pydata_1776_xarray-4966:latest"
    assert image_ref("scikit-learn__scikit-learn-14496") == "swebench/sweb.eval.x86_64.scikit-learn_1776_scikit-learn-14496:latest"

def test_unique_amd64():
    wanted = {"digest": "sha256:" + "a" * 64, "platform": {"os": "linux", "architecture": "amd64"}}
    index = {"manifests": [
        wanted,
        {"digest": "sha256:" + "b" * 64, "platform": {"os": "linux", "architecture": "arm64"}},
    ]}
    assert unique_amd64(index) is wanted

@pytest.mark.parametrize("rows", [[], [
    {"digest": "sha256:" + "a" * 64, "platform": {"os": "linux", "architecture": "amd64"}},
    {"digest": "sha256:" + "b" * 64, "platform": {"os": "linux", "architecture": "amd64"}},
]])
def test_unique_amd64_fail_closed(rows):
    with pytest.raises(RuntimeError):
        unique_amd64({"manifests": rows})

def test_atomic_bytes_and_digest_tamper_detected(tmp_path: Path):
    path = tmp_path / "raw"
    digest = atomic_bytes(path, b"exact response")
    assert sha_file(path) == digest
    path.write_bytes(b"changed response")
    assert sha_file(path) != digest
