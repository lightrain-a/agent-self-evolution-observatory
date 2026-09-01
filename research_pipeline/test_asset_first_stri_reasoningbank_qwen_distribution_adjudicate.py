import pytest

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_adjudicate import (
    average_ranks, behavior_blocks, equality_fraction, r4_proportions,
    spearman, valid_counts,
)


def signature(name):
    return {
        "atoms": [{"relative_path": f"{name}.py", "qualified_symbol": "f"}],
        "signature_sha256": name,
    }


def receipt(task, arm, valid=True, resolved=False):
    return {
        "instance_id": task, "arm": arm, "behavior_valid": valid,
        "behavior_observables": {
            "edit_target_set": signature(f"{task}-{arm}"),
        },
        "R4_terminal_outcome": {"valid": True, "resolved": resolved},
    }


def test_behavior_blocks_and_valid_counts_exclude_invalid_trials():
    rows = [receipt("t", "A"), receipt("t", "A", False), receipt("t", "D")]
    blocks = behavior_blocks(rows)
    assert len(blocks["t"]["A"]) == 1
    assert valid_counts(rows)["t"] == {"A": 1, "D": 1, "N": 0}


def test_r4_proportions_require_behavior_and_evaluator_validity():
    rows = [
        receipt("t", "A", True, True),
        receipt("t", "A", True, False),
        receipt("t", "A", False, True),
        receipt("t", "D", True, False),
    ]
    result = r4_proportions(rows)
    assert result["t"]["A"]["valid_trials"] == 2
    assert result["t"]["A"]["resolution_proportion"] == .5
    assert result["t"]["D"]["resolution_proportion"] == 0


def test_ranks_spearman_and_equality_are_deterministic():
    assert average_ranks([1, 1, 3]) == [1.5, 1.5, 3]
    assert spearman([(1, 2), (2, 4), (3, 6)]) == pytest.approx(1)
    assert equality_fraction(["x", "x", "y"]) == {
        "pair_count": 3, "equal_count": 1, "equal_fraction": pytest.approx(1 / 3)}
