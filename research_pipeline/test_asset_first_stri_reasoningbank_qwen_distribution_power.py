from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_power import (
    percentile, precision_simulation,
)


def atom(*names):
    return {(name, "f") for name in names}


def test_percentile_linear_interpolation():
    assert percentile([0, 1, 2], .5) == 1


def test_precision_uses_only_four_A_pools_and_is_deterministic():
    pilot = {
        f"task-{i}": [atom("a"), atom("a", "b"), atom("b"), atom()]
        for i in range(4)
    }
    first = precision_simulation(pilot, seed=7, replicates=100)
    second = precision_simulation(pilot, seed=7, replicates=100)
    assert first == second
    assert first["pilot_A_D_effect_used"] is False
    assert first["design"] == {
        "N_tasks": 24, "K_per_arm": 6,
        "primary_analysis": "task-blocked cross-minus-within T",
    }
    assert set(first["power_by_synthetic_T"]) == {"0.05", "0.10", "0.15", "0.20", "0.25"}
    assert first["changes_N_or_K"] is False
