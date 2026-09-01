from collections import Counter

from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_pilot import (
    pilot_plan,
)


def test_pilot_schedule_48_exact_balanced_deterministic():
    tasks = [f"task-{i}" for i in range(4)]
    structural = {"structural_receipts": {
        task: {"complete_R1_sha256": {arm: (task + arm).ljust(64, "x")
                                     for arm in ("A", "D", "N")}}
        for task in tasks}}
    split = {"task_receipts": {
        task: {"qualification_receipt": f"generated/{task}.json",
               "qualification_receipt_sha256": "a" * 64}
        for task in tasks}}
    seed, first = pilot_plan(
        tasks, manifest_sha256="b" * 64, structural=structural, split=split)
    assert (seed, first) == pilot_plan(
        tasks, manifest_sha256="b" * 64, structural=structural, split=split)
    assert len(first) == 48
    assert Counter((row["instance_id"], row["arm"]) for row in first) == Counter(
        {(task, arm): 4 for task in tasks for arm in ("A", "D", "N")})
    assert {row["attempt_count"] for row in first} == {1}
