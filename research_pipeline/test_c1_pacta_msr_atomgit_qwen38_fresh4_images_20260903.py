from __future__ import annotations

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh4_images_20260903 as img


def test_fresh4_image_binding_audit_is_zero_provider_twenty_images():
    result = img.audit()
    assert result["status"] == "FRESH4_IMAGE_RESOLVER_BINDING_PASS"
    assert result["image_count"] == 20
    assert result["source_count"] == 10
    assert result["future_count"] == 10
    assert result["provider_calls"] == 0
    assert result["scientific_source_calls"] == 0


def test_fresh4_image_pool_sha_is_frozen():
    assert img.POOL_SHA == "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"


def test_fresh4_image_root_is_new_and_disjoint():
    assert "fresh4-images-20260903-v1" in str(img.DEFAULT)
    assert "fresh3" not in str(img.DEFAULT)


def test_fresh4_image_units_are_unique():
    img.bind()
    rows = img.base.image_units()
    assert len(rows) == 20
    assert len({row["instance_id"] for row in rows}) == 20
