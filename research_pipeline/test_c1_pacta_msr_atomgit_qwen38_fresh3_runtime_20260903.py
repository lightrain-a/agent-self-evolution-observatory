from __future__ import annotations

import inspect

import pytest

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_runtime_20260903 as r
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_fresh3_manifest_and_blob_plan_are_content_addressed() -> None:
    assert sha256_file(r.IMAGE_ROOT / "manifest-freeze.json") == r.MANIFEST_SHA
    assert sha256_file(r.IMAGE_ROOT / "blob-plan.json") == r.BLOB_PLAN_SHA


def test_blob_receipt_sha_is_runtime_parameter_not_posthoc_code_edit() -> None:
    r.bind("0" * 64)
    assert r.base.BLOB_RECEIPT_SHA == "0" * 64
    with pytest.raises(RuntimeError):
        r.bind("bad")


def test_runtime_is_zero_provider_and_reuses_exact_digest_importer() -> None:
    source = inspect.getsource(r)
    assert "atomcode" not in source.lower()
    assert "provider_calls" in source
    assert "base.import_all(root)" in source
    assert "base.preflight(root)" in source


def test_targeted_build_clean_is_uniform_and_conservative() -> None:
    source = inspect.getsource(r.qualify_one)
    assert "git diff --quiet && git diff --cached --quiet" in source
    assert "git ls-files --others --exclude-standard" in source
    assert "path == \"build\" or path.startswith(\"build/\")" in source
    assert "git clean -fd -- build" in source
    assert "-fdx" not in source


def test_qualification_requires_all_twenty() -> None:
    source = inspect.getsource(r.qualify)
    assert "qualified == 20" in source
    assert "FRESH3_MSR_20_RUNTIME_READY_AFTER_TARGETED_BUILD_CLEAN" in source
    assert "HOLD_FRESH3_RUNTIME_SUPPORT_INCOMPLETE" in source


def test_no_scientific_execution_surface() -> None:
    source = inspect.getsource(r)
    for forbidden in ("execute_trajectory(", "writer_twins_valid(", "shadow_phase(", "final_measurement("):
        assert forbidden not in source
