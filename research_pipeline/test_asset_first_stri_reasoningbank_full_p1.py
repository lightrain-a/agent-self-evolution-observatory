"""Targeted guards for the frozen Full-P1 preregistration and runner."""

from __future__ import annotations

import pytest

from research_pipeline import asset_first_stri_reasoningbank_p1_core as core
from research_pipeline import asset_first_stri_reasoningbank_full_p1_runner as runner


def test_planned_units_are_exactly_once_and_frozen_order() -> None:
    units = runner.planned_units()
    assert len(units) == 40
    assert [row["ordinal"] for row in units] == list(range(1, 41))
    assert all(row["attempt_count"] == 1 for row in units)
    expected = [
        (rank, arm)
        for rank in [7, 8, 9, 11, 12, 13, 14, 19]
        for arm in ["A", "B", "C", "D", "E"]
    ]
    assert [(row["selection_rank"], row["arm"]) for row in units] == expected
    assert len({row["run_id"] for row in units}) == 40


def test_full_p1_adapter_binds_digest_and_q10_policy() -> None:
    value = "a" * 64
    adapter = runner.FullP1DockerRun(
        f"example.invalid/repo@sha256:{value}",
        "b" * 40,
        "targeted-test",
        True,
    )
    assert adapter.expected_image_digest == f"sha256:{value}"
    assert adapter.exact_base is True
    assert adapter.START_TIMEOUT_SECONDS == 600
    assert adapter.START_INSPECT_TIMEOUT_SECONDS == 180
    assert adapter.ACK_CONTRACT_SHA256 == (
        "bc4781ce0188d899af3b1a491b51f30467e6c655c7f8d3074b919a043b2878bd"
    )
    assert adapter.created is False
    runner._ACTIVE_CONTAINERS.pop("targeted-test", None)


def test_full_p1_adapter_rejects_unbound_image() -> None:
    with pytest.raises(RuntimeError, match="digest-bound"):
        runner.FullP1DockerRun("example.invalid/repo:latest", "b" * 40, "bad", True)


def test_core_runtime_monkeypatch_is_restored_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    original = core.DockerRun

    def fail(*args: object, **kwargs: object) -> object:
        assert core.DockerRun is runner.FullP1DockerRun
        raise RuntimeError("synthetic provider-free failure")

    monkeypatch.setattr(core, "execute_agent", fail)
    with pytest.raises(RuntimeError, match="synthetic"):
        runner.execute_with_q10(
            {
                "image_pull_reference": "example.invalid/repo@sha256:" + "a" * 64,
                "model_visible": {"base_commit": "b" * 40},
            },
            selected_memory="frozen",
            run_id="restore-test",
        )
    assert core.DockerRun is original
    runner._ACTIVE_CONTAINERS.pop("restore-test", None)


def test_runner_refuses_existing_index_before_any_execution(tmp_path) -> None:
    index = tmp_path / "index.json"
    index.write_text("{}\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="refusing duplicate"):
        runner.run(output_dir=tmp_path / "runs", index_path=index)
