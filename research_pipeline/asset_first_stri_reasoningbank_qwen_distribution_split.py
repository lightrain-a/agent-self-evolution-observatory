"""Freeze outcome-blind source/calibration/structural-candidate splits after D0/Q1."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
D0_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-index-20260901.json"
Q1_RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-q1-result-20260901.json"
RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-receipts-20260901"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
SOURCE_PER_REPO = 8
CALIBRATION_PER_REPO = 2
MIN_STRUCTURAL_CANDIDATES_PER_REPO = 11


def load_gates() -> tuple[dict[str, Any], dict[str, Any]]:
    d0 = json.loads(D0_INDEX.read_text(encoding="utf-8"))
    q1 = json.loads(Q1_RESULT.read_text(encoding="utf-8"))
    if not d0.get("execution_complete"):
        raise RuntimeError("D0 is not terminal")
    if d0["decision"] not in {
        "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
        "D0_FALLBACK_THREE_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
    }:
        raise RuntimeError("D0 feasibility did not pass")
    if q1.get("backend_classification") not in {"DETERMINISTIC", "STOCHASTIC"}:
        raise RuntimeError("Q1 did not open source freeze")
    return d0, q1


def split_for_repo(repo: str, task_ids: list[str]) -> dict[str, Any]:
    required = SOURCE_PER_REPO + CALIBRATION_PER_REPO + MIN_STRUCTURAL_CANDIDATES_PER_REPO
    if len(task_ids) < required:
        raise RuntimeError(f"insufficient qualified capacity for {repo}")
    source = task_ids[:SOURCE_PER_REPO]
    calibration = task_ids[SOURCE_PER_REPO:SOURCE_PER_REPO + CALIBRATION_PER_REPO]
    candidates = task_ids[SOURCE_PER_REPO + CALIBRATION_PER_REPO:]
    groups = [source, calibration, candidates]
    if len(set().union(*map(set, groups))) != sum(map(len, groups)):
        raise RuntimeError("within-repository split overlap")
    return {
        "repo": repo,
        "qualified_order": task_ids,
        "source_task_ids": source,
        "calibration_task_ids": calibration,
        "structural_candidate_task_ids": candidates,
        "counts": {
            "qualified": len(task_ids), "source": len(source),
            "calibration": len(calibration), "structural_candidates": len(candidates),
        },
        "ordering_rule": "frozen D0 SHA256(instance_id) order",
    }



def apply_fallback_calibration(repo_splits: list[dict[str, Any]]) -> list[str]:
    if len(repo_splits) != 3:
        raise RuntimeError("fallback calibration requires three repositories")
    extras = []
    for row in repo_splits[:2]:
        extra = row["structural_candidate_task_ids"].pop(0)
        row["calibration_task_ids"].append(extra)
        row["counts"]["calibration"] += 1
        row["counts"]["structural_candidates"] -= 1
        extras.append(extra)
    return extras


def build_payload() -> dict[str, Any]:
    d0, q1 = load_gates()
    selected = list(d0["selected_repositories"])
    expected_repos = 4 if "PRIMARY_FOUR" in d0["decision"] else 3
    if len(selected) != expected_repos:
        raise RuntimeError("D0 selected repository count drift")
    repo_splits = [
        split_for_repo(repo, list(d0["selected_qualified_task_ids"][repo]))
        for repo in selected
    ]
    fallback_extra_calibration: list[str] = []
    if expected_repos == 3:
        # Section 28 fixes eight total calibration tasks. The first structural
        # candidate from each of the first two hash-ordered repositories supplies
        # the two extras without outcome use and leaves ten candidates there.
        fallback_extra_calibration = apply_fallback_calibration(repo_splits)
    all_source = [x for row in repo_splits for x in row["source_task_ids"]]
    all_calibration = [x for row in repo_splits for x in row["calibration_task_ids"]]
    all_candidates = [x for row in repo_splits for x in row["structural_candidate_task_ids"]]
    if set(all_source) & set(all_calibration) or set(all_source) & set(all_candidates) or set(all_calibration) & set(all_candidates):
        raise RuntimeError("global split overlap")
    if len(all_calibration) != 8:
        raise RuntimeError("calibration count drift")
    receipts = {}
    for task_id in all_source + all_calibration + all_candidates:
        candidates = sorted(RECEIPT_DIR.glob(f"*-{task_id.replace('__', '-')}.json"))
        if len(candidates) != 1:
            raise RuntimeError(f"missing unique qualification receipt for {task_id}")
        receipt = json.loads(candidates[0].read_text(encoding="utf-8"))
        if not receipt.get("qualified") or receipt.get("qualification_attempt_count") != 1:
            raise RuntimeError(f"unqualified or repeated task entered split: {task_id}")
        receipts[task_id] = {
            "qualification_receipt": str(candidates[0].relative_to(ROOT)),
            "qualification_receipt_sha256": sha256_file(candidates[0]),
            "task_sha256": sha256_text(task_id),
            "base_commit": receipt["task_receipt"]["base_commit"],
            "image_manifest_digest": receipt["task_receipt"]["image_manifest"],
        }
    split_identity = {
        "repositories": selected, "repo_splits": repo_splits,
        "source_task_ids": all_source, "calibration_task_ids": all_calibration,
        "structural_candidate_task_ids": all_candidates,
    }
    return {
        "schema_version": 1, "experiment_id": EXPERIMENT_ID,
        "stage": "SOURCE_CALIBRATION_STRUCTURAL_CANDIDATE_FREEZE",
        "created_at_utc": utcnow(),
        "decision": "QWEN_OUTCOME_BLIND_TASK_SPLITS_FROZEN",
        "d0_index_path": str(D0_INDEX.relative_to(ROOT)),
        "d0_index_sha256": sha256_file(D0_INDEX),
        "q1_result_path": str(Q1_RESULT.relative_to(ROOT)),
        "q1_result_sha256": sha256_file(Q1_RESULT),
        "dataset_design": "PRIMARY_4_REPOSITORY" if expected_repos == 4 else "FALLBACK_3_REPOSITORY",
        "fallback_extra_calibration_task_ids": fallback_extra_calibration,
        "fallback_extra_rule": (
            "none"
            if expected_repos == 4
            else "first structural candidate from each of first two repo-hash-ordered repositories"
        ),
        **split_identity,
        "split_identity_sha256": sha256_text(canonical_json(split_identity)),
        "task_receipts": receipts,
        "checks": {
            "source_calibration_candidate_disjoint": True,
            "source_count": len(all_source),
            "calibration_count": len(all_calibration),
            "no_behavioral_outcomes_used": True,
            "all_qualification_attempt_counts_one": True,
        },
        "scientific_boundary": {
            "pilot_task_ids_finalized": False,
            "confirmatory_task_ids_finalized": False,
            "source_execution_authorized": True,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable task split")
    payload = build_payload()
    return {"decision": payload["decision"], "file_sha256": write_json(output, payload),
            "source_count": len(payload["source_task_ids"]),
            "calibration_count": len(payload["calibration_task_ids"])}


if __name__ == "__main__":
    print(json.dumps(freeze(), sort_keys=True))
