from collections import Counter

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_schedule import (
    build_schedule,
)


def test_confirmatory_schedule_has_exact_task_arm_round_counts_and_tercile_balance():
    tasks = [f"task-{i:02d}" for i in range(24)]
    result = build_schedule(tasks, experiment_id="experiment", frozen_manifest_sha256="a" * 64)
    units = result["units"]
    assert len(units) == 432
    assert Counter((row["instance_id"], row["arm"]) for row in units) == Counter(
        {(task, arm): 6 for task in tasks for arm in ("A", "D", "N")})
    for trial_round in range(1, 7):
        rows = [row for row in units if row["round"] == trial_round]
        for third in range(3):
            segment = rows[third * 24:(third + 1) * 24]
            assert Counter(row["arm"] for row in segment) == Counter({"A": 8, "D": 8, "N": 8})
