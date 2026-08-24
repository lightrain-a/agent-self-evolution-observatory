from __future__ import annotations

import numpy as np

from .asset_first_stri_support_edit_radius_20260824 import support_edit_radius
from .asset_first_stri_target_null_analysis_20260824 import degree_preserving_switch_null, tool_frequency_target


def test_tool_frequency_target_is_positive_mean_one_and_representation_free() -> None:
    rows = [
        {"tool": "a", "accepted_skill_ids": ["x"]},
        {"tool": "a", "accepted_skill_ids": ["y"]},
        {"tool": "b", "accepted_skill_ids": ["x", "y"]},
    ]
    q = tool_frequency_target(rows, -1.0)
    assert np.all(q > 0)
    assert np.isclose(float(q.mean()), 1.0)
    assert q[0] == q[1]
    assert q[2] > q[0]


def test_degree_preserving_switch_null_preserves_both_margins() -> None:
    A = np.asarray(
        [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 0, 1],
        ],
        dtype=float,
    )
    B, successes, attempts = degree_preserving_switch_null(A, seed=7, successful_switches=20)
    assert successes == 20
    assert attempts >= successes
    assert np.array_equal(A.sum(axis=0), B.sum(axis=0))
    assert np.array_equal(A.sum(axis=1), B.sum(axis=1))
    assert np.all((B == 0.0) | (B == 1.0))


def test_exact_support_edit_radius_on_factor2_witness() -> None:
    A = np.asarray(
        [
            [1, 0],
            [0, 1],
            [1, 1],
        ],
        dtype=float,
    )
    result = support_edit_radius(A)
    assert np.isclose(result["observed_R_star"], 2.0)
    assert result["minimum_additions_to_equalizable"] == 1
    assert result["minimum_deletions_to_equalizable"] == 1
    assert np.isclose(result["addition_solution"]["verified_R_star"], 1.0)
    assert np.isclose(result["deletion_solution"]["verified_R_star"], 1.0)
    assert result["addition_solution"]["mip_gap"] == 0.0
    assert result["deletion_solution"]["mip_gap"] == 0.0
