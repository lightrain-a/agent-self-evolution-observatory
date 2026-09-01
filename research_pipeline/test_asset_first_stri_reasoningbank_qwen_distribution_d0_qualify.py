"""Zero-model guards for Qwen STRI D0 evaluator qualification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from research_pipeline import (
    asset_first_stri_reasoningbank_qwen_distribution_d0_qualify as qualify,
)
from research_pipeline import (
    asset_first_stri_reasoningbank_qwen_distribution_evaluator as evaluator,
)


def result(output: str = "", returncode: int = 0) -> dict[str, Any]:
    return {"output": output, "returncode": returncode, "timed_out": False}


def test_official_parser_family_mapping_is_complete() -> None:
    assert set(evaluator.PARSERS) == {
        "parse_log_astropy",
        "parse_log_django",
        "parse_log_matplotlib",
        "parse_log_seaborn",
        "parse_log_flask",
        "parse_log_requests",
        "parse_log_xarray",
        "parse_log_pylint",
        "parse_log_pytest",
        "parse_log_scikit",
        "parse_log_sphinx",
        "parse_log_sympy",
    }
    assert evaluator.SWEBENCH_WHEEL_SHA256 == (
        "b7f0416a1e686eca22c2f749b5f816685a202835032f6683080e2b53545bbb62"
    )


def test_pinned_parser_replay_and_grading() -> None:
    log = (
        ">>>>> Start Test Output\n"
        "PASSED tests/test_a.py::test_a\n"
        "SKIPPED [3] summary\n"
        "FAILED tests/test_b.py::test_b - assertion\n"
        ">>>>> End Test Output\n"
    )
    status = evaluator.parse_status_map("parse_log_xarray", log)
    assert status == {
        "tests/test_a.py::test_a": "PASSED",
        "tests/test_b.py::test_b": "FAILED",
    }
    grade = evaluator.grade_status_map(
        status,
        ["tests/test_a.py::test_a"],
        ["tests/test_b.py::test_b"],
    )
    assert grade["all_fail_to_pass"] is True
    assert grade["all_pass_to_pass"] is False
    assert grade["resolved"] is False


def test_specialized_official_parser_replays() -> None:
    assert evaluator.parse_status_map(
        "parse_log_astropy", "tests/test_a.py::test_a PASSED"
    ) == {"tests/test_a.py::test_a": "PASSED"}
    assert evaluator.parse_status_map(
        "parse_log_requests", "PASSED tests/test_a.py::test_a[/long/path/file.py]"
    ) == {"tests/test_a.py::test_a[/file.py]": "PASSED"}
    assert evaluator.parse_status_map(
        "parse_log_sympy", "test_issue_1 ok\ntest_issue_2 F"
    ) == {"test_issue_1": "PASSED", "test_issue_2": "FAILED"}
    assert evaluator.parse_status_map(
        "parse_log_matplotlib",
        "PASSED lib/test.py::test_button[MouseButton.LEFT]",
    ) == {"lib/test.py::test_button[1]": "PASSED"}


def test_candidate_schedule_is_frozen_and_provider_free() -> None:
    schedule = qualify.candidate_schedule()
    assert len(schedule) == 446
    assert [row["ordinal"] for row in schedule] == list(range(1, 447))
    assert all(row["qualification_attempt_count"] == 1 for row in schedule)
    assert schedule == sorted(
        schedule,
        key=lambda row: (
            row["repo_hash_rank"],
            row["task_hash_rank_within_repo"],
        ),
    )
    contract = qualify.contract_payload()
    assert contract["scientific_boundary"]["model_calls_authorized"] is False
    assert contract["scientific_boundary"]["provider_calls_authorized"] is False
    assert contract["credential_material_present"] is False


def test_repository_gate_stops_at_21_without_outcomes() -> None:
    schedule = [
        {
            "ordinal": index,
            "repo": "a/repo",
            "repo_hash_rank": 1,
            "instance_id": f"a__{index}",
        }
        for index in range(1, 23)
    ]
    completed = {
        index: {
            "ordinal": index,
            "repo": "a/repo",
            "instance_id": f"a__{index}",
            "qualified": True,
        }
        for index in range(1, 22)
    }
    state = qualify.repository_state(schedule, completed)
    assert state[0]["eligibility"] == "ELIGIBLE"
    assert state[0]["qualified_count"] == 21
    assert qualify.next_unit(schedule, completed) is None


def test_qualification_receipt_requires_cleanup_and_hides_gold(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    class FakeContainer:
        name = "fake"

        def __init__(self, image: str, base_commit: str, run_id: str) -> None:
            self.base_commit = base_commit

        def start(self) -> dict[str, Any]:
            return {
                "base_commit_receipt": {
                    "observed_head": self.base_commit,
                }
            }

        def exec(self, action: str, timeout: int = 0) -> dict[str, Any]:
            if action == "EVAL":
                return result(
                    ">>>>> Start Test Output\n"
                    "PASSED tests/test_demo.py::test_demo\n"
                    ">>>>> End Test Output\n"
                )
            if "git -c core.fileMode=false diff" in action:
                return result("gold-state\n__STATUS__\n M demo.py\n")
            return result()

        def close(self) -> dict[str, Any]:
            return {"accepted": True}

    monkeypatch.setattr(qualify, "QualificationDockerRun", FakeContainer)
    monkeypatch.setattr(qualify, "_docker_copy", lambda *args, **kwargs: result())
    monkeypatch.setattr(qualify, "RAW_LOG_DIR", tmp_path / "raw")
    patch = "diff --git a/demo.py b/demo.py\n"
    unit = {
        "ordinal": 1,
        "repo": "demo/repo",
        "repo_hash_rank": 1,
        "task_hash_rank_within_repo": 1,
        "instance_id": "demo__repo-1",
        "model_visible_task_sha256": "a" * 64,
        "gold_patch_sha256": qualify.sha256_text(patch),
    }
    row = {
        "instance_id": unit["instance_id"],
        "base_commit": "b" * 40,
        "patch": patch,
        "test_patch": "diff --git a/test.py b/test.py\n",
        "eval_script": "EVAL",
        "log_parser": "parse_log_xarray",
        "FAIL_TO_PASS": ["tests/test_demo.py::test_demo"],
        "PASS_TO_PASS": [],
        "image": "example/image:latest",
        "eval_type": "pytest",
    }
    receipt = qualify.qualify_task(
        unit,
        row,
        {"manifest_digest": "sha256:" + "c" * 64},
        {
            "image_pull_reference": "example/image@sha256:" + "c" * 64,
            "exact_digest_visible": True,
            "architecture_amd64_visible": True,
        },
    )
    assert receipt["qualified"] is True
    assert receipt["checks"]["container_cleanup_accepted"] is True
    assert receipt["task_receipt"]["gold_patch_content_persisted_in_receipt"] is False
    assert "patch" not in receipt
    assert receipt["model_calls"] == 0
    assert receipt["provider_calls"] == 0
