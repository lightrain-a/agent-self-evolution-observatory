from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_runtime as rt


def fake_split(repo_count: int = 4) -> dict:
    repos = [f"org/repo{i}" for i in range(repo_count)]
    rows = []
    receipts = {}
    for r, repo in enumerate(repos, start=1):
        ids = [f"repo{r}__task-{j:02d}" for j in range(1, 22)]
        rows.append({"repo": repo, "qualified_order": ids})
        for task_id in ids:
            receipts[task_id] = {
                "qualification_receipt": f"generated/{task_id}.json",
                "qualification_receipt_sha256": "a" * 64,
                "task_sha256": "b" * 64,
                "base_commit": "c" * 40,
                "image_manifest_digest": "sha256:" + "d" * 64,
            }
    return {"repositories": repos, "repo_splits": rows, "task_receipts": receipts}


def test_runtime_plan_primary_and_fallback_counts_are_frozen() -> None:
    primary = rt.runtime_plan(fake_split(4))
    fallback = rt.runtime_plan(fake_split(3))
    assert len(primary) == 84
    assert len(fallback) == 63
    assert [row["ordinal"] for row in primary] == list(range(1, 85))
    assert len({row["instance_id"] for row in primary}) == 84
    assert all(row["attempt_count"] == 1 for row in primary)


def test_runtime_plan_rejects_duplicate_tasks() -> None:
    split = fake_split(3)
    split["repo_splits"][1]["qualified_order"][0] = split["repo_splits"][0]["qualified_order"][0]
    with pytest.raises(RuntimeError, match="duplicate"):
        rt.runtime_plan(split)


def test_qualify_unit_is_zero_model_zero_evaluator_and_exact(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rt, "ROOT", tmp_path)
    rel = Path("generated/q.json")
    qpath = tmp_path / rel
    qpath.parent.mkdir(parents=True)
    q = {
        "qualified": True,
        "qualification_attempt_count": 1,
        "task_receipt": {
            "model_visible_task_sha256": "b" * 64,
            "base_commit": "c" * 40,
            "image_manifest": {
                "manifest_digest": "sha256:" + "d" * 64,
                "manifest_path": "generated/manifest.json",
            },
        },
    }
    qpath.write_text(json.dumps(q), encoding="utf-8")
    qsha = rt.sha256_file(qpath)
    unit = {
        "ordinal": 1,
        "runtime_id": "QWEN-RUNTIME-001",
        "instance_id": "repo1__task-01",
        "repo": "org/repo1",
        "qualification_receipt": str(rel),
        "qualification_receipt_sha256": qsha,
        "task_sha256": "b" * 64,
        "base_commit": "c" * 40,
        "image_manifest_digest": "sha256:" + "d" * 64,
        "attempt_count": 1,
    }
    monkeypatch.setattr(rt, "candidate_schedule", lambda: [{
        "instance_id": unit["instance_id"], "ordinal": 1,
    }])
    monkeypatch.setattr(rt, "acquire_and_import", lambda schedule_unit, meta: {
        "image_pull_reference": "mirror/repo@sha256:" + "d" * 64,
        "exact_digest_visible": True,
        "architecture_amd64_visible": True,
    })

    class FakeContainer:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def start(self):
            return {"base_commit_receipt": {"observed_head": "c" * 40}}

        def exec(self, action: str, timeout: int = 0):
            assert "QWEN_BEHAVIORAL_RUNTIME_OK" in action
            return {"returncode": 0, "timed_out": False,
                    "output": "QWEN_BEHAVIORAL_RUNTIME_OK\n"}

        def close(self):
            return {"accepted": True}

    monkeypatch.setattr(rt, "QualificationDockerRun", FakeContainer)
    receipt = rt.qualify_unit(unit)
    assert receipt["qualified"] is True
    assert receipt["docker_host"] == "unix:///var/run/docker.sock"
    assert receipt["model_calls"] == 0
    assert receipt["provider_calls"] == 0
    assert receipt["evaluator_calls"] == 0
    assert receipt["behavioral_outcomes_observed"] is False
    assert receipt["checks"]["gold_patch_not_applied"] is True
    assert receipt["checks"]["test_patch_not_applied"] is True
    assert receipt["checks"]["evaluator_not_run"] is True
    assert receipt["checks"]["behavioral_outcomes_not_observed"] is True


def test_require_qualified_fails_closed_without_result(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rt, "RESULT", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="result absent"):
        rt.require_qualified()
