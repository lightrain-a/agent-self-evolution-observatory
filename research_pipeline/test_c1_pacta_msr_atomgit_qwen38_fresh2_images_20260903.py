from __future__ import annotations

import inspect

from research_pipeline import prepare_c1_pacta_msr_atomgit_qwen38_fresh2_images_20260903 as m


def test_fresh2_image_binding_is_exact():
    m.bind()
    assert m.base.POOL == m.POOL
    rows = m.image_units()
    assert len(rows) == 20
    assert len({x["instance_id"] for x in rows}) == 20
    assert sum(x["role"] == "source" for x in rows) == 10
    assert sum(x["role"] == "future" for x in rows) == 10


def test_wrapper_reuses_verified_image_resolver_and_is_zero_provider():
    src = inspect.getsource(m)
    assert "base.resolve" in src
    assert "base.finalize_existing" in src
    assert "AA_API_KEY" not in src
    assert "chat/completions" not in src
    assert "atomcode" not in src.lower()


def test_pool_hash_is_frozen():
    assert m.EXPECTED_POOL_SHA == "1e52b3e00d7c8d82cf0846d66c87223c44bc137765cbd10e4ca139809134c3b1"
