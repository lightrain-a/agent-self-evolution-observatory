from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh3_runtime_20260903 as fresh3_runtime
from research_pipeline import run_c1_pacta_msr_atomgit_qwen38_fresh4_runtime_20260903 as fresh4
from research_pipeline.c1_pacta_rb_qwen397 import sha256_file


def test_fresh4_runtime_binds_frozen_inputs() -> None:
    assert fresh4.POOL_SHA == "9582877385413807dea6316c25585d5714662cce17f83fa298934229dc4f0927"
    assert fresh4.MANIFEST_SHA == "8b84467e67bc4c514a921f53515b50741a7427051941671084e2263e5f95d91f"
    assert fresh4.BLOB_PLAN_SHA == "5e7bddd3772f43c2e9bd3dd8895c3bb7039fe90952934aaa42db7286eda76478"
    assert fresh4.UNIQUE_BLOB_COUNT == 86
    assert sha256_file(fresh4.IMAGE_ROOT / "manifest-freeze.json") == fresh4.MANIFEST_SHA
    assert sha256_file(fresh4.IMAGE_ROOT / "blob-plan.json") == fresh4.BLOB_PLAN_SHA


def test_fresh4_manifest_geometry_is_twenty_stable_images() -> None:
    freeze = json.loads((fresh4.IMAGE_ROOT / "manifest-freeze.json").read_text())
    plan = json.loads((fresh4.IMAGE_ROOT / "blob-plan.json").read_text())
    assert freeze["fresh_pool_sha256"] == fresh4.POOL_SHA
    assert freeze["image_count"] == 20
    assert freeze["stable_twice"] is True
    assert len(freeze["rows"]) == 20
    assert len({row["instance_id"] for row in freeze["rows"]}) == 20
    assert plan["unique_blob_count"] == 86


def test_blob_receipt_sha_is_mandatory_and_validated() -> None:
    with pytest.raises(RuntimeError, match="SHA_FORMAT"):
        fresh4.bind("not-a-sha")


def test_fresh4_reuses_targeted_build_clean_qualifier_unchanged() -> None:
    source = inspect.getsource(fresh3_runtime.qualify_one)
    assert 'git clean -fd -- build' in source
    assert 'git clean -fdx' not in source
    assert 'initial_tracked_tree_clean' in source
    assert 'initial_untracked_only_build' in source
    assert 'post_reset_working_tree_clean' in source


def test_runtime_runner_has_no_model_or_source_execution_surface() -> None:
    source = inspect.getsource(fresh4)
    assert "atomcode" not in source.lower()
    assert "execute_trajectory(" not in source
    assert "def acquire(" not in source
    assert "writer_phase(" not in source
    assert "shadow_phase(" not in source


def test_runtime_stays_zero_provider_and_future_execution() -> None:
    source = inspect.getsource(fresh4)
    assert '"provider_calls": 0' in source
    assert '"scientific_source_tasks_used": 0' in source
    assert '"future_task_executions": 0' in source
