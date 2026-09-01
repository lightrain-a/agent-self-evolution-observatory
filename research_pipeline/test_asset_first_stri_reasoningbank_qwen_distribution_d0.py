"""Guards for the prospective Qwen behavioral-distribution D0 freeze."""

from __future__ import annotations

import json

import pytest

from research_pipeline import (
    asset_first_stri_reasoningbank_qwen_distribution_d0 as d0,
)


def test_d0_payload_freezes_exact_dataset_and_exclusions() -> None:
    payload = d0.build_payload(starting_sha=d0.STARTING_CANONICAL_SHA)
    assert payload["dataset"]["parquet_sha256"] == d0.DATASET_SHA256
    assert payload["dataset"]["row_count"] == 500
    assert payload["historical_exclusion_count"] == 15
    assert payload["fresh_task_count"] == 485
    assert len(payload["candidate_pool"]) == 485
    assert payload["checks"]["model_calls_zero"] is True
    assert payload["checks"]["task_outcomes_unobserved"] is True
    assert payload["credential_material_present"] is False


def test_d0_repository_and_task_order_is_hash_deterministic() -> None:
    payload = d0.build_payload(starting_sha=d0.STARTING_CANONICAL_SHA)
    repos = payload["repository_summaries"]
    assert repos == sorted(repos, key=lambda row: (row["repo_name_sha256"], row["repo"]))
    assert payload["raw_capacity_repository_order"] == [
        "astropy/astropy",
        "pydata/xarray",
        "sympy/sympy",
        "matplotlib/matplotlib",
        "django/django",
        "scikit-learn/scikit-learn",
        "sphinx-doc/sphinx",
    ]
    for repo in {row["repo"] for row in payload["candidate_pool"]}:
        rows = [row for row in payload["candidate_pool"] if row["repo"] == repo]
        assert [row["task_hash_rank_within_repo"] for row in rows] == list(
            range(1, len(rows) + 1)
        )
        assert rows == sorted(
            rows, key=lambda row: (row["instance_id_sha256"], row["instance_id"])
        )


def test_d0_candidate_fixture_never_persists_patch_content() -> None:
    payload = d0.build_payload(starting_sha=d0.STARTING_CANONICAL_SHA)
    forbidden_keys = {"patch", "test_patch", "gold_patch"}
    historical = set(d0.HISTORICAL_EXPOSURE_RECEIPTS)
    for row in payload["candidate_pool"]:
        assert forbidden_keys.isdisjoint(row)
        assert row["gold_patch_content_persisted"] is False
        assert row["test_patch_content_persisted"] is False
        assert row["instance_id"] not in historical
        assert row["model_calls_made"] == 0
        assert row["task_outcome_observed"] is False
    serialized = json.dumps(payload, sort_keys=True)
    assert "Authorization" not in serialized
    assert "api_key" not in serialized.lower()


def test_d0_refuses_overwrite(tmp_path) -> None:
    output = tmp_path / "d0.json"
    output.write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="refusing to overwrite"):
        d0.freeze(output)
