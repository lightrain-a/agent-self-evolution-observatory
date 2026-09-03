from __future__ import annotations

import inspect

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh2_runtime_20260903 as fresh
from research_pipeline import run_c1_pacta_msr_runtime_20260902 as base


def test_fresh2_runtime_binding_is_content_addressed():
    assert fresh.MANIFEST_SHA256 == "45be64121d04d8b5146364463154a2c87e43f410e4449b274f77bd99cbd553c4"
    assert fresh.BLOB_PLAN_SHA256 == "d770b3da1527709114aa866d54f944f833069ae2c72c3f46cefb6421d467d8a3"
    assert fresh.BLOB_RECEIPT_SHA256 == "ba50bb14f170d6c180bb7fa500b5110bfde73e967e04228cde03be3707e4569a"
    assert fresh.FRESH2_POOL_SHA256 == "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"


def test_fresh2_runtime_uses_separate_roots():
    assert "fresh2-images-20260903-v1" in str(fresh.IMAGE_ROOT)
    assert "fresh2-runtime-20260903-v1" in str(fresh.DEFAULT_ROOT)
    assert "fresh2-oci-layouts" in str(fresh.LAYOUT_ROOT)


def test_binding_changes_only_runtime_input_roots_and_hashes():
    source = inspect.getsource(fresh.bind)
    for name in ("IMAGE_ROOT", "DEFAULT", "LAYOUT_ROOT", "MANIFEST_SHA", "BLOB_RECEIPT_SHA"):
        assert f"base.{name}" in source
    assert "docker" not in source.lower()
    assert "provider" not in source.lower()


def test_audit_passes_and_remains_zero_provider():
    row = fresh.audit_inputs()
    assert row["fresh_pool_sha256"] == fresh.FRESH2_POOL_SHA256
    assert row["image_count"] == 20
    assert row["unique_blob_count"] == 86
    assert row["provider_calls"] == 0
    assert row["scientific_calls"] == 0


def test_underlying_runtime_is_rootful_and_exact_base():
    assert base.ROOTFUL_HOST == "unix:///var/run/docker.sock"
    source = inspect.getsource(base.qualify_one)
    assert "git reset --hard" in source
    assert "merge-base --is-ancestor" in source
    assert "post_reset_head_exact" in source


def test_runtime_surface_has_no_model_calls():
    source = inspect.getsource(base)
    assert "AA_API_KEY" not in source
    assert "atomcode" not in source.lower()
    assert "chat/completions" not in source
