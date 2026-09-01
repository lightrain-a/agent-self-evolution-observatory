from __future__ import annotations

import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_split import (
    split_for_repo,
)


def test_primary_repo_split_counts_and_order():
    ids = [f"task-{index:02d}" for index in range(21)]
    split = split_for_repo("org/repo", ids)
    assert split["source_task_ids"] == ids[:8]
    assert split["calibration_task_ids"] == ids[8:10]
    assert split["structural_candidate_task_ids"] == ids[10:]
    assert split["counts"] == {
        "qualified": 21, "source": 8, "calibration": 2, "structural_candidates": 11,
    }


def test_repo_split_requires_headroom():
    with pytest.raises(RuntimeError, match="insufficient"):
        split_for_repo("org/repo", [str(i) for i in range(20)])


def test_repo_split_is_deterministic():
    ids = [f"task-{index:02d}" for index in range(25)]
    assert split_for_repo("r", ids) == split_for_repo("r", ids)
