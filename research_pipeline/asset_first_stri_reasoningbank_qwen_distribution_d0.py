"""Prospectively freeze Qwen STRI D0 dataset feasibility without model calls."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT,
    canonical_json,
    sha256_file,
    sha256_text,
    utcnow,
    write_json,
)

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
STARTING_CANONICAL_SHA = "da3ebe8fc66503b28183853e251fa291bfb8d118"
DATASET = Path(
    "/data/wyt/agent-self-evolution-observatory/external/"
    "stri-swebench-verified-78f471bf655a3137b2e8a75af1501690ec009ec3/"
    "data/test-00000-of-00001.parquet"
)
DATASET_REVISION = "78f471bf655a3137b2e8a75af1501690ec009ec3"
DATASET_SHA256 = "030cfd7f2a704c4c0226e7f104c725a3b41230b1d3517f9c915ad7ea5be3fa25"
OUTPUT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-feasibility-20260901.json"

# One content-addressed historical receipt per task is enough to establish exposure.
HISTORICAL_EXPOSURE_RECEIPTS = {
    "django__django-11740": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-11880": "generated/asset-first-stri-reasoningbank-p1-q10-adjudication-20260831.json",
    "django__django-13809": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-14787": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-15315": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-15695": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-15731": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "django__django-16100": "generated/asset-first-stri-reasoningbank-p1-q2-adjudication-20260830.json",
    "django__django-16454": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "pytest-dev__pytest-5631": "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-adjudication-20260829.json",
    "sphinx-doc__sphinx-9230": "generated/asset-first-stri-reasoningbank-p1-q10-adjudication-20260831.json",
    "sphinx-doc__sphinx-9711": "generated/asset-first-stri-reasoningbank-full-p1-adjudication-20260831.json",
    "sympy__sympy-13798": "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-adjudication-20260829.json",
    "sympy__sympy-17318": "generated/asset-first-stri-reasoningbank-p1-minimal-pilot-adjudication-20260829.json",
    "sympy__sympy-18211": "generated/asset-first-stri-reasoningbank-p1-q2-adjudication-20260830.json",
}
EXPECTED_FRESH_COUNTS = {
    "astropy/astropy": 22,
    "mwaskom/seaborn": 2,
    "pydata/xarray": 22,
    "sympy/sympy": 72,
    "matplotlib/matplotlib": 34,
    "django/django": 222,
    "pallets/flask": 1,
    "psf/requests": 8,
    "scikit-learn/scikit-learn": 32,
    "pytest-dev/pytest": 18,
    "sphinx-doc/sphinx": 42,
    "pylint-dev/pylint": 10,
}


def git_head() -> str:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=10,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError("unable to resolve isolated worktree HEAD")
    return completed.stdout.strip()


def public_candidate(row: dict[str, Any], repo_rank: int, task_rank: int) -> dict[str, Any]:
    """Return a qualification fixture with no gold or test-patch content."""
    instance_id = str(row["instance_id"])
    model_visible = {
        "instance_id": instance_id,
        "problem_statement": str(row["problem_statement"]),
        "base_commit": str(row["base_commit"]),
        "repo": str(row["repo"]),
        "version": str(row["version"]),
    }
    evaluator_contract = {
        "eval_type": str(row["eval_type"]),
        "eval_script_sha256": sha256_text(str(row["eval_script"])),
        "log_parser": str(row["log_parser"]),
        "FAIL_TO_PASS": list(row["FAIL_TO_PASS"]),
        "PASS_TO_PASS": list(row["PASS_TO_PASS"]),
        "test_patch_sha256": sha256_text(str(row["test_patch"])),
        "test_patch_available": bool(str(row["test_patch"]).strip()),
    }
    full_record = {
        key: value
        for key, value in row.items()
        if key not in {"patch", "test_patch"}
    }
    full_record.update(
        {
            "gold_patch_sha256": sha256_text(str(row["patch"])),
            "test_patch_sha256": sha256_text(str(row["test_patch"])),
        }
    )
    return {
        "repo_hash_rank": repo_rank,
        "task_hash_rank_within_repo": task_rank,
        "instance_id": instance_id,
        "instance_id_sha256": sha256_text(instance_id),
        "repo": str(row["repo"]),
        "base_commit": str(row["base_commit"]),
        "environment_setup_commit": str(row["environment_setup_commit"]),
        "image_tag": str(row["image"]),
        "difficulty_dataset_value": str(row["difficulty"]),
        "difficulty_use_status": "PENDING_OFFICIAL_PROVENANCE_QUALIFICATION",
        "model_visible": model_visible,
        "model_visible_task_sha256": sha256_text(canonical_json(model_visible)),
        "evaluator_contract": evaluator_contract,
        "evaluator_contract_sha256": sha256_text(canonical_json(evaluator_contract)),
        "gold_patch_sha256": sha256_text(str(row["patch"])),
        "public_record_without_patch_content_sha256": sha256_text(canonical_json(full_record)),
        "gold_patch_content_persisted": False,
        "test_patch_content_persisted": False,
        "model_calls_made": 0,
        "task_outcome_observed": False,
    }


def build_payload(*, starting_sha: str | None = None) -> dict[str, Any]:
    if sha256_file(DATASET) != DATASET_SHA256:
        raise RuntimeError("D0 dataset SHA-256 drift")
    rows = pq.read_table(DATASET).to_pylist()
    if len(rows) != 500:
        raise RuntimeError("D0 dataset row-count drift")
    row_ids = {str(row["instance_id"]) for row in rows}
    historical = set(HISTORICAL_EXPOSURE_RECEIPTS)
    if not historical.issubset(row_ids):
        raise RuntimeError("historical exclusion ID missing from frozen dataset")

    exposure_ledger = []
    for instance_id in sorted(historical):
        relative = HISTORICAL_EXPOSURE_RECEIPTS[instance_id]
        receipt = ROOT / relative
        if not receipt.is_file():
            raise RuntimeError(f"historical receipt missing: {relative}")
        if instance_id not in receipt.read_text(encoding="utf-8"):
            raise RuntimeError(f"historical receipt does not bind task: {instance_id}")
        exposure_ledger.append(
            {
                "instance_id": instance_id,
                "receipt_path": relative,
                "receipt_sha256": sha256_file(receipt),
                "exclusion_reason": "HISTORICAL_E1_OUTCOME_OR_EXECUTION_EXPOSURE",
            }
        )

    fresh_rows = [row for row in rows if str(row["instance_id"]) not in historical]
    by_repo: dict[str, list[dict[str, Any]]] = {}
    for row in fresh_rows:
        by_repo.setdefault(str(row["repo"]), []).append(row)
    repo_order = sorted(by_repo, key=lambda name: (sha256_text(name), name))
    repo_summaries = []
    candidates = []
    for repo_rank, repo in enumerate(repo_order, start=1):
        ordered = sorted(
            by_repo[repo],
            key=lambda row: (
                sha256_text(str(row["instance_id"])),
                str(row["instance_id"]),
            ),
        )
        repo_summaries.append(
            {
                "repo_hash_rank": repo_rank,
                "repo": repo,
                "repo_name_sha256": sha256_text(repo),
                "fresh_raw_count": len(ordered),
                "raw_capacity_at_least_21": len(ordered) >= 21,
                "zero_model_qualified_count": None,
                "final_repository_eligibility": "PENDING_D0_EVALUATOR_QUALIFICATION",
            }
        )
        candidates.extend(
            public_candidate(row, repo_rank, task_rank)
            for task_rank, row in enumerate(ordered, start=1)
        )

    actual_counts = {repo: len(values) for repo, values in by_repo.items()}
    if actual_counts != EXPECTED_FRESH_COUNTS:
        raise RuntimeError("D0 deterministic fresh-count drift")
    raw_capacity = [row["repo"] for row in repo_summaries if row["raw_capacity_at_least_21"]]
    expected_capacity = [
        "astropy/astropy",
        "pydata/xarray",
        "sympy/sympy",
        "matplotlib/matplotlib",
        "django/django",
        "scikit-learn/scikit-learn",
        "sphinx-doc/sphinx",
    ]
    if raw_capacity != expected_capacity:
        raise RuntimeError("D0 deterministic repository hash ordering drift")

    head = starting_sha or git_head()
    if head != STARTING_CANONICAL_SHA:
        raise RuntimeError(f"D0 must freeze from live canonical {STARTING_CANONICAL_SHA}, got {head}")
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "D0_ZERO_MODEL_DATASET_FEASIBILITY",
        "created_at_utc": utcnow(),
        "decision": "D0_RAW_FEASIBILITY_FROZEN_EVALUATOR_QUALIFICATION_REQUIRED",
        "starting_canonical_sha": head,
        "dataset": {
            "id": "SWE-bench/SWE-bench_Verified",
            "revision": DATASET_REVISION,
            "parquet_path": str(DATASET),
            "parquet_sha256": DATASET_SHA256,
            "row_count": len(rows),
            "acquisition_contract": "hf-mirror + fixed revision + SHA-256 verification",
        },
        "historical_exclusion_ledger": exposure_ledger,
        "historical_exclusion_count": len(exposure_ledger),
        "fresh_task_count": len(fresh_rows),
        "repository_order_rule": "ascending (SHA256(repo_name), repo_name)",
        "task_order_rule": "within repo ascending (SHA256(instance_id), instance_id)",
        "repository_summaries": repo_summaries,
        "raw_capacity_repository_order": raw_capacity,
        "candidate_pool": candidates,
        "selection_boundary": {
            "primary_design": "first four repositories in frozen repo-hash order with >=21 zero-model-qualified fresh tasks",
            "fallback_design": "first three repositories in frozen repo-hash order satisfying frozen fallback capacity after zero-model and structural qualification",
            "primary_repository_count": 4,
            "primary_minimum_qualified_per_repo": 21,
            "fallback_repository_count": 3,
            "fallback_confirmatory_total": 24,
            "single_repository_fallback_forbidden": True,
            "final_repositories_selected": False,
            "behavioral_outcomes_used": False,
        },
        "difficulty": {
            "dataset_field_present": all(bool(str(row["difficulty"])) for row in rows),
            "use_for_stratification": False,
            "status": "PENDING_EXACT_OFFICIAL_HUMAN_DIFFICULTY_PROVENANCE_QUALIFICATION",
            "llm_derived_labels_forbidden": True,
        },
        "checks": {
            "dataset_sha_exact": True,
            "row_count_exact": len(rows) == 500,
            "historical_exclusions_exact": len(exposure_ledger) == 15,
            "fresh_count_exact": len(fresh_rows) == 485,
            "candidate_ids_unique": len({row["instance_id"] for row in candidates}) == len(candidates),
            "historical_ids_absent_from_candidates": not historical.intersection(
                row["instance_id"] for row in candidates
            ),
            "gold_patch_content_absent": all(
                row["gold_patch_content_persisted"] is False for row in candidates
            ),
            "test_patch_content_absent": all(
                row["test_patch_content_persisted"] is False for row in candidates
            ),
            "model_calls_zero": True,
            "task_outcomes_unobserved": True,
            "credential_material_absent": True,
        },
        "scientific_boundary": {
            "zero_model_evaluator_qualification_required": True,
            "repository_feasibility_passed": False,
            "provider_calls_authorized": False,
            "source_generation_authorized": False,
            "confirmatory_execution_authorized": False,
            "paper_result_claim_authorized": False,
        },
        "credential_material_present": False,
    }


def freeze(output: Path = OUTPUT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable Qwen D0 freeze")
    payload = build_payload()
    if not all(payload["checks"].values()):
        raise RuntimeError("D0 invariant failed")
    file_sha = write_json(output, payload)
    return {
        "decision": payload["decision"],
        "file_sha256": file_sha,
        "candidate_count": len(payload["candidate_pool"]),
        "historical_exclusion_count": payload["historical_exclusion_count"],
        "model_calls_made": 0,
    }


def main() -> None:
    print(json.dumps(freeze(), sort_keys=True))


if __name__ == "__main__":
    main()
