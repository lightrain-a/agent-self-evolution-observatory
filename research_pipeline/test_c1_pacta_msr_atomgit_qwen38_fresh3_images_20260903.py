from __future__ import annotations

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh3_images_20260903 as img
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_fresh3_pool_binding_is_content_addressed() -> None:
    assert sha256_file(img.POOL) == img.POOL_SHA
    assert img.POOL_SHA == "3780fa80ee0bbfce01e3fd4f6bcabe6aaaa21111c0aa910ea7ce1bde302a9257"


def test_image_geometry_is_twenty_unique_source_future_rows() -> None:
    img.bind(); rows = img.base.image_units()
    assert len(rows) == 20
    assert len({row["instance_id"] for row in rows}) == 20
    assert sum(row["role"] == "source" for row in rows) == 10
    assert sum(row["role"] == "future" for row in rows) == 10


def test_audit_is_zero_provider() -> None:
    row = img.audit()
    assert row["status"] == "FRESH3_IMAGE_RESOLVER_BINDING_PASS"
    assert row["image_count"] == 20
    assert row["provider_calls"] == 0
    assert row["scientific_source_calls"] == 0


def test_wrapper_reuses_double_resolution_logic() -> None:
    assert callable(img.base.resolve)
    assert callable(img.base.finalize_existing)
    assert callable(img.base.freeze_from_rows)
