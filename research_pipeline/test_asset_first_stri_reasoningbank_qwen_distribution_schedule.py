from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_schedule import (
    build_schedule, schedule_seed,
)


def test_schedule_exact_counts_order_and_balance():
    tasks = [f"task-{i:02d}" for i in range(24)]
    first = build_schedule(tasks, experiment_id="e", frozen_manifest_sha256="a" * 64)
    second = build_schedule(tasks, experiment_id="e", frozen_manifest_sha256="a" * 64)
    assert first == second
    assert first["unit_count"] == 432
    assert [row["ordinal"] for row in first["units"]] == list(range(1, 433))
    assert {row["attempt_count"] for row in first["units"]} == {1}
    assert not any(row["automatic_retry"] or row["replacement"] for row in first["units"])
    assert len(first["schedule_sha256"]) == 64


def test_seed_binds_manifest_and_experiment():
    base = schedule_seed("e", "a" * 64)
    assert base != schedule_seed("f", "a" * 64)
    assert base != schedule_seed("e", "b" * 64)


def test_schedule_rejects_wrong_or_duplicate_population():
    try:
        build_schedule(["x"] * 24, experiment_id="e", frozen_manifest_sha256="a" * 64)
    except ValueError as error:
        assert "24 unique" in str(error)
    else:
        raise AssertionError("expected rejection")
