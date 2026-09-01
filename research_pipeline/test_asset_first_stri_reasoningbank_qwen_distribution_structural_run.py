import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_structural_run import (
    allocate, allocation_rule,
)


def primary_split():
    return {
        "dataset_design": "PRIMARY_4_REPOSITORY",
        "repo_splits": [
            {"repo": f"r{i}", "structural_candidate_task_ids": [
                f"r{i}-t{j}" for j in range(11)]}
            for i in range(4)
        ],
    }


def test_primary_allocation_uses_first_structurally_qualified_only():
    split = primary_split()
    qualified = {task: not task.endswith("t1")
                 for row in split["repo_splits"]
                 for task in row["structural_candidate_task_ids"]}
    pilots, main = allocate(split, qualified)
    assert pilots == ["r0-t0", "r1-t0", "r2-t0", "r3-t0"]
    assert len(main) == 24
    assert "r0-t1" not in main


def test_fallback_allocation_has_four_pilot_and_twenty_four_main():
    split = {
        "dataset_design": "FALLBACK_3_REPOSITORY",
        "repo_splits": [
            {"repo": f"r{i}", "structural_candidate_task_ids": [
                f"r{i}-t{j}" for j in range(10 if i < 2 else 11)]}
            for i in range(3)
        ],
    }
    qualified = {task: True for row in split["repo_splits"]
                 for task in row["structural_candidate_task_ids"]}
    pilots, main = allocate(split, qualified)
    assert pilots == ["r0-t0", "r0-t1", "r1-t0", "r2-t0"]
    assert len(main) == 24
    assert allocation_rule("FALLBACK_3_REPOSITORY")["required_structural_per_repo"] == [10, 9, 9]


def test_allocation_holds_instead_of_replacing_when_capacity_insufficient():
    split = primary_split()
    qualified = {task: True for row in split["repo_splits"]
                 for task in row["structural_candidate_task_ids"]}
    qualified["r2-t6"] = False
    for j in range(7, 11):
        qualified[f"r2-t{j}"] = False
    with pytest.raises(RuntimeError, match="insufficient"):
        allocate(split, qualified)
