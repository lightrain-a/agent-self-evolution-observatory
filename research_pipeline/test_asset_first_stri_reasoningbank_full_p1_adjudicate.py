"""Outcome-blind tests for Full-P1 paired adjudication helpers."""

from __future__ import annotations

from research_pipeline.asset_first_stri_reasoningbank_full_p1_adjudicate import (
    exact_r4,
    holm,
    interval,
    r2_signature,
    r3_signature,
)


def test_clopper_pearson_bounds_cover_boundary_counts() -> None:
    assert interval(0, 8)[0] == 0.0
    assert interval(8, 8)[1] == 1.0
    middle = interval(4, 8)
    assert 0.0 < middle[0] < 0.5 < middle[1] < 1.0


def test_exact_r4_uses_discordant_pairs() -> None:
    row = exact_r4(
        [True, True, False, False],
        [True, False, True, False],
    )
    assert row["a_only"] == 1
    assert row["b_only"] == 1
    assert row["discordant_pairs"] == 2
    assert row["paired_rate_difference"] == 0.0
    assert row["exact_mcnemar_two_sided_pvalue"] == 1.0


def test_holm_primary_adjustment_is_monotone() -> None:
    adjusted = holm({"A_vs_B": 0.01, "A_vs_D": 0.04})
    assert adjusted["A_vs_B"] == 0.02
    assert adjusted["A_vs_D"] == 0.04


def test_behavior_signatures_ignore_wall_clock_metadata() -> None:
    first = {
        "step": 1,
        "type": "shell",
        "action": "rg target",
        "returncode": 0,
        "timed_out": False,
        "started_at_utc": "one",
        "finished_at_utc": "two",
    }
    second = dict(first, started_at_utc="three", finished_at_utc="four")
    assert r2_signature({"R2_first_behavior_action": first}) == r2_signature(
        {"R2_first_behavior_action": second}
    )
    a = {
        "R3_actions": [first],
        "patch_and_status": {"output": "diff"},
        "exit_status": "Submitted",
    }
    b = {
        "R3_actions": [second],
        "patch_and_status": {"output": "diff"},
        "exit_status": "Submitted",
    }
    assert r3_signature(a) == r3_signature(b)
