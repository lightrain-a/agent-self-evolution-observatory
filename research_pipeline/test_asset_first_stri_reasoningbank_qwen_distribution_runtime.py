from __future__ import annotations

import json
from pathlib import Path

import pytest

from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_runtime as rt
from research_pipeline import asset_first_stri_reasoningbank_qwen_distribution_runtime_eval as evrt


def fake_split(repo_count: int = 4) -> dict:
    repos = [f"org/repo{i}" for i in range(repo_count)]
    rows = []
    receipts = {}
    all_source = []
    all_calibration = []
    all_candidates = []
    for r, repo in enumerate(repos, start=1):
        ids = [f"repo{r}__task-{j:02d}" for j in range(1, 22)]
        source = ids[:8]
        calibration = ids[8:10]
        candidates = ids[10:]
        rows.append({
            "repo": repo,
            "qualified_order": ids,
            "source_task_ids": source,
            "calibration_task_ids": calibration,
            "structural_candidate_task_ids": candidates,
        })
        all_source.extend(source)
        all_calibration.extend(calibration)
        all_candidates.extend(candidates)
        for task_id in ids:
            receipts[task_id] = {
                "qualification_receipt": f"generated/{task_id}.json",
                "qualification_receipt_sha256": "a" * 64,
                "task_sha256": "b" * 64,
                "base_commit": "c" * 40,
                "image_manifest_digest": "sha256:" + "d" * 64,
            }
    # The real 3-repo fallback moves one candidate from each of the first two repos
    # into calibration, keeping total calibration at eight.  Reproduce only the
    # aggregate counts needed by the runtime-plan tests here.
    if repo_count == 3:
        extras = [rows[0]["structural_candidate_task_ids"].pop(0),
                  rows[1]["structural_candidate_task_ids"].pop(0)]
        rows[0]["calibration_task_ids"].append(extras[0])
        rows[1]["calibration_task_ids"].append(extras[1])
        all_calibration.extend(extras)
        all_candidates = [x for row in rows for x in row["structural_candidate_task_ids"]]
    return {
        "repositories": repos,
        "repo_splits": rows,
        "task_receipts": receipts,
        "source_task_ids": all_source,
        "calibration_task_ids": all_calibration,
        "structural_candidate_task_ids": all_candidates,
    }


def test_source_runtime_plan_primary_and_fallback_counts_are_frozen() -> None:
    primary = rt.source_runtime_plan(fake_split(4))
    fallback = rt.source_runtime_plan(fake_split(3))
    assert len(primary) == 32
    assert len(fallback) == 24
    assert [row["ordinal"] for row in primary] == list(range(1, 33))
    assert len({row["instance_id"] for row in primary}) == 32
    assert all(row["attempt_count"] == 1 for row in primary)


def test_runtime_plan_rejects_duplicate_tasks() -> None:
    split = fake_split(3)
    duplicate = split["source_task_ids"][0]
    task_ids = [duplicate, duplicate]
    with pytest.raises(RuntimeError, match="duplicate"):
        rt.build_runtime_plan(split, task_ids, prefix="TEST")


def test_evaluation_runtime_plan_is_exactly_36_selected_tasks() -> None:
    split = fake_split(4)
    structural = {
        "pilot_task_ids": [row["structural_candidate_task_ids"][0] for row in split["repo_splits"]],
        "confirmatory_task_ids": [
            task
            for row in split["repo_splits"]
            for task in row["structural_candidate_task_ids"][1:7]
        ],
    }
    plan = evrt.evaluation_runtime_plan(split, structural)
    assert len(plan) == 36
    assert len({row["instance_id"] for row in plan}) == 36
    assert [row["instance_id"] for row in plan[:8]] == split["calibration_task_ids"]
    assert [row["instance_id"] for row in plan[8:12]] == structural["pilot_task_ids"]
    assert [row["instance_id"] for row in plan[12:]] == structural["confirmatory_task_ids"]


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
        "runtime_id": "QWEN-SOURCE-RUNTIME-001",
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
            assert "QWEN_RUNTIME_OK" in action
            return {"returncode": 0, "timed_out": False,
                    "output": "QWEN_RUNTIME_OK\n"}

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


def test_require_source_qualified_fails_closed_without_result(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(rt, "SOURCE_RESULT", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="result absent"):
        rt.require_source_qualified()


def test_require_evaluation_qualified_fails_closed_without_result(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(evrt, "RESULT", tmp_path / "missing.json")
    with pytest.raises(RuntimeError, match="result absent"):
        evrt.require_qualified()
