from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_source import (
    source_plan,
)


def test_source_plan_preserves_frozen_repository_then_task_order():
    ids = [f"task-{i:02d}" for i in range(32)]
    split = {
        "source_task_ids": ids,
        "task_receipts": {
            task: {"task_sha256": str(i) * 64,
                   "qualification_receipt": f"generated/{task}.json",
                   "qualification_receipt_sha256": "a" * 64}
            for i, task in enumerate(ids)
        },
    }
    plan = source_plan(split)
    assert [row["instance_id"] for row in plan] == ids
    assert [row["ordinal"] for row in plan] == list(range(1, 33))
    assert {row["attempt_count"] for row in plan} == {1}
    assert not any(row["automatic_retry"] or row["replacement"] for row in plan)
