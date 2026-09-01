from __future__ import annotations

import math

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_analysis import (
    bootstrap_ci, fisher_exact_two_sided, high_relevance_set, missingness_gate,
    paired_task_sign_flip, permutation_test, seed_from_contract, task_statistic, task_statistics,
)


def atom(*names):
    return {(name, "f") for name in names}


def test_task_statistic_zero_for_identical_point_masses():
    values = [atom("x")] * 4
    assert task_statistic(values, values) == 0


def test_task_statistic_positive_for_separated_point_masses():
    left, right = [atom("x")] * 4, [atom("y")] * 4
    assert task_statistic(left, right) == 2


def test_task_statistics_uses_all_valid_and_minimum_four():
    blocks = {
        "keep": {"A": [atom("x")] * 5, "D": [atom("y")] * 4},
        "drop": {"A": [atom("x")] * 3, "D": [atom("y")] * 6},
    }
    assert task_statistics(blocks, "A", "D") == {"keep": 2}


def test_permutation_is_deterministic_and_task_blocked():
    blocks = {
        "t1": {"A": [atom("x")] * 4, "D": [atom("y")] * 4},
        "t2": {"A": [atom("m")] * 4, "D": [atom("n")] * 4},
    }
    first = permutation_test(blocks, replicates=200, seed=7)
    second = permutation_test(blocks, replicates=200, seed=7)
    assert first == second
    assert first["analyzable_task_count"] == 2
    assert first["observed_global_T"] == 2
    assert first["task_blocked"] is True


def test_bootstrap_resamples_tasks():
    result = bootstrap_ci({"a": 0.0, "b": 1.0, "c": 2.0}, replicates=500, seed=9)
    assert result["resampling_unit"] == "task"
    assert result["estimate"] == 1
    assert result["lower"] <= 1 <= result["upper"]


def test_fisher_and_missingness_gate():
    assert fisher_exact_two_sided(6, 0, 6, 0) == 1
    passed = missingness_gate(planned_a=144, valid_a=140, planned_d=144, valid_d=139)
    assert passed["decision"] == "MISSINGNESS_GATE_PASS"
    held = missingness_gate(planned_a=144, valid_a=144, planned_d=144, valid_d=100)
    assert held["decision"] == "MISSINGNESS_ARM_IMBALANCED"
    assert held["absolute_failure_rate_difference"] > .10
    assert held["fisher_exact_two_sided_p"] < .05


def test_paired_task_sign_flip_is_task_blocked_and_deterministic():
    first = paired_task_sign_flip({"a": .5, "b": .25}, replicates=200, seed=11)
    second = paired_task_sign_flip({"a": .5, "b": .25}, replicates=200, seed=11)
    assert first == second
    assert first["task_count"] == 2
    assert first["observed_mean_task_difference"] == .375
    assert first["paired"] is True


def test_seed_and_relevance_order_are_deterministic():
    assert seed_from_contract("e", "a" * 64, "permutation") == seed_from_contract(
        "e", "a" * 64, "permutation")
    rows = [
        {"instance_id": "b", "top1_relevance": .8, "task_sha256": "2"},
        {"instance_id": "a", "top1_relevance": .8, "task_sha256": "1"},
        {"instance_id": "c", "top1_relevance": .7, "task_sha256": "0"},
    ]
    assert high_relevance_set(rows, 2) == ["a", "b"]
