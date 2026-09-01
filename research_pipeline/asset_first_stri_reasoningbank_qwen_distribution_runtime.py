"""Stage-1 rootful runtime qualification for Qwen source trajectories.

This module also exposes the common zero-model runtime qualification primitive used
by the later evaluation-runtime gate.  Source runtime qualification is deliberately
limited to the frozen source split so unselected structural candidates are not
materialized into the rootful Docker daemon before they are needed.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

from research_pipeline import asset_first_stri_reasoningbank_p1_core as p1_core
from research_pipeline import asset_first_stri_swebench_oci_import as oci
from research_pipeline.asset_first_stri_reasoningbank_p1_core import (
    ROOT, canonical_json, sha256_file, sha256_text, utcnow, write_json,
)
from research_pipeline.asset_first_stri_reasoningbank_qwen_distribution_d0_qualify import (
    QualificationDockerRun, acquire_and_import, candidate_schedule,
)
ROOTFUL_DOCKER_HOST = "unix:///var/run/docker.sock"

EXPERIMENT_ID = "E1-STRI-REASONINGBANK-QWEN-DISTRIBUTION-V3-20260901"
SPLIT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-task-split-20260901.json"
D0_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-d0-evaluator-index-20260901.json"
SOURCE_CONTRACT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-contract-20260901.json"
SOURCE_INDEX = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-index-20260901.json"
SOURCE_RECEIPT_DIR = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-receipts-20260901"
SOURCE_RESULT = ROOT / "generated/asset-first-stri-reasoningbank-qwen-distribution-source-runtime-result-20260901.json"
EXPECTED_SOURCE_CONTRACT_SHA256 = "PENDING"


class BehavioralRuntimeBlocker(RuntimeError):
    """Pre-scientific runtime/substrate blocker; never changes task eligibility."""


def load_split_d0() -> tuple[dict[str, Any], dict[str, Any]]:
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    d0 = json.loads(D0_INDEX.read_text(encoding="utf-8"))
    if split.get("decision") != "QWEN_OUTCOME_BLIND_TASK_SPLITS_FROZEN":
        raise RuntimeError("Qwen split gate closed")
    if d0.get("execution_complete") is not True or d0.get("decision") not in {
        "D0_PRIMARY_FOUR_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
        "D0_FALLBACK_THREE_REPOSITORY_EVALUATOR_FEASIBILITY_PASS",
    }:
        raise RuntimeError("D0 evaluator feasibility not terminal/pass")
    if split.get("d0_index_sha256") != sha256_file(D0_INDEX):
        raise RuntimeError("split/D0 binding drift")
    return split, d0


def build_runtime_plan(
    split: dict[str, Any], task_ids: Sequence[str], *, prefix: str,
) -> list[dict[str, Any]]:
    repo_by_task = {
        task_id: row["repo"]
        for row in split["repo_splits"]
        for task_id in row["qualified_order"]
    }
    plan: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ordinal, task_id in enumerate(task_ids, start=1):
        if task_id in seen:
            raise RuntimeError("runtime plan duplicate task")
        seen.add(task_id)
        if task_id not in split["task_receipts"] or task_id not in repo_by_task:
            raise RuntimeError(f"runtime task absent from frozen split: {task_id}")
        meta = split["task_receipts"][task_id]
        plan.append({
            "ordinal": ordinal,
            "runtime_id": f"{prefix}-{ordinal:03d}",
            "instance_id": task_id,
            "repo": repo_by_task[task_id],
            "qualification_receipt": meta["qualification_receipt"],
            "qualification_receipt_sha256": meta["qualification_receipt_sha256"],
            "task_sha256": meta["task_sha256"],
            "base_commit": meta["base_commit"],
            "image_manifest_digest": meta["image_manifest_digest"],
            "attempt_count": 1,
        })
    return plan


def source_runtime_plan(split: dict[str, Any]) -> list[dict[str, Any]]:
    plan = build_runtime_plan(split, list(split["source_task_ids"]), prefix="QWEN-SOURCE-RUNTIME")
    expected = 32 if len(split["repositories"]) == 4 else 24
    if len(plan) != expected:
        raise RuntimeError(f"source runtime plan count drift: {len(plan)} != {expected}")
    return plan


def common_contract_fields(*, split: dict[str, Any], d0: dict[str, Any], plan: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "split_path": str(SPLIT.relative_to(ROOT)),
        "split_sha256": sha256_file(SPLIT),
        "d0_index_path": str(D0_INDEX.relative_to(ROOT)),
        "d0_index_sha256": sha256_file(D0_INDEX),
        "d0_decision": d0["decision"],
        "docker_host": ROOTFUL_DOCKER_HOST,
        "rootful_runtime_authority": "this prospective population-scoped runtime contract",
        "historical_D0_rootful_repair_authority_reused": False,
        "plan": plan,
        "plan_sha256": sha256_text(canonical_json(plan)),
        "qualification_semantics": {
            "exact_frozen_image_digest_required": True,
            "linux_amd64_required": True,
            "exact_base_commit_required": True,
            "clean_base_required": True,
            "container_start_required": True,
            "read_only_exec_probe_required": True,
            "cleanup_required": True,
            "gold_patch_applied": False,
            "test_patch_applied": False,
            "evaluator_run": False,
            "model_calls": 0,
            "provider_calls": 0,
            "behavioral_outcomes_observed": False,
        },
        "failure_policy": {
            "operational_failure_changes_task_eligibility": False,
            "automatic_retry": False,
            "task_replacement": False,
            "on_blocker": "freeze index and require prospective implementation repair before resuming same untouched runtime unit",
        },
        "credential_material_present": False,
    }


def source_contract_payload() -> dict[str, Any]:
    split, d0 = load_split_d0()
    plan = source_runtime_plan(split)
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFICATION_AUTHORIZED",
        **common_contract_fields(split=split, d0=d0, plan=plan),
        "scientific_boundary": {
            "source_generation_authorized": False,
            "evaluation_runtime_qualification_authorized": False,
            "calibration_authorized": False,
            "pilot_authorized": False,
            "confirmatory_execution_authorized": False,
        },
    }


def freeze_source_contract(output: Path = SOURCE_CONTRACT) -> dict[str, Any]:
    if output.exists():
        raise RuntimeError("refusing to overwrite immutable source runtime contract")
    payload = source_contract_payload()
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(output, payload),
        "planned_task_count": len(payload["plan"]),
    }


def receipt_path(receipt_dir: Path, unit: dict[str, Any]) -> Path:
    safe = unit["instance_id"].replace("__", "-")
    return receipt_dir / f"{int(unit['ordinal']):03d}-{safe}.json"


def load_completed(plan: list[dict[str, Any]], receipt_dir: Path) -> list[dict[str, Any]]:
    completed: list[dict[str, Any]] = []
    missing_seen = False
    for unit in plan:
        path = receipt_path(receipt_dir, unit)
        if not path.exists():
            missing_seen = True
            continue
        if missing_seen:
            raise RuntimeError("runtime receipts are not a frozen-order prefix")
        row = json.loads(path.read_text(encoding="utf-8"))
        if row["runtime_id"] != unit["runtime_id"] or row["attempt_count"] != 1:
            raise RuntimeError("runtime receipt identity/attempt drift")
        completed.append(row)
    return completed


def index_payload(
    *, stage: str, contract_path: Path, receipt_dir: Path,
    contract: dict[str, Any], completed: list[dict[str, Any]],
    blocker: dict[str, Any] | None = None,
    inflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    complete = len(completed) == len(contract["plan"])
    return {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": stage,
        "created_at_utc": utcnow(),
        "decision": f"{stage}_COMPLETE" if complete else f"{stage}_IN_PROGRESS",
        "execution_complete": complete,
        "contract_sha256": sha256_file(contract_path),
        "planned_count": len(contract["plan"]),
        "completed_count": len(completed),
        "journal_record_count": len(completed),
        "inflight": inflight,
        "operational_blocker": blocker,
        "journal": [{
            "ordinal": row["ordinal"],
            "runtime_id": row["runtime_id"],
            "instance_id": row["instance_id"],
            "attempt_count": row["attempt_count"],
            "qualified": row["qualified"],
            "persisted": True,
            "receipt_sha256": sha256_file(receipt_path(receipt_dir, row)),
        } for row in completed],
        "checks": {
            "every_attempt_count_one": all(row["attempt_count"] == 1 for row in completed),
            "every_completed_runtime_qualified": all(row["qualified"] for row in completed),
            "no_model_calls": True,
            "no_provider_calls": True,
            "no_evaluator_calls": True,
            "no_gold_or_test_patch": True,
            "no_behavioral_outcomes": True,
        },
        "credential_material_present": False,
    }


def activate_rootful_runtime() -> dict[str, str]:
    """Bind helper calls to rootful Docker under the current runtime contract."""
    p1_core.DOCKER_HOST = ROOTFUL_DOCKER_HOST
    oci.DOCKER_HOST = ROOTFUL_DOCKER_HOST
    return {"docker_host": ROOTFUL_DOCKER_HOST}


def qualify_unit(unit: dict[str, Any]) -> dict[str, Any]:
    qpath = ROOT / unit["qualification_receipt"]
    if sha256_file(qpath) != unit["qualification_receipt_sha256"]:
        raise BehavioralRuntimeBlocker("D0 qualification receipt drift")
    q = json.loads(qpath.read_text(encoding="utf-8"))
    if q.get("qualified") is not True or q.get("qualification_attempt_count") != 1:
        raise BehavioralRuntimeBlocker("unqualified D0 task entered runtime plan")
    task = q["task_receipt"]
    if task["model_visible_task_sha256"] != unit["task_sha256"]:
        raise BehavioralRuntimeBlocker("runtime task hash drift")
    if task["base_commit"] != unit["base_commit"]:
        raise BehavioralRuntimeBlocker("runtime base commit drift")
    meta = task["image_manifest"]
    if meta["manifest_digest"] != unit["image_manifest_digest"]:
        raise BehavioralRuntimeBlocker("runtime image digest drift")
    schedule_by_id = {row["instance_id"]: row for row in candidate_schedule()}
    schedule_unit = schedule_by_id.get(unit["instance_id"])
    if schedule_unit is None:
        raise BehavioralRuntimeBlocker("task absent from frozen D0 candidate schedule")
    try:
        image = acquire_and_import(schedule_unit, meta)
    except Exception as error:
        raise BehavioralRuntimeBlocker(
            f"rootful exact image materialization failed: {type(error).__name__}: {error}"
        ) from error
    if not image.get("exact_digest_visible") or not image.get("architecture_amd64_visible"):
        raise BehavioralRuntimeBlocker("rootful materialized image lacks exact digest/architecture proof")
    container = QualificationDockerRun(
        image=image["image_pull_reference"],
        base_commit=unit["base_commit"],
        run_id=f"{unit['runtime_id']}-{unit['instance_id']}",
    )
    runtime: dict[str, Any] | None = None
    probe: dict[str, Any] | None = None
    cleanup: dict[str, Any] | None = None
    try:
        runtime = container.start()
        probe = container.exec(
            "test \"$(git rev-parse HEAD)\" = " + unit["base_commit"] +
            " && test -z \"$(git status --porcelain=v1 --untracked-files=all)\""
            " && printf 'QWEN_RUNTIME_OK\\n'",
            timeout=60,
        )
        if probe["returncode"] != 0 or probe["timed_out"] or "QWEN_RUNTIME_OK" not in probe["output"]:
            raise BehavioralRuntimeBlocker("rootful runtime read-only probe failed")
    finally:
        cleanup = container.close()
    if not cleanup or cleanup.get("accepted") is not True:
        raise BehavioralRuntimeBlocker("rootful runtime cleanup not accepted")
    checks = {
        "d0_receipt_exact": True,
        "task_hash_exact": True,
        "base_commit_exact": True,
        "image_manifest_digest_exact": True,
        "rootful_docker_host_exact": ROOTFUL_DOCKER_HOST == "unix:///var/run/docker.sock",
        "exact_digest_visible": bool(image["exact_digest_visible"]),
        "architecture_amd64_visible": bool(image["architecture_amd64_visible"]),
        "runtime_started": runtime is not None,
        "read_only_probe_pass": True,
        "cleanup_accepted": True,
        "gold_patch_not_applied": True,
        "test_patch_not_applied": True,
        "evaluator_not_run": True,
        "model_calls_zero": True,
        "provider_calls_zero": True,
        "behavioral_outcomes_not_observed": True,
    }
    return {
        **unit,
        "created_at_utc": utcnow(),
        "docker_host": ROOTFUL_DOCKER_HOST,
        "image_runtime": image,
        "runtime_receipt": runtime,
        "probe_receipt": probe,
        "cleanup_receipt": cleanup,
        "checks": checks,
        "qualified": all(checks.values()),
        "model_calls": 0,
        "provider_calls": 0,
        "evaluator_calls": 0,
        "behavioral_outcomes_observed": False,
        "credential_material_present": False,
    }


def execute_runtime_plan(
    *, stage: str, contract_path: Path, expected_contract_sha256: str,
    index_path: Path, receipt_dir: Path,
) -> dict[str, Any]:
    if expected_contract_sha256 == "PENDING":
        raise RuntimeError("runtime contract SHA not pinned")
    if sha256_file(contract_path) != expected_contract_sha256:
        raise RuntimeError("runtime contract SHA drift")
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["split_sha256"] != sha256_file(SPLIT):
        raise RuntimeError("runtime split binding drift")
    activate_rootful_runtime()
    receipt_dir.mkdir(parents=True, exist_ok=True)
    completed = load_completed(contract["plan"], receipt_dir)
    if index_path.exists():
        prior = json.loads(index_path.read_text(encoding="utf-8"))
        inflight = prior.get("inflight")
        if inflight:
            unit = contract["plan"][int(inflight["ordinal"]) - 1]
            if not receipt_path(receipt_dir, unit).exists():
                raise RuntimeError("RUNTIME_AMBIGUOUS_INFLIGHT_HOLD: refusing duplicate runtime unit")
    write_json(index_path, index_payload(
        stage=stage, contract_path=contract_path, receipt_dir=receipt_dir,
        contract=contract, completed=completed))
    for unit in contract["plan"][len(completed):]:
        write_json(index_path, index_payload(
            stage=stage, contract_path=contract_path, receipt_dir=receipt_dir,
            contract=contract, completed=completed,
            inflight={
                "ordinal": unit["ordinal"], "runtime_id": unit["runtime_id"],
                "instance_id": unit["instance_id"], "attempt_count": 1,
                "state": "DISPATCHED_BEFORE_RUNTIME_SIDE_EFFECT",
            }))
        try:
            receipt = qualify_unit(unit)
        except Exception as error:
            blocker = {
                "ordinal": unit["ordinal"],
                "runtime_id": unit["runtime_id"],
                "instance_id": unit["instance_id"],
                "failure_layer": "runtime_or_execution_substrate",
                "error_type": type(error).__name__,
                "message": str(error),
                "changes_task_eligibility": False,
                "scientific_belief_update": "none",
                "authorized_next_action": "prospectively diagnose/repair runtime, then resume same untouched runtime qualification unit",
            }
            write_json(index_path, index_payload(
                stage=stage, contract_path=contract_path, receipt_dir=receipt_dir,
                contract=contract, completed=completed, blocker=blocker))
            return {
                "decision": f"{stage}_HOLD", "execution_complete": False,
                "completed_count": len(completed), "blocker": blocker,
                "index_sha256": sha256_file(index_path),
            }
        target = receipt_path(receipt_dir, unit)
        if target.exists():
            raise RuntimeError("refusing to overwrite runtime receipt")
        write_json(target, receipt)
        completed.append(json.loads(target.read_text(encoding="utf-8")))
        write_json(index_path, index_payload(
            stage=stage, contract_path=contract_path, receipt_dir=receipt_dir,
            contract=contract, completed=completed))
        print(json.dumps({
            "ordinal": unit["ordinal"], "instance_id": unit["instance_id"],
            "qualified": receipt["qualified"], "completed": len(completed),
        }, sort_keys=True), flush=True)
    if any(row.get("qualified") is not True for row in completed):
        raise RuntimeError("completed runtime receipt is not qualified")
    return {
        "decision": f"{stage}_COMPLETE",
        "execution_complete": True,
        "completed_count": len(completed),
        "index_sha256": sha256_file(index_path),
    }


def execute_source_runtime() -> dict[str, Any]:
    result = execute_runtime_plan(
        stage="QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFICATION",
        contract_path=SOURCE_CONTRACT,
        expected_contract_sha256=EXPECTED_SOURCE_CONTRACT_SHA256,
        index_path=SOURCE_INDEX,
        receipt_dir=SOURCE_RECEIPT_DIR,
    )
    if not result["execution_complete"]:
        return result
    contract = json.loads(SOURCE_CONTRACT.read_text(encoding="utf-8"))
    completed = load_completed(contract["plan"], SOURCE_RECEIPT_DIR)
    payload = {
        "schema_version": 1,
        "experiment_id": EXPERIMENT_ID,
        "stage": "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFICATION",
        "created_at_utc": utcnow(),
        "decision": "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFIED_SOURCE_GATE_OPEN",
        "contract_sha256": sha256_file(SOURCE_CONTRACT),
        "index_sha256": sha256_file(SOURCE_INDEX),
        "split_sha256": sha256_file(SPLIT),
        "docker_host": ROOTFUL_DOCKER_HOST,
        "planned_count": len(contract["plan"]),
        "qualified_count": len(completed),
        "all_attempt_count_one": all(row["attempt_count"] == 1 for row in completed),
        "model_calls": 0, "provider_calls": 0, "evaluator_calls": 0,
        "behavioral_outcomes_observed": False,
        "scientific_boundary": {
            "source_generation_authorized": True,
            "evaluation_runtime_qualification_authorized": False,
            "calibration_authorized": False,
            "pilot_authorized": False,
            "confirmatory_execution_authorized": False,
        },
        "credential_material_present": False,
    }
    if SOURCE_RESULT.exists():
        raise RuntimeError("refusing to overwrite source runtime result")
    return {
        "decision": payload["decision"],
        "file_sha256": write_json(SOURCE_RESULT, payload),
        "qualified_count": len(completed),
    }


def require_source_qualified() -> dict[str, Any]:
    if not SOURCE_RESULT.is_file():
        raise RuntimeError("Qwen source runtime result absent")
    result = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    if result.get("decision") != "QWEN_ROOTFUL_SOURCE_RUNTIME_QUALIFIED_SOURCE_GATE_OPEN":
        raise RuntimeError("Qwen source rootful runtime gate closed")
    if result.get("docker_host") != ROOTFUL_DOCKER_HOST:
        raise RuntimeError("Qwen source runtime Docker host drift")
    if result.get("split_sha256") != sha256_file(SPLIT):
        raise RuntimeError("Qwen source runtime split binding drift")
    activate_rootful_runtime()
    return result


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze-contract", action="store_true")
    args = parser.parse_args()
    value = freeze_source_contract() if args.freeze_contract else execute_source_runtime()
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
